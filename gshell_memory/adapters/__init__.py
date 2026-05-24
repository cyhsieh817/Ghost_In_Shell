"""CLI adapters — multi-CLI integration layer."""

from __future__ import annotations

from gshell_memory.adapters.base import CLIAdapter
from gshell_memory.adapters.claude import ClaudeAdapter
from gshell_memory.adapters.codex import CodexAdapter
from gshell_memory.adapters.copilot import CopilotAdapter
from gshell_memory.adapters.gemini import GeminiAdapter

_REGISTRY: dict[str, type[CLIAdapter]] = {
    "claude": ClaudeAdapter,
    "gemini": GeminiAdapter,
    "codex": CodexAdapter,
    "copilot": CopilotAdapter,
}


def get_adapter(name: str) -> CLIAdapter:
    """Return an instantiated adapter by name. Raises KeyError for unknown names."""
    cls = _REGISTRY[name]
    return cls()


__all__ = [
    "CLIAdapter",
    "ClaudeAdapter",
    "CodexAdapter",
    "CopilotAdapter",
    "GeminiAdapter",
    "get_adapter",
]
