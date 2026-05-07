#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time

from _paths import SCRIPTS, WORKSPACE
from memory_runtime import list_launcher_profiles, resolve_launcher_profile


def env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def default_min_files() -> int:
    try:
        return max(1, int(os.environ.get("GHOST_MEMORY_MIN_FILES", "2")))
    except ValueError:
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch a CLI via the Ghost multi-CLI memory wrapper.")
    parser.add_argument("--launcher", help="Launcher profile id")
    parser.add_argument("--session-id", help="Override generated session id")
    parser.add_argument("--trigger", default=os.environ.get("GHOST_MEMORY_LOG_TRIGGER", "wrapper-exit"), help="Trigger label written to episodic memory")
    parser.add_argument("--min-files", type=int, default=default_min_files(), help="Minimum changed files required before logging")
    parser.add_argument("--dry-run", action="store_true", help="Print wrapper plan without launching the target CLI")
    parser.add_argument("--skip-session-log", action="store_true", help="Launch target CLI without logging on exit")
    parser.add_argument("--list-launchers", action="store_true", help="Show configured launchers and exit")
    parser.add_argument("cli_args", nargs=argparse.REMAINDER)
    return parser


def print_launchers() -> None:
    print("Available launchers:")
    for profile in list_launcher_profiles():
        args = " ".join(profile.get("args", [])) or "<none>"
        print(f"  - {profile['id']}: {profile.get('label', profile['id'])} (binary={profile.get('binary', '?')}, runtime={profile.get('runtime', '?')}, executor={profile.get('executor', '?')}, base_args={args})")


def normalize_cli_args(raw_args: list[str]) -> list[str]:
    return raw_args[1:] if raw_args and raw_args[0] == "--" else raw_args


def build_session_id(runtime_id: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", runtime_id).strip("-") or "runtime"
    return f"{slug}-{int(time.time())}-{os.getpid()}"


def build_log_command(runtime_id: str, session_id: str, trigger: str, min_files: int) -> list[str]:
    return [sys.executable, str(SCRIPTS / "memory_session_log.py"), "--runtime", runtime_id, "--session-id", session_id, "--trigger", trigger, "--min-files", str(min_files)]


def run_session_log(runtime_id: str, session_id: str, trigger: str, min_files: int) -> None:
    try:
        subprocess.run(build_log_command(runtime_id, session_id, trigger, min_files), cwd=str(WORKSPACE), capture_output=True, text=True, timeout=15)
    except Exception as exc:
        print(f"⚠ session log failed: {exc}", file=sys.stderr)


def main() -> int:
    args = build_parser().parse_args()
    if args.list_launchers:
        print_launchers()
        return 0
    launcher = resolve_launcher_profile(args.launcher)
    cli_args = normalize_cli_args(args.cli_args)
    session_id = args.session_id or os.environ.get("GHOST_MEMORY_SESSION_ID") or build_session_id(launcher["runtime"])
    dry_run = args.dry_run or env_flag("GHOST_MEMORY_WRAPPER_DRY_RUN")
    skip_session_log = args.skip_session_log or env_flag("GHOST_MEMORY_WRAPPER_SKIP_LOG")
    command = [launcher["binary"], *launcher.get("args", []), *cli_args]
    if dry_run:
        print(json.dumps({
            "launcher": launcher["id"],
            "label": launcher.get("label", launcher["id"]),
            "command": command,
            "runtime": launcher["runtime"],
            "executor": launcher["executor"],
            "session_id": session_id,
            "session_log_command": build_log_command(launcher["runtime"], session_id, args.trigger, args.min_files),
            "skip_session_log": skip_session_log,
        }, ensure_ascii=False, indent=2))
        return 0
    binary = shutil.which(launcher["binary"])
    if binary is None:
        print(f"CLI binary not found: {launcher['binary']}", file=sys.stderr)
        return 127
    command[0] = binary
    env = os.environ.copy()
    env["GHOST_MEMORY_LAUNCHER"] = launcher["id"]
    env["GHOST_MEMORY_RUNTIME"] = launcher["runtime"]
    env["GHOST_MEMORY_EXECUTOR"] = launcher["executor"]
    env["GHOST_MEMORY_SESSION_ID"] = session_id
    env["GHOST_MEMORY_WRAPPER_ACTIVE"] = "1"
    launched = False
    returncode = 0
    try:
        launched = True
        result = subprocess.run(command, cwd=str(WORKSPACE), env=env)
        returncode = result.returncode
    except KeyboardInterrupt:
        returncode = 130
    except Exception as exc:
        print(f"Unable to start {launcher['binary']}: {exc}", file=sys.stderr)
        returncode = 1
    if launched and not skip_session_log:
        run_session_log(launcher["runtime"], session_id, args.trigger, args.min_files)
    return returncode


if __name__ == "__main__":
    sys.exit(main())
