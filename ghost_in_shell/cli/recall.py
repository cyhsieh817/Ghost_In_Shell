"""gish recall — search episodic memory (M2)."""

from __future__ import annotations

from pathlib import Path

import click

from ghost_in_shell.memory._paths import WorkspacePaths, resolve_workspace
from ghost_in_shell.memory.episodic import EpisodicStore


@click.command("recall")
@click.argument("query", required=True)
@click.option("--workspace", required=True, type=click.Path(exists=True), help="Workspace root path.")
@click.option("--limit", type=int, default=5, help="Maximum results.")
def recall_cmd(query: str, workspace: str, limit: int) -> None:
    """Recall episodes matching QUERY."""
    paths = WorkspacePaths(resolve_workspace(Path(workspace)))
    store = EpisodicStore(paths)
    results = store.search(query, limit=limit)
    if not results:
        click.echo("No matching episodes found.")
        return
    for r in results:
        click.echo(f"[{r['id']}] {r['title']}  (importance={r['importance']}, status={r['decay_status']})")
