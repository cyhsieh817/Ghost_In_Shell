# Chapter 10 — Migration from v4

Ghost In Shell v5 introduces a unified fact store, standardised brain regions, and a
stricter schema for episodic entries. This chapter covers the automated migration path
and manual fallback steps.

---

## What Changed from v4 to v5

| Area | v4.x | v5 |
|------|------|----|
| Fact store | Multiple `fact_*.yml` files | Single `memory/fact.yml` |
| Brain regions | Arbitrary names allowed | 5 fixed names only |
| Episodic fingerprint | Not always present | Required; SHA-256 enforced |
| Archive namespace | Implicit / fragmented | Explicit `archive:` top-level key |
| Schema validation | Optional | Pydantic enforced at append |

---

## Automated Migration: `gish migrate v4`

The `migrate v4` command handles the most common migration scenarios automatically.

### Basic Usage

```bash
gish migrate v4 /path/to/old-workspace /path/to/new-workspace
```

### Dry Run (preview changes without writing)

```bash
gish migrate v4 --dry-run /path/to/old-workspace /path/to/new-workspace
```

### What the Command Does

**Step 1 — Merge fact files**

All `fact*.yml` and `fact_*.yml` files in `old-workspace/memory/` are read and merged
into a single `new-workspace/memory/fact.yml`.

- Keys with an `archive/` prefix → moved under `archive:` namespace.
- Falsy values → moved under `archive:` namespace.
- Existing `archive:` block → merged into the new `archive:` section.

**Step 2 — Migrate episodic.jsonl**

Each episode line is copied. If the `fingerprint` field is missing or incorrect (does not
match `SHA-256(title + "\n" + content + "\n" + YYYY-MM-DD)`), it is recomputed.

**Step 3 — Coerce brain regions**

`brain_region_manifest.yml` is copied. Any region name not in the fixed set
(`hippocampus`, `prefrontal`, `limbic`, `cerebellum`, `default`) is remapped to
`default`. The files assigned to the invalid region are merged into `default`'s file lists.

**Step 4 — Copy optional files**

These files are copied if they exist; skipped gracefully if not:
- `sanctum_registry.yml`
- `associations.jsonl`
- `runtime_profiles.yml`
- `memory_manifest.yml`

**Step 5 — Initialise workspace config**

Creates `new-workspace/.gish/config.yml` if it does not already exist.

**Step 6 — Run doctor**

Runs `gish doctor` on the new workspace and prints the health report.

**Step 7 — Print summary**

```
── Migration summary ──
  Facts merged:     12
  Episodes:         47
  Regions coerced:  2

✓ Migration complete → /path/to/new-workspace
```

---

## Manual Migration Steps

Use manual steps if the automated migration fails or if your v4 layout is unusual.

### 1. Merge fact files manually

```bash
# Collect all fact files
cat old-workspace/memory/fact.yml \
    old-workspace/memory/fact_tools.yml \
    old-workspace/memory/fact_prefs.yml \
    > merged_facts.txt

# Then edit merged_facts.txt to resolve key conflicts
# and save as new-workspace/memory/fact.yml
```

### 2. Recompute fingerprints

```python
import hashlib, json
from pathlib import Path

src = Path("old-workspace/memory/episodic.jsonl")
dst = Path("new-workspace/memory/episodic.jsonl")

lines = []
for raw in src.read_text().splitlines():
    if not raw.strip():
        continue
    entry = json.loads(raw)
    title, content, ts = entry["title"], entry["content"], entry["ts"]
    fp = hashlib.sha256(f"{title}\n{content}\n{ts[:10]}".encode()).hexdigest()
    entry["fingerprint"] = fp
    lines.append(json.dumps(entry))

dst.write_text("\n".join(lines) + "\n")
```

### 3. Fix brain regions

Edit `new-workspace/memory/brain_region_manifest.yml` and rename any non-standard regions
to one of the five valid names:
- `hippocampus`, `prefrontal`, `limbic`, `cerebellum`, `default`

### 4. Validate

```bash
gish doctor --workspace new-workspace
```

Expected output:

```
Status: ok
Episodes: 47  Edges: 0
```

---

## Common Migration Issues

### `fact.yml missing` in doctor output

The fact merge step produced an empty dict. Check whether the old workspace had any
`fact*.yml` files:

```bash
ls old-workspace/memory/fact*.yml
```

If none exist, create a minimal `fact.yml`:

```yaml
identity:
  name: "Migrated Agent"
  language: "en"
archive: {}
```

### Fingerprint mismatch warnings

The `migrate v4` command recomputes all fingerprints. If you are migrating manually and
see fingerprint errors in `gish doctor`, re-run the recompute script above.

### Invalid region names after migration

If `gish doctor` reports a brain region error, check that all region names in
`brain_region_manifest.yml` are in the five valid names. If not, rename them manually.

---

## Post-Migration Checklist

- [ ] `gish doctor --workspace new-workspace` shows `Status: ok`
- [ ] `gish recall --workspace new-workspace "test"` returns results
- [ ] Identity Trinity files (`IDENTITY.md`, `SOUL.md`, `USER.md`) copied or recreated
- [ ] Session hooks updated to point to `new-workspace`
- [ ] Cron schedule updated to use `new-workspace` path
- [ ] Old workspace archived (moved, not deleted)

---

## Next Steps

→ [Chapter 00 — Overview](ch.00-overview.md) (start over)  
→ [Chapter 01 — Quick Start](ch.01-quick-start.md) (set up hooks in new workspace)

---

## Reconnecting custom regions after v4 migration (5.1)

`gish migrate v4` collapses any non-default region into `default`. If you had
custom regions in v4 that you want back (e.g. `amygdala` for security gating,
`parietal` for path management), re-declare them as 5.1 extensions:

```bash
gish region declare amygdala \
    --display "amygdala (security / vigilance)" \
    --on-demand POLICY.md \
    --aliases security \
    --workspace ~/my-workspace

gish region declare parietal \
    --display "parietal (paths / spatial)" \
    --on-demand PATHS.md \
    --workspace ~/my-workspace
```

After declaration, the manifest's `extensions:` block holds these regions.
5.0 readers ignore them gracefully; 5.1+ readers activate them. Files
mistakenly merged into `default` during migration must be moved manually —
gish does not preserve enough history to do this automatically.
