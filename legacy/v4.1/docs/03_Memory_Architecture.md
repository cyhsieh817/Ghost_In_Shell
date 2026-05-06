# 03 — Memory Architecture (v4.1)

> Hot/cold layered memory with association graphs, strength decay, principle extraction, and operational extensions.

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
│   Claude Code Auto Memory (Built-in)    │
│  ~/.claude/projects/<id>/memory/        │
│  ┌──────────────────────────────────┐   │
│  │ MEMORY.md  (≤80 lines)           │   │
│  │ Guidance summaries only          │   │
│  │ ⚠️ Must be created manually      │   │
│  └──────────────────────────────────┘   │
│  Independent from @import layer below   │
├─────────────────────────────────────────┤
│        Always Loaded (~500 lines)        │
│  ┌──────────────┐  ┌─────────────────┐  │
│  │ L0 MEMORY.md │  │ L1 fact.yml     │  │
│  │  ~120 lines  │  │  (hot) ~375 ln  │  │
│  │  Index only  │  │  Active facts   │  │
│  └──────────────┘  └─────────────────┘  │
├─────────────────────────────────────────┤
│        Load on Demand                    │
│  ┌──────────────────────────────────┐   │
│  │ L1 fact_tools_archive.yml (cold) │   │
│  │ L1 fact_tools_detail.yml  (cold) │   │
│  │ L1 fact_decisions.yml     (cold) │   │
│  │ L1 episodic.jsonl     (episodes) │   │
│  │ L0.5 scratchpad.md    (scratch)  │   │
│  │ L2 consolidations.jsonl   (meta) │   │
│  └──────────────────────────────────┘   │
├─────────────────────────────────────────┤
│   v4  Cognitive Layer (Background)      │
│  ┌──────────────────────────────────┐   │
│  │ associations.jsonl  (graph)      │   │
│  │ knowledge.jsonl     (extracted)  │   │
│  │ .retrieval_buffer.jsonl (hook)   │   │
│  │ principles_candidates.jsonl      │   │
│  │ .last_strength_run  (marker)     │   │
│  └──────────────────────────────────┘   │
├─────────────────────────────────────────┤
│   v4.1 Operational Extensions           │
│  ┌──────────────────────────────────┐   │
│  │ skill_dispatch.yml    (routing)  │   │
│  │ agent_dispatch_policy.md (agent) │   │
│  │ skills_agents_manifest.json      │   │
│  │ tag_governance.md     (tags)     │   │
│  │ hook_heal_log.jsonl   (healing)  │   │
│  │ memory_manifest.yml   (health)   │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**Result**: ~500 lines loaded per session via `@import` (MEMORY.md + fact.yml), while the cognitive layer works in the background to strengthen useful memories and surface patterns. Cold layers, operational extensions, and episodic history are loaded on demand.

> **Note on fact.yml growth**: As the agent system matures, fact.yml naturally grows beyond the initial 150-line target. The the-upstream-workspace production instance runs ~375 lines with 9 top-level blocks (user, system, rules, sop_dispatch, agent_model_tiers, tools, ycbio_workflow, cross_machine_sync, memory_governance). This is acceptable when the content is structured YAML with clear section boundaries — the key metric is *relevance density*, not raw line count.

> **Important**: The "Always Loaded" layer loads via `@import` in `CLAUDE.md` — it works regardless of whether the Claude Code Auto Memory layer exists. The two layers are fully independent.

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
| L1 Hot | `memory/fact.yml` | Every session (via @import) |
| L1 Cold | `memory/fact_tools_archive.yml` | Evaluating new tools |
| L1 Cold | `memory/fact_tools_detail.yml` | Tool commands/config |
| L1 Cold | `memory/fact_decisions.yml` | Reviewing past decisions |
| L1 Episodes | `memory/episodic.jsonl` | Need past lessons |
| L0.5 Scratch | `memory/scratchpad.md` | During active tasks |
| L2 Meta | `memory/consolidations.jsonl` | Pattern analysis |
| Cognitive | `memory/associations.jsonl` | Graph queries |
| Cognitive | `memory/knowledge.jsonl` | Domain knowledge |
| Cognitive | `memory/principles_candidates.jsonl` | Principle review |
| Ops | `memory/skill_dispatch.yml` | Task start (skill routing) |
| Ops | `memory/memory_manifest.yml` | Health checks |

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
**Size target**: < 150 lines for simple agents; up to ~400 lines acceptable for mature systems with structured sections.
**Format**: YAML (machine-readable, human-editable)

