"""Carryover — cross-session task hand-off with 7-day default expiry."""

from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path

import yaml
from gshell_memory_schema.models import Carryover

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


class CarryoverEngine:
    def __init__(self, workspace_path: Path | str) -> None:
        self.workspace_path = Path(workspace_path)
        self._dir = self.workspace_path / "memory" / "carryover"

    def _slug_filename(self, project_slug: str, topic: str) -> str:
        return f"carryover_{project_slug}_{topic}.md"

    def _read_one(self, path: Path) -> Carryover:
        text = path.read_text(encoding="utf-8")
        match = _FRONTMATTER_RE.match(text)
        if not match:
            raise ValueError(f"missing frontmatter in {path}")
        data = yaml.safe_load(match.group(1))
        return Carryover.model_validate(data)

    def _write_one(self, c: Carryover, body: str = "") -> Path:
        self._dir.mkdir(parents=True, exist_ok=True)
        path = self._dir / self._slug_filename(c.project_slug, c.topic)
        fm = yaml.safe_dump(c.model_dump(mode="json"), allow_unicode=True, sort_keys=False)
        path.write_text(f"---\n{fm}---\n\n{body}", encoding="utf-8")
        return path

    def create(self, project_slug: str, topic: str, today: date | None = None) -> Carryover:
        today = today or date.today()
        c = Carryover(
            project_slug=project_slug,
            topic=topic,
            created=today,
            expires=today + timedelta(days=7),
            status="active",
        )
        self._write_one(c)
        return c

    def list_all(self) -> list[Carryover]:
        if not self._dir.exists():
            return []
        return [self._read_one(p) for p in sorted(self._dir.glob("*.md"))]

    def expire(self, today: date | None = None) -> list[Carryover]:
        today = today or date.today()
        expired: list[Carryover] = []
        for path in self._dir.glob("*.md") if self._dir.exists() else []:
            c = self._read_one(path)
            if c.status == "active" and c.expires < today:
                updated = c.model_copy(update={"status": "expired"})
                self._write_one(updated)
                expired.append(updated)
        return expired

    def promote_to_episodic(self, project_slug: str, topic: str) -> Path | None:
        """Move file to memory/_archive/ with status=promoted."""
        path = self._dir / self._slug_filename(project_slug, topic)
        if not path.exists():
            return None
        c = self._read_one(path)
        promoted = c.model_copy(update={"status": "promoted"})
        archive_dir = self.workspace_path / "memory" / "_archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_path = archive_dir / path.name
        fm = yaml.safe_dump(promoted.model_dump(mode="json"), allow_unicode=True, sort_keys=False)
        archive_path.write_text(f"---\n{fm}---\n", encoding="utf-8")
        path.unlink()  # safe per project policy: file was just written to archive with full content
        return archive_path
