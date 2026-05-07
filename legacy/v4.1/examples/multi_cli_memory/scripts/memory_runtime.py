#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from _paths import MEMORY, WORKSPACE

PROFILE_PATH = MEMORY / "runtime_profiles.yml"

DEFAULT_PROFILE_CONFIG = {
    "default_executor": "claude",
    "default_runtime": "claude-code",
    "default_launcher": "claude",
    "executors": {
        "claude": {"label": "Claude Code", "binary": "claude", "args": ["-p", "{prompt}", "--output-format", "text"], "timeout": 180, "output_mode": "text"},
        "gemini": {"label": "Gemini CLI", "binary": "gemini", "args": ["-p", "{prompt}"], "timeout": 180, "output_mode": "text"},
        "copilot": {"label": "GitHub Copilot CLI", "binary": "copilot", "args": ["-p", "{prompt}", "--allow-all-tools", "--output-format", "text"], "timeout": 180, "output_mode": "text"},
        "codex": {"label": "Codex CLI", "binary": "codex", "args": ["-p", "{prompt}"], "timeout": 180, "output_mode": "text"},
        "openclaw-local": {"label": "OpenClaw Agent (local)", "binary": "openclaw", "args": ["agent", "--local", "--json", "--message", "{prompt}"], "timeout": 300, "output_mode": "json-envelope", "output_text_fields": ["assistant", "response", "reply", "content", "message", "text", "output"]},
    },
    "runtimes": {
        "claude-code": {"label": "Claude Code", "source": "stop_hook:claude-code", "tags": ["runtime:claude-code"]},
        "gemini-cli": {"label": "Gemini CLI", "source": "stop_hook:gemini-cli", "tags": ["runtime:gemini-cli"]},
        "copilot-cli": {"label": "GitHub Copilot CLI", "source": "stop_hook:copilot-cli", "tags": ["runtime:copilot-cli"]},
        "codex-cli": {"label": "Codex CLI", "source": "stop_hook:codex-cli", "tags": ["runtime:codex-cli"]},
        "openclaw": {"label": "OpenClaw", "source": "stop_hook:openclaw", "tags": ["runtime:openclaw"]},
    },
    "launchers": {
        "claude": {"label": "Ghost Claude Wrapper", "binary": "claude", "args": [], "runtime": "claude-code", "executor": "claude"},
        "gemini": {"label": "Ghost Gemini Wrapper", "binary": "gemini", "args": [], "runtime": "gemini-cli", "executor": "gemini"},
        "copilot": {"label": "Ghost Copilot Wrapper", "binary": "copilot", "args": [], "runtime": "copilot-cli", "executor": "copilot"},
        "codex": {"label": "Ghost Codex Wrapper", "binary": "codex", "args": [], "runtime": "codex-cli", "executor": "codex"},
        "openclaw": {"label": "Ghost OpenClaw Wrapper", "binary": "openclaw", "args": ["agent", "--local"], "runtime": "openclaw", "executor": "openclaw-local"},
    },
}


@dataclass(frozen=True)
class PromptExecution:
    executor_id: str
    label: str
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    text_output: str


class _SafeFormatDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def _deep_merge(base: Any, override: Any) -> Any:
    if isinstance(base, dict) and isinstance(override, dict):
        merged = copy.deepcopy(base)
        for key, value in override.items():
            merged[key] = _deep_merge(merged[key], value) if key in merged else copy.deepcopy(value)
        return merged
    return copy.deepcopy(override)


def load_profile_config() -> dict[str, Any]:
    config = copy.deepcopy(DEFAULT_PROFILE_CONFIG)
    if not PROFILE_PATH.exists():
        return config
    try:
        loaded = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return config
    if not isinstance(loaded, dict):
        return config
    return _deep_merge(config, loaded)


def detect_runtime_name() -> str | None:
    if os.environ.get("CLAUDECODE"):
        return "claude-code"
    if os.environ.get("OPENCLAW_STATE_DIR") or os.environ.get("OPENCLAW_CONFIG_PATH"):
        return "openclaw"
    return None


