"""Verify gshell-memory readers handle workspaces that have seen LGD writes.

Fixture mimics LGD's write pattern (e.g. appended episode + association)
and checks that gish's own reader still accepts the workspace.
"""

import json
from datetime import UTC, datetime

from click.testing import CliRunner

from gshell_memory.cli.main import gish


def test_gish_reads_workspace_after_lgd_style_writes(tmp_path):
    runner = CliRunner()
    runner.invoke(gish, ["init", str(tmp_path / "ws"), "--non-interactive"])

    ws = tmp_path / "ws"
    # Append an LGD-style episode (no fingerprint by mistake) — gish doctor
    # should report a problem but not crash.
    entry = {
        "id": "ep-2026-05-24-100",
        "title": "from LGD",
        "content": "test",
        "date": "2026-05-24",
        "ts": datetime.now(UTC).isoformat(),
        "type": "decision",
        "tags": [],
        "importance": 5,
        "retrieval": {"count": 0, "last_accessed": None, "strength": 1.0},
        "decay_status": "active",
        "linked_to": [],
        # NOTE: no fingerprint — required by 5.1 schema
    }
    with (ws / "memory" / "episodic.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    result = runner.invoke(gish, ["doctor", "--workspace", str(ws)])
    # doctor must not crash even though the schema is violated
    assert result.exit_code in {0, 1}
    assert "fingerprint" in result.output.lower() or "schema" in result.output.lower()
