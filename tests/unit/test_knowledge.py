"""Tests for the knowledge engine: index budget, note contract, index lint (ch.19)."""

import datetime
import json

import pytest
from click.testing import CliRunner

from gshell_memory.cli.main import gish
from gshell_memory.engines import knowledge

TODAY = datetime.date(2026, 10, 1)


def _note(paths, shelf, slug, *, fm=None, body="The rule.\n\n**Why:** x\n\n**How to apply:** y\n"):
    meta = {"type": "feedback", "updated": "2026-09-30"}
    front = {"name": slug, "description": "one line", "metadata": meta}
    if fm is not None:
        front = fm
    import yaml

    path = paths.knowledge_dir / shelf / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{yaml.safe_dump(front, sort_keys=False)}---\n\n{body}", encoding="utf-8")
    return path


def _index(paths, text):
    paths.index_file.write_text(text, encoding="utf-8")


# --------------------------------------------------------------------- budget


def test_budget_missing_index(tmp_paths):
    assert knowledge.budget(tmp_paths)["exit_code"] == knowledge.EXIT_MISSING


def test_budget_counts_characters_not_bytes(tmp_paths):
    _index(tmp_paths, "記憶" * 10)  # 20 chars, 60 bytes
    result = knowledge.budget(tmp_paths)
    assert result["chars"] == 20
    assert result["bytes"] == 60
    assert result["exit_code"] == knowledge.EXIT_OK


@pytest.mark.parametrize(
    ("size", "status", "code"),
    [(99, "ok", 0), (100, "over_budget", 1), (149, "over_budget", 1), (150, "truncating", 2)],
)
def test_budget_thresholds_from_config(tmp_paths, size, status, code):
    tmp_paths.config.write_text("index:\n  max_chars: 100\n  truncate_edge_chars: 150\n")
    _index(tmp_paths, "x" * size)
    result = knowledge.budget(tmp_paths)
    assert (result["status"], result["exit_code"]) == (status, code)


def test_cli_budget_exit_code_and_json(tmp_workspace, tmp_paths):
    tmp_paths.config.write_text("index:\n  max_chars: 10\n  truncate_edge_chars: 50\n")
    _index(tmp_paths, "x" * 20)
    result = CliRunner().invoke(
        gish, ["index", "budget", "--workspace", str(tmp_workspace), "--json"]
    )
    assert result.exit_code == 1
    assert json.loads(result.output)["status"] == "over_budget"


# ----------------------------------------------------------------- note lint


def test_valid_note_has_no_issues(tmp_paths):
    path = _note(tmp_paths, "feedback", "verify-final-state")
    assert knowledge.lint_note(path, "n", today=TODAY) == []


def test_name_must_match_stem(tmp_paths):
    fm = {
        "name": "other",
        "description": "d",
        "metadata": {"type": "feedback", "updated": "2026-09-30"},
    }
    path = _note(tmp_paths, "feedback", "real-slug", fm=fm)
    msgs = [i.message for i in knowledge.lint_note(path, "n", today=TODAY)]
    assert any("file stem" in m for m in msgs)


def test_type_must_match_shelf(tmp_paths):
    fm = {
        "name": "x",
        "description": "d",
        "metadata": {"type": "reference", "updated": "2026-09-30"},
    }
    path = _note(tmp_paths, "feedback", "x", fm=fm)
    msgs = [i.message for i in knowledge.lint_note(path, "n", today=TODAY)]
    assert any("belongs on shelf 'references/'" in m for m in msgs)


def test_updated_is_required(tmp_paths):
    fm = {"name": "x", "description": "d", "metadata": {"type": "feedback"}}
    path = _note(tmp_paths, "feedback", "x", fm=fm)
    issues = knowledge.lint_note(path, "n", today=TODAY)
    assert any(i.level == "error" and "metadata.updated" in i.message for i in issues)


@pytest.mark.parametrize("conf", [1.5, -0.1, "high"])
def test_confidence_range(tmp_paths, conf):
    fm = {
        "name": "x",
        "description": "d",
        "metadata": {"type": "feedback", "updated": "2026-09-30", "confidence": conf},
    }
    path = _note(tmp_paths, "feedback", "x", fm=fm)
    assert any("confidence" in i.message for i in knowledge.lint_note(path, "n", today=TODAY))


def test_expired_note_is_a_warning_not_an_error(tmp_paths):
    fm = {
        "name": "x",
        "description": "d",
        "metadata": {"type": "feedback", "updated": "2026-01-01", "expires": "2026-06-01"},
    }
    path = _note(tmp_paths, "feedback", "x", fm=fm)
    issues = knowledge.lint_note(path, "n", today=TODAY)
    assert [i.level for i in issues] == ["warning"]
    assert "expired" in issues[0].message


