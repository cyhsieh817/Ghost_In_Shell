"""`gish sop` sub-commands."""

from __future__ import annotations

from pathlib import Path

import click
from gshell_memory_schema.models import SOPRoute

from gshell_memory.engines.sop import SOPEngine


@click.group(name="sop")
def sop_group() -> None:
    """SOP dispatch — natural-language triggers to required reading."""


def _workspace_option(f):
    return click.option(
        "--workspace",
        type=click.Path(file_okay=False, path_type=Path),
        required=True,
        help="Path to the gshell workspace.",
    )(f)


@sop_group.command("list")
@_workspace_option
def list_cmd(workspace: Path) -> None:
    """List registered SOP routes."""
    engine = SOPEngine(workspace)
    routes = engine.list_routes()
    if not routes:
        click.echo("(no routes registered)")
        return
    for r in routes:
        click.echo(f"{r.name}  triggers={r.triggers}  must_read={r.must_read}")


@sop_group.command("register")
@click.option("--name", required=True)
@click.option("--trigger", "triggers", multiple=True, required=True)
@click.option("--must-read", "must_read", multiple=True, required=True)
@click.option("--also-read", "also_read", multiple=True)
@click.option("--note", default=None)
@_workspace_option
def register_cmd(
    workspace: Path,
    name: str,
    triggers: tuple[str, ...],
    must_read: tuple[str, ...],
    also_read: tuple[str, ...],
    note: str | None,
) -> None:
    """Register a new SOP route."""
    route = SOPRoute(
        name=name,
        triggers=list(triggers),
        must_read=list(must_read),
        also_read=list(also_read),
        note=note,
    )
    SOPEngine(workspace).register(route)
    click.echo(f"registered: {name}")


@sop_group.command("trigger")
@click.option("--text", required=True, help="Input text to match against triggers.")
@_workspace_option
def trigger_cmd(workspace: Path, text: str) -> None:
    """Show which routes match given input text."""
    hits = SOPEngine(workspace).trigger(text)
    if not hits:
        click.echo("(no match)")
        return
    for r in hits:
        click.echo(f"{r.name}:")
        for f in r.must_read:
            click.echo(f"  must_read: {f}")


@sop_group.command("test")
@_workspace_option
def test_cmd(workspace: Path) -> None:
    """Validate all SOP routes parse cleanly."""
    routes = SOPEngine(workspace).list_routes()
    click.echo(f"OK: {len(routes)} route(s) loaded")
