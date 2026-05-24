# Chapter 14 — Frozen Enums

## Why this engine exists

State machines drift silently. A decision-log writer adds `"deferred"`
this week, `"defer"` next week, `"postponed"` the week after. By the
time anyone notices, six months of records have inconsistent vocabulary
and dashboards quietly mis-count. Frozen enums lock the value set as
data: once an enum is declared, only its registered values are legal,
adding a new value requires a major-version bump, and every addition
must reference a spec for the rationale.

Concrete example: the audit layer needs `decision_kind` to be exactly
`{adopt, reject, defer, supersede}`. Anyone trying to write a
seventh kind triggers either an audit warning (soft layer) or a
runtime block (hard layer), depending on `enforcement`.

## Schema

`FrozenEnum` is defined in [`gshell_memory_schema/gshell_memory_schema/models.py`](../gshell_memory_schema/gshell_memory_schema/models.py).
The on-disk form is an `enums:` map under `memory/frozen_enums.yml`,
keyed by enum name. From the v5_full golden fixture, here are the two
canonical examples — one audit-level, one block-level:

```yaml
enums:
  - name: "decision_kind"
    values: ["adopt", "reject", "defer", "supersede"]
    introduced: "5.0"
    layer: "memory"
    enforcement: "audit"
    spec_ref: "spec/m6/frozen_enums.md"
  - name: "rerun_status"
    values: ["pending", "running", "succeeded", "failed", "cancelled"]
    introduced: "5.0"
    layer: "engine"
    enforcement: "block"
    spec_ref: "spec/m6/frozen_enums.md"
```

Pydantic enforces uniqueness on `values` and rejects unknown keys.
`enforcement` is a `Literal["audit", "block"]`.

## CLI walkthrough

```bash
# 1. Freeze a brand-new enum at the engine layer with hard enforcement
gish enum freeze --name task_priority \
    --value low --value normal --value high --value urgent \
    --introduced 5.1 --layer engine --enforcement block \
    --spec-ref spec/m7/task_priority.md \
    --workspace ./ws

# 2. List every frozen enum currently in the workspace
gish enum list --workspace ./ws

# 3. Check whether a candidate value is legal
gish enum validate --name task_priority --candidate "urgent" --workspace ./ws
gish enum validate --name task_priority --candidate "asap"   --workspace ./ws
```

## Python API

```python
from pathlib import Path
from gshell_memory.engines.enum_freeze import FrozenEnumEngine

engine = FrozenEnumEngine(Path("./ws"))
engine.freeze(
    "task_priority",
    ["low", "normal", "high", "urgent"],
    introduced="5.1", layer="engine", enforcement="block",
    spec_ref="spec/m7/task_priority.md",
)
assert engine.validate("task_priority", "urgent") is True
assert engine.validate("task_priority", "asap")   is False
```

The underlying `freeze_helper` (in `gshell_memory_schema.enums`) refuses
to mutate an existing enum's values without an explicit superseding
declaration — this is what guarantees the "once frozen, additions only
on major bump" property.

## Operational notes

- **File location**: `memory/frozen_enums.yml`. Single document holding
  all enums for the workspace.
- **Failure modes**: duplicate `values` are rejected at validation;
  attempting to redefine an existing enum with a different value set
  raises in `freeze_helper`. `validate()` raises `KeyError` if the
  enum name is unknown — the engine deliberately refuses to silently
  return `False` for typos.
- **Two-layer enforcement**: `audit` is advisory; downstream tooling
  may log a warning and continue. `block` is meant to be wired into
  schema validators that hard-fail invalid values.

## Forward compatibility

- 6.0 may add a per-value `deprecated_in` field so enums can carry
  forward "legal but discouraged" values across a deprecation window.
- 6.0 may expose `freeze --supersede <old_name>` for renames, recording
  the lineage so dashboards can stitch old + new histories together.
