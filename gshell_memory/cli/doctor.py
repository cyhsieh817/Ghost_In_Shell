"""gish doctor — run health check (M2) + HEAL loop (M3)."""

from __future__ import annotations

from pathlib import Path

import click

from gshell_memory.engines import health


@click.command("doctor")
@click.option("--workspace", required=True, type=click.Path(exists=True), help="Workspace root path.")
@click.option("--dry-run", is_flag=True, default=False)
@click.option(
    "--heal-hooks",
    is_flag=True,
    default=False,
    help="Check heal.log for missed trigger hints and print fix instructions.",
)
def doctor_cmd(workspace: str, dry_run: bool, heal_hooks: bool) -> None:
    """Run health check on the workspace."""
    report = health.run(Path(workspace), dry_run=dry_run)
    status = report["status"]
    color = "green" if status == "ok" else "yellow"
    click.echo(click.style(f"Status: {status}", fg=color))
    click.echo(f"Episodes: {report['episode_count']}  Edges: {report['edge_count']}")
    if report["issues"]:
        for issue in report["issues"]:
            click.echo(click.style(f"  ⚠  {issue}", fg="yellow"))

    if heal_hooks:
        _print_heal_report(Path(workspace), report)


def _print_heal_report(workspace: Path, report: dict) -> None:
    """Print HEAL hook suggestions from heal.log and live report hints."""
    heal_log = workspace / ".gish" / "logs" / "heal.log"
    heal_hints = report.get("heal_hints", [])

    click.echo("\n── HEAL hooks report ──")

    if heal_hints:
        click.echo(click.style("Missed trigger hints (from this run):", fg="yellow"))
        for hint in heal_hints:
            click.echo(f"  • {hint}")

    if heal_log.exists():
        lines = heal_log.read_text(encoding="utf-8").splitlines()
        if lines:
            click.echo(click.style(f"\nHeal log ({heal_log}):", fg="yellow"))
            for line in lines[-10:]:
                click.echo(f"  {line}")

    if not heal_hints and (not heal_log.exists() or not heal_log.read_text().strip()):
        click.echo(click.style("No missed triggers detected.", fg="green"))
        return

    click.echo("\nHow to fix:")
    click.echo("  • Claude Code: add stop-hook to ~/.claude/settings.json")
    click.echo('    {"type": "command", "command": "gish log --from-session", "matcher": ".*"}')
    click.echo("  • Other CLIs: add `gish log --from-session` to your wrapper exit handler.")
    click.echo("  • Run `gish init <workspace>` to see per-CLI hook snippets.")

