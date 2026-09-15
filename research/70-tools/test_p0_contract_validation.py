"""Focused tests for P0 contract consistency and deterministic rejection."""

from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from p0_contract_validation import ContractError, P0_ROOT, validate_phase_01


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


if __name__ == "__main__":
    unittest.main()
