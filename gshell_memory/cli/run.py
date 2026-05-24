"""gish run-maintenance — run maintenance engines (M2)."""

from __future__ import annotations

from pathlib import Path

import click

_ALL_ENGINES = ["session_log", "health", "audit", "decay", "associate", "consolidate"]


@click.command("run-maintenance")
@click.option("--workspace", required=True, type=click.Path(exists=True), help="Workspace root path.")
@click.option("--engine", type=str, default=None, help="Run a specific engine (default: all).")
@click.option("--dry-run", is_flag=True, default=False)
def run_maintenance_cmd(workspace: str, engine: str | None, dry_run: bool) -> None:
    """Run all (or one) maintenance engine."""
    from gshell_memory.engines import associate, audit, consolidate, decay, health, session_log
    _MAP = {
        "session_log": session_log,
        "health": health,
        "audit": audit,
        "decay": decay,
        "associate": associate,
        "consolidate": consolidate,
    }
    to_run = [engine] if engine else _ALL_ENGINES
    for name in to_run:
        if name not in _MAP:
            click.echo(click.style(f"Unknown engine: {name}", fg="red"), err=True)
            raise SystemExit(1)
        mod = _MAP[name]
        result = mod.run(Path(workspace), dry_run=dry_run)
        click.echo(f"[{name}] {result}")
