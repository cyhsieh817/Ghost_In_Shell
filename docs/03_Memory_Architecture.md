# 03 — Memory Architecture (v3)

> Hot/cold layered memory — load less, remember more.

---

## The Problem

AI agents have no persistent memory. Common workarounds:

| Approach | Problem |
|----------|---------|
| Paste everything into system prompt | 🔥 Token bonfire |
| Use a single knowledge file | Grows unbounded, wastes context |
| Rely on conversation history | Lost on new session |
| External vector DB only | Retrieval latency, setup complexity |

## The Solution: Layered Memory

Ghost In Shell uses a **hot/cold separation** strategy inspired by CPU cache hierarchies:

```
┌─────────────────────────────────────────┐
│        Always Loaded (~230 lines)        │
│  ┌──────────────┐  ┌─────────────────┐  │
│  │ L0 MEMORY.md │  │ L1 fact.yml     │  │
│  │  ~100 lines  │  │  (hot) ~130 ln  │  │
│  │  Index only  │  │  Active facts   │  │
│  └──────────────┘  └─────────────────┘  │
├─────────────────────────────────────────┤
│        Load on Demand                    │
│  ┌──────────────────────────────────┐   │
│  │ L1 fact_archive.yml  (cold)      │   │
│  │ L1 fact_decisions.yml (cold)     │   │
│  │ L1 episodic.jsonl    (episodes)  │   │
│  │ L0.5 scratchpad.md   (scratch)   │   │
│  │ L2 consolidations.jsonl (meta)   │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**Result**: Only ~230 lines loaded per session vs 500+ in a single-file approach.

---

## Layer Details

### L0: MEMORY.md — The Index

**Role**: Navigation hub. Always loaded, never stores actual knowledge.
**Size target**: < 200 lines

```markdown
# Memory Index

## Memory Layers

| Layer | File | When to Load |
|-------|------|--------------|
| L1 Hot | `memory/fact.yml` | Every session |
| L1 Cold | `memory/fact_archive.yml` | Evaluating new tools |
| L1 Cold | `memory/fact_decisions.yml` | Reviewing past decisions |
| L1 Episodes | `memory/episodic.jsonl` | Need past lessons |
| L0.5 Scratch | `memory/scratchpad.md` | During active tasks |
| L2 Meta | `memory/consolidations.jsonl` | Pattern analysis |

## Quick Links
- [Key file paths]
- [Active project status]
- [Recent milestones]

## Loading Strategy
1. Start → read this file
2. Need details → load relevant layer
3. Task done → update episodic.jsonl
```

**Key principle**: MEMORY.md is a **router**, not a database.

---

### L1 Hot: fact.yml — Active Facts

**Role**: Structured data the agent needs every session.
**Size target**: < 150 lines
**Format**: YAML (machine-readable, human-editable)

```yaml
# fact.yml — Hot Layer
# Always loaded. Only active, frequently-needed facts.

user:
  name: "Jane"
  call_as: "Dr. Chen"
  language: "English"
  timezone: "America/New_York"
  preferences:
    communication: ["direct", "concise"]
    tech_stack: ["Python", "React", "PostgreSQL"]
  sensitive_areas: ["patents", "client data"]

system:
  identity: "Meridian"
  emoji: "🔬"
  paths:
    workspace: "/home/jane/projects/meridian"
    vault: "/home/jane/projects/meridian/vault"

rules:
  - "Always use absolute paths"
  - "Ask before deletion — use _DELETE_ prefix"
  - "Never expose credentials in output"

tools:
  last_updated: "2025-01-15"
  active_tool_1:
    status: "installed"
    purpose: "..."
  active_tool_2:
    status: "installed"
    purpose: "..."
```

**Design rules**:
- Only **active, frequently-accessed** items
- When something becomes inactive → move to `fact_archive.yml`
- Review quarterly; archive stale entries

---

### L1 Cold: fact_archive.yml — Inactive Facts

**Role**: Historical or evaluated-but-not-active data.
**Loaded**: Only when evaluating new tools or checking past evaluations.

```yaml
# fact_archive.yml — Cold Layer
# Load on demand. Inactive/evaluated items.

archived_tools:
  tool_name:
    evaluated: "2025-01-10"
    verdict: "not installed — needs GPU"
    notes: "Revisit when GPU available"
```

---

### L1 Cold: fact_decisions.yml — Decision Log

**Role**: Historical record of important decisions.
**Loaded**: When reviewing past decisions or checking precedent.

```yaml
# fact_decisions.yml — Decision History

