"""gish log — append an episodic entry (M2)."""

from __future__ import annotations

import datetime
import hashlib
from pathlib import Path

import click

from ghost_in_shell.memory._paths import WorkspacePaths, resolve_workspace
from ghost_in_shell.memory.episodic import EpisodicStore, make_fingerprint


@click.command("log")
@click.argument("title", required=True)
@click.option("--workspace", required=True, type=click.Path(exists=True), help="Workspace root path.")
@click.option("--content", default="", help="Episode content.")
@click.option("--tags", default="", help="Comma-separated tags.")
@click.option("--importance", type=int, default=5, help="Importance 1-10.")
@click.option("--type", "episode_type", default="decision", help="Episode type.")
@click.option("--source", default="cli", help="Source label.")
def log_cmd(
    title: str,
    workspace: str,
    content: str,
    tags: str,
    importance: int,
    episode_type: str,
    source: str,
) -> None:
    """Append an episodic memory entry."""
    paths = WorkspacePaths(resolve_workspace(Path(workspace)))
    store = EpisodicStore(paths)
    ts = datetime.datetime.now(datetime.UTC).isoformat()
    date = ts[:10]
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    fp = make_fingerprint(title, content or title, date)
    entry_id = f"ep-{hashlib.sha256(fp.encode()).hexdigest()[:8]}"

    eid = store.append({
        "id": entry_id,
        "ts": ts,
        "type": episode_type,
        "title": title,
        "content": content or title,
        "tags": tag_list,
        "importance": max(1, min(10, importance)),
        "source": source,
        "fingerprint": fp,
        "links": {"facts": [], "files": []},
        "decay_status": "active",
        "quality": {},
        "retrieval": {},
    })
    click.echo(f"Logged episode: {eid}")
