# 14 — Multi-CLI Orchestration

> Three minds, one mission — the Trident architecture.

---

## The Problem

A single AI CLI has blind spots. The same model reviewing its own code won't catch systematic biases. A text-only model can't process 200-page PDFs efficiently. And no single context window holds everything.

The solution: **orchestrate multiple AI CLIs**, each with different strengths, under one identity.

---

## The Trident Pattern

```
┌─────────────────────────────────────────────┐
│                  User (Human)                │
│                      │                       │
│                      ▼                       │
│            ┌─────────────────┐               │
│            │   Primary CLI   │               │
│            │  (Orchestrator) │               │
│            └───────┬─────────┘               │
│                    │                         │
│          ┌─────────┼──────────┐              │
│          ▼         ▼          ▼              │
│    ┌──────────┐ ┌────────┐ ┌──────────┐     │
│    │ Overflow │ │ Review │ │ Specialist│     │
│    │  CLI     │ │  CLI   │ │   CLI    │     │
│    │ (long    │ │ (cross-│ │ (domain  │     │
│    │ context) │ │ model) │ │ specific)│     │
│    └──────────┘ └────────┘ └──────────┘     │
└─────────────────────────────────────────────┘
```

### Role Definitions

| Role | Purpose | When to Use |
|------|---------|-------------|
| **Primary (Orchestrator)** | Full control, memory, task dispatch | Default — handles everything unless overflow |
| **Overflow** | Ultra-long context, batch processing | Content >10K tokens, multi-document analysis |
| **Reviewer** | Cross-model code review | Post-implementation quality gate |
| **Specialist** | Domain-specific tasks | Platform-specific operations (Google APIs, etc.) |

### Why Multiple CLIs?

| Limitation | Single CLI | Trident |
|-----------|-----------|---------|
| Self-review bias | Same model checks itself | Different model architecture catches different bugs |
| Context overflow | Truncation or compression | Overflow CLI handles long content natively |
| Cost optimization | One model for everything | Match model tier to task complexity |
| Vendor lock-in | One provider | Resilience through diversity |

---

## Architecture

### Identity Sharing

All CLIs share the same identity, but through **role-specific root files**:

| CLI / Role | Root File | Identity Depth |
|------------|-----------|----------------|
| Primary orchestrator | `CLAUDE.md` | Full (SOUL + memory + rules + dispatch) |
| Overflow / long-context | `GEMINI.md` | Just-enough context + language rules |
| Reviewer | `AGENTS.md` / `COPILOT.md` | Read-only review protocol |
| Alternate implementation engine | `CODEX.md` | Focused execution context |
| Local agent / bridge | `OPENCLAW.md` | Local runtime expectations + safety rules |

**Key principle**: the Primary owns the identity. Other CLIs receive **just enough context** to do their job correctly.

> **⚠️ Copilot CLI: Global Config Required**
>
> Unlike Claude Code and Gemini CLI (which read per-project root files), GitHub Copilot CLI loads instructions from global config (`~/.github/copilot/`). For the memory flow to work reliably, Copilot's identity, memory paths, and language rules must be placed in the global config, then reference the project-level `AGENTS.md` from there. Without global setup, Copilot sessions will start without identity or memory context.

### Communication Pattern

```
Primary decides to delegate
  ↓
Primary invokes other CLI via Bash
  ↓
Primary passes: task + relevant context (not full memory)
  ↓
Other CLI executes and returns result
  ↓
Primary interprets result and reports to user
```

Other CLIs never talk to each other. The Primary is always the intermediary.

### Shared Memory Automation

To make this portable across tools, add a thin automation layer:

| File / Layer | Responsibility |
|--------------|----------------|
| `memory/runtime_profiles.yml` | Canonical IDs for runtimes, executors, and launchers |
| `scripts/llm_memory_wrapper.py` | Start a CLI, inject runtime metadata, call session logger on exit |
| `scripts/memory_session_log.py` | Convert session-end changes into `episodic.jsonl` entries |
| `scripts/install_llm_shell_aliases.py` | Optional shell installer for `claude`, `gemini`, `copilot`, `codex`, `openclaw` |

**Why this matters**:

- LLMs are good at reasoning, not at remembering operational hygiene
- the wrapper layer guarantees `runtime`, `session_id`, and `trigger` are captured
- the same memory system can then be shared across Claude / Gemini / Copilot / Codex / OpenClaw without drift

**Reference command surface** (example naming scheme):

```bash
bash scripts/void-claude.sh
bash scripts/void-gemini.sh
bash scripts/void-copilot.sh
bash scripts/void-codex.sh
bash scripts/void-openclaw.sh

# optional shell-level install
python3 scripts/install_llm_shell_aliases.py
```

After shell installation, people can use:

- `claude`, `gemini`, `copilot`, `codex`, `openclaw`
- and keep `claude_native`, `gemini_native`, etc. as escape hatches

Working reference: [`../examples/multi_cli_memory/`](../examples/multi_cli_memory/)

---

## Setting Up Each Role

### Overflow CLI (Long Context)

For processing content that exceeds your primary CLI's practical context:

