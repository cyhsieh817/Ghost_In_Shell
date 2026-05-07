"""FactStore — load/get/set/archive with audit log (spec § 4.1)."""

from __future__ import annotations

import datetime
from typing import Any

import yaml

from ghost_in_shell.memory._lock import file_lock
from ghost_in_shell.memory._paths import WorkspacePaths
from ghost_in_shell.memory._safe_io import append_jsonl, atomic_write_text


class FactStore:
    """Thin YAML-backed store for the user fact document."""

    def __init__(self, paths: WorkspacePaths) -> None:
        self._paths = paths
        self._audit = paths.memory_dir / "facts_audit.jsonl"

    # ------------------------------------------------------------------
    def load(self) -> dict:
        """Return the current fact document as a plain dict."""
        p = self._paths.fact_yml
        if not p.exists():
            return {}
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}

    # ------------------------------------------------------------------
    def get(self, key: str, default: Any = None) -> Any:
        """Dot-separated key lookup (e.g. ``identity.name``)."""
        doc = self.load()
        parts = key.split(".")
        node: Any = doc
        for part in parts:
            if not isinstance(node, dict):
                return default
            node = node.get(part, default)
        return node

    # ------------------------------------------------------------------
    def set(self, key: str, value: Any) -> None:
        """Dot-separated key setter; atomically rewrites fact.yml."""
        with file_lock(self._paths.fact_yml):
            doc = self.load()
            parts = key.split(".")
            node = doc
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = value
            atomic_write_text(self._paths.fact_yml, yaml.dump(doc, allow_unicode=True))
        self._audit_entry("set", key, value)

    # ------------------------------------------------------------------
    def archive(self, key: str) -> None:
        """Move a top-level key into ``archive``."""
        with file_lock(self._paths.fact_yml):
            doc = self.load()
            if key not in doc:
                return
            val = doc.pop(key)
            doc.setdefault("archive", {})[key] = val
            atomic_write_text(self._paths.fact_yml, yaml.dump(doc, allow_unicode=True))
        self._audit_entry("archive", key, None)

    # ------------------------------------------------------------------
    def _audit_entry(self, action: str, key: str, value: Any) -> None:
        ts = datetime.datetime.now(datetime.UTC).isoformat()
        append_jsonl(self._audit, [{"ts": ts, "action": action, "key": key, "value": str(value)}])
