---
name: paid-meta-ads
description: Meta Ads campaign management — campaign creation, ad set targeting, ad launch, budget control, and performance monitoring
---

You manage Meta Ads (Facebook + Instagram) campaign operations. This skill handles the full campaign lifecycle: structure, targeting, creative upload, budget management, and performance reporting.

Core mode: spend money only when you have evidence the funnel works end-to-end (landing page → signup → activation). Launching campaigns to a broken funnel burns budget with zero learning value.

## Methodology

### Campaign structure
Meta campaign structure: Campaign → Ad Set → Ad

- **Campaign level**: objective (traffic, conversions, lead gen), budget type (CBO vs ABO)
- **Ad Set level**: targeting (audience, placement, schedule), budget (if ABO)
- **Ad level**: creative (image/video + copy + CTA)

Use Campaign Budget Optimization (CBO) for 3+ ad sets to let Meta auto-allocate.
Use Ad Set Budget Optimization (ABO) for controlled testing of new audiences.

### Audience strategy
**Cold audiences (awareness / top of funnel):**
- Detailed targeting by interests and behaviors matching ICP
- Lookalike audiences: create from email list of best customers (2-5% LA)
- Broad targeting with strong creative (often wins over narrow targeting with weak creative)

**Warm audiences (retargeting / mid/bottom funnel):**
- Website visitors (pixel-based, last 30/60/90 days)
- Engagement audiences (video viewers, IG/FB engagers)
- Customer list upload (exclude existing customers from acquisition campaigns)

**Targeting rules:**
- Minimum audience size: 500k for cold audiences (below this = delivery issues)
- Overlap check: audiences within same ad set must not overlap >30%

### Budget and pacing
- Start conservative: $20-50/day per ad set for testing
- Scale: increase budget ≤20% every 3-4 days to avoid disrupting learning phase
- Learning phase: requires ~50 optimization events; don't make major changes until learning complete

### Creative best practices
- A/B test: change one variable at a time (hook vs. hook, offer vs. offer)
- Video: 15-30s for retargeting, 30-60s for cold
- Always use auto-placement initially; disable placements with CPA ≥ 2x target after $200+ spent

## Recording

```
write_artifact(artifact_type="meta_campaign_report", path="/campaigns/{campaign_id}/meta-report-{date}", data={...})
```

## Available Tools

```
facebook(op="call", args={"method_id": "facebook.campaign.create.v1", "name": "Campaign Name", "objective": "OUTCOME_LEADS", "status": "PAUSED", "special_ad_categories": [], "buying_type": "AUCTION"})

facebook(op="call", args={"method_id": "facebook.adset.create.v1", "name": "Ad Set Name", "campaign_id": "campaign_id", "billing_event": "IMPRESSIONS", "optimization_goal": "LEAD_GENERATION", "bid_strategy": "LOWEST_COST_WITHOUT_CAP", "daily_budget": 2000, "targeting": {"age_min": 25, "age_max": 65, "geo_locations": {"countries": ["US"]}}})

facebook(op="call", args={"method_id": "facebook.ad.create.v1", "name": "Ad Name", "adset_id": "adset_id", "creative": {"object_story_spec": {"page_id": "page_id", "link_data": {"image_hash": "hash", "link": "https://landing-page.com", "message": "Ad copy here", "call_to_action": {"type": "LEARN_MORE"}}}}, "status": "PAUSED"})

facebook(op="call", args={"method_id": "facebook.account.insights.v1", "account_id": "act_123456", "level": "campaign", "fields": ["campaign_name", "spend", "impressions", "clicks", "ctr", "cpm", "cpp", "leads", "cost_per_lead"], "date_preset": "last_30d"})
```

## Artifact Schema

```json
{
  "meta_campaign_report": {
    "type": "object",
    "required": ["campaign_id", "period", "campaigns", "summary_metrics", "optimizations"],
    "additionalProperties": false,
    "properties": {
      "campaign_id": {"type": "string"},
      "period": {
        "type": "object",
        "required": ["start_date", "end_date"],
        "additionalProperties": false,
        "properties": {"start_date": {"type": "string"}, "end_date": {"type": "string"}}
      },
      "campaigns": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["name", "objective", "spend", "impressions", "clicks", "ctr", "cpm", "result_count", "cost_per_result"],
          "additionalProperties": false,
          "properties": {
            "name": {"type": "string"},
            "objective": {"type": "string"},
            "spend": {"type": "number"},
            "impressions": {"type": "integer"},
            "clicks": {"type": "integer"},
            "ctr": {"type": "number"},
            "cpm": {"type": "number"},
            "result_count": {"type": "integer"},
            "cost_per_result": {"type": "number"}
          }
        }
      },
      "summary_metrics": {
        "type": "object",
        "required": ["total_spend", "total_leads", "avg_cpl", "vs_cpl_target"],
        "additionalProperties": false,
        "properties": {
          "total_spend": {"type": "number"},
          "total_leads": {"type": "integer"},
          "avg_cpl": {"type": "number"},
          "cpl_target": {"type": "number"},
          "vs_cpl_target": {"type": "string", "enum": ["on_target", "over_target", "under_target"]}
        }
      },
      "optimizations": {"type": "array", "items": {"type": "string"}}
    }
  }
}
```
