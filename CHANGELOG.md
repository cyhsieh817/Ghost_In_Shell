# Changelog

All notable changes to gshell-memory will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [5.2.0] — 2026-10-07

Lessons from a year of daily multi-agent use, moved from convention into code.

### Added
- Knowledge layer (docs ch.19): `memory/knowledge/{feedback,projects,references,user}/`
  notes with a frontmatter contract (`name`, `description`, `metadata.type`,
  `metadata.updated`, optional `confidence` / `evidence` / `expires`).
  `gish init` creates the shelves; `MEMORY.md` template rewritten as a
  trigger-phrase index with a Tier 1 section.
- `gish index budget` — measures `MEMORY.md` in characters against
  `index.max_chars` / `index.truncate_edge_chars`; exit 0 / 1 / 2 / 3.
- `gish knowledge new` / `gish knowledge lint` — note skeletons, frontmatter
  checks, broken index links (error), orphan notes and trigger-less index
  lines (warning), expired notes (warning). `health` / `doctor` / `dream`
  report over-budget indexes and lint errors.
- Single-writer guard (docs ch.20): device-local machine role from
  `GISH_MACHINE_ROLE` or `$XDG_CONFIG_HOME/gish/machine_role`; secondary
  machines are refused by `gish dream`, `consolidate`, `decay`, and
  `EpisodicStore.append` (dry runs still allowed). Unknown roles fail closed.
- `judge.grade_proposal` — deterministic pre-checks plus an optional external
  judge (`consolidate.judge_command`) that fails closed.
- Docs: ch.19 Knowledge Index, ch.20 Write Discipline, ch.21 Field Lessons.

### Changed
- **Consolidation is now propose → judge → apply.** Proposals are written to
  `.gish/proposals/` with their verdict; only grades A-C apply; apply
  re-checks the sources under the lock and refuses stale proposals.
- **Consolidation no longer deletes episodes.** Sources move to
  `memory/_archive/episodic_consolidated.jsonl` before the rewrite, and the
  merged entry lists them in `linked_to`.
- `EpisodicStore.append`, `decay`, and consolidation apply hold
  `memory/.episodic.lock` across the whole read-modify-write.
- `.gish/config.yml` stores `workspace_path: "."` instead of an absolute path;
  `IDENTITY.md` no longer embeds the absolute workspace path. The stale
  `cron:` block (pointing at non-existent engines) is removed from the config
  template.
- Docs: module paths updated to `gshell_memory`, example paths made
  workspace-relative, stale version strings and API names corrected.

### Fixed
- `EpisodicStore.append` crashed with `AttributeError` when a near-duplicate
  episode had no `quality` field (the schema allows omitting it).
- The nightly `verdict` stage crashed on episodes stored with
  `"quality": null`. Both found by an end-to-end run, now regression-tested.
- `test_file_lock_blocks_concurrent_holder` raced the child process start-up
  under the macOS `spawn` start method; it now waits on an Event.

### Security / Privacy
- The public deny list now holds only generic credential prefixes. Every
  organisation, product, tool, and workspace-convention entry moved to the
  gitignored local list / CI secret.
- Test fixture renamed to `legacy_v4_sample` (internal codename removed).
- README no longer links a private repository.

### Earlier unreleased work included in 5.2.0

#### Added
- `gish dream` — unified nightly sleep-cycle maintenance, modeled on human sleep:
  replay (associate) → rem (consolidate) → verdict (judge) → prune (decay) →
  gate (health). Deep sleep on Sundays (or `--deep`) adds a full audit and
  carryover expiry. Stages are failure-isolated: one crashing engine never
  blocks pruning or the wake-up gate.
- New engine `gshell_memory.engines.dream` with `run(workspace, dry_run, deep, today)`.

#### Changed
- `gish init --schedule` now installs a single nightly `gish dream` entry
  (03:30) instead of five scattered `run-maintenance` lines, across cron,
  Windows Task XML, and the fallback shell script.

#### Fixed
- Cron/scheduler templates referenced engines that never existed
  (`associate-strength`, `consolidate-check`) and omitted the required
  `--workspace` option — every installed schedule line failed at runtime.
  Regression-guarded by `test_cron_template_only_schedules_real_commands`.
- `gish init` now creates all four root identity files (`IDENTITY.md`,
  `SOUL.md`, `USER.md`, `MEMORY.md`). Previously the adapters' `@imports`
  snippets referenced `USER.md` / `MEMORY.md` that init never wrote, so a
  fresh Claude Code setup started with two broken imports.

#### Security / Privacy
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
