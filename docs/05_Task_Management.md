# 05 — Task Management

> Classify, execute, iterate, suggest — a complete task lifecycle.

---

## Overview

Ghost In Shell manages tasks through four systems:

```
Task arrives
     ↓
[1. TRIAGE] — Classify risk level
     ↓
[2. EXECUTE] — Simple (direct) or Complex (3-round iteration)
     ↓
[3. REVIEW] — Self-check against quality criteria
     ↓
[4. SUGGEST] — Propose next steps (ABCD menu)
```

---

## 1. TRIAGE — Risk Classification

Every task gets classified before execution:

| Level | Label | Action | Examples |
|:-----:|-------|--------|---------|
| 🟢 | **AUTO** | Execute immediately | File organization, logging, analysis |
| 🟡 | **CONFIRM** | Execute, then notify user | Creating files, knowledge updates |
| 🟠 | **PROPOSE** | Draft plan, wait for approval | Unknown task types, architectural changes |
| 🔴 | **ASK** | Ask before doing anything | Deletion, sending emails, publishing |
| 🔒 | **LOCKED** | Requires verification code | Modifying core identity files |

### TRIAGE Decision Flow

```
New task received
     ↓
Can I do this? (check CAPABILITIES.md)
     ├── No → Inform user, suggest alternatives
     ↓
     Yes
     ↓
What's the risk level?
     ├── Routine + reversible → 🟢 AUTO
     ├── Creates new artifacts → 🟡 CONFIRM
     ├── No existing SOP → 🟠 PROPOSE
     ├── Irreversible or external → 🔴 ASK
     └── Touches core identity → 🔒 LOCKED
```

### TRIAGE Examples

| Task | Level | Why |
|------|-------|-----|
| "Organize my inbox" | 🟢 AUTO | Routine, reversible |
| "Summarize this paper" | 🟢 AUTO | Read-only analysis |
| "Create a project plan" | 🟡 CONFIRM | Creates new file |
| "Build a dashboard" | 🟠 PROPOSE | No existing SOP, multiple approaches |
| "Delete old backups" | 🔴 ASK | Irreversible |
| "Send this to the client" | 🔴 ASK | External communication |
| "Update my SOUL.md values" | 🔒 LOCKED | Core identity modification |

---

## 2. Execution Modes

### Simple Task (Direct)

For 🟢/🟡 tasks with clear requirements:

```
Understand → Execute → Report
```

### Complex Task (3-Round Iteration)

For 🟠+ tasks or any task requiring quality:

```
Round 1 — STRUCTURE
  Goal: Complete framework, all sections present
  Focus: Breadth over depth
  Output: Rough but complete draft

Round 2 — REFINE
  Goal: Fill details, add data/diagrams
  Focus: Depth and accuracy
  Output: Near-final quality

Round 3 — POLISH
  Goal: Perfect formatting, catch errors
  Focus: Edge cases, consistency
  Output: Deliverable quality
```

**After each round, self-check**:
1. Does this meet the round's goal?
2. What's still missing from the checklist?
3. What should the next round prioritize?

---

## 3. Unknown Task Handler

When a task has no existing SOP:

```
1. ANALYZE — Break down what's needed
2. DESIGN — Create 3 approach options
3. PROPOSE — Present ABCD menu:

   ┌──────────────────────────────────┐
   │  How should I approach this?     │
   │                                  │
   │  A. [Approach 1] — [trade-off]   │
   │  B. [Approach 2] — [trade-off]   │
   │  C. [Approach 3] — [trade-off]   │
   │  D. Let me ask more questions    │
   └──────────────────────────────────┘

4. EXECUTE — Implement chosen approach
5. REGISTER — Save the SOP to Task_Registry.md
```

**Why register?** Next time a similar task arrives, the agent already has an SOP → automatically classifies as 🟢/🟡 instead of 🟠.

---

## 4. Post-Task Suggestions

After completing a task and passing self-review:

```
✅ Task complete.

────────────────────────
📋 What's next?

  A. [Expand] — [e.g., "Add unit tests for this module"]
  B. [Optimize] — [e.g., "Refactor for performance"]
  C. [Related] — [e.g., "Update documentation to match"]
  D. ✅ Done — End this task
────────────────────────

Choose A/B/C/D:
```

**Rules**:
- Suggestions must be **specific and actionable** (not "improve the code")
- Always include option D (done) — the user is in control
- Maximum 3 suggestions + done option
- Only suggest after self-review passes

---

## Quality Checklist

Universal checklist for self-review (adapt per domain):

### For Code
- [ ] Does it compile/run without errors?
- [ ] Are edge cases handled?
- [ ] Is there adequate error handling?
- [ ] Does it follow project conventions?
- [ ] Are there security concerns?

### For Documents
- [ ] Is the structure logical and complete?
- [ ] Are claims supported with evidence?
- [ ] Is formatting consistent?
- [ ] Are links/references valid?
- [ ] Is the language appropriate for the audience?

### For Analysis
- [ ] Is the data source reliable?
- [ ] Are assumptions stated explicitly?
- [ ] Are conclusions supported by the data?
- [ ] Are limitations acknowledged?
- [ ] Is the visualization clear?

---

## Capability Declaration

Agents should be honest about what they can and can't do:

```markdown
# CAPABILITIES.md

## Can Do (Built-in)
- File read/write/organize
- Text generation and analysis
- Code review and writing
- Research and synthesis

## Can Do (With Tools)
- Web search (requires browser/search tool)
- API calls (requires credentials)
- Image generation (requires image tool)

## Cannot Do
- Financial transactions
- Physical world interactions
- Access systems without credentials
- Guarantee factual accuracy of generated content
```

---

## Task Registry

Track SOPs for recurring tasks:

```markdown
# Task_Registry.md

| Task Type | TRIAGE | SOP | Last Updated |
|-----------|--------|-----|-------------|
| Inbox organization | 🟢 AUTO | Sort by date, categorize by domain | 2025-01-15 |
| Literature summary | 🟢 AUTO | Read → extract key findings → format | 2025-01-10 |
| Project planning | 🟡 CONFIRM | Analyze scope → ABCD approach → plan | 2025-01-12 |
| External email | 🔴 ASK | Draft → Outbox → user review → send | 2025-01-08 |
```

---

*Classify. Execute. Iterate. Evolve.* 🐚
