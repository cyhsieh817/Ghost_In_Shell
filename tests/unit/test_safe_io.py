"""Tests for ghost_in_shell.memory._safe_io — atomic writes + jsonl helpers."""

import json
from pathlib import Path

import pytest

from ghost_in_shell.memory._safe_io import (
    append_jsonl,
    atomic_write_text,
    read_jsonl,
)


def test_atomic_write_text_creates_file(tmp_path: Path):
    target = tmp_path / "f.txt"
    atomic_write_text(target, "hello")
    assert target.read_text() == "hello"


def test_atomic_write_text_does_not_leave_tmp_on_success(tmp_path: Path):
    target = tmp_path / "f.txt"
    atomic_write_text(target, "x")
    siblings = list(tmp_path.iterdir())
    assert siblings == [target], f"unexpected sibling files: {siblings}"


def test_append_jsonl_creates_file(tmp_path: Path):
    target = tmp_path / "j.jsonl"
    append_jsonl(target, [{"a": 1}, {"b": 2}])
    lines = target.read_text().splitlines()
    assert json.loads(lines[0]) == {"a": 1}
    assert json.loads(lines[1]) == {"b": 2}


def test_append_jsonl_appends_to_existing(tmp_path: Path):
    target = tmp_path / "j.jsonl"
    append_jsonl(target, [{"a": 1}])
    append_jsonl(target, [{"b": 2}])
    assert len(target.read_text().splitlines()) == 2


def test_read_jsonl_skips_blank_lines(tmp_path: Path):
    target = tmp_path / "j.jsonl"
    target.write_text('{"a": 1}\n\n{"b": 2}\n')
    rows = list(read_jsonl(target))
    assert rows == [{"a": 1}, {"b": 2}]


def test_read_jsonl_raises_on_invalid_json(tmp_path: Path):
    target = tmp_path / "j.jsonl"
    target.write_text('{"a": 1}\nNOT_JSON\n')
    with pytest.raises(ValueError):
        list(read_jsonl(target))
