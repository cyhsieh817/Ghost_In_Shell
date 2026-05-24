"""Subdirectory registry — white-list of permitted memory/ subdirs."""

from __future__ import annotations

from pathlib import Path

import yaml
from gshell_memory_schema.models import RegisteredSubdir, SubdirRegistry


class SubdirRegistryEngine:
    def __init__(self, workspace_path: Path | str) -> None:
        self.workspace_path = Path(workspace_path)
        self._file = self.workspace_path / "memory" / "subdir_registry.yml"

    def _read(self) -> SubdirRegistry:
        if not self._file.exists():
            return SubdirRegistry(registered=[], enforcement="warn")
        raw = yaml.safe_load(self._file.read_text(encoding="utf-8")) or {}
        return SubdirRegistry.model_validate(raw)

    def _write(self, reg: SubdirRegistry) -> None:
        self._file.parent.mkdir(parents=True, exist_ok=True)
        self._file.write_text(
            yaml.safe_dump(reg.model_dump(mode="json"), allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    def register(self, *, path: str, purpose: str, lifecycle: str) -> None:
        reg = self._read()
        if any(r.path == path for r in reg.registered):
            return
        reg.registered.append(RegisteredSubdir(path=path, purpose=purpose, lifecycle=lifecycle))
        self._write(reg)

    def list_all(self) -> list[RegisteredSubdir]:
        return self._read().registered

    def set_enforcement(self, mode: str) -> None:
        reg = self._read()
        updated = reg.model_copy(update={"enforcement": mode})
        self._write(updated)

    def enforce(self, mode: str | None = None) -> list[str]:
        """Return list of unregistered subdirs. In block mode, raise if any."""
        reg = self._read()
        effective = mode or reg.enforcement
        memory_dir = self.workspace_path / "memory"
        if not memory_dir.exists():
            return []
        registered_paths = {r.path.rstrip("/") for r in reg.registered}
        found_unregistered: list[str] = []
        for child in memory_dir.iterdir():
            if not child.is_dir():
                continue
            rel = f"memory/{child.name}"
            if rel not in registered_paths:
                found_unregistered.append(rel)
        if effective == "block" and found_unregistered:
            raise RuntimeError(f"unregistered subdirs: {found_unregistered}")
        return found_unregistered
