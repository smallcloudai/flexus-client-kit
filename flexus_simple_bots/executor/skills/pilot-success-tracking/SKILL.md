---
name: pilot-success-tracking
description: Pilot success criteria tracking — measuring progress against pre-defined pilot success metrics and generating status reports
---

You track pilot progress against the pre-defined success criteria from the pilot package. This skill produces structured status updates at regular intervals during the pilot.

Core mode: success criteria were defined BEFORE the pilot started (in `pricing-pilot-packaging`). Your job is to measure against them, not to redefine them based on what's achievable now. If success criteria need to change, that requires explicit agreement with the customer.

## Methodology

### Measurement cadence
- Weekly pulse: quick check-in (email or call) — primary metric status, blockers, action items
- Mid-point review (50% through pilot): formal review with sponsor — is pilot on track? Any adjustment needed?
- Success review (end of pilot): formal go/no-go evaluation against success criteria

### Measurement methods
Pull success criteria from pilot package, then map each to a measurement source:
- Usage metrics: ask for export from customer's system or from your product analytics
- Time savings: self-reported via structured survey (`surveymonkey` or `typeform`)
- Error rate / quality: customer provides before/after data
- Financial impact: customer calculates against agreed methodology

### Success status classification
For each criterion:
- **Met**: threshold achieved or exceeded
- **On track**: current trajectory will meet threshold by end date
- **At risk**: current trajectory suggests threshold will be missed; corrective action needed
- **Not measurable**: measurement method not working; agree alternative approach

### Escalation triggers
Escalate to senior stakeholder if:
- Any P0 criterion is "At risk" by mid-point review
- Customer has gone quiet for >5 business days
- Customer indicates they are "reconsidering" the pilot

## Recording

```
write_artifact(artifact_type="pilot_status_report", path="/pilots/{account_id}/status-{date}", data={...})
```

## Available Tools

```
surveymonkey(op="call", args={"method_id": "surveymonkey.surveys.create.v1", "title": "Pilot Progress Check-in", "pages": [...]})

typeform(op="call", args={"method_id": "typeform.forms.create.v1", "title": "Pilot Mid-Point Survey", "fields": [...]})

zendesk(op="call", args={"method_id": "zendesk.tickets.list.v1", "requester_id": "customer_id", "status": "open"})

google_calendar(op="call", args={"method_id": "google_calendar.events.insert.v1", "calendarId": "primary", "summary": "Pilot Mid-Point Review - [Company]", "start": {"dateTime": "2024-04-01T10:00:00-05:00"}})
```

## Artifact Schema

```json
{
  "pilot_status_report": {
    "type": "object",
    "required": ["account_id", "report_date", "pilot_day", "overall_status", "criteria_status", "blockers", "next_actions"],
    "additionalProperties": false,
    "properties": {
      "account_id": {"type": "string"},
      "report_date": {"type": "string"},
      "pilot_day": {"type": "integer", "minimum": 0},
      "overall_status": {"type": "string", "enum": ["green", "yellow", "red"]},
      "criteria_status": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["criterion", "current_value", "target_value", "status"],
          "additionalProperties": false,
          "properties": {
            "criterion": {"type": "string"},
            "current_value": {"type": "string"},
            "target_value": {"type": "string"},
            "status": {"type": "string", "enum": ["met", "on_track", "at_risk", "not_measurable"]},
            "notes": {"type": "string"}
          }
        }
      },
      "blockers": {"type": "array", "items": {"type": "string"}},
      "next_actions": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["action", "owner", "due_date"],
          "additionalProperties": false,
          "properties": {
            "action": {"type": "string"},
            "owner": {"type": "string"},
            "due_date": {"type": "string"}
          }
        }
      }
    }
  }
}
```
