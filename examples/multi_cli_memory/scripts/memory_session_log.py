#!/usr/bin/env python3
"""
memory_session_log.py — Multi-runtime session-end memory logger
(Ghost In Shell v4.1 — fingerprinting + cooldown + lifecycle hooks)

Triggered by stop hooks / wrapper exits for any CLI runtime
(Claude Code / Gemini CLI / Copilot CLI / Codex / OpenClaw).

Behavior:
  1. Reads `git diff` (staged + unstaged) to infer the session's work.
  2. If material changes exist, appends an entry to `memory/episodic.jsonl`.
  3. Skips duplicates via a SHA-256 fingerprint of the changed file list.
  4. Skips entries within a cooldown window (default 300 s).
  5. Optionally invokes `memory_associate.py` and `memory_trigger_check.py`
     (best-effort — silently skipped if those scripts are absent).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from _paths import MEMORY, WORKSPACE
from memory_lock import memory_lock
from memory_runtime import list_runtime_profiles, resolve_runtime_profile

EPISODIC = MEMORY / "episodic.jsonl"


def _compute_fingerprint(files: list[str]) -> str:
    """SHA-256 over the sorted file list — stable across reorderings."""
    return hashlib.sha256("\n".join(sorted(files)).encode()).hexdigest()[:16]


def _is_duplicate(fingerprint: str, date_str: str, runtime_id: str, cooldown_seconds: int) -> bool:
    """True if recent entry has same fingerprint, OR last entry was inside cooldown window."""
    if not EPISODIC.exists():
        return False
    try:
        recent = []
        for line in EPISODIC.read_text(encoding="utf-8").splitlines():
            try:
                e = json.loads(line)
            except Exception:
                continue
            if e.get("date") == date_str and e.get("runtime") == runtime_id:
                recent.append(e)
        if not recent:
            return False
        last = recent[-1]
        if cooldown_seconds > 0 and "ts" in last:
            try:
                last_ts = datetime.fromisoformat(last["ts"])
                now_ts = datetime.now().astimezone()
                if (now_ts - last_ts).total_seconds() < cooldown_seconds:
                    return True
            except Exception:
                pass
        for e in recent[-5:]:
            if e.get("_fingerprint") == fingerprint:
                return True
        return False
    except Exception:
        return False


def _maybe_run(script_name: str, *extra_args: str, timeout: int = 10) -> None:
    """Best-effort invocation of an optional sibling script."""
    script = WORKSPACE / "scripts" / script_name
    if not script.exists():
        return
    try:
        subprocess.run(
            [sys.executable, str(script), *extra_args],
            cwd=str(WORKSPACE),
            timeout=timeout,
            capture_output=True,
        )
    except Exception:
        pass


def get_git_summary(include_untracked: bool = False) -> dict | None:
    try:
        diff = subprocess.run(
            ["git", "diff", "--stat", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(WORKSPACE),
            timeout=5,
        )
        diff_staged = subprocess.run(
            ["git", "diff", "--stat", "--cached"],
            capture_output=True,
            text=True,
            cwd=str(WORKSPACE),
            timeout=5,
        )
    except Exception:
        return None
    raw = f"{diff.stdout.strip()}\n{diff_staged.stdout.strip()}".strip()
    lines = raw.splitlines() if raw else []
    files_changed = [line.split("|")[0].strip() for line in lines if "|" in line]
    if include_untracked:
        try:
            untracked = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                capture_output=True,
                text=True,
                cwd=str(WORKSPACE),
                timeout=5,
            )
            files_changed.extend(line for line in untracked.stdout.strip().splitlines() if line)
        except Exception:
            pass
    if not files_changed:
        return None
    categories: set[str] = set()
    for file_path in files_changed:
        name = Path(file_path).name
        if file_path.startswith("memory/") or "episodic" in file_path:
            categories.add("memory")
        elif file_path.startswith("scripts/"):
            categories.add("scripts")
        elif name in {
            "CLAUDE.md",
            "GEMINI.md",
            "AGENTS.md",
            "COPILOT.md",
            "CODEX.md",
            "OPENCLAW.md",
            "MEMORY.md",
            "SOUL.md",
            "IDENTITY.md",
            "USER.md",
        }:
            categories.add("config")
        elif "bootstrap" in file_path or ".nosync" in file_path or "setup-symlinks" in file_path:
            categories.add("infra")
        else:
            categories.add("other")
    return {
        "files": files_changed,
        "count": len(files_changed),
        "categories": sorted(categories),
        "summary_line": lines[-1] if lines else "",
    }


def next_id(date_str: str) -> str:
    prefix = f"ep-{date_str}-"
    highest = 0
    if EPISODIC.exists():
        for line in EPISODIC.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                current = json.loads(line).get("id", "")
            except json.JSONDecodeError:
                continue
            if current.startswith(prefix):
                try:
                    highest = max(highest, int(current[len(prefix) :]))
                except ValueError:
                    continue
    return f"{prefix}{highest + 1:03d}"


def infer_type(categories: list[str]) -> str:
    if "infra" in categories:
        return "setup"
    if "scripts" in categories:
        return "refactor"
    if "config" in categories:
        return "setup"
    return "milestone"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Append a session-end episodic entry for a runtime."
    )
    parser.add_argument("--runtime", help="Runtime profile id")
    parser.add_argument("--source", help="Override source field")
    parser.add_argument("--session-id", help="Optional runtime session identifier")
    parser.add_argument("--trigger", default="wrapper-exit", help="Trigger label")
    parser.add_argument(
        "--min-files",
        type=int,
        default=2,
        help="Minimum changed files required before logging",
    )
    parser.add_argument(
        "--no-trigger-check",
        action="store_true",
        help="Skip trigger check after writing",
    )
    parser.add_argument(
        "--list-runtimes",
        action="store_true",
        help="Show configured runtimes and exit",
    )
    parser.add_argument(
        "--cooldown",
        type=int,
        default=300,
        help="Skip write if last entry for same runtime was within N seconds (default: 300)",
    )
    parser.add_argument(
        "--include-untracked",
        action="store_true",
        help="Include untracked files in change summary (default: False)",
    )
    return parser


def print_runtimes() -> None:
    print("Available runtimes:")
    for profile in list_runtime_profiles():
        print(
            f"  - {profile['id']}: {profile.get('label', profile['id'])} "
            f"(source={profile.get('source', '?')})"
        )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.list_runtimes:
        print_runtimes()
        return 0
    runtime = resolve_runtime_profile(args.runtime)
    summary = get_git_summary(include_untracked=args.include_untracked)
    if not summary or summary["count"] < args.min_files:
        return 0
    now = datetime.now().astimezone()
    date_str = now.strftime("%Y-%m-%d")

    fingerprint = _compute_fingerprint(summary["files"])
    if _is_duplicate(fingerprint, date_str, runtime["id"], args.cooldown):
        return 0

    top_files = ", ".join(Path(name).name for name in summary["files"][:5])
    if summary["count"] > 5:
        top_files += f" and {summary['count'] - 5} more"
    entry = {
        "date": date_str,
        "ts": now.isoformat(timespec="seconds"),
        "type": infer_type(summary["categories"]),
        "title": f"Session auto-log: {top_files}",
        "content": f"Modified {summary['count']} files. {summary['summary_line']}".strip(),
        "tags": sorted(set(summary["categories"] + runtime.get("tags", []))),
        "importance": min(5 + summary["count"] // 3, 8),
        "source": args.source or runtime.get("source", f"stop_hook:{runtime['id']}"),
        "runtime": runtime["id"],
        "trigger": args.trigger,
        "decay_status": "active",
        "retrieval": {"count": 0, "last_accessed": None, "strength": 0.0},
        "linked_to": [],
        "_fingerprint": fingerprint,
    }
    if args.session_id:
        entry["session_id"] = args.session_id
    with memory_lock(f"session-log-{runtime['id']}"):
        entry["id"] = next_id(date_str)
        with EPISODIC.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Best-effort lifecycle hooks (silently skipped if scripts are absent)
    _maybe_run("memory_associate.py", "suggest", entry["id"], timeout=15)
    _maybe_run("memory_associate.py", "flush-buffer", timeout=10)

    if args.no_trigger_check:
        return 0
    _maybe_run("memory_trigger_check.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
