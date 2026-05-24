import pytest


def test_sop_route_minimal():
    from gshell_memory_schema.models import SOPRoute

    route = SOPRoute(
        name="example",
        triggers=["foo", "bar"],
        must_read=["docs/x.md"],
    )
    assert route.name == "example"
    assert route.also_read == []
    assert route.skills_pipeline == []


def test_sop_route_full():
    from gshell_memory_schema.models import SOPRoute

    route = SOPRoute(
        name="full",
        triggers=["a"],
        must_read=["a.md"],
        also_read=["b.md"],
        skills_pipeline=["/skill1", "/skill2"],
        note="example note",
        inline_sop="1. step\n2. step",
    )
    assert route.skills_pipeline == ["/skill1", "/skill2"]


def test_sop_route_requires_triggers():
    import pydantic
    from gshell_memory_schema.models import SOPRoute

    with pytest.raises(pydantic.ValidationError):
        SOPRoute(name="bad", triggers=[], must_read=["x.md"])


def test_sop_route_requires_must_read():
    import pydantic
    from gshell_memory_schema.models import SOPRoute

    with pytest.raises(pydantic.ValidationError):
        SOPRoute(name="bad", triggers=["x"], must_read=[])
