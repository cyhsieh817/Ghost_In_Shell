import pytest
from gshell_memory.engines.enum_freeze import FrozenEnumEngine


def test_freeze_then_list(tmp_path):
    (tmp_path / "memory").mkdir()
    eng = FrozenEnumEngine(tmp_path)
    eng.freeze(
        "decision_kind",
        ["brain_decision", "agent_output"],
        introduced="2026-05-24",
        layer="metadata",
        enforcement="audit",
    )
    items = eng.list_all()
    assert len(items) == 1
    assert items[0].name == "decision_kind"


def test_freeze_rejects_redefinition_with_different_values(tmp_path):
    (tmp_path / "memory").mkdir()
    eng = FrozenEnumEngine(tmp_path)
    eng.freeze("x", ["a", "b"], introduced="2026-05-24", layer="l", enforcement="audit")
    with pytest.raises(ValueError, match="different values"):
        eng.freeze("x", ["a", "c"], introduced="2026-05-24", layer="l", enforcement="audit")


def test_validate_value_in_enum(tmp_path):
    (tmp_path / "memory").mkdir()
    eng = FrozenEnumEngine(tmp_path)
    eng.freeze("status", ["ok", "fail"], introduced="2026-05-24", layer="l", enforcement="block")
    assert eng.validate("status", "ok") is True
    assert eng.validate("status", "unknown") is False


def test_validate_unknown_enum_raises(tmp_path):
    (tmp_path / "memory").mkdir()
    eng = FrozenEnumEngine(tmp_path)
    with pytest.raises(KeyError):
        eng.validate("nonexistent", "anything")
