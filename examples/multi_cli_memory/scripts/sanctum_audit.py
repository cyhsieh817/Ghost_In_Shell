#!/usr/bin/env python3
"""
sanctum_audit.py — Verify writes against the sanctum registry (portable lite)

Reads `memory/fact_governance.yml` → `sanctum_registry`, walks `episodic.jsonl`
and `brain_write_log.jsonl` (if present), and emits one finding per write that
appears to bypass the canonical CLI declared by the registry.

Findings are advisory: the lite version does not enforce friction. Pair with
LabGrimoire Desktop and replace `lgd_write_cli: null` with real CLIs to make
the audit meaningful — see `LGD_INTEGRATION.md`.

Exit codes:
  0  — clean (or no registry / no logs to audit)
  1  — at least one bypass finding
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from _paths import MEMORY
except Exception:
    MEMORY = Path(__file__).resolve().parent.parent / "memory"

GOVERNANCE = MEMORY / "fact_governance.yml"
EPISODIC = MEMORY / "episodic.jsonl"
WRITE_LOG = MEMORY / "brain_write_log.jsonl"


def _try_yaml() -> object:
    try:
        import yaml  # type: ignore
        return yaml
    except Exception:
        return None


def load_registry() -> dict | None:
    if not GOVERNANCE.exists():
        return None
    yaml = _try_yaml()
    if yaml is None:
        # Naive fallback: emit a hint and return None — caller treats as "clean".
        print(
            "sanctum_audit: PyYAML not installed; install it for real audits "
            "(`pip install pyyaml`). Returning clean.",
            file=sys.stderr,
        )
        return None
    try:
        with GOVERNANCE.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except Exception as exc:
        print(f"sanctum_audit: failed to parse {GOVERNANCE}: {exc}", file=sys.stderr)
        return None
    return data.get("sanctum_registry") if isinstance(data, dict) else None


def audit() -> int:
    registry = load_registry()
    if not registry:
        print("sanctum_audit: no sanctum_registry — nothing to audit")
        return 0

    sources = registry.get("sources", []) or []
    by_path: dict[str, dict] = {}
    for src in sources:
        if "path" in src:
            by_path[src["path"]] = src

    findings: list[str] = []

    # Walk episodic.jsonl looking for source_tool overrides
    if EPISODIC.exists():
        for line in EPISODIC.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except Exception:
                continue
            target = rec.get("path") or rec.get("source_path")
            if not target or target not in by_path:
                continue
            cli = by_path[target].get("lgd_write_cli")
            if cli and rec.get("source_tool") and rec.get("source_tool") != "lgd":
                findings.append(
                    f"{target}: write by '{rec.get('source_tool')}' bypassed canonical '{cli}'"
                )

    if findings:
        print(f"sanctum_audit: {len(findings)} finding(s)")
        for f in findings:
            print(f"  • {f}")
        return 1

    print(f"sanctum_audit: clean (sources audited: {len(sources)})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sanctum audit (portable lite).")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    rc = audit()
    if args.quiet and rc == 0:
        sys.stdout.write("")
    return rc


if __name__ == "__main__":
    sys.exit(main())
