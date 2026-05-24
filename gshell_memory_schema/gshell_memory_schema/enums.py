"""Helpers for working with FrozenEnum registrations."""

from __future__ import annotations

from typing import Literal

from gshell_memory_schema.models import FrozenEnum


def freeze(
    registry: dict[str, FrozenEnum],
    name: str,
    values: list[str],
    *,
    introduced: str,
    layer: str,
    enforcement: Literal["audit", "block"] = "audit",
    spec_ref: str | None = None,
) -> FrozenEnum:
    """Register a frozen enum into ``registry``.

    Raises ``ValueError`` if ``name`` is already registered with different values.
    """
    enum = FrozenEnum(
        name=name,
        values=values,
        introduced=introduced,
        layer=layer,
        enforcement=enforcement,
        spec_ref=spec_ref,
    )
    if name in registry and registry[name].values != enum.values:
        raise ValueError(f"frozen enum {name!r} already registered with different values")
    registry[name] = enum
    return enum
