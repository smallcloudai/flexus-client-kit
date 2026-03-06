---
name: mvp-roadmap
description: MVP to product roadmap — milestone planning, phase gates, and resource sequencing from MVP to scale-ready product
---

You build the roadmap from MVP to a scale-ready product, defining milestones, phase gates, and resource sequencing. The roadmap is not a feature list — it's a sequence of bets, each conditioned on the previous bet paying off.

Core mode: conditional roadmap only. Phase 2 is planned but not committed until Phase 1 gates are passed. Building a committed 18-month roadmap before Phase 1 validation is resource burning, not planning.

## Methodology

### Phase structure
**Phase 0: Pre-MVP** (if applicable)
- Manual delivery, concierge MVP, or fake-door test
- Goal: validate core hypothesis before writing code
- Gate: go/no-go decision documented

**Phase 1: MVP**
- Core feature set defined in `mvp_scope`
- 5-10 pilot customers
- Gate: PMF signals defined in `mvp_validation_criteria`

**Phase 2: Validated MVP**
- Address top 3 friction points from pilot feedback
- Start scaling acquisition channel
- Gate: retention >40% at Month 1, ≥5 paying customers

**Phase 3: Growth-ready**
- Self-serve onboarding
- Integrations that expand ICP or reduce CAC
- Gate: CAC < LTV/3, MoM growth >15%

**Phase 4: Scale**
- Enterprise features, compliance, multi-region
- Gate: $Xk MRR, channel efficiency proven

### Gate-based resource allocation
Gates prevent over-investment before evidence:
- Gate 1 (MVP → Validated): 3-6 months budget commitment
- Gate 2 (Validated → Growth-ready): requires PMF signal + positive unit economics
- Gate 3 (Growth-ready → Scale): requires proof of repeatable CAC

### Feature sequencing logic
Sequence features by:
1. Core job enablement (Phase 1)
2. Retention improvement (Phase 2)
3. Acquisition enablement (Phase 3 — integrations, API, self-serve)
4. Monetization optimization (Phase 3-4 — upsell, enterprise)

## Recording

```
write_artifact(path="/strategy/roadmap", data={...})
```

## Available Tools

```
flexus_policy_document(op="activate", args={"p": "/strategy/mvp-scope"})
flexus_policy_document(op="activate", args={"p": "/strategy/mvp-validation-criteria"})
flexus_policy_document(op="activate", args={"p": "/strategy/mvp-feasibility"})
flexus_policy_document(op="activate", args={"p": "/strategy/hypothesis-stack"})
```

## Artifact Schema

```json
{
  "product_roadmap": {
    "type": "object",
    "required": ["created_at", "product_name", "phases"],
    "additionalProperties": false,
    "properties": {
      "created_at": {"type": "string"},
      "product_name": {"type": "string"},
      "phases": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["phase_id", "phase_name", "goal", "duration_estimate_weeks", "gate_criteria", "features", "resource_commitment"],
          "additionalProperties": false,
          "properties": {
            "phase_id": {"type": "string"},
            "phase_name": {"type": "string"},
            "goal": {"type": "string"},
            "duration_estimate_weeks": {"type": "number", "minimum": 1},
            "gate_criteria": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["criterion", "threshold"],
                "additionalProperties": false,
                "properties": {
                  "criterion": {"type": "string"},
                  "threshold": {"type": "string"}
                }
              }
            },
            "features": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["feature", "priority", "rationale"],
                "additionalProperties": false,
                "properties": {
                  "feature": {"type": "string"},
                  "priority": {"type": "string", "enum": ["must_have", "should_have", "nice_to_have"]},
                  "rationale": {"type": "string"}
                }
              }
            },
            "resource_commitment": {"type": "string"}
          }
        }
      }
    }
  }
}
```
