# Chapter 11 — SOP Dispatch

## Why this engine exists

Long-running agents accumulate informal conventions: "before touching the
release pipeline, re-read RELEASE.md"; "any user request mentioning the
mailbox must consult mailbox-policy.md first." These conventions live in
human memory or scattered prompts, and they drift. SOP dispatch records
them as data — a list of `(triggers, must_read)` pairs — so that the agent
can mechanically intercept its own input and surface the right context
before acting.

Concrete example: a project that publishes scientific posts mandates that
any request containing the word "publish" or "release notes" must re-read
the editorial checklist. The SOP engine matches the trigger, returns the
route, and the agent loads the checklist before generating output.

## Schema

`SOPRoute` is defined in [`gshell_memory_schema/gshell_memory_schema/models.py`](../gshell_memory_schema/gshell_memory_schema/models.py).
The on-disk form is a `routes:` list under `memory/sop_dispatch.yml`. From
the v5_full golden fixture:

```yaml
routes:
  - name: "example_route"
    triggers: ["fixture_trigger"]
    must_read: ["docs/example.md"]
    also_read: []
    skills_pipeline: []
    note: "Synthetic SOP route for the v5_full golden fixture."
```

Required fields: `name`, `triggers` (min length 1), `must_read` (min
length 1). Optional: `also_read`, `skills_pipeline`, `note`, `inline_sop`.
Extra keys are rejected (`extra="forbid"`).

## CLI walkthrough

```bash
# 1. Register a new route
gish sop register --name publish_flow \
    --trigger publish --trigger "release notes" \
    --must-read docs/editorial-checklist.md \
    --workspace ./ws

# 2. Confirm it landed
gish sop list --workspace ./ws

# 3. Probe with a user-style input — returns matching routes
gish sop trigger --text "please publish the post" --workspace ./ws

# 4. Run the round-trip test (loads + revalidates every route)
gish sop test --workspace ./ws
```

## Python API

```python
from pathlib import Path
from gshell_memory.engines.sop import SOPEngine
from gshell_memory_schema.models import SOPRoute

engine = SOPEngine(Path("./ws"))
engine.register(SOPRoute(
    name="publish_flow",
    triggers=["publish", "release notes"],
    must_read=["docs/editorial-checklist.md"],
))
matched = engine.trigger("please publish the post")
for r in matched:
    print(r.name, r.must_read)
```

`trigger()` returns every route whose triggers appear as a substring of
the input. Order is preserved from disk.

## Operational notes

- **File location**: `memory/sop_dispatch.yml`. Single file, fully
  rewritten on every `register()` — safe for small N, not designed for
  thousands of routes.
- **Failure modes**: malformed YAML or unknown keys raise on `_read()`;
  the CLI surfaces the Pydantic error and exits non-zero. A registered
  route with zero `triggers` or zero `must_read` is rejected at write
  time.
- **Matching is naive substring**: lower-casing and tokenisation are the
  caller's responsibility. The engine deliberately does not assume any
  natural-language model.

## Forward compatibility

- 6.0 may add `match_mode: literal | glob | regex` per route. Today every
  trigger is a literal substring check; routes that need word boundaries
  must include the surrounding spaces themselves.
- `skills_pipeline` is reserved but unused inside the engine in 5.x; the
  agent layer is expected to consume it. 6.0 may add a driver that
  invokes registered skills directly.
