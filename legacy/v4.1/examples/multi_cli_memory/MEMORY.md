# Memory Index

> Always-loaded router for the shared multi-CLI memory system.

## Core Layers

| Layer | File | Purpose |
|-------|------|---------|
| L1 Hot | `memory/fact.yml` | Active identity, rules, tools, runtime policy |
| L1 Episodes | `memory/episodic.jsonl` | Append-only lessons and milestones |
| L0.5 Scratch | `memory/scratchpad.md` | Current task notes |

## Runtime Registry

| File | Purpose |
|------|---------|
| `memory/runtime_profiles.yml` | Canonical runtime / executor / launcher map |
| `scripts/memory_runtime.py` | Runtime lookup helpers |
| `scripts/memory_session_log.py` | Session-end episodic logging |

## Interactive Entry Points

| CLI | Command | Runtime ID |
|-----|---------|------------|
| Claude Code | `bash scripts/void-claude.sh` | `claude-code` |
| Gemini CLI | `bash scripts/void-gemini.sh` | `gemini-cli` |
| GitHub Copilot CLI | `bash scripts/void-copilot.sh` | `copilot-cli` |
| Codex CLI | `bash scripts/void-codex.sh` | `codex-cli` |
| OpenClaw | `bash scripts/void-openclaw.sh` | `openclaw` |

## Maintenance

- `python3 scripts/memory_status.py`
- `python3 scripts/memory_trigger_check.py`
- `python3 scripts/llm_memory_wrapper.py --list-launchers`
