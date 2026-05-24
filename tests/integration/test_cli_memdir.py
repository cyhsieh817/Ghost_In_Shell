from click.testing import CliRunner

from gshell_memory.cli.main import gish


def test_cli_memdir_register_and_list(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    r = runner.invoke(
        gish,
        [
            "memory-dir",
            "register",
            "--path",
            "memory/_archive/",
            "--purpose",
            "archive",
            "--lifecycle",
            "permanent",
            "--workspace",
            str(tmp_path),
        ],
    )
    assert r.exit_code == 0, r.output
    out = runner.invoke(gish, ["memory-dir", "list", "--workspace", str(tmp_path)])
    assert "memory/_archive/" in out.output


def test_cli_memdir_enforce_warn(tmp_path):
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "rogue").mkdir()
    runner = CliRunner()
    r = runner.invoke(gish, ["memory-dir", "enforce", "--workspace", str(tmp_path)])
    assert r.exit_code == 0
    assert "rogue" in r.output
