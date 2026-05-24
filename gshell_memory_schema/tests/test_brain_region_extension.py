"""Tests for BrainRegionExtension and BrainRegionManifest.extensions block.

Compatibility note: the existing BrainRegionManifest (5.0) requires
`generated_at` plus exactly the 5 fixed regions (REQUIRED_REGIONS). The
plan's illustrative test omits `generated_at`; we keep the spirit of the
plan (verify extensions block is accepted) while honoring the existing
validators so previous tests keep passing.
"""

from __future__ import annotations


def test_brain_region_extension_minimal():
    from gshell_memory_schema.models import BrainRegionExtension

    ext = BrainRegionExtension(
        display="custom region",
        core_files=[{"path": "X.md"}],
    )
    assert ext.aliases == []
    assert ext.on_demand_files == []


def test_brain_region_extension_with_aliases():
    from gshell_memory_schema.models import BrainRegionExtension

    ext = BrainRegionExtension(
        display="security gate",
        core_files=[{"path": "POLICY.md"}],
        aliases=["warning", "safety"],
        on_demand_files=[{"path": "POLICY-extended.md"}],
    )
    assert "warning" in ext.aliases
    assert ext.on_demand_files[0]["path"] == "POLICY-extended.md"


def test_brain_region_extension_forbids_extra():
    import pytest
    from gshell_memory_schema.models import BrainRegionExtension
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        BrainRegionExtension(
            display="x",
            core_files=[],
            unknown_field="boom",  # type: ignore[call-arg]
        )


def _five_region_payload() -> dict:
    """Build a minimal 5-region payload matching REQUIRED_REGIONS."""
    return {
        name: {"display": name, "core_files": [], "on_demand_files": []}
        for name in ("hippocampus", "prefrontal", "limbic", "cerebellum", "default")
    }


def test_brain_region_manifest_accepts_extensions():
    """The existing BrainRegionManifest model accepts the new extensions block."""
    from gshell_memory_schema.models import BrainRegionManifest

    m = BrainRegionManifest(
        schema_version=1,
        generated_at="2026-05-24T00:00:00Z",
        regions=_five_region_payload(),
        extensions={
            "amygdala": {
                "display": "amygdala",
                "core_files": [{"path": "POLICY.md"}],
            },
        },
    )
    assert "amygdala" in m.extensions
    assert m.extensions["amygdala"].display == "amygdala"


def test_brain_region_manifest_extensions_default_empty():
    """Backward compat: manifests without extensions still work, default to {}."""
    from gshell_memory_schema.models import BrainRegionManifest

    m = BrainRegionManifest(
        schema_version=1,
        generated_at="2026-05-24T00:00:00Z",
        regions=_five_region_payload(),
    )
    assert m.extensions == {}
