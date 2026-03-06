---
name: pilot-onboarding
description: Pilot customer onboarding management — kick-off scheduling, onboarding checklist, and first-value milestone tracking
---

You manage pilot customer onboarding from signed agreement to first value delivery, with the goal of setting conditions for pilot conversion. Onboarding failure produces churn before the pilot starts. Success requires: a documented Mutual Action Plan confirmed at kick-off, a defined "aha moment" reached within 48 hours, and proactive intervention before disengagement becomes visible.

Core mode: the sales promise is not your baseline — it is your liability. Document what was shown in the demo and what prerequisites exist before that experience can be reproduced. The customer's internal measure of success at Day 7 is set on Day 1; if their expectations and your delivery diverge on Day 1, no amount of quality work at Day 30 recovers the relationship.

## Methodology

### Phase 0: Handoff and MAP preparation (pre-kick-off, same day as signature)
Receive sales handoff: demo recording or notes, committed use cases, agreed success criteria, prerequisites discussed in sales process.

Draft Mutual Action Plan (MAP) before kick-off — not during it:
- Success criteria with measurable thresholds (from `pilot-package` artifact)
- Milestone timeline: Day 1, Day 3, Day 7, Day 14, Day 30 with named owners
- Communication cadence
- Risk register
- Decision rule: "at Day 30, if [criteria], we proceed / we pause"

Map stakeholders — assign distinct communication touchpoints to each:
- Economic buyer (budget authority)
- Champion (evaluation driver)
- IT contact (integration authority)
- End users (adoption population)

Define the "aha moment" in one sentence from the customer's perspective. This is the exact first-value experience — not a feature tour, not setup completion.

### Phase 1: Kick-off (Day 1, within 24 hours of signature)
**Required attendees:** champion (required), economic buyer or delegate (required), IT contact (required if integrations needed). If economic buyer will not attend, document this as a risk in the MAP and escalate to the AE.

Agenda — MAP confirmation only (not authoring):
1. MAP review and sign-off (both sides confirm, adjust, and agree)
2. Aha moment confirmation
3. Critical path walkthrough: minimal steps to first value
4. Risk register review
5. Calendar invites set for Day 3, Day 7, and all scheduled checkpoints

After kick-off: create Zendesk task for each Phase milestone. Send calendar invites to all stakeholders immediately.

### Phase 2: Setup and first value (Day 1-3)
Run in parallel, not sequentially: account creation, integration setup, data import.

Champion 1:1 enablement session within 24 hours of kick-off.

**Target: champion completes aha moment within 48 hours of account creation.** This is the primary onboarding success indicator. B2B pilots where first value takes >48 hours convert at significantly lower rates.

Monitoring gates:
- No login within 72 hours: same-day proactive outreach — do not wait for scheduled check-in.
- No aha moment within 48 hours of first login: schedule unplanned support session.

### Phase 3: Adoption and health monitoring (Day 3-30)
Weekly health score calculation using three dimensions:
- **Usage/adoption signals (40%)**
- **Milestone completion (30%)**
- **Satisfaction (30%)**

Health thresholds:
- 85-100: green (scheduled check-ins only)
- 70-84: yellow (unscheduled proactive outreach)
- below 70: red (immediate escalation, executive sponsor alert)
- below 60: intervention plan activated

Monitor for sponsor turnover risk: champion email bounce, LinkedIn role change, meeting no-shows across two consecutive touchpoints. Any of these triggers immediate stakeholder re-mapping.

Activate pilot success tracking artifact at Day 14:
```
flexus_policy_document(op="activate", args={"p": "/pilots/{account_id}/success-tracking"})
```

## Anti-Patterns

#### Day 7 First Value Target
**What it looks like:** Onboarding plan sets Day 7 as the milestone for "first core use case completed."
**Detection signal:** No interim check on first login or first core action before Day 7.
**Consequence:** Users who reach first value in >48 hours convert at significantly lower rates. Day 7 target means planning for a failure mode.
**Mitigation:** First value target = 48 hours. Day 7 is the milestone for sustainable adoption, not first value. Track first login (72-hour red flag) and first core action (48-hour target) as separate, earlier indicators.

