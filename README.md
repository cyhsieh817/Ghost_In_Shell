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
│              Ghost In Shell                   │
├──────────────┬──────────────┬────────────────┤
│   Identity   │    Memory    │   Governance   │
│   ─────────  │   ────────   │   ──────────   │
│   IDENTITY   │  L0: Index   │   TRIAGE       │
│   SOUL       │  L1: Facts   │   Permissions  │
│   USER       │  L1: Episode │   Core Lock    │
│              │  L0.5:Scratch│   Naming Rules │
│              │  v4:Cognitive│                │
├──────────────┴──────────────┴────────────────┤
│              Workspace (PARA)                 │
│   _Agent_System/  (agent's domain)           │
│   _User_Workspace/ (human's domain)          │
├──────────────────────────────────────────────┤
│            Optional Extensions                │
│   Multi-Agent · Cross-Machine · Vector Memory │
│   Evolution Protocol · Claude Code Native     │
│   Agent Orchestration (Lane Routing)          │
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

### Option B: Manual Setup

1. Copy `examples/minimal/` to your project root
2. Edit `IDENTITY.md`, `SOUL.md`, `USER.md`
3. Configure `memory/fact.yml`
4. Point your AI tool's config to load these files

→ [Full Quick Start Guide](docs/01_Quick_Start.md)

---

## Documentation

### Foundation (Start Here)

| # | Document | What You'll Learn |
|---|----------|-------------------|
| 01 | [Quick Start](docs/01_Quick_Start.md) | 5-minute setup, first session |
| 02 | [Core Identity](docs/02_Core_Identity.md) | The Trinity — IDENTITY + SOUL + USER |
| 03 | [Memory Architecture](docs/03_Memory_Architecture.md) | Hot/cold layered memory + cognitive engine (v4) |
| 04 | [Workspace Structure](docs/04_Workspace_Structure.md) | PARA-based dual workspace |

### Operations

| # | Document | What You'll Learn |
|---|----------|-------------------|
| 05 | [Task Management](docs/05_Task_Management.md) | TRIAGE + iteration + task proposals |
| 06 | [Security Model](docs/06_Security_Model.md) | Permission zones + deletion protection |
| 07 | [Evolution Protocol](docs/07_Evolution_Protocol.md) | Self-improvement loops + heartbeat |
| 08 | [Naming Convention](docs/08_Naming_Convention.md) | File & folder naming rules |

### Advanced

| # | Document | What You'll Learn |
|---|----------|-------------------|
| 09 | [Multi-Agent Sync](docs/09_Multi_Agent_Sync.md) | Horcrux architecture, shared vault |
| 10 | [Cross-Machine Sync](docs/10_Cross_Machine_Sync.md) | Bootstrap script, symlinks, any device |
| 11 | [Claude Code Integration](docs/11_Claude_Code_Integration.md) | CLAUDE.md + @import native patterns |
| 12 | [Real World Example](docs/12_Real_World_Example.md) | Full deployment walkthrough |
| 13 | [Agent Orchestration](docs/13_Agent_Orchestration.md) | Lane routing, keyword detection, multi-agent dispatch |
| 14 | [Multi-CLI Orchestration](docs/14_Multi_CLI_Orchestration.md) | Trident pattern — multiple AI CLIs under one identity |
| 15 | [Domain Knowledge Pipeline](docs/15_Domain_Knowledge_Pipeline.md) | Local literature DB, enrichment, search CLI |
| 16 | [Skill Ecosystem](docs/16_Skill_Ecosystem.md) | Skill lifecycle, security audit, governance |

---

## Core Concepts

### 1. Identity Trinity

| File | Purpose | Analogy |
|------|---------|---------|
| `IDENTITY.md` | Name, type, capabilities | Business card |
| `SOUL.md` | Values, tone, boundaries, language | Personality & ethics |
| `USER.md` | Who it serves, preferences, sensitive areas | Client brief |

### 2. Layered Memory (v4 — Hot/Cold + Cognitive Engine)

```
Always loaded (low token cost):
  L0   MEMORY.md        ← Index & navigation (~100 lines)
  L1   fact.yml (hot)    ← Active preferences & tools (~130 lines)

Load on demand:
  L1   fact_archive.yml  ← Evaluated but inactive items
  L1   fact_decisions.yml ← Historical decisions
  L1   episodic.jsonl    ← Lessons learned, milestones
  L0.5 scratchpad.md     ← Current task working notes
  L2   consolidations.jsonl ← Cross-episode pattern recognition

v4 Cognitive layer (background):
  associations.jsonl          ← Memory graph (typed, weighted edges)
  principles_candidates.jsonl ← Auto-extracted rules (human-approved)
  .retrieval_buffer.jsonl     ← Hook-based access tracking
```

**Result**: 76% token reduction vs loading everything, plus memories that strengthen with use and fade when forgotten.

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
| [`minimal/`](examples/minimal/) | Bare essentials — identity + memory + rules | 6 files |
| [`team/`](examples/team/) | Multi-agent with shared vault & worker inboxes | Full setup |

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
| Claude Code | Native `CLAUDE.md` + `@import` |
| Cursor | `.cursorrules` or project rules |
| OpenClaw | `openclaw.json` multi-agent config |
| Any LLM | Markdown files as system context |

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
├── docs/                  ← 16 design documents
│   ├── 01_Quick_Start.md
│   ├── ...
│   └── 16_Skill_Ecosystem.md
├── starter_kit/           ← Interactive CLI + templates
│   ├── create_agent.py
│   ├── config/            ← 19 .template files
│   └── structure/         ← Directory skeleton
├── examples/
│   ├── minimal/           ← ⭐ Start here
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
