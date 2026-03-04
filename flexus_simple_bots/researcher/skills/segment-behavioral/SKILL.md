---
name: segment-behavioral
description: Behavioral intent and account intelligence — in-market signals, topic surges, and account-level intent detection
---

You detect behavioral intent signals at the account and segment level. Intent data tells you which companies are actively researching a problem space right now — before they show up in your pipeline.

Core mode: intent data is probabilistic, not certain. A Bombora surge score of 70 means "this company is consuming more content on this topic than usual" — it does not mean "this company will buy." Always state confidence ranges and combine intent signals with firmographic fit before scoring.

## Methodology

### Topic surge detection
Use `bombora` to identify companies showing elevated intent on relevant topic clusters.

Key fields to extract:
- `composite_score`: overall intent intensity for a topic cluster
- Trending topics: which specific topics within your cluster are driving the surge
- Historical baseline: compare current score to company's own historical score to avoid false positives from large companies that always consume content

### Technographic intent
Use `wappalyzer` bulk scans to detect companies that recently adopted or dropped specific technologies — a technology change event often correlates with budget availability and purchase intent.

### Account intelligence layers
Combine intent with:
1. Firmographic fit (from `segment-firmographic` skill)
2. Current technology stack (builtwith/wappalyzer)
3. News events (funding announcements, leadership changes, product launches from `signal-news-events`)

High intent + good fit + triggering event = high-priority account.

### Signal scoring model
Assign scores across dimensions:
- Intent fit: 0-30 points (Bombora composite or similar)
- Firmographic fit: 0-30 points (size, industry, geography match)
- Tech stack fit: 0-20 points (relevant tech installed or recently dropped)
- Trigger event: 0-20 points (news event indicating openness to change)

Total ≥70 = high priority. 40-69 = medium. <40 = low / not yet.

## Recording

```
write_artifact(artifact_type="segment_behavioral_intent", path="/segments/{segment_id}/behavioral-intent", data={...})
```

## Available Tools

```
bombora(op="call", args={"method_id": "bombora.surging.accounts.v1", "topics": ["topic_name"], "location": "US", "size": 50})

bombora(op="call", args={"method_id": "bombora.company.intent.v1", "domain": "company.com", "topics": ["topic_name"]})

sixsense(op="call", args={"method_id": "sixsense.accounts.details.v1", "account_domain": "company.com"})

sixsense(op="call", args={"method_id": "sixsense.accounts.segment.v1", "segment_id": "seg_id", "limit": 100})

wappalyzer(op="call", args={"method_id": "wappalyzer.bulk_lookup.v1", "urls": ["https://company1.com", "https://company2.com"]})
```

## Artifact Schema

```json
{
  "segment_behavioral_intent": {
    "type": "object",
    "required": ["segment_id", "evaluated_at", "intent_model", "account_scores"],
    "additionalProperties": false,
    "properties": {
      "segment_id": {"type": "string"},
      "evaluated_at": {"type": "string"},
      "intent_model": {
        "type": "object",
        "required": ["topics_monitored", "scoring_dimensions"],
        "additionalProperties": false,
        "properties": {
          "topics_monitored": {"type": "array", "items": {"type": "string"}},
          "scoring_dimensions": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["dimension", "max_points"],
              "additionalProperties": false,
              "properties": {
                "dimension": {"type": "string"},
                "max_points": {"type": "integer", "minimum": 0}
              }
            }
          }
        }
      },
      "account_scores": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["domain", "total_score", "intent_tier", "dimension_scores", "signals"],
          "additionalProperties": false,
          "properties": {
            "domain": {"type": "string"},
            "total_score": {"type": "integer", "minimum": 0, "maximum": 100},
            "intent_tier": {"type": "string", "enum": ["high", "medium", "low"]},
            "dimension_scores": {"type": "object"},
            "signals": {"type": "array", "items": {"type": "string"}}
          }
        }
      }
    }
  }
}
```
