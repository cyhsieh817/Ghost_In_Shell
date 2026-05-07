# Codex CLI Root Instruction (managed by gish)

@./IDENTITY.md
@./SOUL.md
@./USER.md
@./MEMORY.md

## CLI-specific notes
- CODEX.md is the root instruction file for Codex CLI.
- The wrapper injects runtime metadata at session start.
- Runtime profile is sourced from memory/runtime_profiles.yml.
- Session-end hook: add `gish log --from-session --workspace . --runtime codex-cli` to your codex wrapper exit handler.
