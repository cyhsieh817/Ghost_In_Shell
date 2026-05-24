from pathlib import Path

import yaml
from gshell_memory_schema.models import ArchiveRoute

from gshell_memory.engines.archive_router import ArchiveRouter


def _ws(tmp_path: Path, routes: list[dict]) -> Path:
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "archive_routing.yml").write_text(yaml.safe_dump({"routes": routes}))
    return tmp_path


def test_routes_sorted_by_priority(tmp_path):
    ws = _ws(
        tmp_path,
        [
            {"condition": "low", "target_dir": "low/", "naming_pattern": "x.md", "priority": 10},
            {"condition": "high", "target_dir": "high/", "naming_pattern": "y.md", "priority": 1},
        ],
    )
    router = ArchiveRouter(ws)
    routes = router.list_routes()
    assert routes[0].priority == 1


def test_preview_returns_first_match(tmp_path):
    ws = _ws(
        tmp_path,
        [
            {
                "condition": "tag:security",
                "target_dir": "logs/security/",
                "naming_pattern": "YYYY-Www.md",
                "priority": 1,
            },
            {
                "condition": "tag:learning",
                "target_dir": "logs/learning/",
                "naming_pattern": "YYYY-MM-DD-{slug}.md",
                "priority": 10,
            },
        ],
    )
    router = ArchiveRouter(ws)
    chosen = router.preview("tag:security CVE-2026-9999")
    assert chosen is not None
    assert chosen.target_dir == "logs/security/"


def test_preview_no_match(tmp_path):
    ws = _ws(tmp_path, [])
    router = ArchiveRouter(ws)
    assert router.preview("anything") is None


def test_add_route(tmp_path):
    (tmp_path / "memory").mkdir()
    router = ArchiveRouter(tmp_path)
    router.add(
        ArchiveRoute(
            condition="tag:x",
            target_dir="dir/",
            naming_pattern="n.md",
            priority=5,
        )
    )
    assert len(router.list_routes()) == 1
