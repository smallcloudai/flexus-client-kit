---
name: discovery-context-import
description: Import customer context from CRM, support, and conversation platforms to seed discovery with existing evidence
---

You pull existing customer evidence from first-party systems to accelerate and contextualize discovery work. CRM and support data is NOT a substitute for qualitative interviews — it seeds and directs them.

Core mode: treat imported data as evidence with known limitations. CRM data reflects sales process bias (what salespeople logged, not what customers actually said). Support ticket data oversamples unhappy users. Always note these biases in limitations.

## Methodology

### CRM evidence pull
HubSpot, Salesforce, Pipedrive contain deal notes, call logs, and contact records that can reveal:
- Common objections from prospects who didn't convert
- Frequent questions during sales calls
- Reasons cited for choosing or rejecting the product
- Account characteristics that predict success or failure

Pull notes and call logs: `hubspot.notes.list.v1`, `hubspot.calls.list.v1`

### Support evidence pull
Zendesk and Intercom contain raw customer pain language:
- Search for recurring ticket themes: `zendesk.incremental.ticket_events.comment_events.list.v1`
- Pull conversation threads: `intercom.conversations.list.v1`

High-signal support patterns:
- Tickets that generate multiple replies (unresolved pain)
- Ticket volume spikes around specific product events
- Recurring keywords across unrelated tickets (widespread pain)

### Dovetail export
If research insights already exist in Dovetail (a research repository), export them before starting new research: `dovetail.insights.export.markdown.v1`

### PII handling
Support and CRM data contains PII. Never include personal names, emails, or account names in the output artifact. Anonymize to "Customer A (enterprise, finance)", "Prospect B (mid-market, SaaS)".

### Usage pattern
Use this skill BEFORE designing instruments (`discovery-survey`) — context import informs which hypotheses to test. Use it AFTER corpus creation to cross-reference interview findings against CRM/support patterns.

## Recording

```
write_artifact(path="/discovery/{study_id}/context", data={...})
```

## Available Tools

```
hubspot(op="call", args={"method_id": "hubspot.contacts.search.v1", "filterGroups": [{"filters": [{"propertyName": "company", "operator": "EQ", "value": "Company Name"}]}]})

hubspot(op="call", args={"method_id": "hubspot.notes.list.v1", "objectType": "contacts", "objectId": "contact_id"})

hubspot(op="call", args={"method_id": "hubspot.calls.list.v1", "objectType": "contacts", "objectId": "contact_id"})

zendesk(op="call", args={"method_id": "zendesk.incremental.ticket_events.comment_events.list.v1", "start_time": 1704067200})

zendesk(op="call", args={"method_id": "zendesk.tickets.audits.list.v1", "ticket_id": "ticket_id"})

intercom(op="call", args={"method_id": "intercom.conversations.list.v1", "per_page": 50, "starting_after": null})

dovetail(op="call", args={"method_id": "dovetail.insights.export.markdown.v1", "projectId": "project_id"})
```
