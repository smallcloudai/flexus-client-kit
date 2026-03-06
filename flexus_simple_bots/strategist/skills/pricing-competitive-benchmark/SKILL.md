---
name: pricing-competitive-benchmark
description: Competitive pricing benchmark — document competitor pricing structures, identify pricing gaps, and validate positioning vs. price
---

You benchmark your pricing against competitors to identify positioning vs. price gaps, avoid underpricing relative to inferior alternatives, and support enterprise pricing negotiations.

Core mode: competitor pricing pages change frequently. Treat any benchmark as a point-in-time snapshot. Always note when the data was collected. Pricing that differs significantly from category norm requires explicit justification.

## Methodology

### Competitor pricing data collection
Sources:
- Competitor pricing pages (directly scraped via web)
- G2 Pricing tab (often contains community-validated pricing with tier structures)
- Capterra pricing section
- Trustpilot and reddit where users discuss pricing complaints

For each competitor, document:
- Pricing model (flat, per-seat, consumption)
- Tier names and price points (or "pricing on request" if enterprise)
- What's included at each tier
- Discount structure (annual discount %, enterprise negotiation signals)

### Category norm analysis
Establish the category norm:
- Median price for comparable tier across 3-5 direct competitors
- Common pricing model in the category
- Common value metric in the category

Deviations from category norm require justification:
- Premium over norm: "We charge more because X" (must be provable)
- Discount vs. norm: "We're cheaper because Y" (must be sustainable)

### Positioning-price alignment check
The price signal must be consistent with positioning:
- If positioned as "premium for enterprise" → must be priced above median
- If positioned as "best value for SMB" → must be priced below category median for relevant tier
- Mismatch between positioning and price = confused buyer perception

## Recording

```
write_artifact(path="/strategy/pricing-benchmark", data={...})
```

## Available Tools

```
web(open=[{"url": "https://competitor.com/pricing"}])

g2(op="call", args={"method_id": "g2.products.list.v1", "filter[name]": "competitor name"})

similarweb(op="call", args={"method_id": "similarweb.traffic_and_engagement.get.v1", "domain": "competitor.com"})

flexus_policy_document(op="activate", args={"p": "/strategy/positioning-map"})
```
