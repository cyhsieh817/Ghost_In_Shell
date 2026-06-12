"""gish dream — nightly sleep-cycle maintenance."""

from __future__ import annotations

from pathlib import Path

import click


@click.command("dream")
@click.option(
    "--workspace", required=True, type=click.Path(exists=True), help="Workspace root path."
)
@click.option(
    "--deep/--light",
    "deep",
    default=None,
    help="Force deep/light sleep (default: deep on Sundays).",
)
@click.option("--dry-run", is_flag=True, default=False)
def dream_cmd(workspace: str, deep: bool | None, dry_run: bool) -> None:
    """Run the unified sleep cycle: replay → rem → verdict → prune → gate.

    Deep sleep (Sundays or --deep) adds: audit → carryover expiry.
    """
    from gshell_memory.engines import dream

    result = dream.run(Path(workspace), dry_run=dry_run, deep=deep)

    for name, stage in result["stages"].items():
        ok = "error" not in stage
        mark = click.style("✓", fg="green") if ok else click.style("✗", fg="red")
        click.echo(f"  {mark} {name}: {stage}")

    if result["slept_well"]:
        click.echo(click.style(f"slept well — {result['mode']} sleep complete", fg="green"))
    else:
        click.echo(
            click.style(
                f"restless night — failed stages: {', '.join(result['failures'])}", fg="red"
            ),
            err=True,
        )
        raise SystemExit(1)
