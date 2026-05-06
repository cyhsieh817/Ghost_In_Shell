"""gish recall — M1 stub."""

import sys

import click


@click.command("recall")
@click.argument("query", required=True)
@click.option("--limit", type=int, default=5)
def recall_cmd(query: str, limit: int) -> None:
    """Recall episodes matching QUERY. (M1 stub.)"""
    click.echo(f"gish recall {query!r} (limit={limit}): M1 stub — not yet implemented (lands in M2)")
    sys.exit(1)
