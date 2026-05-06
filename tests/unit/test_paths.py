"""Tests for ghost_in_shell.memory._paths — workspace path resolver."""

from pathlib import Path

import pytest

from ghost_in_shell.memory._paths import WorkspacePaths, resolve_workspace


def test_workspace_paths_dataclass_has_known_files(tmp_workspace: Path):
    paths = WorkspacePaths(tmp_workspace)
    assert paths.root == tmp_workspace
    assert paths.fact_yml == tmp_workspace / "memory" / "fact.yml"
    assert paths.episodic == tmp_workspace / "memory" / "episodic.jsonl"
    assert paths.associations == tmp_workspace / "memory" / "associations.jsonl"
    assert paths.graph_db == tmp_workspace / "memory" / "graph.db"
    assert paths.brain_region_manifest == tmp_workspace / "memory" / "brain_region_manifest.yml"
    assert paths.sanctum_registry == tmp_workspace / "memory" / "sanctum_registry.yml"
    assert paths.runtime_profiles == tmp_workspace / "memory" / "runtime_profiles.yml"
    assert paths.memory_manifest == tmp_workspace / "memory" / "memory_manifest.yml"
    assert paths.config == tmp_workspace / ".gish" / "config.yml"
    assert paths.fact_audit == tmp_workspace / "memory" / ".fact_audit.jsonl"


def test_resolve_workspace_rejects_non_directory(tmp_path: Path):
    not_a_dir = tmp_path / "missing"
    with pytest.raises(NotADirectoryError):
        resolve_workspace(not_a_dir)


def test_resolve_workspace_returns_absolute(tmp_workspace: Path):
    resolved = resolve_workspace(tmp_workspace)
    assert resolved.is_absolute()
    assert resolved == tmp_workspace.resolve()
