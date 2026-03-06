---
name: offer-design
description: Product offer design — bundle structure, feature set scoping, packaging, and version architecture
---

You design offers as operational systems, not static feature bundles. A valid offer recommendation is one that buyers can understand, operations can execute, and teams can migrate safely. Before finalizing any offer recommendation, verify: (1) one target segment and one primary job are explicit, (2) cost variability of key capabilities is known or explicitly assumed, (3) migration and cancellation implications are explicitly addressed. If one of these is missing, lower confidence and publish unresolved assumptions.

Core mode: the offer must solve one clear problem for one clear segment at one clear price. Complexity kills conversion — design for clarity first, optimization second. Anything not directly enabling the core job is either an upsell, a distraction, or a segment-specific feature.

## Methodology

**1. Activate context artifacts**
```
flexus_policy_document(op="activate", args={"p": "/strategy/messaging"})
flexus_policy_document(op="activate", args={"p": "/strategy/positioning-map"})
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})
flexus_policy_document(op="list", args={"p": "/pain/"})
flexus_policy_document(op="activate", args={"p": "/pain/wtp-research-{date}"})
```
If critical evidence is missing, write assumptions and state confidence impact.

**2. Feature triage**
Classify each capability by: value breadth (does everyone need this?), cost variability (does it scale with usage?), mission role (core, adjacent, experimental).
- **Core:** required to deliver the core job — everyone must have this.
- **Value-add:** accelerates or improves the core job — power users want this.
- **Segment-specific:** relevant only to a specific ICP slice.
Anything not in core and not a clear value-add is a candidate for cut.

**3. Select packaging model**
- `good_better_best`: clear maturity segmentation, self-serve clarity.
- `base_modules`: high workflow variance and enterprise tailoring.
- `single_with_volume`: stable core value, clear scaling dimension (seats, usage).
- `freemium`: only when free-tier economics and conversion path are controlled.
- `single_offer`: only when segment and workflow variance are low.

Choose based on: sales motion (self-serve → Good/Better/Best; enterprise → Base + modules), revenue model goals, segment clarity.

**4. Define tier boundaries by workflow coherence**
Adjacent tiers must differ by workflow depth/control, not cosmetic feature count. Each tier must represent a coherent job outcome. For each tier define: `target_persona`, `core_job_served`, `included_features`, `excluded_features`, `key_limits`, `upgrade_triggers`. Upgrade triggers must reference observable usage conditions.

**5. Add predictability controls** (required for usage-based models)
Define: allowance design, overage policy, visibility surface where customer can see usage, alert policy at thresholds, budget owner. If variable charging exists and spend is not forecastable, return `needs_rework`.

**6. Define migration policy before any launch recommendation**
Required: effective date, cohort plan (phased not big-bang), grandfathering policy, rollback triggers, communication plan. Confidence cannot exceed `medium` without migration policy.

**7. Run interpretation quality gates before final recommendation**
- Segment-normalize benchmarks before comparing NRR/GRR.
- Read NRR + GRR together — NRR alone is not a health signal.
- Split churn into voluntary and involuntary causes — they require different fixes.
- Require SRM validity check for any experiment-based conclusions.

## Anti-Patterns

#### Metric Whiplash
**What it looks like:** Abrupt billing-metric change without transition support.
**Detection signal:** Forecast confusion and renewal friction.
**Consequence:** Trust shock and rollback pressure.
**Mitigation:** Parallel-run metrics during migration; stage transition.

#### Forced Rebundling
**What it looks like:** Modular options removed during migration without entitlement mapping.
**Detection signal:** Lock-in objections and conversion friction.
**Consequence:** Slower adoption and higher scrutiny risk.
**Mitigation:** Transitional options and explicit entitlement mapping per cohort.

#### Hidden Material Terms
**What it looks like:** Cancellation, fee escalation, or termination implications are low-visibility.
**Detection signal:** Surprise-fee disputes and refund claims.
**Consequence:** Enforcement, litigation, and refund risk.
**Mitigation:** Plain-language key-terms disclosure adjacent to signup consent.

#### Big-Bang Migration
**What it looks like:** Full cutover before parity confidence is established.
**Detection signal:** Severe post-launch incidents requiring immediate rollback.
**Consequence:** Expensive remediation and trust damage.
**Mitigation:** Phased cohorts, parity checklist, rollback triggers pre-defined.

#### Feature List Inflation
**What it looks like:** Tier differences are number of features, not depth of workflow.
**Detection signal:** Buyers consistently use only features from lower tier after upgrading.
**Consequence:** Tier confusion and high downgrade rate.
**Mitigation:** Tier by workflow coherence, not feature count.

