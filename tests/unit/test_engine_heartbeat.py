from gshell_memory.engines.heartbeat import HeartbeatEngine


def test_load_default_config_when_missing(tmp_path):
    (tmp_path / "memory").mkdir()
    eng = HeartbeatEngine(tmp_path)
    cfg = eng.load_config()
    assert cfg.cadence == "hourly"
    assert cfg.idle_threshold == 5


def test_save_and_reload(tmp_path):
    (tmp_path / "memory").mkdir()
    eng = HeartbeatEngine(tmp_path)
    eng.save_config(cadence="daily", checks=["a", "b"], idle_threshold=10)
    cfg = eng.load_config()
    assert cfg.cadence == "daily"
    assert cfg.checks == ["a", "b"]
    assert cfg.idle_threshold == 10


def test_run_writes_log_entry(tmp_path):
    (tmp_path / "memory").mkdir()
    eng = HeartbeatEngine(tmp_path)
    eng.save_config(cadence="hourly", checks=["identity"], idle_threshold=5)
    entry = eng.run()
    assert entry["status"] in {"OK", "SUMMARY", "ALERT"}
    log_dir = tmp_path / "memory" / "heartbeat_logs"
    assert log_dir.exists()
    assert any(log_dir.iterdir())


def test_cron_snippet_format(tmp_path):
    (tmp_path / "memory").mkdir()
    eng = HeartbeatEngine(tmp_path)
    eng.save_config(cadence="hourly", checks=["x"])
    snippet = eng.cron_snippet(gish_path="/usr/local/bin/gish")
    assert "0 * * * *" in snippet
    assert "gish heartbeat run" in snippet
