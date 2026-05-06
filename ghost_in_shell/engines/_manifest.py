"""memory_manifest.yml read/write helper. Used by every engine."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from ghost_in_shell.memory._paths import WorkspacePaths
from ghost_in_shell.memory._safe_io import atomic_write_text


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def load_manifest(paths: WorkspacePaths) -> dict[str, Any]:
    if not paths.memory_manifest.exists():
        return {
            "schema_version": 1,
            "last_consolidation": None,
            "last_decay_run": None,
            "last_audit_run": None,
            "last_health_run": None,
            "stats": {},
            "next_consolidation_trigger": {"type": "count", "threshold": 20, "last_count": 0},
            "consolidation_history": [],
            "quality_history": [],
        }
    return yaml.safe_load(paths.memory_manifest.read_text(encoding="utf-8")) or {}


def save_manifest(paths: WorkspacePaths, data: dict[str, Any]) -> None:
    atomic_write_text(paths.memory_manifest, yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


def stamp_run(paths: WorkspacePaths, engine_name: str) -> None:
    """Update last_<engine>_run timestamp in manifest."""
    key = f"last_{engine_name}_run"
    data = load_manifest(paths)
    data[key] = _now_iso()
    save_manifest(paths, data)
