"""Audit engine — scan audit logs for anomalies (spec § 4.7)."""

from __future__ import annotations

import datetime
from pathlib import Path

from ghost_in_shell.engines._manifest import stamp_run
from ghost_in_shell.memory._paths import WorkspacePaths, resolve_workspace
from ghost_in_shell.memory._safe_io import read_jsonl


def run(workspace: Path, *, dry_run: bool = False) -> dict:
    """Scan all audit logs and report anomaly counts.

    An anomaly is any audit entry where the ``action`` field is ``delete``
    or is missing entirely.
    """
    paths = WorkspacePaths(resolve_workspace(workspace))
    ts = datetime.datetime.now(datetime.UTC).isoformat()

    audit_files = list(paths.memory_dir.glob("*_audit.jsonl")) if paths.memory_dir.exists() else []
    total = 0
    anomalies: list[dict] = []

    for af in audit_files:
        for row in read_jsonl(af):
            total += 1
            if row.get("action") == "delete" or "action" not in row:
                anomalies.append({"file": af.name, "row": row})

    report = {
        "ts": ts,
        "audit_files_scanned": len(audit_files),
        "total_entries": total,
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
        "dry_run": dry_run,
    }

    if not dry_run:
        stamp_run(paths, "audit")

    return report


def schedule_cron() -> str:
    return "0 3 * * 0"
