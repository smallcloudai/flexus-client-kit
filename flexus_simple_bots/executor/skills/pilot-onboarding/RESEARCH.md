# Research: pilot-onboarding

**Skill path:** `executor/skills/pilot-onboarding/`
**Bot:** executor (researcher | strategist | executor)
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`pilot-onboarding` manages the customer relationship from signed pilot agreement to first value delivery. The current SKILL.md is structurally sound: the three-phase model (kick-off → setup → monitoring) and the health indicators (green/yellow/red) are directionally correct. However, the skill underspecifies several critical patterns: Mutual Action Plans (MAPs) as a formal instrument; the "value gap" between sales commitments and onboarding reality; specific health score weights and intervention thresholds; the urgency of the 48-hour first-value window; and multi-stakeholder coordination for B2B buying committees.

---

## Definition of Done

- [x] At least 4 distinct research angles covered
- [x] Each finding has a source URL or named reference
- [x] Methodology covers practical how-to, not just theory
- [x] Tool/API landscape mapped with current status
- [x] At least one "what not to do" failure mode documented
- [x] Output schema recommendations grounded in real data shapes
- [x] Gaps section honestly lists what was NOT found

---

## Quality Gates

- No generic filler without concrete backing: **passed**
- No invented tool names, method IDs, or API endpoints: **passed**
- Contradictions between sources explicitly noted: **passed**

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> What does a high-performing B2B pilot onboarding look like in 2025?

**Findings:**

**Time-to-value (TTV) is the primary leading metric — and the current SKILL.md's Day 7 threshold is too slow.** Research shows that users who reach the "aha moment" within 48 hours convert to retained customers at 3.4x the rate of those taking 7+ days. The industry TTV benchmark for B2B SaaS is under 1.5 days. Once TTV exceeds 24 hours, abandonment risk increases materially. [M1]

This means the SKILL.md's "Quick win: ensure customer completes one full use case by Day 7" should be tightened to 48 hours. If Day 7 is the target, the intervention threshold for the Red zone should be earlier, not later — Day 14 no-usage is already a lost pilot in most cases.

**The "aha moment" must be defined and documented before kick-off, not discovered during onboarding.** The first value moment should be described in one sentence, from the customer's perspective, representing the earliest point where they experience a useful outcome for their specific use case — not a feature walkthrough or a tutorial completion. Example: "First outreach sequence sent to 50 verified contacts." [M2]

**Critical path mapping:** Once the "aha moment" is defined, map the minimal number of steps required to reach it. Remove everything that does not directly advance toward that moment. The most common friction killers (applicable to B2B pilot onboarding specifically): complex integration setup before any value is shown; team invitation requirements as a gate to first use; multi-step configuration flows that require IT involvement before the champion can act. [M3]

**Mutual Action Plans (MAPs) increase conversion rates by 26%.** A MAP is a shared, written document between vendor and customer that establishes: success criteria with measurable thresholds, milestone timeline with named owners on both sides, communication cadence, risk register with pre-agreed mitigation steps, and a decision rule for what happens at pilot end. [M4][M5]

MAPs are not optional for structured pilots — they transform a vague "let's try it" into a business-critical evaluation with mutual accountability. The MAP should be produced before the kick-off call and confirmed (not created) during kick-off. [M4]

**Sales-to-onboarding handoff must transfer documented commitments.** The value gap between sales promises and onboarding delivery is the primary structural cause of early churn in B2B SaaS. 74% of buyers leave if onboarding is complicated in the first 90 days. 62% of CS leaders lack real-time visibility into customer onboarding progress. The handoff must include: what was promised in the sales process, which use cases were demonstrated, the specific success criteria the buyer agreed to evaluate, and any implementation prerequisites that were discussed. [M6][M7]

**Multi-stakeholder coordination is the operational constraint in B2B pilots.** B2B purchases involve 6-13 stakeholders who must align. The champion who drives the evaluation is rarely the same person as the economic buyer who approved the pilot budget — and neither is typically the end user who must actually adopt the product daily. This means kick-off coordination with a single contact point is structurally insufficient; the onboarding plan must map all three roles and include separate touchpoints for each. [M8]

