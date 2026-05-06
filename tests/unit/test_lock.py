"""Tests for ghost_in_shell.memory._lock — file-based lock context manager."""

import multiprocessing
import time
from pathlib import Path

from ghost_in_shell.memory._lock import file_lock


def _holds_lock(lock_path: str, hold_seconds: float) -> None:
    with file_lock(Path(lock_path)):
        time.sleep(hold_seconds)


def test_file_lock_blocks_concurrent_holder(tmp_path: Path):
    lock = tmp_path / "x.lock"
    p = multiprocessing.Process(target=_holds_lock, args=(str(lock), 0.4))
    p.start()
    time.sleep(0.05)  # let p acquire
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
