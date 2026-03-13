# 07 — Evolution Protocol

> Static prompts create static tools. Let your agent grow.

---

## The Problem

Most AI agent setups are **frozen at birth** — same instructions, same behavior, forever. Ghost In Shell makes agents **living systems** that learn and adapt.

---

## R-M-E-C: The Evolution Loop

```
┌──────────────────────────────────────┐
│         R-M-E-C Cycle                │
│                                      │
│  [R] Reflect   → What happened?      │
│       ↓                              │
│  [M] Mutate    → What could change?  │
│       ↓                              │
│  [E] Evolve    → Apply the change    │
│       ↓                              │
│  [C] Commit    → Record & persist    │
│       ↓                              │
│  (back to R on next trigger)         │
└──────────────────────────────────────┘
```

### Reflect

After significant tasks, the agent asks itself:
- What went well?
- What failed or was inefficient?
- What patterns am I seeing across recent tasks?

**Output**: Entry in `episodic.jsonl`

### Mutate

Based on reflection, propose changes:
- New rule for `fact.yml`
- Updated SOP in `Task_Registry.md`
- Modified communication style in `SOUL.md`

**Output**: Proposed change (not yet applied)

### Evolve

Apply the change with appropriate TRIAGE level:
- New rule → 🟡 CONFIRM (add to fact.yml, notify user)
- Task SOP → 🟢 AUTO (update Task_Registry)
- SOUL.md change → 🔒 LOCKED (requires approval)

### Commit

Record the evolution:
```jsonl
{"date":"2025-01-15","type":"evolution","title":"Added JSON safety rule","content":"After 3 config corruptions, added rule: always use json.load/modify/dump","tags":["evolution","rules"]}
```

---

## Heartbeat Mechanism

A periodic self-check that keeps the agent healthy:

### What to Check

```markdown
## Heartbeat Checklist

### Inbox
- [ ] Any unprocessed items in _User_Workspace/01_Inbox/?
- [ ] Any items in _Agent_System/01_Inbox/?

### Outbox
- [ ] Any deliverables pending review in 03_Outbox/?
- [ ] Any stale items (>48h without review)?

### Memory
- [ ] Is scratchpad.md stale? (task completed but not cleared)
- [ ] Are there >20 new episodes since last consolidation?
- [ ] Is fact.yml over 200 lines? (needs archiving)
- [ ] Strength pipeline last run < 8 days ago?
- [ ] Any pending principle candidates to review?
- [ ] Retrieval buffer flushed?

### Tasks
- [ ] Any blocked tasks?
- [ ] Any overdue deadlines?
- [ ] Task_Registry up to date?

### System Health
- [ ] Any _DELETE_ files pending review?
- [ ] Any errors in recent logs?
- [ ] Backup current?
```

### Scheduling

| Frequency | Check | Action |
|-----------|-------|--------|
| Every session start | Inbox scan | Process new items |
| Daily | Full heartbeat | Report status |
| Weekly | Consolidation | Synthesize patterns from episodes |
| Monthly | Deep review | Review SOUL.md, clean archives |
| Quarterly | Evolution audit | Full system health assessment |

### Heartbeat Report

```markdown
# Heartbeat Report — 2025-01-15

## Status: 🟢 HEALTHY

### Inbox: 2 items pending
- [x] Research request (processing)
- [ ] New document to categorize

### Memory: OK
- fact.yml: 128 lines (within limits)
- Episodes since last consolidation: 8 (below threshold)
- Scratchpad: clear

### Issues: None

### Suggested Actions:
- Process remaining inbox item
- Schedule weekly consolidation for Sunday
```

---

## Evolution Log

Track how the agent has changed over time:

```markdown
# Evolution Log

| Date | Change | Trigger | Impact |
|------|--------|---------|--------|
| 2025-01-05 | Added JSON safety rule | 3x config corruption | Prevented future config damage |
| 2025-01-10 | Hot/cold memory split | fact.yml reached 574 lines | 76% token reduction |
| 2025-01-15 | Updated communication tone | User feedback | More concise responses |
```

---

## v4: Cognitive Evolution

The v4 memory system adds **automated evolution** through the cognitive layer:

### Strength-Driven Cleanup

Memories with decaying strength signal what's no longer relevant:

```
High strength (>0.8) → Core knowledge, frequently accessed
Mid strength (0.4-0.8) → Useful but aging
Low strength (<0.4) → Candidate for archival or deletion
```

The agent can use strength scores during heartbeat to identify stale knowledge without manual review.

### Principle Extraction

The system automatically proposes rules from recurring patterns:

```
3+ episodes show the same failure pattern
    ↓
extract-principles generates candidate
    ↓
Human reviews and approves (or rejects)
    ↓
Approved principle → promoted to fact.yml rules
```

This closes the R-M-E-C loop automatically: the agent **Reflects** (consolidation), **Mutates** (principle candidate), and waits for human **Evolve** approval before **Committing** to rules.

### Association-Driven Discovery

When the agent queries memories, the association graph surfaces related knowledge:

```
Agent recalls "config corruption"
    ↓
Association graph shows:
  → causal link to "JSON safety rule"
  → similar link to "deployment failure"
  → evolves_into link to "automated validation"
    ↓
Agent gains broader context without manually searching
```

---

## Feedback Loop

Users can trigger evolution explicitly:

```
User: "You've been too verbose lately. Be more concise."
     ↓
Agent reflects: Communication style needs adjustment
     ↓
Agent proposes: "I'll update my SOUL.md communication section"
     ↓
User approves (TRIAGE: 🔒 for SOUL.md)
     ↓
Agent updates SOUL.md + logs in episodic.jsonl + Evolution Log
```

---

## Backup Before Evolution

Before modifying any core file:

1. **Snapshot current state** (especially for SOUL.md, fact.yml)
2. **Make the change**
3. **Verify** — next session, check if the change improved things
4. **Rollback if needed** — restore from snapshot

### Backup Strategy

```bash
# Create timestamped backup
tar -czf backup_YYYYMMDD.tar.gz \
  IDENTITY.md SOUL.md USER.md MEMORY.md \
  memory/fact.yml memory/episodic.jsonl

# Keep last 10 backups, archive older ones
```

---

## Anti-Patterns

| ❌ Don't | ✅ Do Instead |
|----------|--------------|
| Change SOUL.md without logging | Log every identity change in episodic.jsonl |
| Evolve without reflection | Always R before M-E-C |
| Skip heartbeat checks | Automate them on schedule |
| Make sweeping changes at once | Small, incremental mutations |
| Evolve without user awareness | At minimum, 🟡 CONFIRM for any evolution |

---

*Growth is not optional. It's the difference between a tool and a partner.* 🐚
