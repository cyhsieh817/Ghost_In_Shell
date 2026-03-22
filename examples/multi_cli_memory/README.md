# Multi-CLI Memory Reference Implementation

> A copy-ready reference workspace for Claude Code, Gemini CLI, GitHub Copilot CLI, Codex, and OpenClaw sharing one memory system.

---

## What This Example Includes

- one shared memory layer (`MEMORY.md` + `memory/fact.yml` + `memory/episodic.jsonl`)
- one root instruction file per CLI (`CLAUDE.md`, `GEMINI.md`, `AGENTS.md`, `COPILOT.md`, `CODEX.md`, `OPENCLAW.md`)
- wrapper-first automation (`scripts/void-*.sh`, `scripts/llm_memory_wrapper.py`)
- session-end auto-logging (`scripts/memory_session_log.py`)
- optional shell installer (`scripts/install_llm_shell_aliases.py`)

This is the layer you add **after** the starter kit when a single workspace must support multiple AI CLIs.

---

## Layout

```
multi_cli_memory/
├── CLAUDE.md
├── GEMINI.md
├── AGENTS.md
├── COPILOT.md
├── CODEX.md
├── OPENCLAW.md
├── IDENTITY.md
├── SOUL.md
├── USER.md
├── MEMORY.md
├── memory/
│   ├── fact.yml
│   ├── episodic.jsonl
│   ├── runtime_profiles.yml
│   └── scratchpad.md
├── scripts/
│   ├── memory_runtime.py
│   ├── llm_memory_wrapper.py
│   ├── memory_session_log.py
│   ├── install_llm_shell_aliases.py
│   ├── void-shell-wrappers.sh
│   └── void-*.sh
└── .claude/
    └── settings.json.example
```

---

## Quick Start

1. Copy this folder to your own workspace root.
2. Personalize `IDENTITY.md`, `USER.md`, `SOUL.md`, and `memory/fact.yml`.
3. Review launcher profiles:

   ```bash
   python3 scripts/llm_memory_wrapper.py --list-launchers
   ```

4. Dry-run one wrapper:

   ```bash
   GHOST_MEMORY_WRAPPER_DRY_RUN=1 bash scripts/void-claude.sh --help
   ```

5. Optionally install shell-level wrappers:

   ```bash
   python3 scripts/install_llm_shell_aliases.py
   ```

6. Start using your CLI of choice:

   ```bash
   claude
   gemini
   copilot
   ```

---

## Design Notes

### 1. Wrapper-first, not model-first

The model should not have to remember:

- when to log a session
- which runtime ID to attach
- when to append to `episodic.jsonl`

The wrapper / hook layer owns that responsibility.

### 2. One memory, many executors

Every CLI writes to the same:

- `memory/episodic.jsonl`
- `memory/fact.yml`
- `MEMORY.md`

But each CLI gets its own root file and runtime ID.

### 3. JSON syntax in `runtime_profiles.yml`

This reference file uses JSON-compatible syntax even though the extension is `.yml`.
That keeps the example **stdlib-only** while still demonstrating a canonical runtime registry.

---

## Native Hook Option (Claude Code)

If you prefer a native Stop hook instead of wrapper-only logging, start from:

- `.claude/settings.json.example`

Then replace `/absolute/path/to/your/workspace` with your real workspace path.

---

## Escape Hatches

If you install shell wrappers, the original binaries remain available as:

- `claude_native`
- `gemini_native`
- `copilot_native`
- `codex_native`
- `openclaw_native`

---

*Use this as a teaching bundle: copy it, rename it, adapt it, and keep the memory path canonical.*
