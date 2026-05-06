"""Unit tests for associate engine (spec § 4.7)."""

import json
import hashlib
import datetime

from ghost_in_shell.engines import associate


def _ep(eid: str, tags: list) -> dict:
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    fp = hashlib.sha256(eid.encode()).hexdigest()
    return {
        "id": eid,
        "ts": ts,
        "type": "decision",
        "title": f"Episode {eid}",
        "content": "content",
        "tags": tags,
        "importance": 5,
        "source": "test",
        "fingerprint": fp,
        "links": {"facts": [], "files": []},
        "decay_status": "active",
        "quality": {"duplicate_suspect": False, "exclusive": True,
                    "predictive": False, "recurrence": 0, "score": 0.65},
        "retrieval": {"count": 0, "last_accessed": None, "strength": 0.7},
    }


def test_associate_creates_shared_tag_link(tmp_paths):
    entries = [_ep("a", ["python", "bug"]), _ep("b", ["python", "test"])]
    tmp_paths.episodic.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    result = associate.run(tmp_paths.root)
    assert result["created"] == 1


def test_associate_no_link_without_shared_tag(tmp_paths):
    entries = [_ep("a", ["python"]), _ep("b", ["ruby"])]
    tmp_paths.episodic.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    result = associate.run(tmp_paths.root)
    assert result["created"] == 0


def test_associate_dry_run_does_not_write(tmp_paths):
    entries = [_ep("a", ["tag1"]), _ep("b", ["tag1"])]
    tmp_paths.episodic.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    result = associate.run(tmp_paths.root, dry_run=True)
    assert result["created"] == 1
    assert result["dry_run"] is True
    assert not tmp_paths.associations.exists()


def test_schedule_cron():
    assert associate.schedule_cron() == "0 5 * * *"
