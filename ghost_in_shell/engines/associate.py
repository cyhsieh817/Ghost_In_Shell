"""Associate engine — auto-create tag-based associations (spec § 4.7)."""

from __future__ import annotations

import datetime
from pathlib import Path

from ghost_in_shell.engines._manifest import stamp_run
from ghost_in_shell.memory._paths import WorkspacePaths, resolve_workspace
from ghost_in_shell.memory._safe_io import read_jsonl
from ghost_in_shell.memory.associations import AssociationGraph


def run(workspace: Path, *, dry_run: bool = False) -> dict:
    """Scan episodic entries and link those sharing common tags.

    For each pair of entries sharing at least one tag, add an
    ``elaborates`` association if none already exists.
    """
    paths = WorkspacePaths(resolve_workspace(workspace))
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if not paths.episodic.exists():
        return {"ts": ts, "created": 0, "dry_run": dry_run}

    entries = list(read_jsonl(paths.episodic))
    graph = AssociationGraph(paths)
    existing = {
        (e.get("src", {}).get("id"), e.get("dst", {}).get("id"))
        for e in graph.all_edges()
    }

    created = 0
    for i, a in enumerate(entries):
        for b in entries[i + 1 :]:
            tags_a = set(a.get("tags", []))
            tags_b = set(b.get("tags", []))
            if not tags_a & tags_b:
                continue
            pair = (a["id"], b["id"])
            if pair in existing:
                continue
            if not dry_run:
                graph.add({
                    "ts": ts,
                    "src": {"kind": "episode", "id": a["id"]},
                    "dst": {"kind": "episode", "id": b["id"]},
                    "type": "elaborates",
                    "weight": 0.5,
                    "evidence": f"shared tags: {sorted(tags_a & tags_b)}",
                    "created_by": "associate_engine",
                })
                existing.add(pair)
            created += 1

    if not dry_run:
        stamp_run(paths, "health")

    return {"ts": ts, "created": created, "dry_run": dry_run}


def schedule_cron() -> str:
    return "0 5 * * *"
