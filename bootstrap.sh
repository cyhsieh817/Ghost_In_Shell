#!/usr/bin/env bash
# Ghost In Shell v5 bootstrap installer.
#
# Steps:
#   1. detect Python >= 3.11
#   2. pip install -e .
#   3. ask: target workspace path? (default ~/.gish-workspace)
#   4. exec: gish init <path>
#   5. detect installed CLIs (claude/gemini/codex/gh/copilot)
#   6. print hook snippets (read-only — never modifies ~/.claude/settings.json
#      unless --auto-hooks is passed)
#   7. ask: install cron schedule? [Y/n]
#   8. print "Next steps" checklist

set -euo pipefail

usage() {
    cat <<'EOF'
Ghost In Shell v5 bootstrap

Usage:
  ./bootstrap.sh [--non-interactive] [--help]

Options:
  --non-interactive   Skip all prompts; use defaults (workspace: ~/.gish-workspace)
  --help / -h         Show this help and exit

This script:
  1. Verifies Python >= 3.11
  2. Installs ghost_in_shell via `pip install -e .`
  3. Initializes a gish workspace with `gish init`
  4. Detects installed CLIs and prints hook snippets
  5. Optionally installs cron maintenance schedule

The `gish` CLI is then available: try `gish --help`.
EOF
}

NON_INTERACTIVE=false

for arg in "$@"; do
    case "$arg" in
        --help|-h)
            usage
            exit 0
            ;;
        --non-interactive)
            NON_INTERACTIVE=true
            ;;
        *)
            echo "Unknown option: $arg" >&2
            usage >&2
            exit 2
            ;;
    esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

echo "→ Ghost In Shell v5 bootstrap"
echo

# 1. Python version check
if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 not found in PATH" >&2
    exit 1
fi

PY_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
PY_MAJOR="${PY_VERSION%.*}"
PY_MINOR="${PY_VERSION#*.}"
if (( PY_MAJOR < 3 )) || { (( PY_MAJOR == 3 )) && (( PY_MINOR < 11 )); }; then
    echo "ERROR: Python 3.11+ required (found $PY_VERSION)" >&2
    exit 1
fi
echo "✓ python3 $PY_VERSION"

# 2. pip install -e .
echo "→ Installing ghost_in_shell in editable mode..."
python3 -m pip install -e . >/dev/null
echo "✓ pip install -e . succeeded"

# Verify gish is invocable
if ! command -v gish >/dev/null 2>&1; then
    echo "WARNING: 'gish' not found in PATH after install. Ensure the active venv's bin/ is on PATH."
else
    echo "✓ gish CLI installed: $(gish version)"
fi

# 3. Ask for workspace path
DEFAULT_WORKSPACE="$HOME/.gish-workspace"

if [ "$NON_INTERACTIVE" = "true" ]; then
    WORKSPACE_PATH="$DEFAULT_WORKSPACE"
    echo "→ workspace path (non-interactive): $WORKSPACE_PATH"
else
    echo
    read -r -p "Target workspace path? [default: $DEFAULT_WORKSPACE]: " WS_INPUT
    WORKSPACE_PATH="${WS_INPUT:-$DEFAULT_WORKSPACE}"
fi
echo "→ workspace: $WORKSPACE_PATH"

# 4. Run gish init
echo
echo "→ Running: gish init \"$WORKSPACE_PATH\" --non-interactive"
gish init "$WORKSPACE_PATH" --non-interactive

# 5. Detect installed CLIs
echo
echo "── Detecting installed CLIs ──"
DETECTED_CLIS=""
for CLI in claude gemini codex gh; do
    if command -v "$CLI" >/dev/null 2>&1; then
        echo "  ✓ $CLI found: $(command -v "$CLI")"
        DETECTED_CLIS="$DETECTED_CLIS $CLI"
    else
        echo "  ✗ $CLI not found"
    fi
done

# 6. Hook snippets are already printed by gish init above.
# Remind user where to find them.
if [ -n "$DETECTED_CLIS" ]; then
    echo
    echo "→ Hook snippets for detected CLIs were printed by gish init above."
    echo "  Add them to your CLI config files as instructed."
fi

# 7. Cron schedule
if [ "$NON_INTERACTIVE" = "true" ]; then
    INSTALL_CRON="n"
else
    echo
    read -r -p "Install cron schedule for maintenance tasks? [y/N]: " CRON_INPUT
    INSTALL_CRON="${CRON_INPUT:-n}"
fi

if [[ "$INSTALL_CRON" =~ ^[Yy]$ ]]; then
    echo "→ Installing cron schedule..."
    gish init "$WORKSPACE_PATH" --schedule --non-interactive
fi

# 8. Next steps checklist
cat <<EOF

── Next steps ──
  1. Edit $WORKSPACE_PATH/IDENTITY.md  to describe your workspace.
  2. Edit $WORKSPACE_PATH/SOUL.md       to choose a persona.
  3. Edit $WORKSPACE_PATH/memory/fact.yml   to set identity & preferences.
  4. Add the hook snippets above to your CLI configuration files.
  5. Run: gish doctor --workspace "$WORKSPACE_PATH"   to verify health.
  6. Try: gish recall "your query" --workspace "$WORKSPACE_PATH"

  Full docs: https://github.com/cyhsieh817/Ghost_In_Shell#documentation

EOF

