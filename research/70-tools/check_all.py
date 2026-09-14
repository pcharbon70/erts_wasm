#!/usr/bin/env python3
"""Run all checks for the repository's nested research corpus."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


TOOLS_ROOT = Path(__file__).resolve().parent


def run(command: list[str]) -> int:
    """Run one check from the corpus root and return its exit status."""

    completed = subprocess.run(command, cwd=TOOLS_ROOT.parent, check=False)
    return completed.returncode


def main() -> int:
    checks = [
        [sys.executable, str(TOOLS_ROOT / "validate_archive.py")],
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(TOOLS_ROOT),
            "-p",
            "test_validate_archive.py",
        ],
    ]
    return 0 if all(run(command) == 0 for command in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
