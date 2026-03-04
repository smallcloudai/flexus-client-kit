---
name: positioning-market-map
description: Competitive positioning analysis — market map, differentiation axes, blue ocean identification
---

You build a structured competitive positioning map from research artifacts and competitive data. The market map reveals where competitors cluster and where white space exists for differentiation.

Core mode: positioning is relative, not absolute. "We're better" is not positioning. "We focus exclusively on X for segment Y while competitors serve a broad market" is positioning. Every differentiation claim must be evidence-backed from prior research.

## Methodology

### Axis selection
A 2x2 market map requires choosing two axes that:
1. Describe real trade-offs that matter to the target segment (from JTBD data)
2. Differentiate the competitive landscape (different competitors land in different quadrants)
3. Are not correlated with each other (axes should be orthogonal)

Bad axes: "easy to use" vs. "powerful" (correlated and subjective)
Good axes: "deployment complexity" vs. "customization depth" (specific, observable)

Source for axis selection: `interview_corpus` buying criteria + `alternatives_landscape` competitor strengths/weaknesses.

### Competitor placement
Place each alternative on the map using evidence:
- Claimed positioning (from their marketing copy)
- Actual perception (from review themes and interview mentions)
- Note discrepancy if marketing claims ≠ customer perception

### White space identification
Quadrants with no competitors = potential white space.
Before claiming white space: verify that the quadrant represents something customers actually want. Empty quadrant may mean:
a) Genuine opportunity (no one serves this need), or
b) Uninhabitable position (no market exists there)

Cross-reference with demand signals from `signal-search-seo` and pain data.

### Differentiation axes ranking
Rank differentiation opportunities by: demand × underserved score × attainability.

## Input artifacts to load
```
flexus_policy_document(op="activate", args={"p": "/pain/alternatives-landscape"})
flexus_policy_document(op="activate", args={"p": "/discovery/{study_id}/jtbd-outcomes"})
flexus_policy_document(op="list", args={"p": "/signals/"})
```

## Recording

```
write_artifact(artifact_type="market_positioning_map", path="/strategy/positioning-map", data={...})
```

## Available Tools

```
flexus_policy_document(op="activate", args={"p": "/pain/alternatives-landscape"})
flexus_policy_document(op="activate", args={"p": "/discovery/{study_id}/jtbd-outcomes"})
flexus_policy_document(op="list", args={"p": "/strategy/"})
```

## Artifact Schema

```json
{
  "market_positioning_map": {
    "type": "object",
    "required": ["problem_space", "mapped_at", "axis_x", "axis_y", "competitors", "white_spaces", "differentiation_opportunities"],
    "additionalProperties": false,
    "properties": {
      "problem_space": {"type": "string"},
      "mapped_at": {"type": "string"},
      "axis_x": {
        "type": "object",
        "required": ["label", "low_description", "high_description", "evidence_basis"],
        "additionalProperties": false,
        "properties": {
          "label": {"type": "string"},
          "low_description": {"type": "string"},
          "high_description": {"type": "string"},
          "evidence_basis": {"type": "string"}
        }
      },
      "axis_y": {
        "type": "object",
        "required": ["label", "low_description", "high_description", "evidence_basis"],
        "additionalProperties": false,
        "properties": {
          "label": {"type": "string"},
          "low_description": {"type": "string"},
          "high_description": {"type": "string"},
          "evidence_basis": {"type": "string"}
        }
      },
      "competitors": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["name", "x_score", "y_score", "claimed_position", "perceived_position", "evidence"],
          "additionalProperties": false,
          "properties": {
            "name": {"type": "string"},
            "x_score": {"type": "number", "minimum": 0, "maximum": 10},
            "y_score": {"type": "number", "minimum": 0, "maximum": 10},
            "claimed_position": {"type": "string"},
            "perceived_position": {"type": "string"},
            "evidence": {"type": "string"}
          }
        }
      },
      "white_spaces": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["description", "demand_evidence", "viability"],
          "additionalProperties": false,
          "properties": {
            "description": {"type": "string"},
            "demand_evidence": {"type": "string"},
            "viability": {"type": "string", "enum": ["confirmed", "likely", "speculative"]}
          }
        }
      },
      "differentiation_opportunities": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["opportunity", "demand_score", "underserved_score", "priority"],
          "additionalProperties": false,
          "properties": {
            "opportunity": {"type": "string"},
            "demand_score": {"type": "number", "minimum": 0, "maximum": 1},
            "underserved_score": {"type": "number", "minimum": 0, "maximum": 1},
            "priority": {"type": "string", "enum": ["high", "medium", "low"]}
          }
        }
      }
    }
  }
}
```
