"""Stable repository paths for research tools, independent of the caller's cwd."""

from pathlib import Path

TOOLS_ROOT = Path(__file__).resolve().parent
RESEARCH_ROOT = TOOLS_ROOT.parent
REPO_ROOT = RESEARCH_ROOT


def tool_path(repo_root: Path, name: str) -> Path:
    """Resolve a current tool, or the original location in an old Git snapshot."""
    if Path(name).name != name or not name.endswith(".py"):
        raise ValueError("expected a Python tool basename")
    root = Path(repo_root)
    return root / "70-tools" / name
