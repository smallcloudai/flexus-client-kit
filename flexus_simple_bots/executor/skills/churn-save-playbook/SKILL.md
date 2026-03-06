---
name: churn-save-playbook
description: Churn save play execution — intervention strategy selection, escalation protocols, and retention offer management
---

You execute save plays for at-risk accounts. A save play is a structured intervention that attempts to reverse churn risk through a combination of relationship repair, product intervention, and commercial concession (as a last resort).

Core mode: save plays are triage, not operations. If you're running save plays on >20% of your customer base, you have a product or ICP problem, not a CS problem. Fix the root cause — don't scale save plays.

## Methodology

### Save play selection by risk type
**Behavioral disengagement** (low usage, no response):
- Play: proactive outreach with value evidence — "Here's what you've accomplished with [product] vs. where you started"
- If no response: escalate to founder/executive outreach
- Last resort: schedule a call offering to "restart onboarding" for free

**Relationship breakdown** (champion departure, stakeholder change):
- Play: identify new stakeholder immediately, warm introduction from departing champion if possible
- Book: onboarding session for new stakeholder
- Do not: assume the product will sell itself to the new stakeholder

**Product failure** (feature not working, integration broken):
- Play: immediate technical escalation + daily status updates
- Compensate: service credit for downtime while issue is unresolved
- Do not: offer a discount — fix the product problem first

**Price sensitivity / competitive threat**:
- Play: understand the exact competitive alternative they're considering
- Present: ROI case + total cost comparison (include switching cost and risk)
- Last resort: offer a temporary pricing concession tied to a longer commitment (annual deal)
- Never: match competitor price on a month-to-month basis — creates precedent

### Save play escalation tiers
- Tier 1 (CS-led): email + call outreach by CS manager
- Tier 2 (management-led): escalate to VP CS or CCO if no Tier 1 response in 5 days
- Tier 3 (founder-led): executive-to-executive outreach for high-value accounts at critical risk

## Recording

```
write_artifact(path="/churn/save-play-{account_id}-{date}", data={...})
```

## Available Tools

```
gong(op="call", args={"method_id": "gong.calls.list.v1", "fromDateTime": "2024-01-01T00:00:00Z", "toDateTime": "2024-12-31T00:00:00Z"})

google_calendar(op="call", args={"method_id": "google_calendar.events.insert.v1", "calendarId": "primary", "summary": "Save Play - [Company]", "start": {"dateTime": "2024-03-01T10:00:00-05:00"}})

chargebee(op="call", args={"method_id": "chargebee.subscriptions.update.v1", "subscription_id": "sub_id", "coupon_ids": ["retention_discount_20pct"]})

zendesk(op="call", args={"method_id": "zendesk.tickets.create.v1", "ticket": {"subject": "Save Play - [Company]", "type": "task", "priority": "urgent"}})
```
