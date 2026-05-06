#!/usr/bin/env bash
# Ghost In Shell v5 bootstrap installer (M1 stub).
#
# What this script will do (target behaviour for later milestones):
#   1. detect Python >= 3.11
#   2. pip install -e . into the active environment
#   3. ask: target workspace path? (default ~/.gish-workspace)
#   4. exec: gish init <path>
#   5. detect installed CLIs (claude/gemini/codex/copilot)
#   6. print hook snippets (read-only — never modifies ~/.claude/settings.json
#      unless --auto-hooks is passed)
#   7. ask: install cron schedule? [Y/n]
#   8. print "Next steps" checklist
#
# In M1 this script only ensures the package can be installed and prints the
# next-step checklist. Steps 3-7 land in M3.

set -euo pipefail

usage() {
    cat <<'EOF'
Ghost In Shell v5 bootstrap (alpha, M1)

Usage:
  ./bootstrap.sh [--help]

Currently this script:
  - verifies Python >= 3.11
  - installs the ghost_in_shell package via `pip install -e .`
  - prints next-steps for completing the setup once M2/M3 milestones land

The full installer (workspace init, hook snippets, cron) lands in M3.
The `gish` CLI itself is available now: try `gish version`.
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    usage
    exit 0
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

echo "→ Ghost In Shell v5 bootstrap (M1 alpha)"
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
echo "→ installing ghost_in_shell in editable mode..."
python3 -m pip install -e . >/dev/null
echo "✓ pip install -e . succeeded"

# 3. verify gish is invocable
if ! command -v gish >/dev/null 2>&1; then
    echo "WARNING: 'gish' not found in PATH after install. Make sure the active venv's bin/ is on PATH."
else
    echo "✓ gish CLI installed: $(gish version)"
fi

# 4. next steps
cat <<'EOF'

Next steps:
  - Try   `gish --help`   to see the planned subcommands.
  - The `gish init`, `gish recall`, `gish audit` etc. are stubs in M1 — they will
    print "M1 stub — not yet implemented" and exit non-zero. Full behaviour
    arrives in M2 (memory + engines) and M3 (adapters + bootstrap polish).
  - Track progress on branch `v5/rewrite`; design spec lives in the
    TheVoidWeaver workspace (see README.md).

EOF
