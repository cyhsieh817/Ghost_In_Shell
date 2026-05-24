from datetime import date

import pytest


def test_carryover_minimal():
    from gshell_memory_schema.models import Carryover

    c = Carryover(
        project_slug="proj-x",
        topic="install-db",
        created=date(2026, 5, 24),
        expires=date(2026, 5, 31),
        status="active",
    )
    assert c.status == "active"


def test_carryover_rejects_too_long_expiry():
    import pydantic
    from gshell_memory_schema.models import Carryover

    with pytest.raises(pydantic.ValidationError):
        Carryover(
            project_slug="x",
            topic="t",
            created=date(2026, 5, 24),
            expires=date(2026, 6, 5),  # 12 days
            status="active",
        )


def test_carryover_rejects_inverted_dates():
    import pydantic
    from gshell_memory_schema.models import Carryover

    with pytest.raises(pydantic.ValidationError):
        Carryover(
            project_slug="x",
            topic="t",
            created=date(2026, 5, 31),
            expires=date(2026, 5, 24),
            status="active",
        )


def test_carryover_status_enum():
    import pydantic
    from gshell_memory_schema.models import Carryover

    with pytest.raises(pydantic.ValidationError):
        Carryover(
            project_slug="x",
            topic="t",
            created=date(2026, 5, 24),
            expires=date(2026, 5, 25),
            status="invalid_state",
        )
