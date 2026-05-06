"""Unit tests for RetrievalBuffer (spec § 4.6)."""

import pytest

from ghost_in_shell.memory.retrieval import RetrievalBuffer, compute_strength


def test_record_increments_count(tmp_paths):
    buf = RetrievalBuffer(tmp_paths)
    c1 = buf.record("ep-001")
    c2 = buf.record("ep-001")
    assert c1 == 1
    assert c2 == 2


def test_retrieval_count_returns_zero_for_unknown(tmp_paths):
    buf = RetrievalBuffer(tmp_paths)
    assert buf.retrieval_count("no-such-id") == 0


def test_record_persists_to_log(tmp_paths):
    buf = RetrievalBuffer(tmp_paths)
    buf.record("ep-002")
    log = tmp_paths.memory_dir / "retrieval_log.jsonl"
    assert log.exists()
    import json
    lines = log.read_text().splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["id"] == "ep-002"
    assert row["count"] == 1


def test_strength_formula_clamped(tmp_paths):
    # importance=10, count=0, edges=0, weeks=0 → 1.0 (max)
    s = compute_strength(10, 0, 0, 0.0)
    assert s == 1.0

    # importance=1, count=0, edges=0, weeks=100 → clamped to 0.0
    s2 = compute_strength(1, 0, 0, 100.0)
    assert s2 == 0.0


def test_strength_formula_values(tmp_paths):
    # importance=5, count=2, edges=1, weeks=1
    # = 0.5 + 0.16 + 0.05 - 0.03 = 0.68
    s = compute_strength(5, 2, 1, 1.0)
    assert abs(s - 0.68) < 1e-9


def test_strength_method_uses_retrieval_count(tmp_paths):
    import datetime
    buf = RetrievalBuffer(tmp_paths)
    # Use a recent ts so decay doesn't clamp everything to 0
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    s0 = buf.strength("ep-x", importance=5, association_edges=0, created_ts=ts)
    buf.record("ep-x")
    s1 = buf.strength("ep-x", importance=5, association_edges=0, created_ts=ts)
    assert s1 > s0
