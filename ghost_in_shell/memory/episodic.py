"""EpisodicStore — append + fingerprint dedup + soft dedup + search (spec § 4.2)."""

from __future__ import annotations

import datetime
import hashlib
from difflib import SequenceMatcher
from typing import Iterator

from ghost_in_shell.memory._paths import WorkspacePaths
from ghost_in_shell.memory._safe_io import append_jsonl, read_jsonl
from ghost_in_shell.memory.schemas import EpisodicEntry

_SOFT_RATIO = 0.80


def _fp(title: str, content: str, date: str) -> str:
    raw = f"{title}\n{content}\n{date}"
    return hashlib.sha256(raw.encode()).hexdigest()


class EpisodicStore:
    def __init__(self, paths: WorkspacePaths, cooldown_seconds: int = 60) -> None:
        self._paths = paths
        self._cooldown = cooldown_seconds

    # ------------------------------------------------------------------
    def append(self, entry: dict) -> str:
        """Validate, dedup, and persist an episodic entry. Returns the entry id."""
        validated = EpisodicEntry(**entry)
        fp = validated.fingerprint
        now = datetime.datetime.now(datetime.timezone.utc)

        # Cooldown dedup — same fingerprint within cooldown window
        for existing in self._iter_raw():
            if existing.get("fingerprint") == fp:
                delta = (now - _parse_ts(existing["ts"])).total_seconds()
                if delta < self._cooldown:
                    return existing["id"]

        # Soft dedup — mark suspect if very similar content
        from ghost_in_shell.memory.schemas import Quality
        for existing in self._iter_raw():
            ratio = SequenceMatcher(
                None,
                existing.get("content", ""),
                validated.content,
            ).ratio()
            if ratio >= _SOFT_RATIO:
                new_q = Quality(**{**validated.quality.model_dump(), "duplicate_suspect": True})
                validated = validated.model_copy(update={"quality": new_q})
                break

        append_jsonl(self._paths.episodic, [validated.model_dump()])
        return validated.id

    # ------------------------------------------------------------------
    def search(self, query: str, limit: int = 20) -> list[dict]:
        """Return entries whose title or content contains *query* (case-insensitive)."""
        q = query.lower()
        results = []
        for row in self._iter_raw():
            if q in row.get("title", "").lower() or q in row.get("content", "").lower():
                results.append(row)
                if len(results) >= limit:
                    break
        return results

    # ------------------------------------------------------------------
    def get(self, entry_id: str) -> dict | None:
        for row in self._iter_raw():
            if row.get("id") == entry_id:
                return row
        return None

    # ------------------------------------------------------------------
    def all(self) -> list[dict]:
        return list(self._iter_raw())

    # ------------------------------------------------------------------
    def _iter_raw(self) -> Iterator[dict]:
        yield from read_jsonl(self._paths.episodic)


# ---------------------------------------------------------------------------

def _parse_ts(ts: str) -> datetime.datetime:
    dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def make_fingerprint(title: str, content: str, date: str) -> str:
    return _fp(title, content, date)
