"""gish log — M1 stub."""

import sys

import click


@click.command("log")
@click.argument("title", required=False)
@click.option("--from-git", is_flag=True, default=False)
def log_cmd(title: str | None, from_git: bool) -> None:
    """Append an episodic entry. (M1 stub.)"""
    click.echo(f"gish log title={title!r} from_git={from_git}: M1 stub — not yet implemented (lands in M2)")
    sys.exit(1)
