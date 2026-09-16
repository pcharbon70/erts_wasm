#!/usr/bin/env python3
"""Validate authored P0 contracts without treating them as acceptance evidence."""

from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path


RESEARCH_ROOT = Path(__file__).resolve().parents[1]
P0_ROOT = RESEARCH_ROOT / "assets" / "p0-governed-baseline"


class ContractError(ValueError):
    """A deterministic P0 contract validation failure."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError("invalid-json", f"{path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("invalid-root", f"{path}: root must be an object")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def unique(items: list[dict], key: str, code: str) -> None:
    values = [item.get(key) for item in items]
    if any(not isinstance(value, str) or not value for value in values):
        raise ContractError(code, f"every {key} must be a non-empty string")
    if len(values) != len(set(values)):
        raise ContractError(code, f"duplicate {key}")


def validate_phase_01(root: Path = P0_ROOT / "phase-01") -> list[str]:
    baseline = load_json(root / "p0-baseline-lock.json")
    trust = load_json(root / "p0-trust-scope-matrix.json")
    languages = load_json(root / "p0-language-ownership.json")
    inventory = load_json(root / "p0-runtime-inventory.json")
    census = load_json(root / "p0-thread-census-contract.json")

    pins = baseline.get("pins", [])
    unique(pins, "id", "duplicate-pin")
    required_pins = {
        "otp-source", "native-bootstrap", "emsdk-repository",
        "emscripten-release", "emscripten-source", "llvm-project",
        "binaryen", "build-image", "chrome-for-testing", "firefox",
    }
    if {pin["id"] for pin in pins} != required_pins:
        raise ContractError("missing-pin", "pin ledger does not match the required identity set")
    floating = {"latest", "stable", "beta", "nightly", "main", "master"}
    for pin in pins:
        tokens = str(pin.get("version", "")).lower().replace(":", " ").split()
        if floating.intersection(tokens):
            raise ContractError("floating-pin", f"{pin['id']} contains a floating version")
        for field in ("version", "revision", "origin", "verification", "materialization_state"):
            if not pin.get(field):
                raise ContractError("incomplete-pin", f"{pin['id']} lacks {field}")
    required_materialization = {
        "native-bootstrap": "materialized-and-identity-verified",
        "emscripten-release": "materialized-in-pinned-build-image",
        "build-image": "materialized-and-digest-verified",
        "chrome-for-testing": "materialized-and-locally-hashed",
        "firefox": "materialized-and-official-checksum-verified",
    }
    pin_by_id = {pin["id"]: pin for pin in pins}
    for pin_id, expected_state in required_materialization.items():
        if pin_by_id[pin_id].get("materialization_state") != expected_state:
            raise ContractError("unmaterialized-pin", f"{pin_id} is not materialized and verified")
    for browser_id in ("chrome-for-testing", "firefox"):
        digest = pin_by_id[browser_id].get("archive_sha256", "")
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise ContractError("missing-browser-digest", f"{browser_id} lacks an exact SHA-256")

    zones = trust.get("zones", [])
    unique(zones, "id", "duplicate-authority")
    if any(not row.get("owner") or "unassigned" in row.get("owner", "") for row in zones):
        raise ContractError("unassigned-trust-owner", "every trust zone must bind an assigned owner")
    if trust.get("import_abi", {}).get("default") != "deny":
        raise ContractError("ambient-authority", "import ABI must deny by default")
    if not trust.get("stop_conditions") or not trust.get("quota_owners"):
        raise ContractError("incomplete-trust-model", "stop conditions and quota owners are required")

    language_rows = languages.get("owners", [])
    unique(language_rows, "language", "duplicate-language-owner")
    required_languages = {"C", "TypeScript", "Erlang", "Elixir", "Rust", "C++"}
    if {row["language"] for row in language_rows} != required_languages:
        raise ContractError("missing-language-owner", "language ownership set is incomplete")
    admitted_languages = {"C", "TypeScript", "Erlang", "Elixir"}
    if any(not row.get("abi_owner") or "unassigned" in row.get("abi_owner", "") for row in language_rows if row.get("language") in admitted_languages):
        raise ContractError("unassigned-language-owner", "every admitted or deferred language boundary must bind an assigned owner")
    if languages.get("adr_state") != "proposed":
        raise ContractError("premature-adr-acceptance", "ADR-0001 must remain proposed until P1 evidence")
    browser_toolchain = languages.get("browser_host_toolchain", {})
    if browser_toolchain.get("node", {}).get("version") != "24.19.0":
        raise ContractError("missing-typescript-toolchain-pin", "browser-host Node must match the pinned build image")
    if browser_toolchain.get("package_manager", {}).get("version") != "11.17.0":
        raise ContractError("missing-typescript-toolchain-pin", "browser-host package manager is not pinned")
    typescript = browser_toolchain.get("typescript", {})
    if typescript.get("version") != "6.0.3" or not typescript.get("integrity") or not typescript.get("sha256"):
        raise ContractError("missing-typescript-toolchain-pin", "TypeScript compiler identity is incomplete")

    categories = inventory.get("categories", [])
    unique(categories, "id", "duplicate-runtime-category")
    required_categories = {
        "startup-threads", "syscalls-and-os-services", "sys-h-services",
        "preloads", "boot-modules", "allocator", "poll-and-wakeup", "time",
        "native-edges", "loader-entry-points", "code-indices-and-literals",
        "purgers", "on-load",
    }
    if {item["id"] for item in categories} != required_categories:
        raise ContractError("missing-runtime-category", "runtime inventory category set is incomplete")
    for item in categories:
        if not item.get("method") or not item.get("findings") or not item.get("classification"):
            raise ContractError("silent-runtime-category", f"{item['id']} lacks method, findings, or classification")
        if "erts/emulator/beam/erl_driver.c" in item.get("source_paths", []):
            raise ContractError("stale-runtime-path", "OTP 29.0.6 has no erts/emulator/beam/erl_driver.c")
    inventory_by_id = {item["id"]: item for item in categories}
    if "22 preloaded Erlang source modules are present" not in inventory_by_id["preloads"].get("findings", []):
        raise ContractError("stale-preload-count", "OTP 29.0.6 preload count must be the reproduced value")

    pool_rule = census.get("pool_size_rule", {})
    if pool_rule.get("source") != "measured-full-runtime-high-water-plus-declared-headroom":
        raise ContractError("topology-selected-census", "pool size must derive from full-runtime measurement")
    if "+S scheduler count" not in pool_rule.get("forbidden_sources", []):
        raise ContractError("scheduler-derived-pool", "+S must be an explicit forbidden pool-size source")
    experiment_ids = {item.get("id") for item in census.get("experiments", [])}
    if experiment_ids != {"P0-THREAD-N", "P0-THREAD-N-1"}:
        raise ContractError("missing-n-minus-one", "thread census needs N and N-1 experiments")
    if "unassigned" in census.get("owners", {}).get("review", ""):
        raise ContractError("unassigned-census-reviewer", "thread-census review must bind an assigned reviewer")

    return ["pins", "trust-boundary", "language-ownership", "runtime-inventory", "thread-census"]


def finite_positive(value: object, code: str, label: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise ContractError(code, f"{label} must be a finite positive number")


def finite_positive_integer(value: object, code: str, label: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ContractError(code, f"{label} must be a finite positive integer")


def validate_phase_02(root: Path = P0_ROOT / "phase-02") -> list[str]:
    experiments = load_json(root / "p0-experiment-bounds.json")
    unsupported = load_json(root / "p0-unsupported-operations.json")
    loader = load_json(root / "p0-loader-startup-bounds.json")
    product = load_json(root / "p0-product-budget-method.json")
    evidence = load_json(root / "p0-evidence-profiles.json")
    validation = load_json(root / "p0-phase-02-validation-contract.json")

    series = experiments.get("series", {})
    for field in ("cold_boot_attempts", "warmup_cycles_discarded", "measured_boot_dispose_cycles", "maximum_total_cycles_per_run"):
        finite_positive_integer(series.get(field), "infinite-test-series", field)
    if sum(series[field] for field in ("cold_boot_attempts", "warmup_cycles_discarded", "measured_boot_dispose_cycles")) > series["maximum_total_cycles_per_run"]:
        raise ContractError("inconsistent-test-series", "component cycle counts exceed the total ceiling")
    if not experiments.get("frozen_before_runtime_measurement"):
        raise ContractError("post-result-threshold-edit", "experiment bounds must be frozen before measurement")
    if series.get("randomized_order") is not True or not series.get("randomization_seed_rule") or not series.get("series_identity_rule"):
        raise ContractError("unreproducible-randomization", "randomized series must retain a predeclared seed, order, and complete identity")
    settling = experiments.get("settling", {})
    offsets = settling.get("post_dispose_sample_offsets_ms", [])
    if (
        not isinstance(offsets, list)
        or len(offsets) < 3
        or any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in offsets)
        or offsets != sorted(set(offsets))
        or settling.get("maximum_settling_ms") != offsets[-1]
        or not settling.get("sample_rule")
        or not settling.get("quiescence_rule")
    ):
        raise ContractError("invalid-settling-series", "settling samples must be ordered, finite, retained, and end at the declared maximum")
    ceilings = experiments.get("safety_ceilings", [])
    unique(ceilings, "id", "duplicate-experiment-bound")
    required_ceilings = {
        "run-wall-clock", "single-startup", "generation-workers",
        "shared-memory", "aggregate-artifacts", "browser-host-rss-observation",
    }
    if {item["id"] for item in ceilings} != required_ceilings:
        raise ContractError("missing-experiment-bound", "experimental safety ceiling set is incomplete")
    for item in ceilings:
        finite_positive(item.get("limit"), "unbounded-resource", item.get("id", "resource"))
        for field in ("unit", "owner", "enforcement_point", "mechanism", "breach_action"):
            if not item.get(field):
                raise ContractError(f"missing-{field.replace('_', '-')}", f"{item['id']} lacks {field}")
    comparison = experiments.get("semantic_comparison", {})
    if not comparison.get("oracle") or not comparison.get("normalization_allowlist") or not comparison.get("required_exact_fields") or not comparison.get("mismatch_disposition"):
        raise ContractError("incomplete-semantic-comparison", "semantic comparison requires an oracle, closed normalization, exact fields, and mismatch disposition")

    operations = unsupported.get("operations", [])
    unique(operations, "id", "duplicate-unsupported-operation")
    required_operations = {
        "dynamic-nif", "dynamic-driver", "os-process-port", "fork-exec",
        "raw-tcp-udp", "distribution", "shell-terminal", "eval",
        "runtime-compiler", "arbitrary-code-loading", "ambient-host-filesystem",
        "general-posix-signals", "unlisted-on-load", "hot-code-replacement",
        "dynamic-side-module", "wasm-memory-growth", "generic-javascript",
        "dom-access", "browser-network-capability", "browser-persistence-capability",
        "browser-cryptography-capability", "external-term-browser-boundary",
    }
    if {item["id"] for item in operations} != required_operations:
        raise ContractError("missing-unsupported-operation", "unsupported-operation inventory is incomplete")
    for item in operations:
        for field in ("request_surface", "owner", "expected_result"):
            if not item.get(field):
                raise ContractError(f"missing-{field.replace('_', '-')}", f"{item['id']} lacks {field}")

    bounds = loader.get("bounds", [])
    unique(bounds, "id", "duplicate-loader-bound")
    required_resources = {
        "manifest-bytes", "manifest-depth", "manifest-record-count", "artifact-count",
        "artifact-encoded-bytes", "aggregate-encoded-artifact-bytes",
        "release-expanded-bytes", "release-entry-count", "release-entry-expanded-bytes",
        "beam-module-bytes", "artifact-url-bytes", "path-bytes", "code-path-count",
        "argv-count", "argv-entry-bytes", "worker-agents", "initial-shared-memory",
        "maximum-shared-memory", "pre-ready-message-queue", "pre-ready-message-bytes",
        "pre-ready-queued-bytes", "concurrent-fetches", "startup-timers",
        "startup-wall-clock",
    }
    if not required_resources.issubset({item["id"] for item in bounds}):
        raise ContractError("missing-loader-bound", "loader/startup bounds omit a required resource")
    for item in bounds:
        finite_positive(item.get("limit"), "unbounded-resource", item.get("id", "resource"))
        for field in ("resource", "owner", "unit", "enforcement_point", "mechanism", "breach_action"):
            if not item.get(field):
                raise ContractError(f"missing-{field.replace('_', '-')}", f"{item['id']} lacks {field}")
    bound_by_id = {item["id"]: item for item in bounds}
    if bound_by_id["initial-shared-memory"]["limit"] != bound_by_id["maximum-shared-memory"]["limit"] or not loader.get("memory_rule"):
        raise ContractError("growable-poc-memory", "POC initial and maximum shared-memory bounds must match and prohibit growth")
    if not loader.get("content_encoding_rule"):
        raise ContractError("missing-expanded-byte-accounting", "transport bytes and expanded release bytes require separate accounting")
    ceiling_by_id = {item["id"]: item for item in ceilings}
    consistent_limits = (
        ceiling_by_id["single-startup"]["limit"] * 1000 == bound_by_id["startup-wall-clock"]["limit"]
        and ceiling_by_id["generation-workers"]["limit"] == bound_by_id["worker-agents"]["limit"]
        and ceiling_by_id["shared-memory"]["limit"] == bound_by_id["initial-shared-memory"]["limit"] == bound_by_id["maximum-shared-memory"]["limit"]
        and ceiling_by_id["aggregate-artifacts"]["limit"] == bound_by_id["aggregate-encoded-artifact-bytes"]["limit"]
    )
    if not consistent_limits:
        raise ContractError("inconsistent-safety-bound", "experiment and loader safety ceilings disagree")

    if product.get("numeric_product_budgets") is not None:
        raise ContractError("premature-product-budget", "numeric product budgets require the actual authority")
    if product.get("authority") != "unassigned-until-post-p6-pre-c1" or product.get("approval_state") != "producer-reviewed-owner-disposition-pending-product-approval-deferred-pre-c1":
        raise ContractError("fabricated-product-authority", "P0 must defer numeric product approval and its authority until post-P6/pre-C1")
    forbidden_derivations = product.get("forbidden_derivations", [])
    if "copy an experimental safety ceiling" not in forbidden_derivations:
        raise ContractError("copied-safety-ceiling", "product method must prohibit copying safety ceilings")
    if not any("baseline, coefficient, percentile, margin, sample count, population, or exclusion" in rule for rule in forbidden_derivations):
        raise ContractError("post-result-selection", "product method must prohibit post-result selection of statistical inputs")
    if not product.get("entry_requirements") or not product.get("metric_contract_requires") or not product.get("insufficient_evidence_rule"):
        raise ContractError("incomplete-product-method", "product budget method requires entry, metric, and insufficient-evidence rules")

    profiles = evidence.get("profiles", [])
    unique(profiles, "id", "duplicate-evidence-profile")
    required_profiles = {
        "native-debug", "native-release", "wasm-debug", "wasm-release",
        "browser-host-fuzz", "native-c-boundary-fuzz", "wasm-boundary-replay",
    }
    if {item["id"] for item in profiles} != required_profiles:
        raise ContractError("silent-instrumentation-omission", "required evidence profile set is incomplete")
    if not evidence.get("unsupported_combination_rule"):
        raise ContractError("silent-sanitizer-omission", "unsupported instrumentation needs an explicit disposition")
    if not evidence.get("failure_minimization", {}).get("orphan_rule"):
        raise ContractError("orphaned-fuzz-failure", "fuzz failures require retained ownership and reproduction")
    profiles_by_id = {item["id"]: item for item in profiles}
    toolchains = evidence.get("toolchains", {})
    required_toolchains = {"native-clang", "emscripten", "node", "typescript", "chrome", "firefox"}
    if set(toolchains) != required_toolchains or any(not toolchains[key] for key in required_toolchains):
        raise ContractError("incomplete-evidence-toolchain", "evidence profiles require exact native, Wasm, host, and browser identities")
    configurations = evidence.get("profile_configurations", {})
    if set(configurations) != required_profiles:
        raise ContractError("missing-profile-configuration", "every evidence profile requires a matching toolchain and flag configuration")
    for profile_id, configuration in configurations.items():
        if (
            not configuration.get("toolchain_refs")
            or not configuration.get("required_flags")
            or not configuration.get("parameter_rule")
            or any(reference not in toolchains for reference in configuration.get("toolchain_refs", []))
        ):
            raise ContractError("incomplete-profile-configuration", f"{profile_id} has an incomplete toolchain or flag configuration")
    for item in profiles:
        for field in ("target", "purpose", "required_features", "sanitizers", "status"):
            if field not in item or item[field] in (None, "", [] if field == "required_features" else None):
                raise ContractError("incomplete-evidence-profile", f"{item['id']} lacks {field}")
    if profiles_by_id["browser-host-fuzz"].get("sanitizers") != []:
        raise ContractError("wrong-host-instrumentation", "TypeScript host fuzzing cannot claim C address/undefined sanitizers")
    if set(profiles_by_id["native-c-boundary-fuzz"].get("sanitizers", [])) != {"address", "undefined"}:
        raise ContractError("missing-native-sanitizer", "native C boundary fuzzing requires address and undefined sanitizers")
    if not evidence.get("sbom", {}).get("format", "").startswith("SPDX") or not evidence.get("sbom", {}).get("required_fields"):
        raise ContractError("incomplete-sbom-profile", "POC SBOM profile must name SPDX and required fields")
    if evidence.get("provenance", {}).get("compatibility") != "SLSA-compatible provenance statement" or not evidence.get("provenance", {}).get("required_fields"):
        raise ContractError("incomplete-provenance-profile", "POC provenance must be SLSA-compatible and declare required fields")
    if not evidence.get("reproducibility", {}).get("rule") or evidence.get("reproducibility", {}).get("unexplained_difference") != "fails evidence handoff":
        raise ContractError("missing-rebuild-comparison", "evidence profile must require independent rebuild comparison")

    positive = validation.get("positive_case", {})
    if positive.get("command") != ["python3", "research/70-tools/p0_contract_validation.py", "phase-02"]:
        raise ContractError("stale-validation-command", "Phase 2 positive validation command is stale")
    negative_cases = validation.get("negative_cases", [])
    unique(negative_cases, "id", "duplicate-validation-case")
    required_negative_errors = {
        "post-result-threshold-edit", "unreproducible-randomization",
        "missing-enforcement-point", "missing-owner", "infinite-test-series",
        "missing-loader-bound", "growable-poc-memory",
        "inconsistent-safety-bound",
        "silent-instrumentation-omission", "wrong-host-instrumentation",
        "incomplete-evidence-toolchain",
        "orphaned-fuzz-failure", "copied-safety-ceiling", "post-result-selection",
        "missing-unsupported-operation", "missing-rebuild-comparison",
    }
    if {item.get("expected_error") for item in negative_cases} != required_negative_errors:
        raise ContractError("incomplete-validation-contract", "Phase 2 validation contract does not cover every required rejection")
    if not validation.get("acceptance_boundary"):
        raise ContractError("missing-acceptance-boundary", "Phase 2 validation must preserve its non-acceptance boundary")

    owner_result_path = root / "p0-phase-02-owner-review-result.json"
    if owner_result_path.exists():
        owner_result = load_json(owner_result_path)
        if (
            owner_result.get("reviewer") != "Pascal Charbonneau (pcharbon70)"
            or owner_result.get("reviewer_statement") != "I accept the P0.2 owner-review packet and its recorded limitations."
            or owner_result.get("outcome") != "accepted"
        ):
            raise ContractError("invalid-owner-attestation", "P0.2 owner result does not contain the exact accepted disposition")
        reviewed_packet = owner_result.get("reviewed_packet", {})
        producer_receipt = owner_result.get("producer_review_receipt", {})
        packet_path = root / "p0-phase-02-owner-review-packet.json"
        receipt_path = root / "p0-phase-02-producer-review-receipt.json"
        if reviewed_packet.get("sha256") != sha256_file(packet_path) or producer_receipt.get("sha256") != sha256_file(receipt_path):
            raise ContractError("stale-owner-attestation", "P0.2 owner result does not bind the reviewed packet and producer receipt")

    return ["experiment-bounds", "unsupported-operations", "loader-bounds", "product-budget-method", "evidence-profiles"]


def acyclic(states: set[str], edges: list[list[str]]) -> bool:
    outgoing = {state: set() for state in states}
    incoming = {state: 0 for state in states}
    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2 or any(node not in states for node in edge):
            raise ContractError("invalid-loader-edge", "loader edges must reference two declared states")
        source, target = edge
        if target not in outgoing[source]:
            outgoing[source].add(target)
            incoming[target] += 1
    ready = [state for state, count in incoming.items() if count == 0]
    visited = 0
    while ready:
        source = ready.pop()
        visited += 1
        for target in outgoing[source]:
            incoming[target] -= 1
            if incoming[target] == 0:
                ready.append(target)
    return visited == len(states)


def validate_phase_03(root: Path = P0_ROOT / "phase-03") -> list[str]:
    schema = load_json(root / "p0-runtime-manifest.schema.json")
    loader = load_json(root / "p0-loader-contract.json")
    trust = load_json(root / "p0-bootstrap-trust.json")
    ledger = load_json(root / "p0-asset-dependency-patch-ledger.json")
    roles = load_json(root / "p0-role-assignments.json")
    environment = load_json(root / "p0-empty-environment-contract.json")
    acceptance = load_json(root / "p0-acceptance-contract.json")
    report = load_json(root / "p0-acceptance-report.json")
    validation = load_json(root / "p0-phase-03-validation-contract.json")
    accepted_bounds_path = P0_ROOT / "phase-02" / "p0-loader-startup-bounds.json"
    accepted_bounds = load_json(accepted_bounds_path)
    accepted_bound_rows = {row["id"]: row for row in accepted_bounds.get("bounds", [])}
    accepted_bound_digest = sha256_file(accepted_bounds_path)

    required_manifest = {"format", "profile", "trust", "sources", "artifacts", "runtime", "boot", "modules", "abi", "capabilities", "bounds"}
    if set(schema.get("required", [])) != required_manifest:
        raise ContractError("incomplete-manifest-schema", "manifest required fields do not match the generation contract")
    format_const = schema.get("properties", {}).get("format", {}).get("const")
    if format_const != "erts-wasm-manifest-v1" or loader.get("schema_version") != format_const:
        raise ContractError("mixed-manifest-identity", "loader and manifest schema versions differ")
    manifest_auth = schema.get("x-manifest-authentication", {})
    schema_trust = schema.get("properties", {}).get("trust", {})
    schema_trust_required = set(schema_trust.get("required", []))
    if (
        schema_trust.get("properties", {}).get("anchor", {}).get("const") != "external-bootstrap-sha256"
        or "manifest_digest" in schema_trust_required
        or "outside the manifest" not in manifest_auth.get("anchor", "")
        or "duplicate object members" not in manifest_auth.get("parse_order", "")
    ):
        raise ContractError("self-authenticating-manifest", "manifest authentication must be externally anchored and precede strict bounded decoding")

    bound_bindings = schema.get("x-p0-bound-bindings", {})
    if (
        bound_bindings.get("contract_sha256") != accepted_bound_digest
        or set(bound_bindings.get("bound_ids", [])) != set(accepted_bound_rows)
        or loader.get("accepted_bounds_contract", {}).get("sha256") != accepted_bound_digest
    ):
        raise ContractError("stale-manifest-bounds", "manifest and loader must bind every accepted Phase 2 bound at its exact digest")
    if len(bound_bindings.get("non_schema_rules", [])) < 6:
        raise ContractError("incomplete-non-schema-bounds", "byte, aggregate, equality, release, and native-parser rules must remain explicit")

    properties = schema.get("properties", {})
    artifacts = properties.get("artifacts", {})
    artifact_properties = artifacts.get("items", {}).get("properties", {})
    runtime_schema = properties.get("runtime", {}).get("properties", {})
    boot_schema = properties.get("boot", {}).get("properties", {})
    module_schema = properties.get("modules", {}).get("properties", {}).get("entries", {}).get("items", {}).get("properties", {})
    manifest_bounds = properties.get("bounds", {}).get("properties", {})

    def bound_limit(bound_id: str) -> int:
        value = accepted_bound_rows.get(bound_id, {}).get("limit")
        if not isinstance(value, int) or isinstance(value, bool):
            raise ContractError("invalid-accepted-bound", f"{bound_id} lacks an integer limit")
        return value

    schema_limit_checks = {
        "artifact-count": artifacts.get("maxItems"),
        "artifact-encoded-bytes": artifact_properties.get("encoded_bytes", {}).get("maximum"),
        "artifact-url-bytes": artifact_properties.get("url", {}).get("x-maxUtf8Bytes"),
        "path-bytes": boot_schema.get("code_paths", {}).get("items", {}).get("x-maxUtf8Bytes"),
        "code-path-count": boot_schema.get("code_paths", {}).get("maxItems"),
        "argv-count": boot_schema.get("argv", {}).get("maxItems"),
        "argv-entry-bytes": boot_schema.get("argv", {}).get("items", {}).get("x-maxUtf8Bytes"),
        "worker-agents": runtime_schema.get("worker_agents", {}).get("maximum"),
        "initial-shared-memory": runtime_schema.get("initial_memory", {}).get("maximum"),
        "maximum-shared-memory": runtime_schema.get("maximum_memory", {}).get("maximum"),
        "beam-module-bytes": module_schema.get("bytes", {}).get("maximum"),
        "aggregate-encoded-artifact-bytes": manifest_bounds.get("aggregate_encoded_artifact_bytes", {}).get("maximum"),
        "release-expanded-bytes": manifest_bounds.get("release_expanded_bytes", {}).get("maximum"),
        "release-entry-count": manifest_bounds.get("release_entry_count", {}).get("maximum"),
        "release-entry-expanded-bytes": manifest_bounds.get("release_entry_expanded_bytes", {}).get("maximum"),
        "pre-ready-message-queue": manifest_bounds.get("pre_ready_message_queue", {}).get("maximum"),
        "pre-ready-message-bytes": manifest_bounds.get("pre_ready_message_bytes", {}).get("maximum"),
        "pre-ready-queued-bytes": manifest_bounds.get("pre_ready_queued_bytes", {}).get("maximum"),
        "concurrent-fetches": manifest_bounds.get("concurrent_fetches", {}).get("maximum"),
        "startup-timers": manifest_bounds.get("startup_timers", {}).get("maximum"),
        "startup-wall-clock": manifest_bounds.get("startup_wall_clock_ms", {}).get("maximum"),
    }
    for bound_id, schema_limit in schema_limit_checks.items():
        if schema_limit != bound_limit(bound_id):
            raise ContractError("manifest-bound-drift", f"{bound_id} schema limit differs from the accepted contract")
    if artifact_properties.get("content_encoding", {}).get("const") != "identity":
        raise ContractError("ambiguous-content-encoding", "first-proof artifact representation must use identity content encoding")
    if properties.get("capabilities", {}).get("maxItems") != 0:
        raise ContractError("ambient-poc-capability", "the POC manifest must admit no optional host capabilities")
    if runtime_schema.get("initial_memory", {}).get("multipleOf") != 65536 or runtime_schema.get("maximum_memory", {}).get("multipleOf") != 65536:
        raise ContractError("invalid-memory-page-rule", "shared memory values must be WebAssembly-page aligned")
    source_required = set(properties.get("sources", {}).get("required", []))
    if not {"build_profile", "build_flags_digest", "generated_sources_digest"}.issubset(source_required):
        raise ContractError("incomplete-build-identity", "manifest must bind profile, build flags, and generated sources")

    states_list = loader.get("states", [])
    if len(states_list) != len(set(states_list)):
        raise ContractError("duplicate-loader-state", "loader states must be unique")
    states = set(states_list)
    required_states = {"created", "bootstrap-trust-established", "manifest-authenticated", "runtime-instantiated-main-suppressed", "immutable-release-mounted", "explicit-erts-entry-invoked", "runtime-identity-attested", "booted-for-qualification", "qualification-admission-consumed-and-closed", "ready", "cancelling", "all-generation-resources-revoked", "terminated"}
    if not required_states.issubset(states):
        raise ContractError("missing-loader-state", "loader state machine is incomplete")
    topology_rows = loader.get("topology_partial_orders", [])
    unique(topology_rows, "id", "duplicate-topology")
    if {row["id"] for row in topology_rows} != {"outer-dedicated-worker", "proxy-to-pthread"}:
        raise ContractError("topology-preselected", "both candidate topology partial orders are required")
    for row in topology_rows:
        if row.get("selection_state") != "candidate":
            raise ContractError("topology-preselected", "P0 may not select a Worker topology")
        edges = loader.get("common_partial_order", []) + row.get("edges", [])
        if not acyclic(states, edges):
            raise ContractError("circular-loader-order", f"{row['id']} loader order contains a cycle")

    boot = loader.get("boot_inputs", {})
    if boot.get("environment") != {} or boot.get("root") != "/runtime" or boot.get("cwd") != "/runtime":
        raise ContractError("unfixed-boot-input", "environment, root, and cwd must be fixed")
    if not boot.get("argv") or not boot.get("code_paths") or any("*" in path for path in boot.get("code_paths", [])):
        raise ContractError("unfixed-boot-input", "argv and explicit code paths are required without globs")
    modules = loader.get("module_policy", {})
    if modules.get("qualification_module") != "erts_wasm_loader_probe" or modules.get("post_ready") != "all code loading denied":
        raise ContractError("undeclared-module-policy", "qualification and post-ready loading policy are incomplete")
    if modules.get("qualification_in_boot_script") or modules.get("qualification_referenced_during_boot"):
        raise ContractError("qualification-preloaded", "qualification module must remain outside boot reachability")
    if "before native parsing" not in modules.get("closure_action", ""):
        raise ContractError("late-admission-closure", "admission must close before native parsing")

    failures = loader.get("failure_matrix", [])
    unique(failures, "id", "duplicate-loader-failure")
    required_failures = {"untrusted-manifest", "malformed-manifest", "stale-generation", "duplicate-start", "identity-skew", "out-of-bounds", "release-expansion-breach", "memory-profile-mismatch", "ambient-capability", "worker-descendant-load", "undeclared-module", "entry-before-mount", "partial-worker-graph", "trust-preflight-failure"}
    if {row["id"] for row in failures} != required_failures:
        raise ContractError("incomplete-failure-matrix", "loader failure matrix is incomplete")
    for row in failures:
        if not row.get("owner") or not row.get("action") or not row.get("detect"):
            raise ContractError("ownerless-loader-failure", f"{row['id']} lacks detection, owner, or action")

    ownership = loader.get("generation_ownership", {})
    if ownership.get("owner") != "page-supervisor" or not ownership.get("register_before_effect"):
        raise ContractError("unowned-generation", "page supervisor must register generation resources before effect")
    if "stored outside the immutable manifest" not in ownership.get("token", ""):
        raise ContractError("manifest-owned-generation-token", "runtime-generation tokens must be fresh external supervisor state")
    if trust.get("selected_policy") != "secure-origin-tcb-v1" or trust.get("self_authentication") is not False:
        raise ContractError("circular-root-trust", "root policy must not self-authenticate")
    if trust.get("service_worker_policy", "").find("fails preflight") < 0:
        raise ContractError("service-worker-ambiguity", "an active service worker must fail preflight")
    if trust.get("redirect_policy", "").find("error") < 0:
        raise ContractError("redirect-ambiguity", "redirects must fail")
    if trust.get("wasm_policy", "").find("verify the complete") < 0:
        raise ContractError("stream-before-trust", "Wasm must be fully verified before compile")
    if (
        "exact SHA-256 outside the manifest" not in trust.get("root", "")
        or "duplicate object names" not in trust.get("manifest_policy", "")
        or "credentials omit" not in trust.get("manifest_policy", "")
        or "identity content encoding" not in trust.get("manifest_policy", "")
    ):
        raise ContractError("incomplete-manifest-trust", "root trust must externally pin and strictly decode identity-encoded manifest bytes")
    if not all(term in trust.get("worker_integrity", "") for term in ("credentials omit", "identity content encoding", "importScripts", "child Workers")):
        raise ContractError("incomplete-worker-integrity", "Worker policy must prohibit credential and descendant executable authority")
    required_headers = {"Cross-Origin-Opener-Policy", "Cross-Origin-Embedder-Policy", "Cross-Origin-Resource-Policy", "Content-Security-Policy", "X-Content-Type-Options", "Cache-Control"}
    if set(trust.get("headers", {})) != required_headers:
        raise ContractError("missing-deployment-prerequisite", "required header policy is incomplete")

    unique(ledger.get("assets", []), "id", "duplicate-asset")
    unique(ledger.get("dependencies", []), "id", "duplicate-dependency")
    patch_stack = ledger.get("patch_stack", {})
    if patch_stack.get("patches") != [] or patch_stack.get("state") != "empty-baseline-frozen":
        raise ContractError("fabricated-patch-stack", "P0 must record that no implementation patch stack exists")
    if patch_stack.get("digest") != "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855":
        raise ContractError("invalid-empty-patch-digest", "empty patch stack must use the canonical empty-stream SHA-256")
    assignee = roles.get("assignee", {})
    if roles.get("contract_id") != "p0-role-assignments" or assignee.get("name") != "Pascal Charbonneau" or assignee.get("github") != "pcharbon70":
        raise ContractError("missing-role-assignment", "P0 review and experiment roles must bind the project owner's stable identity")
    review_roles = roles.get("review_roles", [])
    experiment_roles = roles.get("experiment_owner_roles", [])
    unique(review_roles, "id", "duplicate-review-role")
    unique(experiment_roles, "id", "duplicate-experiment-owner-role")
    required_review_roles = {
        "build-reproducibility-reviewer", "security-reviewer", "architecture-reviewer",
        "erts-c-port-reviewer", "runtime-concurrency-reviewer", "measurement-reviewer",
        "method-reviewer", "test-evidence-reviewer", "loader-protocol-reviewer",
        "c-browser-abi-reviewer", "browser-host-reviewer", "browser-wasm-reviewer",
        "lifecycle-reviewer", "memory-reviewer", "loader-runtime-reviewer",
        "loader-delivery-reviewer",
        "integration-reviewer", "milestone-reviewer",
    }
    required_experiment_roles = {
        "c-runtime-owner", "browser-host-owner", "beam-fixture-owner", "build-release-owner",
        "browser-test-owner", "deployment-owner", "update-owner", "runtime-owner",
        "renderer-owner", "compatibility-owner",
    }
    if {row["id"] for row in review_roles} != required_review_roles or {row["id"] for row in experiment_roles} != required_experiment_roles:
        raise ContractError("incomplete-role-assignment", "P0 reviewer and experiment-owner role sets are incomplete")
    if any(row.get("state") != "assigned-review-not-run" for row in review_roles) or any(row.get("state") != "assigned-work-not-started" for row in experiment_roles):
        raise ContractError("fabricated-role-completion", "role assignment must not claim completed review or experiment work")
    if "different independent reviewer" not in roles.get("independence_rule", ""):
        raise ContractError("missing-review-independence", "owner-produced evidence needs a different independent reviewer")
    assigned_owner = "Pascal Charbonneau (pcharbon70)"
    if any(row.get("source_owner") != assigned_owner for row in ledger.get("assets", [])) or any(row.get("owner") != assigned_owner for row in ledger.get("dependencies", [])) or patch_stack.get("owner") != assigned_owner:
        raise ContractError("unassigned-experiment-owner", "forecast assets, dependencies, and patch stack must bind the assigned experiment owner")
    if environment.get("reproduction_state") != "specified-not-run" or not environment.get("blockers"):
        raise ContractError("fabricated-empty-environment", "clean environment is specified but not reproduced")
    if not environment.get("deferred") or any("target probe" in blocker or "asset and patch digests" in blocker for blocker in environment.get("blockers", [])):
        raise ContractError("downstream-environment-blocker", "P1+ work must be deferred rather than required by P0 environment readiness")
    required_contracts = {
        "p0-baseline", "p0-trust-model", "p0-language-ownership",
        "p0-runtime-inventory", "p0-thread-census-contract",
        "p0-experiment-bounds", "p0-unsupported-matrix", "p0-loader-bounds",
        "p0-product-budget-method", "p0-evidence-profile",
        "p0-loader-contract", "p0-bootstrap-trust",
        "p0-asset-dependency-patch-ledger", "p0-role-assignments", "p0-empty-target-environment",
        "p0-phase-03-validation",
    }
    if set(acceptance.get("required_contracts", [])) != required_contracts:
        raise ContractError("missing-p0-contract", "P0 acceptance contract set is incomplete")
    required_deferred = {
        "successful C or Emscripten compilation",
        "built Wasm, generated JavaScript, Worker, release-pack, or qualification-BEAM artifacts",
        "ERTS or OTP browser boot",
        "browser runtime semantics, lifecycle, sanitizer, fuzz, or compatibility results",
        "a nonempty implementation patch stack",
        "numeric product budgets or appointment of their post-P6/pre-C1 authority",
    }
    if set(acceptance.get("downstream_not_required_for_p0", [])) != required_deferred:
        raise ContractError("missing-deferred-outcome", "P0 must enumerate downstream outcomes that cannot block entry")
    if report.get("review_complete") is not False or not report.get("blockers"):
        raise ContractError("missing-p0-blocker", "P0 report must retain unresolved review and execution blockers")
    assignment_report = report.get("role_assignment", {})
    if assignment_report.get("contract") != "p0-role-assignments" or assignment_report.get("assignee") != assigned_owner:
        raise ContractError("missing-role-assignment", "P0 acceptance report must bind the role-assignment contract")
    if any("owners are unassigned" in blocker for blocker in report.get("blockers", [])):
        raise ContractError("stale-owner-blocker", "assigned experiment owners cannot remain listed as a P0 blocker")
    forbidden_blocker_terms = ("no C/Emscripten compile", "product-budget authority", "product values", "runtime evidence")
    if any(any(term in blocker for term in forbidden_blocker_terms) for blocker in report.get("blockers", [])):
        raise ContractError("downstream-p0-blocker", "downstream implementation or product outcomes cannot block P0")
    if len(report.get("deferred_outcomes_not_blocking_p0", [])) != 6:
        raise ContractError("missing-deferred-outcome", "P0 report must preserve six downstream outcome classes")
    expected_partial_evidence = (
        "P0-A01: research/assets/p0-governed-baseline/phase-01/"
        "p0-phase-01-acceptance.planning-evidence.json; "
        "P0-A02: research/assets/p0-governed-baseline/phase-02/"
        "p0-phase-02-acceptance.planning-evidence.json; "
        "P0-A03 and P0-GATE: none"
    )
    local_results = report.get("local_contract_results", {})
    if local_results.get("P0-A01") != "passed-reviewed-evidence-bound" or local_results.get("P0-A02") != "passed-reviewed-evidence-bound":
        raise ContractError("stale-accepted-phase", "P0 acceptance report must retain passed P0-A01 and P0-A02 evidence state")
    if report.get("gate_state") != "blocked" or report.get("planning_evidence") != expected_partial_evidence:
        raise ContractError("premature-p0-closure", "P0 cannot close with unresolved blockers")
    negative_rows = validation.get("negative_cases", [])
    unique(negative_rows, "id", "duplicate-phase-03-negative")
    expected_negative_codes = {
        "mixed-manifest-identity", "self-authenticating-manifest", "stale-manifest-bounds",
        "manifest-bound-drift", "ambiguous-content-encoding", "ambient-poc-capability",
        "invalid-memory-page-rule", "incomplete-build-identity", "circular-loader-order",
        "manifest-owned-generation-token", "incomplete-failure-matrix", "circular-root-trust",
        "incomplete-manifest-trust", "incomplete-worker-integrity", "missing-deployment-prerequisite",
        "fabricated-role-completion", "fabricated-empty-environment", "downstream-p0-blocker",
        "premature-p0-closure",
    }
    if {row.get("expected_code") for row in negative_rows} != expected_negative_codes or len(negative_rows) != 20:
        raise ContractError("incomplete-phase-03-validation", "Phase 3 validation contract does not cover every reviewed rejection class")
    if len(validation.get("positive_assertions", [])) < 8 or not validation.get("acceptance_boundary"):
        raise ContractError("missing-phase-03-acceptance-boundary", "Phase 3 validation must preserve its non-acceptance boundary")

    receipt_path = root / "p0-phase-03-producer-review-receipt.json"
    packet_path = root / "p0-phase-03-owner-review-packet.json"
    if receipt_path.exists() or packet_path.exists():
        if not receipt_path.exists() or not packet_path.exists():
            raise ContractError("incomplete-review-packet", "Phase 3 producer receipt and owner packet must be published together")
        receipt = load_json(receipt_path)
        packet = load_json(packet_path)
        if receipt.get("review_state") != "ready-for-explicit-owner-disposition" or packet.get("state") != "ready-for-explicit-owner-disposition":
            raise ContractError("invalid-review-state", "Phase 3 review artifacts must await explicit owner disposition")
        entry = receipt.get("entry_evidence", {})
        if entry.get("gate") != "P0-A02" or entry.get("sha256") != sha256_file(P0_ROOT / "phase-02" / "p0-phase-02-acceptance.planning-evidence.json"):
            raise ContractError("stale-entry-evidence", "Phase 3 producer review must bind accepted P0-A02 evidence")
        for binding in receipt.get("reviewed_contracts", []):
            relative = Path(binding.get("path", ""))
            if not relative.name:
                raise ContractError("invalid-review-binding", "Phase 3 reviewed contract binding lacks a path")
            bound_path = root / relative.name
            if not bound_path.exists() or binding.get("sha256") != sha256_file(bound_path):
                raise ContractError("stale-producer-review", f"Phase 3 producer receipt does not bind {relative.name}")
        packet_receipt = packet.get("producer_review_receipt", {})
        requested = packet.get("explicit_disposition_requested", {})
        if packet_receipt.get("sha256") != sha256_file(receipt_path):
            raise ContractError("stale-owner-review-packet", "Phase 3 owner packet does not bind the producer receipt")
        if requested.get("acceptable_response") != "I accept the P0.3 owner-review packet and its recorded limitations.":
            raise ContractError("invalid-owner-review-request", "Phase 3 packet lacks the exact owner disposition request")

    owner_result_path = root / "p0-phase-03-owner-review-result.json"
    if owner_result_path.exists():
        owner_result = load_json(owner_result_path)
        if (
            owner_result.get("reviewer") != "Pascal Charbonneau (pcharbon70)"
            or owner_result.get("reviewer_statement") != "I accept the P0.3 owner-review packet and its recorded limitations."
            or owner_result.get("user_statement_verbatim") != "accept the P0.3 owner-review packet and its recorded limitations."
            or not owner_result.get("statement_normalization")
            or owner_result.get("outcome") != "accepted"
        ):
            raise ContractError("invalid-owner-attestation", "P0.3 owner result does not contain the exact accepted disposition")
        reviewed_packet = owner_result.get("reviewed_packet", {})
        producer_receipt = owner_result.get("producer_review_receipt", {})
        packet_path = root / "p0-phase-03-owner-review-packet.json"
        receipt_path = root / "p0-phase-03-producer-review-receipt.json"
        if reviewed_packet.get("sha256") != sha256_file(packet_path) or producer_receipt.get("sha256") != sha256_file(receipt_path):
            raise ContractError("stale-owner-attestation", "P0.3 owner result does not bind the reviewed packet and producer receipt")

    validate_phase_01()
    validate_phase_02()
    return ["manifest-schema", "loader-state-and-ownership", "bootstrap-trust", "asset-dependency-patch-ledger", "role-assignments", "empty-environment-contract", "blocked-p0-disposition"]


def main(argv: list[str]) -> int:
    phase = argv[1] if len(argv) > 1 else "phase-01"
    validators = {
        "phase-01": validate_phase_01,
        "phase-02": validate_phase_02,
        "phase-03": validate_phase_03,
    }
    if phase not in validators:
        print(f"unsupported phase: {phase}", file=sys.stderr)
        return 2
    try:
        validated = validators[phase]()
    except ContractError as exc:
        print(f"P0 contract validation failed [{exc.code}]: {exc}", file=sys.stderr)
        return 1
    print(f"P0 {phase} contract validation passed: {', '.join(validated)}")
    if phase == "phase-01":
        print("Acceptance status: P0-A01 passed by independent reviewed evidence")
    elif phase == "phase-02":
        evidence_path = P0_ROOT / "phase-02" / "p0-phase-02-acceptance.planning-evidence.json"
        owner_result_path = P0_ROOT / "phase-02" / "p0-phase-02-owner-review-result.json"
        if evidence_path.exists():
            print("Acceptance status: P0-A02 passed by independent reviewed evidence")
        elif owner_result_path.exists():
            print("Acceptance status: owner review accepted; clean pass-closing evidence pending")
        else:
            print("Acceptance status: independent review pending; P0-A02 remains open")
    else:
        print("Acceptance status: P0-A01 and P0-A02 passed; P0-A03 and P0-GATE remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
