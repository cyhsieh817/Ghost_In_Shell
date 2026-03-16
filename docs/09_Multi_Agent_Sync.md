# 09 — Multi-Agent Sync

> One brain, multiple bodies — the Horcrux architecture.

---

## The Concept

When you run the same agent on multiple devices (laptop, desktop, cloud), you need:
- **Shared memory** — all instances see the same facts and history
- **No conflicts** — two agents don't overwrite each other's work
- **Clear handoff** — work started on one device can continue on another

Ghost In Shell solves this with the **Horcrux pattern**: one shared Vault, isolated worker inboxes.

---

## Architecture

```
┌──────────────────────────────────────────┐
│            Shared Vault (Cloud)           │
│  ┌────────────────────────────────────┐  │
│  │  _Agent_System/                    │  │
│  │  ├── Shared memory (fact.yml, etc) │  │
│  │  ├── Shared projects               │  │
│  │  └── 99_System/                    │  │
│  │      ├── 993_Worker_Inbox/         │  │
│  │      │   ├── device_a/  ← 🔒      │  │
│  │      │   ├── device_b/  ← 🔒      │  │
│  │      │   └── device_c/  ← 🔒      │  │
│  │      └── 993_Outbox/   ← shared   │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
         ↑            ↑            ↑
    Device A      Device B     Device C
    (laptop)      (desktop)    (cloud)
```

### Key Principle: Partitioned Write, Shared Read

| Operation | Scope |
|-----------|-------|
| **Read** | All agents can read everything |
| **Write (memory)** | Any agent can append to episodic.jsonl |
| **Write (work)** | Each agent writes to its own Worker_Inbox |
| **Write (shared)** | Outbox is shared (deliverables) |

---

## Worker Inbox Pattern

Each device gets its own inbox — a private workspace for in-progress tasks:

```
993_Worker_Inbox/
├── device_laptop_abc123/
│   ├── AGENT.md           ← Device identity
│   ├── current_task.md    ← What this device is working on
│   └── [work in progress files]
│
├── device_desktop_def456/
│   ├── AGENT.md
│   └── [different task files]
```

**Why?**
- No two agents edit the same file simultaneously
- Work-in-progress is isolated until ready
- Completed work moves to shared Outbox

### Device Registration

When a new device joins:

```markdown
# AGENT.md (in Worker_Inbox/device_xxx/)

- Device ID: laptop_abc123
- Registered: 2025-01-15
- Platform: macOS / Linux / Windows
- Agent Version: Ghost In Shell v3
- Status: active
```

---

## Conflict Resolution

### Memory Conflicts

For append-only files (episodic.jsonl, consolidations.jsonl):
- **No conflicts possible** — each agent appends, order doesn't matter

For fact.yml:
- **Last write wins** — cloud sync resolves
- **Mitigation**: Agents should check timestamp before modifying
- **Best practice**: Only one "primary" device modifies fact.yml

### File Conflicts

For project files:
- Worker Inbox prevents conflicts (each device has its own)
- Completed work goes to Outbox → human reviews

---

## Coordination Channels

Agents can coordinate through:

| Method | Use Case | Setup Complexity |
|--------|----------|-----------------|
| Shared `TODO.md` | Task assignment | ⭐ Simple |
| Worker Inbox | Isolation + handoff | ⭐⭐ Medium |
| Notification service (Telegram/Slack) | Real-time alerts | ⭐⭐⭐ Advanced |
| Central orchestrator (OpenClaw) | Full multi-agent ops | ⭐⭐⭐⭐ Complex |

---

## Setting Up Multi-Agent

### Step 1: Choose a Sync Backend

| Backend | Pros | Cons |
|---------|------|------|
| iCloud | Zero setup on Apple devices | macOS/iOS only |
| Dropbox | Cross-platform, reliable | Paid for larger storage |
| Google Drive | Team-friendly, shared drives | Requires gog CLI or API |
| Git repo | Version controlled | Not great for non-code files |

### Step 2: Create Worker Inboxes

```bash
mkdir -p vault/_Agent_System/99_System/993_Worker_Inbox/device_$(hostname)_$(openssl rand -hex 4)
```

### Step 3: Register Each Device

Create `AGENT.md` in each device's Worker_Inbox with device info.

### Step 4: Define Primary Device

Choose one device as "primary" for:
- Modifying fact.yml
- Running consolidation scripts
- Managing core identity files

Other devices are "secondary" — they read shared memory but write only to their Worker_Inbox.

---

## Handoff Protocol

When work needs to move between devices:

```
Device A: Working on task
     ↓
Device A: Saves progress to Worker_Inbox/device_a/
     ↓
Device A: Updates TODO.md: "Task X — ready for handoff"
     ↓
[Cloud sync happens]
     ↓
Device B: Reads TODO.md, picks up task
     ↓
Device B: Reads Device A's Worker_Inbox for context
     ↓
Device B: Continues work in Worker_Inbox/device_b/
```

---

## Different Agent Roles

You can also run **different agents** on different devices:

| Device | Agent Role | Focus |
|--------|-----------|-------|
| Laptop | Research Agent | Literature, web research |
| Desktop | Development Agent | Coding, testing |
| Cloud VM | Automation Agent | Scheduled tasks, monitoring |

Each agent shares the same Vault but has its own IDENTITY.md and SOUL.md appropriate to its role.

---

## Mature Pattern: Role-Based Worker Inboxes

The basic pattern (Chapter 9) uses **device-based** inboxes. A mature system evolves to **role-based** inboxes — each specialized agent gets its own workspace regardless of which device it runs on:

```
993_Worker_Inbox/
├── Writer/
│   ├── Inbox/    ← Tasks for the writing agent
│   └── Outbox/   ← Completed articles
│
├── Researcher/
│   ├── Inbox/    ← Research requests
│   └── Outbox/   ← Research reports
│
├── Analyst/
│   ├── Inbox/    ← Analysis requests
│   └── Outbox/   ← Analysis reports
│
└── Coder/
    ├── Inbox/    ← Development tasks
    └── Outbox/   ← Code deliverables
```

### Why Role-Based > Device-Based

| Aspect | Device-Based | Role-Based |
|--------|-------------|-----------|
| **Organization** | By where work happens | By what work is |
| **Routing** | Manual assignment | Lane system auto-routes |
| **History** | Scattered across devices | Centralized per role |
| **Scaling** | New device = new inbox | New role = new inbox |

### Integration with Lane Routing

When [Agent Orchestration (Chapter 13)](13_Agent_Orchestration.md) dispatches a task to Lane 1 (Creation), the Writer agent knows exactly where to find its pending work and where to deliver results.

### For Multi-CLI Setups

See [Chapter 14: Multi-CLI Orchestration](14_Multi_CLI_Orchestration.md) for how different AI CLIs (not just different devices) coordinate through the same Vault.

---

*One soul, many vessels. All connected through the void.* 🐚
