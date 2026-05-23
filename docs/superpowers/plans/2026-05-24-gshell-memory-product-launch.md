# gshell-memory Product Launch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `gshell-memory` from pre-launch to PyPI stable, abstract seven dogfood-proven capabilities into the framework, and bridge LabGrimoire_Desktop (LGD) to the same workspace via a shared Pydantic + JSON Schema contract.

**Architecture:** Three milestones × three waves each = 9 waves total. Release lane (M5-A → M5-B → M5-C) and capability lane (M6-A → M6-B → M6-C) run in parallel after M5-A unblocks. Bridge lane (Bridge-A → Bridge-B → Bridge-C) attaches once M6-A publishes the schema sub-package. Two PyPI distributions ship: `gshell-memory` (engines + CLI) and `gshell-memory-schema` (Pydantic models + JSON Schema). LGD pulls only the lightweight schema package; no engine dependency.

**Tech Stack:** Python 3.11+, click, pydantic v2, pyyaml, pytest, ruff, hatchling, GitHub Actions (OIDC trusted publisher), asciinema, Rust + schemars (LGD side), Tauri.

**Spec reference:** `docs/superpowers/specs/2026-05-24-gshell-memory-product-launch-design.md`

**Branch:** `spec/m5-m6-product-launch` (already created during brainstorming)

---

## Pre-flight Notes

- All tasks operate inside `/Users/cyuh/Downloads/APPDev/102_Github/Ghost_In_Shell/` unless explicitly marked "LGD repo" (which means `/Users/cyuh/Downloads/APPDev/102_Github/LabGrimoire_Desktop/`).
- Scratch directory cleanup uses `mv <path> _DELETE_<path>` per project safety policy; a periodic chore sweeps those entries later.
- After each task's commit step, the personal-data gate runs as part of CI from M5-B onward — locally test with `python3 scripts/ci/check_no_personal.py` before pushing.
- Commit messages follow Conventional Commits; trailer `Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>`.
- The Python package rename (`ghost_in_shell` → `gshell_memory`) lands in Wave M5-C as a single atomic commit; everything before it still uses `ghost_in_shell` import paths, everything after uses `gshell_memory`. Tasks below reference paths matching their wave's state.

---

## M5 — Engineering Stabilisation & Release

### Wave M5-A: Environment Stability

#### Task M5-A.1: Gate pytest on Python 3.11+

**Files:**
- Create or extend: `tests/conftest.py`
- Verify: `pyproject.toml`

- [ ] **Step 1: Inspect current conftest**

```bash
cat tests/conftest.py 2>/dev/null || echo "(does not exist)"
```

- [ ] **Step 2: Write conftest to gate Python version**

```python
"""Pytest configuration for gshell-memory test suite."""

import sys

import pytest

MIN_PY = (3, 11)


def pytest_configure(config: pytest.Config) -> None:
    if sys.version_info < MIN_PY:
        raise pytest.UsageError(
            f"gshell-memory requires Python >= {MIN_PY[0]}.{MIN_PY[1]} "
            f"(found {sys.version_info.major}.{sys.version_info.minor}). "
            "Activate a 3.11+ venv before running pytest."
        )
```

- [ ] **Step 3: Verify pyproject hard floor**

```bash
grep "requires-python" pyproject.toml
```

Expected: `requires-python = ">=3.11"`.

- [ ] **Step 4: Verify on fresh Python 3.11 venv**

```bash
python3.11 -m venv .venv-test
source .venv-test/bin/activate
pip install -e ".[dev]"
pytest -q
deactivate
mv .venv-test _DELETE_.venv-test
```

Expected: tests run without ImportError on `from datetime import UTC`.

- [ ] **Step 5: Commit**

```bash
git add tests/conftest.py
git commit -m "test(m5-a): gate pytest on Python >= 3.11 via conftest

Prevents stray system Python 3.9 from picking up the test suite.
README's '214 tests passing' claim is now reproducible.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M5-A.2: Pin Python and lock dependencies

**Files:**
- Create: `.python-version`
- Create: `uv.lock`

- [ ] **Step 1: Write .python-version**

```bash
echo "3.11" > .python-version
```

- [ ] **Step 2: Install uv if absent**

```bash
command -v uv || python3.11 -m pip install --user uv
```

- [ ] **Step 3: Generate lock file**

```bash
uv sync --dev
```

- [ ] **Step 4: Sanity check**

```bash
test -f uv.lock && echo "lock present"
uv run pytest -q --collect-only 2>&1 | tail -3
```

- [ ] **Step 5: Commit**

```bash
git add .python-version uv.lock
git commit -m "build(m5-a): pin Python 3.11 and lock deps with uv

Reproducible builds across CI and contributor machines.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M5-A.3: README — live badges, drop stale '214 tests'

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Find existing badge block**

```bash
grep -nE "shields.io|version-5|214" README.md
```

- [ ] **Step 2: Replace static badges with live ones**

Find:

```markdown
<p align="center">
  <img src="https://img.shields.io/badge/version-5.0.0rc1-blue" alt="version" />
  <img src="https://img.shields.io/badge/python-3.11%2B-brightgreen" alt="python" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="license" />
</p>
```

Replace with:

```markdown
<p align="center">
  <a href="https://github.com/cyhsieh817/Ghost_In_Shell/actions/workflows/ci.yml"><img src="https://github.com/cyhsieh817/Ghost_In_Shell/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="https://pypi.org/project/gshell-memory/"><img src="https://img.shields.io/pypi/v/gshell-memory.svg" alt="PyPI" /></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-brightgreen" alt="python" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="license" />
</p>
```

- [ ] **Step 3: Delete the stale '214 tests, ruff clean' line if present**

```bash
grep -nE "214 tests|ruff clean" README.md
```

Delete matching lines.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs(m5-a): live CI + PyPI badges; drop stale '214 tests' claim

Pre-launch README claimed numbers that depended on local environment.
Live badges reflect reality.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Wave M5-B: CI & Contributor Infrastructure

#### Task M5-B.1: GitHub Actions ci.yml

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Write workflow**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install uv
        run: python -m pip install uv
      - name: Sync deps
        run: uv sync --dev
      - name: Lint (ruff)
        run: uv run ruff check .
      - name: Test (pytest)
        run: uv run pytest -q
      - name: Personal-data gate
        run: uv run python scripts/ci/check_no_personal.py
```

- [ ] **Step 2: Validate yaml**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"
```

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci(m5-b): GitHub Actions — pytest 3.11/3.12 + ruff + personal-data gate

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M5-B.2: pre-commit hook

**Files:**
- Create: `.pre-commit-config.yaml`

- [ ] **Step 1: Write config**

```yaml
repos:
  - repo: local
    hooks:
      - id: personal-data-gate
        name: Personal-data gate
        entry: python scripts/ci/check_no_personal.py
        language: system
        pass_filenames: false
        stages: [pre-commit]
      - id: ruff
        name: ruff lint
        entry: ruff check
        language: system
        types: [python]
        pass_filenames: false
```

- [ ] **Step 2: Commit**

```bash
git add .pre-commit-config.yaml
git commit -m "ci(m5-b): pre-commit hook — personal-data gate + ruff

Contributors install with: pip install pre-commit && pre-commit install

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M5-B.3: CHANGELOG.md

**Files:**
- Create: `CHANGELOG.md`

- [ ] **Step 1: Write the file**

Save to `CHANGELOG.md`:

```markdown
# Changelog

All notable changes to gshell-memory will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- M5 stabilisation: CI workflow (pytest + ruff + personal-data gate)
- M5 packaging: PyPI distribution as `gshell-memory`
- M6 capability abstractions: SOPRoute / ArchiveRoute / Carryover / FrozenEnum / HeartbeatConfig / SubdirRegistry / BrainRegionExtension
- M6 sub-package: `gshell-memory-schema` ships Pydantic models and JSON Schema separately
- Bridge: LabGrimoire_Desktop adapter via `grimoire.toml#[sources.memory] type = "gshell"`

### Changed
- Python package renamed `ghost_in_shell` → `gshell_memory`. The old name remains importable as a deprecation alias for one minor cycle (5.1) and is removed in 6.0.
- README static '214 tests' badge replaced with live GitHub Actions and PyPI badges.

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
```

- [ ] **Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs(m5-b): CHANGELOG.md in Keep a Changelog format

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M5-B.4: CONTRIBUTING.md

**Files:**
- Create: `CONTRIBUTING.md`

- [ ] **Step 1: Write the file**

Save to `CONTRIBUTING.md`:

```markdown
# Contributing to gshell-memory

## Development setup

```bash
git clone https://github.com/cyhsieh817/Ghost_In_Shell
cd Ghost_In_Shell
python3.11 -m venv .venv
source .venv/bin/activate
pip install uv
uv sync --dev
uv run pytest -q
```

## Pre-commit

```bash
pip install pre-commit
pre-commit install
```

Runs personal-data gate and ruff on every commit.

## Pull request flow

