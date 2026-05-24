"""BrainRegionRouter — 5 fixed regions, file→region index (spec § 4.4).

Also exposes :class:`BrainRegionStore` (spec § 5.1) which manages the
manifest file directly and supports opt-in extension regions beyond the
5 immutable defaults.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from gshell_memory_schema.models import BrainRegionExtension

from gshell_memory.memory._paths import WorkspacePaths
from gshell_memory.memory.schemas import BrainRegionManifest

DEFAULT_REGIONS = {"hippocampus", "prefrontal", "limbic", "cerebellum", "default"}


class BrainRegionStore:
    """Read/write the brain-region manifest and manage extension regions."""

    def __init__(self, workspace_path: Path | str) -> None:
        self.workspace_path = Path(workspace_path)
        self._file = self.workspace_path / "memory" / "brain_region_manifest.yml"

    def _load(self) -> dict:
        if not self._file.exists():
            raise FileNotFoundError(self._file)
        return yaml.safe_load(self._file.read_text(encoding="utf-8")) or {}

    def _save(self, data: dict) -> None:
        self._file.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    def declare(
        self,
        name: str,
        *,
        display: str,
        core_files: list[str] | None = None,
        on_demand_files: list[str] | None = None,
        aliases: list[str] | None = None,
    ) -> BrainRegionExtension:
        if name in DEFAULT_REGIONS:
            raise ValueError(f"{name!r} is a reserved default region")
        data = self._load()
        ext = BrainRegionExtension(
            display=display,
            core_files=[{"path": p} for p in (core_files or [])],
            on_demand_files=[{"path": p} for p in (on_demand_files or [])],
            aliases=list(aliases or []),
        )
        data.setdefault("extensions", {})[name] = ext.model_dump(exclude_none=True)
        self._save(data)
        return ext

    def list_all(self) -> list[dict]:
        data = self._load()
        out = [{"name": n, "kind": "default", **v} for n, v in data.get("regions", {}).items()]
        for n, v in (data.get("extensions") or {}).items():
            out.append({"name": n, "kind": "extension", **v})
        return out


class BrainRegionRouter:
    """Route files to one of the 5 fixed brain regions.

    Builds an index of ``path → region`` from the manifest so lookup is O(1).
    """

    def __init__(self, paths: WorkspacePaths) -> None:
        self._paths = paths
        self._manifest: BrainRegionManifest | None = None
        self._index: dict[str, str] = {}

    # ------------------------------------------------------------------
    def load(self) -> BrainRegionManifest:
        raw = yaml.safe_load(self._paths.brain_region_manifest.read_text(encoding="utf-8"))
        self._manifest = BrainRegionManifest(**raw)
        self._index = {}
        for region_name, region_def in self._manifest.regions.items():
            for file_ref in region_def.core_files + region_def.on_demand_files:
                self._index[file_ref.path] = region_name
        return self._manifest

    # ------------------------------------------------------------------
    def region_for(self, file_path: str) -> str:
        """Return the region name for *file_path*, or ``"default"``."""
        if self._manifest is None:
            try:
                self.load()
            except FileNotFoundError:
                return "default"
        return self._index.get(file_path, "default")

    # ------------------------------------------------------------------
    def files_in_region(self, region: str) -> list[str]:
        """Return all file paths assigned to *region*."""
        if self._manifest is None:
            try:
                self.load()
            except FileNotFoundError:
                return []
        rd = self._manifest.regions.get(region)
        if rd is None:
            return []
        return [f.path for f in rd.core_files + rd.on_demand_files]
