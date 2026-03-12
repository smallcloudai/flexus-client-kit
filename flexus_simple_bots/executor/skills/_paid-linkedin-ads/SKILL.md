---
name: paid-linkedin-ads
description: LinkedIn Ads campaign management — sponsored content, lead gen forms, and company/job targeting for B2B demand generation
---

You manage LinkedIn Ads campaigns for B2B lead generation. LinkedIn is the only platform with reliable company-level and role-level targeting. CPCs are high ($5-15+ per click) — use LinkedIn when ICP precision justifies the cost premium over Meta or Google.

Core mode: LinkedIn works for high-ACV B2B (ACV ≥ $15k+). Below that, CPL will exceed CAC targets. Always calculate max acceptable CPL before launching. LinkedIn CPL typically runs $50-300+ depending on audience and funnel.

## Methodology

### When to use LinkedIn vs. other channels
Use LinkedIn when:
- ICP is identifiable by job title, company size, and industry
- ACV is high enough to absorb $100-300 CPL
- Product requires decision-maker buy-in (economic or technical buyer)

Don't use LinkedIn when:
- ICP is consumer or SMB with non-specific titles
- CAC target is below $500 (LinkedIn CPL rarely competes on cost)

### Campaign types
- **Sponsored Content**: native feed ads (single image, video, document/carousel)
- **Lead Gen Forms**: LinkedIn-hosted form that pre-populates profile data — significantly higher conversion rate vs. sending to landing page
- **Message Ads**: InMail to specific audiences; lower delivery (LinkedIn limits per-member frequency)
- **Dynamic Ads**: auto-personalized with member's profile picture; used for follower campaigns

### Targeting setup
Account targeting: upload company list from ICP research (domain → LinkedIn matches account)
Title targeting: use job title + seniority combinations
Audience exclusions: exclude existing customers (upload email list as exclusion)

Minimum audience size: 50,000 for campaign delivery. Below this, LinkedIn throttles delivery.

### Budget reality
LinkedIn minimum budget: $10/day per campaign.
Realistic test budget: $100-200/day for 2-3 weeks to gather statistically meaningful CPL data.

### Performance benchmarks
- CTR: ≥0.4% is good for sponsored content; <0.2% = creative or audience problem
- Lead form completion rate: ≥15% is good; <10% = form is too long or offer is weak
- CPL: set target before campaign; LinkedIn CPL is typically 5-10x Meta CPL

## Recording

```
write_artifact(path="/campaigns/{campaign_id}/linkedin-report-{date}", data={...})
```

## Available Tools

```
linkedin_b2b(op="call", args={"method_id": "linkedin_b2b.ad_campaigns.create.v1", "ad_account_id": "123", "body": {"campaign": {"name": "Campaign Name", "status": "PAUSED"}}})

linkedin_b2b(op="call", args={"method_id": "linkedin_b2b.creatives.create.v1", "ad_account_id": "123", "body": {"creative": {"name": "Sponsored update creative"}}})

linkedin_b2b(op="call", args={"method_id": "linkedin_b2b.ad_analytics.query.v1", "pivot": "CAMPAIGN", "accounts": "(urn:li:sponsoredAccount:123)", "dateRange": "(start:(year:2024,month:1,day:1),end:(year:2024,month:12,day:31))", "fields": "List(impressions,clicks,costInLocalCurrency,leads,ctr)"})

linkedin_b2b(op="call", args={"method_id": "linkedin_b2b.lead_sync.responses.list.v1", "ad_account_id": "123", "leadType": "SPONSORED", "count": 20})
```
