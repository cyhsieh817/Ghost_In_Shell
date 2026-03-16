# 13 — Agent Orchestration

> One orchestrator, many specialists — the Lane routing pattern.

---

## The Problem

When you have multiple specialized agents (writer, researcher, coder, reviewer...), the orchestrator faces a routing problem:

- **Default self-handle**: LLMs naturally try to do everything themselves
- **Buried dispatch rules**: Rules in external files get lost during context compression
- **Overlapping agents**: Multiple agents can handle the same task (e.g., 4 different code reviewers)
- **No enforcement**: Text-only rules have zero binding force

**Result**: Your specialized agents sit idle while the orchestrator does all the work poorly.

---

## The Solution: Lane Routing

Inspired by the [Sisyphus orchestrator pattern](https://github.com/Yeachan-Heo/oh-my-claude-sisyphus), Ghost In Shell uses a **three-layer enforcement** approach:

```
┌─────────────────────────────────────────────────┐
│              User Prompt Arrives                 │
│         ┌───────────────────────┐               │
│    1.   │  keyword-detector     │  ← Hook layer │
│         │  (auto-injects hint)  │               │
│         └───────────┬───────────┘               │
│                     ▼                           │
│         ┌───────────────────────┐               │
│    2.   │  AGENTS.md            │  ← Always in  │
│         │  (routing table)      │    context     │
│         └───────────┬───────────┘               │
│                     ▼                           │
│         ┌───────────────────────┐               │
│    3.   │  Agent definitions    │  ← Self-aware │
│         │  (NOT responsible)    │    boundaries  │
│         └───────────────────────┘               │
└─────────────────────────────────────────────────┘
```

### Why Three Layers?

| Layer | What It Does | Why It's Needed |
|-------|-------------|-----------------|
| **Hook** | Injects routing hint before LLM processes | Catches the prompt before default behavior kicks in |
| **AGENTS.md** | Permanent routing rules in always-loaded context | Survives context compression, unlike external files |
| **Agent definitions** | Each agent knows what it should NOT do | Prevents scope creep when dispatched |

Any single layer can fail. All three together create reliable routing.

---

## Core Concepts

### 1. Lanes

A **Lane** is a category of work routed to a specific agent or skill:

```
L0: Self-Handle  — trivial tasks, no dispatch needed
L1: Creation     — writing, editing, content
L2: Research     — search, literature, analysis
L3: Analysis     — data, strategy, evaluation
L4: Development  — code, deploy, architecture
L5: Quality      — review, testing, security
L6: [Custom]     — your domain-specific lane
```

**Key rule**: Each lane has **one primary entry point**. No ambiguity.

### 2. Default Delegate

The orchestrator's default should be **delegate**, not self-handle:

```markdown
<!-- In AGENTS.md -->
<delegation_rules>
Default behavior: DELEGATE.
Self-handle ONLY when:
- Single file edit (<10 lines)
- Git operations
- Memory queries
- Quick Q&A

Everything else: route to the matching Lane.
</delegation_rules>
```

This flips the LLM's natural instinct. Instead of "I'll do it unless there's a reason to delegate," it becomes "I'll delegate unless it's trivially simple."

### 3. Keyword Detection

Trigger words map to Lanes:

```markdown
<keyword_detection>
| Keywords | Lane | Agent |
|----------|------|-------|
| write, draft, article, edit | L1 | writer |
| search, find, research, literature | L2 | researcher |
| analyze, compare, evaluate, ROI | L3 | analyst |
| build, deploy, fix, API, bug | L4 | coder |
| review, PR, security, test | L5 | reviewer |
</keyword_detection>
```

### 4. Two-Level Routing

Some Lanes need a second routing decision:

```
L4 (Development) →
  ├─ Simple (<30 lines)     → Self-handle (L0)
  ├─ Medium (feature work)  → coder agent
  ├─ Large (needs planning) → planning skill/workflow
  └─ Architecture question  → architect agent
```

### 5. Skill-Orchestrated Agent Groups

Some agents should **never be dispatched directly**. They're internal workers managed by a skill or workflow:

```markdown
<!-- In AGENTS.md -->
### Never Dispatch Directly
These agents are orchestrated by their parent skill:
- build-agents (5) → managed by /build skill
- review-agents (3) → managed by /review skill
- deploy-agents (2) → managed by /deploy skill
```

This prevents the "46 agents in a flat list" problem.

---

## Setting Up Orchestration

### Step 1: Define Your Lanes

Start with the question: **What types of work does your agent team handle?**

Common patterns:

| Team Type | Typical Lanes |
|-----------|--------------|
| Solo developer | L0 Self, L4 Dev, L5 Quality |
| Research team | L0 Self, L1 Writing, L2 Research, L3 Analysis |
| Full-stack | L0-L5 all active |
| Domain-specific | L0 Self + 2-3 custom lanes |

### Step 2: Create AGENTS.md

Use the template in `_starter_kit/config/AGENTS.md.template`:

```markdown
# AGENTS.md — Orchestration Protocol

<delegation_rules>
Default: DELEGATE. Self-handle only for trivial tasks.
</delegation_rules>

<keyword_detection>
[Your keyword → lane mapping table]
</keyword_detection>

<lane_routing>
[Detailed routing rules for each lane]
</lane_routing>

<agent_catalog>
[Complete list: direct-dispatch vs skill-managed]
</agent_catalog>
```

**Placement**: Same directory as your `CLAUDE.md` or equivalent config file, so it's always loaded.

### Step 3: Enhance Agent Definitions

Each agent definition should include:

```markdown
---
name: writer
description: "Lane 1: Content creation. Triggers: write, draft, article, edit"
model: claude-sonnet-4-6
tools: [Read, Write]
---

<Role>
You are Writer. You create and polish written content.
</Role>

<Not_Responsible_For>
- Code development (→ coder)
- Data analysis (→ analyst)
- Research/search (→ researcher)
</Not_Responsible_For>

<Success_Criteria>
- [What "done" looks like]
</Success_Criteria>

<Investigation_Protocol>
1. [Step-by-step workflow]
</Investigation_Protocol>
```

**Critical fields**:
- `Not_Responsible_For`: Prevents scope creep. Agent knows to bounce tasks back.
- `Success_Criteria`: Agent knows when to stop.
- `Investigation_Protocol`: Agent knows how to work.

### Step 4: Add Keyword Detection Hook (Optional but Recommended)

Create a hook that fires on each user prompt:

```bash
#!/bin/bash
# keyword-detector.sh — UserPromptSubmit hook

PROMPT=$(cat)
MATCHES=""

# Check keywords per lane
if echo "$PROMPT" | grep -qiE 'write|draft|article|edit'; then
  MATCHES="${MATCHES}L1:writer "
fi

if echo "$PROMPT" | grep -qiE 'search|find|research|literature'; then
  MATCHES="${MATCHES}L2:researcher "
fi

# ... more lanes ...

if [ -z "$MATCHES" ]; then
  echo '{"decision":"allow"}'
  exit 0
fi

MSG="Lane detected: ${MATCHES}. Check AGENTS.md routing table."
echo "{\"decision\":\"allow\",\"message\":\"${MSG}\"}"
```

Register in your settings:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [{
          "type": "command",
          "command": "bash /path/to/keyword-detector.sh",
          "timeout": 3
        }]
      }
    ]
  }
}
```

---

## Architecture Patterns

### Pattern A: Hub and Spoke (Recommended for ≤10 agents)

```
         Orchestrator
        /    |    \
    Writer  Coder  Researcher
