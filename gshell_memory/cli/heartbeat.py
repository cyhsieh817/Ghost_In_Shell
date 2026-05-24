"""`gish heartbeat` sub-commands."""

from __future__ import annotations

from pathlib import Path

import click

from gshell_memory.engines.heartbeat import HeartbeatEngine


@click.group(name="heartbeat")
def heartbeat_group() -> None:
    """Heartbeat — periodic self-check."""


def _ws_opt(f):
    return click.option(
        "--workspace",
        type=click.Path(file_okay=False, path_type=Path),
        required=True,
    )(f)


@heartbeat_group.command("run")
@_ws_opt
def run_cmd(workspace):
    entry = HeartbeatEngine(workspace).run()
    click.echo(f"{entry['status']}  ts={entry['ts']}  cadence={entry['cadence']}")


@heartbeat_group.command("install")
@click.option("--cron", "use_cron", is_flag=True)
@click.option("--launchd", "use_launchd", is_flag=True)
@_ws_opt
def install_cmd(workspace, use_cron, use_launchd):
    if not (use_cron or use_launchd):
        raise click.UsageError("specify --cron or --launchd")
    eng = HeartbeatEngine(workspace)
    if use_cron:
        click.echo(eng.cron_snippet())
        click.echo("# Add the line above to your crontab (crontab -e).")
    if use_launchd:
        click.echo(eng.launchd_plist())
        click.echo(
            "<!-- Save to ~/Library/LaunchAgents/io.gshell-memory.heartbeat.plist and load with launchctl. -->"
        )
