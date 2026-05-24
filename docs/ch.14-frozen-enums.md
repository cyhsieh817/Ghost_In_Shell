# Chapter 14 — Frozen Enums

> Stub. Filled out in M6-C.

Lock state-machine value sets against silent drift. Once frozen, adding
values requires a major version bump and a spec reference.

## CLI

- `gish enum freeze --name N --value V1 --value V2 --introduced YYYY-MM-DD --layer L`
- `gish enum list`
- `gish enum validate --name N --candidate X`
