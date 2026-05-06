from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_readme_mentions_v5():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "v5" in readme.lower(), "README must reference v5"
    assert "in progress" in readme.lower() or "rewrite" in readme.lower(), (
        "README should signal v5 is in progress"
    )


def test_legacy_v4_dir_exists():
    assert (REPO_ROOT / "legacy" / "v4.1").is_dir()
