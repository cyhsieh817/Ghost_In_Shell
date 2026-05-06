"""Health engine — report workspace integrity metrics (spec § 4.7)."""

from __future__ import annotations

import datetime
from pathlib import Path

from ghost_in_shell.engines._manifest import load_manifest, save_manifest, stamp_run
from ghost_in_shell.memory._paths import WorkspacePaths, resolve_workspace
from ghost_in_shell.memory._safe_io import read_jsonl


def run(workspace: Path, *, dry_run: bool = False) -> dict:
    """Scan the workspace and return a health report.

    Returns a dict with counts of episodes, edges, issues, and overall status.
    """
    paths = WorkspacePaths(resolve_workspace(workspace))
    ts = datetime.datetime.now(datetime.UTC).isoformat()

    episode_count = sum(1 for _ in read_jsonl(paths.episodic)) if paths.episodic.exists() else 0
    edge_count = sum(1 for _ in read_jsonl(paths.associations)) if paths.associations.exists() else 0

    issues: list[str] = []
    if not paths.fact_yml.exists():
        issues.append("fact.yml missing")
    if not paths.memory_manifest.exists():
        issues.append("memory_manifest.yml missing")

    status = "ok" if not issues else "degraded"

    report = {
        "ts": ts,
        "episode_count": episode_count,
        "edge_count": edge_count,
        "issues": issues,
        "status": status,
        "dry_run": dry_run,
    }

    if not dry_run:
        manifest = load_manifest(paths)
        stamp_run(paths, "health")
        manifest["stats"] = manifest.get("stats", {})
        manifest["stats"]["episode_count"] = episode_count
        manifest["stats"]["edge_count"] = edge_count
        save_manifest(paths, manifest)

    return report


def schedule_cron() -> str:
    return "0 6 * * *"
