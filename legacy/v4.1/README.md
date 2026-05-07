# Ghost In Shell 🐚

> **Give your AI agent a soul, not just a prompt.**

Ghost In Shell is an open-source framework for building AI agents with persistent identity, layered memory, and autonomous task management. It turns stateless LLM sessions into evolving digital entities that remember, learn, and grow.

---

## The Problem

Every time you start a new AI session, your agent:
- 🔥 **Burns tokens** re-reading entire knowledge bases
- 🧠 **Forgets** everything from previous sessions
- 🎭 **Loses personality** — different tone every conversation
- 📂 **Scatters files** without consistent organization
- 🔓 **Has no boundaries** — does whatever you ask, even dangerous things

## The Solution

```
┌──────────────────────────────────────────────┐
│              Ghost In Shell  v4.1             │
├──────────────┬──────────────┬────────────────┤
│   Identity   │    Memory    │   Governance   │
│   ─────────  │   ────────   │   ──────────   │
│   IDENTITY   │  L0: Index   │   TRIAGE       │
│   SOUL       │  L1: Facts   │   Sanctum Reg. │
│   USER       │  L1: Episode │   Archive Tree │
│              │  L0.5:Scratch│   Frontmatter  │
│              │  v4:Cognitive│   Audit Hooks  │
│              │  v4.1: Brain │                │
│              │  Region Map  │                │
├──────────────┴──────────────┴────────────────┤
│           Three-Layer Enforcement             │
│   L1: deny list (settings.json) — 100%       │
│   L2: PreToolUse Hook (shell guard) — 100%   │
│   L3: rules/ + SOUL.md (guidance) — ~80%     │
├──────────────────────────────────────────────┤
│              Workspace (PARA)                 │
│   _Agent_System/  (agent's domain)           │
│   _User_Workspace/ (human's domain)          │
├──────────────────────────────────────────────┤
│            Optional Extensions                │
│   Multi-Agent · Cross-Machine · Vector Memory │
│   Evolution Protocol · Claude Code Native     │
│   Agent Contracts · Verify/Fix · Drift Audit  │
│   Agent Orchestration · Hook Self-Healing     │
│   Skill Dispatch · Knowledge Graph             │
│   ★ NEW v4.1: Sanctum Governance              │
│   ★ NEW v4.1: Brain Region Manifest           │
│   ★ NEW v4.1: LGD Pairing (LabGrimoire)       │
└──────────────────────────────────────────────┘
```

---

## Quick Start

### Option A: Interactive CLI (Recommended)

```bash
cd starter_kit
python3 create_agent.py
```

5-step wizard → complete agent config in ~3 minutes, zero placeholder residue.

If you plan to run **more than one AI CLI** in the same workspace, treat the starter kit as your **core memory layer** first, then add:

- one root instruction file per CLI (`CLAUDE.md`, `GEMINI.md`, `AGENTS.md`, etc.)
- a shared launcher / wrapper layer
- session-end auto-logging to `memory/episodic.jsonl`

### Option B: Manual Setup

1. Copy `examples/minimal/` to your project root
2. Edit `IDENTITY.md`, `SOUL.md`, `USER.md`
3. Configure `memory/fact.yml`
4. Point your primary AI tool to load these files
5. If multiple CLIs will share the same workspace, add companion root files (`GEMINI.md`, `AGENTS.md`, `COPILOT.md`, `CODEX.md`, `OPENCLAW.md`)
6. Add a wrapper or native stop-hook layer so session-end logging does not depend on human memory

→ [Full Quick Start Guide](docs/01_Quick_Start.md)

If you want a copy-ready bundle, start from [`examples/multi_cli_memory/`](examples/multi_cli_memory/).

---

## Portable Memory Automation (Recommended for Real Use)

The framework works with just Markdown files, but **teaching it to other people becomes much easier** when you also package the automation layer. The filenames below are a **reference naming scheme**, not a starter-kit requirement.

| File / Layer | Purpose |
|--------------|---------|
| `memory/runtime_profiles.yml` | Canonical map of runtime IDs, executors, and launchers |
| `scripts/llm_memory_wrapper.py` | Shared launcher that injects runtime metadata before starting a CLI |
| `scripts/memory_session_log.py` | Session-end logger that turns `git diff` into `episodic.jsonl` entries |
| `scripts/install_llm_shell_aliases.py` | Optional shell installer so `claude`, `gemini`, etc. automatically route through wrappers |
| `CLAUDE.md` / `GEMINI.md` / `AGENTS.md` / `COPILOT.md` / `CODEX.md` / `OPENCLAW.md` | Per-CLI root instructions with just-enough context |

**Key lesson**: the model should not have to "remember" to run memory scripts. The **wrapper / hook layer owns that responsibility**.

---

