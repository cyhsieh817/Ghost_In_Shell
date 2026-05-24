# Chapter 12 — Archive Routing

## Why this engine exists

Every long-lived workspace eventually grows a junk drawer: notes that
should have been filed, drafts that should have been folded into a
project, fragments that ought to be on the cutting-room floor. Ad-hoc
filing decays — two months in, three different agents have invented
three different naming schemes. Archive routing replaces that drift with
a small, ordered decision tree: `(condition, target_dir, naming_pattern)`
triples evaluated in priority order, first match wins.

Concrete example: a research workspace wants every note tagged
`fixture` to land under `_archive/fixture/` with a `YYYY-MM-DD-slug.md`
filename, and everything tagged `legacy` to land under `_archive/legacy/`
as a lower-priority fallback. Both rules are declared once and any agent
or script consults the engine instead of guessing.

## Schema

`ArchiveRoute` is defined in [`gshell_memory_schema/gshell_memory_schema/models.py`](../gshell_memory_schema/gshell_memory_schema/models.py).
The on-disk form is a `routes:` list under `memory/archive_routing.yml`.
From the v5_full golden fixture:

```yaml
routes:
  - condition: "tag:fixture"
    target_dir: "_archive/fixture/"
    naming_pattern: "{date}-{slug}.md"
    frontmatter_required: ["date", "slug"]
    note: "Synthetic archive route A."
    priority: 1
  - condition: "tag:legacy"
    target_dir: "_archive/legacy/"
    naming_pattern: "{date}-{slug}.md"
    frontmatter_required: ["date", "slug"]
    note: "Synthetic archive route B."
    priority: 2
```

`priority` must be `>= 1`; lower numbers win. `condition` is a free-form
string interpreted as a literal substring at the engine layer in 5.x.

## CLI walkthrough

```bash
# 1. Inspect existing routes
gish archive route list --workspace ./ws

# 2. Add a high-priority route for project-X notes
gish archive route add \
    --condition "tag:project-x" --target-dir "_archive/project-x/" \
    --naming-pattern "{date}-{slug}.md" --priority 1 \
    --workspace ./ws

# 3. Dry-run: which route would this candidate hit?
gish archive route preview --input "tag:project-x cleanup notes" \
    --workspace ./ws
```

## Python API

```python
from pathlib import Path
from gshell_memory.engines.archive_router import ArchiveRouter
from gshell_memory_schema.models import ArchiveRoute

router = ArchiveRouter(Path("./ws"))
router.add(ArchiveRoute(
    condition="tag:project-x",
    target_dir="_archive/project-x/",
    naming_pattern="{date}-{slug}.md",
    priority=1,
))
hit = router.preview("tag:project-x cleanup notes")
print(hit.target_dir if hit else "no match")
```

`preview()` returns the first matching `ArchiveRoute` after sorting by
ascending `priority`, or `None` if nothing matches.

## Operational notes

- **File location**: `memory/archive_routing.yml`. Re-sorted on every
  `add()` so the on-disk order always reflects priority.
- **Failure modes**: duplicate `priority` values are permitted in 5.x —
  ties resolve by insertion order. `target_dir` is treated as a path
  hint, not a guarantee; the engine does not create the directory or
  move files itself, leaving that to the caller.
- **Performance**: linear scan. Designed for < 100 routes. Larger rule
  sets should be split per project.

## Forward compatibility

- 6.0 may upgrade `condition` to a discriminated union — `literal | glob
  | regex` — keeping today's strings as the `literal` default.
- 6.0 may also add an optional `move: true` flag that actually performs
  the file move (with safe-rename semantics) rather than just resolving
  the route, closing the gap between preview and execution.