```yaml
# fact.yml — Hot Layer
# Always loaded. Only active, frequently-needed facts.
# Organized into top-level blocks. Each block is independently parseable.

user:                    # Identity, preferences, language rules
  name: "Jane"
  call_as: "Dr. Chen"
  language: "English"
  timezone: "America/New_York"
  preferences:
    communication: ["direct", "concise"]
    tech_stack: ["Python", "React", "PostgreSQL"]
  sensitive_areas: ["patents", "client data"]

system:                  # Agent identity, paths, platform configs
  identity: "Meridian"
  emoji: "🔬"
  paths:
    workspace: "/home/jane/projects/meridian"
    vault: "/home/jane/projects/meridian/vault"

rules:                   # Hard constraints (always enforced)
  - "Always use absolute paths"
  - "Ask before deletion — use _DELETE_ prefix"
  - "Never expose credentials in output"

# --- Optional blocks (add as your system matures) ---

sop_dispatch:            # Keyword → SOP file routing (auto-trigger)
  routes:
    writing:
      triggers: ["write article", "draft"]
      must_read: ["templates/writing_sop.md"]

agent_model_tiers:       # Which model for which subagent
  fixed:
    analyst: "opus"
    explorer: "sonnet"

tools:                   # One-line summaries (details → fact_tools_detail.yml)
  last_updated: "2025-01-15"
  active_tool: "Purpose summary (install path, key flag)"

memory_governance:       # Anti-bloat rules, archive routing, naming
  milestones:
    max_entries: 5
    overflow: "vault/logs/"
  archive:
    naming: "YYYY-MM-DD-topic-slug.md"
    separator: "-"
```

**Design rules**:
- Only **active, frequently-accessed** items
- When something becomes inactive → move to `fact_tools_archive.yml`
- Tool one-liners in hot layer; full configs in `fact_tools_detail.yml`
- Review quarterly; archive stale entries

---

### L1 Cold: fact_tools_archive.yml — Evaluated Tools

**Role**: Tools that were evaluated but not installed (or previously installed and retired).
**Loaded**: Only when evaluating new tools or checking past evaluations.

```yaml
# fact_tools_archive.yml — Cold Layer (Evaluated Tools)
# Load on demand. Previously evaluated items.

archived_tools:
  tool_name:
    evaluated: "2025-01-10"
    verdict: "not installed — needs GPU"
    notes: "Revisit when GPU available"
```

### L1 Cold: fact_tools_detail.yml — Full Tool Configs

**Role**: Complete configuration for active tools (key commands, install steps, features).
**Loaded**: When user asks "how do I use X?" or needs specific tool commands.
**Relationship**: `fact.yml → tools` has one-line summaries; this file has full details.

```yaml
# fact_tools_detail.yml — Cold Layer (Tool Details)
# Each tool entry includes key_commands, features, install notes.

gogcli:
  key_commands:
    - "gog -a user@domain.com drive list"
    - "gog -a user@domain.com gmail search 'subject:report'"
  features: ["Drive CRUD", "Gmail search", "Docs export"]
  install: "npm install -g @nicholasgasior/gog"
```

> **Why two cold layers?** `fact_tools_archive.yml` tracks *rejected* tools (prevents re-evaluation). `fact_tools_detail.yml` holds *active tool details* too verbose for the hot layer. Different access patterns, different files.

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

### Knowledge Extraction (`knowledge.jsonl`)

A structured knowledge base extracted from literature, articles, and research — separate from episodic memory because knowledge is *timeless* while episodes are *time-bound*.

