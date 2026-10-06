"""Single-writer guard: only the primary machine writes memory.

When one workspace is shared by several machines (a synced folder, a NAS,
a second laptop), two writers will eventually allocate the same episode id
or rewrite episodic.jsonl from stale reads. The fix is organisational, not
clever locking: exactly one machine is ``primary`` and owns every write.
Other machines are ``secondary`` and may only read.

The role is device-local by design. It is resolved, in order, from:

1. the ``GISH_MACHINE_ROLE`` environment variable;
2. ``$XDG_CONFIG_HOME/gish/machine_role`` (default ``~/.config/gish/machine_role``).

It is never read from inside the workspace: a role file stored in a synced
folder would sync to every machine and make them all ``primary``.

A machine with no role configured is treated as ``primary`` so that the
common single-machine setup needs no configuration.
"""

from __future__ import annotations

import os
from pathlib import Path

ROLE_ENV = "GISH_MACHINE_ROLE"
VALID_ROLES = ("primary", "secondary")


class SecondaryWriteRefused(RuntimeError):
    """Raised when a secondary machine attempts a memory write."""


def device_config_dir() -> Path:
    """Per-machine gish config: ``$XDG_CONFIG_HOME/gish`` (default ``~/.config/gish``)."""
    base = os.environ.get("XDG_CONFIG_HOME")
    root = Path(base) if base else Path.home() / ".config"
    return root / "gish"


def role_file() -> Path:
    return device_config_dir() / "machine_role"


def machine_role() -> str:
    """Return ``primary`` or ``secondary``. Unknown values fail closed to ``secondary``."""
    raw = os.environ.get(ROLE_ENV)
    if raw is None:
        path = role_file()
        raw = path.read_text(encoding="utf-8") if path.is_file() else "primary"
    role = raw.strip().lower()
    return role if role in VALID_ROLES else "secondary"


def is_primary() -> bool:
    return machine_role() == "primary"


def require_primary(action: str) -> None:
    """Refuse ``action`` unless this machine is the primary writer."""
    if not is_primary():
        raise SecondaryWriteRefused(
            f"refused: {action} writes memory, but this machine's role is "
            f"'{machine_role()}'. Run it on the primary machine, or set "
            f"{ROLE_ENV}=primary if this machine is the single writer."
        )
