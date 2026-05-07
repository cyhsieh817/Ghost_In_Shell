"""Smoke test that the personal-data gate script is wired up correctly.

The seeded forbidden term is read from `forbidden_strings.txt` at runtime so
this test source file itself does not contain a forbidden literal (which would
trip the gate when scanning the repo).
"""

import subprocess
import sys
from pathlib import Path


def _first_term(repo_root: Path) -> str:
    denylist = (repo_root / "tests" / "forbidden_strings.txt").read_text(encoding="utf-8")
    for raw in denylist.splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            return line
    raise AssertionError("forbidden_strings.txt has no usable entries")


def test_check_no_personal_clean_repo_passes(repo_root: Path):
    result = subprocess.run(
        [sys.executable, str(repo_root / "scripts" / "ci" / "check_no_personal.py")],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"clean repo failed personal-data gate:\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


def test_check_no_personal_detects_seeded_string(repo_root: Path):
    """Drop a temporary file containing a forbidden string and confirm the gate fails."""
    term = _first_term(repo_root)
    seeded = repo_root / "tests" / "fixtures" / "_seeded_personal.tmp"
    try:
        seeded.write_text(f"This file contains the forbidden token: {term}\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(repo_root / "scripts" / "ci" / "check_no_personal.py")],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0, "gate should fail when forbidden string present"
        assert term in result.stdout + result.stderr
    finally:
        if seeded.exists():
            seeded.unlink()
