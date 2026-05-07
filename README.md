# Ghost In Shell

> **Give your AI agent a soul, not just a prompt.**

**Status:** v5 clean rewrite in progress on branch `v5/rewrite`. The previous v4.1 documentation framework is preserved in `legacy/v4.1/` and on branch `legacy/v4` (tag `v4.1.0-final`).

The v5 design spec lives in the companion TheVoidWeaver workspace at `docs/superpowers/specs/2026-05-06-ghost-in-shell-v5-design.md`. A condensed public spec will be published here once v5.0.0a1 is tagged.

## What v5 will be

- A Python package `ghost_in_shell` with a `gish` CLI
- A multi-CLI agent memory framework (Claude Code, Gemini CLI, Codex CLI, GitHub Copilot CLI)
- An installable engine that performs episodic memory, association graphs, strength decay, sanctum governance, and brain-region routing
- MIT licensed

## Why v5 (clean rewrite)

v4.1 shipped as documentation + reference scripts. The engine that made the system reliable was never published as a runnable, installable artifact. v5 fixes that.

## Roadmap

| Milestone | Status |
|---|---|
| M1 — skeleton, CLI stubs, CI gate | ✓ COMPLETE |
| M2 — memory layer + engines | ✓ COMPLETE |
| M3 — multi-CLI adapters + bootstrap | ✓ COMPLETE 2026-05-07 |
| M4 — docs, examples, migrate command | not started |
| M5 — RC, merge to main | not started |

## License

MIT (see `LICENSE`).
