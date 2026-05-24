import pytest


def test_archive_route_minimal():
    from gshell_memory_schema.models import ArchiveRoute

    route = ArchiveRoute(
        condition="content matches /pattern/",
        target_dir="archive/x/",
        naming_pattern="YYYY-MM-DD-{slug}.md",
        priority=10,
    )
    assert route.priority == 10
    assert route.frontmatter_required == []


def test_archive_route_full():
    from gshell_memory_schema.models import ArchiveRoute

    route = ArchiveRoute(
        condition="tag includes 'security'",
        target_dir="logs/security/",
        naming_pattern="YYYY-Www-{topic}.md",
        frontmatter_required=["title", "date", "tags", "source"],
        note="weekly bucket",
        priority=5,
    )
    assert route.frontmatter_required == ["title", "date", "tags", "source"]


def test_archive_route_priority_must_be_positive():
    import pydantic
    from gshell_memory_schema.models import ArchiveRoute

    with pytest.raises(pydantic.ValidationError):
        ArchiveRoute(
            condition="x",
            target_dir="y/",
            naming_pattern="z.md",
            priority=0,
        )
