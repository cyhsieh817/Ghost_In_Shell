"""Dream engine — unified nightly sleep-cycle maintenance orchestrator.

Modeled on the human sleep cycle: instead of scattering maintenance
engines across the week, one nightly "dream" reorganizes and archives
memory in the physiologically sensible order:

  light sleep (nightly)
    1. replay     — associate: replay today's episodes into the link graph
    2. rem        — consolidate: compress episodes into insights
    3. verdict    — judge: quality verdict on what was consolidated
    4. prune      — decay: active → fading → archived
    5. gate       — health: wake-up self check

  deep sleep (Sundays, or ``deep=True``)
    6. audit      — full governance audit
    7. carryover  — expire stale cross-session carryovers (7-day TTL)

Each stage is failure-isolated: a crashing engine is recorded in the
result and the dream continues, so one bad stage never blocks pruning
or the wake-up gate.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

_LIGHT_STAGES = ["replay", "rem", "verdict", "prune", "gate"]
_DEEP_STAGES = ["audit", "carryover"]


def _stage_runners(workspace: Path, *, dry_run: bool) -> dict:
    """Lazy import engines so a broken optional engine never blocks the dream."""
    from gshell_memory.engines import associate, audit, consolidate, decay, health, judge
    from gshell_memory.engines.carryover import CarryoverEngine

    def _expire_carryovers() -> dict:
        engine = CarryoverEngine(workspace)
        if dry_run:
            return {"expired": 0, "dry_run": True}
        expired = engine.expire()
        return {"expired": len(expired), "dry_run": False}

    return {
        "replay": lambda: associate.run(workspace, dry_run=dry_run),
        "rem": lambda: consolidate.run(workspace, dry_run=dry_run),
        "verdict": lambda: judge.run(workspace, dry_run=dry_run),
        "prune": lambda: decay.run(workspace, dry_run=dry_run),
        "gate": lambda: health.run(workspace, dry_run=dry_run),
        "audit": lambda: audit.run(workspace, dry_run=dry_run),
        "carryover": _expire_carryovers,
    }


def run(
    workspace: Path,
    *,
    dry_run: bool = False,
    deep: bool | None = None,
    today: date | None = None,
) -> dict:
    """Run the full sleep cycle. ``deep=None`` auto-detects Sunday."""
    workspace = Path(workspace)
    if today is None:
        today = date.today()
    if deep is None:
        deep = today.weekday() == 6  # Sunday deep sleep

    stages = _LIGHT_STAGES + (_DEEP_STAGES if deep else [])
    runners = _stage_runners(workspace, dry_run=dry_run)

    results: dict[str, dict] = {}
    failures: list[str] = []
    for name in stages:
        try:
            results[name] = runners[name]()
        except Exception as exc:
            results[name] = {"error": f"{type(exc).__name__}: {exc}"}
            failures.append(name)

    return {
        "ts": datetime.now(UTC).isoformat(),
        "mode": "deep" if deep else "light",
        "stages": results,
        "failures": failures,
        "slept_well": not failures,
        "dry_run": dry_run,
    }
