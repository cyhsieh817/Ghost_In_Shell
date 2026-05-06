"""Unit tests for pydantic schemas (spec § 5)."""

import pytest
from pydantic import ValidationError

from ghost_in_shell.memory.schemas import (
    AssociationEntry,
    BrainRegionManifest,
    EpisodicEntry,
    FactDocument,
    MemoryManifest,
    NodeRef,
    RuntimeProfiles,
    SanctumRegistry,
)


# ---------------------------------------------------------------------------
# EpisodicEntry
# ---------------------------------------------------------------------------

MINIMAL_EPISODE: dict = {
    "id": "ep-001",
    "ts": "2024-01-01T00:00:00Z",
    "type": "decision",
    "title": "Test title",
    "content": "Some content",
    "tags": ["test"],
    "importance": 7,
    "source": "test",
    "fingerprint": "a" * 64,
    "links": {"facts": [], "files": []},
    "decay_status": "active",
    "quality": {},
    "retrieval": {},
}


def test_episodic_entry_round_trip():
    ep = EpisodicEntry(**MINIMAL_EPISODE)
    assert ep.id == "ep-001"
    assert ep.importance == 7


def test_episodic_entry_importance_bounds():
    with pytest.raises(ValidationError):
        EpisodicEntry(**{**MINIMAL_EPISODE, "importance": 11})
    with pytest.raises(ValidationError):
        EpisodicEntry(**{**MINIMAL_EPISODE, "importance": 0})


def test_episodic_entry_bad_fingerprint():
    with pytest.raises(ValidationError):
        EpisodicEntry(**{**MINIMAL_EPISODE, "fingerprint": "tooshort"})


def test_episodic_entry_invalid_type():
    with pytest.raises(ValidationError):
        EpisodicEntry(**{**MINIMAL_EPISODE, "type": "unknown_type"})


# ---------------------------------------------------------------------------
# BrainRegionManifest — exactly 5 fixed keys
# ---------------------------------------------------------------------------

def _make_region():
    return {"display": "X", "core_files": [], "on_demand_files": []}


FIVE_REGIONS = {
    "hippocampus": _make_region(),
    "prefrontal": _make_region(),
    "limbic": _make_region(),
    "cerebellum": _make_region(),
    "default": _make_region(),
}


def test_brain_region_manifest_valid():
    m = BrainRegionManifest(schema_version=1, generated_at="2024-01-01", regions=FIVE_REGIONS)
    assert set(m.regions.keys()) == {"hippocampus", "prefrontal", "limbic", "cerebellum", "default"}


def test_brain_region_manifest_rejects_extra_region():
    bad = {**FIVE_REGIONS, "extra": _make_region()}
    with pytest.raises(ValidationError):
        BrainRegionManifest(schema_version=1, generated_at="2024-01-01", regions=bad)


def test_brain_region_manifest_rejects_missing_region():
    incomplete = {k: v for k, v in FIVE_REGIONS.items() if k != "default"}
    with pytest.raises(ValidationError):
        BrainRegionManifest(schema_version=1, generated_at="2024-01-01", regions=incomplete)


# ---------------------------------------------------------------------------
# MemoryManifest
# ---------------------------------------------------------------------------

def test_memory_manifest_defaults():
    m = MemoryManifest()
    assert m.schema_version == 1
    assert m.last_consolidation is None
    assert m.next_consolidation_trigger.threshold == 20


# ---------------------------------------------------------------------------
# AssociationEntry
# ---------------------------------------------------------------------------

def test_association_entry_weight_bounds():
    base = {
        "ts": "2024-01-01T00:00:00Z",
        "src": {"kind": "episode", "id": "ep-001"},
        "dst": {"kind": "fact", "id": "fact-001"},
        "type": "supports",
        "weight": 0.5,
        "evidence": "test",
        "created_by": "test",
    }
    a = AssociationEntry(**base)
    assert a.weight == 0.5
    with pytest.raises(ValidationError):
        AssociationEntry(**{**base, "weight": 1.5})


# ---------------------------------------------------------------------------
# SanctumRegistry
# ---------------------------------------------------------------------------

def test_sanctum_registry_empty():
    sr = SanctumRegistry()
    assert sr.entries == []


# ---------------------------------------------------------------------------
# FactDocument
# ---------------------------------------------------------------------------

def test_fact_document_valid():
    fd = FactDocument(
        identity={
            "name": "CYu",
            "call_as": "CYu",
            "language": "en",
            "timezone": "UTC",
            "last_updated": "2024-01-01",
        },
        preferences={},
    )
    assert fd.identity.name == "CYu"
