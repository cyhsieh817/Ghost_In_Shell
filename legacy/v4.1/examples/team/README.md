# Team Setup Example

> Multi-agent configuration with shared vault and isolated worker inboxes.

## Architecture

```
shared_vault/                        ← Cloud-synced (iCloud/Dropbox/Git)
├── CLAUDE.md                        ← Shared project rules
├── _Agent_System/
│   ├── 00_Framework/
│   │   └── AGENT_REGISTRY.md        ← All agents listed here
│   ├── 10_Projects/                 ← Shared projects
│   ├── 30_Resources/                ← Shared knowledge base
│   ├── 40_Archive/                  ← Shared archive
│   └── 99_System/
│       ├── 990_POLICY/              ← Shared policies
│       ├── 992_Config/
│       │   ├── bootstrap.sh         ← New machine setup
│       │   ├── agents/              ← Agent definitions (symlinked)
│       │   └── skills/              ← Skills (symlinked)
│       └── 993_Worker_Inbox/        ← ⚡ One per device
│           ├── laptop_alice/
│           ├── desktop_bob/
│           └── cloud_ci/
└── _User_Workspace/
    ├── 01_Inbox/                    ← Tasks for any agent
    └── 03_Outbox/                   ← Deliverables for review
```

## Setup Steps

1. **Create shared vault** in a cloud-synced location
2. **Run starter kit** for the primary agent identity
3. **Create Worker_Inbox/** subdirectory for each device/person
4. **Define AGENT_REGISTRY.md** listing all agents and their roles
5. **Run bootstrap.sh** on each machine
6. **Define coordination rules** (who can modify what)

## Agent Registry Example

```markdown
# Agent Registry

| Agent | Device | Role | Status |
|-------|--------|------|--------|
| Meridian-A | laptop_alice | Research Lead | 🟢 Active |
| Meridian-B | desktop_bob | Development | 🟢 Active |
| Meridian-CI | cloud_ci | Automation | 🟢 Active |
```

## Coordination Rules

- **fact.yml**: Only primary device (laptop_alice) modifies
- **episodic.jsonl**: Any agent can append
- **Project files**: Work in Worker_Inbox, move to shared when done
- **Outbox**: Any agent can deliver; human reviews all

## See Also

- [09 Multi-Agent Sync](../../docs/09_Multi_Agent_Sync.md)
- [10 Cross-Machine Sync](../../docs/10_Cross_Machine_Sync.md)
