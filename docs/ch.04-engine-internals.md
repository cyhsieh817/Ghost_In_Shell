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

## Capability engines (M6)

Beyond the seven maintenance engines above, the M6 milestone introduces seven capability engines. These do not run on the maintenance cron; instead they expose declarative configuration files under `memory/` and small Python entry points that callers (skills, hooks, CLI sub-commands) invoke on demand. Each engine ships with a `gish` sub-command for inspection and a frozen YAML schema so workspaces can evolve without breaking downstream agents.

### `sop_dispatch` — Trigger-Matched Required-Reading Dispatcher

**Entry point**: `ghost_in_shell.engines.sop_dispatch.SOPEngine`

Reads `memory/sop_dispatch.yml`, a table of trigger phrases mapped to required reading material (SOPs, templates, checklists). When an agent receives user input matching a trigger, `SOPEngine.trigger(phrase)` returns the ordered list of documents that must be loaded before proceeding. `list()` enumerates all registered SOPs and `register(entry)` appends new mappings while preserving precedence. The engine guarantees deterministic dispatch: identical input always yields the same SOP bundle, which makes it safe to wire into pre-prompt hooks. Designed so that domain-specific workflows (popsci, proposal writing, slide decks) can be onboarded without touching CLI code.

### `archive_routing` — Priority-Sorted Routing Decision Tree

**Entry point**: `ghost_in_shell.engines.archive_routing.ArchiveRouter`

Reads `memory/archive_routing.yml`, a priority-sorted list of `condition → target_dir` rules. Given a candidate artifact (path, tags, frontmatter), `ArchiveRouter.preview(artifact)` walks the rules top-down and returns the first matching destination plus the rule trace, without performing the move. This dry-run posture lets callers confirm routing before mutating disk. Conditions support tag predicates, path globs, and frontmatter equality checks; ties are broken by declaration order, so higher-priority rules sit at the top of the file. The engine is the canonical answer to "where does this file belong" and underpins both manual archive commands and automated post-write hooks.

### `carryover` — 7-Day Cross-Session Task Hand-Off

**Entry point**: `ghost_in_shell.engines.carryover.CarryoverEngine`

Manages `memory/carryover/*.md` notes, each with frontmatter recording `created_at`, `expires_at`, `owner`, and `status`. `create(task)` writes a new carryover with a default 7-day TTL so an unfinished thread survives a session boundary. `expire()` sweeps stale notes (past `expires_at`) into the archive, and `promote(note)` upgrades a carryover into a tracked task when the work resumes. The 7-day window is deliberately short: longer-lived intent belongs in episodic memory or a project plan. Together these three operations form a minimal cross-session inbox that prevents in-flight work from being silently dropped.

### `frozen_enums` — Locked State-Machine Values

**Entry point**: `ghost_in_shell.engines.frozen_enums.FrozenEnumEngine`

Reads `memory/frozen_enums.yml`, which records enum names whose value sets are contractually frozen (e.g. `source.kind` with 18 values, `session.status` with 6). `freeze(name, values)` locks a new enum and `validate(name, value)` checks an incoming value against the locked set, raising on drift. Freezing prevents the silent value-set expansion that erodes downstream consumers; any change requires an explicit unfreeze plus a migration plan. The engine is intentionally dumb: it stores nothing about semantics, only the exact allowed strings, so platform contracts stay readable in a single YAML file.

### `heartbeat` — Periodic Self-Check + Log Emission

**Entry point**: `ghost_in_shell.engines.heartbeat.HeartbeatEngine`

Reads `memory/heartbeat.yml` and emits a periodic liveness record to `.gish/logs/heartbeat.jsonl`. `run()` executes a single self-check (workspace reachable, memory writable, last maintenance timestamp fresh) and appends one log entry; `install()` writes a platform-appropriate scheduler snippet (cron on Linux, launchd plist on macOS) so the run happens on the configured cadence. The log lets external monitors confirm an agent is alive even when no user input is flowing, and gives the health engine a concrete signal for "system has been quiet too long". Default cadence is every 15 minutes.

### `brain_region` — Opt-In Regions Beyond the Default Five

**Entry point**: `ghost_in_shell.engines.brain_region.BrainRegionStore`

The default brain has five regions (episodic, semantic, procedural, working, sensory). For workspaces that need more, `BrainRegionStore.declare(name, schema)` registers an opt-in region in the `extensions` block of `brain_region_manifest.yml`. The manifest stays the single source of truth for which regions exist and what fields each entry must carry, so consolidate/associate/decay engines can continue to operate uniformly. Extensions are explicitly opt-in: a workspace gets no extra regions until it declares them, which keeps minimal installs minimal and stops region sprawl. Declared regions appear in `gish region list` and become valid targets for writes immediately.

### `subdir_registry` — `memory/` Subdirectory White-List

**Entry point**: `ghost_in_shell.engines.subdir_registry.SubdirRegistryEngine`

Reads `memory/subdir_registry.yml`, a white-list of approved subdirectory names under `memory/` plus an enforcement level (`warn` or `block`). `enforce(path)` checks a proposed write target against the list: `warn` emits a log entry and continues, `block` raises and aborts the write. This keeps the memory tree shaped according to the documented layout, so agents do not silently grow ad-hoc directories that the rest of the system cannot find. New subdirectories are added explicitly via the registry, which makes layout changes auditable and reversible.

---

## Next Steps

→ [Chapter 05 — Multi-CLI Adapters](ch.05-multi-cli-adapters.md)
