# Chapter 07 — Brain Regions

Brain regions provide a named routing system for memory access. Rather than loading all
memory files at every session, the agent can selectively activate a region to load only
the files most relevant to the current task.

---

## The Five Fixed Regions

Ghost In Shell v5 defines exactly five fixed regions. All workspaces must use these names;
custom names are coerced to `default` (see [Chapter 10 — Migration](ch.10-migration.md)).

| Region | Analogy | Default files |
|--------|---------|---------------|
| `hippocampus` | Episodic recall | `memory/episodic.jsonl` |
| `prefrontal` | Working context | `memory/fact.yml`, `memory/memory_manifest.yml` |
| `limbic` | Emotional / goal context | _(none by default)_ |
| `cerebellum` | Skills / tools | `memory/runtime_profiles.yml` |
| `default` | Catch-all / unclassified | _(none by default)_ |

---

## `brain_region_manifest.yml` Format

The manifest maps each region to its files. Two file lists per region:

- `core_files` — always loaded when the region is active.
- `on_demand_files` — loaded only when explicitly requested.

```yaml
schema_version: 1
generated_at: "2026-01-01"
regions:
  hippocampus:
    display: "Hippocampus (episodic recall)"
    core_files:
      - path: "memory/episodic.jsonl"
    on_demand_files: []

  prefrontal:
    display: "Prefrontal (working context)"
    core_files:
      - path: "memory/fact.yml"
    on_demand_files:
      - path: "memory/memory_manifest.yml"

  limbic:
    display: "Limbic (emotional / goal context)"
    core_files: []
    on_demand_files: []

  cerebellum:
    display: "Cerebellum (skills / tools)"
    core_files: []
    on_demand_files:
      - path: "memory/runtime_profiles.yml"

  default:
    display: "Default (catch-all)"
    core_files: []
    on_demand_files: []
```

---

## Routing Concept

When a session starts, `MEMORY.md` typically activates the `prefrontal` and `hippocampus`
regions by default. The agent can then request additional regions as the task requires.

Example `MEMORY.md` routing hint:

```markdown
## Memory Index

Active regions: prefrontal, hippocampus

### Prefrontal (working context)
@memory/fact.yml

### Hippocampus (recent episodes)
@memory/episodic.jsonl  <!-- last 20 entries -->
```

For a coding task, the agent might also activate `cerebellum` to load tool profiles:

```
activate_region("cerebellum")
→ loads memory/runtime_profiles.yml
```

---

## Adding Files to a Region

Edit `memory/brain_region_manifest.yml` directly. To add a custom config file to the
`prefrontal` region:

```yaml
prefrontal:
  core_files:
    - path: "memory/fact.yml"
    - path: "memory/my_project_config.yml"  # added
  on_demand_files:
    - path: "memory/memory_manifest.yml"
```

---

## Programmatic Access

```python
from ghost_in_shell.memory.brain_regions import BrainRegionManifest
from ghost_in_shell.memory._paths import WorkspacePaths, resolve_workspace
from pathlib import Path

paths = WorkspacePaths(resolve_workspace(Path("~/my-workspace")))
manifest = BrainRegionManifest(paths)

# Get files for a region
files = manifest.core_files("hippocampus")
print(files)  # [Path("memory/episodic.jsonl")]
```

---

## Region Coercion in Migration

If a v4 workspace contains non-standard region names, `gish migrate v4` will coerce them
to `default`. For example:

- `working_memory` → `default`
- `long_term` → `default`
- `scratchpad` → `default`

Files assigned to the coerced region are merged into the `default` region's file lists.
See [Chapter 10 — Migration](ch.10-migration.md).

---

## Design Rationale

Five regions is a deliberate constraint. Having too many regions creates cognitive overhead
for both the agent (routing decisions) and the developer (manifest maintenance). The fixed
set maps cleanly to how memory access patterns differ in practice:

- **Frequent, small reads** → prefrontal (fact.yml)
- **Narrative lookup** → hippocampus (episodic.jsonl)
- **Tool invocation** → cerebellum (runtime_profiles.yml)
- **Goal / emotional context** → limbic (free-form)
- **Everything else** → default

---

## Next Steps

→ [Chapter 08 — Cron & Hooks](ch.08-cron-hooks.md)
