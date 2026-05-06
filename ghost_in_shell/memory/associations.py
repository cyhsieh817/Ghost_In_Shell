"""AssociationGraph — jsonl audit log + SQLite cache + depth-1 neighbors (spec § 4.3)."""

from __future__ import annotations

import datetime
import sqlite3
from pathlib import Path

from ghost_in_shell.memory._paths import WorkspacePaths
from ghost_in_shell.memory._safe_io import append_jsonl, read_jsonl
from ghost_in_shell.memory.schemas import AssociationEntry

_CREATE_EDGES = """
CREATE TABLE IF NOT EXISTS edges (
    src_kind TEXT NOT NULL,
    src_id   TEXT NOT NULL,
    dst_kind TEXT NOT NULL,
    dst_id   TEXT NOT NULL,
    type     TEXT NOT NULL,
    weight   REAL NOT NULL DEFAULT 1.0,
    PRIMARY KEY (src_kind, src_id, dst_kind, dst_id, type)
);
"""


class AssociationGraph:
    def __init__(self, paths: WorkspacePaths) -> None:
        self._paths = paths
        self._audit = paths.associations
        self._db_path = paths.graph_db
        self._init_db()

    # ------------------------------------------------------------------
    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(_CREATE_EDGES)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self._db_path))

    # ------------------------------------------------------------------
    def add(self, entry: dict) -> None:
        """Validate and persist a new association (audit log + sqlite cache)."""
        validated = AssociationEntry(**entry)
        append_jsonl(self._audit, [validated.model_dump()])
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO edges
                    (src_kind, src_id, dst_kind, dst_id, type, weight)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    validated.src.kind,
                    validated.src.id,
                    validated.dst.kind,
                    validated.dst.id,
                    validated.type,
                    validated.weight,
                ),
            )

    # ------------------------------------------------------------------
    def neighbors(self, kind: str, node_id: str) -> list[dict]:
        """Return all depth-1 neighbors (both directions) for a node."""
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT dst_kind AS neighbor_kind, dst_id AS neighbor_id,
                       type, weight
                FROM edges WHERE src_kind=? AND src_id=?
                UNION ALL
                SELECT src_kind, src_id, type, weight
                FROM edges WHERE dst_kind=? AND dst_id=?
                """,
                (kind, node_id, kind, node_id),
            ).fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    def all_edges(self) -> list[dict]:
        return list(read_jsonl(self._audit))
