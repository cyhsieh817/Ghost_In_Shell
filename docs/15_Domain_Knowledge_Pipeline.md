# 15 — Domain Knowledge Pipeline

> Your agent should know the literature before you ask.

---

## The Problem

AI agents are great at searching the web in real-time, but terrible at:
- Knowing what you've **already read**
- Citing papers from **your own library**
- Searching across **4,000+ papers** with domain-specific filters
- Connecting new findings to **your existing knowledge**

The solution: build a **local knowledge pipeline** that syncs, enriches, and indexes your domain literature.

---

## Architecture

```
┌────────────────────────────────────────────────┐
│           Domain Knowledge Pipeline             │
│                                                │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│  │  Source   │───▶│ Enricher │───▶│   Index  │ │
│  │  (Zotero, │    │ (PMID,   │    │  (CLI    │ │
│  │  Mendeley,│    │  methods,│    │  search) │ │
│  │  BibTeX)  │    │  citekeys│    │          │ │
│  └──────────┘    └──────────┘    └──────────┘ │
│       ↑                               │       │
│       │         ┌──────────┐          ▼       │
│       └─────────│ Scheduler│    Agent uses    │
│                 │ (weekly) │    search CLI    │
│                 └──────────┘                  │
└────────────────────────────────────────────────┘
```

### Three Stages

| Stage | Purpose | Frequency |
|-------|---------|-----------|
| **Sync** | Pull latest from reference manager | Weekly (automated) |
| **Enrich** | Add metadata (PMID, citekey, methods, citations) | After each sync |
| **Search** | Query the indexed library via CLI | On demand |

---

## Stage 1: Sync

Pull your reference library into a format the agent can search.

### Supported Sources

| Source | Method | Notes |
|--------|--------|-------|
| Zotero | Local API (localhost:23119) | Requires Zotero desktop running |
| Mendeley | Export BibTeX periodically | Less real-time |
| BibTeX files | Direct file read | Simplest setup |
| Paperpile | Export JSON/BibTeX | Manual or scheduled |

### Sync Script Pattern

```python
#!/usr/bin/env python3
"""Sync reference library to local searchable format."""

import json
import requests

def sync_from_zotero():
    """Pull all items from Zotero local API."""
    base_url = "http://localhost:23119/api"
    items = requests.get(f"{base_url}/users/0/items",
                         params={"format": "json", "limit": 100}).json()

    records = []
    for item in items:
        data = item.get("data", {})
        records.append({
            "key": data.get("key"),
            "title": data.get("title", ""),
            "creators": data.get("creators", []),
            "date": data.get("date", ""),
            "DOI": data.get("DOI", ""),
            "abstract": data.get("abstractNote", ""),
            "tags": [t["tag"] for t in data.get("tags", [])],
            "itemType": data.get("itemType", ""),
        })

    return records

def save_library(records, path="literature_db.json"):
    with open(path, "w") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"Synced {len(records)} items to {path}")
```

---

## Stage 2: Enrich

Raw bibliographic data is useful but insufficient. Enrichment adds:

| Field | Source | Value |
|-------|--------|-------|
| **PMID** | PubMed API (DOI→PMID lookup) | Unique biomedical identifier |
| **Citekey** | Generated (AuthorYYYY pattern) | Citation shorthand |
| **Methods** | Text analysis of title/abstract | Experiment technique tags |
| **Study type** | Classification rules | in_vivo / in_vitro / clinical / review |
| **Citation count** | CrossRef API | Impact indicator |

### Enrichment Script Pattern

```python
def enrich_record(record):
    """Add PMID, citekey, and method tags to a record."""

    # 1. PMID lookup (with cache)
    if record.get("DOI") and not record.get("PMID"):
        record["PMID"] = lookup_pmid(record["DOI"])

    # 2. Citekey generation
    if not record.get("citekey"):
        first_author = get_first_author_surname(record)
        year = extract_year(record.get("date", ""))
        record["citekey"] = f"{first_author}{year}"

    # 3. Method detection
    text = f"{record.get('title', '')} {record.get('abstract', '')}"
    record["methods"] = detect_methods(text, METHOD_PATTERNS)

    # 4. Study type classification
    record["study_type"] = classify_study_type(text)

    return record

# Method detection patterns
METHOD_PATTERNS = {
    "Western blot": r"[Ww]estern\s*[Bb]lot",
    "ELISA": r"ELISA",
    "qPCR": r"q(?:RT-?)?PCR|real-time PCR",
    "Flow cytometry": r"[Ff]low\s*cytometry|FACS",
    "RNA-seq": r"RNA-?seq|transcriptom",
    "CRISPR": r"CRISPR|Cas[0-9]|guide RNA",
    # Add your domain-specific patterns...
}
```

### PMID Cache

DOI→PMID lookups are slow (API rate limits). Use a persistent cache:

