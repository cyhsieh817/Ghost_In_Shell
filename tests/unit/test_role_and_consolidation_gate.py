"""Single-writer guard (ch.20) and the judge-gated consolidation pipeline."""

import datetime
import hashlib
import json
import shlex
import sys

import pytest
from click.testing import CliRunner

from gshell_memory.cli.main import gish
from gshell_memory.engines import consolidate, judge
from gshell_memory.memory import _role
from gshell_memory.memory._safe_io import read_jsonl
from gshell_memory.memory.episodic import EpisodicStore


@pytest.fixture(autouse=True)
def _isolated_role(monkeypatch, tmp_path):
    """Never read the developer's real role file."""
    monkeypatch.delenv(_role.ROLE_ENV, raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))


def _ep(eid, importance, status="active"):
    return {
        "id": eid,
        "ts": datetime.datetime.now(datetime.UTC).isoformat(),
        "type": "decision",
        "title": f"Episode {eid}",
        "content": f"content {eid}",
        "tags": [],
        "importance": importance,
        "source": "test",
        "fingerprint": hashlib.sha256(eid.encode()).hexdigest(),
        "decay_status": status,
        "retrieval": {"count": 0, "last_accessed": None, "strength": 0.7},
    }


def _write(paths, entries):
    paths.episodic.write_text("\n".join(json.dumps(e) for e in entries) + "\n")


# ----------------------------------------------------------------------- role


def test_default_role_is_primary():
    assert _role.machine_role() == "primary"


def test_role_file_outside_workspace(tmp_path):
    path = _role.role_file()
    assert str(path).startswith(str(tmp_path / "xdg"))
    path.parent.mkdir(parents=True)
    path.write_text("secondary\n")
    assert _role.machine_role() == "secondary"


def test_env_overrides_file(monkeypatch):
    path = _role.role_file()
    path.parent.mkdir(parents=True)
    path.write_text("secondary")
    monkeypatch.setenv(_role.ROLE_ENV, "primary")
    assert _role.is_primary()


def test_unknown_role_fails_closed(monkeypatch):
    monkeypatch.setenv(_role.ROLE_ENV, "primray")  # typo
    assert _role.machine_role() == "secondary"


def test_secondary_cannot_append_episode(monkeypatch, tmp_paths):
    monkeypatch.setenv(_role.ROLE_ENV, "secondary")
    with pytest.raises(_role.SecondaryWriteRefused):
        EpisodicStore(tmp_paths).append(_ep("ep-1", 5))
    assert not tmp_paths.episodic.exists() or tmp_paths.episodic.read_text() == ""


def test_secondary_dream_refused_but_dry_run_allowed(monkeypatch, tmp_workspace):
    monkeypatch.setenv(_role.ROLE_ENV, "secondary")
    runner = CliRunner()
    refused = runner.invoke(gish, ["dream", "--workspace", str(tmp_workspace)])
    assert refused.exit_code != 0
    assert "refused" in refused.output
    dry = runner.invoke(gish, ["dream", "--workspace", str(tmp_workspace), "--dry-run"])
    assert dry.exit_code == 0, dry.output


# --------------------------------------------------------- consolidation gate


def test_apply_archives_sources_instead_of_deleting(tmp_paths):
    entries = [_ep(f"low-{i}", 3) for i in range(4)] + [_ep("high-1", 9)]
    _write(tmp_paths, entries)
    result = consolidate.run(tmp_paths.root)
    assert result["applied"] is True
    assert result["verdict"]["grade"] == "A"

    remaining = list(read_jsonl(tmp_paths.episodic))
    ids = [e["id"] for e in remaining]
    assert "high-1" in ids
    assert not any(i.startswith("low-") for i in ids)
    merged = next(e for e in remaining if e["id"].startswith("consolidated-"))
    assert sorted(merged["linked_to"]) == [f"low-{i}" for i in range(4)]

    archived = list(read_jsonl(tmp_paths.archive_dir / consolidate.ARCHIVE_NAME))
    assert sorted(e["id"] for e in archived) == [f"low-{i}" for i in range(4)]


def test_proposal_file_is_kept_with_its_verdict(tmp_paths):
    _write(tmp_paths, [_ep(f"low-{i}", 2) for i in range(3)])
    result = consolidate.run(tmp_paths.root)
    saved = json.loads((tmp_paths.root / result["proposal"]).read_text())
    assert saved["verdict"]["grade"] == "A"
    assert saved["sources"] == ["low-0", "low-1", "low-2"]


def test_protected_importance_grades_f():
    entries = [_ep("a", 3), _ep("b", 3), _ep("c", 9)]
    proposal = consolidate.propose(
        [_ep("a", 3), _ep("b", 3), _ep("c", 3)], ts="2026-10-01T00:00:00"
    )
    verdict = judge.grade_proposal(proposal, entries)
    assert verdict["grade"] == "F"
    assert verdict["passed"] is False


