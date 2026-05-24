"""Golden fixtures parse against current Pydantic models.

Per plan Task M6-B.0: minimal/full v5 fixtures must validate; lgd_legacy
and voidweaver_v4_sample are intentional "pre-migration" snapshots and
are exercised only at the file-presence level here. Their full
validation lives in migration tests that wave M6-B introduces.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

FIXTURES = Path(__file__).parent / "golden"


def _load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_v5_minimal_manifest_loads():
    from gshell_memory_schema.models import MemoryManifest

    p = FIXTURES / "gshell_v5_minimal" / "memory" / "memory_manifest.yml"
    MemoryManifest.model_validate(_load_yaml(p))


def test_v5_minimal_fact_loads():
    from gshell_memory_schema.models import FactDocument

    p = FIXTURES / "gshell_v5_minimal" / "memory" / "fact.yml"
    FactDocument.model_validate(_load_yaml(p))


def test_v5_minimal_brain_region_loads():
    from gshell_memory_schema.models import BrainRegionManifest

    p = FIXTURES / "gshell_v5_minimal" / "memory" / "brain_region_manifest.yml"
    m = BrainRegionManifest.model_validate(_load_yaml(p))
    assert set(m.regions.keys()) == {
        "hippocampus",
        "prefrontal",
        "limbic",
        "cerebellum",
        "default",
    }


def test_v5_full_brain_region_loads_with_extensions():
    from gshell_memory_schema.models import BrainRegionManifest

    p = FIXTURES / "gshell_v5_full" / "memory" / "brain_region_manifest.yml"
    m = BrainRegionManifest.model_validate(_load_yaml(p))
    assert "amygdala" in m.extensions
    assert "parietal" in m.extensions


def test_v5_full_sop_dispatch_loads():
    from gshell_memory_schema.models import SOPRoute

    p = FIXTURES / "gshell_v5_full" / "memory" / "sop_dispatch.yml"
    doc = _load_yaml(p)
    assert "routes" in doc and len(doc["routes"]) >= 1
    for entry in doc["routes"]:
        SOPRoute.model_validate(entry)


def test_v5_full_archive_routing_loads():
    from gshell_memory_schema.models import ArchiveRoute

    p = FIXTURES / "gshell_v5_full" / "memory" / "archive_routing.yml"
    doc = _load_yaml(p)
    assert "routes" in doc and len(doc["routes"]) == 2
    for entry in doc["routes"]:
        ArchiveRoute.model_validate(entry)


def test_v5_full_frozen_enums_load():
    from gshell_memory_schema.models import FrozenEnum

    p = FIXTURES / "gshell_v5_full" / "memory" / "frozen_enums.yml"
    doc = _load_yaml(p)
    names = {e["name"] for e in doc["enums"]}
    assert {"decision_kind", "rerun_status"} <= names
    for entry in doc["enums"]:
        FrozenEnum.model_validate(entry)


def test_v5_full_heartbeat_loads():
    from gshell_memory_schema.models import HeartbeatConfig

    p = FIXTURES / "gshell_v5_full" / "memory" / "heartbeat.yml"
    HeartbeatConfig.model_validate(_load_yaml(p))


def test_v5_full_subdir_registry_loads():
    from gshell_memory_schema.models import SubdirRegistry

    p = FIXTURES / "gshell_v5_full" / "memory" / "subdir_registry.yml"
    SubdirRegistry.model_validate(_load_yaml(p))


def test_lgd_legacy_files_present():
    base = FIXTURES / "lgd_legacy" / "memory"
    assert (base / "episodic.jsonl").exists()
    assert (base / "fact.yml").exists()
    # Single line, no fingerprint (intentional pre-migration shape).
    line = (base / "episodic.jsonl").read_text(encoding="utf-8").strip()
    entry = json.loads(line)
    assert "fingerprint" not in entry


def test_voidweaver_v4_sample_files_present():
    base = FIXTURES / "voidweaver_v4_sample" / "memory"
    for name in (
        "fact.yml",
        "fact_governance.yml",
        "fact_tools_detail.yml",
        "episodic.jsonl",
        "brain_region_manifest.yml",
    ):
        assert (base / name).exists(), f"missing {name}"
    # Three entries, none with fingerprint.
    lines = [
        json.loads(ln)
        for ln in (base / "episodic.jsonl").read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    assert len(lines) == 3
    assert all("fingerprint" not in e for e in lines)
