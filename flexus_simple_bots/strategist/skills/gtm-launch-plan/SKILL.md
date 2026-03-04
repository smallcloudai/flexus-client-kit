---
name: gtm-launch-plan
description: Go-to-market launch plan — execution timeline, launch day checklist, first 90-day milestones, and owner assignments
---

You produce the operational launch plan: who does what, by when, and with what success metrics for the first 90 days post-launch. The launch plan converts channel strategy into an executable calendar.

Core mode: dates and owners are required. A launch plan without assigned owners and dates is a wish list. Every milestone needs one name attached to it (not a team — one person).

## Methodology

### Launch phases
**Pre-launch (T-30 to T-0):**
- Prospect list finalized (from `pipeline-contact-enrichment`)
- Messaging approved (from `positioning-messaging`)
- Outreach sequences loaded (from `pipeline-outreach-sequencing`)
- Pilot packages prepared (from `pricing-pilot-packaging`)
- Website / landing page live
- Analytics instrumented (tracking events for success metrics)
- Internal enablement: everyone who touches customers knows the pitch

**Launch week (T-0 to T+7):**
- Launch batch outreach: first wave of outreach to top ICP contacts
- Community announcements (Reddit, Slack, ProductHunt if relevant)
- Direct network outreach (founder personal network)
- Track: email open rates, reply rates, meeting requests

**First 30 days (T+0 to T+30):**
- Milestone: first discovery call booked
- Milestone: first pilot proposal delivered
- Milestone: first pilot customer signed
- Weekly pipeline review

**30-60 days:**
- Milestone: first pilot customer completes onboarding
- Milestone: first payment received (if applicable)
- Insight: what messaging is resonating / not resonating?

**60-90 days:**
- Milestone: 3+ pilots running simultaneously
- Pilot feedback synthesized → iteration on MVP scope
- Channel efficiency measured vs. CAC targets

### Launch day blockers (pre-flight checklist)
Must be complete before any outreach:
- [ ] Product delivers core job for at least 1 live test user
- [ ] Payments / invoicing working
- [ ] SLA / support process defined
- [ ] Data handling / privacy policy signed off

## Recording

```
write_artifact(artifact_type="gtm_launch_plan", path="/strategy/gtm-launch-plan", data={...})
```

## Available Tools

```
flexus_policy_document(op="activate", args={"p": "/strategy/gtm-channel-strategy"})
flexus_policy_document(op="activate", args={"p": "/strategy/pricing-pilot-packaging"})
flexus_policy_document(op="activate", args={"p": "/strategy/mvp-validation-criteria"})
google_calendar(op="call", args={"method_id": "google_calendar.events.insert.v1", "calendarId": "primary", "summary": "GTM Launch Day", "start": {"date": "2024-03-01"}})
```

## Artifact Schema

```json
{
  "gtm_launch_plan": {
    "type": "object",
    "required": ["created_at", "launch_date", "pre_launch_checklist", "phases", "success_metrics"],
    "additionalProperties": false,
    "properties": {
      "created_at": {"type": "string"},
      "launch_date": {"type": "string"},
      "pre_launch_checklist": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["item", "owner", "due_date", "status"],
          "additionalProperties": false,
          "properties": {
            "item": {"type": "string"},
            "owner": {"type": "string"},
            "due_date": {"type": "string"},
            "status": {"type": "string", "enum": ["done", "in_progress", "blocked", "not_started"]}
          }
        }
      },
      "phases": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["phase_name", "start_day", "end_day", "milestones"],
          "additionalProperties": false,
          "properties": {
            "phase_name": {"type": "string"},
            "start_day": {"type": "integer"},
            "end_day": {"type": "integer"},
            "milestones": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["milestone", "owner", "due_day", "success_metric"],
                "additionalProperties": false,
                "properties": {
                  "milestone": {"type": "string"},
                  "owner": {"type": "string"},
                  "due_day": {"type": "integer"},
                  "success_metric": {"type": "string"}
                }
              }
            }
          }
        }
      },
      "success_metrics": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["metric", "target_30d", "target_60d", "target_90d"],
          "additionalProperties": false,
          "properties": {
            "metric": {"type": "string"},
            "target_30d": {"type": "string"},
            "target_60d": {"type": "string"},
            "target_90d": {"type": "string"}
          }
        }
      }
    }
  }
}
```
