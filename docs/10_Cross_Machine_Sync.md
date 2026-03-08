# 10 — Cross-Machine Sync

> One bootstrap script. Any machine. Full agent in minutes.

---

## The Problem

You set up your AI agent perfectly on one machine. Then you:
- Get a new laptop
- Work from a different computer
- Set up a cloud VM

And you have to redo everything — identity files, memory, tools, plugins, configurations.

## The Solution: Vault-First Architecture

Store all agent config in the **Vault** (cloud-synced). On any new machine, run one bootstrap script to create symlinks and restore the full environment.

```
Vault (iCloud/Dropbox/Git)         Local Machine
┌──────────────────────┐           ┌─────────────────────┐
│ 992_Claude_Config/   │           │ ~/.claude/           │
│ ├── agents/          │──symlink──│ ├── agents/      → ⬆ │
│ ├── skills/          │──symlink──│ ├── skills/      → ⬆ │
│ ├── hooks/           │──symlink──│ ├── hooks/       → ⬆ │
│ ├── CLAUDE.md.tmpl   │──generate─│ ├── CLAUDE.md       │
│ ├── settings.tmpl    │──generate─│ ├── settings.json   │
│ └── bootstrap.sh     │           │ └── (ready to use)   │
└──────────────────────┘           └─────────────────────┘
```

---

## Bootstrap Script

### What It Does

1. Detects the current machine's OS and paths
2. Verifies cloud sync is complete
3. Creates symlinks for agents, skills, hooks
4. Generates `CLAUDE.md` from template (replacing path variables)
5. Generates `settings.json` from template
6. Validates everything works

### Example: bootstrap.sh

```bash
#!/bin/bash
set -euo pipefail

# ─── Configuration ───────────────────────────
VAULT_CONFIG="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_HOME="$HOME/.claude"
WORKSPACE="$(dirname "$(dirname "$(dirname "$VAULT_CONFIG")")")"

echo "🐚 Ghost In Shell — Bootstrap"
echo "  Vault Config: $VAULT_CONFIG"
echo "  Claude Home:  $CLAUDE_HOME"
echo "  Workspace:    $WORKSPACE"
echo ""

# ─── Create Claude Home ─────────────────────
mkdir -p "$CLAUDE_HOME"

# ─── Symlinks ────────────────────────────────
create_symlink() {
    local source="$1"
    local target="$2"

    if [ -L "$target" ]; then
        rm "$target"  # Remove old symlink
    elif [ -e "$target" ]; then
        echo "⚠️  $target exists and is not a symlink. Backing up..."
        mv "$target" "${target}.backup.$(date +%s)"
    fi

    ln -s "$source" "$target"
    echo "✅ Linked: $target → $source"
}

# Link shared directories
for dir in agents skills hooks; do
    if [ -d "$VAULT_CONFIG/$dir" ]; then
        create_symlink "$VAULT_CONFIG/$dir" "$CLAUDE_HOME/$dir"
    fi
done

# ─── Generate CLAUDE.md ─────────────────────
if [ -f "$VAULT_CONFIG/CLAUDE.md.template" ]; then
    sed "s|{{WORKSPACE}}|$WORKSPACE|g" \
        "$VAULT_CONFIG/CLAUDE.md.template" > "$CLAUDE_HOME/CLAUDE.md"
    echo "✅ Generated: $CLAUDE_HOME/CLAUDE.md"
fi

# ─── Generate settings.json ─────────────────
if [ -f "$VAULT_CONFIG/settings.template.json" ]; then
    cp "$VAULT_CONFIG/settings.template.json" "$CLAUDE_HOME/settings.json"
    echo "✅ Copied: $CLAUDE_HOME/settings.json"
fi

# ─── Verify ──────────────────────────────────
echo ""
echo "─── Verification ───"
errors=0

for dir in agents skills hooks; do
    if [ -L "$CLAUDE_HOME/$dir" ]; then
        count=$(ls "$CLAUDE_HOME/$dir" 2>/dev/null | wc -l | tr -d ' ')
        echo "✅ $dir: $count items"
    else
        echo "❌ $dir: not linked"
        errors=$((errors + 1))
    fi
done

if [ -f "$CLAUDE_HOME/CLAUDE.md" ]; then
    echo "✅ CLAUDE.md: exists"
else
    echo "❌ CLAUDE.md: missing"
    errors=$((errors + 1))
fi

echo ""
if [ $errors -eq 0 ]; then
    echo "🐚 Bootstrap complete. Your agent is ready."
else
    echo "⚠️  Bootstrap completed with $errors errors. Check above."
fi
```

---

## Directory Layout

### In Your Vault

```
99_System/992_Config/
├── bootstrap.sh              ← Run this on new machines
├── CLAUDE.md.template        ← Template with {{WORKSPACE}} variable
├── settings.template.json    ← Claude Code settings
├── plugins_manifest.txt      ← List of required plugins
├── agents/                   ← Custom agent definitions
│   ├── researcher.md
│   ├── coder.md
│   └── analyst.md
├── skills/                   ← Skill definitions
│   ├── skill_a/
│   └── skill_b/
└── hooks/                    ← Event hooks
    └── pre-commit.sh
```

### Template Variables

In `CLAUDE.md.template`:
```markdown
# Agent Configuration

@{{WORKSPACE}}/SOUL.md
@{{WORKSPACE}}/MEMORY.md
@{{WORKSPACE}}/memory/fact.yml
```

Bootstrap replaces `{{WORKSPACE}}` with the actual path on each machine.

---

## New Machine Setup

```bash
# 1. Wait for cloud sync to complete
ls ~/path/to/vault/  # Verify files are there

# 2. Run bootstrap
bash ~/path/to/vault/_Agent_System/99_System/992_Config/bootstrap.sh

# 3. Start your AI tool
claude  # or cursor, etc.

# 4. Verify identity
# Ask: "Who are you?" — should respond with full identity
```

---

## What Gets Synced vs Local

| Item | Synced (Vault) | Local Only |
|------|---------------|------------|
| agents/ | ✅ | Symlinked |
| skills/ | ✅ | Symlinked |
| hooks/ | ✅ | Symlinked |
| CLAUDE.md | Template in vault | Generated per machine |
| settings.json | Template in vault | Generated per machine |
| settings.local.json | ❌ | Machine-specific |
| Memory (fact.yml etc.) | ✅ | Via vault |
| Plugins | ❌ | Installed per machine |

---

## Updating Across Machines

When you change agent config:

1. **Change in Vault** (the source of truth)
2. **Cloud sync** distributes to all machines
3. **Symlinks** mean changes are instant (no re-bootstrap needed)

When to re-run bootstrap:
- New directory added (agents/, skills/, hooks/)
- CLAUDE.md.template changed (path variables updated)
- New machine setup

---

*One source of truth. Infinite deployments.* 🐚
