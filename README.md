# Ghost In Shell

> **Give your AI agent a soul, not just a prompt.**

Ghost In Shell v5 is a Python package (`ghost_in_shell`) with a `gish` CLI — a multi-CLI agent memory framework with episodic recall, association graphs, strength decay, sanctum governance, and brain-region routing.

Supports: **Claude Code · Gemini CLI · Codex CLI · GitHub Copilot CLI**

The v4.1 documentation framework is preserved on branch [`legacy/v4`](https://github.com/cyhsieh817/Ghost_In_Shell/tree/legacy/v4) (tag `v4.1.0-final`).

---

## Quick Start

```bash
git clone https://github.com/cyhsieh817/Ghost_In_Shell
cd Ghost_In_Shell
./bootstrap.sh

# Or manually:
pip install -e .
gish init ~/my-workspace
gish recall "anything"
```

See [docs/ch.01-quick-start.md](docs/ch.01-quick-start.md) for the full guide.

---

## Features

- **Episodic memory** — SHA-256 dedup, fingerprint cooldown, soft-dedup
- **Association graph** — jsonl log + SQLite cache + depth-1 neighbor query
- **Strength formula** — `base(importance/10) + retrieval(count×0.08) + assoc(edges×0.05) − decay(weeks×0.03)`
- **7 engines** — associate · decay · consolidate · judge · health · audit · session_log
- **4 CLI adapters** — Claude / Gemini / Codex / Copilot with hook snippets
- **Sanctum governance** — 3-tier (public / private / sacred) access control
- **Brain regions** — 5 fixed memory zones (hippocampus / prefrontal / limbic / cerebellum / default)
- **Migration** — `gish migrate v4` to upgrade from v4.1 workspaces

---

## Roadmap

| Milestone | Status |
|---|---|
| M1 — skeleton, CLI stubs, CI gate | ✓ COMPLETE 2026-05-06 |
| M2 — memory layer + 7 engines | ✓ COMPLETE 2026-05-07 |
| M3 — multi-CLI adapters + gish init + bootstrap | ✓ COMPLETE 2026-05-07 |
| M4 — docs, examples, migrate command | ✓ COMPLETE 2026-05-07 |
| M5 — 5.0.0rc1, merge to main | ✓ COMPLETE 2026-05-07 |

---

## Documentation

| Chapter | Topic |
|---|---|
| [00 Overview](docs/ch.00-overview.md) | Why Ghost In Shell; what it is and isn't |
| [01 Quick Start](docs/ch.01-quick-start.md) | Zero → `gish recall` in 5 min |
| [02 Identity Trinity](docs/ch.02-identity-trinity.md) | IDENTITY + SOUL + USER |
| [03 Memory Architecture](docs/ch.03-memory-architecture.md) | 6 stores + strength formula |
| [04 Engine Internals](docs/ch.04-engine-internals.md) | All 7 engines |
| [05 Multi-CLI Adapters](docs/ch.05-multi-cli-adapters.md) | Claude / Gemini / Codex / Copilot |
| [06 Governance & Sanctum](docs/ch.06-governance-sanctum.md) | 3-tier access control |
| [07 Brain Regions](docs/ch.07-brain-regions.md) | 5-zone memory routing |
| [08 Cron & Hooks](docs/ch.08-cron-hooks.md) | Trigger guide |
| [09 Customization](docs/ch.09-customization.md) | Extending adapters & engines |
| [10 Migration from v4](docs/ch.10-migration.md) | `gish migrate v4` |

---

## License

MIT — see [LICENSE](LICENSE).
