# 18. Sanctum Governance — Three-tier file protection

> **Sanctum** = "the parts of the workspace where the agent must not improvise".
> The registry declares each protected source, its canonical write CLI, and
> the audit/enforcement tier. Audits run post-hoc; enforcement is opt-in.

---

## Why a registry?

The agent will eventually try to write to files that look "normal" but are
actually load-bearing — `episodic.jsonl`, `fact.yml`, kanban, daily tasks.
A free-form edit may corrupt structure or skip the validation that lives
inside a dedicated CLI.

**The fix**: declare those files in a registry, point each at its canonical
write CLI, and have a script audit recent writes against the registry.

This is not a permission system — it is an **observability + advisory** layer
that surfaces drift. Real friction (PreToolUse blocks, hook denials) is opt-in.

---

## Tier vocabulary

| Tier | Meaning | Enforcement today |
|------|---------|-------------------|
| `core` | Highest priority. Future C-layer guarded — direct writes will be friction-blocked. | Audit-only |
| `extended` | Default for protected sources that have a canonical CLI today. | Audit-only |
| `extended_degraded` | Source has no canonical CLI yet → permanently audit-only. | Audit-only |

The expected lifecycle:

```
extended_degraded   ──[CLI ships]──▶   extended   ──[friction layer ready]──▶   core
```

---

## Registry shape (excerpt)

Lives at `memory/fact_governance.yml` → `sanctum_registry`.

```yaml
sanctum_registry:
  version: 1
  last_updated: "2026-04-26"
  sources:
    - id: episodic
      path: "memory/episodic.jsonl"
      format: jsonl
      tier: core
      lgd_write_cli: "lgd brain:write-episode"

    - id: fact_cold
      path_glob: "memory/fact_*.yml"
      format: yaml
      tier: extended
      lgd_write_cli: null
      exclude: ["memory/fact_governance.yml"]

    - id: scratchpad
      path: "memory/scratchpad.md"
      format: markdown
      tier: extended
      lgd_write_cli: null
      audit_skip_tag: true
```

### Field reference

| Field | Purpose |
|-------|---------|
| `id` | Stable identifier — never rename |
| `path` / `path_glob` | Concrete path or glob (use `path_glob` for fan-out) |
| `format` | `jsonl` / `yaml` / `markdown` / `mixed` |
| `tier` | `core` / `extended` / `extended_degraded` |
| `lgd_write_cli` | Canonical write command, or `null` if none yet |
| `exclude` | Paths within `path_glob` to skip |
| `audit_skip_tag` | If true, omit from frontmatter audit (e.g. scratchpad) |

---

## Audit flow

```
┌─────────────────────────────────────────────────────┐
│ scripts/sanctum_audit.py                            │
│   1. Loads sanctum_registry                         │
│   2. Walks episodic.jsonl + brain_write_log.jsonl   │
│   3. For each write, checks if source_tool matches  │
│      the source's lgd_write_cli                     │
│   4. Emits findings for bypasses                    │
│   5. Exit 0 = clean, Exit 1 = findings              │
└─────────────────────────────────────────────────────┘
```

The portable lite version (in `examples/multi_cli_memory/scripts/`) only
reads the registry; the full reference (the-upstream-workspace's version) also
checks frontmatter, write actor, and last-modified mtime drift.

---

## Adding a new source

1. **Pick a tier.** No CLI yet? → `extended_degraded`. CLI exists? → `extended`.
2. **Append to `sanctum_registry.sources`** with a unique `id`.
3. **Bump `last_updated`.**
4. **Run the audit.** If you see findings, decide: was the bypass intentional
   (stop-gap) or accidental (file the bug)?

```bash
python3 scripts/sanctum_audit.py
```

---

## Open question (deferred)

> Should the C-layer be a hook-level block (PreToolUse) or a wrapper-level
> reject? See the parent project's spec
> `2026-04-24-lgd-skill-trigger-philosophy-design.md` §5.3.

Until that's resolved, all sanctum enforcement is **post-hoc audit**, not
real-time friction.

---

## Reference

- `examples/multi_cli_memory/memory/fact_governance.yml`
- `examples/multi_cli_memory/scripts/sanctum_audit.py`
- `_starter_kit/config/fact_governance.yml.template`
- `docs/17_LGD_Integration.md`
