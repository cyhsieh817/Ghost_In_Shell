"""Personal-data gate. Fails CI if any forbidden substring leaks into the repo.

Deny list sources (merged):
  - tests/forbidden_strings.txt        — public, generic entries only
  - tests/forbidden_strings.local.txt  — gitignored, private identifiers
  - $GISH_FORBIDDEN_EXTRA              — newline-separated, e.g. a CI secret

Structural checks (no literals needed):
  - any `/Users/<name>` home path whose <name> is not a documented
    example persona (alice, alex, you, ...) is flagged as a leak.

Excluded paths:
  - .git/
  - legacy/         (intentional snapshot of v4.1)
  - docs/superpowers/  (gitignored internal dev plans)
  - the deny list files themselves
  - .venv/, build/, dist/, *.egg-info/

Exit codes:
  0 — clean
  2 — usage error
  1 — at least one forbidden substring detected
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DENYLIST_PATH = REPO_ROOT / "tests" / "forbidden_strings.txt"
LOCAL_DENYLIST_PATH = REPO_ROOT / "tests" / "forbidden_strings.local.txt"
EXTRA_ENV = "GISH_FORBIDDEN_EXTRA"

# Home-path personas allowed in documentation examples.
_EXAMPLE_PERSONAS = {"alice", "alex", "you", "yourname", "username", "example", "demo", "me"}
_HOME_PATH_RE = re.compile(r"/(?:Users|home)/([A-Za-z0-9._-]+)")

EXCLUDED_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "env",
    "build",
    "dist",
    "legacy",
    "superpowers",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    ".idea",
    ".vscode",
}


def load_denylist(path: Path) -> list[str]:
    if not path.exists():
        print(f"ERROR: denylist not found at {path}", file=sys.stderr)
        sys.exit(2)
    terms: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        terms.append(line)
    return terms


def load_all_terms() -> list[str]:
    """Merge public list + gitignored local list + $GISH_FORBIDDEN_EXTRA."""
    terms = load_denylist(DENYLIST_PATH)
    if LOCAL_DENYLIST_PATH.exists():
        for raw in LOCAL_DENYLIST_PATH.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line and not line.startswith("#"):
                terms.append(line)
    for raw in os.environ.get(EXTRA_ENV, "").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            terms.append(line)
    return terms


def iter_files(root: Path):
    denylist_paths = {DENYLIST_PATH.resolve(), LOCAL_DENYLIST_PATH.resolve()}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(
            part in EXCLUDED_DIR_NAMES or part.startswith(".venv") or "_DELETE_" in part
            for part in path.parts
        ):
            continue
        # Skip the denylist files themselves
        try:
            if path.resolve() in denylist_paths:
                continue
        except OSError:
            pass
        # Skip non-text-likely files (binary heuristic on extension)
        if path.suffix.lower() in {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".pdf",
            ".zip",
            ".db",
            ".sqlite",
        }:
            continue
        yield path


def main() -> int:
    terms = load_all_terms()
    if not terms:
        print("ERROR: denylist is empty", file=sys.stderr)
        return 2

    hits: list[tuple[Path, int, str, str]] = []
    for path in iter_files(REPO_ROOT):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for term in terms:
                if term in line:
                    rel = path.relative_to(REPO_ROOT)
                    hits.append((rel, lineno, term, line.strip()))
            # Structural check: real home paths that are not example personas
            for match in _HOME_PATH_RE.finditer(line):
                if match.group(1).lower() not in _EXAMPLE_PERSONAS:
                    rel = path.relative_to(REPO_ROOT)
                    hits.append((rel, lineno, "home-path:" + match.group(0), line.strip()))

    if hits:
        print("Personal-data gate FAILED. Forbidden substrings detected:\n")
        for rel, lineno, term, line in hits:
            print(f"  {rel}:{lineno}  [term={term!r}]  {line[:120]}")
        print(f"\nTotal hits: {len(hits)}")
        return 1

    print("Personal-data gate clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
