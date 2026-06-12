"""Cron schedule installer — spec § 6.3."""

from __future__ import annotations

import platform
import subprocess
from pathlib import Path

_COMMENT = "# Ghost In Shell maintenance — managed by gish init (workspace: {workspace})"

# One nightly dream replaces the former five scattered entries. The old
# template was broken twice over: `associate-strength` / `consolidate-check`
# never existed as engine names, and every line omitted the required
# --workspace option. `gish dream` auto-escalates to deep sleep on Sundays.
_CRON_TEMPLATE = """\
{comment}
30 3 * * *  cd {workspace} && gish dream --workspace .
"""


def install_cron(workspace: Path) -> dict:
    """Install cron schedule for workspace. Returns status dict."""
    system = platform.system()
    if system in ("Darwin", "Linux"):
        return _install_unix_cron(workspace)
    elif system == "Windows":
        return _emit_windows_xml(workspace)
    else:
        return _emit_fallback_sh(workspace)


def _install_unix_cron(workspace: Path) -> dict:
    comment = _COMMENT.format(workspace=workspace)
    new_lines = _CRON_TEMPLATE.format(workspace=workspace, comment=comment)

    result = subprocess.run(
        ["crontab", "-l"],
        capture_output=True,
        text=True,
    )
    existing = result.stdout if result.returncode == 0 else ""

    if comment in existing:
        return {"status": "already_installed", "system": "unix"}

    updated = existing.rstrip("\n") + ("\n" if existing else "") + new_lines
    proc = subprocess.run(
        ["crontab", "-"],
        input=updated,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return {"status": "error", "system": "unix", "detail": proc.stderr.strip()}
    return {"status": "installed", "system": "unix"}


def _emit_windows_xml(workspace: Path) -> dict:
    cron_dir = workspace / "cron"
    cron_dir.mkdir(parents=True, exist_ok=True)
    xml_path = cron_dir / f"{workspace.name}-tasks.xml"

    xml_content = f"""<?xml version="1.0" encoding="UTF-16"?>
<!-- Ghost In Shell maintenance tasks — managed by gish init (workspace: {workspace}) -->
<!-- Import this file via: schtasks /create /xml "{xml_path}" /tn "GishMaintenance" -->
<Tasks>
  <Task><Action><Execute>gish</Execute><Arguments>dream --workspace {workspace}</Arguments></Action></Task>
</Tasks>
"""
    xml_path.write_text(xml_content, encoding="utf-8")
    return {"status": "emitted_xml", "system": "windows", "path": str(xml_path)}


def _emit_fallback_sh(workspace: Path) -> dict:
    cron_dir = workspace / "cron"
    cron_dir.mkdir(parents=True, exist_ok=True)
    sh_path = cron_dir / "run-all.sh"

    sh_content = f"""#!/usr/bin/env sh
# Ghost In Shell maintenance — managed by gish init (workspace: {workspace})
# Run this script manually or add to your system scheduler.
set -e
cd {workspace}
gish dream --workspace .
"""
    sh_path.write_text(sh_content, encoding="utf-8")
    sh_path.chmod(0o755)
    return {"status": "emitted_sh", "system": "unknown", "path": str(sh_path)}
