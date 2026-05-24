"""Unit tests for CLI adapters — M3."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from gshell_memory.adapters import get_adapter
from gshell_memory.adapters.base import CLIAdapter
from gshell_memory.adapters.claude import ClaudeAdapter
from gshell_memory.adapters.codex import CodexAdapter
from gshell_memory.adapters.copilot import CopilotAdapter
from gshell_memory.adapters.gemini import GeminiAdapter


@pytest.fixture(
    params=[
        ("claude", ClaudeAdapter),
        ("gemini", GeminiAdapter),
        ("codex", CodexAdapter),
        ("copilot", CopilotAdapter),
    ]
)
def adapter_pair(request):
    name, cls = request.param
    return name, cls()


class TestAdapterNames:
    def test_claude_name(self):
        assert ClaudeAdapter.name == "claude"

    def test_gemini_name(self):
        assert GeminiAdapter.name == "gemini"

    def test_codex_name(self):
        assert CodexAdapter.name == "codex"

    def test_copilot_name(self):
        assert CopilotAdapter.name == "copilot"


class TestRootInstructionTemplate:
    def test_contains_workspace_identity(self, adapter_pair):
        _, adapter = adapter_pair
        tmpl = adapter.root_instruction_template()
        assert "@<workspace>/IDENTITY.md" in tmpl

    def test_contains_workspace_soul(self, adapter_pair):
        _, adapter = adapter_pair
        tmpl = adapter.root_instruction_template()
        assert "@<workspace>/SOUL.md" in tmpl

    def test_contains_workspace_user(self, adapter_pair):
        _, adapter = adapter_pair
        tmpl = adapter.root_instruction_template()
        assert "@<workspace>/USER.md" in tmpl

    def test_contains_workspace_memory(self, adapter_pair):
        _, adapter = adapter_pair
        tmpl = adapter.root_instruction_template()
        assert "@<workspace>/MEMORY.md" in tmpl

    def test_is_non_empty_string(self, adapter_pair):
        _, adapter = adapter_pair
        assert isinstance(adapter.root_instruction_template(), str)
        assert len(adapter.root_instruction_template()) > 0


class TestHooks:
    def test_session_start_hook_non_empty(self, adapter_pair):
        _, adapter = adapter_pair
        result = adapter.session_start_hook()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_session_end_hook_non_empty(self, adapter_pair):
        _, adapter = adapter_pair
        result = adapter.session_end_hook()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_claude_end_hook_contains_gish_log(self):
        adapter = ClaudeAdapter()
        assert "gish log --from-session" in adapter.session_end_hook()

    def test_claude_end_hook_contains_settings_json(self):
        adapter = ClaudeAdapter()
        assert "settings.json" in adapter.session_end_hook()


class TestDetectInstallation:
    def test_returns_bool(self, adapter_pair):
        _, adapter = adapter_pair
        result = adapter.detect_installation()
        assert isinstance(result, bool)

    def test_claude_false_when_not_in_path(self):
        adapter = ClaudeAdapter()
        with patch("shutil.which", return_value=None):
            assert adapter.detect_installation() is False

    def test_claude_true_when_in_path(self):
        adapter = ClaudeAdapter()
        with patch("shutil.which", return_value="/usr/local/bin/claude"):
            assert adapter.detect_installation() is True

    def test_copilot_false_when_nothing(self, tmp_path):
        adapter = CopilotAdapter()
        with patch("shutil.which", return_value=None), patch(
            "gshell_memory.adapters.copilot.Path.home", return_value=tmp_path
        ):
            assert adapter.detect_installation() is False

    def test_copilot_true_when_gh_in_path(self):
        adapter = CopilotAdapter()
        with patch("shutil.which", return_value="/usr/local/bin/gh"):
            assert adapter.detect_installation() is True


class TestGetAdapter:
    def test_returns_claude_adapter(self):
        adapter = get_adapter("claude")
        assert isinstance(adapter, ClaudeAdapter)

    def test_returns_gemini_adapter(self):
        adapter = get_adapter("gemini")
        assert isinstance(adapter, GeminiAdapter)

    def test_returns_codex_adapter(self):
        adapter = get_adapter("codex")
        assert isinstance(adapter, CodexAdapter)

    def test_returns_copilot_adapter(self):
        adapter = get_adapter("copilot")
        assert isinstance(adapter, CopilotAdapter)

    def test_raises_keyerror_for_unknown(self):
        with pytest.raises(KeyError):
            get_adapter("unknown_cli")

    def test_all_adapters_are_cli_adapter_instances(self):
        for name in ["claude", "gemini", "codex", "copilot"]:
            adapter = get_adapter(name)
            assert isinstance(adapter, CLIAdapter)


class TestLaunch:
    def test_launch_calls_subprocess(self):
        adapter = ClaudeAdapter()
        with patch("subprocess.call", return_value=0) as mock_call:
            rc = adapter.launch(["--help"])
        mock_call.assert_called_once_with(["claude", "--help"])
        assert rc == 0

    def test_launch_returns_subprocess_return_code(self):
        adapter = GeminiAdapter()
        with patch("subprocess.call", return_value=42):
            rc = adapter.launch(["arg1"])
        assert rc == 42

    def test_copilot_launch_uses_gh_binary(self):
        adapter = CopilotAdapter()
        with patch("subprocess.call", return_value=0) as mock_call:
            adapter.launch(["suggest", "list files"])
        mock_call.assert_called_once_with(["gh", "suggest", "list files"])

    def test_launch_with_empty_args(self):
        adapter = CodexAdapter()
        with patch("subprocess.call", return_value=0) as mock_call:
            adapter.launch([])
        mock_call.assert_called_once_with(["codex"])
