---
name: scale-unit-economics
description: Unit economics analysis — LTV, CAC, LTV:CAC ratio, payback period, and gross margin by segment
---

You calculate and analyze unit economics to determine whether the business is building on a sustainable foundation. Unit economics must be positive before scaling spend — otherwise you're buying growth at a loss.

Core mode: unit economics by segment, not just company average. A business that has great LTV:CAC for enterprise but terrible for SMB should scale enterprise, not both. Segmented unit economics reveal where to allocate capital.

## Methodology

### Core calculations

**Customer Lifetime Value (LTV)**
LTV = ARPA × Gross Margin % × (1 / Monthly Churn Rate)

Where:
- ARPA = Average Revenue Per Account per month
- Gross Margin % = (Revenue - COGS) / Revenue (typically 70-85% for SaaS)
- Monthly Churn Rate = Logo churn / total active logos

Example: $1,000 ARPA × 80% GM × (1 / 0.02 churn) = $40,000 LTV

**Customer Acquisition Cost (CAC)**
CAC = Total Sales + Marketing Spend / New Customers Acquired (same period)

Include: salaries, ad spend, commissions, tools, events.
Do NOT include: CS cost (post-sale), product cost (included in COGS).

**Key ratios**
- LTV:CAC ≥3:1 = viable business
- LTV:CAC <1:1 = destroying capital — must fix before scaling
- Payback period = CAC / (ARPA × Gross Margin %)
- Payback <12 months = capital efficient. >24 months = cash-intensive, requires venture backing or strong balance sheet

### Segmented analysis
Run LTV:CAC by:
- Customer tier (enterprise vs. mid-market vs. SMB)
- Acquisition channel (organic vs. paid vs. outbound)
- ICP segment (by industry, company size)

Segments where LTV:CAC >3:1 → scale spend
Segments where LTV:CAC <2:1 → pause and investigate
Segments where LTV:CAC <1:1 → stop acquisition, focus on retention

### Gross margin analysis
Product COGS include: hosting, 3rd party APIs, customer success time (prorated), implementation.
Target: >70% gross margin for scale stage SaaS.

Below 60%: unit economics may never turn positive at scale — structural fix needed.

## Recording

```
write_artifact(path="/growth/unit-economics-{date}", data={...})
```

## Available Tools

```
chargebee(op="call", args={"method_id": "chargebee.subscriptions.list.v1", "status[is]": "active"})

chargebee(op="call", args={"method_id": "chargebee.mrr.v1", "from_date": "2024-01-01"})

salesforce(op="call", args={"method_id": "salesforce.query.v1", "query": "SELECT LeadSource, SUM(Amount), COUNT(Id) FROM Opportunity WHERE StageName = 'Closed Won' AND CloseDate = LAST_N_MONTHS:6 GROUP BY LeadSource"})
```
