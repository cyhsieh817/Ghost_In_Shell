"""BrainRegionRouter — 5 fixed regions, file→region index (spec § 4.4)."""

from __future__ import annotations

import yaml

from gshell_memory.memory._paths import WorkspacePaths
from gshell_memory.memory.schemas import BrainRegionManifest


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
        raw = yaml.safe_load(
            self._paths.brain_region_manifest.read_text(encoding="utf-8")
        )
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
