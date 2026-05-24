"""Claude Code adapter — spec § 7 Claude Code row."""

import shutil

from gshell_memory.adapters.base import CLIAdapter


class ClaudeAdapter(CLIAdapter):
    name = "claude"
    cli_binary = "claude"

    def session_start_hook(self) -> str:
        return (
            "# Claude Code session-start hook (managed by gish)\n"
            "# Add this to your CLAUDE.md @imports block:\n"
            "@<workspace>/IDENTITY.md\n"
            "@<workspace>/SOUL.md\n"
            "@<workspace>/USER.md\n"
            "@<workspace>/MEMORY.md\n"
        )

    def session_end_hook(self) -> str:
        return (
            "# Add to ~/.claude/settings.json → hooks → Stop:\n"
            "{\n"
            '  "type": "command",\n'
            '  "command": "gish log --from-session",\n'
            '  "matcher": ".*"\n'
            "}\n"
        )

    def root_instruction_template(self) -> str:
        return (
            "# Claude Code Root Instruction (managed by gish)\n\n"
            "@<workspace>/IDENTITY.md\n"
            "@<workspace>/SOUL.md\n"
            "@<workspace>/USER.md\n"
            "@<workspace>/MEMORY.md\n\n"
            "## CLI-specific notes\n"
            "- Use the `Skill` tool for agent skill loading.\n"
            "- PreToolUse on Read triggers retrieval-buffer access.\n"
        )

    def detect_installation(self) -> bool:
        return shutil.which("claude") is not None
