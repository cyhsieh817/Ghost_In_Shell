"""`gish enum` sub-commands."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from gshell_memory.engines.enum_freeze import FrozenEnumEngine


@click.group(name="enum")
def enum_group() -> None:
    """Frozen enum registry."""


def _ws_opt(f):
    return click.option(
        "--workspace",
        type=click.Path(file_okay=False, path_type=Path),
        required=True,
    )(f)


@enum_group.command("freeze")
@click.option("--name", required=True)
@click.option("--value", "values", multiple=True, required=True)
@click.option("--introduced", required=True)
@click.option("--layer", required=True)
@click.option("--enforcement", type=click.Choice(["audit", "block"]), default="audit")
@click.option("--spec-ref", default=None)
@_ws_opt
def freeze_cmd(workspace, name, values, introduced, layer, enforcement, spec_ref):
    e = FrozenEnumEngine(workspace).freeze(
        name=name,
        values=list(values),
        introduced=introduced,
        layer=layer,
        enforcement=enforcement,
        spec_ref=spec_ref,
    )
    click.echo(f"frozen: {e.name} = {e.values}")


@enum_group.command("list")
@_ws_opt
def list_cmd(workspace):
    enums = FrozenEnumEngine(workspace).list_all()
    if not enums:
        click.echo("(none)")
        return
    for e in enums:
        click.echo(f"{e.name}  values={e.values}  enforcement={e.enforcement}")


@enum_group.command("validate")
@click.option("--name", required=True)
@click.option("--candidate", required=True)
@_ws_opt
def validate_cmd(workspace, name, candidate):
    if FrozenEnumEngine(workspace).validate(name, candidate):
        click.echo("ok")
    else:
        click.echo(f"REJECT: {candidate!r} not in enum {name!r}", err=True)
        sys.exit(1)
