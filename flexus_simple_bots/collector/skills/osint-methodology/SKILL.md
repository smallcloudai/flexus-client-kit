---
name: osint-methodology
description: OSINT collection methodology, source reliability tiers, entity extraction, and change detection
---

## Source Reliability Tiers

- **Tier 1 — Official**: Company press releases, SEC filings, regulatory documents, court records
- **Tier 2 — Authoritative**: Major news agencies (Reuters, AP, Bloomberg), peer-reviewed research
- **Tier 3 — Reputable**: Industry publications, established tech blogs, analyst reports
- **Tier 4 — Secondary**: Social media posts by verified accounts, forums, community discussions
- **Tier 5 — Unverified**: Anonymous sources, rumors, unconfirmed reports

## Entity Extraction Patterns

### Person Entities
- Names following titles: CEO, CTO, VP, Director, Founder
- Quoted speakers in articles
- Authors of publications

### Organization Entities
- Company names in context of: founded, acquired, raised, launched, partnered
- Regulatory bodies mentioned in compliance context

### Financial Entities
- Dollar amounts with context: raised, revenue, valuation, funding
- Percentage changes: growth, decline, market share

### Event Entities
- Dates + actions: launched, announced, acquired, filed

## Knowledge Graph JSON Schema

### Entity
```json
{
  "id": "entity_001",
  "type": "Organization|Person|Product|Event|Financial|Technology",
  "name": "Entity Name",
  "attributes": {},
  "first_seen": "2025-01-01T00:00:00Z",
  "last_updated": "2025-01-15T00:00:00Z",
  "sources": ["url1", "url2"]
}
```

### Relation
```json
{
  "from": "entity_001",
  "to": "entity_002",
  "type": "works_at|founded|competes_with|acquired|invested_in|partners_with",
  "confidence": 0.95,
  "first_seen": "2025-01-01T00:00:00Z",
  "sources": ["url1"]
}
```

## Change Detection Methodology

### Snapshot Comparison
1. Serialize current state (entities + relations + key facts)
2. Load previous snapshot
3. Diff by entity ID and attribute values
4. Classify changes by significance (CRITICAL/IMPORTANT/MINOR)
5. Store new snapshot with timestamp

### Significance Scoring
- Leadership change: CRITICAL (score: 90-100)
- M&A activity: CRITICAL (score: 85-100)
- Funding > $10M: CRITICAL (score: 80-95)
- Product launch: IMPORTANT (score: 60-80)
- Partnership: IMPORTANT (score: 50-70)
- Hiring activity: IMPORTANT (score: 40-60)
- Blog/content: MINOR (score: 10-30)

## Sentiment Analysis

### Scale
- +2: Very positive (major win, breakthrough)
- +1: Positive (good news, growth)
-  0: Neutral (factual, no sentiment)
- -1: Negative (setback, criticism)
- -2: Very negative (crisis, scandal, failure)

### Tracking
Store sentiment over time as array:
```json
{"date": "2025-01-15", "score": 1.2, "sample_size": 8, "sources": 5}
```
