"""SOP dispatch — natural-language triggers to required reading."""

from __future__ import annotations

from pathlib import Path

import yaml
from gshell_memory_schema.models import SOPRoute


class SOPEngine:
    def __init__(self, workspace_path: Path | str) -> None:
        self.workspace_path = Path(workspace_path)
        self._file = self.workspace_path / "memory" / "sop_dispatch.yml"

    def _read(self) -> list[SOPRoute]:
        if not self._file.exists():
            return []
        raw = yaml.safe_load(self._file.read_text(encoding="utf-8")) or {}
        return [SOPRoute.model_validate(r) for r in raw.get("routes", [])]

    def _write(self, routes: list[SOPRoute]) -> None:
        self._file.parent.mkdir(parents=True, exist_ok=True)
        data = {"routes": [r.model_dump(exclude_none=True) for r in routes]}
        self._file.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )

    def list_routes(self) -> list[SOPRoute]:
        return self._read()

    def register(self, route: SOPRoute) -> None:
        routes = self._read()
        if any(r.name == route.name for r in routes):
            raise ValueError(f"duplicate SOP route name: {route.name!r}")
        routes.append(route)
        self._write(routes)

    def trigger(self, text: str) -> list[SOPRoute]:
        return [r for r in self._read() if any(t in text for t in r.triggers)]
