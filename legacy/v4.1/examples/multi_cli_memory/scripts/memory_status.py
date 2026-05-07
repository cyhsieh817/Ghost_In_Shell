#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter

from _paths import MEMORY

EPISODIC = MEMORY / "episodic.jsonl"


def load_entries() -> list[dict]:
    if not EPISODIC.exists():
        return []
    entries: list[dict] = []
    for line in EPISODIC.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entries.append(json.loads(line))
    return entries


def main() -> None:
    entries = load_entries()
    statuses = Counter(entry.get("decay_status", "active") for entry in entries)
    runtimes = Counter(entry.get("runtime", "unknown") for entry in entries)
    print("Ghost In Shell Memory Status")
    print("-" * 30)
    print(f"Entries: {len(entries)}")
    print(f"Active: {statuses.get('active', 0)}")
    print(f"Fading: {statuses.get('fading', 0)}")
    print(f"Archived: {statuses.get('archived', 0)}")
    if runtimes:
        print("Runtimes:")
        for runtime, count in sorted(runtimes.items()):
            print(f"  - {runtime}: {count}")


if __name__ == "__main__":
    main()
