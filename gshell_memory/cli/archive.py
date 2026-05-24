"""`gish archive route` sub-commands."""

from __future__ import annotations

from pathlib import Path

import click
from gshell_memory_schema.models import ArchiveRoute

from gshell_memory.engines.archive_router import ArchiveRouter


@click.group(name="archive")
def archive_group() -> None:
    """Archive routing decision tree."""


@archive_group.group(name="route")
def route_subgroup() -> None:
    """Manage archive routes."""


def _ws_opt(f):
    return click.option(
        "--workspace",
        type=click.Path(file_okay=False, path_type=Path),
        required=True,
    )(f)


@route_subgroup.command("add")
@click.option("--condition", required=True)
@click.option("--target-dir", required=True)
@click.option("--naming-pattern", required=True)
@click.option("--priority", type=int, required=True)
@click.option("--frontmatter", "frontmatter_required", multiple=True)
@click.option("--note", default=None)
@_ws_opt
def add_cmd(workspace, condition, target_dir, naming_pattern, priority, frontmatter_required, note):
    route = ArchiveRoute(
        condition=condition,
        target_dir=target_dir,
        naming_pattern=naming_pattern,
        frontmatter_required=list(frontmatter_required),
        note=note,
        priority=priority,
    )
    ArchiveRouter(workspace).add(route)
    click.echo(f"added route at priority {priority}")


@route_subgroup.command("list")
@_ws_opt
def list_cmd(workspace):
    routes = ArchiveRouter(workspace).list_routes()
    if not routes:
        click.echo("(no routes)")
        return
    for r in routes:
        click.echo(f"[{r.priority:>3}] {r.condition} -> {r.target_dir} ({r.naming_pattern})")


@route_subgroup.command("preview")
@click.option("--input", "input_text", required=True)
@_ws_opt
def preview_cmd(workspace, input_text):
    chosen = ArchiveRouter(workspace).preview(input_text)
    if not chosen:
        click.echo("(no route matches)")
        return
    click.echo(f"matched: {chosen.condition}")
    click.echo(f"target_dir: {chosen.target_dir}")
    click.echo(f"naming: {chosen.naming_pattern}")
