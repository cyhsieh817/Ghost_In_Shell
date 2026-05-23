---
title: gshell-memory Product Launch — M5 + M6 + LGD Bridge
status: approved
created: 2026-05-24
spec_ref: null
plan_ref: null
owners: ["@cyhsieh817"]
---

# gshell-memory Product Launch — M5 + M6 + LGD Bridge

> **One-line**: Push `gshell-memory` (gish) from pre-launch to PyPI stable, abstract 7 dogfood-proven capabilities into the framework, and bridge LabGrimoire_Desktop (LGD) to the same workspace via a shared Pydantic + JSON Schema contract.

---

## 1. Goals & Success Criteria

Move `gshell-memory` (gish) from `5.0.0rc1` pre-launch state to a **shipping product**:

- `pip install gshell-memory` installs cleanly in one line — first PyPI release.
- GitHub Actions enforces every PR: pytest (3.11 / 3.12) + ruff + Personal-data gate.
- README and reality fully aligned (test count via dynamic CI badge).
- All seven M6 capabilities implemented with engines + CLI + docs + tests.
- A formal **Workspace Schema Spec** (Pydantic + JSON Schema dual output) shipped as a separate PyPI distribution: `gshell-memory-schema`.
- LGD `grimoire.toml#[sources.memory]` learns `type = "gshell"`; LGD `lgd_agent/memory/` rebuilt against the schema package (no engine dependency).
- Cross-repo interop verified: gish init's output is readable by LGD; LGD writes are readable by gish doctor/recall.

---

## 2. Scope

### In Scope

- gish M5 (stabilisation, CI, PyPI, CHANGELOG, CONTRIBUTING, .github templates)
- gish M6 (seven new engines + CLI + docs)
- `gshell-memory-schema` sub-package (Pydantic + auto-generated JSON Schema + version compatibility tooling)
- LGD `[sources.memory]` adapter for `type = "gshell"`
- LGD `lgd_agent/memory/` migration to schema-compliant implementation
- Cross-repo interop tests (golden fixtures + integration)
- Demo asciinema embedded in README

### Out of Scope

- Logo / branding / landing page (deferred until after engineering stable)
- Business model rollout (paid plugins, hosted dashboard) — observe-first
- gish daemon / HTTP API mode (contractor selected "parallel + shared workspace", not server-client)
- LGD GUI redesign — bridge touches the memory source layer only
- Any change to the private TheVoidWeaver workspace itself
- HN / Reddit / Twitter announcement — M7 distribution, separate effort
- Adding a fifth CLI adapter beyond claude/gemini/codex/copilot
- Docker image, mem0/letta/cognee comparison blog
- TheVoidWeaver-specific brain regions outside the 5 defaults + 4 documented extensions

---

