"""gish doctor — run health check (M2)."""

from __future__ import annotations

from pathlib import Path

import click

from ghost_in_shell.engines import health


@click.command("doctor")
@click.option("--workspace", required=True, type=click.Path(exists=True), help="Workspace root path.")
@click.option("--dry-run", is_flag=True, default=False)
def doctor_cmd(workspace: str, dry_run: bool) -> None:
    """Run health check on the workspace."""
    report = health.run(Path(workspace), dry_run=dry_run)
    status = report["status"]
    color = "green" if status == "ok" else "yellow"
    click.echo(click.style(f"Status: {status}", fg=color))
    click.echo(f"Episodes: {report['episode_count']}  Edges: {report['edge_count']}")
    if report["issues"]:
        for issue in report["issues"]:
            click.echo(click.style(f"  ⚠  {issue}", fg="yellow"))
