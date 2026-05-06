#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from _paths import SCRIPTS

HOME = Path.home()
SNIPPET_PATH = SCRIPTS / "void-shell-wrappers.sh"
MARKER_BEGIN = "# >>> Ghost In Shell multi-CLI wrappers >>>"
MARKER_END = "# <<< Ghost In Shell multi-CLI wrappers <<<"
BLOCK_RE = re.compile(
    rf"(?ms)^[ \t]*{re.escape(MARKER_BEGIN)}\n.*?^[ \t]*{re.escape(MARKER_END)}\n?"
)


@dataclass(frozen=True)
class TargetFile:
    shell: str
    path: Path
    purpose: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install persistent shell wrappers for the Ghost multi-CLI reference implementation."
    )
    parser.add_argument("--shell", choices=["all", "zsh", "bash"], default="all")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--uninstall", action="store_true")
    return parser


def source_block() -> str:
    return (
        f"{MARKER_BEGIN}\n"
        f'export GHOST_IN_SHELL_REF_SCRIPTS="{SCRIPTS}"\n'
        'if [ -f "$GHOST_IN_SHELL_REF_SCRIPTS/void-shell-wrappers.sh" ]; then\n'
        '  . "$GHOST_IN_SHELL_REF_SCRIPTS/void-shell-wrappers.sh"\n'
        "fi\n"
        f"{MARKER_END}\n"
    )


def targets(shell: str) -> list[TargetFile]:
    items: list[TargetFile] = []
    if shell in {"all", "zsh"}:
        items.append(TargetFile("zsh", HOME / ".zshrc", "zsh interactive shell"))
    if shell in {"all", "bash"}:
        items.append(TargetFile("bash", HOME / ".bashrc", "bash interactive shell"))
        login_target = (
            HOME / ".bash_profile" if (HOME / ".bash_profile").exists() else HOME / ".profile"
        )
        items.append(TargetFile("bash", login_target, "bash login shell"))
    deduped: list[TargetFile] = []
    seen: set[Path] = set()
    for item in items:
        if item.path in seen:
            continue
        seen.add(item.path)
        deduped.append(item)
    return deduped


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def with_block(text: str) -> str:
    block = source_block()
    if BLOCK_RE.search(text):
        return BLOCK_RE.sub(block, text, count=1)
    updated = text
    if updated and not updated.endswith("\n"):
        updated += "\n"
    if updated:
        updated += "\n"
    return updated + block


def without_block(text: str) -> str:
    updated = BLOCK_RE.sub("", text, count=1).rstrip()
    return updated + ("\n" if updated else "")


def write_target(path: Path, content: str, dry_run: bool) -> None:
    if dry_run:
        return
    path.write_text(content, encoding="utf-8")


def install(target_list: list[TargetFile], dry_run: bool) -> int:
    for target in target_list:
        original = read_text(target.path)
        updated = with_block(original)
        state = "[changed]" if updated != original else "[already]"
        print(f"[install] {target.path} ({target.purpose}) {state}")
        write_target(target.path, updated, dry_run)
    return 0


def uninstall(target_list: list[TargetFile], dry_run: bool) -> int:
    for target in target_list:
        original = read_text(target.path)
        updated = without_block(original)
        state = "[changed]" if updated != original else "[absent]"
        print(f"[uninstall] {target.path} ({target.purpose}) {state}")
        write_target(target.path, updated, dry_run)
    return 0


def status(target_list: list[TargetFile]) -> int:
    print(f"Snippet: {SNIPPET_PATH}")
    for target in target_list:
        state = "installed" if BLOCK_RE.search(read_text(target.path)) else "missing"
        print(f"  - {target.path}: {state} ({target.purpose})")
    return 0


def main() -> int:
    args = build_parser().parse_args()
    if not SNIPPET_PATH.exists():
        print(f"Missing snippet file: {SNIPPET_PATH}", file=sys.stderr)
        return 1
    target_list = targets(args.shell)
    if args.status:
        return status(target_list)
    if args.uninstall:
        return uninstall(target_list, args.dry_run)
    return install(target_list, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
