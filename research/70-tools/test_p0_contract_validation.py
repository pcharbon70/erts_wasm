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

    def test_unmaterialized_pin_is_rejected(self) -> None:
        self.mutate(
            "p0-baseline-lock.json",
            lambda value: value["pins"][1].update(materialization_state="required-not-materialized"),
        )
        self.assert_code("unmaterialized-pin")

    def test_missing_browser_digest_is_rejected(self) -> None:
        self.mutate("p0-baseline-lock.json", lambda value: value["pins"][8].update(archive_sha256=""))
        self.assert_code("missing-browser-digest")

    def test_duplicate_authority_is_rejected(self) -> None:
        def duplicate(value: dict) -> None:
            value["zones"].append(copy.deepcopy(value["zones"][0]))

        self.mutate("p0-trust-scope-matrix.json", duplicate)
        self.assert_code("duplicate-authority")

    def test_unassigned_trust_owner_is_rejected(self) -> None:
        self.mutate("p0-trust-scope-matrix.json", lambda value: value["zones"][0].update(owner="deployment-owner-unassigned"))
        self.assert_code("unassigned-trust-owner")

    def test_unassigned_language_owner_is_rejected(self) -> None:
        self.mutate("p0-language-ownership.json", lambda value: value["owners"][0].update(abi_owner="c-runtime-owner-unassigned"))
        self.assert_code("unassigned-language-owner")

    def test_missing_typescript_toolchain_pin_is_rejected(self) -> None:
        self.mutate("p0-language-ownership.json", lambda value: value.pop("browser_host_toolchain"))
        self.assert_code("missing-typescript-toolchain-pin")

    def test_unassigned_census_reviewer_is_rejected(self) -> None:
        self.mutate("p0-thread-census-contract.json", lambda value: value["owners"].update(review="runtime-concurrency-reviewer-unassigned"))
        self.assert_code("unassigned-census-reviewer")

    def test_missing_runtime_category_is_rejected(self) -> None:
        self.mutate("p0-runtime-inventory.json", lambda value: value["categories"].pop())
        self.assert_code("missing-runtime-category")

    def test_stale_runtime_source_path_is_rejected(self) -> None:
        self.mutate(
            "p0-runtime-inventory.json",
            lambda value: value["categories"][8]["source_paths"].append("erts/emulator/beam/erl_driver.c"),
        )
        self.assert_code("stale-runtime-path")

    def test_stale_preload_count_is_rejected(self) -> None:
        self.mutate(
            "p0-runtime-inventory.json",
            lambda value: value["categories"][3].update(findings=["23 preloaded Erlang source modules are present"]),
        )
        self.assert_code("stale-preload-count")

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

    def test_unrecorded_randomization_is_rejected(self) -> None:
        self.mutate("p0-experiment-bounds.json", lambda value: value["series"].update(randomization_seed_rule=""))
        self.assert_code("unreproducible-randomization")

    def test_experiment_bound_without_enforcement_is_rejected(self) -> None:
        self.mutate("p0-experiment-bounds.json", lambda value: value["safety_ceilings"][0].update(enforcement_point=""))
        self.assert_code("missing-enforcement-point")

    def test_missing_resource_owner_is_rejected(self) -> None:
        self.mutate("p0-loader-startup-bounds.json", lambda value: value["bounds"][0].update(owner=""))
        self.assert_code("missing-owner")

    def test_missing_breach_action_is_rejected(self) -> None:
        self.mutate("p0-loader-startup-bounds.json", lambda value: value["bounds"][0].update(breach_action=""))
        self.assert_code("missing-breach-action")

    def test_missing_expanded_release_bound_is_rejected(self) -> None:
        self.mutate(
            "p0-loader-startup-bounds.json",
            lambda value: value["bounds"].__setitem__(slice(None), [item for item in value["bounds"] if item["id"] != "release-expanded-bytes"]),
        )
        self.assert_code("missing-loader-bound")

    def test_growable_poc_memory_is_rejected(self) -> None:
        self.mutate(
            "p0-loader-startup-bounds.json",
            lambda value: next(item for item in value["bounds"] if item["id"] == "initial-shared-memory").update(limit=268435456),
        )
        self.assert_code("growable-poc-memory")

    def test_cross_contract_safety_bound_drift_is_rejected(self) -> None:
        self.mutate(
            "p0-loader-startup-bounds.json",
            lambda value: next(item for item in value["bounds"] if item["id"] == "worker-agents").update(limit=63),
        )
        self.assert_code("inconsistent-safety-bound")

    def test_infinite_or_nonfinite_series_is_rejected(self) -> None:
        self.mutate("p0-experiment-bounds.json", lambda value: value["series"].update(maximum_total_cycles_per_run=0))
        self.assert_code("infinite-test-series")

    def test_silent_instrumentation_omission_is_rejected(self) -> None:
        self.mutate("p0-evidence-profiles.json", lambda value: value["profiles"].pop())
        self.assert_code("silent-instrumentation-omission")

    def test_c_sanitizers_on_typescript_host_profile_are_rejected(self) -> None:
        self.mutate(
            "p0-evidence-profiles.json",
            lambda value: next(item for item in value["profiles"] if item["id"] == "browser-host-fuzz").update(sanitizers=["address"]),
        )
        self.assert_code("wrong-host-instrumentation")

    def test_missing_profile_toolchain_is_rejected(self) -> None:
        self.mutate("p0-evidence-profiles.json", lambda value: value["toolchains"].pop("typescript"))
        self.assert_code("incomplete-evidence-toolchain")

    def test_orphaned_fuzz_failure_is_rejected(self) -> None:
        self.mutate("p0-evidence-profiles.json", lambda value: value["failure_minimization"].pop("orphan_rule"))
        self.assert_code("orphaned-fuzz-failure")

    def test_copying_safety_ceiling_to_product_budget_is_rejected(self) -> None:
        self.mutate("p0-product-budget-method.json", lambda value: value.update(forbidden_derivations=[]))
        self.assert_code("copied-safety-ceiling")

    def test_post_result_statistical_selection_is_rejected(self) -> None:
        self.mutate(
            "p0-product-budget-method.json",
            lambda value: value.update(forbidden_derivations=["copy an experimental safety ceiling"]),
        )
        self.assert_code("post-result-selection")

    def test_missing_required_unsupported_operation_is_rejected(self) -> None:
        self.mutate("p0-unsupported-operations.json", lambda value: value["operations"].pop())
        self.assert_code("missing-unsupported-operation")

    def test_missing_rebuild_comparison_is_rejected(self) -> None:
        self.mutate("p0-evidence-profiles.json", lambda value: value.pop("reproducibility"))
        self.assert_code("missing-rebuild-comparison")

    def test_incomplete_validation_contract_is_rejected(self) -> None:
        self.mutate("p0-phase-02-validation-contract.json", lambda value: value["negative_cases"].pop())
        self.assert_code("incomplete-validation-contract")

    def test_invalid_owner_attestation_is_rejected(self) -> None:
        self.mutate("p0-phase-02-owner-review-result.json", lambda value: value.update(reviewer_statement="accepted"))
        self.assert_code("invalid-owner-attestation")


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

    def test_self_authenticating_manifest_is_rejected(self) -> None:
        self.mutate(
            "p0-runtime-manifest.schema.json",
            lambda value: value["properties"]["trust"]["required"].append("manifest_digest"),
        )
        self.assert_code("self-authenticating-manifest")

    def test_stale_bounds_digest_is_rejected(self) -> None:
        self.mutate(
            "p0-runtime-manifest.schema.json",
            lambda value: value["x-p0-bound-bindings"].update(contract_sha256="0" * 64),
        )
        self.assert_code("stale-manifest-bounds")

    def test_missing_bound_binding_is_rejected(self) -> None:
        self.mutate("p0-runtime-manifest.schema.json", lambda value: value["x-p0-bound-bindings"]["bound_ids"].pop())
        self.assert_code("stale-manifest-bounds")

    def test_manifest_bound_drift_is_rejected(self) -> None:
        self.mutate(
            "p0-runtime-manifest.schema.json",
            lambda value: value["properties"]["bounds"]["properties"]["pre_ready_message_bytes"].update(maximum=1),
        )
        self.assert_code("manifest-bound-drift")

    def test_ambient_poc_capability_is_rejected(self) -> None:
        self.mutate("p0-runtime-manifest.schema.json", lambda value: value["properties"]["capabilities"].update(maxItems=1))
        self.assert_code("ambient-poc-capability")

    def test_incomplete_build_identity_is_rejected(self) -> None:
        self.mutate("p0-runtime-manifest.schema.json", lambda value: value["properties"]["sources"]["required"].remove("build_flags_digest"))
        self.assert_code("incomplete-build-identity")

    def test_ownerless_loader_failure_is_rejected(self) -> None:
        self.mutate("p0-loader-contract.json", lambda value: value["failure_matrix"][0].update(owner=""))
        self.assert_code("ownerless-loader-failure")

    def test_manifest_owned_generation_token_is_rejected(self) -> None:
        self.mutate("p0-loader-contract.json", lambda value: value["generation_ownership"].update(token="manifest generation field"))
        self.assert_code("manifest-owned-generation-token")

    def test_undeclared_module_policy_is_rejected(self) -> None:
        self.mutate("p0-loader-contract.json", lambda value: value["module_policy"].update(qualification_module="other"))
        self.assert_code("undeclared-module-policy")

    def test_missing_deployment_header_is_rejected(self) -> None:
        self.mutate("p0-bootstrap-trust.json", lambda value: value["headers"].pop("Cross-Origin-Opener-Policy"))
        self.assert_code("missing-deployment-prerequisite")

    def test_incomplete_worker_integrity_is_rejected(self) -> None:
        self.mutate("p0-bootstrap-trust.json", lambda value: value.update(worker_integrity="verify bytes"))
        self.assert_code("incomplete-worker-integrity")

    def test_premature_gate_closure_is_rejected(self) -> None:
        self.mutate("p0-acceptance-report.json", lambda value: value.update(gate_state="passed"))
        self.assert_code("premature-p0-closure")

    def test_missing_partial_p0_a01_evidence_is_rejected(self) -> None:
        self.mutate("p0-acceptance-report.json", lambda value: value.update(planning_evidence="none"))
        self.assert_code("invalid-p0-a03-evidence")

    def test_missing_project_owner_assignment_is_rejected(self) -> None:
        self.mutate("p0-role-assignments.json", lambda value: value["assignee"].update(github=""))
        self.assert_code("missing-role-assignment")

    def test_role_assignment_cannot_claim_review_completion(self) -> None:
        self.mutate("p0-role-assignments.json", lambda value: value["review_roles"][0].update(state="completed"))
        self.assert_code("fabricated-role-completion")

    def test_stale_unassigned_owner_blocker_is_rejected(self) -> None:
        self.mutate(
            "p0-acceptance-report.json",
            lambda value: value["blockers"].append("immediate P1 experiment owners are unassigned"),
        )
        self.assert_code("stale-owner-blocker")

    def test_accepted_phase_evidence_state_cannot_regress(self) -> None:
        self.mutate(
            "p0-acceptance-report.json",
            lambda value: value["local_contract_results"].__setitem__("P0-A02", "pass-local-review-pending"),
        )
        self.assert_code("stale-accepted-phase")

    def test_downstream_runtime_work_cannot_be_a_p0_blocker(self) -> None:
        self.mutate(
            "p0-acceptance-report.json",
            lambda value: value["blockers"].append("no C/Emscripten compile or runtime evidence exists"),
        )
        self.assert_code("downstream-p0-blocker")

    def test_downstream_environment_work_cannot_block_p0(self) -> None:
        self.mutate(
            "p0-empty-environment-contract.json",
            lambda value: value["blockers"].append("target probe does not exist"),
        )
        self.assert_code("downstream-environment-blocker")

    def test_incomplete_phase_03_validation_contract_is_rejected(self) -> None:
        self.mutate("p0-phase-03-validation-contract.json", lambda value: value["negative_cases"].pop())
        self.assert_code("incomplete-phase-03-validation")

    def test_invalid_phase_03_owner_attestation_is_rejected(self) -> None:
        self.mutate("p0-phase-03-owner-review-result.json", lambda value: value.update(reviewer_statement="accepted"))
        self.assert_code("invalid-owner-attestation")

    def test_product_budget_authority_is_deferred_not_fabricated(self) -> None:
        product_root = Path(self.temp_dir.name) / "phase-02"
        shutil.copytree(P0_ROOT / "phase-02", product_root)
        path = product_root / "p0-product-budget-method.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["authority"] = "p0-reviewer"
        path.write_text(json.dumps(value), encoding="utf-8")
        with self.assertRaises(ContractError) as raised:
            validate_phase_02(product_root)
        self.assertEqual("fabricated-product-authority", raised.exception.code)


if __name__ == "__main__":
    unittest.main()
