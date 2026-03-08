# 04 — Workspace Structure

> PARA meets AI — a dual workspace that keeps agents and humans organized.

---

## The Dual Workspace Model

Ghost In Shell separates the agent's workspace from the human's workspace:

```
Vault/                          ← Root (synced via iCloud/Dropbox/Git)
│
├── _Agent_System/              ← 🤖 Agent's domain
│   ├── 00_Framework/           ← System architecture docs
│   ├── 00_Self_Introduction/   ← Agent identity files
│   ├── 01_Inbox/               ← Agent's incoming items
│   ├── 02_Memory/              ← Extended memory storage
│   ├── 10_Projects/            ← Active project workspaces
│   ├── 20_Areas/               ← Ongoing responsibilities
│   ├── 30_Resources/           ← Knowledge base by domain
│   ├── 31_Assets/              ← Static assets (images, templates)
│   ├── 40_Archive/             ← Completed/inactive items
│   └── 99_System/              ← System config, logs, policies
│       ├── 990_POLICY/         ← Access control, autonomy rules
│       ├── 991_Logs/           ← Learning logs, evolution logs
│       ├── 992_Config/         ← Cross-machine config sync
│       └── 993_Tools/          ← Tool configs and scripts
│
└── _User_Workspace/            ← 👤 Human's domain
    ├── 00_About_Me/            ← User profiles, preferences, habits
    ├── 01_Inbox/               ← Items for agent to process
    ├── 02_Tasks/               ← Active human tasks
    └── 03_Outbox/              ← Agent deliverables for human review
```

---

## Why Two Workspaces?

| Single workspace problems | Dual workspace solution |
|--------------------------|------------------------|
| Agent files mixed with user files | Clear ownership boundaries |
| No review step for agent output | Outbox → human review → finalize |
| Can't tell who created what | Path tells you: `_Agent_System/` vs `_User_Workspace/` |
| Agent accidentally modifies user's work | Permission zones prevent this |

---

## The PARA Method (Adapted for AI)

Ghost In Shell adapts Tiago Forte's PARA method:

| PARA | Ghost In Shell | Purpose |
|------|---------------|---------|
| **P**rojects | `10_Projects/` | Active, goal-driven work with deadlines |
| **A**reas | `20_Areas/` | Ongoing responsibilities (no end date) |
| **R**esources | `30_Resources/` | Reference material by domain |
| **A**rchive | `40_Archive/` | Completed or inactive items |

### 10_Projects/ — Active Projects

```
10_Projects/
├── 101_Project_Alpha/
│   ├── AGENT.md            ← Context for this project
│   ├── PLAN.md             ← Current plan
│   ├── progress.md         ← Status tracking
│   └── [work files]
├── 102_Project_Beta/
└── 103_Project_Gamma/
```

**Rules**:
- Numbered prefix (`101_`, `102_`) for sort order
- Each project gets an `AGENT.md` with project-specific context
- Completed projects → move to `40_Archive/`

### 20_Areas/ — Ongoing Domains

```
20_Areas/
├── 21_Research/
├── 22_Engineering/
├── 23_Marketing/
├── 24_Operations/
└── 26_Security/           ← 🔴 PROTECTED zone
```

### 30_Resources/ — Knowledge Base

```
30_Resources/
├── 301_General/
├── 302_Domain_A/           ← e.g., Biotech Research
│   ├── Knowledge_Digest/   ← Processed knowledge
│   └── Literature/         ← Reference papers
├── 303_Domain_B/           ← e.g., Marketing
├── 305_Tech/
│   └── Research/
└── 309_Templates/          ← Reusable templates
```

### 40_Archive/ — Cold Storage

```
40_Archive/
├── 2025-01_Project_Alpha/
├── 2025-02_Cleanup/
└── [date-prefixed for chronological order]
```

---

## 99_System/ — The Engine Room

```
99_System/
├── 990_POLICY/
│   ├── ACCESS_POLICY.md     ← Permission zones (🔴/🟡/🟢)
│   ├── AUTONOMY_POLICY.md   ← What agent can do without asking
│   └── NAMING_CONVENTION.md ← File/folder naming rules
│
├── 991_Logs/
│   ├── Learning_Log/        ← What the agent learned
│   └── Evolution_Log/       ← Identity/system changes
│
├── 992_Config/
│   ├── bootstrap.sh         ← Cross-machine setup script
│   └── [config templates]
│
└── 993_Tools/
    └── [tool configs, scripts]
```

---

## Deliverable Flow

How work moves from agent to human:

```
Agent creates work
       ↓
_Agent_System/10_Projects/xxx/draft.md    (agent's draft)
       ↓
_User_Workspace/03_Outbox/draft.md        (ready for review)
       ↓
Human reviews & approves
       ↓
Final destination (wherever it belongs)
```

This creates a **review checkpoint** — agents never directly modify the human's workspace without going through Outbox.

---

## AGENT.md — Breadcrumb Files

Every important directory should contain an `AGENT.md` file:

```markdown
# AGENT.md

## Purpose
[What this directory contains and why]

## Contents
[Brief description of key files]

## Rules
[Any directory-specific rules for the agent]
```

**Why**: When the agent enters a new directory, it reads `AGENT.md` first to understand context. Think of it as a "README for AI agents."

---

## Permission Zones

Directories have permission levels (defined in `ACCESS_POLICY.md`):

| Zone | Directories | Agent Can... |
|------|-------------|-------------|
| 🔴 PROTECTED | `00_Self_Introduction/`, `26_Security/` | Read only. Changes need human approval |
| 🟡 MANAGED | `10_Projects/`, `20_Areas/`, `30_Resources/` | Create/modify. Delete = `_DELETE_` prefix |
| 🟢 OPEN | `01_Inbox/`, `40_Archive/`, Logs | Full read/write/delete access |

---

## Setting Up Your Vault

### Minimal (Solo Developer)

```
my_vault/
├── _Agent_System/
│   ├── 10_Projects/
│   ├── 30_Resources/
│   └── 99_System/
│       └── 990_POLICY/
└── _User_Workspace/
    ├── 01_Inbox/
    └── 03_Outbox/
```

### Full (Team/Power User)

Use the complete structure from the starter kit:
```bash
cd starter_kit
python3 create_agent.py
```

---

## Sync Options

| Method | Best For | Notes |
|--------|----------|-------|
| Git | Code-heavy projects | Version controlled, mergeable |
| iCloud/Dropbox | Personal knowledge bases | Automatic, works with Obsidian |
| Google Drive | Team collaboration | Shared drives, access control |
| Local only | Maximum privacy | No sync overhead |

---

*A place for everything, and everything in its place.* 🐚
