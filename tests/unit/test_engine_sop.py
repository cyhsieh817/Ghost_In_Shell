from pathlib import Path

import pytest
import yaml
from gshell_memory_schema.models import SOPRoute

from gshell_memory.engines.sop import SOPEngine


def _ws_with_sop(tmp_path: Path, routes: list[dict]) -> Path:
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "sop_dispatch.yml").write_text(yaml.safe_dump({"routes": routes}))
    return tmp_path


def test_engine_loads_routes(tmp_path):
    ws = _ws_with_sop(
        tmp_path,
        [
            {"name": "popsci", "triggers": ["科普", "popsci"], "must_read": ["docs/popsci.md"]},
        ],
    )
    engine = SOPEngine(ws)
    routes = engine.list_routes()
    assert len(routes) == 1
    assert isinstance(routes[0], SOPRoute)
    assert routes[0].name == "popsci"


def test_engine_trigger_matches_substring(tmp_path):
    ws = _ws_with_sop(
        tmp_path,
        [
            {"name": "popsci", "triggers": ["科普"], "must_read": ["a.md"]},
            {"name": "irb", "triggers": ["IRB", "倫理審查"], "must_read": ["b.md"]},
        ],
    )
    engine = SOPEngine(ws)
    hits = engine.trigger("請幫我寫一篇科普文章")
    assert [r.name for r in hits] == ["popsci"]


def test_engine_no_match(tmp_path):
    ws = _ws_with_sop(
        tmp_path,
        [
            {"name": "popsci", "triggers": ["科普"], "must_read": ["a.md"]},
        ],
    )
    engine = SOPEngine(ws)
    assert engine.trigger("hello world") == []


def test_register_rejects_duplicate_name(tmp_path):
    ws = _ws_with_sop(
        tmp_path,
        [
            {"name": "popsci", "triggers": ["a"], "must_read": ["x.md"]},
        ],
    )
    engine = SOPEngine(ws)
    with pytest.raises(ValueError, match="duplicate"):
        engine.register(SOPRoute(name="popsci", triggers=["b"], must_read=["y.md"]))
