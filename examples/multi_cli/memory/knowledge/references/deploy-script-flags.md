---
name: deploy-script-flags
description: Flags the example deploy script accepts, and which one skips the cache purge
metadata:
  type: reference
  updated: 2026-10-01
  expires: 2027-04-01
---

`scripts/deploy.sh --env staging|prod [--no-purge]`. `--no-purge` skips the CDN
purge; use it only for asset-free changes. Re-check this note when the script
changes (see `expires`).
