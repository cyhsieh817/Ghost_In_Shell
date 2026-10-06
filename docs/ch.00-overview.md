# Chapter 00 — Overview

Ghost In Shell (gish) is a **multi-CLI agent memory framework** that gives AI command-line
tools a persistent, structured memory layer. It is designed to work alongside Claude Code,
Gemini CLI, Codex CLI, and GitHub Copilot CLI — or any combination thereof.

---

## Why Ghost In Shell?

Every AI CLI session starts fresh. Context that was relevant yesterday is gone today.
Ghost In Shell solves this by maintaining a workspace of structured memory files that
each CLI root instruction can reference at session start.

Key problems it addresses:

| Problem | Solution |
|---------|----------|
| No memory across sessions | Episodic store with persistent `.jsonl` log |
| Inconsistent identity across CLIs | Identity Trinity files loaded by all adapters |
| Uncontrolled file access | 3-tier sanctum governance |
| Stale or noisy memories | Decay + judge-gated consolidation engines |
| Lessons that are never found again | Knowledge notes behind a trigger-phrase index |
| Two machines overwriting each other | Single-writer role + locked write path |
| Single-CLI lock-in | Adapter architecture supports 4 CLIs simultaneously |

---

## What It Is

- A **workspace** of structured YAML/JSONL files that live next to your code or project.
- A **CLI tool** (`gish`) for initialising workspaces, recalling memories, running
  maintenance, auditing governance, and migrating legacy workspaces.
- A **Python library** (`gshell_memory`) exposing engines and adapters you can call
  programmatically.
- A **hook system** that integrates with each CLI's native session start/end mechanism.

## What It Is Not

- Not an LLM. gish does not make AI API calls.
- Not a chat interface. It is a memory and governance layer.
- Not cloud-dependent. All data stays in your local workspace directory.
- Not opinionated about which CLI you use. All four adapters are first-class.

---

## Key Concepts

### Workspace

A workspace is a directory containing:

```
my-workspace/
  IDENTITY.md          # Who the agent is
  SOUL.md              # Persona and style
  USER.md              # User preferences (optional)
  MEMORY.md            # Startup index: one trigger + link per line (ch.19)
  memory/
    knowledge/         # One note per fact: feedback/ projects/ references/ user/
    fact.yml           # Structured facts
    episodic.jsonl     # Episodic memory log
    associations.jsonl # Association graph edges
    brain_region_manifest.yml
    sanctum_registry.yml
    runtime_profiles.yml
    memory_manifest.yml
  .gish/
    config.yml
    logs/
```

### Identity Trinity

Three markdown files (`IDENTITY.md`, `SOUL.md`, `USER.md`) that every adapter loads at
session start to ensure consistent agent identity. See [Chapter 02](ch.02-identity-trinity.md).

### Memory Stores

Six stores with different retention characteristics. The primary ones are the fact store
(structured KV) and the episodic store (timestamped narrative entries). See
[Chapter 03](ch.03-memory-architecture.md).

### Engines

Background processes (`associate`, `decay`, `consolidate`, `judge`, `health`, `audit`,
`session_log`) that maintain memory quality over time. See [Chapter 04](ch.04-engine-internals.md).

### Adapters

Thin wrappers per CLI that emit the correct hook code and root instruction format.
See [Chapter 05](ch.05-multi-cli-adapters.md).

### Sanctum

A three-tier governance system that controls which files agents can read, write, or delete.
See [Chapter 06](ch.06-governance-sanctum.md).

### Brain Regions

Five named routing buckets for classifying memory access patterns (hippocampus, prefrontal,
limbic, cerebellum, default). See [Chapter 07](ch.07-brain-regions.md).

---

## Project Status

Ghost In Shell 5.2 is the current release line. Since 5.0 the file formats are
stable; 5.x releases add capabilities without breaking existing workspaces.

- 5.0 — stores, engines, CLI, adapters, migration, schema package
- 5.1 — capability engines (SOP, archive routing, carryover, frozen enums,
  heartbeat, region extensions, subdir registry) and the LabGrimoire bridge
- 5.2 — lessons from a year of daily use: the knowledge index and its budget
  ([ch.19](ch.19-knowledge-index.md)), write discipline — single writer,
  locked write path, judge-gated consolidation, archive instead of delete
  ([ch.20](ch.20-write-discipline.md)) — and field lessons
  ([ch.21](ch.21-field-lessons.md))

---

## Next Steps

→ [Chapter 01 — Quick Start](ch.01-quick-start.md)
