# 17. LGD Integration — Pairing with LabGrimoire Desktop

> **Optional layer.** Ghost In Shell works perfectly without LGD. Pair only
> when you want a local LLM, a brain visualizer, and first-class write CLIs
> for your sanctum sources.

---

## What is LabGrimoire Desktop?

LGD is a local-first AI desktop app that ships with:

| Component | Purpose |
|-----------|---------|
| Local model runtime | Run Gemma / Llama / etc. without sending data off-machine |
| Tool registry | A catalog of native tools (file ops, web fetch, code, etc.) |
| Brain visualizer | A UI on top of `memory/brain_region_manifest.yml` |
| Write CLIs | `lgd brain:write-episode`, `lgd kanban:add`, etc. — canonical writers for sanctum sources |
| Workflow runner | Reusable agent workflows defined in TOML |

LGD **reads from the same `memory/` folder** that Ghost In Shell uses. The two
projects share the workspace contract — they don't fight over it.

---

## Pairing in three steps

### 1. Install LGD

```bash
# Replace with the actual install instructions when LGD ships
brew install labgrimoire-desktop   # placeholder
lgd --version                       # confirm CLI on PATH
```

### 2. Drop in `lgd_bridge.py`

The reference is at:

```
examples/multi_cli_memory/scripts/lgd_bridge.py
```

It reads `GHOST_LGD_BIN` (or PATH) to locate the `lgd` binary, builds a
non-interactive call, and writes an audit trail to
`memory/lgd_bridge_log.jsonl`.

```bash
python3 scripts/lgd_bridge.py --check                       # probe
python3 scripts/lgd_bridge.py "Summarize today's session"   # real call
python3 scripts/lgd_bridge.py --model gemma-4-26b "..."     # override model
python3 scripts/lgd_bridge.py --max-turns 20 "long task"
```

If LGD is not installed, the bridge **exits 0** with a stderr hint — calling
code can treat absence as "pairing not configured" without aborting.

### 3. Upgrade your sanctum registry

Open `memory/fact_governance.yml` and replace each `lgd_write_cli: null`
with the canonical CLI command:

```yaml
sanctum_registry:
  sources:
    - id: episodic
      path: "memory/episodic.jsonl"
      tier: core
      lgd_write_cli: "lgd brain:write-episode"   # ← was: null
    - id: kanban
      path: "kanban/CY_Kanban.md"
      tier: extended
      lgd_write_cli: "lgd kanban:add"            # ← was: null
```

After this change, `python3 scripts/sanctum_audit.py` flags any write that
bypasses the canonical CLI. Sources that still have `lgd_write_cli: null`
remain in **`extended_degraded`** mode — they are tracked but not enforced.

---

## What you gain

| Before pairing | After pairing |
|----------------|---------------|
| `lgd_write_cli: null` everywhere | Real CLI commands on each source |
| `sanctum_audit.py` finds nothing to audit | Audit reports bypasses |
| `brain_region_manifest.yml` is informational | LGD's brain visualizer renders it |
| Each CLI runtime calls its own model | LGD adds a local-LLM option for headless calls |

---

## When NOT to pair

- You only run one CLI (Claude Code) and don't need a local LLM.
- You're on a server / headless machine.
- You'd rather not run a desktop app.

The framework is designed so that pairing is **additive**, never required.
The sanctum registry's `extended_degraded` tier exists precisely for this
"degraded but observable" state.

---

## Bidirectional contract

Ghost In Shell promises LGD:

1. `memory/brain_region_manifest.yml` follows the documented schema.
2. `memory/episodic.jsonl` entries always include `id`, `date`, `ts`,
   `runtime`, `source`.
3. The `sanctum_registry` paths are stable across releases.

LGD promises Ghost In Shell:

1. `lgd brain:write-episode` produces a valid `episodic.jsonl` entry.
2. CLI exit codes are non-zero on failure.
3. `lgd --version` is always available for capability detection.

---

## Reference

- `examples/multi_cli_memory/scripts/lgd_bridge.py` — portable bridge
- `examples/multi_cli_memory/memory/fact_governance.yml` — sanctum registry
- `examples/multi_cli_memory/memory/brain_region_manifest.yml` — region map
- `_starter_kit/config/LGD_INTEGRATION.md.template` — generated per-workspace guide
- `docs/18_Sanctum_Governance.md` — registry semantics
- `docs/19_Brain_Region_Memory.md` — region semantics