def test_missing_source_grades_f():
    proposal = consolidate.propose([_ep(x, 3) for x in "abc"], ts="2026-10-01T00:00:00")
    verdict = judge.grade_proposal(proposal, [_ep("a", 3), _ep("b", 3)])
    assert verdict["grade"] == "F"


def test_stale_proposal_is_refused_at_apply(tmp_paths):
    _write(tmp_paths, [_ep(x, 3) for x in "abc"])
    proposal = consolidate.propose([_ep(x, 3) for x in "abc"], ts="2026-10-01T00:00:00")
    _write(tmp_paths, [_ep(x, 3) for x in "ab"])  # "c" vanished after proposing
    outcome = consolidate.apply(tmp_paths, proposal)
    assert outcome["applied"] is False
    assert [e["id"] for e in read_jsonl(tmp_paths.episodic)] == ["a", "b"]


def _judge_script(tmp_path, body):
    script = tmp_path / "judge.py"
    script.write_text(body)
    return [sys.executable, str(script)]


@pytest.mark.parametrize(
    ("script", "applied", "grade"),
    [
        ("print('reasoning...')\nprint('B')\n", True, "B"),
        ("print('D - restates its sources')\n", False, "D"),
        ("import sys\nsys.exit(2)\n", False, "F"),  # crashing judge fails closed
        ("print('looks fine')\n", False, "F"),  # no grade on last line fails closed
    ],
)
def test_external_judge_gates_apply(monkeypatch, tmp_path, tmp_paths, script, applied, grade):
    cmd = _judge_script(tmp_path, script)
    monkeypatch.setenv("GISH_JUDGE_COMMAND", shlex.join(cmd))
    _write(tmp_paths, [_ep(f"low-{i}", 3) for i in range(3)])
    before = tmp_paths.episodic.read_text()
    result = consolidate.run(tmp_paths.root)
    assert result["verdict"]["grade"] == grade
    assert result["applied"] is applied
    if not applied:
        assert tmp_paths.episodic.read_text() == before


def test_secondary_cannot_consolidate(monkeypatch, tmp_paths):
    monkeypatch.setenv(_role.ROLE_ENV, "secondary")
    _write(tmp_paths, [_ep(f"low-{i}", 3) for i in range(3)])
    with pytest.raises(_role.SecondaryWriteRefused):
        consolidate.run(tmp_paths.root)
    # dry run is read-only and still allowed
    assert consolidate.run(tmp_paths.root, dry_run=True)["merged"] == 3


# ------------------------------------------------- regressions found in e2e run


def test_soft_dedup_without_quality_field(tmp_paths):
    """quality is optional; soft dedup used to crash with AttributeError."""
    store = EpisodicStore(tmp_paths)
    a = {k: v for k, v in _ep("ep-a", 3).items()}
    b = {**_ep("ep-b", 3), "content": a["content"] + "!"}  # near-duplicate
    store.append(a)
    store.append(b)
    rows = list(read_jsonl(tmp_paths.episodic))
    assert rows[1]["quality"]["duplicate_suspect"] is True


def test_judge_tolerates_null_quality():
    assert judge.evaluate({"importance": 5, "quality": None, "decay_status": "active"})["keep"]


def test_workspace_config_cannot_name_a_judge_command(tmp_path, tmp_paths):
    """A synced or cloned workspace must not be able to run code via the judge."""
    marker = tmp_path / "executed"
    cmd = _judge_script(tmp_path, f"open({str(marker)!r}, 'w').write('x')\nprint('A')\n")
    tmp_paths.config.write_text(json.dumps({"consolidate": {"judge_command": cmd}}))
    _write(tmp_paths, [_ep(f"low-{i}", 3) for i in range(3)])
    before = tmp_paths.episodic.read_text()
    result = consolidate.run(tmp_paths.root)
    assert not marker.exists(), "workspace-configured judge command was executed"
    assert result["applied"] is False
    assert result["verdict"]["grade"] == "F"
    assert "device-local" in result["verdict"]["external"]["error"]
    assert tmp_paths.episodic.read_text() == before


def test_judge_command_from_device_config_file(tmp_path, tmp_paths):
    from gshell_memory.memory._role import device_config_dir

    cmd = _judge_script(tmp_path, "print('B')\n")
    device_config_dir().mkdir(parents=True, exist_ok=True)
    (device_config_dir() / "judge_command").write_text(shlex.join(cmd) + "\n")
    _write(tmp_paths, [_ep(f"low-{i}", 3) for i in range(3)])
    result = consolidate.run(tmp_paths.root)
    assert (result["verdict"]["grade"], result["applied"]) == ("B", True)
