# Chapter 16 — Brain Region Extensions

## Why this engine exists

The five canonical brain regions — `hippocampus`, `prefrontal`,
`limbic`, `cerebellum`, `default` — were chosen as a forced minimum:
small enough that every workspace must own all five, opinionated enough
that any agent reading any workspace knows where to look first.
But real projects develop genuinely distinct memory shapes — an emotion
log that doesn't fit limbic, a spatial workspace map that doesn't fit
cerebellum — and forcing them into the five defaults muddies the
defaults for everyone.

Region extensions are the negotiated escape valve. The five defaults
stay immutable; projects declare additional named regions under
`extensions:`. The schema is structured so old 5.0 readers can safely
ignore the new block, while 5.1+ readers can opt in and route to it.

Concrete example: a research workspace declares `amygdala` (for
threat-coded notes) and `parietal` (for spatial scratch). Existing
tooling targeting the 5 defaults keeps working unchanged. New tooling
can list `extensions` and route to them deliberately.

## Schema

`BrainRegionExtension` and the extended `BrainRegionManifest` live in
[`gshell_memory_schema/gshell_memory_schema/models.py`](../gshell_memory_schema/gshell_memory_schema/models.py).
The on-disk file is `memory/brain_region_manifest.yml`. From the
v5_full golden fixture, with both `amygdala` and `parietal` declared:

```yaml
schema_version: 1
generated_at: "2026-05-24T00:00:00Z"
regions:
  hippocampus:   { display: "h",  core_files: [], on_demand_files: [] }
  prefrontal:    { display: "p",  core_files: [], on_demand_files: [] }
  limbic:        { display: "l",  core_files: [], on_demand_files: [] }
  cerebellum:    { display: "c",  core_files: [], on_demand_files: [] }
  default:       { display: "d",  core_files: [], on_demand_files: [] }
extensions:
  amygdala:
    display: "a"
    core_files: []
    on_demand_files: []
    aliases: []
  parietal:
    display: "pa"
    core_files: []
    on_demand_files: []
    aliases: []
```

The `regions:` map is locked to exactly the five `REQUIRED_REGIONS`;
attempting to add or remove any of them fails the
`_exactly_five_fixed_regions` validator. The `extensions:` map has no
key constraints.

## CLI walkthrough

```bash
# 1. Declare an extension region (created lazily on first declare)
gish region declare amygdala --display a \
    --on-demand emotion_log.jsonl \
    --workspace ./ws

# 2. Declare a second one with an alias
gish region declare parietal --display pa --aliases spatial \
    --workspace ./ws

# 3. List every region — defaults and extensions side-by-side
gish region list --workspace ./ws
```

## Python API

```python
from pathlib import Path
from gshell_memory.memory.brain_regions import BrainRegionStore

store = BrainRegionStore(Path("./ws"))
store.declare(name="amygdala", display="a",
              core_files=[], on_demand_files=["emotion_log.jsonl"],
              aliases=[])
store.declare(name="parietal", display="pa",
              core_files=[], on_demand_files=[], aliases=["spatial"])
for entry in store.list_all():
    print(entry["name"], entry["kind"], entry.get("display"))
```

## Operational notes

- **5.0 vs 5.1 reader behaviour**: this is the load-bearing
  compatibility split. A 5.0 reader validates only the five required
  regions and treats unknown top-level keys conservatively. A 5.1+
  reader additionally parses `extensions:` and routes lookups through
  them. The schema is forward-compatible by construction: a 5.1 manifest
  on a 5.0 reader still loads (extensions ignored), and a 5.0 manifest
  on a 5.1 reader still loads (extensions empty).
- **File location**: `memory/brain_region_manifest.yml`. Single source
  of truth; agents should not maintain a parallel cache.
- **Failure modes**: declaring an extension that collides with one of
  the five required region names fails the schema validator. Display
  collisions between regions are not enforced — they're a cosmetic
  concern.

## Forward compatibility

- 6.0 may promote selected extensions into the required set, breaking
  5.x ignore-semantics. Promotion path: declare in 5.x, observe usage,
  bake into 6.0 defaults with a migration in `ch.10`.
- 6.0 may add a per-extension `version_introduced` field so dashboards
  can correlate region appearance with schema bumps.
