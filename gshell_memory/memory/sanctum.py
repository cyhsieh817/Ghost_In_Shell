"""SanctumRegistry — tier-based action verdict (spec § 4.5)."""

from __future__ import annotations

import yaml

from gshell_memory.memory._paths import WorkspacePaths
from gshell_memory.memory.schemas import SanctumRegistry as SanctumRegistrySchema

# Tier ordering: public < private < sacred
_TIER_ORDER = {"public": 0, "private": 1, "sacred": 2}


class Verdict:
    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"


class SanctumRegistry:
    """Load and query the sanctum registry for action verdicts."""

    def __init__(self, paths: WorkspacePaths) -> None:
        self._paths = paths
        self._registry: SanctumRegistrySchema | None = None

    # ------------------------------------------------------------------
    def load(self) -> SanctumRegistrySchema:
        p = self._paths.sanctum_registry
        if not p.exists():
            self._registry = SanctumRegistrySchema()
            return self._registry
        raw = yaml.safe_load(p.read_text(encoding="utf-8"))
        self._registry = SanctumRegistrySchema(**(raw or {}))
        return self._registry

    # ------------------------------------------------------------------
    def verdict(self, file_path: str, action: str) -> str:
        """Return ALLOW / DENY / WARN for the given file + action pair.

        Rules:
        - public tier: ALLOW all
        - private tier: WARN on write, DENY on delete
        - sacred tier: DENY on write and delete, WARN on read
        """
        if self._registry is None:
            self.load()

        entry = next(
            (e for e in (self._registry.entries if self._registry else []) if e.path == file_path),
            None,
        )
        if entry is None:
            return Verdict.ALLOW

        tier = entry.tier
        if action not in entry.enforced_actions:
            return Verdict.ALLOW

        if tier == "public":
            return Verdict.ALLOW
        if tier == "private":
            if action == "delete":
                return Verdict.DENY
            return Verdict.WARN
        # sacred
        if action == "read":
            return Verdict.WARN
        return Verdict.DENY
