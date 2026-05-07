# Claude Code Root Instruction (managed by gish)

@./IDENTITY.md
@./SOUL.md
@./USER.md
@./MEMORY.md

## CLI-specific notes
- Use the `Skill` tool for agent skill loading.
- PreToolUse on Read triggers retrieval-buffer access.
- Session-end hook: add to ~/.claude/settings.json → hooks → Stop:
  `{"type": "command", "command": "gish log --from-session --workspace . --runtime claude-code", "matcher": ".*"}`
