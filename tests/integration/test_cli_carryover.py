from click.testing import CliRunner

from gshell_memory.cli.main import gish


def test_cli_carryover_create_and_list(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    create = runner.invoke(
        gish,
        [
            "carryover",
            "create",
            "--project",
            "proj-x",
            "--topic",
            "install-db",
            "--workspace",
            str(tmp_path),
        ],
    )
    assert create.exit_code == 0, create.output

    lst = runner.invoke(gish, ["carryover", "list", "--workspace", str(tmp_path)])
    assert "proj-x" in lst.output
    assert "install-db" in lst.output
