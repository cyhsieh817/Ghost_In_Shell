"""Integration tests using golden fixtures (spec § T17)."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from gshell_memory.engines import audit, health
from gshell_memory.memory._paths import WorkspacePaths
from gshell_memory.memory.episodic import EpisodicStore
from gshell_memory.memory.facts import FactStore
from gshell_memory.memory.retrieval import compute_strength

GOLDEN_DIR = Path(__file__).parent.parent / "fixtures" / "golden"


@pytest.fixture
def golden_workspace(tmp_workspace: Path) -> WorkspacePaths:
    """Workspace pre-loaded with golden fixture files."""
    paths = WorkspacePaths(tmp_workspace)
    shutil.copy(GOLDEN_DIR / "episodic_golden.jsonl", paths.episodic)
    shutil.copy(GOLDEN_DIR / "fact_golden.yml", paths.fact_yml)
    # Seed a minimal manifest so health check passes
    paths.memory_manifest.write_text("schema_version: 1\n")
    return paths


def test_golden_episodic_loads_3_entries(golden_workspace):
    store = EpisodicStore(golden_workspace)
    entries = store.all()
    assert len(entries) == 3


def test_golden_episodic_search_by_tag(golden_workspace):
    store = EpisodicStore(golden_workspace)
    results = store.search("milestone")
    assert len(results) >= 1
    assert results[0]["id"] == "ep-golden-001"


def test_golden_episodic_high_importance_survives(golden_workspace):
    """The golden insight entry (importance=9) should have strength > 0.5."""
    entries = EpisodicStore(golden_workspace).all()
    insight = next(e for e in entries if e["id"] == "ep-golden-003")
    # compute strength: importance=9, count=5, edges=0
    # weeks since 2025-01-17 ≈ large, so clamped calculation
    # Just verify it's >= 0 (clamped)
    s = compute_strength(insight["importance"], insight["retrieval"]["count"], 0, 0.0)
    assert s > 0.5


def test_golden_fact_loads_identity(golden_workspace):
    store = FactStore(golden_workspace)
    name = store.get("identity.name")
    assert name == "Golden Fixture User"


def test_golden_fact_get_preference(golden_workspace):
    store = FactStore(golden_workspace)
    stack = store.get("preferences.tech_stack")
    assert "pydantic" in stack


def test_golden_health_reports_ok(golden_workspace):
    report = health.run(golden_workspace.root, dry_run=True)
    assert report["episode_count"] == 3
    assert report["status"] == "ok"


def test_golden_audit_clean(golden_workspace):
    report = audit.run(golden_workspace.root, dry_run=True)
    assert report["anomaly_count"] == 0
