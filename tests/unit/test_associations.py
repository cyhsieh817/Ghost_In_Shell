"""Unit tests for AssociationGraph (spec § 4.3)."""


from ghost_in_shell.memory.associations import AssociationGraph

TS = "2024-01-01T00:00:00Z"


def _edge(**kwargs) -> dict:
    base = {
        "ts": TS,
        "src": {"kind": "episode", "id": "ep-001"},
        "dst": {"kind": "fact", "id": "fact-001"},
        "type": "supports",
        "weight": 0.8,
        "evidence": "test",
        "created_by": "test",
    }
    base.update(kwargs)
    return base


def test_add_persists_to_audit_log(tmp_paths):
    g = AssociationGraph(tmp_paths)
    g.add(_edge())
    edges = g.all_edges()
    assert len(edges) == 1
    assert edges[0]["type"] == "supports"


def test_add_persists_to_sqlite(tmp_paths):
    g = AssociationGraph(tmp_paths)
    g.add(_edge())
    import sqlite3
    conn = sqlite3.connect(str(tmp_paths.graph_db))
    rows = conn.execute("SELECT * FROM edges").fetchall()
    assert len(rows) == 1
    conn.close()


def test_add_deduplicates_via_insert_or_replace(tmp_paths):
    g = AssociationGraph(tmp_paths)
    g.add(_edge(weight=0.5))
    g.add(_edge(weight=0.9))  # same PK — should replace
    import sqlite3
    conn = sqlite3.connect(str(tmp_paths.graph_db))
    rows = conn.execute("SELECT weight FROM edges").fetchall()
    assert len(rows) == 1
    assert abs(rows[0][0] - 0.9) < 0.001
    conn.close()


def test_neighbors_returns_depth1_from_source(tmp_paths):
    g = AssociationGraph(tmp_paths)
    g.add(_edge())
    nbrs = g.neighbors("episode", "ep-001")
    assert len(nbrs) == 1
    assert nbrs[0]["neighbor_id"] == "fact-001"


def test_neighbors_bidirectional(tmp_paths):
    g = AssociationGraph(tmp_paths)
    g.add(_edge())
    # Query from the destination side
    nbrs = g.neighbors("fact", "fact-001")
    assert len(nbrs) == 1
    assert nbrs[0]["neighbor_id"] == "ep-001"


def test_neighbors_empty_for_unknown_node(tmp_paths):
    g = AssociationGraph(tmp_paths)
    assert g.neighbors("episode", "no-such-id") == []
