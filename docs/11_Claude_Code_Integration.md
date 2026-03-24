# 11 — Claude Code Integration

> Native integration with Claude Code using CLAUDE.md and @import.

---

## How Claude Code Loads Context

Claude Code automatically loads `CLAUDE.md` files at session start:

1. `~/.claude/CLAUDE.md` — Global (all projects)
2. `.claude/CLAUDE.md` — Project-level (in repo root)
3. `CLAUDE.md` — Project-level (in repo root)

Files loaded later override earlier ones. All three can coexist.

---

## The @import Pattern

Claude Code supports `@import` to inject file contents:

```markdown
# CLAUDE.md

## Identity
@./SOUL.md

## Memory
@./MEMORY.md

## Active Facts
@./memory/fact.yml
```

This auto-injects the contents of those files every session — no manual pasting.

### Rules for @import

| Rule | Detail |
|------|--------|
| Syntax | `@path/to/file` at the start of a line |
| Paths | Relative to the CLAUDE.md file, or absolute |
| Nesting | Imported files can also use @import |
| File types | Any text file (`.md`, `.yml`, `.txt`, etc.) |

---

## Recommended Setup

### Global CLAUDE.md (`~/.claude/CLAUDE.md`)

For settings that apply to **every project**:

```markdown
# Global Agent Configuration

## Core Identity
@/path/to/workspace/SOUL.md

## Memory System
@/path/to/workspace/MEMORY.md

## Active Facts
@/path/to/workspace/memory/fact.yml
```

### Project CLAUDE.md (`./CLAUDE.md`)

For **project-specific** instructions:

```markdown
# Project: [Name]

## Project Context
- This is a [type] project using [tech stack]
- Key directories: src/, tests/, docs/

## Project Rules
- Follow [style guide]
- Run tests before committing
- Use [naming convention]

## Project Memory (optional)
@./project_memory.yml
```

---

## Ghost In Shell + Claude Code

### Minimal Integration (5 files)

```
project/
├── CLAUDE.md          ← @imports SOUL + MEMORY + fact.yml
├── SOUL.md            ← Agent personality
├── MEMORY.md          ← Memory index
└── memory/
    ├── fact.yml       ← Hot facts
    └── episodic.jsonl ← Lesson log
```

### Full Integration

```
project/
├── CLAUDE.md           ← @imports + project rules (<200 lines!)
├── .claude/
│   ├── rules/          ← Path-scoped conditional rules
│   │   ├── safety.md   ← Always loaded (no paths restriction)
│   │   ├── project.md  ← Loaded only when touching project/** files
│   │   └── domain.md   ← Loaded only when touching domain/** files
│   ├── skills/         ← Agent-callable workflow skills
│   └── agents/         ← Specialized sub-agents with own context
├── IDENTITY.md
├── SOUL.md
├── USER.md
├── MEMORY.md
├── PROJECTS.md
├── memory/
│   ├── fact.yml
│   ├── fact_archive.yml
│   ├── fact_decisions.yml
│   ├── episodic.jsonl
│   ├── scratchpad.md
│   └── consolidations.jsonl
└── [project files...]
```

---

## Token Budget

What gets loaded every session:

| File | Typical Size | Purpose |
|------|-------------|---------|
| CLAUDE.md | ~80 lines | Config + @import directives |
| SOUL.md | ~85 lines | Personality & rules |
| MEMORY.md | ~100 lines | Navigation index |
| fact.yml | ~130 lines | Active preferences & tools |
| **Total** | **~400 lines** | Complete agent context |

Compare to loading everything (~2000+ lines) — this is an **80% reduction**.

---

## Path-Scoped Rules (`.claude/rules/`)

Rules files in `.claude/rules/` provide **conditional context injection** — they only load when the agent operates on matching files, saving tokens on unrelated tasks.

### How It Works

```
project/
├── .claude/
│   └── rules/
│       ├── safety.md       ← Always loaded (no paths restriction)
│       ├── ycbio.md         ← Loaded only when touching ycbio/** files
│       └── literature.md    ← Loaded only when touching lit_* files
```

### Rule File Format

```markdown
---
paths:
  - "scripts/lit_*"
  - "memory/knowledge.jsonl"
  - "**/Knowledge_Digest/**"
description: Literature pipeline rules — only loaded when touching literature files
---

# Literature Pipeline Rules

- knowledge.jsonl ID format: k{NNN}, three-digit sequential
- Frontmatter tags must be JSON array format (not YAML list)
- Use atomic write: tempfile + rename to prevent corruption on interrupt
```

### Key Properties

| Property | Detail |
|----------|--------|
| `paths` | Glob patterns — rule loads only when the tool target matches |
| No `paths` | Rule loads for **all** operations (use for global safety rules) |
| Scope | Project-level (`.claude/rules/`) or global (`~/.claude/rules/`) |
| Priority | User-level rules < project-level rules |
| Token savings | 20-30 lines per skipped rule file on unrelated tasks |

### When to Use Rules vs CLAUDE.md

