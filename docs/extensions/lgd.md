# LGD Integration (Optional Extension)

Ghost In Shell v5 provides an optional integration path for Lightweight Governance
Definitions (LGD) — a pattern for declaring fine-grained governance rules in a
structured format alongside memory files.

---

## What Is LGD?

LGD is a convention, not a library. It defines a set of YAML files that supplement the
Sanctum registry with more granular access rules:

- **Read policies**: which regions and agents can read each file.
- **Write policies**: conditions under which writes are permitted.
- **Lifecycle policies**: retention periods, archival triggers, and deletion rules.

---

## Enabling LGD in a Workspace

Create `memory/lgd_policy.yml`:

```yaml
schema_version: 1
policies:
  - path: "memory/fact.yml"
    read:
      regions: [prefrontal]
      agents: [all]
    write:
      require_justification: true
      allowed_by: [session_log, manual]
    lifecycle:
      retain_days: null    # never auto-delete
      archive_after_days: 365

  - path: "memory/episodic.jsonl"
    read:
      regions: [hippocampus]
      agents: [all]
    write:
      require_justification: false
      allowed_by: [append_only]
    lifecycle:
      retain_days: 730
      archive_after_days: 365
```

---

## Enforcing LGD Policies

LGD policies are enforced at two levels:

1. **Static enforcement** — `gish audit` reads `lgd_policy.yml` and checks that no
   existing audit log entries violate the declared policies.

2. **Runtime enforcement** — Custom engines or wrapper scripts can call
   `ghost_in_shell.memory.sanctum.check_lgd(path, action)` to validate before acting.

---

## Relationship to the Sanctum

LGD extends the Sanctum (Chapter 06) rather than replacing it. The Sanctum is the
minimum governance layer (always present). LGD adds optional fine-grained control.

| Feature | Sanctum | LGD |
|---------|---------|-----|
| Required | Yes | No |
| Tier model | 3 tiers | Per-file policies |
| Lifecycle rules | No | Yes |
| Region-aware | No | Yes |

---

## Further Reading

- [Chapter 06 — Governance & Sanctum](../ch.06-governance-sanctum.md)
- [Chapter 07 — Brain Regions](../ch.07-brain-regions.md)
- [Chapter 09 — Customization](../ch.09-customization.md)
