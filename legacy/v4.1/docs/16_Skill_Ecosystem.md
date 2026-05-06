# 16 — Skill Ecosystem

> An agent that can't learn new skills is just a prompt.

---

## The Problem

AI coding tools have a growing ecosystem of **skills** — reusable prompt packages that add specialized capabilities (statistics, visualization, writing styles, domain expertise). But without governance:

- Agents install skills that conflict with each other
- Malicious skills get installed without review
- 300+ skills create decision paralysis
- Unused skills clutter the context
- No way to know which skills are actually valuable

---

## Skill Lifecycle

```
Discovery → Audit → Install → Use → Review → Archive/Remove
```

| Stage | Who | Action |
|-------|-----|--------|
| **Discovery** | Agent or user | Find skill from marketplace or repo |
| **Audit** | Security agent | Scan for safety, review permissions |
| **Install** | Agent (after audit) | Add to skills directory |
| **Use** | Agent | Invoke during tasks |
| **Review** | Monthly automation | Check usage frequency |
| **Archive** | Agent | Move unused skills to cold storage |

---

## Skill Categories

Organize skills by domain to reduce decision paralysis:

| Category | Examples | Typical Count |
|----------|---------|---------------|
| **Core** | Git, file management, search | 5-10 |
| **Development** | Frontend, backend, testing, CI/CD | 20-50 |
| **Writing** | Academic, blog, technical docs | 10-20 |
| **Research** | Literature, data analysis, statistics | 10-30 |
| **Domain** | Biomedical, legal, finance | 50-200 |
| **Marketing** | SEO, content, social media | 10-30 |
| **Design** | UI, visualization, diagrams | 10-20 |

### Skill Quick Reference

Maintain a living reference document:

```markdown
# Skills Quick Reference

## Most Used (Weekly)
| Skill | Purpose | Trigger |
|-------|---------|---------|
| lit-search | Search local literature | "find papers", "cite" |
| statistics | Statistical analysis | "t-test", "ANOVA" |
| frontend-design | UI components | "build a page" |

## Available by Category
### Research (25 skills)
- deep-research, literature-review, citation-management...

### Development (40 skills)
- frontend-design, playwright, firebase...

## Recently Installed
- [date] skill-name — purpose — source
```

---

## Security Audit Protocol

**Rule: Every new skill must pass security audit before installation.**

### Audit Checklist

| Check | What to Look For | Severity |
|-------|-----------------|----------|
| **Permissions** | Does it need Bash? Write? Network? | High if Bash |
| **Data access** | Does it read sensitive files? | High |
| **External calls** | Does it contact external APIs? | Medium |
| **Source trust** | Official marketplace vs. random repo | High |
| **License** | Compatible with your usage? | Medium |
| **Dependencies** | Does it install additional packages? | Medium |

### Audit Flow

```
New skill found
  ↓
Security agent reviews (automated)
  ├─ ✅ benign → Install
  ├─ ⚠️ unknown → Flag for human review
  └─ 🚨 malicious → Block + log
```

### Batch Installation

When installing multiple skills from a source:

```
1. Clone/download the skill set
2. Run security scan on ALL skills
3. Categorize results (benign/unknown/malicious)
4. Install benign, flag unknown, block malicious
5. Log everything to audit trail
```

---

## Skill Governance

### Monthly Review

Check which skills are actually being used:

```python
# Concept: skill usage tracker
def monthly_skill_review(usage_log, skills_dir):
    all_skills = list_installed_skills(skills_dir)
    used_skills = get_used_skills(usage_log, days=30)

    unused = all_skills - used_skills

    print(f"Installed: {len(all_skills)}")
    print(f"Used (30d): {len(used_skills)}")
    print(f"Unused: {len(unused)}")

    for skill in unused:
        print(f"  Consider archiving: {skill}")
```

### Hot/Cold Skill Separation

Mirror the memory architecture:

| Layer | Location | Content |
|-------|----------|---------|
| **Hot** | `~/.claude/skills/` (active) | Skills used in past 30 days |
| **Cold** | `vault/skills_archive/` | Evaluated but rarely used |
| **Index** | `skills-quickref.md` | Navigation + categories |

### Version Tracking

When skills update, track changes:

```json
{
  "skill": "statistics",
  "version": "2.1.0",
  "installed": "2025-01-15",
  "updated": "2025-03-01",
  "source": "official-marketplace",
  "audit_status": "benign",
  "usage_count_30d": 12
}
```

---

## Skill Conflict Resolution

When multiple skills can handle the same task:

### Priority Rules

1. **Domain-specific > General**: A biomedical statistics skill beats a generic statistics skill for biology data
2. **Recently used > Rarely used**: The skill you used last week is probably more relevant
3. **Official > Community**: Official marketplace skills over random repos
4. **Explicit > Implicit**: If user names a skill, use that one

### Conflict Examples

| Task | Competing Skills | Resolution |
|------|-----------------|-----------|
| "Analyze this data" | `statistics`, `exploratory-data-analysis`, `scientific-visualization` | `statistics` (most specific for analysis) |
| "Write a paper" | `scientific-writing`, `academic-paper`, `article-writing` | `academic-paper` (most specific for papers) |
| "Review this code" | `code-review`, `pr-review-toolkit`, `simplify` | Depends on context (PR vs. general vs. refactor) |

### Integration with Lane Routing

Skills map to Lanes:

```markdown
<keyword_detection>
| Skill Trigger | Lane | Skill |
|--------------|------|-------|
| "run statistics" | L3 | $statistics |
| "write paper" | L1 | $academic-paper |
| "deep research on" | L2 | $deep-research |
</keyword_detection>
```

---

## Cross-Machine Skill Sync

Skills should be available on all your machines:

```
Vault (cloud-synced)
└── 992_Config/
    └── skills/          ← Source of truth (380+ skills)

Machine A                Machine B
~/.claude/skills/ ──symlink──▶ Vault/992_Config/skills/
```

**Bootstrap handles this** (see [Chapter 10](10_Cross_Machine_Sync.md)):

```bash
# In bootstrap.sh
ln -sf "$VAULT/992_Config/skills" "$HOME/.claude/skills"
```

---

## Anti-Patterns

### ❌ Install Everything

Having 500 skills when you use 20 creates noise. Audit and archive unused skills.

### ❌ Skip Security Audit

One malicious skill with Bash access can compromise your entire system.

### ❌ No Categorization

A flat list of 300 skills is unusable. Categorize and maintain a quick reference.

### ❌ Never Update

Skills evolve. Outdated skills may have bugs or miss new capabilities.

### ❌ Duplicate Skills

Multiple skills for the same purpose create confusion. Pick one per task type.

---

## Relationship to Other Chapters

| Chapter | Connection |
|---------|-----------|
| [06 Security Model](06_Security_Model.md) | Skill audit is an extension of the security model |
| [10 Cross-Machine Sync](10_Cross_Machine_Sync.md) | Skills sync via bootstrap symlinks |
| [13 Agent Orchestration](13_Agent_Orchestration.md) | Skills are invocation targets in Lane routing |
| [07 Evolution Protocol](07_Evolution_Protocol.md) | Monthly skill review is part of evolution heartbeat |

---

*A tool is only as good as the hand that knows when to use it.* 🐚
