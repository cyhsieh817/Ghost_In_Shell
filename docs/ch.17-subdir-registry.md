# Chapter 17 — Memory Subdir Registry

> Stub. Filled out in M6-C.

White-list of permitted subdirectories under memory/. Default enforcement
is warn (report unregistered directories). Block mode raises an error
during enforce().

## CLI

- `gish memory-dir register --path memory/X/ --purpose Y --lifecycle Z`
- `gish memory-dir list`
- `gish memory-dir enforce [--mode warn|block]`