decisions:
  - date: "2025-01-05"
    topic: "Memory architecture"
    decision: "Adopted hot/cold split to reduce token cost"
    rationale: "574 lines → 133 lines, 76% reduction"

  - date: "2025-01-10"
    topic: "Deletion policy"
    decision: "Use _DELETE_ prefix instead of rm"
    rationale: "Allows recovery, prevents accidental data loss"
```

---

### L1: episodic.jsonl — Episodes

**Role**: Time-ordered events — failures, milestones, insights.
**Format**: JSONL (one JSON object per line, append-only)

```jsonl
{"date":"2025-01-05","type":"failure","title":"Config corruption","content":"Used cp instead of json.load/modify/dump, corrupted openclaw.json","tags":["config","critical"]}
{"date":"2025-01-08","type":"milestone","title":"Memory v3 deployed","content":"Hot/cold split reduced token cost by 76%","tags":["memory","optimization"]}
{"date":"2025-01-10","type":"insight","title":"Defense before connection","content":"Always secure the system before adding integrations","tags":["pattern","architecture"]}
```

**Query examples**:
```bash
# Recent failures
grep '"type":"failure"' memory/episodic.jsonl | tail -5

# All insights
grep '"type":"insight"' memory/episodic.jsonl

# Everything tagged "config"
grep '"config"' memory/episodic.jsonl
```

---

### L0.5: scratchpad.md — Working Notes

**Role**: Temporary workspace for the current task.
**Lifecycle**: Created when task starts → distilled to episodic.jsonl when done → cleared.

```markdown
# Scratchpad

## Current Task
[What I'm working on right now]

## Notes
- [Discovery 1]
- [Decision made]
- [Blocked by X]

## TODO
- [ ] Step 1
- [ ] Step 2
```

---

### L2: consolidations.jsonl — Meta-Patterns

**Role**: Periodic synthesis across multiple episodes.
**Created by**: Weekly/monthly review process.

```jsonl
{"date":"2025-01-15","pattern":"Config corruption is the #1 failure mode","evidence":["ep_001","ep_005","ep_012"],"recommendation":"Always use json.load/modify/dump, never cp or echo >"}
{"date":"2025-01-15","pattern":"Defense before connection","evidence":["ep_003","ep_007"],"recommendation":"Secure system first, then add integrations"}
```

---

## Memory Write Routing

When the agent learns something new, it goes to the right layer:

| What | Where | Format |
|------|-------|--------|
| User preference change | `fact.yml` → `user.preferences` | YAML |
| New tool installed | `fact.yml` → `tools` | YAML |
| Tool evaluated, not installed | `fact_archive.yml` | YAML |
| Important decision made | `fact_decisions.yml` | YAML |
| Task failed / succeeded | `episodic.jsonl` | JSONL append |
| Pattern across multiple episodes | `consolidations.jsonl` | JSONL append |
| Current task notes | `scratchpad.md` | Markdown |
| Navigation update | `MEMORY.md` | Markdown |

---

## Maintenance Automation

### Session End Check
```bash
# Check if memory needs consolidation
python3 scripts/memory_trigger_check.py
```

### Weekly Consolidation
```bash
# Synthesize patterns from recent episodes
bash scripts/memory_weekly_consolidate.sh
```

### Memory Health Check
```bash
# Verify all layers are consistent
python3 scripts/memory_status.py
```

---

## Migration from v1/v2

If you're upgrading from a single-file memory system:

1. **Identify hot vs cold** — What do you actually need every session?
2. **Extract hot facts** → `fact.yml` (target: <150 lines)
3. **Archive the rest** → `fact_archive.yml`, `fact_decisions.yml`
4. **Convert event log** → `episodic.jsonl` (one JSON per line)
5. **Create index** → `MEMORY.md` pointing to all layers
6. **Test**: Start a new session, verify agent has full context with only hot layer

---

## Anti-Patterns

| ❌ Don't | ✅ Do Instead |
|----------|--------------|
| Put everything in MEMORY.md | MEMORY.md is an index only |
| Let fact.yml grow beyond 200 lines | Archive inactive items to cold layer |
| Delete old episodes | Append-only; mark resolved with tags |
| Store task-specific notes in fact.yml | Use scratchpad.md |
| Skip consolidation | Weekly review catches patterns |

---

*Less in context. More in memory. Zero in the void.* 🐚
