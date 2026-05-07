# Minimal Example Workspace

This is the smallest valid Ghost In Shell v5 workspace. Use it to verify your
installation and understand the required file structure.

## Quick Start

```bash
# From the repo root
gish init examples/minimal
gish recall --workspace examples/minimal "sample episode"
```

## Contents

```
examples/minimal/
  memory/
    fact.yml                     # Structured facts (identity, preferences)
    episodic.jsonl               # Episodic memory log (1 sample entry)
    brain_region_manifest.yml    # 5-region routing table
    sanctum_registry.yml         # Governance tiers
    runtime_profiles.yml         # CLI executor configuration
    memory_manifest.yml          # Maintenance ledger
```

## What to Do Next

1. Run `gish doctor --workspace examples/minimal` to verify workspace health.
2. Run `gish recall --workspace examples/minimal "example"` to test recall.
3. Run `gish log --workspace examples/minimal --title "My first note" --content "Testing gish." --importance 5` to add a memory.
4. Customise `memory/fact.yml` with your actual identity and preferences.
5. Copy this directory as a starting point for your real workspace.

## See Also

- [Chapter 01 — Quick Start](../../docs/ch.01-quick-start.md)
- [Chapter 03 — Memory Architecture](../../docs/ch.03-memory-architecture.md)
