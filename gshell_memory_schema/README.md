# gshell-memory-schema

Pydantic models + JSON Schema for the gshell-memory workspace file format.

This is a **schema-only** package. It contains no engines, no CLI, no business
logic. Use it when you need to read or write a gshell workspace from your own
code without depending on the full `gshell-memory` framework.

```python
from gshell_memory_schema.models import EpisodicEntry

entry = EpisodicEntry.model_validate(json.loads(line))
```

JSON Schema files live under `gshell_memory_schema/jsonschema/`. They are
auto-generated from the Pydantic models. Rust consumers can drive validation
with `schemars` or `serde_json`.

Versioning follows the workspace `schema_version`. Package version 5.0.x
serves workspace schema 5.0, 5.1.x serves 5.1, etc.
