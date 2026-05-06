"""gish doctor — M1 stub."""

import sys

import click


@click.command("doctor")
def doctor_cmd() -> None:
    """Run health check. (M1 stub.)"""
    click.echo("gish doctor: M1 stub — not yet implemented (lands in M2)")
    sys.exit(1)
