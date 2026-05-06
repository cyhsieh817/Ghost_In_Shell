"""Unit tests for health engine (spec § 4.7)."""

from ghost_in_shell.engines import health


def test_health_dry_run_no_files(tmp_paths):
    result = health.run(tmp_paths.root, dry_run=True)
    assert result["status"] == "degraded"
    assert result["dry_run"] is True
    assert "fact.yml missing" in result["issues"]


def test_health_ok_with_required_files(tmp_paths):
    tmp_paths.fact_yml.write_text("identity:\n  name: test\n")
    tmp_paths.memory_manifest.write_text("schema_version: 1\n")
    result = health.run(tmp_paths.root)
    assert result["status"] == "ok"
    assert result["issues"] == []


def test_health_counts_episodes(tmp_paths):
    import json
    tmp_paths.episodic.write_text(
        json.dumps({"id": "ep-1"}) + "\n" + json.dumps({"id": "ep-2"}) + "\n"
    )
    tmp_paths.fact_yml.write_text("")
    tmp_paths.memory_manifest.write_text("schema_version: 1\n")
    result = health.run(tmp_paths.root)
    assert result["episode_count"] == 2


def test_schedule_cron():
    assert health.schedule_cron() == "0 6 * * *"
