#!/usr/bin/env python3
"""Validate authored P0 contracts without treating them as acceptance evidence."""

from __future__ import annotations

import json
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

    zones = trust.get("zones", [])
    unique(zones, "id", "duplicate-authority")
    if trust.get("import_abi", {}).get("default") != "deny":
        raise ContractError("ambient-authority", "import ABI must deny by default")
    if not trust.get("stop_conditions") or not trust.get("quota_owners"):
        raise ContractError("incomplete-trust-model", "stop conditions and quota owners are required")

    language_rows = languages.get("owners", [])
    unique(language_rows, "language", "duplicate-language-owner")
    required_languages = {"C", "TypeScript", "Erlang", "Elixir", "Rust", "C++"}
    if {row["language"] for row in language_rows} != required_languages:
        raise ContractError("missing-language-owner", "language ownership set is incomplete")
    if languages.get("adr_state") != "proposed":
        raise ContractError("premature-adr-acceptance", "ADR-0001 must remain proposed until P1 evidence")

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

    pool_rule = census.get("pool_size_rule", {})
    if pool_rule.get("source") != "measured-full-runtime-high-water-plus-declared-headroom":
        raise ContractError("topology-selected-census", "pool size must derive from full-runtime measurement")
    if "+S scheduler count" not in pool_rule.get("forbidden_sources", []):
        raise ContractError("scheduler-derived-pool", "+S must be an explicit forbidden pool-size source")
    experiment_ids = {item.get("id") for item in census.get("experiments", [])}
    if experiment_ids != {"P0-THREAD-N", "P0-THREAD-N-1"}:
        raise ContractError("missing-n-minus-one", "thread census needs N and N-1 experiments")

    return ["pins", "trust-boundary", "language-ownership", "runtime-inventory", "thread-census"]


def finite_positive(value: object, code: str, label: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise ContractError(code, f"{label} must be a finite positive number")


def validate_phase_02(root: Path = P0_ROOT / "phase-02") -> list[str]:
    experiments = load_json(root / "p0-experiment-bounds.json")
    unsupported = load_json(root / "p0-unsupported-operations.json")
    loader = load_json(root / "p0-loader-startup-bounds.json")
    product = load_json(root / "p0-product-budget-method.json")
    evidence = load_json(root / "p0-evidence-profiles.json")

    series = experiments.get("series", {})
    for field in ("cold_boot_attempts", "warmup_cycles_discarded", "measured_boot_dispose_cycles", "maximum_total_cycles_per_run"):
        finite_positive(series.get(field), "infinite-test-series", field)
    if sum(series[field] for field in ("cold_boot_attempts", "warmup_cycles_discarded", "measured_boot_dispose_cycles")) > series["maximum_total_cycles_per_run"]:
        raise ContractError("inconsistent-test-series", "component cycle counts exceed the total ceiling")
    if not experiments.get("frozen_before_runtime_measurement"):
        raise ContractError("post-result-threshold-edit", "experiment bounds must be frozen before measurement")
    ceilings = experiments.get("safety_ceilings", [])
    unique(ceilings, "id", "duplicate-experiment-bound")
    for item in ceilings:
        finite_positive(item.get("limit"), "unbounded-resource", item.get("id", "resource"))
        for field in ("unit", "owner", "breach_action"):
            if not item.get(field):
                raise ContractError(f"missing-{field.replace('_', '-')}", f"{item['id']} lacks {field}")

    operations = unsupported.get("operations", [])
    unique(operations, "id", "duplicate-unsupported-operation")
    for item in operations:
        for field in ("request_surface", "owner", "expected_result"):
            if not item.get(field):
                raise ContractError(f"missing-{field.replace('_', '-')}", f"{item['id']} lacks {field}")

    bounds = loader.get("bounds", [])
    unique(bounds, "id", "duplicate-loader-bound")
    required_resources = {"manifest-bytes", "artifact-count", "artifact-bytes", "aggregate-artifact-bytes", "path-bytes", "worker-agents", "shared-memory", "pre-ready-message-queue", "concurrent-fetches", "startup-timers", "startup-wall-clock"}
    if not required_resources.issubset({item["id"] for item in bounds}):
        raise ContractError("missing-loader-bound", "loader/startup bounds omit a required resource")
    for item in bounds:
        finite_positive(item.get("limit"), "unbounded-resource", item.get("id", "resource"))
        for field in ("resource", "owner", "unit", "enforcement_point", "mechanism", "breach_action"):
            if not item.get(field):
                raise ContractError(f"missing-{field.replace('_', '-')}", f"{item['id']} lacks {field}")

    if product.get("numeric_product_budgets") is not None:
        raise ContractError("premature-product-budget", "numeric product budgets require the actual authority")
    if product.get("authority") != "unassigned" or product.get("approval_state") != "blocked-authority-unassigned":
        raise ContractError("fabricated-product-authority", "product authority must remain explicitly unassigned")
    if "copy an experimental safety ceiling" not in product.get("forbidden_derivations", []):
        raise ContractError("copied-safety-ceiling", "product method must prohibit copying safety ceilings")

    profiles = evidence.get("profiles", [])
    unique(profiles, "id", "duplicate-evidence-profile")
    required_profiles = {"native-debug", "native-release", "wasm-debug", "wasm-release", "host-parser-fuzz", "c-boundary-fuzz"}
    if {item["id"] for item in profiles} != required_profiles:
        raise ContractError("silent-instrumentation-omission", "required evidence profile set is incomplete")
    if not evidence.get("unsupported_combination_rule"):
        raise ContractError("silent-sanitizer-omission", "unsupported instrumentation needs an explicit disposition")
    if not evidence.get("failure_minimization", {}).get("orphan_rule"):
        raise ContractError("orphaned-fuzz-failure", "fuzz failures require retained ownership and reproduction")

    return ["experiment-bounds", "unsupported-operations", "loader-bounds", "product-budget-method", "evidence-profiles"]


def main(argv: list[str]) -> int:
    phase = argv[1] if len(argv) > 1 else "phase-01"
    validators = {"phase-01": validate_phase_01, "phase-02": validate_phase_02}
    if phase not in validators:
        print(f"unsupported phase: {phase}", file=sys.stderr)
        return 2
    try:
        validated = validators[phase]()
    except ContractError as exc:
        print(f"P0 contract validation failed [{exc.code}]: {exc}", file=sys.stderr)
        return 1
    print(f"P0 {phase} contract validation passed: {', '.join(validated)}")
    print("Acceptance status: independent review pending; no P0 gate closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
