"""`gish memory-dir` sub-commands."""

from __future__ import annotations

from pathlib import Path

import click

from gshell_memory.engines.subdir_registry import SubdirRegistryEngine


@click.group(name="memory-dir")
def memdir_group() -> None:
    """Subdirectory registry under memory/."""


def _ws_opt(f):
    return click.option(
        "--workspace",
        type=click.Path(file_okay=False, path_type=Path),
        required=True,
    )(f)


@memdir_group.command("register")
@click.option("--path", required=True)
@click.option("--purpose", required=True)
@click.option(
    "--lifecycle",
    type=click.Choice(["permanent", "rotating", "ephemeral"]),
    required=True,
)
@_ws_opt
def register_cmd(workspace, path, purpose, lifecycle):
    SubdirRegistryEngine(workspace).register(path=path, purpose=purpose, lifecycle=lifecycle)
    click.echo(f"registered: {path}")


@memdir_group.command("list")
@_ws_opt
def list_cmd(workspace):
    for r in SubdirRegistryEngine(workspace).list_all():
        click.echo(f"{r.path:30}  {r.purpose:20}  ({r.lifecycle})")


@memdir_group.command("enforce")
@click.option("--mode", type=click.Choice(["warn", "block"]), default=None)
@_ws_opt
def enforce_cmd(workspace, mode):
    unregistered = SubdirRegistryEngine(workspace).enforce(mode=mode)
    if not unregistered:
        click.echo("clean")
        return
    for path in unregistered:
        click.echo(f"unregistered: {path}")
