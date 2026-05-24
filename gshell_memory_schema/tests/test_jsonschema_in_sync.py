"""Ensure committed JSON Schema matches current Pydantic models."""

import subprocess
import sys
from pathlib import Path


def test_jsonschema_in_sync():
    repo = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, str(repo / "scripts" / "generate_jsonschema.py"), "--check"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"JSON Schema out of sync:\n{result.stdout}\n{result.stderr}\n"
        "Run: python scripts/generate_jsonschema.py"
    )
