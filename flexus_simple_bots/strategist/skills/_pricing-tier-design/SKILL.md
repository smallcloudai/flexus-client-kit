---
name: pricing-tier-design
description: Pricing tier structure design — price points, tier names, feature fencing, upgrade triggers, and upsell architecture
---

You design the specific price points and tier structure for each packaging tier. Inputs are: pricing model (from `pricing-model-design`), offer design (from `offer-design`), and WTP research (from `pain-wtp-research`).

Core mode: price is anchored to WTP evidence, not to cost-plus or gut feel. The bottom tier must be low enough to reduce friction for initial adoption. The top tier must capture value from power users without causing mid-market to over-pay.

## Methodology

### Price point derivation from WTP data
From Van Westendorp PSM results:
- Bottom tier price: above "too cheap" threshold (≥ 20th percentile "cheap" response)
- Top tier price: below "stress point" for target buyer (≤ 80th percentile "expensive" response)
- Mid tier: optimal price point from PSM (intersection of "expensive" and "not cheap")

Adjust downward by 15-25% to account for the gap between stated WTP and actual WTP.

### Tier naming
Effective tier names:
- Reflect persona identity, not internal product labels ("Starter/Pro/Enterprise" vs. "Individual/Team/Organization")
- Avoid "Basic" (sounds cheap and limiting)
- Can use verb/adjective naming ("Launch/Grow/Scale" for a SaaS with an activation metaphor)

### Feature fencing logic
Strong feature fences are based on:
- **Usage limits** that create natural upgrade pressure (e.g., "5 projects/month")
- **Collaboration features** that require team upgrade (single user gets core; team features require Pro)
- **Reporting/analytics** that managers need but individual users don't

Weak feature fences:
- Arbitrary limitations with no UX rationale
- Hiding features that the free tier should include to be useful

### Upgrade trigger design
What causes a user to upgrade?
1. They hit a usage limit (natural trigger — design the limit deliberately)
2. They invite a collaborator and discover team features require upgrade
3. They want a specific report/export that's behind a paywall

Map each upgrade trigger to an expected timeline (e.g., "typical user hits the 5-project limit in week 3").

## Recording

```
write_artifact(path="/strategy/pricing-tiers", data={...})
```

## Available Tools

```
flexus_policy_document(op="activate", args={"p": "/strategy/pricing-model"})
flexus_policy_document(op="activate", args={"p": "/strategy/offer-design"})
flexus_policy_document(op="list", args={"p": "/pain/"})
```
