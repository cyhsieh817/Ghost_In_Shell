"""Unit tests for BrainRegionRouter (spec § 4.4)."""

import yaml

from ghost_in_shell.memory.brain_regions import BrainRegionRouter


def _write_manifest(tmp_paths) -> None:
    manifest = {
        "schema_version": 1,
        "generated_at": "2024-01-01",
        "regions": {
            "hippocampus": {
                "display": "Hippocampus",
                "core_files": [{"path": "memory/episodic.jsonl"}],
                "on_demand_files": [],
            },
            "prefrontal": {
                "display": "Prefrontal",
                "core_files": [{"path": "memory/fact.yml"}],
                "on_demand_files": [{"path": "memory/memory_manifest.yml"}],
            },
            "limbic": {
                "display": "Limbic",
                "core_files": [],
                "on_demand_files": [],
            },
            "cerebellum": {
                "display": "Cerebellum",
                "core_files": [],
                "on_demand_files": [{"path": "memory/runtime_profiles.yml"}],
            },
            "default": {
                "display": "Default",
                "core_files": [],
                "on_demand_files": [],
            },
        },
    }
    tmp_paths.brain_region_manifest.write_text(yaml.dump(manifest))


def test_region_for_known_file(tmp_paths):
    _write_manifest(tmp_paths)
    router = BrainRegionRouter(tmp_paths)
    assert router.region_for("memory/episodic.jsonl") == "hippocampus"
    assert router.region_for("memory/fact.yml") == "prefrontal"


def test_region_for_unknown_file_returns_default(tmp_paths):
    _write_manifest(tmp_paths)
    router = BrainRegionRouter(tmp_paths)
    assert router.region_for("unknown/file.txt") == "default"


def test_files_in_region_returns_all_files(tmp_paths):
    _write_manifest(tmp_paths)
    router = BrainRegionRouter(tmp_paths)
    files = router.files_in_region("prefrontal")
    assert "memory/fact.yml" in files
    assert "memory/memory_manifest.yml" in files


def test_files_in_region_unknown_returns_empty(tmp_paths):
    _write_manifest(tmp_paths)
    router = BrainRegionRouter(tmp_paths)
    assert router.files_in_region("nonexistent") == []


def test_region_for_no_manifest_returns_default(tmp_paths):
    router = BrainRegionRouter(tmp_paths)
    # No manifest file present — should gracefully fall back
    assert router.region_for("any/file.txt") == "default"
