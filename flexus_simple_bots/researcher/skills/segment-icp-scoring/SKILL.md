---
name: segment-icp-scoring
description: ICP scoring synthesis — combine firmographic, behavioral, and signal data into a ranked Ideal Customer Profile scorecard
---

You synthesize firmographic profiles, behavioral intent signals, and market evidence into a structured ICP scorecard. This is the final aggregation step before segment qualification passes to the strategist. Every scoring criterion must cite source evidence. A score without a source reference is not a score — it is an opinion. The output must be reproducible: another analyst with the same data must reach the same tier assignment.

Core mode: ICP scoring is an evidence synthesis problem, not a judgment call. Build three explicit subscores: `fit_score` (firmographic and structural fit), `intent_score` (in-market and research-intent behavior), `engagement_score` (first-party interaction and readiness). Compute `total_score` from governed subscores. Never output only `total_score` without subscore decomposition.

## Methodology

### Step 0: Activate input artifacts
Before scoring, activate all required artifacts:
```
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/firmographic"})
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/behavioral-intent"})
flexus_policy_document(op="list", args={"p": "/signals/"})
flexus_policy_document(op="activate", args={"p": "/discovery/{study_id}/jtbd-outcomes"})
```
If required artifacts do not exist, are stale beyond freshness policy, or do not meet minimum sample rules, return `run_status: "insufficient_data"` and do not tier accounts.

### Step 1: Input validation and quality gates
Check required fields and freshness before any scoring math. Required baseline: account/domain identity, firmographic banding, at least one intent-family signal, and at least one first-party engagement or interview-derived signal. Records failing baseline = quarantined from scoring.

**Source-specific gating (mandatory before normalization):**
- **Bombora Company Surge:** enforce score thresholding (typically ≥60) and topic coverage filters before including in `intent_score`. Mark source as `gated_out` with reason if fails.
- **G2 Buyer Intent:** require stage/activity constraints and minimum event volume for the chosen interval.
- Reject ambiguous account identity matches.
- Validate technographic observations against recency windows.

### Step 2: Scoring dimensions
Define 4-6 dimensions for the specific hypothesis. Typical set:
1. **Problem fit:** does this segment have the pain we solve? (Source: JTBD data, review signals)
2. **Budget fit:** buying power present? (Source: firmographic — revenue/headcount, funding stage)
3. **Tech fit:** tech stack compatible? (Source: BuiltWith/Wappalyzer — use as fit/risk context only, not buying intent)
4. **Timing fit:** active search or change event? (Source: intent data, news events, trigger signals)
5. **Access fit:** can we reach decision-makers? (Source: social graph data, channel presence)

### Step 3: Build subscores
Compute `fit_score`, `intent_score`, and `engagement_score` independently. Store not only numeric values but also source evidence summary and timestamp windows used. A reviewer must be able to reconstruct each subscore from artifact references alone.

### Step 4: Apply recency decay
Dynamic signals must have explicit recency logic (rolling windows and/or decay). If source lacks native decay signal, apply local policy decay and persist that policy version in the scorecard. Do not carry historical signal strength unchanged when no signal occurred within the policy window.

### Step 5: Compute composite and assign tier
Default tier thresholds (fallback — tune against business outcomes when data available):
- **Tier 1 (ICP):** total_score ≥ 75 — prioritize for pipeline
- **Tier 2 (near-ICP):** 50-74 — include in broad campaigns, lighter touch
- **Tier 3 (not ICP):** <50 — deprioritize

If thresholds are not yet tuned against outcomes, mark `threshold_policy_status: "default_thresholds"`.

### Step 6: Confidence model
Confidence is NOT just source count. Calculate from: coverage factor (independent source families), reliability factor (source performance in this environment), conflict factor (contradiction between source families), missingness factor (missing high-impact dimensions).
- **High:** strong coverage, low conflict, low missingness, no critical gates failed.
- **Medium:** acceptable coverage with moderate conflict or missingness.
- **Low:** poor coverage, high conflict, high missingness, or high intent + poor fit (requires review before Tier 1).

If conflict is high (strong intent but poor fit and no buying-committee corroboration), cap confidence at low and block auto-promotion to Tier 1.

### Step 7: Reproducibility validation before publish
Run and record:
1. Tier ordering sanity: higher tiers should not underperform lower tiers on key downstream outcomes.
2. Baseline comparison: quantify lift of each tier versus overall baseline.
3. Distribution stability: detect abrupt score distribution shifts versus prior run.

If any required check fails: mark `validation_status: "needs_review"`. Do not silently ship updated tiering when validation fails.

## Anti-Patterns

#### Single-Spike Intent Routing
**What it looks like:** One-off intent spike from a single source routes account directly to Tier 1.
**Detection signal:** Intent-qualified count rises while meeting conversion stagnates.
**Consequence:** False positives, SDR capacity waste, and trust erosion.
**Mitigation:** Require multi-signal persistence and buying-stage corroboration before handoff.

