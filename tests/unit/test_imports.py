"""Verify every spec'd module is importable as a stub."""

import importlib

import pytest

MEMORY_MODULES = [
    "ghost_in_shell.memory.facts",
    "ghost_in_shell.memory.episodic",
    "ghost_in_shell.memory.associations",
    "ghost_in_shell.memory.brain_regions",
    "ghost_in_shell.memory.sanctum",
    "ghost_in_shell.memory.retrieval",
]
ENGINE_MODULES = [
    "ghost_in_shell.engines.associate",
    "ghost_in_shell.engines.decay",
    "ghost_in_shell.engines.consolidate",
    "ghost_in_shell.engines.health",
    "ghost_in_shell.engines.audit",
    "ghost_in_shell.engines.session_log",
]
ADAPTER_MODULES = [
    "ghost_in_shell.adapters.base",
    "ghost_in_shell.adapters.claude",
    "ghost_in_shell.adapters.gemini",
    "ghost_in_shell.adapters.codex",
    "ghost_in_shell.adapters.copilot",
]


@pytest.mark.parametrize(
    "module_name",
    MEMORY_MODULES + ENGINE_MODULES + ADAPTER_MODULES,
)
def test_module_importable(module_name):
    importlib.import_module(module_name)


def test_package_has_version():
    import ghost_in_shell

    assert ghost_in_shell.__version__ == "5.0.0a1"
