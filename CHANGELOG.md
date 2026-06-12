# Changelog

All notable changes to gshell-memory will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `gish dream` — unified nightly sleep-cycle maintenance, modeled on human sleep:
  replay (associate) → rem (consolidate) → verdict (judge) → prune (decay) →
  gate (health). Deep sleep on Sundays (or `--deep`) adds a full audit and
  carryover expiry. Stages are failure-isolated: one crashing engine never
  blocks pruning or the wake-up gate.
- New engine `gshell_memory.engines.dream` with `run(workspace, dry_run, deep, today)`.

### Changed
- `gish init --schedule` now installs a single nightly `gish dream` entry
  (03:30) instead of five scattered `run-maintenance` lines, across cron,
  Windows Task XML, and the fallback shell script.

### Fixed
- Cron/scheduler templates referenced engines that never existed
  (`associate-strength`, `consolidate-check`) and omitted the required
  `--workspace` option — every installed schedule line failed at runtime.
  Regression-guarded by `test_cron_template_only_schedules_real_commands`.
- `gish init` now creates all four root identity files (`IDENTITY.md`,
  `SOUL.md`, `USER.md`, `MEMORY.md`). Previously the adapters' `@imports`
  snippets referenced `USER.md` / `MEMORY.md` that init never wrote, so a
  fresh Claude Code setup started with two broken imports.

### Security / Privacy
- Personal-data gate redesigned: the public `forbidden_strings.txt` no
  longer lists private identifiers (which itself leaked them). Private
  entries move to gitignored `tests/forbidden_strings.local.txt` or the
  `GISH_FORBIDDEN_EXTRA` env var (CI secret); a literal-free structural
  check now flags any real `/Users/<name>` home path that is not a
  documented example persona.
- Internal development plan documents removed from the published tree;
  remaining upstream-workspace references in `legacy/` neutralized.

## [5.1.0] — 2026-05-24

### Added
- LabGrimoire Desktop Bridge: see docs/ch.18-lgd-bridge.md.
- `gish doctor` is hardened against schema-violating writes; reports issues via structured `health.issues` list instead of crashing.
- New integration test `tests/integration/test_lgd_interop.py`.

## gshell-memory [5.0.0] — 2026-05-24

### Added
- M5 stabilisation: CI workflow (pytest + ruff + personal-data gate)
- M5 packaging: PyPI distribution as `gshell-memory`
- M6 capability abstractions: SOPRoute / ArchiveRoute / Carryover / FrozenEnum / HeartbeatConfig / SubdirRegistry / BrainRegionExtension
- M6 sub-package: `gshell-memory-schema` ships Pydantic models and JSON Schema separately
- Bridge: LabGrimoire_Desktop adapter via `grimoire.toml#[sources.memory] type = "gshell"`

### Changed
- First stable release. Promoted from `5.0.0rc1`.
- Depends on `gshell-memory-schema>=5.1,<6.0`.
- Python package renamed `ghost_in_shell` → `gshell_memory`. The old name remains importable as a deprecation alias for one minor cycle (5.1) and is removed in 6.0.
- README static '214 tests' badge replaced with live GitHub Actions and PyPI badges.

## gshell-memory-schema [5.1.0] — 2026-05-24

### Added
- `BrainRegionExtension` model for opt-in regions beyond the 5 fixed defaults; lives under `extensions:` so that 5.0 readers can safely ignore it.
- New capability models: `SOPRoute`, `ArchiveRoute`, `Carryover` (7-day expiry validator), `FrozenEnum`, `HeartbeatConfig`, `SubdirRegistry`.
- JSON Schema artifacts regenerated and gated by an in-sync CI check.

### Changed
- `BrainRegionManifest.schema_version` accepts both legacy `int` and new `"5.1"` string; new `init` writes `"5.1"`.
- `__schema_version__` bumped to `(5, 1)`.

## [5.0.0rc1] — 2026-05-22

### Added
- M4: `gish migrate v4` command
- M4: docs/ch.00 through ch.10
- M4: examples/minimal and examples/multi_cli

## [5.0.0a4] — 2026-05-15 (M3)
- Adapters (Claude / Gemini / Codex / Copilot)
- `gish init` wizard
- `gish run-maintenance`

## [5.0.0a3] — 2026-05-08 (M2)
- CLI: `gish log` / `gish recall` / `gish doctor` / `gish audit`
- Executor + ConsolidateEngine + JudgeEngine

## [5.0.0a2] — 2026-05-01 (M1)
- Memory stores, engines, schemas — foundation
