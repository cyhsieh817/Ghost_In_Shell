"""Unit tests for consolidate engine + judge (spec § 4.7)."""

import datetime
import hashlib
import json

from gshell_memory.engines import consolidate, judge


def _ep(eid: str, importance: int) -> dict:
    ts = datetime.datetime.now(datetime.UTC).isoformat()
    fp = hashlib.sha256(eid.encode()).hexdigest()
    return {
        "id": eid,
        "ts": ts,
        "type": "decision",
        "title": f"Episode {eid}",
        "content": "content",
        "tags": [],
        "importance": importance,
        "source": "test",
        "fingerprint": fp,
        "links": {"facts": [], "files": []},
        "decay_status": "active",
        "quality": {"duplicate_suspect": False, "exclusive": True,
                    "predictive": False, "recurrence": 0, "score": 0.65},
        "retrieval": {"count": 0, "last_accessed": None, "strength": 0.7},
    }


def test_consolidate_merges_low_importance(tmp_paths):
    # 4 low + 1 high importance
    entries = [_ep(f"low-{i}", 3) for i in range(4)] + [_ep("high-1", 8)]
    tmp_paths.episodic.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    result = consolidate.run(tmp_paths.root)
    assert result["merged"] == 4
    assert result["verdict"] is not None


def test_consolidate_skips_when_too_few(tmp_paths):
    entries = [_ep(f"low-{i}", 3) for i in range(2)]
    tmp_paths.episodic.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    result = consolidate.run(tmp_paths.root)
    assert result["merged"] == 0


def test_consolidate_dry_run_no_write(tmp_paths):
    entries = [_ep(f"low-{i}", 2) for i in range(4)]
    tmp_paths.episodic.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    original = tmp_paths.episodic.read_text()
    consolidate.run(tmp_paths.root, dry_run=True)
    assert tmp_paths.episodic.read_text() == original


# ---------------------------------------------------------------------------
# Judge tests
# ---------------------------------------------------------------------------

def test_judge_keep_high_importance():
    v = judge.evaluate({"importance": 9, "quality": {"score": 0.9}, "decay_status": "active"})
    assert v["keep"] is True
    assert v["suggested_action"] == "keep"


def test_judge_archive_low_score():
    v = judge.evaluate({"importance": 5, "quality": {"score": 0.2}, "decay_status": "active"})
    assert v["keep"] is False
    assert v["suggested_action"] == "archive"


def test_judge_review_duplicate():
    v = judge.evaluate({"importance": 5,
                        "quality": {"score": 0.6, "duplicate_suspect": True},
                        "decay_status": "active"})
    assert v["keep"] is False
    assert v["suggested_action"] == "review"
