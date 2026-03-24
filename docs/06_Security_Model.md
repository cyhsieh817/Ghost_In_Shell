# 06 — Security Model

> Three permission zones, deletion protection, and core file locking.

---

## Permission Zones

All directories fall into one of three zones:

```
🔴 PROTECTED — Read only. Any modification requires human approval.
🟡 MANAGED   — Create/modify freely. Deletion requires _DELETE_ marking.
🟢 OPEN      — Full access. Agent can read, write, and delete.
```

### Zone Assignment

| Zone | Directories | Rationale |
|------|-------------|-----------|
| 🔴 PROTECTED | `SOUL.md`, `IDENTITY.md`, `USER.md` (workspace root), `26_Security/` | Core identity and security — too critical for unsupervised changes |
| 🟡 MANAGED | `10_Projects/`, `20_Areas/`, `30_Resources/`, `99_System/` | Active workspace — agent needs write access but deletions should be traceable |
| 🟢 OPEN | `01_Inbox/`, `40_Archive/`, Log files | Transient or archival — low risk |

### Example: ACCESS_POLICY.md

```markdown
# Access Policy

## 🔴 PROTECTED (Read-Only)
- Workspace root identity files: `SOUL.md`, `IDENTITY.md`, `USER.md`
- `_Agent_System/20_Areas/26_Security/`

## 🟡 MANAGED (Write with Constraints)
- `_Agent_System/10_Projects/`
- `_Agent_System/20_Areas/` (except 26_Security)
- `_Agent_System/30_Resources/`
- `_Agent_System/99_System/`

## 🟢 OPEN (Full Access)
- `_Agent_System/01_Inbox/`
- `_Agent_System/40_Archive/`
- `_Agent_System/99_System/991_Logs/`
```

---

## Deletion Protection

**Core rule**: `rm` is forbidden. Always use rename-to-mark:

```bash
# ❌ NEVER do this
rm important_file.md

# ✅ Always do this
mv important_file.md _DELETE_important_file.md
```

**Why**:
- Creates a recovery window
- Makes deletions visible in directory listings
- Human reviews `_DELETE_` files and confirms permanent removal
- Maintains audit trail

### Deletion Lifecycle

```
File exists
     ↓
Agent marks: mv file.md _DELETE_file.md
     ↓
Human reviews _DELETE_ files periodically
     ├── Approve → permanently delete
     └── Reject → rename back (remove _DELETE_ prefix)
```

---

## Autonomy Boundaries

Define what the agent can do **without asking**:

### 🟢 Autonomous (Just Do It)

| Action | Examples |
|--------|---------|
| Read any file | Exploring codebase, checking docs |
| Create in Inbox | New notes, incoming items |
| Web search | Research, fact-checking |
| Analysis & summary | Processing data, generating insights |
| Update logs | Learning log, status updates |
| Run safe commands | `ls`, `cat`, `grep`, build/test |

### 🟡 Do Then Report

| Action | Examples |
|--------|---------|
| Create new files in projects | New code files, documentation |
| Modify existing project files | Code changes, doc updates |
| Reorganize files | Moving to better locations |
| Install packages | npm install, pip install |

### 🔴 Ask First

| Action | Examples |
|--------|---------|
| Delete anything | Even with _DELETE_ prefix |
| External communication | Emails, messages, API calls to external services |
| Deploy code | Push to production, publish |
| Modify configurations | System config, environment variables |
| Financial operations | Any monetary transaction |

### ⛔ Never (Even If Asked)

| Action | Why |
|--------|-----|
| Expose sensitive data | Privacy violation |
| Cross-project data leaks | Contamination risk |
| Modify core identity without verification | Identity integrity |
| Permanent deletion without `_DELETE_` step | Data safety |

---

## Core File Locking

Critical files get extra protection:

### Protected Files

```
IDENTITY.md    — Who the agent is
SOUL.md        — How the agent thinks
AGENTS.md      — Collaboration rules
CORE_LOCK.md   — The lock list itself
```

### Protection Mechanism

```
Modification request for locked file
          ↓
Step 1: Confirm intent (ask user to confirm)
          ↓
Step 2: Explain what will change (diff preview)
          ↓
Step 3: Get explicit approval
          ↓
Step 4: (Optional) Verification code for highest-security files
          ↓
Execute change + log in episodic.jsonl
```

### Optional: 2FA Verification

For maximum security, core file changes can require a verification code:

```
Agent: "To modify SOUL.md, please provide the verification code
        I just sent to your notification channel."

[Agent generates 6-digit code → sends via Telegram/Slack/etc.]

User: "482916"

Agent: "Verified. Proceeding with modification."
```

---

## Audit Logging

All significant actions should be logged:

```jsonl
{"date":"2025-01-15","action":"file_create","path":"/projects/alpha/plan.md","triage":"CONFIRM"}
{"date":"2025-01-15","action":"file_delete_mark","path":"/archive/_DELETE_old_draft.md","triage":"ASK","approved":true}
{"date":"2025-01-15","action":"core_modify","path":"/SOUL.md","triage":"LOCKED","verified":true,"change":"Updated communication style"}
```

---

## Security Checklist

When setting up a new agent:

**Basics**:
- [ ] Define permission zones in ACCESS_POLICY.md
- [ ] Define autonomy boundaries in AUTONOMY_POLICY.md
- [ ] List core locked files in CORE_LOCK.md
- [ ] Set up deletion protection rules

**Three-Layer Enforcement** (recommended):
- [ ] Layer 1: Add dangerous commands to `settings.json` → `permissions.deny`
- [ ] Layer 2: Create `~/.claude/hooks/safety-guard.sh` PreToolUse Hook
- [ ] Layer 3: Create `.claude/rules/safety.md` with behavioral guidance
- [ ] Create path-scoped rules for domain-specific workflows (`.claude/rules/`)

**Verification**:
- [ ] Configure notification channel for 🔴/🔒 events (optional)
- [ ] Test: Can agent read 🔴 files? ✅
- [ ] Test: Can agent modify 🔴 files without approval? ❌
- [ ] Test: Does `_DELETE_` prefix work correctly? ✅
- [ ] Test: Does `rm -rf` get blocked by deny list? ✅
- [ ] Test: Does safety Hook intercept `git push --force`? ✅
- [ ] Test: Do path-scoped rules load only for matching files? ✅

---

## Mature Pattern: Distributed Policy

As your agent evolves, standalone policy files (ACCESS_POLICY.md, AUTONOMY_POLICY.md) may become redundant. A mature agent embeds security rules directly in always-loaded files:

| Rule Type | Where to Embed | Example |
|-----------|---------------|---------|
| Absolute prohibitions | SOUL.md | "Never delete without _DELETE_ prefix" |
| Operational rules | fact.yml → rules | "New tool install requires security audit" |
| Delegation boundaries | AGENTS.md | "Lane 5 Quality: security changes → copilot review" |

**Why this is better**: Standalone policy files add token cost and can be dropped during context compression. Rules embedded in SOUL.md and fact.yml are **always in context** — they cannot be forgotten.

**When to keep standalone files**: For complex compliance requirements (e.g., HIPAA, SOC2) where the policy is too large to embed, or when external auditors need a self-contained document.

---

*Trust, but verify. Freedom, but with fences.* 🐚
