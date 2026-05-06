# 10 — Cross-Machine Sync

> One bootstrap script. Any machine. Full agent in minutes.

---

## The Problem

You set up your AI agent perfectly on one machine. Then you:
- Get a new laptop
- Work from a different computer
- Set up a cloud VM

And you have to redo everything — identity files, memory, tools, plugins, configurations.

**The hidden trap**: If your workspace is cloud-synced (iCloud, Dropbox), **symlinks inside it get synced too**. When two machines have different usernames (`$HOME` differs), symlinks from Machine A overwrite Machine B's — and vice versa, creating an infinite conflict loop.

## The Solution: Vault-First Architecture + .nosync Protection

Store all agent config in the **Vault** (cloud-synced). On any new machine, run one bootstrap script to create symlinks and restore the full environment. **All workspace-level symlinks use `.nosync` suffix** to prevent cloud sync from propagating machine-specific paths.

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

Workspace (cloud-synced)
┌──────────────────────────────────────────┐
│ MyVault.nosync → ~/Library/.../iCloud/   │  ← .nosync = not synced
│ .claude.nosync → ~/.claude               │  ← each machine has its own
│ scripts/_paths.sh  → resolves VAULT      │  ← fallback chain
└──────────────────────────────────────────┘
```

### Why `.nosync`?

macOS iCloud (and some other cloud providers) sync symlinks as-is, including their **target paths**. If Machine A creates:
```
MyVault → /Users/alice/Library/.../iCloud/MyVault
```
iCloud syncs this to Machine B, where Alice's path doesn't exist. Machine B's bootstrap fixes it, but that fix syncs back to A — **ping-pong forever**.

Adding `.nosync` to the symlink name tells iCloud to **skip syncing that file entirely**. Each machine maintains its own symlinks independently.

```
# ❌ BAD — synced, overwrites other machine
MyVault → /Users/alice/Library/.../iCloud/MyVault

# ✅ GOOD — not synced, each machine independent
MyVault.nosync → /Users/alice/Library/.../iCloud/MyVault
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

| Item | Synced (Vault) | Local Only | Notes |
|------|---------------|------------|-------|
| agents/ | ✅ | Symlinked | Content synced; symlink local |
| skills/ | ✅ | Symlinked | Content synced; symlink local |
| hooks/ | ✅ | Symlinked | Content synced; symlink local |
| CLAUDE.md | Template in vault | Generated per machine | Path variables differ |
| settings.json | Template in vault | Generated per machine | Path variables differ |
| settings.local.json | ❌ | Machine-specific | Personal overrides |
| Memory (fact.yml etc.) | ✅ | Via vault | Shared across machines |
| Plugins | ❌ | Installed per machine | `plugins_manifest.txt` lists them |
| Workspace symlinks | ❌ | `.nosync` suffix | **Each machine independent** |
| `.machine_role` | ✅ (safe) | Per-hostname entries | `hostname=role` format |

---

## Path Resolution: _paths.sh / _paths.py

All scripts **must** use `_paths.sh` (bash) or `_paths.py` (Python) to resolve the VAULT path. **Never hardcode** `/Users/alice/...` in scripts.

### Fallback Chain

```bash
# _paths.sh
if [ -e "$WORKSPACE/MyVault.nosync" ]; then
    export VAULT="$WORKSPACE/MyVault.nosync"          # .nosync symlink (preferred)
elif [ -e "$WORKSPACE/MyVault" ]; then
    export VAULT="$WORKSPACE/MyVault"                  # legacy symlink
else
    export VAULT="$HOME/Library/.../iCloud/MyVault"    # direct iCloud path
fi
```

```python
# _paths.py
_vault_nosync = WORKSPACE / "MyVault.nosync"
_vault_legacy = WORKSPACE / "MyVault"
_vault_direct = Path.home() / "Library" / "..." / "MyVault"

VAULT = next(p for p in [_vault_nosync, _vault_legacy, _vault_direct] if p.exists())
```

**Key principle**: Scripts reference `VAULT` from `_paths`, never construct the path themselves. This ensures the `.nosync` migration doesn't break anything — old scripts using the fallback chain still work.

---

## ~/.claude/ Symlinks: Direct to Vault

**Critical**: The `~/.claude/agents`, `~/.claude/skills`, and `~/.claude/hooks` symlinks must point **directly to the Vault's iCloud path**, not through the workspace symlink.

```bash
# ❌ BAD — breaks if workspace symlink is renamed
~/.claude/agents → /workspace/MyVault/_Agent_System/.../agents
#                   ↑ this is a symlink, if renamed → chain breaks

# ✅ GOOD — direct to iCloud container
~/.claude/agents → ~/Library/Mobile Documents/iCloud~md~obsidian/.../agents
#                   ↑ this is the real path, always stable
```

The bootstrap script handles this automatically.

---

## Primary / Secondary Machine Roles

`.machine_role` uses hostname-based entries so multiple machines can share the file via cloud sync:

```
# .machine_role
AliceMacBook=primary
WorkDesktop=secondary
```

- **Primary**: Full write access to shared resources (memory consolidation, scheduled tasks)
- **Secondary**: Read-only for shared resources; local tasks still work

Scripts use `require_primary()` to guard write operations:

```python
from _paths import require_primary
require_primary("memory consolidation")  # exits if not primary
```

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
- **After migrating symlinks to `.nosync`** (one-time)

---

## Migration Checklist: Adding .nosync

If you're adding `.nosync` protection to an existing setup:

1. **Rename workspace symlinks**: `mv MyVault MyVault.nosync`
2. **Update `_paths.sh` / `_paths.py`**: Add `.nosync` to fallback chain
3. **Update `setup-symlinks.sh`**: Create `.nosync` symlinks, clean old names
4. **Update `bootstrap.sh`**: Same as above
5. **Fix `~/.claude/` symlinks**: Point directly to iCloud, not through workspace
6. **Update `.gitignore`**: Add `*.nosync` entries
7. **Grep for hardcoded paths**: `grep -r 'MyVault/' scripts/ | grep -v _paths`
8. **Run all scripts**: Verify nothing breaks with the new paths

---

*One source of truth. Infinite deployments. Zero symlink conflicts.* 🐚
