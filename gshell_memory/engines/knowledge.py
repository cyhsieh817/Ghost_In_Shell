"""Knowledge engine — startup-index budget, note contract, and index lint (ch.19).

The knowledge layer has two parts:

* ``MEMORY.md`` at the workspace root — the startup index every session loads
  in full. It holds one line per note: a trigger phrase plus a link. It never
  holds the lesson itself.
* ``memory/knowledge/<shelf>/<slug>.md`` — one note per fact, with a small
  YAML frontmatter contract (see :data:`SHELVES` and :func:`lint_note`).

The index is paid for in every session, and some CLIs silently cut a startup
file that grows past a fixed size. :func:`budget` measures the index in
characters against ``index.max_chars`` and ``index.truncate_edge_chars`` from
``.gish/config.yml`` so the cost is measured, not guessed.
"""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from gshell_memory.memory._paths import WorkspacePaths

# note type -> shelf directory under memory/knowledge/
SHELVES: dict[str, str] = {
    "feedback": "feedback",
    "project": "projects",
    "reference": "references",
    "user": "user",
}

DEFAULT_MAX_CHARS = 20000
DEFAULT_TRUNCATE_EDGE = 24400

EXIT_OK = 0
EXIT_OVER_BUDGET = 1
EXIT_TRUNCATING = 2
EXIT_MISSING = 3

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_LINK_RE = re.compile(r"\]\(([^)\s]+\.md)(?:#[^)]*)?\)")
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


# ---------------------------------------------------------------------------
# Budget
# ---------------------------------------------------------------------------


def load_index_config(paths: WorkspacePaths) -> dict:
    cfg = {"max_chars": DEFAULT_MAX_CHARS, "truncate_edge_chars": DEFAULT_TRUNCATE_EDGE}
    if paths.config.exists():
        data = yaml.safe_load(paths.config.read_text(encoding="utf-8")) or {}
        section = data.get("index") or {}
        for key in cfg:
            if key in section:
                cfg[key] = int(section[key])
    return cfg


def budget(paths: WorkspacePaths) -> dict:
    """Measure the startup index. ``exit_code`` follows the EXIT_* constants."""
    cfg = load_index_config(paths)
    index = paths.index_file
    if not index.is_file():
        return {"status": "missing", "exit_code": EXIT_MISSING, **cfg}
    text = index.read_text(encoding="utf-8")
    chars = len(text)
    if chars >= cfg["truncate_edge_chars"]:
        status, code = "truncating", EXIT_TRUNCATING
    elif chars >= cfg["max_chars"]:
        status, code = "over_budget", EXIT_OVER_BUDGET
    else:
        status, code = "ok", EXIT_OK
    return {
        "status": status,
        "exit_code": code,
        "chars": chars,
        "bytes": len(text.encode("utf-8")),
        "lines": text.count("\n") + (0 if text.endswith("\n") or not text else 1),
        "headroom": cfg["max_chars"] - chars,
        **cfg,
    }


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Issue:
    path: str
    level: str  # "error" | "warning"
    message: str

    def as_dict(self) -> dict:
        return {"path": self.path, "level": self.level, "message": self.message}


