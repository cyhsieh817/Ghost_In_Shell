"""Deprecated alias for the gshell_memory package.

This shim exists for one minor version (5.1) only. Migrate imports
from 'ghost_in_shell' to 'gshell_memory'. Removed in 6.0.
"""

import warnings as _warnings

import gshell_memory as _gshell_memory

_warnings.warn(
    "Importing 'ghost_in_shell' is deprecated; use 'gshell_memory' instead. "
    "This alias is removed in gshell-memory 6.0.",
    DeprecationWarning,
    stacklevel=2,
)

from gshell_memory import *  # noqa: F403, E402

__all__ = _gshell_memory.__all__ if hasattr(_gshell_memory, "__all__") else []
