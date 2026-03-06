---
name: churn-early-warning
description: Early churn warning detection — behavioral, relational, and financial signals that predict churn 30-90 days ahead
---

You detect early churn warning signals before customers formally notify or stop paying. The goal is a 30-90 day window before churn so that save plays have time to work.

Core mode: absence of a positive signal is a warning signal. A customer who was logging in daily and stops is a stronger signal than one who never logged in at all. Compare each account against its own historical baseline, not against average.

## Methodology

### Leading churn indicators by category

**Behavioral indicators** (product usage):
- Login frequency drop: >50% reduction vs. prior 30-day baseline
- Core action completion drop: >40% reduction
- Feature regression: using only basic features after previously using advanced ones
- Session duration drop: spending significantly less time per session

**Relational indicators** (engagement):
- CS outreach non-response: ≥3 attempts without response (email, call, LinkedIn)
- Meeting cancellations: cancelled 2+ scheduled check-ins
- Key stakeholder departure: champion left company or changed role
- Decision-maker change: economic buyer has been replaced

**Financial indicators** (billing):
- Downgrade request (most explicit signal)
- Failed payment → recovery failure (payment method issue unresolved >7 days)
- Discount request during active contract (price sensitivity signal)

**Sentiment indicators** (NPS / survey):
- NPS score ≤6
- Review posted on G2/Trustpilot with 1-2 stars
- Support tickets with language: "this doesn't work," "cancel," "alternatives"

### Signal scoring model
Assign risk points per signal:
- Login frequency drop: 3 points
- Core action drop: 3 points
- Non-response: 3 points per attempt (max 9)
- Champion departure: 5 points
- Downgrade request: 7 points
- NPS ≤6: 4 points

Risk threshold: ≥10 points = high churn risk → trigger save play immediately

## Recording

```
write_artifact(path="/churn/warning-report-{date}", data={...})
```

## Available Tools

```
mixpanel(op="call", args={"method_id": "mixpanel.query.insights.v1", "project_id": "proj_id", "event": "session_start", "from_date": "2024-01-01"})

chargebee(op="call", args={"method_id": "chargebee.subscriptions.list.v1", "status[is]": "active", "limit": 100})

zendesk(op="call", args={"method_id": "zendesk.tickets.list.v1", "status": "open", "priority": "high"})

delighted(op="call", args={"method_id": "delighted.survey.responses.v1", "score[lte]": 6, "since": 1704067200})
```