def test_top_level_governance_field_warns(tmp_paths):
    fm = {
        "name": "x",
        "description": "d",
        "tier": 1,
        "metadata": {"type": "feedback", "updated": "2026-09-30"},
    }
    path = _note(tmp_paths, "feedback", "x", fm=fm)
    assert any(
        "belongs under metadata" in i.message for i in knowledge.lint_note(path, "n", today=TODAY)
    )


def test_missing_frontmatter_is_an_error(tmp_paths):
    path = tmp_paths.knowledge_dir / "feedback" / "bare.md"
    path.parent.mkdir(parents=True)
    path.write_text("just text\n")
    assert knowledge.lint_note(path, "n", today=TODAY)[0].level == "error"


# ---------------------------------------------------------------- index lint


def test_broken_index_link_is_an_error(tmp_paths):
    _index(tmp_paths, '- "symptom" → [gone](memory/knowledge/feedback/gone.md)\n')
    result = knowledge.lint(tmp_paths, today=TODAY)
    assert result["ok"] is False
    assert "broken link" in result["issues"][0]["message"]


def test_orphan_note_is_a_warning(tmp_paths):
    _note(tmp_paths, "feedback", "lonely")
    _index(tmp_paths, "# index\n")
    result = knowledge.lint(tmp_paths, today=TODAY)
    assert result["ok"] is True
    assert any("orphan" in i["message"] for i in result["issues"])


def test_linked_note_with_trigger_is_clean(tmp_paths):
    _note(tmp_paths, "feedback", "verify-final-state")
    _index(
        tmp_paths,
        '- "the tool said OK, so it is done" → [verify](memory/knowledge/feedback/verify-final-state.md)\n',
    )
    result = knowledge.lint(tmp_paths, today=TODAY)
    assert result["issues"] == []


def test_index_line_without_trigger_warns(tmp_paths):
    _note(tmp_paths, "feedback", "a")
    _index(tmp_paths, "- [a](memory/knowledge/feedback/a.md)\n")
    result = knowledge.lint(tmp_paths, today=TODAY)
    assert any("trigger phrase" in i["message"] for i in result["issues"])


def test_links_inside_html_comments_are_ignored(tmp_paths):
    _index(tmp_paths, '<!--\n- "x" → [x](memory/knowledge/feedback/nope.md)\n-->\n')
    assert knowledge.lint(tmp_paths, today=TODAY)["issues"] == []


def test_shelf_index_links_resolve_relative_to_their_folder(tmp_paths):
    _note(
        tmp_paths,
        "references",
        "api-limits",
        fm={
            "name": "api-limits",
            "description": "d",
            "metadata": {"type": "reference", "updated": "2026-09-30"},
        },
        body="fact\n",
    )
    (tmp_paths.knowledge_dir / "INDEX_tools.md").write_text(
        '- "rate limited again" → [limits](references/api-limits.md)\n'
    )
    result = knowledge.lint(tmp_paths, today=TODAY)
    assert result["issues"] == []


# ------------------------------------------------------------------ new note


def test_new_note_passes_its_own_lint(tmp_paths):
    path = knowledge.new_note(tmp_paths, "feedback", "measure-first", "Measure before building: x")
    assert path.parent.name == "feedback"
    issues = knowledge.lint_note(path, "n")
    assert [i for i in issues if i.level == "error"] == []


def test_new_note_refuses_overwrite_and_bad_slug(tmp_paths):
    knowledge.new_note(tmp_paths, "project", "alpha", "d")
    with pytest.raises(FileExistsError):
        knowledge.new_note(tmp_paths, "project", "alpha", "d")
    with pytest.raises(ValueError):
        knowledge.new_note(tmp_paths, "project", "Bad Slug", "d")


def test_init_creates_shelves_and_a_lint_clean_index(tmp_path):
    ws = tmp_path / "ws"
    runner = CliRunner()
    assert runner.invoke(gish, ["init", str(ws), "--non-interactive"]).exit_code == 0
    for shelf in knowledge.SHELVES.values():
        assert (ws / "memory" / "knowledge" / shelf).is_dir()
    lint = runner.invoke(gish, ["knowledge", "lint", "--workspace", str(ws), "--strict"])
    assert lint.exit_code == 0, lint.output
    budget = runner.invoke(gish, ["index", "budget", "--workspace", str(ws)])
    assert budget.exit_code == 0, budget.output


def test_shipped_example_workspace_lints_clean(repo_root):
    ws = repo_root / "examples" / "multi_cli"
    result = CliRunner().invoke(gish, ["knowledge", "lint", "--workspace", str(ws), "--strict"])
    assert result.exit_code == 0, result.output
