from click.testing import CliRunner

from gshell_memory.cli.main import gish


def test_cli_enum_freeze_and_list(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    r = runner.invoke(
        gish,
        [
            "enum",
            "freeze",
            "--name",
            "decision_kind",
            "--value",
            "brain_decision",
            "--value",
            "agent_output",
            "--introduced",
            "2026-05-24",
            "--layer",
            "metadata",
            "--workspace",
            str(tmp_path),
        ],
    )
    assert r.exit_code == 0, r.output
    out = runner.invoke(gish, ["enum", "list", "--workspace", str(tmp_path)])
    assert "decision_kind" in out.output


def test_cli_enum_validate(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    runner.invoke(
        gish,
        [
            "enum",
            "freeze",
            "--name",
            "status",
            "--value",
            "ok",
            "--introduced",
            "2026-05-24",
            "--layer",
            "l",
            "--workspace",
            str(tmp_path),
        ],
    )
    good = runner.invoke(
        gish,
        [
            "enum",
            "validate",
            "--name",
            "status",
            "--candidate",
            "ok",
            "--workspace",
            str(tmp_path),
        ],
    )
    assert good.exit_code == 0
    bad = runner.invoke(
        gish,
        [
            "enum",
            "validate",
            "--name",
            "status",
            "--candidate",
            "unknown",
            "--workspace",
            str(tmp_path),
        ],
    )
    assert bad.exit_code != 0
