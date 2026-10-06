# Chapter 20 — Write Discipline

Reading memory wrongly costs one bad answer. Writing memory wrongly costs every
future session that trusts it. This chapter collects the write-side rules that
v5.2 enforces in code, and the conventions that sit next to them.

---

## 1. One writer per workspace

When a workspace is shared by several machines (a synced folder, a network
drive, a second laptop), two writers eventually collide: both compute "last id
+ 1" and allocate the same episode id, or one rewrites `episodic.jsonl` from a
read that is already stale. The loss is silent — the later write simply wins.

The rule is organisational: **exactly one machine is `primary` and owns every
memory write.** Other machines are `secondary` and read only.

```bash
# on the secondary machine (device-local, never inside the workspace)
mkdir -p ~/.config/gish && echo secondary > ~/.config/gish/machine_role
# or per process
export GISH_MACHINE_ROLE=secondary
```

The role is resolved from `GISH_MACHINE_ROLE`, then
`$XDG_CONFIG_HOME/gish/machine_role` (default `~/.config/gish/machine_role`).
It is **never** read from the workspace: a role file inside a synced folder
would sync to every machine and make all of them primary. A machine with no
role configured counts as primary, so single-machine setups need nothing. An
unrecognised value (a typo) fails closed to `secondary`.

On a secondary machine, `gish dream`, `consolidate`, `decay`, and
`EpisodicStore.append` refuse with `SecondaryWriteRefused`. `--dry-run` still
works, because it writes nothing.

Work produced on a secondary machine reaches memory by hand-off: write it to a
file the primary reads (an inbox, a carryover note), and let the primary write
it.

## 2. One write path, under one lock

Episodes enter memory through `EpisodicStore.append` only. It validates against
the schema, deduplicates, and appends **while holding** `memory/.episodic.lock`.
Every engine that rewrites `episodic.jsonl` (decay, consolidate apply) holds the
same lock for its whole read-modify-write.

Why the lock covers the read and not just the write: a rewrite computed from a
read taken before someone else's append will write the file back without that
append. The lock makes "read, decide, write" one step.

Do not append to `episodic.jsonl` with `echo >>` or an editor. A hook that
rejects direct writes to memory files is a cheap way to make this stick.

## 3. Never delete; archive

Nothing in the maintenance pipeline deletes an episode.

- `decay` moves entries `active → fading → archived` by changing
  `decay_status`; the line stays.
- `consolidate` moves the source episodes to
  `memory/_archive/episodic_consolidated.jsonl` **before** it rewrites
  `episodic.jsonl`. If the process dies between the two writes, the result is
  a duplicate, never a loss. The merged entry lists every source in
  `linked_to`, so the trail runs both ways.

Apply the same rule by hand: to retire a file, rename or move it (for example
with a `_DELETE_` prefix) instead of removing it. A timeline you can walk back
is worth more than the disk it uses.

## 4. Nothing grades its own work

Consolidation rewrites memory, so it is split into three steps, and the step
that writes is never the step that judges:

```
propose ──► judge ──► apply
   │          │          │
   │          │          └─ only on grade A–C, under the lock,
   │          │             refuses if the sources changed since proposing
   │          └─ deterministic pre-checks (+ optional external judge)
   └─ .gish/proposals/consolidation_<stamp>.json (kept, with its verdict)
```

The deterministic pre-checks:

| Check | Level | Fails when |
|:--|:--|:--|
| `sources-exist` | hard (F) | a source id is missing or already archived |
| `protected-importance` | hard (F) | a source has importance ≥ 8 |
| `id-unique` | hard (F) | the merged id already exists |
| `enough-evidence` | soft (D) | fewer than 3 sources |
| `links-back` | soft (D) | `linked_to` does not list exactly the sources |
| `non-empty` | soft (D) | the merged content is empty |

An optional external judge adds a second opinion — typically a script that asks
a *different* model from the one that writes memory:

```bash
# device-local only — run as: <command> <proposal.json>
export GISH_JUDGE_COMMAND="python3 /path/to/my_judge.py"
# or, persistently for this machine:
echo "python3 /path/to/my_judge.py" > ~/.config/gish/judge_command
```

The judge command is an executable, so it is **never** read from the
workspace. A workspace may be synced or cloned from someone else; if its
config could name a command, anyone able to write the workspace could run code
on every machine during the nightly dream. A `.gish/config.yml` that still sets
`consolidate.judge_command` is refused: nothing is executed, the proposal is
graded F, and the verdict says where to configure the judge instead.

The judge's last line of output must start with a grade `A`–`F`. The final
grade is the worse of the two. **The judge fails closed:** if it is configured
but crashes, times out, or prints no grade, the proposal is not applied.
A rejected proposal stays in `.gish/proposals/` for a person to read.

Why independence matters: a model asked to grade its own summary agrees with
itself. Use a different model family for the judge, or no external judge at
all — a judge from the same family adds cost and confidence without adding a
check.

## 5. Promotion: from working notes to long-term records

Sessions produce a lot of working material — full source texts, step-by-step
reasoning, scoring. Almost none of it should become long-term memory. When you
distil a source (an article, a report, a long session) into a one-line
long-term record, use a promotion contract:

- **Fixed required fields**, each filled from something you can point to.
  If a field cannot be filled with a traceable value (for example, the source
  is an image-only PDF), the item is not promoted; it is listed as skipped
  with the reason.
- **A traceability path is mandatory and must exist** — the location of the
  full digest the one-liner was distilled from. It is the only way back from
  the summary to the evidence.
- **Do not filter by your own scores.** "Interesting" or "useful" ratings are
  for ranking, not for deciding what gets remembered. A low-scored item that
  was processed successfully is still promoted.
- **A hard batch cap** (we use 8 items per run) is the real limit. If a run is
  near its context budget, record a warning; never drop items silently or cut
  a run in the middle of an item.

## 6. Paths stay relative

Memory files, configs, and notes refer to locations relative to the workspace
root. `gish init` writes `workspace_path: "."`. An absolute path in a memory
file is wrong on every other machine, and in a synced folder it is wrong on
every machine but one.

---

## Next Steps

→ [Chapter 21 — Field Lessons](ch.21-field-lessons.md)