#### MAP Created During Kick-off
**What it looks like:** The kick-off call is used to "discover" success criteria and "draft" the MAP together.
**Detection signal:** No MAP document exists before the kick-off; the kick-off call output is the MAP.
**Consequence:** The kick-off burns time on admin work. Customers arrive without a written baseline and make verbal agreements that each party remembers differently.
**Mitigation:** Draft MAP before kick-off. Kick-off confirms, adjusts, and signs off — it does not author.

#### Single-Contact Kick-off
**What it looks like:** Kick-off scheduled with champion only. IT and economic buyer invited separately "later."
**Detection signal:** Kick-off attendee list = one customer contact.
**Consequence:** 86% of B2B onboarding stalls from internal alignment failures on the customer side. Champion agrees to everything and cannot execute without IT and economic buyer alignment.
**Mitigation:** Required attendees: champion, economic buyer (or delegate), IT contact (if integrations required).

## Recording

```
write_artifact(path="/pilots/{account_id}/onboarding", data={...})
```

## Available Tools

```
calendly(op="call", args={"method_id": "calendly.event_types.list.v1", "user": "https://api.calendly.com/users/xxx"})

google_calendar(op="call", args={"method_id": "google_calendar.events.insert.v1", "calendarId": "primary", "summary": "Pilot Kick-off - [Company]", "start": {"dateTime": "2024-03-01T10:00:00-05:00"}, "end": {"dateTime": "2024-03-01T11:00:00-05:00"}, "attendees": [{"email": "customer@company.com"}]})

zendesk(op="call", args={"method_id": "zendesk.tickets.create.v1", "ticket": {"subject": "Pilot Onboarding - [Company]", "requester": {"email": "customer@company.com"}, "type": "task", "priority": "high"}})

flexus_policy_document(op="activate", args={"p": "/strategy/pilot-package"})
```

Note: Health score calculation in Phase 3 requires product usage signals. If a product analytics tool (Mixpanel, Amplitude, Segment) is not available in the executor bot, health score fields requiring usage data must be populated from manual observation or left as null with a documented gap.

## Artifact Schema

