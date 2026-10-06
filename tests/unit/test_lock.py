"""Tests for gshell_memory.memory._lock — file-based lock context manager."""

import multiprocessing
import time
from pathlib import Path

from gshell_memory.memory._lock import file_lock


def _holds_lock(lock_path: str, hold_seconds: float, acquired) -> None:
    with file_lock(Path(lock_path)):
        acquired.set()
        time.sleep(hold_seconds)


def test_file_lock_blocks_concurrent_holder(tmp_path: Path):
    lock = tmp_path / "x.lock"
    acquired = multiprocessing.Event()
    p = multiprocessing.Process(target=_holds_lock, args=(str(lock), 0.4, acquired))
    p.start()
    # Wait for the child to hold the lock. A fixed sleep raced the child's
    # interpreter start-up under the macOS "spawn" start method.
    assert acquired.wait(timeout=10), "child never acquired the lock"
    start = time.time()
    with file_lock(lock, timeout=2.0):
        elapsed = time.time() - start
    p.join()
    assert elapsed >= 0.3, f"expected to wait at least ~0.3s, waited {elapsed}"


def test_file_lock_releases_on_exception(tmp_path: Path):
    lock = tmp_path / "y.lock"
    try:
        with file_lock(lock, timeout=1.0):
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    # Must be acquirable again
    with file_lock(lock, timeout=1.0):
        pass
