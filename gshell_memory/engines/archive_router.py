"""Archive routing — condition->target decision tree."""

from __future__ import annotations

from pathlib import Path

import yaml
from gshell_memory_schema.models import ArchiveRoute


class ArchiveRouter:
    def __init__(self, workspace_path: Path | str) -> None:
        self.workspace_path = Path(workspace_path)
        self._file = self.workspace_path / "memory" / "archive_routing.yml"

    def _read(self) -> list[ArchiveRoute]:
        if not self._file.exists():
            return []
        raw = yaml.safe_load(self._file.read_text(encoding="utf-8")) or {}
        routes = [ArchiveRoute.model_validate(r) for r in raw.get("routes", [])]
        return sorted(routes, key=lambda r: r.priority)

    def _write(self, routes: list[ArchiveRoute]) -> None:
        self._file.parent.mkdir(parents=True, exist_ok=True)
        data = {"routes": [r.model_dump(exclude_none=True) for r in routes]}
        self._file.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    def list_routes(self) -> list[ArchiveRoute]:
        return self._read()

    def add(self, route: ArchiveRoute) -> None:
        routes = self._read()
        routes.append(route)
        self._write(routes)

    def preview(self, candidate_text: str) -> ArchiveRoute | None:
        for r in self._read():  # already sorted by priority
            if r.condition in candidate_text:
                return r
        return None
