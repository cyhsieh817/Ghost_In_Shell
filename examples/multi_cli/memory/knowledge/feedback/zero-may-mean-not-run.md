---
name: zero-may-mean-not-run
description: An error count of zero is also what a pipeline reports when the step never ran
metadata:
  type: feedback
  updated: 2026-10-01
  confidence: 0.9
---

Treat "0 errors" as meaningful only together with a separate end-of-run
signal: a completion line, or an output file dated today.

**Why:** a nightly job reported zero failures for a week because an early
exit skipped the stage that produces failures.

**How to apply:** when a check reports zero, confirm the check reached its
last step before trusting the zero.