## Documentation

### Foundation (Start Here)

| # | Document | What You'll Learn |
|---|----------|-------------------|
| 01 | [Quick Start](docs/01_Quick_Start.md) | 5-minute setup, first session |
| 02 | [Core Identity](docs/02_Core_Identity.md) | The Trinity — IDENTITY + SOUL + USER |
| 03 | [Memory Architecture](docs/03_Memory_Architecture.md) | Hot/cold layered memory + cognitive engine (v4) + auto-logging |
| 04 | [Workspace Structure](docs/04_Workspace_Structure.md) | PARA-based dual workspace |

### Operations

| # | Document | What You'll Learn |
|---|----------|-------------------|
| 05 | [Task Management](docs/05_Task_Management.md) | TRIAGE + iteration + task proposals |
| 06 | [Security Model](docs/06_Security_Model.md) | Permission zones + deletion protection + hook self-healing |
| 07 | [Evolution Protocol](docs/07_Evolution_Protocol.md) | Self-improvement loops + heartbeat |
| 08 | [Naming Convention](docs/08_Naming_Convention.md) | File & folder naming rules |

### Advanced

| # | Document | What You'll Learn |
|---|----------|-------------------|
| 09 | [Multi-Agent Sync](docs/09_Multi_Agent_Sync.md) | Horcrux architecture, shared vault |
| 10 | [Cross-Machine Sync](docs/10_Cross_Machine_Sync.md) | Bootstrap, `.nosync` protection, primary/secondary roles |
| 11 | [Claude Code Integration](docs/11_Claude_Code_Integration.md) | CLAUDE.md + @import native patterns |
| 12 | [Real World Example](docs/12_Real_World_Example.md) | Full deployment walkthrough |
| 13 | [Agent Orchestration](docs/13_Agent_Orchestration.md) | Lane routing, agent contracts, verify/fix, drift audit |
| 14 | [Multi-CLI Orchestration](docs/14_Multi_CLI_Orchestration.md) | Trident pattern — multiple AI CLIs under one identity |
| 15 | [Domain Knowledge Pipeline](docs/15_Domain_Knowledge_Pipeline.md) | Local literature DB, enrichment, search CLI |
| 16 | [Skill Ecosystem](docs/16_Skill_Ecosystem.md) | Skill lifecycle, security audit, governance |
| 17 | [LGD Integration](docs/17_LGD_Integration.md) | Pair with LabGrimoire Desktop — local LLM, brain visualizer, write CLIs |
| 18 | [Sanctum Governance](docs/18_Sanctum_Governance.md) | Three-tier file protection registry + audit |
| 19 | [Brain Region Memory](docs/19_Brain_Region_Memory.md) | Neuro-anatomical file routing manifest |

---

## Core Concepts

### 1. Identity Trinity

| File | Purpose | Analogy |
|------|---------|---------|
| `IDENTITY.md` | Name, type, capabilities | Business card |
| `SOUL.md` | Values, tone, boundaries, language | Personality & ethics |
| `USER.md` | Who it serves, preferences, sensitive areas | Client brief |

### 2. Layered Memory (v4.1 — Hot/Cold + Cognitive Engine + Brain Regions + Auto-Logging)

```
Always loaded (low token cost):
  L0   MEMORY.md        ← Index & navigation (~80 lines)
  L1   fact.yml (hot)    ← Active preferences & tools (~150 lines)

Load on demand:
  L1   fact_archive.yml      ← Evaluated but inactive items
  L1   fact_decisions.yml    ← Historical decisions
  L1   fact_governance.yml   ← Archive routing + sanctum registry (NEW v4.1)
  L1   episodic.jsonl        ← Lessons learned, milestones
  L0.5 scratchpad.md         ← Current task working notes
  L2   consolidations.jsonl  ← Cross-episode pattern recognition

v4 Cognitive layer (background):
  associations.jsonl          ← Memory graph (typed, weighted edges)
  principles_candidates.jsonl ← Auto-extracted rules (human-approved)
  .retrieval_buffer.jsonl     ← Hook-based access tracking

v4.1 Brain region routing (NEW):
  brain_region_manifest.yml  ← Maps each file to a brain region
                               (hippocampus / prefrontal / limbic / etc.)
                               so the agent loads the right slice for the task

Auto-logging (wrapper exit or native stop hook):
  Session ends → memory_session_log.py → episodic.jsonl
  + SHA-256 fingerprint dedup, configurable cooldown window,
    auto-association suggestions on every entry
```

**Result**: 76% token reduction vs loading everything, plus memories that strengthen with use and fade when forgotten. **Auto-session logging** ensures no work goes unrecorded. **Brain region routing** narrows context to the cognitively relevant slice.

### 3. TRIAGE — Task Classification

