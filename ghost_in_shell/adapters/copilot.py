"""GitHub Copilot CLI adapter — spec § 7 GitHub Copilot CLI row."""

from __future__ import annotations

import shutil
from pathlib import Path

from ghost_in_shell.adapters.base import CLIAdapter


class CopilotAdapter(CLIAdapter):
    name = "copilot"
    cli_binary = "gh"

    def session_start_hook(self) -> str:
        return (
            "# GitHub Copilot CLI session-start hook (managed by gish)\n"
            "# COPILOT.md is referenced from ~/.github/copilot/ global config.\n"
            "# Add this to your COPILOT.md @imports block:\n"
            "@<workspace>/IDENTITY.md\n"
            "@<workspace>/SOUL.md\n"
            "@<workspace>/USER.md\n"
            "@<workspace>/MEMORY.md\n"
            "# An alias wrapper is required to trigger session logging.\n"
        )

    def session_end_hook(self) -> str:
        return (
            "# GitHub Copilot CLI session-end hook (managed by gish)\n"
            "# No native stop-hook is available. Use an alias wrapper:\n"
            "# alias copilot='gh copilot; gish log --from-session'\n"
            "# Add to your shell profile (~/.bashrc or ~/.zshrc).\n"
        )

    def root_instruction_template(self) -> str:
        return (
            "# GitHub Copilot CLI Root Instruction (managed by gish)\n\n"
            "@<workspace>/IDENTITY.md\n"
            "@<workspace>/SOUL.md\n"
            "@<workspace>/USER.md\n"
            "@<workspace>/MEMORY.md\n\n"
            "## CLI-specific notes\n"
            "- COPILOT.md is the root instruction file for GitHub Copilot CLI.\n"
            "- Global config lives in ~/.github/copilot/.\n"
            "- An alias wrapper is required for session-end logging.\n"
        )

    def detect_installation(self) -> bool:
        if shutil.which("gh") is not None:
            return True
        copilot_dir = Path.home() / ".github" / "copilot"
        return copilot_dir.exists()
