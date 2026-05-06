"""Judge engine — quality verdict for episodic entries (spec § 4.7)."""

from __future__ import annotations


_HIGH_IMPORTANCE = 7
_HIGH_SCORE = 0.75
_LOW_SCORE = 0.3


def evaluate(entry: dict) -> dict:
    """Return a verdict dict for a single episodic entry.

    Verdict keys:
    - ``keep``: bool — entry is worth keeping
    - ``reason``: str — short explanation
    - ``suggested_action``: "keep" | "archive" | "review"
    """
    importance = entry.get("importance", 5)
    score = entry.get("quality", {}).get("score", 0.65)
    duplicate = entry.get("quality", {}).get("duplicate_suspect", False)
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
    from ghost_in_shell.memory._paths import WorkspacePaths, resolve_workspace
    from ghost_in_shell.memory._safe_io import read_jsonl

    paths = WorkspacePaths(resolve_workspace(Path(workspace) if not isinstance(workspace, Path) else workspace))
    if not paths.episodic.exists():
        return {"keep": 0, "archive": 0, "review": 0}

    counts: dict[str, int] = {"keep": 0, "archive": 0, "review": 0}
    for entry in read_jsonl(paths.episodic):
        verdict = evaluate(entry)
        action = verdict.get("suggested_action", "keep")
        counts[action] = counts.get(action, 0) + 1

    return counts
