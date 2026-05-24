# Chapter 13 — Carryover

## Why this engine exists

A session ends mid-task. The agent has half-debugged a flaky test,
half-drafted a review reply, half-decided a release strategy. None of it
belongs in episodic memory yet — episodic entries are durable, dated
decisions, and half-finished work is neither. But losing the state means
the next session re-derives the same context from scratch.

Carryover is the bounded hand-off slot: a tiny `memory/carryover/`
folder of dated markdown stubs, each tied to a project and a topic, each
auto-expiring after 7 days. If the work survives the week it gets
promoted into the archive and (eventually) folded into episodic memory.
If it doesn't, it expires loudly and the agent stops trying to act on it.

Concrete example: a researcher leaves a note "follow up with the new
dataset by Friday." The carryover file `carryover_dataset_followup.md`
sits in the folder with `expires: 2026-05-31`. By Monday the engine has
flipped it to `expired` if nothing happened, and any agent listing
carryovers sees that signal.

## Schema

`Carryover` is defined in [`gshell_memory_schema/gshell_memory_schema/models.py`](../gshell_memory_schema/gshell_memory_schema/models.py).
Each entry is a markdown file with a YAML frontmatter block under
`memory/carryover/`. The validator enforces `0 <= expires - created <= 7`
days. From the v5_full golden fixture:

```yaml
---
project_slug: "fixture"
topic: "example_topic"
created: "2026-05-24"
expires: "2026-05-31"
status: "active"
---
```

Status is a `Literal["active", "expired", "promoted"]`.

## CLI walkthrough

```bash
# 1. Create a fresh carryover — expires 7 days out
gish carryover create --project research --topic dataset_followup \
    --workspace ./ws

# 2. List all carryovers with their status
gish carryover list --workspace ./ws

# 3. Sweep — flip anything past its expiry to status=expired
gish carryover expire --workspace ./ws

# 4. Promote a surviving carryover to the archive
gish carryover promote-to-episodic \
    --project research --topic dataset_followup --workspace ./ws
```

## Python API

```python
from pathlib import Path
from gshell_memory.engines.carryover import CarryoverEngine

engine = CarryoverEngine(Path("./ws"))
c = engine.create("research", "dataset_followup")
print(c.expires)                  # date 7 days from today

engine.expire()                   # active → expired sweep
engine.promote_to_episodic("research", "dataset_followup")
# returns Path to memory/_archive/carryover_research_dataset_followup.md
```

## Operational notes

- **File location**: `memory/carryover/carryover_<project>_<topic>.md`.
  One file per topic; re-creating the same topic overwrites.
- **Lifecycle**: `create` → `active` → (`expire` sweep flips to)
  `expired` → (`promote-to-episodic` moves to `memory/_archive/` with
  status `promoted` and removes the original).
- **Failure modes**: the 7-day window is enforced at construction time;
  hand-rolling a YAML with an 8-day gap will fail validation on next
  load. `promote_to_episodic` is a no-op (returns `None`) if the file
  doesn't exist.
- **Performance**: one file per carryover; linear scan on list/expire.
  The engine assumes carryover count stays small (< 100).

## Forward compatibility

- 6.0 may make the 7-day window configurable per project — today it's a
  schema-level constant.
- 6.0 may add a `promote` policy that writes a real `EpisodicEntry`
  instead of only moving the file. Today "promoted" means archived; the
  episodic write is the caller's responsibility.
