# Chapter 05 — Multi-CLI Adapters

Ghost In Shell supports four AI CLI tools as first-class adapters. Each adapter generates
the correct hook code and root instruction format for its CLI, so the memory system works
transparently regardless of which tool you use.

---

## Supported Adapters

| Adapter | CLI Binary | Root File | Hook Mechanism |
|---------|-----------|-----------|----------------|
| `claude` | `claude` | `CLAUDE.md` | `~/.claude/settings.json` Stop hook |
| `gemini` | `gemini` | `GEMINI.md` | Wrapper exit handler |
| `codex` | `codex` | `CODEX.md` | Wrapper exit handler |
| `copilot` | `gh` | `COPILOT.md` | Shell alias wrapper |

---

## Adapter Architecture

Every adapter inherits from `CLIAdapter` (abstract base class in
`ghost_in_shell.adapters.base`):

```python
class CLIAdapter(ABC):
    name: str = ""
    cli_binary: str = ""

    def session_start_hook(self) -> str: ...   # Emit start-hook snippet
    def session_end_hook(self) -> str: ...     # Emit stop-hook snippet
    def root_instruction_template(self) -> str: ...  # Full root instruction
    def detect_installation(self) -> bool: ...  # Check if CLI is installed
    def launch(self, args: list[str]) -> int: ...   # Generic launcher
```

`ghost_in_shell.adapters.get_adapter(name)` returns the correct concrete adapter.

---

## Claude Code Adapter

**Binary**: `claude`  
**Root file**: `CLAUDE.md`

The Claude Code adapter uses the `@import` mechanism. Add to your `CLAUDE.md`:

```markdown
@/path/to/workspace/IDENTITY.md
@/path/to/workspace/SOUL.md
@/path/to/workspace/USER.md
@/path/to/workspace/MEMORY.md
```

**Session-end hook** — add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "type": "command",
        "command": "gish log --from-session",
        "matcher": ".*"
      }
    ]
  }
}
```

**PreToolUse hook** (optional) — trigger retrieval-buffer access before reads:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "type": "command",
        "command": "gish recall --workspace /path/to/workspace",
        "matcher": "Read|Write"
      }
    ]
  }
}
```

---

## Gemini CLI Adapter

**Binary**: `gemini`  
**Root file**: `GEMINI.md`

GEMINI.md is automatically loaded at session start by Gemini CLI. Add:

```markdown
@/path/to/workspace/IDENTITY.md
@/path/to/workspace/SOUL.md
@/path/to/workspace/USER.md
@/path/to/workspace/MEMORY.md
```

**Session-end hook** — in your gemini wrapper script:

```bash
#!/usr/bin/env bash
gemini "$@"
gish log --from-session --workspace /path/to/workspace
```

---

## Codex CLI Adapter

**Binary**: `codex`  
**Root file**: `CODEX.md`

```markdown
@/path/to/workspace/IDENTITY.md
@/path/to/workspace/SOUL.md
@/path/to/workspace/USER.md
@/path/to/workspace/MEMORY.md
```

**Session-end hook** — in your codex wrapper script:

```bash
#!/usr/bin/env bash
codex "$@"
gish log --from-session --workspace /path/to/workspace
```

---

## GitHub Copilot CLI Adapter

**Binary**: `gh` (via `gh copilot`)  
**Root file**: `COPILOT.md`

Copilot CLI does not natively support stop hooks. Use a shell alias:

```bash
# ~/.zshrc or ~/.bashrc
alias copilot='gh copilot; gish log --from-session --workspace /path/to/workspace'
```

Reference `COPILOT.md` from the Copilot global config at `~/.github/copilot/`.

---

## Getting Hook Snippets

Run `gish init` (or `gish init --non-interactive`) to automatically detect installed CLIs
and print the correct hook snippets for each:

```bash
gish init ~/my-workspace --non-interactive
```

Output:

```
── Hook snippets for detected CLIs ──

[claude] session-start hook:
@/path/to/workspace/IDENTITY.md
...

[claude] session-end hook:
# Add to ~/.claude/settings.json → hooks → Stop:
...
```

---

## Checking Adapter Detection

```python
from ghost_in_shell.adapters import get_adapter

adapter = get_adapter("claude")
print(adapter.detect_installation())   # True / False
print(adapter.session_start_hook())
print(adapter.root_instruction_template())
```

---

## Using Multiple Adapters Simultaneously

Because each adapter loads the same workspace files, all four CLIs share a single memory
store. Sessions from different CLIs are differentiated in the session log by the
`--runtime` flag passed to `gish log`:

```bash
gish log --from-session --workspace ~/ws --runtime claude-code
gish log --from-session --workspace ~/ws --runtime gemini-cli
```

See `examples/multi_cli/` for a complete multi-adapter workspace example.

---

## Next Steps

→ [Chapter 06 — Governance & Sanctum](ch.06-governance-sanctum.md)
