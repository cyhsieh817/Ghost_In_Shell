# Chapter 06 — Governance & Sanctum

The Sanctum system is Ghost In Shell's access-control layer. It prevents agents from
inadvertently reading, writing, or deleting sensitive memory files without explicit
permission.

---

## Three-Tier Model

Sanctum uses a three-tier classification:

| Tier | Label | Meaning |
|------|-------|---------|
| 1 | `public` | Readable by all agents without restriction |
| 2 | `protected` | Readable, but writes require explicit justification |
| 3 | `private` | Read/write/delete all require explicit clearance |

The tier for each file is declared in `memory/sanctum_registry.yml`.

---

## `sanctum_registry.yml` Format

```yaml
schema_version: 1
entries:
  - path: "memory/fact.yml"
    tier: private
    reason: "Contains personal identity and preferences"
    enforced_actions: [write, delete]

  - path: "memory/episodic.jsonl"
    tier: private
    reason: "Personal episodic memory"
    enforced_actions: [delete]

  - path: "SOUL.md"
    tier: protected
    reason: "Agent persona definition"
    enforced_actions: [write]
```

Fields:

- `path` — workspace-relative path.
- `tier` — `public`, `protected`, or `private`.
- `reason` — human-readable justification (shown in audit output).
- `enforced_actions` — the actions that trigger enforcement: `read`, `write`, `delete`.

---

## Three-Layer Enforcement

Enforcement is applied at three layers:

### Layer 1: Read access

When the agent loads files at session start (via `MEMORY.md` imports), only files at tier
`public` are loaded automatically. Files at `protected` or `private` tiers require the
agent to explicitly request them using the retrieval interface.

### Layer 2: Write access

The `FactStore` and `EpisodicStore` write operations check the sanctum registry before
persisting data. Writes to `private` files are logged to `memory/.fact_audit.jsonl`.

### Layer 3: Delete protection

No engine or CLI command deletes files directly. Deletion is logged as an audit event
and requires a separate confirmation step.

gish follows the rule: **never `rm`; always `mv` to `_DELETE_<filename>`**. This applies
to all file operations in the codebase.

---

## Audit Trail

Every write and delete action against a sanctum-registered file is appended to
`memory/.fact_audit.jsonl`:

```json
{"ts": "2026-01-01T12:00:00Z", "action": "write", "path": "memory/fact.yml", "reason": "session update", "tier": "private"}
```

View the audit trail:

```bash
gish audit --workspace ~/my-workspace
```

Audit output shows tier violations, missing registrations, and recent write events.

---

## Running the Audit Engine

```bash
# CLI
gish audit --workspace ~/my-workspace

# Programmatic
from ghost_in_shell.engines import audit
from pathlib import Path

report = audit.run(Path("~/my-workspace"))
print(report["violations"])   # List of violation dicts
print(report["status"])       # "ok" | "violations_found"
```

---

## Practical Governance Rules

1. **Identity files are private**. `fact.yml`, `episodic.jsonl`, and the identity Trinity
   should always be tier `private`.

2. **Docs and READMEs are public**. Any file an agent needs to read without restriction
   should be tier `public`.

3. **The audit log itself is append-only**. The `gish audit` command reads but never
   modifies `.fact_audit.jsonl`.

4. **Never hardcode credentials**. The sanctum is not a secrets manager. Use environment
   variables or OS keychain for secrets.

---

## Customising the Sanctum

Edit `memory/sanctum_registry.yml` directly. To add a new protected file:

```yaml
entries:
  - path: "memory/my_sensitive_config.yml"
    tier: protected
    reason: "Contains API endpoint configuration"
    enforced_actions: [write, delete]
```

Run `gish audit` after editing to verify the registry is consistent.

---

## Next Steps

→ [Chapter 07 — Brain Regions](ch.07-brain-regions.md)
