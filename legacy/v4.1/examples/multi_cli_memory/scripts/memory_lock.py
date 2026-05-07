from __future__ import annotations

import os
import time
from contextlib import contextmanager
from pathlib import Path

from _paths import MEMORY

LOCK_DIR = MEMORY / ".locks"
LOCK_DIR.mkdir(parents=True, exist_ok=True)


@contextmanager
def memory_lock(name: str, timeout: float = 5.0, poll: float = 0.05):
    lock_path = LOCK_DIR / f"{name}.lock"
    start = time.time()
    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            if time.time() - start >= timeout:
                raise TimeoutError(f"Timed out waiting for lock: {lock_path}")
            time.sleep(poll)
    try:
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
