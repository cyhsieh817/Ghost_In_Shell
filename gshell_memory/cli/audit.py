"""gish audit — run sanctum + audit engine (M2)."""

from __future__ import annotations

from pathlib import Path

import click

from gshell_memory.engines import audit as audit_engine


@click.command("audit")
@click.option("--workspace", required=True, type=click.Path(exists=True), help="Workspace root path.")
@click.option("--dry-run", is_flag=True, default=False)
def audit_cmd(workspace: str, dry_run: bool) -> None:
    """Run sanctum and personal-data audit."""
    report = audit_engine.run(Path(workspace), dry_run=dry_run)
    click.echo(f"Audit files scanned: {report['audit_files_scanned']}")
    click.echo(f"Total entries: {report['total_entries']}")
    anomaly_count = report["anomaly_count"]
    color = "green" if anomaly_count == 0 else "red"
    click.echo(click.style(f"Anomalies: {anomaly_count}", fg=color))
