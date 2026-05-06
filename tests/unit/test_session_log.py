"""Unit tests for session_log engine (spec § 4.7)."""

from ghost_in_shell.engines import session_log


def test_session_log_dry_run(tmp_paths):
    result = session_log.run(tmp_paths.root, dry_run=True)
    assert "ts" in result
    assert result["dry_run"] is True
    log = tmp_paths.memory_dir / "session_log.jsonl"
    assert not log.exists()


def test_session_log_writes_event(tmp_paths):
    result = session_log.run(tmp_paths.root)
    assert result["dry_run"] is False
    log = tmp_paths.memory_dir / "session_log.jsonl"
    assert log.exists()
    import json
    row = json.loads(log.read_text().strip())
    assert row["event"] == "session_start"


def test_schedule_cron(tmp_paths):
    assert session_log.schedule_cron() == "@session_start"