```bash
# Invocation pattern
overflow-cli -p "Summarize in Traditional Chinese.
Forbidden terms: 软件→軟體, 信息→資訊, 视频→影片.
$(cat <<'EOF'
[long content here]
EOF
)" --output-format text
```

**Agent definition** (for the Primary to wrap):

```markdown
---
name: overflow-handler
description: "Overflow for ultra-long context. Triggers: multi-doc, batch, >10K"
model: [lightweight model]
tools: [Bash]
---

<Role>
You are a lightweight wrapper. Your ONLY job is to invoke the overflow CLI
via Bash and return its output unchanged.
</Role>

<Not_Responsible_For>
- Any task that fits in primary context
- File operations (no Read/Write/Edit)
- Memory updates
</Not_Responsible_For>

<Execution_Protocol>
1. Receive task + content from orchestrator
2. Select model (default vs fast)
3. Assemble prompt with language rules
4. Execute: `overflow-cli -p "..." --output-format text`
5. Return raw output, no post-processing
</Execution_Protocol>
```

### Reviewer CLI (Cross-Model Review)

For catching bugs that your primary model's architecture systematically misses:

```bash
# Invocation pattern
reviewer-cli -p "You are a strict Code Reviewer. Review this diff:
[git diff content]

Focus on:
1. Security vulnerabilities
2. Logic errors
3. Performance issues
4. Language rule compliance
" --model [review-model] --quiet --output-format text
```

**Trigger conditions**:

| Trigger | Required | Model |
|---------|:--------:|-------|
| New feature (>30 lines) | ✅ | Standard |
| Bug fix | ✅ | Standard |
| Security-related changes | ✅ | Premium |
| Config/docs/formatting | ❌ | — |

**Review flow**:

```
Primary completes code → git diff → Reviewer CLI reviews →
  ├─ ✅ LGTM → Report to user, ready to commit
  └─ ❌ Issues → Primary fixes → Re-submit → Until pass
```

**Critical rules**:
- Reviewer is **read-only** — never gives it write access
- On disagreement between Primary and Reviewer → user decides
- Always show user the Reviewer's raw feedback

### Specialist CLI (Domain-Specific)

For tasks that require specific platform access or capabilities:

```
Example specialists:
- Google Workspace CLI (Drive, Gmail, Docs)
- Cloud platform CLI (AWS, GCP, Azure)
- Database CLI (specialized query optimization)
```

These are invoked via the Primary's Bash tool, passing structured prompts.

---

## Model Routing

Match task complexity to model cost:

| Task Type | Model Tier | Examples |
|-----------|-----------|---------|
| Quick lookup, formatting | Economy | Summarize, translate, extract |
| Standard implementation | Standard | Code, write, research |
| Architecture, deep analysis | Premium | Design review, security audit |

**Implementation**: Define model routing in your AGENTS.md:

```markdown
<model_routing>
| Task Complexity | CLI | Model |
|----------------|-----|-------|
| Batch/overflow | Overflow | economy-model |
| Standard work | Primary | standard-model |
| Critical review | Reviewer | premium-model |
</model_routing>
```

---

## Cost Optimization

The Trident pattern naturally optimizes costs:

| Without Trident | With Trident |
|----------------|-------------|
| Premium model for everything | Premium only for architecture/security |
| Long content in expensive context | Overflow CLI uses economy model |
| Self-review (same cost, less value) | Cross-model review (different perspective) |

Typical savings: 30-50% on token costs with better quality output.

---

## Anti-Patterns

### ❌ All CLIs Talk to Each Other

```
CLI-A ↔ CLI-B ↔ CLI-C  (mesh)
```

Creates confusion about who owns state. Always use hub-and-spoke with Primary as hub.

### ❌ Sharing Full Memory with All CLIs

Other CLIs don't need your episodic memory, association graph, or full fact.yml. Pass only what's needed for the specific task.

### ❌ Expecting the Model to Remember Logging

If session-end logging depends on "the model should remember to run a script," it will eventually fail. Put logging in a deterministic wrapper or native hook.

### ❌ Giving Every CLI a Different Memory Write Path

Cross-CLI systems need one canonical log path (`memory/episodic.jsonl`) and one canonical runtime registry. Otherwise the same agent fragments into incompatible histories.

### ❌ Letting Reviewer CLI Modify Files

The Reviewer's value comes from being read-only. The moment it can edit, it becomes another implementation agent, not a reviewer.

### ❌ Using Same Model for Review

Cross-model review catches systematic biases. Same-model review is just expensive self-checking.

---

## Relationship to Other Chapters

| Chapter | Connection |
|---------|-----------|
| [09 Multi-Agent Sync](09_Multi_Agent_Sync.md) | Same agent across devices. This chapter: different AI engines on one device. |
| [13 Agent Orchestration](13_Agent_Orchestration.md) | Lane routing dispatches to agents. This chapter: some agents wrap other CLIs. |
| [06 Security Model](06_Security_Model.md) | Reviewer CLI enforces read-only policy. |

---

*Three edges, one blade. The cut is cleaner when each edge serves its purpose.* 🐚
