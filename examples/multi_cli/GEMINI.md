# Gemini CLI Root Instruction (managed by gish)

@./IDENTITY.md
@./SOUL.md
@./USER.md
@./MEMORY.md

## CLI-specific notes
- GEMINI.md is the root instruction file for Gemini CLI.
- Use activate_skill() for agent skill loading.
- Tool-name mapping: see memory/runtime_profiles.yml.
- Session-end hook: add `gish log --from-session --workspace . --runtime gemini-cli` to your gemini wrapper exit handler.
