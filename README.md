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

> **New in 5.2** — the knowledge index and its budget, single-writer guard, and judge-gated consolidation, distilled from a year of daily use. See [ch.19](docs/ch.19-knowledge-index.md), [ch.20](docs/ch.20-write-discipline.md), [ch.21](docs/ch.21-field-lessons.md).
>
> Optional desktop pairing: LabGrimoire Desktop reads the same workspace — see [Chapter 18](docs/ch.18-lgd-bridge.md).

---

**Ghost In Shell** (`gish`) is a multi-CLI agent memory framework for AI command-line tools. It provides persistent episodic memory, a trigger-phrase knowledge index, association graphs, strength-based recall, sanctum governance, and brain-region routing — all running locally, no cloud required.

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
gish init ./my-workspace
gish doctor --workspace ./my-workspace
gish recall "last architecture decision" --workspace ./my-workspace
```

The bootstrap script detects your installed CLIs and prints hook snippets for each one.

> Full walkthrough: [ch.01 — Quick Start](docs/ch.01-quick-start.md)

---

## Features

### Memory Layer

| Store | Format | Purpose |
|:------|:-------|:--------|
| **Knowledge** | Markdown + YAML frontmatter | One note per rule or fact, found through the startup index (`MEMORY.md`) |
| **Fact** | YAML | Structured identity, preferences, rules, tools |
| **Episodic** | JSONL | Timestamped decisions, failures, milestones, insights |
| **Associations** | JSONL + SQLite cache | Typed edges between episodes, facts, files, and skills |
| **Brain Regions** | YAML manifest | 5-zone routing (hippocampus / prefrontal / limbic / cerebellum / default) |
| **Sanctum** | YAML registry | 3-tier access control (public / private / sacred) |
| **Runtime Profiles** | YAML | Executor and launcher configs per CLI |

### 15 Engines (7 maintenance + 8 capability)

| Engine | Category | What it does |
|:-------|:---------|:-------------|
| `associate` | maintenance | Builds and updates edges in the association graph |
| `decay` | maintenance | Applies time-based strength decay; marks fading / archived entries |
| `consolidate` | maintenance | Proposes merges of low-importance episodes; applies only after the judge passes; archives sources |
| `judge` | maintenance | Grades consolidation proposals (A–F, fail-closed external judge); advisory episode verdicts |
| `health` | maintenance | Runs workspace integrity checks |
| `audit` | maintenance | Validates sanctum governance compliance |
| `session_log` | maintenance | Logs session start/end events |
| `sop` | capability | Natural-language triggers map to required reading (`gish sop`) |
| `archive_router` | capability | Condition->target decision tree (`gish archive route`) |
| `carryover` | capability | Cross-session task hand-off (`gish carryover`) |
| `enum_freeze` | capability | Lock state-machine values against drift (`gish enum`) |
| `heartbeat` | capability | Periodic self-check + cron/launchd snippets (`gish heartbeat`) |
| `brain_region_ext` | capability | Declare regions beyond the 5 defaults (`gish region`) |
| `subdir_registry` | capability | White-list governance for memory/ subdirs (`gish memory-dir`) |
| `knowledge` | capability | Startup-index budget, note frontmatter contract, broken-link and orphan lint (`gish index`, `gish knowledge`) |

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
├── MEMORY.md                  # startup index: one trigger + link per line
├── memory/
│   ├── knowledge/             # feedback/ projects/ references/ user/ notes
│   ├── _archive/              # consolidated sources (never deleted)
│   ├── fact.yml               # structured facts
│   ├── episodic.jsonl         # episodic memory log
│   ├── associations.jsonl     # association graph edges
│   ├── brain_region_manifest.yml
│   ├── sanctum_registry.yml
│   ├── runtime_profiles.yml
│   └── memory_manifest.yml    # engine run state
└── .gish/
    ├── config.yml             # workspace-relative paths only
    ├── proposals/             # consolidation proposals + verdicts
    └── logs/
```

The machine role (`primary` / `secondary`) is device-local and is never stored in
the workspace — see [ch.20](docs/ch.20-write-discipline.md).

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
| `gish dream` | Nightly sleep cycle: replay → rem → verdict → prune → gate (deep sleep on Sundays) |
| `gish log` | View session log entries |
| `gish migrate v4` | Migrate a legacy v4.1 workspace to v5 format |
| `gish version` | Print version |
| `gish sop register/list/trigger/test` | Manage SOP dispatch routes |
| `gish archive route add/list/preview` | Manage archive routing decision tree |
| `gish carryover create/list/expire/promote-to-episodic` | Cross-session task hand-off |
| `gish enum freeze/list/validate` | Manage frozen state enums |
| `gish heartbeat run/install` | Heartbeat + cron/launchd snippets |
| `gish region declare/list` | Declare extension brain regions |
| `gish memory-dir register/list/enforce` | Subdir white-list |
| `gish index budget` | Measure `MEMORY.md` in characters (exit 0 ok · 1 over budget · 2 truncating) |
| `gish knowledge new/lint` | Create notes with the frontmatter contract; lint notes, links, orphans |

All commands accept `--workspace <path>` to target a specific workspace.

---

## Documentation

| Chapter | Topic |
|:--------|:------|
| [00 — Overview](docs/ch.00-overview.md) | Why Ghost In Shell; what it is and isn't |
| [01 — Quick Start](docs/ch.01-quick-start.md) | From zero to `gish recall` in 5 minutes |
| [02 — Identity Trinity](docs/ch.02-identity-trinity.md) | IDENTITY + SOUL + USER |
| [03 — Memory Architecture](docs/ch.03-memory-architecture.md) | 6 stores + strength formula |
| [04 — Engine Internals](docs/ch.04-engine-internals.md) | Maintenance engines, incl. the propose → judge → apply pipeline |
| [05 — Multi-CLI Adapters](docs/ch.05-multi-cli-adapters.md) | Claude / Gemini / Codex / Copilot |
| [06 — Governance & Sanctum](docs/ch.06-governance-sanctum.md) | 3-tier access control |
| [07 — Brain Regions](docs/ch.07-brain-regions.md) | 5-zone memory routing |
| [08 — Cron & Hooks](docs/ch.08-cron-hooks.md) | Trigger guide for all CLIs |
| [09 — Customization](docs/ch.09-customization.md) | Extending adapters and engines |
| [10 — Migration](docs/ch.10-migration.md) | Upgrading from v4.1 workspaces |
| [11–17 — Capabilities](docs/ch.11-sop-dispatch.md) | SOP dispatch, archive routing, carryover, frozen enums, heartbeat, region extensions, subdir registry |
| [18 — LabGrimoire Bridge](docs/ch.18-lgd-bridge.md) | Optional desktop GUI contract |
| [19 — Knowledge Index](docs/ch.19-knowledge-index.md) | Trigger phrases, Tier 1 vs shelves, note contract, index budget |
| [20 — Write Discipline](docs/ch.20-write-discipline.md) | Single writer, locked write path, judge-gated consolidation, archive-not-delete, promotion |
| [21 — Field Lessons](docs/ch.21-field-lessons.md) | Ten lessons from a year of daily multi-agent use |

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