## 3. Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                  L3 — LabGrimoire_Desktop (LGD)                      │
│       Tauri / Rust GUI + Rust harness + lgd_agent (Python)            │
│                                                                       │
│  ┌───────────────────────┐         ┌──────────────────────────────┐  │
│  │  grimoire.toml         │         │  lgd_agent/memory/           │  │
│  │  [sources.memory]      │ ──┬──→ │  schema-compliant 自實作      │  │
│  │  type = "gshell"       │   │     │  (Pydantic via schema pkg)   │  │
│  └───────────────────────┘   │     └──────────────────────────────┘  │
│                                │                                       │
└────────────────────────────────┼───────────────────────────────────────┘
                                 │
                                 │ read/write same workspace dir
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│           L2 — Workspace Schema Contract                              │
│       Pydantic models + JSON Schema + version evolution               │
│                                                                       │
│   schema_version: 5.1                                                 │
│   ├─ IDENTITY.md / SOUL.md / USER.md / MEMORY.md                      │
│   └─ memory/                                                          │
│      ├─ fact.yml                  ← FactStore                         │
│      ├─ episodic.jsonl            ← EpisodicEntry (SHA-256 fp)        │
│      ├─ associations.jsonl        ← Association                       │
│      ├─ brain_region_manifest.yml ← BrainRegionManifest + extensions  │
│      ├─ sanctum_registry.yml      ← SanctumRegistry                   │
│      ├─ runtime_profiles.yml      ← RuntimeProfiles                   │
│      ├─ memory_manifest.yml       ← MemoryManifest (#schema_version)  │
│      │── M6 new ──                                                    │
│      ├─ sop_dispatch.yml          ← SOPRoute                          │
│      ├─ archive_routing.yml       ← ArchiveRoute                      │
│      ├─ frozen_enums.yml          ← FrozenEnum                        │
│      ├─ heartbeat.yml             ← HeartbeatConfig                   │
│      ├─ subdir_registry.yml       ← SubdirRegistry                    │
│      └─ carryover/*.md            ← Carryover (frontmatter)           │
└─────────────────────────────────────────────────────────────────────┘
                                 ▲
                                 │ schema-compliant read/write
                                 │
┌────────────────────────────────┼───────────────────────────────────────┐
│           L1 — gshell-memory (gish)                                   │
│       Python 3.11+ pip package — CLI + library                        │
│                                                                       │
│   ┌─────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │
│   │  gish CLI   │  │  14 engines     │  │  4 CLI adapters         │  │
│   │  (click)    │  │  7 v5 + 7 M6    │  │  claude/gemini/codex/   │  │
│   │             │  │                 │  │  copilot                │  │
│   └─────────────┘  └─────────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

**Core contract**: L2 (Workspace Schema) is the source of truth. L1 (gish) and L3 (LGD lgd_agent) implement readers/writers independently but obey L2 schema. Schema is **first published / maintained** from the gish monorepo (gish is the reference implementation). LGD pulls `pip install gshell-memory-schema` (light sub-package) for validation without importing the engine.

**Why split schema into a sub-package**: gish main package includes engines/CLI/adapters (heavy). The schema sub-package contains only Pydantic models + JSON Schema files (light). LGD needs validation, not engines — pulling the light package preserves the "parallel & independent" contract.

---

## 4. Workspace Schema Contract Details

### 4.1 schema_version Strategy

SemVer-style: `<major>.<minor>`, written to `memory/memory_manifest.yml#schema_version`.

| Change | Bump | Example | Old reader impact |
|---|---|---|---|
| Add optional field | minor | `5.0` → `5.1`: add `quality.recurrence_count?` to episodic | Ignored; still readable |
| Add required field | **major** | `5.x` → `6.0`: add required `fingerprint` to episodic | Fail-fast; migrate needed |
| Rename field | **major** | `tags` → `labels` | Same as above |
| Tighten validation | **major** | importance from `0-10` to `1-10` | Same as above |
| Remove field | **major** | Drop `linked_to` | Old reader rejects; new reader ignores |

`gshell-memory-schema` package version == the `schema_version` it ships.

```python
def load_workspace(path: Path) -> Workspace:
    manifest = read_yaml(path / "memory/memory_manifest.yml")
    ws_version = parse_version(manifest["schema_version"])
    pkg_version = parse_version(gshell_memory_schema.__version__)
    if ws_version.major > pkg_version.major:
        raise SchemaTooNew(f"workspace is {ws_version}, package supports up to {pkg_version}")
    if ws_version.major < pkg_version.major:
        raise SchemaTooOld("run: gish migrate v<N>")
    # minor mismatch: ok (forward-compat)
```

### 4.2 Sub-Package Structure

```
gshell-memory-schema/                ← independent PyPI distribution
├── pyproject.toml
├── README.md
├── gshell_memory_schema/
│   ├── __init__.py                  ← __version__ = "5.1.0"
│   ├── models.py                    ← All Pydantic models
│   ├── enums.py                     ← Frozen enums
│   ├── version.py                   ← compatibility utilities
│   └── jsonschema/                  ← auto-generated JSON Schemas
│       ├── workspace.json
│       ├── episodic_entry.json
│       ├── fact.json
│       └── ...
├── tests/
│   └── test_models.py
└── scripts/
    └── generate_jsonschema.py       ← Pydantic → JSON Schema export
```

Monorepo decision: sub-package lives at root of the same repo, parallel to `gshell_memory/`. Each has its own `pyproject.toml` and ships as a separate PyPI distribution.

`gshell-memory` `pyproject.toml` declares: `dependencies = ["gshell-memory-schema>=5.0,<6.0"]`.

### 4.3 Model Inventory

**Existing v5 models (relocated and tightened):**

| Model | File | Key Fields |
|---|---|---|
| `Workspace` | (whole workspace dir) | `schema_version` / `paths` / metadata |
| `FactStore` | `memory/fact.yml` | `identity` / `preferences` / `rules` / `tools` / `archive` |
| `EpisodicEntry` | `memory/episodic.jsonl` | `id` / `title` / `content` / `date` / `ts` / `type` / `tags` / `importance` / `fingerprint` (SHA-256 required) / `retrieval{count,last_accessed,strength}` / `decay_status` / `linked_to` |
| `Association` | `memory/associations.jsonl` | `id` / `from` / `to` / `relation` / `confidence` / `created_at` / `created_by` / `evidence` |
| `BrainRegionManifest` | `memory/brain_region_manifest.yml` | `regions: {<name>: {display, core_files[], on_demand_files[]}}` + optional `extensions:` (5.1) |
| `SanctumRegistry` | `memory/sanctum_registry.yml` | `sources: [{id, path|path_glob, format, tier, write_cli?, exclude?}]` |
| `RuntimeProfiles` | `memory/runtime_profiles.yml` | `executors / runtimes / launchers` |
| `MemoryManifest` | `memory/memory_manifest.yml` | `schema_version` / `stats` / `last_consolidation` / `prompt_integrity{sha256}` |

**M6 new models:**

| Model | File | Purpose |
|---|---|---|
| `SOPRoute` | `memory/sop_dispatch.yml` | `name` / `triggers[]` / `must_read[]` / `also_read[]` / `skills_pipeline[]` / `note?` / `inline_sop?` |
| `ArchiveRoute` | `memory/archive_routing.yml` | `condition` / `target_dir` / `naming_pattern` / `frontmatter_required[]` / `note?` / `priority` |
| `Carryover` | `memory/carryover/*.md` (frontmatter) | `created` / `expires` (max 7d) / `project_slug` / `topic` / `status: active|expired|promoted` |
| `FrozenEnum` | `memory/frozen_enums.yml` | `name` / `values[]` / `introduced` / `layer` / `enforcement` / `spec_ref?` |
| `HeartbeatConfig` | `memory/heartbeat.yml` | `cadence: hourly|four_hourly|daily|monthly` / `checks[]` / `output_format` / `idle_threshold` |
| `SubdirRegistry` | `memory/subdir_registry.yml` | `registered: [{path, purpose, lifecycle}]` / `enforcement: warn|block` |
| `BrainRegionExtension` | `brain_region_manifest.yml#extensions` | Allow declaring regions beyond the 5 defaults (amygdala / parietal / occipital / temporal etc.), with `aliases?` |

### 4.4 Backward Compatibility

gish v5 ships 5 default brain regions (hippocampus / prefrontal / limbic / cerebellum / default). `BrainRegionExtension` lives in a separate `extensions:` block in the manifest (5.1 minor add):

```yaml
schema_version: 5.1
regions:
  hippocampus: { display: "...", core_files: [...] }
  prefrontal:  { display: "...", core_files: [...] }
  limbic:      { display: "...", core_files: [...] }
  cerebellum:  { display: "...", core_files: [...] }
  default:     { display: "...", core_files: [...] }
extensions:                                # 5.1 opt-in
  amygdala:
    display: "amygdala (security / vigilance)"
    core_files: [{ path: "POLICY.md" }]
  parietal:  { ... }
  occipital: { ... }
  temporal:  { ... }
```

Old 5.0 readers ignore `extensions:`; new 5.1 readers activate them.

### 4.5 JSON Schema Auto-Generation

`scripts/generate_jsonschema.py` uses Pydantic v2 `.model_json_schema()` to export each model as a standalone `.json` committed under `gshell_memory_schema/jsonschema/`. CI runs `--check` after pytest to ensure schemas are regenerated when models change.

**Rust consumption (LGD)**: `app/src-tauri/build.rs` declares `cargo:rerun-if-changed=path/to/gshell_memory_schema/jsonschema/`; runtime uses `schemars` derive or `serde_json` validation against these schemas.

### 4.6 Migration Matrix

| From | To | Tool |
|---|---|---|
| TheVoidWeaver private v4 | gshell workspace 5.0+ | `gish migrate v4 <old> <new>` (already shipped) |
| LGD existing `lgd_agent/memory/` | gshell workspace 5.0+ | New `lgd-agent migrate-to-gshell` (Bridge wave) |
| Fresh user | gshell workspace 5.0+ | `gish init <path>` |
| 5.0 → 5.1 (minor) | Same file, no action | Auto; reader ignores unknown fields |
| 5.x → 6.0 (major) | Write `gish migrate v5` | Out of scope; separate spec when v6 arrives |

---

## 5. M5 — Engineering Stabilisation & Release (3 Waves)

### Wave M5-A: Environment Stability (blocks all)

| Task | File | Acceptance |
|---|---|---|
| Fix pytest environment | `tests/conftest.py` + `pyproject.toml` | `pytest -q` runs clean on fresh venv; no `from datetime import UTC` ImportError |
| Add `.python-version` and/or `tox.ini` | new | Forces Python 3.11+; consistent between CI and local |
| Lock dependencies via `uv` | `pyproject.toml` + `uv.lock` | `uv sync` reproducibly rebuilds venv |
| Fix README "214 tests" → dynamic badge | `README.md` | Badge reflects real CI test count |

**Gate**: `pytest -q` fully green; README contains no stale numeric claims.

### Wave M5-B: CI & Contributor Infrastructure

| Task | File | Acceptance |
|---|---|---|
| GitHub Actions ci.yml | `.github/workflows/ci.yml` | on push / PR; matrix py3.11+3.12; steps: pytest + ruff + check_no_personal |
| Personal-data gate CI enforcement | within ci.yml | PRs containing deny-list strings fail automatically |
| CHANGELOG.md (Keep a Changelog) | new | M1–M4 milestones extracted from git log |
| CONTRIBUTING.md | new | fork/PR flow; deny-list maintenance; commit conventions |
| .github/ISSUE_TEMPLATE/, PULL_REQUEST_TEMPLATE.md | new | Bug template demands repro steps / gish version / Python version |
| CODE_OF_CONDUCT.md | new | Contributor Covenant 2.1 |

**Gate**: A test PR triggers full green CI and is rejected when injecting a deny-list term.

### Wave M5-C: PyPI Release

| Task | File | Acceptance |
|---|---|---|
| PyPI register `gshell-memory` (trusted publisher OIDC) | PyPI web | Account configured |
| `.github/workflows/release.yml` | new | on tag `v*` → build wheel + sdist → publish to PyPI |
| Rename `pyproject.toml#name` to `gshell-memory` | `pyproject.toml` | name aligns with distribution |
| Rename Python package `ghost_in_shell` → `gshell_memory` | repo-wide `git mv` | `import gshell_memory` works; legacy `ghost_in_shell` retained as deprecation alias one minor cycle |
| Preserve `gish` CLI entry | `[project.scripts]` | `gish --help` still works |
| Tag `v5.0.0rc1` → CI auto-publishes | git tag + push | `pip install gshell-memory==5.0.0rc1` resolves from PyPI |
| Demo asciinema | `docs/demo.cast` + README embed | 60-second flow: init → recall → run-maintenance |

**Gate**: `pip install gshell-memory` works in a clean venv; `gish version` prints 5.0.0rc1.

---

## 6. M6 — Capability Abstraction (3 Waves)

### Wave M6-A: Schema Sub-Package Born

| Task | File | Acceptance |
|---|---|---|
| Create monorepo sub-package | `gshell-memory-schema/` parallel to `gshell_memory/` | Independent pyproject.toml; independent PyPI distribution |
| 7 new M6 Pydantic models | `gshell_memory_schema/models.py` | SOPRoute / ArchiveRoute / Carryover / FrozenEnum / HeartbeatConfig / SubdirRegistry / BrainRegionExtension |
| Frozen enum utilities | `gshell_memory_schema/enums.py` | `decision_kind` / `rerun_status`; helper `freeze(name, values)` |
| Compatibility utilities | `gshell_memory_schema/version.py` | `is_compatible(workspace_ver, package_ver) → bool` |
| `scripts/generate_jsonschema.py` | new | Pydantic → 7 `.json` files; CI step `--check` |
| Schema package PyPI release | release.yml additional job | `pip install gshell-memory-schema` works |
| Main package dependency switch | `gshell-memory/pyproject.toml` | `dependencies = ["gshell-memory-schema>=5.0,<6.0"]` |

**Gate**: both PyPI distributions install cleanly; schema package tests at 100%; auto-generated JSON Schemas in sync.

### Wave M6-B: Engines & CLI Wiring (7 capabilities)

| Capability | Engine | CLI |
|---|---|---|
| SOP dispatch | `gshell_memory/engines/sop.py` | `gish sop register / list / trigger / test` |
| Archive routing | `gshell_memory/engines/archive_router.py` | `gish archive route add / list / preview <input>` |
| Carryover | `gshell_memory/engines/carryover.py` | `gish carryover create / list / expire / promote-to-episodic` |
| Frozen enums | `gshell_memory/engines/enum_freeze.py` | `gish enum freeze / list / validate` |
| Heartbeat | `gshell_memory/engines/heartbeat.py` | `gish heartbeat run / install --cron / install --launchd` |
| Brain region extension | `gshell_memory/memory/brain_regions.py` (modify) | `gish region declare <name> --aliases ... --on-demand <files>` |
| Subdirectory registry | `gshell_memory/engines/subdir_registry.py` | `gish memory dir register / list / enforce` |

For **each** capability:

- 1 unit test (`tests/unit/test_<name>.py`)
- 1 CLI integration test (`tests/integration/test_cli_<name>.py`)
- 1 doc chapter (`docs/ch.11-sop-dispatch.md` through `ch.17-subdir-registry.md`)

**Gate**: all 7 new commands listed by `gish --help`; docs ch.11-17 complete; module test coverage ≥ 80%.

### Wave M6-C: Stable Release & Doc Integration

| Task | File | Acceptance |
|---|---|---|
| Update README Features → 14 engines total | `README.md` | Table covers v5 7 + M6 7 |
| Update ch.04 Engine Internals (all 14) | `docs/ch.04-engine-internals.md` | Comprehensive |
| Add ch.11-17 (7 M6 capability deep-dives) | new files | Each has use case + CLI examples + Python API + schema mapping |
| Update ch.10 migration with v4 → v5.1 + brain region extension | `docs/ch.10-migration.md` | Documents the 7-region reattach path for TheVoidWeaver-style migrations |
| Bump `5.0.0rc1` → `5.0.0` stable | `pyproject.toml` + tag | Stable visible on PyPI |
| Bump schema_version 5.0 → 5.1 (minor, due to extensions) | `memory_manifest.yml` template | New init outputs 5.1 |

**Gate**: `gshell-memory==5.0.0` and `gshell-memory-schema==5.1.0` published; docs 14 chapters complete.

---

## 7. Bridge — LGD Integration (3 Waves)

### Wave Bridge-A: LGD Schema Adoption

| Task | File | Acceptance |
|---|---|---|
| LGD `lgd_agent/pyproject.toml` declares `gshell-memory-schema` dependency | LGD repo | `uv sync` resolves |
| `lgd_agent/memory/` refactor: drop self-made models, import sub-package | LGD repo `lgd_agent/memory/` | All readers/writers use `gshell_memory_schema` Pydantic |
| LGD Rust side ingests `gshell_memory_schema/jsonschema/*.json` | `app/src-tauri/build.rs` + `app/src-tauri/src/sources/` | Rust uses `schemars` derive aligned to schemas; build-time `cargo:rerun-if-changed` |
| LGD adds `tests/test_schema_compliance.rs` | LGD repo | Confirms LGD reads gish init output cleanly |

**Gate**: LGD pulls the schema sub-package; local schema-compliance test green.

### Wave Bridge-B: `[sources.memory]` Rewrite

| Task | File | Acceptance |
|---|---|---|
| `grimoire.example.toml` adds `type = "gshell"` + `path = "<workspace>"` | LGD repo | Type enum extended; legacy `jsonl-graph` kept for backward compat |
| Rust `src-tauri/src/sources/memory.rs` (or equivalent) adds `GshellSource` adapter | LGD repo | Reads all schema files (fact / episodic / associations / brain_region / sanctum / runtime_profiles / manifest) |
| New LGD command `lgd-agent migrate-to-gshell <old> <new>` | LGD `lgd_agent/` | Converts legacy LGD memory → gshell workspace |
| UI settings panel shows source type `gshell` connection status | LGD `app/src/modules/settings/` | GUI surfaces "Memory source: gshell @ ~/..." |

**Gate**: After switching `grimoire.toml` to `type = "gshell"` in the LGD app, all memory-dependent UI (Knowledge tab, Autonomy Timeline, Brain Region view) functions normally.

### Wave Bridge-C: Cross-Repo Interop Tests & Documentation

| Task | File | Acceptance |
|---|---|---|
| Add gish integration test `tests/integration/test_lgd_interop.py` | gish repo | Fixture mocks LGD writes; gish reader stays green |
| Add LGD integration test `tests/integration/test_gshell_interop.py` | LGD repo | Fixture simulates gish init / run-maintenance; LGD reader stays green |
| Write `docs/ch.18-lgd-bridge.md` (gish side) | gish repo | Architecture diagram / roles / grimoire.toml example / troubleshooting |
| Write `docs/integration/gshell-memory.md` (LGD side) | LGD repo | grimoire.toml#sources.memory config / migration from jsonl-graph |
| Add Bridge banner to README | gish README + LGD README | Cross-links between projects |
| Tag releases: gish `v5.0.0`, schema `v5.1.0`, LGD `v<next>` | git tag | Release notes cross-reference |

**Gate**: Contractor can locally run `gish init ~/test-ws` → set LGD `grimoire.toml` to point to `~/test-ws` → LGD starts and shows gish-written episodic / fact / brain region content in Knowledge tab.

---

## 8. Wave Dependency Graph

```
M5-A (blocker)
  └→ M5-B ─→ M5-C  (release track complete)

M6-A  (parallel with M5-B / M5-C)
  └→ M6-B
       └→ M6-C  (stable bump complete)

Bridge-A  (needs M6-A done)
  └→ Bridge-B
       └→ Bridge-C  (interop verified)
```

**Strict prerequisites:**

| Wave | Requires |
|---|---|
| M5-A | (none — blocker for everything else in the M5 track) |
| M5-B | M5-A |
| M5-C | M5-B (and trusted PyPI publisher configured) |
| M6-A | (none — runs parallel to M5-B onward) |
| M6-B | M6-A (sub-package models in place) |
| M6-C | M6-B |
| Bridge-A | M6-A (schema sub-package published to PyPI) |
| Bridge-B | Bridge-A (LGD pulled schema package) |
| Bridge-C | Bridge-B and M6-C (LGD adapter + gish stable both required) |

Two practical execution lanes can advance in parallel: the **release lane** (M5-A → M5-B → M5-C) and the **capability lane** (M6-A → M6-B → M6-C). Bridge waves attach to the capability lane once `M6-A` completes.

---

## 9. Time Estimate

| Wave | Effort | Estimate |
|---|---|---|
| M5-A Environment stability | Small | 0.5 day |
| M5-B CI + contributor infra | Medium | 1 day |
| M5-C PyPI release | Medium | 1 day |
| M6-A Schema sub-package | Medium | 1.5 days |
| M6-B Seven engines + CLI | **Large** | 3-5 days |
| M6-C Docs + stable bump | Medium | 1 day |
| Bridge-A LGD schema adoption | Medium | 1 day |
| Bridge-B sources.memory rewrite | Medium-Large | 2 days |
| Bridge-C Interop tests + docs | Medium | 1 day |
| **Total** | | **12-14 working days** |

---

## 10. Testing Strategy

### Test Layers

| Layer | Scope | Tool | Coverage Target |
|---|---|---|---|
| **Unit** | Single Pydantic model / pure engine functions | pytest | main pkg ≥ 80%, schema pkg ≥ 90% |
| **Integration** | engine ↔ workspace read/write / migrate flow | pytest + tmp_path | Each engine: 1 happy + 1 edge case |
| **Schema compliance** | Fuzz workspace, verify LGD reader accepts | Hypothesis + pytest | Each model: ≥ 10 fuzz cases |
| **Cross-repo interop** | gish write → LGD read; LGD write → gish read | both repos with fixtures | Wave Bridge-C must pass |
| **CLI integration** | `gish <cmd>` on fresh venv + tmp workspace | pytest + click CliRunner | All 14 engine commands + init + recall + doctor + migrate |
| **CI smoke** | PyPI-installed `gish version` / `init` / `doctor` | release.yml post-publish job | Runs after every PyPI release |

### Golden Fixtures

Under `tests/fixtures/golden/`:

- `voidweaver_v4_sample/` — de-personalised TheVoidWeaver v4 workspace (deny-list filtered) for migrate v4 regression
- `gshell_v5_minimal/` — minimal viable 5.0 workspace
- `gshell_v5_full/` — workspace with all 7 M6 capabilities configured (5.1)
- `lgd_legacy/` — synthetic LGD legacy `lgd_agent/memory/` format for Bridge migration testing

CI diff-checks golden output when schema sub-package PRs touch models.

### Personal-Data Gate Hardening

`scripts/ci/check_no_personal.py` already exists. This spec adds:

- Fail-fast mode: exit immediately on first deny-list hit
- `pre-commit` hook (`.pre-commit-config.yaml`) blocks local commits before push
- Deny-list additions discovered during this work: `labgrimoire/` path prefix (allow `LabGrimoire_Desktop` name)

---

## 11. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Python rename (`ghost_in_shell` → `gshell_memory`) breaks existing imports | Medium | High | Keep `ghost_in_shell` as deprecation alias one minor cycle; CHANGELOG callout; grep entire codebase before PR |
| Schema sub-package version mismatch with main | Medium | Medium | Main pins `gshell-memory-schema>=5.0,<6.0`; cross-package version check in release.yml |
| LGD Rust schema lags after gish schema bump | Medium | Medium-High | Bridge-A pins version; LGD `Cargo.lock` enforces; cross-repo dispatch issue on minor bump |
| README dynamic badge fails (Actions outage) | Low | Low | shields.io workflow-status badge has fallback |
| PyPI OIDC trusted publisher hiccup | Low | Medium | Backup: local twine upload (manual) |
| `migrate v4` blows up on TheVoidWeaver (fact_*.yml collisions) | Medium | Medium | Collision detector in M6-A: warn + suffix in archive namespace, never silent overwrite |
| Personal-data gate false positive | Low | Low | Each deny-list line documented; `--allow <term>` per-PR escape hatch |
| M6-B (7 engines one wave) loses control | Medium | Medium | writing-plans phase decomposes into sub-tasks; one engine = one atomic commit |
| Bridge-B breaks existing LGD users | Low | Medium | Keep legacy `type = "jsonl-graph"` one minor cycle; GUI prompts migration |
| 7 new schema models cause `gish init` to write too many files | Medium | Low | Template builds only the 5.1 baseline; M6 capability files lazy-created on first command use |

---

## 12. Out of Scope (Restated)

- gish daemon / HTTP API mode
- Logo / branding / landing page (M7+)
- LGD GUI redesign — bridge limited to memory source layer
- TheVoidWeaver private repo changes — dogfood stays dogfood; deny list handles leak protection
- HN / Reddit / Twitter launch (M7 distribution, separate effort)
- Business model rollout (M8 observe-first)
- Fifth CLI adapter beyond claude/gemini/codex/copilot
- Docker image, comparison blog versus mem0/letta/cognee
- Brain regions beyond 5 defaults + 4 documented extensions

---

## 13. Open Questions

To resolve during writing-plans or implementation:

| # | Question | Tentative | Decide By |
|---|---|---|---|
| O1 | Keep `ghost_in_shell` deprecation alias for how many minor versions? | 1 minor (5.1) then drop | M6-C stable bump |
| O2 | Sub-package layout: parallel to `gshell_memory/` at root, or under `packages/`? | Root parallel | M6-A start |
| O3 | LGD legacy `type = "jsonl-graph"` vs new `type = "gshell"` co-existence — how long? | At least 1 minor | Bridge-B |
| O4 | Where do M6 yml files live — flat in `memory/` or grouped subdirs? | Flat in `memory/`; SubdirRegistry allows user to declare own subdirs | M6-A model work |
| O5 | `Carryover` canonical format — markdown frontmatter vs pure yaml? | Markdown frontmatter (human-readable; matches TheVoidWeaver pattern) | M6-A model work |
| O6 | `HeartbeatConfig` default output location — inside workspace vs `~/.gish/logs/`? | Inside workspace (`memory/heartbeat_logs/`) — travels with workspace | M6-B engine work |
| O7 | LGD UI button for "migrate to gshell" needed? | No; CLI-only `lgd-agent migrate-to-gshell` suffices for now | Bridge-B |

---

## 14. References

- Ghost_In_Shell repo: https://github.com/cyhsieh817/Ghost_In_Shell
- LabGrimoire_Desktop repo: https://github.com/cyhsieh817/LabGrimoire_Desktop
- Existing v5 docs: `docs/ch.00-ch.10`
- Personal-data gate: `scripts/ci/check_no_personal.py` + `tests/forbidden_strings.txt`
- TheVoidWeaver internal spec series (private): `docs/voidweaver-specs/` (in TheVoidWeaver repo, not this one)

---

*Approved: 2026-05-24 by @cyhsieh817 (verbal sign-off across four design parts)*
*Implementation plan: see `docs/superpowers/plans/2026-05-24-gshell-memory-product-launch.md` (to be generated by writing-plans)*
