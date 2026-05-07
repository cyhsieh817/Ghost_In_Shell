# Chapter 02 — Identity Trinity

The Identity Trinity is the set of three markdown files that establish who the agent is,
how it behaves, and what the user expects. Every supported CLI adapter is configured to
load all three at session start.

---

## The Three Files

### `IDENTITY.md`

Describes the workspace and the agent's role. This is the "who am I" file.

Typical contents:

```markdown
# Identity

## Workspace
This workspace supports the Acme project.

## Role
You are a senior software engineer assistant focused on Python and distributed systems.

## Core responsibilities
- Review code changes for correctness and security.
- Explain architecture decisions with context from memory.
- Log important insights and decisions to episodic memory.
```

This file should be factual and stable. Change it when the project's scope changes, not
on every session.

### `SOUL.md`

Defines the agent's persona — tone, communication style, and any absolute rules.
This is the "how I behave" file.

Typical contents:

```markdown
# Soul

## Persona
Precise, concise, technically grounded. Prefer code over prose when explaining concepts.

## Communication style
- Use bullet lists for enumerations.
- Lead with the answer, then provide context.
- Do not hedge with "I think" or "possibly".

## Absolute rules
- Never delete files without explicit confirmation.
- Always cite sources when referencing external documentation.
```

SOUL.md is where you put the rules you never want the agent to violate.

### `USER.md`

Captures the user's personal preferences, workflow habits, and environmental context.
This is optional but recommended.

```markdown
# User Preferences

## Environment
- OS: macOS
- Shell: zsh
- Editor: neovim

## Workflow preferences
- Commit messages follow Conventional Commits.
- Use British English spelling.
- Tests before implementation (TDD).
```

---

## How the Trinity Is Loaded

Each adapter generates a root instruction (CLAUDE.md, GEMINI.md, CODEX.md, COPILOT.md)
that imports all three files. The import mechanism differs per CLI:

| CLI | Load mechanism |
|-----|----------------|
| Claude Code | `@<path>/IDENTITY.md` in CLAUDE.md |
| Gemini CLI | `@<path>/IDENTITY.md` in GEMINI.md |
| Codex CLI | `@<path>/IDENTITY.md` in CODEX.md |
| Copilot CLI | Referenced in the Copilot custom instruction file |

`gish init` generates the correct import block for each detected CLI.

A fourth file, `MEMORY.md`, serves as the **memory index** — it points the session to
the `memory/` directory and summarises what is stored there. It is loaded alongside the
Trinity at session start.

---

## Managing the Files

The files are plain markdown. You edit them directly. There is no schema enforcement —
they are prose instructions for the agent.

Recommendations:

- Keep `IDENTITY.md` under 100 lines. Agents context-windows are finite.
- Keep `SOUL.md` rule lists under 20 items — prioritise the most important ones.
- Version-control all three files with your project so changes are tracked.

---

## Generating from `gish init`

`gish init <workspace>` seeds template versions of all three files from
`ghost_in_shell/templates/identity/`. Edit the templates before running `gish init` to
customise defaults for your organisation.

---

## Next Steps

→ [Chapter 03 — Memory Architecture](ch.03-memory-architecture.md)
