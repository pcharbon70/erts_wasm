"""Stable repository paths for research tools, independent of the caller's cwd."""

from pathlib import Path

TOOLS_ROOT = Path(__file__).resolve().parent
RESEARCH_ROOT = TOOLS_ROOT.parent
REPO_ROOT = RESEARCH_ROOT.parent


def tool_path(research_root: Path, name: str) -> Path:
    """Resolve a validator tool below a research-corpus root."""
    if Path(name).name != name or not name.endswith(".py"):
        raise ValueError("expected a Python tool basename")
    root = Path(research_root)
    return root / "70-tools" / name
