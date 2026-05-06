"""Decay engine — mark fading/archived entries by strength floor (spec § 4.7)."""

from __future__ import annotations

import datetime
from pathlib import Path

from ghost_in_shell.engines._manifest import stamp_run
from ghost_in_shell.memory._paths import WorkspacePaths, resolve_workspace
from ghost_in_shell.memory._safe_io import atomic_write_text, read_jsonl
from ghost_in_shell.memory.retrieval import compute_strength

import json

_FADING_THRESHOLD = 0.4
_ARCHIVED_THRESHOLD = 0.2
_SAFETY_FLOOR = 5  # don't mutate if fewer than 5 active entries


def run(workspace: Path, *, dry_run: bool = False) -> dict:
    """Apply strength-based decay to episodic entries.

    Safety floor: if fewer than ``_SAFETY_FLOOR`` active entries exist,
    return ``{"paused": True}`` without mutating.
    """
    paths = WorkspacePaths(resolve_workspace(workspace))
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if not paths.episodic.exists():
        return {"ts": ts, "paused": False, "mutated": 0, "dry_run": dry_run}

    entries = list(read_jsonl(paths.episodic))
    active_count = sum(1 for e in entries if e.get("decay_status") == "active")

    if active_count < _SAFETY_FLOOR:
        return {"ts": ts, "paused": True, "active_count": active_count, "dry_run": dry_run}

    now = datetime.datetime.now(datetime.timezone.utc)
    mutated = 0
    updated: list[dict] = []

    for entry in entries:
        if entry.get("decay_status") == "archived":
            updated.append(entry)
            continue

        created_ts = entry.get("ts", ts)
        try:
            created = datetime.datetime.fromisoformat(created_ts.replace("Z", "+00:00"))
        except ValueError:
            created = now
        weeks = (now - created).total_seconds() / (7 * 24 * 3600)

        importance = entry.get("importance", 5)
        retrieval_count = entry.get("retrieval", {}).get("count", 0)
        edges = 0  # no graph access in decay engine

        strength = compute_strength(importance, retrieval_count, edges, weeks)

        new_status = entry.get("decay_status", "active")
        if strength < _ARCHIVED_THRESHOLD:
            new_status = "archived"
        elif strength < _FADING_THRESHOLD:
            new_status = "fading"

        if new_status != entry.get("decay_status"):
            entry = {**entry, "decay_status": new_status}
            mutated += 1
        updated.append(entry)

    if not dry_run and mutated > 0:
        lines = "\n".join(json.dumps(e, ensure_ascii=False) for e in updated) + "\n"
        atomic_write_text(paths.episodic, lines)
        stamp_run(paths, "decay")

    return {"ts": ts, "paused": False, "mutated": mutated, "dry_run": dry_run}


def schedule_cron() -> str:
    return "0 4 * * *"