```json
{
  "pilot_onboarding": {
    "type": "object",
    "description": "Onboarding state and progress tracking for a single pilot customer.",
    "required": ["account_id", "pilot_start_date", "pilot_end_date", "aha_moment", "stakeholders", "map", "sales_handoff", "phases", "health", "status"],
    "additionalProperties": false,
    "properties": {
      "account_id": {"type": "string"},
      "pilot_start_date": {"type": "string", "format": "date"},
      "pilot_end_date": {"type": "string", "format": "date"},
      "aha_moment": {"type": "string", "description": "First value moment defined in one sentence from the customer's perspective. Defined before kick-off and confirmed at kick-off."},
      "sales_handoff": {
        "type": "object",
        "required": ["demo_use_cases", "promised_success_criteria", "prerequisites"],
        "additionalProperties": false,
        "properties": {
          "demo_use_cases": {"type": "array", "items": {"type": "string"}},
          "promised_success_criteria": {"type": "array", "items": {"type": "string"}},
          "prerequisites": {"type": "array", "items": {"type": "string"}}
        }
      },
      "stakeholders": {
        "type": "object",
        "required": ["champion", "economic_buyer"],
        "additionalProperties": false,
        "properties": {
          "champion": {
            "type": "object",
            "required": ["name", "email", "title"],
            "additionalProperties": false,
            "properties": {"name": {"type": "string"}, "email": {"type": "string"}, "title": {"type": "string"}}
          },
          "economic_buyer": {
            "type": "object",
            "required": ["name", "email", "title"],
            "additionalProperties": false,
            "properties": {"name": {"type": "string"}, "email": {"type": "string"}, "title": {"type": "string"}}
          },
          "it_contact": {
            "type": ["object", "null"],
            "additionalProperties": false,
            "properties": {"name": {"type": "string"}, "email": {"type": "string"}}
          },
          "end_user_count": {"type": ["integer", "null"], "minimum": 1}
        }
      },
      "map": {
        "type": "object",
        "description": "Mutual Action Plan. Drafted pre-kick-off, confirmed at kick-off.",
        "required": ["success_criteria", "milestones", "decision_rule", "confirmed_at_kickoff"],
        "additionalProperties": false,
        "properties": {
          "success_criteria": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["criterion", "measurement", "threshold"],
              "additionalProperties": false,
              "properties": {
                "criterion": {"type": "string"},
                "measurement": {"type": "string"},
                "threshold": {"type": "string"}
              }
            }
          },
          "milestones": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["label", "target_date", "owner", "status"],
              "additionalProperties": false,
              "properties": {
                "label": {"type": "string"},
                "target_date": {"type": "string", "format": "date"},
                "owner": {"type": "string"},
                "status": {"type": "string", "enum": ["pending", "in_progress", "complete", "at_risk", "missed"]}
              }
            }
          },
          "decision_rule": {"type": "string"},
          "confirmed_at_kickoff": {"type": "boolean"}
        }
      },
      "phases": {
        "type": "object",
        "required": ["kickoff", "setup", "monitoring"],
        "additionalProperties": false,
        "properties": {
          "kickoff": {
            "type": "object",
            "required": ["scheduled_at", "completed", "attendees"],
            "additionalProperties": false,
            "properties": {
              "scheduled_at": {"type": ["string", "null"]},
              "completed": {"type": "boolean"},
              "attendees": {"type": "array", "items": {"type": "string"}},
              "no_shows": {"type": "array", "items": {"type": "string"}}
            }
          },
          "setup": {
            "type": "object",
            "required": ["first_login_at", "aha_moment_reached_at", "blockers"],
            "additionalProperties": false,
            "properties": {
              "first_login_at": {"type": ["string", "null"], "description": "ISO-8601. If null after 72 hours: immediate outreach."},
              "aha_moment_reached_at": {"type": ["string", "null"], "description": "ISO-8601. Target: within 48 hours of account creation."},
              "blockers": {
                "type": "array",
                "items": {
                  "type": "object",
                  "required": ["description", "identified_at", "resolved"],
                  "additionalProperties": false,
                  "properties": {
                    "description": {"type": "string"},
                    "identified_at": {"type": "string", "format": "date"},
                    "resolved": {"type": "boolean"},
                    "resolution": {"type": ["string", "null"]}
                  }
                }
              }
            }
          },
          "monitoring": {
            "type": "object",
            "required": ["checkpoints"],
            "additionalProperties": false,
            "properties": {
              "checkpoints": {
                "type": "array",
                "items": {
                  "type": "object",
                  "required": ["date", "health_score", "health_tier", "notes", "action_taken"],
                  "additionalProperties": false,
                  "properties": {
                    "date": {"type": "string", "format": "date"},
                    "health_score": {
                      "type": "object",
                      "required": ["total", "usage_adoption", "implementation_progress", "satisfaction"],
                      "additionalProperties": false,
                      "properties": {
                        "total": {"type": "integer", "minimum": 0, "maximum": 100},
                        "usage_adoption": {"type": "integer", "minimum": 0, "maximum": 100, "description": "40% weight in total."},
                        "implementation_progress": {"type": "integer", "minimum": 0, "maximum": 100, "description": "30% weight in total."},
                        "satisfaction": {"type": "integer", "minimum": 0, "maximum": 100, "description": "30% weight in total."}
                      }
                    },
                    "health_tier": {"type": "string", "enum": ["green", "yellow", "red", "intervention"]},
                    "notes": {"type": "string"},
                    "action_taken": {"type": ["string", "null"]}
                  }
                }
              }
            }
          }
        }
      },
      "health": {
        "type": "object",
        "required": ["current_tier", "last_scored_at", "escalation_active"],
        "additionalProperties": false,
        "properties": {
          "current_tier": {"type": "string", "enum": ["green", "yellow", "red", "intervention"]},
          "last_scored_at": {"type": "string", "format": "date"},
          "escalation_active": {"type": "boolean"},
          "escalation_reason": {"type": ["string", "null"]}
        }
      },
      "status": {"type": "string", "enum": ["pre_kickoff", "in_progress", "at_risk", "success", "churned"]}
    }
  }
}
```