```jsonl
{"id":"know-20250120-001","date":"2025-01-20","title":"NAD+ Biosynthesis Pathway","source":"doi:10.1234/example","author":"Smith et al.","tags":["biochemistry","NAD"],"one_liner":"De novo NAD+ synthesis from tryptophan via the kynurenine pathway","key_insights":["Rate-limiting enzyme: IDO1","Tissue-specific regulation"],"relevance":"drug_target","obsidian_path":"Literature/NAD_Biosynthesis.md"}
```

**When to use**: Domain knowledge that needs to persist beyond a single session — literature summaries, extracted facts, concept definitions.

---

### Association Surfacing (`association_surfacer.py`)

An optional script that materializes the association graph into human-readable documents:

```bash
python3 scripts/association_surfacer.py
# → Generates an Obsidian MOC (Map of Content) with:
#   - Mermaid causal graph
#   - Continuation chains (multi-session threads)
#   - Timeline view
```

This bridges the gap between machine-readable `associations.jsonl` and human-browsable knowledge maps.

---

## v4.1: Operational Extensions

As the agent system matures, certain operational concerns require their own dedicated files. These are **not cognitive memory** — they are configuration and governance layers that inform agent behavior.

### Skill Dispatch (`skill_dispatch.yml`)

Routes user intent to the best available skill, eliminating the need for users to remember slash commands:

```yaml
# skill_dispatch.yml — Keyword → Skill routing
literature_research:
  label: "Literature Research"
  triggers: ["papers", "PubMed", "literature review"]
  primary:
    - literature-search
    - deep-research
  secondary:
    - pubmed-search
    - biorxiv-search
```

**Loaded**: At task start, to match user intent → skill.

### Agent Dispatch Policy (`agent_dispatch_policy.md`)

Defines which subagent handles which type of work:

```markdown
| Scenario | Agent | Model |
|----------|-------|-------|
| Writing | writer | sonnet (upgrade to opus for publication) |
| Research | researcher | sonnet (upgrade to opus for synthesis) |
| Data analysis | analyst | opus |
| Code review | copilot | external CLI |
```

### Skills & Agents Manifest (`skills_agents_manifest.json`)

Canonical inventory of all installed skills and agent configurations. Machine-readable, used by audit scripts to detect drift.

### Tag Governance (`tag_governance.md`)

Rules for consistent tagging across episodic entries, Obsidian notes, and archives. Prevents tag proliferation and ensures searchability.

### Hook Heal Log (`hook_heal_log.jsonl`)

Records self-healing actions taken by the hook integrity system — when a hook fails and is auto-repaired, the action is logged here for audit.

### Memory Manifest (`memory_manifest.yml`)

System health metadata — episodic counts, consolidation history, trigger thresholds, prompt integrity hashes. Used by `memory_validate.py` for consistency checks.

```yaml
version: "3.0"
stats:
  episodic_total: 70
  episodic_active: 62
  episodic_fading: 8
next_consolidation_trigger:
  type: count
  threshold: 5
  last_count: 70
```

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
| New tool installed (summary) | `fact.yml` → `tools` | YAML (one-liner) |
| New tool installed (full config) | `fact_tools_detail.yml` | YAML (commands, features) |
| Tool evaluated, not installed | `fact_tools_archive.yml` | YAML |
| Important decision made | `fact_decisions.yml` | YAML |
| Task failed / succeeded | `episodic.jsonl` | JSONL append |
| Pattern across multiple episodes | `consolidations.jsonl` | JSONL append |
| Memory connection discovered | `associations.jsonl` | JSONL append |
| Domain knowledge extracted | `knowledge.jsonl` | JSONL append |
| Recurring principle identified | `principles_candidates.jsonl` | JSONL append |
| Hook self-repair action | `hook_heal_log.jsonl` | JSONL append |
| Current task notes | `scratchpad.md` | Markdown |
| Navigation update | `MEMORY.md` | Markdown |
| Skill routing rules | `skill_dispatch.yml` | YAML |
| Agent assignment rules | `agent_dispatch_policy.md` | Markdown |
| Tag naming rules | `tag_governance.md` | Markdown |
| Cross-session guidance summaries | `~/.claude/projects/<id>/memory/MEMORY.md` | Markdown (≤80 lines) |

