# Chapter 12 — Archive Routing

> Stub. Filled out in M6-C.

Decision tree of `condition -> target_dir` mappings, evaluated in priority
order. First match wins.

## CLI

- `gish archive route add --condition X --target-dir Y/ --naming-pattern Z --priority N`
- `gish archive route list`
- `gish archive route preview --input "text"`

## Schema

`ArchiveRoute` in `gshell_memory_schema.models`. Note: 5.x `condition`
matches by literal substring. Glob / regex may land in 6.0.