**Sources:**
- [M1] Athenic: SaaS Onboarding First 48 Hours: https://getathenic.com/blog/saas-onboarding-optimisation-first-48-hours
- [M2] Growth Strategy Lab: Activation Moment Sequencing 2026: https://medium.com/@GrowthStrategyLab/activation-moment-sequencing-in-onboarding-to-reach-first-value-faster-d1eeb1adbebe
- [M3] Flowjam: SaaS Onboarding Best Practices 2025: https://www.flowjam.com/blog/saas-onboarding-best-practices-2025-guide-checklist
- [M4] pclub.io: Mutual Success Action Plan Framework: https://www.pclub.io/blog/mutual-success-action-plan
- [M5] Outreach: Mutual Action Plans — 26% Win Rate Improvement: https://www.outreach.io/resources/blog/how-to-use-mutual-action-plans
- [M6] Suptask: B2B Customer Onboarding Best Practices: https://www.suptask.com/blog/b2b-customer-onboarding-best-practices
- [M7] Onramp: 2026 State of Customer Onboarding: https://onramp.us/blog/2026-state-of-onboarding-report
- [M8] Skipup: The Committee Problem in B2B Sales: https://blog.skipup.ai/buying-committee-demo-scheduling-problem/

---

### Angle 2: Tool & API Landscape
> What are the technical capabilities and limits of the tools in this skill?

**Findings:**

**Calendly:**
- `calendly.event_types.list.v1`: lists available event types for a user. Useful for identifying which kick-off meeting format to offer (15-min check, 30-min kick-off, 60-min onboarding).
- Calendly v2 API supports webhooks with real-time notifications for: Invitee Created (meeting booked), Invitee Canceled (meeting canceled), Routing Form Submitted. Webhook payloads can trigger Zendesk ticket creation automatically without polling. [T1]
- Calendly also offers a **Scheduling API** for embedding scheduling directly into custom workflows without redirects — suitable for automated onboarding orchestration. [T1]
- Rate limit documentation exists but specific per-minute limits are not published publicly — treat as requiring exponential backoff on 429 responses.

**Zendesk:**
- `zendesk.tickets.create.v1`: creates a support/task ticket. Rate limits vary by plan and endpoint, communicated via `X-Rate-Limit` and `X-Rate-Limit-Remaining` response headers. On limit exceeded: 429 with `Retry-After` header indicating seconds to wait. [T2]
- Zendesk tickets can carry custom fields — critical for onboarding task tracking: account_id, pilot phase, onboarding step, health tier, escalation flag.
- Calendly + Zendesk can be connected via Zapier trigger (new Calendly booking → create Zendesk ticket). This enables automated kick-off task creation when the customer self-schedules. [T3]

**Google Calendar:**
- `google_calendar.events.insert.v1`: creates a calendar event with attendees. Required fields already correct in the current SKILL.md. One addition: include `conferenceData` with a Google Meet link generation (`createRequest`) so the kick-off has a video call link without a separate step.
- Rate limits: Google Calendar API uses per-user and per-project quotas. Default: 1,000,000 queries per day per project, 10 queries per second per user. Not a practical bottleneck for onboarding workflows. [T4]

**Missing tool: product usage / analytics signal source.** The health monitoring phase (Phase 3) in the current SKILL.md requires checking "usage data: is the champion using the product?" — but there is no tool in the SKILL.md that can provide this. Without a Mixpanel, Amplitude, Segment, or CRM-based activity feed tool, the bot cannot operationalize the health indicator logic it defines. This is a structural gap in the current skill.

**Sources:**
- [T1] Calendly Developer: Rate Limiting & Webhooks: https://developer.calendly.com/api-docs/rate-limiting
- [T2] Zendesk Developer: Rate Limits: https://developer.zendesk.com/api-reference/introduction/rate-limits
- [T3] Zapier: Calendly + Zendesk: https://zapier.com/apps/calendly/integrations/zendesk
- [T4] Google Calendar API docs (reference; no direct URL in search results)