**Auto Memory routing rules**:
- ✅ Allowed: default output paths, tool selection rules, trigger reminders, feedback index
- ❌ Forbidden: complete memory content (that belongs in workspace layer)

---

## Maintenance Automation

### Auto Session Logging (Wrapper Exit or Native Stop Hook)

When a session ends, the **launcher / hook layer** automatically records what was done:

```
CLI exits through wrapper
  ── or ──
Native Stop event fires
    ↓
memory_session_log.py (async, non-blocking)
    ↓
    1. Resolve runtime profile (`claude-code`, `gemini-cli`, `copilot-cli`, etc.)
    2. git diff --stat HEAD → infer changed files
    3. git ls-files --others → catch untracked new files
    4. Changes ≥ 2 files → append to episodic.jsonl
       (auto-generates id / type / title / importance / runtime / trigger)
    5. Run memory_trigger_check.py → consolidation if threshold met
```

**Why wrapper-first?**

- The model should **not** have to remember to run `memory_runtime.py`
- The model should **not** have to remember to append to `episodic.jsonl`
- The launcher or hook is deterministic; the model is not

**Portable wrapper pattern** (example naming scheme):

```bash
bash scripts/void-claude.sh
bash scripts/void-gemini.sh
bash scripts/void-copilot.sh
bash scripts/void-openclaw.sh
```

These wrappers can:

1. set `VOID_MEMORY_RUNTIME`
2. set `VOID_MEMORY_EXECUTOR`
3. generate a `VOID_MEMORY_SESSION_ID`
4. call `memory_session_log.py` on exit

**Native hook configuration** (example: Claude Code `~/.claude/settings.json`):

```json
{
  "hooks": {
    "Stop": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "python3 /path/to/scripts/memory_session_log.py --runtime claude-code --trigger stop-hook",
        "timeout": 15,
        "async": true
      }]
    }]
  }
}
```

**Shared runtime registry** (recommended):

```yaml
default_executor: claude
default_runtime: claude-code
executors:
  claude: { binary: "claude" }
  gemini: { binary: "gemini" }
  copilot: { binary: "copilot" }
runtimes:
  claude-code: { source: "stop_hook:claude-code" }
  gemini-cli:  { source: "stop_hook:gemini-cli" }
  copilot-cli: { source: "stop_hook:copilot-cli" }
launchers:
  claude:  { runtime: "claude-code", executor: "claude" }
  gemini:  { runtime: "gemini-cli", executor: "gemini" }
  copilot: { runtime: "copilot-cli", executor: "copilot" }
```

**Auto-generated entry schema**:

```jsonl
{"id":"ep-2025-01-20-003","date":"2025-01-20","ts":"2025-01-20T22:04:40+08:00","type":"refactor","title":"Session auto-log: _paths.py, bootstrap.sh, etc. 26 files","content":"Modified 26 files. 26 files changed, 1294 insertions(+), 114 deletions(-)","tags":["scripts","config","runtime:claude-code"],"importance":8,"source":"stop_hook:claude-code","runtime":"claude-code","trigger":"wrapper-exit","session_id":"claude-code-1737381880-1234","decay_status":"active"}
```

**Key details**:
- `source` identifies the runtime source (`stop_hook:claude-code`, `stop_hook:gemini-cli`, etc.)
- `trigger` distinguishes wrapper-exit from native hook entrypoints
- `runtime` makes cross-CLI memory traces searchable later
- `importance` scales with file count: `min(5 + file_count / 3, 8)`
- Type is inferred from changed paths: `scripts/` → refactor, root config files → setup, etc.
- Sessions with < 2 file changes are skipped (avoids trivial records)

### Session End Check
```bash
# Check if memory needs consolidation
python3 scripts/memory_trigger_check.py
```

### Validation

