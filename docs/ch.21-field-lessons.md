# Chapter 21 — Field Lessons

The rules in chapters 19 and 20 came from running this architecture every day
for most of a year, with several AI CLIs writing to one workspace. This chapter
lists the lessons that changed the design. Each one is written the way it
should appear in your own index: the symptom first, then the rule.

None of them is about a specific model or tool. They are about how memory and
verification fail when an agent works on its own.

---

### 1. "The tool said it succeeded, so it is done"

A success message describes what the tool *attempted*. A deploy reported
success while users still received the old page from a cache; a file write
reported success while a formatter hook removed the line a moment later.

**Rule:** verify the final state where the user will see it — the live page
with a cache-buster, the file on disk after hooks ran, the row in the database.
A report from a channel is a claim, not evidence.

### 2. "Zero errors, so nothing is wrong"

Zero errors also appears when the step that would produce errors never ran: an
early exit, a skipped stage, an empty input.

**Rule:** every pipeline needs an end-of-run signal (a "completed" line, a
fresh output file dated today) that is checked separately from the error
count. `gish dream` reports each stage's result and treats a stage that raised
as a failure, rather than as zero findings.

### 3. "We already have a check for that"

A function with its own unit tests, a config field documented in the README,
and a memory note that mentions it — and no code path that calls it. The
check had never run in production.

**Rule:** count the call sites, excluding the definition and the tests. Zero
means dead code, however green its tests are. When you wire an old check in,
run it on real data before making it blocking: a check that has never run has
never been checked either.

### 4. "Memory says X is not possible"

A note said a tool did not support a feature. The tool had added it months
before. The opposite also happens: memory says a record exists, one search
returns nothing, and the agent concludes it does not exist.

**Rule:** a negative claim in memory is a snapshot with a date, not a fact.
Give such notes an `expires` date (ch.19). When memory says something exists
and a search finds nothing, suspect the query first; report "not found" only
together with the terms and endpoints you tried.

### 5. "Let's compress the index; it must be full of stale lines"

The request to shrink the startup index came up again and again across
sessions. When we finally measured — every index entry against a year of
session transcripts — no entry had zero hits. The cleanup's target set was
empty.

**Rule:** measure the denominator before building. Ask how often a cost is
paid and by whom (per session vs per call); the most frequent cost is the one
to cut, not the largest single item. And do not prune Tier 1 rules by
frequency (ch.19): low use is what a rule you don't know you need looks like.

### 6. "The other agent's report matches what I expected"

When a task description handed to another agent contains an assumption
("the cache is probably the cause"), the work often comes back with that
assumption restated as a finding.

**Rule:** write unverified beliefs in a hand-off as questions, not statements,
and check the returned evidence against the original source rather than
against your own expectation.

### 7. "The code and its check agree"

When the same writer produces an implementation and its test, both can carry
the same mistake and confirm each other. A test can also re-derive the formula
it is meant to check, or assert against a helper instead of the real function.

**Rule:** compare against the source of truth, not against a second copy. Use
mutation checks: break the implementation on purpose and confirm the test goes
red. (The v5.2 consolidation gate and knowledge lint were mutation-checked
this way before release.)

### 8. "Open a reminder for this follow-up"

The same follow-up was created again in later sessions, each time in different
words, until there were many copies of one task.

**Rule:** before creating a follow-up, search for it using more than one
keyword. If it exists, update it instead. A carryover note (ch.13) with an
expiry date is easier to deduplicate than free-text reminders.

### 9. "Two records say the same path, so it is confirmed"

Two notes written at the same time agree with each other — and both are out of
date, because the thing they describe moved later.

**Rule:** records written together expire together; agreement between them is
not independent confirmation. Before a path from memory goes into a plan or a
hand-off, check that it exists.

### 10. "Tests pass, but it still behaves the old way"

The tests ran against the repository source; the command line ran an installed
copy that was several versions behind.

**Rule:** before debugging behaviour, confirm which copy actually runs
(`gish version`, `which gish`). When the installed copy and the source differ,
look at the direction of the difference before syncing: if both sides have
changes, it is a fork, and a blind sync deletes work.

---

## Putting the lessons to work

1. Copy the ones that match your situation into `memory/knowledge/feedback/`
   with `gish knowledge new feedback <slug> -d "..."`.
2. Write the index line as the symptom, both directions where they exist.
3. Run `gish index budget` before adding the line, and `gish knowledge lint`
   after.
4. When a lesson stops being true, do not delete it: set `expires`, update it,
   or move it to the archive with a note on what replaced it.

---

## Next Steps

→ [README](../README.md#documentation)
