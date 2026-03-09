---
name: lead-generation
description: B2B lead generation methodology, ICP construction, scoring rubrics, and search patterns
---

## ICP Construction Framework

### Industry Segmentation
Define the target market at 3 levels:
1. **Sector**: Technology, Finance, Healthcare
2. **Vertical**: SaaS, Fintech, Biotech
3. **Sub-vertical**: DevTools, Payments, Drug Discovery

### Role Targeting
Map decision-making hierarchies:
- **C-Level**: CEO, CTO, CFO, CMO
- **VP-Level**: VP Engineering, VP Product, VP Sales
- **Director**: Director of Engineering, Director of IT
- **Manager**: Engineering Manager, IT Manager

### Company Size Bands
- **Startup**: 1-10 employees
- **Small**: 11-50 employees
- **Mid-market**: 51-500 employees
- **Enterprise**: 501-5000 employees
- **Large Enterprise**: 5000+ employees

## Search Query Patterns

### LinkedIn Discovery
- `"{title}" "{industry}" "{location}" site:linkedin.com/in`
- `"{company}" "{role}" site:linkedin.com/in`

### Company Discovery
- `"top {industry} companies" "{location}" {year}`
- `"{industry}" "series A" OR "raised" "{location}"`
- `"{industry}" companies "{size} employees" site:crunchbase.com`

### Growth Signal Detection
- `"{company}" hiring OR "open positions"`
- `"{company}" "series" OR "raised" OR "funding"`
- `"{company}" "launches" OR "announces" OR "partnership"`

### Technology Stack Detection
- `"{company}" "we use" OR "built with" OR "powered by" "{technology}"`
- `site:stackshare.io "{company}"`
- `site:builtwith.com "{domain}"`

## Scoring Rubric

### Score Interpretation
- **90-100**: Hot lead — immediate outreach recommended
- **75-89**: Warm lead — prioritize for outreach
- **60-74**: Qualified lead — add to nurture sequence
- **40-59**: Cool lead — monitor for changes
- **Below 40**: Unqualified — archive

## Deduplication Algorithm

### Company Normalization
1. Lowercase all text
2. Remove suffixes: Inc, LLC, Ltd, GmbH, Corp, Co, SA, AG
3. Remove punctuation and extra spaces
4. Extract root domain from URLs

### Person Matching
1. Normalize names (lowercase, trim)
2. Compare first + last name
3. Match against company
4. Levenshtein distance < 2 = likely match

## Output Format Templates

### Markdown Table
```
| # | Company | Contact | Title | Score | Key Signal |
|---|---------|---------|-------|-------|------------|
| 1 | Acme Inc | J. Doe | CTO | 87 | Series B |
```

### JSON Structure
```json
{
  "lead_id": "lead_001",
  "company": {"name": "", "domain": "", "size": "", "industry": ""},
  "contact": {"name": "", "title": "", "linkedin": ""},
  "score": {"total": 0, "icp_match": 0, "growth": 0, "quality": 0, "recency": 0, "access": 0},
  "enrichment": {},
  "sources": [],
  "discovered_at": ""
}
```
