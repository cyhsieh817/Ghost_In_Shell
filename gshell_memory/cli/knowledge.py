"""gish index / gish knowledge — startup-index budget and knowledge-note tooling (ch.19)."""

from __future__ import annotations

import json
from pathlib import Path

import click

from gshell_memory.memory._paths import WorkspacePaths, resolve_workspace

_WS = click.option(
    "--workspace", required=True, type=click.Path(exists=True), help="Workspace root path."
)


def _paths(workspace: str) -> WorkspacePaths:
    return WorkspacePaths(resolve_workspace(Path(workspace)))


@click.group("index")
def index_group() -> None:
    """Measure the startup index (MEMORY.md) that every session loads."""


@index_group.command("budget")
@_WS
@click.option("--json", "as_json", is_flag=True, default=False)
def budget_cmd(workspace: str, as_json: bool) -> None:
    """Measure MEMORY.md in characters. Run before adding an index line.

    Exit codes: 0 ok · 1 over max_chars (compress first) · 2 past the
    truncation edge (the tail is already being cut) · 3 MEMORY.md missing.
    """
    from gshell_memory.engines import knowledge

    result = knowledge.budget(_paths(workspace))
    if as_json:
        click.echo(json.dumps(result, ensure_ascii=False))
    elif result["status"] == "missing":
        click.echo("MEMORY.md not found", err=True)
    else:
        click.echo(
            f"{result['chars']} chars  {result['bytes']} B  {result['lines']} lines  "
            f"status={result['status']}  max={result['max_chars']}  "
            f"edge={result['truncate_edge_chars']}  headroom={result['headroom']}"
        )
    raise SystemExit(result["exit_code"])


@click.group("knowledge")
def knowledge_group() -> None:
    """Create and lint knowledge notes under memory/knowledge/."""


@knowledge_group.command("new")
@_WS
@click.argument("note_type", type=click.Choice(["feedback", "project", "reference", "user"]))
@click.argument("slug")
@click.option("--description", "-d", required=True, help="One line used to judge relevance.")
def new_cmd(workspace: str, note_type: str, slug: str, description: str) -> None:
    """Create a note skeleton with the frontmatter contract filled in."""
    from gshell_memory.engines import knowledge

    paths = _paths(workspace)
    try:
        dest = knowledge.new_note(paths, note_type, slug, description)
    except (ValueError, FileExistsError) as exc:
        raise click.ClickException(str(exc)) from exc
    rel = dest.relative_to(paths.root)
    click.echo(f"created {rel}")
    click.echo(
        "next: fill in the body, then add one index line to MEMORY.md:\n"
        f'  - "<the symptom you will have when this matters>" → [{slug}]({rel})'
    )


@knowledge_group.command("lint")
@_WS
@click.option("--json", "as_json", is_flag=True, default=False)
@click.option("--strict", is_flag=True, default=False, help="Treat warnings as failures.")
def lint_cmd(workspace: str, as_json: bool, strict: bool) -> None:
    """Check note frontmatter, broken index links, and orphan notes."""
    from gshell_memory.engines import knowledge

    result = knowledge.lint(_paths(workspace))
    if as_json:
        click.echo(json.dumps(result, ensure_ascii=False))
    else:
        for issue in result["issues"]:
            color = "red" if issue["level"] == "error" else "yellow"
            click.echo(
                click.style(f"{issue['level']:7}", fg=color)
                + f" {issue['path']}: {issue['message']}"
            )
        click.echo(
            f"{result['notes']} notes · {result['errors']} errors · {result['warnings']} warnings"
        )
    failed = result["errors"] > 0 or (strict and result["warnings"] > 0)
    raise SystemExit(1 if failed else 0)
