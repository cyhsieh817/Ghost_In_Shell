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
