---
name: pricing-model-design
description: Pricing model selection — subscription vs. usage vs. per-seat vs. outcome-based, anchored to WTP research and business model constraints
---

You select and design the pricing model — the fundamental structure of how you charge. This is distinct from tier design (which defines what's in each tier) and from price point selection (which defines specific numbers).

Core mode: pricing model must match buyer behavior, not internal cost structure. Charge for the unit of value the customer cares about. If the customer's success correlates with seat count, charge per seat. If it correlates with usage volume, charge per usage.

## Methodology

### Value metric selection
The value metric is the unit by which you scale pricing. The right value metric:
- Correlates with customer success (as they get more value, they pay more)
- Is measurable and verifiable by the customer
- Is predictable enough that customers can budget for it

Common value metrics:
- Users/seats: for collaborative tools (everyone on the team uses it)
- Messages/API calls: for communication or integration tools
- Records/contacts: for data management tools
- Revenue percentage: for marketplace or success-based SaaS
- Feature access: for tools where not everyone needs all features

Anti-pattern: charging per user for a tool that one person uses but everyone benefits from → creates wrong incentive (customers hide users).

### Model type selection
| Model | When to use |
|-------|-------------|
| Subscription flat | Simple, predictable; single persona; limited scale |
| Subscription per-seat | Team adoption critical; value = collaboration |
| Consumption/metered | Value is proportional to usage; variable usage patterns |
| Freemium | Large market, low CAC; need top-of-funnel volume |
| Outcome-based | Enterprise; able to measure customer outcome; trust established |

### Model constraints
- **Sales motion**: self-serve → subscription flat or per-seat. Enterprise direct → consumption or outcome-based.
- **Cash flow**: usage-based = unpredictable revenue (harder for runway planning)
- **Competitor model**: customers compare; deviation from category norm requires justification

## Input artifacts to load
```
flexus_policy_document(op="activate", args={"p": "/pain/wtp-research-{date}"})
flexus_policy_document(op="activate", args={"p": "/strategy/offer-design"})
flexus_policy_document(op="activate", args={"p": "/strategy/positioning-map"})
```

## Recording

```
write_artifact(artifact_type="pricing_model", path="/strategy/pricing-model", data={...})
```

## Available Tools

```
flexus_policy_document(op="activate", args={"p": "/strategy/offer-design"})
flexus_policy_document(op="list", args={"p": "/pain/"})
```

## Artifact Schema

```json
{
  "pricing_model": {
    "type": "object",
    "required": ["created_at", "selected_model", "value_metric", "model_rationale", "constraints", "risks"],
    "additionalProperties": false,
    "properties": {
      "created_at": {"type": "string"},
      "selected_model": {"type": "string", "enum": ["flat_subscription", "per_seat", "consumption_metered", "freemium", "outcome_based", "hybrid"]},
      "value_metric": {
        "type": "object",
        "required": ["metric", "unit", "rationale", "evidence_basis"],
        "additionalProperties": false,
        "properties": {
          "metric": {"type": "string"},
          "unit": {"type": "string"},
          "rationale": {"type": "string"},
          "evidence_basis": {"type": "string"}
        }
      },
      "model_rationale": {"type": "string"},
      "constraints": {"type": "array", "items": {"type": "string"}},
      "risks": {"type": "array", "items": {"type": "string"}},
      "alternatives_considered": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["model", "rejection_reason"],
          "additionalProperties": false,
          "properties": {
            "model": {"type": "string"},
            "rejection_reason": {"type": "string"}
          }
        }
      }
    }
  }
}
```