| Content | Put In | Why |
|---------|--------|-----|
| Global safety rules | `rules/safety.md` (no paths) | Always available, separated from project config |
| Project-specific conventions | `rules/project.md` | Keeps CLAUDE.md lean |
| Domain-specific workflows | `rules/domain.md` (with paths) | Only loaded when relevant |
| Identity, memory, navigation | `CLAUDE.md` + @import | Core context, always needed |

**Key lesson**: CLAUDE.md should stay under **200 lines**. Beyond that, compliance drops. Split domain-specific rules into `rules/` and use path-scoping to load them only when needed.

---

## Tips

### Keep @imported Files Small
Each imported file should be <200 lines. If it grows beyond that, split it.

### Use MEMORY.md as a Router
Don't import everything — import the index, and let the agent load details on demand.

### Project vs Global
- **Global** (`~/.claude/CLAUDE.md`): Identity, memory, preferences
- **Project** (`./CLAUDE.md`): Tech stack, conventions, project-specific rules
- **Path-scoped** (`.claude/rules/*.md`): Domain rules that only apply to matching files

### Multiple Projects, Same Agent
If you work across multiple repos, your global CLAUDE.md imports identity/memory once, and each project's CLAUDE.md adds project-specific context. Path-scoped rules keep domain logic isolated.

---

## Claude Code Auto Memory

Claude Code has a built-in persistent memory feature that writes to a project-specific directory:

```
~/.claude/projects/<encoded-project-path>/memory/MEMORY.md
```

Where `<encoded-project-path>` is the project directory path with `/` replaced by `-`.

### Key Facts

| Property | Detail |
|----------|--------|
| Location | `~/.claude/projects/-Users-alice-projects-myagent/memory/MEMORY.md` |
| Created | **Manually** — does NOT auto-create |
| Purpose | Cross-session guidance summaries |
| Max size | ≤ 80 lines |
| Independence | **Completely separate from @import layer** — missing this dir does NOT break primary memory |

### What Goes Here vs Workspace Memory

| Auto Memory (`~/.claude/projects/.../memory/`) | Workspace Memory (`$WORKSPACE/memory/`) |
|---|---|
| Guidance summaries | Formal knowledge |
| Tool selection rules | fact.yml facts |
| Trigger reminders | episodic.jsonl events |
| Output path pointers | scratchpad.md tasks |
| ≤ 80 lines | No size limit |

**Important**: Claude Code auto memory is a **guidance layer**, not your primary event log. Session logging still belongs in the workspace layer (`memory/episodic.jsonl`), ideally through a wrapper or native Stop hook.

### Initial Setup (Per Machine)

```bash
# Create the directory (one-time, per machine)
mkdir -p ~/.claude/projects/$(pwd | tr '/' '-' | sed 's/^-//')/memory/

# Write a guidance summary
cat > ~/.claude/projects/.../memory/MEMORY.md << 'EOF'
# Auto Memory — Guidance Layer
# ⛔ Summaries only. Full memory lives in $WORKSPACE/memory/

## Default Output Paths
- Formal facts: $WORKSPACE/memory/fact.yml
- Episodes: $WORKSPACE/memory/episodic.jsonl
- Tasks: $WORKSPACE/memory/scratchpad.md

## Tool Selection Rules
- [Your rules here]

## Trigger Reminders
- [Your reminders here]
EOF
```

### Diagnostic Check

```bash
# Verify both layers exist
PROJ_PATH=$(pwd | sed 's|/|-|g' | sed 's/^-//')
ls ~/.claude/projects/$PROJ_PATH/memory/MEMORY.md 2>/dev/null \
  && echo "✅ Auto memory: present" \
  || echo "⚠️  Auto memory: missing (non-critical)"

ls $WORKSPACE/memory/fact.yml 2>/dev/null \
  && echo "✅ Primary memory: present" \
  || echo "❌ Primary memory: MISSING (critical)"
```

---

## Non-Claude Code Platforms

The same identity and memory files also work with other tools:

| Platform | How to Load |
|----------|-------------|
| **Gemini CLI** | Add `GEMINI.md`, then launch via shared wrapper / hook |
| **GitHub Copilot CLI** | Use `AGENTS.md` or `COPILOT.md`, plus shared wrapper / hook |
| **Codex CLI** | Add `CODEX.md`, plus shared wrapper / hook |
| **OpenClaw** | Add `OPENCLAW.md` or `openclaw.json`, plus shared wrapper / hook |
| **Cursor** | Add to `.cursorrules` or project settings |
| **Continue.dev** | Reference in `.continuerc.json` context |
| **Windsurf** | Add to `.windsurfrules` |
| **Any LLM** | Paste SOUL.md + MEMORY.md + fact.yml into system prompt |

The framework is the same — only the loading mechanism changes. In a multi-CLI stack:

- `CLAUDE.md` usually remains the **primary orchestrator** file
- companion files (`GEMINI.md`, `AGENTS.md`, `COPILOT.md`, `CODEX.md`, `OPENCLAW.md`) provide **just-enough context**
- the wrapper / hook layer owns `memory_session_log.py`, not the model

---

*Claude Code reads the files. Ghost In Shell gives them meaning.* 🐚
