"""Ensure existing v5 models import cleanly from the sub-package."""

import pytest


def test_workspace_model_imports():
    from gshell_memory_schema.models import Workspace

    assert Workspace is not None


def test_episodic_entry_imports():
    from gshell_memory_schema.models import EpisodicEntry

    assert EpisodicEntry is not None


def test_episodic_entry_validates_minimal():
    from gshell_memory_schema.models import EpisodicEntry

    entry = EpisodicEntry(
        id="ep-2026-05-24-001",
        title="Test",
        content="Body",
        date="2026-05-24",
        ts="2026-05-24T00:00:00Z",
        type="decision",
        tags=[],
        importance=5,
        fingerprint="a" * 64,
        retrieval={"count": 0, "last_accessed": None, "strength": 1.0},
        decay_status="active",
        linked_to=[],
    )
    assert entry.id == "ep-2026-05-24-001"


def test_episodic_entry_rejects_short_fingerprint():
    import pydantic
    from gshell_memory_schema.models import EpisodicEntry

    with pytest.raises(pydantic.ValidationError):
        EpisodicEntry(
            id="ep-x",
            title="t",
            content="c",
            date="2026-05-24",
            ts="2026-05-24T00:00:00Z",
            type="decision",
            tags=[],
            importance=5,
            fingerprint="short",
            retrieval={"count": 0, "last_accessed": None, "strength": 1.0},
            decay_status="active",
            linked_to=[],
        )
