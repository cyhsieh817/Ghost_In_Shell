"""Shared pytest fixtures for ghost_in_shell tests."""

from pathlib import Path

import pytest

from ghost_in_shell.memory._paths import WorkspacePaths


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
