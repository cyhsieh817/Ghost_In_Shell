"""Unit tests for FactStore (spec § 4.1)."""

import yaml

from gshell_memory.memory.facts import FactStore


def test_load_empty_when_no_file(tmp_paths):
    store = FactStore(tmp_paths)
    assert store.load() == {}


def test_set_and_get_simple_key(tmp_paths):
    store = FactStore(tmp_paths)
    store.set("identity.name", "CYu")
    assert store.get("identity.name") == "CYu"


def test_set_nested_creates_structure(tmp_paths):
    store = FactStore(tmp_paths)
    store.set("preferences.communication", ["繁中"])
    doc = store.load()
    assert doc["preferences"]["communication"] == ["繁中"]


def test_get_missing_key_returns_default(tmp_paths):
    store = FactStore(tmp_paths)
    assert store.get("does.not.exist", "fallback") == "fallback"


def test_archive_moves_key(tmp_paths):
    store = FactStore(tmp_paths)
    # Seed a fact.yml with a top-level key
    fact_path = tmp_paths.fact_yml
    fact_path.write_text(yaml.dump({"old_key": "value123"}))
    store.archive("old_key")
    doc = store.load()
    assert "old_key" not in doc
    assert doc["archive"]["old_key"] == "value123"


def test_archive_nonexistent_key_is_noop(tmp_paths):
    store = FactStore(tmp_paths)
    fact_path = tmp_paths.fact_yml
    fact_path.write_text(yaml.dump({"a": 1}))
    store.archive("nonexistent")
    doc = store.load()
    assert "archive" not in doc


def test_audit_log_written(tmp_paths):
    store = FactStore(tmp_paths)
    store.set("x", 42)
    audit = tmp_paths.memory_dir / "facts_audit.jsonl"
    assert audit.exists()
    lines = audit.read_text().strip().splitlines()
    assert len(lines) == 1
    import json
    entry = json.loads(lines[0])
    assert entry["action"] == "set"
    assert entry["key"] == "x"
