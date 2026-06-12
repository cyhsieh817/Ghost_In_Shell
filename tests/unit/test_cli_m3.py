"""CLI M3 tests — gish init wizard + cron helper."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from gshell_memory.cli.main import gish


@pytest.fixture
def runner():
    return CliRunner()


class TestInitHelp:
    def test_init_help_exits_zero(self, runner):
        result = runner.invoke(gish, ["init", "--help"])
        assert result.exit_code == 0

    def test_init_help_shows_workspace_arg(self, runner):
        result = runner.invoke(gish, ["init", "--help"])
        assert "WORKSPACE" in result.output or "workspace" in result.output.lower()

    def test_init_help_shows_schedule_option(self, runner):
        result = runner.invoke(gish, ["init", "--help"])
        assert "--schedule" in result.output

    def test_init_help_shows_non_interactive_option(self, runner):
        result = runner.invoke(gish, ["init", "--help"])
        assert "--non-interactive" in result.output


class TestInitCreatesStructure:
    def test_creates_memory_dir(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        result = runner.invoke(gish, ["init", ws, "--non-interactive"])
        assert result.exit_code == 0, result.output
        assert (Path(ws) / "memory").is_dir()

    def test_creates_gish_dir(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        result = runner.invoke(gish, ["init", ws, "--non-interactive"])
        assert result.exit_code == 0
        assert (Path(ws) / ".gish").is_dir()

    def test_creates_config_yml(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        result = runner.invoke(gish, ["init", ws, "--non-interactive"])
        assert result.exit_code == 0
        config = Path(ws) / ".gish" / "config.yml"
        assert config.exists()
        content = config.read_text()
        assert "version: 5" in content
        assert str(Path(ws).resolve()) in content

    def test_creates_identity_md(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        result = runner.invoke(gish, ["init", ws, "--non-interactive"])
        assert result.exit_code == 0
        assert (Path(ws) / "IDENTITY.md").exists()

    def test_creates_soul_md(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        result = runner.invoke(gish, ["init", ws, "--non-interactive"])
        assert result.exit_code == 0
        assert (Path(ws) / "SOUL.md").exists()

    def test_creates_fact_yml(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        result = runner.invoke(gish, ["init", ws, "--non-interactive"])
        assert result.exit_code == 0
        assert (Path(ws) / "memory" / "fact.yml").exists()

    def test_creates_episodic_jsonl(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        result = runner.invoke(gish, ["init", ws, "--non-interactive"])
        assert result.exit_code == 0
        assert (Path(ws) / "memory" / "episodic.jsonl").exists()

    def test_creates_associations_jsonl(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        result = runner.invoke(gish, ["init", ws, "--non-interactive"])
        assert result.exit_code == 0
        assert (Path(ws) / "memory" / "associations.jsonl").exists()

    def test_creates_memory_manifest(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        result = runner.invoke(gish, ["init", ws, "--non-interactive"])
        assert result.exit_code == 0
        assert (Path(ws) / "memory" / "memory_manifest.yml").exists()

    def test_creates_brain_region_manifest(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        result = runner.invoke(gish, ["init", ws, "--non-interactive"])
        assert result.exit_code == 0
        assert (Path(ws) / "memory" / "brain_region_manifest.yml").exists()

    def test_creates_sanctum_registry(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        result = runner.invoke(gish, ["init", ws, "--non-interactive"])
        assert result.exit_code == 0
        assert (Path(ws) / "memory" / "sanctum_registry.yml").exists()

    def test_creates_runtime_profiles(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        result = runner.invoke(gish, ["init", ws, "--non-interactive"])
        assert result.exit_code == 0
        assert (Path(ws) / "memory" / "runtime_profiles.yml").exists()


class TestInitIdempotent:
    def test_second_init_does_not_fail(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        r1 = runner.invoke(gish, ["init", ws, "--non-interactive"])
        assert r1.exit_code == 0
        r2 = runner.invoke(gish, ["init", ws, "--non-interactive"])
        assert r2.exit_code == 0

    def test_second_init_does_not_overwrite_config(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        runner.invoke(gish, ["init", ws, "--non-interactive"])

        config = Path(ws) / ".gish" / "config.yml"
        original = config.read_text()
        config.write_text(original + "\n# custom note\n")

        runner.invoke(gish, ["init", ws, "--non-interactive"])
        assert "# custom note" in config.read_text()

    def test_second_init_does_not_overwrite_soul(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        runner.invoke(gish, ["init", ws, "--non-interactive"])

        soul = Path(ws) / "SOUL.md"
        soul.write_text("# custom soul\n")

        runner.invoke(gish, ["init", ws, "--non-interactive"])
        assert "# custom soul" in soul.read_text()

    def test_second_init_skipped_message(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        runner.invoke(gish, ["init", ws, "--non-interactive"])
        r2 = runner.invoke(gish, ["init", ws, "--non-interactive"])
        assert "skipped" in r2.output.lower() or "exists" in r2.output.lower()


class TestInitNonInteractive:
    def test_non_interactive_skips_prompts(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        result = runner.invoke(gish, ["init", ws, "--non-interactive"])
        assert result.exit_code == 0

    def test_non_interactive_still_creates_all_files(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        result = runner.invoke(gish, ["init", ws, "--non-interactive"])
        assert result.exit_code == 0
        ws_path = Path(ws)
        for expected in [
            "memory/fact.yml",
            "memory/episodic.jsonl",
            "memory/associations.jsonl",
            ".gish/config.yml",
            "IDENTITY.md",
            "SOUL.md",
        ]:
            assert (ws_path / expected).exists(), f"missing: {expected}"


class TestCronGeneration:
    def test_schedule_flag_triggers_cron_install(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        with patch("gshell_memory.engines._cron._install_unix_cron") as mock_cron:
            mock_cron.return_value = {"status": "installed", "system": "unix"}
            result = runner.invoke(gish, ["init", ws, "--schedule", "--non-interactive"])
        assert result.exit_code == 0
        mock_cron.assert_called_once()

    def test_cron_already_installed_does_not_fail(self, runner, tmp_path):
        ws = str(tmp_path / "ws")
        with patch("gshell_memory.engines._cron._install_unix_cron") as mock_cron:
            mock_cron.return_value = {"status": "already_installed", "system": "unix"}
            result = runner.invoke(gish, ["init", ws, "--schedule", "--non-interactive"])
        assert result.exit_code == 0

    def test_cron_lines_contain_workspace_path(self, tmp_path):
        from gshell_memory.engines._cron import _COMMENT, _CRON_TEMPLATE

        ws = tmp_path / "myworkspace"
        comment = _COMMENT.format(workspace=ws)
        lines = _CRON_TEMPLATE.format(workspace=ws, comment=comment)
        assert str(ws) in lines
        # 5.2: one nightly dream replaces five scattered run-maintenance
        # entries (two of which named engines that never existed).
        assert "gish dream" in lines
        assert "--workspace" in lines
        assert "run-maintenance" not in lines

    def test_cron_unix_skips_if_already_present(self, tmp_path):
        from gshell_memory.engines._cron import _COMMENT, _install_unix_cron

        ws = tmp_path / "ws"
        comment = _COMMENT.format(workspace=ws)
        existing = f"0 2 * * * echo hello\n{comment}\n"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = existing
            result = _install_unix_cron(ws)
        assert result["status"] == "already_installed"

    def test_cron_unix_installs_when_not_present(self, tmp_path):
        from gshell_memory.engines._cron import _install_unix_cron

        ws = tmp_path / "ws"
        existing = "0 2 * * * echo hello\n"
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                type("R", (), {"returncode": 0, "stdout": existing, "stderr": ""})(),
                type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})(),
            ]
            result = _install_unix_cron(ws)
        assert result["status"] == "installed"
