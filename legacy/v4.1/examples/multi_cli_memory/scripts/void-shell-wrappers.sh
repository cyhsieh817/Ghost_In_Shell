        #!/usr/bin/env bash

        if [ -n "${GHOST_MEMORY_WRAPPERS_LOADED:-}" ]; then
          return 0 2>/dev/null || exit 0
        fi
        export GHOST_MEMORY_WRAPPERS_LOADED=1

        : "${GHOST_IN_SHELL_REF_SCRIPTS:?Set by install_llm_shell_aliases.py before sourcing this file.}"

        claude() { "$GHOST_IN_SHELL_REF_SCRIPTS/void-claude.sh" "$@"; }
        claude_native() { command claude "$@"; }
        gemini() { "$GHOST_IN_SHELL_REF_SCRIPTS/void-gemini.sh" "$@"; }
        gemini_native() { command gemini "$@"; }
        copilot() { "$GHOST_IN_SHELL_REF_SCRIPTS/void-copilot.sh" "$@"; }
        copilot_native() { command copilot "$@"; }
        codex() { "$GHOST_IN_SHELL_REF_SCRIPTS/void-codex.sh" "$@"; }
        codex_native() { command codex "$@"; }
        openclaw() { "$GHOST_IN_SHELL_REF_SCRIPTS/void-openclaw.sh" "$@"; }
        openclaw_native() { command openclaw "$@"; }

        ghost_memory_wrappers_status() {
          printf '%s
'             "claude      -> $GHOST_IN_SHELL_REF_SCRIPTS/void-claude.sh"             "gemini      -> $GHOST_IN_SHELL_REF_SCRIPTS/void-gemini.sh"             "copilot     -> $GHOST_IN_SHELL_REF_SCRIPTS/void-copilot.sh"             "codex       -> $GHOST_IN_SHELL_REF_SCRIPTS/void-codex.sh"             "openclaw    -> $GHOST_IN_SHELL_REF_SCRIPTS/void-openclaw.sh"             "native cmds -> claude_native / gemini_native / copilot_native / codex_native / openclaw_native"
        }
