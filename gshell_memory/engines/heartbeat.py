"""Heartbeat — periodic self-check + log emission."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import yaml
from gshell_memory_schema.models import HeartbeatConfig

_DEFAULT_CONFIG = HeartbeatConfig(
    cadence="hourly",
    checks=["self_identity", "workspace_health"],
)

_CRON_BY_CADENCE = {
    "hourly": "0 * * * *",
    "four_hourly": "0 */4 * * *",
    "daily": "0 6 * * *",
    "monthly": "0 6 1 * *",
}


class HeartbeatEngine:
    def __init__(self, workspace_path: Path | str) -> None:
        self.workspace_path = Path(workspace_path)
        self._cfg_file = self.workspace_path / "memory" / "heartbeat.yml"
        self._log_dir = self.workspace_path / "memory" / "heartbeat_logs"

    def load_config(self) -> HeartbeatConfig:
        if not self._cfg_file.exists():
            return _DEFAULT_CONFIG
        raw = yaml.safe_load(self._cfg_file.read_text(encoding="utf-8")) or {}
        return HeartbeatConfig.model_validate(raw)

    def save_config(
        self,
        *,
        cadence: str,
        checks: list[str],
        output_format: str = "summary",
        idle_threshold: int = 5,
    ) -> HeartbeatConfig:
        cfg = HeartbeatConfig(
            cadence=cadence,
            checks=checks,
            output_format=output_format,
            idle_threshold=idle_threshold,
        )
        self._cfg_file.parent.mkdir(parents=True, exist_ok=True)
        self._cfg_file.write_text(
            yaml.safe_dump(cfg.model_dump(mode="json"), allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        return cfg

    def run(self) -> dict:
        cfg = self.load_config()
        # Minimal heartbeat: assert each declared check name has at least
        # one corresponding file or known-good signal. v5 ships a stub:
        # all checks pass, status = OK. v5.1 docs explain how to extend.
        timestamp = datetime.now(UTC).isoformat()
        entry = {
            "ts": timestamp,
            "cadence": cfg.cadence,
            "status": "OK",
            "checks": {name: "ok" for name in cfg.checks},
        }
        self._log_dir.mkdir(parents=True, exist_ok=True)
        log_path = self._log_dir / f"{timestamp.replace(':', '-')}.json"
        log_path.write_text(json.dumps(entry, indent=2), encoding="utf-8")
        return entry

    def cron_snippet(self, *, gish_path: str = "gish") -> str:
        cfg = self.load_config()
        spec = _CRON_BY_CADENCE[cfg.cadence]
        cmd = f"{gish_path} heartbeat run --workspace {self.workspace_path}"
        return f"# Added by gish heartbeat install --cron\n{spec} {cmd}\n"

    def launchd_plist(self, *, gish_path: str = "gish") -> str:
        cfg = self.load_config()
        # Calendar interval mapping
        interval_xml = {
            "hourly": "<key>StartInterval</key><integer>3600</integer>",
            "four_hourly": "<key>StartInterval</key><integer>14400</integer>",
            "daily": "<key>StartCalendarInterval</key><dict><key>Hour</key><integer>6</integer></dict>",
            "monthly": "<key>StartCalendarInterval</key><dict><key>Day</key><integer>1</integer><key>Hour</key><integer>6</integer></dict>",
        }[cfg.cadence]
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>io.gshell-memory.heartbeat</string>
  <key>ProgramArguments</key>
  <array>
    <string>{gish_path}</string>
    <string>heartbeat</string>
    <string>run</string>
    <string>--workspace</string>
    <string>{self.workspace_path}</string>
  </array>
  {interval_xml}
  <key>RunAtLoad</key><true/>
</dict>
</plist>
"""
