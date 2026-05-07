#!/usr/bin/env python3
"""
lgd_bridge.py — LabGrimoire Desktop headless bridge (portable skeleton)

Lets the agent call LGD's local LLM + tool registry without opening the GUI.
This is a **portable** version: paths and CLI binaries are read from the
shared `_paths.py` and `memory/runtime_profiles.yml`, not hard-coded.

Pre-requisites:
  • LabGrimoire Desktop installed
  • `lgd` CLI on PATH (or set GHOST_LGD_BIN environment variable)

Usage:
  python3 scripts/lgd_bridge.py "Summarize today's session log"
  python3 scripts/lgd_bridge.py --model gemma-4-26b "Build a report"
  python3 scripts/lgd_bridge.py --session <id> "follow-up"
  python3 scripts/lgd_bridge.py --max-turns 20 "long task"
  python3 scripts/lgd_bridge.py --check     # dry run: confirm LGD is reachable

If LGD is not installed, this script exits with status 0 and prints a hint
to stderr — calling code can treat absence as "LGD pairing not configured"
without aborting.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    from _paths import MEMORY, WORKSPACE
except Exception:
    MEMORY = Path(__file__).resolve().parent.parent / "memory"
    WORKSPACE = MEMORY.parent


def _lgd_binary() -> str | None:
    """Locate the lgd CLI. Prefer GHOST_LGD_BIN env var, else PATH."""
    explicit = os.environ.get("GHOST_LGD_BIN")
    if explicit and Path(explicit).exists():
        return explicit
    return shutil.which("lgd")


def _hint_missing() -> None:
    print(
        "lgd_bridge: LabGrimoire Desktop CLI not found.\n"
        "  Install: https://github.com/cyhsieh817/labgrimoire-desktop\n"
        "  Or set GHOST_LGD_BIN to the absolute path of the lgd binary.",
        file=sys.stderr,
    )


def check() -> int:
    """Probe LGD availability — used by setup scripts and CI."""
    binary = _lgd_binary()
    if binary is None:
        _hint_missing()
        return 0  # absence is not a hard failure
    try:
        result = subprocess.run(
            [binary, "--version"],
            capture_output=True, text=True, timeout=5,
        )
        print(f"lgd_bridge: LGD reachable at {binary}")
        if result.stdout.strip():
            print(f"  version: {result.stdout.strip()}")
        return 0
    except Exception as exc:
        print(f"lgd_bridge: LGD binary at {binary} but probe failed: {exc}", file=sys.stderr)
        return 1


def call(prompt: str, *, model: str | None, session: str | None, max_turns: int) -> int:
    binary = _lgd_binary()
    if binary is None:
        _hint_missing()
        return 0
    cmd: list[str] = [binary, "agent", "run"]
    if model:
        cmd.extend(["--model", model])
    if session:
        cmd.extend(["--session", session])
    cmd.extend(["--max-turns", str(max_turns), "--message", prompt])

    started = datetime.now(timezone.utc).isoformat()
    invocation_id = uuid.uuid4().hex[:12]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True,
            cwd=str(WORKSPACE),
            timeout=max_turns * 60,
        )
    except Exception as exc:
        print(f"lgd_bridge: invocation failed: {exc}", file=sys.stderr)
        return 2

    sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)

    # Optional audit trail — only if memory dir exists
    audit_log = MEMORY / "lgd_bridge_log.jsonl"
    if MEMORY.exists():
        try:
            audit_log.parent.mkdir(parents=True, exist_ok=True)
            with audit_log.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({
                    "invocation_id": invocation_id,
                    "started": started,
                    "model": model,
                    "session": session,
                    "max_turns": max_turns,
                    "returncode": result.returncode,
                    "prompt_preview": prompt[:120],
                }, ensure_ascii=False) + "\n")
        except Exception:
            pass

    return result.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Headless bridge to LabGrimoire Desktop's agent runtime."
    )
    parser.add_argument("prompt", nargs="?", help="Prompt to send to LGD")
    parser.add_argument("--model", help="Override model id (defaults to LGD config)")
    parser.add_argument("--session", help="Resume an existing chat session id")
    parser.add_argument("--max-turns", type=int, default=10, help="Max agent turns (default: 10)")
    parser.add_argument("--check", action="store_true", help="Probe LGD availability and exit")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.check:
        return check()
    if not args.prompt:
        parser.print_help(sys.stderr)
        return 2
    return call(args.prompt, model=args.model, session=args.session, max_turns=args.max_turns)


if __name__ == "__main__":
    sys.exit(main())
