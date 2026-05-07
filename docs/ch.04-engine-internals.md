# Chapter 04 — Engine Internals

Ghost In Shell ships seven engines that maintain memory quality over time. Each engine
is a pure Python module in `ghost_in_shell/engines/`. They can be invoked individually
or together via `gish run-maintenance`.

---

## Engine Overview

| Engine | Module | Purpose |
|--------|--------|---------|
| `associate` | `engines.associate` | Build association graph edges between episodes |
| `decay` | `engines.decay` | Apply strength decay to episodic entries over time |
| `consolidate` | `engines.consolidate` | Merge/summarise similar episodes to reduce noise |
| `judge` | `engines.judge` | Score episode quality; flag low-quality entries |
| `health` | `engines.health` | Report workspace integrity; emit HEAL hints |
| `audit` | `engines.audit` | Check sanctum governance compliance |
| `session_log` | `engines.session_log` | Record session boundaries from CLI stop hooks |

---

## `associate` — Association Graph Builder

**Entry point**: `ghost_in_shell.engines.associate.run(workspace: Path)`

The associate engine scans episodic entries and creates directed edges in
`memory/associations.jsonl` when two entries share tags, overlapping content, or similar
timestamps within a configurable window.

```python
from ghost_in_shell.engines import associate
from pathlib import Path

result = associate.run(Path("~/my-workspace"))
print(result["edges_created"])
```

Return dict keys: `edges_created`, `total_edges`, `status`.

---

## `decay` — Strength Decay

**Entry point**: `ghost_in_shell.engines.decay.run(workspace: Path)`

Applies exponential decay to `retrieval.strength` for all active episodic entries.
The decay formula uses a configurable λ (lambda) decay rate from `memory_manifest.yml`.

Entries whose strength falls below the configured `faded_threshold` (default: 0.1)
have their `decay_status` updated to `"faded"`.

Return dict keys: `decayed`, `faded`, `status`.

---

## `consolidate` — Episode Consolidation

**Entry point**: `ghost_in_shell.engines.consolidate.run(workspace: Path)`

When the episode count exceeds the `next_consolidation_trigger.threshold` in
`memory_manifest.yml` (default: 20 new episodes), consolidation runs. It groups similar
episodes using SequenceMatcher and creates summary entries, marking the originals as
`decay_status: consolidated`.

This keeps the episodic store from growing unbounded while preserving the essential
narrative.

Return dict keys: `groups_found`, `summaries_created`, `status`.

---

## `judge` — Quality Scoring

**Entry point**: `ghost_in_shell.engines.judge.run(workspace: Path)`

Scores each episode across five quality dimensions:

| Dimension | Meaning |
|-----------|---------|
| `duplicate_suspect` | Too similar to an existing episode |
| `exclusive` | Covers unique information not found elsewhere |
| `predictive` | Contains a prediction about future state |
| `recurrence` | Pattern recurs across multiple episodes |
| `score` | Composite quality score 0.0–1.0 |

The judge does not delete entries — it only annotates the `quality` field so other
engines (decay, consolidate) can prioritise accordingly.

Return dict keys: `scored`, `updated`, `status`.

---

## `health` — Workspace Health Check

**Entry point**: `ghost_in_shell.engines.health.run(workspace: Path, *, dry_run: bool = False)`

Produces a health report dict:

```python
{
    "ts": "2026-01-01T12:00:00+00:00",
    "episode_count": 42,
    "edge_count": 18,
    "issues": [],
    "status": "ok",           # "ok" | "degraded"
    "dry_run": False,
    "heal_hints": []
}
```

When `heal_hints` is non-empty, hints are written to `.gish/logs/heal.log`. The
`gish doctor --heal-hooks` command reads this log and prints fix instructions.

HEAL hints are emitted when session boundaries are missing — a sign that the session-end
hook is not configured.

---

## `audit` — Sanctum Compliance

**Entry point**: `ghost_in_shell.engines.audit.run(workspace: Path)`

Checks that files listed in `sanctum_registry.yml` are present and accessible according
to their declared tier. Also validates that no disallowed actions have been performed
(based on the audit log at `memory/.fact_audit.jsonl`).

Return dict keys: `violations`, `warnings`, `status`.

---

## `session_log` — Session Boundary Recording

**Entry point**: `ghost_in_shell.engines.session_log.record(workspace: Path, ...)`

Called by `gish log --from-session` at session end. Records a session boundary entry to
`.gish/logs/session_boundaries.jsonl`.

This is what lets the health engine detect whether session hooks are properly configured.

---

## Running All Engines via CLI

```bash
# Run all maintenance engines
gish run-maintenance --workspace ~/my-workspace

# Dry-run mode (no writes)
gish run-maintenance --workspace ~/my-workspace --dry-run

# Just run health check
gish doctor --workspace ~/my-workspace
```

---

## Running Engines Programmatically

```python
from pathlib import Path
from ghost_in_shell.engines import associate, decay, consolidate, health

ws = Path("~/my-workspace").expanduser().resolve()

health.run(ws)
decay.run(ws)
consolidate.run(ws)
associate.run(ws)
```

---

## Engine Scheduling

Engines are designed to run on a cron schedule. The default schedule installed by
`gish init --schedule` is:

```cron
0 6 * * *  gish run-maintenance --workspace /path/to/workspace
```

See [Chapter 08 — Cron & Hooks](ch.08-cron-hooks.md) for full scheduling details.

---

## Next Steps

→ [Chapter 05 — Multi-CLI Adapters](ch.05-multi-cli-adapters.md)
