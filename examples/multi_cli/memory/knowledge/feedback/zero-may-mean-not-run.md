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

**Why:** an acceptance check counted zero load failures and passed, while the
service had already exited before it reached the load step.

**How to apply:** when a check reports zero, confirm the check reached its
last step before trusting the zero.
