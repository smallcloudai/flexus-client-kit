---
name: gtm-channel-strategy
description: Go-to-market channel strategy — channel selection, sequencing, CAC targets, and channel fit analysis
---

You select and sequence go-to-market channels based on ICP, offer type, and stage of business. Channel strategy determines where to find potential customers, at what cost, and in what sequence to de-risk the sales motion.

Core mode: do fewer channels better, not many channels poorly. A startup that runs 5 channels simultaneously rarely has signal on which one works. Run 1-2 channels to saturation before adding a third.

## Methodology

### Channel fit analysis
Match channel to offer type:
- **Outbound sales**: high ACV ($10k+), complex sale, defined ICP, small market — use when you can identify decision-makers by name
- **Inbound content/SEO**: longer sales cycle acceptable, educational buying journey, competitive search volume exists — takes 6-18 months to compound
- **Paid acquisition**: measurable LTV, clear landing page → signup → monetization funnel, positive unit economics — expensive to learn but fast to scale
- **Product-led growth**: self-serve product, low ACV, large market, viral/collaboration mechanic — requires product to be the sales motion
- **Community/partnerships**: ICP concentrates in identifiable communities or buys through specific partners — requires relationship investment

### Stage-appropriate sequencing
Early stage (0-5 customers):
- Founder-led outbound: fastest to learn, zero CAC
- Warm network: referrals from prior relationships
- Manual community participation: Reddit, Slack communities, industry forums

Stage 1 (5-50 customers):
- Outbound systematized (SDR or automated sequences)
- 1-2 content pieces targeting core ICP search queries
- Partnership with 1 complementary vendor

Stage 2 (50+ customers):
- Add paid channel if unit economics proven
- Product-led motion if product supports it

### CAC target setting
CAC must be < LTV / 3 to be viable.
Calculate: max CAC = (ARPU × gross margin) × (avg customer lifetime months) / 3

Set per-channel CAC targets before running campaigns.

### Channel selection decision criteria
| Criterion | Weight | Channel A Score | Channel B Score |
|-----------|--------|----------------|----------------|
| ICP concentration | 30% | ... | ... |
| Time to first customer | 25% | ... | ... |
| CAC predictability | 25% | ... | ... |
| Scalability | 20% | ... | ... |

## Recording

```
write_artifact(artifact_type="gtm_channel_strategy", path="/strategy/gtm-channel-strategy", data={...})
```

## Available Tools

```
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})
flexus_policy_document(op="activate", args={"p": "/strategy/positioning-map"})
flexus_policy_document(op="activate", args={"p": "/strategy/pricing-tiers"})
flexus_policy_document(op="activate", args={"p": "/strategy/hypothesis-stack"})
```

## Artifact Schema

```json
{
  "gtm_channel_strategy": {
    "type": "object",
    "required": ["created_at", "stage", "primary_channels", "channel_sequence", "cac_targets", "exclusions"],
    "additionalProperties": false,
    "properties": {
      "created_at": {"type": "string"},
      "stage": {"type": "string", "enum": ["pre_pmf", "post_pmf_early", "growth", "scale"]},
      "primary_channels": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["channel", "rationale", "icp_fit_score", "time_to_first_result_weeks", "cac_range", "scalability"],
          "additionalProperties": false,
          "properties": {
            "channel": {"type": "string", "enum": ["founder_outbound", "sdr_outbound", "inbound_seo", "paid_search", "paid_social", "product_led", "community", "partnerships", "events"]},
            "rationale": {"type": "string"},
            "icp_fit_score": {"type": "number", "minimum": 0, "maximum": 10},
            "time_to_first_result_weeks": {"type": "integer", "minimum": 0},
            "cac_range": {"type": "string"},
            "scalability": {"type": "string", "enum": ["high", "medium", "low"]}
          }
        }
      },
      "channel_sequence": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["phase", "channels", "trigger_for_next_phase"],
          "additionalProperties": false,
          "properties": {
            "phase": {"type": "string"},
            "channels": {"type": "array", "items": {"type": "string"}},
            "trigger_for_next_phase": {"type": "string"}
          }
        }
      },
      "cac_targets": {
        "type": "object",
        "required": ["max_cac", "cac_per_channel"],
        "additionalProperties": false,
        "properties": {
          "max_cac": {"type": "number"},
          "ltv_estimate": {"type": "number"},
          "cac_per_channel": {"type": "object"}
        }
      },
      "exclusions": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["channel", "reason"],
          "additionalProperties": false,
          "properties": {"channel": {"type": "string"}, "reason": {"type": "string"}}
        }
      }
    }
  }
}
```
