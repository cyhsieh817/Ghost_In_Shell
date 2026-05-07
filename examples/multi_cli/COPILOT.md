# GitHub Copilot CLI Root Instruction (managed by gish)

@./IDENTITY.md
@./SOUL.md
@./USER.md
@./MEMORY.md

## CLI-specific notes
- COPILOT.md is the root instruction file for GitHub Copilot CLI.
- Global config lives in ~/.github/copilot/.
- An alias wrapper is required for session-end logging:
  `alias copilot='gh copilot; gish log --from-session --workspace . --runtime copilot-cli'`
