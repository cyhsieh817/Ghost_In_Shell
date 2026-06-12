# 19. Brain Region Memory — Neuro-anatomical file routing

> A **manifest** that maps each workspace file to a brain region (hippocampus,
> prefrontal, limbic, amygdala, parietal, temporal, occipital). Used by:
>
> - The agent (to load only the region relevant to the current task)
> - The brain visualizer (LGD shows recent activity per region)
> - Audits (to spot files that drift outside their region)

---

## Why a brain metaphor?

Earlier memory generations grouped files by purpose (hot / cold / archive).
That works for storage tier but says nothing about **what cognitive function**
each file serves.

Mapping files to regions makes one thing easy that was hard before: ask
"what does this agent know about emotion?" and the answer is the contents
of the limbic region, not a grep over the entire workspace.

This is a **navigation aid**, not a permission boundary. Files are not
locked to their region.

---

## Region semantics

| Region | Cognitive role | Typical files |
|--------|---------------|---------------|
| **hippocampus** | Encoding, episodic memory | `episodic.jsonl`, `consolidations.jsonl`, `MEMORY.md` |
| **prefrontal** | Execution, planning, tools | `AGENTS.md`, `fact_governance.yml`, skill catalogs |
| **limbic** | Emotion, personality, preferences | `SOUL.md`, `USER.md` |
| **amygdala** | Vigilance, taboos, rules | `ACCESS_POLICY.md`, `AUTONOMY_POLICY.md` |
| **parietal** | Space, paths, structure | `PATHS.md`, project-tree maps |
| **temporal** | Knowledge, semantics | literature DBs, knowledge graphs |
| **occipital** | Visual, image | image manifests, screenshot indices |

Each region has two buckets:

- **`core_files`** — load every session (the region's identity)
- **`on_demand_files`** — load only when the region is "lit up" by a task

---

## Manifest shape

```yaml
schema_version: 1
generated_at: "2026-04-26T00:00:00+08:00"

regions:
  hippocampus:
    display: "Hippocampus — encoding, episodic memory"
    core_files:
      - { path: "MEMORY.md" }
      - { path: "memory/fact.yml" }
      - { path: "memory/episodic.jsonl" }
    on_demand_files:
      - { path: "CLAUDE.md" }
      - { path: "memory/consolidations.jsonl" }

refresh:
  enabled: true
  interval_days: 7
  last_run: null
```

- The manifest is **rebuilt** by `memory_region_manifest_build.py`
  (upstream reference; portable version coming).
- Manual edits live in `brain_region_overrides.yml` so the rebuild
  doesn't clobber them.
- Refresh tick: `bash scripts/memory_region_refresh_tick.sh` (weekly default).

---

## How the agent uses it

1. **Session start.** Load the L0/L1 hot layer (auto via CLAUDE.md).
2. **Task arrives.** Pick the region(s) most relevant to the prompt.
3. **Load `core_files`** for those regions.
4. **Selectively** pull `on_demand_files` as the task evolves.
5. **Skip** unrelated regions to keep context lean.

This is essentially **MOE-style routing for context**: not every file is
relevant to every task. The manifest makes "which files should I look at?"
answerable in O(1) instead of "search the whole workspace."

---

## Pairing with LGD

LGD's brain visualizer is the natural consumer:

- Each region renders as a node sized by `core_files + on_demand_files` count.
- Recent file modifications light up the corresponding region.
- Click a region to see its files in a tree.

Without LGD the manifest is still useful — `memory_region_refresh_tick.sh`
keeps it accurate, and the agent can read it directly.

---

## Migrating an existing workspace

```bash
# 1. Create the seed manifest (the starter kit does this for you)
cp _starter_kit/config/brain_region_manifest.yml.template \
   memory/brain_region_manifest.yml

# 2. Customize the seed for your workspace's specific files

# 3. (Optional) install the rebuild tick if you have the full memory script suite
bash scripts/memory_region_refresh_tick.sh
```

Until you install the rebuild tick, manual edits are fine — the manifest is
just YAML.

---

## Reference

- `examples/multi_cli_memory/memory/brain_region_manifest.yml`
- `_starter_kit/config/brain_region_manifest.yml.template`
- `docs/03_Memory_Architecture.md` (foundation)
- `docs/17_LGD_Integration.md` (pairing)
- `docs/18_Sanctum_Governance.md` (sibling concept)
