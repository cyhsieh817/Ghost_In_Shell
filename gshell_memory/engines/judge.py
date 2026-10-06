"""Judge engine — quality verdicts for episodes and consolidation proposals.

Two jobs:

* :func:`evaluate` / :func:`run` — advisory keep/archive/review verdicts for
  existing episodes (the nightly ``verdict`` stage).
* :func:`grade_proposal` — the gate in front of every consolidation. The
  consolidate engine writes a proposal; only an A-C grade lets it apply.

``grade_proposal`` combines deterministic pre-checks with an optional external
judge command (for example a script that asks a *different* model than the one
that wrote the proposal). The external judge fails closed: if it is configured
but cannot run or returns no grade, the proposal is not applied.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

_HIGH_IMPORTANCE = 7
_HIGH_SCORE = 0.75
_LOW_SCORE = 0.3

PROTECTED_IMPORTANCE = 8
PASSING_GRADES = ("A", "B", "C")
_GRADE_ORDER = "ABCDF"
_JUDGE_TIMEOUT_S = 300


def grade_proposal(
    proposal: dict,
    entries: list[dict],
    *,
    judge_command: list[str] | None = None,
    proposal_path: Path | None = None,
    min_sources: int = 3,
) -> dict:
    """Grade a consolidation proposal. Returns ``{grade, passed, checks, external}``.

    Hard failures (sources missing, protected memories consumed, id clash)
    grade F; soft failures grade D. Both block the apply.
    """
    by_id = {e.get("id"): e for e in entries if e.get("id")}
    active = {i for i, e in by_id.items() if e.get("decay_status") != "archived"}
    sources = list(proposal.get("sources") or [])
    merged = proposal.get("merged") or {}

    missing = [s for s in sources if s not in active]
    protected = [
        s for s in sources if (by_id.get(s, {}).get("importance") or 0) >= PROTECTED_IMPORTANCE
    ]
    checks = [
        (
            "sources-exist",
            not missing,
            "hard",
            f"missing or archived: {missing}" if missing else "ok",
        ),
        (
            "protected-importance",
            not protected,
            "hard",
            f"importance >= {PROTECTED_IMPORTANCE}: {protected}" if protected else "ok",
        ),
        ("id-unique", merged.get("id") not in by_id, "hard", str(merged.get("id"))),
        ("enough-evidence", len(sources) >= min_sources, "soft", f"{len(sources)} sources"),
        (
            "links-back",
            sorted(merged.get("linked_to") or []) == sorted(sources),
            "soft",
            "linked_to",
        ),
        ("non-empty", bool(str(merged.get("content", "")).strip()), "soft", "content"),
    ]

    if any(not ok and level == "hard" for _, ok, level, _ in checks):
        grade = "F"
    elif any(not ok for _, ok, _, _ in checks):
        grade = "D"
    else:
        grade = "A"

    external = None
    if judge_command:
        external = _run_external_judge(judge_command, proposal_path)
        ext_grade = external.get("grade")
        grade = _worse(grade, ext_grade) if ext_grade else "F"

    return {
        "grade": grade,
        "passed": grade in PASSING_GRADES,
        "checks": [{"name": n, "ok": ok, "level": lvl, "detail": d} for n, ok, lvl, d in checks],
        "external": external,
    }


def _run_external_judge(cmd: list[str], proposal_path: Path | None) -> dict:
    """Run ``cmd <proposal_path>``; the last stdout line must start with a grade A-F."""
    if proposal_path is None:
        return {"grade": None, "error": "no proposal file to judge"}
    try:
        proc = subprocess.run(
            [*cmd, str(proposal_path)],
            capture_output=True,
            text=True,
            timeout=_JUDGE_TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"grade": None, "error": f"{type(exc).__name__}: {exc}"}
    lines = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
    first = lines[-1][:1].upper() if lines else ""
    if proc.returncode != 0 or first not in _GRADE_ORDER:
        return {"grade": None, "error": f"rc={proc.returncode}, no grade on last line"}
    return {"grade": first, "error": None}


def _worse(a: str, b: str) -> str:
    return a if _GRADE_ORDER.index(a) >= _GRADE_ORDER.index(b) else b


def evaluate(entry: dict) -> dict:
    """Return a verdict dict for a single episodic entry.

    Verdict keys:
    - ``keep``: bool — entry is worth keeping
    - ``reason``: str — short explanation
    - ``suggested_action``: "keep" | "archive" | "review"
    """
    importance = entry.get("importance", 5)
    quality = entry.get("quality") or {}  # absent or null on schema-valid entries
    score = quality.get("score", 0.65)
    duplicate = quality.get("duplicate_suspect", False)
    decay_status = entry.get("decay_status", "active")

    if decay_status == "archived":
        return {"keep": False, "reason": "already archived", "suggested_action": "archive"}

    if duplicate:
        return {"keep": False, "reason": "duplicate suspect", "suggested_action": "review"}

    if importance >= _HIGH_IMPORTANCE and score >= _HIGH_SCORE:
        return {"keep": True, "reason": "high importance + high score", "suggested_action": "keep"}

    if score < _LOW_SCORE:
        return {"keep": False, "reason": "low quality score", "suggested_action": "archive"}

    return {"keep": True, "reason": "within acceptable range", "suggested_action": "keep"}


def run(workspace, *, dry_run: bool = False) -> dict:
    """Batch-evaluate all episodic entries and return a summary."""
    from pathlib import Path

    from gshell_memory.memory._paths import WorkspacePaths, resolve_workspace
    from gshell_memory.memory._safe_io import read_jsonl

    paths = WorkspacePaths(
        resolve_workspace(Path(workspace) if not isinstance(workspace, Path) else workspace)
    )
    if not paths.episodic.exists():
        return {"keep": 0, "archive": 0, "review": 0}

    counts: dict[str, int] = {"keep": 0, "archive": 0, "review": 0}
    for entry in read_jsonl(paths.episodic):
        verdict = evaluate(entry)
        action = verdict.get("suggested_action", "keep")
        counts[action] = counts.get(action, 0) + 1

    return counts
