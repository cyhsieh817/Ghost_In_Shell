"""gish migrate — workspace migration utilities (spec § 11.4)."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import click

_VALID_REGIONS = {"hippocampus", "prefrontal", "limbic", "cerebellum", "default"}

_OPTIONAL_FILES = [
    "sanctum_registry.yml",
    "associations.jsonl",
    "runtime_profiles.yml",
    "memory_manifest.yml",
]


# ---------------------------------------------------------------------------
# Fingerprint helper (mirrors EpisodicStore._fp)
# ---------------------------------------------------------------------------

def _compute_fingerprint(title: str, content: str, ts: str) -> str:
    date_part = ts[:10]
    raw = f"{title}\n{content}\n{date_part}"
    return hashlib.sha256(raw.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Internal migration helpers
# ---------------------------------------------------------------------------

def _merge_fact_files(old_mem: Path, new_mem: Path, dry_run: bool) -> int:
    """Merge all fact*.yml / fact_*.yml files into a single fact.yml.

    Entries whose key starts with 'archive/' or whose value is falsy go into
    the top-level ``archive:`` namespace.  Returns the count of merged keys.
    """
    import yaml  # type: ignore[import-untyped]

    pattern_files = list(old_mem.glob("fact*.yml")) + list(old_mem.glob("fact_*.yml"))
    # Deduplicate while preserving order
    seen: set[Path] = set()
    fact_files: list[Path] = []
    for f in pattern_files:
        if f not in seen:
            fact_files.append(f)
            seen.add(f)

    merged: dict = {}
    archive: dict = {}

    for fpath in fact_files:
        try:
            data = yaml.safe_load(fpath.read_text(encoding="utf-8")) or {}
        except Exception as exc:
            click.echo(f"  ⚠  Could not parse {fpath.name}: {exc}")
            continue
        if not isinstance(data, dict):
            continue
        for key, value in data.items():
            if key == "archive" and isinstance(value, dict):
                archive.update(value)
                continue
            if key.startswith("archive/") or not value:
                archive[key] = value
            else:
                merged[key] = value

    if archive:
        merged["archive"] = archive

    if not dry_run:
        new_mem.mkdir(parents=True, exist_ok=True)
        dest = new_mem / "fact.yml"
        dest.write_text(yaml.dump(merged, allow_unicode=True, sort_keys=False), encoding="utf-8")

    return len(merged) - (1 if "archive" in merged else 0) + len(archive)


def _migrate_episodic(old_mem: Path, new_mem: Path, dry_run: bool) -> int:
    """Copy episodic.jsonl, recomputing missing or wrong fingerprints.

    Returns the count of migrated episodes.
    """
    src = old_mem / "episodic.jsonl"
    if not src.exists():
        return 0

    lines: list[str] = []
    for raw_line in src.read_text(encoding="utf-8").splitlines():
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            entry: dict = json.loads(raw_line)
        except json.JSONDecodeError:
            continue

        title = entry.get("title", "")
        content = entry.get("content", "")
        ts = entry.get("ts", "")
        expected_fp = _compute_fingerprint(title, content, ts)

        if entry.get("fingerprint") != expected_fp:
            entry["fingerprint"] = expected_fp

        lines.append(json.dumps(entry, ensure_ascii=False))

    if not dry_run and lines:
        new_mem.mkdir(parents=True, exist_ok=True)
        dest = new_mem / "episodic.jsonl"
        dest.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return len(lines)


def _migrate_brain_regions(old_mem: Path, new_mem: Path, dry_run: bool) -> int:
    """Copy brain_region_manifest.yml, coercing invalid region names to 'default'.

    Returns the count of regions that were coerced.
    """
    import yaml  # type: ignore[import-untyped]

    src = old_mem / "brain_region_manifest.yml"
    if not src.exists():
        return 0

    try:
        data = yaml.safe_load(src.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        click.echo(f"  ⚠  Could not parse brain_region_manifest.yml: {exc}")
        return 0

    coerced = 0
    regions: dict = data.get("regions", {})
    new_regions: dict = {}

    for region_name, region_data in regions.items():
        if region_name not in _VALID_REGIONS:
            click.echo(f"  → Coercing brain region '{region_name}' → 'default'")
            existing_default = new_regions.get("default", {})
            # Merge files_in / core_files from invalid region into default
            for files_key in ("core_files", "on_demand_files", "files_in"):
                incoming = (region_data or {}).get(files_key, [])
                existing_default.setdefault(files_key, [])
                existing_default[files_key].extend(incoming)
            new_regions["default"] = existing_default
            coerced += 1
        else:
            new_regions[region_name] = region_data

    data["regions"] = new_regions

    if not dry_run:
        new_mem.mkdir(parents=True, exist_ok=True)
        dest = new_mem / "brain_region_manifest.yml"
        dest.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    elif not dry_run:
        shutil.copy2(src, new_mem / "brain_region_manifest.yml")

    return coerced


def _copy_optional_files(old_mem: Path, new_mem: Path, dry_run: bool) -> None:
    """Copy optional memory files if they exist in old_workspace."""
    for filename in _OPTIONAL_FILES:
        src = old_mem / filename
        if src.exists():
            if not dry_run:
                new_mem.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, new_mem / filename)
            click.echo(f"  ✓ copied {filename}")
        else:
            click.echo(f"  - {filename} not found, skipping")


def _init_gish_config(new_ws: Path, dry_run: bool) -> None:
    """Create .gish/config.yml in the new workspace if missing."""
    config_path = new_ws / ".gish" / "config.yml"
    if config_path.exists():
        return
    if not dry_run:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        (config_path.parent / "logs").mkdir(exist_ok=True)
        config_path.write_text(
            "schema_version: 1\nworkspace_name: migrated\n",
            encoding="utf-8",
        )
        click.echo("  ✓ created .gish/config.yml")


# ---------------------------------------------------------------------------
# CLI group + commands
# ---------------------------------------------------------------------------


@click.group("migrate")
def migrate_cmd() -> None:
    """Migration utilities for Ghost In Shell workspaces."""


@migrate_cmd.command("v4")
@click.argument("old_workspace")
@click.argument("new_workspace")
@click.option("--dry-run", is_flag=True, default=False, help="Preview changes without writing files.")
def migrate_v4_cmd(old_workspace: str, new_workspace: str, dry_run: bool) -> None:
    """Migrate a v4.1 workspace to v5 format.

    OLD_WORKSPACE is the source v4.1 workspace directory.
    NEW_WORKSPACE is the destination v5 workspace (created if needed).
    """
    old_ws = Path(old_workspace).expanduser().resolve()
    new_ws = Path(new_workspace).expanduser().resolve()

    # Step 1 — validate source
    if not old_ws.is_dir():
        raise click.BadParameter(f"Not a directory: {old_ws}", param_hint="old_workspace")

    click.echo(f"{'[DRY RUN] ' if dry_run else ''}Migrating: {old_ws} → {new_ws}")

    if not dry_run:
        new_ws.mkdir(parents=True, exist_ok=True)

    old_mem = old_ws / "memory"
    new_mem = new_ws / "memory"

    # Step 2 — merge fact files
    click.echo("\n── Step 1: Merge fact files ──")
    fact_count = _merge_fact_files(old_mem, new_mem, dry_run)
    click.echo(f"  ✓ merged {fact_count} fact keys → fact.yml")

    # Step 3 — copy & recompute episodic
    click.echo("\n── Step 2: Migrate episodic.jsonl ──")
    ep_count = _migrate_episodic(old_mem, new_mem, dry_run)
    click.echo(f"  ✓ migrated {ep_count} episodes (fingerprints verified/recomputed)")

    # Step 4 — coerce brain regions
    click.echo("\n── Step 3: Coerce brain regions ──")
    coerced = _migrate_brain_regions(old_mem, new_mem, dry_run)
    if coerced == 0:
        click.echo("  ✓ all regions valid (no coercion needed)")
    else:
        click.echo(f"  ✓ coerced {coerced} invalid region(s) → 'default'")

    # Step 5 — copy optional files
    click.echo("\n── Step 4: Copy optional files ──")
    _copy_optional_files(old_mem, new_mem, dry_run)

    # Step 6 — initialise .gish/config.yml
    click.echo("\n── Step 5: Initialise workspace config ──")
    _init_gish_config(new_ws, dry_run)

    # Step 7 — run doctor (only when not dry_run and workspace is writable)
    if not dry_run and new_ws.is_dir():
        click.echo("\n── Step 6: Run gish doctor ──")
        try:
            from ghost_in_shell.engines import health

            report = health.run(new_ws)
            status = report["status"]
            click.echo(f"  Status: {status}  Episodes: {report['episode_count']}  Edges: {report['edge_count']}")
            if report.get("issues"):
                for issue in report["issues"]:
                    click.echo(f"  ⚠  {issue}")
        except Exception as exc:
            click.echo(f"  ⚠  doctor failed: {exc}")

    # Step 8 — summary
    click.echo("\n── Migration summary ──")
    click.echo(f"  Facts merged:     {fact_count}")
    click.echo(f"  Episodes:         {ep_count}")
    click.echo(f"  Regions coerced:  {coerced}")
    if dry_run:
        click.echo("\n[DRY RUN] No files were written.")
    else:
        click.echo(f"\n✓ Migration complete → {new_ws}")