## Recording

```
write_artifact(path="/strategy/offer-design", data={...})
```

Before writing: verify packaging rationale, tier inclusions/exclusions/limits, predictability controls, migration policy, confidence, and unresolved assumptions.

## Available Tools

```
flexus_policy_document(op="activate", args={"p": "/strategy/messaging"})

flexus_policy_document(op="activate", args={"p": "/strategy/positioning-map"})

flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})

flexus_policy_document(op="list", args={"p": "/pain/"})

flexus_policy_document(op="activate", args={"p": "/pain/wtp-research-{date}"})
```

## Artifact Schema

```json
{
  "offer_design": {
    "type": "object",
    "description": "Product offer design: packaging model, tier definitions, predictability controls, migration policy, and evidence log.",
    "required": ["product_name", "created_at", "target_segment", "primary_job", "packaging_model", "packaging_rationale", "tiers", "core_features", "predictability_controls", "migration_policy", "confidence", "unresolved_assumptions"],
    "additionalProperties": false,
    "properties": {
      "product_name": {"type": "string"},
      "created_at": {"type": "string", "description": "ISO-8601 UTC timestamp."},
      "target_segment": {"type": "string"},
      "primary_job": {"type": "string", "description": "Primary job-to-be-done this offer solves."},
      "packaging_model": {"type": "string", "enum": ["good_better_best", "base_modules", "single_with_volume", "freemium", "single_offer"]},
      "packaging_rationale": {
        "type": "object",
        "required": ["chosen_for", "rejected_options"],
        "additionalProperties": false,
        "properties": {
          "chosen_for": {"type": "array", "items": {"type": "string"}, "description": "Evidence-backed reasons for selected model."},
          "rejected_options": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["model", "reason_rejected"],
              "additionalProperties": false,
              "properties": {
                "model": {"type": "string", "enum": ["good_better_best", "base_modules", "single_with_volume", "freemium", "single_offer"]},
                "reason_rejected": {"type": "string"}
              }
            }
          }
        }
      },
      "tiers": {
        "type": "array",
        "minItems": 1,
        "maxItems": 5,
        "items": {
          "type": "object",
          "required": ["tier_name", "target_persona", "core_job_served", "included_features", "excluded_features", "key_limits", "upgrade_triggers"],
          "additionalProperties": false,
          "properties": {
            "tier_name": {"type": "string"},
            "target_persona": {"type": "string"},
            "core_job_served": {"type": "string", "description": "Workflow outcome this tier completes."},
            "included_features": {"type": "array", "items": {"type": "string"}},
            "excluded_features": {"type": "array", "items": {"type": "string"}, "description": "Explicit exclusions — not just absent, but declared excluded."},
            "key_limits": {"type": "object", "additionalProperties": true, "description": "Usage limits: seats, API calls, storage, etc."},
            "upgrade_triggers": {"type": "array", "items": {"type": "string"}, "description": "Observable conditions that indicate need for upgrade."}
          }
        }
      },
      "core_features": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["feature", "category", "rationale"],
          "additionalProperties": false,
          "properties": {
            "feature": {"type": "string"},
            "category": {"type": "string", "enum": ["core", "value_add", "segment_specific"]},
            "rationale": {"type": "string", "description": "Evidence-based categorization rationale."}
          }
        }
      },
      "predictability_controls": {
        "type": "object",
        "required": ["allowance_design", "overage_policy", "visibility_surface", "alert_policy", "budget_owner"],
        "additionalProperties": false,
        "properties": {
          "allowance_design": {"type": "string"},
          "overage_policy": {"type": "string"},
          "visibility_surface": {"type": "string"},
          "alert_policy": {"type": "string"},
          "budget_owner": {"type": "string"}
        }
      },
      "migration_policy": {
        "type": "object",
        "required": ["effective_date", "cohort_plan", "grandfathering_policy", "rollback_triggers", "communication_plan"],
        "additionalProperties": false,
        "properties": {
          "effective_date": {"type": "string"},
          "cohort_plan": {"type": "array", "items": {"type": "object", "required": ["cohort_name", "transition_date", "treatment"], "additionalProperties": false, "properties": {"cohort_name": {"type": "string"}, "transition_date": {"type": "string"}, "treatment": {"type": "string"}}}},
          "grandfathering_policy": {"type": "string"},
          "rollback_triggers": {"type": "array", "items": {"type": "string"}},
          "communication_plan": {"type": "array", "items": {"type": "string"}}
        }
      },
      "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
      "unresolved_assumptions": {"type": "array", "items": {"type": "string"}}
    }
  }
}
```
