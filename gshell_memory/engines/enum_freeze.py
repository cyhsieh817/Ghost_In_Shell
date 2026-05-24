"""Frozen enums — state machine values locked against drift."""

from __future__ import annotations

from pathlib import Path

import yaml
from gshell_memory_schema.enums import freeze as freeze_helper
from gshell_memory_schema.models import FrozenEnum


class FrozenEnumEngine:
    def __init__(self, workspace_path: Path | str) -> None:
        self.workspace_path = Path(workspace_path)
        self._file = self.workspace_path / "memory" / "frozen_enums.yml"

    def _read(self) -> dict[str, FrozenEnum]:
        if not self._file.exists():
            return {}
        raw = yaml.safe_load(self._file.read_text(encoding="utf-8")) or {}
        return {
            name: FrozenEnum.model_validate(data) for name, data in raw.get("enums", {}).items()
        }

    def _write(self, enums: dict[str, FrozenEnum]) -> None:
        self._file.parent.mkdir(parents=True, exist_ok=True)
        data = {"enums": {n: e.model_dump(exclude_none=True) for n, e in enums.items()}}
        self._file.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )

    def freeze(
        self,
        name: str,
        values: list[str],
        *,
        introduced: str,
        layer: str,
        enforcement: str = "audit",
        spec_ref: str | None = None,
    ) -> FrozenEnum:
        enums = self._read()
        freeze_helper(
            enums,
            name,
            values,
            introduced=introduced,
            layer=layer,
            enforcement=enforcement,
            spec_ref=spec_ref,
        )
        self._write(enums)
        return enums[name]

    def list_all(self) -> list[FrozenEnum]:
        return list(self._read().values())

    def validate(self, enum_name: str, candidate: str) -> bool:
        enums = self._read()
        if enum_name not in enums:
            raise KeyError(enum_name)
        return candidate in enums[enum_name].values
