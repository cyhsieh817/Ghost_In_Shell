#!/usr/bin/env python3
"""
memory_associate.py — Memory graph association helper (portable lite)

Subcommands:
  suggest <episode_id>     Suggest associations for a single episode (no-op
                           in the lite version — emits a structured stub so
                           the parent pipeline does not break).
  flush-buffer             Drain `.retrieval_buffer.jsonl` into associations
                           (no-op in the lite version).
  audit                    Print a summary of the current associations file.

This is a **portable seed**: it understands the on-disk schema but skips the
heavyweight scoring logic. Replace with a richer implementation when you
want true automatic linking. The full reference lives in TheVoidWeaver's
`scripts/memory_associate.py`.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    from _paths import MEMORY
except Exception:
    MEMORY = Path(__file__).resolve().parent.parent / "memory"

ASSOCIATIONS = MEMORY / "associations.jsonl"
RETRIEVAL_BUFFER = MEMORY / ".retrieval_buffer.jsonl"
EPISODIC = MEMORY / "episodic.jsonl"


def _ensure_parent() -> None:
    MEMORY.mkdir(parents=True, exist_ok=True)


def cmd_suggest(episode_id: str) -> int:
    """Emit a placeholder association stub so callers don't crash."""
    _ensure_parent()
    if not EPISODIC.exists():
        return 0
    entry = {
        "kind": "association.suggest.stub",
        "for": episode_id,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "note": "lite version — replace memory_associate.py with the full reference for real edges",
    }
    with ASSOCIATIONS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return 0


def cmd_flush_buffer() -> int:
    """No-op in lite mode — the full reference drains buffered retrievals."""
    if not RETRIEVAL_BUFFER.exists():
        return 0
    return 0


def cmd_audit() -> int:
    if not ASSOCIATIONS.exists():
        print("associations.jsonl: not yet created")
        return 0
    count = sum(1 for _ in ASSOCIATIONS.open("r", encoding="utf-8"))
    print(f"associations.jsonl: {count} edges")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Memory association helper (portable lite).")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("suggest", help="Append an association suggestion stub")
    sp.add_argument("episode_id")
    sub.add_parser("flush-buffer", help="Drain retrieval buffer (no-op in lite)")
    sub.add_parser("audit", help="Print association summary")
    args = parser.parse_args()

    if args.cmd == "suggest":
        return cmd_suggest(args.episode_id)
    if args.cmd == "flush-buffer":
        return cmd_flush_buffer()
    if args.cmd == "audit":
        return cmd_audit()
    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
