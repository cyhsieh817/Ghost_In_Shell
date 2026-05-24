"""Codex CLI adapter — spec § 7 Codex CLI row."""

import shutil

from gshell_memory.adapters.base import CLIAdapter


class CodexAdapter(CLIAdapter):
    name = "codex"
    cli_binary = "codex"

    def session_start_hook(self) -> str:
        return (
            "# Codex CLI session-start hook (managed by gish)\n"
            "# CODEX.md is loaded at session start.\n"
            "# Add this to your CODEX.md @imports block:\n"
            "@<workspace>/IDENTITY.md\n"
            "@<workspace>/SOUL.md\n"
            "@<workspace>/USER.md\n"
            "@<workspace>/MEMORY.md\n"
            "# The gish wrapper injects runtime metadata from runtime_profiles.yml.\n"
        )

    def session_end_hook(self) -> str:
        return (
            "# Codex CLI session-end hook (managed by gish)\n"
            "# Add to your codex wrapper exit handler:\n"
            "gish log --from-session\n"
        )

    def root_instruction_template(self) -> str:
        return (
            "# Codex CLI Root Instruction (managed by gish)\n\n"
            "@<workspace>/IDENTITY.md\n"
            "@<workspace>/SOUL.md\n"
            "@<workspace>/USER.md\n"
            "@<workspace>/MEMORY.md\n\n"
            "## CLI-specific notes\n"
            "- CODEX.md is the root instruction file for Codex CLI.\n"
            "- The wrapper injects runtime metadata at session start.\n"
            "- Runtime profile is sourced from memory/runtime_profiles.yml.\n"
        )

    def detect_installation(self) -> bool:
        return shutil.which("codex") is not None
