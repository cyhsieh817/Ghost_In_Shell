"""Schema version compatibility utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SchemaVersion:
    major: int
    minor: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"


_VERSION_RE = re.compile(r"^(\d+)\.(\d+)$")


def parse(s: str | float | int) -> SchemaVersion:
    if isinstance(s, (int, float)):
        s = str(s)
    m = _VERSION_RE.match(s.strip())
    if not m:
        raise ValueError(f"invalid schema version: {s!r}")
    return SchemaVersion(int(m.group(1)), int(m.group(2)))


def is_compatible(workspace: SchemaVersion, package: SchemaVersion) -> bool:
    """Forward-compatible within same major; minor mismatch okay."""
    return workspace.major == package.major and workspace.minor <= package.minor