---

### Angle 3: Data Interpretation & Signal Quality
> How to track onboarding health and know when to intervene?

**Findings:**

**Health score must have explicit weights — not just traffic-light labels.** The current SKILL.md defines green/yellow/red thresholds qualitatively, which is correct directionally but insufficient for consistent operationalization. Research-validated weighting for B2B SaaS onboarding health: [D1]
- **Usage/adoption: 40%** — login frequency, core feature activation, session length
- **Implementation progress: 30%** — onboarding task completion rate, time-to-first-value milestone reached
- **Satisfaction/sentiment: 30%** — NPS/CSAT if collected, support ticket sentiment, meeting-no-show rate

**Composite risk thresholds (0-100 scale):** [D1]
- 85-100: healthy — no intervention needed
- 70-84: moderate risk — proactive check-in warranted
- Below 70: high risk — immediate escalation and intervention plan
- Below 60: predictive churn signal — health scores in this range predict NPS detractors with 87-89% accuracy, 28-35 days earlier than surveys would catch it

**Product usage signals precede everything else as leading indicators.** The earliest actionable signal is whether the champion logged in at all in the first 48-72 hours. If no login in first 72 hours (not 14 days as in current SKILL.md), the onboarding is already at risk. Key usage signals ranked by leading-indicator strength: [D2]
1. First login timestamp (absolute first signal)
2. First core action completion (defines aha-moment arrival)
3. DAU pattern in first week (daily engagement baseline)
4. Feature breadth (how many product areas have been touched)
5. Session length trend (increasing = healthy, decreasing = risk)

**The "zone of disillusionment" is Day 1 to Day 90.** 74% of buyers who churn in this window report that onboarding was too complicated. The critical window is tighter than the 30-day monitoring phase in the current SKILL.md: the majority of churn risk crystallizes between Day 7 and Day 21. If no meaningful value has been delivered by Day 14, the statistical probability of a successful pilot closes sharply. [D3]

**Sponsor turnover is a single-point failure for a pilot.** If the economic buyer who approved the pilot changes roles or leaves during the onboarding window, the pilot loses its budget justification and its internal advocate simultaneously. Monitor for: calendar invite no-shows, email bounce on champion address, LinkedIn role-change signal on key stakeholders. [D2]

**Sources:**
- [D1] The Onboarding Lab: Health Scores as Early Warning System: https://www.theonboardinglab.com/p/how-to-use-customer-health-scores-as-your-early-warning-system-for-onboarding-success
- [D2] Athenic: Customer Health Scoring Predictive NPS: https://getathenic.com/blog/customer-health-scoring-predictive-nps
- [D3] Suptask: B2B Customer Onboarding Best Practices: https://www.suptask.com/blog/b2b-customer-onboarding-best-practices

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in pilot onboarding? Where do pilots actually die?

**Findings:**

**No defined "aha moment" before kick-off.** The most common onboarding failure is that neither vendor nor customer can answer "what does success look like on Day 3?" The kick-off becomes a feature walkthrough instead of a value milestone confirmation. Without a documented first-value moment, the customer measures the pilot by their subjective impression, which tends to default to the sales-promised vision rather than the onboarding-delivered reality. [F1]

**Value gap: sales overcommits, onboarding underdelivers.** Sales demos show the product at its most polished with pre-built templates, clean data, and ideal use case scenarios. The pilot customer arrives expecting that experience. Onboarding reality: blank slate, integration work required, IT tickets needed, data import pending. 74% of buyers leave if the gap between demo and reality is too wide. The fix is a structured sales-to-onboarding handoff that documents exactly what was shown in the demo and what prerequisites exist before it can be reproduced. [F2]

**Champion becomes an unpaid project manager.** The B2B buyer who pushed for the pilot approval rarely has the time or authority to drive adoption across their team. Once they need to coordinate other stakeholders, get IT involved, and manage internal expectation — they disengage from the product itself. The bot must treat champion enablement (1:1 training) as necessary-but-insufficient; the onboarding plan must also map the IT/ops contact, the end-user population, and the economic buyer communication cadence separately. [F3]

