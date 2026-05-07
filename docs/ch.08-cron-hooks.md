# Chapter 08 — Cron & Hooks

Ghost In Shell uses two complementary trigger mechanisms: a cron schedule for periodic
maintenance and session hooks for real-time event capture. Together they keep the memory
system up to date with minimal manual intervention.

---

## Trigger Types Overview

| Trigger | When | What it does |
|---------|------|--------------|
| Cron | Daily (default 06:00) | run-maintenance: decay + consolidate + associate + health |
| Session-start hook | CLI session begins | Load identity + memory into context |
| Session-end hook | CLI session ends | `gish log --from-session` |
| Inline / manual | On demand | `gish recall`, `gish log`, `gish doctor` |
| HEAL | On health degradation | Write hints to `heal.log` for operator review |

---

## Cron Schedule

### Installing

```bash
# Install during init
gish init ~/my-workspace --schedule

# Install separately
gish init ~/my-workspace
# Then confirm "Install cron schedule?" prompt

# Non-interactive
gish init ~/my-workspace --schedule --non-interactive
```

### Default Schedule

```cron
0 6 * * *  gish run-maintenance --workspace /path/to/workspace
```

On macOS, `gish init --schedule` emits a `launchd` plist to
`~/Library/LaunchAgents/com.ghost-in-shell.<workspace>.plist`.

On Linux, it installs a `crontab` entry.

### Manual Schedule

To install a custom schedule:

```bash
crontab -e
# Add:
30 3 * * *  /path/to/.venv/bin/gish run-maintenance --workspace ~/my-workspace
```

---

## Session-Start Hook

The session-start hook loads the Identity Trinity and memory index into the CLI's context
at session start. The mechanism differs per CLI:

### Claude Code

Add to `CLAUDE.md` or as `@import` directives:

```markdown
@/path/to/workspace/IDENTITY.md
@/path/to/workspace/SOUL.md
@/path/to/workspace/USER.md
@/path/to/workspace/MEMORY.md
```

### Gemini CLI

GEMINI.md is loaded automatically. Add the same `@import` directives.

### Codex CLI

CODEX.md is loaded automatically. Add the same `@import` directives.

### Copilot CLI

COPILOT.md is referenced from `~/.github/copilot/`. Add imports there.

---

## Session-End Hook

The session-end hook calls `gish log --from-session` to record a session boundary.
This is what lets `gish doctor` detect whether hooks are properly configured.

### Claude Code Stop Hook

`~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "type": "command",
        "command": "gish log --from-session --workspace /path/to/workspace",
        "matcher": ".*"
      }
    ]
  }
}
```

### Gemini / Codex Wrapper Script

```bash
#!/usr/bin/env bash
# ~/bin/gemini-with-memory
gemini "$@"
exit_code=$?
gish log --from-session --workspace ~/my-workspace --runtime gemini-cli
exit $exit_code
```

Make executable and alias:

```bash
chmod +x ~/bin/gemini-with-memory
alias gemini='~/bin/gemini-with-memory'
```

### Copilot Shell Alias

```bash
# ~/.zshrc
alias copilot='gh copilot; gish log --from-session --workspace ~/my-workspace --runtime copilot-cli'
```

---

## Inline Triggers

Any command can be called manually at any time:

```bash
# Record a memory
gish log --workspace ~/my-workspace \
  --title "Decided to use PostgreSQL" \
  --content "Chose PostgreSQL over SQLite for concurrent write support." \
  --tags database,decision \
  --importance 8

# Search memory
gish recall --workspace ~/my-workspace "PostgreSQL"

# Run all maintenance
gish run-maintenance --workspace ~/my-workspace

# Health check
gish doctor --workspace ~/my-workspace
```

---

## HEAL Loop

HEAL (Health Engine Automated Loop) provides self-healing hints when the health engine
detects degraded state.

**Trigger**: `health.run()` calls `_detect_missed_triggers()` which checks whether
`session_boundaries.jsonl` exists. If not, it emits a hint.

**Output**: Hints are written to `.gish/logs/heal.log`.

**Viewing hints**:

```bash
gish doctor --workspace ~/my-workspace --heal-hooks
```

Output:

```
── HEAL hooks report ──
Missed trigger hints (from this run):
  • session_boundaries.jsonl not found — session-end hook may not be configured.

How to fix:
  • Claude Code: add stop-hook to ~/.claude/settings.json
  • Other CLIs: add `gish log --from-session` to your wrapper exit handler.
```

**Programmatic access**:

```python
from ghost_in_shell.engines import health
from pathlib import Path

report = health.run(Path("~/my-workspace"))
for hint in report["heal_hints"]:
    print(hint)
```

---

## Maintenance Engine Order

`gish run-maintenance` runs engines in this order:

1. `session_log` (flush any buffered session data)
2. `judge` (score quality)
3. `decay` (apply strength decay)
4. `consolidate` (merge if threshold reached)
5. `associate` (rebuild association graph)
6. `health` (update manifest stats + emit HEAL hints)

---

## Next Steps

→ [Chapter 09 — Customization](ch.09-customization.md)