def _resolve_named_profile(section_name: str, explicit_name: str | None, env_var: str | None, fallback_key: str) -> dict[str, Any]:
    config = load_profile_config()
    section = config.get(section_name, {})
    if not isinstance(section, dict) or not section:
        raise RuntimeError(f"No profiles configured for {section_name}")

    profile_name = explicit_name or (os.environ.get(env_var) if env_var else None)
    if not profile_name and section_name == "runtimes":
        profile_name = detect_runtime_name()
    if not profile_name:
        profile_name = config.get(fallback_key)
    if profile_name not in section:
        raise RuntimeError(f"Unknown {section_name[:-1]} '{profile_name}'")
    profile = copy.deepcopy(section[profile_name])
    profile["id"] = profile_name
    profile.setdefault("label", profile_name)
    return profile


def resolve_executor_profile(explicit_name: str | None = None) -> dict[str, Any]:
    return _resolve_named_profile("executors", explicit_name, "GHOST_MEMORY_EXECUTOR", "default_executor")


def resolve_runtime_profile(explicit_name: str | None = None) -> dict[str, Any]:
    profile = _resolve_named_profile("runtimes", explicit_name, "GHOST_MEMORY_RUNTIME", "default_runtime")
    profile.setdefault("source", f"stop_hook:{profile['id']}")
    profile.setdefault("tags", [f"runtime:{profile['id']}"])
    return profile


def resolve_launcher_profile(explicit_name: str | None = None) -> dict[str, Any]:
    return _resolve_named_profile("launchers", explicit_name, "GHOST_MEMORY_LAUNCHER", "default_launcher")


def list_executor_profiles() -> list[dict[str, Any]]:
    return [dict(profile, id=profile_id) for profile_id, profile in load_profile_config().get("executors", {}).items()]


def list_runtime_profiles() -> list[dict[str, Any]]:
    return [dict(profile, id=profile_id) for profile_id, profile in load_profile_config().get("runtimes", {}).items()]


def list_launcher_profiles() -> list[dict[str, Any]]:
    return [dict(profile, id=profile_id) for profile_id, profile in load_profile_config().get("launchers", {}).items()]


def _format_value(template: str, context: dict[str, Any]) -> str:
    return template.format_map(_SafeFormatDict(context))


def build_executor_command(profile: dict[str, Any], prompt: str, extra_context: dict[str, Any] | None = None) -> list[str]:
    context = {"prompt": prompt, "workspace": str(WORKSPACE), "memory": str(MEMORY), "profile": profile["id"]}
    if extra_context:
        context.update(extra_context)
    return [_format_value(str(profile["binary"]), context), *[_format_value(str(arg), context) for arg in profile.get("args", [])]]


def _extract_text_from_payload(payload: Any, field_names: list[str]) -> str | None:
    if isinstance(payload, str):
        return payload.strip() or None
    if isinstance(payload, dict):
        for field_name in field_names:
            value = payload.get(field_name)
            if isinstance(value, str) and value.strip():
                return value.strip()
        for value in payload.values():
            extracted = _extract_text_from_payload(value, field_names)
            if extracted:
                return extracted
    if isinstance(payload, list):
        for value in payload:
            extracted = _extract_text_from_payload(value, field_names)
            if extracted:
                return extracted
    return None


def extract_text_output(raw_stdout: str, profile: dict[str, Any]) -> str:
    if profile.get("output_mode", "text") == "text":
        return raw_stdout or ""
    try:
        payload = json.loads(raw_stdout or "")
    except json.JSONDecodeError:
        return raw_stdout or ""
    return _extract_text_from_payload(payload, profile.get("output_text_fields", [])) or (raw_stdout or "")


def run_prompt(prompt: str, executor_name: str | None = None, timeout: int | None = None, env: dict[str, str] | None = None) -> PromptExecution:
    profile = resolve_executor_profile(executor_name)
    binary = shutil.which(profile["binary"])
    if binary is None:
        raise RuntimeError(f"Executor binary not found: {profile['binary']}")
    command = build_executor_command(profile, prompt)
    command[0] = binary
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout or int(profile.get("timeout", 180)), cwd=str(WORKSPACE), env=dict(os.environ, **(env or {})))
    return PromptExecution(profile["id"], profile.get("label", profile["id"]), command, result.returncode, result.stdout or "", result.stderr or "", extract_text_output(result.stdout or "", profile))
