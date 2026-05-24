"""Workspace path resolver. Single source of truth for canonical filesystem layout."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WorkspacePaths:
    root: Path

    @property
    def memory_dir(self) -> Path:
        return self.root / "memory"

    @property
    def fact_yml(self) -> Path:
        return self.memory_dir / "fact.yml"

    @property
    def fact_audit(self) -> Path:
        return self.memory_dir / ".fact_audit.jsonl"

    @property
    def episodic(self) -> Path:
        return self.memory_dir / "episodic.jsonl"

    @property
    def associations(self) -> Path:
        return self.memory_dir / "associations.jsonl"

    @property
    def graph_db(self) -> Path:
        return self.memory_dir / "graph.db"

    @property
    def brain_region_manifest(self) -> Path:
        return self.memory_dir / "brain_region_manifest.yml"

    @property
    def sanctum_registry(self) -> Path:
        return self.memory_dir / "sanctum_registry.yml"

    @property
    def runtime_profiles(self) -> Path:
        return self.memory_dir / "runtime_profiles.yml"

    @property
    def memory_manifest(self) -> Path:
        return self.memory_dir / "memory_manifest.yml"

    @property
    def config(self) -> Path:
        return self.root / ".gish" / "config.yml"

    @property
    def logs_dir(self) -> Path:
        return self.root / ".gish" / "logs"


def resolve_workspace(path: Path) -> Path:
    """Validate a workspace path and return its absolute form."""
    path = path.expanduser()
    if not path.is_dir():
        raise NotADirectoryError(f"workspace not a directory: {path}")
    return path.resolve()
