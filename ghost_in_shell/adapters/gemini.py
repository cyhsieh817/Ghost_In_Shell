"""Gemini CLI adapter — spec § 7 Gemini CLI row."""

import shutil

from ghost_in_shell.adapters.base import CLIAdapter


class GeminiAdapter(CLIAdapter):
    name = "gemini"
    cli_binary = "gemini"

    def session_start_hook(self) -> str:
        return (
            "# Gemini CLI session-start hook (managed by gish)\n"
            "# GEMINI.md is loaded automatically at session start.\n"
            "# Add this to your GEMINI.md @imports block:\n"
            "@<workspace>/IDENTITY.md\n"
            "@<workspace>/SOUL.md\n"
            "@<workspace>/USER.md\n"
            "@<workspace>/MEMORY.md\n"
            "# Use activate_skill() in GEMINI.md to load skills.\n"
        )

    def session_end_hook(self) -> str:
        return (
            "# Gemini CLI session-end hook (managed by gish)\n"
            "# Add to your gemini wrapper exit handler:\n"
            "gish log --from-session\n"
        )

    def root_instruction_template(self) -> str:
        return (
            "# Gemini CLI Root Instruction (managed by gish)\n\n"
            "@<workspace>/IDENTITY.md\n"
            "@<workspace>/SOUL.md\n"
            "@<workspace>/USER.md\n"
            "@<workspace>/MEMORY.md\n\n"
            "## CLI-specific notes\n"
            "- GEMINI.md is the root instruction file for Gemini CLI.\n"
            "- Use activate_skill() for agent skill loading.\n"
            "- Tool-name mapping: see memory/runtime_profiles.yml.\n"
        )

    def detect_installation(self) -> bool:
        return shutil.which("gemini") is not None