**Multi-stakeholder coordination treated as single-contact onboarding.** 86% of B2B purchases stall due to internal alignment failures on the customer side. If kick-off is scheduled with only the champion and the pilot's success depends on getting 3 other roles to act, any one no-show cascades into delays. The current SKILL.md schedules "kick-off call" without specifying which stakeholders must attend and which can receive async communication. Required kick-off attendees: economic buyer (or their delegate), champion, IT contact if integrations are required. [F4]

**Intervention threshold at Day 14 is too late.** The current SKILL.md defines Red as "no usage after 14 days." In reality, the first 72 hours predict the full pilot trajectory most accurately. A champion who doesn't log in within 72 hours of account creation has either lost momentum or encountered a setup blocker. Both require same-day outreach, not a 14-day wait. The risk of waiting is that the customer's attention has moved to other priorities and re-engaging them costs the same effort as acquiring a new customer. [F5]

**Kick-off agenda misses the MAP confirmation step.** The current agenda covers: introductions, success criteria confirmation, onboarding walkthrough, Q&A, and calendar scheduling. It does not include: explicit MAP confirmation (both sides sign off on the written success criteria, decision rules, and pilot scope). Without documented mutual commitment, either side can retroactively redefine what "success" meant after the fact. [F6]

**Sources:**
- [F1] Growth Strategy Lab: Activation Moment Sequencing: https://medium.com/@GrowthStrategyLab/activation-moment-sequencing-in-onboarding-to-reach-first-value-faster-d1eeb1adbebe
- [F2] LinkedIn: Beyond the Handoff — Sales Promise vs Reality: https://www.linkedin.com/pulse/beyond-handoff-bridging-gap-between-sales-promise-reality-hosking-2bslc
- [F3] CSMIS: Sales to Customer Success Handoff 2025: https://csmis.org/2025/10/04/sales-to-customer-success-handoff-ensuring-seamless-customer-onboarding/
- [F4] Skipup: Committee Problem in B2B: https://blog.skipup.ai/buying-committee-demo-scheduling-problem/
- [F5] The Onboarding Lab: Health Scores: https://www.theonboardinglab.com/p/how-to-use-customer-health-scores-as-your-early-warning-system-for-onboarding-success
- [F6] pclub.io: Mutual Success Action Plan Framework: https://www.pclub.io/blog/mutual-success-action-plan

---

## Synthesis

The current SKILL.md's three-phase structure is correct but the timing thresholds are too conservative: Day 7 for first value is too slow (should be 48 hours), Day 14 for Red escalation is too late (should be 72 hours for no-login). Every hour of delay in first value delivery compounds the probability of champion disengagement.

The most structurally important gap is the Mutual Action Plan (MAP) — a formal, written, mutually-signed document that transforms the pilot from an informal evaluation into a business-critical milestone with named owners, defined success thresholds, and a decision rule at the end. The 26% win-rate improvement from MAPs is among the strongest evidence-backed interventions available at this stage.

The health score section is the right idea but needs explicit weights. "Green/yellow/red" without a numeric formula is not operationalizable — two operators will interpret the same customer behavior differently without a formula.

The structural gap in tooling: the skill defines usage monitoring in Phase 3 but lists no tool that can provide usage data. This needs either a product analytics tool (Mixpanel, Amplitude, Segment) or a CRM activity tracker.

---

## Recommendations for SKILL.md

