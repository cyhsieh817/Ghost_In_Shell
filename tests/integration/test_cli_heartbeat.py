from click.testing import CliRunner

from gshell_memory.cli.main import gish


def test_cli_heartbeat_run(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    r = runner.invoke(
        gish,
        [
            "heartbeat",
            "run",
            "--workspace",
            str(tmp_path),
        ],
    )
    assert r.exit_code == 0
    assert "OK" in r.output


def test_cli_heartbeat_install_cron_prints_snippet(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    r = runner.invoke(
        gish,
        [
            "heartbeat",
            "install",
            "--cron",
            "--workspace",
            str(tmp_path),
        ],
    )
    assert r.exit_code == 0
    assert "0 * * * *" in r.output  # default hourly cadence


def test_cli_heartbeat_install_launchd_prints_plist(tmp_path):
    (tmp_path / "memory").mkdir()
    runner = CliRunner()
    r = runner.invoke(
        gish,
        [
            "heartbeat",
            "install",
            "--launchd",
            "--workspace",
            str(tmp_path),
        ],
    )
    assert r.exit_code == 0
    assert "io.gshell-memory.heartbeat" in r.output
