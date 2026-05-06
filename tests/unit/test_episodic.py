"""Unit tests for EpisodicStore (spec § 4.2)."""

import datetime

import pytest

from ghost_in_shell.memory.episodic import EpisodicStore, make_fingerprint

TODAY = "2024-01-01"
TS = "2024-01-01T00:00:00Z"
NOW_TS = datetime.datetime.now(datetime.timezone.utc).isoformat()


def _entry(**kwargs) -> dict:
    base = {
        "id": "ep-001",
        "ts": TS,
        "type": "decision",
        "title": "Test entry",
        "content": "Some content here",
        "tags": ["test"],
        "importance": 5,
        "source": "test",
        "fingerprint": make_fingerprint("Test entry", "Some content here", TODAY),
        "links": {"facts": [], "files": []},
        "decay_status": "active",
        "quality": {},
        "retrieval": {},
    }
    base.update(kwargs)
    return base


def test_append_returns_id(tmp_paths):
    store = EpisodicStore(tmp_paths)
    eid = store.append(_entry())
    assert eid == "ep-001"


def test_append_persists_entry(tmp_paths):
    store = EpisodicStore(tmp_paths)
    store.append(_entry())
    rows = store.all()
    assert len(rows) == 1
    assert rows[0]["id"] == "ep-001"


def test_cooldown_dedup_returns_existing_id(tmp_paths):
    store = EpisodicStore(tmp_paths, cooldown_seconds=3600)
    e = _entry(ts=NOW_TS)
    store.append(e)
    # Same fingerprint within cooldown — should not write a second entry
    eid = store.append(e)
    assert eid == "ep-001"
    assert len(store.all()) == 1


def test_cooldown_dedup_respects_window(tmp_paths):
    store = EpisodicStore(tmp_paths, cooldown_seconds=0)
    store.append(_entry())
    # cooldown=0 means always write again
    entry2 = _entry(id="ep-002", ts=TS)
    store.append(entry2)
    assert len(store.all()) == 2


def test_soft_dedup_marks_suspect(tmp_paths):
    store = EpisodicStore(tmp_paths, cooldown_seconds=0)
    base_content = "The deployment pipeline failed due to a missing environment variable."
    similar_content = "The deployment pipeline failed due to a missing environment variable in production."
    store.append(_entry(content=base_content, fingerprint=make_fingerprint("Test entry", base_content, TODAY)))
    # Very similar content (>80% similarity) with different fingerprint
    sim_fp = make_fingerprint("Test entry", similar_content, TODAY + "x")
    entry2 = _entry(id="ep-002", content=similar_content, fingerprint=sim_fp)
    store.append(entry2)
    rows = store.all()
    suspect = next(r for r in rows if r["id"] == "ep-002")
    assert suspect["quality"]["duplicate_suspect"] is True


def test_search_returns_matching_entries(tmp_paths):
    store = EpisodicStore(tmp_paths)
    store.append(_entry(title="Deploy to production", content="ran deploy script"))
    fp2 = make_fingerprint("Unrelated thing", "Nothing to see here", TODAY)
    store.append(_entry(id="ep-002", title="Unrelated thing", content="Nothing to see here", fingerprint=fp2))
    results = store.search("deploy")
    assert len(results) == 1
    assert results[0]["id"] == "ep-001"


def test_get_returns_entry_by_id(tmp_paths):
    store = EpisodicStore(tmp_paths)
    store.append(_entry())
    row = store.get("ep-001")
    assert row is not None
    assert row["title"] == "Test entry"


def test_get_returns_none_for_missing(tmp_paths):
    store = EpisodicStore(tmp_paths)
    assert store.get("nonexistent") is None
