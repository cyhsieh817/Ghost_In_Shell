from gshell_memory.engines.subdir_registry import SubdirRegistryEngine


def test_register_then_list(tmp_path):
    (tmp_path / "memory").mkdir()
    eng = SubdirRegistryEngine(tmp_path)
    eng.register(path="memory/_archive/", purpose="archive", lifecycle="permanent")
    items = eng.list_all()
    assert len(items) == 1
    assert items[0].path == "memory/_archive/"


def test_enforce_warn_returns_unregistered(tmp_path):
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "_archive").mkdir()
    (tmp_path / "memory" / "carryover").mkdir()
    (tmp_path / "memory" / "rogue").mkdir()
    eng = SubdirRegistryEngine(tmp_path)
    eng.register(path="memory/_archive/", purpose="archive", lifecycle="permanent")
    eng.register(path="memory/carryover/", purpose="carryover", lifecycle="rotating")
    unregistered = eng.enforce(mode="warn")
    assert "memory/rogue" in unregistered or "memory/rogue/" in unregistered


def test_enforce_block_raises_on_unregistered(tmp_path):
    import pytest

    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "rogue").mkdir()
    eng = SubdirRegistryEngine(tmp_path)
    eng.set_enforcement("block")
    with pytest.raises(RuntimeError, match="unregistered"):
        eng.enforce(mode="block")
