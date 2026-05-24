from datetime import date

from gshell_memory.engines.carryover import CarryoverEngine


def test_create_writes_file(tmp_path):
    eng = CarryoverEngine(tmp_path)
    eng.create(project_slug="proj-x", topic="install-db", today=date(2026, 5, 24))
    files = list((tmp_path / "memory" / "carryover").glob("*.md"))
    assert len(files) == 1
    body = files[0].read_text(encoding="utf-8")
    assert "project_slug: proj-x" in body
    assert "topic: install-db" in body
    assert "status: active" in body


def test_default_expiry_is_seven_days(tmp_path):
    eng = CarryoverEngine(tmp_path)
    c = eng.create(project_slug="x", topic="t", today=date(2026, 5, 24))
    assert (c.expires - c.created).days == 7


def test_list_returns_all(tmp_path):
    eng = CarryoverEngine(tmp_path)
    eng.create(project_slug="a", topic="t1", today=date(2026, 5, 24))
    eng.create(project_slug="b", topic="t2", today=date(2026, 5, 24))
    items = eng.list_all()
    assert {i.project_slug for i in items} == {"a", "b"}


def test_expire_marks_overdue(tmp_path):
    eng = CarryoverEngine(tmp_path)
    eng.create(project_slug="old", topic="t", today=date(2026, 5, 1))
    expired = eng.expire(today=date(2026, 5, 24))
    assert len(expired) == 1
    assert expired[0].project_slug == "old"
    files = list((tmp_path / "memory" / "carryover").glob("*.md"))
    body = files[0].read_text(encoding="utf-8")
    assert "status: expired" in body


def test_promote_to_episodic_moves_file(tmp_path):
    eng = CarryoverEngine(tmp_path)
    eng.create(project_slug="proj", topic="x", today=date(2026, 5, 24))
    moved = eng.promote_to_episodic(project_slug="proj", topic="x")
    assert moved is not None
    files = list((tmp_path / "memory" / "carryover").glob("*.md"))
    assert len(files) == 0
