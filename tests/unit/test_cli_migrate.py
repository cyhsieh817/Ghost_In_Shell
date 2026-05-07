"""Unit tests for `gish migrate v4` command."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml
from click.testing import CliRunner

from ghost_in_shell.cli.main import gish

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fp(title: str, content: str, ts: str) -> str:
    return hashlib.sha256(f"{title}\n{content}\n{ts[:10]}".encode()).hexdigest()


def _make_old_workspace(root: Path) -> Path:
    """Create a minimal v4-style workspace fixture."""
    old = root / "old_ws"
    mem = old / "memory"
    mem.mkdir(parents=True)

    # Fact files (two fragmented files)
    (mem / "fact.yml").write_text(
        yaml.dump({"name": "Test Agent", "language": "en"}, allow_unicode=True),
        encoding="utf-8",
    )
    (mem / "fact_tools.yml").write_text(
        yaml.dump({"tools": {"editor": "neovim"}, "archive/old_key": "legacy"}),
        encoding="utf-8",
    )

    # Episodic with one entry that has a wrong fingerprint
    episode = {
        "id": "ep_00000001",
        "ts": "2025-01-01T10:00:00Z",
        "type": "insight",
        "title": "Hello",
        "content": "World",
        "tags": [],
        "importance": 5,
        "fingerprint": "WRONG_FINGERPRINT",
        "quality": {
            "score": 0.7,
            "duplicate_suspect": False,
            "exclusive": False,
            "predictive": False,
            "recurrence": False,
        },
        "decay_status": "active",
        "retrieval": {"count": 0, "last_accessed": None, "strength": 0.5},
    }
    (mem / "episodic.jsonl").write_text(json.dumps(episode) + "\n", encoding="utf-8")

    # Brain region manifest with one invalid region
    manifest = {
        "schema_version": 1,
        "regions": {
            "hippocampus": {"core_files": [], "on_demand_files": []},
            "invalid_region": {"core_files": [{"path": "memory/foo.yml"}], "on_demand_files": []},
        },
    }
    (mem / "brain_region_manifest.yml").write_text(
        yaml.dump(manifest, allow_unicode=True), encoding="utf-8"
    )

    return old


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_migrate_v4_basic(tmp_path: Path) -> None:
    """Migrate v4 workspace: fact merge, episode migration, region coercion."""
    old_ws = _make_old_workspace(tmp_path)
    new_ws = tmp_path / "new_ws"

    runner = CliRunner()
    result = runner.invoke(gish, ["migrate", "v4", str(old_ws), str(new_ws)])
    assert result.exit_code == 0, result.output

    # New workspace must exist
    assert new_ws.is_dir()

    # fact.yml must exist
    fact_path = new_ws / "memory" / "fact.yml"
    assert fact_path.exists(), "fact.yml not created"

    # Episodic must exist
    ep_path = new_ws / "memory" / "episodic.jsonl"
    assert ep_path.exists(), "episodic.jsonl not created"

    # Summary in output
    assert "Migration complete" in result.output


def test_migrate_v4_dry_run_no_files(tmp_path: Path) -> None:
    """--dry-run must not write any files."""
    old_ws = _make_old_workspace(tmp_path)
    new_ws = tmp_path / "dry_new"

    runner = CliRunner()
    result = runner.invoke(gish, ["migrate", "v4", "--dry-run", str(old_ws), str(new_ws)])
    assert result.exit_code == 0, result.output

    assert not new_ws.exists(), "dry-run must not create new workspace"
    assert "[DRY RUN]" in result.output


def test_migrate_v4_fact_files_merged(tmp_path: Path) -> None:
    """Fragmented fact*.yml files are merged into one fact.yml."""
    old_ws = _make_old_workspace(tmp_path)
    new_ws = tmp_path / "merged_ws"

    runner = CliRunner()
    result = runner.invoke(gish, ["migrate", "v4", str(old_ws), str(new_ws)])
    assert result.exit_code == 0, result.output

    fact_path = new_ws / "memory" / "fact.yml"
    data = yaml.safe_load(fact_path.read_text(encoding="utf-8"))

    # Keys from both fact.yml and fact_tools.yml should be present
    assert "name" in data, "key 'name' from fact.yml missing"
    assert "tools" in data, "key 'tools' from fact_tools.yml missing"


def test_migrate_v4_archive_namespace(tmp_path: Path) -> None:
    """Keys with 'archive/' prefix move into archive namespace."""
    old_ws = _make_old_workspace(tmp_path)
    new_ws = tmp_path / "arch_ws"

    runner = CliRunner()
    runner.invoke(gish, ["migrate", "v4", str(old_ws), str(new_ws)])

    fact_path = new_ws / "memory" / "fact.yml"
    data = yaml.safe_load(fact_path.read_text(encoding="utf-8"))
    # 'archive/old_key' should be inside 'archive:' namespace
    assert "archive" in data
    assert "archive/old_key" in data["archive"]


def test_migrate_v4_fingerprint_recomputed(tmp_path: Path) -> None:
    """Missing or wrong fingerprints are recomputed from title+content+date."""
    old_ws = _make_old_workspace(tmp_path)
    new_ws = tmp_path / "fp_ws"

    runner = CliRunner()
    runner.invoke(gish, ["migrate", "v4", str(old_ws), str(new_ws)])

    ep_path = new_ws / "memory" / "episodic.jsonl"
    line = ep_path.read_text(encoding="utf-8").strip().splitlines()[0]
    entry = json.loads(line)

    expected = _fp("Hello", "World", "2025-01-01T10:00:00Z")
    assert entry["fingerprint"] == expected, (
        f"Fingerprint not recomputed correctly: got {entry['fingerprint']}"
    )


def test_migrate_v4_invalid_region_coerced(tmp_path: Path) -> None:
    """Brain regions not in the 5 fixed set are coerced to 'default'."""
    old_ws = _make_old_workspace(tmp_path)
    new_ws = tmp_path / "region_ws"

    runner = CliRunner()
    result = runner.invoke(gish, ["migrate", "v4", str(old_ws), str(new_ws)])
    assert result.exit_code == 0, result.output

    manifest_path = new_ws / "memory" / "brain_region_manifest.yml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    regions = data.get("regions", {})

    assert "invalid_region" not in regions, "'invalid_region' should have been coerced"
    assert "hippocampus" in regions, "valid region 'hippocampus' should be preserved"
    assert "default" in regions, "coerced entries should land in 'default'"
    assert "Coercing" in result.output


def test_migrate_v4_missing_old_workspace(tmp_path: Path) -> None:
    """Passing a non-existent old_workspace should fail gracefully."""
    runner = CliRunner()
    result = runner.invoke(
        gish,
        ["migrate", "v4", str(tmp_path / "does_not_exist"), str(tmp_path / "new")],
    )
    assert result.exit_code != 0


def test_migrate_help() -> None:
    """gish migrate --help should exit cleanly."""
    runner = CliRunner()
    result = runner.invoke(gish, ["migrate", "--help"])
    assert result.exit_code == 0
    assert "migrate" in result.output.lower()


def test_migrate_v4_help() -> None:
    """gish migrate v4 --help should exit cleanly."""
    runner = CliRunner()
    result = runner.invoke(gish, ["migrate", "v4", "--help"])
    assert result.exit_code == 0
    assert "OLD_WORKSPACE" in result.output
    assert "NEW_WORKSPACE" in result.output
    assert "--dry-run" in result.output
