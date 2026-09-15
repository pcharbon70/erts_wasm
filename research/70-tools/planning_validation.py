"""Validation helpers for structured plans and bounded execution evidence."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterator

import jsonschema
import yaml


PLANNING_FENCE = re.compile(
    r"^```planning-meta\s*\n(.*?)^```\s*$",
    flags=re.MULTILINE | re.DOTALL,
)
FENCED_BLOCK = re.compile(
    r"^(?P<fence>`{3,}|~{3,})[^\n]*\n.*?^(?P=fence)\s*$",
    flags=re.MULTILINE | re.DOTALL,
)
STREAM_DIRECTORY = re.compile(r"^\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")
PHASE_FILENAME = re.compile(
    r"^phase-(?P<number>\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$"
)
EVIDENCE_FILENAME = re.compile(
    r"^[a-z0-9]+(?:-[a-z0-9]+)*\.planning-evidence\.json$"
)
TASK_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
GATE_ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
TASK_LABEL = re.compile(
    r"^[ \t]*- \[(?P<state>[ xX])\] "
    r"(?P<number>\d+\.\d+\.\d+) Task "
    r"\[id: (?P<id>[a-z0-9][a-z0-9-]*)\] "
    r"\[area: (?P<area>[^\]]+)\] "
    r"\[after: (?P<after>[^\]]+)\]",
    flags=re.MULTILINE,
)
SUBTASK_LABEL = re.compile(
    r"^[ \t]*- \[(?P<state>[ xX])\] "
    r"(?P<number>\d+\.\d+\.\d+\.\d+) Subtask\s+—\s+.+?\.?\s*$",
    flags=re.MULTILINE,
)
CHECKED_BOX = re.compile(r"^[ \t]*- \[[xX]\][ \t]+.+$", flags=re.MULTILINE)
PHASE_LABEL = re.compile(
    r"^- \[(?P<state>[ xX])\] (?P<number>\d+) Phase\s+—\s+.+?\.?\s*$",
    flags=re.MULTILINE,
)
SECTION_LABEL = re.compile(
    r"^[ \t]+- \[(?P<state>[ xX])\] (?P<phase>\d+)\.(?P<section>\d+) "
    r"Section\s+—\s+(?P<title>.+?)\.?\s*$",
    flags=re.MULTILINE,
)
SHA256 = re.compile(r"^[0-9a-f]{64}$")

ALLOWED_TASK_AREAS = frozenset(
    {
        "beam-fixtures",
        "browser-host",
        "build-release",
        "c-runtime",
        "cross-cutting",
        "research-tools",
        "unresolved",
    }
)
REAL_EVIDENCE_ROOT = Path("assets")
SYNTHETIC_FIXTURE_DIRECTORY = Path("assets/planning-conformance")
MAX_EVIDENCE_RECORD_BYTES = 1_048_576
MAX_EVIDENCE_REFERENCE_BYTES = 16_777_216
MAX_EVIDENCE_AGGREGATE_BYTES = 134_217_728
MAX_EVIDENCE_RECORDS = 4096
HASH_CHUNK_BYTES = 65_536


class StringDateLoader(yaml.SafeLoader):
    """A safe loader that keeps ISO-looking values as strings."""

    def construct_mapping(
        self, node: yaml.nodes.MappingNode, deep: bool = False
    ) -> dict[object, object]:
        """Reject duplicate YAML keys instead of silently taking the last."""

        self.flatten_mapping(node)
        mapping: dict[object, object] = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                repeated = key in mapping
            except TypeError as error:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    "found an unhashable key",
                    key_node.start_mark,
                ) from error
            if repeated:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key {key!r}",
                    key_node.start_mark,
                )
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


StringDateLoader.yaml_implicit_resolvers = copy.deepcopy(
    yaml.SafeLoader.yaml_implicit_resolvers
)
for initial, resolvers in list(StringDateLoader.yaml_implicit_resolvers.items()):
    StringDateLoader.yaml_implicit_resolvers[initial] = [
        (tag, expression)
        for tag, expression in resolvers
        if tag != "tag:yaml.org,2002:timestamp"
    ]


@dataclass(frozen=True)
class PlanningDocument:
    """The validated machine-readable projection of one planning document."""

    path: Path
    document_id: str
    entities: dict[str, dict[str, object]]
    relations: tuple[dict[str, str], ...]
    tasks: dict[str, tuple[str, ...]]
    task_areas: dict[str, str] = field(default_factory=dict)
    checked_tasks: frozenset[str] = frozenset()
    task_numbers: dict[str, tuple[int, int, int]] = field(default_factory=dict)
    gates: frozenset[str] = frozenset()
    task_plan_ids: dict[str, str] = field(default_factory=dict)
    gate_plan_ids: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class PlanningAuthority:
    """Repository-wide identities that execution evidence may bind to."""

    entity_ids: frozenset[str]
    task_ids: frozenset[str]
    gate_ids: frozenset[str]
    task_plan_ids: dict[str, str] = field(default_factory=dict)
    gate_plan_ids: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class EvidenceValidationResult:
    """Validated real evidence identities and tasks closed by pass records."""

    record_ids: frozenset[str]
    passed_task_ids: frozenset[str]


def planning_blocks(markdown: str) -> list[str]:
    """Return fenced planning-authoring YAML blocks."""

    return PLANNING_FENCE.findall(markdown)


def mask_fenced_code(markdown: str) -> str:
    """Blank fenced blocks while preserving offsets and line boundaries."""

    return FENCED_BLOCK.sub(
        lambda match: "".join(
            "\n" if character == "\n" else " " for character in match.group(0)
        ),
        markdown,
    )


def github_heading_anchors(markdown: str) -> set[str]:
    """Approximate GitHub heading IDs, including duplicate suffixes."""

    anchors: set[str] = set()
    occurrences: defaultdict[str, int] = defaultdict(int)
    for line in markdown.splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        heading = re.sub(r"<[^>]+>", "", match.group(1))
        heading = re.sub(r"[`*_~]", "", heading).strip().lower()
        slug = re.sub(r"[^\w\- ]", "", heading, flags=re.UNICODE)
        slug = re.sub(r"\s+", "-", slug)
        suffix = occurrences[slug]
        occurrences[slug] += 1
        anchors.add(slug if suffix == 0 else f"{slug}-{suffix}")
    return anchors


def markdown_heading_section(markdown: str, level: int, title: str) -> str | None:
    """Return one named heading section, or None if absent or ambiguous."""

    lines = markdown.splitlines()
    starts: list[int] = []
    heading = re.compile(rf"^{'#' * level}\s+{re.escape(title)}\s*$")
    for index, line in enumerate(lines):
        if heading.fullmatch(line):
            starts.append(index + 1)
    if len(starts) != 1:
        return None
    start = starts[0]
    end = len(lines)
    next_heading = re.compile(r"^(#{1,6})\s+")
    for index in range(start, len(lines)):
        match = next_heading.match(lines[index])
        if match and len(match.group(1)) <= level:
            end = index
            break
    return "\n".join(lines[start:end])


def is_structured_planning_document(path: Path, research_root: Path) -> bool:
    """Return whether a document belongs to the adopted numbered plan tree."""

    planning_root = research_root / "60-planning"
    try:
        parts = path.relative_to(planning_root).parts
    except ValueError:
        return False
    return len(parts) >= 2 and STREAM_DIRECTORY.fullmatch(parts[0]) is not None


def _display(path: Path, display_path: Callable[[Path], str] | None) -> str:
    return display_path(path) if display_path is not None else path.as_posix()


def _table_rows(section: str | None) -> tuple[list[str], list[list[str]]]:
    """Parse the first simple pipe table in one Markdown section."""

    if section is None:
        return [], []
    lines = [
        line.strip()
        for line in section.splitlines()
        if line.strip().startswith("|")
    ]
    if len(lines) < 2:
        return [], []
    rows = [
        [cell.strip() for cell in line.strip("|").split("|")]
        for line in lines
    ]
    header = rows[0]
    if not all(
        re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in rows[1]
    ):
        return [], []
    return header, [row for row in rows[2:] if len(row) == len(header)]


def _plain_cell(value: str) -> str:
    """Remove the limited inline syntax used in planning identity tables."""

    text = value.strip().strip("`")
    link = re.fullmatch(r"\[([^\]]+)\]\([^)]+\)", text)
    return link.group(1).strip("`") if link else text


def _dependency_cell(value: str) -> tuple[tuple[str, ...], list[str]]:
    """Parse comma-separated IDs, accepting links whose labels are IDs."""

    text = value.strip()
    if text.casefold() == "none":
        return (), []
    dependencies: list[str] = []
    invalid: list[str] = []
    for part in text.split(","):
        task_id = _plain_cell(part.strip())
        if TASK_ID.fullmatch(task_id):
            dependencies.append(task_id)
        else:
            invalid.append(task_id)
    return tuple(dependencies), invalid


def _gate_ids(body: str, shown: str, errors: list[str]) -> frozenset[str]:
    section = markdown_heading_section(
        body, 2, "Gate-to-phase and artifact mapping"
    )
    if section is None:
        return frozenset()
    header, rows = _table_rows(section)
    column = "Gate / acceptance ID"
    if not header or column not in header:
        errors.append(f"{shown}: gate mapping must contain a {column!r} column")
        return frozenset()
    index = header.index(column)
    values: list[str] = []
    for row in rows:
        gate_id = _plain_cell(row[index])
        if not GATE_ID.fullmatch(gate_id):
            errors.append(f"{shown}: invalid gate or acceptance ID {gate_id!r}")
            continue
        values.append(gate_id)
    repeated = sorted({value for value in values if values.count(value) > 1})
    if repeated:
        errors.append(f"{shown}: gate mapping repeats IDs {repeated!r}")
    if not values:
        errors.append(
            f"{shown}: gate mapping must declare at least one gate or acceptance ID"
        )
    return frozenset(values)


def _validate_document_shape(
    path: Path,
    document_id: str,
    entities: dict[str, dict[str, object]],
    relations: tuple[dict[str, str], ...],
    shown: str,
    errors: list[str],
) -> None:
    """Bind stream/milestone/phase identities to their filesystem position."""

    entity = entities.get(document_id)
    if entity is None:
        return
    is_stream = path.name == "README.md" and bool(
        STREAM_DIRECTORY.fullmatch(path.parent.name)
    )
    is_milestone = path.name == "README.md" and bool(
        STREAM_DIRECTORY.fullmatch(path.parent.parent.name)
    )
    is_phase = PHASE_FILENAME.fullmatch(path.name) is not None
    if is_stream:
        if entity.get("kind") != "planning_stream" or len(entities) != 1:
            errors.append(
                f"{shown}: stream README must author exactly one planning_stream entity"
            )
        if relations:
            errors.append(f"{shown}: stream README must not author structural relations")
    elif is_milestone:
        plan_id = f"{document_id}.plan"
        plan = entities.get(plan_id)
        if entity.get("kind") != "milestone" or plan is None or plan.get("kind") != "plan":
            errors.append(
                f"{shown}: milestone README must author its milestone and {plan_id!r} plan"
            )
        if set(entities) != {document_id, plan_id}:
            errors.append(
                f"{shown}: milestone README may author only its milestone and plan"
            )
        if not any(
            relation == {
                "subject": document_id,
                "predicate": "contains",
                "object": plan_id,
            }
            for relation in relations
        ):
            errors.append(f"{shown}: milestone README is missing its contains relation")
        belongs = [
            relation
            for relation in relations
            if relation["predicate"] == "belongs_to"
        ]
        if len(belongs) != 1 or belongs[0]["subject"] != document_id:
            errors.append(
                f"{shown}: milestone README must belong to exactly one planning stream"
            )
    elif is_phase:
        if entity.get("kind") != "phase" or len(entities) != 1:
            errors.append(f"{shown}: phase must author exactly one phase entity")
        belongs = [
            relation
            for relation in relations
            if relation["predicate"] == "belongs_to"
        ]
        if (
            len(belongs) != 1
            or belongs[0]["subject"] != document_id
            or not belongs[0]["object"].endswith(".plan")
        ):
            errors.append(f"{shown}: phase must belong to exactly one milestone plan")
        if any(
            relation["predicate"] not in {"belongs_to", "precedes"}
            for relation in relations
        ):
            errors.append(
                f"{shown}: phase may author only belongs_to and optional precedes relations"
            )


def validate_planning_document(
    path: Path,
    body: str,
    validator: jsonschema.Draft202012Validator,
    errors: list[str],
    *,
    required: bool,
    display_path: Callable[[Path], str] | None = None,
) -> PlanningDocument | None:
    """Validate one planning block and its task/body projections."""

    shown = _display(path, display_path)
    blocks = planning_blocks(body)
    if not blocks:
        if required:
            errors.append(f"{shown}: missing required planning-meta block")
        return None
    if len(blocks) != 1:
        errors.append(f"{shown}: expected exactly one planning-meta block")
        return None

    try:
        value = yaml.load(blocks[0], Loader=StringDateLoader)
    except yaml.YAMLError as error:
        errors.append(f"{shown}: invalid planning-meta YAML: {error}")
        return None

    schema_errors = list(validator.iter_errors(value))
    for schema_error in sorted(
        schema_errors, key=lambda item: list(item.absolute_path)
    ):
        location = ".".join(str(part) for part in schema_error.absolute_path)
        errors.append(
            f"{shown}: planning-meta {location or '<root>'}: "
            f"{schema_error.message}"
        )
    if schema_errors or not isinstance(value, dict):
        return None

    structural_body = mask_fenced_code(body)
    anchors = github_heading_anchors(structural_body)
    entities: dict[str, dict[str, object]] = {}
    for entity in value["entities"]:
        entity_id = entity["id"]
        anchor = entity["source_anchor"]
        if anchor[1:] not in anchors:
            errors.append(
                f"{shown}: planning-meta entity {entity_id!r} "
                f"has missing source anchor {anchor!r}"
            )
        if entity_id in entities:
            errors.append(f"{shown}: planning-meta repeats entity id {entity_id!r}")
        entities[entity_id] = entity

    document_id = value["document_id"]
    if document_id not in entities:
        errors.append(
            f"{shown}: planning-meta document_id must identify an entity "
            "declared in the same block"
        )

    tasks: dict[str, tuple[str, ...]] = {}
    task_areas: dict[str, str] = {}
    task_numbers: dict[str, tuple[int, int, int]] = {}
    task_positions: dict[str, int] = {}
    checked_tasks: set[str] = set()
    task_matches = list(TASK_LABEL.finditer(structural_body))
    phase_labels = list(PHASE_LABEL.finditer(structural_body))
    section_labels = list(SECTION_LABEL.finditer(structural_body))
    subtask_matches = list(SUBTASK_LABEL.finditer(structural_body))
    phase_match = PHASE_FILENAME.fullmatch(path.name)
    recognized_matches = [task_matches]
    if phase_match is not None:
        recognized_matches.extend(
            [phase_labels, section_labels, subtask_matches]
        )
    hierarchy_match_starts = {
        match.start()
        for matches in recognized_matches
        for match in matches
    }
    for checkbox in CHECKED_BOX.finditer(structural_body):
        if checkbox.start() not in hierarchy_match_starts:
            errors.append(
                f"{shown}: checked planning checkbox is not a recognized "
                "phase, section, task, or subtask"
            )
    task_ids = [match.group("id") for match in task_matches]
    for task_id in sorted(set(task_ids)):
        if task_ids.count(task_id) > 1:
            errors.append(f"{shown}: planning task id {task_id!r} is repeated")
    for match in task_matches:
        task_id = match.group("id")
        area = match.group("area").strip()
        if area not in ALLOWED_TASK_AREAS:
            errors.append(
                f"{shown}: planning task {task_id!r} has unsupported area {area!r}"
            )
        dependencies, invalid = _dependency_cell(match.group("after"))
        if invalid:
            errors.append(
                f"{shown}: planning task {task_id!r} "
                f"has invalid after IDs {invalid!r}"
            )
        tasks[task_id] = dependencies
        task_areas[task_id] = area
        task_numbers[task_id] = tuple(
            int(part) for part in match.group("number").split(".")
        )
        task_positions[task_id] = match.start()
        if match.group("state").casefold() == "x":
            checked_tasks.add(task_id)

    task_section = markdown_heading_section(
        structural_body, 2, "Task identity, ownership, and dependencies"
    )
    header, rows = _table_rows(task_section)
    table: dict[str, tuple[str, tuple[str, ...]]] = {}
    required_columns = {"Task ID", "Area", "Requires"}
    if task_matches and task_section is None:
        errors.append(f"{shown}: missing unique task identity table section")
    elif task_section is not None and not required_columns.issubset(header):
        errors.append(
            f"{shown}: task identity table must contain "
            f"{sorted(required_columns)!r}"
        )
    elif header:
        task_index = header.index("Task ID")
        area_index = header.index("Area")
        requires_index = header.index("Requires")
        for row in rows:
            task_id = _plain_cell(row[task_index])
            area = _plain_cell(row[area_index])
            dependencies, invalid = _dependency_cell(row[requires_index])
            if not TASK_ID.fullmatch(task_id):
                errors.append(
                    f"{shown}: task identity table has invalid ID {task_id!r}"
                )
                continue
            if task_id in table:
                errors.append(
                    f"{shown}: task identity table repeats ID {task_id!r}"
                )
            if area not in ALLOWED_TASK_AREAS:
                errors.append(
                    f"{shown}: task identity table task {task_id!r} "
                    f"has unsupported area {area!r}"
                )
            if invalid:
                errors.append(
                    f"{shown}: task identity table task {task_id!r} "
                    f"has invalid Requires IDs {invalid!r}"
                )
            table[task_id] = (area, dependencies)

    table_ids = set(table)
    if set(task_ids) != table_ids:
        errors.append(
            f"{shown}: planning task identity conflict; "
            f"missing table rows={sorted(set(task_ids) - table_ids)}, "
            f"missing task labels={sorted(table_ids - set(task_ids))}"
        )
    for task_id in sorted(set(task_ids) & table_ids):
        table_area, table_dependencies = table[task_id]
        if table_area != task_areas[task_id]:
            errors.append(
                f"{shown}: planning task {task_id!r} area disagrees with its table row"
            )
        if set(table_dependencies) != set(tasks[task_id]):
            errors.append(
                f"{shown}: planning task {task_id!r} dependencies disagree "
                "with its Requires row"
            )

    in_milestone_directory = (
        path.name != "README.md"
        and path.parent != path.parent.parent
        and STREAM_DIRECTORY.fullmatch(path.parent.parent.name) is not None
    )
    if in_milestone_directory and phase_match is None:
        errors.append(
            f"{shown}: milestone plan document must use a "
            "phase-NN-kebab-case.md filename"
        )
    if phase_match is not None:
        phase_number = phase_match.group("number")
        expected_suffix = f".phase_{phase_number}"
        entity = entities.get(document_id)
        if not document_id.endswith(expected_suffix):
            errors.append(
                f"{shown}: phase document_id must end with {expected_suffix!r}"
            )
        if entity is not None and entity.get("kind") != "phase":
            errors.append(f"{shown}: phase document_id entity must use kind 'phase'")
        if (
            len(phase_labels) != 1
            or int(phase_labels[0].group("number")) != int(phase_number)
        ):
            errors.append(
                f"{shown}: expected one phase checkbox numbered {int(phase_number)}"
            )
        if not task_matches:
            errors.append(f"{shown}: phase must declare at least one task")
        if any(
            number[0] != int(phase_number) for number in task_numbers.values()
        ):
            errors.append(f"{shown}: task numbering does not match phase number")
        sections = section_labels
        section_numbers = [int(section.group("section")) for section in sections]
        if section_numbers and (
            len(section_numbers) != len(set(section_numbers))
            or sorted(section_numbers) != list(range(1, max(section_numbers) + 1))
        ):
            errors.append(
                f"{shown}: section numbers must be unique and contiguous from 1"
            )
        if len(task_numbers.values()) != len(set(task_numbers.values())):
            errors.append(f"{shown}: task hierarchy numbers must be unique")
        if any(number[1] not in set(section_numbers) for number in task_numbers.values()):
            errors.append(f"{shown}: task numbering references an undeclared section")
        subtask_states: dict[tuple[int, int, int, int], bool] = {}
        repeated_subtasks: set[tuple[int, int, int, int]] = set()
        for subtask in subtask_matches:
            number = tuple(
                int(part) for part in subtask.group("number").split(".")
            )
            if number in subtask_states:
                repeated_subtasks.add(number)
            subtask_states[number] = subtask.group("state").casefold() == "x"
        if repeated_subtasks:
            errors.append(
                f"{shown}: subtask hierarchy numbers are repeated: "
                f"{sorted(repeated_subtasks)!r}"
            )
        if any(number[0] != int(phase_number) for number in subtask_states):
            errors.append(f"{shown}: subtask numbering does not match phase number")
        task_number_set = set(task_numbers.values())
        orphaned_subtasks = sorted(
            number for number in subtask_states if number[:3] not in task_number_set
        )
        if orphaned_subtasks:
            errors.append(
                f"{shown}: subtask numbering references an undeclared task: "
                f"{orphaned_subtasks!r}"
            )
        section_entries = [
            (
                section.start(),
                (int(section.group("phase")), int(section.group("section"))),
                len(section.group(0)) - len(section.group(0).lstrip(" \t")),
            )
            for section in sections
        ]
        task_entries = [
            (
                task.start(),
                tuple(int(part) for part in task.group("number").split(".")),
                len(task.group(0)) - len(task.group(0).lstrip(" \t")),
            )
            for task in task_matches
        ]
        for task_position, task_number, task_indent in task_entries:
            preceding_sections = [
                entry for entry in section_entries if entry[0] < task_position
            ]
            active_section = preceding_sections[-1] if preceding_sections else None
            if (
                active_section is None
                or active_section[1] != task_number[:2]
                or task_indent <= active_section[2]
            ):
                errors.append(
                    f"{shown}: task {'.'.join(str(part) for part in task_number)} "
                    "is not physically nested under its numbered section"
                )
        for subtask in subtask_matches:
            subtask_number = tuple(
                int(part) for part in subtask.group("number").split(".")
            )
            subtask_indent = len(subtask.group(0)) - len(
                subtask.group(0).lstrip(" \t")
            )
            preceding_tasks = [
                entry for entry in task_entries if entry[0] < subtask.start()
            ]
            active_task = preceding_tasks[-1] if preceding_tasks else None
            preceding_sections = [
                entry for entry in section_entries if entry[0] < subtask.start()
            ]
            active_section = preceding_sections[-1] if preceding_sections else None
            if (
                active_task is None
                or active_section is None
                or active_task[0] < active_section[0]
                or active_task[1] != subtask_number[:3]
                or subtask_indent <= active_task[2]
            ):
                errors.append(
                    f"{shown}: subtask "
                    f"{'.'.join(str(part) for part in subtask_number)} is not "
                    "physically nested under its numbered task"
                )
        section_states = {
            (int(section.group("phase")), int(section.group("section"))):
            section.group("state").casefold() == "x"
            for section in sections
        }
        for section_number in sorted(section_states):
            task_ordinals = sorted(
                number[2]
                for number in task_numbers.values()
                if number[:2] == section_number
            )
            if task_ordinals and task_ordinals != list(
                range(1, max(task_ordinals) + 1)
            ):
                errors.append(
                    f"{shown}: task numbers for section {section_number[0]}."
                    f"{section_number[1]} must be unique and contiguous from 1; "
                    f"found {task_ordinals!r}"
                )
        for task_number in sorted(task_number_set):
            child_numbers = sorted(
                number[3]
                for number in subtask_states
                if number[:3] == task_number
            )
            if child_numbers and child_numbers != list(
                range(1, max(child_numbers) + 1)
            ):
                errors.append(
                    f"{shown}: subtask numbers for task "
                    f"{'.'.join(str(part) for part in task_number)} must be "
                    f"unique and contiguous from 1; found {child_numbers!r}"
                )

        for task_id in sorted(checked_tasks):
            number = task_numbers[task_id]
            unchecked = sorted(
                subtask_number
                for subtask_number, is_checked in subtask_states.items()
                if subtask_number[:3] == number and not is_checked
            )
            if unchecked:
                errors.append(
                    f"{shown}: checked task {task_id!r} has unchecked descendant "
                    f"subtasks: {unchecked!r}"
                )

        for section_number, is_checked in sorted(section_states.items()):
            if not is_checked:
                continue
            descendant_tasks = sorted(
                task_id
                for task_id, number in task_numbers.items()
                if number[:2] == section_number
            )
            unchecked_tasks = [
                task_id for task_id in descendant_tasks if task_id not in checked_tasks
            ]
            unchecked_subtasks = sorted(
                number
                for number, subtask_checked in subtask_states.items()
                if number[:2] == section_number and not subtask_checked
            )
            if not descendant_tasks:
                errors.append(
                    f"{shown}: checked section {section_number[0]}."
                    f"{section_number[1]} has no descendant tasks"
                )
            if unchecked_tasks or unchecked_subtasks:
                errors.append(
                    f"{shown}: checked section {section_number[0]}."
                    f"{section_number[1]} has unchecked descendants; "
                    f"tasks={unchecked_tasks!r}, subtasks={unchecked_subtasks!r}"
                )

        if (
            len(phase_labels) == 1
            and phase_labels[0].group("state").casefold() == "x"
        ):
            unchecked_sections = sorted(
                number for number, is_checked in section_states.items() if not is_checked
            )
            unchecked_tasks = sorted(set(tasks) - checked_tasks)
            unchecked_subtasks = sorted(
                number
                for number, is_checked in subtask_states.items()
                if not is_checked
            )
            if unchecked_sections or unchecked_tasks or unchecked_subtasks:
                errors.append(
                    f"{shown}: checked phase {int(phase_number)} has unchecked "
                    f"descendants; sections={unchecked_sections!r}, "
                    f"tasks={unchecked_tasks!r}, subtasks={unchecked_subtasks!r}"
                )
        expected_title = f"Phase {int(phase_number)} Integration Tests"
        if (
            not sections
            or sections[-1].group("title").rstrip(".") != expected_title
        ):
            errors.append(f"{shown}: final section must be {expected_title!r}")
        elif any(
            int(section.group("phase")) != int(phase_number)
            for section in sections
        ):
            errors.append(f"{shown}: section numbering does not match phase number")
        else:
            integration = sections[-1]
            integration_number = int(integration.group("section"))
            appended = [
                task_id
                for task_id, number in task_numbers.items()
                if task_positions[task_id] > integration.start()
                and number[1] != integration_number
            ]
            if appended:
                errors.append(
                    f"{shown}: work appears after the final integration section: "
                    f"{sorted(appended)!r}"
                )

    relations = tuple(
        {
            "subject": relation["subject"],
            "predicate": relation["predicate"],
            "object": relation["object"],
        }
        for relation in value["relations"]
    )
    _validate_document_shape(
        path, document_id, entities, relations, shown, errors
    )
    gates = _gate_ids(structural_body, shown, errors)
    owning_plan = next(
        (
            relation["object"]
            for relation in relations
            if relation["subject"] == document_id
            and relation["predicate"] == "belongs_to"
            and relation["object"].endswith(".plan")
        ),
        None,
    )
    task_plan_ids = (
        {task_id: owning_plan for task_id in tasks}
        if owning_plan is not None
        else {}
    )
    milestone_plan = f"{document_id}.plan"
    gate_plan_ids = (
        {gate_id: milestone_plan for gate_id in gates}
        if milestone_plan in entities
        else {}
    )
    return PlanningDocument(
        path,
        document_id,
        entities,
        relations,
        tasks,
        task_areas,
        frozenset(checked_tasks),
        task_numbers,
        gates,
        task_plan_ids,
        gate_plan_ids,
    )


def _cycle_nodes(edges: dict[str, set[str]]) -> list[str]:
    """Return cycle members using an iterative depth-first traversal."""

    nodes = set(edges)
    for targets in edges.values():
        nodes.update(targets)
    state: dict[str, int] = {node: 0 for node in nodes}
    cycle: set[str] = set()
    for start in sorted(nodes):
        if state[start] != 0:
            continue
        state[start] = 1
        path = [start]
        positions = {start: 0}
        stack: list[tuple[str, Iterator[str]]] = [
            (start, iter(sorted(edges.get(start, set()))))
        ]
        while stack:
            node, targets = stack[-1]
            try:
                target = next(targets)
            except StopIteration:
                stack.pop()
                state[node] = 2
                positions.pop(node, None)
                path.pop()
                continue
            target_state = state.get(target, 0)
            if target_state == 0:
                state[target] = 1
                positions[target] = len(path)
                path.append(target)
                stack.append(
                    (target, iter(sorted(edges.get(target, set()))))
                )
            elif target_state == 1:
                cycle.update(path[positions[target] :])
    return sorted(cycle)


def validate_planning_graph(
    documents: list[PlanningDocument],
    errors: list[str],
    *,
    display_path: Callable[[Path], str] | None = None,
) -> PlanningAuthority:
    """Validate identities/dependencies and return the evidence authority."""

    entities: dict[str, Path] = {}
    tasks: dict[str, Path] = {}
    gates: dict[str, Path] = {}
    task_plan_ids: dict[str, str] = {}
    gate_plan_ids: dict[str, str] = {}
    precedence: defaultdict[str, set[str]] = defaultdict(set)
    task_dependencies: defaultdict[str, set[str]] = defaultdict(set)
    phase_sequences: defaultdict[Path, list[int]] = defaultdict(list)

    for document in documents:
        shown = _display(document.path, display_path)
        phase_match = PHASE_FILENAME.fullmatch(document.path.name)
        if (
            phase_match is not None
            and STREAM_DIRECTORY.fullmatch(document.path.parent.parent.name)
        ):
            phase_sequences[document.path.parent].append(
                int(phase_match.group("number"))
            )
        for entity_id in document.entities:
            previous = entities.get(entity_id)
            if previous is not None:
                errors.append(
                    f"{shown}: planning-meta entity id {entity_id!r} is already "
                    f"authoritative in {_display(previous, display_path)}"
                )
            else:
                entities[entity_id] = document.path
        for task_id in document.tasks:
            previous = tasks.get(task_id)
            if previous is not None:
                errors.append(
                    f"{shown}: planning task id {task_id!r} is already "
                    f"authoritative in {_display(previous, display_path)}"
                )
            else:
                tasks[task_id] = document.path
            plan_id = document.task_plan_ids.get(task_id)
            if plan_id is None:
                errors.append(
                    f"{shown}: planning task {task_id!r} has no authoritative owning plan"
                )
            else:
                task_plan_ids[task_id] = plan_id
        for gate_id in document.gates:
            previous = gates.get(gate_id)
            if previous is not None:
                errors.append(
                    f"{shown}: planning gate id {gate_id!r} is already "
                    f"authoritative in {_display(previous, display_path)}"
                )
            else:
                gates[gate_id] = document.path
            plan_id = document.gate_plan_ids.get(gate_id)
            if plan_id is None:
                errors.append(
                    f"{shown}: planning gate {gate_id!r} has no authoritative owning plan"
                )
            else:
                gate_plan_ids[gate_id] = plan_id

    structural = {"belongs_to", "contains", "precedes"}
    for document in documents:
        shown = _display(document.path, display_path)
        for relation in document.relations:
            subject = relation["subject"]
            target = relation["object"]
            predicate = relation["predicate"]
            if subject not in entities:
                errors.append(
                    f"{shown}: planning relation subject {subject!r} is unresolved"
                )
            if predicate in structural and target not in entities:
                errors.append(
                    f"{shown}: planning relation target {target!r} is unresolved"
                )
            if (
                predicate == "implements"
                and target.startswith("planning.")
                and target not in entities
            ):
                errors.append(
                    f"{shown}: planning relation target {target!r} is unresolved"
                )
            if predicate == "precedes":
                precedence[subject].add(target)

        for task_id, dependencies in document.tasks.items():
            for dependency in dependencies:
                if dependency not in tasks:
                    errors.append(
                        f"{shown}: planning task {task_id!r} has unresolved "
                        f"dependency {dependency!r}"
                    )
                task_dependencies[task_id].add(dependency)

    entity_cycle = _cycle_nodes(precedence)
    if entity_cycle:
        errors.append(f"planning precedence cycle: {entity_cycle!r}")
    task_cycle = _cycle_nodes(task_dependencies)
    if task_cycle:
        errors.append(f"planning task dependency cycle: {task_cycle!r}")
    for milestone, numbers in sorted(
        phase_sequences.items(), key=lambda item: item[0].as_posix()
    ):
        expected = list(range(1, max(numbers) + 1))
        if sorted(numbers) != expected:
            errors.append(
                f"{_display(milestone, display_path)}: phase filenames must be "
                f"unique and contiguous from 01; found {sorted(numbers)!r}"
            )
    return PlanningAuthority(
        frozenset(entities),
        frozenset(tasks),
        frozenset(gates),
        task_plan_ids,
        gate_plan_ids,
    )


def validate_checked_tasks(
    documents: list[PlanningDocument],
    passed_task_ids: frozenset[str] | set[str],
    errors: list[str],
    *,
    display_path: Callable[[Path], str] | None = None,
) -> None:
    """Reject prospective checkmarks unless a validated pass record binds them."""

    for document in documents:
        missing = document.checked_tasks - set(passed_task_ids)
        for task_id in sorted(missing):
            errors.append(
                f"{_display(document.path, display_path)}: checked planning task "
                f"{task_id!r} has no validated pass evidence"
            )


def _usable_root(root: Path) -> Path | None:
    """Resolve a directory root while rejecting a symlink at the boundary."""

    try:
        if root.is_symlink() or not root.is_dir():
            return None
        return root.resolve(strict=True)
    except OSError:
        return None


def safe_fixture_path(root: Path, raw: str) -> Path | None:
    """Resolve one member without accepting symlink roots or escaping paths."""

    resolved_root = _usable_root(root)
    candidate = Path(raw)
    if (
        resolved_root is None
        or not raw
        or candidate.is_absolute()
        or ".." in candidate.parts
    ):
        return None
    lexical = root / candidate
    current = lexical
    while current != root and current != current.parent:
        if current.is_symlink():
            return None
        current = current.parent
    try:
        resolved = lexical.resolve(strict=False)
        resolved.relative_to(resolved_root)
    except (OSError, ValueError):
        return None
    return resolved


def sha256_file(path: Path) -> str:
    """Return a file digest without reading the complete file into memory."""

    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(HASH_CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_bounded_json(path: Path, maximum_bytes: int) -> object:
    """Read JSON only after applying a regular-file and byte-count bound."""

    if path.is_symlink() or not path.is_file():
        raise ValueError(f"expected a regular JSON file: {path}")
    if path.stat().st_size > maximum_bytes:
        raise ValueError(f"JSON file exceeds {maximum_bytes} bytes: {path}")
    def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        value: dict[str, object] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON key {key!r}")
            value[key] = item
        return value

    with path.open("r", encoding="utf-8") as source:
        return json.load(source, object_pairs_hook=unique_object)


def load_unique_yaml(text: str) -> object:
    """Load inert YAML with timestamp preservation and duplicate-key rejection."""

    return yaml.load(text, Loader=StringDateLoader)


def _verified_reference(
    repository_root: Path,
    entry: dict[str, object],
    errors: list[str],
    seen: set[Path],
    total: list[int],
    digest_cache: dict[Path, str],
    *,
    maximum_file_bytes: int,
    maximum_aggregate_bytes: int,
) -> Path | None:
    target = safe_fixture_path(repository_root, str(entry.get("path", "")))
    if target is None:
        errors.append("evidence_path_escape")
        return None
    if not entry.get("available"):
        return target
    if target.is_symlink() or not target.is_file():
        errors.append("evidence_artifact_missing")
        return None
    size = target.stat().st_size
    if size > maximum_file_bytes:
        errors.append("evidence_file_size_limit_exceeded")
        return None
    if target not in seen:
        seen.add(target)
        total[0] += size
        if total[0] > maximum_aggregate_bytes:
            errors.append("evidence_aggregate_size_limit_exceeded")
            return None
    digest = entry.get("sha256")
    byte_count = entry.get("bytes")
    if not isinstance(digest, str) or not SHA256.fullmatch(digest):
        errors.append("evidence_digest_missing")
    else:
        actual_digest = digest_cache.get(target)
        if actual_digest is None:
            actual_digest = sha256_file(target)
            digest_cache[target] = actual_digest
        if actual_digest != digest:
            errors.append("evidence_digest_mismatch")
    if not isinstance(byte_count, int):
        errors.append("evidence_size_missing")
    elif size != byte_count:
        errors.append("evidence_size_mismatch")
    return target


def _contract_expectations(
    contract: object, errors: list[str]
) -> dict[str, object] | None:
    if not isinstance(contract, dict) or not isinstance(contract.get("expected"), dict):
        errors.append("evidence_contract_invalid")
        return None
    expected = contract["expected"]
    if expected.get("evidence_kind") not in {
        "contract_research",
        "native_c",
        "emscripten_wasm",
        "browser_runtime",
    }:
        errors.append("evidence_contract_invalid")
        return None
    return expected


def validate_evidence_semantics(
    value: dict[str, object],
    repository_root: Path,
    authority: PlanningAuthority,
    *,
    maximum_file_bytes: int = MAX_EVIDENCE_REFERENCE_BYTES,
    maximum_aggregate_bytes: int = MAX_EVIDENCE_AGGREGATE_BYTES,
    _reference_seen: set[Path] | None = None,
    _reference_total: list[int] | None = None,
    _digest_cache: dict[Path, str] | None = None,
) -> list[str]:
    """Check evidence semantics using only the digest-bound referenced contract."""

    errors: list[str] = []
    candidate = value.get("candidate")
    execution = value.get("execution")
    baseline = value.get("plan_baseline")
    if (
        not isinstance(candidate, dict)
        or not isinstance(execution, dict)
        or not isinstance(baseline, dict)
    ):
        return ["evidence_structure_invalid"]
    if candidate.get("revision") != execution.get("tested_revision"):
        errors.append("fixture_revision_mismatch")
    if (
        candidate.get("dirty_state") == "dirty"
        and not candidate.get("diff_sha256")
    ):
        errors.append("dirty_state_digest_missing")
    if (
        candidate.get("dirty_state") == "clean"
        and candidate.get("diff_sha256") is not None
    ):
        errors.append("clean_state_has_diff_digest")

    task_ids = baseline.get("task_ids", [])
    gate_ids = baseline.get("gate_ids", [])
    if baseline.get("document_id") not in authority.entity_ids:
        errors.append("unresolved_plan_document")
    if not task_ids:
        errors.append("evidence_requires_task_ids")
    if not gate_ids:
        errors.append("evidence_requires_gate_ids")
    if isinstance(task_ids, list) and set(task_ids) - authority.task_ids:
        errors.append("unresolved_planning_task")
    if isinstance(gate_ids, list) and set(gate_ids) - authority.gate_ids:
        errors.append("unresolved_planning_gate")
    if isinstance(task_ids, list) and any(
        authority.task_plan_ids.get(task_id) != baseline.get("document_id")
        for task_id in task_ids
        if task_id in authority.task_ids
    ):
        errors.append("planning_task_plan_mismatch")
    if isinstance(gate_ids, list) and any(
        authority.gate_plan_ids.get(gate_id) != baseline.get("document_id")
        for gate_id in gate_ids
        if gate_id in authority.gate_ids
    ):
        errors.append("planning_gate_plan_mismatch")

    record_id = value.get("record_id")
    support_refs = value.get("support_refs", [])
    if isinstance(support_refs, list) and record_id in support_refs:
        errors.append("circular_evidence_support")

    seen = _reference_seen if _reference_seen is not None else set()
    total = _reference_total if _reference_total is not None else [0]
    digest_cache = _digest_cache if _digest_cache is not None else {}
    source_paths: set[Path] = set()
    applicable_artifacts: dict[str, dict[str, object]] = {}
    artifact_paths: dict[str, Path] = {}
    evidence_ids: list[str] = []
    for category in ("sources", "artifacts"):
        entries = value.get(category, [])
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            target = _verified_reference(
                repository_root,
                entry,
                errors,
                seen,
                total,
                digest_cache,
                maximum_file_bytes=maximum_file_bytes,
                maximum_aggregate_bytes=maximum_aggregate_bytes,
            )
            entry_id = entry.get("id")
            if isinstance(entry_id, str):
                evidence_ids.append(entry_id)
            if target is not None and category == "sources":
                source_paths.add(target)
            if (
                target is not None
                and category == "artifacts"
                and entry.get("applicability") == "applicable"
            ):
                if isinstance(entry_id, str):
                    applicable_artifacts[entry_id] = entry
                    artifact_paths[entry_id] = target
            if not entry.get("available") and (
                entry.get("sha256") is not None or entry.get("bytes") is not None
            ):
                errors.append("unavailable_evidence_has_result")
            if entry.get("applicability") == "not_applicable" and (
                entry.get("available")
                or entry.get("sha256") is not None
                or entry.get("bytes") is not None
            ):
                errors.append("non_applicable_evidence_has_result")
    if len(evidence_ids) != len(set(evidence_ids)):
        errors.append("duplicate_evidence_file_id")

    contract_ref = value.get("contract_ref")
    expected: dict[str, object] | None = None
    if not isinstance(contract_ref, dict):
        errors.append("evidence_contract_invalid")
    else:
        contract_path = safe_fixture_path(
            repository_root, str(contract_ref.get("path", ""))
        )
        if contract_path is None:
            errors.append("evidence_path_escape")
        elif contract_path.is_symlink() or not contract_path.is_file():
            errors.append("evidence_contract_missing")
        else:
            size = contract_path.stat().st_size
            if size > maximum_file_bytes:
                errors.append("evidence_file_size_limit_exceeded")
            elif contract_path not in seen and total[0] + size > maximum_aggregate_bytes:
                errors.append("evidence_aggregate_size_limit_exceeded")
            else:
                actual_digest = digest_cache.get(contract_path)
                if actual_digest is None:
                    actual_digest = sha256_file(contract_path)
                    digest_cache[contract_path] = actual_digest
                if actual_digest != contract_ref.get("sha256"):
                    errors.append("evidence_contract_digest_mismatch")
                else:
                    if contract_path not in seen:
                        seen.add(contract_path)
                        total[0] += size
                    try:
                        expected = _contract_expectations(
                            read_bounded_json(contract_path, maximum_file_bytes), errors
                        )
                    except (OSError, ValueError, json.JSONDecodeError):
                        errors.append("evidence_contract_invalid")

    outcome = value.get("outcome")
    status = execution.get("status")
    required_status = {
        "pass": "completed",
        "fail": "completed",
        "blocked": "blocked",
        "not_run": "not_run",
    }.get(str(outcome))
    if required_status is not None and status != required_status:
        errors.append(f"{outcome}_status_mismatch")

    commands = execution.get("commands", [])
    if not isinstance(commands, list) or not commands:
        errors.append("evidence_requires_commands")
        commands = []
    if status == "completed":
        for command in commands:
            if not isinstance(command, dict) or any(
                command.get(field) is None
                for field in ("exit_code", "stdout_sha256", "stderr_sha256")
            ):
                errors.append("completed_command_result_missing")
    if status == "not_run":
        for command in commands:
            if isinstance(command, dict) and any(
                command.get(field) is not None
                for field in ("exit_code", "stdout_sha256", "stderr_sha256")
            ):
                errors.append("not_run_command_has_result")
            if isinstance(command, dict) and command.get("result_artifact_ids"):
                errors.append("not_run_command_has_artifact_result")
        if value.get("observations") is not None:
            errors.append("not_run_has_observations")
        if value.get("observation_artifact_ids"):
            errors.append("not_run_has_observation_artifact")
        artifacts = value.get("artifacts", [])
        if isinstance(artifacts, list) and any(
            isinstance(artifact, dict) and artifact.get("available")
            for artifact in artifacts
        ):
            errors.append("not_run_has_available_artifact")

    if outcome == "pass":
        if value.get("synthetic") is not False:
            errors.append("synthetic_pass_forbidden")
        if value.get("reviewer") is None:
            errors.append("pass_requires_independent_reviewer")
        elif value.get("reviewer") == value.get("producer"):
            errors.append("reviewer_must_differ_from_producer")
        for command in commands:
            if (
                isinstance(command, dict)
                and isinstance(command.get("exit_code"), int)
                and command.get("exit_code") != 0
            ):
                errors.append("nonzero_command_marked_pass")
        if not value.get("toolchains"):
            errors.append("pass_requires_toolchain_identity")
        applicable = list(applicable_artifacts.values())
        if not applicable:
            errors.append("pass_requires_applicable_artifact")
        elif any(not artifact.get("available") for artifact in applicable):
            errors.append("pass_requires_available_artifacts")
        available_artifact_ids = {
            artifact_id
            for artifact_id, artifact in applicable_artifacts.items()
            if artifact.get("available")
        }
        if any(path in source_paths for path in artifact_paths.values()):
            errors.append("pass_artifact_must_not_alias_source")
        if any(
            not isinstance(artifact.get("bytes"), int) or artifact.get("bytes", 0) <= 0
            for artifact in applicable
            if artifact.get("available")
        ):
            errors.append("pass_artifact_must_be_nonempty")
        for command in commands:
            result_ids = (
                command.get("result_artifact_ids", [])
                if isinstance(command, dict)
                else []
            )
            if not result_ids:
                errors.append("pass_command_requires_result_artifact")
            elif set(result_ids) - available_artifact_ids:
                errors.append("command_result_artifact_unresolved")
        observation_artifact_ids = value.get("observation_artifact_ids", [])
        if not observation_artifact_ids:
            errors.append("pass_observation_requires_artifact")
        elif set(observation_artifact_ids) - available_artifact_ids:
            errors.append("observation_artifact_unresolved")
        observations = value.get("observations")
        if observations is None:
            errors.append("pass_requires_observations")
        elif expected is not None and isinstance(observations, dict):
            kind = value.get("evidence_kind")
            if expected.get("evidence_kind") != kind or observations.get("kind") != kind:
                errors.append("evidence_kind_contract_mismatch")
            elif kind == "contract_research":
                expected_criteria = expected.get("criteria")
                actual_criteria = observations.get("criteria")
                if not isinstance(expected_criteria, list) or not isinstance(
                    actual_criteria, list
                ):
                    errors.append("evidence_contract_invalid")
                else:
                    expected_ids = {
                        item.get("id") for item in expected_criteria if isinstance(item, dict)
                    }
                    actual_ids = {
                        item.get("id") for item in actual_criteria if isinstance(item, dict)
                    }
                    if expected_ids != actual_ids:
                        errors.append("research_criteria_mismatch")
                    if any(
                        not isinstance(item, dict) or item.get("outcome") != "pass"
                        for item in actual_criteria
                    ):
                        errors.append("research_criterion_not_passed")
                    criterion_artifacts = {
                        artifact_id
                        for item in actual_criteria
                        if isinstance(item, dict)
                        for artifact_id in item.get("artifact_ids", [])
                    }
                    if not criterion_artifacts or (
                        criterion_artifacts - available_artifact_ids
                    ):
                        errors.append("research_criterion_artifact_unresolved")
            elif kind in {"native_c", "emscripten_wasm"}:
                if observations.get("target_triple") != expected.get("target_triple"):
                    errors.append(
                        "wasm_target_mismatch"
                        if kind == "emscripten_wasm"
                        else "native_target_mismatch"
                    )
                if observations.get("c_standard") != expected.get("c_standard"):
                    errors.append("c_standard_mismatch")
                if observations.get("pointer_bits") != expected.get("pointer_bits"):
                    errors.append("abi_width_mismatch")
                if kind == "emscripten_wasm":
                    raw_expected_imports = expected.get("logical_host_imports")
                    raw_expected_exports = expected.get("logical_c_exports")
                    if not isinstance(raw_expected_imports, list) or not isinstance(
                        raw_expected_exports, list
                    ):
                        errors.append("evidence_contract_invalid")
                    else:
                        expected_imports = set(raw_expected_imports)
                        actual_imports = set(
                            observations.get("logical_host_imports", [])
                        )
                        if actual_imports - expected_imports:
                            errors.append("unexpected_wasm_import")
                        if expected_imports - actual_imports:
                            errors.append("missing_wasm_import")
                        expected_exports = set(raw_expected_exports)
                        actual_exports = set(
                            observations.get("logical_c_exports", [])
                        )
                        if actual_exports - expected_exports:
                            errors.append("unexpected_wasm_export")
                        if expected_exports - actual_exports:
                            errors.append("missing_wasm_export")
                    memory = observations.get("memory")
                    expected_memory = expected.get("memory")
                    if not isinstance(memory, dict) or not isinstance(
                        expected_memory, dict
                    ):
                        errors.append("evidence_contract_invalid")
                    else:
                        if memory.get("shared") != expected_memory.get("shared"):
                            errors.append("shared_memory_contract_mismatch")
                        if expected_memory.get("initial_equals_maximum") is True and (
                            memory.get("initial_bytes")
                            != memory.get("maximum_bytes")
                        ):
                            errors.append("fixed_memory_contract_mismatch")
            elif kind == "browser_runtime":
                expected_browsers = expected.get("browsers")
                actual_browsers = observations.get("browsers")
                if not isinstance(expected_browsers, list) or not isinstance(
                    actual_browsers, list
                ):
                    errors.append("evidence_contract_invalid")
                else:
                    expected_identities = {
                        (item.get("name"), item.get("version"))
                        for item in expected_browsers
                        if isinstance(item, dict)
                    }
                    actual_identities = {
                        (item.get("name"), item.get("version"))
                        for item in actual_browsers
                        if isinstance(item, dict)
                    }
                    if expected_identities != actual_identities:
                        errors.append("browser_matrix_mismatch")
                    if any(
                        not isinstance(item, dict) or item.get("outcome") != "pass"
                        for item in actual_browsers
                    ):
                        errors.append("browser_result_not_passed")
                for key in ("worker_topology", "cross_origin_isolated"):
                    if observations.get(key) != expected.get(key):
                        errors.append("browser_runtime_contract_mismatch")
                minimum_cycles = expected.get("minimum_boot_dispose_cycles")
                if not isinstance(minimum_cycles, int) or (
                    observations.get("boot_dispose_cycles", 0) < minimum_cycles
                ):
                    errors.append("browser_cycle_count_mismatch")
                if observations.get("leaked_resources") != 0:
                    errors.append("browser_resource_leak")
    return sorted(set(errors))


def validate_evidence_records(
    research_root: Path,
    repository_root: Path,
    validator: jsonschema.Draft202012Validator,
    authority: PlanningAuthority,
    errors: list[str],
    *,
    display_path: Callable[[Path], str] | None = None,
    maximum_record_bytes: int = MAX_EVIDENCE_RECORD_BYTES,
    maximum_aggregate_bytes: int = MAX_EVIDENCE_AGGREGATE_BYTES,
) -> EvidenceValidationResult:
    """Discover and validate real evidence records in one bounded directory."""

    evidence_root = research_root / REAL_EVIDENCE_ROOT
    resolved_repository = _usable_root(repository_root)
    resolved_root = _usable_root(evidence_root)
    if resolved_repository is None or resolved_root is None:
        errors.append(
            f"{_display(evidence_root, display_path)}: "
            "evidence discovery root is missing or symlinked"
        )
        return EvidenceValidationResult(frozenset(), frozenset())
    try:
        resolved_root.relative_to(resolved_repository)
    except ValueError:
        errors.append(
            f"{_display(evidence_root, display_path)}: "
            "evidence discovery root escapes repository root"
        )
        return EvidenceValidationResult(frozenset(), frozenset())

    files: list[Path] = []
    aggregate = 0
    synthetic_root = (research_root / SYNTHETIC_FIXTURE_DIRECTORY).resolve()
    candidates: list[Path] = []
    for candidate in evidence_root.rglob("*.planning-evidence.json"):
        if len(candidates) >= MAX_EVIDENCE_RECORDS:
            errors.append(
                f"{_display(evidence_root, display_path)}: evidence candidate "
                f"count exceeds hard limit {MAX_EVIDENCE_RECORDS}"
            )
            break
        candidates.append(candidate)
    candidates.sort(key=lambda item: item.as_posix())
    for child in candidates:
        try:
            child.resolve(strict=False).relative_to(synthetic_root)
        except ValueError:
            pass
        else:
            errors.append(
                f"{_display(child, display_path)}: synthetic conformance fixtures "
                "cannot be discovered as real evidence"
            )
            continue
        relative_member = child.relative_to(evidence_root).as_posix()
        bounded_child = safe_fixture_path(evidence_root, relative_member)
        if (
            bounded_child is None
            or child.is_symlink()
            or not child.is_file()
            or not EVIDENCE_FILENAME.fullmatch(child.name)
        ):
            errors.append(
                f"{_display(child, display_path)}: evidence record must be a "
                "regular, non-symlinked file beneath research/assets"
            )
            continue
        size = child.stat().st_size
        if size > maximum_record_bytes:
            errors.append(
                f"{_display(child, display_path)}: "
                "evidence record exceeds per-file byte limit"
            )
            continue
        aggregate += size
        if aggregate > maximum_aggregate_bytes:
            errors.append(
                f"{_display(child, display_path)}: "
                "evidence records exceed aggregate byte limit"
            )
            continue
        files.append(child)

    records: dict[str, tuple[Path, dict[str, object], bool]] = {}
    reference_seen: set[Path] = set()
    reference_total = [0]
    digest_cache: dict[Path, str] = {}
    for path in files:
        shown = _display(path, display_path)
        try:
            value = read_bounded_json(path, maximum_record_bytes)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"{shown}: invalid evidence JSON: {error}")
            continue
        schema_errors = list(validator.iter_errors(value))
        for schema_error in sorted(
            schema_errors, key=lambda item: list(item.absolute_path)
        ):
            location = ".".join(str(part) for part in schema_error.absolute_path)
            errors.append(
                f"{shown}: evidence {location or '<root>'}: {schema_error.message}"
            )
        if schema_errors or not isinstance(value, dict):
            continue
        record_id = str(value["record_id"])
        if record_id in records:
            errors.append(f"{shown}: duplicate evidence record_id {record_id!r}")
            continue
        semantic_errors = validate_evidence_semantics(
            value,
            repository_root,
            authority,
            maximum_aggregate_bytes=maximum_aggregate_bytes,
            _reference_seen=reference_seen,
            _reference_total=reference_total,
            _digest_cache=digest_cache,
        )
        for code in semantic_errors:
            errors.append(f"{shown}: evidence semantic error: {code}")
        records[record_id] = (path, value, not semantic_errors)

    support_edges: defaultdict[str, set[str]] = defaultdict(set)
    invalid_support: set[str] = set()
    for record_id, (path, value, _valid) in records.items():
        for support_ref in value["support_refs"]:
            if support_ref not in records:
                errors.append(
                    f"{_display(path, display_path)}: unresolved evidence "
                    f"support reference {support_ref!r}"
                )
                invalid_support.add(record_id)
            support_edges[record_id].add(support_ref)
    support_cycle = _cycle_nodes(support_edges)
    if support_cycle:
        errors.append(f"evidence support cycle: {support_cycle!r}")
        invalid_support.update(support_cycle)

    invalid_records = {
        record_id for record_id, (_path, _value, valid) in records.items() if not valid
    }
    invalid_records.update(invalid_support)
    for record_id, (_path, value, _valid) in records.items():
        if value["outcome"] == "pass" and any(
            target in records and records[target][1]["outcome"] != "pass"
            for target in support_edges.get(record_id, set())
        ):
            errors.append(
                f"{_display(records[record_id][0], display_path)}: pass evidence "
                "cannot rely on failed, blocked, or not-run support"
            )
            invalid_records.add(record_id)
    changed = True
    while changed:
        changed = False
        for record_id, targets in support_edges.items():
            if record_id not in invalid_records and targets & invalid_records:
                invalid_records.add(record_id)
                changed = True

    passed_tasks: set[str] = set()
    for record_id, (_path, value, valid) in records.items():
        if valid and record_id not in invalid_records and value["outcome"] == "pass":
            passed_tasks.update(value["plan_baseline"]["task_ids"])
    return EvidenceValidationResult(
        frozenset(records), frozenset(passed_tasks)
    )
