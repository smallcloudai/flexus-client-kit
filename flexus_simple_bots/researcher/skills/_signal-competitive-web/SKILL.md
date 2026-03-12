---
name: signal-competitive-web
description: Competitor web traffic and marketplace demand signal detection
---

You are detecting competitive traction signals from web traffic and marketplace data for one competitor set or category per run.

Core mode: evidence-first. Traffic and marketplace data are estimates, not ground truth. Always state confidence range. Do not compare raw numbers across providers — each has its own methodology.

## Methodology

### Competitor web traffic
Use `similarweb` to benchmark competitor traffic volume, trends, and acquisition channels.

Key questions:
- Is competitor traffic growing or shrinking over the last 3-6 months?
- What channels drive their traffic (SEO vs paid vs direct vs referral)?
- Which geographies are they strong in?
- Are there new or similar sites gaining traction?

Patterns to detect:
- Competitor acceleration: >20% MoM traffic growth = market pull
- Competitor contraction: sustained drop = market share opportunity
- Channel concentration: competitor relies heavily on one channel = vulnerability
- Traffic similarity: discover adjacent competitors via `similar_sites`

### Marketplace demand
Use `amazon` catalog and pricing APIs to detect product category demand:
- Category search volume via product counts and rank
- Pricing pressure: price spread between top sellers vs median
- Best-seller rank trends: consistent rank improvement = growing demand

Use `ebay` marketplace insights to see actual transaction velocity in a category.

### Data interpretation rules
- Similarweb numbers have ±20% variance — use for direction, not absolute truth
- Amazon BSR (Best Seller Rank) changes daily — compare relative rank, not absolute
- Never cite traffic numbers without stating "estimated" and provider name

## Recording

```
write_artifact(
  artifact_type="signal_competitive_web",
  path="/signals/competitive-web-{YYYY-MM-DD}",
  data={...}
)
```

## Available Tools

```
similarweb(op="call", args={"method_id": "similarweb.traffic_and_engagement.get.v1", "domain": "competitor.com", "start_date": "2024-01", "end_date": "2024-12", "country": "us", "granularity": "monthly"})

similarweb(op="call", args={"method_id": "similarweb.traffic_sources.get.v1", "domain": "competitor.com", "start_date": "2024-01", "end_date": "2024-12", "country": "us"})

similarweb(op="call", args={"method_id": "similarweb.traffic_geography.get.v1", "domain": "competitor.com", "start_date": "2024-01", "end_date": "2024-12"})

similarweb(op="call", args={"method_id": "similarweb.similar_sites.get.v1", "domain": "competitor.com"})

amazon(op="call", args={"method_id": "amazon.catalog.search_items.v1", "keywords": "product category", "marketplaceIds": ["ATVPDKIKX0DER"]})

amazon(op="call", args={"method_id": "amazon.pricing.get_item_offers_batch.v1", "requests": [{"uri": "/products/pricing/v0/items/{asin}/offers", "method": "GET", "MarketplaceId": "ATVPDKIKX0DER", "ItemCondition": "New"}]})

ebay(op="call", args={"method_id": "ebay.browse.search.v1", "q": "product category", "sort": "newlyListed", "limit": 25})

ebay(op="call", args={"method_id": "ebay.marketplace_insights.item_sales_search.v1", "q": "product category", "limit": 25})
```
