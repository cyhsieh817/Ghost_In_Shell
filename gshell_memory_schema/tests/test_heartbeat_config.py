import pytest


def test_heartbeat_config_minimal():
    from gshell_memory_schema.models import HeartbeatConfig

    cfg = HeartbeatConfig(
        cadence="hourly",
        checks=["self_identity", "inbox", "outbox"],
    )
    assert cfg.idle_threshold == 5
    assert cfg.output_format == "summary"


def test_heartbeat_config_cadence_enum():
    import pydantic
    from gshell_memory_schema.models import HeartbeatConfig

    with pytest.raises(pydantic.ValidationError):
        HeartbeatConfig(cadence="biweekly", checks=["x"])


def test_heartbeat_config_idle_threshold_range():
    import pydantic
    from gshell_memory_schema.models import HeartbeatConfig

    with pytest.raises(pydantic.ValidationError):
        HeartbeatConfig(cadence="hourly", checks=["x"], idle_threshold=0)
    with pytest.raises(pydantic.ValidationError):
        HeartbeatConfig(cadence="hourly", checks=["x"], idle_threshold=100)
