"""Verify every spec'd module is importable as a stub."""

import importlib

import pytest

MEMORY_MODULES = [
    "gshell_memory.memory.facts",
    "gshell_memory.memory.episodic",
    "gshell_memory.memory.associations",
    "gshell_memory.memory.brain_regions",
    "gshell_memory.memory.sanctum",
    "gshell_memory.memory.retrieval",
]
ENGINE_MODULES = [
    "gshell_memory.engines.associate",
    "gshell_memory.engines.decay",
    "gshell_memory.engines.consolidate",
    "gshell_memory.engines.health",
    "gshell_memory.engines.audit",
    "gshell_memory.engines.session_log",
]
ADAPTER_MODULES = [
    "gshell_memory.adapters.base",
    "gshell_memory.adapters.claude",
    "gshell_memory.adapters.gemini",
    "gshell_memory.adapters.codex",
    "gshell_memory.adapters.copilot",
]


@pytest.mark.parametrize(
    "module_name",
    MEMORY_MODULES + ENGINE_MODULES + ADAPTER_MODULES,
)
def test_module_importable(module_name):
    importlib.import_module(module_name)


def test_package_has_version():
    import gshell_memory

    assert gshell_memory.__version__ == "5.0.0rc1"