def split_frontmatter(text: str) -> tuple[dict | None, str]:
    """Return ``(frontmatter, body)``; frontmatter is None when absent or invalid YAML."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError:
        return None, text
    body = text[end + 4 :].lstrip("\n")
    return (data if isinstance(data, dict) else None), body


def _is_date(value) -> bool:
    if isinstance(value, datetime.date):
        return True
    return isinstance(value, str) and bool(_DATE_RE.match(value))


def _as_date(value) -> datetime.date | None:
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str) and _DATE_RE.match(value):
        return datetime.date.fromisoformat(value)
    return None


def lint_note(path: Path, rel: str, *, today: datetime.date | None = None) -> list[Issue]:
    """Check one note against the frontmatter contract."""
    today = today or datetime.date.today()
    fm, body = split_frontmatter(path.read_text(encoding="utf-8"))
    if fm is None:
        return [Issue(rel, "error", "missing or invalid YAML frontmatter")]

    issues: list[Issue] = []

    def err(msg: str) -> None:
        issues.append(Issue(rel, "error", msg))

    def warn(msg: str) -> None:
        issues.append(Issue(rel, "warning", msg))

    if fm.get("name") != path.stem:
        err(f"name must equal the file stem '{path.stem}' (got {fm.get('name')!r})")
    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        err("description is required (one line, used to judge relevance at recall)")
    elif "\n" in desc.strip():
        err("description must be a single line")

    meta = fm.get("metadata")
    if not isinstance(meta, dict):
        err("metadata block is required (metadata.type, metadata.updated)")
        meta = {}
    note_type = meta.get("type")
    if note_type not in SHELVES:
        err(f"metadata.type must be one of {sorted(SHELVES)} (got {note_type!r})")
    elif path.parent.name != SHELVES[note_type]:
        err(f"metadata.type '{note_type}' belongs on shelf '{SHELVES[note_type]}/'")

    if not _is_date(meta.get("updated")):
        err("metadata.updated is required as YYYY-MM-DD (date the content was last verified)")

    if "confidence" in meta:
        conf = meta["confidence"]
        if not isinstance(conf, int | float) or not 0.0 <= float(conf) <= 1.0:
            err("metadata.confidence must be a number between 0.0 and 1.0")
    if "evidence" in meta and not isinstance(meta["evidence"], list):
        err("metadata.evidence must be a list of episode ids or file paths")
    if "expires" in meta:
        expires = _as_date(meta["expires"])
        if expires is None:
            err("metadata.expires must be YYYY-MM-DD")
        elif expires < today:
            warn(f"expired on {expires.isoformat()}; re-verify or archive this note")

    for key in ("type", "tier", "updated", "confidence", "evidence", "expires"):
        if key in fm:
            warn(f"'{key}' belongs under metadata:, not at the top level")

    if not body.strip():
        err("note body is empty")
    elif note_type == "feedback" and not ("**Why:**" in body and "**How to apply:**" in body):
        warn("feedback notes should carry '**Why:**' and '**How to apply:**' lines")
    return issues


def _iter_notes(paths: WorkspacePaths):
    root = paths.knowledge_dir
    if not root.is_dir():
        return
    for path in sorted(root.rglob("*.md")):
        if path.parent == root:  # shelf indexes such as INDEX_*.md live at the root
            continue
        yield path


def _index_files(paths: WorkspacePaths) -> list[Path]:
    files = [paths.index_file] if paths.index_file.is_file() else []
    if paths.knowledge_dir.is_dir():
        files.extend(sorted(paths.knowledge_dir.glob("INDEX_*.md")))
    return files


def lint(paths: WorkspacePaths, *, today: datetime.date | None = None) -> dict:
    """Lint every note plus the index links. Errors make ``ok`` False."""
    issues: list[Issue] = []
    notes = list(_iter_notes(paths))
    for path in notes:
        issues.extend(lint_note(path, str(path.relative_to(paths.root)), today=today))

    linked: set[Path] = set()
    for index in _index_files(paths):
        rel_index = str(index.relative_to(paths.root))
        text = _COMMENT_RE.sub(
            lambda m: "\n" * m.group(0).count("\n"), index.read_text(encoding="utf-8")
        )
        for lineno, line in enumerate(text.splitlines(), 1):
            targets = _LINK_RE.findall(line)
            for target in targets:
                if "://" in target:
                    continue
                resolved = (index.parent / target).resolve()
                if not resolved.is_file():
                    issues.append(Issue(rel_index, "error", f"line {lineno}: broken link {target}"))
                else:
                    linked.add(resolved)
            if targets and line.lstrip().startswith("- ") and "→" not in line and "->" not in line:
                issues.append(
                    Issue(
                        rel_index,
                        "warning",
                        f"line {lineno}: link without a trigger phrase "
                        "(write '\"<symptom you will have>\" → [note](...)')",
                    )
                )

    if _index_files(paths):
        for path in notes:
            if path.resolve() not in linked:
                issues.append(
                    Issue(
                        str(path.relative_to(paths.root)),
                        "warning",
                        "orphan note: no index line points here, so no session will find it",
                    )
                )

    errors = sum(1 for i in issues if i.level == "error")
    return {
        "ok": errors == 0,
        "notes": len(notes),
        "errors": errors,
        "warnings": len(issues) - errors,
        "issues": [i.as_dict() for i in issues],
    }


_FEEDBACK_BODY = """<the rule, in one or two sentences>

**Why:** <what went wrong, or what was confirmed, that makes this rule necessary>

**How to apply:** <the situation where it applies and the concrete action to take>
"""


def new_note(paths: WorkspacePaths, note_type: str, slug: str, description: str) -> Path:
    """Create a note skeleton on the right shelf. Refuses to overwrite."""
    if note_type not in SHELVES:
        raise ValueError(f"type must be one of {sorted(SHELVES)}")
    if not _SLUG_RE.match(slug):
        raise ValueError("slug must be lowercase kebab-case, e.g. 'verify-final-state'")
    if not description.strip() or "\n" in description.strip():
        raise ValueError("description must be one non-empty line")
    dest = paths.knowledge_dir / SHELVES[note_type] / f"{slug}.md"
    if dest.exists():
        raise FileExistsError(f"{dest.relative_to(paths.root)} already exists")
    body = _FEEDBACK_BODY if note_type == "feedback" else "<the fact, with its source>\n"
    frontmatter = yaml.safe_dump(
        {
            "name": slug,
            "description": description.strip(),
            "metadata": {"type": note_type, "updated": datetime.date.today().isoformat()},
        },
        sort_keys=False,
        allow_unicode=True,
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(f"---\n{frontmatter}---\n\n{body}", encoding="utf-8")
    return dest
