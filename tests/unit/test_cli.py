"""CLI smoke tests — `gish version` works, other subcommands stub-exit cleanly."""

import pytest
from click.testing import CliRunner

from ghost_in_shell.cli.main import gish


def test_gish_version_prints_version():
    runner = CliRunner()
    result = runner.invoke(gish, ["version"])
    assert result.exit_code == 0
    assert "5.0.0a1" in result.output


def test_gish_help_lists_all_subcommands():
    runner = CliRunner()
    result = runner.invoke(gish, ["--help"])
    assert result.exit_code == 0
    for sub in ["init", "doctor", "recall", "audit", "run-maintenance", "log", "version"]:
        assert sub in result.output, f"subcommand {sub!r} missing from --help"


@pytest.mark.parametrize(
    "subcommand",
    ["init", "doctor", "recall", "audit", "run-maintenance", "log"],
)
def test_stub_subcommands_exit_with_clear_message(subcommand):
    runner = CliRunner()
    args = [subcommand]
    if subcommand in {"init", "recall", "log"}:
        args.append("dummy-arg")
    result = runner.invoke(gish, args)
    assert "M1" in result.output or "not yet implemented" in result.output.lower()
    assert result.exit_code != 0
