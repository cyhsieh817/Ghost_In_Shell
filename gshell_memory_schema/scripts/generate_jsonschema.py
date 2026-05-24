"""Generate JSON Schema files from Pydantic models.

Usage:
  python scripts/generate_jsonschema.py            # write files
  python scripts/generate_jsonschema.py --check    # CI mode: fail if out of sync
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from gshell_memory_schema import models

_SNAKE_PASS1 = re.compile(r"(.)([A-Z][a-z]+)")
_SNAKE_PASS2 = re.compile(r"([a-z0-9])([A-Z])")

MODEL_NAMES = [
    "Workspace",
    "FactStore",
    "EpisodicEntry",
    "Association",
    "BrainRegionManifest",
    "BrainRegionExtension",
    "SanctumRegistry",
    "RuntimeProfiles",
    "MemoryManifest",
    "SOPRoute",
    "ArchiveRoute",
    "Carryover",
    "FrozenEnum",
    "HeartbeatConfig",
    "SubdirRegistry",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if out of sync.")
    args = parser.parse_args()

    out_dir = Path(__file__).resolve().parent.parent / "gshell_memory_schema" / "jsonschema"
    out_dir.mkdir(parents=True, exist_ok=True)

    diffs: list[str] = []
    for name in MODEL_NAMES:
        cls = getattr(models, name)
        schema = cls.model_json_schema()
        path = out_dir / f"{_snake(name)}.json"
        new = json.dumps(schema, indent=2, sort_keys=True) + "\n"
        if args.check:
            existing = path.read_text(encoding="utf-8") if path.exists() else ""
            if existing != new:
                diffs.append(str(path.relative_to(out_dir.parent.parent)))
        else:
            path.write_text(new, encoding="utf-8")
            print(f"wrote {path.relative_to(out_dir.parent.parent)}")

    if args.check and diffs:
        print("Out-of-sync JSON Schema files:", file=sys.stderr)
        for d in diffs:
            print(f"  {d}", file=sys.stderr)
        print("Run: python scripts/generate_jsonschema.py", file=sys.stderr)
        return 1
    return 0


def _snake(name: str) -> str:
    """Convert PascalCase/CamelCase to snake_case, handling acronyms."""
    s = _SNAKE_PASS1.sub(r"\1_\2", name)
    return _SNAKE_PASS2.sub(r"\1_\2", s).lower()


if __name__ == "__main__":
    sys.exit(main())