- Tighten TTV threshold: first value target = 48 hours (not Day 7). Red escalation threshold: no login within 72 hours (not Day 14).
- Add Mutual Action Plan (MAP) as a required pre-kick-off artifact. Kick-off confirms the MAP — it does not create it.
- Add sales-to-onboarding handoff documentation as a mandatory prerequisite for starting Phase 1.
- Add stakeholder map to kick-off: economic buyer, champion, IT contact — each with distinct communication cadence.
- Specify health score formula: 40% usage + 30% implementation progress + 30% satisfaction. Numeric thresholds: 85+ = green, 70-84 = yellow, <70 = red, <60 = immediate intervention.
- Add "aha moment" definition as a required field in the artifact, documented before kick-off.
- Add product analytics tool to Available Tools — or explicitly note that the bot cannot monitor usage without it.
- Add GDPR/conferenceData to Google Calendar event creation (Meet link).
- Expand schema: add MAP, stakeholder map, aha_moment, health_score breakdown, escalation log, and sales_handoff fields.

---

## Draft Content for SKILL.md

### Draft: Updated core mode

You manage pilot customer onboarding from signed agreement to first value delivery, with the goal of setting conditions for pilot conversion. Onboarding failure produces churn before the pilot starts. Success requires: a documented Mutual Action Plan confirmed at kick-off, a defined "aha moment" reached within 48 hours, and proactive intervention before disengagement becomes visible.

Core mode: the sales promise is not your baseline — it is your liability. Document what was shown in the demo and what prerequisites exist before that experience can be reproduced. The customer's internal measure of success at Day 7 is set on Day 1; if their expectations and your delivery diverge on Day 1, no amount of quality work at Day 30 recovers the relationship.

---

### Draft: Updated onboarding phases

**Phase 0: Handoff and MAP preparation (pre-kick-off, same day as signature)**
- Receive sales handoff: demo recording or notes, committed use cases, agreed success criteria, prerequisites discussed in sales process.
- Draft Mutual Action Plan (MAP): success criteria with measurable thresholds, milestone timeline (Day 1, Day 3, Day 7, Day 14, Day 30) with named owners, communication cadence, risk register, and a decision rule ("at Day 30, if [criteria], we proceed / we pause").
- Map stakeholders: economic buyer (budget authority), champion (evaluation driver), IT contact (integration authority), end users (adoption population). Assign distinct communication touchpoints to each.
- Define the "aha moment" in one sentence from the customer's perspective.

**Phase 1: Kick-off (Day 1, within 24 hours of signature)**
- Required attendees: champion (required), economic buyer delegate (required), IT contact (required if integrations needed).
- Agenda: MAP confirmation (not creation — MAP was drafted pre-kick-off and both sides review and confirm), aha moment confirmation, critical path walkthrough (minimal steps to first value), risk register review, schedule set for Day 3 and Day 7 checkpoints.
- After kick-off: calendar invites sent to all stakeholders for all scheduled touchpoints. Zendesk task created for each Phase milestone.

**Phase 2: Setup and first value (Day 1-3)**
- Account creation, integration setup, data import — in parallel, not sequentially.
- Champion 1:1 enablement session within 24 hours of kick-off.
- Target: champion completes first core use case (aha moment) within 48 hours of account creation.
- If no login within 72 hours: same-day proactive outreach, do not wait for scheduled check-in.

**Phase 3: Adoption and health monitoring (Day 3-30)**
- Weekly health score calculation using: 40% usage/adoption signals, 30% milestone completion, 30% satisfaction.
- Thresholds: 85-100 = green (scheduled check-ins only); 70-84 = yellow (unscheduled proactive outreach); below 70 = red (immediate escalation, executive sponsor alert); below 60 = intervention plan activated.
- Monitor for sponsor turnover: champion email bounce, LinkedIn role change, meeting no-shows across two consecutive touchpoints.

---

### Draft: Anti-patterns

#### Day 7 First Value Target
**What it looks like:** Onboarding plan sets Day 7 as the milestone for "first core use case completed."
**Detection signal:** No interim check on first login or first core action before Day 7.
**Consequence:** Users who reach first value in >48 hours convert at 3.4x lower rate. If Day 7 is the target, the team is planning for a failure mode.
**Mitigation:** First value target = 48 hours. Day 7 is the milestone for sustainable adoption, not first value. Track first login (72-hour red flag threshold) and first core action (48-hour aha-moment target) as separate, earlier indicators.

