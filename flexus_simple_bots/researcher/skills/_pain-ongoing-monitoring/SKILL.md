---
name: pain-ongoing-monitoring
description: Ongoing customer pain monitoring from support and conversation data — ticket theme tracking, sentiment trends, and pain signal drift
---

You monitor ongoing customer pain signals from support and customer success data. Unlike `discovery-context-import` (which seeds research one time), this skill runs periodically to track how pain patterns evolve — are problems getting better or worse? Are new pains emerging?

Core mode: trend over time, not point-in-time. A single week of ticket data is noise. Meaningful signals emerge from comparing 30-day windows to the prior 30 days, or tracking month-over-month changes in theme frequency.

## Methodology

### Ticket theme tracking
Pull support tickets for a time window, then extract recurring themes.

Key metrics:
- Theme frequency: how many tickets mention X in this period vs. prior period?
- First-contact resolution rate: if dropping, indicates growing complexity of a problem
- Escalation rate: tickets that escalate signal severe unresolved pain
- Reopened tickets: customers recontacting = problem not actually solved

Use `zendesk.incremental.ticket_events.v1` for continuous ticket stream.

### Conversation analysis
Intercom conversations contain richer context than formal support tickets.

Focus on:
- Long conversations (>5 messages): high-effort sessions signal confusion or frustration
- Conversations with negative CSAT scores
- Conversations where representative uses workaround language ("one way to do this is...")

### Sentiment trend
Dovetail maintains a research repository. If prior interview insights are stored there, pull them to compare against current support patterns: are customers mentioning new issues or is it the same recurring pain?

### Alert thresholds
Flag to human review if:
- Any theme increases by >50% vs. prior period
- CSAT drops by >0.3 points
- Ticket volume grows >30% without corresponding product/user growth

## Recording

```
write_artifact(path="/pain/{period}/monitoring-snapshot", data={...})
```

## Available Tools

```
zendesk(op="call", args={"method_id": "zendesk.incremental.ticket_events.v1", "start_time": 1704067200, "per_page": 100})

zendesk(op="call", args={"method_id": "zendesk.tickets.audits.list.v1", "ticket_id": "ticket_id"})

zendesk(op="call", args={"method_id": "zendesk.satisfaction_ratings.list.v1", "start_time": 1704067200, "per_page": 100})

intercom(op="call", args={"method_id": "intercom.conversations.list.v1", "per_page": 50, "starting_after": null})

intercom(op="call", args={"method_id": "intercom.conversations.get.v1", "id": "conversation_id"})

dovetail(op="call", args={"method_id": "dovetail.insights.export.markdown.v1", "projectId": "project_id"})
```
