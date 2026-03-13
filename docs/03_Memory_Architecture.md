# 03 — Memory Architecture (v4)

> Hot/cold layered memory with association graphs, strength decay, and principle extraction.

---

## The Problem

AI agents have no persistent memory. Common workarounds:

| Approach | Problem |
|----------|---------|
| Paste everything into system prompt | Token bonfire |
| Use a single knowledge file | Grows unbounded, wastes context |
| Rely on conversation history | Lost on new session |
| External vector DB only | Retrieval latency, setup complexity |

## The Solution: Layered Memory + Cognitive Engine

Ghost In Shell uses a **hot/cold separation** strategy inspired by CPU cache hierarchies, plus a **cognitive layer** that creates associations, tracks retrieval patterns, and extracts principles.

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
├─────────────────────────────────────────┤
│   v4  Cognitive Layer (Background)      │
│  ┌──────────────────────────────────┐   │
│  │ associations.jsonl  (graph)      │   │
│  │ .retrieval_buffer.jsonl (hook)   │   │
│  │ principles_candidates.jsonl      │   │
│  │ .last_strength_run  (marker)     │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**Result**: Only ~230 lines loaded per session vs 500+ in a single-file approach, while the cognitive layer works in the background to strengthen useful memories and surface patterns.

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
| Cognitive | `memory/associations.jsonl` | Graph queries |
| Cognitive | `memory/principles_candidates.jsonl` | Principle review |

## Quick Links
- [Key file paths]
- [Active project status]
- [Recent milestones]

## Loading Strategy
1. Start → read this file
2. Need details → load relevant layer
3. Task done → update episodic.jsonl
4. Background → association engine runs post-session
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

In v4, each episode gains a `retrieval` field that tracks access patterns:

```jsonl
{"id":"ep-2025-01-05-001","date":"2025-01-05","type":"failure","title":"Config corruption","content":"Used cp instead of json.load/modify/dump, corrupted config","tags":["config","critical"],"importance":9,"retrieval":{"count":3,"last_accessed":"2025-01-20","strength":0.82}}
{"id":"ep-2025-01-08-001","date":"2025-01-08","type":"milestone","title":"Memory v3 deployed","content":"Hot/cold split reduced token cost by 76%","tags":["memory","optimization"],"importance":8,"retrieval":{"count":1,"last_accessed":"2025-01-15","strength":0.65}}
```

**v4 additions to each entry**:
- `id`: Unique identifier (format: `ep-YYYY-MM-DD-NNN`)
- `importance`: 1–10 scale, used in strength computation
- `retrieval.count`: How many times this memory was accessed
- `retrieval.last_accessed`: Date of last access
- `retrieval.strength`: Computed score (0.1–1.0)

**Query examples**:
```bash
# Recent failures
grep '"type":"failure"' memory/episodic.jsonl | tail -5

# All insights
grep '"type":"insight"' memory/episodic.jsonl

# Strongest memories
python3 -c "
import json
entries = [json.loads(l) for l in open('memory/episodic.jsonl')]
top = sorted(entries, key=lambda e: e.get('retrieval',{}).get('strength',0), reverse=True)[:5]
for e in top: print(f'{e[\"id\"]} strength={e.get(\"retrieval\",{}).get(\"strength\",0):.3f} — {e[\"title\"]}')"
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
{"date":"2025-01-15","pattern":"Config corruption is the #1 failure mode","evidence":["ep-2025-01-01-001","ep-2025-01-05-001","ep-2025-01-12-001"],"recommendation":"Always use json.load/modify/dump, never cp or echo >"}
{"date":"2025-01-15","pattern":"Defense before connection","evidence":["ep-2025-01-03-001","ep-2025-01-07-001"],"recommendation":"Secure system first, then add integrations"}
```

---

## v4: Cognitive Layer

The cognitive layer turns passive storage into an active knowledge graph. It runs in the background and does not increase context window cost.

### Association Graph (`associations.jsonl`)

