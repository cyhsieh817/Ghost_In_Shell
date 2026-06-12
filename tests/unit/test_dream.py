"""Unit tests for the dream engine (unified sleep-cycle orchestrator)."""

import datetime

from gshell_memory.engines import dream
from gshell_memory.engines._cron import _CRON_TEMPLATE

MONDAY = datetime.date(2026, 6, 8)
SUNDAY = datetime.date(2026, 6, 14)


def test_light_sleep_runs_five_stages_in_order(tmp_workspace):
    result = dream.run(tmp_workspace, today=MONDAY)
    assert result["mode"] == "light"
    assert list(result["stages"]) == ["replay", "rem", "verdict", "prune", "gate"]


def test_deep_sleep_auto_detected_on_sunday(tmp_workspace):
    result = dream.run(tmp_workspace, today=SUNDAY)
    assert result["mode"] == "deep"
    assert list(result["stages"]) == [
        "replay",
        "rem",
        "verdict",
        "prune",
        "gate",
        "audit",
        "carryover",
    ]


def test_deep_flag_overrides_weekday(tmp_workspace):
    assert dream.run(tmp_workspace, today=MONDAY, deep=True)["mode"] == "deep"
    assert dream.run(tmp_workspace, today=SUNDAY, deep=False)["mode"] == "light"


def test_slept_well_on_blank_workspace(tmp_workspace):
    result = dream.run(tmp_workspace, today=MONDAY)
    assert result["slept_well"] is True
    assert result["failures"] == []


def test_dry_run_propagates_to_stages(tmp_workspace):
    result = dream.run(tmp_workspace, today=MONDAY, dry_run=True)
    assert result["dry_run"] is True
    assert all("error" not in s for s in result["stages"].values())


def test_failure_isolation_continues_past_crashing_stage(tmp_workspace, monkeypatch):
    from gshell_memory.engines import consolidate

    def _boom(workspace, *, dry_run=False):
        raise RuntimeError("nightmare")

    monkeypatch.setattr(consolidate, "run", _boom)
    result = dream.run(tmp_workspace, today=MONDAY)
    assert result["failures"] == ["rem"]
    assert result["slept_well"] is False
    assert "nightmare" in result["stages"]["rem"]["error"]
    # later stages still ran despite the rem crash
    assert "error" not in result["stages"]["prune"]
    assert "error" not in result["stages"]["gate"]


def test_cron_template_only_schedules_real_commands():
    """Regression: the old template scheduled engines that never existed
    (associate-strength / consolidate-check) and omitted --workspace."""
    assert "run-maintenance" not in _CRON_TEMPLATE
    assert "gish dream" in _CRON_TEMPLATE
    assert "--workspace" in _CRON_TEMPLATE
