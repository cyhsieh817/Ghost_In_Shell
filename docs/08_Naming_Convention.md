# 08 — Naming Convention

> Consistent naming makes everything findable — by humans and agents alike.

---

## Directory Naming

### Depth 1: Top-Level Categories

```
NN_PascalCase
```

| Prefix | Example | Purpose |
|--------|---------|---------|
| `00_` | `00_Framework` | System-level docs |
| `01_` | `01_Inbox` | Incoming items |
| `10_` | `10_Projects` | Active projects |
| `20_` | `20_Areas` | Ongoing responsibilities |
| `30_` | `30_Resources` | Knowledge base |
| `40_` | `40_Archive` | Cold storage |
| `99_` | `99_System` | System internals |

### Depth 2: Sub-Categories

```
NNN_PascalCase_Description
```

Examples:
- `101_Project_Alpha`
- `302_Biotech_Research`
- `991_Logs`

### Depth 3: Fine-Grained

```
NNNN_Description   or   YYYY-MM-DD_Description
```

Examples:
- `3021_Methods`
- `2025-01-15_Sprint_Review`

---

## File Naming

### General Files

```
PascalCase_Description.ext
```

Examples:
- `Project_Plan.md`
- `API_Integration_Guide.md`
- `Meeting_Notes.md`

### Date-Prefixed Files

```
YYYY-MM-DD_Description.ext
```

Use when chronological sorting matters:
- `2025-01-15_Sprint_Review.md`
- `2025-01-10_Bug_Report.md`

### System Files (Fixed Names)

These names are **reserved** and should not be changed:

| File | Purpose |
|------|---------|
| `AGENT.md` | Directory context for the AI agent |
| `README.md` | Human-readable directory description |
| `CLAUDE.md` | Claude Code auto-load configuration |
| `INDEX.md` | Central navigation hub |
| `IDENTITY.md` | Agent identity definition |
| `SOUL.md` | Agent personality & values |
| `USER.md` | User profile & preferences |
| `MEMORY.md` | Memory system index |

---

## Archival Flow

```
Active location
     ↓ (completed or inactive)
40_Archive/YYYY-MM-DD_Description/
     ↓ (marked for deletion)
_DELETE_filename.ext
     ↓ (human approves)
Permanently removed
```

---

## Rules Summary

1. **Directories**: Always numbered prefix (`NN_` or `NNN_`)
2. **Files**: PascalCase or date-prefixed
3. **No spaces in filenames** — use underscores
4. **System files**: Fixed names, never rename
5. **Archive**: Date-prefix the archive folder
6. **Delete**: `_DELETE_` prefix, never `rm`

---

*Names are the first thing an agent reads. Make them count.* 🐚
