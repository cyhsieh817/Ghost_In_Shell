# Copilot Runtime

Read `AGENTS.md` first.

Use this runtime as a reviewer or secondary executor.
Start interactive sessions via `bash scripts/void-copilot.sh` or installed shell wrappers.

## Global Configuration Required

> **Important**: GitHub Copilot CLI must be configured at the **global** level (`~/.github/copilot/`) for the memory flow to work reliably. Unlike Claude Code (which reads per-project `CLAUDE.md`) or Gemini CLI (which reads per-project `GEMINI.md`), Copilot CLI loads its instructions from global config. If you only configure it at the project level, the identity and memory paths will not be injected into every session.
>
> Place your Copilot instructions (identity, memory paths, language rules) in the global config location, then reference your project-level `AGENTS.md` from there.
