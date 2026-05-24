"""Shared pytest fixtures for gshell_memory tests."""

import sys
from pathlib import Path

import pytest

from gshell_memory.memory._paths import WorkspacePaths

MIN_PY = (3, 11)


def pytest_configure(config: pytest.Config) -> None:
    if sys.version_info < MIN_PY:
        raise pytest.UsageError(
            f"gshell-memory requires Python >= {MIN_PY[0]}.{MIN_PY[1]} "
            f"(found {sys.version_info.major}.{sys.version_info.minor}). "
            "Activate a 3.11+ venv before running pytest."
        )


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Path:
    """A blank workspace directory under pytest's tmp_path."""
    ws = tmp_path / "workspace"
    ws.mkdir()
    (ws / "memory").mkdir()
    (ws / ".gish").mkdir()
    return ws


@pytest.fixture
def tmp_paths(tmp_workspace: Path) -> WorkspacePaths:
    """WorkspacePaths wrapping the blank tmp_workspace."""
    return WorkspacePaths(tmp_workspace)


@pytest.fixture
def repo_root() -> Path:
    """Absolute path to the Ghost_In_Shell repo root."""
    return Path(__file__).resolve().parents[1]
