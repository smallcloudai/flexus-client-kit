---
name: channel-performance
description: Channel performance tracking — CAC, lead volume, conversion rates, and efficiency benchmarks across all acquisition channels
---

You measure and report the efficiency of all acquisition channels. Channel performance data drives budget allocation decisions — moving spend from underperforming channels to overperforming ones is the single highest-leverage allocation lever.

Core mode: compare apples to apples. CAC must be calculated with consistent attribution methodology. If paid ads use last-touch attribution and outbound uses first-touch, the comparison is invalid. Define attribution model upfront, apply consistently.

## Methodology

### Channel metrics framework
For each active channel, track:
- **Volume**: leads generated, meetings booked, qualified opportunities
- **Conversion rates**: lead-to-meeting, meeting-to-qualified, qualified-to-closed
- **Cost**: spend (paid) or time cost (outbound), total channel cost
- **CAC**: total channel cost / new customers from that channel
- **Velocity**: average days from channel entry to close

### Attribution methodology (document your choice)
**Last-touch**: attribute the deal to the last channel the customer engaged with before converting. Simple, undervalues awareness channels (SEO, social).

**First-touch**: attribute to the first channel. Better for demand gen understanding, undervalues bottom-funnel channels.

**Multi-touch linear**: distribute credit equally across all touchpoints. More accurate, harder to track.

Document the model you use and apply it consistently. Don't switch mid-quarter.

### Channel efficiency comparison
For each channel:
- CAC vs. target CAC (from `gtm_channel_strategy`)
- Payback period: CAC / (ARPA × gross margin)
- Qualified opportunity rate: what % of leads are actually qualified?

Reallocation decision rules:
- CAC > 2x target for 3+ months → pause channel, investigate
- Payback period > 18 months → channel may be unsustainable, review pricing
- Low qualified rate (<20%) → targeting or messaging problem, not volume problem

### GA4 vs. CRM reconciliation
GA4 tracks traffic and landing page conversions. CRM tracks pipeline. Reconcile weekly:
- If GA4 shows signups but CRM shows fewer SQLs → MQL-to-SQL conversion issue
- If CRM shows deals with no originating channel → attribution gap

## Recording

```
write_artifact(path="/growth/channel-performance-{date}", data={...})
```

## Available Tools

```
ga4(op="call", args={"method_id": "ga4.data.run_report.v1", "property": "properties/123456", "dateRanges": [{"startDate": "30daysAgo", "endDate": "today"}], "dimensions": [{"name": "sessionDefaultChannelGroup"}], "metrics": [{"name": "sessions"}, {"name": "newUsers"}, {"name": "conversions"}]})

mixpanel(op="call", args={"method_id": "mixpanel.query.insights.v1", "project_id": "proj_id", "event": "signup_completed", "from_date": "2024-01-01"})

salesforce(op="call", args={"method_id": "salesforce.query.v1", "query": "SELECT LeadSource, COUNT(Id) total, SUM(Amount) arr FROM Opportunity WHERE StageName = 'Closed Won' AND CloseDate = THIS_YEAR GROUP BY LeadSource"})

hubspot(op="call", args={"method_id": "hubspot.analytics.sessions.v1", "breakdown": "source", "period": "month", "start": "2024-01-01", "end": "2024-12-31"})
```
