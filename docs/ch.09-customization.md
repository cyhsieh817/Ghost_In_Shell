# Chapter 09 — Customization

Ghost In Shell is designed to be extended. This chapter covers the two primary extension
points: adding a new CLI adapter and writing a custom engine.

---

## Extending Adapters

### Create a New Adapter

All adapters inherit from `CLIAdapter` in `ghost_in_shell.adapters.base`:

```python
# ghost_in_shell/adapters/my_cli.py
import shutil
from ghost_in_shell.adapters.base import CLIAdapter


class MyCLIAdapter(CLIAdapter):
    name = "my-cli"
    cli_binary = "my-cli"

    def session_start_hook(self) -> str:
        return (
            "# my-cli session-start hook (managed by gish)\n"
            "# Add to your MY_CLI.md:\n"
            "@<workspace>/IDENTITY.md\n"
            "@<workspace>/SOUL.md\n"
            "@<workspace>/USER.md\n"
            "@<workspace>/MEMORY.md\n"
        )

    def session_end_hook(self) -> str:
        return (
            "# Add to your my-cli wrapper exit handler:\n"
            "gish log --from-session\n"
        )

    def root_instruction_template(self) -> str:
        return (
            "# my-cli Root Instruction (managed by gish)\n\n"
            "@<workspace>/IDENTITY.md\n"
            "@<workspace>/SOUL.md\n"
            "@<workspace>/USER.md\n"
            "@<workspace>/MEMORY.md\n\n"
            "## CLI-specific notes\n"
            "- Add any my-cli-specific context here.\n"
        )

    def detect_installation(self) -> bool:
        return shutil.which(self.cli_binary) is not None
```

### Register the Adapter

Edit `ghost_in_shell/adapters/__init__.py` to include your adapter:

```python
from ghost_in_shell.adapters.my_cli import MyCLIAdapter

_ADAPTERS: dict[str, type[CLIAdapter]] = {
    "claude": ClaudeAdapter,
    "gemini": GeminiAdapter,
    "codex": CodexAdapter,
    "copilot": CopilotAdapter,
    "my-cli": MyCLIAdapter,   # added
}
```

After registration, `gish init` will detect your CLI and print hook snippets.

### Testing Your Adapter

```python
from ghost_in_shell.adapters import get_adapter

adapter = get_adapter("my-cli")
assert adapter.name == "my-cli"
assert "@<workspace>/IDENTITY.md" in adapter.session_start_hook()
assert "@<workspace>/IDENTITY.md" in adapter.root_instruction_template()
```

---

## Writing a Custom Engine

Engines are plain Python modules. The only convention is that the primary entry point
is a function named `run(workspace: Path, *, dry_run: bool = False) -> dict`.

### Minimal Custom Engine

```python
# my_engine.py
from __future__ import annotations

from pathlib import Path

from ghost_in_shell.memory._paths import WorkspacePaths, resolve_workspace
from ghost_in_shell.memory._safe_io import read_jsonl


def run(workspace: Path, *, dry_run: bool = False) -> dict:
    """Custom engine: count episodes by tag."""
    paths = WorkspacePaths(resolve_workspace(workspace))

    tag_counts: dict[str, int] = {}
    for entry in read_jsonl(paths.episodic):
        for tag in entry.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    return {
        "tag_counts": tag_counts,
        "total_tags": sum(tag_counts.values()),
        "status": "ok",
    }
```

### Integrating with `run-maintenance`

To include your engine in `gish run-maintenance`, edit
`ghost_in_shell/cli/run.py` to call your engine in the maintenance sequence:

```python
import my_engine

my_engine.run(ws, dry_run=dry_run)
```

### Using `_safe_io` for Writes

All file writes should use the safe I/O helpers to ensure atomicity:

```python
from ghost_in_shell.memory._safe_io import append_jsonl, write_yaml

# Append to a JSONL file (atomic)
append_jsonl(paths.episodic, [{"key": "value"}])

# Write a YAML file (atomic)
write_yaml(paths.fact_yml, {"identity": {"name": "Agent"}})
```

---

## Customising Templates

Templates live in `ghost_in_shell/templates/`. Edit them to change the defaults seeded
by `gish init`:

```
ghost_in_shell/templates/
  identity/
    IDENTITY.md.template
    SOUL.md.template
    config.yml.template
  memory/
    fact.yml.template
    brain_region_manifest.yml.template
    sanctum_registry.yml.template
    runtime_profiles.yml.template
    memory_manifest.yml.template
```

Templates support `{{KEY}}` substitutions. Available substitutions:

| Key | Value |
|-----|-------|
| `{{workspace_name}}` | Basename of the workspace directory |
| `{{workspace_path}}` | Absolute path to the workspace |
| `{{TODAY}}` | ISO date at time of init |
| `{{NAME}}` | Workspace name (same as `workspace_name`) |

---

## Customising Decay Parameters

The decay λ (lambda) rate can be configured in `memory/memory_manifest.yml`:

```yaml
# memory_manifest.yml
decay_config:
  lambda: 0.005          # slower decay (default: 0.01)
  faded_threshold: 0.05  # lower bar for "faded" (default: 0.1)
  retrieval_boost: 0.15  # larger boost per retrieval (default: 0.1)
```

---

## Extending the Brain Region Manifest

Add a new file to an existing region, or extend the `default` region with project-specific
files:

```yaml
regions:
  default:
    display: "Default (catch-all)"
    core_files:
      - path: "memory/project_notes.md"
    on_demand_files:
      - path: "memory/architecture_decisions.md"
```

---

## Next Steps

→ [Chapter 10 — Migration from v4](ch.10-migration.md)
