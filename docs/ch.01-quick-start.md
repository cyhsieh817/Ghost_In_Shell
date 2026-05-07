# Chapter 01 — Quick Start

Get from zero to `gish recall "anything"` in under five minutes.

---

## Prerequisites

- Python 3.11+
- At least one supported CLI installed: `claude`, `gemini`, `codex`, or `gh` (Copilot)

---

## Install gish

```bash
# From the repo root
pip install -e .

# Or from PyPI once published
pip install ghost-in-shell
```

Verify:

```bash
gish version
# Ghost In Shell 5.0.0a4
```

---

## Bootstrap a Workspace

The fastest path uses the provided `bootstrap.sh` script which initialises a workspace and
installs a cron schedule in one step:

```bash
bash bootstrap.sh ~/my-workspace
```

To do it manually:

```bash
gish init ~/my-workspace
```

`gish init` will:

1. Create the directory structure under `~/my-workspace/`.
2. Seed all template files (`fact.yml`, `episodic.jsonl`, `brain_region_manifest.yml`, etc.).
3. Detect installed CLIs and print the appropriate hook snippets.
4. Optionally install the cron maintenance schedule.

---

## Edit Your Identity

Open the three identity files and fill in relevant details:

```bash
# Who the agent is
$EDITOR ~/my-workspace/IDENTITY.md

# Persona / tone
$EDITOR ~/my-workspace/SOUL.md

# Your preferences (optional)
$EDITOR ~/my-workspace/USER.md
```

At minimum, edit `memory/fact.yml` to set your workspace name:

```yaml
# ~/my-workspace/memory/fact.yml
identity:
  name: "My Agent"
  language: "en"
  timezone: "UTC"
```

---

## Wire the Session Hook

Each CLI needs to know about your workspace at session start. `gish init` prints the
correct snippet for each detected CLI. For Claude Code, add to `CLAUDE.md`:

```markdown
@/path/to/my-workspace/IDENTITY.md
@/path/to/my-workspace/SOUL.md
@/path/to/my-workspace/MEMORY.md
```

For the session-end hook (so sessions are logged), add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "type": "command",
        "command": "gish log --from-session",
        "matcher": ".*"
      }
    ]
  }
}
```

See [Chapter 08 — Cron & Hooks](ch.08-cron-hooks.md) for full hook setup per CLI.

---

## Log a Memory

```bash
gish log --workspace ~/my-workspace \
  --title "Learned about gish" \
  --content "Ghost In Shell stores episodic memories in a JSONL file." \
  --tags learned,gish \
  --importance 7
```

---

## Recall a Memory

```bash
gish recall --workspace ~/my-workspace "episodic memories"
```

Sample output:

```
── Recall results for "episodic memories" ──
[ep_00000001] Learned about gish (importance: 7)
  Ghost In Shell stores episodic memories in a JSONL file.
  Tags: learned, gish
```

---

## Check Workspace Health

```bash
gish doctor --workspace ~/my-workspace
# Status: ok
# Episodes: 1  Edges: 0
```

---

## Run Maintenance

Apply decay, consolidation, and association engines in one command:

```bash
gish run-maintenance --workspace ~/my-workspace
```

This is also what the cron schedule runs nightly.

---

## Next Steps

→ [Chapter 02 — Identity Trinity](ch.02-identity-trinity.md)
