# Memory Index

## Memory Layers

| Layer | File | When to Load |
|-------|------|--------------|
| L1 Hot | `memory/fact.yml` | Every session (auto via CLAUDE.md) |
| L1 Episodes | `memory/episodic.jsonl` | When needing past lessons |
| L0.5 Scratch | `memory/scratchpad.md` | During active tasks |

## Quick Links
- Identity: see `memory/fact.yml` → `system` section
- User prefs: see `memory/fact.yml` → `user` section
- Rules: see `memory/fact.yml` → `rules` section
