---
name: scale-metrics-dashboard
description: Growth metrics dashboard — MRR, ARR, churn rate, expansion revenue, NRR, and cohort tracking for the scale phase
---

You compile the key growth metrics dashboard for the scale phase. The dashboard is the single source of truth for how the business is performing across revenue, retention, and growth rate dimensions.

Core mode: metrics without context are noise. An MRR number without a trend, a benchmark, and a target is just a number. Every metric in the dashboard needs: current value, prior period comparison, target, and status (on track / at risk).

## Methodology

### Core SaaS metrics

**Revenue metrics:**
- MRR: sum of all active subscription revenue, normalized to monthly
- ARR: MRR × 12
- New MRR: MRR from new customers this month
- Expansion MRR: MRR added from existing customers (upgrades, seats)
- Churned MRR: MRR lost to cancellations
- Net New MRR: New MRR + Expansion MRR - Churned MRR

**Retention metrics:**
- Gross Revenue Retention (GRR): (Beginning MRR - Churned MRR) / Beginning MRR. Best-in-class B2B SaaS: >90%
- Net Revenue Retention (NRR): (Beginning MRR + Expansion MRR - Churned MRR) / Beginning MRR. Best-in-class: >120%
- Logo churn rate: customers lost / total customers. Red flag: >2% monthly

**Growth metrics:**
- MoM MRR growth rate
- ARR growth rate YoY
- Payback period: CAC / (ARPA × gross margin)

### Metric hierarchy
Level 1 (board-level): ARR, ARR growth, NRR, payback period
Level 2 (leadership): MRR breakdown (new/expansion/churned), logo churn, CAC by channel
Level 3 (operational): cohort retention curves, feature adoption, NPS trend

### Data sources
- MRR/ARR: billing system (`chargebee`, `recurly`, `paddle`, `stripe` via Chargebee)
- Customer counts: CRM (Salesforce or HubSpot)
- Usage data: `mixpanel` or `ga4`
- NPS: `delighted`

## Recording

```
write_artifact(artifact_type="growth_metrics_dashboard", path="/growth/metrics-dashboard-{date}", data={...})
```

## Available Tools

```
chargebee(op="call", args={"method_id": "chargebee.subscriptions.list.v1", "status[is]": "active", "limit": 100})

chargebee(op="call", args={"method_id": "chargebee.mrr.v1", "from_date": "2024-01-01", "to_date": "2024-12-31"})

recurly(op="call", args={"method_id": "recurly.subscriptions.list.v1", "state": "active", "limit": 200})

salesforce(op="call", args={"method_id": "salesforce.query.v1", "query": "SELECT SUM(Amount), StageName FROM Opportunity WHERE StageName = 'Closed Won' AND CloseDate = THIS_MONTH GROUP BY StageName"})

mixpanel(op="call", args={"method_id": "mixpanel.query.retention.v1", "project_id": "proj_id", "from_date": "2024-01-01", "to_date": "2024-12-31", "retention_type": "compactage"})
```

## Artifact Schema

```json
{
  "growth_metrics_dashboard": {
    "type": "object",
    "required": ["period", "revenue_metrics", "retention_metrics", "growth_metrics", "status_summary"],
    "additionalProperties": false,
    "properties": {
      "period": {
        "type": "object",
        "required": ["start_date", "end_date"],
        "additionalProperties": false,
        "properties": {"start_date": {"type": "string"}, "end_date": {"type": "string"}}
      },
      "revenue_metrics": {
        "type": "object",
        "required": ["mrr", "arr", "new_mrr", "expansion_mrr", "churned_mrr", "net_new_mrr"],
        "additionalProperties": false,
        "properties": {
          "mrr": {"type": "number"},
          "arr": {"type": "number"},
          "new_mrr": {"type": "number"},
          "expansion_mrr": {"type": "number"},
          "churned_mrr": {"type": "number"},
          "net_new_mrr": {"type": "number"},
          "mom_growth_pct": {"type": "number"}
        }
      },
      "retention_metrics": {
        "type": "object",
        "required": ["grr", "nrr", "logo_churn_rate"],
        "additionalProperties": false,
        "properties": {
          "grr": {"type": "number", "minimum": 0, "maximum": 1},
          "nrr": {"type": "number"},
          "logo_churn_rate": {"type": "number", "minimum": 0, "maximum": 1}
        }
      },
      "growth_metrics": {
        "type": "object",
        "required": ["arr_growth_yoy", "payback_period_months", "avg_cac"],
        "additionalProperties": false,
        "properties": {
          "arr_growth_yoy": {"type": "number"},
          "payback_period_months": {"type": "number"},
          "avg_cac": {"type": "number"}
        }
      },
      "status_summary": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["metric", "current", "target", "status"],
          "additionalProperties": false,
          "properties": {
            "metric": {"type": "string"},
            "current": {"type": "string"},
            "target": {"type": "string"},
            "status": {"type": "string", "enum": ["on_track", "at_risk", "off_track"]}
          }
        }
      }
    }
  }
}
```
