# Chapter 16 — Brain Region Extensions

> Stub. Filled out in M6-C.

Default 5 regions (hippocampus / prefrontal / limbic / cerebellum / default)
are immutable in 5.x. Projects with extra needs declare extensions under
`extensions:` in the manifest. Old 5.0 readers ignore extensions; 5.1+
readers activate them.

## CLI

- `gish region declare NAME --display ... --on-demand FILE --aliases ALIAS`
- `gish region list`
