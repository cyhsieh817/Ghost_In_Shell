"""CLI smoke tests — `gish version` works, subcommands listed in --help."""

from click.testing import CliRunner

from ghost_in_shell.cli.main import gish


def test_gish_version_prints_version():
    runner = CliRunner()
    result = runner.invoke(gish, ["version"])
    assert result.exit_code == 0
    assert "5.0.0rc1" in result.output


def test_gish_help_lists_all_subcommands():
    runner = CliRunner()
    result = runner.invoke(gish, ["--help"])
    assert result.exit_code == 0
    for sub in ["init", "doctor", "recall", "audit", "run-maintenance", "log", "version", "migrate"]:
        assert sub in result.output, f"subcommand {sub!r} missing from --help"
