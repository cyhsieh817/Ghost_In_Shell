---
name: verify-final-state
description: A tool's success message is a claim; check the final state where the user will see it
metadata:
  type: feedback
  updated: 2026-10-01
  confidence: 0.9
---

Before reporting a write, deploy, or edit as done, read the result back from
where the user will see it: the live page (with a cache-buster), the file on
disk after hooks have run, the row in the database.

**Why:** a deploy reported success while users still received the cached old
page; a formatter hook silently removed a line right after the editor reported
the edit as saved.

**How to apply:** any time the evidence for "done" is a message from the tool
that did the work, add one independent read of the end state.
