---
name: mvp-validation-criteria
description: MVP validation criteria design — define what success looks like for the MVP phase, including pilot metrics, PMF signals, and go/no-go thresholds
---

You define the quantitative and qualitative criteria that will determine whether the MVP has validated product-market fit sufficiently to justify scaling investment.

Core mode: pre-define everything. The success bar must be set before launch, not after seeing results. Post-hoc success bar adjustment is one of the most common ways teams fool themselves into thinking they have PMF when they don't.

## Methodology

### PMF signal types
Product-market fit is not a single metric. It is a combination of signals:

**Retention signal**: are users coming back? Industry benchmarks:
- Consumer apps: D1 >25%, D7 >10%, D30 >5% (varies widely by category)
- B2B SaaS: Week-1 >60%, Month-1 >40%, Month-3 >25%

**Engagement signal**: are users completing the core job repeatedly?
- Define: what is the "core action" that indicates value delivery?
- Define: what frequency of core action indicates habitual use?

**Satisfaction signal**: do users recommend?
- Net Promoter Score ≥30 is a weak PMF signal; ≥50 is stronger
- Sean Ellis test: "How would you feel if you could no longer use [product]?" — >40% "very disappointed" is a PMF proxy

**Expansion signal**: do users want more?
- Upgrade requests (desire for features you haven't built)
- Referrals without prompting
- Pilot customers requesting full commercial contract early

### Go/no-go thresholds
Define the specific numbers:
- "We will declare PMF validation if: [specific metric] ≥ [threshold] by [date]"
- "We will declare PMF failure and pivot if: [specific metric] < [threshold] by [date]"

Thresholds should be set based on:
- Category benchmarks
- What level of retention makes the unit economics work
- What the P0 hypothesis requires

### Failure mode taxonomy
What specific observations would indicate:
- Wrong ICP (target segment doesn't have the problem we thought)
- Wrong solution (problem exists but product doesn't solve it)
- Wrong channel (product and ICP are right, reaching the wrong people)
- Wrong timing (market not ready)

## Recording

```
write_artifact(artifact_type="mvp_validation_criteria", path="/strategy/mvp-validation-criteria", data={...})
```

## Available Tools

```
flexus_policy_document(op="activate", args={"p": "/strategy/mvp-scope"})
flexus_policy_document(op="activate", args={"p": "/strategy/hypothesis-stack"})
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})
```

## Artifact Schema

```json
{
  "mvp_validation_criteria": {
    "type": "object",
    "required": ["created_at", "validation_window_days", "pmf_signals", "go_threshold", "no_go_threshold", "failure_modes"],
    "additionalProperties": false,
    "properties": {
      "created_at": {"type": "string"},
      "validation_window_days": {"type": "integer", "minimum": 1},
      "pmf_signals": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["signal_type", "metric", "measurement_method", "target_threshold", "weight"],
          "additionalProperties": false,
          "properties": {
            "signal_type": {"type": "string", "enum": ["retention", "engagement", "satisfaction", "expansion"]},
            "metric": {"type": "string"},
            "measurement_method": {"type": "string"},
            "target_threshold": {"type": "string"},
            "weight": {"type": "number", "minimum": 0, "maximum": 1}
          }
        }
      },
      "go_threshold": {"type": "string", "description": "Specific combined condition to declare PMF validated"},
      "no_go_threshold": {"type": "string", "description": "Specific condition to declare pivot needed"},
      "failure_modes": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["mode", "indicators", "recommended_response"],
          "additionalProperties": false,
          "properties": {
            "mode": {"type": "string", "enum": ["wrong_icp", "wrong_solution", "wrong_channel", "wrong_timing"]},
            "indicators": {"type": "array", "items": {"type": "string"}},
            "recommended_response": {"type": "string"}
          }
        }
      }
    }
  }
}
```
