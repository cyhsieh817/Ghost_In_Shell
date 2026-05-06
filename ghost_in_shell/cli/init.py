"""gish init — M1 stub."""

import sys

import click


@click.command("init")
@click.argument("workspace", required=True)
def init_cmd(workspace: str) -> None:
    """Initialize a workspace at WORKSPACE. (M1 stub.)"""
    click.echo(f"gish init {workspace}: M1 stub — not yet implemented (lands in M3)")
    sys.exit(1)