Memories are connected through typed, weighted associations — like synapses between neurons.

```jsonl
{"id":"assoc-20250120-0001","from":"ep-2025-01-05-001","to":"ep-2025-01-12-001","relation":"causal","confidence":0.95,"created_by":"auto","created_at":"2025-01-20","evidence":"tags: config, critical; temporal: 7d apart"}
{"id":"assoc-20250120-0002","from":"ep-2025-01-08-001","to":"ep-2025-01-15-001","relation":"evolves_into","confidence":0.85,"created_by":"consolidation","created_at":"2025-01-20","evidence":"from consolidation 2025-01-15"}
```

**Relation types**:

| Relation | Meaning | Example |
|----------|---------|---------|
| `causal` | A caused or led to B | Failure → Fix |
| `similar` | A and B are alike | Two similar bugs |
| `contradicts` | A conflicts with B | Opposing decisions |
| `evolves_into` | A became B over time | v1 → v2 of a system |
| `supports` | A reinforces B | Evidence for a rule |
| `linked` | General connection | Related topics |
| `continuation` | A continues from B | Multi-session task |
| `conflict` | A and B are in tension | Competing approaches |

**Auto-association**: When a new episode is created, the engine suggests associations based on:
1. **Tag overlap** (Jaccard similarity)
2. **Temporal proximity** (within 3 days = bonus)
3. **Content keyword overlap** (3+ shared meaningful terms)

Suggestions with confidence ≥ 0.7 are auto-adopted. Lower-confidence suggestions are presented for review.

---

### Strength Computation

Every memory has a **strength score** (0.1–1.0) that determines its relevance:

```
strength = base + retrieval_boost + association_boost - decay

where:
  base             = importance / 10
  retrieval_boost  = min(retrieval_count × 0.08, 0.4)
  association_boost = min(association_edges × 0.05, 0.3)
  decay            = weeks_since_last_access × 0.03
```

**How strength is used**:
- High-strength memories surface first in searches
- Low-strength memories are candidates for archival
- Strength naturally decays for unused memories, keeping the system lean

**Example**:
```
Memory: "Config corruption incident"
  importance: 9 → base = 0.9
  retrieved 3 times → boost = 0.24
  4 associations → boost = 0.2
  last accessed 2 weeks ago → decay = 0.06
  strength = 0.9 + 0.24 + 0.2 - 0.06 = 1.0 (capped)
```

---

### Retrieval Tracking

v4 tracks when memories are accessed to feed the strength computation.

**Architecture**:

```
Session: agent reads episodic.jsonl
    ↓
PostToolUse hook detects Read of episodic.jsonl
    ↓
Writes entry IDs to .retrieval_buffer.jsonl
    ↓
Daily review job flushes buffer → updates retrieval counts in episodic.jsonl
    ↓
Strength recomputed
```

The hook-based approach means tracking is transparent — the agent doesn't need to manually log access.

---

### Principle Extraction (`principles_candidates.jsonl`)

The system automatically extracts candidate principles from consolidation patterns:

```jsonl
{"id":"prin-20250120-001","principle":"Config file corruption is the most dangerous failure mode — always use json.load/modify/dump, never direct file writes","evidence":["ep-2025-01-05-001","ep-2025-01-07-001","ep-2025-01-12-001"],"confidence":0.95,"generated_at":"2025-01-15","status":"pending","approved_at":null,"promoted_to":null}
```

**Lifecycle**:

```
Consolidation identifies pattern (3+ evidence entries)
    ↓
extract-principles generates candidate
    ↓
status: "pending" — awaits human review
    ↓
Human approves → status: "approved"
    ↓
Optionally promoted to fact.yml rule
    promoted_to: "rules[5]"
```

**Why human-in-the-loop**: Principles shape agent behavior. Auto-extracting ensures patterns aren't missed; human approval ensures they're correct.

---

### Self-Healing

The cognitive layer monitors its own health:

