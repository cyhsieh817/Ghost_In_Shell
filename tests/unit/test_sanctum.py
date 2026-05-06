"""Unit tests for SanctumRegistry (spec § 4.5)."""

import yaml

from ghost_in_shell.memory.sanctum import SanctumRegistry, Verdict


def _write_registry(tmp_paths) -> None:
    registry = {
        "schema_version": 1,
        "entries": [
            {
                "path": "memory/fact.yml",
                "tier": "private",
                "reason": "Personal identity",
                "enforced_actions": ["write", "delete"],
            },
            {
                "path": "memory/secret.yml",
                "tier": "sacred",
                "reason": "Most sensitive",
                "enforced_actions": ["read", "write", "delete"],
            },
            {
                "path": "memory/public.yml",
                "tier": "public",
                "reason": "Open data",
                "enforced_actions": ["read"],
            },
        ],
    }
    tmp_paths.sanctum_registry.write_text(yaml.dump(registry))


def test_unknown_file_allows_all(tmp_paths):
    _write_registry(tmp_paths)
    s = SanctumRegistry(tmp_paths)
    assert s.verdict("memory/unknown.yml", "write") == Verdict.ALLOW


def test_private_write_warns(tmp_paths):
    _write_registry(tmp_paths)
    s = SanctumRegistry(tmp_paths)
    assert s.verdict("memory/fact.yml", "write") == Verdict.WARN


def test_private_delete_denies(tmp_paths):
    _write_registry(tmp_paths)
    s = SanctumRegistry(tmp_paths)
    assert s.verdict("memory/fact.yml", "delete") == Verdict.DENY


def test_sacred_write_denies(tmp_paths):
    _write_registry(tmp_paths)
    s = SanctumRegistry(tmp_paths)
    assert s.verdict("memory/secret.yml", "write") == Verdict.DENY


def test_sacred_read_warns(tmp_paths):
    _write_registry(tmp_paths)
    s = SanctumRegistry(tmp_paths)
    assert s.verdict("memory/secret.yml", "read") == Verdict.WARN


def test_no_registry_file_allows_all(tmp_paths):
    s = SanctumRegistry(tmp_paths)
    assert s.verdict("anything", "delete") == Verdict.ALLOW
