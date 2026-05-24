"""Consolidate engine — merge low-importance episodes and call judge (spec § 4.7)."""

from __future__ import annotations

import datetime
import json
from pathlib import Path

from gshell_memory.engines._manifest import load_manifest, save_manifest
from gshell_memory.memory._paths import WorkspacePaths, resolve_workspace
from gshell_memory.memory._safe_io import atomic_write_text, read_jsonl

_LOW_IMPORTANCE_THRESHOLD = 4
_MIN_CONSOLIDATE_COUNT = 3


def run(workspace: Path, *, dry_run: bool = False) -> dict:
    """Consolidate low-importance episodes into a summary entry.

    Collects episodes with importance <= threshold, merges them into a
    single synthetic entry, then calls the judge engine for a verdict.
    """
    paths = WorkspacePaths(resolve_workspace(workspace))
    ts = datetime.datetime.now(datetime.UTC).isoformat()

    if not paths.episodic.exists():
        return {"ts": ts, "merged": 0, "verdict": None, "dry_run": dry_run}

    entries = list(read_jsonl(paths.episodic))
    low = [e for e in entries if e.get("importance", 5) <= _LOW_IMPORTANCE_THRESHOLD
           and e.get("decay_status") != "archived"]

    if len(low) < _MIN_CONSOLIDATE_COUNT:
        return {"ts": ts, "merged": 0, "verdict": None, "dry_run": dry_run}

    # Build merged summary entry
    titles = [e["title"] for e in low]
    merged_content = "Consolidated: " + "; ".join(titles)
    merged_id = f"consolidated-{ts[:10].replace('-', '')}"

    import hashlib
    fp = hashlib.sha256(merged_content.encode()).hexdigest()

    merged_entry = {
        "id": merged_id,
        "ts": ts,
        "type": "knowledge_digest",
        "title": f"Consolidation {ts[:10]}",
        "content": merged_content,
        "tags": ["consolidated"],
        "importance": _LOW_IMPORTANCE_THRESHOLD,
        "source": "consolidate_engine",
        "fingerprint": fp,
        "links": {"facts": [], "files": []},
        "decay_status": "active",
        "quality": {"duplicate_suspect": False, "exclusive": True,
                    "predictive": False, "recurrence": 0, "score": 0.5},
        "retrieval": {"count": 0, "last_accessed": None, "strength": 0.5},
    }

    if not dry_run:
        # Replace low entries with merged; keep the rest
        kept = [e for e in entries if e not in low]
        kept.append(merged_entry)
        lines = "\n".join(json.dumps(e, ensure_ascii=False) for e in kept) + "\n"
        atomic_write_text(paths.episodic, lines)

        manifest = load_manifest(paths)
        manifest["last_consolidation"] = ts
        manifest.setdefault("consolidation_history", []).append(
            {"ts": ts, "merged": len(low), "result_id": merged_id}
        )
        save_manifest(paths, manifest)

    # Call judge inline
    from gshell_memory.engines import judge
    verdict = judge.evaluate(merged_entry)

    return {"ts": ts, "merged": len(low), "verdict": verdict, "dry_run": dry_run}


def schedule_cron() -> str:
    return "0 2 * * 0"
