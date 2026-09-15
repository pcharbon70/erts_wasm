#!/usr/bin/env python3
"""Focused tests for planning authoring and bounded execution evidence."""

from __future__ import annotations

import copy
import contextlib
import hashlib
import io
import inspect
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import jsonschema
import yaml

import check_all
from planning_validation import (
    EvidenceValidationResult,
    PlanningAuthority,
    PlanningDocument,
    StringDateLoader,
    is_structured_planning_document,
    load_unique_yaml,
    read_bounded_json,
    safe_fixture_path,
    sha256_file,
    validate_checked_tasks,
    validate_evidence_records,
    validate_evidence_semantics,
    validate_planning_document,
    validate_planning_graph,
)
from research_paths import REPO_ROOT, RESEARCH_ROOT
from verify_planning_fixtures import main as verify_fixtures
from verify_planning_fixtures import resolve_fixture_member


EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def valid_phase_body() -> str:
    """Return one complete, small phase document body."""

    return """# Phase 1 — Example

```planning-meta
profile: planning.authoring.v1
document_id: planning.example.phase_01
entities:
  - id: planning.example.phase_01
    kind: phase
    source_anchor: '#phase-1-example'
relations:
  - subject: planning.example.phase_01
    predicate: belongs_to
    object: planning.example.plan
```

## Entry, scope, and dependencies

Synthetic entry conditions.

## Task identity, ownership, and dependencies

| Task ID | Area | Requires |
| --- | --- | --- |
| `p0-p01-build` | c-runtime | None |
| `p0-p01-integration` | cross-cutting | [p0-p01-build](phase-00.md) |

## Planned work

- [ ] 1 Phase — Example.

  - [ ] 1.1 Section — Build fixture.

    - [ ] 1.1.1 Task [id: p0-p01-build] [area: c-runtime] [after: none] — Build it.

      - [ ] 1.1.1.1 Subtask — Check widths.

  - [ ] 1.2 Section — Phase 1 Integration Tests.

    - [ ] 1.2.1 Task [id: p0-p01-integration] [area: cross-cutting] [after: p0-p01-build] — Verify it.

      - [ ] 1.2.1.1 Subtask — Retain evidence.
"""


def planning_authority() -> PlanningAuthority:
    return PlanningAuthority(
        frozenset(
            {
                "planning.synthetic.proof",
                "planning.synthetic.proof.p1",
                "planning.synthetic.proof.p1.plan",
                "planning.synthetic.proof.p1.phase_01",
            }
        ),
        frozenset({"p1-p01-c-abi-probe"}),
        frozenset({"P1-A01"}),
        {"p1-p01-c-abi-probe": "planning.synthetic.proof.p1.plan"},
        {"P1-A01": "planning.synthetic.proof.p1.plan"},
    )


def pass_evidence(
    evidence: dict[str, object], contract: dict[str, object]
) -> dict[str, object]:
    """Construct a schema-valid, in-memory pass candidate for negative tests."""

    value = copy.deepcopy(evidence)
    expected = contract["expected"]
    result_path = RESEARCH_ROOT / "assets/planning-conformance/synthetic-result-artifact.txt"
    result_id = "artifact.synthetic.validator_result"
    value["synthetic"] = False
    value["reviewer"] = "independent-test-reviewer"
    value["outcome"] = "pass"
    value["execution"]["status"] = "completed"
    for command in value["execution"]["commands"]:
        command["exit_code"] = 0
        command["stdout_sha256"] = EMPTY_SHA256
        command["stderr_sha256"] = EMPTY_SHA256
        command["result_artifact_ids"] = [result_id]
    value["toolchains"] = [
        {
            "name": "synthetic-test-tool",
            "executable": "/not-executed/emcc",
            "version": "synthetic",
            "target": "wasm32-unknown-emscripten",
            "compile_flags": ["-std=c11", "-pthread"],
            "link_flags": ["-pthread"],
        }
    ]
    value["artifacts"] = [
        {
            "id": result_id,
            "role": "synthetic nonempty validator result bytes",
            "applicability": "applicable",
            "path": "research/assets/planning-conformance/synthetic-result-artifact.txt",
            "available": True,
            "sha256": sha256_file(result_path),
            "bytes": result_path.stat().st_size,
        }
    ]
    value["observations"] = {
        "kind": "emscripten_wasm",
        "target_triple": expected["target_triple"],
        "c_standard": expected["c_standard"],
        "pointer_bits": expected["pointer_bits"],
        "logical_host_imports": expected["logical_host_imports"],
        "logical_c_exports": expected["logical_c_exports"],
        "memory": {
            "shared": True,
            "initial_bytes": 65536,
            "maximum_bytes": 65536,
        },
    }
    value["observation_artifact_ids"] = [result_id]
    return value


class PlanningAuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        schema = json.loads(
            (RESEARCH_ROOT / "70-tools/planning-authoring-v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        cls.validator = jsonschema.Draft202012Validator(schema)

    def validate_document(
        self, body: str, name: str = "phase-01-example.md", nested: bool = False
    ) -> tuple[PlanningDocument | None, list[str]]:
        path = Path("/fixture") / name
        if nested:
            path = Path("/fixture/01-proof/p0-example") / name
        errors: list[str] = []
        document = validate_planning_document(
            path, body, self.validator, errors, required=True
        )
        return document, errors

    def test_accepts_phase_and_full_table_projection(self) -> None:
        document, errors = self.validate_document(valid_phase_body())
        self.assertEqual([], errors)
        assert document is not None
        self.assertEqual(("p0-p01-build",), document.tasks["p0-p01-integration"])
        self.assertEqual("c-runtime", document.task_areas["p0-p01-build"])

    def test_rejects_table_area_and_requires_mismatch(self) -> None:
        area = valid_phase_body().replace(
            "| `p0-p01-build` | c-runtime |",
            "| `p0-p01-build` | browser-host |",
        )
        _document, errors = self.validate_document(area)
        self.assertIn("area disagrees", " ".join(errors))
        requires = valid_phase_body().replace(
            "[p0-p01-build](phase-00.md)", "none"
        )
        _document, errors = self.validate_document(requires)
        self.assertIn("dependencies disagree", " ".join(errors))

    def test_rejects_unsupported_area(self) -> None:
        body = valid_phase_body().replace("c-runtime", "metagraph-role")
        _document, errors = self.validate_document(body)
        self.assertIn("unsupported area", " ".join(errors))

    def test_accepts_documented_beam_fixtures_area(self) -> None:
        body = valid_phase_body().replace("c-runtime", "beam-fixtures")
        _document, errors = self.validate_document(body)
        self.assertEqual([], errors)

    def test_phase_template_uses_validator_area_header(self) -> None:
        template = (
            RESEARCH_ROOT / "templates/implementation-phase.md"
        ).read_text(encoding="utf-8")
        self.assertIn("| Task ID | Area |", template)
        self.assertIn("{task IDs or none; keep entry gates in the Entry section}", template)

    def test_rejects_empty_phase_tasks(self) -> None:
        body = valid_phase_body()
        body = body.replace(
            "| `p0-p01-build` | c-runtime | None |\n"
            "| `p0-p01-integration` | cross-cutting | [p0-p01-build](phase-00.md) |",
            "",
        )
        body = "\n".join(
            line
            for line in body.splitlines()
            if "Task [id:" not in line
        )
        _document, errors = self.validate_document(body)
        self.assertIn("phase must declare at least one task", " ".join(errors))

    def test_rejects_checked_task_without_pass_evidence(self) -> None:
        body = valid_phase_body().replace(
            "- [ ] 1.1.1 Task", "- [x] 1.1.1 Task"
        ).replace(
            "- [ ] 1.1.1.1 Subtask", "- [x] 1.1.1.1 Subtask"
        )
        document, errors = self.validate_document(body)
        self.assertEqual([], errors)
        assert document is not None
        checked_errors: list[str] = []
        validate_checked_tasks([document], frozenset(), checked_errors)
        self.assertIn("has no validated pass evidence", " ".join(checked_errors))
        checked_errors = []
        validate_checked_tasks(
            [document], frozenset({"p0-p01-build"}), checked_errors
        )
        self.assertEqual([], checked_errors)

    def test_accepts_checked_subtask_as_progress_without_evidence(self) -> None:
        body = valid_phase_body().replace(
            "- [ ] 1.1.1.1 Subtask", "- [x] 1.1.1.1 Subtask"
        )
        document, errors = self.validate_document(body)
        self.assertEqual([], errors)
        assert document is not None
        self.assertEqual(frozenset(), document.checked_tasks)
        checked_errors: list[str] = []
        validate_checked_tasks([document], frozenset(), checked_errors)
        self.assertEqual([], checked_errors)

    def test_checked_hierarchy_label_is_allowed_only_in_phase_document(self) -> None:
        body = valid_phase_body().replace(
            "- [ ] 1.1.1.1 Subtask", "- [x] 1.1.1.1 Subtask"
        )
        _document, errors = self.validate_document(body, name="README.md")
        self.assertIn(
            "not a recognized phase, section, task, or subtask",
            " ".join(errors),
        )

    def test_rejects_noncontiguous_subtask_numbers(self) -> None:
        body = valid_phase_body().replace(
            "1.1.1.1 Subtask", "1.1.1.2 Subtask"
        )
        _document, errors = self.validate_document(body)
        self.assertIn(
            "subtask numbers for task 1.1.1 must be unique and contiguous from 1",
            " ".join(errors),
        )

    def test_rejects_displaced_subtask_even_when_numbered_parent_exists(self) -> None:
        body = valid_phase_body().replace(
            "1.1.1.1 Subtask", "1.2.1.2 Subtask"
        )
        _document, errors = self.validate_document(body)
        self.assertIn(
            "subtask 1.2.1.2 is not physically nested under its numbered task",
            " ".join(errors),
        )

    def test_rejects_noncontiguous_task_ordinals_within_section(self) -> None:
        body = valid_phase_body().replace("1.1.1 Task", "1.1.2 Task").replace(
            "1.1.1.1 Subtask", "1.1.2.1 Subtask"
        )
        _document, errors = self.validate_document(body)
        self.assertIn(
            "task numbers for section 1.1 must be unique and contiguous from 1",
            " ".join(errors),
        )

    def test_checked_task_requires_complete_subtasks_and_pass_evidence(self) -> None:
        incomplete = valid_phase_body().replace(
            "- [ ] 1.1.1 Task", "- [x] 1.1.1 Task"
        )
        _document, errors = self.validate_document(incomplete)
        self.assertIn("checked task 'p0-p01-build' has unchecked", " ".join(errors))

        complete = incomplete.replace(
            "- [ ] 1.1.1.1 Subtask", "- [x] 1.1.1.1 Subtask"
        )
        document, errors = self.validate_document(complete)
        self.assertEqual([], errors)
        assert document is not None
        checked_errors: list[str] = []
        validate_checked_tasks([document], frozenset(), checked_errors)
        self.assertIn("has no validated pass evidence", " ".join(checked_errors))
        checked_errors = []
        validate_checked_tasks(
            [document], frozenset({"p0-p01-build"}), checked_errors
        )
        self.assertEqual([], checked_errors)

    def test_checked_section_requires_complete_descendants(self) -> None:
        incomplete = valid_phase_body().replace(
            "- [ ] 1.1 Section", "- [x] 1.1 Section"
        )
        _document, errors = self.validate_document(incomplete)
        self.assertIn("checked section 1.1 has unchecked descendants", " ".join(errors))

        complete = incomplete.replace(
            "- [ ] 1.1.1 Task", "- [x] 1.1.1 Task"
        ).replace(
            "- [ ] 1.1.1.1 Subtask", "- [x] 1.1.1.1 Subtask"
        )
        document, errors = self.validate_document(complete)
        self.assertEqual([], errors)
        assert document is not None
        checked_errors: list[str] = []
        validate_checked_tasks([document], frozenset(), checked_errors)
        self.assertIn("has no validated pass evidence", " ".join(checked_errors))
        checked_errors = []
        validate_checked_tasks(
            [document], frozenset({"p0-p01-build"}), checked_errors
        )
        self.assertEqual([], checked_errors)

    def test_rejects_vacuously_checked_empty_section(self) -> None:
        body = valid_phase_body().replace(
            "  - [ ] 1.2 Section — Phase 1 Integration Tests.",
            "  - [x] 1.2 Section — Empty.\n\n"
            "  - [ ] 1.3 Section — Phase 1 Integration Tests.",
        ).replace("1.2.1 Task", "1.3.1 Task").replace(
            "1.2.1.1 Subtask", "1.3.1.1 Subtask"
        )
        _document, errors = self.validate_document(body)
        self.assertIn("checked section 1.2 has no descendant tasks", " ".join(errors))

    def test_checked_phase_requires_complete_descendants_and_task_evidence(self) -> None:
        incomplete = valid_phase_body().replace(
            "- [ ] 1 Phase", "- [x] 1 Phase"
        )
        _document, errors = self.validate_document(incomplete)
        self.assertIn("checked phase 1 has unchecked descendants", " ".join(errors))

        complete = valid_phase_body().replace("- [ ]", "- [x]")
        document, errors = self.validate_document(complete)
        self.assertEqual([], errors)
        assert document is not None
        checked_errors: list[str] = []
        validate_checked_tasks(
            [document], frozenset({"p0-p01-build"}), checked_errors
        )
        self.assertIn("p0-p01-integration", " ".join(checked_errors))
        checked_errors = []
        validate_checked_tasks(
            [document],
            frozenset({"p0-p01-build", "p0-p01-integration"}),
            checked_errors,
        )
        self.assertEqual([], checked_errors)

    def test_new_unchecked_subtask_reopens_checked_ancestors(self) -> None:
        body = valid_phase_body().replace("- [ ]", "- [x]").replace(
            "      - [x] 1.1.1.1 Subtask — Check widths.",
            "      - [x] 1.1.1.1 Subtask — Check widths.\n\n"
            "      - [ ] 1.1.1.2 Subtask — Review the changed plan.",
        )
        _document, errors = self.validate_document(body)
        joined = " ".join(errors)
        self.assertIn("checked task 'p0-p01-build' has unchecked", joined)
        self.assertIn("checked section 1.1 has unchecked descendants", joined)
        self.assertIn("checked phase 1 has unchecked descendants", joined)

    def test_rejects_checked_nonhierarchy_checkbox(self) -> None:
        body = valid_phase_body() + "\n- [x] Unclassified planning claim.\n"
        _document, errors = self.validate_document(body)
        self.assertIn("not a recognized phase, section, task, or subtask", " ".join(errors))

    def test_rejects_malformed_phase_filename_in_milestone(self) -> None:
        _document, errors = self.validate_document(
            valid_phase_body(), "implementation.md", nested=True
        )
        self.assertIn("phase-NN-kebab-case.md", " ".join(errors))

    def test_rejects_work_appended_after_integration(self) -> None:
        body = valid_phase_body().replace(
            "| `p0-p01-integration` | cross-cutting | [p0-p01-build](phase-00.md) |",
            "| `p0-p01-integration` | cross-cutting | [p0-p01-build](phase-00.md) |\n"
            "| `p0-p01-late` | c-runtime | p0-p01-integration |",
        )
        body += (
            "\n    - [ ] 1.3.1 Task [id: p0-p01-late] [area: c-runtime] "
            "[after: p0-p01-integration] — Too late.\n"
        )
        _document, errors = self.validate_document(body)
        self.assertIn("work appears after", " ".join(errors))

    def test_fenced_syntax_cannot_spoof_tasks_or_headings(self) -> None:
        body = valid_phase_body() + """

```text
## Fake heading
- [x] 1.9.1 Task [id: fake-task] [area: c-runtime] [after: none] — Fake.
```
"""
        document, errors = self.validate_document(body)
        self.assertEqual([], errors)
        assert document is not None
        self.assertNotIn("fake-task", document.tasks)
        missing = valid_phase_body().replace(
            "# Phase 1 — Example", "# Other\n\n```text\n# Phase 1 — Example\n```"
        )
        _document, errors = self.validate_document(missing)
        self.assertIn("missing source anchor", " ".join(errors))

    def test_rejects_invalid_path_derived_document_shape(self) -> None:
        stream = """# Stream

```planning-meta
profile: planning.authoring.v1
document_id: planning.bad.stream
entities:
  - id: planning.bad.stream
    kind: milestone
    source_anchor: '#stream'
relations: []
```
"""
        _document, errors = self.validate_document(
            stream, "README.md"
        )
        # /fixture/README.md is not a stream; use explicit numbered parent.
        explicit_errors: list[str] = []
        validate_planning_document(
            Path("/fixture/01-bad/README.md"),
            stream,
            self.validator,
            explicit_errors,
            required=True,
        )
        self.assertIn("planning_stream", " ".join(explicit_errors))

    def test_iterative_cycle_detection_handles_long_graph(self) -> None:
        count = 3000
        entities = {
            f"planning.long.n_{index}": {"id": f"planning.long.n_{index}"}
            for index in range(count)
        }
        relations = tuple(
            {
                "subject": f"planning.long.n_{index}",
                "predicate": "precedes",
                "object": f"planning.long.n_{index + 1}",
            }
            for index in range(count - 1)
        )
        document = PlanningDocument(
            Path("long.md"), "planning.long.n_0", entities, relations, {}
        )
        errors: list[str] = []
        validate_planning_graph([document], errors)
        self.assertEqual([], errors)

    def test_rejects_relation_and_task_cycles(self) -> None:
        document = PlanningDocument(
            Path("cycle.md"),
            "planning.cycle.a",
            {
                "planning.cycle.a": {"id": "planning.cycle.a"},
                "planning.cycle.b": {"id": "planning.cycle.b"},
            },
            (
                {"subject": "planning.cycle.a", "predicate": "precedes", "object": "planning.cycle.b"},
                {"subject": "planning.cycle.b", "predicate": "precedes", "object": "planning.cycle.a"},
            ),
            {"task-a": ("task-b",), "task-b": ("task-a",)},
        )
        errors: list[str] = []
        validate_planning_graph([document], errors)
        joined = " ".join(errors)
        self.assertIn("precedence cycle", joined)
        self.assertIn("task dependency cycle", joined)

    def test_rejects_noncontiguous_phase_sequence(self) -> None:
        documents = [
            PlanningDocument(
                Path(f"/fixture/01-proof/p0/phase-{number:02d}-x.md"),
                f"planning.sequence.phase_{number:02d}",
                {
                    f"planning.sequence.phase_{number:02d}": {
                        "id": f"planning.sequence.phase_{number:02d}"
                    }
                },
                (),
                {},
            )
            for number in (1, 3)
        ]
        errors: list[str] = []
        validate_planning_graph(documents, errors)
        self.assertIn("contiguous from 01", " ".join(errors))

    def test_numbered_stream_paths_are_structured(self) -> None:
        path = RESEARCH_ROOT / "60-planning/01-proof-of-concept/p0/phase-01-x.md"
        self.assertTrue(is_structured_planning_document(path, RESEARCH_ROOT))
        self.assertFalse(
            is_structured_planning_document(
                RESEARCH_ROOT / "60-planning/legacy-plan.md", RESEARCH_ROOT
            )
        )


class PlanningEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture_root = RESEARCH_ROOT / "assets/planning-conformance"
        cls.contract = json.loads(
            (cls.fixture_root / "abi-contract.json").read_text(encoding="utf-8")
        )
        cls.evidence = json.loads(
            (cls.fixture_root / "synthetic-not-run-evidence.json").read_text(
                encoding="utf-8"
            )
        )
        schema = json.loads(
            (RESEARCH_ROOT / "70-tools/planning-evidence-v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        cls.validator = jsonschema.Draft202012Validator(schema)
        cls.authority = planning_authority()

    def semantics(self, value: dict[str, object], **kwargs: int) -> list[str]:
        return validate_evidence_semantics(
            value, REPO_ROOT, self.authority, **kwargs
        )

    def test_accepts_synthetic_not_run_evidence(self) -> None:
        self.assertEqual([], list(self.validator.iter_errors(self.evidence)))
        self.assertEqual([], self.semantics(self.evidence))

    def test_accepts_complete_non_synthetic_pass_candidate(self) -> None:
        value = pass_evidence(self.evidence, self.contract)
        self.assertEqual([], list(self.validator.iter_errors(value)))
        self.assertEqual([], self.semantics(value))

    def test_semantic_contract_is_loaded_only_from_contract_ref(self) -> None:
        parameters = inspect.signature(validate_evidence_semantics).parameters
        self.assertNotIn("contract", parameters)
        value = pass_evidence(self.evidence, self.contract)
        value["observations"]["target_triple"] = "wasm32-wasi"
        self.assertIn("wasm_target_mismatch", self.semantics(value))

    def test_rejects_tampered_contract_digest(self) -> None:
        value = copy.deepcopy(self.evidence)
        value["contract_ref"]["sha256"] = "0" * 64
        self.assertIn("evidence_contract_digest_mismatch", self.semantics(value))

    def test_rejects_synthetic_or_vacuous_pass(self) -> None:
        value = pass_evidence(self.evidence, self.contract)
        value["synthetic"] = True
        self.assertIn("synthetic_pass_forbidden", self.semantics(value))
        value = pass_evidence(self.evidence, self.contract)
        value["plan_baseline"]["task_ids"] = []
        value["plan_baseline"]["gate_ids"] = []
        value["execution"]["commands"] = []
        value["artifacts"] = []
        schema_errors = list(self.validator.iter_errors(value))
        self.assertGreaterEqual(len(schema_errors), 4)
        errors = self.semantics(value)
        for code in (
            "evidence_requires_task_ids",
            "evidence_requires_gate_ids",
            "evidence_requires_commands",
            "pass_requires_applicable_artifact",
        ):
            self.assertIn(code, errors)

    def test_rejects_unresolved_task_gate_and_document(self) -> None:
        value = copy.deepcopy(self.evidence)
        value["plan_baseline"]["document_id"] = "planning.missing.plan"
        value["plan_baseline"]["task_ids"] = ["missing-task"]
        value["plan_baseline"]["gate_ids"] = ["P9-MISSING"]
        errors = self.semantics(value)
        self.assertIn("unresolved_plan_document", errors)
        self.assertIn("unresolved_planning_task", errors)
        self.assertIn("unresolved_planning_gate", errors)

    def test_outcome_status_and_command_result_matrix(self) -> None:
        for outcome, status in (
            ("fail", "completed"),
            ("blocked", "blocked"),
            ("not_run", "not_run"),
        ):
            with self.subTest(outcome=outcome):
                value = copy.deepcopy(self.evidence)
                value["outcome"] = outcome
                value["execution"]["status"] = status
                if status == "completed":
                    for command in value["execution"]["commands"]:
                        command["exit_code"] = 1
                        command["stdout_sha256"] = EMPTY_SHA256
                        command["stderr_sha256"] = EMPTY_SHA256
                self.assertEqual([], self.semantics(value))
        for outcome, status, code in (
            ("fail", "blocked", "fail_status_mismatch"),
            ("blocked", "completed", "blocked_status_mismatch"),
            ("not_run", "completed", "not_run_status_mismatch"),
        ):
            with self.subTest(outcome=outcome, status=status):
                value = copy.deepcopy(self.evidence)
                value["outcome"] = outcome
                value["execution"]["status"] = status
                self.assertIn(code, self.semantics(value))

    def test_rejects_missing_completed_results_and_nonzero_pass(self) -> None:
        value = pass_evidence(self.evidence, self.contract)
        value["execution"]["commands"][0]["exit_code"] = None
        self.assertIn("completed_command_result_missing", self.semantics(value))
        value = pass_evidence(self.evidence, self.contract)
        value["execution"]["commands"][0]["exit_code"] = 2
        self.assertIn("nonzero_command_marked_pass", self.semantics(value))

    def test_rejects_not_run_results_observations_and_artifacts(self) -> None:
        value = copy.deepcopy(self.evidence)
        value["execution"]["commands"][0]["exit_code"] = 0
        value["observations"] = pass_evidence(self.evidence, self.contract)["observations"]
        value["artifacts"][0] = copy.deepcopy(value["sources"][0])
        errors = self.semantics(value)
        self.assertIn("not_run_command_has_result", errors)
        self.assertIn("not_run_has_observations", errors)
        self.assertIn("not_run_has_available_artifact", errors)

    def test_rejects_unavailable_or_nonapplicable_result_metadata(self) -> None:
        value = copy.deepcopy(self.evidence)
        value["artifacts"][0]["sha256"] = "0" * 64
        value["artifacts"][0]["bytes"] = 1
        errors = self.semantics(value)
        self.assertIn("unavailable_evidence_has_result", errors)
        value["artifacts"][0]["applicability"] = "not_applicable"
        self.assertIn("non_applicable_evidence_has_result", self.semantics(value))

    def test_rejects_file_and_aggregate_size_limits(self) -> None:
        self.assertIn(
            "evidence_file_size_limit_exceeded",
            self.semantics(self.evidence, maximum_file_bytes=10),
        )
        self.assertIn(
            "evidence_aggregate_size_limit_exceeded",
            self.semantics(self.evidence, maximum_aggregate_bytes=1000),
        )

    def test_contract_research_profile_can_close_non_c_task(self) -> None:
        value = pass_evidence(self.evidence, self.contract)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            contract_path = root / "contract.json"
            artifact_path = root / "artifact.json"
            contract_value = {
                "expected": {
                    "evidence_kind": "contract_research",
                    "criteria": [{"id": "scope-frozen"}],
                }
            }
            contract_path.write_text(json.dumps(contract_value), encoding="utf-8")
            artifact_path.write_text("{}", encoding="utf-8")
            value["evidence_kind"] = "contract_research"
            value["contract_ref"] = {
                "path": "contract.json",
                "sha256": sha256_file(contract_path),
            }
            value["sources"] = [
                {
                    "id": "source.research.contract",
                    "role": "reviewed contract input",
                    "applicability": "applicable",
                    "path": "contract.json",
                    "available": True,
                    "sha256": sha256_file(contract_path),
                    "bytes": contract_path.stat().st_size,
                }
            ]
            value["artifacts"] = [
                {
                    "id": "artifact.research.contract",
                    "role": "reviewed contract result",
                    "applicability": "applicable",
                    "path": "artifact.json",
                    "available": True,
                    "sha256": sha256_file(artifact_path),
                    "bytes": artifact_path.stat().st_size,
                }
            ]
            for command in value["execution"]["commands"]:
                command["result_artifact_ids"] = ["artifact.research.contract"]
            value["observation_artifact_ids"] = ["artifact.research.contract"]
            value["observations"] = {
                "kind": "contract_research",
                "criteria": [
                    {
                        "id": "scope-frozen",
                        "outcome": "pass",
                        "artifact_ids": ["artifact.research.contract"],
                    }
                ],
            }
            self.assertEqual([], list(self.validator.iter_errors(value)))
            self.assertEqual(
                [], validate_evidence_semantics(value, root, self.authority)
            )

    def test_schema_has_all_role_neutral_observation_profiles(self) -> None:
        for kind in (
            "contract_research",
            "native_c",
            "emscripten_wasm",
            "browser_runtime",
        ):
            with self.subTest(kind=kind):
                value = copy.deepcopy(self.evidence)
                value["evidence_kind"] = kind
                if kind == "native_c":
                    value["observations"] = {
                        "kind": kind,
                        "target_triple": "x86_64-unknown-linux-gnu",
                        "c_standard": "c11",
                        "pointer_bits": 64,
                    }
                elif kind == "browser_runtime":
                    value["observations"] = {
                        "kind": kind,
                        "browsers": [{"name": "Firefox", "version": "pinned", "outcome": "blocked"}],
                        "worker_topology": "candidate-a",
                        "cross_origin_isolated": True,
                        "boot_dispose_cycles": 1,
                        "leaked_resources": 0,
                    }
                elif kind == "contract_research":
                    value["observations"] = {
                        "kind": kind,
                        "criteria": [{"id": "criterion", "outcome": "blocked", "artifact_ids": []}],
                    }
                # not_run forbids observations semantically but Schema still proves shape.
                self.assertEqual([], list(self.validator.iter_errors(value)))

    def test_rejects_escaping_symlinked_paths_and_root(self) -> None:
        self.assertIsNone(safe_fixture_path(REPO_ROOT, "../../outside"))
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            real = parent / "real"
            real.mkdir()
            link = parent / "root-link"
            link.symlink_to(real, target_is_directory=True)
            self.assertIsNone(safe_fixture_path(link, "member"))
            outside = parent / "outside"
            outside.mkdir()
            child_link = real / "child"
            child_link.symlink_to(outside, target_is_directory=True)
            self.assertIsNone(safe_fixture_path(real, "child/file"))

    def test_streaming_hash_matches_hashlib_for_multiple_chunks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "large.bin"
            data = b"planning-evidence" * 10000
            path.write_bytes(data)
            self.assertEqual(hashlib.sha256(data).hexdigest(), sha256_file(path))

    def test_duplicate_json_and_yaml_keys_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"a": 1, "a": 2}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                read_bounded_json(path, 100)
        with self.assertRaises(yaml.YAMLError):
            load_unique_yaml("a: 1\na: 2\n")


class EvidenceDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        schema = json.loads(
            (RESEARCH_ROOT / "70-tools/planning-evidence-v1.schema.json").read_text()
        )
        cls.validator = jsonschema.Draft202012Validator(schema)

    def write_record(
        self,
        repository: Path,
        record_id: str,
        *,
        support_refs: list[str] | None = None,
        outcome: str = "not_run",
        revision_mismatch: bool = False,
    ) -> Path:
        records = repository / "research/assets/results"
        records.mkdir(parents=True, exist_ok=True)
        source = records / "source.txt"
        contract = records / "contract.json"
        result_artifact = records / "result.json"
        source.write_text("bounded fixture source\n", encoding="utf-8")
        result_artifact.write_text('{"result":"synthetic-test"}\n', encoding="utf-8")
        contract_value = {
            "expected": {
                "evidence_kind": "contract_research",
                "criteria": [{"id": "scope-frozen"}],
            }
        }
        contract.write_text(json.dumps(contract_value), encoding="utf-8")
        source_record = {
            "id": "source.discovery.input",
            "role": "bounded discovery input",
            "applicability": "applicable",
            "path": "research/assets/results/source.txt",
            "available": True,
            "sha256": sha256_file(source),
            "bytes": source.stat().st_size,
        }
        command = {
            "id": "validate-contract",
            "argv": ["validator", "--data-only"],
            "cwd": "research/assets/results",
            "exit_code": None,
            "stdout_sha256": None,
            "stderr_sha256": None,
            "result_artifact_ids": [],
        }
        value = {
            "profile": "erts-wasm.planning-evidence.v1",
            "record_id": record_id,
            "evidence_kind": "contract_research",
            "synthetic": True,
            "producer": "discovery-test-producer",
            "reviewer": None,
            "plan_baseline": {
                "document_id": "planning.synthetic.proof.p1.plan",
                "revision": "test-revision",
                "task_ids": ["p1-p01-c-abi-probe"],
                "gate_ids": ["P1-A01"],
            },
            "candidate": {
                "revision": "different" if revision_mismatch else "test-revision",
                "dirty_state": "clean",
                "diff_sha256": None,
            },
            "execution": {
                "status": "not_run",
                "tested_revision": "test-revision",
                "commands": [command],
            },
            "toolchains": [],
            "sources": [source_record],
            "artifacts": [
                {
                    "id": "artifact.discovery.result",
                    "role": "planned result",
                    "applicability": "applicable",
                    "path": "research/assets/results/result.json",
                    "available": False,
                    "sha256": None,
                    "bytes": None,
                }
            ],
            "contract_ref": {
                "path": "research/assets/results/contract.json",
                "sha256": sha256_file(contract),
            },
            "observations": None,
            "observation_artifact_ids": [],
            "outcome": "not_run",
            "limitations": ["Synthetic test record only."],
            "support_refs": support_refs or [],
        }
        if outcome == "pass":
            value["synthetic"] = False
            value["reviewer"] = "independent-discovery-reviewer"
            value["execution"]["status"] = "completed"
            for field in ("stdout_sha256", "stderr_sha256"):
                command[field] = EMPTY_SHA256
            command["exit_code"] = 0
            command["result_artifact_ids"] = ["artifact.discovery.result"]
            value["toolchains"] = [
                {
                    "name": "contract-validator",
                    "executable": "/not-executed/validator",
                    "version": "test",
                    "target": "repository",
                    "compile_flags": [],
                    "link_flags": [],
                }
            ]
            value["artifacts"] = [
                {
                    "id": "artifact.discovery.result",
                    "role": "bounded reviewed result",
                    "applicability": "applicable",
                    "path": "research/assets/results/result.json",
                    "available": True,
                    "sha256": sha256_file(result_artifact),
                    "bytes": result_artifact.stat().st_size,
                }
            ]
            value["observations"] = {
                "kind": "contract_research",
                "criteria": [
                    {
                        "id": "scope-frozen",
                        "outcome": "pass",
                        "artifact_ids": ["artifact.discovery.result"],
                    }
                ],
            }
            value["observation_artifact_ids"] = ["artifact.discovery.result"]
            value["outcome"] = "pass"
        slug = record_id.replace(".", "-")
        path = records / f"{slug}.planning-evidence.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_empty_assets_tree_has_no_real_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            research = repository / "research"
            (research / "assets").mkdir(parents=True)
            errors: list[str] = []
            result = validate_evidence_records(
                research,
                repository,
                self.validator,
                planning_authority(),
                errors,
            )
            self.assertEqual(EvidenceValidationResult(frozenset(), frozenset()), result)
            self.assertEqual([], errors)

    def test_symlinked_discovery_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            research = repository / "research"
            research.mkdir()
            real = repository / "outside-assets"
            real.mkdir()
            (research / "assets").symlink_to(real, target_is_directory=True)
            errors: list[str] = []
            validate_evidence_records(
                research,
                repository,
                self.validator,
                planning_authority(),
                errors,
            )
            self.assertIn("missing or symlinked", " ".join(errors))

    def test_discovers_and_validates_real_suffix_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            research = repository / "research"
            (research / "assets").mkdir(parents=True)
            self.write_record(repository, "evidence.test.discovered")
            errors: list[str] = []
            result = validate_evidence_records(
                research,
                repository,
                self.validator,
                planning_authority(),
                errors,
            )
            self.assertEqual([], errors)
            self.assertEqual(
                frozenset({"evidence.test.discovered"}), result.record_ids
            )

    def test_support_refs_resolve_are_acyclic_and_gate_pass_closure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            research = repository / "research"
            (research / "assets").mkdir(parents=True)
            self.write_record(
                repository,
                "evidence.test.invalid",
                revision_mismatch=True,
            )
            self.write_record(
                repository,
                "evidence.test.pass",
                support_refs=["evidence.test.invalid"],
                outcome="pass",
            )
            errors: list[str] = []
            result = validate_evidence_records(
                research,
                repository,
                self.validator,
                planning_authority(),
                errors,
            )
            self.assertIn("fixture_revision_mismatch", " ".join(errors))
            self.assertEqual(frozenset(), result.passed_task_ids)

        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            research = repository / "research"
            (research / "assets").mkdir(parents=True)
            self.write_record(
                repository,
                "evidence.test.one",
                support_refs=["evidence.test.two"],
            )
            self.write_record(
                repository,
                "evidence.test.two",
                support_refs=["evidence.test.one"],
            )
            errors = []
            validate_evidence_records(
                research,
                repository,
                self.validator,
                planning_authority(),
                errors,
            )
            self.assertIn("evidence support cycle", " ".join(errors))

    def test_unresolved_support_and_record_byte_bounds_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            research = repository / "research"
            (research / "assets").mkdir(parents=True)
            self.write_record(
                repository,
                "evidence.test.unresolved",
                support_refs=["evidence.test.missing"],
            )
            errors: list[str] = []
            validate_evidence_records(
                research,
                repository,
                self.validator,
                planning_authority(),
                errors,
                maximum_record_bytes=10,
            )
            self.assertIn("per-file byte limit", " ".join(errors))
            errors = []
            validate_evidence_records(
                research,
                repository,
                self.validator,
                planning_authority(),
                errors,
            )
            self.assertIn("unresolved evidence support", " ".join(errors))

    def test_conformance_subtree_cannot_be_promoted_by_filename(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            research = repository / "research"
            fixture = research / "assets/planning-conformance"
            fixture.mkdir(parents=True)
            (fixture / "fake.planning-evidence.json").write_text("{}", encoding="utf-8")
            errors: list[str] = []
            validate_evidence_records(
                research,
                repository,
                self.validator,
                planning_authority(),
                errors,
            )
            self.assertIn("cannot be discovered as real evidence", " ".join(errors))


class ToolIntegrationTests(unittest.TestCase):
    def test_manifest_scalar_reference_cannot_escape_fixture_root(self) -> None:
        fixture_root = RESEARCH_ROOT / "assets/planning-conformance"
        with self.assertRaises(ValueError):
            resolve_fixture_member(fixture_root, "../../frontmatter.schema.json")

    def test_fixture_verifier_is_end_to_end_and_authored_argv_is_inert(self) -> None:
        marker = Path("/tmp/erts-wasm-planning-fixture-must-not-exist")
        self.assertFalse(marker.exists())
        with mock.patch.object(
            sys, "argv", ["verify_planning_fixtures.py", str(REPO_ROOT)]
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0, verify_fixtures())
        self.assertFalse(marker.exists())

    def test_fixture_manifest_scalar_must_match_its_hashed_role(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            fixture = repository / "research/assets/planning-conformance"
            tools = repository / "research/70-tools"
            fixture.parent.mkdir(parents=True)
            tools.mkdir(parents=True)
            shutil.copytree(
                RESEARCH_ROOT / "assets/planning-conformance",
                fixture,
            )
            for name in (
                "planning-authoring-v1.schema.json",
                "planning-evidence-v1.schema.json",
            ):
                shutil.copy2(RESEARCH_ROOT / "70-tools" / name, tools / name)
            manifest_path = fixture / "fixture-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["expected_graph"] = "abi-contract.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with mock.patch.object(
                sys, "argv", ["verify_planning_fixtures.py", str(repository)]
            ):
                with self.assertRaisesRegex(ValueError, "hash-bound to role"):
                    verify_fixtures()
    def test_check_all_runs_every_check_after_failure(self) -> None:
        with mock.patch.object(check_all, "run", side_effect=[1, 0, 0]) as run:
            self.assertEqual(1, check_all.main())
            self.assertEqual(3, run.call_count)


if __name__ == "__main__":
    unittest.main()
