# Memory Index

## Memory Layers (v4.1)

| Layer | File | When to Load |
|-------|------|--------------|
| L1 Hot | `memory/fact.yml` | Every session (auto via CLAUDE.md) |
| L1 Episodes | `memory/episodic.jsonl` | When needing past lessons |
| L0.5 Scratch | `memory/scratchpad.md` | During active tasks |
| L1 Cognitive | `memory/associations.jsonl` | Memory graph (background) |
| L1 Cognitive | `memory/principles_candidates.jsonl` | Auto-extracted rules |

## Quick Links
- Identity: see `memory/fact.yml` → `system` section
- User prefs: see `memory/fact.yml` → `user` section
- Rules: see `memory/fact.yml` → `rules` section

## Optional Upgrades
For governance + sanctum + LGD pairing, see the full
`examples/multi_cli_memory/` reference and `docs/17_LGD_Integration.md`.