```python
CACHE_PATH = "pmid_cache.json"

def lookup_pmid(doi, cache=None):
    if cache is None:
        cache = load_cache(CACHE_PATH)

    if doi in cache:
        return cache[doi]

    # Query PubMed
    pmid = query_pubmed_by_doi(doi)
    cache[doi] = pmid
    save_cache(CACHE_PATH, cache)
    return pmid
```

---

## Stage 3: Search CLI

The agent needs a fast, flexible way to query the library:

```bash
# Basic search
python3 lit_search.py "NLRP3 inflammasome"

# With filters
python3 lit_search.py "apoptosis" --method "Western blot" --year 2020-
python3 lit_search.py --protein "NLRP3" --type in_vivo

# Citation format
python3 lit_search.py "cancer therapy" --cite --limit 5

# JSON output for agent consumption
python3 lit_search.py "immunotherapy" --json --limit 10

# Validate library health
python3 lit_search.py --validate
```

### Search CLI Design

```python
def search(query, method=None, protein=None, year=None,
           study_type=None, cite=False, json_output=False, limit=20):
    """Search the local literature database."""

    db = load_database()
    results = []

    for record in db:
        score = 0
        text = f"{record['title']} {record.get('abstract', '')}"

        # Text match
        if query and query.lower() in text.lower():
            score += 1

        # Method filter
        if method and method in record.get("methods", []):
            score += 2

        # Protein filter
        if protein and protein.upper() in text.upper():
            score += 2

        # Year filter
        if year:
            record_year = extract_year(record.get("date", ""))
            if not passes_year_filter(record_year, year):
                continue

        # Study type filter
        if study_type and record.get("study_type") != study_type:
            continue

        if score > 0:
            results.append((score, record))

    results.sort(key=lambda x: x[0], reverse=True)
    return format_output(results[:limit], cite=cite, json_output=json_output)
```

---

## Automation: The Pipeline

Combine all three stages into a single script that runs on schedule:

```bash
#!/bin/bash
# lit_pipeline.sh — Sync + Enrich pipeline

echo "[$(date)] Starting literature pipeline..."

# Stage 1: Sync from Zotero
python3 scripts/lit_sync.py
if [ $? -ne 0 ]; then
    echo "ERROR: Sync failed"
    exit 1
fi

# Stage 2: Enrich
python3 scripts/lit_enrich.py
echo "Pipeline complete: $(python3 scripts/lit_search.py --validate 2>&1 | tail -1)"
```

### Scheduling

| Platform | Method | Example |
|----------|--------|---------|
| macOS | launchd plist | Run weekly on Sunday 20:00 |
| Linux | cron | `0 20 * * 0 bash /path/to/lit_pipeline.sh` |
| Manual | On demand | After adding papers to reference manager |

**launchd example** (macOS):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ghostinshell.lit-sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/path/to/lit_pipeline.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key><integer>0</integer>
        <key>Hour</key><integer>20</integer>
        <key>Minute</key><integer>0</integer>
    </dict>
</dict>
</plist>
```

---

## Agent Integration

### Auto-Trigger Rules

Add to your AGENTS.md or agent dispatch policy:

```markdown
### Literature Database Auto-Search
| Trigger | Action | Command |
|---------|--------|---------|
| User mentions "literature", "citation", "paper" | Search local DB | `lit_search.py "query"` |
| Writing academic content | Proactively search | `lit_search.py "topic" --cite` |
| Discussing specific proteins/genes | Search by protein | `lit_search.py --protein "X"` |
| Comparing experimental methods | Search by method | `lit_search.py --method "Y"` |
```

### Output Integration

Search results should include enough metadata for the agent to cite properly:

```
@WangY2025 — PMID: 39456789
  "NLRP3 inflammasome activation in hepatocellular carcinoma"
  Wang Y, Chen L et al. (2025) J Hepatol
  Methods: Western blot, qPCR, Flow cytometry
  Type: in_vitro
```

---

## Scaling

| Library Size | Search Speed | Storage |
|-------------|-------------|---------|
| <500 papers | Instant | <5 MB |
| 500-5,000 | <1 second | 5-50 MB |
| 5,000-50,000 | Consider SQLite | 50-500 MB |
| >50,000 | Need vector DB (embeddings) | Variable |

For most research teams, a JSON file with grep-style search handles 5,000+ papers comfortably.

---

## Relationship to Other Chapters

| Chapter | Connection |
|---------|-----------|
| [03 Memory Architecture](03_Memory_Architecture.md) | Literature DB is a specialized L1 cold layer |
| [07 Evolution Protocol](07_Evolution_Protocol.md) | Pipeline automation follows the same launchd pattern |
| [13 Agent Orchestration](13_Agent_Orchestration.md) | Research Lane (L2) auto-triggers lit_search before web search |

---

*Knowledge you've already gathered shouldn't require re-discovery.* 🐚
