# Chapter 17 — Memory Subdir Registry

## Why this engine exists

Free-form `memory/` directories devolve into archaeology. One script
creates `memory/cache/`, another `memory/tmp/`, a third
`memory/scratch_2024/` — each one perfectly reasonable on the day it
was created, collectively unreadable a year later. The subdir registry
flips the default: every subdirectory of `memory/` must be declared,
or it gets reported (`warn` mode) or rejected (`block` mode).

Concrete example: a workspace ships with three legal subdirectories —
`_archive` (permanent storage), `carryover` (rotating week-long notes),
`heartbeat_logs` (ephemeral). A rogue script that drops
`memory/random_dump/` shows up immediately in `enforce()`, and the
operator either registers the new directory deliberately or removes it
before it ossifies.

## Schema

`SubdirRegistry` and `RegisteredSubdir` are defined in
[`gshell_memory_schema/gshell_memory_schema/models.py`](../gshell_memory_schema/gshell_memory_schema/models.py).
The on-disk form is a single document at `memory/subdir_registry.yml`.
From the v5_full golden fixture:

```yaml
enforcement: "warn"
registered:
  - path: "_archive"
    purpose: "Long-term archived material."
    lifecycle: "permanent"
  - path: "carryover"
    purpose: "Cross-session task hand-off notes."
    lifecycle: "rotating"
  - path: "heartbeat_logs"
    purpose: "Heartbeat check outputs."
    lifecycle: "ephemeral"
```

`lifecycle` is a `Literal["permanent", "rotating", "ephemeral"]`;
`enforcement` is a `Literal["warn", "block"]`.

## CLI walkthrough

```bash
# 1. Register a new directory (idempotent — re-registering the same path is a no-op)
gish memory-dir register --path memory/sessions --purpose "Per-session logs" \
    --lifecycle ephemeral --workspace ./ws

# 2. List what's registered
gish memory-dir list --workspace ./ws

# 3. Walk memory/ and report any unregistered subdir (default: warn)
gish memory-dir enforce --workspace ./ws

# 4. Promote enforcement once the warns are clean
gish memory-dir enforce --mode block --workspace ./ws
```

## Python API

```python
from pathlib import Path
from gshell_memory.engines.subdir_registry import SubdirRegistryEngine

reg = SubdirRegistryEngine(Path("./ws"))
reg.register(path="memory/sessions",
             purpose="Per-session logs", lifecycle="ephemeral")

# warn mode: returns list of unregistered subdirs, never raises
stragglers = reg.enforce()
print(stragglers)

# tighten enforcement once the workspace is clean
reg.set_enforcement("block")
reg.enforce()   # raises RuntimeError if anything is still unregistered
```

## Operational notes

- **File location**: `memory/subdir_registry.yml`.
- **warn → block transition**: this is the intended adoption path. New
  workspaces start in `warn` to discover their actual on-disk shape
  without breaking anything; once `enforce()` returns an empty list
  consistently, the operator flips to `block` and any new unregistered
  directory hard-fails. The flip is a one-line config change, reversible.
- **Failure modes**: in `block` mode, `enforce()` raises `RuntimeError`
  listing every unregistered subdir. Files at the top of `memory/`
  are ignored — only directories are policed. The engine does not
  recurse; nested directories under a registered parent are implicitly
  allowed.
- **Performance**: single directory scan, linear in the number of
  direct children. Designed for workspaces with < 50 top-level
  memory subdirectories.

## Forward compatibility

- 6.0 may add a `pattern:` field on `RegisteredSubdir` to allow
  glob-based registration (e.g., `sessions_*` matching any
  session-named directory).
- 6.0 may add an `auto_register: true` policy on creation hooks so
  engines that legitimately need new directories can register them
  atomically with the directory creation, removing the warn-and-then-
  register two-step.
