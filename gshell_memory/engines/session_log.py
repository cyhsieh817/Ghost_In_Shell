"""SessionLog engine — append runtime session events (spec § 4.7)."""

from __future__ import annotations

import datetime
from pathlib import Path

from gshell_memory.engines._manifest import stamp_run
from gshell_memory.memory._paths import WorkspacePaths, resolve_workspace
from gshell_memory.memory._safe_io import append_jsonl

_LOG_FILE = "session_log.jsonl"


def run(workspace: Path, *, dry_run: bool = False) -> dict:
    """Append a session-start event to the session log.

    Returns a summary dict with ``ts``, ``dry_run``, and ``log_path``.
    """
    paths = WorkspacePaths(resolve_workspace(workspace))
    log_path = paths.memory_dir / _LOG_FILE
    ts = datetime.datetime.now(datetime.UTC).isoformat()
    entry = {"ts": ts, "event": "session_start", "engine": "session_log"}

    if not dry_run:
        append_jsonl(log_path, [entry])
        stamp_run(paths, "health")  # stamps last_health_run

    return {"ts": ts, "dry_run": dry_run, "log_path": str(log_path)}


def schedule_cron() -> str:
    return "@session_start"
