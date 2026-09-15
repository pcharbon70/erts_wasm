#!/usr/bin/env python3
"""Verify bounded planning fixtures without executing authored commands."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import jsonschema
import yaml

from planning_validation import (
    PlanningDocument,
    load_unique_yaml,
    read_bounded_json,
    safe_fixture_path,
    sha256_file,
    validate_evidence_semantics,
    validate_planning_document,
    validate_planning_graph,
)
from research_paths import REPO_ROOT


EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
SCALAR_ROLES = {
    "expected_graph": "plan_graph_oracle",
    "negative_cases": "negative_cases",
    "abi_contract": "abi_contract",
    "evidence_record": "synthetic_not_run_evidence",
}


def fail(message: str) -> None:
    """Raise one stable fixture-integrity failure."""

    raise ValueError(message)


def read_json(path: Path, maximum_bytes: int) -> object:
    """Read bounded, duplicate-key-free JSON from a regular file."""

    return read_bounded_json(path, maximum_bytes)


def resolve_fixture_member(fixture_root: Path, raw: str) -> Path:
    """Resolve one manifest member within the fixture directory."""

    path = safe_fixture_path(fixture_root, raw)
    if path is None or not path.is_file() or path.is_symlink():
        fail(f"fixture member is missing, escaping, or a symlink: {raw}")
    return path


def _schema(path: Path, maximum_bytes: int) -> jsonschema.Draft202012Validator:
    value = read_json(path, maximum_bytes)
    if not isinstance(value, dict):
        fail(f"schema must be an object: {path}")
    jsonschema.Draft202012Validator.check_schema(value)
    return jsonschema.Draft202012Validator(value)


def _oracle_authority(
    oracle: dict[str, object],
    authoring_validator: jsonschema.Draft202012Validator,
    fixture_root: Path,
) -> tuple[set[str], object]:
    """Feed the fixture oracle through the production document/graph validators."""

    entities = oracle["expected_entities"]
    relations = oracle["expected_relations"]
    tasks = oracle["expected_tasks"]
    gates = oracle["expected_gates"]
    if not all(isinstance(value, list) for value in (entities, relations, tasks, gates)):
        fail("plan graph arrays are malformed")
    projection = {
        "profile": "planning.authoring.v1",
        "document_id": entities[0]["id"],
        "entities": entities,
        "relations": [
            {"subject": row[0], "predicate": row[1], "object": row[2]}
            for row in relations
        ],
    }
    headings = "\n".join(
        f"## {entity['source_anchor'][1:].replace('-', ' ').title()}"
        for entity in entities
    )
    body = (
        "# Synthetic fixture projection\n\n"
        "```planning-meta\n"
        f"{yaml.safe_dump(projection, sort_keys=False)}```\n\n"
        f"{headings}\n"
    )
    document_errors: list[str] = []
    document = validate_planning_document(
        fixture_root / "oracle-projection.md",
        body,
        authoring_validator,
        document_errors,
        required=True,
    )
    if document is None or document_errors:
        fail(f"production planning document validation failed: {document_errors}")
    task_graph: dict[str, tuple[str, ...]] = {}
    for task in tasks:
        if not isinstance(task, dict):
            fail("oracle task must be an object")
        task_graph[str(task["id"])] = tuple(str(item) for item in task["requires"])
    document = PlanningDocument(
        document.path,
        document.document_id,
        document.entities,
        document.relations,
        task_graph,
        gates=frozenset(str(gate) for gate in gates),
        task_plan_ids={
            task_id: "planning.synthetic.proof.p1.plan" for task_id in task_graph
        },
        gate_plan_ids={
            str(gate): "planning.synthetic.proof.p1.plan" for gate in gates
        },
    )
    graph_errors: list[str] = []
    authority = validate_planning_graph([document], graph_errors)
    if graph_errors:
        fail(f"production planning graph validation failed: {graph_errors}")
    return set(authority.entity_ids), authority


def _pass_candidate(
    evidence: dict[str, object],
    contract: dict[str, object],
    repository_root: Path,
) -> dict[str, object]:
    """Create an in-memory candidate used only to exercise pass rejection paths."""

    value = copy.deepcopy(evidence)
    expected = contract["expected"]
    value["synthetic"] = False
    result_id = "artifact.synthetic.validator_result"
    result_relative = "research/assets/planning-conformance/synthetic-result-artifact.txt"
    result_path = repository_root / result_relative
    value["reviewer"] = "independent-fixture-reviewer"
    value["outcome"] = "pass"
    value["execution"]["status"] = "completed"
    for command in value["execution"]["commands"]:
        command["exit_code"] = 0
        command["stdout_sha256"] = EMPTY_SHA256
        command["stderr_sha256"] = EMPTY_SHA256
        command["result_artifact_ids"] = [result_id]
    value["toolchains"] = [
        {
            "name": "synthetic-emcc-identity",
            "executable": "/synthetic/not-executed/emcc",
            "version": "synthetic-not-executed",
            "target": "wasm32-unknown-emscripten",
            "compile_flags": ["-std=c11", "-pthread"],
            "link_flags": ["-pthread", "-sINITIAL_MEMORY=65536", "-sMAXIMUM_MEMORY=65536"],
        }
    ]
    value["artifacts"] = [
        {
            "id": result_id,
            "role": "synthetic nonempty validator result bytes",
            "applicability": "applicable",
            "path": result_relative,
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
            "shared": expected["memory"]["shared"],
            "initial_bytes": 65536,
            "maximum_bytes": 65536,
        },
    }
    value["observation_artifact_ids"] = [result_id]
    return value


def _apply_operations(value: object, operations: object) -> None:
    """Apply data-only replacements from a bounded negative fixture."""

    if not isinstance(operations, list) or len(operations) > 32:
        fail("negative case operations must be a bounded array")
    for operation in operations:
        if not isinstance(operation, dict) or set(operation) != {"path", "value"}:
            fail("negative case operation must contain only path and value")
        path = operation["path"]
        if not isinstance(path, list) or not path or len(path) > 16:
            fail("negative case path must be a bounded nonempty array")
        cursor = value
        for part in path[:-1]:
            if isinstance(cursor, dict) and isinstance(part, str):
                cursor = cursor[part]
            elif isinstance(cursor, list) and isinstance(part, int):
                cursor = cursor[part]
            else:
                fail(f"negative case path cannot traverse {part!r}")
        final = path[-1]
        if isinstance(cursor, dict) and isinstance(final, str) and final in cursor:
            cursor[final] = operation["value"]
        elif isinstance(cursor, list) and isinstance(final, int) and 0 <= final < len(cursor):
            cursor[final] = operation["value"]
        else:
            fail(f"negative case path cannot replace {final!r}")


def main() -> int:
    raw_repository = (
        Path(sys.argv[1]).absolute() if len(sys.argv) > 1 else REPO_ROOT.absolute()
    )
    if raw_repository.is_symlink() or not raw_repository.is_dir():
        fail("repository root must be a real, non-symlinked directory")
    repository_root = raw_repository.resolve(strict=True)
    fixture_relative = "research/assets/planning-conformance"
    fixture_root = safe_fixture_path(repository_root, fixture_relative)
    if fixture_root is None or fixture_root.is_symlink() or not fixture_root.is_dir():
        fail("fixture root is missing, escaping, or symlinked")

    maximum_manifest_bytes = 1_048_576
    manifest_path = resolve_fixture_member(fixture_root, "fixture-manifest.json")
    manifest = read_json(manifest_path, maximum_manifest_bytes)
    if not isinstance(manifest, dict):
        fail("fixture manifest must be an object")
    if manifest.get("profile") != "erts-wasm.planning-fixture-manifest.v1":
        fail("unexpected fixture manifest profile")
    if manifest.get("fixture_only") is not True:
        fail("fixture manifest must remain fixture-only")
    if manifest.get("execution_status") != "not_run":
        fail("fixture manifest must remain not-run")

    bounds = manifest["bounds"]
    files = manifest["files"]
    if not isinstance(bounds, dict) or not isinstance(files, list):
        fail("fixture bounds/files are malformed")
    maximum_source_bytes = int(bounds["maximum_source_bytes"])
    maximum_total_bytes = int(bounds["maximum_total_source_bytes"])
    roles: set[str] = set()
    paths: set[Path] = set()
    path_roles: dict[Path, str] = {}
    total_bytes = 0
    for source in files:
        if not isinstance(source, dict) or set(source) != {"role", "path", "sha256"}:
            fail("fixture file entry must contain only role, path, and sha256")
        role = str(source["role"])
        if role in roles:
            fail(f"fixture repeats role: {role}")
        roles.add(role)
        path = safe_fixture_path(repository_root, str(source["path"]))
        if path is None or not path.is_file() or path.is_symlink():
            fail(f"fixture path is missing, escaping, or a symlink: {source['path']}")
        try:
            path.relative_to(fixture_root)
        except ValueError:
            fail(f"fixture hash entry escapes fixture root: {source['path']}")
        if path in paths:
            fail(f"fixture repeats path: {source['path']}")
        paths.add(path)
        path_roles[path] = role
        size = path.stat().st_size
        total_bytes += size
        if size > maximum_source_bytes or total_bytes > maximum_total_bytes:
            fail(f"fixture exceeds byte bounds: {source['path']}")
        if sha256_file(path) != source["sha256"]:
            fail(f"fixture digest mismatch: {source['path']}")

    scalar_paths: dict[str, Path] = {}
    for field, role in SCALAR_ROLES.items():
        path = resolve_fixture_member(fixture_root, str(manifest[field]))
        if path_roles.get(path) != role:
            fail(f"manifest scalar {field!r} is not hash-bound to role {role!r}")
        scalar_paths[field] = path

    oracle = read_json(scalar_paths["expected_graph"], maximum_source_bytes)
    if not isinstance(oracle, dict) or oracle.get("fixture_only") is not True:
        fail("plan graph oracle must be a fixture-only object")
    entities = oracle["expected_entities"]
    relations = oracle["expected_relations"]
    if len(entities) > int(bounds["maximum_entities"]):
        fail("plan graph exceeds entity bound")
    if len(relations) > int(bounds["maximum_relations"]):
        fail("plan graph exceeds relation bound")
    authoring_validator = _schema(
        repository_root / "research/70-tools/planning-authoring-v1.schema.json",
        maximum_source_bytes,
    )
    entity_ids, authority = _oracle_authority(
        oracle, authoring_validator, fixture_root
    )

    contract = read_json(scalar_paths["abi_contract"], maximum_source_bytes)
    if not isinstance(contract, dict) or contract.get("fixture_only") is not True:
        fail("ABI contract must be a fixture-only object")
    evidence = read_json(scalar_paths["evidence_record"], maximum_source_bytes)
    if not isinstance(evidence, dict):
        fail("evidence fixture must be an object")
    evidence_validator = _schema(
        repository_root / "research/70-tools/planning-evidence-v1.schema.json",
        maximum_source_bytes,
    )
    schema_errors = list(evidence_validator.iter_errors(evidence))
    if schema_errors:
        fail(
            "invalid synthetic evidence fixture: "
            + "; ".join(error.message for error in schema_errors)
        )
    semantic_errors = validate_evidence_semantics(
        evidence, repository_root, authority
    )
    if semantic_errors:
        fail(f"synthetic evidence semantic failure: {semantic_errors}")
    if evidence["synthetic"] is not True or evidence["outcome"] != "not_run":
        fail("fixture evidence must remain synthetic and not-run")

    cases_path = scalar_paths["negative_cases"]
    cases_document = load_unique_yaml(cases_path.read_text(encoding="utf-8"))
    if (
        not isinstance(cases_document, dict)
        or cases_document.get("fixture_only") is not True
    ):
        fail("negative cases must be a fixture-only mapping")
    cases = cases_document["cases"]
    if not isinstance(cases, list) or len(cases) > int(bounds["maximum_negative_cases"]):
        fail("negative cases exceed fixture bound")
    case_ids = {case["id"] for case in cases}
    if len(case_ids) != len(cases):
        fail("negative cases repeat an id")
    pass_candidate = _pass_candidate(evidence, contract, repository_root)
    if list(evidence_validator.iter_errors(pass_candidate)):
        fail("internal pass candidate does not satisfy the production schema")
    if validate_evidence_semantics(pass_candidate, repository_root, authority):
        fail("internal pass candidate does not satisfy production semantics")

    observed_codes: set[str] = set()
    marker = Path("/tmp/erts-wasm-planning-fixture-must-not-exist")
    if marker.exists():
        fail(f"inert-command marker already exists: {marker}")
    for case in cases:
        if not isinstance(case, dict) or set(case) != {
            "id",
            "baseline",
            "operations",
            "expected_codes",
        }:
            fail("negative case has an unexpected shape")
        baseline = evidence if case["baseline"] == "not_run" else pass_candidate
        value = copy.deepcopy(baseline)
        _apply_operations(value, case["operations"])
        # Both production layers are exercised. Some deliberately malformed pass
        # cases are expected to fail Schema as well as the semantic policy.
        list(evidence_validator.iter_errors(value))
        actual = set(validate_evidence_semantics(value, repository_root, authority))
        expected = set(case["expected_codes"])
        if actual != expected:
            fail(
                f"negative-case {case['id']!r} mismatch: "
                f"expected={sorted(expected)!r} observed={sorted(actual)!r}"
            )
        observed_codes.update(actual)
    if marker.exists():
        fail("an authored fixture command was executed")
    required_codes = set(oracle["required_rejection_codes"])
    if observed_codes != required_codes:
        fail(
            "negative cases do not cover every required production rejection: "
            f"expected={sorted(required_codes)!r} observed={sorted(observed_codes)!r}"
        )

    print(
        "Planning fixtures verified: "
        f"{len(files)} streamed/hash-bound inputs, {len(entity_ids)} entities, "
        f"{len(relations)} relations, {len(cases)} inert production-validator "
        "negative cases, and one schema-valid synthetic not-run C/Emscripten "
        "evidence record."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        KeyError,
        IndexError,
        OSError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
        jsonschema.SchemaError,
        yaml.YAMLError,
    ) as error:
        print(f"Planning fixture verification failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
