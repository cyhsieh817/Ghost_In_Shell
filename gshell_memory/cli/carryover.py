"""`gish carryover` sub-commands."""

from __future__ import annotations

from pathlib import Path

import click

from gshell_memory.engines.carryover import CarryoverEngine


@click.group(name="carryover")
def carryover_group() -> None:
    """Cross-session task hand-off."""


def _ws_opt(f):
    return click.option(
        "--workspace",
        type=click.Path(file_okay=False, path_type=Path),
        required=True,
    )(f)


@carryover_group.command("create")
@click.option("--project", "project_slug", required=True)
@click.option("--topic", required=True)
@_ws_opt
def create_cmd(workspace, project_slug, topic):
    c = CarryoverEngine(workspace).create(project_slug=project_slug, topic=topic)
    click.echo(f"created: {c.project_slug}/{c.topic}  expires={c.expires}")


@carryover_group.command("list")
@_ws_opt
def list_cmd(workspace):
    items = CarryoverEngine(workspace).list_all()
    if not items:
        click.echo("(none)")
        return
    for c in items:
        click.echo(f"{c.project_slug:20} {c.topic:30} {c.status:9} expires={c.expires}")


@carryover_group.command("expire")
@_ws_opt
def expire_cmd(workspace):
    """Mark all overdue active carryovers as expired."""
    expired = CarryoverEngine(workspace).expire()
    if not expired:
        click.echo("(none expired)")
        return
    for c in expired:
        click.echo(f"expired: {c.project_slug}/{c.topic}")


@carryover_group.command("promote-to-episodic")
@click.option("--project", "project_slug", required=True)
@click.option("--topic", required=True)
@_ws_opt
def promote_cmd(workspace, project_slug, topic):
    path = CarryoverEngine(workspace).promote_to_episodic(project_slug=project_slug, topic=topic)
    if not path:
        click.echo("(not found)", err=True)
        return
    click.echo(f"promoted -> {path}")
