"""Unit tests for decay engine (spec § 4.7)."""

import datetime
import json

from gshell_memory.engines import decay


def _make_episode(eid: str, importance: int, weeks_ago: float = 0.0) -> dict:
    ts = (
        datetime.datetime.now(datetime.UTC)
        - datetime.timedelta(weeks=weeks_ago)
    ).isoformat()
    import hashlib
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


def test_decay_pauses_when_too_few_active(tmp_paths):
    # Only 3 active entries — below safety floor of 5
    entries = [_make_episode(f"ep-{i}", 5) for i in range(3)]
    tmp_paths.episodic.write_text(
        "\n".join(json.dumps(e) for e in entries) + "\n"
    )
    result = decay.run(tmp_paths.root)
    assert result["paused"] is True


def test_decay_runs_with_enough_active(tmp_paths):
    entries = [_make_episode(f"ep-{i}", 5) for i in range(6)]
    tmp_paths.episodic.write_text(
        "\n".join(json.dumps(e) for e in entries) + "\n"
    )
    result = decay.run(tmp_paths.root, dry_run=True)
    assert result["paused"] is False


def test_decay_dry_run_does_not_write(tmp_paths):
    entries = [_make_episode(f"ep-{i}", 1, weeks_ago=200) for i in range(6)]
    tmp_paths.episodic.write_text(
        "\n".join(json.dumps(e) for e in entries) + "\n"
    )
    original = tmp_paths.episodic.read_text()
    decay.run(tmp_paths.root, dry_run=True)
    assert tmp_paths.episodic.read_text() == original


def test_schedule_cron():
    assert decay.schedule_cron() == "0 4 * * *"
