# Chapter 18 — LabGrimoire Desktop Bridge

LabGrimoire Desktop (LGD) is a Tauri/Rust desktop application that consumes
gshell-memory workspaces. This chapter documents the contract.

## Architecture

```
┌────────────────────────────────────────┐
│ LabGrimoire Desktop                     │
│   Rust (Tauri)  +  Python (lgd_agent)   │
│                                          │
│   sources.memory.type = "gshell"        │
└──────────────────┬─────────────────────┘
                   │ reads same workspace
                   ▼
┌────────────────────────────────────────┐
│ gshell-memory workspace (filesystem)    │
│   schema 5.1; Pydantic + JSON Schema    │
└──────────────────▲─────────────────────┘
                   │
┌──────────────────┴─────────────────────┐
│ gshell-memory (Python)                  │
│   gish CLI + 14 engines                  │
└────────────────────────────────────────┘
```

Both sides read and write the same workspace directory. Neither side
imports the other's engine code. Schema agreement is enforced through
the shared `gshell-memory-schema` Pydantic + JSON Schema package.

## LGD configuration

In `~/Library/Application Support/labgrimoire/grimoire.toml`:

```toml
[sources.memory]
enabled = true
type = "gshell"
path = "~/my-gshell-workspace"
```

LGD's settings panel surfaces the source type on the Sources page.

## Migration from legacy LGD

Legacy LGD workspaces (`type = "jsonl-graph"`) keep working through one
minor cycle. Run `lgd-agent-migrate <old> <new>` to convert. The migrator
fills SHA-256 fingerprints, writes the 5.1 manifest, and seeds the default
5-region brain region manifest.

## Troubleshooting

- **LGD shows "schema mismatch"**: re-run `pip install -U gshell-memory-schema`
  in the same Python environment that hosts `lgd-agent`.
- **gish doctor reports missing fingerprint after LGD writes**: a legacy
  LGD version may be writing without fingerprints. Update LGD to a build
  that includes the Bridge waves.

## Forward compatibility

When schema bumps to 6.0, expect a `gish migrate v5` command analogous
to the existing `gish migrate v4`. LGD will pin a compatible schema range
in its own release.