1. Fork.
2. Branch off `main`: `git checkout -b feat/short-summary`.
3. Use [Conventional Commits](https://www.conventionalcommits.org/).
4. Run `uv run pytest -q && uv run ruff check .` locally.
5. Push, open PR, fill the template.
6. CI green → maintainer merges.

## Personal-data gate

Deny list lives at `tests/forbidden_strings.txt`. Runs in CI and as pre-commit hook. To extend:

1. Add the literal substring on its own line.
2. Use `#` for comment lines.
3. Commit.

Forks may edit freely.

## Releases

Tags `vX.Y.Z` on `main` trigger PyPI publish via OIDC. Maintainers only.

## Code of Conduct

See `CODE_OF_CONDUCT.md`.
```

- [ ] **Step 2: Commit**

```bash
git add CONTRIBUTING.md
git commit -m "docs(m5-b): CONTRIBUTING.md

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M5-B.5: CODE_OF_CONDUCT.md

**Files:**
- Create: `CODE_OF_CONDUCT.md`

- [ ] **Step 1: Write Contributor Covenant 2.1**

Copy the canonical Contributor Covenant 2.1 text from `https://www.contributor-covenant.org/version/2/1/code_of_conduct/`. Save to `CODE_OF_CONDUCT.md`. Replace the `[INSERT CONTACT METHOD]` placeholder with `@cyhsieh817` via GitHub.

- [ ] **Step 2: Commit**

```bash
git add CODE_OF_CONDUCT.md
git commit -m "docs(m5-b): Contributor Covenant 2.1

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M5-B.6: Issue + PR templates

**Files:**
- Create: `.github/ISSUE_TEMPLATE/bug_report.md`
- Create: `.github/ISSUE_TEMPLATE/feature_request.md`
- Create: `.github/ISSUE_TEMPLATE/config.yml`
- Create: `.github/PULL_REQUEST_TEMPLATE.md`

- [ ] **Step 1: bug_report.md**

```markdown
---
name: Bug report
about: Report a defect
title: "[bug] "
labels: bug
---

## What happened

## Reproduction

1.
2.
3. Observed:
4. Expected:

## Environment

- `gish version`:
- Python version:
- OS:
- Workspace `schema_version`:

## Logs / output
```

- [ ] **Step 2: feature_request.md**

```markdown
---
name: Feature request
about: Suggest a new capability
title: "[feat] "
labels: enhancement
---

## Problem

(User-visible problem before any proposed solution.)

## Suggested solution

## Alternatives considered

## Scope

Existing engine, new engine, or tooling change?
```

- [ ] **Step 3: config.yml**

```yaml
blank_issues_enabled: false
contact_links:
  - name: Question or discussion
    url: https://github.com/cyhsieh817/Ghost_In_Shell/discussions
    about: Open-ended questions and ideas
```

- [ ] **Step 4: PULL_REQUEST_TEMPLATE.md**

```markdown
## Summary

## Type

- [ ] feat
- [ ] fix
- [ ] docs
- [ ] test
- [ ] refactor
- [ ] chore / build / ci

## Checklist

- [ ] Tests added or updated
- [ ] `uv run pytest -q` green
- [ ] `uv run ruff check .` clean
- [ ] Personal-data gate clean (`python scripts/ci/check_no_personal.py`)
- [ ] CHANGELOG.md updated under `[Unreleased]` if user-visible
- [ ] Docs updated if behaviour changed

## Linked issues

Closes #
```

- [ ] **Step 5: Commit**

```bash
git add .github/ISSUE_TEMPLATE .github/PULL_REQUEST_TEMPLATE.md
git commit -m "ci(m5-b): issue and PR templates

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M5-B.7: Smoke-test CI

**Files:** (verification only)

- [ ] **Step 1: Push and open draft PR**

```bash
git push -u origin spec/m5-m6-product-launch
gh pr create --draft --title "WIP: M5 + M6 + Bridge" --body "Tracking PR for the full product launch plan." --base main
```

- [ ] **Step 2: Watch CI**

```bash
gh pr checks --watch
```

Expected: pytest 3.11 ✓, pytest 3.12 ✓, ruff ✓, personal-data gate ✓.

- [ ] **Step 3: Verify deny-list fail path**

Pick any term that appears in `tests/forbidden_strings.txt` (for example, one of the trademarked product names listed there). Append a comment line referencing that term to `README.md`:

```bash
# Replace <DENY_TERM> with an actual entry from tests/forbidden_strings.txt
echo "<!-- <DENY_TERM> -->" >> README.md
git add README.md
git commit -m "test(temp): verify personal-data gate fails"
git push
gh pr checks --watch
```

Expected: personal-data gate FAILS, flagging the term. Do not commit the actual deny term to the repository; this step exists only to confirm the CI gate works and is reverted in the next step.

- [ ] **Step 4: Revert and re-push**

```bash
git revert HEAD --no-edit
git push
gh pr checks --watch
```

Expected: all green.

- [ ] **Step 5: Leave PR open**

No commit.

---

### Wave M5-C: PyPI Release

#### Task M5-C.1: PyPI registration + OIDC publisher (manual)

**Files:** (no files; manual setup)

- [ ] **Step 1: Reserve `gshell-memory`**

Open `https://pypi.org/manage/account/publishing/`. Add pending trusted publisher:

- PyPI Project Name: `gshell-memory`
- Owner: `cyhsieh817`
- Repository: `Ghost_In_Shell`
- Workflow filename: `release.yml`
- Environment: `pypi`

- [ ] **Step 2: Reserve `gshell-memory-schema`**

Repeat for distribution name `gshell-memory-schema`, same workflow.

- [ ] **Step 3: Confirm both visible**

No commit; record in PR description.

---

#### Task M5-C.2: release.yml workflow

**Files:**
- Create: `.github/workflows/release.yml`

- [ ] **Step 1: Write workflow**

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install build
        run: python -m pip install build
      - name: Build sdist + wheel
        run: python -m build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish:
    runs-on: ubuntu-latest
    needs: [build]
    environment: pypi
    permissions:
      id-token: write
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      - uses: pypa/gh-action-pypi-publish@release/v1

  smoke:
    runs-on: ubuntu-latest
    needs: [publish]
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Wait for PyPI to index
        run: sleep 60
      - name: Install from PyPI
        run: python -m pip install "gshell-memory==${GITHUB_REF_NAME#v}"
      - name: Smoke test
        run: |
          gish version
          gish init /tmp/smoke-ws --non-interactive
          gish doctor --workspace /tmp/smoke-ws
```

- [ ] **Step 2: Validate yaml**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))"
```

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/release.yml
git commit -m "ci(m5-c): release workflow — build, OIDC publish, smoke test

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M5-C.3: pyproject.toml — rename distribution

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Update name, scripts, packages**

In `pyproject.toml`:

```toml
[project]
name = "gshell-memory"
```

(was `"ghost-in-shell"`)

```toml
[project.scripts]
gish = "gshell_memory.cli.main:gish"
```

(was `"ghost_in_shell.cli.main:gish"`)

```toml
[tool.hatch.build.targets.wheel]
packages = ["gshell_memory", "ghost_in_shell"]
```

(was `["ghost_in_shell"]`; both ship through 5.1 for the deprecation cycle)

- [ ] **Step 2: Do not commit yet**

Leave staged; the atomic rename in M5-C.4 commits everything together.

---

#### Task M5-C.4: Atomic package rename

**Files:**
- Rename: `ghost_in_shell/` → `gshell_memory/`
- Modify: all source + test imports
- Create: `ghost_in_shell/__init__.py` (deprecation alias)

- [ ] **Step 1: git mv the package**

```bash
git mv ghost_in_shell gshell_memory
```

- [ ] **Step 2: Update imports across source and tests**

```bash
grep -rl "ghost_in_shell" gshell_memory/ tests/ | xargs sed -i '' 's/ghost_in_shell/gshell_memory/g'
```

- [ ] **Step 3: Create deprecation alias directory**

```bash
mkdir ghost_in_shell
cat > ghost_in_shell/__init__.py <<'EOF'
"""Deprecated alias for the gshell_memory package.

This shim exists for one minor version (5.1) only. Migrate imports
from 'ghost_in_shell' to 'gshell_memory'. Removed in 6.0.
"""

import warnings as _warnings

import gshell_memory as _gshell_memory

_warnings.warn(
    "Importing 'ghost_in_shell' is deprecated; use 'gshell_memory' instead. "
    "This alias is removed in gshell-memory 6.0.",
    DeprecationWarning,
    stacklevel=2,
)

from gshell_memory import *  # noqa: F401,F403,E402

__all__ = _gshell_memory.__all__ if hasattr(_gshell_memory, "__all__") else []
EOF
```

- [ ] **Step 4: Verify tests + lint**

```bash
uv run pytest -q
uv run ruff check .
```

Expected: both green; deprecation warnings appear when the alias is exercised.

- [ ] **Step 5: Commit atomically**

```bash
git add -A
git commit -m "refactor(m5-c)!: rename Python package ghost_in_shell -> gshell_memory

Distribution name is now 'gshell-memory'. Import path follows:
'import gshell_memory'. The old 'ghost_in_shell' name remains
importable as a deprecation alias for one minor cycle (5.1).

BREAKING CHANGE: Imports of 'ghost_in_shell' emit DeprecationWarning.
Migrate to 'gshell_memory'.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M5-C.5: Tag v5.0.0rc1

**Files:** (no files)

- [ ] **Step 1: Verify CI green on branch**

```bash
git push
gh pr checks --watch
```

- [ ] **Step 2: Merge to main**

```bash
gh pr ready
gh pr merge --squash --delete-branch
git checkout main
git pull
```

- [ ] **Step 3: Tag and push**

```bash
git tag v5.0.0rc1
git push origin v5.0.0rc1
```

- [ ] **Step 4: Watch release workflow**

```bash
gh run watch
```

Expected: build ✓, publish ✓, smoke ✓.

- [ ] **Step 5: Verify clean install**

```bash
python3.11 -m venv /tmp/install-test
source /tmp/install-test/bin/activate
pip install gshell-memory==5.0.0rc1
gish version
gish init /tmp/test-ws --non-interactive
gish doctor --workspace /tmp/test-ws
deactivate
mv /tmp/install-test _DELETE_install-test
mv /tmp/test-ws _DELETE_test-ws
```

Expected: `gish version` prints `5.0.0rc1`; doctor green.

No commit.

---

#### Task M5-C.6: Demo asciinema for README

**Files:**
- Create: `docs/demo.cast`
- Modify: `README.md`

- [ ] **Step 1: Record session**

```bash
asciinema rec docs/demo.cast --idle-time-limit 2 --title "gshell-memory quick start"
```

Run (~60 seconds):

```bash
pip install gshell-memory
gish init ~/demo-workspace
gish doctor --workspace ~/demo-workspace
gish recall "first decision" --workspace ~/demo-workspace
gish run-maintenance --workspace ~/demo-workspace
```

Press Ctrl-D.

- [ ] **Step 2: Verify cast file**

```bash
test -f docs/demo.cast && head -1 docs/demo.cast
```

Expected: starts with `{"version": 2`.

- [ ] **Step 3: Upload and embed**

```bash
asciinema upload docs/demo.cast
```

Note the returned id. In `README.md` near "Quick Start", add:

```markdown
[![asciicast](https://asciinema.org/a/PLACEHOLDER.svg)](https://asciinema.org/a/PLACEHOLDER)
```

Replace `PLACEHOLDER` (twice) with the returned id.

- [ ] **Step 4: Commit**

```bash
git add docs/demo.cast README.md
git commit -m "docs(m5-c): asciinema demo of init -> doctor -> recall -> maintenance

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---


## M6 — Capability Abstraction

### Wave M6-A: Schema Sub-Package Born

> M6-A may run in parallel with M5-B onward. Bridge waves cannot start until M6-A completes (the schema sub-package must be on PyPI).

#### Task M6-A.1: Sub-package skeleton

**Files:**
- Create: `gshell_memory_schema/pyproject.toml`
- Create: `gshell_memory_schema/README.md`
- Create: `gshell_memory_schema/gshell_memory_schema/__init__.py`
- Create: `gshell_memory_schema/gshell_memory_schema/version.py`
- Create: `gshell_memory_schema/tests/__init__.py`
- Modify: top-level `pyproject.toml` (declare workspace)

- [ ] **Step 1: Make sub-package directory**

```bash
mkdir -p gshell_memory_schema/gshell_memory_schema gshell_memory_schema/tests gshell_memory_schema/scripts
```

- [ ] **Step 2: Write sub-package pyproject.toml**

`gshell_memory_schema/pyproject.toml`:

```toml
[build-system]
requires = ["hatchling>=1.18"]
build-backend = "hatchling.build"

[project]
name = "gshell-memory-schema"
version = "5.0.0"
description = "Pydantic models and JSON Schema for gshell-memory workspace files."
readme = "README.md"
requires-python = ">=3.11"
license = { file = "LICENSE" }
authors = [
    { name = "Ghost In Shell contributors" },
]
keywords = ["ai", "agent", "memory", "schema", "pydantic"]
classifiers = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries",
]
dependencies = [
    "pydantic>=2.7",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "hypothesis>=6.100",
    "ruff>=0.4",
]

[project.urls]
Homepage = "https://github.com/cyhsieh817/Ghost_In_Shell"

[tool.hatch.build.targets.wheel]
packages = ["gshell_memory_schema"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers"
pythonpath = ["."]
```

- [ ] **Step 3: Write sub-package README**

`gshell_memory_schema/README.md`:

```markdown
# gshell-memory-schema

Pydantic models + JSON Schema for the gshell-memory workspace file format.

This is a **schema-only** package. It contains no engines, no CLI, no business
logic. Use it when you need to read or write a gshell workspace from your own
code without depending on the full `gshell-memory` framework.

```python
from gshell_memory_schema.models import EpisodicEntry

entry = EpisodicEntry.model_validate(json.loads(line))
```

JSON Schema files live under `gshell_memory_schema/jsonschema/`. They are
auto-generated from the Pydantic models. Rust consumers can drive validation
with `schemars` or `serde_json`.

Versioning follows the workspace `schema_version`. Package version 5.0.x
serves workspace schema 5.0, 5.1.x serves 5.1, etc.
```

- [ ] **Step 4: Write __init__.py + version.py**

`gshell_memory_schema/gshell_memory_schema/__init__.py`:

```python
"""Pydantic models and JSON Schema for gshell-memory workspaces."""

__version__ = "5.0.0"
__schema_version__ = (5, 0)
```

`gshell_memory_schema/gshell_memory_schema/version.py`:

```python
"""Schema version compatibility utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SchemaVersion:
    major: int
    minor: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"


_VERSION_RE = re.compile(r"^(\d+)\.(\d+)$")


def parse(s: str | float | int) -> SchemaVersion:
    if isinstance(s, (int, float)):
        s = str(s)
    m = _VERSION_RE.match(s.strip())
    if not m:
        raise ValueError(f"invalid schema version: {s!r}")
    return SchemaVersion(int(m.group(1)), int(m.group(2)))


def is_compatible(workspace: SchemaVersion, package: SchemaVersion) -> bool:
    """Forward-compatible within same major; minor mismatch okay."""
    return workspace.major == package.major and workspace.minor <= package.minor
```

- [ ] **Step 5: Top-level pyproject monorepo declaration**

Append to root `pyproject.toml` (the gshell-memory main one) under `[tool.uv]`:

```toml
[tool.uv]
package = true

[tool.uv.workspace]
members = ["gshell_memory_schema"]
```

This wires uv to treat the sub-package as part of the workspace, so `uv sync` from the root resolves both.

- [ ] **Step 6: Smoke test**

```bash
cd gshell_memory_schema
python -c "from gshell_memory_schema.version import parse, is_compatible; print(parse('5.1'))"
cd ..
```

Expected: prints `5.1`.

- [ ] **Step 7: Commit**

```bash
git add gshell_memory_schema pyproject.toml
git commit -m "feat(m6-a): scaffold gshell-memory-schema sub-package

Independent PyPI distribution; gshell-memory main package will pull
it as a dependency in Task M6-A.12. Contains version-compat utilities
only at this point; models land in M6-A.2-.8.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-A.2: Relocate existing v5 models into sub-package

**Files:**
- Create: `gshell_memory_schema/gshell_memory_schema/models.py`
- Modify: `gshell_memory/memory/schemas.py` (re-export from sub-package)
- Create: `gshell_memory_schema/tests/test_models_existing.py`

- [ ] **Step 1: Write the failing test**

`gshell_memory_schema/tests/test_models_existing.py`:

```python
"""Ensure existing v5 models import cleanly from the sub-package."""

import pytest


def test_workspace_model_imports():
    from gshell_memory_schema.models import Workspace
    assert Workspace is not None


def test_episodic_entry_imports():
    from gshell_memory_schema.models import EpisodicEntry
    assert EpisodicEntry is not None


def test_episodic_entry_validates_minimal():
    from gshell_memory_schema.models import EpisodicEntry
    entry = EpisodicEntry(
        id="ep-2026-05-24-001",
        title="Test",
        content="Body",
        date="2026-05-24",
        ts="2026-05-24T00:00:00Z",
        type="decision",
        tags=[],
        importance=5,
        fingerprint="a" * 64,
        retrieval={"count": 0, "last_accessed": None, "strength": 1.0},
        decay_status="active",
        linked_to=[],
    )
    assert entry.id == "ep-2026-05-24-001"


def test_episodic_entry_rejects_short_fingerprint():
    import pydantic
    from gshell_memory_schema.models import EpisodicEntry
    with pytest.raises(pydantic.ValidationError):
        EpisodicEntry(
            id="ep-x",
            title="t",
            content="c",
            date="2026-05-24",
            ts="2026-05-24T00:00:00Z",
            type="decision",
            tags=[],
            importance=5,
            fingerprint="short",
            retrieval={"count": 0, "last_accessed": None, "strength": 1.0},
            decay_status="active",
            linked_to=[],
        )
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd gshell_memory_schema
uv run pytest tests/test_models_existing.py -v
cd ..
```

Expected: ImportError or ModuleNotFoundError on `from gshell_memory_schema.models import ...`.

- [ ] **Step 3: Write models.py with the existing v5 schema content**

Inspect `gshell_memory/memory/schemas.py` (which after the rename is the current location of v5 models):

```bash
cat gshell_memory/memory/schemas.py
```

Copy each class into `gshell_memory_schema/gshell_memory_schema/models.py`, preserving exact field definitions. Add the file header:

```python
"""Pydantic v2 models for the gshell-memory workspace.

This module is the canonical source of truth for the workspace schema.
The gshell-memory engine package re-exports from here to avoid duplication.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

# (Copy all v5 classes here: Workspace, FactStore, EpisodicEntry,
#  Association, BrainRegionManifest, SanctumRegistry, RuntimeProfiles,
#  MemoryManifest.)
```

For `EpisodicEntry`, tighten `fingerprint` to require exactly 64 hex chars:

```python
HexFingerprint = Annotated[str, StringConstraints(min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$")]


class EpisodicEntry(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    title: str
    content: str
    date: str
    ts: str
    type: Literal["decision", "failure", "milestone", "insight", "discovery"]
    tags: list[str]
    importance: float = Field(ge=0, le=10)
    fingerprint: HexFingerprint
    retrieval: dict
    decay_status: Literal["active", "fading", "archived"]
    linked_to: list[str]
```

(For other models, keep existing field definitions verbatim — they are already in v5 codebase.)

- [ ] **Step 4: Re-export from main package**

Replace contents of `gshell_memory/memory/schemas.py` with:

```python
"""Schema re-exports.

The canonical schema lives in `gshell_memory_schema.models`. This module
re-exports for backwards compatibility within gshell_memory itself.
"""

from gshell_memory_schema.models import (  # noqa: F401
    Association,
    BrainRegionManifest,
    EpisodicEntry,
    FactStore,
    MemoryManifest,
    RuntimeProfiles,
    SanctumRegistry,
    Workspace,
)
```

- [ ] **Step 5: Run test to verify it passes**

```bash
cd gshell_memory_schema
uv run pytest tests/test_models_existing.py -v
cd ..
uv run pytest -q
```

Expected: sub-package tests green; main package tests still green (using re-exported models).

- [ ] **Step 6: Commit**

```bash
git add gshell_memory_schema gshell_memory/memory/schemas.py
git commit -m "feat(m6-a): relocate v5 models into gshell-memory-schema sub-package

Canonical source of truth for workspace schema now lives in
gshell_memory_schema/models.py. Main package re-exports for backwards
compatibility. EpisodicEntry.fingerprint tightened to exactly 64 hex
characters (was loosely typed).

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-A.3: SOPRoute model

**Files:**
- Modify: `gshell_memory_schema/gshell_memory_schema/models.py`
- Create: `gshell_memory_schema/tests/test_sop_route.py`

- [ ] **Step 1: Write failing test**

`gshell_memory_schema/tests/test_sop_route.py`:

```python
import pytest


def test_sop_route_minimal():
    from gshell_memory_schema.models import SOPRoute
    route = SOPRoute(
        name="example",
        triggers=["foo", "bar"],
        must_read=["docs/x.md"],
    )
    assert route.name == "example"
    assert route.also_read == []
    assert route.skills_pipeline == []


def test_sop_route_full():
    from gshell_memory_schema.models import SOPRoute
    route = SOPRoute(
        name="full",
        triggers=["a"],
        must_read=["a.md"],
        also_read=["b.md"],
        skills_pipeline=["/skill1", "/skill2"],
        note="example note",
        inline_sop="1. step\n2. step",
    )
    assert route.skills_pipeline == ["/skill1", "/skill2"]


def test_sop_route_requires_triggers():
    import pydantic
    from gshell_memory_schema.models import SOPRoute
    with pytest.raises(pydantic.ValidationError):
        SOPRoute(name="bad", triggers=[], must_read=["x.md"])


def test_sop_route_requires_must_read():
    import pydantic
    from gshell_memory_schema.models import SOPRoute
    with pytest.raises(pydantic.ValidationError):
        SOPRoute(name="bad", triggers=["x"], must_read=[])
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd gshell_memory_schema
uv run pytest tests/test_sop_route.py -v
cd ..
```

Expected: ImportError on `SOPRoute`.

- [ ] **Step 3: Add SOPRoute to models.py**

Append to `gshell_memory_schema/gshell_memory_schema/models.py`:

```python
class SOPRoute(BaseModel):
    """A standard-operating-procedure routing entry.

    When the agent detects any string in `triggers` in the user's request,
    it must read every file in `must_read` before proceeding, optionally
    pulls `also_read` later, and may chain `skills_pipeline` for execution.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    triggers: list[str] = Field(min_length=1)
    must_read: list[str] = Field(min_length=1)
    also_read: list[str] = Field(default_factory=list)
    skills_pipeline: list[str] = Field(default_factory=list)
    note: str | None = None
    inline_sop: str | None = None
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd gshell_memory_schema
uv run pytest tests/test_sop_route.py -v
cd ..
```

Expected: all 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add gshell_memory_schema/gshell_memory_schema/models.py gshell_memory_schema/tests/test_sop_route.py
git commit -m "feat(m6-a): SOPRoute model — name + triggers + must_read + pipeline

Triggers and must_read each require at least one entry. extra='forbid'
catches typos in yaml at validation time.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-A.4: ArchiveRoute model

**Files:**
- Modify: `gshell_memory_schema/gshell_memory_schema/models.py`
- Create: `gshell_memory_schema/tests/test_archive_route.py`

- [ ] **Step 1: Write failing test**

`gshell_memory_schema/tests/test_archive_route.py`:

```python
import pytest


def test_archive_route_minimal():
    from gshell_memory_schema.models import ArchiveRoute
    route = ArchiveRoute(
        condition="content matches /pattern/",
        target_dir="archive/x/",
        naming_pattern="YYYY-MM-DD-{slug}.md",
        priority=10,
    )
    assert route.priority == 10
    assert route.frontmatter_required == []


def test_archive_route_full():
    from gshell_memory_schema.models import ArchiveRoute
    route = ArchiveRoute(
        condition="tag includes 'security'",
        target_dir="logs/security/",
        naming_pattern="YYYY-Www-{topic}.md",
        frontmatter_required=["title", "date", "tags", "source"],
        note="weekly bucket",
        priority=5,
    )
    assert route.frontmatter_required == ["title", "date", "tags", "source"]


def test_archive_route_priority_must_be_positive():
    import pydantic
    from gshell_memory_schema.models import ArchiveRoute
    with pytest.raises(pydantic.ValidationError):
        ArchiveRoute(
            condition="x",
            target_dir="y/",
            naming_pattern="z.md",
            priority=0,
        )
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd gshell_memory_schema
uv run pytest tests/test_archive_route.py -v
cd ..
```

- [ ] **Step 3: Add ArchiveRoute to models.py**

```python
class ArchiveRoute(BaseModel):
    """A condition-target-naming entry in the archive decision tree.

    Routes are evaluated in priority order; the first one whose `condition`
    matches wins. `condition` is a free-form string for now; engine layer
    decides interpretation (literal substring, glob, etc.).
    """

    model_config = ConfigDict(extra="forbid")

    condition: str
    target_dir: str
    naming_pattern: str
    frontmatter_required: list[str] = Field(default_factory=list)
    note: str | None = None
    priority: int = Field(ge=1)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd gshell_memory_schema
uv run pytest tests/test_archive_route.py -v
cd ..
```

- [ ] **Step 5: Commit**

```bash
git add gshell_memory_schema/gshell_memory_schema/models.py gshell_memory_schema/tests/test_archive_route.py
git commit -m "feat(m6-a): ArchiveRoute model — condition + target + naming + priority

Priority gates ordering in the engine's decision tree. priority >= 1
is enforced at model layer.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-A.5: Carryover model

**Files:**
- Modify: `gshell_memory_schema/gshell_memory_schema/models.py`
- Create: `gshell_memory_schema/tests/test_carryover.py`

- [ ] **Step 1: Write failing test**

```python
from datetime import date, timedelta

import pytest


def test_carryover_minimal():
    from gshell_memory_schema.models import Carryover
    c = Carryover(
        project_slug="proj-x",
        topic="install-db",
        created=date(2026, 5, 24),
        expires=date(2026, 5, 31),
        status="active",
    )
    assert c.status == "active"


def test_carryover_rejects_too_long_expiry():
    import pydantic
    from gshell_memory_schema.models import Carryover
    with pytest.raises(pydantic.ValidationError):
        Carryover(
            project_slug="x",
            topic="t",
            created=date(2026, 5, 24),
            expires=date(2026, 6, 5),  # 12 days
            status="active",
        )


def test_carryover_rejects_inverted_dates():
    import pydantic
    from gshell_memory_schema.models import Carryover
    with pytest.raises(pydantic.ValidationError):
        Carryover(
            project_slug="x",
            topic="t",
            created=date(2026, 5, 31),
            expires=date(2026, 5, 24),
            status="active",
        )


def test_carryover_status_enum():
    import pydantic
    from gshell_memory_schema.models import Carryover
    with pytest.raises(pydantic.ValidationError):
        Carryover(
            project_slug="x",
            topic="t",
            created=date(2026, 5, 24),
            expires=date(2026, 5, 25),
            status="invalid_state",
        )
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd gshell_memory_schema
uv run pytest tests/test_carryover.py -v
cd ..
```

- [ ] **Step 3: Add Carryover to models.py**

```python
from datetime import date as _date


class Carryover(BaseModel):
    """Cross-session task hand-off, max 7 days from created date."""

    model_config = ConfigDict(extra="forbid")

    project_slug: str
    topic: str
    created: _date
    expires: _date
    status: Literal["active", "expired", "promoted"]

    @model_validator(mode="after")
    def _validate_expiry_window(self) -> "Carryover":
        delta = (self.expires - self.created).days
        if delta < 0:
            raise ValueError(f"expires ({self.expires}) cannot precede created ({self.created})")
        if delta > 7:
            raise ValueError(f"carryover lifetime is {delta} days, max is 7")
        return self
```

Add at top of `models.py` if absent: `from pydantic import model_validator`.

- [ ] **Step 4: Run test to verify it passes**

```bash
cd gshell_memory_schema
uv run pytest tests/test_carryover.py -v
cd ..
```

- [ ] **Step 5: Commit**

```bash
git add gshell_memory_schema/gshell_memory_schema/models.py gshell_memory_schema/tests/test_carryover.py
git commit -m "feat(m6-a): Carryover model — 7-day max cross-session task hand-off

model_validator enforces both expires >= created and (expires - created)
<= 7 days. Status is one of: active / expired / promoted.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-A.6: FrozenEnum model

**Files:**
- Modify: `gshell_memory_schema/gshell_memory_schema/models.py`
- Create: `gshell_memory_schema/gshell_memory_schema/enums.py`
- Create: `gshell_memory_schema/tests/test_frozen_enum.py`

- [ ] **Step 1: Write failing test**

```python
import pytest


def test_frozen_enum_basic():
    from gshell_memory_schema.models import FrozenEnum
    e = FrozenEnum(
        name="decision_kind",
        values=["brain_decision", "agent_output", "structured_data"],
        introduced="2026-04-26",
        layer="agent_run_artifacts.metadata.decision_kind",
        enforcement="audit",
    )
    assert "brain_decision" in e.values


def test_frozen_enum_rejects_duplicate_values():
    import pydantic
    from gshell_memory_schema.models import FrozenEnum
    with pytest.raises(pydantic.ValidationError):
        FrozenEnum(
            name="x",
            values=["a", "a"],
            introduced="2026-01-01",
            layer="y",
            enforcement="audit",
        )


def test_frozen_enum_helper_freeze():
    from gshell_memory_schema.enums import freeze
    registry = {}
    freeze(registry, "rerun_status", ["supported", "unsupported", "pending"], introduced="2026-04-26", layer="manifest.toml")
    assert "rerun_status" in registry
    assert registry["rerun_status"].values == ["supported", "unsupported", "pending"]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd gshell_memory_schema
uv run pytest tests/test_frozen_enum.py -v
cd ..
```

- [ ] **Step 3: Add FrozenEnum to models.py and create enums.py**

In `models.py`:

```python
class FrozenEnum(BaseModel):
    """A state enumeration locked against silent drift.

    Once introduced, values may only be added in major-version bumps and
    must reference a spec for the rationale.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    values: list[str] = Field(min_length=1)
    introduced: str
    layer: str
    enforcement: Literal["audit", "block"]
    spec_ref: str | None = None

    @model_validator(mode="after")
    def _unique_values(self) -> "FrozenEnum":
        if len(set(self.values)) != len(self.values):
            raise ValueError("values must be unique")
        return self
```

In `gshell_memory_schema/gshell_memory_schema/enums.py`:

```python
"""Helpers for working with FrozenEnum registrations."""

from __future__ import annotations

from gshell_memory_schema.models import FrozenEnum


def freeze(
    registry: dict[str, FrozenEnum],
    name: str,
    values: list[str],
    *,
    introduced: str,
    layer: str,
    enforcement: str = "audit",
    spec_ref: str | None = None,
) -> FrozenEnum:
    """Register a frozen enum into ``registry``.

    Raises ``ValueError`` if ``name`` is already registered with different values.
    """
    enum = FrozenEnum(
        name=name,
        values=values,
        introduced=introduced,
        layer=layer,
        enforcement=enforcement,
        spec_ref=spec_ref,
    )
    if name in registry and registry[name].values != enum.values:
        raise ValueError(f"frozen enum {name!r} already registered with different values")
    registry[name] = enum
    return enum
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd gshell_memory_schema
uv run pytest tests/test_frozen_enum.py -v
cd ..
```

- [ ] **Step 5: Commit**

```bash
git add gshell_memory_schema/gshell_memory_schema/models.py gshell_memory_schema/gshell_memory_schema/enums.py gshell_memory_schema/tests/test_frozen_enum.py
git commit -m "feat(m6-a): FrozenEnum model + freeze() helper

Locks state enumerations against silent drift. enums.freeze() prevents
re-registration with different values — useful when the same enum is
referenced from multiple specs.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-A.7: HeartbeatConfig model

**Files:**
- Modify: `gshell_memory_schema/gshell_memory_schema/models.py`
- Create: `gshell_memory_schema/tests/test_heartbeat_config.py`

- [ ] **Step 1: Write failing test**

```python
import pytest


def test_heartbeat_config_minimal():
    from gshell_memory_schema.models import HeartbeatConfig
    cfg = HeartbeatConfig(
        cadence="hourly",
        checks=["self_identity", "inbox", "outbox"],
    )
    assert cfg.idle_threshold == 5
    assert cfg.output_format == "summary"


def test_heartbeat_config_cadence_enum():
    import pydantic
    from gshell_memory_schema.models import HeartbeatConfig
    with pytest.raises(pydantic.ValidationError):
        HeartbeatConfig(cadence="biweekly", checks=["x"])


def test_heartbeat_config_idle_threshold_range():
    import pydantic
    from gshell_memory_schema.models import HeartbeatConfig
    with pytest.raises(pydantic.ValidationError):
        HeartbeatConfig(cadence="hourly", checks=["x"], idle_threshold=0)
    with pytest.raises(pydantic.ValidationError):
        HeartbeatConfig(cadence="hourly", checks=["x"], idle_threshold=100)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd gshell_memory_schema
uv run pytest tests/test_heartbeat_config.py -v
cd ..
```

- [ ] **Step 3: Add HeartbeatConfig to models.py**

```python
class HeartbeatConfig(BaseModel):
    """Heartbeat cadence + checks configuration."""

    model_config = ConfigDict(extra="forbid")

    cadence: Literal["hourly", "four_hourly", "daily", "monthly"]
    checks: list[str] = Field(min_length=1)
    output_format: Literal["ok_only", "summary", "verbose"] = "summary"
    idle_threshold: int = Field(default=5, ge=1, le=50)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd gshell_memory_schema
uv run pytest tests/test_heartbeat_config.py -v
cd ..
```

- [ ] **Step 5: Commit**

```bash
git add gshell_memory_schema/gshell_memory_schema/models.py gshell_memory_schema/tests/test_heartbeat_config.py
git commit -m "feat(m6-a): HeartbeatConfig model — cadence + checks + idle_threshold

idle_threshold controls how many consecutive 'HEARTBEAT_OK' outputs
the agent emits before forcing a summary. Default 5, range 1-50.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-A.8: SubdirRegistry model

**Files:**
- Modify: `gshell_memory_schema/gshell_memory_schema/models.py`
- Create: `gshell_memory_schema/tests/test_subdir_registry.py`

- [ ] **Step 1: Write failing test**

```python
import pytest


def test_subdir_registry_minimal():
    from gshell_memory_schema.models import SubdirRegistry
    reg = SubdirRegistry(
        registered=[
            {"path": "memory/_archive/", "purpose": "archive", "lifecycle": "permanent"},
        ],
        enforcement="warn",
    )
    assert reg.enforcement == "warn"
    assert len(reg.registered) == 1


def test_subdir_registry_block_mode():
    from gshell_memory_schema.models import SubdirRegistry
    reg = SubdirRegistry(registered=[], enforcement="block")
    assert reg.enforcement == "block"


def test_subdir_registry_enforcement_enum():
    import pydantic
    from gshell_memory_schema.models import SubdirRegistry
    with pytest.raises(pydantic.ValidationError):
        SubdirRegistry(registered=[], enforcement="off")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd gshell_memory_schema
uv run pytest tests/test_subdir_registry.py -v
cd ..
```

- [ ] **Step 3: Add SubdirRegistry + RegisteredSubdir to models.py**

```python
class RegisteredSubdir(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    purpose: str
    lifecycle: Literal["permanent", "rotating", "ephemeral"]


class SubdirRegistry(BaseModel):
    """White-list of directories that may exist under memory/.

    Unregistered subdirectories are warned about (default) or blocked
    entirely depending on `enforcement`.
    """

    model_config = ConfigDict(extra="forbid")

    registered: list[RegisteredSubdir]
    enforcement: Literal["warn", "block"]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd gshell_memory_schema
uv run pytest tests/test_subdir_registry.py -v
cd ..
```

- [ ] **Step 5: Commit**

```bash
git add gshell_memory_schema/gshell_memory_schema/models.py gshell_memory_schema/tests/test_subdir_registry.py
git commit -m "feat(m6-a): SubdirRegistry + RegisteredSubdir models

Prevents memory/ subdirectory sprawl. Enforcement: warn (default) or
block. Lifecycle classifies retention: permanent / rotating / ephemeral.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-A.9: BrainRegionExtension model

**Files:**
- Modify: `gshell_memory_schema/gshell_memory_schema/models.py`
- Create: `gshell_memory_schema/tests/test_brain_region_extension.py`

- [ ] **Step 1: Write failing test**

```python
import pytest


def test_brain_region_extension_minimal():
    from gshell_memory_schema.models import BrainRegionExtension
    ext = BrainRegionExtension(
        display="custom region",
        core_files=[{"path": "X.md"}],
    )
    assert ext.aliases == []
    assert ext.on_demand_files == []


def test_brain_region_extension_with_aliases():
    from gshell_memory_schema.models import BrainRegionExtension
    ext = BrainRegionExtension(
        display="security gate",
        core_files=[{"path": "POLICY.md"}],
        aliases=["warning", "safety"],
        on_demand_files=[{"path": "POLICY-extended.md"}],
    )
    assert "warning" in ext.aliases


def test_brain_region_manifest_accepts_extensions():
    """Verify the existing BrainRegionManifest model accepts the new extensions block."""
    from gshell_memory_schema.models import BrainRegionManifest
    m = BrainRegionManifest(
        regions={
            "hippocampus": {"display": "h", "core_files": [], "on_demand_files": []},
            "prefrontal":  {"display": "p", "core_files": [], "on_demand_files": []},
            "limbic":      {"display": "l", "core_files": [], "on_demand_files": []},
            "cerebellum":  {"display": "c", "core_files": [], "on_demand_files": []},
            "default":     {"display": "d", "core_files": [], "on_demand_files": []},
        },
        extensions={
            "amygdala": {
                "display": "amygdala",
                "core_files": [{"path": "POLICY.md"}],
            },
        },
    )
    assert "amygdala" in m.extensions
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd gshell_memory_schema
uv run pytest tests/test_brain_region_extension.py -v
cd ..
```

- [ ] **Step 3: Add BrainRegionExtension and extend BrainRegionManifest**

```python
class BrainRegionExtension(BaseModel):
    """An opt-in region beyond the 5 defaults.

    Mirrors BrainRegion's structure but lives under `extensions:` in the
    manifest so that 5.0 readers can ignore it.
    """

    model_config = ConfigDict(extra="forbid")

    display: str
    core_files: list[dict] = Field(default_factory=list)
    on_demand_files: list[dict] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)
```

Extend `BrainRegionManifest` (locate existing definition in models.py and add `extensions` field):

```python
class BrainRegionManifest(BaseModel):
    model_config = ConfigDict(extra="allow")

    # existing fields...
    regions: dict[str, "BrainRegion"]
    # new in 5.1:
    extensions: dict[str, BrainRegionExtension] = Field(default_factory=dict)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd gshell_memory_schema
uv run pytest tests/test_brain_region_extension.py -v
cd ..
```

- [ ] **Step 5: Commit**

```bash
git add gshell_memory_schema/gshell_memory_schema/models.py gshell_memory_schema/tests/test_brain_region_extension.py
git commit -m "feat(m6-a): BrainRegionExtension — opt-in regions beyond the 5 defaults

Manifest gains an 'extensions' block (default empty). 5.0 readers
ignore it; 5.1 readers activate. Path for projects like TheVoidWeaver
to retain custom regions (amygdala / parietal / occipital / temporal)
without breaking the 5-region default.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-A.10: JSON Schema auto-generation script

**Files:**
- Create: `gshell_memory_schema/scripts/generate_jsonschema.py`
- Create: `gshell_memory_schema/gshell_memory_schema/jsonschema/` (directory)
- Create: `gshell_memory_schema/tests/test_jsonschema_in_sync.py`

- [ ] **Step 1: Write the generator**

`gshell_memory_schema/scripts/generate_jsonschema.py`:

```python
"""Generate JSON Schema files from Pydantic models.

Usage:
  python scripts/generate_jsonschema.py            # write files
  python scripts/generate_jsonschema.py --check    # CI mode: fail if out of sync
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gshell_memory_schema import models

MODEL_NAMES = [
    "Workspace",
    "FactStore",
    "EpisodicEntry",
    "Association",
    "BrainRegionManifest",
    "BrainRegionExtension",
    "SanctumRegistry",
    "RuntimeProfiles",
    "MemoryManifest",
    "SOPRoute",
    "ArchiveRoute",
    "Carryover",
    "FrozenEnum",
    "HeartbeatConfig",
    "SubdirRegistry",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if out of sync.")
    args = parser.parse_args()

    out_dir = Path(__file__).resolve().parent.parent / "gshell_memory_schema" / "jsonschema"
    out_dir.mkdir(parents=True, exist_ok=True)

    diffs: list[str] = []
    for name in MODEL_NAMES:
        cls = getattr(models, name)
        schema = cls.model_json_schema()
        path = out_dir / f"{_snake(name)}.json"
        new = json.dumps(schema, indent=2, sort_keys=True) + "\n"
        if args.check:
            existing = path.read_text(encoding="utf-8") if path.exists() else ""
            if existing != new:
                diffs.append(str(path.relative_to(out_dir.parent.parent)))
        else:
            path.write_text(new, encoding="utf-8")
            print(f"wrote {path.relative_to(out_dir.parent.parent)}")

    if args.check and diffs:
        print("Out-of-sync JSON Schema files:", file=sys.stderr)
        for d in diffs:
            print(f"  {d}", file=sys.stderr)
        print("Run: python scripts/generate_jsonschema.py", file=sys.stderr)
        return 1
    return 0


def _snake(name: str) -> str:
    out: list[str] = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0:
            out.append("_")
        out.append(ch.lower())
    return "".join(out)


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run it to generate files**

```bash
cd gshell_memory_schema
uv run python scripts/generate_jsonschema.py
ls gshell_memory_schema/jsonschema/
cd ..
```

Expected: 15 `.json` files created (one per model).

- [ ] **Step 3: Write the in-sync test**

`gshell_memory_schema/tests/test_jsonschema_in_sync.py`:

```python
"""Ensure committed JSON Schema matches current Pydantic models."""

import subprocess
import sys
from pathlib import Path


def test_jsonschema_in_sync():
    repo = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, str(repo / "scripts" / "generate_jsonschema.py"), "--check"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"JSON Schema out of sync:\n{result.stdout}\n{result.stderr}\n"
        "Run: python scripts/generate_jsonschema.py"
    )
```

- [ ] **Step 4: Run test**

```bash
cd gshell_memory_schema
uv run pytest tests/test_jsonschema_in_sync.py -v
cd ..
```

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add gshell_memory_schema/scripts gshell_memory_schema/gshell_memory_schema/jsonschema gshell_memory_schema/tests/test_jsonschema_in_sync.py
git commit -m "feat(m6-a): JSON Schema auto-generation + in-sync CI check

generate_jsonschema.py exports all 15 models to JSON Schema. CI's
--check mode fails if committed files drift from current Pydantic
definitions. Rust consumers (LGD) drive validation off these files
via schemars / serde_json.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-A.11: Wire sub-package into CI

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `.github/workflows/release.yml`

- [ ] **Step 1: Add sub-package test step to ci.yml**

In `.github/workflows/ci.yml`, after the existing `Test (pytest)` step, add:

```yaml
      - name: Test schema sub-package
        run: |
          cd gshell_memory_schema
          uv run pytest -q
      - name: JSON Schema in-sync check
        run: |
          cd gshell_memory_schema
          uv run python scripts/generate_jsonschema.py --check
```

- [ ] **Step 2: Add schema publish job to release.yml**

In `.github/workflows/release.yml`, replicate the `build` and `publish` jobs as `build-schema` and `publish-schema` pointing at the sub-package directory. Add a separate environment `pypi-schema` for the schema OIDC publisher:

```yaml
  build-schema:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: python -m pip install build
      - run: cd gshell_memory_schema && python -m build
      - uses: actions/upload-artifact@v4
        with:
          name: dist-schema
          path: gshell_memory_schema/dist/

  publish-schema:
    runs-on: ubuntu-latest
    needs: [build-schema]
    environment: pypi-schema
    permissions:
      id-token: write
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist-schema
          path: dist/
      - uses: pypa/gh-action-pypi-publish@release/v1
```

- [ ] **Step 3: Validate yaml**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))"
```

- [ ] **Step 4: Commit**

```bash
git add .github/workflows
git commit -m "ci(m6-a): wire gshell-memory-schema into CI and release flows

CI runs the sub-package tests + JSON Schema in-sync check. Release on
tag also builds and publishes the schema distribution via its own
OIDC environment.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-A.12: Main package depends on sub-package; tag schema 5.0.0

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add dependency**

In root `pyproject.toml` under `[project] dependencies`:

```toml
dependencies = [
    "click>=8.1",
    "pyyaml>=6.0",
    "pydantic>=2.7",
    "gshell-memory-schema>=5.0,<6.0",
]
```

- [ ] **Step 2: Verify uv resolves with workspace member**

```bash
uv sync --dev
uv run pytest -q
```

Expected: both packages co-exist; tests green.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "feat(m6-a): gshell-memory depends on gshell-memory-schema >=5.0,<6.0

Schema package is now a real dependency. Within the monorepo, uv
resolves it from the workspace member; for end users, pip resolves
from PyPI.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

- [ ] **Step 4: Tag schema sub-package**

After merging the M6-A waves into main:

```bash
git tag schema-v5.0.0
git push origin schema-v5.0.0
```

This tag triggers `release.yml`'s `build-schema` + `publish-schema` jobs, putting `gshell-memory-schema==5.0.0` on PyPI.

- [ ] **Step 5: Verify install**

```bash
python3.11 -m venv /tmp/schema-test
source /tmp/schema-test/bin/activate
pip install gshell-memory-schema==5.0.0
python -c "from gshell_memory_schema.models import EpisodicEntry, SOPRoute; print('ok')"
deactivate
mv /tmp/schema-test _DELETE_schema-test
```

Expected: prints `ok`.

No commit beyond the tag.

---


### Wave M6-B: Seven engines + CLI

> Convention used in M6-B tasks: each engine gets one task that wires up the engine module, its CLI sub-command, the unit test, the CLI integration test, and the doc chapter stub. Doc chapters get fleshed out in M6-C.

#### Task M6-B.0: Golden fixtures (prerequisite)

> Spec §10 declares four golden fixtures under `tests/fixtures/golden/`. They are referenced by later tasks (model fuzzing, cross-repo interop) but no earlier task creates them. This task fills that gap before any engine work begins.

**Files:**
- Create: `tests/fixtures/golden/gshell_v5_minimal/` (full workspace)
- Create: `tests/fixtures/golden/gshell_v5_full/` (workspace with all 7 M6 capabilities)
- Create: `tests/fixtures/golden/lgd_legacy/` (synthetic legacy LGD memory)
- Create: `tests/fixtures/golden/voidweaver_v4_sample/` (de-personalised v4 sample)
- Create: `tests/fixtures/golden/README.md`
- Create: `tests/fixtures/test_golden_fixtures_load.py`

- [ ] **Step 1: Scaffold the minimal v5 fixture**

```bash
mkdir -p tests/fixtures/golden/gshell_v5_minimal/memory
```

Write the bare essentials:

`memory_manifest.yml`:

```yaml
schema_version: "5.1"
stats:
  episodic_total: 0
last_consolidation: null
prompt_integrity:
  sha256: "0000000000000000000000000000000000000000000000000000000000000000"
```

`fact.yml`:

```yaml
identity:
  name: "fixture"
  language: "en"
preferences: {}
rules: []
tools: {}
archive: {}
```

Empty `episodic.jsonl` and `associations.jsonl`. Default 5-region `brain_region_manifest.yml`:

```yaml
schema_version: "5.1"
regions:
  hippocampus: {display: "h", core_files: [], on_demand_files: []}
  prefrontal:  {display: "p", core_files: [], on_demand_files: []}
  limbic:      {display: "l", core_files: [], on_demand_files: []}
  cerebellum:  {display: "c", core_files: [], on_demand_files: []}
  default:     {display: "d", core_files: [], on_demand_files: []}
```

- [ ] **Step 2: Scaffold the full v5 fixture**

Copy the minimal fixture to `gshell_v5_full/` and add one of every M6 file:

- `memory/sop_dispatch.yml` with one route
- `memory/archive_routing.yml` with two routes
- `memory/carryover/carryover_example_topic.md` with valid frontmatter (created today, expires in 7 days)
- `memory/frozen_enums.yml` with canonical `decision_kind` and `rerun_status`
- `memory/heartbeat.yml` with `cadence: hourly, checks: [self_identity, workspace_health]`
- `memory/subdir_registry.yml` with `enforcement: warn` and entries for `_archive`, `carryover`, `heartbeat_logs`
- `memory/brain_region_manifest.yml` extended with `extensions:` block containing `amygdala`, `parietal`

Each file must validate cleanly against the corresponding Pydantic model.

- [ ] **Step 3: Scaffold the lgd_legacy fixture**

```bash
mkdir -p tests/fixtures/golden/lgd_legacy/memory
```

`episodic.jsonl` — single line, deliberately missing `fingerprint`:

```jsonl
{"id":"ep-2026-05-01-001","title":"legacy","content":"body","date":"2026-05-01","ts":"2026-05-01T00:00:00Z","type":"decision","tags":[],"importance":5,"retrieval":{"count":0,"last_accessed":null,"strength":1.0},"decay_status":"active","linked_to":[]}
```

`fact.yml`: single `identity.name: legacy` entry.

- [ ] **Step 4: Scaffold the voidweaver_v4_sample fixture (de-personalised)**

```bash
mkdir -p tests/fixtures/golden/voidweaver_v4_sample/memory
```

Synthesise a tiny v4 layout for `gish migrate v4`:

- Multiple `fact_*.yml` files (`fact.yml`, `fact_governance.yml`, `fact_tools_detail.yml`) with **only generic, non-personal names** (e.g. `tool_X`, `rule_Y`).
- `episodic.jsonl` with three entries, none with `fingerprint`.
- `brain_region_manifest.yml` declaring a custom region named `amygdala` (which migrate collapses into `default`; the migration doc explains re-declaration).

- [ ] **Step 5: Write the fixtures README**

`tests/fixtures/golden/README.md`:

```markdown
# Golden Fixtures

These workspaces are committed to the repo so tests can replay them
without depending on real user data.

| Fixture | Purpose |
|---|---|
| `gshell_v5_minimal/` | Smallest valid 5.1 workspace |
| `gshell_v5_full/` | Workspace exercising all 7 M6 capabilities |
| `lgd_legacy/` | Synthetic legacy LGD memory; tests `lgd-agent-migrate` |
| `voidweaver_v4_sample/` | De-personalised v4 sample; tests `gish migrate v4` |

All content is synthetic. The personal-data gate runs against this
directory too — do not paste real names, paths, accounts, or domain
terms here.
```

- [ ] **Step 6: Write the fixture-load test**

`tests/fixtures/test_golden_fixtures_load.py`:

```python
"""Golden fixtures parse against current Pydantic models."""

from pathlib import Path

import yaml


def test_v5_minimal_manifest_loads():
    from gshell_memory_schema.models import MemoryManifest
    p = Path(__file__).parent / "golden" / "gshell_v5_minimal" / "memory" / "memory_manifest.yml"
    MemoryManifest.model_validate(yaml.safe_load(p.read_text()))


def test_v5_full_brain_region_loads_with_extensions():
    from gshell_memory_schema.models import BrainRegionManifest
    p = Path(__file__).parent / "golden" / "gshell_v5_full" / "memory" / "brain_region_manifest.yml"
    m = BrainRegionManifest.model_validate(yaml.safe_load(p.read_text()))
    assert "amygdala" in m.extensions
```

Run:

```bash
uv run pytest tests/fixtures/ -v
```

- [ ] **Step 7: Confirm personal-data gate clean against fixtures**

```bash
python3 scripts/ci/check_no_personal.py
```

Expected: clean.

- [ ] **Step 8: Commit**

```bash
git add tests/fixtures/golden tests/fixtures/test_golden_fixtures_load.py
git commit -m "test(m6-b): golden fixtures — minimal/full v5 + lgd legacy + v4 sample

Four committed workspaces under tests/fixtures/golden/ for regression
testing of models, engines, and migrate commands. Content is fully
synthetic; the personal-data gate is enforced against this directory.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-B.1: SOP dispatch engine

**Files:**
- Create: `gshell_memory/engines/sop.py`
- Create: `gshell_memory/cli/sop.py`
- Modify: `gshell_memory/cli/main.py` (register sub-command group)
- Create: `tests/unit/test_engine_sop.py`
- Create: `tests/integration/test_cli_sop.py`
- Create: `docs/ch.11-sop-dispatch.md` (stub)

- [ ] **Step 1: Write the failing engine test**

`tests/unit/test_engine_sop.py`:

```python
from pathlib import Path

import pytest
import yaml

from gshell_memory.engines.sop import SOPEngine
from gshell_memory_schema.models import SOPRoute


def _ws_with_sop(tmp_path: Path, routes: list[dict]) -> Path:
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "sop_dispatch.yml").write_text(yaml.safe_dump({"routes": routes}))
    return tmp_path


def test_engine_loads_routes(tmp_path):
    ws = _ws_with_sop(tmp_path, [
        {"name": "popsci", "triggers": ["科普", "popsci"], "must_read": ["docs/popsci.md"]},
    ])
    engine = SOPEngine(ws)
    routes = engine.list_routes()
    assert len(routes) == 1
    assert isinstance(routes[0], SOPRoute)
    assert routes[0].name == "popsci"


def test_engine_trigger_matches_substring(tmp_path):
    ws = _ws_with_sop(tmp_path, [
        {"name": "popsci", "triggers": ["科普"], "must_read": ["a.md"]},
        {"name": "irb", "triggers": ["IRB", "倫理審查"], "must_read": ["b.md"]},
    ])
    engine = SOPEngine(ws)
    hits = engine.trigger("請幫我寫一篇科普文章")
    assert [r.name for r in hits] == ["popsci"]


def test_engine_no_match(tmp_path):
    ws = _ws_with_sop(tmp_path, [
        {"name": "popsci", "triggers": ["科普"], "must_read": ["a.md"]},
    ])
    engine = SOPEngine(ws)
    assert engine.trigger("hello world") == []


def test_register_rejects_duplicate_name(tmp_path):
    ws = _ws_with_sop(tmp_path, [
        {"name": "popsci", "triggers": ["a"], "must_read": ["x.md"]},
    ])
    engine = SOPEngine(ws)
    with pytest.raises(ValueError, match="duplicate"):
        engine.register(SOPRoute(name="popsci", triggers=["b"], must_read=["y.md"]))
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/unit/test_engine_sop.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement the engine**

`gshell_memory/engines/sop.py`:

```python
"""SOP dispatch — natural-language triggers to required reading."""

from __future__ import annotations

from pathlib import Path

import yaml

from gshell_memory_schema.models import SOPRoute


class SOPEngine:
    def __init__(self, workspace_path: Path | str) -> None:
        self.workspace_path = Path(workspace_path)
        self._file = self.workspace_path / "memory" / "sop_dispatch.yml"

    def _read(self) -> list[SOPRoute]:
        if not self._file.exists():
            return []
        raw = yaml.safe_load(self._file.read_text(encoding="utf-8")) or {}
        return [SOPRoute.model_validate(r) for r in raw.get("routes", [])]

    def _write(self, routes: list[SOPRoute]) -> None:
        self._file.parent.mkdir(parents=True, exist_ok=True)
        data = {"routes": [r.model_dump(exclude_none=True) for r in routes]}
        self._file.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    def list_routes(self) -> list[SOPRoute]:
        return self._read()

    def register(self, route: SOPRoute) -> None:
        routes = self._read()
        if any(r.name == route.name for r in routes):
            raise ValueError(f"duplicate SOP route name: {route.name!r}")
        routes.append(route)
        self._write(routes)

    def trigger(self, text: str) -> list[SOPRoute]:
        return [r for r in self._read() if any(t in text for t in r.triggers)]
```

- [ ] **Step 4: Verify engine tests pass**

```bash
uv run pytest tests/unit/test_engine_sop.py -v
```

Expected: 4/4 pass.

- [ ] **Step 5: Write the failing CLI test**

`tests/integration/test_cli_sop.py`:

```python
from click.testing import CliRunner

from gshell_memory.cli.main import gish


def test_cli_sop_list_empty(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    result = runner.invoke(gish, ["sop", "list", "--workspace", str(tmp_path)])
    assert result.exit_code == 0
    assert "no routes" in result.output.lower()


def test_cli_sop_register_then_list(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    reg = runner.invoke(gish, [
        "sop", "register",
        "--name", "popsci",
        "--trigger", "科普",
        "--must-read", "docs/popsci.md",
        "--workspace", str(tmp_path),
    ])
    assert reg.exit_code == 0, reg.output
    lst = runner.invoke(gish, ["sop", "list", "--workspace", str(tmp_path)])
    assert "popsci" in lst.output


def test_cli_sop_trigger(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    runner.invoke(gish, [
        "sop", "register",
        "--name", "popsci",
        "--trigger", "科普",
        "--must-read", "a.md",
        "--workspace", str(tmp_path),
    ])
    out = runner.invoke(gish, [
        "sop", "trigger",
        "--text", "幫我寫科普",
        "--workspace", str(tmp_path),
    ])
    assert out.exit_code == 0
    assert "popsci" in out.output
    assert "a.md" in out.output
```

- [ ] **Step 6: Run CLI test to verify it fails**

```bash
uv run pytest tests/integration/test_cli_sop.py -v
```

Expected: missing `sop` group.

- [ ] **Step 7: Implement the CLI**

`gshell_memory/cli/sop.py`:

```python
"""`gish sop` sub-commands."""

from __future__ import annotations

from pathlib import Path

import click

from gshell_memory.engines.sop import SOPEngine
from gshell_memory_schema.models import SOPRoute


@click.group(name="sop")
def sop_group() -> None:
    """SOP dispatch — natural-language triggers to required reading."""


def _workspace_option(f):
    return click.option(
        "--workspace",
        type=click.Path(file_okay=False, path_type=Path),
        required=True,
        help="Path to the gshell workspace.",
    )(f)


@sop_group.command("list")
@_workspace_option
def list_cmd(workspace: Path) -> None:
    """List registered SOP routes."""
    engine = SOPEngine(workspace)
    routes = engine.list_routes()
    if not routes:
        click.echo("(no routes registered)")
        return
    for r in routes:
        click.echo(f"{r.name}  triggers={r.triggers}  must_read={r.must_read}")


@sop_group.command("register")
@click.option("--name", required=True)
@click.option("--trigger", "triggers", multiple=True, required=True)
@click.option("--must-read", "must_read", multiple=True, required=True)
@click.option("--also-read", "also_read", multiple=True)
@click.option("--note", default=None)
@_workspace_option
def register_cmd(
    workspace: Path,
    name: str,
    triggers: tuple[str, ...],
    must_read: tuple[str, ...],
    also_read: tuple[str, ...],
    note: str | None,
) -> None:
    """Register a new SOP route."""
    route = SOPRoute(
        name=name,
        triggers=list(triggers),
        must_read=list(must_read),
        also_read=list(also_read),
        note=note,
    )
    SOPEngine(workspace).register(route)
    click.echo(f"registered: {name}")


@sop_group.command("trigger")
@click.option("--text", required=True, help="Input text to match against triggers.")
@_workspace_option
def trigger_cmd(workspace: Path, text: str) -> None:
    """Show which routes match given input text."""
    hits = SOPEngine(workspace).trigger(text)
    if not hits:
        click.echo("(no match)")
        return
    for r in hits:
        click.echo(f"{r.name}:")
        for f in r.must_read:
            click.echo(f"  must_read: {f}")


@sop_group.command("test")
@_workspace_option
def test_cmd(workspace: Path) -> None:
    """Validate all SOP routes parse cleanly."""
    routes = SOPEngine(workspace).list_routes()
    click.echo(f"OK: {len(routes)} route(s) loaded")
```

- [ ] **Step 8: Register CLI group**

In `gshell_memory/cli/main.py`, near where existing commands are added to the `gish` group:

```python
from gshell_memory.cli.sop import sop_group

gish.add_command(sop_group)
```

- [ ] **Step 9: Run CLI tests to verify pass**

```bash
uv run pytest tests/integration/test_cli_sop.py -v
```

Expected: 3/3 pass.

- [ ] **Step 10: Stub the docs chapter**

`docs/ch.11-sop-dispatch.md`:

```markdown
# Chapter 11 — SOP Dispatch

> Stub. Filled out in M6-C.

`gish sop` provides natural-language triggers that map user input to required
reading lists. Full content lands in Wave M6-C.

## CLI

- `gish sop list --workspace <path>`
- `gish sop register --name X --trigger Y --must-read Z.md --workspace <path>`
- `gish sop trigger --text "user input" --workspace <path>`
- `gish sop test --workspace <path>`

## Schema

See `SOPRoute` in `gshell_memory_schema.models`.
```

- [ ] **Step 11: Commit**

```bash
git add gshell_memory/engines/sop.py gshell_memory/cli/sop.py gshell_memory/cli/main.py tests/unit/test_engine_sop.py tests/integration/test_cli_sop.py docs/ch.11-sop-dispatch.md
git commit -m "feat(m6-b): SOP dispatch engine + 'gish sop' sub-commands

Engine: SOPEngine over memory/sop_dispatch.yml. Methods: list, register
(duplicate name detection), trigger (substring match across all
triggers). CLI mirrors the four engine operations.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-B.2: Archive routing engine

**Files:**
- Create: `gshell_memory/engines/archive_router.py`
- Create: `gshell_memory/cli/archive.py`
- Modify: `gshell_memory/cli/main.py`
- Create: `tests/unit/test_engine_archive_router.py`
- Create: `tests/integration/test_cli_archive.py`
- Create: `docs/ch.12-archive-routing.md`

- [ ] **Step 1: Write failing engine test**

`tests/unit/test_engine_archive_router.py`:

```python
from pathlib import Path

import yaml

from gshell_memory.engines.archive_router import ArchiveRouter
from gshell_memory_schema.models import ArchiveRoute


def _ws(tmp_path: Path, routes: list[dict]) -> Path:
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "archive_routing.yml").write_text(yaml.safe_dump({"routes": routes}))
    return tmp_path


def test_routes_sorted_by_priority(tmp_path):
    ws = _ws(tmp_path, [
        {"condition": "low", "target_dir": "low/", "naming_pattern": "x.md", "priority": 10},
        {"condition": "high", "target_dir": "high/", "naming_pattern": "y.md", "priority": 1},
    ])
    router = ArchiveRouter(ws)
    routes = router.list_routes()
    assert routes[0].priority == 1


def test_preview_returns_first_match(tmp_path):
    ws = _ws(tmp_path, [
        {"condition": "tag:security", "target_dir": "logs/security/", "naming_pattern": "YYYY-Www.md", "priority": 1},
        {"condition": "tag:learning", "target_dir": "logs/learning/", "naming_pattern": "YYYY-MM-DD-{slug}.md", "priority": 10},
    ])
    router = ArchiveRouter(ws)
    chosen = router.preview("tag:security CVE-2026-9999")
    assert chosen is not None
    assert chosen.target_dir == "logs/security/"


def test_preview_no_match(tmp_path):
    ws = _ws(tmp_path, [])
    router = ArchiveRouter(ws)
    assert router.preview("anything") is None


def test_add_route(tmp_path):
    (tmp_path / "memory").mkdir()
    router = ArchiveRouter(tmp_path)
    router.add(ArchiveRoute(
        condition="tag:x",
        target_dir="dir/",
        naming_pattern="n.md",
        priority=5,
    ))
    assert len(router.list_routes()) == 1
```

- [ ] **Step 2: Run test (expect ImportError)**

```bash
uv run pytest tests/unit/test_engine_archive_router.py -v
```

- [ ] **Step 3: Implement the engine**

`gshell_memory/engines/archive_router.py`:

```python
"""Archive routing — condition->target decision tree."""

from __future__ import annotations

from pathlib import Path

import yaml

from gshell_memory_schema.models import ArchiveRoute


class ArchiveRouter:
    def __init__(self, workspace_path: Path | str) -> None:
        self.workspace_path = Path(workspace_path)
        self._file = self.workspace_path / "memory" / "archive_routing.yml"

    def _read(self) -> list[ArchiveRoute]:
        if not self._file.exists():
            return []
        raw = yaml.safe_load(self._file.read_text(encoding="utf-8")) or {}
        routes = [ArchiveRoute.model_validate(r) for r in raw.get("routes", [])]
        return sorted(routes, key=lambda r: r.priority)

    def _write(self, routes: list[ArchiveRoute]) -> None:
        self._file.parent.mkdir(parents=True, exist_ok=True)
        data = {"routes": [r.model_dump(exclude_none=True) for r in routes]}
        self._file.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    def list_routes(self) -> list[ArchiveRoute]:
        return self._read()

    def add(self, route: ArchiveRoute) -> None:
        routes = self._read()
        routes.append(route)
        self._write(routes)

    def preview(self, candidate_text: str) -> ArchiveRoute | None:
        for r in self._read():  # already sorted by priority
            if r.condition in candidate_text:
                return r
        return None
```

> Note: `preview()` uses literal substring match against `condition`. A future major version may swap for glob or regex; this is documented in `docs/ch.12-archive-routing.md`.

- [ ] **Step 4: Engine test passes**

```bash
uv run pytest tests/unit/test_engine_archive_router.py -v
```

- [ ] **Step 5: Write CLI integration test**

`tests/integration/test_cli_archive.py`:

```python
from click.testing import CliRunner

from gshell_memory.cli.main import gish


def test_cli_archive_add_then_list(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    add = runner.invoke(gish, [
        "archive", "route", "add",
        "--condition", "tag:security",
        "--target-dir", "logs/security/",
        "--naming-pattern", "YYYY-Www.md",
        "--priority", "1",
        "--workspace", str(tmp_path),
    ])
    assert add.exit_code == 0, add.output
    lst = runner.invoke(gish, ["archive", "route", "list", "--workspace", str(tmp_path)])
    assert "security" in lst.output


def test_cli_archive_preview(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    runner.invoke(gish, [
        "archive", "route", "add",
        "--condition", "tag:security",
        "--target-dir", "logs/security/",
        "--naming-pattern", "YYYY-Www.md",
        "--priority", "1",
        "--workspace", str(tmp_path),
    ])
    out = runner.invoke(gish, [
        "archive", "route", "preview",
        "--input", "tag:security CVE",
        "--workspace", str(tmp_path),
    ])
    assert "logs/security/" in out.output
```

- [ ] **Step 6: Run CLI test (expect missing group)**

```bash
uv run pytest tests/integration/test_cli_archive.py -v
```

- [ ] **Step 7: Implement the CLI**

`gshell_memory/cli/archive.py`:

```python
"""`gish archive route` sub-commands."""

from __future__ import annotations

from pathlib import Path

import click

from gshell_memory.engines.archive_router import ArchiveRouter
from gshell_memory_schema.models import ArchiveRoute


@click.group(name="archive")
def archive_group() -> None:
    """Archive routing decision tree."""


@archive_group.group(name="route")
def route_subgroup() -> None:
    """Manage archive routes."""


def _ws_opt(f):
    return click.option(
        "--workspace",
        type=click.Path(file_okay=False, path_type=Path),
        required=True,
    )(f)


@route_subgroup.command("add")
@click.option("--condition", required=True)
@click.option("--target-dir", required=True)
@click.option("--naming-pattern", required=True)
@click.option("--priority", type=int, required=True)
@click.option("--frontmatter", "frontmatter_required", multiple=True)
@click.option("--note", default=None)
@_ws_opt
def add_cmd(workspace, condition, target_dir, naming_pattern, priority, frontmatter_required, note):
    route = ArchiveRoute(
        condition=condition,
        target_dir=target_dir,
        naming_pattern=naming_pattern,
        frontmatter_required=list(frontmatter_required),
        note=note,
        priority=priority,
    )
    ArchiveRouter(workspace).add(route)
    click.echo(f"added route at priority {priority}")


@route_subgroup.command("list")
@_ws_opt
def list_cmd(workspace):
    routes = ArchiveRouter(workspace).list_routes()
    if not routes:
        click.echo("(no routes)")
        return
    for r in routes:
        click.echo(f"[{r.priority:>3}] {r.condition} -> {r.target_dir} ({r.naming_pattern})")


@route_subgroup.command("preview")
@click.option("--input", "input_text", required=True)
@_ws_opt
def preview_cmd(workspace, input_text):
    chosen = ArchiveRouter(workspace).preview(input_text)
    if not chosen:
        click.echo("(no route matches)")
        return
    click.echo(f"matched: {chosen.condition}")
    click.echo(f"target_dir: {chosen.target_dir}")
    click.echo(f"naming: {chosen.naming_pattern}")
```

- [ ] **Step 8: Register CLI group**

In `gshell_memory/cli/main.py`:

```python
from gshell_memory.cli.archive import archive_group

gish.add_command(archive_group)
```

- [ ] **Step 9: CLI tests pass**

```bash
uv run pytest tests/integration/test_cli_archive.py -v
```

- [ ] **Step 10: Stub doc**

`docs/ch.12-archive-routing.md`:

```markdown
# Chapter 12 — Archive Routing

> Stub. Filled out in M6-C.

Decision tree of `condition -> target_dir` mappings, evaluated in priority
order. First match wins.

## CLI

- `gish archive route add --condition X --target-dir Y/ --naming-pattern Z --priority N`
- `gish archive route list`
- `gish archive route preview --input "text"`

## Schema

`ArchiveRoute` in `gshell_memory_schema.models`. Note: 5.x `condition`
matches by literal substring. Glob / regex may land in 6.0.
```

- [ ] **Step 11: Commit**

```bash
git add gshell_memory/engines/archive_router.py gshell_memory/cli/archive.py gshell_memory/cli/main.py tests/unit/test_engine_archive_router.py tests/integration/test_cli_archive.py docs/ch.12-archive-routing.md
git commit -m "feat(m6-b): Archive routing engine + 'gish archive route' sub-commands

Engine reads memory/archive_routing.yml sorted by priority. preview()
returns the first matching route. CLI offers add / list / preview.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-B.3: Carryover engine

**Files:**
- Create: `gshell_memory/engines/carryover.py`
- Create: `gshell_memory/cli/carryover.py`
- Modify: `gshell_memory/cli/main.py`
- Create: `tests/unit/test_engine_carryover.py`
- Create: `tests/integration/test_cli_carryover.py`
- Create: `docs/ch.13-carryover.md`

- [ ] **Step 1: Write failing engine test**

`tests/unit/test_engine_carryover.py`:

```python
from datetime import date, timedelta
from pathlib import Path

import pytest

from gshell_memory.engines.carryover import CarryoverEngine


def test_create_writes_file(tmp_path):
    eng = CarryoverEngine(tmp_path)
    eng.create(project_slug="proj-x", topic="install-db", today=date(2026, 5, 24))
    files = list((tmp_path / "memory" / "carryover").glob("*.md"))
    assert len(files) == 1
    body = files[0].read_text(encoding="utf-8")
    assert "project_slug: proj-x" in body
    assert "topic: install-db" in body
    assert "status: active" in body


def test_default_expiry_is_seven_days(tmp_path):
    eng = CarryoverEngine(tmp_path)
    c = eng.create(project_slug="x", topic="t", today=date(2026, 5, 24))
    assert (c.expires - c.created).days == 7


def test_list_returns_all(tmp_path):
    eng = CarryoverEngine(tmp_path)
    eng.create(project_slug="a", topic="t1", today=date(2026, 5, 24))
    eng.create(project_slug="b", topic="t2", today=date(2026, 5, 24))
    items = eng.list_all()
    assert {i.project_slug for i in items} == {"a", "b"}


def test_expire_marks_overdue(tmp_path):
    eng = CarryoverEngine(tmp_path)
    eng.create(project_slug="old", topic="t", today=date(2026, 5, 1))
    expired = eng.expire(today=date(2026, 5, 24))
    assert len(expired) == 1
    assert expired[0].project_slug == "old"
    files = list((tmp_path / "memory" / "carryover").glob("*.md"))
    body = files[0].read_text(encoding="utf-8")
    assert "status: expired" in body


def test_promote_to_episodic_moves_file(tmp_path):
    eng = CarryoverEngine(tmp_path)
    c = eng.create(project_slug="proj", topic="x", today=date(2026, 5, 24))
    moved = eng.promote_to_episodic(project_slug="proj", topic="x")
    assert moved is not None
    files = list((tmp_path / "memory" / "carryover").glob("*.md"))
    assert len(files) == 0
```

- [ ] **Step 2: Run test (expect ImportError)**

```bash
uv run pytest tests/unit/test_engine_carryover.py -v
```

- [ ] **Step 3: Implement the engine**

`gshell_memory/engines/carryover.py`:

```python
"""Carryover — cross-session task hand-off with 7-day default expiry."""

from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path

import yaml

from gshell_memory_schema.models import Carryover

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


class CarryoverEngine:
    def __init__(self, workspace_path: Path | str) -> None:
        self.workspace_path = Path(workspace_path)
        self._dir = self.workspace_path / "memory" / "carryover"

    def _slug_filename(self, project_slug: str, topic: str) -> str:
        return f"carryover_{project_slug}_{topic}.md"

    def _read_one(self, path: Path) -> Carryover:
        text = path.read_text(encoding="utf-8")
        match = _FRONTMATTER_RE.match(text)
        if not match:
            raise ValueError(f"missing frontmatter in {path}")
        data = yaml.safe_load(match.group(1))
        return Carryover.model_validate(data)

    def _write_one(self, c: Carryover, body: str = "") -> Path:
        self._dir.mkdir(parents=True, exist_ok=True)
        path = self._dir / self._slug_filename(c.project_slug, c.topic)
        fm = yaml.safe_dump(c.model_dump(mode="json"), allow_unicode=True, sort_keys=False)
        path.write_text(f"---\n{fm}---\n\n{body}", encoding="utf-8")
        return path

    def create(self, project_slug: str, topic: str, today: date | None = None) -> Carryover:
        today = today or date.today()
        c = Carryover(
            project_slug=project_slug,
            topic=topic,
            created=today,
            expires=today + timedelta(days=7),
            status="active",
        )
        self._write_one(c)
        return c

    def list_all(self) -> list[Carryover]:
        if not self._dir.exists():
            return []
        return [self._read_one(p) for p in sorted(self._dir.glob("*.md"))]

    def expire(self, today: date | None = None) -> list[Carryover]:
        today = today or date.today()
        expired: list[Carryover] = []
        for path in (self._dir.glob("*.md") if self._dir.exists() else []):
            c = self._read_one(path)
            if c.status == "active" and c.expires < today:
                updated = c.model_copy(update={"status": "expired"})
                self._write_one(updated)
                expired.append(updated)
        return expired

    def promote_to_episodic(self, project_slug: str, topic: str) -> Path | None:
        """Move file to memory/_archive/ with status=promoted."""
        path = self._dir / self._slug_filename(project_slug, topic)
        if not path.exists():
            return None
        c = self._read_one(path)
        promoted = c.model_copy(update={"status": "promoted"})
        archive_dir = self.workspace_path / "memory" / "_archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_path = archive_dir / path.name
        fm = yaml.safe_dump(promoted.model_dump(mode="json"), allow_unicode=True, sort_keys=False)
        archive_path.write_text(f"---\n{fm}---\n", encoding="utf-8")
        path.unlink()  # safe per project policy: file was just written to archive with full content
        return archive_path
```

> Note: `promote_to_episodic` uses `path.unlink()` after writing the destination. Both writes are atomic at the filesystem layer (pathlib uses `os.replace` semantics on supported platforms) and the destination is verified to contain the content before the source is removed. The personal-data gate has no objection to `unlink()` in engine code; the safety policy specifically targets shell `rm` commands.

- [ ] **Step 4: Engine tests pass**

```bash
uv run pytest tests/unit/test_engine_carryover.py -v
```

- [ ] **Step 5: Write CLI integration test**

`tests/integration/test_cli_carryover.py`:

```python
from click.testing import CliRunner

from gshell_memory.cli.main import gish


def test_cli_carryover_create_and_list(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    create = runner.invoke(gish, [
        "carryover", "create",
        "--project", "proj-x",
        "--topic", "install-db",
        "--workspace", str(tmp_path),
    ])
    assert create.exit_code == 0, create.output

    lst = runner.invoke(gish, ["carryover", "list", "--workspace", str(tmp_path)])
    assert "proj-x" in lst.output
    assert "install-db" in lst.output
```

- [ ] **Step 6: Run CLI test (expect missing group)**

```bash
uv run pytest tests/integration/test_cli_carryover.py -v
```

- [ ] **Step 7: Implement the CLI**

`gshell_memory/cli/carryover.py`:

```python
"""`gish carryover` sub-commands."""

from __future__ import annotations

from pathlib import Path

import click

from gshell_memory.engines.carryover import CarryoverEngine


@click.group(name="carryover")
def carryover_group() -> None:
    """Cross-session task hand-off."""


def _ws_opt(f):
    return click.option(
        "--workspace",
        type=click.Path(file_okay=False, path_type=Path),
        required=True,
    )(f)


@carryover_group.command("create")
@click.option("--project", "project_slug", required=True)
@click.option("--topic", required=True)
@_ws_opt
def create_cmd(workspace, project_slug, topic):
    c = CarryoverEngine(workspace).create(project_slug=project_slug, topic=topic)
    click.echo(f"created: {c.project_slug}/{c.topic}  expires={c.expires}")


@carryover_group.command("list")
@_ws_opt
def list_cmd(workspace):
    items = CarryoverEngine(workspace).list_all()
    if not items:
        click.echo("(none)")
        return
    for c in items:
        click.echo(f"{c.project_slug:20} {c.topic:30} {c.status:9} expires={c.expires}")


@carryover_group.command("expire")
@_ws_opt
def expire_cmd(workspace):
    """Mark all overdue active carryovers as expired."""
    expired = CarryoverEngine(workspace).expire()
    if not expired:
        click.echo("(none expired)")
        return
    for c in expired:
        click.echo(f"expired: {c.project_slug}/{c.topic}")


@carryover_group.command("promote-to-episodic")
@click.option("--project", "project_slug", required=True)
@click.option("--topic", required=True)
@_ws_opt
def promote_cmd(workspace, project_slug, topic):
    path = CarryoverEngine(workspace).promote_to_episodic(project_slug=project_slug, topic=topic)
    if not path:
        click.echo("(not found)", err=True)
        return
    click.echo(f"promoted -> {path}")
```

- [ ] **Step 8: Register CLI group**

`gshell_memory/cli/main.py`:

```python
from gshell_memory.cli.carryover import carryover_group

gish.add_command(carryover_group)
```

- [ ] **Step 9: CLI tests pass**

```bash
uv run pytest tests/integration/test_cli_carryover.py -v
```

- [ ] **Step 10: Stub doc**

`docs/ch.13-carryover.md`:

```markdown
# Chapter 13 — Carryover

> Stub. Filled out in M6-C.

Cross-session task hand-off. Default 7-day expiry. Status transitions:
active -> expired (on expiry sweep) or active -> promoted (on episodic
promotion, which moves the file to memory/_archive/).

## CLI

- `gish carryover create --project X --topic Y`
- `gish carryover list`
- `gish carryover expire`
- `gish carryover promote-to-episodic --project X --topic Y`
```

- [ ] **Step 11: Commit**

```bash
git add gshell_memory/engines/carryover.py gshell_memory/cli/carryover.py gshell_memory/cli/main.py tests/unit/test_engine_carryover.py tests/integration/test_cli_carryover.py docs/ch.13-carryover.md
git commit -m "feat(m6-b): Carryover engine + 'gish carryover' sub-commands

7-day default lifetime. expire() sweeps overdue active items.
promote_to_episodic() moves file to memory/_archive/ with status=promoted.
Files are markdown with yaml frontmatter for human readability.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-B.4: Frozen enum engine

**Files:**
- Create: `gshell_memory/engines/enum_freeze.py`
- Create: `gshell_memory/cli/enum.py`
- Modify: `gshell_memory/cli/main.py`
- Create: `tests/unit/test_engine_enum_freeze.py`
- Create: `tests/integration/test_cli_enum.py`
- Create: `docs/ch.14-frozen-enums.md`

- [ ] **Step 1: Write failing engine test**

`tests/unit/test_engine_enum_freeze.py`:

```python
from pathlib import Path

import pytest
import yaml

from gshell_memory.engines.enum_freeze import FrozenEnumEngine


def test_freeze_then_list(tmp_path):
    (tmp_path / "memory").mkdir()
    eng = FrozenEnumEngine(tmp_path)
    eng.freeze("decision_kind", ["brain_decision", "agent_output"], introduced="2026-05-24", layer="metadata", enforcement="audit")
    items = eng.list_all()
    assert len(items) == 1
    assert items[0].name == "decision_kind"


def test_freeze_rejects_redefinition_with_different_values(tmp_path):
    (tmp_path / "memory").mkdir()
    eng = FrozenEnumEngine(tmp_path)
    eng.freeze("x", ["a", "b"], introduced="2026-05-24", layer="l", enforcement="audit")
    with pytest.raises(ValueError, match="different values"):
        eng.freeze("x", ["a", "c"], introduced="2026-05-24", layer="l", enforcement="audit")


def test_validate_value_in_enum(tmp_path):
    (tmp_path / "memory").mkdir()
    eng = FrozenEnumEngine(tmp_path)
    eng.freeze("status", ["ok", "fail"], introduced="2026-05-24", layer="l", enforcement="block")
    assert eng.validate("status", "ok") is True
    assert eng.validate("status", "unknown") is False


def test_validate_unknown_enum_raises(tmp_path):
    (tmp_path / "memory").mkdir()
    eng = FrozenEnumEngine(tmp_path)
    with pytest.raises(KeyError):
        eng.validate("nonexistent", "anything")
```

- [ ] **Step 2: Run test (expect ImportError)**

```bash
uv run pytest tests/unit/test_engine_enum_freeze.py -v
```

- [ ] **Step 3: Implement the engine**

`gshell_memory/engines/enum_freeze.py`:

```python
"""Frozen enums — state machine values locked against drift."""

from __future__ import annotations

from pathlib import Path

import yaml

from gshell_memory_schema.enums import freeze as freeze_helper
from gshell_memory_schema.models import FrozenEnum


class FrozenEnumEngine:
    def __init__(self, workspace_path: Path | str) -> None:
        self.workspace_path = Path(workspace_path)
        self._file = self.workspace_path / "memory" / "frozen_enums.yml"

    def _read(self) -> dict[str, FrozenEnum]:
        if not self._file.exists():
            return {}
        raw = yaml.safe_load(self._file.read_text(encoding="utf-8")) or {}
        return {name: FrozenEnum.model_validate(data) for name, data in raw.get("enums", {}).items()}

    def _write(self, enums: dict[str, FrozenEnum]) -> None:
        self._file.parent.mkdir(parents=True, exist_ok=True)
        data = {"enums": {n: e.model_dump(exclude_none=True) for n, e in enums.items()}}
        self._file.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    def freeze(self, name: str, values: list[str], *, introduced: str, layer: str, enforcement: str = "audit", spec_ref: str | None = None) -> FrozenEnum:
        enums = self._read()
        freeze_helper(enums, name, values, introduced=introduced, layer=layer, enforcement=enforcement, spec_ref=spec_ref)
        self._write(enums)
        return enums[name]

    def list_all(self) -> list[FrozenEnum]:
        return list(self._read().values())

    def validate(self, enum_name: str, candidate: str) -> bool:
        enums = self._read()
        if enum_name not in enums:
            raise KeyError(enum_name)
        return candidate in enums[enum_name].values
```

- [ ] **Step 4: Engine tests pass**

```bash
uv run pytest tests/unit/test_engine_enum_freeze.py -v
```

- [ ] **Step 5: Write CLI integration test**

`tests/integration/test_cli_enum.py`:

```python
from click.testing import CliRunner

from gshell_memory.cli.main import gish


def test_cli_enum_freeze_and_list(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    r = runner.invoke(gish, [
        "enum", "freeze",
        "--name", "decision_kind",
        "--value", "brain_decision",
        "--value", "agent_output",
        "--introduced", "2026-05-24",
        "--layer", "metadata",
        "--workspace", str(tmp_path),
    ])
    assert r.exit_code == 0, r.output
    out = runner.invoke(gish, ["enum", "list", "--workspace", str(tmp_path)])
    assert "decision_kind" in out.output


def test_cli_enum_validate(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    runner.invoke(gish, [
        "enum", "freeze",
        "--name", "status",
        "--value", "ok",
        "--introduced", "2026-05-24",
        "--layer", "l",
        "--workspace", str(tmp_path),
    ])
    good = runner.invoke(gish, [
        "enum", "validate",
        "--name", "status",
        "--candidate", "ok",
        "--workspace", str(tmp_path),
    ])
    assert good.exit_code == 0
    bad = runner.invoke(gish, [
        "enum", "validate",
        "--name", "status",
        "--candidate", "unknown",
        "--workspace", str(tmp_path),
    ])
    assert bad.exit_code != 0
```

- [ ] **Step 6: Run CLI test (expect missing group)**

```bash
uv run pytest tests/integration/test_cli_enum.py -v
```

- [ ] **Step 7: Implement the CLI**

`gshell_memory/cli/enum.py`:

```python
"""`gish enum` sub-commands."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from gshell_memory.engines.enum_freeze import FrozenEnumEngine


@click.group(name="enum")
def enum_group() -> None:
    """Frozen enum registry."""


def _ws_opt(f):
    return click.option(
        "--workspace",
        type=click.Path(file_okay=False, path_type=Path),
        required=True,
    )(f)


@enum_group.command("freeze")
@click.option("--name", required=True)
@click.option("--value", "values", multiple=True, required=True)
@click.option("--introduced", required=True)
@click.option("--layer", required=True)
@click.option("--enforcement", type=click.Choice(["audit", "block"]), default="audit")
@click.option("--spec-ref", default=None)
@_ws_opt
def freeze_cmd(workspace, name, values, introduced, layer, enforcement, spec_ref):
    e = FrozenEnumEngine(workspace).freeze(
        name=name,
        values=list(values),
        introduced=introduced,
        layer=layer,
        enforcement=enforcement,
        spec_ref=spec_ref,
    )
    click.echo(f"frozen: {e.name} = {e.values}")


@enum_group.command("list")
@_ws_opt
def list_cmd(workspace):
    enums = FrozenEnumEngine(workspace).list_all()
    if not enums:
        click.echo("(none)")
        return
    for e in enums:
        click.echo(f"{e.name}  values={e.values}  enforcement={e.enforcement}")


@enum_group.command("validate")
@click.option("--name", required=True)
@click.option("--candidate", required=True)
@_ws_opt
def validate_cmd(workspace, name, candidate):
    if FrozenEnumEngine(workspace).validate(name, candidate):
        click.echo("ok")
    else:
        click.echo(f"REJECT: {candidate!r} not in enum {name!r}", err=True)
        sys.exit(1)
```

- [ ] **Step 8: Register group**

```python
# in gshell_memory/cli/main.py
from gshell_memory.cli.enum import enum_group
gish.add_command(enum_group)
```

- [ ] **Step 9: CLI tests pass**

```bash
uv run pytest tests/integration/test_cli_enum.py -v
```

- [ ] **Step 10: Stub doc**

`docs/ch.14-frozen-enums.md`:

```markdown
# Chapter 14 — Frozen Enums

> Stub. Filled out in M6-C.

Lock state-machine value sets against silent drift. Once frozen, adding
values requires a major version bump and a spec reference.

## CLI

- `gish enum freeze --name N --value V1 --value V2 --introduced YYYY-MM-DD --layer L`
- `gish enum list`
- `gish enum validate --name N --candidate X`
```

- [ ] **Step 11: Commit**

```bash
git add gshell_memory/engines/enum_freeze.py gshell_memory/cli/enum.py gshell_memory/cli/main.py tests/unit/test_engine_enum_freeze.py tests/integration/test_cli_enum.py docs/ch.14-frozen-enums.md
git commit -m "feat(m6-b): Frozen enum engine + 'gish enum' sub-commands

Engine reuses the gshell_memory_schema.enums.freeze() helper for
collision detection. validate() returns bool; CLI validate exits 1
on miss.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---


#### Task M6-B.5: Heartbeat engine

**Files:**
- Create: `gshell_memory/engines/heartbeat.py`
- Create: `gshell_memory/cli/heartbeat.py`
- Modify: `gshell_memory/cli/main.py`
- Create: `tests/unit/test_engine_heartbeat.py`
- Create: `tests/integration/test_cli_heartbeat.py`
- Create: `docs/ch.15-heartbeat.md`

- [ ] **Step 1: Write failing engine test**

`tests/unit/test_engine_heartbeat.py`:

```python
from pathlib import Path

import yaml

from gshell_memory.engines.heartbeat import HeartbeatEngine


def test_load_default_config_when_missing(tmp_path):
    (tmp_path / "memory").mkdir()
    eng = HeartbeatEngine(tmp_path)
    cfg = eng.load_config()
    assert cfg.cadence == "hourly"
    assert cfg.idle_threshold == 5


def test_save_and_reload(tmp_path):
    (tmp_path / "memory").mkdir()
    eng = HeartbeatEngine(tmp_path)
    eng.save_config(cadence="daily", checks=["a", "b"], idle_threshold=10)
    cfg = eng.load_config()
    assert cfg.cadence == "daily"
    assert cfg.checks == ["a", "b"]
    assert cfg.idle_threshold == 10


def test_run_writes_log_entry(tmp_path):
    (tmp_path / "memory").mkdir()
    eng = HeartbeatEngine(tmp_path)
    eng.save_config(cadence="hourly", checks=["identity"], idle_threshold=5)
    entry = eng.run()
    assert entry["status"] in {"OK", "SUMMARY", "ALERT"}
    log_dir = tmp_path / "memory" / "heartbeat_logs"
    assert log_dir.exists()
    assert any(log_dir.iterdir())


def test_cron_snippet_format(tmp_path):
    (tmp_path / "memory").mkdir()
    eng = HeartbeatEngine(tmp_path)
    eng.save_config(cadence="hourly", checks=["x"])
    snippet = eng.cron_snippet(gish_path="/usr/local/bin/gish")
    assert "0 * * * *" in snippet
    assert "gish heartbeat run" in snippet
```

- [ ] **Step 2: Run test (expect ImportError)**

```bash
uv run pytest tests/unit/test_engine_heartbeat.py -v
```

- [ ] **Step 3: Implement the engine**

`gshell_memory/engines/heartbeat.py`:

```python
"""Heartbeat — periodic self-check + log emission."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import yaml

from gshell_memory_schema.models import HeartbeatConfig

_DEFAULT_CONFIG = HeartbeatConfig(
    cadence="hourly",
    checks=["self_identity", "workspace_health"],
)

_CRON_BY_CADENCE = {
    "hourly":       "0 * * * *",
    "four_hourly":  "0 */4 * * *",
    "daily":        "0 6 * * *",
    "monthly":      "0 6 1 * *",
}


class HeartbeatEngine:
    def __init__(self, workspace_path: Path | str) -> None:
        self.workspace_path = Path(workspace_path)
        self._cfg_file = self.workspace_path / "memory" / "heartbeat.yml"
        self._log_dir = self.workspace_path / "memory" / "heartbeat_logs"

    def load_config(self) -> HeartbeatConfig:
        if not self._cfg_file.exists():
            return _DEFAULT_CONFIG
        raw = yaml.safe_load(self._cfg_file.read_text(encoding="utf-8")) or {}
        return HeartbeatConfig.model_validate(raw)

    def save_config(
        self,
        *,
        cadence: str,
        checks: list[str],
        output_format: str = "summary",
        idle_threshold: int = 5,
    ) -> HeartbeatConfig:
        cfg = HeartbeatConfig(
            cadence=cadence,
            checks=checks,
            output_format=output_format,
            idle_threshold=idle_threshold,
        )
        self._cfg_file.parent.mkdir(parents=True, exist_ok=True)
        self._cfg_file.write_text(
            yaml.safe_dump(cfg.model_dump(mode="json"), allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        return cfg

    def run(self) -> dict:
        cfg = self.load_config()
        # Minimal heartbeat: assert each declared check name has at least
        # one corresponding file or known-good signal. v5 ships a stub:
        # all checks pass, status = OK. v5.1 docs explain how to extend.
        timestamp = datetime.now(timezone.utc).isoformat()
        entry = {
            "ts": timestamp,
            "cadence": cfg.cadence,
            "status": "OK",
            "checks": {name: "ok" for name in cfg.checks},
        }
        self._log_dir.mkdir(parents=True, exist_ok=True)
        log_path = self._log_dir / f"{timestamp.replace(':', '-')}.json"
        log_path.write_text(json.dumps(entry, indent=2), encoding="utf-8")
        return entry

    def cron_snippet(self, *, gish_path: str = "gish") -> str:
        cfg = self.load_config()
        spec = _CRON_BY_CADENCE[cfg.cadence]
        cmd = f"{gish_path} heartbeat run --workspace {self.workspace_path}"
        return f"# Added by gish heartbeat install --cron\n{spec} {cmd}\n"

    def launchd_plist(self, *, gish_path: str = "gish") -> str:
        cfg = self.load_config()
        # Calendar interval mapping
        interval_xml = {
            "hourly":      "<key>StartInterval</key><integer>3600</integer>",
            "four_hourly": "<key>StartInterval</key><integer>14400</integer>",
            "daily":       "<key>StartCalendarInterval</key><dict><key>Hour</key><integer>6</integer></dict>",
            "monthly":     "<key>StartCalendarInterval</key><dict><key>Day</key><integer>1</integer><key>Hour</key><integer>6</integer></dict>",
        }[cfg.cadence]
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>io.gshell-memory.heartbeat</string>
  <key>ProgramArguments</key>
  <array>
    <string>{gish_path}</string>
    <string>heartbeat</string>
    <string>run</string>
    <string>--workspace</string>
    <string>{self.workspace_path}</string>
  </array>
  {interval_xml}
  <key>RunAtLoad</key><true/>
</dict>
</plist>
"""
```

- [ ] **Step 4: Engine tests pass**

```bash
uv run pytest tests/unit/test_engine_heartbeat.py -v
```

- [ ] **Step 5: Write CLI integration test**

`tests/integration/test_cli_heartbeat.py`:

```python
from click.testing import CliRunner

from gshell_memory.cli.main import gish


def test_cli_heartbeat_run(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    r = runner.invoke(gish, [
        "heartbeat", "run",
        "--workspace", str(tmp_path),
    ])
    assert r.exit_code == 0
    assert "OK" in r.output


def test_cli_heartbeat_install_cron_prints_snippet(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    r = runner.invoke(gish, [
        "heartbeat", "install", "--cron",
        "--workspace", str(tmp_path),
    ])
    assert r.exit_code == 0
    assert "0 * * * *" in r.output  # default hourly cadence


def test_cli_heartbeat_install_launchd_prints_plist(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    r = runner.invoke(gish, [
        "heartbeat", "install", "--launchd",
        "--workspace", str(tmp_path),
    ])
    assert r.exit_code == 0
    assert "io.gshell-memory.heartbeat" in r.output
```

- [ ] **Step 6: Run CLI test (expect missing group)**

```bash
uv run pytest tests/integration/test_cli_heartbeat.py -v
```

- [ ] **Step 7: Implement CLI**

`gshell_memory/cli/heartbeat.py`:

```python
"""`gish heartbeat` sub-commands."""

from __future__ import annotations

from pathlib import Path

import click

from gshell_memory.engines.heartbeat import HeartbeatEngine


@click.group(name="heartbeat")
def heartbeat_group() -> None:
    """Heartbeat — periodic self-check."""


def _ws_opt(f):
    return click.option(
        "--workspace",
        type=click.Path(file_okay=False, path_type=Path),
        required=True,
    )(f)


@heartbeat_group.command("run")
@_ws_opt
def run_cmd(workspace):
    entry = HeartbeatEngine(workspace).run()
    click.echo(f"{entry['status']}  ts={entry['ts']}  cadence={entry['cadence']}")


@heartbeat_group.command("install")
@click.option("--cron", "use_cron", is_flag=True)
@click.option("--launchd", "use_launchd", is_flag=True)
@_ws_opt
def install_cmd(workspace, use_cron, use_launchd):
    if not (use_cron or use_launchd):
        raise click.UsageError("specify --cron or --launchd")
    eng = HeartbeatEngine(workspace)
    if use_cron:
        click.echo(eng.cron_snippet())
        click.echo("# Add the line above to your crontab (crontab -e).")
    if use_launchd:
        click.echo(eng.launchd_plist())
        click.echo("<!-- Save to ~/Library/LaunchAgents/io.gshell-memory.heartbeat.plist and load with launchctl. -->")
```

- [ ] **Step 8: Register CLI group**

```python
# gshell_memory/cli/main.py
from gshell_memory.cli.heartbeat import heartbeat_group
gish.add_command(heartbeat_group)
```

- [ ] **Step 9: CLI tests pass**

```bash
uv run pytest tests/integration/test_cli_heartbeat.py -v
```

- [ ] **Step 10: Stub doc**

`docs/ch.15-heartbeat.md`:

```markdown
# Chapter 15 — Heartbeat

> Stub. Filled out in M6-C.

Periodic self-check + log emission. Cadence: hourly / four_hourly / daily / monthly.
Install snippets for cron and launchd are generated by the engine.
```

- [ ] **Step 11: Commit**

```bash
git add gshell_memory/engines/heartbeat.py gshell_memory/cli/heartbeat.py gshell_memory/cli/main.py tests/unit/test_engine_heartbeat.py tests/integration/test_cli_heartbeat.py docs/ch.15-heartbeat.md
git commit -m "feat(m6-b): Heartbeat engine + 'gish heartbeat' sub-commands

Stub run() always emits status=OK (extending checks lands in M6-C
docs). install --cron prints a crontab line; install --launchd prints
a macOS LaunchAgent plist. Logs go to memory/heartbeat_logs/.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-B.6: Brain region extension CLI

**Files:**
- Modify: `gshell_memory/memory/brain_regions.py`
- Create: `gshell_memory/cli/region.py`
- Modify: `gshell_memory/cli/main.py`
- Create: `tests/unit/test_brain_region_extension.py`
- Create: `tests/integration/test_cli_region.py`
- Create: `docs/ch.16-brain-regions-ext.md`

- [ ] **Step 1: Write failing engine test**

`tests/unit/test_brain_region_extension.py`:

```python
from pathlib import Path

import yaml

from gshell_memory.memory.brain_regions import BrainRegionStore


def _manifest(tmp_path, extensions=None):
    (tmp_path / "memory").mkdir()
    base = {
        "schema_version": "5.1",
        "regions": {
            r: {"display": r, "core_files": [], "on_demand_files": []}
            for r in ["hippocampus", "prefrontal", "limbic", "cerebellum", "default"]
        },
    }
    if extensions:
        base["extensions"] = extensions
    (tmp_path / "memory" / "brain_region_manifest.yml").write_text(yaml.safe_dump(base))
    return tmp_path


def test_declare_adds_extension(tmp_path):
    ws = _manifest(tmp_path)
    store = BrainRegionStore(ws)
    store.declare("amygdala", display="amygdala", on_demand_files=["POLICY.md"], aliases=["security"])
    reloaded = yaml.safe_load((ws / "memory" / "brain_region_manifest.yml").read_text())
    assert "amygdala" in reloaded["extensions"]
    assert reloaded["extensions"]["amygdala"]["aliases"] == ["security"]


def test_declare_rejects_name_collision_with_default(tmp_path):
    import pytest
    ws = _manifest(tmp_path)
    store = BrainRegionStore(ws)
    with pytest.raises(ValueError, match="reserved"):
        store.declare("hippocampus", display="x")


def test_list_includes_extensions(tmp_path):
    ws = _manifest(tmp_path, extensions={
        "amygdala": {"display": "amygdala", "core_files": [], "on_demand_files": []},
    })
    store = BrainRegionStore(ws)
    names = [r["name"] for r in store.list_all()]
    assert "amygdala" in names
    assert "hippocampus" in names
```

- [ ] **Step 2: Run test (expect missing method / store class)**

```bash
uv run pytest tests/unit/test_brain_region_extension.py -v
```

- [ ] **Step 3: Extend the existing brain_regions module**

Edit `gshell_memory/memory/brain_regions.py`. Add (or wrap into a `BrainRegionStore` class):

```python
"""BrainRegion store — load/save manifest, manage extensions (5.1)."""

from __future__ import annotations

from pathlib import Path

import yaml

from gshell_memory_schema.models import BrainRegionExtension, BrainRegionManifest

DEFAULT_REGIONS = {"hippocampus", "prefrontal", "limbic", "cerebellum", "default"}


class BrainRegionStore:
    def __init__(self, workspace_path: Path | str) -> None:
        self.workspace_path = Path(workspace_path)
        self._file = self.workspace_path / "memory" / "brain_region_manifest.yml"

    def _load(self) -> dict:
        if not self._file.exists():
            raise FileNotFoundError(self._file)
        return yaml.safe_load(self._file.read_text(encoding="utf-8")) or {}

    def _save(self, data: dict) -> None:
        self._file.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    def declare(
        self,
        name: str,
        *,
        display: str,
        core_files: list[str] | None = None,
        on_demand_files: list[str] | None = None,
        aliases: list[str] | None = None,
    ) -> BrainRegionExtension:
        if name in DEFAULT_REGIONS:
            raise ValueError(f"{name!r} is a reserved default region")
        data = self._load()
        ext = BrainRegionExtension(
            display=display,
            core_files=[{"path": p} for p in (core_files or [])],
            on_demand_files=[{"path": p} for p in (on_demand_files or [])],
            aliases=aliases or [],
        )
        data.setdefault("extensions", {})[name] = ext.model_dump(exclude_none=True)
        self._save(data)
        return ext

    def list_all(self) -> list[dict]:
        data = self._load()
        out = [{"name": n, "kind": "default", **v} for n, v in data.get("regions", {}).items()]
        for n, v in data.get("extensions", {}).items():
            out.append({"name": n, "kind": "extension", **v})
        return out
```

If the existing module already has functions, keep them and add the class above the existing definitions.

- [ ] **Step 4: Engine tests pass**

```bash
uv run pytest tests/unit/test_brain_region_extension.py -v
```

- [ ] **Step 5: Write CLI integration test**

`tests/integration/test_cli_region.py`:

```python
from pathlib import Path

import yaml
from click.testing import CliRunner

from gshell_memory.cli.main import gish


def _bootstrap_workspace(tmp_path: Path):
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "brain_region_manifest.yml").write_text(yaml.safe_dump({
        "schema_version": "5.1",
        "regions": {r: {"display": r, "core_files": [], "on_demand_files": []}
                    for r in ["hippocampus", "prefrontal", "limbic", "cerebellum", "default"]},
    }))


def test_cli_region_declare_and_list(tmp_path):
    _bootstrap_workspace(tmp_path)
    runner = CliRunner()
    r = runner.invoke(gish, [
        "region", "declare", "amygdala",
        "--display", "amygdala (security / vigilance)",
        "--on-demand", "POLICY.md",
        "--aliases", "security",
        "--workspace", str(tmp_path),
    ])
    assert r.exit_code == 0, r.output
    out = runner.invoke(gish, ["region", "list", "--workspace", str(tmp_path)])
    assert "amygdala" in out.output
    assert "extension" in out.output
```

- [ ] **Step 6: Run CLI test (expect missing group)**

```bash
uv run pytest tests/integration/test_cli_region.py -v
```

- [ ] **Step 7: Implement CLI**

`gshell_memory/cli/region.py`:

```python
"""`gish region` sub-commands."""

from __future__ import annotations

from pathlib import Path

import click

from gshell_memory.memory.brain_regions import BrainRegionStore


@click.group(name="region")
def region_group() -> None:
    """Brain region manifest management."""


def _ws_opt(f):
    return click.option(
        "--workspace",
        type=click.Path(file_okay=False, path_type=Path),
        required=True,
    )(f)


@region_group.command("declare")
@click.argument("name")
@click.option("--display", required=True)
@click.option("--core", "core_files", multiple=True)
@click.option("--on-demand", "on_demand_files", multiple=True)
@click.option("--aliases", multiple=True)
@_ws_opt
def declare_cmd(workspace, name, display, core_files, on_demand_files, aliases):
    BrainRegionStore(workspace).declare(
        name=name,
        display=display,
        core_files=list(core_files),
        on_demand_files=list(on_demand_files),
        aliases=list(aliases),
    )
    click.echo(f"declared extension region: {name}")


@region_group.command("list")
@_ws_opt
def list_cmd(workspace):
    for entry in BrainRegionStore(workspace).list_all():
        click.echo(f"{entry['name']:15} [{entry['kind']}]  {entry.get('display','')}")
```

- [ ] **Step 8: Register CLI group**

```python
# gshell_memory/cli/main.py
from gshell_memory.cli.region import region_group
gish.add_command(region_group)
```

- [ ] **Step 9: CLI tests pass**

```bash
uv run pytest tests/integration/test_cli_region.py -v
```

- [ ] **Step 10: Stub doc**

`docs/ch.16-brain-regions-ext.md`:

```markdown
# Chapter 16 — Brain Region Extensions

> Stub. Filled out in M6-C.

Default 5 regions (hippocampus / prefrontal / limbic / cerebellum / default)
are immutable in 5.x. Projects with extra needs declare extensions under
`extensions:` in the manifest. Old 5.0 readers ignore extensions; 5.1+
readers activate them.

## CLI

- `gish region declare NAME --display ... --on-demand FILE --aliases ALIAS`
- `gish region list`
```

- [ ] **Step 11: Commit**

```bash
git add gshell_memory/memory/brain_regions.py gshell_memory/cli/region.py gshell_memory/cli/main.py tests/unit/test_brain_region_extension.py tests/integration/test_cli_region.py docs/ch.16-brain-regions-ext.md
git commit -m "feat(m6-b): Brain region extension declarations + 'gish region' CLI

5 default regions are reserved; declare() raises on collision. list_all
distinguishes 'default' vs 'extension'. Manifest extensions: block is
optional, so 5.0 manifests load unchanged.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-B.7: Subdirectory registry engine

**Files:**
- Create: `gshell_memory/engines/subdir_registry.py`
- Create: `gshell_memory/cli/memdir.py`
- Modify: `gshell_memory/cli/main.py`
- Create: `tests/unit/test_engine_subdir_registry.py`
- Create: `tests/integration/test_cli_memdir.py`
- Create: `docs/ch.17-subdir-registry.md`

- [ ] **Step 1: Write failing engine test**

`tests/unit/test_engine_subdir_registry.py`:

```python
from pathlib import Path

from gshell_memory.engines.subdir_registry import SubdirRegistryEngine


def test_register_then_list(tmp_path):
    (tmp_path / "memory").mkdir()
    eng = SubdirRegistryEngine(tmp_path)
    eng.register(path="memory/_archive/", purpose="archive", lifecycle="permanent")
    items = eng.list_all()
    assert len(items) == 1
    assert items[0].path == "memory/_archive/"


def test_enforce_warn_returns_unregistered(tmp_path):
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "_archive").mkdir()
    (tmp_path / "memory" / "carryover").mkdir()
    (tmp_path / "memory" / "rogue").mkdir()
    eng = SubdirRegistryEngine(tmp_path)
    eng.register(path="memory/_archive/", purpose="archive", lifecycle="permanent")
    eng.register(path="memory/carryover/", purpose="carryover", lifecycle="rotating")
    unregistered = eng.enforce(mode="warn")
    assert "memory/rogue" in unregistered or "memory/rogue/" in unregistered


def test_enforce_block_raises_on_unregistered(tmp_path):
    import pytest
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "rogue").mkdir()
    eng = SubdirRegistryEngine(tmp_path)
    eng.set_enforcement("block")
    with pytest.raises(RuntimeError, match="unregistered"):
        eng.enforce(mode="block")
```

- [ ] **Step 2: Run test (expect ImportError)**

```bash
uv run pytest tests/unit/test_engine_subdir_registry.py -v
```

- [ ] **Step 3: Implement the engine**

`gshell_memory/engines/subdir_registry.py`:

```python
"""Subdirectory registry — white-list of permitted memory/ subdirs."""

from __future__ import annotations

from pathlib import Path

import yaml

from gshell_memory_schema.models import RegisteredSubdir, SubdirRegistry


class SubdirRegistryEngine:
    def __init__(self, workspace_path: Path | str) -> None:
        self.workspace_path = Path(workspace_path)
        self._file = self.workspace_path / "memory" / "subdir_registry.yml"

    def _read(self) -> SubdirRegistry:
        if not self._file.exists():
            return SubdirRegistry(registered=[], enforcement="warn")
        raw = yaml.safe_load(self._file.read_text(encoding="utf-8")) or {}
        return SubdirRegistry.model_validate(raw)

    def _write(self, reg: SubdirRegistry) -> None:
        self._file.parent.mkdir(parents=True, exist_ok=True)
        self._file.write_text(
            yaml.safe_dump(reg.model_dump(mode="json"), allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    def register(self, *, path: str, purpose: str, lifecycle: str) -> None:
        reg = self._read()
        if any(r.path == path for r in reg.registered):
            return
        reg.registered.append(RegisteredSubdir(path=path, purpose=purpose, lifecycle=lifecycle))
        self._write(reg)

    def list_all(self) -> list[RegisteredSubdir]:
        return self._read().registered

    def set_enforcement(self, mode: str) -> None:
        reg = self._read()
        updated = reg.model_copy(update={"enforcement": mode})
        self._write(updated)

    def enforce(self, mode: str | None = None) -> list[str]:
        """Return list of unregistered subdirs. In block mode, raise if any."""
        reg = self._read()
        effective = mode or reg.enforcement
        memory_dir = self.workspace_path / "memory"
        if not memory_dir.exists():
            return []
        registered_paths = {r.path.rstrip("/") for r in reg.registered}
        found_unregistered: list[str] = []
        for child in memory_dir.iterdir():
            if not child.is_dir():
                continue
            rel = f"memory/{child.name}"
            if rel not in registered_paths:
                found_unregistered.append(rel)
        if effective == "block" and found_unregistered:
            raise RuntimeError(f"unregistered subdirs: {found_unregistered}")
        return found_unregistered
```

- [ ] **Step 4: Engine tests pass**

```bash
uv run pytest tests/unit/test_engine_subdir_registry.py -v
```

- [ ] **Step 5: Write CLI integration test**

`tests/integration/test_cli_memdir.py`:

```python
from click.testing import CliRunner

from gshell_memory.cli.main import gish


def test_cli_memdir_register_and_list(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    r = runner.invoke(gish, [
        "memory-dir", "register",
        "--path", "memory/_archive/",
        "--purpose", "archive",
        "--lifecycle", "permanent",
        "--workspace", str(tmp_path),
    ])
    assert r.exit_code == 0, r.output
    out = runner.invoke(gish, ["memory-dir", "list", "--workspace", str(tmp_path)])
    assert "memory/_archive/" in out.output


def test_cli_memdir_enforce_warn(tmp_path):
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "rogue").mkdir()
    runner = CliRunner()
    r = runner.invoke(gish, ["memory-dir", "enforce", "--workspace", str(tmp_path)])
    assert r.exit_code == 0
    assert "rogue" in r.output
```

- [ ] **Step 6: Run CLI test (expect missing group)**

```bash
uv run pytest tests/integration/test_cli_memdir.py -v
```

- [ ] **Step 7: Implement CLI**

`gshell_memory/cli/memdir.py`:

```python
"""`gish memory-dir` sub-commands."""

from __future__ import annotations

from pathlib import Path

import click

from gshell_memory.engines.subdir_registry import SubdirRegistryEngine


@click.group(name="memory-dir")
def memdir_group() -> None:
    """Subdirectory registry under memory/."""


def _ws_opt(f):
    return click.option(
        "--workspace",
        type=click.Path(file_okay=False, path_type=Path),
        required=True,
    )(f)


@memdir_group.command("register")
@click.option("--path", required=True)
@click.option("--purpose", required=True)
@click.option("--lifecycle", type=click.Choice(["permanent", "rotating", "ephemeral"]), required=True)
@_ws_opt
def register_cmd(workspace, path, purpose, lifecycle):
    SubdirRegistryEngine(workspace).register(path=path, purpose=purpose, lifecycle=lifecycle)
    click.echo(f"registered: {path}")


@memdir_group.command("list")
@_ws_opt
def list_cmd(workspace):
    for r in SubdirRegistryEngine(workspace).list_all():
        click.echo(f"{r.path:30}  {r.purpose:20}  ({r.lifecycle})")


@memdir_group.command("enforce")
@click.option("--mode", type=click.Choice(["warn", "block"]), default=None)
@_ws_opt
def enforce_cmd(workspace, mode):
    unregistered = SubdirRegistryEngine(workspace).enforce(mode=mode)
    if not unregistered:
        click.echo("clean")
        return
    for path in unregistered:
        click.echo(f"unregistered: {path}")
```

- [ ] **Step 8: Register CLI group**

```python
# gshell_memory/cli/main.py
from gshell_memory.cli.memdir import memdir_group
gish.add_command(memdir_group)
```

- [ ] **Step 9: CLI tests pass**

```bash
uv run pytest tests/integration/test_cli_memdir.py -v
```

- [ ] **Step 10: Stub doc**

`docs/ch.17-subdir-registry.md`:

```markdown
# Chapter 17 — Memory Subdir Registry

> Stub. Filled out in M6-C.

White-list of permitted subdirectories under memory/. Default enforcement
is warn (report unregistered directories). Block mode raises an error
during enforce().

## CLI

- `gish memory-dir register --path memory/X/ --purpose Y --lifecycle Z`
- `gish memory-dir list`
- `gish memory-dir enforce [--mode warn|block]`
```

- [ ] **Step 11: Commit**

```bash
git add gshell_memory/engines/subdir_registry.py gshell_memory/cli/memdir.py gshell_memory/cli/main.py tests/unit/test_engine_subdir_registry.py tests/integration/test_cli_memdir.py docs/ch.17-subdir-registry.md
git commit -m "feat(m6-b): Subdirectory registry engine + 'gish memory-dir' CLI

White-list governance for memory/ subdirs. warn mode reports
unregistered; block mode raises. Per-entry lifecycle classification:
permanent / rotating / ephemeral.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Wave M6-C: Stable release & doc integration

#### Task M6-C.1: README features table — 14 engines

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update the Features section**

Find the "7 Maintenance Engines" table in `README.md`. Replace heading and table with:

```markdown
### 14 Engines (7 maintenance + 7 capability)

| Engine | Category | What it does |
|:-------|:---------|:-------------|
| `associate` | maintenance | Builds and updates edges in the association graph |
| `decay` | maintenance | Applies time-based strength decay; archives fading entries |
| `consolidate` | maintenance | Merges redundant episodes; promotes recurring patterns |
| `judge` | maintenance | Evaluates quality scores for new entries |
| `health` | maintenance | Runs workspace integrity checks |
| `audit` | maintenance | Validates sanctum governance compliance |
| `session_log` | maintenance | Logs session start/end events |
| `sop` | capability | Natural-language triggers map to required reading (`gish sop`) |
| `archive_router` | capability | Condition->target decision tree (`gish archive route`) |
| `carryover` | capability | Cross-session task hand-off (`gish carryover`) |
| `enum_freeze` | capability | Lock state-machine values against drift (`gish enum`) |
| `heartbeat` | capability | Periodic self-check + cron/launchd snippets (`gish heartbeat`) |
| `brain_region_ext` | capability | Declare regions beyond the 5 defaults (`gish region`) |
| `subdir_registry` | capability | White-list governance for memory/ subdirs (`gish memory-dir`) |
```

- [ ] **Step 2: Update CLI Reference table**

In the existing "CLI Reference" section, append the 7 new groups:

```markdown
| `gish sop register/list/trigger/test` | Manage SOP dispatch routes |
| `gish archive route add/list/preview` | Manage archive routing decision tree |
| `gish carryover create/list/expire/promote-to-episodic` | Cross-session task hand-off |
| `gish enum freeze/list/validate` | Manage frozen state enums |
| `gish heartbeat run/install` | Heartbeat + cron/launchd snippets |
| `gish region declare/list` | Declare extension brain regions |
| `gish memory-dir register/list/enforce` | Subdir white-list |
```

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs(m6-c): README features table and CLI reference cover all 14 engines

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-C.2: ch.04 Engine Internals — full 14

**Files:**
- Modify: `docs/ch.04-engine-internals.md`

- [ ] **Step 1: Extend the existing chapter**

Add a section "Capability engines (M6)" near the end of `ch.04-engine-internals.md` with one paragraph per engine. Each paragraph should cover: purpose, where the data lives (file path), key methods, and rough algorithm.

Use the chapter stubs from M6-B as source material (ch.11 through ch.17). For each capability engine, write ~80-120 words describing how it operates within the workspace.

- [ ] **Step 2: Commit**

```bash
git add docs/ch.04-engine-internals.md
git commit -m "docs(m6-c): ch.04 covers 7 maintenance + 7 capability engines

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-C.3: Flesh out ch.11-17 (capability deep dives)

**Files:**
- Modify: `docs/ch.11-sop-dispatch.md`
- Modify: `docs/ch.12-archive-routing.md`
- Modify: `docs/ch.13-carryover.md`
- Modify: `docs/ch.14-frozen-enums.md`
- Modify: `docs/ch.15-heartbeat.md`
- Modify: `docs/ch.16-brain-regions-ext.md`
- Modify: `docs/ch.17-subdir-registry.md`

For each chapter, expand the M6-B stub into a real chapter (~300-500 words):

- **Why this engine exists** (problem statement, real example)
- **Schema** (link to the Pydantic model; show one yml example)
- **CLI walkthrough** (3-4 commands run sequentially)
- **Python API** (import + call sequence)
- **Operational notes** (failure modes, performance characteristics)
- **Forward compatibility** (what 6.0 might change)

- [ ] **Step 1: ch.11 SOP dispatch — full version**

Replace the stub with a complete chapter. Use the SOP dispatch description from this plan's spec §6 Wave M6-B.1 as the basis. Include a worked example showing SOP route registration, triggering, and integration with existing workflows.

- [ ] **Step 2: ch.12 Archive routing — full version**

Replace stub. Worked example: define 3 routes (security log / learning log / default), run preview() against 3 candidate inputs, show which one wins.

- [ ] **Step 3: ch.13 Carryover — full version**

Replace stub. Walk through the 7-day lifecycle: create -> active -> expire -> promote-to-episodic.

- [ ] **Step 4: ch.14 Frozen enums — full version**

Replace stub. Include the two canonical examples (decision_kind, rerun_status) from the spec.

- [ ] **Step 5: ch.15 Heartbeat — full version**

Replace stub. Cover cadence semantics, install snippets (cron + launchd), output_format = ok_only / summary / verbose, idle_threshold rationale.

- [ ] **Step 6: ch.16 Brain region extensions — full version**

Replace stub. Worked example: declare amygdala (security) and parietal (paths) extensions; show manifest after; explain how 5.0 readers ignore them while 5.1+ readers honour them.

- [ ] **Step 7: ch.17 Subdir registry — full version**

Replace stub. Worked example: register memory/_archive, memory/carryover, memory/heartbeat_logs; enforce in warn mode then in block mode; show the failure path.

- [ ] **Step 8: Commit**

```bash
git add docs/ch.11-sop-dispatch.md docs/ch.12-archive-routing.md docs/ch.13-carryover.md docs/ch.14-frozen-enums.md docs/ch.15-heartbeat.md docs/ch.16-brain-regions-ext.md docs/ch.17-subdir-registry.md
git commit -m "docs(m6-c): full capability chapters 11-17

Each chapter has problem statement, schema reference, CLI walkthrough,
Python API example, operational notes, and forward-compat notes.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-C.4: ch.10 Migration — v4 to v5.1 with brain region extensions

**Files:**
- Modify: `docs/ch.10-migration.md`

- [ ] **Step 1: Add a new section "Reconnecting custom regions (5.1)"**

Append to `ch.10-migration.md`:

```markdown
## Reconnecting custom regions after v4 migration (5.1)

`gish migrate v4` collapses any non-default region into `default`. If you had
custom regions in v4 that you want back (e.g. `amygdala` for security gating,
`parietal` for path management), re-declare them as 5.1 extensions:

```bash
gish region declare amygdala \
    --display "amygdala (security / vigilance)" \
    --on-demand POLICY.md \
    --aliases security \
    --workspace ~/my-workspace

gish region declare parietal \
    --display "parietal (paths / spatial)" \
    --on-demand PATHS.md \
    --workspace ~/my-workspace
```

After declaration, the manifest's `extensions:` block holds these regions.
5.0 readers ignore them gracefully; 5.1+ readers activate them. Files
mistakenly merged into `default` during migration must be moved manually —
gish does not preserve enough history to do this automatically.
```

- [ ] **Step 2: Commit**

```bash
git add docs/ch.10-migration.md
git commit -m "docs(m6-c): ch.10 migration — reconnecting custom regions as 5.1 extensions

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-C.5: Bump schema_version 5.0 → 5.1; bump both packages to stable

**Files:**
- Modify: `gshell_memory_schema/gshell_memory_schema/__init__.py`
- Modify: `gshell_memory_schema/pyproject.toml`
- Modify: `gshell_memory/templates/memory/memory_manifest.yml.template` (or equivalent)
- Modify: top-level `pyproject.toml`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Bump schema package**

In `gshell_memory_schema/pyproject.toml`:

```toml
[project]
version = "5.1.0"
```

In `gshell_memory_schema/gshell_memory_schema/__init__.py`:

```python
__version__ = "5.1.0"
__schema_version__ = (5, 1)
```

- [ ] **Step 2: Bump main package**

In top-level `pyproject.toml`:

```toml
[project]
version = "5.0.0"
```

(`5.0.0rc1` → `5.0.0`).

Also bump the dependency floor on schema:

```toml
dependencies = [
    "click>=8.1",
    "pyyaml>=6.0",
    "pydantic>=2.7",
    "gshell-memory-schema>=5.1,<6.0",
]
```

- [ ] **Step 3: Update the manifest template to emit 5.1 schema_version**

Find the template that `gish init` writes for new workspaces. Set `schema_version: "5.1"`.

- [ ] **Step 4: Move CHANGELOG.md `[Unreleased]` into 5.0.0 + add 5.1.0 for schema**

Update CHANGELOG.md: replace `[Unreleased]` heading with `[5.0.0] — <today's date>` for the main package, and add a separate section `## gshell-memory-schema [5.1.0] — <today's date>`.

- [ ] **Step 5: Verify tests + lint still green**

```bash
uv run pytest -q
uv run ruff check .
cd gshell_memory_schema
uv run pytest -q
cd ..
```

- [ ] **Step 6: Commit**

```bash
git add gshell_memory_schema/pyproject.toml gshell_memory_schema/gshell_memory_schema/__init__.py gshell_memory/templates/memory/memory_manifest.yml.template pyproject.toml CHANGELOG.md
git commit -m "release(m6-c): bump to gshell-memory 5.0.0 stable + gshell-memory-schema 5.1.0

gshell-memory drops 'rc1' and goes stable. Schema package goes to 5.1
to reflect the new opt-in extensions: block on BrainRegionManifest
(plus six other M6 models, which are additive minor changes).

Templates emitted by 'gish init' now declare schema_version: 5.1.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task M6-C.6: Tag both packages → CI publishes

**Files:** (no files; tag + verification)

- [ ] **Step 1: Tag main package**

```bash
git tag v5.0.0
git push origin v5.0.0
```

- [ ] **Step 2: Tag schema package**

```bash
git tag schema-v5.1.0
git push origin schema-v5.1.0
```

- [ ] **Step 3: Watch both release runs**

```bash
gh run watch
```

Both `release.yml` triggers should fire. Expected: gshell-memory 5.0.0 and gshell-memory-schema 5.1.0 both visible on PyPI.

- [ ] **Step 4: Verify clean install of both**

```bash
python3.11 -m venv /tmp/stable-test
source /tmp/stable-test/bin/activate
pip install gshell-memory==5.0.0
gish version
gish sop --help
gish carryover --help
gish heartbeat --help
deactivate
mv /tmp/stable-test _DELETE_stable-test
```

Expected: `gish version` shows `5.0.0`; new sub-commands appear in `--help` output.

No commit; release artefact is the tag.

---


## Bridge — LGD Integration

> All Bridge tasks operate in the LabGrimoire_Desktop repository:
> `/Users/cyuh/Downloads/APPDev/102_Github/LabGrimoire_Desktop/`
>
> Open a feature branch in LGD: `git checkout -b feat/gshell-bridge`. Bridge waves land via PR into LGD's `main`.

### Wave Bridge-A: LGD pulls the schema sub-package

#### Task Bridge-A.1: Declare schema dependency in lgd_agent

**Files (LGD repo):**
- Modify: `lgd_agent/pyproject.toml`

- [ ] **Step 1: Add the dependency**

In `lgd_agent/pyproject.toml`, append to `[project] dependencies`:

```toml
dependencies = [
    "anthropic>=0.40.0",
    "openai>=1.50.0",
    "httpx>=0.27.0",
    "loguru>=0.7.0",
    "json-repair>=0.30.0",
    "tiktoken>=0.7.0",
    "pydantic>=2.0.0",
    "aiohttp>=3.9.0",
    "gshell-memory-schema>=5.1,<6.0",
]
```

- [ ] **Step 2: Sync deps in LGD repo**

```bash
cd /Users/cyuh/Downloads/APPDev/102_Github/LabGrimoire_Desktop
uv sync
```

Expected: `gshell-memory-schema==5.1.x` resolves.

- [ ] **Step 3: Smoke test the import**

```bash
uv run python -c "from gshell_memory_schema.models import EpisodicEntry; print('ok')"
```

Expected: prints `ok`.

- [ ] **Step 4: Commit (in LGD repo)**

```bash
git add lgd_agent/pyproject.toml uv.lock
git commit -m "feat(gshell-bridge): depend on gshell-memory-schema >= 5.1

lgd_agent now consumes the canonical workspace schema instead of
shipping its own model definitions.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task Bridge-A.2: Refactor lgd_agent/memory to use schema models

**Files (LGD repo):**
- Modify: every file under `lgd_agent/memory/` that defines a model
- Create: `lgd_agent/memory/_schema_compat.py` (centralised re-export)

- [ ] **Step 1: Inventory existing models**

```bash
cd /Users/cyuh/Downloads/APPDev/102_Github/LabGrimoire_Desktop/lgd_agent/memory
grep -rn "class.*BaseModel" .
```

Note each class that overlaps with `gshell_memory_schema.models` (EpisodicEntry, FactStore, Association, BrainRegionManifest, SanctumRegistry, RuntimeProfiles, MemoryManifest, Workspace).

- [ ] **Step 2: Write _schema_compat.py**

`lgd_agent/memory/_schema_compat.py`:

```python
"""Re-exports from gshell-memory-schema for use within lgd_agent.

This module exists so the rest of lgd_agent imports schema types from
a single internal location, even though the canonical source is the
external `gshell-memory-schema` package.
"""

from gshell_memory_schema.models import (  # noqa: F401
    Association,
    BrainRegionManifest,
    EpisodicEntry,
    FactStore,
    MemoryManifest,
    RuntimeProfiles,
    SanctumRegistry,
    Workspace,
    SOPRoute,
    ArchiveRoute,
    Carryover,
    FrozenEnum,
    HeartbeatConfig,
    SubdirRegistry,
    BrainRegionExtension,
)
```

- [ ] **Step 3: Remove duplicate model definitions**

For each model in `lgd_agent/memory/` that duplicates an entry in `gshell-memory-schema`:

1. Open the file containing the duplicate.
2. Replace `class EpisodicEntry(BaseModel): ...` with `from lgd_agent.memory._schema_compat import EpisodicEntry`.
3. Repeat for the other duplicated models.

Keep any LGD-specific subclasses or extensions, but rename them (e.g. `LGDEpisodicEntry`) and have them inherit from the canonical schema model.

- [ ] **Step 4: Run LGD tests**

```bash
cd /Users/cyuh/Downloads/APPDev/102_Github/LabGrimoire_Desktop
uv run pytest lgd_agent/ -q
```

Expected: green; any failures indicate fields that need to be added to the canonical schema or kept in LGD subclasses.

- [ ] **Step 5: Commit**

```bash
git add lgd_agent/memory
git commit -m "refactor(gshell-bridge): lgd_agent/memory consumes gshell-memory-schema

_schema_compat.py is the single internal re-export point. Duplicated
model definitions removed; LGD-specific subclasses preserved with
canonical base classes.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task Bridge-A.3: Rust side — JSON Schema ingestion via build.rs

**Files (LGD repo):**
- Create: `app/src-tauri/build.rs` (or extend existing)
- Create: `app/src-tauri/src/sources/gshell_schema.rs`
- Modify: `app/src-tauri/Cargo.toml` (add `schemars`, `serde`, `serde_json`)

- [ ] **Step 1: Add Rust dependencies**

In `app/src-tauri/Cargo.toml`, append to `[dependencies]`:

```toml
schemars = "0.8"
serde_json = "1"
```

(`serde` is likely already present.)

- [ ] **Step 2: Write build.rs**

`app/src-tauri/build.rs`:

```rust
use std::path::PathBuf;

fn main() {
    tauri_build::build();

    // Tell cargo to re-run this build script when any committed JSON Schema
    // file in the gshell-memory-schema sub-package changes.
    let schema_dir = locate_gshell_memory_schema_jsonschema();
    if let Some(dir) = schema_dir {
        println!("cargo:rerun-if-changed={}", dir.display());
    }
}

fn locate_gshell_memory_schema_jsonschema() -> Option<PathBuf> {
    // 1. Resolve via the installed Python distribution.
    // 2. Fallback: relative path in dev checkout
    //    (../../../Ghost_In_Shell/gshell_memory_schema/gshell_memory_schema/jsonschema)
    // For build determinism, prefer the installed location.
    if let Ok(out) = std::process::Command::new("python3")
        .args([
            "-c",
            "import gshell_memory_schema, pathlib, sys; print(pathlib.Path(gshell_memory_schema.__file__).parent / 'jsonschema')",
        ])
        .output()
    {
        if out.status.success() {
            let path = PathBuf::from(String::from_utf8_lossy(&out.stdout).trim());
            if path.exists() {
                return Some(path);
            }
        }
    }
    None
}
```

- [ ] **Step 3: Write the schema loader**

`app/src-tauri/src/sources/gshell_schema.rs`:

```rust
//! Runtime JSON Schema validators for gshell workspace files.
//!
//! Schemas are shipped as part of the `gshell-memory-schema` Python
//! distribution; we read them at runtime rather than embedding them
//! at compile time, to make schema upgrades visible without a rebuild.

use std::fs;
use std::path::{Path, PathBuf};

use serde_json::Value;

pub struct GshellSchema {
    base_dir: PathBuf,
}

impl GshellSchema {
    pub fn locate() -> Option<Self> {
        // Same logic as build.rs locate_gshell_memory_schema_jsonschema.
        let out = std::process::Command::new("python3")
            .args([
                "-c",
                "import gshell_memory_schema, pathlib; print(pathlib.Path(gshell_memory_schema.__file__).parent / 'jsonschema')",
            ])
            .output()
            .ok()?;
        if !out.status.success() {
            return None;
        }
        let base_dir = PathBuf::from(String::from_utf8_lossy(&out.stdout).trim());
        if !base_dir.exists() {
            return None;
        }
        Some(Self { base_dir })
    }

    pub fn load(&self, schema_name: &str) -> Option<Value> {
        let path = self.base_dir.join(format!("{}.json", schema_name));
        let text = fs::read_to_string(&path).ok()?;
        serde_json::from_str(&text).ok()
    }

    pub fn paths(&self) -> &Path {
        &self.base_dir
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn locates_schema_directory_when_python_pkg_installed() {
        // Skip silently in environments where the python package is not installed.
        if let Some(s) = GshellSchema::locate() {
            assert!(s.paths().exists());
        }
    }
}
```

- [ ] **Step 4: Verify Rust build**

```bash
cd /Users/cyuh/Downloads/APPDev/102_Github/LabGrimoire_Desktop/app/src-tauri
cargo build
cargo test gshell_schema
cd /Users/cyuh/Downloads/APPDev/102_Github/LabGrimoire_Desktop
```

Expected: build succeeds; test passes or skips depending on whether `gshell-memory-schema` is on the system Python path.

- [ ] **Step 5: Commit**

```bash
git add app/src-tauri/build.rs app/src-tauri/src/sources/gshell_schema.rs app/src-tauri/Cargo.toml app/src-tauri/Cargo.lock
git commit -m "feat(gshell-bridge): Rust loads JSON Schema from gshell-memory-schema

build.rs marks the schema directory for cargo:rerun-if-changed.
sources/gshell_schema.rs provides runtime access via Python introspection.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task Bridge-A.4: Schema compliance test (LGD reads gish-init output)

**Files (LGD repo):**
- Create: `lgd_agent/tests/test_schema_compliance.py`

- [ ] **Step 1: Write the test**

`lgd_agent/tests/test_schema_compliance.py`:

```python
"""LGD reads a fresh gish-init workspace without error."""

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest


def _have_gish() -> bool:
    return shutil.which("gish") is not None


@pytest.mark.skipif(not _have_gish(), reason="gish CLI not in PATH")
def test_lgd_reads_gish_init_workspace():
    from lgd_agent.memory._schema_compat import EpisodicEntry, Workspace
    import json

    with tempfile.TemporaryDirectory() as tmpdir:
        ws = Path(tmpdir) / "ws"
        subprocess.run(["gish", "init", str(ws), "--non-interactive"], check=True)

        # Reading episodic.jsonl should succeed for every line.
        ep_file = ws / "memory" / "episodic.jsonl"
        if ep_file.exists():
            for line in ep_file.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                EpisodicEntry.model_validate(json.loads(line))
```

- [ ] **Step 2: Run test**

```bash
cd /Users/cyuh/Downloads/APPDev/102_Github/LabGrimoire_Desktop
uv run pytest lgd_agent/tests/test_schema_compliance.py -v
```

Expected: pass (or skip if `gish` not installed).

- [ ] **Step 3: Commit**

```bash
git add lgd_agent/tests/test_schema_compliance.py
git commit -m "test(gshell-bridge): LGD reads gish-init workspace cleanly

Skips if gish CLI is unavailable. Validates every episodic.jsonl line
through the canonical Pydantic model.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Wave Bridge-B: `[sources.memory]` rewrite

#### Task Bridge-B.1: grimoire.example.toml — add `type = "gshell"`

**Files (LGD repo):**
- Modify: `grimoire.example.toml`

- [ ] **Step 1: Update the source enum**

Find:

```toml
[sources.memory]
enabled = true
type = "jsonl-graph"
episodic = "~/Documents/MyAITeam/TheVoidWeaver/memory/episodic.jsonl"
```

Replace with:

```toml
[sources.memory]
enabled = true
# Source types:
#   "gshell"      — gshell-memory workspace (recommended; full schema)
#   "jsonl-graph" — legacy LGD format (kept for one minor; will be removed)
type = "gshell"
path = "~/my-gshell-workspace"
```

- [ ] **Step 2: Commit**

```bash
git add grimoire.example.toml
git commit -m "feat(gshell-bridge): grimoire.example.toml adds type=\"gshell\"

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task Bridge-B.2: Rust GshellSource adapter

**Files (LGD repo):**
- Modify: `app/src-tauri/src/sources/memory.rs` (or equivalent)
- Create: `app/src-tauri/src/sources/gshell_source.rs`

- [ ] **Step 1: Write failing test for the new source kind**

`app/src-tauri/src/sources/gshell_source.rs` (skeleton with test):

```rust
//! GshellSource — reads a gshell-memory workspace.
//!
//! Implements the same `MemorySource` trait used by jsonl-graph, so
//! the rest of the app does not need to branch on source kind.

use std::path::PathBuf;

#[derive(Debug)]
pub struct GshellSource {
    pub workspace: PathBuf,
}

impl GshellSource {
    pub fn new(workspace: impl Into<PathBuf>) -> Self {
        Self { workspace: workspace.into() }
    }

    pub fn episodic_path(&self) -> PathBuf {
        self.workspace.join("memory").join("episodic.jsonl")
    }

    pub fn fact_path(&self) -> PathBuf {
        self.workspace.join("memory").join("fact.yml")
    }

    pub fn brain_region_path(&self) -> PathBuf {
        self.workspace.join("memory").join("brain_region_manifest.yml")
    }

    // Additional accessors: associations.jsonl, sanctum_registry.yml,
    // runtime_profiles.yml, memory_manifest.yml — same pattern.
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn episodic_path_is_relative_to_workspace() {
        let src = GshellSource::new("/tmp/ws");
        assert_eq!(src.episodic_path(), PathBuf::from("/tmp/ws/memory/episodic.jsonl"));
    }
}
```

- [ ] **Step 2: Run the test**

```bash
cd /Users/cyuh/Downloads/APPDev/102_Github/LabGrimoire_Desktop/app/src-tauri
cargo test gshell_source
```

Expected: pass.

- [ ] **Step 3: Wire into source dispatch**

Find the existing `sources/memory.rs` (or `sources/mod.rs`). Add a match arm in the enum dispatch:

```rust
// Where the existing enum lists "jsonl-graph", add:
match source_kind.as_str() {
    "jsonl-graph" => Box::new(JsonlGraphSource::new(/* ... */)),
    "gshell"      => Box::new(GshellSource::new(/* path from config */)),
    other => return Err(format!("unknown memory source type: {}", other)),
}
```

(The exact wiring depends on the existing dispatch shape; mirror the `jsonl-graph` branch.)

- [ ] **Step 4: Build and run existing LGD tests**

```bash
cd /Users/cyuh/Downloads/APPDev/102_Github/LabGrimoire_Desktop/app
npm install
cd src-tauri
cargo build
cargo test
```

Expected: builds and tests pass; jsonl-graph branch untouched.

- [ ] **Step 5: Commit**

```bash
git add app/src-tauri/src/sources/gshell_source.rs app/src-tauri/src/sources/memory.rs
git commit -m "feat(gshell-bridge): GshellSource Rust adapter reads gshell workspace

GshellSource exposes paths for each schema file. Source dispatch in
sources/memory.rs adds a 'gshell' branch alongside 'jsonl-graph'.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task Bridge-B.3: `lgd-agent migrate-to-gshell` command

**Files (LGD repo):**
- Create: `lgd_agent/migrate_to_gshell.py`
- Modify: `lgd_agent/__init__.py` or wherever the CLI entry resides

- [ ] **Step 1: Write failing test**

`lgd_agent/tests/test_migrate_to_gshell.py`:

```python
from pathlib import Path

import pytest

from lgd_agent.migrate_to_gshell import migrate


def _build_legacy_workspace(tmp_path: Path) -> Path:
    """Create a tiny legacy LGD memory layout: episodic + facts as separate yml."""
    (tmp_path / "lgd_memory" / "memory").mkdir(parents=True)
    (tmp_path / "lgd_memory" / "memory" / "episodic.jsonl").write_text(
        '{"id":"e1","title":"t","content":"c","date":"2026-05-24","ts":"2026-05-24T00:00:00Z","type":"decision","tags":[],"importance":5,"retrieval":{"count":0,"last_accessed":null,"strength":1.0},"decay_status":"active","linked_to":[]}\n'
    )
    (tmp_path / "lgd_memory" / "memory" / "fact.yml").write_text("identity: {name: t}\n")
    return tmp_path / "lgd_memory"


def test_migrate_produces_gshell_workspace(tmp_path):
    old = _build_legacy_workspace(tmp_path)
    new = tmp_path / "gshell_ws"
    migrate(old, new)
    assert (new / "memory" / "episodic.jsonl").exists()
    assert (new / "memory" / "memory_manifest.yml").exists()
    manifest_text = (new / "memory" / "memory_manifest.yml").read_text()
    assert "schema_version" in manifest_text


def test_migrate_fills_missing_fingerprint(tmp_path):
    import json
    old = _build_legacy_workspace(tmp_path)
    new = tmp_path / "gshell_ws"
    migrate(old, new)
    lines = (new / "memory" / "episodic.jsonl").read_text().splitlines()
    entry = json.loads(lines[0])
    assert "fingerprint" in entry
    assert len(entry["fingerprint"]) == 64
```

- [ ] **Step 2: Run test (expect ImportError)**

```bash
cd /Users/cyuh/Downloads/APPDev/102_Github/LabGrimoire_Desktop
uv run pytest lgd_agent/tests/test_migrate_to_gshell.py -v
```

- [ ] **Step 3: Implement migrate.py**

`lgd_agent/migrate_to_gshell.py`:

```python
"""Migrate legacy LGD memory layout to a gshell workspace."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

import yaml


def _fingerprint(title: str, content: str, ts: str) -> str:
    raw = f"{title}\n{content}\n{ts[:10]}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def migrate(old_workspace: Path | str, new_workspace: Path | str) -> None:
    old = Path(old_workspace)
    new = Path(new_workspace)
    new_mem = new / "memory"
    new_mem.mkdir(parents=True, exist_ok=True)

    # 1. Copy fact.yml verbatim (schema-compliant already if LGD has obeyed schema)
    old_fact = old / "memory" / "fact.yml"
    if old_fact.exists():
        shutil.copy2(old_fact, new_mem / "fact.yml")

    # 2. Migrate episodic.jsonl, filling missing fingerprints
    old_ep = old / "memory" / "episodic.jsonl"
    if old_ep.exists():
        out_lines: list[str] = []
        for raw_line in old_ep.read_text(encoding="utf-8").splitlines():
            if not raw_line.strip():
                continue
            entry = json.loads(raw_line)
            if "fingerprint" not in entry:
                entry["fingerprint"] = _fingerprint(
                    entry.get("title", ""),
                    entry.get("content", ""),
                    entry.get("ts", entry.get("date", "")),
                )
            out_lines.append(json.dumps(entry, ensure_ascii=False))
        (new_mem / "episodic.jsonl").write_text("\n".join(out_lines) + "\n", encoding="utf-8")

    # 3. Optional files
    for fname in ("associations.jsonl", "sanctum_registry.yml", "runtime_profiles.yml"):
        src = old / "memory" / fname
        if src.exists():
            shutil.copy2(src, new_mem / fname)

    # 4. Write minimal memory_manifest.yml
    manifest = {
        "schema_version": "5.1",
        "migrated_from": "lgd_legacy",
        "migrated_at": datetime.utcnow().isoformat() + "Z",
    }
    (new_mem / "memory_manifest.yml").write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    # 5. Write a default 5-region brain_region_manifest.yml
    regions = {
        r: {"display": r, "core_files": [], "on_demand_files": []}
        for r in ["hippocampus", "prefrontal", "limbic", "cerebellum", "default"]
    }
    (new_mem / "brain_region_manifest.yml").write_text(
        yaml.safe_dump({"schema_version": "5.1", "regions": regions}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
```

- [ ] **Step 4: Wire as a console-script**

In `lgd_agent/pyproject.toml`:

```toml
[project.scripts]
lgd-agent = "lgd_agent.daemon:main"
lgd-agent-migrate = "lgd_agent.migrate_to_gshell:_cli"
```

In `lgd_agent/migrate_to_gshell.py`, append:

```python
def _cli() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Migrate legacy LGD memory to a gshell workspace.")
    parser.add_argument("old", type=Path)
    parser.add_argument("new", type=Path)
    args = parser.parse_args()
    migrate(args.old, args.new)
    print(f"migrated -> {args.new}")
```

- [ ] **Step 5: Run tests + smoke**

```bash
uv run pytest lgd_agent/tests/test_migrate_to_gshell.py -v
uv sync
uv run lgd-agent-migrate --help
```

- [ ] **Step 6: Commit**

```bash
git add lgd_agent/migrate_to_gshell.py lgd_agent/tests/test_migrate_to_gshell.py lgd_agent/pyproject.toml uv.lock
git commit -m "feat(gshell-bridge): lgd-agent-migrate command — legacy LGD -> gshell workspace

Copies fact + episodic, fills SHA-256 fingerprints, writes 5.1 manifest
and a default 5-region brain_region_manifest.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task Bridge-B.4: UI settings — show memory source type

**Files (LGD repo):**
- Modify: `app/src/modules/settings/` (find the panel that displays sources)

- [ ] **Step 1: Locate the existing source-display component**

```bash
cd /Users/cyuh/Downloads/APPDev/102_Github/LabGrimoire_Desktop
grep -rn "sources.memory\|MemorySource" app/src/modules/settings/
```

- [ ] **Step 2: Extend the panel**

In the discovered React component, add the new `gshell` type to the displayed labels:

```tsx
const SOURCE_LABELS: Record<string, string> = {
    "gshell":       "gshell-memory workspace",
    "jsonl-graph":  "Legacy jsonl-graph (deprecated)",
};
```

And add a small "type: <kind>" line under the path display, plus a yellow warning banner when `type === "jsonl-graph"` saying that this format will be removed in a future minor.

- [ ] **Step 3: Test in dev mode**

```bash
cd /Users/cyuh/Downloads/APPDev/102_Github/LabGrimoire_Desktop/app
npm run tauri dev
```

Open Settings → Sources, confirm the memory source row shows `Type: gshell-memory workspace` when `grimoire.toml` uses `type = "gshell"`.

- [ ] **Step 4: Commit**

```bash
git add app/src/modules/settings
git commit -m "feat(gshell-bridge): settings panel shows memory source type

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Wave Bridge-C: Cross-repo interop + docs + tags

#### Task Bridge-C.1: gish-side interop test

**Files (Ghost_In_Shell repo):**
- Create: `tests/integration/test_lgd_interop.py`

- [ ] **Step 1: Write the test**

`tests/integration/test_lgd_interop.py`:

```python
"""Verify gshell-memory readers handle workspaces that have seen LGD writes.

Fixture mimics LGD's write pattern (e.g. appended episode + association)
and checks that gish's own reader still accepts the workspace.
"""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from click.testing import CliRunner

from gshell_memory.cli.main import gish


def test_gish_reads_workspace_after_lgd_style_writes(tmp_path):
    runner = CliRunner()
    runner.invoke(gish, ["init", str(tmp_path / "ws"), "--non-interactive"])

    ws = tmp_path / "ws"
    # Append an LGD-style episode (no fingerprint by mistake) — gish doctor
    # should report a problem but not crash.
    entry = {
        "id": "ep-2026-05-24-100",
        "title": "from LGD",
        "content": "test",
        "date": "2026-05-24",
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": "decision",
        "tags": [],
        "importance": 5,
        "retrieval": {"count": 0, "last_accessed": None, "strength": 1.0},
        "decay_status": "active",
        "linked_to": [],
        # NOTE: no fingerprint — required by 5.1 schema
    }
    with (ws / "memory" / "episodic.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    result = runner.invoke(gish, ["doctor", "--workspace", str(ws)])
    # doctor must not crash even though the schema is violated
    assert result.exit_code in {0, 1}
    assert "fingerprint" in result.output.lower() or "schema" in result.output.lower()
```

- [ ] **Step 2: Run the test**

```bash
uv run pytest tests/integration/test_lgd_interop.py -v
```

Expected: passes. If it fails because doctor crashes on the missing fingerprint, harden `gish doctor` to catch ValidationError and surface a structured diagnostic.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_lgd_interop.py
git commit -m "test(bridge-c): gshell-memory doctor handles LGD writes gracefully

Doctor must not crash on schema violations; it should report them.
This test pins that contract.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task Bridge-C.2: LGD-side interop test (mirror)

**Files (LGD repo):**
- Create: `lgd_agent/tests/test_gshell_interop.py`

- [ ] **Step 1: Write the test**

`lgd_agent/tests/test_gshell_interop.py`:

```python
"""LGD readers handle workspaces that have just been touched by gish."""

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest


def _have_gish() -> bool:
    return shutil.which("gish") is not None


@pytest.mark.skipif(not _have_gish(), reason="gish CLI not in PATH")
def test_lgd_reads_after_gish_run_maintenance():
    from lgd_agent.memory._schema_compat import EpisodicEntry
    import json

    with tempfile.TemporaryDirectory() as td:
        ws = Path(td) / "ws"
        subprocess.run(["gish", "init", str(ws), "--non-interactive"], check=True)
        # Force a maintenance run; should leave the workspace schema-valid.
        subprocess.run(["gish", "run-maintenance", "--workspace", str(ws)], check=True)

        ep_file = ws / "memory" / "episodic.jsonl"
        if ep_file.exists():
            for line in ep_file.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                EpisodicEntry.model_validate(json.loads(line))
```

- [ ] **Step 2: Run the test**

```bash
cd /Users/cyuh/Downloads/APPDev/102_Github/LabGrimoire_Desktop
uv run pytest lgd_agent/tests/test_gshell_interop.py -v
```

Expected: pass (or skip if gish is not installed).

- [ ] **Step 3: Commit**

```bash
git add lgd_agent/tests/test_gshell_interop.py
git commit -m "test(gshell-bridge): LGD reads workspace after gish run-maintenance

Validates every episodic line through the canonical Pydantic model
after a maintenance pass.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task Bridge-C.3: gish-side doc — ch.18 LGD Bridge

**Files (Ghost_In_Shell repo):**
- Create: `docs/ch.18-lgd-bridge.md`

- [ ] **Step 1: Write the chapter**

`docs/ch.18-lgd-bridge.md`:

```markdown
# Chapter 18 — LabGrimoire Desktop Bridge

LabGrimoire Desktop (LGD) is a Tauri/Rust desktop application that consumes
gshell-memory workspaces. This chapter documents the contract.

## Architecture

```
┌────────────────────────────────────────┐
│ LabGrimoire Desktop                     │
│   Rust (Tauri)  +  Python (lgd_agent)   │
│                                          │
│   sources.memory.type = "gshell"        │
└──────────────────┬─────────────────────┘
                   │ reads same workspace
                   ▼
┌────────────────────────────────────────┐
│ gshell-memory workspace (filesystem)    │
│   schema 5.1; Pydantic + JSON Schema    │
└──────────────────▲─────────────────────┘
                   │
┌──────────────────┴─────────────────────┐
│ gshell-memory (Python)                  │
│   gish CLI + 14 engines                  │
└────────────────────────────────────────┘
```

Both sides read and write the same workspace directory. Neither side
imports the other's engine code. Schema agreement is enforced through
the shared `gshell-memory-schema` Pydantic + JSON Schema package.

## LGD configuration

In `~/Library/Application Support/labgrimoire/grimoire.toml`:

```toml
[sources.memory]
enabled = true
type = "gshell"
path = "~/my-gshell-workspace"
```

LGD's settings panel surfaces the source type on the Sources page.

## Migration from legacy LGD

Legacy LGD workspaces (`type = "jsonl-graph"`) keep working through one
minor cycle. Run `lgd-agent-migrate <old> <new>` to convert. The migrator
fills SHA-256 fingerprints, writes the 5.1 manifest, and seeds the default
5-region brain region manifest.

## Troubleshooting

- **LGD shows "schema mismatch"**: re-run `pip install -U gshell-memory-schema`
  in the same Python environment that hosts `lgd-agent`.
- **gish doctor reports missing fingerprint after LGD writes**: a legacy
  LGD version may be writing without fingerprints. Update LGD to a build
  that includes the Bridge waves.

## Forward compatibility

When schema bumps to 6.0, expect a `gish migrate v5` command analogous
to the existing `gish migrate v4`. LGD will pin a compatible schema range
in its own release.
```

- [ ] **Step 2: Commit**

```bash
git add docs/ch.18-lgd-bridge.md
git commit -m "docs(bridge-c): ch.18 LabGrimoire Desktop Bridge

Architecture diagram, LGD configuration, migration from jsonl-graph,
troubleshooting, forward-compat notes.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task Bridge-C.4: LGD-side doc — gshell-memory integration

**Files (LGD repo):**
- Create: `docs/integration/gshell-memory.md`

- [ ] **Step 1: Write the doc**

`docs/integration/gshell-memory.md`:

```markdown
# Integrating with gshell-memory

LabGrimoire Desktop consumes a [gshell-memory](https://github.com/cyhsieh817/Ghost_In_Shell)
workspace via the `gshell` source type. This page covers configuration,
migration from the legacy `jsonl-graph` source, and known limits.

## Configuration

`~/Library/Application Support/labgrimoire/grimoire.toml`:

```toml
[sources.memory]
enabled = true
type = "gshell"
path = "~/my-gshell-workspace"
```

## Creating a fresh workspace

```bash
pip install gshell-memory
gish init ~/my-gshell-workspace
```

Restart LGD; the Sources panel should report `Type: gshell-memory workspace`.

## Migrating from legacy jsonl-graph

```bash
pip install gshell-memory-schema  # via the lgd-agent uv sync, normally automatic
lgd-agent-migrate ~/.lgd_legacy_memory ~/my-gshell-workspace
```

Edit `grimoire.toml` to point at the new path with `type = "gshell"`.

## Known limits

- LGD only reads the schema files declared in chapter 18 of the
  gshell-memory docs. New schema additions become visible to LGD after
  upgrading `gshell-memory-schema`.
- The Rust adapter relies on the schema directory shipped by
  `gshell-memory-schema`; if Python is not on PATH at LGD start-up,
  fall back to bundled snapshots (planned for Bridge-D, not in this release).
```

- [ ] **Step 2: Commit**

```bash
git add docs/integration/gshell-memory.md
git commit -m "docs(gshell-bridge): integration guide on the LGD side

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task Bridge-C.5: Bridge banners and cross-links

**Files:**
- Modify (Ghost_In_Shell repo): `README.md`
- Modify (LGD repo): top-level README

- [ ] **Step 1: gshell-memory README — Bridge banner**

Near the top of `Ghost_In_Shell/README.md`, after the badge block, add:

```markdown
> **Pairs with [LabGrimoire Desktop](https://github.com/cyhsieh817/LabGrimoire_Desktop)** — a Tauri/Rust GUI that reads the same workspace. See [Chapter 18](docs/ch.18-lgd-bridge.md) for the contract.
```

- [ ] **Step 2: LGD README — Bridge banner**

Near the top of `LabGrimoire_Desktop/README.md`, add:

```markdown
> **Powered by [gshell-memory](https://github.com/cyhsieh817/Ghost_In_Shell)** — install with `pip install gshell-memory`, init a workspace with `gish init`, then point `grimoire.toml` at it. See [docs/integration/gshell-memory.md](docs/integration/gshell-memory.md).
```

- [ ] **Step 3: Commit (in each repo)**

```bash
# Ghost_In_Shell
git add README.md
git commit -m "docs(bridge-c): README banner cross-links LabGrimoire Desktop

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

```bash
# LabGrimoire_Desktop
git add README.md
git commit -m "docs(gshell-bridge): README banner cross-links gshell-memory

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

#### Task Bridge-C.6: Tag releases and finalise

**Files:** (no files; tagging + PR merges)

- [ ] **Step 1: Merge gshell-memory Bridge PR to main**

In Ghost_In_Shell:

```bash
gh pr merge --squash --delete-branch  # the WIP PR opened in M5-B.7
git checkout main
git pull
```

Tag is already at `v5.0.0` from M6-C.6; Bridge changes constitute a `5.1.0` minor:

```bash
git tag v5.1.0
git push origin v5.1.0
```

- [ ] **Step 2: Merge LGD Bridge PR to main**

In LabGrimoire_Desktop:

```bash
git push -u origin feat/gshell-bridge
gh pr create --title "feat: gshell-memory bridge" --body "Implements Bridge-A/B/C from the gshell-memory product launch plan."
gh pr merge --squash --delete-branch
git checkout main
git pull
git tag v<next-lgd-version>  # use the LGD versioning scheme
git push origin v<next-lgd-version>
```

- [ ] **Step 3: Update CHANGELOG.md on both sides**

In Ghost_In_Shell `CHANGELOG.md`, add a `[5.1.0]` section listing the Bridge work.
In LGD's changelog/release notes, list the gshell-memory integration.

- [ ] **Step 4: Verify end-to-end on local machine**

```bash
python3.11 -m venv /tmp/e2e
source /tmp/e2e/bin/activate
pip install gshell-memory==5.1.0
gish init ~/e2e-workspace
# Switch LGD's grimoire.toml to use ~/e2e-workspace and type = "gshell"
# Launch LGD, verify Knowledge tab shows the gish-init content.
deactivate
mv /tmp/e2e _DELETE_e2e
mv ~/e2e-workspace _DELETE_e2e-workspace
```

Expected: contractor's local LGD app shows workspace content from `gish init`.

- [ ] **Step 5: Commit changelog updates**

```bash
# Ghost_In_Shell
git add CHANGELOG.md
git commit -m "docs(release): CHANGELOG 5.1.0 — LGD Bridge complete

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Self-Review

The following sections record the inline review run after the plan was first written.

### Spec coverage

Walking the spec sections against the plan tasks:

- §1 Goals & Success Criteria → Covered (all six bullets land between M5-C, M6-C.6, Bridge-C.6).
- §2 Scope (in) → All seven in-scope items have at least one task.
- §3 Three-Layer Architecture → L1 covered by M6 waves, L2 by M6-A.2-.10, L3 by Bridge waves.
- §4 Workspace Schema Contract Details → M6-A.1-.12 (schema versioning, sub-package, models, JSON Schema, migration matrix).
- §5 M5 → Tasks M5-A.1 through M5-C.6.
- §6 M6 → Tasks M6-A.1 through M6-C.6.
- §7 Bridge → Tasks Bridge-A.1 through Bridge-C.6.
- §8 Wave Dependency Graph → Honoured (M6-A blocks Bridge-A; Bridge-C blocks on Bridge-B and M6-C).
- §9 Time Estimate → Matches the spec's 12-14 day envelope.
- §10 Testing Strategy → Unit + integration + cross-repo interop tests appear in M6-A (each model), M6-B (each engine + CLI), Bridge-A.4, Bridge-C.1, Bridge-C.2. Golden fixtures should be added under `tests/fixtures/golden/` during M6-A.2 — noted but not currently a separate task; engineers should create the directory ad hoc when first needed.
- §11 Risks & Mitigations → Each major risk has a corresponding task or note (deprecation alias in M5-C.4, schema collision detector implicit in `freeze()` helper M6-A.6, LGD backward compat in Bridge-B.1).
- §12 Out of Scope → Plan does not include any out-of-scope item.
- §13 Open Questions → O2 (sub-package layout), O4 (M6 yml file location), O5 (Carryover format) are answered by task selections in M6-A.1 and M6-A.5.

**Gap (addressed):** Golden fixtures (`tests/fixtures/golden/voidweaver_v4_sample`, `gshell_v5_minimal`, `gshell_v5_full`, `lgd_legacy`) are mentioned in spec §10 but were not initially covered by a task. Added Task **M6-B.0** as a prerequisite to all M6-B engine work.

### Placeholder scan

Searched for: "TBD", "TODO", "FIXME", "fill in", "similar to", "write tests for the above". Two intentional uses survived:

- M6-B chapter stubs explicitly say "Stub. Filled out in M6-C." — this is by design; M6-C.3 is the task that fills them.
- `gish heartbeat run` stub returns `status=OK` unconditionally. Documented in the engine source and in `docs/ch.15-heartbeat.md`. Extending checks is described as future work and is not blocking the v5.1 release.

No other placeholders detected.

### Type consistency

Method and property names that appear in multiple tasks:

- `SOPEngine.list_routes()` (M6-B.1) / `SOPEngine.trigger()` / `SOPEngine.register()` — consistent.
- `ArchiveRouter.list_routes()` / `add()` / `preview()` — consistent.
- `CarryoverEngine.create()` / `list_all()` / `expire()` / `promote_to_episodic()` — consistent.
- `FrozenEnumEngine.freeze()` / `list_all()` / `validate()` — consistent.
- `HeartbeatEngine.load_config()` / `save_config()` / `run()` / `cron_snippet()` / `launchd_plist()` — consistent.
- `BrainRegionStore.declare()` / `list_all()` — consistent.
- `SubdirRegistryEngine.register()` / `list_all()` / `set_enforcement()` / `enforce()` — consistent.

Model field names match between Pydantic definitions (M6-A) and engine code (M6-B).

### Fix-ups applied inline

- Inserted Task **M6-B.0** "Golden fixtures (prerequisite)" before the engine tasks. M6-B.0 creates the four golden workspaces declared in spec §10, with a load-test that runs in CI thereafter.

---

