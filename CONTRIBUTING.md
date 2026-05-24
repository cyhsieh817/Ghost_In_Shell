# Contributing to gshell-memory

## Development setup

```bash
git clone https://github.com/cyhsieh817/Ghost_In_Shell
cd Ghost_In_Shell
python3.11 -m venv .venv
source .venv/bin/activate
pip install uv
uv sync --extra dev
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
