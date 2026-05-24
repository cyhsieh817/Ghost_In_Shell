"""Health engine — report workspace integrity metrics (spec § 4.7 + § 6.5 HEAL)."""

from __future__ import annotations

import datetime
from pathlib import Path

from gshell_memory.engines._manifest import load_manifest, save_manifest, stamp_run
from gshell_memory.memory._paths import WorkspacePaths, resolve_workspace
from gshell_memory.memory._safe_io import read_jsonl

try:
    from gshell_memory_schema.models import EpisodicEntry
except ImportError:  # pragma: no cover - schema package always present in this repo
    EpisodicEntry = None  # type: ignore[assignment,misc]


def run(workspace: Path, *, dry_run: bool = False) -> dict:
    """Scan the workspace and return a health report.

    Returns a dict with counts of episodes, edges, issues, and overall status.
    Also writes HEAL hints to .gish/logs/heal.log when cron triggers are missed.
    """
    paths = WorkspacePaths(resolve_workspace(workspace))
    ts = datetime.datetime.now(datetime.UTC).isoformat()

    episode_count = sum(1 for _ in read_jsonl(paths.episodic)) if paths.episodic.exists() else 0
    edge_count = (
        sum(1 for _ in read_jsonl(paths.associations)) if paths.associations.exists() else 0
    )

    issues: list[str] = []
    if not paths.fact_yml.exists():
        issues.append("fact.yml missing")
    if not paths.memory_manifest.exists():
        issues.append("memory_manifest.yml missing")

    # Schema validation — surface ValidationError as a diagnostic, do not crash.
    # Bridge contract: tolerate LGD-style writes that may be schema-violating.
    if EpisodicEntry is not None and paths.episodic.exists():
        schema_issues = _validate_episodes(paths.episodic)
        issues.extend(schema_issues)

    heal_hints = _detect_missed_triggers(paths)

    status = "ok" if not issues else "degraded"

    report = {
        "ts": ts,
        "episode_count": episode_count,
        "edge_count": edge_count,
        "issues": issues,
        "status": status,
        "dry_run": dry_run,
        "heal_hints": heal_hints,
    }

    if not dry_run:
        manifest = load_manifest(paths)
        stamp_run(paths, "health")
        manifest["stats"] = manifest.get("stats", {})
        manifest["stats"]["episode_count"] = episode_count
        manifest["stats"]["edge_count"] = edge_count
        save_manifest(paths, manifest)

        if heal_hints:
            _write_heal_log(paths, ts, heal_hints)

    return report


def _validate_episodes(episodic_path: Path, *, max_report: int = 5) -> list[str]:
    """Validate each episode against the schema. Return human-readable issue strings.

    Never raises. Truncates after ``max_report`` entries to keep doctor output readable.
    """
    issues: list[str] = []
    invalid_count = 0
    try:
        for entry in read_jsonl(episodic_path):
            try:
                EpisodicEntry.model_validate(entry)
            except ValidationError as exc:
                invalid_count += 1
                if len(issues) < max_report:
                    ep_id = entry.get("id", "<no-id>") if isinstance(entry, dict) else "<malformed>"
                    fields = sorted({str(err.get("loc", ("?",))[0]) for err in exc.errors()})
                    issues.append(f"episode {ep_id!r}: schema violation in field(s) {fields}")
            except Exception as exc:  # pragma: no cover - defensive
                invalid_count += 1
                if len(issues) < max_report:
                    issues.append(f"episode validation error: {exc}")
    except Exception as exc:  # pragma: no cover - defensive
        issues.append(f"could not read episodic.jsonl for schema check: {exc}")
        return issues

    if invalid_count > len(issues):
        issues.append(f"... and {invalid_count - len(issues)} more schema violation(s)")
    return issues


def _detect_missed_triggers(paths: WorkspacePaths) -> list[str]:
    """Detect likely missed triggers and return hint strings."""
    hints: list[str] = []
    session_log = paths.root / ".gish" / "logs" / "session_boundaries.jsonl"
    if not session_log.exists():
        hints.append(
            "session_boundaries.jsonl not found — session-end hook may not be configured. "
            "Run `gish doctor --heal-hooks` for setup instructions."
        )
    return hints


def _write_heal_log(paths: WorkspacePaths, ts: str, hints: list[str]) -> None:
    """Append HEAL hints to .gish/logs/heal.log."""
    logs_dir = paths.logs_dir
    logs_dir.mkdir(parents=True, exist_ok=True)
    heal_log = logs_dir / "heal.log"
    lines = [f"[{ts}] HEAL hint: {h}" for h in hints]
    with heal_log.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def schedule_cron() -> str:
    return "0 6 * * *"
