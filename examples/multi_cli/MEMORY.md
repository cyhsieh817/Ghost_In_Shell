# Memory Index

This workspace uses Ghost In Shell 5.2. Every session loads this file in full,
so it holds only trigger phrases and links. Facts and episodes are read on
demand — never `@`-import `episodic.jsonl` here: it grows without limit and
every session would pay for all of it.

## Tier 1 — rules you will not know you are breaking

- "The tool returned success, so it is done" **or the reverse** "it says it failed, retry the same thing" → [verify the final state](memory/knowledge/feedback/verify-final-state.md)
- "Zero errors, so the run was clean" → [zero can mean the stage never ran](memory/knowledge/feedback/zero-may-mean-not-run.md)

## Shelves

- "Which command/flag does the deploy script take" → [tools shelf](memory/knowledge/INDEX_tools.md)

## Memory layers

| Layer | Location | Load when |
|:------|:---------|:----------|
| Knowledge notes | `memory/knowledge/<shelf>/` | an index line above matches the task |
| Facts | `memory/fact.yml` | user preferences / settings needed |
| Episodic | `memory/episodic.jsonl` | `gish recall` for past decisions |

## Commands

```bash
gish recall --workspace . "<query>"         # search episodes
gish knowledge lint --workspace .            # notes, links, orphans
gish index budget --workspace .              # measure this file before adding a line
gish doctor --workspace .                    # health check
```
