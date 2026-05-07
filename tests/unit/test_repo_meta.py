from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_readme_mentions_v5():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "v5" in readme.lower(), "README must reference v5"
    # v5 is now on main (5.0.0rc1); "rewrite", "in progress", or "complete" are all valid signals
    assert any(
        kw in readme.lower()
        for kw in ("in progress", "rewrite", "complete", "quick start", "ghost_in_shell")
    ), "README should describe v5 status or features"


def test_legacy_v4_dir_exists():
    assert (REPO_ROOT / "legacy" / "v4.1").is_dir()
