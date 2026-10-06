"""Consolidate engine — propose, judge, then apply (spec § 4.7, ch.20).

Consolidation rewrites memory, so it never grades its own work:

1. **propose** — collect low-importance active episodes and build one merged
   entry that links back to every source (``linked_to``).
2. **judge**  — :func:`gshell_memory.engines.judge.grade_proposal` runs
   deterministic pre-checks and, when configured device-locally, an external
   judge command (``GISH_JUDGE_COMMAND`` / ``~/.config/gish/judge_command``).
   Only grades A-C pass. A missing or crashing external judge fails closed.
3. **apply**  — only after a passing grade, under the episodic lock: sources
   are appended to ``memory/_archive/episodic_consolidated.jsonl`` first,
   then removed from ``episodic.jsonl`` and replaced by the merged entry.
   Nothing is deleted; the archive keeps the full timeline.

A rejected proposal stays in ``.gish/proposals/`` for a human to read.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import shlex
from pathlib import Path

import yaml

from gshell_memory.engines._manifest import load_manifest, save_manifest
from gshell_memory.memory._lock import file_lock
from gshell_memory.memory._paths import WorkspacePaths, resolve_workspace
from gshell_memory.memory._role import device_config_dir, require_primary
from gshell_memory.memory._safe_io import append_jsonl, atomic_write_text, read_jsonl

LOW_IMPORTANCE_THRESHOLD = 4
MIN_CONSOLIDATE_COUNT = 3
ARCHIVE_NAME = "episodic_consolidated.jsonl"
JUDGE_ENV = "GISH_JUDGE_COMMAND"


def judge_command_file() -> Path:
    return device_config_dir() / "judge_command"


def run(workspace: Path, *, dry_run: bool = False) -> dict:
    """Propose → judge → apply. ``dry_run`` builds and grades in memory only."""
    paths = WorkspacePaths(resolve_workspace(workspace))
    ts = datetime.datetime.now(datetime.UTC).isoformat()
    result = {
        "ts": ts,
        "merged": 0,
        "applied": False,
        "verdict": None,
        "proposal": None,
        "dry_run": dry_run,
    }

    if not paths.episodic.exists():
        return result

    entries = list(read_jsonl(paths.episodic))
    proposal = propose(entries, ts=ts)
    if proposal is None:
        return result
    result["merged"] = len(proposal["sources"])

    from gshell_memory.engines import judge

    if dry_run:
        result["verdict"] = judge.grade_proposal(proposal, entries, judge_command=None)
        return result

    require_primary("consolidate")
    proposal_path = _write_proposal(paths, proposal)
    result["proposal"] = str(proposal_path.relative_to(paths.root))

    judge_cmd, refusal = _judge_command(paths)
    verdict = judge.grade_proposal(
        proposal,
        entries,
        judge_command=judge_cmd,
        proposal_path=proposal_path,
    )
    if refusal:
        verdict = {
            **verdict,
            "grade": "F",
            "passed": False,
            "external": {"grade": None, "error": refusal},
        }
    result["verdict"] = verdict
    _record_verdict(proposal_path, proposal, verdict)
    if not verdict["passed"]:
        return result

    applied = apply(paths, proposal)
    result["applied"] = applied["applied"]
    if not applied["applied"]:
        result["verdict"] = {**verdict, "apply_refused": applied["reason"]}
    return result


def propose(entries: list[dict], *, ts: str) -> dict | None:
    """Build a consolidation proposal, or ``None`` when below the threshold."""
    low = [
        e
        for e in entries
        if e.get("importance", 5) <= LOW_IMPORTANCE_THRESHOLD
        and e.get("decay_status") != "archived"
        and e.get("id")
    ]
    if len(low) < MIN_CONSOLIDATE_COUNT:
        return None

    source_ids = [e["id"] for e in low]
    merged_content = "Consolidated: " + "; ".join(str(e.get("title", "")) for e in low)
    fingerprint = hashlib.sha256(merged_content.encode()).hexdigest()
    merged_id = f"consolidated-{ts[:10].replace('-', '')}-{fingerprint[:8]}"

    merged_entry = {
        "id": merged_id,
        "ts": ts,
        "date": ts[:10],
        "type": "knowledge_digest",
        "title": f"Consolidation {ts[:10]}",
        "content": merged_content,
        "tags": ["consolidated"],
        "importance": LOW_IMPORTANCE_THRESHOLD,
        "source": "consolidate_engine",
        "fingerprint": fingerprint,
        "links": {"facts": [], "files": []},
        "decay_status": "active",
        "quality": {
            "duplicate_suspect": False,
            "exclusive": True,
            "predictive": False,
            "recurrence": 0,
            "score": 0.5,
        },
        "retrieval": {"count": 0, "last_accessed": None, "strength": 0.5},
        "linked_to": source_ids,
    }
    return {"created": ts, "sources": source_ids, "merged": merged_entry}


def apply(paths: WorkspacePaths, proposal: dict) -> dict:
    """Apply a graded proposal. Refuses when the sources changed since proposing."""
    require_primary("consolidate apply")
    sources = set(proposal["sources"])
    with file_lock(paths.episodic_lock):
        entries = list(read_jsonl(paths.episodic))
        active_ids = {e.get("id") for e in entries if e.get("decay_status") != "archived"}
        missing = sorted(sources - active_ids)
        if missing:
            return {"applied": False, "reason": f"stale proposal; sources gone: {missing}"}

        moved = [e for e in entries if e.get("id") in sources]
        kept = [e for e in entries if e.get("id") not in sources]
        kept.append(proposal["merged"])

        # Archive first: a crash between the two writes leaves a duplicate,
        # never a loss.
        append_jsonl(paths.archive_dir / ARCHIVE_NAME, moved)
        lines = "\n".join(json.dumps(e, ensure_ascii=False) for e in kept) + "\n"
        atomic_write_text(paths.episodic, lines)

    manifest = load_manifest(paths)
    manifest["last_consolidation"] = proposal["created"]
    manifest.setdefault("consolidation_history", []).append(
        {"ts": proposal["created"], "merged": len(moved), "result_id": proposal["merged"]["id"]}
    )
    save_manifest(paths, manifest)
    return {"applied": True, "reason": "ok"}


def _write_proposal(paths: WorkspacePaths, proposal: dict) -> Path:
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = paths.proposals_dir / f"consolidation_{stamp}.json"
    atomic_write_text(path, json.dumps(proposal, ensure_ascii=False, indent=2) + "\n")
    return path


def _record_verdict(path: Path, proposal: dict, verdict: dict) -> None:
    atomic_write_text(
        path, json.dumps({**proposal, "verdict": verdict}, ensure_ascii=False, indent=2) + "\n"
    )


def _judge_command(paths: WorkspacePaths) -> tuple[list[str] | None, str | None]:
    """Return ``(argv, refusal)`` for the external judge.

    The judge is an executable, so it is configured device-locally only:
    ``GISH_JUDGE_COMMAND`` or ``$XDG_CONFIG_HOME/gish/judge_command``. A
    workspace may be synced or cloned from elsewhere; if its config could name
    a command, anyone able to write the workspace could run code on every
    machine during the nightly dream. A workspace that still sets
    ``consolidate.judge_command`` is refused (fail closed) with a message.
    """
    if paths.config.exists():
        data = yaml.safe_load(paths.config.read_text(encoding="utf-8")) or {}
        if (data.get("consolidate") or {}).get("judge_command"):
            return None, (
                "refused: .gish/config.yml sets consolidate.judge_command; judge commands "
                f"are read only from {JUDGE_ENV} or {judge_command_file()} (device-local)"
            )
    raw = os.environ.get(JUDGE_ENV)
    if raw is None:
        path = judge_command_file()
        raw = path.read_text(encoding="utf-8") if path.is_file() else ""
    argv = shlex.split(raw.strip())
    return (argv or None), None


def schedule_cron() -> str:
    return "0 2 * * 0"
