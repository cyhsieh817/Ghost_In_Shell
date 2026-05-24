<p align="center">
  <strong>Ghost In Shell</strong><br>
  <em>Give your AI agent a soul, not just a prompt.</em>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> &middot;
  <a href="#features">Features</a> &middot;
  <a href="#architecture">Architecture</a> &middot;
  <a href="#cli-reference">CLI</a> &middot;
  <a href="#documentation">Docs</a> &middot;
  <a href="#license">License</a>
</p>

<p align="center">
  <a href="https://github.com/cyhsieh817/Ghost_In_Shell/actions/workflows/ci.yml"><img src="https://github.com/cyhsieh817/Ghost_In_Shell/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="https://pypi.org/project/gshell-memory/"><img src="https://img.shields.io/pypi/v/gshell-memory.svg" alt="PyPI" /></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-brightgreen" alt="python" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="license" />
</p>

---

**Ghost In Shell** (`gish`) is a multi-CLI agent memory framework for AI command-line tools. It provides persistent episodic memory, association graphs, strength-based recall, sanctum governance, and brain-region routing — all running locally, no cloud required.

Works with **Claude Code** &middot; **Gemini CLI** &middot; **Codex CLI** &middot; **GitHub Copilot CLI**

---

## Quick Start

```bash
git clone https://github.com/cyhsieh817/Ghost_In_Shell
cd Ghost_In_Shell
./bootstrap.sh
```

Or install manually:

```bash
pip install -e .
gish init ~/my-workspace
gish doctor --workspace ~/my-workspace
gish recall "last architecture decision" --workspace ~/my-workspace
```

The bootstrap script detects your installed CLIs and prints hook snippets for each one.

> Full walkthrough: [ch.01 — Quick Start](docs/ch.01-quick-start.md)

---

## Features

### Memory Layer

| Store | Format | Purpose |
|:------|:-------|:--------|
| **Fact** | YAML | Structured identity, preferences, rules, tools |
| **Episodic** | JSONL | Timestamped decisions, failures, milestones, insights |
| **Associations** | JSONL + SQLite cache | Typed edges between episodes, facts, files, and skills |
| **Brain Regions** | YAML manifest | 5-zone routing (hippocampus / prefrontal / limbic / cerebellum / default) |
| **Sanctum** | YAML registry | 3-tier access control (public / private / sacred) |
| **Runtime Profiles** | YAML | Executor and launcher configs per CLI |

### 7 Maintenance Engines

| Engine | What it does |
|:-------|:-------------|
| `associate` | Builds and updates edges in the association graph |
| `decay` | Applies time-based strength decay; archives fading entries |
| `consolidate` | Merges redundant episodes; promotes recurring patterns |
| `judge` | Evaluates quality scores for new entries |
| `health` | Runs workspace integrity checks |
| `audit` | Validates sanctum governance compliance |
| `session_log` | Logs session start/end events |

### Strength Formula

```
strength = base(importance / 10)
         + retrieval(count * 0.08)
         + association(edges * 0.05)
         - decay(weeks * 0.03)
```

Memories strengthen through retrieval and association, weaken through disuse. The `consolidate` engine merges redundant entries; `decay` archives what fades below threshold.

### Identity Trinity

Three files loaded at every session start — consistent identity across all CLIs:

| File | Role |
|:-----|:-----|
| `IDENTITY.md` | Who the agent is |
| `SOUL.md` | Persona, tone, and behavioral constraints |
| `USER.md` | User preferences and context |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   CLI Adapters                       │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐               │
│  │Claude│ │Gemini│ │Codex │ │Copilt│  session hooks  │
│  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘               │
│     └────────┴────────┴────────┘                    │
│                    │                                 │
│              ┌─────▼──────┐                          │
│              │  gish CLI   │                          │
│              └─────┬──────┘                          │
│     ┌──────────────┼──────────────┐                  │
│     ▼              ▼              ▼                  │
│ ┌────────┐  ┌───────────┐  ┌──────────┐             │
│ │ Memory │  │  Engines  │  │Governance│             │
│ │ Layer  │  │  (7 maint)│  │ (Sanctum)│             │
│ └────────┘  └───────────┘  └──────────┘             │
│     │              │              │                  │
│     └──────────────┴──────────────┘                  │
│                    │                                 │
│          ┌─────────▼──────────┐                      │
│          │    Workspace       │                      │
│          │  (local YAML/JSONL)│                      │
│          └────────────────────┘                      │
└─────────────────────────────────────────────────────┘
```

### Workspace Structure

```
my-workspace/
├── IDENTITY.md
├── SOUL.md
├── USER.md                    # optional
├── MEMORY.md                  # index loaded at session start
├── memory/
│   ├── fact.yml               # structured facts
│   ├── episodic.jsonl         # episodic memory log
│   ├── associations.jsonl     # association graph edges
│   ├── brain_region_manifest.yml
│   ├── sanctum_registry.yml
│   ├── runtime_profiles.yml
│   └── memory_manifest.yml    # engine run state
└── .gish/
    ├── config.yml
    └── logs/
```

---

## CLI Reference

```
gish <command> [options]
```

| Command | Description |
|:--------|:------------|
| `gish init <path>` | Initialize a new workspace with templates and hook snippets |
| `gish recall <query>` | Search episodic memory by keyword |
| `gish doctor` | Run workspace health checks |
| `gish audit` | Validate sanctum governance compliance |
| `gish run-maintenance` | Execute all maintenance engines (decay, consolidate, etc.) |
| `gish log` | View session log entries |
| `gish migrate v4` | Migrate a legacy v4.1 workspace to v5 format |
| `gish version` | Print version |

All commands accept `--workspace <path>` to target a specific workspace.

---

## Documentation

| Chapter | Topic |
|:--------|:------|
| [00 — Overview](docs/ch.00-overview.md) | Why Ghost In Shell; what it is and isn't |
| [01 — Quick Start](docs/ch.01-quick-start.md) | From zero to `gish recall` in 5 minutes |
| [02 — Identity Trinity](docs/ch.02-identity-trinity.md) | IDENTITY + SOUL + USER |
| [03 — Memory Architecture](docs/ch.03-memory-architecture.md) | 6 stores + strength formula |
| [04 — Engine Internals](docs/ch.04-engine-internals.md) | All 7 maintenance engines |
| [05 — Multi-CLI Adapters](docs/ch.05-multi-cli-adapters.md) | Claude / Gemini / Codex / Copilot |
| [06 — Governance & Sanctum](docs/ch.06-governance-sanctum.md) | 3-tier access control |
| [07 — Brain Regions](docs/ch.07-brain-regions.md) | 5-zone memory routing |
| [08 — Cron & Hooks](docs/ch.08-cron-hooks.md) | Trigger guide for all CLIs |
| [09 — Customization](docs/ch.09-customization.md) | Extending adapters and engines |
| [10 — Migration](docs/ch.10-migration.md) | Upgrading from v4.1 workspaces |

---

## Examples

| Example | What it shows |
|:--------|:--------------|
| [`examples/minimal/`](examples/minimal/) | Bare-minimum workspace with seeded memory files |
| [`examples/multi_cli/`](examples/multi_cli/) | Full workspace with all Identity Trinity files and 4 CLI configs |

---

## Requirements

- Python 3.11+
- Dependencies: `click`, `pyyaml`, `pydantic`
- No cloud services, no API keys, no external databases

---

## Development

```bash
git clone https://github.com/cyhsieh817/Ghost_In_Shell
cd Ghost_In_Shell
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
```

---

## License

MIT — see [LICENSE](LICENSE).