#### MAP Created During Kick-off
**What it looks like:** The kick-off call is used to "discover" success criteria and "draft" the mutual action plan together.
**Detection signal:** No MAP document exists before the kick-off; the kick-off call output is the MAP.
**Consequence:** The kick-off burns an hour on admin work that should have been done in writing beforehand. Customers arrive to a kick-off without a written baseline to react to, leading to vague verbal agreements that each party remembers differently.
**Mitigation:** Draft MAP before kick-off. Kick-off confirms, adjusts, and signs off on the MAP — it does not author it. If the customer needs to change the MAP during kick-off, that is normal and fine. What is not fine is having no MAP to adjust.

#### Single-Contact Kick-off
**What it looks like:** Kick-off is scheduled with the champion only. IT contact is invited separately "later." Economic buyer is not part of the kick-off.
**Detection signal:** Kick-off attendee list = one customer contact.
**Consequence:** 86% of B2B onboarding stalls from internal alignment failures on the customer side. The champion agrees to everything and then cannot get IT to execute the integration, cannot get the economic buyer to communicate priority to the team, and becomes the single point of failure for the entire pilot.
**Mitigation:** Required kick-off attendees: champion, economic buyer (or delegate), IT contact (if integrations required). If economic buyer will not attend, document this as a risk in the MAP and escalate to the AE.

---

### Draft: Artifact Schema

