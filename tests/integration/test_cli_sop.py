from click.testing import CliRunner

from gshell_memory.cli.main import gish


def test_cli_sop_list_empty(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    result = runner.invoke(gish, ["sop", "list", "--workspace", str(tmp_path)])
    assert result.exit_code == 0
    assert "no routes" in result.output.lower()


def test_cli_sop_register_then_list(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    reg = runner.invoke(
        gish,
        [
            "sop",
            "register",
            "--name",
            "popsci",
            "--trigger",
            "科普",
            "--must-read",
            "docs/popsci.md",
            "--workspace",
            str(tmp_path),
        ],
    )
    assert reg.exit_code == 0, reg.output
    lst = runner.invoke(gish, ["sop", "list", "--workspace", str(tmp_path)])
    assert "popsci" in lst.output


def test_cli_sop_trigger(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    runner.invoke(
        gish,
        [
            "sop",
            "register",
            "--name",
            "popsci",
            "--trigger",
            "科普",
            "--must-read",
            "a.md",
            "--workspace",
            str(tmp_path),
        ],
    )
    out = runner.invoke(
        gish,
        [
            "sop",
            "trigger",
            "--text",
            "幫我寫科普",
            "--workspace",
            str(tmp_path),
        ],
    )
    assert out.exit_code == 0
    assert "popsci" in out.output
    assert "a.md" in out.output
