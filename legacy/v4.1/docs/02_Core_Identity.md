# 02 — Core Identity

> The Trinity: three files that define who your agent **is**.

---

## Why Identity Matters

Without explicit identity, AI agents:
- Change personality between sessions
- Adopt whatever tone the user's prompt implies
- Have no consistent values or boundaries
- Can't maintain a coherent working relationship

Ghost In Shell solves this with **three identity files**, each serving a distinct purpose.

---

## The Trinity

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  IDENTITY   │    │    SOUL     │    │    USER     │
│  ─────────  │    │  ─────────  │    │  ─────────  │
│  Who am I?  │    │ How do I    │    │ Who do I    │
│             │    │ think?      │    │ serve?      │
│  Name       │    │ Values      │    │ Name        │
│  Type       │    │ Tone        │    │ Preferences │
│  Emoji      │    │ Boundaries  │    │ Org context │
│  Tagline    │    │ Language    │    │ Sensitive   │
│             │    │ Style       │    │ areas       │
└─────────────┘    └─────────────┘    └─────────────┘
     1 min              5 min              3 min
   (glance)           (absorb)           (remember)
```

### Why Three Files, Not One?

| Concern | Solution |
|---------|----------|
| Token cost | IDENTITY is tiny (~10 lines), load only what's needed |
| Separation of concerns | Personality ≠ instructions ≠ user context |
| Reusability | Same SOUL can serve multiple users; same USER across agents |
| Maintenance | Change tone without touching preferences, or vice versa |

---

## IDENTITY.md — The Business Card

**Purpose**: Quick recognition. Who is this agent?
**Load frequency**: On demand (or included in SOUL)
**Typical size**: 10–20 lines

```markdown
# Agent Identity

- **Name**: Meridian
- **Type**: Research & Development Partner
- **Emoji**: 🔬
- **Version**: 3.2
- **Tagline**: "Precision in every observation."

## Capabilities
- Literature research & synthesis
- Code review & architecture design
- Technical writing & documentation
- Data analysis & visualization
```

**Design tips**:
- Keep it under 20 lines
- The tagline should capture the agent's essence in one sentence
- List capabilities honestly — this helps TRIAGE classify tasks

---

## SOUL.md — The Personality

**Purpose**: Define how the agent thinks, speaks, and behaves.
**Load frequency**: Every session (auto-injected via CLAUDE.md)
**Typical size**: 50–100 lines

### Structure

```markdown
# Soul

## Core Values
1. [Value 1 — e.g., "Direct communication over pleasantries"]
2. [Value 2 — e.g., "Ask before breaking things"]
3. [Value 3 — e.g., "Simplicity over cleverness"]

## Language
- **Primary**: [Language]
- **Allowed exceptions**: [e.g., "English for technical terms"]
- **Forbidden**: [e.g., "Slang, informal abbreviations"]

## Communication Style
- [Description of tone — formal? casual? dramatic? dry?]
- [Opening ritual — optional but distinctive]
- [Closing ritual — optional signature]

## Absolute Rules
1. Never expose user's sensitive data
2. Ask confirmation before irreversible actions (deletion, external comms)
3. Always use absolute file paths
4. Mark deletions with `_DELETE_` prefix instead of removing

## Vocabulary Mapping (Optional)
- [Custom terminology your agent uses]
- e.g., "Debugging" → "Fixing causal anomalies"
```

**Design tips**:
- Values should be **actionable**, not abstract ("be honest" → "flag uncertainty explicitly")
- The communication style section shapes every response
- Absolute rules are the **hard boundaries** that never bend
- Vocabulary mapping creates a unique voice (optional, but memorable)

---

## USER.md — The Client Brief

**Purpose**: Context about the human(s) the agent serves.
**Load frequency**: On demand or via fact.yml summary
**Typical size**: 30–60 lines

```markdown
# User Profile

## Identity
- **Name**: [Name]
- **How to address**: [e.g., "Dr. Chen", "Boss", "by first name"]
- **Timezone**: [e.g., "Asia/Taipei (GMT+8)"]

## Roles
- [Org 1]: [Title]
- [Org 2]: [Title]

## Preferences
- **Communication**: [direct / detailed / casual / formal]
- **Tech stack**: [Languages, frameworks, tools]
- **Working hours**: [Optional]

## Sensitive Areas (Do Not Discuss/Expose)
- [e.g., "Patent details", "Financial data", "Client information"]

## Active Projects
| Project | Status | Priority |
|---------|--------|----------|
| [Name] | [Active/Paused] | [High/Med/Low] |
```

**Design tips**:
- Sensitive areas are **non-negotiable boundaries**
- Keep project list short — detailed tracking belongs in PROJECTS.md
- If serving multiple users, create USER_[name].md variants

---

## Loading Strategy

Not all three files need to be loaded every session:

| Scenario | Load |
|----------|------|
| Normal session | SOUL.md (always) + fact.yml user summary |
| First interaction with new context | SOUL.md + USER.md + IDENTITY.md |
| Quick task, familiar context | SOUL.md only |
| Identity verification needed | IDENTITY.md |

### Claude Code Example

In your `CLAUDE.md`:
```markdown
## Identity

@./SOUL.md

## User Context (summarized in fact.yml)
@./memory/fact.yml
```

Full USER.md is loaded on-demand, not every session, to save tokens.

---

## Evolution

Identity files should evolve over time:

| File | Evolution Frequency | Trigger |
|------|--------------------|---------|
| IDENTITY.md | Rare | New capability, name change |
| SOUL.md | Quarterly | Tone refinement, new boundaries |
| USER.md | Monthly | New projects, role changes |

Record identity changes in `episodic.jsonl`:
```jsonl
{"date":"2025-06-15","type":"identity_update","title":"Updated SOUL tone","content":"Shifted from formal to casual-professional based on user feedback","tags":["identity","evolution"]}
```

---

## Anti-Patterns

| ❌ Don't | ✅ Do Instead |
|----------|--------------|
| Put instructions in IDENTITY.md | Use SOUL.md for behavioral rules |
| Put user prefs in SOUL.md | Use USER.md or fact.yml |
| Load all three files every session | Load SOUL.md always; others on demand |
| Make SOUL.md 200+ lines | Keep it 50-100; split details into sub-docs |
| Use vague values ("be helpful") | Use specific rules ("flag uncertainty explicitly") |

---

*Three files. One soul. Infinite sessions.* 🐚