The **memory validator** (`memory_validate.py`) performs 21 checks across structure, integrity, and consistency:

```bash
# Full validation
python3 scripts/memory_validate.py

# Runs as part of daily review
python3 scripts/memory_daily_review_launcher.py
```

**Validation checks**:

| Check | What |
|-------|------|
| V01 | JSON parseable |
| V02 | Schema (required fields, valid types, ID format) |
| V03 | Consolidations JSON parseable |
| V04 | Manifest parseable and version check |
| V05 | Consolidation prompt file exists |
| V06 | ID uniqueness |
| V07 | ID date matches date field |
| V08-V12 | Consolidation reference integrity (xrefs, insights, updates, decay, importance) |
| V13 | Manifest stats match actual episodic counts |
| V14 | No archived entries in active episodic |
| V15 | No high-importance entries in decay candidates |
| V16 | No duplicate consolidations |
| V17 | All `linked_to` references valid |
| V18 | No self-references in cross_references |
| V19 | Trigger config sane (last_count ≤ episodic total) |
| V20 | Core memory paths intact |
| V21 | Last decay run recorded |

**Allowed episode types**: `decision`, `failure`, `milestone`, `insight`, `pitfall`, `bugfix`, `setup`, `integration`, `refactor`, `knowledge_digest`, `discovery`, `architecture`, `deployment`, `security`, `lesson`

**Defensive coding**: All field accesses use `.get()` with defaults — entries with missing fields produce warnings, not crashes.

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
| Every session end | **Auto-log + trigger check** | Wrapper exit or Stop hook → `memory_session_log.py` |
| Daily | Review + validate + flush buffer | `bash scripts/memory_daily_review.sh` |
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

### From v4 → v4.1

1. **Split cold layer** — If you have `fact_archive.yml`, rename to `fact_tools_archive.yml` and create `fact_tools_detail.yml` for active tool configs
2. **Create `knowledge.jsonl`** — Start empty; populate when extracting domain knowledge from literature
3. **Create `memory_manifest.yml`** — Run `memory_validate.py` to auto-generate
4. **Add operational files** (optional) — `skill_dispatch.yml`, `agent_dispatch_policy.md`, `tag_governance.md` as your agent system grows
5. **Deduplicate episodic** — If stop-hooks have created duplicates, merge by title (keep latest `ts`, sum retrieval counts)
6. **Sync consolidation refs** — After dedup, prune orphan episode IDs from `consolidations.jsonl`

---

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Put everything in MEMORY.md | MEMORY.md is an index only |
| Let fact.yml grow without structure | Keep sections as independent YAML blocks; archive stale tools to cold layer |
| Delete old episodes | Append-only; mark resolved with tags |
| Store task-specific notes in fact.yml | Use scratchpad.md |
| Skip consolidation | Weekly review catches patterns |
| Ignore strength decay | Low-strength memories signal cleanup opportunities |
| Auto-approve all principles | Human review prevents bad rules from propagating |
| Manually track memory access | Let the retrieval hook do it transparently |
| Let MEMORY.md header date go stale | Update timestamp whenever milestones are added |
| Hardcode `$HOME` in reference paths | Use `$WORKSPACE/` — MEMORY.md is cross-machine too |
| Assume auto memory directory exists | It must be created manually on each machine; absence doesn't affect @import layer |
| Store complete memory in auto memory layer | Auto memory is summaries only (≤80 lines); formal memory goes in workspace |
| Let stop-hook log every trivial session | Deduplicate by title — identical auto-logged sessions should merge, not accumulate |
| Skip manifest sync after episodic cleanup | Always update `memory_manifest.yml` stats after dedup/cleanup to avoid V13/V19 drift |
| Forget to clean consolidation refs after dedup | Consolidation entries reference episode IDs — when episodes are merged, orphan refs must be pruned |

---

*Less in context. More in memory. Synapses in the void.* 🐚

---

*Last updated: 2026-03-29 — v4.1 (operational extensions, dual cold layer, knowledge graph, 21 validation checks)*
