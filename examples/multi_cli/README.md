# Multi-CLI Example Workspace

A reference workspace with all four CLI roots pre-wired to a shared Ghost In Shell memory
store. Use this as a template when you work across Claude Code, Gemini CLI, Codex CLI,
and GitHub Copilot CLI in the same project.

## How It Works

All four CLIs load the same `IDENTITY.md`, `SOUL.md`, `USER.md`, and `MEMORY.md` at
session start. Their session-end hooks all call `gish log --from-session`, appending to
the same `memory/episodic.jsonl`.

The `memory/runtime_profiles.yml` file has entries for all four CLIs.

## File Guide

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Claude Code root instruction |
| `GEMINI.md` | Gemini CLI root instruction |
| `CODEX.md` | Codex CLI root instruction |
| `COPILOT.md` | GitHub Copilot CLI root instruction |
| `IDENTITY.md` | Shared agent identity |
| `SOUL.md` | Shared agent persona |
| `USER.md` | User preferences (shared) |
| `MEMORY.md` | Memory index (points to memory/) |
| `memory/` | Shared memory store |

## Quick Start

```bash
# 1. Initialise from this example (copies templates for missing files)
gish init examples/multi_cli

# 2. Edit identity files
$EDITOR examples/multi_cli/IDENTITY.md
$EDITOR examples/multi_cli/SOUL.md

# 3. Install hooks (run gish init to see per-CLI snippets)
gish init examples/multi_cli --non-interactive

# 4. Verify health
gish doctor --workspace examples/multi_cli

# 5. Test recall
gish recall --workspace examples/multi_cli "multi-cli"
```

## Session Logging Per CLI

```bash
# Claude Code (via ~/.claude/settings.json Stop hook)
gish log --from-session --workspace . --runtime claude-code

# Gemini CLI (via wrapper exit handler)
gish log --from-session --workspace . --runtime gemini-cli

# Codex CLI (via wrapper exit handler)
gish log --from-session --workspace . --runtime codex-cli

# Copilot CLI (via shell alias)
gish log --from-session --workspace . --runtime copilot-cli
```

## See Also

- [Chapter 05 — Multi-CLI Adapters](../../docs/ch.05-multi-cli-adapters.md)
- [Chapter 08 — Cron & Hooks](../../docs/ch.08-cron-hooks.md)
