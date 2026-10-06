# Chapter 19 — The Knowledge Index

The episodic log records *what happened*. It does not tell the agent, at the
start of tomorrow's session, *what to be careful about*. That is the job of the
knowledge layer: short notes, one fact or rule each, found through a startup
index that every session loads.

This chapter describes the layout, the frontmatter contract, how to write index
lines that are actually found, and the budget that keeps the index from
silently breaking.

---

## Layout

```
my-workspace/
├── MEMORY.md                      # startup index — loaded in full every session
└── memory/knowledge/
    ├── INDEX_<topic>.md           # optional shelf indexes (second level)
    ├── feedback/                  # rules: corrections and confirmed approaches
    ├── projects/                  # ongoing work, goals, constraints
    ├── references/                # pointers to external resources
    └── user/                      # who the user is and how they work
```

`gish init` creates the four shelves. Each note is one Markdown file.

| Note type (`metadata.type`) | Shelf | Holds |
|:--|:--|:--|
| `feedback` | `feedback/` | A rule plus **Why** and **How to apply** |
| `project` | `projects/` | State of ongoing work; convert relative dates to absolute |
| `reference` | `references/` | Where to look, and what you will find there |
| `user` | `user/` | Role, expertise, preferences |

---

## The note contract

```markdown
---
name: verify-final-state
description: A tool's success message is not proof; check the final state yourself
metadata:
  type: feedback
  updated: 2026-09-30        # date the content was last verified, not edited
  confidence: 0.9            # optional, see scale below
  evidence: [ep-2026-09-28-004]   # optional: episode ids or file paths
  expires: 2027-03-31        # optional: only for claims that go stale
---

Check the end state (the file, the page, the row) before reporting done.

**Why:** a deploy reported success while the live page still served the old build.

**How to apply:** after any write that goes through a tool or channel, read the
result back from where the user will see it.
```

`gish knowledge lint` enforces:

- `name` equals the file stem; `description` is one non-empty line.
- `metadata.type` is one of the four types and matches the shelf.
- `metadata.updated` is a `YYYY-MM-DD` date.
- `confidence` (if present) is between 0.0 and 1.0; `evidence` is a list;
  `expires` is a date. A past `expires` is a warning: re-verify or archive.
- Governance fields belong under `metadata:`, not at the top level.
- Feedback notes carry `**Why:**` and `**How to apply:**` lines (warning).

A suggested confidence scale: `1.0` stated by the user; `0.9` measured, with
output to show for it; `0.7` observed once, not repeated; `≤0.5` inferred.
**Never back-fill confidence mechanically.** A guessed number is worse than an
empty field, because readers trust it.

Create notes with the skeleton already correct:

```bash
gish knowledge new feedback verify-final-state \
  -d "A tool's success message is not proof; check the final state yourself" \
  --workspace .
```

---

## Writing index lines that get found

An index line is a trigger phrase plus a link:

```markdown
- "The tool returned success, so it is done" → [verify the final state](memory/knowledge/feedback/verify-final-state.md)
```

Two rules decide whether a line ever fires.

**1. Write the symptom you will have, not the cause.** At the moment the note
matters, the agent is thinking "the tool said OK, so it is done". It is not
thinking "tool reports are unreliable" — if it were, it would not need the note.
An index keyed by causes is an index of things you already know.

**2. Name both directions of a two-sided failure.** Many failures come in
pairs: a check that misses real problems *and* a check that blocks good work; a
false green *and* a false red. If the line names only one direction, the other
direction is never found, even though the answer is in the note. Write both:

```markdown
- "The gate passed, so it is fine" **or the reverse** "the gate blocked me but I did nothing wrong" → [...]
```

`gish knowledge lint` warns about index lines that link a note without a
trigger (`→`), about notes that no index line points to (an orphan note is a
note no session will ever read), and fails on links to notes that do not exist.

---

## Tier 1 and shelves: what belongs in the startup index

Every line in `MEMORY.md` is paid for in every session. The test for putting a
line there is **"will the agent look this up on its own?"** — not "is it
important?".

- **Startup index (Tier 1)** — rules the agent *does not know it is breaking*
  and that touch almost every task: verifying results, delegating work,
  destructive operations, how memory itself is written.
- **Shelf index (`memory/knowledge/INDEX_<topic>.md`)** — notes the agent will
  look for when it knows it is in that area: a tool's quirks, a test
  framework's traps, a build system's conventions. Link each shelf index from
  `MEMORY.md` with its own trigger line.

When unsure, put it on a shelf. Moving a line down is reversible; overflowing
the startup index is not (see below).

**Do not prune Tier 1 by hit frequency.** A Tier 1 rule is, by definition, one
the agent will not think to look up. Low usage is the reason it exists, not a
reason to remove it. Measure before pruning, and prune shelf-worthy lines first.

---

## The budget

Some CLIs load a startup memory file only up to a fixed size and drop the rest
**without any warning**. The lines that vanish are the newest ones — usually
the lesson you just learned. The index therefore has a budget, measured in
characters (not bytes, not lines: a line of CJK text and a line of ASCII cost
very differently in bytes).

```yaml
# .gish/config.yml
index:
  max_chars: 20000            # soft ceiling: compress before adding
  truncate_edge_chars: 24400  # where the tail starts to disappear
```

```bash
gish index budget --workspace .
# 12480 chars  15102 B  96 lines  status=ok  max=20000  edge=24400  headroom=7520
```

| Exit | Meaning | Action |
|:--|:--|:--|
| 0 | under `max_chars` | add the line |
| 1 | over `max_chars` | move entries to a shelf index first |
| 2 | past the truncation edge | the tail is already being cut; fix now |
| 3 | `MEMORY.md` missing | run `gish init` |

Set `truncate_edge_chars` from your own CLI's documented or measured limit.
`gish doctor` and the nightly `dream` gate report an over-budget index and any
`knowledge lint` errors as health issues.

**When over budget:** move the *full* line (trigger and link) into a shelf
index, then leave one line in `MEMORY.md` that points at the shelf. Do not
shorten lines by deleting the unique number, exception, or path that made the
note findable; a shorter line that no longer matches the symptom is worse than
no line.

---

## Next Steps

→ [Chapter 20 — Write Discipline](ch.20-write-discipline.md)