| Level | Action | Example |
|:-----:|--------|---------|
| 🟢 AUTO | Execute immediately | File organization, logging |
| 🟡 CONFIRM | Execute, then notify | Creating files, knowledge updates |
| 🟠 PROPOSE | Propose plan, wait for approval | Unknown task types |
| 🔴 ASK | Ask before executing | Deletion, external communications |
| 🔒 LOCKED | Requires 2FA verification | Modifying core identity files |

### 4. Dual Workspace

```
Vault/
├── _Agent_System/      ← Agent's domain
│   ├── 10_Projects/    ← Active projects
│   ├── 20_Areas/       ← Ongoing responsibilities
│   ├── 30_Resources/   ← Knowledge base
│   ├── 40_Archive/     ← Completed work
│   └── 99_System/      ← Config, logs, policies
│
└── _User_Workspace/    ← Human's domain
    ├── 01_Inbox/       ← New items to process
    ├── 02_Tasks/       ← Active tasks
    └── 03_Outbox/      ← Agent deliverables for review
```

---

## Examples

| Example | Description | Files |
|---------|-------------|-------|
| [`minimal/`](examples/minimal/) | Bare essentials — identity + memory + rules | 8 files |
| [`multi_cli_memory/`](examples/multi_cli_memory/) | Wrappers + runtime registry + session logging + sanctum + brain regions + LGD bridge | Reference bundle (v4.1) |
| [`team/`](examples/team/) | Multi-agent with shared vault & worker inboxes | Full setup |

### Pairing with LabGrimoire Desktop (LGD)

If you install **LabGrimoire Desktop**, the framework upgrades automatically:

- `scripts/lgd_bridge.py` lets the agent call LGD's local LLM + tool registry headlessly
- `lgd_write_cli` rows in your sanctum registry become enforceable
- `brain_region_manifest.yml` powers LGD's brain visualizer

See [docs/17_LGD_Integration.md](docs/17_LGD_Integration.md) for the pairing
contract. Pairing is **always optional** — the framework works fully without LGD.

---

## Who Is This For?

- **Solo developers** wanting persistent AI memory across sessions
- **Teams** building multi-agent workflows with consistent behavior
- **Power users** of Claude Code, Cursor, or AI coding tools
- **Anyone** tired of re-explaining preferences every session

## Compatibility

Ghost In Shell is **LLM-agnostic**. The framework works with:

| Platform | Integration Method |
|----------|-------------------|
| Claude Code | `CLAUDE.md` + `@import` + optional native auto-memory |
| Gemini CLI | `GEMINI.md` + shared wrapper / launcher |
| GitHub Copilot CLI | `COPILOT.md` + global config (`~/.github/copilot/`) |
| Codex CLI | `CODEX.md` + shared wrapper / launcher |
| OpenClaw | `OPENCLAW.md` / `openclaw.json` + shared wrapper / launcher |
| Cursor / Windsurf / Continue | Project rules + the same workspace memory files |
| Any LLM | Markdown files as system context + optional wrapper / hook layer |

---

## Philosophy

1. **Index, don't inject** — Point to knowledge, don't paste it all
2. **Separate identity from instructions** — Who you are ≠ what you do
3. **Memory should have layers** — Not everything belongs in context
4. **Autonomy needs boundaries** — Freedom without guardrails is chaos
5. **Agents should evolve** — Static prompts create static tools
6. **Embed rules in context, not in files** — Rules in always-loaded files beat standalone policy documents
7. **Default to delegation** — An orchestrator that does everything itself wastes its specialists
8. **Multiple enforcement layers** — Single-layer rules don't change LLM behavior; hooks + config + agent boundaries together do

---

## Project Structure

```
Ghost_In_Shell/
├── README.md              ← You are here
├── docs/                  ← 19 design documents (3 added in v4.1)
│   ├── 01_Quick_Start.md
│   ├── ...
│   ├── 16_Skill_Ecosystem.md
│   ├── 17_LGD_Integration.md       ← NEW v4.1
│   ├── 18_Sanctum_Governance.md    ← NEW v4.1
│   └── 19_Brain_Region_Memory.md   ← NEW v4.1
├── _starter_kit/          ← Interactive CLI + templates (v4.1)
│   ├── create_agent.py
│   └── config/            ← .template files (incl. fact_governance,
│                            brain_region_manifest, LGD_INTEGRATION)
├── examples/
│   ├── minimal/           ← ⭐ Start here
│   ├── multi_cli_memory/  ← Reference bundle w/ sanctum + brain region + LGD
│   └── team/              ← Multi-agent setup
└── LICENSE
```

---

## Contributing

PRs welcome. Please read the docs first to understand the architecture.

## License

MIT

---

*Built by humans and their agents, for humans and their agents.* 🐚
