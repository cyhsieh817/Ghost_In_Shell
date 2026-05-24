import pytest


def test_subdir_registry_minimal():
    from gshell_memory_schema.models import SubdirRegistry

    reg = SubdirRegistry(
        registered=[
            {"path": "memory/_archive/", "purpose": "archive", "lifecycle": "permanent"},
        ],
        enforcement="warn",
    )
    assert reg.enforcement == "warn"
    assert len(reg.registered) == 1


def test_subdir_registry_block_mode():
    from gshell_memory_schema.models import SubdirRegistry

    reg = SubdirRegistry(registered=[], enforcement="block")
    assert reg.enforcement == "block"


def test_subdir_registry_enforcement_enum():
    import pydantic
    from gshell_memory_schema.models import SubdirRegistry

    with pytest.raises(pydantic.ValidationError):
        SubdirRegistry(registered=[], enforcement="off")
