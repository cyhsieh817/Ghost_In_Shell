"""Shared pytest fixtures for ghost_in_shell tests."""

from pathlib import Path

import pytest


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Path:
    """A blank workspace directory under pytest's tmp_path."""
    ws = tmp_path / "workspace"
    ws.mkdir()
    (ws / "memory").mkdir()
    (ws / ".gish").mkdir()
    return ws


@pytest.fixture
def repo_root() -> Path:
    """Absolute path to the Ghost_In_Shell repo root."""
    return Path(__file__).resolve().parents[1]
