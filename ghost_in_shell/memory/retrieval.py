"""RetrievalBuffer — spec § 4.6 strength formula + retrieval log."""

from __future__ import annotations

import datetime
import sqlite3

from ghost_in_shell.memory._paths import WorkspacePaths
from ghost_in_shell.memory._safe_io import append_jsonl

_CREATE_RETRIEVAL_LOG = """
CREATE TABLE IF NOT EXISTS retrieval_log (
    id          TEXT PRIMARY KEY,
    kind        TEXT NOT NULL,
    count       INTEGER NOT NULL DEFAULT 0,
    last_access TEXT
);
"""

# Strength formula (frozen, spec § 4.6):
#   base(imp/10) + retrieval(count*0.08) + assoc(edges*0.05) - decay(weeks*0.03)
#   clamped [0.0, 1.0]


def compute_strength(
    importance: int,
    retrieval_count: int,
    association_edges: int,
    weeks_since_creation: float,
) -> float:
    raw = (
        importance / 10.0
        + retrieval_count * 0.08
        + association_edges * 0.05
        - weeks_since_creation * 0.03
    )
    return max(0.0, min(1.0, raw))


class RetrievalBuffer:
    """Track retrieval events and compute entry strength scores."""

    def __init__(self, paths: WorkspacePaths) -> None:
        self._paths = paths
        self._log_path = paths.memory_dir / "retrieval_log.jsonl"
        self._init_db()

    # ------------------------------------------------------------------
    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(_CREATE_RETRIEVAL_LOG)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self._paths.graph_db))

    # ------------------------------------------------------------------
    def record(self, entry_id: str, kind: str = "episode") -> int:
        """Increment retrieval count for *entry_id*. Returns new count."""
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO retrieval_log (id, kind, count, last_access)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(id) DO UPDATE SET
                    count = count + 1,
                    last_access = excluded.last_access
                """,
                (entry_id, kind, ts),
            )
            row = conn.execute(
                "SELECT count FROM retrieval_log WHERE id=?", (entry_id,)
            ).fetchone()
        new_count = row[0] if row else 1
        append_jsonl(self._log_path, [{"ts": ts, "id": entry_id, "kind": kind, "count": new_count}])
        return new_count

    # ------------------------------------------------------------------
    def retrieval_count(self, entry_id: str) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT count FROM retrieval_log WHERE id=?", (entry_id,)
            ).fetchone()
        return row[0] if row else 0

    # ------------------------------------------------------------------
    def strength(
        self,
        entry_id: str,
        importance: int,
        association_edges: int,
        created_ts: str,
    ) -> float:
        count = self.retrieval_count(entry_id)
        created = datetime.datetime.fromisoformat(created_ts.replace("Z", "+00:00"))
        now = datetime.datetime.now(datetime.timezone.utc)
        weeks = (now - created).total_seconds() / (7 * 24 * 3600)
        return compute_strength(importance, count, association_edges, weeks)
