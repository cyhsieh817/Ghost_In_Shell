#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from _paths import MEMORY

EPISODIC = MEMORY / "episodic.jsonl"
THRESHOLD = max(1, int(os.environ.get("GHOST_MEMORY_TRIGGER_THRESHOLD", "5")))


def load_entries() -> list[dict]:
    if not EPISODIC.exists():
        return []
    entries: list[dict] = []
    for line in EPISODIC.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entries.append(json.loads(line))
    return entries


def main() -> int:
    count = len(load_entries())
    if count > 0 and count % THRESHOLD == 0:
        print(f"Trigger threshold reached: {count} total entries (threshold={THRESHOLD})")
        return 0
    remaining = THRESHOLD - (count % THRESHOLD) if count % THRESHOLD else THRESHOLD
    print(f"No trigger yet: {remaining} more entries until suggested review (threshold={THRESHOLD})")
    return 1


if __name__ == "__main__":
    sys.exit(main())
