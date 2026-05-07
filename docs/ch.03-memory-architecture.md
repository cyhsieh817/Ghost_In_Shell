# Chapter 03 — Memory Architecture

Ghost In Shell maintains six distinct memory stores, each optimised for a different
access pattern. Together they form a layered memory system that balances speed,
permanence, and relevance.

---

## The Six Stores

### 1. Fact Store (`memory/fact.yml`)

Structured key-value facts about identity, preferences, tools, and rules. Read at every
session start by the agent. Designed for low latency access to high-value stable data.

Schema (top-level keys):

```yaml
identity:         # Who the agent is
  name: "Agent"
  language: "en"
  timezone: "UTC"
preferences:      # User preferences
  tech_stack: []
  forbidden_words: []
rules: []         # Absolute rules
tools: {}         # Tool configurations
archive: {}       # Inactive or historical entries
```

The fact store is the only memory loaded in full at every session. Keep it lean — aim
for under 200 lines.

### 2. Episodic Store (`memory/episodic.jsonl`)

Timestamped narrative entries recording decisions, learnings, and observations. Each entry
is a JSON object on a single line.

Required fields per entry:

```json
{
  "id": "ep_00000001",
  "ts": "2026-01-01T00:00:00Z",
  "type": "insight",
  "title": "Short summary",
  "content": "Full narrative text.",
  "tags": ["example"],
  "importance": 5,
  "fingerprint": "<sha256>",
  "quality": {
    "score": 0.7,
    "duplicate_suspect": false,
    "exclusive": false,
    "predictive": false,
    "recurrence": false
  },
  "decay_status": "active",
  "retrieval": {
    "count": 0,
    "last_accessed": null,
    "strength": 0.5
  }
}
```

**Fingerprint**: `SHA-256(title + "\n" + content + "\n" + YYYY-MM-DD)`. Used for
hard-dedup at append time.

**Soft dedup**: If a new entry's content is ≥ 80% similar to an existing entry
(SequenceMatcher ratio), it is flagged as `duplicate_suspect`.

### 3. Association Store (`memory/associations.jsonl`)

Directed edges between episodic entries, representing semantic or causal relationships.
Maintained by the `associate` engine.

```json
{"source": "ep_00000001", "target": "ep_00000002", "label": "caused_by", "weight": 0.8}
```

### 4. Brain Region Manifest (`memory/brain_region_manifest.yml`)

Routing table that maps the five brain regions to files. Governs which files are loaded
per access pattern. See [Chapter 07](ch.07-brain-regions.md).

### 5. Sanctum Registry (`memory/sanctum_registry.yml`)

Governance policy: which files require which tier of permission. See
[Chapter 06](ch.06-governance-sanctum.md).

### 6. Runtime Profiles (`memory/runtime_profiles.yml`)

Executor and launcher configuration per CLI. Tells `gish run` how to invoke each CLI
binary and which runtime profile to use for session logging.

---

## Memory Manifest (`memory/memory_manifest.yml`)

Not a store itself, but a maintenance ledger. Tracks when each engine last ran,
episode counts, and consolidation history.

```yaml
schema_version: 1
last_consolidation: null
last_decay_run: null
stats:
  episode_count: 0
  edge_count: 0
```

---

## Retrieval Strength Formula

Each episodic entry carries a `retrieval.strength` value in `[0.0, 1.0]`. This is
updated by the decay and retrieval engines using:

```
strength(t) = base_strength * exp(-λ * Δt_days) + retrieval_boost
```

where:
- `base_strength` — initial strength (default 0.5)
- `λ` — decay rate (default 0.01 per day)
- `Δt_days` — days since last access
- `retrieval_boost` — +0.1 per retrieval, capped at 1.0

The `decay` engine runs nightly (via cron) and updates `strength` for all active
entries. Entries falling below the configured threshold are marked `decay_status: faded`
and eventually moved to `archive:` namespace in the fact store.

---

## Correctness Guarantees

| Guarantee | Mechanism |
|-----------|-----------|
| No duplicate appends | SHA-256 fingerprint hard-dedup at `EpisodicStore.append` |
| No near-duplicate spam | Soft-dedup via SequenceMatcher ≥ 0.80 ratio |
| Cooldown dedup | Same fingerprint within 60 s is deduplicated |
| Schema validation | Pydantic `EpisodicEntry` model validates every append |
| Safe I/O | `_safe_io` module uses atomic writes (write to `.tmp`, rename) |
| Sanctum enforcement | Read/write/delete checked against `sanctum_registry.yml` tiers |

---

## Adding a Memory Programmatically

```python
from pathlib import Path
from ghost_in_shell.memory._paths import WorkspacePaths, resolve_workspace
from ghost_in_shell.memory.episodic import EpisodicStore, make_fingerprint

ws = resolve_workspace(Path("~/my-workspace"))
paths = WorkspacePaths(ws)
store = EpisodicStore(paths)

ts = "2026-06-01T12:00:00Z"
fp = make_fingerprint("My title", "My content", ts[:10])

entry_id = store.append({
    "id": "ep_custom_001",
    "ts": ts,
    "type": "decision",
    "title": "My title",
    "content": "My content",
    "tags": ["custom"],
    "importance": 6,
    "fingerprint": fp,
    "quality": {"score": 0.8, "duplicate_suspect": False,
                "exclusive": False, "predictive": False, "recurrence": False},
    "decay_status": "active",
    "retrieval": {"count": 0, "last_accessed": None, "strength": 0.5},
})
print(entry_id)
```

---

## Next Steps

→ [Chapter 04 — Engine Internals](ch.04-engine-internals.md)