```bash
# Check if strength pipeline is overdue
python3 scripts/memory_associate.py health
# → [OK] healthy (last run 3d ago)
# → [OVERDUE] strength last ran 12 days ago (threshold: 8)

# Auto catch-up if pipeline missed
python3 scripts/memory_associate.py catchup
# Runs: flush-buffer → strength → absorb-consolidation → extract-principles
```

The daily review job automatically detects if strength hasn't run in >8 days and triggers a catchup.

---

### Horcrux Merge (Multi-Machine)

When running the same agent on multiple machines, associations can be merged:

```bash
python3 scripts/memory_associate.py merge /path/to/remote/associations.jsonl
```

Deduplication rules:
- Same `from` + `to` + `relation` = skip (keep higher confidence)
- Retrieval metadata: take `max(count)`, latest `last_accessed`

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
| Memory connection discovered | `associations.jsonl` | JSONL append |
| Recurring principle identified | `principles_candidates.jsonl` | JSONL append |
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

### Association Engine (v4)
```bash
# Recompute all memory strengths (includes buffer flush)
python3 scripts/memory_associate.py strength

# Suggest associations for a specific memory
python3 scripts/memory_associate.py suggest ep-2025-01-05-001

# Absorb associations from consolidation cross-references
python3 scripts/memory_associate.py absorb-consolidation

# Extract candidate principles from patterns
python3 scripts/memory_associate.py extract-principles

# Full system status
python3 scripts/memory_associate.py status

# Health check & auto-recovery
python3 scripts/memory_associate.py health
python3 scripts/memory_associate.py catchup
```

### Memory Health Check
```bash
# Verify all layers are consistent
python3 scripts/memory_status.py
```

---

## Recommended Automation Schedule

| Frequency | Task | Command |
|-----------|------|---------|
| Every session end | Trigger check | `python3 scripts/memory_trigger_check.py` |
| Daily | Review + flush buffer | `bash scripts/memory_daily_review.sh` |
| Weekly | Consolidation + strength | `bash scripts/memory_weekly_consolidate.sh` |
| Weekly | Extract principles | `python3 scripts/memory_associate.py extract-principles` |
| On demand | Health check | `python3 scripts/memory_associate.py health` |

---

## Migration

### From v1/v2 (Single File → Layered)

1. **Identify hot vs cold** — What do you actually need every session?
2. **Extract hot facts** → `fact.yml` (target: <150 lines)
3. **Archive the rest** → `fact_archive.yml`, `fact_decisions.yml`
4. **Convert event log** → `episodic.jsonl` (one JSON per line)
5. **Create index** → `MEMORY.md` pointing to all layers
6. **Test**: Start a new session, verify agent has full context with only hot layer

### From v3 → v4

1. **Add IDs to episodes** — Each entry needs a unique `id` field (format: `ep-YYYY-MM-DD-NNN`)
2. **Add importance** — Rate each episode 1–10
3. **Initialize retrieval** — Add `"retrieval": {"count": 0, "last_accessed": null, "strength": 0.5}` to each entry
4. **Create `associations.jsonl`** — Start empty; the engine will build associations automatically
5. **Create `principles_candidates.jsonl`** — Start empty
6. **Set up daily review** — Configure a cron/launchd job for `memory_daily_review.sh`
7. **Run initial strength** — `python3 scripts/memory_associate.py strength`

---

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Put everything in MEMORY.md | MEMORY.md is an index only |
| Let fact.yml grow beyond 200 lines | Archive inactive items to cold layer |
| Delete old episodes | Append-only; mark resolved with tags |
| Store task-specific notes in fact.yml | Use scratchpad.md |
| Skip consolidation | Weekly review catches patterns |
| Ignore strength decay | Low-strength memories signal cleanup opportunities |
| Auto-approve all principles | Human review prevents bad rules from propagating |
| Manually track memory access | Let the retrieval hook do it transparently |

---

*Less in context. More in memory. Synapses in the void.* 🐚
