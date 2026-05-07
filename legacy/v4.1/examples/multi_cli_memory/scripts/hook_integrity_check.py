#!/usr/bin/env python3
"""
hook_integrity_check.py — Verify Stop-hook configuration is intact

Reads the hook config (Claude Code's `~/.claude/settings.json`, or a custom
path passed via `--config`) and reports whether the canonical Stop hook —
the one that calls `memory_session_log.py` — is present and pointing at the
right workspace.

Returns:
  0  — hook present and pointing at this workspace's session log
  1  — hook missing or misconfigured (run `hook_integrity_fix.py` next)
  2  — config file unreadable / invalid JSON
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

try:
    from _paths import WORKSPACE
except Exception:
    WORKSPACE = Path(__file__).resolve().parent.parent

DEFAULT_CONFIG = Path(os.path.expanduser("~/.claude/settings.json"))
EXPECTED_SCRIPT = (WORKSPACE / "scripts" / "memory_session_log.py").resolve()


def find_stop_hooks(cfg: dict) -> list[dict]:
    return cfg.get("hooks", {}).get("Stop", []) or []


def commands(stop_hooks: list[dict]) -> list[str]:
    out: list[str] = []
    for entry in stop_hooks:
        for hook in entry.get("hooks", []):
            cmd = hook.get("command", "")
            if cmd:
                out.append(cmd)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Stop-hook integrity.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG),
                        help=f"Path to settings.json (default: {DEFAULT_CONFIG})")
    parser.add_argument("--quiet", action="store_true", help="Suppress success output")
    args = parser.parse_args()

    cfg_path = Path(args.config)
    if not cfg_path.exists():
        print(f"hook_integrity_check: config not found at {cfg_path}", file=sys.stderr)
        return 1
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"hook_integrity_check: invalid JSON in {cfg_path}: {exc}", file=sys.stderr)
        return 2

    cmds = commands(find_stop_hooks(cfg))
    if not cmds:
        print("hook_integrity_check: no Stop hooks configured", file=sys.stderr)
        return 1

    expected_str = str(EXPECTED_SCRIPT)
    found = any(expected_str in cmd for cmd in cmds)
    if not found:
        print(
            f"hook_integrity_check: Stop hook does NOT reference {expected_str}",
            file=sys.stderr,
        )
        for cmd in cmds:
            print(f"  observed: {cmd}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"hook_integrity_check: OK — Stop hook points at {expected_str}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
