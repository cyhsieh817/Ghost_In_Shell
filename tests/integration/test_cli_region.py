from pathlib import Path

import yaml
from click.testing import CliRunner

from gshell_memory.cli.main import gish


def _bootstrap_workspace(tmp_path: Path):
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "brain_region_manifest.yml").write_text(
        yaml.safe_dump(
            {
                "schema_version": "5.1",
                "regions": {
                    r: {"display": r, "core_files": [], "on_demand_files": []}
                    for r in ["hippocampus", "prefrontal", "limbic", "cerebellum", "default"]
                },
            }
        )
    )


def test_cli_region_declare_and_list(tmp_path):
    _bootstrap_workspace(tmp_path)
    runner = CliRunner()
    r = runner.invoke(
        gish,
        [
            "region",
            "declare",
            "amygdala",
            "--display",
            "amygdala (security / vigilance)",
            "--on-demand",
            "POLICY.md",
            "--aliases",
            "security",
            "--workspace",
            str(tmp_path),
        ],
    )
    assert r.exit_code == 0, r.output
    out = runner.invoke(gish, ["region", "list", "--workspace", str(tmp_path)])
    assert "amygdala" in out.output
    assert "extension" in out.output
