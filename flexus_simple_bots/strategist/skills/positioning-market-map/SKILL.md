---
name: positioning-market-map
description: Competitive positioning analysis — market map, differentiation axes, blue ocean identification
---

You build a structured competitive positioning map from research artifacts and competitive data. The market map reveals where competitors cluster and where white space exists for differentiation. Positioning is relative, not absolute. "We're better" is not positioning. "We focus exclusively on X for segment Y while competitors serve a broad market" is positioning.

Core mode: dual-lens evidence-first. Build market maps using two explicit lenses: (1) **buyer perception** — how buyers actually perceive options; (2) **capability/execution** — what providers can reliably deliver. Never merge these lenses into one implicit score. If you combine them without labeling, you hide contradictions and produce false clarity. Every differentiation claim must be evidence-backed from prior research artifacts.

## Methodology

### Step 0: Activate input artifacts
```
flexus_policy_document(op="activate", args={"p": "/pain/alternatives-landscape"})
flexus_policy_document(op="activate", args={"p": "/discovery/{study_id}/jtbd-outcomes"})
flexus_policy_document(op="list", args={"p": "/signals/"})
```
If alternatives-landscape or jtbd-outcomes are unavailable, output is hypothesis-only, confidence = low.

### Step 1: Declare map scope
Before placing any competitor, declare in the artifact:
- Target segment
- Geography
- Time window for evidence
- Decision context: selection / replacement / expansion / category entry

### Step 2: Axis selection (evidence-gated)
A market map requires two axes that represent buyer-relevant tradeoffs, not internal slogans.

Axis requirements:
1. Each axis must be tied to observed buyer criteria from JTBD and alternatives evidence (not product pride).
2. Axes must be clearly non-duplicative — avoid semantic overlap like "easy" vs "intuitive."
3. Each axis must include low/high endpoint definitions interpretable without extra context.

Source for axis selection: `interview_corpus` buying criteria + `alternatives_landscape` competitor strengths/weaknesses.

**Bad axes:** "easy to use" vs. "powerful" (correlated and subjective)
**Good axes:** "deployment complexity" vs. "customization depth" (specific, observable)

If you cannot justify axis relevance with evidence, replace the axis. Do not continue with "best guess" axis labels.

### Step 3: Competitor placement
For each competitor, collect and compare:
1. Claimed positioning (marketing narrative, pricing page, hero messaging)
2. Perceived positioning (review/interview signal from G2, Capterra, Reddit)
3. Execution evidence (capability delivery, known limitations)
4. Recency metadata

Then assign: x/y coordinates, placement confidence, source references.

If claimed and perceived positions diverge, preserve both and explain the delta. Do not collapse divergence into one polished sentence — divergence is often the most actionable finding.

### Step 4: White-space validation
Treat every empty quadrant as a hypothesis until validated.

Validation sequence:
1. Identify empty or weakly populated region.
2. Check demand evidence: signals from `signal-search-seo`, `signal-reviews-voice`, pain data.
3. Check attainability: can your team credibly deliver this position in the planning horizon?
4. Check economic/segment viability: does this segment have WTP and sufficient size?
5. Assign status: `hypothesis` / `validated` / `rejected`.

Never label white space as blue-ocean opportunity from map geometry alone. If demand signal is weak or contradictory, keep status `hypothesis`. If demand is strong but attainability is weak, propose staged tests, not immediate positioning shift.

### Step 5: Differentiation ranking
Rank differentiation opportunities by: demand strength × underserved score × attainability.

### Signal quality gates (hard — all must pass for `strong` signal)
1. **Triangulation gate:** Competitor placement requires ≥2 independent signal families. White-space recommendation requires ≥3 signal families including one non-modeled source class.
2. **Review depth gate:** If review base is below meaningful threshold for category interpretation, downgrade confidence.
3. **Traffic/trend gate:** Treat modeled traffic and normalized trend data as directional signals only — not proof of market demand or winner status.
4. **Materiality gate:** A measurable delta must be decision-relevant in your GTM context, not just statistically detectable.

If any gate fails: downgrade confidence and output hypothesis language instead of final recommendation language.

## Anti-Patterns

#### Inside-Out Axes
**What it looks like:** Axis labels mirror internal product pride, not buyer decision criteria.
**Detection signal:** Win/loss reasons do not match axis logic.
**Consequence:** Positioning appears differentiated but fails in market selection.
**Mitigation:** Derive axes from JTBD + alternatives evidence, then revalidate with buyer language.

#### Empty Quadrant = Opportunity
**What it looks like:** Unoccupied map area treated as validated white space.
**Detection signal:** No demand proof, weak WTP evidence, low conversion in tests.
**Consequence:** Strategy shifts into low-viability territory.
**Mitigation:** Mark as hypothesis; require demand + attainability validation before recommendation.

#### Snapshot Positioning
**What it looks like:** One-time data pull drives durable positioning decision.
**Detection signal:** Missing recency metadata and no refresh cadence.
**Consequence:** Overreaction to temporary signal noise or provider methodology artifacts.
**Mitigation:** Enforce monthly delta checks and quarterly synthesis before strategic changes.

