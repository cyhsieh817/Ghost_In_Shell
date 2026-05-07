"""gish init — workspace initialisation wizard (M3)."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from ghost_in_shell.adapters import get_adapter

_ADAPTER_NAMES = ["claude", "gemini", "codex", "copilot"]

_TEMPLATE_BASE = Path(__file__).resolve().parents[1] / "templates"
_IDENTITY_TMPL = _TEMPLATE_BASE / "identity"
_MEMORY_TMPL = _TEMPLATE_BASE / "memory"


def _load_template(path: Path, substitutions: dict[str, str] | None = None) -> str:
    text = path.read_text(encoding="utf-8")
    if substitutions:
        for key, value in substitutions.items():
            text = text.replace(f"{{{{{key}}}}}", value)
    return text


def _seed_file(dest: Path, template_path: Path, substitutions: dict[str, str] | None = None) -> bool:
    """Write dest from template only if dest does not yet exist. Returns True if written."""
    if dest.exists():
        return False
    text = _load_template(template_path, substitutions)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    return True


def _seed_empty(dest: Path) -> bool:
    if dest.exists():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("", encoding="utf-8")
    return True


@click.command("init")
@click.argument("workspace")
@click.option("--schedule/--no-schedule", default=False, help="Install cron schedule after init.")
@click.option("--auto-hooks", is_flag=True, default=False, help="Auto-append hooks (with .bak backup).")
@click.option("--non-interactive", is_flag=True, default=False, help="Skip prompts; use defaults.")
def init_cmd(workspace: str, schedule: bool, auto_hooks: bool, non_interactive: bool) -> None:
    """Initialize a Ghost In Shell workspace at WORKSPACE."""
    # Step 1 — resolve path
    ws = Path(workspace).expanduser().resolve()
    ws.mkdir(parents=True, exist_ok=True)
    click.echo(f"✓ workspace: {ws}")

    # Step 2 — seed memory files
    mem = ws / "memory"
    mem.mkdir(exist_ok=True)

    today = _today_str()
    subst = {"workspace_name": ws.name, "workspace_path": str(ws), "TODAY": today}

    memory_seeds = [
        (mem / "fact.yml", _MEMORY_TMPL / "fact.yml.template"),
        (mem / "brain_region_manifest.yml", _MEMORY_TMPL / "brain_region_manifest.yml.template"),
        (mem / "sanctum_registry.yml", _MEMORY_TMPL / "sanctum_registry.yml.template"),
        (mem / "runtime_profiles.yml", _MEMORY_TMPL / "runtime_profiles.yml.template"),
        (mem / "memory_manifest.yml", _MEMORY_TMPL / "memory_manifest.yml.template"),
    ]
    for dest, tmpl in memory_seeds:
        written = _seed_file(dest, tmpl, subst)
        _echo_seed(dest, ws, written)

    for empty_file in ["episodic.jsonl", "associations.jsonl"]:
        dest = mem / empty_file
        written = _seed_empty(dest)
        _echo_seed(dest, ws, written)

    # Step 3 — create .gish/config.yml
    gish_dir = ws / ".gish"
    gish_dir.mkdir(exist_ok=True)
    (gish_dir / "logs").mkdir(exist_ok=True)
    config_dest = gish_dir / "config.yml"
    written = _seed_file(config_dest, _IDENTITY_TMPL / "config.yml.template", subst)
    _echo_seed(config_dest, ws, written)

    # Step 3b — create IDENTITY.md and SOUL.md at workspace root
    for tmpl_name, dest_name in [("IDENTITY.md.template", "IDENTITY.md"), ("SOUL.md.template", "SOUL.md")]:
        dest = ws / dest_name
        written = _seed_file(dest, _IDENTITY_TMPL / tmpl_name, subst)
        _echo_seed(dest, ws, written)

    # Step 4 — detect installed CLIs and print hook snippets
    detected = _detect_adapters()
    if detected:
        click.echo("\n── Hook snippets for detected CLIs ──")
        for name in detected:
            adapter = get_adapter(name)
            click.echo(f"\n[{name}] session-start hook:")
            click.echo(adapter.session_start_hook())
            click.echo(f"[{name}] session-end hook:")
            click.echo(adapter.session_end_hook())
    else:
        click.echo("\n(No known CLIs detected; install claude/gemini/codex/gh to see hook snippets.)")

    # Step 5 — cron schedule
    do_schedule = schedule
    if not do_schedule and not non_interactive:
        do_schedule = click.confirm("\nInstall cron schedule?", default=False)

    if do_schedule:
        from ghost_in_shell.engines._cron import install_cron

        result = install_cron(ws)
        _echo_cron_result(result)

    click.echo("\n✓ gish init complete.")
    click.echo(_next_steps(ws, detected))


def _today_str() -> str:
    import datetime

    return datetime.date.today().isoformat()


def _detect_adapters() -> list[str]:
    detected = []
    for name in _ADAPTER_NAMES:
        try:
            adapter = get_adapter(name)
            if adapter.detect_installation():
                detected.append(name)
        except Exception:
            pass
    return detected


def _echo_seed(dest: Path, ws: Path, written: bool) -> None:
    rel = dest.relative_to(ws)
    status = "created" if written else "exists (skipped)"
    click.echo(f"  {rel}: {status}")


def _echo_cron_result(result: dict) -> None:
    status = result.get("status", "unknown")
    if status == "installed":
        click.echo("✓ Cron schedule installed.")
    elif status == "already_installed":
        click.echo("✓ Cron schedule already present (skipped).")
    elif status in ("emitted_xml", "emitted_sh"):
        path = result.get("path", "")
        click.echo(f"✓ Schedule emitted to: {path}")
    else:
        detail = result.get("detail", "")
        click.echo(f"⚠  Cron install issue: {status}" + (f" — {detail}" if detail else ""))


def _next_steps(ws: Path, detected: list[str]) -> str:
    lines = [
        "",
        "── Next steps ──",
        f"  1. Edit {ws / 'IDENTITY.md'} to describe your workspace.",
        f"  2. Edit {ws / 'SOUL.md'} to choose a persona.",
        f"  3. Edit {ws / 'memory' / 'fact.yml'} to set identity & preferences.",
        "  4. Add the hook snippets above to your CLI configuration.",
        "  5. Run `gish doctor --workspace <path>` to verify workspace health.",
    ]
    if not detected:
        lines.append("  6. Install a supported CLI: claude / gemini / codex / gh")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(init_cmd())

