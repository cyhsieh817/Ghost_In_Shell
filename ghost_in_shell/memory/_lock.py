"""File-based lock using fcntl on POSIX, msvcrt on Windows. Cross-platform."""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def file_lock(lock_path: Path, timeout: float = 30.0):
    """Block until the lock is acquired or timeout (seconds) elapses."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + timeout
    fh = open(lock_path, "a+")
    try:
        if os.name == "posix":
            import fcntl

            while True:
                try:
                    fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.time() > deadline:
                        raise TimeoutError(f"could not acquire {lock_path} within {timeout}s")
                    time.sleep(0.05)
            try:
                yield
            finally:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        else:  # pragma: no cover — Windows path
            import msvcrt

            while True:
                try:
                    msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    if time.time() > deadline:
                        raise TimeoutError(f"could not acquire {lock_path} within {timeout}s")
                    time.sleep(0.05)
            try:
                yield
            finally:
                msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
    finally:
        fh.close()
