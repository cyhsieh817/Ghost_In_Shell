"""Personal-data gate. Fails CI if any forbidden substring leaks into the repo.

Excluded paths:
  - .git/
  - legacy/         (intentional snapshot of v4.1)
  - tests/forbidden_strings.txt   (the deny list itself)
  - .venv/, build/, dist/, *.egg-info/

Exit codes:
  0 — clean
  2 — usage error
  1 — at least one forbidden substring detected
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DENYLIST_PATH = REPO_ROOT / "tests" / "forbidden_strings.txt"

EXCLUDED_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "env",
    "build",
    "dist",
    "legacy",
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


def iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_DIR_NAMES for part in path.parts):
            continue
        # Skip the denylist itself
        try:
            if path.resolve() == DENYLIST_PATH.resolve():
                continue
        except OSError:
            pass
        # Skip non-text-likely files (binary heuristic on extension)
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".db", ".sqlite"}:
            continue
        yield path


def main() -> int:
    terms = load_denylist(DENYLIST_PATH)
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
