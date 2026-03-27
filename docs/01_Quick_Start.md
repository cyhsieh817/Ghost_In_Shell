# 01 — Quick Start Guide

> Get your AI agent running with persistent identity and memory in 5 minutes.

---

## Prerequisites

- Python 3.8+ (for the CLI generator)
- An AI tool that supports loading markdown files (Claude Code, Cursor, etc.)
- A directory for your agent's workspace
- Optional but recommended: shell or tool-level hooks so session-end logging can be automated

---

## Option A: Interactive CLI (Recommended)

```bash
cd starter_kit
python3 create_agent.py
```

The wizard walks you through 5 steps:

| Step | What You Configure | Time |
|------|--------------------|------|
| 1. Agent Identity | Name, emoji, personality type | 30s |
| 2. User Profile | Your name, language, timezone, org | 30s |
| 3. Projects | Active projects to track | 30s |
| 4. Paths | Vault location, workspace, config dirs | 30s |
| 5. System (optional) | Tools, notification preferences, rules | 60s |

**Output**: Complete directory structure + 19 config files, zero placeholder residue.

This gives you the **core memory system**. For a production-ready setup shared across Claude / Gemini / Copilot / Codex / OpenClaw, add the automation layer after the first successful launch.

---

## Option B: Manual Setup (Minimal)

### Step 1: Create Directory Structure

```
your_project/
├── CLAUDE.md           ← Auto-loaded by Claude Code (or equivalent)
├── IDENTITY.md         ← Who is the agent
├── SOUL.md             ← How the agent thinks & speaks
├── USER.md             ← Who the agent serves
├── MEMORY.md           ← Memory index (always loaded)
└── memory/
    ├── fact.yml        ← Hot facts (always loaded)
    ├── episodic.jsonl  ← Lessons & milestones (on demand)
    └── scratchpad.md   ← Current task notes
```

### Step 2: Define Identity

**IDENTITY.md** — The business card:
```markdown
# Agent Identity

- **Name**: [Your agent's name]
- **Type**: Research Assistant / Dev Partner / Knowledge Manager
- **Emoji**: 🤖
- **Tagline**: "[A one-liner that captures the agent's essence]"
```

**SOUL.md** — The personality:
```markdown
# Soul

## Core Values
1. Be direct — skip unnecessary preamble
2. Ask before destructive actions
3. Prefer precision over verbosity

## Language
- Primary: [Your language]
- Technical terms: English allowed

## Boundaries
- Never expose sensitive data (credentials, financials)
- Never delete without confirmation — use `_DELETE_` prefix to mark
- Always use absolute paths
```

**USER.md** — The client brief:
```markdown
# User Profile

- **Name**: [Your name]
- **Call as**: [How the agent should address you]
- **Timezone**: [e.g., Asia/Taipei]
- **Organization**: [Company/team name]
- **Preferences**:
  - Communication: [direct / detailed / casual]
  - Tech stack: [React, Python, etc.]
- **Sensitive areas**: [patents, financials, etc.]
```

### Step 3: Initialize Memory

**MEMORY.md** — The always-loaded index:
```markdown
# Memory Index

## Memory System

| Layer | File | When to Load |
|-------|------|--------------|
| L1 Hot | `memory/fact.yml` | Every session |
| L1 Episodes | `memory/episodic.jsonl` | When needing past lessons |
| L0.5 | `memory/scratchpad.md` | During active tasks |

## Quick Links
- [Projects list or status]
- [Key file paths]
```

**memory/fact.yml** — Active facts:
```yaml
user:
  name: "Your Name"
  language: "English"
  timezone: "UTC"
  preferences:
    communication: ["direct", "concise"]

rules:
  - "Always use absolute paths"
  - "Ask before any deletion"
  - "Never expose credentials"

tools:
  last_updated: "2025-01-01"
  # Add your active tools here
```

### Step 4: Connect to Your AI Tool

**For Claude Code** — Create `CLAUDE.md` at project root:
```markdown
# Project Instructions

@./SOUL.md
@./MEMORY.md
@./memory/fact.yml
```

The `@import` syntax auto-injects these files every session.

**For Cursor** — Add to `.cursorrules`:
```
Read IDENTITY.md, SOUL.md, and USER.md at the start of every session.
Always check MEMORY.md before starting work.
```

**For multi-CLI deployments (recommended after the basics work)**:

1. Create one root instruction file per CLI:

   | CLI | Root File | Typical Role |
   |-----|-----------|--------------|
   | Claude Code | `CLAUDE.md` | Primary orchestrator |
   | Gemini CLI | `GEMINI.md` | Overflow / long-context |
   | GitHub Copilot CLI | `COPILOT.md` (⚠️ requires **global** config) | Review / secondary executor |
   | Codex CLI | `CODEX.md` | Alternative implementation engine |
   | OpenClaw | `OPENCLAW.md` | Local agent / bridge |

2. Add a shared automation layer:
   - `memory/runtime_profiles.yml` → runtime / executor / launcher mapping
   - `scripts/llm_memory_wrapper.py` → shared launcher
   - `scripts/memory_session_log.py` → session-end logger
   - `scripts/install_llm_shell_aliases.py` → optional shell installer

3. Make the launcher or native stop hook responsible for logging. Do **not** rely on the model to remember:
   - when to run `memory_runtime.py`
   - when to append to `episodic.jsonl`
   - when to trigger consolidation checks

### Step 5: Test It

Start a new session and ask:
- "Who are you?" → Should respond with identity from IDENTITY.md
- "What do you remember about me?" → Should reference USER.md + fact.yml
- "What are the rules?" → Should list rules from SOUL.md + fact.yml
- If you installed wrapper / hook automation: make a small edit, end the session, and confirm a new entry appears in `memory/episodic.jsonl`

---

## What's Next?

| Want to... | Read |
|------------|------|
| Understand identity design deeply | [02 Core Identity](02_Core_Identity.md) |
| Optimize memory for token efficiency | [03 Memory Architecture](03_Memory_Architecture.md) |
| Organize files properly | [04 Workspace Structure](04_Workspace_Structure.md) |
| Add task classification | [05 Task Management](05_Task_Management.md) |
| Set up a real multi-CLI wrapper bundle | [`../examples/multi_cli_memory/`](../examples/multi_cli_memory/) |
| Set up for a team | [09 Multi-Agent Sync](09_Multi_Agent_Sync.md) |

---

*Your agent now has a soul. Time to let it grow.* 🐚