#### Dirty-Data Scoring
**What it looks like:** Scoring runs on stale or duplicate CRM/enrichment data.
**Detection signal:** Duplicate rates and missing critical fields increase while top-tier outcomes degrade.
**Consequence:** High-confidence wrong tiers.
**Mitigation:** Enforce pre-score data quality gates, freshness SLAs, and record quarantine.

#### Unversioned Scoring Logic
**What it looks like:** Scoring logic lives in unversioned vendor UI configuration.
**Detection signal:** Unexplained distribution shifts after vendor migration or admin edits.
**Consequence:** Non-reproducible scorecards and broken longitudinal analysis.
**Mitigation:** Version scoring policy externally, stamp every run, parallel-test before cutover.

#### Null-as-Disqualification
**What it looks like:** Missing fields converted into negative scoring signals.
**Detection signal:** Missingness increases and Tier 3 rates rise without corresponding business evidence.
**Consequence:** False disqualification of accounts with incomplete but valid profiles.
**Mitigation:** Carry missingness metrics per account; penalize confidence, not tier.

## Recording

```
write_artifact(path="/segments/{segment_id}/icp-scorecard", data={...})
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
    "description": "ICP scorecard run with per-account tiering, subscore decomposition, and reproducibility metadata.",
    "required": ["segment_id", "scored_at", "run_status", "scoring_model", "accounts", "tier_distribution", "confidence", "validation", "source_artifacts"],
    "additionalProperties": false,
    "properties": {
      "segment_id": {"type": "string"},
      "scored_at": {"type": "string", "description": "ISO-8601 UTC timestamp when scoring completed."},
      "run_status": {"type": "string", "enum": ["ok", "insufficient_data", "needs_review"]},
      "scoring_model": {
        "type": "object",
        "required": ["model_version", "dimensions", "subscore_weights", "tier_thresholds", "threshold_policy_status"],
        "additionalProperties": false,
        "properties": {
          "model_version": {"type": "string"},
          "dimensions": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["name", "max_points", "source_skills"],
              "additionalProperties": false,
              "properties": {
                "name": {"type": "string", "description": "problem_fit / budget_fit / tech_fit / timing_fit / access_fit"},
                "max_points": {"type": "integer", "minimum": 0},
                "source_skills": {"type": "array", "items": {"type": "string"}}
              }
            }
          },
          "subscore_weights": {
            "type": "object",
            "required": ["fit_weight", "intent_weight", "engagement_weight"],
            "additionalProperties": false,
            "properties": {
              "fit_weight": {"type": "number", "minimum": 0},
              "intent_weight": {"type": "number", "minimum": 0},
              "engagement_weight": {"type": "number", "minimum": 0}
            }
          },
          "tier_thresholds": {
            "type": "object",
            "required": ["tier1_min", "tier2_min"],
            "additionalProperties": false,
            "properties": {
              "tier1_min": {"type": "number", "description": "Default: 75"},
              "tier2_min": {"type": "number", "description": "Default: 50"}
            }
          },
          "threshold_policy_status": {"type": "string", "enum": ["tuned", "default_thresholds", "default_due_to_insufficient_outcomes"]}
        }
      },
      "accounts": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["domain", "total_score", "tier", "subscores", "confidence", "missing_dimensions"],
          "additionalProperties": false,
          "properties": {
            "domain": {"type": "string"},
            "total_score": {"type": "number", "minimum": 0, "maximum": 100},
            "tier": {"type": "integer", "enum": [1, 2, 3]},
            "subscores": {
              "type": "object",
              "required": ["fit_score", "intent_score", "engagement_score"],
              "additionalProperties": false,
              "properties": {
                "fit_score": {"type": "number", "minimum": 0, "maximum": 100},
                "intent_score": {"type": "number", "minimum": 0, "maximum": 100},
                "engagement_score": {"type": "number", "minimum": 0, "maximum": 100}
              }
            },
            "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "missing_dimensions": {"type": "array", "items": {"type": "string"}, "description": "Dimensions with missing or quarantined data."},
            "source_evidence": {"type": "array", "items": {"type": "string"}, "description": "Artifact references used for this account's score."}
          }
        }
      },
      "tier_distribution": {
        "type": "object",
        "required": ["tier1_count", "tier2_count", "tier3_count", "quarantined_count"],
        "additionalProperties": false,
        "properties": {
          "tier1_count": {"type": "integer", "minimum": 0},
          "tier2_count": {"type": "integer", "minimum": 0},
          "tier3_count": {"type": "integer", "minimum": 0},
          "quarantined_count": {"type": "integer", "minimum": 0}
        }
      },
      "confidence": {"type": "string", "enum": ["high", "medium", "low"], "description": "Run-level confidence in scoring quality."},
      "validation": {
        "type": "object",
        "required": ["status", "checks_run"],
        "additionalProperties": false,
        "properties": {
          "status": {"type": "string", "enum": ["pass", "needs_review", "skipped"]},
          "checks_run": {"type": "array", "items": {"type": "string"}},
          "failed_checks": {"type": "array", "items": {"type": "string"}}
        }
      },
      "source_artifacts": {
        "type": "array",
        "description": "Policy document paths activated for this run.",
        "items": {"type": "string"}
      }
    }
  }
}
```
