"""gish run-maintenance — M1 stub."""

import sys

import click


@click.command("run-maintenance")
@click.option("--engine", type=str, default=None)
def run_maintenance_cmd(engine: str | None) -> None:
    """Run all (or one) maintenance engine. (M1 stub.)"""
    label = engine or "all"
    click.echo(f"gish run-maintenance --engine {label}: M1 stub — not yet implemented (lands in M2)")
    sys.exit(1)
