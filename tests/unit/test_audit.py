"""Unit tests for audit engine (spec § 4.7)."""

import json

from ghost_in_shell.engines import audit


def test_audit_empty_workspace(tmp_paths):
    result = audit.run(tmp_paths.root, dry_run=True)
    assert result["total_entries"] == 0
    assert result["anomaly_count"] == 0


def test_audit_detects_delete_action(tmp_paths):
    af = tmp_paths.memory_dir / "facts_audit.jsonl"
    af.write_text(
        json.dumps({"action": "set", "key": "x"}) + "\n"
        + json.dumps({"action": "delete", "key": "y"}) + "\n"
    )
    result = audit.run(tmp_paths.root)
    assert result["total_entries"] == 2
    assert result["anomaly_count"] == 1


def test_audit_stamps_manifest(tmp_paths):
    result = audit.run(tmp_paths.root)
    manifest = tmp_paths.memory_manifest
    assert manifest.exists()
    import yaml
    doc = yaml.safe_load(manifest.read_text())
    assert doc.get("last_audit_run") is not None


def test_schedule_cron():
    assert audit.schedule_cron() == "0 3 * * 0"
