# Chapter 15 — Heartbeat

## Why this engine exists

A workspace that nobody touches still rots: lockfiles drift, schemas
quietly break, a renamed directory breaks every saved path. Without a
periodic probe, the rot is only discovered the next time something
fails loudly — which is often the worst possible moment. The heartbeat
engine is a deliberately small periodic self-check: it loads its
config, runs each declared check name, writes a timestamped JSON log,
and exits.

Concrete example: a workspace runs `gish heartbeat run` hourly via
cron. Each invocation appends a log line to `memory/heartbeat_logs/`.
A dashboard tails the directory; if no new file appears for two hours,
the host is suspected dead. If a file appears but `status` is not `OK`,
the failing checks are surfaced.

## Schema

`HeartbeatConfig` is defined in [`gshell_memory_schema/gshell_memory_schema/models.py`](../gshell_memory_schema/gshell_memory_schema/models.py).
The on-disk form is a single document at `memory/heartbeat.yml`. From
the v5_full golden fixture:

```yaml
cadence: "hourly"
checks: ["self_identity", "workspace_health"]
output_format: "summary"
idle_threshold: 5
```

- `cadence`: `Literal["hourly", "four_hourly", "daily", "monthly"]`
- `checks`: list of check names (min length 1)
- `output_format`: `Literal["ok_only", "summary", "verbose"]`
- `idle_threshold`: int in `[1, 50]`, hours before "idle" is reported

## CLI walkthrough

```bash
# 1. Run one heartbeat now — emits a log file under memory/heartbeat_logs/
gish heartbeat run --workspace ./ws

# 2. Generate a cron line for the configured cadence
gish heartbeat install --cron --workspace ./ws
# prints, e.g.:  0 * * * * gish heartbeat run --workspace /abs/path/ws

# 3. Or generate a launchd plist suitable for ~/Library/LaunchAgents/
gish heartbeat install --launchd --workspace ./ws > heartbeat.plist
```

The `install` command **prints** the snippet — it does not register it
with cron or launchd. Wiring is left to the operator so the engine
never silently mutates host configuration.

## Python API

```python
from pathlib import Path
from gshell_memory.engines.heartbeat import HeartbeatEngine

hb = HeartbeatEngine(Path("./ws"))
hb.save_config(
    cadence="four_hourly",
    checks=["self_identity", "workspace_health", "lockfile_age"],
    output_format="summary",
    idle_threshold=6,
)
entry = hb.run()
print(entry["status"], entry["checks"])
print(hb.cron_snippet())
```

## Operational notes

- **File locations**: config at `memory/heartbeat.yml`; logs at
  `memory/heartbeat_logs/<ISO-timestamp>.json` (colons in the timestamp
  are replaced with `-` for filesystem safety).
- **Cadence → cron mapping** (canonical):
  `hourly` → `0 * * * *`,
  `four_hourly` → `0 */4 * * *`,
  `daily` → `0 6 * * *`,
  `monthly` → `0 6 1 * *`.
- **5.x check semantics**: every declared check is reported as `ok` —
  the engine ships a stub runner. Real check implementations are
  workspace-specific and slot in by extending the engine. Hard-failing
  a check is intentionally a 5.1+ concern; 5.0 prioritises log
  cadence over check expressiveness.
- **Idle threshold**: surfaced in the config but interpreted by
  downstream dashboards, not by the engine itself.

## Forward compatibility

- 6.0 may add a `register_check(name, callable)` API so each check can
  return its own `ok` / `warn` / `fail` and a payload, replacing the
  current stub-all-ok behaviour.
- 6.0 may add a log retention policy (e.g., keep last N days) — today
  the log directory grows monotonically and is the operator's problem.
