"""Focused tests for P0 contract consistency and deterministic rejection."""

from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from p0_contract_validation import ContractError, P0_ROOT, validate_phase_01, validate_phase_02, validate_phase_03


class Phase01ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "phase-01"
        shutil.copytree(P0_ROOT / "phase-01", self.root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def mutate(self, name: str, mutation) -> None:
        path = self.root / name
        value = json.loads(path.read_text(encoding="utf-8"))
        mutation(value)
        path.write_text(json.dumps(value), encoding="utf-8")

    def assert_code(self, expected: str) -> None:
        with self.assertRaises(ContractError) as raised:
            validate_phase_01(self.root)
        self.assertEqual(expected, raised.exception.code)

    def test_authored_contract_passes_local_validation(self) -> None:
        self.assertEqual(
            ["pins", "trust-boundary", "language-ownership", "runtime-inventory", "thread-census"],
            validate_phase_01(self.root),
        )

    def test_floating_version_is_rejected(self) -> None:
        self.mutate("p0-baseline-lock.json", lambda value: value["pins"][3].update(version="latest"))
        self.assert_code("floating-pin")

    def test_duplicate_authority_is_rejected(self) -> None:
        def duplicate(value: dict) -> None:
            value["zones"].append(copy.deepcopy(value["zones"][0]))

        self.mutate("p0-trust-scope-matrix.json", duplicate)
        self.assert_code("duplicate-authority")

    def test_missing_runtime_category_is_rejected(self) -> None:
        self.mutate("p0-runtime-inventory.json", lambda value: value["categories"].pop())
        self.assert_code("missing-runtime-category")

    def test_topology_selected_census_is_rejected(self) -> None:
        self.mutate(
            "p0-thread-census-contract.json",
            lambda value: value["pool_size_rule"].update(source="selected-topology"),
        )
        self.assert_code("topology-selected-census")

    def test_scheduler_derived_pool_is_rejected(self) -> None:
        self.mutate(
            "p0-thread-census-contract.json",
            lambda value: value["pool_size_rule"].update(forbidden_sources=[]),
        )
        self.assert_code("scheduler-derived-pool")


class Phase02ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "phase-02"
        shutil.copytree(P0_ROOT / "phase-02", self.root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def mutate(self, name: str, mutation) -> None:
        path = self.root / name
        value = json.loads(path.read_text(encoding="utf-8"))
        mutation(value)
        path.write_text(json.dumps(value), encoding="utf-8")

    def assert_code(self, expected: str) -> None:
        with self.assertRaises(ContractError) as raised:
            validate_phase_02(self.root)
        self.assertEqual(expected, raised.exception.code)

    def test_authored_contract_passes_local_validation(self) -> None:
        self.assertEqual(
            ["experiment-bounds", "unsupported-operations", "loader-bounds", "product-budget-method", "evidence-profiles"],
            validate_phase_02(self.root),
        )

    def test_post_result_threshold_edit_is_rejected(self) -> None:
        self.mutate("p0-experiment-bounds.json", lambda value: value.update(frozen_before_runtime_measurement=False))
        self.assert_code("post-result-threshold-edit")

    def test_missing_resource_owner_is_rejected(self) -> None:
        self.mutate("p0-loader-startup-bounds.json", lambda value: value["bounds"][0].update(owner=""))
        self.assert_code("missing-owner")

    def test_missing_breach_action_is_rejected(self) -> None:
        self.mutate("p0-loader-startup-bounds.json", lambda value: value["bounds"][0].update(breach_action=""))
        self.assert_code("missing-breach-action")

    def test_infinite_or_nonfinite_series_is_rejected(self) -> None:
        self.mutate("p0-experiment-bounds.json", lambda value: value["series"].update(maximum_total_cycles_per_run=0))
        self.assert_code("infinite-test-series")

    def test_silent_instrumentation_omission_is_rejected(self) -> None:
        self.mutate("p0-evidence-profiles.json", lambda value: value["profiles"].pop())
        self.assert_code("silent-instrumentation-omission")

    def test_orphaned_fuzz_failure_is_rejected(self) -> None:
        self.mutate("p0-evidence-profiles.json", lambda value: value["failure_minimization"].pop("orphan_rule"))
        self.assert_code("orphaned-fuzz-failure")

    def test_copying_safety_ceiling_to_product_budget_is_rejected(self) -> None:
        self.mutate("p0-product-budget-method.json", lambda value: value.update(forbidden_derivations=[]))
        self.assert_code("copied-safety-ceiling")


class Phase03ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "phase-03"
        shutil.copytree(P0_ROOT / "phase-03", self.root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def mutate(self, name: str, mutation) -> None:
        path = self.root / name
        value = json.loads(path.read_text(encoding="utf-8"))
        mutation(value)
        path.write_text(json.dumps(value), encoding="utf-8")

    def assert_code(self, expected: str) -> None:
        with self.assertRaises(ContractError) as raised:
            validate_phase_03(self.root)
        self.assertEqual(expected, raised.exception.code)

    def test_authored_contract_has_blocked_not_passing_gate(self) -> None:
        self.assertEqual("blocked-p0-disposition", validate_phase_03(self.root)[-1])

    def test_circular_loader_order_is_rejected(self) -> None:
        self.mutate("p0-loader-contract.json", lambda value: value["common_partial_order"].append(["ready", "created"]))
        self.assert_code("circular-loader-order")

    def test_circular_root_trust_is_rejected(self) -> None:
        self.mutate("p0-bootstrap-trust.json", lambda value: value.update(self_authentication=True))
        self.assert_code("circular-root-trust")

    def test_mixed_manifest_identity_is_rejected(self) -> None:
        self.mutate("p0-runtime-manifest.schema.json", lambda value: value["properties"]["format"].update(const="erts-wasm-manifest-v2"))
        self.assert_code("mixed-manifest-identity")

    def test_ownerless_loader_failure_is_rejected(self) -> None:
        self.mutate("p0-loader-contract.json", lambda value: value["failure_matrix"][0].update(owner=""))
        self.assert_code("ownerless-loader-failure")

    def test_undeclared_module_policy_is_rejected(self) -> None:
        self.mutate("p0-loader-contract.json", lambda value: value["module_policy"].update(qualification_module="other"))
        self.assert_code("undeclared-module-policy")

    def test_missing_deployment_header_is_rejected(self) -> None:
        self.mutate("p0-bootstrap-trust.json", lambda value: value["headers"].pop("Cross-Origin-Opener-Policy"))
        self.assert_code("missing-deployment-prerequisite")

    def test_premature_gate_closure_is_rejected(self) -> None:
        self.mutate("p0-acceptance-report.json", lambda value: value.update(gate_state="passed"))
        self.assert_code("premature-p0-closure")


if __name__ == "__main__":
    unittest.main()
