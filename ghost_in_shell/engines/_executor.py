"""Executor — spawn AI binaries from runtime_profiles.yml (spec § 4.7)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

from ghost_in_shell.memory._paths import WorkspacePaths, resolve_workspace
from ghost_in_shell.memory.schemas import RuntimeProfiles


def load_profiles(paths: WorkspacePaths) -> RuntimeProfiles:
    p = paths.runtime_profiles
    if not p.exists():
        raise FileNotFoundError(f"runtime_profiles.yml not found at {p}")
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    return RuntimeProfiles(**raw)


def execute(
    workspace: Path,
    prompt: str,
    executor_name: str | None = None,
) -> subprocess.CompletedProcess:
    """Spawn the chosen executor binary with the given prompt.

    Falls back to the ``default_executor`` if *executor_name* is None.
    """
    paths = WorkspacePaths(resolve_workspace(workspace))
    profiles = load_profiles(paths)

    name = executor_name or profiles.default_executor
    executor = profiles.executors.get(name)
    if executor is None:
        raise KeyError(f"Unknown executor: {name!r}")

    cmd = [executor.binary] + [
        arg.format(prompt=prompt) if "{prompt}" in arg else arg
        for arg in executor.args
    ]

    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=executor.timeout,
    )
