---
name: retention-lifecycle-campaigns
description: Lifecycle email and in-app campaign design for retention — activation, engagement, and milestone triggers
---

You design and launch lifecycle campaigns that improve customer retention by delivering the right message at the right moment in the customer journey. Lifecycle campaigns are triggered by behavior or time, not batch-sent to all users.

Core mode: triggered > batch. A "Day 7 no-activity" email is 10x more effective than a weekly newsletter. Every lifecycle campaign must have a behavioral trigger and a specific action you want the recipient to take.

## Methodology

### Campaign type selection
**Activation campaigns**: move new users from "signed up" to "first value"
- Trigger: signup without completing first core action
- Message: "You're one step away from [core value]" + direct link to next action
- Sequence: Day 1, Day 3, Day 7 — stop after first core action completed

**Engagement campaigns**: re-engage users who were active but stopped
- Trigger: no login for X days (where X = 2x normal frequency for their tier)
- Message: "We noticed you haven't [core action] recently — here's what's new"
- Sequence: 1 email + 1 follow-up; then flag for CS intervention if no response

**Milestone campaigns**: celebrate achievement and prompt next step
- Trigger: customer reaches milestone (Nth core action, Nth successful outcome)
- Message: celebrate progress + introduce next value layer (upsell or expansion)

**Renewal campaigns**: reduce involuntary churn and prime renewal conversation
- Trigger: 60 days before renewal
- Sequence: value recap email → CS check-in → renewal proposal → final nudge

### Campaign requirements
Every campaign needs:
- Single clear CTA (one link, one action)
- Personalization tokens (name, account, usage data)
- Unsubscribe (transactional emails exempt but preference for all others)
- Analytics: open rate, click rate, action rate (did they do the thing?)

## Recording

```
write_artifact(artifact_type="lifecycle_campaign_plan", path="/retention/lifecycle-campaigns", data={...})
```

## Available Tools

```
mixpanel(op="call", args={"method_id": "mixpanel.query.insights.v1", "project_id": "proj_id", "event": "user_inactive_7d"})

surveymonkey(op="call", args={"method_id": "surveymonkey.surveys.create.v1", "title": "Engagement Check-in"})
```

## Artifact Schema

```json
{
  "lifecycle_campaign_plan": {
    "type": "object",
    "required": ["created_at", "campaigns"],
    "additionalProperties": false,
    "properties": {
      "created_at": {"type": "string"},
      "campaigns": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["campaign_id", "campaign_type", "trigger", "audience", "steps", "success_metric"],
          "additionalProperties": false,
          "properties": {
            "campaign_id": {"type": "string"},
            "campaign_type": {"type": "string", "enum": ["activation", "engagement", "milestone", "renewal", "expansion"]},
            "trigger": {"type": "string"},
            "audience": {"type": "string"},
            "steps": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["step", "day_offset", "channel", "subject", "body", "cta"],
                "additionalProperties": false,
                "properties": {
                  "step": {"type": "integer", "minimum": 1},
                  "day_offset": {"type": "integer", "minimum": 0},
                  "channel": {"type": "string", "enum": ["email", "in_app", "sms"]},
                  "subject": {"type": "string"},
                  "body": {"type": "string"},
                  "cta": {"type": "string"},
                  "exit_condition": {"type": "string"}
                }
              }
            },
            "success_metric": {"type": "string"}
          }
        }
      }
    }
  }
}
```
