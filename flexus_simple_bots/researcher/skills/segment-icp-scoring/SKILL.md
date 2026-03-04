---
name: segment-icp-scoring
description: ICP scoring synthesis — combine firmographic, behavioral, and signal data into a ranked Ideal Customer Profile scorecard
---

You synthesize firmographic profiles, behavioral intent signals, and market evidence into a structured ICP scorecard. This is the final aggregation step before segment qualification passes to the strategist.

Core mode: every scoring criterion must cite source evidence. A score without a source reference is not a score — it's an opinion. The output must be reproducible: another analyst with the same data should reach the same tier assignment.

## Methodology

### Input dependencies
This skill synthesizes from:
- `segment_firmographic_profile` (from `segment-firmographic` skill)
- `segment_behavioral_intent` (from `segment-behavioral` skill)
- Signal artifacts from researcher signal skills
- `interview_corpus` or `jtbd_outcomes` from `discovery-interview-capture`

Pull these artifacts before scoring: `flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/firmographic"})`

### Scoring dimensions
Define 4-6 scoring dimensions based on the specific hypothesis. Typical dimensions:

1. **Problem fit**: does this segment have the pain we solve? (Source: JTBD data, review signals)
2. **Budget fit**: does this segment have buying power? (Source: firmographic — revenue/headcount, funding stage)
3. **Tech fit**: does their tech stack make our solution compatible? (Source: builtwith/wappalyzer)
4. **Timing fit**: are they in an active search / change event? (Source: intent data, news events)
5. **Access fit**: can we reach decision-makers? (Source: social graph data, channel presence)

### Tier thresholds
- **Tier 1** (ICP): score ≥ 75/100 — prioritize for pipeline
- **Tier 2** (near-ICP): 50-74 — include in broad campaigns, lighter touch
- **Tier 3** (not ICP): <50 — deprioritize

### Confidence rating
If fewer than 3 data sources contribute to a score, mark confidence as "low." Require firmographic + at least one signal source for "medium" confidence. All 5 dimensions sourced = "high" confidence.

## Recording

```
write_artifact(artifact_type="segment_icp_scorecard", path="/segments/{segment_id}/icp-scorecard", data={...})
```

## Available Tools

```
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/firmographic"})

flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/behavioral-intent"})

flexus_policy_document(op="list", args={"p": "/signals/"})

flexus_policy_document(op="activate", args={"p": "/discovery/{study_id}/jtbd-outcomes"})
```

## Artifact Schema

```json
{
  "segment_icp_scorecard": {
    "type": "object",
    "required": ["segment_id", "scored_at", "scoring_model", "accounts", "tier_distribution", "confidence", "source_artifacts"],
    "additionalProperties": false,
    "properties": {
      "segment_id": {"type": "string"},
      "scored_at": {"type": "string"},
      "scoring_model": {
        "type": "object",
        "required": ["dimensions", "tier_thresholds"],
        "additionalProperties": false,
        "properties": {
          "dimensions": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["name", "max_points", "source_skills"],
              "additionalProperties": false,
              "properties": {
                "name": {"type": "string"},
                "max_points": {"type": "integer", "minimum": 0},
                "source_skills": {"type": "array", "items": {"type": "string"}}
              }
            }
          },
          "tier_thresholds": {
            "type": "object",
            "required": ["tier1_min", "tier2_min"],
            "additionalProperties": false,
            "properties": {
              "tier1_min": {"type": "integer", "minimum": 0},
              "tier2_min": {"type": "integer", "minimum": 0}
            }
          }
        }
      },
      "accounts": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["domain", "total_score", "icp_tier", "dimension_scores", "confidence"],
          "additionalProperties": false,
          "properties": {
            "domain": {"type": "string"},
            "total_score": {"type": "integer", "minimum": 0, "maximum": 100},
            "icp_tier": {"type": "string", "enum": ["tier1", "tier2", "tier3"]},
            "dimension_scores": {"type": "object"},
            "confidence": {"type": "string", "enum": ["high", "medium", "low"]}
          }
        }
      },
      "tier_distribution": {
        "type": "object",
        "required": ["tier1_count", "tier2_count", "tier3_count"],
        "additionalProperties": false,
        "properties": {
          "tier1_count": {"type": "integer", "minimum": 0},
          "tier2_count": {"type": "integer", "minimum": 0},
          "tier3_count": {"type": "integer", "minimum": 0}
        }
      },
      "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
      "source_artifacts": {"type": "array", "items": {"type": "string"}}
    }
  }
}
```
