import pytest


def test_frozen_enum_basic():
    from gshell_memory_schema.models import FrozenEnum

    e = FrozenEnum(
        name="decision_kind",
        values=["brain_decision", "agent_output", "structured_data"],
        introduced="2026-04-26",
        layer="agent_run_artifacts.metadata.decision_kind",
        enforcement="audit",
    )
    assert "brain_decision" in e.values


def test_frozen_enum_rejects_duplicate_values():
    import pydantic
    from gshell_memory_schema.models import FrozenEnum

    with pytest.raises(pydantic.ValidationError):
        FrozenEnum(
            name="x",
            values=["a", "a"],
            introduced="2026-01-01",
            layer="y",
            enforcement="audit",
        )


def test_frozen_enum_helper_freeze():
    from gshell_memory_schema.enums import freeze

    registry = {}
    freeze(
        registry,
        "rerun_status",
        ["supported", "unsupported", "pending"],
        introduced="2026-04-26",
        layer="manifest.toml",
    )
    assert "rerun_status" in registry
    assert registry["rerun_status"].values == ["supported", "unsupported", "pending"]


def test_freeze_helper_rejects_duplicate_name_with_different_values():
    import pytest
    from gshell_memory_schema.enums import freeze

    registry = {}
    freeze(
        registry,
        "rerun_status",
        ["supported", "unsupported", "pending"],
        introduced="2026-04-26",
        layer="manifest.toml",
    )
    with pytest.raises(ValueError, match="already registered with different values"):
        freeze(
            registry,
            "rerun_status",
            ["supported", "unsupported"],
            introduced="2026-04-26",
            layer="manifest.toml",
        )
