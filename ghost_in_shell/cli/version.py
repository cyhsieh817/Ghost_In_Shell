"""gish version subcommand — the only fully-implemented subcommand in M1."""

import click

from ghost_in_shell import __version__


@click.command("version")
def version_cmd() -> None:
    """Print the ghost_in_shell package version."""
    click.echo(f"ghost-in-shell {__version__}")
