"""`gish region` sub-commands."""

from __future__ import annotations

from pathlib import Path

import click

from gshell_memory.memory.brain_regions import BrainRegionStore


@click.group(name="region")
def region_group() -> None:
    """Brain region manifest management."""


def _ws_opt(f):
    return click.option(
        "--workspace",
        type=click.Path(file_okay=False, path_type=Path),
        required=True,
    )(f)


@region_group.command("declare")
@click.argument("name")
@click.option("--display", required=True)
@click.option("--core", "core_files", multiple=True)
@click.option("--on-demand", "on_demand_files", multiple=True)
@click.option("--aliases", multiple=True)
@_ws_opt
def declare_cmd(workspace, name, display, core_files, on_demand_files, aliases):
    BrainRegionStore(workspace).declare(
        name=name,
        display=display,
        core_files=list(core_files),
        on_demand_files=list(on_demand_files),
        aliases=list(aliases),
    )
    click.echo(f"declared extension region: {name}")


@region_group.command("list")
@_ws_opt
def list_cmd(workspace):
    for entry in BrainRegionStore(workspace).list_all():
        click.echo(f"{entry['name']:15} [{entry['kind']}]  {entry.get('display', '')}")
