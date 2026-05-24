from click.testing import CliRunner

from gshell_memory.cli.main import gish


def test_cli_archive_add_then_list(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    add = runner.invoke(
        gish,
        [
            "archive",
            "route",
            "add",
            "--condition",
            "tag:security",
            "--target-dir",
            "logs/security/",
            "--naming-pattern",
            "YYYY-Www.md",
            "--priority",
            "1",
            "--workspace",
            str(tmp_path),
        ],
    )
    assert add.exit_code == 0, add.output
    lst = runner.invoke(gish, ["archive", "route", "list", "--workspace", str(tmp_path)])
    assert "security" in lst.output


def test_cli_archive_preview(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    runner.invoke(
        gish,
        [
            "archive",
            "route",
            "add",
            "--condition",
            "tag:security",
            "--target-dir",
            "logs/security/",
            "--naming-pattern",
            "YYYY-Www.md",
            "--priority",
            "1",
            "--workspace",
            str(tmp_path),
        ],
    )
    out = runner.invoke(
        gish,
        [
            "archive",
            "route",
            "preview",
            "--input",
            "tag:security CVE",
            "--workspace",
            str(tmp_path),
        ],
    )
    assert "logs/security/" in out.output
