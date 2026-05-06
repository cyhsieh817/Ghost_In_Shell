"""CLI M2 integration tests — log, recall, doctor, audit, run-maintenance."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from ghost_in_shell.cli.main import gish


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def ws(tmp_workspace: Path) -> Path:
    """Return a workspace Path (raw, for --workspace arg)."""
    return tmp_workspace


def test_log_creates_episode(runner, ws):
    result = runner.invoke(gish, [
        "log", "My first episode",
        "--workspace", str(ws),
        "--content", "Deployed to prod",
        "--tags", "deploy,prod",
        "--importance", "7",
    ])
    assert result.exit_code == 0, result.output
    assert "Logged episode:" in result.output
    # Verify file exists
    ep_file = ws / "memory" / "episodic.jsonl"
    assert ep_file.exists()
    row = json.loads(ep_file.read_text().strip())
    assert row["title"] == "My first episode"


def test_recall_finds_episode(runner, ws):
    # First log an episode
    runner.invoke(gish, [
        "log", "Deploy to production",
        "--workspace", str(ws),
        "--content", "Ran deploy script successfully",
        "--tags", "deploy",
    ])
    result = runner.invoke(gish, ["recall", "deploy", "--workspace", str(ws)])
    assert result.exit_code == 0, result.output
    assert "Deploy to production" in result.output


def test_recall_no_results(runner, ws):
    result = runner.invoke(gish, ["recall", "nonexistent", "--workspace", str(ws)])
    assert result.exit_code == 0
    assert "No matching episodes" in result.output


def test_doctor_reports_status(runner, ws):
    result = runner.invoke(gish, ["doctor", "--workspace", str(ws), "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "Status:" in result.output


def test_audit_runs(runner, ws):
    result = runner.invoke(gish, ["audit", "--workspace", str(ws)])
    assert result.exit_code == 0, result.output
    assert "Audit files scanned:" in result.output


def test_run_maintenance_all(runner, ws):
    result = runner.invoke(gish, ["run-maintenance", "--workspace", str(ws), "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "[health]" in result.output


def test_run_maintenance_single_engine(runner, ws):
    result = runner.invoke(gish, [
        "run-maintenance", "--workspace", str(ws), "--engine", "health", "--dry-run"
    ])
    assert result.exit_code == 0, result.output
    assert "[health]" in result.output


def test_run_maintenance_unknown_engine(runner, ws):
    result = runner.invoke(gish, [
        "run-maintenance", "--workspace", str(ws), "--engine", "bogus"
    ])
    assert result.exit_code != 0