#### Source Monoculture
**What it looks like:** One external source controls placement and conclusions.
**Detection signal:** No triangulation table and no contradiction log.
**Consequence:** Hidden source bias becomes strategy bias.
**Mitigation:** Require multiple independent signal families and explicit contradiction handling.

#### Unsubstantiated Differentiation Claims
**What it looks like:** Claims like "AI-powered," "most trusted," or "leading" without linked evidence.
**Detection signal:** Claim has no source ID, no owner, or no timestamp.
**Consequence:** Trust, compliance, and execution risk.
**Mitigation:** Enforce claim registry; downgrade unsupported claims to hypothesis status.

## Recording

```
write_artifact(path="/strategy/positioning-map", data={...})
```

A complete output must record: map scope, lens type for each major conclusion, evidence references for each placement and claim, white-space status, confidence tier, unresolved contradictions, refresh policy. If this metadata is missing, the artifact is incomplete.

## Available Tools

```
flexus_policy_document(op="activate", args={"p": "/pain/alternatives-landscape"})

flexus_policy_document(op="activate", args={"p": "/discovery/{study_id}/jtbd-outcomes"})

flexus_policy_document(op="list", args={"p": "/signals/"})

flexus_policy_document(op="list", args={"p": "/strategy/"})
```

## Artifact Schema

```json
{
  "market_positioning_map": {
    "type": "object",
    "description": "Competitive positioning map with evidence-backed competitor placements, validated white spaces, and differentiation opportunities.",
    "required": ["problem_space", "mapped_at", "mapping_scope", "map_lenses", "axis_x", "axis_y", "competitors", "white_spaces", "differentiation_opportunities", "confidence", "contradictions"],
    "additionalProperties": false,
    "properties": {
      "problem_space": {"type": "string"},
      "mapped_at": {"type": "string", "description": "ISO-8601 UTC timestamp."},
      "mapping_scope": {
        "type": "object",
        "required": ["segment", "geography", "time_window"],
        "additionalProperties": false,
        "properties": {
          "segment": {"type": "string"},
          "geography": {"type": "string"},
          "time_window": {
            "type": "object",
            "required": ["start_date", "end_date"],
            "additionalProperties": false,
            "properties": {"start_date": {"type": "string"}, "end_date": {"type": "string"}}
          }
        }
      },
      "map_lenses": {"type": "array", "minItems": 1, "items": {"type": "string", "enum": ["buyer_perception", "capability_execution"]}},
      "axis_x": {
        "type": "object",
        "required": ["label", "low_description", "high_description", "evidence_basis"],
        "additionalProperties": false,
        "properties": {
          "label": {"type": "string"},
          "low_description": {"type": "string"},
          "high_description": {"type": "string"},
          "evidence_basis": {"type": "string", "description": "Evidence from JTBD + alternatives supporting axis selection."},
          "selection_evidence": {"type": "array", "items": {"type": "string"}}
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
          "evidence_basis": {"type": "string"},
          "selection_evidence": {"type": "array", "items": {"type": "string"}}
        }
      },
      "competitors": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["name", "x_score", "y_score", "claimed_position", "perceived_position", "placement_confidence", "sources"],
          "additionalProperties": false,
          "properties": {
            "name": {"type": "string"},
            "x_score": {"type": "number", "minimum": 0, "maximum": 10},
            "y_score": {"type": "number", "minimum": 0, "maximum": 10},
            "claimed_position": {"type": "string", "description": "Their marketing narrative."},
            "perceived_position": {"type": "string", "description": "Actual buyer perception from reviews/interviews."},
            "claim_perception_delta": {"type": "string", "description": "Discrepancy between claimed and perceived — often the most actionable finding."},
            "placement_confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "sources": {"type": "array", "items": {"type": "string"}}
          }
        }
      },
      "white_spaces": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["description", "status", "demand_evidence", "attainability_note"],
          "additionalProperties": false,
          "properties": {
            "description": {"type": "string"},
            "status": {"type": "string", "enum": ["hypothesis", "validated", "rejected"]},
            "demand_evidence": {"type": "string"},
            "attainability_note": {"type": "string"},
            "economic_viability_note": {"type": "string"}
          }
        }
      },
      "differentiation_opportunities": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["description", "demand_score", "underserved_score", "attainability_score", "priority"],
          "additionalProperties": false,
          "properties": {
            "description": {"type": "string"},
            "demand_score": {"type": "number", "minimum": 0, "maximum": 10},
            "underserved_score": {"type": "number", "minimum": 0, "maximum": 10},
            "attainability_score": {"type": "number", "minimum": 0, "maximum": 10},
            "priority": {"type": "string", "enum": ["high", "medium", "low"]}
          }
        }
      },
      "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
      "contradictions": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["description", "source_a", "source_b", "impact"],
          "additionalProperties": false,
          "properties": {
            "description": {"type": "string"},
            "source_a": {"type": "string"},
            "source_b": {"type": "string"},
            "impact": {"type": "string", "enum": ["major", "minor"]}
          }
        }
      }
    }
  }
}
```