```

One orchestrator directly dispatches specialized agents. Simple, clear, low latency.

### Pattern B: Lane Orchestrators (For >10 agents)

```
    Main Orchestrator
      /      |      \
  Dev Lead  QA Lead  Research Lead
   /  \      |  \       |
 Coder Test Reviewer  Researcher
       Runner Auditor
```

Each lane has its own coordinator that manages sub-agents. The main orchestrator only talks to lane leads.

### Pattern C: Skill-Wrapped (For plugin-heavy setups)

```
    Main Orchestrator
      /      |      \
  /build   /review  /research
  (skill)  (skill)  (skill)
   /  \      |         |
 Agent  Agent Agent   Agent
```

Skills act as stable entry points. Internal agents can change without affecting the routing table.

---

## Anti-Patterns

### ❌ Flat Agent List

```markdown
# Don't do this
Available agents: writer, researcher, analyst, coder, reviewer,
security-reviewer, test-runner, architect, debugger, explorer,
simplifier, auditor, ...
```

Too many choices = no choice. The orchestrator will self-handle.

### ❌ Rules in External Files

```markdown
# Don't do this
See dispatch-rules.md for agent routing.
```

External files get dropped during context compression. Rules must be in always-loaded files.

### ❌ Generic Agent Descriptions

```markdown
# Don't do this
description: "Handles various development tasks"
```

Vague descriptions don't trigger matching. Include specific keywords and lane assignment.

### ❌ Agents Without Boundaries

```markdown
# Don't do this (no Not_Responsible_For section)
<Role>You are Coder. You write code.</Role>
```

Without explicit boundaries, agents accept any task and become mini-orchestrators.

---

## Comparison with Other Approaches

| Approach | Routing | Enforcement | Complexity |
|----------|---------|-------------|-----------|
| **No orchestration** | Manual ("use agent X") | None | ⭐ |
| **Rules in CLAUDE.md** | Text instructions | Weak (single layer) | ⭐⭐ |
| **Ghost In Shell Lanes** | AGENTS.md + hooks + boundaries | Strong (three layers) | ⭐⭐⭐ |
| **Full Sisyphus** | 4-layer hooks + model routing + deliverable verification | Maximum | ⭐⭐⭐⭐ |

Ghost In Shell Lanes is the sweet spot for most teams — strong enough to work reliably, simple enough to maintain.

---

## Relationship to Other Chapters

| Chapter | Connection |
|---------|-----------|
| [09 Multi-Agent Sync](09_Multi_Agent_Sync.md) | Same agent on multiple devices. This chapter: multiple agents on one device. |
| [05 Task Management](05_Task_Management.md) | TRIAGE classifies tasks. Lanes route them to agents. |
| [06 Security Model](06_Security_Model.md) | `disallowedTools` in agent definitions extends the permission model. |
| [02 Core Identity](02_Core_Identity.md) | Each agent has its own identity (Role), inheriting from the shared SOUL. |

---

*Many threads, one loom. The art is in knowing which thread to pull.* 🐚
