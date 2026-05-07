"""bootstrap.sh smoke tests — M1 only checks the script exists, is executable, and prints expected lines on --help."""

import subprocess
from pathlib import Path


def test_bootstrap_exists(repo_root: Path):
    bootstrap = repo_root / "bootstrap.sh"
    assert bootstrap.exists(), "bootstrap.sh missing"
    assert bootstrap.stat().st_mode & 0o111, "bootstrap.sh must be executable"


def test_bootstrap_help_mentions_v5_and_gish(repo_root: Path):
    result = subprocess.run(
        ["bash", str(repo_root / "bootstrap.sh"), "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    out = result.stdout + result.stderr
    assert "v5" in out.lower() or "5.0" in out
    assert "gish" in out
