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
├── CLAUDE.md           ← @imports + project rules
├── .claude/
│   └── CLAUDE.md       ← Global rules (if needed separately)
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

## Tips

### Keep @imported Files Small
Each imported file should be <200 lines. If it grows beyond that, split it.

### Use MEMORY.md as a Router
Don't import everything — import the index, and let the agent load details on demand.

### Project vs Global
- **Global** (`~/.claude/CLAUDE.md`): Identity, memory, preferences
- **Project** (`./CLAUDE.md`): Tech stack, conventions, project-specific rules

### Multiple Projects, Same Agent
If you work across multiple repos, your global CLAUDE.md imports identity/memory once, and each project's CLAUDE.md adds project-specific context.

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

The same files work with other tools:

| Platform | How to Load |
|----------|-------------|
| **Cursor** | Add to `.cursorrules` or project settings |
| **Continue.dev** | Reference in `.continuerc.json` context |
| **Windsurf** | Add to `.windsurfrules` |
| **Any LLM** | Paste SOUL.md + fact.yml into system prompt |

The framework is the same — only the loading mechanism changes.

---

*Claude Code reads the files. Ghost In Shell gives them meaning.* 🐚
