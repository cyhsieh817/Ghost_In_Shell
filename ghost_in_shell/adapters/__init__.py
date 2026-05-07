"""CLI adapters — multi-CLI integration layer."""

from __future__ import annotations

from ghost_in_shell.adapters.base import CLIAdapter
from ghost_in_shell.adapters.claude import ClaudeAdapter
from ghost_in_shell.adapters.codex import CodexAdapter
from ghost_in_shell.adapters.copilot import CopilotAdapter
from ghost_in_shell.adapters.gemini import GeminiAdapter

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