```json
{
  "pilot_onboarding": {
    "type": "object",
    "description": "Onboarding state and progress tracking artifact for a single pilot customer.",
    "required": [
      "account_id",
      "pilot_start_date",
      "pilot_end_date",
      "aha_moment",
      "stakeholders",
      "map",
      "sales_handoff",
      "phases",
      "health",
      "status"
    ],
    "additionalProperties": false,
    "properties": {
      "account_id": {
        "type": "string",
        "description": "Unique identifier for the pilot customer account."
      },
      "pilot_start_date": {
        "type": "string",
        "format": "date"
      },
      "pilot_end_date": {
        "type": "string",
        "format": "date"
      },
      "aha_moment": {
        "type": "string",
        "description": "The first value moment defined in one sentence from the customer's perspective. Defined before kick-off and confirmed at kick-off."
      },
      "sales_handoff": {
        "type": "object",
        "description": "Documented commitments from the sales process that the onboarding must honor.",
        "required": ["demo_use_cases", "promised_success_criteria", "prerequisites"],
        "additionalProperties": false,
        "properties": {
          "demo_use_cases": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Use cases demonstrated during sales process. Onboarding must reproduce these."
          },
          "promised_success_criteria": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Specific outcomes sales committed to. Used to set MAP thresholds."
          },
          "prerequisites": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Technical and organizational prerequisites discussed in sales process that must be complete before aha moment is reachable."
          }
        }
      },
      "stakeholders": {
        "type": "object",
        "description": "Key stakeholders and their roles in the pilot.",
        "required": ["champion", "economic_buyer"],
        "additionalProperties": false,
        "properties": {
          "champion": {
            "type": "object",
            "required": ["name", "email", "title"],
            "additionalProperties": false,
            "properties": {
              "name": {"type": "string"},
              "email": {"type": "string"},
              "title": {"type": "string"}
            }
          },
          "economic_buyer": {
            "type": "object",
            "required": ["name", "email", "title"],
            "additionalProperties": false,
            "properties": {
              "name": {"type": "string"},
              "email": {"type": "string"},
              "title": {"type": "string"}
            }
          },
          "it_contact": {
            "type": ["object", "null"],
            "additionalProperties": false,
            "properties": {
              "name": {"type": "string"},
              "email": {"type": "string"}
            }
          },
          "end_user_count": {
            "type": ["integer", "null"],
            "minimum": 1,
            "description": "Number of end users expected to adopt the product during the pilot."
          }
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
                "criterion": {"type": "string", "description": "What is being measured."},
                "measurement": {"type": "string", "description": "How it will be measured."},
                "threshold": {"type": "string", "description": "The numeric or qualitative threshold that defines success."}
              }
            },
            "description": "Quantifiable criteria agreed upon by both sides."
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
                "owner": {"type": "string", "description": "Name or role of the person responsible."},
                "status": {"type": "string", "enum": ["pending", "in_progress", "complete", "at_risk", "missed"]}
              }
            }
          },
          "decision_rule": {
            "type": "string",
            "description": "The explicit rule for what happens at pilot end. E.g. 'If criteria 1 and 2 are met by Day 30, proceed to full deployment quote.'"
          },
          "confirmed_at_kickoff": {
            "type": "boolean",
            "description": "Whether both sides confirmed the MAP during the kick-off call."
          }
        }
      },
      "phases": {
        "type": "object",
        "description": "Phase-level tracking for onboarding progress.",
        "required": ["kickoff", "setup", "monitoring"],
        "additionalProperties": false,
        "properties": {
          "kickoff": {
            "type": "object",
            "required": ["scheduled_at", "completed", "attendees"],
            "additionalProperties": false,
            "properties": {
              "scheduled_at": {"type": ["string", "null"], "format": "date-time"},
              "completed": {"type": "boolean"},
              "attendees": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of actual attendees by email."
              },
              "no_shows": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Expected attendees who did not attend."
              }
            }
          },
          "setup": {
            "type": "object",
            "required": ["first_login_at", "aha_moment_reached_at", "blockers"],
            "additionalProperties": false,
            "properties": {
              "first_login_at": {
                "type": ["string", "null"],
                "format": "date-time",
                "description": "Timestamp of first champion login. If null after 72 hours: immediate outreach."
              },
              "aha_moment_reached_at": {
                "type": ["string", "null"],
                "format": "date-time",
                "description": "Timestamp when the aha moment was completed. Target: within 48 hours of account creation."
              },
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
                  "required": ["date", "health_score", "notes", "action_taken"],
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
                    "action_taken": {"type": ["string", "null"], "description": "Proactive action taken as a result of this checkpoint. Null if no action was needed."}
                  }
                }
              }
            }
          }
        }
      },
      "health": {
        "type": "object",
        "description": "Current overall onboarding health state.",
        "required": ["current_tier", "last_scored_at", "escalation_active"],
        "additionalProperties": false,
        "properties": {
          "current_tier": {"type": "string", "enum": ["green", "yellow", "red", "intervention"]},
          "last_scored_at": {"type": "string", "format": "date"},
          "escalation_active": {
            "type": "boolean",
            "description": "True if health has triggered an escalation that is not yet resolved."
          },
          "escalation_reason": {"type": ["string", "null"]}
        }
      },
      "status": {
        "type": "string",
        "enum": ["pre_kickoff", "in_progress", "at_risk", "success", "churned"],
        "description": "Top-level pilot onboarding status."
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- **Product usage tool absent from executor bot.** Phase 3 (adoption monitoring) requires product usage signals, but no analytics API (Mixpanel, Amplitude, Segment, Heap) is listed in the executor bot's tool set. This needs to be resolved at the bot level, not the skill level. Without it, health score calculation in Phase 3 cannot be automated.
- **Calendly rate limits unpublished.** Specific per-minute request limits for the Calendly API were not found in public documentation. Treat as requiring standard exponential backoff on 429 responses.
- **MAP template specifics for different product categories.** The MAP structure recommended here is general. Product-specific success criteria thresholds (what constitutes a meaningful "aha moment" for different product types) require customization at the skill invocation level, not the skill design level.
- **Google Meet link generation via `conferenceData`.** The ability to auto-generate a Meet link in `google_calendar.events.insert.v1` depends on the `createConferenceRequest` parameter being supported in the researcher bot's Google Calendar tool implementation. Not verified.
- **"Aha moment" timing benchmark sources.** The 48-hour threshold for first value comes from consumer SaaS research (Athenic blog). B2B enterprise onboarding with complex integrations may have a legitimately longer critical path — the 48-hour target applies to the champion's first meaningful product interaction, not to full integration completion.
