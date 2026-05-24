"""gish version subcommand — the only fully-implemented subcommand in M1."""

import click

from gshell_memory import __version__


@click.command("version")
def version_cmd() -> None:
    """Print the gshell_memory package version."""
    click.echo(f"ghost-in-shell {__version__}")
