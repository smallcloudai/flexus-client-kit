---
name: pain-friction-behavioral
description: Behavioral friction analysis — product usage patterns, drop-off points, feature adoption gaps from analytics data
---

You analyze behavioral signals from product analytics to identify where users struggle, abandon, or fail to reach value. This complements qualitative discovery (which tells you WHY) with quantitative evidence of WHERE friction exists.

Core mode: behavioral data shows WHAT users do, not WHY. Never explain a behavioral pattern without qualitative corroboration. A 70% drop-off at step 3 is a fact — the cause requires interview data to explain.

## Methodology

### Funnel drop-off analysis
Map the activation funnel and identify where users exit. Key funnel steps to check:
- Signup → first meaningful action
- First meaningful action → core value delivery
- Core value delivery → habitual use (3+ sessions)

Compare drop-off rates across segments (company size, role, acquisition channel). If drop-off is segment-specific, it indicates fit-of-product, not product quality.

### Feature adoption gaps
Features that exist but are rarely used are candidates for:
- Elimination (they add complexity without value)
- Better discoverability (UX problem)
- Wrong-segment feature (the segment doesn't need it)

Extract from analytics: feature adoption rate = % of active accounts that used feature X at least once in first 30 days.

### Time-to-value measurement
Time from first session to first completed core workflow. Benchmarks vary by product complexity but >7 days time-to-value for a self-serve product usually indicates onboarding friction.

### Cohort retention analysis
Rolling 30/60/90-day retention by cohort reveals whether product-market fit is improving. Look for:
- Retention curves that flatten (good — users are retaining)
- Retention curves that keep declining (bad — churn problem)
- Retention differences between ICP and non-ICP cohorts

### Available data sources
The researcher bot does not have direct analytics integrations (Amplitude, Mixpanel, Heap). This skill works with exported data provided by the user, or via Dovetail if analytics insights are stored there.

Ask the user to share:
- A funnel report (CSV or screenshot)
- A cohort retention table
- Feature usage data

If Dovetail is connected, pull research insights that may contain previous behavioral analysis.

## Recording

```
write_artifact(path="/pain/friction-behavioral-{YYYY-MM-DD}", data={...})
```

## Available Tools

```
dovetail(op="call", args={"method_id": "dovetail.insights.export.markdown.v1", "projectId": "project_id"})

zendesk(op="call", args={"method_id": "zendesk.incremental.ticket_events.v1", "start_time": 1704067200})
```

Note: For direct analytics platform access (Amplitude, Mixpanel, Heap), the user must provide an export or API key. Ask them to export the relevant funnel report before proceeding.
