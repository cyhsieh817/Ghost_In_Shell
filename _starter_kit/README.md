# Ghost In Shell — Starter Kit 🐚

> **Interactive CLI: deploy a complete AI agent system in ~3 minutes.**
> Zero placeholder residue. Hot/cold memory. CLAUDE.md native. Multi-CLI ready.

---

## Usage

```bash
cd _starter_kit
python3 create_agent.py
```

No arguments needed — the wizard guides you through everything.

This starter kit generates the **core memory system** first. If you later want Claude / Gemini / Copilot / Codex / OpenClaw to share one memory graph, add the multi-CLI automation layer after the initial bootstrap.

---

## 4-Step Interactive Flow

```
╔══════════════════════════════════════════════════╗
║   🐚  Ghost In Shell — Agent Creator  v3.0      ║
╚══════════════════════════════════════════════════╝

1 / 4  🤖  Agent Identity
  → Name, emoji, type, personality, tagline

2 / 4  👤  User Profile
  → Your name, language, timezone, org, tech stack
  → Communication style, sensitive areas

3 / 4  📂  Paths
  → Workspace root, vault location
  💡 Drag folders into the terminal!

4 / 4  ⚙️  Optional Settings
  → System rules (defaults provided)
```

---

## What Gets Generated

The script creates a complete agent workspace:

```
your_workspace/
├── CLAUDE.md              ← Entry point with @import (auto-loads identity + memory)
├── IDENTITY.md            ← Agent business card
├── SOUL.md                ← Personality, values, boundaries
├── USER.md                ← User profile & preferences
├── MEMORY.md              ← Memory index (L0 router)
└── memory/
    ├── fact.yml            ← Hot facts (L1 — loaded every session)
    ├── fact_archive.yml    ← Cold storage (L1 — load on demand)
    ├── fact_decisions.yml  ← Decision history (L1 — load on demand)
    ├── episodic.jsonl      ← Lessons & milestones (append-only)
    └── scratchpad.md       ← Current task notes

your_vault/
└── _Agent_System/
    ├── 10_Projects/
    ├── 20_Areas/
    ├── 30_Resources/
    ├── 40_Archive/
    └── 99_System/
        ├── 990_POLICY/
        │   ├── ACCESS_POLICY.md     ← Permission zones (🔴/🟡/🟢)
        │   └── AUTONOMY_POLICY.md   ← What agent can do without asking
        ├── 991_Logs/
        ├── 992_Config/
        ├── 993_Worker_Inbox/
        ├── TRIAGE.md                ← Task classification matrix
        └── CAPABILITIES.md          ← Agent capability declaration
```

**Total: 14 files generated, zero placeholder residue.**

This is intentionally the **minimal portable core**. For a production multi-CLI deployment, the next upgrade is:

- companion root files: `GEMINI.md`, `AGENTS.md`, `COPILOT.md`, `CODEX.md`, `OPENCLAW.md`
- shared runtime registry: `memory/runtime_profiles.yml`
- wrapper / launcher scripts
- session-end auto-logging to `memory/episodic.jsonl`

---

## Recommended Upgrade: Multi-CLI Memory Layer

Once the generated workspace works with one CLI, add:

1. **One root file per CLI**
   - `CLAUDE.md` for primary orchestration
   - `GEMINI.md` for overflow / long-context work
   - `AGENTS.md` / `COPILOT.md` for read-only review
   - `CODEX.md` / `OPENCLAW.md` for alternate executors

2. **A deterministic launcher / hook layer**
   - wrapper script to inject runtime metadata
   - session-end logger to append `episodic.jsonl`
   - optional shell installer so users can type `claude` / `gemini` directly

3. **A single shared memory registry**
   - one `memory/episodic.jsonl`
   - one `memory/runtime_profiles.yml`
   - one canonical `MEMORY.md` router

See:

- `docs/03_Memory_Architecture.md`
- `docs/11_Claude_Code_Integration.md`
- `docs/14_Multi_CLI_Orchestration.md`
- `../examples/multi_cli_memory/`

---

## Templates (v3)

| Template | Purpose | Output Location |
|----------|---------|-----------------|
| `CLAUDE.md` | Entry point with @import | workspace root |
| `IDENTITY.md` | Agent identity card | workspace root |
| `SOUL.md` | Personality & rules | workspace root |
| `USER.md` | User profile | workspace root |
| `MEMORY.md` | Memory index (L0) | workspace root |
| `fact.yml` | Hot facts (L1) | memory/ |
| `fact_archive.yml` | Cold archive (L1) | memory/ |
| `fact_decisions.yml` | Decision history (L1) | memory/ |
| `episodic.jsonl` | Episode log | memory/ |
| `scratchpad.md` | Task scratch | memory/ |
| `ACCESS_POLICY.md` | Permission zones | vault/_Agent_System/99_System/990_POLICY/ |
| `AUTONOMY_POLICY.md` | Autonomy rules | vault/_Agent_System/99_System/990_POLICY/ |
| `TRIAGE.md` | Task classification | vault/_Agent_System/99_System/ |
| `CAPABILITIES.md` | Ability declaration | vault/_Agent_System/99_System/ |

---

## Zero Residue Guarantee

After generation, the script scans every output file for unresolved `{{PLACEHOLDER}}` tags:

```
✅  CLAUDE.md → workspace/
✅  SOUL.md → workspace/
✅  fact.yml → workspace/memory/
...
Perfect! All placeholders resolved. Zero residue.
```

### Placeholder Alias Mapping

| Template Key | Collected As |
|-------------|-------------|
| `{{DATE}}` | Auto (today's date) |
| `{{EMOJI}}` | = `AGENT_EMOJI` |
| `{{LANGUAGE}}` | = `PRIMARY_LANGUAGE` |
| `{{TIMEZONE}}` | = `USER_TIMEZONE` |
| `{{PREF_1}}` | = `COMMUNICATION_STYLE` |
| `{{TECH_1}}` | = `TECH_STACK` |
| `{{SENSITIVE_1}}` | = `SENSITIVE_AREAS` |

---

## Requirements

- Python 3.8+
- No external packages (stdlib only)

---

## What Changed in v3

| v2 | v3 |
|----|-----|
| 19 templates | 14 templates (focused) |
| No CLAUDE.md | CLAUDE.md with @import (native) |
| Single fact.yml | Hot/cold split (fact.yml + archive + decisions) |
| Chinese UI | English UI (open-source ready) |
| Config dir output | Smart routing (files go to correct locations) |
| structure/ copy | Programmatic directory creation |

**Recommended v4+ operational layer**: add shared wrappers + session-end logging when multiple CLIs will collaborate in one workspace.

---

*Ghost In Shell Starter Kit v3.0 🐚*
