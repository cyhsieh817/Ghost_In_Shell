import yaml

from gshell_memory.memory.brain_regions import BrainRegionStore


def _manifest(tmp_path, extensions=None):
    (tmp_path / "memory").mkdir()
    base = {
        "schema_version": "5.1",
        "regions": {
            r: {"display": r, "core_files": [], "on_demand_files": []}
            for r in ["hippocampus", "prefrontal", "limbic", "cerebellum", "default"]
        },
    }
    if extensions:
        base["extensions"] = extensions
    (tmp_path / "memory" / "brain_region_manifest.yml").write_text(yaml.safe_dump(base))
    return tmp_path


def test_declare_adds_extension(tmp_path):
    ws = _manifest(tmp_path)
    store = BrainRegionStore(ws)
    store.declare(
        "amygdala", display="amygdala", on_demand_files=["POLICY.md"], aliases=["security"]
    )
    reloaded = yaml.safe_load((ws / "memory" / "brain_region_manifest.yml").read_text())
    assert "amygdala" in reloaded["extensions"]
    assert reloaded["extensions"]["amygdala"]["aliases"] == ["security"]


def test_declare_rejects_name_collision_with_default(tmp_path):
    import pytest

    ws = _manifest(tmp_path)
    store = BrainRegionStore(ws)
    with pytest.raises(ValueError, match="reserved"):
        store.declare("hippocampus", display="x")


def test_list_includes_extensions(tmp_path):
    ws = _manifest(
        tmp_path,
        extensions={
            "amygdala": {"display": "amygdala", "core_files": [], "on_demand_files": []},
        },
    )
    store = BrainRegionStore(ws)
    names = [r["name"] for r in store.list_all()]
    assert "amygdala" in names
    assert "hippocampus" in names
