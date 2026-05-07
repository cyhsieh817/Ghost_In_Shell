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
| Stale or noisy memories | Decay + consolidation engines |
| Single-CLI lock-in | Adapter architecture supports 4 CLIs simultaneously |

---

## What It Is

- A **workspace** of structured YAML/JSONL files that live next to your code or project.
- A **CLI tool** (`gish`) for initialising workspaces, recalling memories, running
  maintenance, auditing governance, and migrating legacy workspaces.
- A **Python library** (`ghost_in_shell`) exposing engines and adapters you can call
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
  MEMORY.md            # Memory index loaded at session start
  memory/
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

Ghost In Shell v5 is in alpha (`5.0.0a4`). The API and file formats may change before
the stable 5.0.0 release. Milestone completion:

- M1 ✓ — Foundation: memory stores, engines, schemas
- M2 ✓ — CLI + doctor + recall + audit
- M3 ✓ — Adapters + init + run-maintenance + log + cron
- M4 ✓ — migrate + docs + examples

---

## Next Steps

→ [Chapter 01 — Quick Start](ch.01-quick-start.md)
