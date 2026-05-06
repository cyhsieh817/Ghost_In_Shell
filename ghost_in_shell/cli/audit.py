"""gish audit — M1 stub."""

import sys

import click


@click.command("audit")
def audit_cmd() -> None:
    """Run sanctum + personal-data audit. (M1 stub.)"""
    click.echo("gish audit: M1 stub — not yet implemented (lands in M2)")
    sys.exit(1)
