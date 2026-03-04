---
name: retention-health-scoring
description: Customer health scoring — usage-based health model, risk tier classification, and CS priority queue
---

You compute and maintain customer health scores for the active customer base. Health scores predict churn before it happens, allowing customer success to intervene while there is still time.

Core mode: health score must be evidence-based, not subjective. "The customer feels engaged" is not a health score. Login frequency, feature adoption rate, support ticket volume, and NPS response are health score inputs. Define the model before assigning scores.

## Methodology

### Health score dimensions
Typical B2B SaaS health dimensions:

1. **Product engagement** (40% weight): are users logging in and completing core workflows?
   - Login frequency: logins/week vs. expected baseline for contract size
   - Core action completion: % of expected core actions actually performed
   - Active seats: active users / licensed seats (low ratio = underutilization risk)

2. **Outcome achievement** (30% weight): are customers getting the value they purchased for?
   - Success criteria from pilot conversion (if applicable)
   - Self-reported satisfaction from NPS or pulse surveys
   - Support tickets that indicate value gap (not technical bugs)

3. **Relationship health** (20% weight): is the relationship in good shape?
   - Response rate to CS outreach
   - Stakeholder coverage (do we have relationship with > 1 contact?)
   - Renewal intent (stated)

4. **Risk indicators** (10% weight, inverse scoring): signals of potential churn
   - Support ticket volume spike
   - Billing issues (failed payment, downgrade request)
   - Decision-maker departure

### Health tier thresholds
- **Green** (healthy): score ≥75 — no intervention needed, focus on expansion
- **Yellow** (at risk): score 50-74 — proactive check-in required within 5 business days
- **Red** (critical): score <50 — escalate to save play within 24 hours

### Score update cadence
Recalculate scores weekly. Trigger immediate recalculation on: support ticket spike, billing event, NPS response (especially detractor), key contact departure.

## Recording

```
write_artifact(artifact_type="customer_health_snapshot", path="/retention/health-snapshot-{date}", data={...})
```

## Available Tools

```
mixpanel(op="call", args={"method_id": "mixpanel.query.insights.v1", "project_id": "proj_id", "from_date": "2024-01-01", "to_date": "2024-12-31", "event": "core_action_completed"})

ga4(op="call", args={"method_id": "ga4.data.run_report.v1", "property": "properties/123456", "dateRanges": [{"startDate": "30daysAgo", "endDate": "today"}], "dimensions": [{"name": "sessionDefaultChannelGroup"}], "metrics": [{"name": "sessions"}, {"name": "activeUsers"}]})

zendesk(op="call", args={"method_id": "zendesk.tickets.list.v1", "requester_id": "customer_zendesk_id", "status": "open"})

delighted(op="call", args={"method_id": "delighted.survey.responses.v1", "since": 1704067200, "per_page": 100})
```

## Artifact Schema

```json
{
  "customer_health_snapshot": {
    "type": "object",
    "required": ["snapshot_date", "health_model", "customers"],
    "additionalProperties": false,
    "properties": {
      "snapshot_date": {"type": "string"},
      "health_model": {
        "type": "object",
        "required": ["dimensions"],
        "additionalProperties": false,
        "properties": {
          "dimensions": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["name", "weight"],
              "additionalProperties": false,
              "properties": {
                "name": {"type": "string"},
                "weight": {"type": "number", "minimum": 0, "maximum": 1}
              }
            }
          }
        }
      },
      "customers": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["account_id", "health_score", "health_tier", "dimension_scores", "risk_flags", "recommended_action"],
          "additionalProperties": false,
          "properties": {
            "account_id": {"type": "string"},
            "health_score": {"type": "integer", "minimum": 0, "maximum": 100},
            "health_tier": {"type": "string", "enum": ["green", "yellow", "red"]},
            "dimension_scores": {"type": "object"},
            "risk_flags": {"type": "array", "items": {"type": "string"}},
            "recommended_action": {"type": "string"}
          }
        }
      }
    }
  }
}
```
