# Research: discovery-scheduling

**Skill path:** `flexus_simple_bots/researcher/skills/discovery-scheduling/`  
**Bot:** researcher  
**Research date:** 2026-03-05  
**Status:** complete

---

## Context

`discovery-scheduling` covers interview scheduling logistics and participant panel operations between recruitment and interview capture. The skill is used to turn qualified participants into completed sessions while maintaining traceability from `participant_id` to `study_id`, consent context, and final session status.

In 2024-2026 guidance, scheduling reliability is treated as an operations discipline, not only a calendar action. The recurring risks are no-shows, late cancellations, timezone errors, state drift across tools, and weak traceability for audits and downstream analysis.

---

## Definition of Done

Research is complete when ALL of the following are satisfied:

- [x] At least 4 distinct research angles are covered (see Research Angles section)
- [x] Each finding has a source URL or named reference
- [x] Methodology section covers practical how-to, not just theory
- [x] Tool/API landscape is mapped with at least 3-5 concrete options
- [x] At least one "what not to do" / common failure mode is documented
- [x] Output schema recommendations are grounded in real-world data shapes
- [x] Gaps section honestly lists what was NOT found or is uncertain
- [x] All findings are from 2024–2026 unless explicitly marked as evergreen

---

## Quality Gates

Before marking status `complete`, verify:

- No filler claims without concrete backing or links
- No invented APIs, methods, or endpoint names
- Contradictions between sources are explicitly called out
- Findings are synthesized into usable SKILL.md draft content

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

1. **[2024-2025] 24-hour notice policies are common operational defaults** for cancellation/reschedule behavior in participant marketplaces. This should be modeled as explicit policy (`policy_notice_hours`) rather than implied team habit.  
2. **[2025] No-show handling is first-class workflow logic** with explicit replacement/downscope paths, not an afterthought.  
3. **[2025] Invite operations are target-aware and cadence-driven**, with pause/resume behavior tied to completion targets.  
4. **[2025] Minimum scheduling notice is configurable at platform level**, often in hours, and can be less strict than internal policy.  
5. **[2025] Reschedule flows increasingly require reason capture and state rollback**, which supports immutable transition logging.  
6. **[2025-2026] Communication quality is a reliability control**: timezone clarity, concise logistics, and clear late/reschedule channel reduce no-show risk.  
7. **[2024-2026] Traceability expectations are rising** in consent-adjacent workflows (identity linkage, timestamps, retrievability).

**Contradiction to keep in SKILL.md:**  
Policy expectations (commonly 24h) can be stricter than platform technical cutoffs (hours-level). The skill should model both and enforce policy as default.

**Sources:**
- https://www.userinterviews.com/support/canceling-participants
- https://www.userinterviews.com/support/cancel-reschedule
- https://www.userinterviews.com/support/replacing-no-shows
- https://www.userinterviews.com/support/scheduled-invites
- https://www.userinterviews.com/support/editing-scheduling-buffer
- https://maze.co/product-updates/en/new-request-to-reschedule-for-moderated-studies-pi1PimFo
- https://www.tremendous.com/blog/reduce-research-participant-no-shows/
- https://www.userinterviews.com/support/managing-private-projects
- https://www.fda.gov/media/166215/download
- https://www.irb.pitt.edu/econsent-guidance

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

1. **Calendly API:** OAuth/PAT auth, scope-based permissions, scheduled-events/invitee endpoints, scheduling links, and cancellation APIs are documented.  
2. **Calendly constraints:** no dedicated reschedule endpoint; some behavior depends on plan/tier; release feed shows ongoing changes in 2024-2026.  
3. **Google Calendar API:** `events.insert`, `events.list`, `events.watch`, `channels.stop`, and `freeBusy.query` cover core scheduling/reconciliation needs.  
4. **Google sync/limits:** incremental sync via `syncToken`; `410 Gone` requires full resync; quota/rate failures (`403`, `429`) require backoff.  
5. **Qualtrics v3 APIs:** datacenter-specific base URL, token auth, strict parameter casing, and brand-level policy/rate controls; mailing lists/contacts/distributions are core panel primitives.  
6. **User Interviews APIs:** Hub/Recruit surfaces with participant CRUD, batch updates, recruit lifecycle controls, and documented rate-limit semantics (`429` + `Retry-After`).  
7. **Cross-tool architecture pattern:** one participant-state system + one calendar source + one distribution/scheduling surface, reconciled by stable IDs and sync metadata.

**Concrete options mapped for this skill:** Calendly, Google Calendar API, Qualtrics, User Interviews Hub API, User Interviews Recruit API.

**Sources:**
- https://developer.calendly.com/authentication
- https://developer.calendly.com/personal-access-tokens
- https://developer.calendly.com/scopes
- https://developer.calendly.com/frequently-asked-questions
- https://developer.calendly.com/rss.xml
- https://developers.google.com/workspace/calendar/api/v3/reference/events/insert
- https://developers.google.com/workspace/calendar/api/v3/reference/events/list
- https://developers.google.com/workspace/calendar/api/v3/reference/events/watch
- https://developers.google.com/workspace/calendar/api/v3/reference/channels/stop
- https://developers.google.com/workspace/calendar/api/v3/reference/freebusy/query
- https://developers.google.com/workspace/calendar/api/guides/sync
- https://developers.google.com/calendar/api/guides/errors
- https://developers.google.com/calendar/api/guides/quota
- https://www.qualtrics.com/support/integrations/api-integration/overview/
- https://www.qualtrics.com/support/integrations/api-integration/common-api-questions-by-product/
- https://www.qualtrics.com/support/survey-platform/sp-administration/organization-settings/
- https://api-docs.userinterviews.com/reference/introduction
- https://api-docs.userinterviews.com/reference/authentication
- https://api-docs.userinterviews.com/reference/rate_limiting
- https://api-docs.userinterviews.com/reference/errors
- https://api-docs.userinterviews.com/reference/get_api-participants-2
- https://api-docs.userinterviews.com/reference/post_api-participants-2
- https://api-docs.userinterviews.com/reference/patch_api-participants-batches-2

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

1. **Metric definitions must be explicit.** Completion, response/participation, no-show, cancellation, reschedule, and coverage are not interchangeable (evergreen standards).  
2. **Moderated no-show often falls in single-digit to low-double-digit ranges.** A practical planning baseline around 10% is conservative (context-dependent).  
3. **Over-recruitment is usually necessary, not exceptional.** Recent operational data supports maintaining a replacement buffer.  
4. **Incentive changes can shift schedule outcomes,** so attendance changes should be interpreted with compensation context.  
5. **Reminder systems are one of the highest-leverage controls;** strong older evidence still supports multi-reminder designs (marked evergreen/older benchmark).  
6. **Lead-time is a risk multiplier;** as lead-time rises, reconfirmation rigor should increase.  
7. **Panel health cannot be inferred from completion alone;** retention and invitation burden matter.

**Signal vs noise trigger rules to include in skill draft:**
- Trigger action if rolling no-show exceeds 10% or rises by >=2pp from baseline.
- Trigger action if `coverage_vs_target < 0.90` near close window.
- Trigger action when cancellation/reschedule trend rises for two windows, not one isolated spike.

**Sources:**
- https://www.jmir.org/2012/1/e8/ (evergreen/older benchmark)
- https://aapor.org/response-rates/ (evergreen)
- https://aapor.org/standards-and-ethics/standard-definitions/ (evergreen)
- https://measuringu.com/typical-no-show-rate-for-moderated-studies/
- https://measuringu.com/how-much-should-you-over-recruit/
- https://www.userinterviews.com/blog/research-incentives-report
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9126539/ (evergreen/older benchmark)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC5093388/ (evergreen/older benchmark)
- https://publichealthscotland.scot/publications/cancelled-planned-operations/cancelled-planned-operations-month-ending-31-may-2025/
- https://www.pewresearch.org/short-reads/2024/06/26/q-and-a-what-is-the-american-trends-panel-and-how-has-it-changed/
- https://ssrs.com/insights/when-does-survey-burden-become-too-high-or-too-low-in-probability-panels/

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

1. **Timezone ambiguity anti-pattern:** local-only or ambiguous labels (for example `EST`) without canonical `tzid` and UTC create avoidable no-shows.  
2. **TZ database drift anti-pattern:** stale timezone data can shift future events around DST/legal changes.  
3. **Availability snapshot anti-pattern:** treating free/busy checks as lock/hold causes double-booking race conditions.  
4. **Reminder-without-response anti-pattern:** sends are tracked, but participant action telemetry is missing.  
5. **Missing compliance provenance anti-pattern:** schedule state changes have no lawful-basis/consent linkage.  
6. **Over-messaging anti-pattern:** high touch count without cadence controls degrades panel quality.  
7. **Status collapse anti-pattern:** every failure labeled `cancelled` prevents meaningful remediation.

**Bad output example signature:**  
No `participant_id`, no `study_id`, no UTC timestamp, no `tzid`, no initiator, no reason code.

**Good output example signature:**  
Append-only transition log with `from_status`, `to_status`, `actor`, `reason_code`, UTC+timezone fields, reminder outcomes, and source-system provenance.

**Sources:**
- https://data.iana.org/time-zones/tzdb/NEWS
- https://www.rfc-editor.org/rfc/rfc5545 (evergreen)
- https://developers.google.com/calendar/api/concepts/events-calendars
- https://developers.google.com/workspace/calendar/api/v3/reference/freebusy/query
- https://developers.google.com/calendar/api/concepts/reminders
- https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/recruitment-and-selection/data-protection-and-recruitment/
- https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/data-minimisation/
- https://www.userinterviews.com/support/replacing-no-shows

---

### Angle 5+: Compliance, Traceability, and Retention Controls
> Domain-specific angle: which controls make scheduling artifacts auditable and policy-safe?

**Findings:**

1. **Traceability needs more than IDs:** include notice/consent versioning, actor attribution, and immutable history.  
2. **Retention controls must be explicit in artifacts:** class + expiry + legal-hold flag.  
3. **Role-based data masking is required** for operational sharing without overexposure of participant PII.  
4. **Cross-system mismatch handling must be explicit:** source system, source record ID, last sync timestamp, mismatch fields.

**Sources:**
- https://www.fda.gov/media/166215/download
- https://www.irb.pitt.edu/econsent-guidance
- https://docs.openclinica.com/oc4/using-openclinica-as-a-data-manager/audit-log
- https://swissethics.ch/assets/studieninformationen/240825_guidance_e_consent_v2.1_web.pdf
- https://www.eeoc.gov/employers/recordkeeping-requirements
- https://www.ecfr.gov/current/title-29/subtitle-B/chapter-XIV/part-1602/section-1602.14
- https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/storage-limitation/

---

## Synthesis

The research converges on one main point: interview scheduling quality is determined by policy and state discipline, not by calendar tooling alone. Across sources, successful operations define explicit state transitions, reason-coded outcomes, and traceability metadata that survives system sync and audit review.

A key contradiction is intentional and should be preserved in SKILL guidance: platform cutoffs can be permissive (hours-level), while policy windows are often stricter (commonly 24h). The skill should enforce policy-first behavior with explicit exception paths, rather than inheriting platform defaults.

Interpretation guidance should use operational trigger bands rather than one absolute benchmark. No-show and cancellation are context-sensitive and should be segmented by modality and audience, with confounder checks (incentive changes, lead-time, deliverability) before escalation.

The highest-value improvements for `SKILL.md` are: state machine formalization, reminder telemetry requirements, cross-system reconciliation fields, and schema-level enforcement of compliance/retention metadata. These controls directly address the most common real-world failure modes.

---

## Recommendations for SKILL.md

> Concrete changes to add/replace in the skill.

- [x] Add policy-vs-platform timing controls (`policy_notice_hours`, `platform_cutoff_hours`) and exception flow for late changes.
- [x] Add explicit lifecycle states with append-only transition log requirements.
- [x] Add deterministic no-show branch with replacement/downscope decision within SLA.
- [x] Add reminder telemetry requirements (`delivery_status`, participant action, action timestamp).
- [x] Add cross-system reconciliation fields (`source_system`, `source_record_id`, `last_synced_at`, mismatch status).
- [x] Add interpretation section with formulas, trigger bands, and evidence-tier labeling.
- [x] Add anti-pattern warning blocks with detection signals and mitigation steps.
- [x] Expand schema with compliance envelope and retention controls (`retention_class`, `expires_at_utc`, `legal_hold`).
- [x] Keep tool examples mapped to verified methods/endpoints only.

---

## Draft Content for SKILL.md

> Paste-ready draft text. This section is intentionally the longest section.

### Draft: Operating Model

You run scheduling as a controlled lifecycle, not as one-off booking actions. Every session must be traceable from `participant_id` and `study_id` to consent context, scheduled timestamps, and final outcome. If a required traceability field is missing, do not proceed with scheduling updates until the record is complete.

You must separate policy decisions from platform constraints. Platform capability determines what can technically be executed; policy determines what is allowed in normal operations. When these differ, policy remains authoritative and exceptions must be explicitly logged.

### Draft: Policy Window Logic

Define these controls per study:

- `policy_notice_hours` (default `24`)
- `platform_cutoff_hours` (tool-dependent)
- `late_change_exception_required` (default `true`)
- `max_reschedule_attempts_per_participant` (default `1`)

Decision sequence for cancellation/reschedule requests:

1. Compute `hours_to_session` from canonical UTC timestamps.
2. If `hours_to_session < platform_cutoff_hours`, block technical action and log `decision_code=platform_cutoff`.
3. Else if `hours_to_session < policy_notice_hours`, require exception reason + approver attribution.
4. Else process normal flow.

Do not silently downgrade policy to match tool defaults.

### Draft: Lifecycle and Workflow

Required states:

- `invited`
- `scheduled`
- `reschedule_requested`
- `rescheduled`
- `completed`
- `no_show`
- `cancelled`

Required workflow:

1. Validate schedule-ready roster (`participant_id`, `study_id`, timezone, contact channel, consent linkage).
2. Publish controlled availability from approved interviewer calendars.
3. Send scheduling outreach with minimized sensitive content.
4. Run reminder cadence (for example `T-72h`, `T-24h`, `T-2h`) and capture participant actions.
5. Apply grace window at session start; then set reason-coded outcome.
6. If no-show/cancel reduces coverage below target, trigger replacement flow immediately.
7. Reconcile session state across source tools daily until closure.

### Draft: Available Tools

Use only methods that are available in runtime connectors.

```python
# Calendly
calendly(op="call", args={
  "method_id": "calendly.scheduled_events.list.v1",
  "user": "https://api.calendly.com/users/xxx",
  "count": 50,
  "min_start_time": "2024-01-01T00:00:00Z"
})

calendly(op="call", args={
  "method_id": "calendly.scheduled_events.invitees.list.v1",
  "uuid": "event_uuid",
  "count": 50
})

# Google Calendar
google_calendar(op="call", args={
  "method_id": "google_calendar.events.insert.v1",
  "calendarId": "primary",
  "summary": "Customer Interview",
  "start": {"dateTime": "2024-03-01T10:00:00-05:00"},
  "end": {"dateTime": "2024-03-01T10:45:00-05:00"},
  "attendees": [{"email": "participant@company.com"}]
})

google_calendar(op="call", args={
  "method_id": "google_calendar.events.list.v1",
  "calendarId": "primary",
  "timeMin": "2024-03-01T00:00:00Z",
  "timeMax": "2024-03-31T00:00:00Z"
})

# Qualtrics
qualtrics(op="call", args={
  "method_id": "qualtrics.contacts.create.v1",
  "directoryId": "POOL_xxx",
  "mailingListId": "CG_xxx",
  "firstName": "Name",
  "lastName": "Surname",
  "email": "participant@company.com"
})

qualtrics(op="call", args={
  "method_id": "qualtrics.distributions.create.v1",
  "surveyId": "SV_xxx",
  "mailingListId": "CG_xxx",
  "fromEmail": "research@company.com",
  "fromName": "Research Team",
  "subject": "Interview Invitation"
})

# User Interviews
userinterviews(op="call", args={
  "method_id": "userinterviews.participants.create.v1",
  "name": "Participant Name",
  "email": "participant@company.com",
  "project_id": "proj_id"
})

userinterviews(op="call", args={
  "method_id": "userinterviews.participants.update.v1",
  "participant_id": "part_id",
  "status": "scheduled"
})
```

Reliability rules:

- Treat Google `410 Gone` sync errors as full-resync events.
- Back off on `429` and quota-style `403` responses.
- Do not model Calendly reschedule as a hidden one-step operation; preserve old/new state transitions explicitly.
- For Qualtrics, validate datacenter and strict parameter casing before runtime calls.

### Draft: Signal Interpretation

Compute these metrics:

- `no_show_rate = confirmed_no_shows / confirmed_scheduled`
- `cancellation_rate = cancelled_sessions / planned_sessions`
- `reschedule_rate = rescheduled_sessions / planned_sessions`
- `coverage_vs_target = completed_sessions / target_count`
- `lead_time_days = session_start_utc - booked_at_utc`
- `over_recruitment_rate = (recruited_count - target_count) / target_count`

Escalation triggers:

1. Rolling no-show >10% OR +2pp rise from baseline.
2. Coverage drops below 90% near close window.
3. Cancellation/reschedule trend rises for two consecutive windows.

Interpretation guardrails:

- Segment by modality and audience (for example B2B/B2C, remote/in-person).
- Check incentive and lead-time confounders before declaring process failure.
- Label evidence tier (`strong`, `moderate`, `weak`) for every threshold claim.

### Draft: Anti-Pattern Warnings

> [!WARNING]
> **Anti-pattern: Timezone ambiguity**
> Detection signal: missing UTC timestamp or missing canonical `tzid`.  
> Consequence: avoidable no-shows from mismatched local-time rendering.  
> Mitigation: require UTC + IANA timezone at write time; reject ambiguous time labels.

> [!WARNING]
> **Anti-pattern: Availability snapshot treated as lock**
> Detection signal: overlapping bookings after reschedule/update path.  
> Consequence: double-booking and forced last-minute changes.  
> Mitigation: use hold-then-commit logic with conflict recheck and idempotency keys.

> [!WARNING]
> **Anti-pattern: Reminder without action telemetry**
> Detection signal: reminders sent but no `confirmed/cancelled/reschedule_requested` capture.  
> Consequence: false readiness signal and late no-show surprises.  
> Mitigation: persist delivery and participant-action events for each reminder.

> [!WARNING]
> **Anti-pattern: Compliance provenance missing**
> Detection signal: state change without lawful-basis/notice/consent reference.  
> Consequence: weak auditability and policy risk.  
> Mitigation: enforce compliance envelope fields as required schema.

### Draft: Schema additions

```json
{
  "interview_schedule": {
    "type": "object",
    "required": [
      "study_id",
      "policy",
      "sessions",
      "coverage_status",
      "metrics",
      "audit_log"
    ],
    "additionalProperties": false,
    "properties": {
      "study_id": {
        "type": "string",
        "description": "Unique study identifier for this scheduling artifact."
      },
      "policy": {
        "type": "object",
        "required": [
          "policy_notice_hours",
          "platform_cutoff_hours",
          "late_change_exception_required"
        ],
        "additionalProperties": false,
        "properties": {
          "policy_notice_hours": {
            "type": "integer",
            "minimum": 1,
            "description": "Operational policy window for normal cancel/reschedule handling."
          },
          "platform_cutoff_hours": {
            "type": "integer",
            "minimum": 0,
            "description": "Provider technical cutoff window."
          },
          "late_change_exception_required": {
            "type": "boolean",
            "description": "If true, changes inside policy window require explicit exception log."
          }
        }
      },
      "sessions": {
        "type": "array",
        "items": {
          "type": "object",
          "required": [
            "session_id",
            "participant_id",
            "study_id",
            "status",
            "scheduled_start_utc",
            "scheduled_end_utc",
            "scheduled_tzid",
            "source_system",
            "source_record_id"
          ],
          "additionalProperties": false,
          "properties": {
            "session_id": {
              "type": "string",
              "description": "Unique session identifier."
            },
            "participant_id": {
              "type": "string",
              "description": "Participant identifier linked to recruitment records."
            },
            "study_id": {
              "type": "string",
              "description": "Study identifier duplicated at session level for traceability."
            },
            "status": {
              "type": "string",
              "enum": [
                "invited",
                "scheduled",
                "reschedule_requested",
                "rescheduled",
                "completed",
                "no_show",
                "cancelled"
              ],
              "description": "Current lifecycle status."
            },
            "scheduled_start_utc": {
              "type": "string",
              "format": "date-time",
              "description": "Canonical UTC start timestamp."
            },
            "scheduled_end_utc": {
              "type": "string",
              "format": "date-time",
              "description": "Canonical UTC end timestamp."
            },
            "scheduled_tzid": {
              "type": "string",
              "description": "Canonical IANA timezone identifier."
            },
            "source_system": {
              "type": "string",
              "enum": ["calendly", "google_calendar", "qualtrics", "userinterviews", "manual"],
              "description": "System of origin for this session record."
            },
            "source_record_id": {
              "type": "string",
              "description": "Provider-native ID for reconciliation."
            },
            "last_synced_at": {
              "type": "string",
              "format": "date-time",
              "description": "Last successful sync timestamp from source system."
            },
            "reminder_events": {
              "type": "array",
              "description": "Reminder send/delivery/action telemetry.",
              "items": {
                "type": "object",
                "required": ["sent_at_utc", "delivery_status"],
                "additionalProperties": false,
                "properties": {
                  "sent_at_utc": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Reminder send timestamp."
                  },
                  "delivery_status": {
                    "type": "string",
                    "enum": ["sent", "delivered", "failed", "bounced"],
                    "description": "Delivery outcome."
                  },
                  "participant_action": {
                    "type": "string",
                    "enum": ["none", "confirmed", "cancelled", "reschedule_requested"],
                    "description": "Participant action observed from reminder."
                  },
                  "action_at_utc": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Timestamp of participant action if present."
                  }
                }
              }
            },
            "compliance_envelope": {
              "type": "object",
              "required": ["lawful_basis", "privacy_notice_version", "consent_ref", "retention_class"],
              "additionalProperties": false,
              "properties": {
                "lawful_basis": {
                  "type": "string",
                  "description": "Legal/organizational basis for participant-data processing."
                },
                "privacy_notice_version": {
                  "type": "string",
                  "description": "Version of notice shown when scheduling data was captured."
                },
                "consent_ref": {
                  "type": "string",
                  "description": "Reference to consent artifact."
                },
                "retention_class": {
                  "type": "string",
                  "description": "Retention policy class assigned to this record."
                },
                "expires_at_utc": {
                  "type": "string",
                  "format": "date-time",
                  "description": "Eligibility timestamp for purge/anonymization (absent legal hold)."
                },
                "legal_hold": {
                  "type": "boolean",
                  "description": "If true, record is exempt from routine purge until hold release."
                }
              }
            }
          }
        }
      },
      "coverage_status": {
        "type": "object",
        "required": ["scheduled_count", "completed_count", "target_count"],
        "additionalProperties": false,
        "properties": {
          "scheduled_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Total currently scheduled sessions."
          },
          "completed_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Total completed sessions."
          },
          "target_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Study target completion count."
          }
        }
      },
      "metrics": {
        "type": "object",
        "required": [
          "no_show_rate",
          "cancellation_rate",
          "reschedule_rate",
          "coverage_vs_target",
          "over_recruitment_rate"
        ],
        "additionalProperties": false,
        "properties": {
          "no_show_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Confirmed no-shows divided by confirmed scheduled sessions."
          },
          "cancellation_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Cancelled sessions divided by planned sessions."
          },
          "reschedule_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Rescheduled sessions divided by planned sessions."
          },
          "coverage_vs_target": {
            "type": "number",
            "minimum": 0,
            "description": "Completed sessions divided by target count."
          },
          "over_recruitment_rate": {
            "type": "number",
            "description": "Recruitment surplus/deficit ratio against target."
          }
        }
      },
      "audit_log": {
        "type": "array",
        "description": "Append-only transition events.",
        "items": {
          "type": "object",
          "required": ["event_id", "session_id", "from_status", "to_status", "event_at_utc", "actor_type", "actor_id", "reason_code"],
          "additionalProperties": false,
          "properties": {
            "event_id": {
              "type": "string",
              "description": "Unique event log ID."
            },
            "session_id": {
              "type": "string",
              "description": "Session associated with this transition."
            },
            "from_status": {
              "type": "string",
              "description": "Previous lifecycle status."
            },
            "to_status": {
              "type": "string",
              "description": "New lifecycle status."
            },
            "event_at_utc": {
              "type": "string",
              "format": "date-time",
              "description": "Transition timestamp in UTC."
            },
            "actor_type": {
              "type": "string",
              "enum": ["system", "researcher", "participant"],
              "description": "Actor category responsible for transition."
            },
            "actor_id": {
              "type": "string",
              "description": "Actor identifier where available."
            },
            "reason_code": {
              "type": "string",
              "description": "Normalized transition reason."
            }
          }
        }
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Public benchmark quality for UX interview scheduling remains fragmented; many numeric ranges are platform/operator-specific.
- Some vendor docs are evergreen and not date-stamped, so they are capability references rather than dated change logs.
- Qualtrics tenant-specific throttling/policies can vary by brand admin settings.
- Cross-vendor standard definitions for `reschedule_rate` are inconsistent; SKILL.md should define this explicitly.

**Skill path:** `flexus_simple_bots/researcher/skills/discovery-scheduling/`
**Bot:** researcher
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`discovery-scheduling` handles interview logistics and participant panel management between recruitment and interview capture. In practice this means converting qualified participants into attended sessions while preserving an auditable chain from `participant_id` to `study_id`, consent state, and session outcome. This skill is used whenever a research team must coordinate one-on-one interviews or panel-based sessions across tools such as Calendly, Google Calendar, Qualtrics, and User Interviews.

The core operational problem is not "booking a calendar slot"; it is managing scheduling risk. The most common delivery failures are no-shows, late cancellations, timezone mistakes, over-messaging, and missing traceability fields that break downstream analytics and compliance evidence. Recent 2024-2026 practitioner updates show a shift toward explicit policy windows (for example 24-hour cancellation expectations), stateful no-show replacement flows, and automation tied to target gaps instead of one-time invite blasts.

---

## Definition of Done

Research is complete when ALL of the following are satisfied:

- [x] At least 4 distinct research angles are covered (see Research Angles section)
- [x] Each finding has a source URL or named reference
- [x] Methodology section covers practical how-to, not just theory
- [x] Tool/API landscape is mapped with at least 3-5 concrete options
- [x] At least one "what not to do" / common failure mode is documented
- [x] Output schema recommendations are grounded in real-world data shapes
- [x] Gaps section honestly lists what was NOT found or is uncertain
- [x] All findings are from 2024–2026 unless explicitly marked as evergreen

---

## Quality Gates

Before marking status `complete`, verify:

- No generic filler without concrete backing; all claims below are linked to named sources
- No invented tool names or API endpoints; all endpoint claims map to vendor docs
- Contradictions between sources are called out explicitly (policy windows vs platform cutoffs; automation cadence vs over-messaging risk)
- Findings volume is within target range and synthesized into actionable draft content

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

Practitioner guidance in 2024-2026 converges on a scheduling playbook with explicit policy windows, state transitions, and target-aware invite automation rather than ad-hoc manual coordination.

1. **[2024-2025] 24-hour notice is an operational baseline for cancellations/reschedules in participant platforms.** User Interviews policy docs repeatedly emphasize advance notice and tie late changes to participant or researcher consequences. This should be represented as a policy layer, not an optional courtesy.  
2. **[2025] No-show handling is first-class workflow logic.** User Interviews documents specific "did not show" handling and replacement/downscope paths, indicating that no-show outcomes should trigger deterministic next actions.  
3. **[2025] Invite operations are now target-aware and cadence-driven.** Scheduled invite features (hourly/daily/weekly) pause when goals are met and resume when attrition reopens slots. This suggests scheduling logic should be coupled to target completion gaps.  
4. **[2025] Minimum scheduling notice is configurable and distinct from policy expectations.** Platform-level cutoffs (for example hours-level booking buffers) can be looser than team policy standards (for example 24-hour cancellation policy).  
5. **[2025] Rescheduling increasingly requires reason logging and status rollback.** Maze's moderated-study reschedule flow requires reason capture and updates participant status. Reason fields should be mandatory for auditability.  
6. **[2025-2026] Participant communication quality is now treated as an operations control.** Guidance emphasizes complete session details, timezone clarity, and direct late-arrival/reschedule channels to reduce no-shows.  
7. **[2024-2026] Traceability expectations are rising in consent-adjacent workflows.** FDA revision guidance and institutional IRB materials reinforce identity linkage, timestamping, and retrievable signed artifacts. Even non-clinical discovery programs benefit from adopting this audit discipline.

**Explicit contradiction:** policy expectations (24h baseline) can conflict with platform technical cutoffs (for example 4h minimum notice setting). The skill should separate these controls and enforce stricter policy by default.

**Sources:**
- https://www.userinterviews.com/support/canceling-participants
- https://www.userinterviews.com/support/cancel-reschedule
- https://www.userinterviews.com/support/replacing-no-shows
- https://www.userinterviews.com/support/scheduled-invites
- https://www.userinterviews.com/support/editing-scheduling-buffer
- https://maze.co/product-updates/en/new-request-to-reschedule-for-moderated-studies-pi1PimFo
- https://www.tremendous.com/blog/reduce-research-participant-no-shows/
- https://www.userinterviews.com/support/managing-private-projects
- https://www.fda.gov/media/166215/download
- https://www.irb.pitt.edu/econsent-guidance

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

The current landscape supports reliable scheduling operations if integrations are built around each vendor's real limits, auth model, and sync behavior.

1. **Calendly (2024-2026 updates + evergreen docs):**  
   - Auth supports OAuth and personal access tokens, with scope-based access.  
   - Core APIs include scheduled event listing, invitee listing, scheduling links, and cancellation endpoints.  
   - Known constraints: no dedicated reschedule endpoint, group-event cancellation caveats, and single-use link expiry behavior.  
   - API change feed indicates notable updates in 2024 and 2025/2026 (including scheduling API and scope changes), so integration assumptions should be version-checked periodically.
2. **Google Calendar API (evergreen docs + 2024-2026 release notes):**  
   - Booking and reconciliation anchor on `events.insert`/`events.list`; push sync is `events.watch`; channel cleanup is `channels.stop`; availability precheck is `freeBusy.query`.  
   - `syncToken` incremental sync is the correct large-scale pattern; `410 Gone` requires full resync.  
   - Quota and errors are explicit (`403 usageLimits`, `429`) and require exponential backoff.  
3. **Qualtrics v3 APIs (evergreen + current admin docs):**  
   - API base is datacenter-specific with token auth (`X-API-TOKEN`), strict parameter casing, and brand-level API policy controls.  
   - Mailing lists, contacts, and distributions are the main panel/distribution primitives for this skill domain.  
   - Admin-level rate and policy settings can vary by organization, so production behavior cannot assume uniform tenant limits.
4. **User Interviews Hub and Recruit APIs (current docs):**  
   - Clear participant lifecycle APIs (`GET/POST/PATCH/DELETE /api/participants`) and batch upsert support.  
   - Recruit/project operations include create/launch/pause/unpause/close flows, participant status updates, and session actions.  
   - Published rate limit: 60 requests per minute with `Retry-After` guidance on `429`.
5. **Cross-tool integration pattern (recommended):**  
   - Use one system as source of truth for participant identity state, one for calendar state, and one for outbound distribution; do not infer participant state only from calendar invites.  
   - Persist provider record identifiers and sync tokens per system to avoid duplicate session creation and stale-state race conditions.

**Concrete options mapped for this skill:** Calendly, Google Calendar API, Qualtrics directories/distributions, User Interviews Hub API, User Interviews Recruit API.

**Sources:**
- https://developer.calendly.com/authentication
- https://developer.calendly.com/personal-access-tokens
- https://developer.calendly.com/scopes
- https://developer.calendly.com/frequently-asked-questions
- https://developer.calendly.com/rss.xml
- https://developers.google.com/calendar/api/guides/quota
- https://developers.google.com/calendar/api/guides/errors
- https://developers.google.com/workspace/calendar/api/v3/reference/events/list
- https://developers.google.com/workspace/calendar/api/v3/reference/events/insert
- https://developers.google.com/workspace/calendar/api/v3/reference/events/watch
- https://developers.google.com/workspace/calendar/api/v3/reference/channels/stop
- https://developers.google.com/workspace/calendar/api/v3/reference/freebusy/query
- https://developers.google.com/calendar/docs/release-notes
- https://www.qualtrics.com/support/integrations/api-integration/overview/
- https://www.qualtrics.com/support/integrations/api-integration/common-api-questions-by-product/
- https://www.qualtrics.com/support/survey-platform/sp-administration/organization-settings/
- https://api-docs.userinterviews.com/reference/introduction
- https://api-docs.userinterviews.com/reference/authentication
- https://api-docs.userinterviews.com/reference/rate_limiting
- https://api-docs.userinterviews.com/reference/errors
- https://api-docs.userinterviews.com/reference/get_api-participants-2
- https://api-docs.userinterviews.com/reference/post_api-participants-2
- https://api-docs.userinterviews.com/reference/patch_api-participants-batches-2
- https://api-docs.userinterviews.com/reference/get_api-recruits-1
- https://api-docs.userinterviews.com/reference/post_api-recruits

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

Scheduling operations quality should be interpreted with stage-specific metrics rather than one aggregate completion number. Benchmarks exist, but evidence strength varies between standards bodies, large platform data, and small operational studies.

1. **Define rate metrics precisely and separately.** CHERRIES and AAPOR guidance (evergreen standards) distinguish participation/completion and discourage mixing response terms. In this skill, completion, no-show, cancellation, and over-recruitment must be independently reported.  
2. **No-show for moderated research commonly lands in single-digit to low double-digit ranges.** Recent analysis of moderated studies suggests planning around ~10% as a conservative baseline is practical.  
3. **Over-recruitment is structurally necessary, not exceptional.** Recent operational analysis indicates many studies require replacement buffer; defaulting near 20% is often safer than assuming perfect attendance.  
4. **Incentive design shifts schedule resilience.** Recent platform data suggests incentive levels correlate with recruitment yield and can influence no-show risk, especially across B2B/B2C and in-person vs remote contexts.  
5. **Reminder systems are a high-leverage intervention.** Stronger evidence (including RCT/meta-analysis; older but still relevant) shows reminders reduce no-shows; multiple reminders can outperform single-touch strategies.  
6. **Lead time is a risk multiplier.** Longer booking-to-session windows generally require stronger confirmation protocols; if long lead time rises with no-show/cancellation, operations should adjust reminder cadence and reconfirmation checkpoints.  
7. **Panel health is not captured by completion alone.** Retention and cumulative response dynamics matter; reporting only completion can hide panel depletion and invitation-burden effects.

**Signal vs noise interpretation rules:**  
- Trigger action if rolling 4-week no-show >10% or rises by >=2 percentage points vs baseline.  
- Trigger action if cancellation/reschedule rates remain elevated and coverage forecast drops below 90% of target near close window.  
- Monitor-only when short-term changes stay inside historical variance and target forecast remains on track.

**Sources:**
- https://www.jmir.org/2012/1/e8/ (evergreen/older benchmark)
- https://aapor.org/response-rates/ (evergreen standard)
- https://aapor.org/standards-and-ethics/standard-definitions/ (evergreen standard)
- https://measuringu.com/typical-no-show-rate-for-moderated-studies/
- https://measuringu.com/how-much-should-you-over-recruit/
- https://www.userinterviews.com/blog/research-incentives-report
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9126539/ (older benchmark, still relevant)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC5093388/ (older benchmark, still relevant)
- https://publichealthscotland.scot/publications/cancelled-planned-operations/cancelled-planned-operations-month-ending-31-may-2025/
- https://www.pewresearch.org/short-reads/2024/06/26/q-and-a-what-is-the-american-trends-panel-and-how-has-it-changed/
- https://ssrs.com/insights/when-does-survey-burden-become-too-high-or-too-low-in-probability-panels/

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

Frequent scheduling failures are implementation and governance problems, not only participant behavior.

1. **Timezone ambiguity anti-pattern:** storing "3pm EST" or local-only timestamps causes missed sessions; canonical timezone IDs plus UTC should be mandatory.  
2. **TZ database drift anti-pattern:** stale timezone data can shift future events after DST/legal changes; recurring events need revalidation after tzdata updates.  
3. **"Availability check = booking lock" anti-pattern:** free/busy snapshots are not atomic reservations; race conditions create double-booking unless commit-time conflict checks are enforced.  
4. **Reminder-without-response anti-pattern:** reminders that do not capture confirm/cancel/reschedule signals create operational blindness and false confidence.  
5. **Slow-latency anti-pattern:** delayed first-contact scheduling drives dropout and damages participant experience.  
6. **Sensitive data in invites anti-pattern:** putting protected details in calendar metadata spreads unnecessary PII and increases compliance risk.  
7. **Missing consent/provenance fields anti-pattern:** scheduling actions without lawful-basis/privacy-notice linkage make audit defense weak.  
8. **Interviewer load imbalance anti-pattern:** unmanaged back-to-back schedules reduce interview quality and increase interviewer-side reschedules.  
9. **Sequence bias blind spot:** interview order effects can distort evaluations when scheduling creates clustered similar candidates.

**Bad output signature:** sparse records with no `participant_id`, no timezone ID, no actor, no reason code, and no traceability to consent or study state.  
**Good output signature:** immutable event log with actor, timestamps (UTC + zone), reason codes, reminder outcomes, and compliance envelope fields.

**Sources:**
- https://data.iana.org/time-zones/tzdb/NEWS
- https://www.rfc-editor.org/rfc/rfc5545 (evergreen standard)
- https://developers.google.com/calendar/api/concepts/events-calendars
- https://developers.google.com/workspace/calendar/api/v3/reference/freebusy/query
- https://developers.google.com/calendar/api/concepts/reminders
- https://www.cronofy.com/reports/candidate-expectations-report-2024
- https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/recruitment-and-selection/data-protection-and-recruitment/
- https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/data-minimisation/
- https://www.microsoft.com/en-us/worklab/work-trend-index/breaking-down-infinite-workday
- https://cepr.org/voxeu/columns/sequential-contrast-effects-hiring-and-admission-interviews

---

### Angle 5+: Compliance, Traceability, and Retention Controls
> Domain-specific angle: What governance controls are necessary so scheduling artifacts remain auditable and policy-safe across participant lifecycle operations?

**Findings:**

1. **[2024-2026 + evergreen legal principles] Traceability requires more than IDs.** Auditable workflows need versioned privacy notice references, consent linkage, actor attribution, and immutable event history.  
2. **Retention controls must be explicit in scheduling artifacts.** Storage limitation and recordkeeping guidance imply event-level retention class and expiry timestamps should be attached to artifacts rather than implied by environment defaults.  
3. **Role-based redaction is required for operational sharing.** Logs and exports can remain auditable while masking sensitive participant attributes for non-privileged roles.  
4. **Legal-hold exceptions need structured paths.** Auto-purge without hold controls is risky; indefinite retention without hold discipline is also risky.  
5. **Cross-system reconciliation must preserve provenance.** When calendar, participant system, and distribution system disagree, operators need system-of-origin fields and last-sync metadata to resolve conflicts safely.

**Sources:**
- https://www.fda.gov/media/166215/download
- https://www.irb.pitt.edu/econsent-guidance
- https://docs.openclinica.com/oc4/using-openclinica-as-a-data-manager/audit-log
- https://swissethics.ch/assets/studieninformationen/240825_guidance_e_consent_v2.1_web.pdf
- https://www.ecfr.gov/current/title-29/subtitle-B/chapter-XIV/part-1602/section-1602.14
- https://www.eeoc.gov/employers/recordkeeping-requirements
- https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/storage-limitation/

---

## Synthesis

The strongest cross-source pattern is that modern scheduling operations are policy-and-state systems, not calendar-only workflows. The practical unit of work is an auditable session lifecycle keyed by participant and study identity, where each transition (`scheduled`, `rescheduled`, `no_show`, `completed`) is logged with actor, reason, and timestamps. This pattern appears across participant platforms, API docs, and governance guidance.

A second pattern is the separation between technical capability and policy intent. Sources show that platforms can allow relatively short timing windows (hours-level), while research operations policy often expects materially longer notice (for example 24-hour cancellation norms). The skill should explicitly model both controls rather than assuming platform defaults are acceptable policy.

For data interpretation, evidence supports simple operational thresholds that drive action early: no-show around or above 10%, rising cancellation/reschedule rates, and shrinking coverage forecast near close windows. At the same time, benchmark transferability varies by context. Healthcare cancellation data and older reminder literature are useful directional anchors, but the skill should label evidence strength and avoid pretending that all numbers are universal UX standards.

Failure analysis consistently points to implementation quality: timezone handling, idempotent booking logic, reminder observability, and retention/governance fields. These are tractable engineering and process controls. The most actionable improvement for `SKILL.md` is therefore to formalize a state machine plus required schema fields so the system can prevent common errors by design rather than relying on operator memory.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.

- [x] Add a policy layer that separates `policy_notice_hours` from `platform_cutoff_hours`, with default policy at 24 hours and explicit exception workflow for `<24h` changes.
- [x] Add a required lifecycle state model (`invited`, `scheduled`, `reschedule_requested`, `completed`, `no_show`, `cancelled`) with immutable transition log requirements.
- [x] Expand methodology with a deterministic no-show branch: mark no-show, run one controlled reschedule attempt, then replacement/downscope decision within SLA.
- [x] Expand reminder instructions to require multi-touch cadence and capture of participant actions (`confirmed`, `cancelled`, `reschedule_requested`) as telemetry.
- [x] Strengthen tool section with real vendor capability/limit notes (Google sync token + `410` reset, User Interviews `429` + `Retry-After`, Calendly reschedule caveat).
- [x] Add interpretation guidance section with metric definitions/formulas and action thresholds (no-show, cancellation, lead-time risk, coverage forecast).
- [x] Add anti-pattern warning blocks with detection signals and concrete mitigations (timezone ambiguity, double-booking race, over-messaging, missing consent provenance).
- [x] Expand artifact schema with traceability, compliance envelope, reminder telemetry, and retention fields; enforce `additionalProperties: false` on new objects.
- [x] Add cross-system reconciliation rules and required provenance fields (`source_system`, `source_record_id`, `last_synced_at`) for conflict resolution.

---

## Draft Content for SKILL.md

> This section is intentionally long and paste-ready. It is written as direct instruction text for future SKILL.md editing.

### Draft: Scheduling Policy Layer and Decision Rules

Add a dedicated scheduling policy section that sits above tool-specific defaults. You must not treat provider defaults as policy. Define and enforce these controls for every study:

- `policy_notice_hours` (default `24`)
- `platform_cutoff_hours` (tool-specific, discovered at runtime/config)
- `late_change_exception_required` (default `true`)
- `max_reschedule_attempts_per_participant` (default `1` unless study override)

Before accepting any reschedule or cancellation request, you must evaluate policy and platform windows separately:

1. Compute `hours_to_session` from canonical UTC timestamps.
2. If `hours_to_session < platform_cutoff_hours`: reject technical operation and log `decision_code=platform_cutoff`.
3. Else if `hours_to_session < policy_notice_hours`: allow only via exception path with required `exception_reason` and approver attribution.
4. Else proceed with normal flow.

Do not silently downgrade policy to match platform permissiveness. If policy and platform conflict, policy remains authoritative for operational scoring and audit flags.

### Draft: Lifecycle State Machine and Immutable Transition Log

Add a state model section and require every session record to move through explicit transitions:

- `invited`
- `scheduled`
- `reschedule_requested`
- `rescheduled`
- `completed`
- `no_show`
- `cancelled`

You must write transition events as append-only records. Never overwrite prior status as if it never happened. Every transition event must include:

- `from_status`
- `to_status`
- `event_at_utc`
- `actor_type` (`system`, `researcher`, `participant`)
- `actor_id`
- `reason_code`
- `source_system`
- `source_record_id`

If a transition is invalid (for example `completed -> scheduled`), reject it and log validation failure with the offending actor and payload fingerprint.

### Draft: End-to-End Scheduling Workflow

Use this workflow text in methodology:

1. **Prepare schedule-ready roster.**  
   Before outreach, verify each participant has `participant_id`, `study_id`, eligibility status, contact channel, timezone, and consent/provenance fields required by your policy. If any required field is missing, block scheduling for that participant and raise a data-quality exception instead of proceeding with partial records.

2. **Create controlled availability.**  
   Generate booking availability from approved interviewer calendars. Apply minimum notice and buffer constraints before sharing links. Availability should represent true bookable capacity after interviewer workload caps and required break windows.

3. **Issue scheduling outreach with minimized content.**  
   Send only logistics-required details in calendar-facing surfaces. Keep sensitive notes and protected attributes out of invite summaries/descriptions. Include one-click options for confirm/cancel/reschedule so participant intent is observable.

4. **Run confirmation cadence.**  
   Use a multi-touch reminder schedule (for example T-72h, T-24h, T-2h) that records delivery status and participant action. If no response by the final reminder window, flag session as `at_risk` and queue backup outreach.

5. **Handle no-show deterministically.**  
   Mark `no_show` immediately after grace window, then execute one controlled reschedule offer. If unresolved within 48h, mark participant as lost for this session and trigger replacement/downscope branch according to study coverage status.

6. **Close session with traceability and reconciliation.**  
   After completion/cancellation/no-show, reconcile across scheduling tool, calendar system, and participant system. Persist provenance fields and final session outcome without deleting transition history.

### Draft: Tool Usage (Verified Methods, Constraints, and Error Handling)

Add this section under `## Available Tools` (keep only methods actually installed in runtime):

```python
# Calendly: list scheduled events and invitees for attendance reconciliation
calendly(
  op="call",
  args={
    "method_id": "calendly.scheduled_events.list.v1",
    "user": "https://api.calendly.com/users/xxx",
    "count": 50,
    "min_start_time": "2026-01-01T00:00:00Z",
  },
)

calendly(
  op="call",
  args={
    "method_id": "calendly.scheduled_events.invitees.list.v1",
    "uuid": "event_uuid",
    "count": 50,
  },
)

# Google Calendar: controlled event insertion and list/reconciliation
google_calendar(
  op="call",
  args={
    "method_id": "google_calendar.events.insert.v1",
    "calendarId": "primary",
    "summary": "Research Interview",
    "start": {"dateTime": "2026-03-10T15:00:00-05:00"},
    "end": {"dateTime": "2026-03-10T15:45:00-05:00"},
    "attendees": [{"email": "participant@example.com"}],
  },
)

google_calendar(
  op="call",
  args={
    "method_id": "google_calendar.events.list.v1",
    "calendarId": "primary",
    "timeMin": "2026-03-01T00:00:00Z",
    "timeMax": "2026-03-31T23:59:59Z",
  },
)

# Qualtrics: participant pool and survey distribution operations
qualtrics(
  op="call",
  args={
    "method_id": "qualtrics.contacts.create.v1",
    "directoryId": "POOL_xxx",
    "mailingListId": "CG_xxx",
    "firstName": "A",
    "lastName": "B",
    "email": "participant@example.com",
  },
)

qualtrics(
  op="call",
  args={
    "method_id": "qualtrics.distributions.create.v1",
    "surveyId": "SV_xxx",
    "mailingListId": "CG_xxx",
    "fromEmail": "research@example.com",
    "fromName": "Research Team",
    "subject": "Interview Invitation",
  },
)

# User Interviews: create/update participants in project workflow
userinterviews(
  op="call",
  args={
    "method_id": "userinterviews.participants.create.v1",
    "name": "Participant Name",
    "email": "participant@example.com",
    "project_id": "proj_id",
  },
)

userinterviews(
  op="call",
  args={
    "method_id": "userinterviews.participants.update.v1",
    "participant_id": "part_id",
    "status": "scheduled",
  },
)
```

Tool interpretation guidance:

- **Calendly:** do not assume native reschedule semantics as a single endpoint operation; model reschedule as explicit transition(s) and preserve old/new times in your log.
- **Google Calendar:** if sync-based workflows are used, treat token invalidation (`410 Gone`) as a full-resync trigger. Back off on quota errors (`403 usageLimits`) and `429` responses.
- **Qualtrics:** enforce strict parameter casing and datacenter-specific base configuration through environment validation before runtime calls.
- **User Interviews:** enforce request pacing and honor `Retry-After` on `429`; design idempotent upsert behavior for participant synchronization.

### Draft: Signal Interpretation and Operational Thresholds

Add a section called `### Scheduling Signal Quality`:

You must compute and review these metrics at study and segment levels:

- `no_show_rate = confirmed_no_shows / confirmed_scheduled`
- `cancellation_rate = cancelled_sessions / planned_sessions`
- `reschedule_rate = rescheduled_sessions / planned_sessions`
- `coverage_vs_target = completed_sessions / target_count`
- `lead_time_days = session_start_utc - booked_at_utc`
- `over_recruitment_rate = (recruited_count - target_count) / target_count`

Interpretation rules:

1. If rolling 4-week `no_show_rate > 0.10` or increases by at least 0.02 compared with baseline, trigger no-show mitigation playbook (extra reminder touch + replacement buffer increase + incentive review).
2. If `coverage_vs_target < 0.90` near field-close window, open backup recruitment channels and prioritize underfilled quota cells.
3. If share of sessions with `lead_time_days >= 31` rises while no-show also rises, add reconfirmation checkpoints and shorten booking horizon where possible.
4. If cancellation/reschedule rates remain elevated for two consecutive windows, audit reason codes and simplify self-serve reschedule paths.

Evidence labeling rule:

- Mark thresholds from strong standards/trials as `strong`.
- Mark large platform operational benchmarks as `moderate`.
- Mark small pilot/vendor anecdotal evidence as `weak`.

Do not publish a single benchmark number without context band and evidence tier.

### Draft: Anti-Patterns and Warning Blocks

Add these warning blocks under methodology or a dedicated anti-pattern section:

> [!WARNING]
> **Anti-pattern: Timezone ambiguity**
> What it looks like: session records store local-only time or ambiguous zone labels (for example `EST`) without canonical timezone ID.  
> Detection signal: any record missing `start_utc`, `end_utc`, or `tzid`.  
> Consequence: participants and interviewers join at different times, creating preventable no-shows.  
> Mitigation: require canonical IANA timezone + UTC timestamps at write time; reject ambiguous inputs.

> [!WARNING]
> **Anti-pattern: Availability snapshot treated as reservation**
> What it looks like: booking flow checks free/busy then writes event without conflict recheck.  
> Detection signal: overlapping interviewer sessions discovered after write.  
> Consequence: double-booking, forced reschedules, participant churn.  
> Mitigation: use hold-then-commit flow with commit-time conflict recheck and idempotency keys.

> [!WARNING]
> **Anti-pattern: Reminder without participant action telemetry**
> What it looks like: reminders are sent but confirmation/cancellation outcomes are not captured.  
> Detection signal: high reminder send counts with unknown participant state.  
> Consequence: false sense of readiness and late-stage no-show surprises.  
> Mitigation: include one-click action links and persist `candidate_action` + `action_at_utc`.

> [!WARNING]
> **Anti-pattern: Missing compliance provenance**
> What it looks like: scheduling events have no lawful basis, privacy notice version, or consent linkage.  
> Detection signal: records cannot show what participant agreed to at scheduling time.  
> Consequence: weak audit defensibility and inconsistent handling of withdrawal/erasure requests.  
> Mitigation: require compliance envelope fields for every scheduling write and reject incomplete writes.

> [!WARNING]
> **Anti-pattern: Over-messaging participants**
> What it looks like: frequent outreach touches with no cadence guardrails.  
> Detection signal: rising unsubscribe/decline rates while touch count per participant increases.  
> Consequence: panel fatigue and response quality degradation.  
> Mitigation: cap touches per 24h and separate invite cadence from reminder cadence.

### Draft: Reconciliation and Provenance Rules

Add a section called `### Cross-System Reconciliation`:

You must treat reconciliation as part of core scheduling, not optional reporting. On every terminal session outcome (`completed`, `cancelled`, `no_show`), compare records across:

- scheduling provider (for booking metadata)
- calendar provider (for event state and attendees)
- participant platform/panel system (for participant lifecycle status)

For every reconciled item, store:

- `source_system`
- `source_record_id`
- `source_last_modified_at`
- `last_synced_at`
- `reconciliation_status` (`matched`, `mismatch`, `missing_source`, `needs_manual_review`)
- `mismatch_fields` (array)

If mismatch touches participant identity, study linkage, or session time, route to manual review and block automated closure until resolved.

### Draft: Schema additions

```json
{
  "interview_schedule": {
    "type": "object",
    "required": [
      "study_id",
      "sessions",
      "coverage_status",
      "policy",
      "metrics",
      "audit_log"
    ],
    "additionalProperties": false,
    "properties": {
      "study_id": {
        "type": "string",
        "description": "Unique identifier for the study this schedule belongs to."
      },
      "policy": {
        "type": "object",
        "required": [
          "policy_notice_hours",
          "platform_cutoff_hours",
          "max_reschedule_attempts_per_participant",
          "late_change_exception_required"
        ],
        "additionalProperties": false,
        "properties": {
          "policy_notice_hours": {
            "type": "integer",
            "minimum": 1,
            "description": "Minimum hours before session required by team policy for normal cancellation/reschedule handling."
          },
          "platform_cutoff_hours": {
            "type": "integer",
            "minimum": 0,
            "description": "Minimum hours before session enforced by the scheduling platform for technical acceptance."
          },
          "max_reschedule_attempts_per_participant": {
            "type": "integer",
            "minimum": 0,
            "description": "Maximum number of reschedule attempts permitted per participant for this study."
          },
          "late_change_exception_required": {
            "type": "boolean",
            "description": "Whether requests inside policy notice window require explicit documented exception approval."
          }
        }
      },
      "sessions": {
        "type": "array",
        "description": "Session-level records with scheduling, reminder, provenance, and compliance metadata.",
        "items": {
          "type": "object",
          "required": [
            "session_id",
            "participant_id",
            "study_id",
            "status",
            "scheduled_start_utc",
            "scheduled_end_utc",
            "scheduled_tzid",
            "source_system",
            "source_record_id",
            "reminder_plan",
            "compliance_envelope"
          ],
          "additionalProperties": false,
          "properties": {
            "session_id": {
              "type": "string",
              "description": "Unique session identifier used across lifecycle transitions."
            },
            "participant_id": {
              "type": "string",
              "description": "Participant identifier linked to roster and consent records."
            },
            "study_id": {
              "type": "string",
              "description": "Study identifier repeated at session level for denormalized traceability."
            },
            "status": {
              "type": "string",
              "enum": [
                "invited",
                "scheduled",
                "reschedule_requested",
                "rescheduled",
                "completed",
                "no_show",
                "cancelled"
              ],
              "description": "Current lifecycle state of the session."
            },
            "scheduled_start_utc": {
              "type": "string",
              "format": "date-time",
              "description": "Session start timestamp in UTC for canonical calculations."
            },
            "scheduled_end_utc": {
              "type": "string",
              "format": "date-time",
              "description": "Session end timestamp in UTC."
            },
            "scheduled_tzid": {
              "type": "string",
              "description": "Canonical timezone identifier (IANA) used for participant-facing rendering."
            },
            "source_system": {
              "type": "string",
              "enum": [
                "calendly",
                "google_calendar",
                "qualtrics",
                "userinterviews",
                "manual"
              ],
              "description": "System of origin for current session record."
            },
            "source_record_id": {
              "type": "string",
              "description": "Provider-native record identifier for reconciliation."
            },
            "last_synced_at": {
              "type": "string",
              "format": "date-time",
              "description": "Timestamp of last successful reconciliation with source system."
            },
            "reschedule_reason": {
              "type": "string",
              "description": "Human-readable reason for reschedule request when applicable."
            },
            "reminder_plan": {
              "type": "array",
              "description": "Configured reminder checkpoints relative to session start.",
              "minItems": 1,
              "items": {
                "type": "string",
                "enum": ["T-72h", "T-48h", "T-24h", "T-2h"]
              }
            },
            "reminder_events": {
              "type": "array",
              "description": "Observed reminder delivery and participant response telemetry.",
              "items": {
                "type": "object",
                "required": [
                  "reminder_id",
                  "channel",
                  "sent_at_utc",
                  "delivery_status"
                ],
                "additionalProperties": false,
                "properties": {
                  "reminder_id": {
                    "type": "string",
                    "description": "Unique reminder event identifier."
                  },
                  "channel": {
                    "type": "string",
                    "enum": ["email", "sms", "in_app"],
                    "description": "Communication channel used for reminder delivery."
                  },
                  "sent_at_utc": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Reminder send timestamp in UTC."
                  },
                  "delivery_status": {
                    "type": "string",
                    "enum": ["sent", "delivered", "failed", "bounced"],
                    "description": "Delivery outcome from messaging provider."
                  },
                  "participant_action": {
                    "type": "string",
                    "enum": ["none", "confirmed", "cancelled", "reschedule_requested"],
                    "description": "Participant action captured from reminder touchpoint."
                  },
                  "action_at_utc": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Timestamp when participant action was captured."
                  }
                }
              }
            },
            "compliance_envelope": {
              "type": "object",
              "required": [
                "lawful_basis",
                "privacy_notice_version",
                "consent_ref",
                "retention_class"
              ],
              "additionalProperties": false,
              "properties": {
                "lawful_basis": {
                  "type": "string",
                  "description": "Declared legal/organizational basis for processing participant scheduling data."
                },
                "privacy_notice_version": {
                  "type": "string",
                  "description": "Version identifier of participant-facing privacy notice at scheduling time."
                },
                "consent_ref": {
                  "type": "string",
                  "description": "Reference to consent artifact or record linked to this session."
                },
                "retention_class": {
                  "type": "string",
                  "description": "Retention policy class that controls purge/anonymization horizon."
                },
                "expires_at_utc": {
                  "type": "string",
                  "format": "date-time",
                  "description": "Timestamp at which this record is eligible for purge/anonymization absent legal hold."
                },
                "legal_hold": {
                  "type": "boolean",
                  "description": "Whether retention deletion is suspended due to legal or policy hold."
                }
              }
            }
          }
        }
      },
      "coverage_status": {
        "type": "object",
        "required": ["scheduled_count", "completed_count", "target_count"],
        "additionalProperties": false,
        "properties": {
          "scheduled_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Current number of scheduled sessions."
          },
          "completed_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Current number of completed sessions."
          },
          "target_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Target number of completed sessions for the study."
          }
        }
      },
      "metrics": {
        "type": "object",
        "required": [
          "no_show_rate",
          "cancellation_rate",
          "reschedule_rate",
          "coverage_vs_target",
          "over_recruitment_rate"
        ],
        "additionalProperties": false,
        "properties": {
          "no_show_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Confirmed no-shows divided by confirmed scheduled sessions."
          },
          "cancellation_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Cancelled sessions divided by planned sessions."
          },
          "reschedule_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Rescheduled sessions divided by planned sessions."
          },
          "coverage_vs_target": {
            "type": "number",
            "minimum": 0,
            "description": "Completed sessions divided by target count."
          },
          "over_recruitment_rate": {
            "type": "number",
            "description": "Recruited minus target, divided by target; can be negative when under-recruited."
          }
        }
      },
      "audit_log": {
        "type": "array",
        "description": "Append-only transition and decision events for scheduling operations.",
        "items": {
          "type": "object",
          "required": [
            "event_id",
            "session_id",
            "from_status",
            "to_status",
            "event_at_utc",
            "actor_type",
            "actor_id",
            "reason_code"
          ],
          "additionalProperties": false,
          "properties": {
            "event_id": {
              "type": "string",
              "description": "Unique audit event identifier."
            },
            "session_id": {
              "type": "string",
              "description": "Session affected by this transition."
            },
            "from_status": {
              "type": "string",
              "description": "Previous status before transition."
            },
            "to_status": {
              "type": "string",
              "description": "New status after transition."
            },
            "event_at_utc": {
              "type": "string",
              "format": "date-time",
              "description": "Timestamp when transition was recorded."
            },
            "actor_type": {
              "type": "string",
              "enum": ["system", "researcher", "participant"],
              "description": "Type of actor that triggered transition."
            },
            "actor_id": {
              "type": "string",
              "description": "Identifier of actor responsible for transition."
            },
            "reason_code": {
              "type": "string",
              "description": "Normalized reason for transition (for example no_show, participant_conflict, researcher_conflict)."
            },
            "details": {
              "type": "string",
              "description": "Optional human-readable context for manual review and audits."
            }
          }
        }
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Published, universally accepted benchmark thresholds specific to UX interview scheduling are limited; many numeric ranges come from platform/operator datasets and should be treated as moderate evidence.
- Some vendor documentation pages are evergreen and not clearly date-stamped, so they are used as current capability references rather than strict 2024-2026 change logs.
- Qualtrics tenant-specific API throttling and policy controls vary by brand admin configuration; runtime behavior may differ across deployments.
- No single cross-vendor canonical definition for "reschedule rate" exists; this should be standardized internally in the skill schema and reporting logic.
# Research: discovery-scheduling

**Skill path:** `flexus_simple_bots/researcher/skills/discovery-scheduling/`
**Bot:** researcher
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`discovery-scheduling` handles interview logistics and participant panel management between recruitment and interview capture. In practice this means converting qualified participants into attended sessions while preserving an auditable chain from `participant_id` to `study_id`, consent state, and session outcome. This skill is used whenever a research team must coordinate one-on-one interviews or panel-based sessions across tools such as Calendly, Google Calendar, Qualtrics, and User Interviews.

The core operational problem is not "booking a calendar slot"; it is managing scheduling risk. The most common delivery failures are no-shows, late cancellations, timezone mistakes, over-messaging, and missing traceability fields that break downstream analytics and compliance evidence. Recent 2024-2026 practitioner updates show a shift toward explicit policy windows (for example 24-hour cancellation expectations), stateful no-show replacement flows, and automation tied to target gaps instead of one-time invite blasts.

---

## Definition of Done

Research is complete when ALL of the following are satisfied:

- [x] At least 4 distinct research angles are covered (see Research Angles section)
- [x] Each finding has a source URL or named reference
- [x] Methodology section covers practical how-to, not just theory
- [x] Tool/API landscape is mapped with at least 3-5 concrete options
- [x] At least one "what not to do" / common failure mode is documented
- [x] Output schema recommendations are grounded in real-world data shapes
- [x] Gaps section honestly lists what was NOT found or is uncertain
- [x] All findings are from 2024–2026 unless explicitly marked as evergreen

---

## Quality Gates

Before marking status `complete`, verify:

- No generic filler without concrete backing; all claims below are linked to named sources
- No invented tool names or API endpoints; all endpoint claims map to vendor docs
- Contradictions between sources are called out explicitly (policy windows vs platform cutoffs; automation cadence vs over-messaging risk)
- Findings volume is within target range and synthesized into actionable draft content

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

Practitioner guidance in 2024-2026 converges on a scheduling playbook with explicit policy windows, state transitions, and target-aware invite automation rather than ad-hoc manual coordination.

1. **[2024-2025] 24-hour notice is an operational baseline for cancellations/reschedules in participant platforms.** User Interviews policy docs repeatedly emphasize advance notice and tie late changes to participant or researcher consequences. This should be represented as a policy layer, not an optional courtesy.  
2. **[2025] No-show handling is first-class workflow logic.** User Interviews documents specific "did not show" handling and replacement/downscope paths, indicating that no-show outcomes should trigger deterministic next actions.  
3. **[2025] Invite operations are now target-aware and cadence-driven.** Scheduled invite features (hourly/daily/weekly) pause when goals are met and resume when attrition reopens slots. This suggests scheduling logic should be coupled to target completion gaps.  
4. **[2025] Minimum scheduling notice is configurable and distinct from policy expectations.** Platform-level cutoffs (for example hours-level booking buffers) can be looser than team policy standards (for example 24-hour cancellation policy).  
5. **[2025] Rescheduling increasingly requires reason logging and status rollback.** Maze's moderated-study reschedule flow requires reason capture and updates participant status. Reason fields should be mandatory for auditability.  
6. **[2025-2026] Participant communication quality is now treated as an operations control.** Guidance emphasizes complete session details, timezone clarity, and direct late-arrival/reschedule channels to reduce no-shows.  
7. **[2024-2026] Traceability expectations are rising in consent-adjacent workflows.** FDA revision guidance and institutional IRB materials reinforce identity linkage, timestamping, and retrievable signed artifacts. Even non-clinical discovery programs benefit from adopting this audit discipline.

**Explicit contradiction:** policy expectations (24h baseline) can conflict with platform technical cutoffs (for example 4h minimum notice setting). The skill should separate these controls and enforce stricter policy by default.

**Sources:**
- https://www.userinterviews.com/support/canceling-participants
- https://www.userinterviews.com/support/cancel-reschedule
- https://www.userinterviews.com/support/replacing-no-shows
- https://www.userinterviews.com/support/scheduled-invites
- https://www.userinterviews.com/support/editing-scheduling-buffer
- https://maze.co/product-updates/en/new-request-to-reschedule-for-moderated-studies-pi1PimFo
- https://www.tremendous.com/blog/reduce-research-participant-no-shows/
- https://www.userinterviews.com/support/managing-private-projects
- https://www.fda.gov/media/166215/download
- https://www.irb.pitt.edu/econsent-guidance

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

The current landscape supports reliable scheduling operations if integrations are built around each vendor's real limits, auth model, and sync behavior.

1. **Calendly (2024-2026 updates + evergreen docs):**  
   - Auth supports OAuth and personal access tokens, with scope-based access.  
   - Core APIs include scheduled event listing, invitee listing, scheduling links, and cancellation endpoints.  
   - Known constraints: no dedicated reschedule endpoint, group-event cancellation caveats, and single-use link expiry behavior.  
   - API change feed indicates notable updates in 2024 and 2025/2026 (including scheduling API and scope changes), so integration assumptions should be version-checked periodically.
2. **Google Calendar API (evergreen docs + 2024-2026 release notes):**  
   - Booking and reconciliation anchor on `events.insert`/`events.list`; push sync is `events.watch`; channel cleanup is `channels.stop`; availability precheck is `freeBusy.query`.  
   - `syncToken` incremental sync is the correct large-scale pattern; `410 Gone` requires full resync.  
   - Quota and errors are explicit (`403 usageLimits`, `429`) and require exponential backoff.  
3. **Qualtrics v3 APIs (evergreen + current admin docs):**  
   - API base is datacenter-specific with token auth (`X-API-TOKEN`), strict parameter casing, and brand-level API policy controls.  
   - Mailing lists, contacts, and distributions are the main panel/distribution primitives for this skill domain.  
   - Admin-level rate and policy settings can vary by organization, so production behavior cannot assume uniform tenant limits.
4. **User Interviews Hub and Recruit APIs (current docs):**  
   - Clear participant lifecycle APIs (`GET/POST/PATCH/DELETE /api/participants`) and batch upsert support.  
   - Recruit/project operations include create/launch/pause/unpause/close flows, participant status updates, and session actions.  
   - Published rate limit: 60 requests per minute with `Retry-After` guidance on `429`.
5. **Cross-tool integration pattern (recommended):**  
   - Use one system as source of truth for participant identity state, one for calendar state, and one for outbound distribution; do not infer participant state only from calendar invites.  
   - Persist provider record identifiers and sync tokens per system to avoid duplicate session creation and stale-state race conditions.

**Concrete options mapped for this skill:** Calendly, Google Calendar API, Qualtrics directories/distributions, User Interviews Hub API, User Interviews Recruit API.

**Sources:**
- https://developer.calendly.com/authentication
- https://developer.calendly.com/personal-access-tokens
- https://developer.calendly.com/scopes
- https://developer.calendly.com/frequently-asked-questions
- https://developer.calendly.com/rss.xml
- https://developers.google.com/calendar/api/guides/quota
- https://developers.google.com/calendar/api/guides/errors
- https://developers.google.com/workspace/calendar/api/v3/reference/events/list
- https://developers.google.com/workspace/calendar/api/v3/reference/events/insert
- https://developers.google.com/workspace/calendar/api/v3/reference/events/watch
- https://developers.google.com/workspace/calendar/api/v3/reference/channels/stop
- https://developers.google.com/workspace/calendar/api/v3/reference/freebusy/query
- https://developers.google.com/calendar/docs/release-notes
- https://www.qualtrics.com/support/integrations/api-integration/overview/
- https://www.qualtrics.com/support/integrations/api-integration/common-api-questions-by-product/
- https://www.qualtrics.com/support/survey-platform/sp-administration/organization-settings/
- https://api-docs.userinterviews.com/reference/introduction
- https://api-docs.userinterviews.com/reference/authentication
- https://api-docs.userinterviews.com/reference/rate_limiting
- https://api-docs.userinterviews.com/reference/errors
- https://api-docs.userinterviews.com/reference/get_api-participants-2
- https://api-docs.userinterviews.com/reference/post_api-participants-2
- https://api-docs.userinterviews.com/reference/patch_api-participants-batches-2
- https://api-docs.userinterviews.com/reference/get_api-recruits-1
- https://api-docs.userinterviews.com/reference/post_api-recruits

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

Scheduling operations quality should be interpreted with stage-specific metrics rather than one aggregate completion number. Benchmarks exist, but evidence strength varies between standards bodies, large platform data, and small operational studies.

1. **Define rate metrics precisely and separately.** CHERRIES and AAPOR guidance (evergreen standards) distinguish participation/completion and discourage mixing response terms. In this skill, completion, no-show, cancellation, and over-recruitment must be independently reported.  
2. **No-show for moderated research commonly lands in single-digit to low double-digit ranges.** Recent analysis of moderated studies suggests planning around ~10% as a conservative baseline is practical.  
3. **Over-recruitment is structurally necessary, not exceptional.** Recent operational analysis indicates many studies require replacement buffer; defaulting near 20% is often safer than assuming perfect attendance.  
4. **Incentive design shifts schedule resilience.** Recent platform data suggests incentive levels correlate with recruitment yield and can influence no-show risk, especially across B2B/B2C and in-person vs remote contexts.  
5. **Reminder systems are a high-leverage intervention.** Stronger evidence (including RCT/meta-analysis; older but still relevant) shows reminders reduce no-shows; multiple reminders can outperform single-touch strategies.  
6. **Lead time is a risk multiplier.** Longer booking-to-session windows generally require stronger confirmation protocols; if long lead time rises with no-show/cancellation, operations should adjust reminder cadence and reconfirmation checkpoints.  
7. **Panel health is not captured by completion alone.** Retention and cumulative response dynamics matter; reporting only completion can hide panel depletion and invitation-burden effects.

**Signal vs noise interpretation rules:**  
- Trigger action if rolling 4-week no-show >10% or rises by >=2 percentage points vs baseline.  
- Trigger action if cancellation/reschedule rates remain elevated and coverage forecast drops below 90% of target near close window.  
- Monitor-only when short-term changes stay inside historical variance and target forecast remains on track.

**Sources:**
- https://www.jmir.org/2012/1/e8/ (evergreen/older benchmark)
- https://aapor.org/response-rates/ (evergreen standard)
- https://aapor.org/standards-and-ethics/standard-definitions/ (evergreen standard)
- https://measuringu.com/typical-no-show-rate-for-moderated-studies/
- https://measuringu.com/how-much-should-you-over-recruit/
- https://www.userinterviews.com/blog/research-incentives-report
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9126539/ (older benchmark, still relevant)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC5093388/ (older benchmark, still relevant)
- https://publichealthscotland.scot/publications/cancelled-planned-operations/cancelled-planned-operations-month-ending-31-may-2025/
- https://www.pewresearch.org/short-reads/2024/06/26/q-and-a-what-is-the-american-trends-panel-and-how-has-it-changed/
- https://ssrs.com/insights/when-does-survey-burden-become-too-high-or-too-low-in-probability-panels/

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

Frequent scheduling failures are implementation and governance problems, not only participant behavior.

1. **Timezone ambiguity anti-pattern:** storing "3pm EST" or local-only timestamps causes missed sessions; canonical timezone IDs plus UTC should be mandatory.  
2. **TZ database drift anti-pattern:** stale timezone data can shift future events after DST/legal changes; recurring events need revalidation after tzdata updates.  
3. **"Availability check = booking lock" anti-pattern:** free/busy snapshots are not atomic reservations; race conditions create double-booking unless commit-time conflict checks are enforced.  
4. **Reminder-without-response anti-pattern:** reminders that do not capture confirm/cancel/reschedule signals create operational blindness and false confidence.  
5. **Slow-latency anti-pattern:** delayed first-contact scheduling drives dropout and damages participant experience.  
6. **Sensitive data in invites anti-pattern:** putting protected details in calendar metadata spreads unnecessary PII and increases compliance risk.  
7. **Missing consent/provenance fields anti-pattern:** scheduling actions without lawful-basis/privacy-notice linkage make audit defense weak.  
8. **Interviewer load imbalance anti-pattern:** unmanaged back-to-back schedules reduce interview quality and increase interviewer-side reschedules.  
9. **Sequence bias blind spot:** interview order effects can distort evaluations when scheduling creates clustered similar candidates.

**Bad output signature:** sparse records with no `participant_id`, no timezone ID, no actor, no reason code, and no traceability to consent or study state.  
**Good output signature:** immutable event log with actor, timestamps (UTC + zone), reason codes, reminder outcomes, and compliance envelope fields.

**Sources:**
- https://data.iana.org/time-zones/tzdb/NEWS
- https://www.rfc-editor.org/rfc/rfc5545 (evergreen standard)
- https://developers.google.com/calendar/api/concepts/events-calendars
- https://developers.google.com/workspace/calendar/api/v3/reference/freebusy/query
- https://developers.google.com/calendar/api/concepts/reminders
- https://www.cronofy.com/reports/candidate-expectations-report-2024
- https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/recruitment-and-selection/data-protection-and-recruitment/
- https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/data-minimisation/
- https://www.microsoft.com/en-us/worklab/work-trend-index/breaking-down-infinite-workday
- https://cepr.org/voxeu/columns/sequential-contrast-effects-hiring-and-admission-interviews

---

### Angle 5+: Compliance, Traceability, and Retention Controls
> Domain-specific angle: What governance controls are necessary so scheduling artifacts remain auditable and policy-safe across participant lifecycle operations?

**Findings:**

1. **[2024-2026 + evergreen legal principles] Traceability requires more than IDs.** Auditable workflows need versioned privacy notice references, consent linkage, actor attribution, and immutable event history.  
2. **Retention controls must be explicit in scheduling artifacts.** Storage limitation and recordkeeping guidance imply event-level retention class and expiry timestamps should be attached to artifacts rather than implied by environment defaults.  
3. **Role-based redaction is required for operational sharing.** Logs and exports can remain auditable while masking sensitive participant attributes for non-privileged roles.  
4. **Legal-hold exceptions need structured paths.** Auto-purge without hold controls is risky; indefinite retention without hold discipline is also risky.  
5. **Cross-system reconciliation must preserve provenance.** When calendar, participant system, and distribution system disagree, operators need system-of-origin fields and last-sync metadata to resolve conflicts safely.

**Sources:**
- https://www.fda.gov/media/166215/download
- https://www.irb.pitt.edu/econsent-guidance
- https://docs.openclinica.com/oc4/using-openclinica-as-a-data-manager/audit-log
- https://swissethics.ch/assets/studieninformationen/240825_guidance_e_consent_v2.1_web.pdf
- https://www.ecfr.gov/current/title-29/subtitle-B/chapter-XIV/part-1602/section-1602.14
- https://www.eeoc.gov/employers/recordkeeping-requirements
- https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/storage-limitation/

---

## Synthesis

The strongest cross-source pattern is that modern scheduling operations are policy-and-state systems, not calendar-only workflows. The practical unit of work is an auditable session lifecycle keyed by participant and study identity, where each transition (`scheduled`, `rescheduled`, `no_show`, `completed`) is logged with actor, reason, and timestamps. This pattern appears across participant platforms, API docs, and governance guidance.

A second pattern is the separation between technical capability and policy intent. Sources show that platforms can allow relatively short timing windows (hours-level), while research operations policy often expects materially longer notice (for example 24-hour cancellation norms). The skill should explicitly model both controls rather than assuming platform defaults are acceptable policy.

For data interpretation, evidence supports simple operational thresholds that drive action early: no-show around or above 10%, rising cancellation/reschedule rates, and shrinking coverage forecast near close windows. At the same time, benchmark transferability varies by context. Healthcare cancellation data and older reminder literature are useful directional anchors, but the skill should label evidence strength and avoid pretending that all numbers are universal UX standards.

Failure analysis consistently points to implementation quality: timezone handling, idempotent booking logic, reminder observability, and retention/governance fields. These are tractable engineering and process controls. The most actionable improvement for `SKILL.md` is therefore to formalize a state machine plus required schema fields so the system can prevent common errors by design rather than relying on operator memory.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.

- [x] Add a policy layer that separates `policy_notice_hours` from `platform_cutoff_hours`, with default policy at 24 hours and explicit exception workflow for `<24h` changes.
- [x] Add a required lifecycle state model (`invited`, `scheduled`, `reschedule_requested`, `completed`, `no_show`, `cancelled`) with immutable transition log requirements.
- [x] Expand methodology with a deterministic no-show branch: mark no-show, run one controlled reschedule attempt, then replacement/downscope decision within SLA.
- [x] Expand reminder instructions to require multi-touch cadence and capture of participant actions (`confirmed`, `cancelled`, `reschedule_requested`) as telemetry.
- [x] Strengthen tool section with real vendor capability/limit notes (Google sync token + `410` reset, User Interviews `429` + `Retry-After`, Calendly reschedule caveat).
- [x] Add interpretation guidance section with metric definitions/formulas and action thresholds (no-show, cancellation, lead-time risk, coverage forecast).
- [x] Add anti-pattern warning blocks with detection signals and concrete mitigations (timezone ambiguity, double-booking race, over-messaging, missing consent provenance).
- [x] Expand artifact schema with traceability, compliance envelope, reminder telemetry, and retention fields; enforce `additionalProperties: false` on new objects.
- [x] Add cross-system reconciliation rules and required provenance fields (`source_system`, `source_record_id`, `last_synced_at`) for conflict resolution.

---

## Draft Content for SKILL.md

> This section is intentionally long and paste-ready. It is written as direct instruction text for future SKILL.md editing.

### Draft: Scheduling Policy Layer and Decision Rules

Add a dedicated scheduling policy section that sits above tool-specific defaults. You must not treat provider defaults as policy. Define and enforce these controls for every study:

- `policy_notice_hours` (default `24`)
- `platform_cutoff_hours` (tool-specific, discovered at runtime/config)
- `late_change_exception_required` (default `true`)
- `max_reschedule_attempts_per_participant` (default `1` unless study override)

Before accepting any reschedule or cancellation request, you must evaluate policy and platform windows separately:

1. Compute `hours_to_session` from canonical UTC timestamps.
2. If `hours_to_session < platform_cutoff_hours`: reject technical operation and log `decision_code=platform_cutoff`.
3. Else if `hours_to_session < policy_notice_hours`: allow only via exception path with required `exception_reason` and approver attribution.
4. Else proceed with normal flow.

Do not silently downgrade policy to match platform permissiveness. If policy and platform conflict, policy remains authoritative for operational scoring and audit flags.

### Draft: Lifecycle State Machine and Immutable Transition Log

Add a state model section and require every session record to move through explicit transitions:

- `invited`
- `scheduled`
- `reschedule_requested`
- `rescheduled`
- `completed`
- `no_show`
- `cancelled`

You must write transition events as append-only records. Never overwrite prior status as if it never happened. Every transition event must include:

- `from_status`
- `to_status`
- `event_at_utc`
- `actor_type` (`system`, `researcher`, `participant`)
- `actor_id`
- `reason_code`
- `source_system`
- `source_record_id`

If a transition is invalid (for example `completed -> scheduled`), reject it and log validation failure with the offending actor and payload fingerprint.

### Draft: End-to-End Scheduling Workflow

Use this workflow text in methodology:

1. **Prepare schedule-ready roster.**  
   Before outreach, verify each participant has `participant_id`, `study_id`, eligibility status, contact channel, timezone, and consent/provenance fields required by your policy. If any required field is missing, block scheduling for that participant and raise a data-quality exception instead of proceeding with partial records.

2. **Create controlled availability.**  
   Generate booking availability from approved interviewer calendars. Apply minimum notice and buffer constraints before sharing links. Availability should represent true bookable capacity after interviewer workload caps and required break windows.

3. **Issue scheduling outreach with minimized content.**  
   Send only logistics-required details in calendar-facing surfaces. Keep sensitive notes and protected attributes out of invite summaries/descriptions. Include one-click options for confirm/cancel/reschedule so participant intent is observable.

4. **Run confirmation cadence.**  
   Use a multi-touch reminder schedule (for example T-72h, T-24h, T-2h) that records delivery status and participant action. If no response by the final reminder window, flag session as `at_risk` and queue backup outreach.

5. **Handle no-show deterministically.**  
   Mark `no_show` immediately after grace window, then execute one controlled reschedule offer. If unresolved within 48h, mark participant as lost for this session and trigger replacement/downscope branch according to study coverage status.

6. **Close session with traceability and reconciliation.**  
   After completion/cancellation/no-show, reconcile across scheduling tool, calendar system, and participant system. Persist provenance fields and final session outcome without deleting transition history.

### Draft: Tool Usage (Verified Methods, Constraints, and Error Handling)

Add this section under `## Available Tools` (keep only methods actually installed in runtime):

```python
# Calendly: list scheduled events and invitees for attendance reconciliation
calendly(
  op="call",
  args={
    "method_id": "calendly.scheduled_events.list.v1",
    "user": "https://api.calendly.com/users/xxx",
    "count": 50,
    "min_start_time": "2026-01-01T00:00:00Z",
  },
)

calendly(
  op="call",
  args={
    "method_id": "calendly.scheduled_events.invitees.list.v1",
    "uuid": "event_uuid",
    "count": 50,
  },
)

# Google Calendar: controlled event insertion and list/reconciliation
google_calendar(
  op="call",
  args={
    "method_id": "google_calendar.events.insert.v1",
    "calendarId": "primary",
    "summary": "Research Interview",
    "start": {"dateTime": "2026-03-10T15:00:00-05:00"},
    "end": {"dateTime": "2026-03-10T15:45:00-05:00"},
    "attendees": [{"email": "participant@example.com"}],
  },
)

google_calendar(
  op="call",
  args={
    "method_id": "google_calendar.events.list.v1",
    "calendarId": "primary",
    "timeMin": "2026-03-01T00:00:00Z",
    "timeMax": "2026-03-31T23:59:59Z",
  },
)

# Qualtrics: participant pool and survey distribution operations
qualtrics(
  op="call",
  args={
    "method_id": "qualtrics.contacts.create.v1",
    "directoryId": "POOL_xxx",
    "mailingListId": "CG_xxx",
    "firstName": "A",
    "lastName": "B",
    "email": "participant@example.com",
  },
)

qualtrics(
  op="call",
  args={
    "method_id": "qualtrics.distributions.create.v1",
    "surveyId": "SV_xxx",
    "mailingListId": "CG_xxx",
    "fromEmail": "research@example.com",
    "fromName": "Research Team",
    "subject": "Interview Invitation",
  },
)

# User Interviews: create/update participants in project workflow
userinterviews(
  op="call",
  args={
    "method_id": "userinterviews.participants.create.v1",
    "name": "Participant Name",
    "email": "participant@example.com",
    "project_id": "proj_id",
  },
)

userinterviews(
  op="call",
  args={
    "method_id": "userinterviews.participants.update.v1",
    "participant_id": "part_id",
    "status": "scheduled",
  },
)
```

Tool interpretation guidance:

- **Calendly:** do not assume native reschedule semantics as a single endpoint operation; model reschedule as explicit transition(s) and preserve old/new times in your log.
- **Google Calendar:** if sync-based workflows are used, treat token invalidation (`410 Gone`) as a full-resync trigger. Back off on quota errors (`403 usageLimits`) and `429` responses.
- **Qualtrics:** enforce strict parameter casing and datacenter-specific base configuration through environment validation before runtime calls.
- **User Interviews:** enforce request pacing and honor `Retry-After` on `429`; design idempotent upsert behavior for participant synchronization.

### Draft: Signal Interpretation and Operational Thresholds

Add a section called `### Scheduling Signal Quality`:

You must compute and review these metrics at study and segment levels:

- `no_show_rate = confirmed_no_shows / confirmed_scheduled`
- `cancellation_rate = cancelled_sessions / planned_sessions`
- `reschedule_rate = rescheduled_sessions / planned_sessions`
- `coverage_vs_target = completed_sessions / target_count`
- `lead_time_days = session_start_utc - booked_at_utc`
- `over_recruitment_rate = (recruited_count - target_count) / target_count`

Interpretation rules:

1. If rolling 4-week `no_show_rate > 0.10` or increases by at least 0.02 compared with baseline, trigger no-show mitigation playbook (extra reminder touch + replacement buffer increase + incentive review).
2. If `coverage_vs_target < 0.90` near field-close window, open backup recruitment channels and prioritize underfilled quota cells.
3. If share of sessions with `lead_time_days >= 31` rises while no-show also rises, add reconfirmation checkpoints and shorten booking horizon where possible.
4. If cancellation/reschedule rates remain elevated for two consecutive windows, audit reason codes and simplify self-serve reschedule paths.

Evidence labeling rule:

- Mark thresholds from strong standards/trials as `strong`.
- Mark large platform operational benchmarks as `moderate`.
- Mark small pilot/vendor anecdotal evidence as `weak`.

Do not publish a single benchmark number without context band and evidence tier.

### Draft: Anti-Patterns and Warning Blocks

Add these warning blocks under methodology or a dedicated anti-pattern section:

> [!WARNING]
> **Anti-pattern: Timezone ambiguity**
> What it looks like: session records store local-only time or ambiguous zone labels (for example `EST`) without canonical timezone ID.  
> Detection signal: any record missing `start_utc`, `end_utc`, or `tzid`.  
> Consequence: participants and interviewers join at different times, creating preventable no-shows.  
> Mitigation: require canonical IANA timezone + UTC timestamps at write time; reject ambiguous inputs.

> [!WARNING]
> **Anti-pattern: Availability snapshot treated as reservation**
> What it looks like: booking flow checks free/busy then writes event without conflict recheck.  
> Detection signal: overlapping interviewer sessions discovered after write.  
> Consequence: double-booking, forced reschedules, participant churn.  
> Mitigation: use hold-then-commit flow with commit-time conflict recheck and idempotency keys.

> [!WARNING]
> **Anti-pattern: Reminder without participant action telemetry**
> What it looks like: reminders are sent but confirmation/cancellation outcomes are not captured.  
> Detection signal: high reminder send counts with unknown participant state.  
> Consequence: false sense of readiness and late-stage no-show surprises.  
> Mitigation: include one-click action links and persist `candidate_action` + `action_at_utc`.

> [!WARNING]
> **Anti-pattern: Missing compliance provenance**
> What it looks like: scheduling events have no lawful basis, privacy notice version, or consent linkage.  
> Detection signal: records cannot show what participant agreed to at scheduling time.  
> Consequence: weak audit defensibility and inconsistent handling of withdrawal/erasure requests.  
> Mitigation: require compliance envelope fields for every scheduling write and reject incomplete writes.

> [!WARNING]
> **Anti-pattern: Over-messaging participants**
> What it looks like: frequent outreach touches with no cadence guardrails.  
> Detection signal: rising unsubscribe/decline rates while touch count per participant increases.  
> Consequence: panel fatigue and response quality degradation.  
> Mitigation: cap touches per 24h and separate invite cadence from reminder cadence.

### Draft: Reconciliation and Provenance Rules

Add a section called `### Cross-System Reconciliation`:

You must treat reconciliation as part of core scheduling, not optional reporting. On every terminal session outcome (`completed`, `cancelled`, `no_show`), compare records across:

- scheduling provider (for booking metadata)
- calendar provider (for event state and attendees)
- participant platform/panel system (for participant lifecycle status)

For every reconciled item, store:

- `source_system`
- `source_record_id`
- `source_last_modified_at`
- `last_synced_at`
- `reconciliation_status` (`matched`, `mismatch`, `missing_source`, `needs_manual_review`)
- `mismatch_fields` (array)

If mismatch touches participant identity, study linkage, or session time, route to manual review and block automated closure until resolved.

### Draft: Schema additions

```json
{
  "interview_schedule": {
    "type": "object",
    "required": [
      "study_id",
      "sessions",
      "coverage_status",
      "policy",
      "metrics",
      "audit_log"
    ],
    "additionalProperties": false,
    "properties": {
      "study_id": {
        "type": "string",
        "description": "Unique identifier for the study this schedule belongs to."
      },
      "policy": {
        "type": "object",
        "required": [
          "policy_notice_hours",
          "platform_cutoff_hours",
          "max_reschedule_attempts_per_participant",
          "late_change_exception_required"
        ],
        "additionalProperties": false,
        "properties": {
          "policy_notice_hours": {
            "type": "integer",
            "minimum": 1,
            "description": "Minimum hours before session required by team policy for normal cancellation/reschedule handling."
          },
          "platform_cutoff_hours": {
            "type": "integer",
            "minimum": 0,
            "description": "Minimum hours before session enforced by the scheduling platform for technical acceptance."
          },
          "max_reschedule_attempts_per_participant": {
            "type": "integer",
            "minimum": 0,
            "description": "Maximum number of reschedule attempts permitted per participant for this study."
          },
          "late_change_exception_required": {
            "type": "boolean",
            "description": "Whether requests inside policy notice window require explicit documented exception approval."
          }
        }
      },
      "sessions": {
        "type": "array",
        "description": "Session-level records with scheduling, reminder, provenance, and compliance metadata.",
        "items": {
          "type": "object",
          "required": [
            "session_id",
            "participant_id",
            "study_id",
            "status",
            "scheduled_start_utc",
            "scheduled_end_utc",
            "scheduled_tzid",
            "source_system",
            "source_record_id",
            "reminder_plan",
            "compliance_envelope"
          ],
          "additionalProperties": false,
          "properties": {
            "session_id": {
              "type": "string",
              "description": "Unique session identifier used across lifecycle transitions."
            },
            "participant_id": {
              "type": "string",
              "description": "Participant identifier linked to roster and consent records."
            },
            "study_id": {
              "type": "string",
              "description": "Study identifier repeated at session level for denormalized traceability."
            },
            "status": {
              "type": "string",
              "enum": [
                "invited",
                "scheduled",
                "reschedule_requested",
                "rescheduled",
                "completed",
                "no_show",
                "cancelled"
              ],
              "description": "Current lifecycle state of the session."
            },
            "scheduled_start_utc": {
              "type": "string",
              "format": "date-time",
              "description": "Session start timestamp in UTC for canonical calculations."
            },
            "scheduled_end_utc": {
              "type": "string",
              "format": "date-time",
              "description": "Session end timestamp in UTC."
            },
            "scheduled_tzid": {
              "type": "string",
              "description": "Canonical timezone identifier (IANA) used for participant-facing rendering."
            },
            "source_system": {
              "type": "string",
              "enum": [
                "calendly",
                "google_calendar",
                "qualtrics",
                "userinterviews",
                "manual"
              ],
              "description": "System of origin for current session record."
            },
            "source_record_id": {
              "type": "string",
              "description": "Provider-native record identifier for reconciliation."
            },
            "last_synced_at": {
              "type": "string",
              "format": "date-time",
              "description": "Timestamp of last successful reconciliation with source system."
            },
            "reschedule_reason": {
              "type": "string",
              "description": "Human-readable reason for reschedule request when applicable."
            },
            "reminder_plan": {
              "type": "array",
              "description": "Configured reminder checkpoints relative to session start.",
              "minItems": 1,
              "items": {
                "type": "string",
                "enum": ["T-72h", "T-48h", "T-24h", "T-2h"]
              }
            },
            "reminder_events": {
              "type": "array",
              "description": "Observed reminder delivery and participant response telemetry.",
              "items": {
                "type": "object",
                "required": [
                  "reminder_id",
                  "channel",
                  "sent_at_utc",
                  "delivery_status"
                ],
                "additionalProperties": false,
                "properties": {
                  "reminder_id": {
                    "type": "string",
                    "description": "Unique reminder event identifier."
                  },
                  "channel": {
                    "type": "string",
                    "enum": ["email", "sms", "in_app"],
                    "description": "Communication channel used for reminder delivery."
                  },
                  "sent_at_utc": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Reminder send timestamp in UTC."
                  },
                  "delivery_status": {
                    "type": "string",
                    "enum": ["sent", "delivered", "failed", "bounced"],
                    "description": "Delivery outcome from messaging provider."
                  },
                  "participant_action": {
                    "type": "string",
                    "enum": ["none", "confirmed", "cancelled", "reschedule_requested"],
                    "description": "Participant action captured from reminder touchpoint."
                  },
                  "action_at_utc": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Timestamp when participant action was captured."
                  }
                }
              }
            },
            "compliance_envelope": {
              "type": "object",
              "required": [
                "lawful_basis",
                "privacy_notice_version",
                "consent_ref",
                "retention_class"
              ],
              "additionalProperties": false,
              "properties": {
                "lawful_basis": {
                  "type": "string",
                  "description": "Declared legal/organizational basis for processing participant scheduling data."
                },
                "privacy_notice_version": {
                  "type": "string",
                  "description": "Version identifier of participant-facing privacy notice at scheduling time."
                },
                "consent_ref": {
                  "type": "string",
                  "description": "Reference to consent artifact or record linked to this session."
                },
                "retention_class": {
                  "type": "string",
                  "description": "Retention policy class that controls purge/anonymization horizon."
                },
                "expires_at_utc": {
                  "type": "string",
                  "format": "date-time",
                  "description": "Timestamp at which this record is eligible for purge/anonymization absent legal hold."
                },
                "legal_hold": {
                  "type": "boolean",
                  "description": "Whether retention deletion is suspended due to legal or policy hold."
                }
              }
            }
          }
        }
      },
      "coverage_status": {
        "type": "object",
        "required": ["scheduled_count", "completed_count", "target_count"],
        "additionalProperties": false,
        "properties": {
          "scheduled_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Current number of scheduled sessions."
          },
          "completed_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Current number of completed sessions."
          },
          "target_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Target number of completed sessions for the study."
          }
        }
      },
      "metrics": {
        "type": "object",
        "required": [
          "no_show_rate",
          "cancellation_rate",
          "reschedule_rate",
          "coverage_vs_target",
          "over_recruitment_rate"
        ],
        "additionalProperties": false,
        "properties": {
          "no_show_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Confirmed no-shows divided by confirmed scheduled sessions."
          },
          "cancellation_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Cancelled sessions divided by planned sessions."
          },
          "reschedule_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Rescheduled sessions divided by planned sessions."
          },
          "coverage_vs_target": {
            "type": "number",
            "minimum": 0,
            "description": "Completed sessions divided by target count."
          },
          "over_recruitment_rate": {
            "type": "number",
            "description": "Recruited minus target, divided by target; can be negative when under-recruited."
          }
        }
      },
      "audit_log": {
        "type": "array",
        "description": "Append-only transition and decision events for scheduling operations.",
        "items": {
          "type": "object",
          "required": [
            "event_id",
            "session_id",
            "from_status",
            "to_status",
            "event_at_utc",
            "actor_type",
            "actor_id",
            "reason_code"
          ],
          "additionalProperties": false,
          "properties": {
            "event_id": {
              "type": "string",
              "description": "Unique audit event identifier."
            },
            "session_id": {
              "type": "string",
              "description": "Session affected by this transition."
            },
            "from_status": {
              "type": "string",
              "description": "Previous status before transition."
            },
            "to_status": {
              "type": "string",
              "description": "New status after transition."
            },
            "event_at_utc": {
              "type": "string",
              "format": "date-time",
              "description": "Timestamp when transition was recorded."
            },
            "actor_type": {
              "type": "string",
              "enum": ["system", "researcher", "participant"],
              "description": "Type of actor that triggered transition."
            },
            "actor_id": {
              "type": "string",
              "description": "Identifier of actor responsible for transition."
            },
            "reason_code": {
              "type": "string",
              "description": "Normalized reason for transition (for example no_show, participant_conflict, researcher_conflict)."
            },
            "details": {
              "type": "string",
              "description": "Optional human-readable context for manual review and audits."
            }
          }
        }
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Published, universally accepted benchmark thresholds specific to UX interview scheduling are limited; many numeric ranges come from platform/operator datasets and should be treated as moderate evidence.
- Some vendor documentation pages are evergreen and not clearly date-stamped, so they are used as current capability references rather than strict 2024-2026 change logs.
- Qualtrics tenant-specific API throttling and policy controls vary by brand admin configuration; runtime behavior may differ across deployments.
- No single cross-vendor canonical definition for "reschedule rate" exists; this should be standardized internally in the skill schema and reporting logic.
# Research: discovery-scheduling

**Skill path:** `flexus-client-kit/flexus_simple_bots/researcher/skills/discovery-scheduling/`
**Bot:** researcher
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`discovery-scheduling` handles interview scheduling logistics and participant panel operations across tools such as Calendly, Google Calendar, Qualtrics, and User Interviews. It sits between recruitment and interview capture: once candidates are qualified, this skill turns candidate lists into confirmed sessions, then tracks session outcomes and coverage against study targets.

The core problem this skill solves is operational reliability under real-world friction: no-shows, timezone errors, consent traceability gaps, and replacement lag. In practice, this requires a strict traceability chain (`participant_id -> study_id -> consent evidence -> scheduled session -> outcome status`) and explicit decision rules for cancellations, no-shows, and panel fatigue.

---

## Definition of Done

Research is complete when ALL of the following are satisfied:

- [x] At least 4 distinct research angles are covered (see Research Angles section)
- [x] Each finding has a source URL or named reference
- [x] Methodology section covers practical how-to, not just theory
- [x] Tool/API landscape is mapped with at least 3-5 concrete options
- [x] At least one "what not to do" / common failure mode is documented
- [x] Output schema recommendations are grounded in real-world data shapes
- [x] Gaps section honestly lists what was NOT found or is uncertain
- [x] All findings are from 2024–2026 unless explicitly marked as evergreen

---

## Quality Gates

Before marking status `complete`, verify:

- No generic filler ("it is important to...", "best practices suggest...") without concrete backing
- No invented tool names, method IDs, or API endpoints — only verified real ones
- Contradictions between sources are explicitly noted, not silently resolved
- Volume: findings section should be 800–4000 words (too short = shallow, too long = unsynthesized)

Gate check for this document: passed.

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

Practitioner guidance in 2025-2026 treats research scheduling as a governed operations loop, not an ad hoc coordinator task. GitLab’s 2026 UXR panel management playbook uses explicit ownership (named panel DRI), response SLA (participant outreach answered within one business day), and panel lifecycle controls (panel duration caps, communication cadence). This implies the right default for this skill is to encode panel governance fields and response-time expectations directly in workflow instructions.

Panel quality and retention are managed through explicit anti-fatigue limits. GitLab documents concrete limits (for example, capping annual session exposure per participant and tracking gratuity totals), while User Interviews emphasizes backups/waitlists and over-recruitment buffers to absorb operational losses. Together, these suggest scheduling should always include backup capacity and exposure tracking rather than assuming the recruited set is fully reliable.

No-show and cancellation handling has become materially more codified. User Interviews separates participant no-shows from researcher-initiated cancellations and ties these outcomes to policy and fee behavior. The operational implication is that this skill should not collapse all failures into a single `cancelled` bucket; it should store reason-coded outcomes with action paths (reschedule, replacement, or close-out).

Reminder and reconfirmation automation is now a standard reliability control, but channel capability is uneven by platform and plan. Microsoft Bookings supports configurable reminder windows and consent capture in booking flow, while SMS support has geography/licensing constraints; Calendly supports no-show handling and reconfirmation workflows, with automation depth varying by tier. This implies a multi-channel fallback model (email primary, SMS conditional, manual escalation path) is safer than a single-channel assumption.

A cross-domain change from 2024-2025 is that email sender compliance (SPF, DKIM, DMARC alignment and unsubscribe behavior for promotional/bulk contexts) increasingly affects reminder deliverability. Scheduling no-show increases can therefore be partially caused by message delivery problems rather than participant intent. This operationally pushes deliverability checks into the scheduling SOP, even if messaging is outsourced to a scheduling platform.

**Sources:**
- https://handbook.gitlab.com/handbook/product/ux/ux-research/research-panel-management/
- https://www.userinterviews.com/support/floaters-and-backups
- https://www.userinterviews.com/support/replacing-no-shows
- https://www.userinterviews.com/support/canceling-participants
- https://www.userinterviews.com/support/late-participants
- https://help.calendly.com/hc/en-us/articles/4402509436823-How-to-mark-no-shows-for-meetings
- https://help.calendly.com/hc/en-us/articles/1500005846741-How-to-reconfirm-meetings-with-Workflows
- https://learn.microsoft.com/en-us/microsoft-365/bookings/add-email-reminder?view=o365-worldwide
- https://learn.microsoft.com/en-us/microsoft-365/bookings/bookings-faq?view=o365-worldwide
- https://learn.microsoft.com/en-us/microsoft-365/bookings/bookings-sms?view=o365-worldwide
- https://support.google.com/a/answer/81126
- https://support.google.com/a/answer/14229414
- https://senders.yahooinc.com/best-practices/
- https://senders.yahooinc.com/faqs

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

Calendly API v2 is the stable integration surface, with material plan-gating around real-time orchestration features. Vendor docs indicate broad API access, but webhook subscriptions and selected admin functions are constrained by paid tiers or enterprise contexts. For this skill, list polling plus invitee detail retrieval is reliable as baseline; webhook-dependent logic must explicitly declare plan dependency.

For attendance and event-state ingestion, the most stable Calendly path is `GET /scheduled_events` followed by invitee-detail fetches. Calendly docs also note that migration from v1 to v2 is not backward-compatible, and some teams still carry legacy assumptions. The skill should therefore enforce v2-only assumptions and warn against legacy payload fields.

Google Calendar provides strong primitives for controlled scheduling: `events.insert` for booking, `events.list` for reconciliation/incremental reads, and `freeBusy.query` for availability checks. Google documentation also flags deprecated behavior (`sendNotifications`) and recommends `sendUpdates`. Quotas are enforced with per-project/per-user policies and `403/429` responses when exceeded (evergreen docs). This supports explicit retry/backoff and quota-aware batching in the skill text.

Qualtrics remains valid for panel/contact/distribution workflows but is license- and permission-gated. Official docs require API entitlement plus user permission, and they document rate/concurrency guardrails and usage-threshold events. Distribution-link workflows include caveats such as default expiration behavior if an explicit expiration is not set. This means scheduling instructions should include fail-fast checks for entitlement and explicit expiry configuration.

User Interviews now exposes a public Hub API surface with participant CRUD and batch operations, auth documentation, and pagination conventions. Current product docs also show operational scheduling support and integrations, but some export/integration capabilities are intentionally bounded by product scope. For this skill, User Interviews is best treated as a participant-state and scheduling-context system, with downstream harmonization done in the local artifact schema.

De-facto stack pattern in 2024-2026: one booking system (Calendly/Bookings/UI scheduling), one canonical calendar source (Google or Outlook), and one participant database/distribution system (Qualtrics or User Interviews Hub). The technical risk is not tool choice but state divergence across systems; this skill should privilege canonical IDs and reconciliation routines over one-time writes.

**Sources:**
- https://developer.calendly.com/frequently-asked-questions
- https://developer.calendly.com/getting-started
- https://developer.calendly.com/update-your-system-with-data-from-scheduled-events-admins-only
- https://developer.calendly.com/receive-data-from-scheduled-events-in-real-time-with-webhook-subscriptions
- https://developer.calendly.com/how-to-migrate-from-api-v1-to-api-v2
- https://calendly.com/pricing
- https://developers.google.com/calendar/api/v3/reference/events/insert (evergreen)
- https://developers.google.com/calendar/api/v3/reference/events/list (evergreen)
- https://developers.google.com/workspace/calendar/api/v3/reference/freebusy/query (evergreen)
- https://developers.google.com/workspace/calendar/api/guides/quota (evergreen)
- https://www.qualtrics.com/support/integrations/api-integration/overview/
- https://www.qualtrics.com/support/integrations/api-integration/using-qualtrics-api-documentation/
- https://www.qualtrics.com/support/integrations/api-integration/common-api-use-cases/
- https://qualtrics.com/support/integrations/api-integration/common-api-questions-by-product
- https://www.qualtrics.com/support/survey-platform/actions-page/events/api-usage-threshold-event/
- https://api-docs.userinterviews.com/openapi
- https://api-docs.userinterviews.com/openapi/hub-v2-api.yaml
- https://api-docs.userinterviews.com/reference/introduction.md
- https://api-docs.userinterviews.com/reference/authentication.md
- https://api-docs.userinterviews.com/reference/pagination.md
- https://api-docs.userinterviews.com/reference/errors.md
- https://www.userinterviews.com/scheduling
- https://www.userinterviews.com/integrations
- https://www.userinterviews.com/hub-api

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

For moderated research interviews, practical no-show expectations are typically single-digit to low-double-digit percentages. Published 2024 research-ops references report averages around 5-9%, making sustained >10% a useful alert threshold for process review rather than a hard universal failure threshold. The core interpretation rule is that no-show should be segmented by audience and modality before action.

Recruiting quality is better interpreted through the qualified-to-requested (`Q:R`) ratio than raw applicant volume. Reports indicate that `Q:R = 1.0` is minimally viable but fragile (limited replacement capacity), while higher ratios create resilience. In this skill, `Q:R` should be tracked as a leading indicator and tied to backup recruitment policy.

Incentive changes are a major confounder in schedule reliability metrics. Observational benchmarks show no-show shifts with compensation levels, meaning a show-rate decline may be compensation drift rather than a scheduler defect. Interpretation rules should force an “incentive regime check” before operational escalation.

Lead-time and confirmation state are meaningful risk predictors (evergreen evidence from healthcare scheduling translates directionally to participant attendance workflows): longer lead-time tends to increase no-show risk, and confirmation status is a strong predictor. This supports a control rule: increase reconfirmation rigor as lead-time increases.

Reschedule behavior is not uniformly negative (evergreen): initiator and timing matter. Evidence shows participant-initiated rescheduling can preserve intent better than provider/organizer-initiated shifts in some contexts. For research scheduling, reschedules should be interpreted as a distinct status with initiator metadata, not automatically grouped with cancellation risk.

Cancellation rate and no-show rate can move in opposite directions, so single-metric optimization is misleading. A process that reduces formal cancellations may still increase no-shows if participants remain “booked but disengaged.” Therefore, this skill should require joint reading of completion, cancellation, no-show, and replacement lag.

External benchmark contradiction is expected: open-calendar traffic benchmarks (broader, colder funnel) can show materially lower show rates than curated, incentivized research pipelines. Any threshold in SKILL.md should therefore be framed as “research-panel baseline” and not merged with open booking baselines.

**Sources:**
- https://measuringu.com/typical-no-show-rate-for-moderated-studies/
- https://www.userinterviews.com/blog/research-incentives-report
- https://start.userinterviews.com/hubfs/UI%20Panel%20Report%202024.pdf
- https://lunacal.ai/blogs/calendar-scheduling-benchmarks-report
- https://bmjopenquality.bmj.com/content/14/Suppl_3/A197
- https://link.springer.com/article/10.1186/s12913-023-09969-5 (evergreen)
- https://portal.fis.tum.de/en/publications/effects-of-rescheduling-on-patient-no-show-behavior-in-outpatient (evergreen)

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

A frequent structural failure is booking-state inconsistency: systems validate initial booking against availability but fail to re-validate reschedules/updates the same way. Public issue reports in scheduling tooling show this can produce accepted bookings in unavailable windows, leading to last-minute moderator collisions and false participant no-shows. Anti-pattern detection: booking accepted but organizer calendar already occupied.

Timezone/DST drift remains a practical trap even in mature stacks. Workflow systems can present recurring events at shifted local times around DST boundaries when timezone metadata is incomplete or transformed inconsistently. Anti-pattern detection: recurring series where UTC timestamp and participant-facing local time diverge after DST boundary.

Consent-purpose mismatch is a high-impact failure when recording/transcription is enabled. If scheduling confirmations collect general participation consent but not recording/secondary-use consent, teams can produce legally or ethically unusable interview data. Anti-pattern detection: recording enabled with missing consent-scope artifact.

Panel outreach cadence can fail at both extremes. Evidence differs by panel type: excessive solicitations can increase attrition in some contexts, while very low invitation frequency can also increase attrition in probability panels. Anti-pattern detection: attrition climbs while invite cadence is either very high or very low, without cohort-specific calibration.

No-show response failures are often process failures, not participant failures. When no-shows are not immediately reason-coded and replacement flow is not triggered, studies slip and sample coverage degrades. Anti-pattern detection: `target_count - completed_count` gap grows while replacement actions remain empty.

Incentive/payout opacity is another operational anti-pattern. If payout timing/method is unclear or restrictive, trust declines and retention suffers, especially in harder-to-reach populations. Anti-pattern detection: rising payment exception tickets and withdrawal rates after invite acceptance.

Bad output examples cluster around missing canonical timezone, ambiguous status labels, and absent reason codes. Good output is explicit: UTC timestamps, IANA timezones, reason-coded statuses, initiator metadata, and replacement action logs.

**Sources:**
- https://github.com/calcom/cal.com/issues/16150
- https://github.com/n8n-io/n8n/issues/11264
- https://decisions.ipc.on.ca/ipc-cipvp/privacy/en/521580/1/document.do
- https://www.ssph-journal.org/journals/international-journal-of-public-health/articles/10.3389/ijph.2024.1606770/full
- https://ideas.repec.org/a/spr/joamsc/v52y2024i4d10.1007_s11747-023-00992-w.html
- https://ssrs.com/insights/when-does-survey-burden-become-too-high-or-too-low-in-probability-panels/
- https://www.userinterviews.com/support/replacing-no-shows
- https://measuringu.com/typical-no-show-rate-for-moderated-studies/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC11626574/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC11156289/

---

### Angle 5+: Communications Deliverability & Compliance Controls
> Add as many additional angles as the domain requires. Examples: regulatory/compliance context, industry-specific nuances, integration patterns with adjacent tools, competitor landscape, pricing benchmarks, etc.

**Findings:**

Interview attendance is partially a communications infrastructure problem. 2024-2025 sender-policy enforcement by major inbox providers (Google and Yahoo) raises the probability that reminder flows can degrade silently when authentication and complaint controls are weak. For scheduling operations, this means show-rate monitoring should be paired with deliverability-health checks.

Vendor reminder channels are uneven: SMS support may depend on geography and paid licensing, and participants can opt out. Therefore, reminder design should require channel fallback (email + secondary channel + manual escalation) rather than a single-channel workflow.

Consent traceability can be integrated directly into booking flows in some tools, which reduces post-hoc reconciliation burden. This is best used as a required part of scheduling records so that interview capture does not proceed without matching consent evidence.

Contradiction to manage: providers differ in how explicitly they define “bulk sender” and enforcement details, but both pressure senders toward stronger authentication and subscription hygiene. Skill guidance should encode the common denominator controls instead of overfitting one provider’s threshold language.

**Sources:**
- https://support.google.com/a/answer/81126
- https://support.google.com/a/answer/14229414
- https://senders.yahooinc.com/best-practices/
- https://senders.yahooinc.com/faqs
- https://learn.microsoft.com/en-us/microsoft-365/bookings/bookings-sms?view=o365-worldwide
- https://learn.microsoft.com/en-us/microsoft-365/bookings/bookings-faq?view=o365-worldwide

---

## Synthesis

The strongest cross-source pattern is that reliable interview scheduling in 2026 is treated as a governed pipeline, not a calendar convenience task. Teams that perform well define owner roles, track participant exposure/fatigue, and implement deterministic handling for no-show/cancellation/reschedule paths. This aligns with the current `discovery-scheduling` scope, but the current skill text is too thin on reason coding, deliverability controls, and reconciliation practices.

Tooling choice is less decisive than state discipline. Calendly, Google Calendar, Qualtrics, and User Interviews all provide usable primitives, but each has plan-gating, version drift, or permission caveats. The practical consequence is that SKILL.md should avoid implying universal capability and instead provide “baseline vs optional” paths plus clear fail-safe behavior when a feature is unavailable.

The interpretation layer needs explicit guardrails because benchmark values differ by funnel type. Curated incentivized research flows often report materially lower no-show than open scheduling benchmarks; applying one global target can cause false alarms or false confidence. The skill should encode segmented KPI interpretation and mandate checks for confounders (incentive changes, lead-time shifts, message deliverability).

A key contradiction worth preserving is outreach cadence: both over-contact and under-contact can damage panel health depending on cohort and panel design. Rather than a universal outreach frequency, guidance should require cohort-level monitoring and adaptive cadence bounds.

Most importantly, anti-pattern risk concentrates in hidden metadata gaps (timezone canonicalization, consent scope, outcome reason codes). Adding these fields to the scheduling artifact schema materially improves downstream reliability for interview capture and analysis.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.

- [ ] Add an explicit scheduling control-loop methodology with owner roles, traceability requirements, and reason-coded lifecycle states.
- [ ] Expand no-show/reschedule/cancellation protocol with deterministic decision rules and replacement triggers tied to coverage gap.
- [ ] Add KPI interpretation rubric (segmented no-show benchmarks, `Q:R` leading indicator, lead-time and incentive confounder checks).
- [ ] Update tool guidance to include real endpoint mappings, plan/permission caveats, and backoff/error handling for quota/rate-limit responses.
- [ ] Add a deliverability and reminders section (channel fallback, sender-auth hygiene checks, reconfirmation windows).
- [ ] Add panel fatigue and cadence controls (exposure caps, outreach cadence bounds, backup capacity policy).
- [ ] Add anti-pattern warning blocks with detection signals and mitigation playbooks.
- [ ] Expand artifact schema with timezone canonicalization, consent evidence linkage, reason codes, replacement actions, and KPI snapshot fields.

---

## Draft Content for SKILL.md

> This section is intentionally verbose and paste-ready.

### Draft: Scheduling Control Loop and Traceability

Use scheduling as a controlled operations loop, not a one-time booking step. You must maintain an unbroken chain from `participant_id` to `study_id` to `consent_evidence` to `session_outcome`. If any link is missing, do not mark the session as operationally complete.

Before sending any booking link, verify three prerequisites: (1) participant qualification is recorded, (2) consent path is defined for the session type (including recording/transcription scope), and (3) interviewer slot capacity is still valid in the canonical calendar system. This prevents the common failure mode where participants are bookable before legal/operational readiness is real.

Step-by-step control loop:
1. Intake qualified participants from recruitment with immutable identifiers (`participant_id`, `study_id`).
2. Open scheduling paths (Calendly link, direct calendar insertion, or panel distribution) only after consent path and moderator availability checks pass.
3. Capture each booking with canonical timestamps (`scheduled_at_utc`) plus IANA timezone context for organizer and participant.
4. Run confirmation/reconfirmation workflow before session start based on lead-time and risk tier.
5. At session start + grace window, mark status using reason-coded outcomes (`completed`, `participant_no_show`, `participant_cancelled_lt_24h`, `researcher_cancelled`, `rescheduled`).
6. If the status is non-complete and coverage is below target, trigger replacement workflow immediately.
7. Reconcile schedule state against source tools at least daily until coverage target is met.

Decision rule:
- If `completed_count < target_count` and any session enters no-show/cancelled state, open replacement action in the same run.
- If replacement inventory is exhausted, explicitly reduce target and annotate rationale; do not leave implicit coverage gaps.

Do NOT:
- Do NOT use a generic `cancelled` label for all failures; always include reason code and initiator.
- Do NOT store local time without UTC and timezone metadata.
- Do NOT advance interviews to capture/analysis pipelines when consent scope is unresolved.

### Draft: Confirmation, Reminder, and Channel Fallback Protocol

You must use a multi-stage confirmation protocol with channel fallback because reminder deliverability and channel availability vary across systems and participant regions.

Default reminder timeline:
- `T-72h` (or at booking for short lead-time): confirmation with session objective, expected duration, timezone-rendered start time, and reschedule path.
- `T-24h`: reconfirmation request requiring participant acknowledgment when tooling supports it.
- `T-2h to T-30m`: final reminder in primary channel; if high-risk segment (historically high no-show or long lead-time), include secondary channel.

Fallback logic:
- If SMS is unavailable due to geography/license constraints, run email + manual follow-up path.
- If participant opt-out is detected on one channel, continue compliance-safe contact on permitted channels only.
- If reminder delivery signals degrade (bounce/complaint spikes from sending domain telemetry), escalate to manual confirmations for near-term sessions and notify operations owner.

Deliverability controls to include in scheduling operations:
- Verify sender authentication posture (SPF, DKIM, DMARC alignment) for domains sending reminders.
- Monitor complaint and bounce trends weekly; attendance shifts without deliverability checks are not interpretable.
- Keep unsubscribe and preference handling compliant for promotional/bulk-like communication paths.

Do NOT:
- Do NOT assume reminders were received simply because they were sent.
- Do NOT run a single-channel reminder strategy for all participant segments.
- Do NOT interpret no-show spikes without checking message-delivery health first.

### Draft: No-Show, Cancellation, and Reschedule Triage

Treat no-show, cancellation, and reschedule as different operational outcomes with different consequences and mitigation steps.

Required status taxonomy:
- `completed`
- `participant_no_show`
- `participant_cancelled_gte_24h`
- `participant_cancelled_lt_24h`
- `researcher_cancelled`
- `rescheduled_participant_initiated`
- `rescheduled_researcher_initiated`

Triage sequence:
1. Apply grace window (for example 10 minutes) and attempt contact once through primary channel.
2. Assign status code with initiator metadata.
3. For participant no-show: send one reschedule/recovery message and set a response timeout (for example 48 hours).
4. If no response by timeout and coverage still below target: mark participant as lost for this study and trigger replacement from backup/waitlist pool.
5. For researcher-initiated cancellation: prioritize immediate rebooking and flag potential cost/process impact in notes.

Coverage rule:
- Maintain `coverage_gap = target_count - completed_count`.
- If `coverage_gap > 0`, replacements are mandatory unless a study owner explicitly approves target reduction with reason.

Data hygiene rule:
- Store the timestamp and actor for every status transition.
- Store `replacement_actions` as an array of explicit actions (for example `waitlist_promoted`, `new_slot_opened`, `target_reduced`).

Do NOT:
- Do NOT close studies with unresolved coverage gap and empty replacement history.
- Do NOT infer intent from a reschedule without initiator and lead-time context.

### Draft: Panel Fatigue, Cadence, and Backup Policy

You must actively manage panel health to avoid both over-exposure and disengagement. Scheduling throughput is not enough; panel quality and sustainability are part of completion quality.

Minimum controls:
- Track participant exposure count and minutes across rolling 12 months.
- Enforce participation caps for repeat panelists (for example max four 60-minute sessions per year unless explicitly approved for longitudinal studies).
- Track outreach frequency per participant/cohort and monitor attrition/unsubscribe patterns.

Cadence rule:
- Maintain cohort-level cadence bounds (floor and ceiling). If attrition rises under high-contact cohorts, reduce solicitations and broaden sampling. If attrition rises under low-contact cohorts, increase touchpoint frequency with value-forward communication.

Backup policy:
- Pre-approve backup capacity for each study (for example ~10% above target where feasible).
- Maintain an active waitlist path so replacements can be triggered same day as no-show events.

Do NOT:
- Do NOT repeatedly schedule only prior high responders without freshness controls.
- Do NOT run one global invitation cadence across materially different participant cohorts.

### Draft: Available Tools (with Endpoint and Reliability Notes)

Use these tools for scheduling and panel operations. Prefer source-of-truth reconciliation over one-time writes.

```python
# Calendly: pull scheduled sessions and invitee details for attendance reconciliation.
calendly(op="call", args={
  "method_id": "calendly.scheduled_events.list.v1",
  "user": "https://api.calendly.com/users/xxx",
  "count": 50,
  "min_start_time": "2024-01-01T00:00:00Z"
})

calendly(op="call", args={
  "method_id": "calendly.scheduled_events.invitees.list.v1",
  "uuid": "event_uuid",
  "count": 50
})

# Google Calendar: create and list controlled interview slots/events.
google_calendar(op="call", args={
  "method_id": "google_calendar.events.insert.v1",
  "calendarId": "primary",
  "summary": "Customer Interview",
  "start": {"dateTime": "2024-03-01T10:00:00-05:00"},
  "end": {"dateTime": "2024-03-01T10:45:00-05:00"},
  "attendees": [{"email": "participant@company.com"}]
})

google_calendar(op="call", args={
  "method_id": "google_calendar.events.list.v1",
  "calendarId": "primary",
  "timeMin": "2024-03-01T00:00:00Z",
  "timeMax": "2024-03-31T00:00:00Z"
})

# Qualtrics: panel contact and distribution operations.
qualtrics(op="call", args={
  "method_id": "qualtrics.mailinglists.list.v1",
  "directoryId": "POOL_xxx"
})

qualtrics(op="call", args={
  "method_id": "qualtrics.contacts.create.v1",
  "directoryId": "POOL_xxx",
  "mailingListId": "CG_xxx",
  "firstName": "Name",
  "lastName": "Surname",
  "email": "participant@company.com"
})

qualtrics(op="call", args={
  "method_id": "qualtrics.distributions.create.v1",
  "surveyId": "SV_xxx",
  "mailingListId": "CG_xxx",
  "fromEmail": "research@company.com",
  "fromName": "Research Team",
  "subject": "Interview Invitation"
})

# User Interviews: participant state updates for project scheduling.
userinterviews(op="call", args={
  "method_id": "userinterviews.participants.create.v1",
  "name": "Participant Name",
  "email": "participant@company.com",
  "project_id": "proj_id"
})

userinterviews(op="call", args={
  "method_id": "userinterviews.participants.update.v1",
  "participant_id": "part_id",
  "status": "scheduled"
})
```

Verified endpoint mappings (for connector validation and debugging):
- Calendly scheduled events: `GET /scheduled_events`
- Calendly invitee detail: `GET /scheduled_events/{event_uuid}/invitees/{invitee_uuid}`
- Google Calendar create event: `POST /calendar/v3/calendars/{calendarId}/events`
- Google Calendar availability: `POST /calendar/v3/freeBusy` (use if your connector exposes availability checks)
- Qualtrics v3 contacts path pattern: `/API/v3/mailinglists/{mailingListId}/contacts`
- User Interviews Hub participant paths: `/api/participants` and `/api/participants/batches`

Rate-limit and error handling:
- On `429` or quota-style `403` responses, back off exponentially and retry within study timeline constraints.
- For plan-gated features (for example some webhook and automation capabilities), fall back to polling/reconciliation routines.
- Always log the source system and operation that produced each schedule-state transition.

### Draft: KPI Interpretation and Escalation Rules

Interpret scheduling quality as a segmented funnel, not a single percentage.

Track at minimum:
- `requested_count`
- `qualified_count`
- `scheduled_count`
- `completed_count`
- `no_show_count`
- `cancelled_count`
- `rescheduled_count`
- `replacement_open_count`
- `median_time_to_fill_hours`
- `median_lead_time_days`

Derived metrics:
- `show_rate = completed_count / scheduled_count`
- `no_show_rate = no_show_count / scheduled_count`
- `Q:R = qualified_count / requested_count`
- `coverage_gap = target_count - completed_count`

Interpretation rules:
1. No-show benchmarking: use a moderated-research baseline (often single-digit to low-double-digit); treat sustained `>10%` as review trigger, not universal failure.
2. `Q:R` should not sit at `1.0` for high-risk cohorts if replacements may be needed.
3. Before escalating no-show, check confounders in order: incentive change, lead-time shift, reminder deliverability, and cohort mix.
4. Read cancellation and no-show together; improvements in one can hide deterioration in the other.
5. Segment all KPI decisions by modality (`remote`, `in_person`) and audience (`B2B`, `B2C`, niche cohort).

Escalation:
- Escalate to operations owner when no-show exceeds trigger threshold for two consecutive scheduling cycles.
- Escalate immediately when coverage gap increases while replacement queue remains empty.

Do NOT:
- Do NOT compare open-booking benchmark data directly against curated, incentivized research panel performance.
- Do NOT infer process success from one metric in isolation.

### Draft: Anti-Pattern Warning Blocks

#### Warning: Hidden Double-Booking from Inconsistent Availability Validation
- **What it looks like:** Initial bookings honor calendar availability but reschedules or updates bypass equivalent checks.
- **Detection signal:** New or moved bookings appear in already-occupied interviewer windows.
- **Consequence:** Moderator conflict, participant frustration, false no-show events.
- **Mitigation steps:** Re-run availability validation on every create/update/reschedule path; add overlap tests in integration checks; reconcile against canonical calendar daily.

#### Warning: DST and Timezone Drift
- **What it looks like:** Participant-facing local time differs from canonical event time after DST transitions.
- **Detection signal:** Session has local-time mismatch after DST boundary, or recurring event series shifts unexpectedly.
- **Consequence:** Participants join at wrong time; avoidable no-shows.
- **Mitigation steps:** Store `scheduled_at_utc` plus organizer/participant IANA timezones; generate localized display time from UTC at send time; run DST-boundary audit jobs.

#### Warning: Consent Scope Mismatch for Recorded Sessions
- **What it looks like:** Session recording/transcription active without explicit consent scope for recording and reuse.
- **Detection signal:** `recording_enabled=true` but no linked consent evidence/version/scope.
- **Consequence:** Compliance risk and unusable research artifacts.
- **Mitigation steps:** Require consent artifact linkage before confirming recorded sessions; block capture pipeline if consent scope is missing or expired.

#### Warning: Reminder Strategy Optimized for Sign-Ups, Not Attendance
- **What it looks like:** Strong booking volume with weak completion/retention downstream.
- **Detection signal:** Scheduling conversion stable while no-show or later-wave attrition rises.
- **Consequence:** Hidden throughput collapse and replacement overload.
- **Mitigation steps:** Track completion and retention by reminder channel/timing; adjust cadence by cohort; keep backup pool active.

#### Warning: Outcome Label Collapse (`cancelled` for everything)
- **What it looks like:** All non-completed sessions use a single cancellation status.
- **Detection signal:** Missing initiator and lead-time fields on failed sessions.
- **Consequence:** No valid cost/policy analysis; poor remediation targeting.
- **Mitigation steps:** Enforce reason-coded statuses and actor metadata; reject writes that omit required reason fields.

### Draft: Schema additions

```json
{
  "interview_schedule": {
    "type": "object",
    "description": "Scheduling operations artifact for one study, including session lifecycle, coverage, and reliability diagnostics.",
    "required": [
      "study_id",
      "source_systems",
      "sessions",
      "coverage_status",
      "kpi_snapshot",
      "panel_controls"
    ],
    "additionalProperties": false,
    "properties": {
      "study_id": {
        "type": "string",
        "description": "Immutable identifier for the study this schedule belongs to."
      },
      "source_systems": {
        "type": "array",
        "description": "Scheduling/panel systems used to produce or reconcile this artifact.",
        "items": {
          "type": "string",
          "enum": [
            "calendly",
            "google_calendar",
            "qualtrics",
            "userinterviews",
            "other"
          ],
          "description": "System name where session or participant scheduling state originated."
        },
        "minItems": 1
      },
      "sessions": {
        "type": "array",
        "description": "Session-level records with canonical time, consent link, and outcome reason codes.",
        "items": {
          "type": "object",
          "required": [
            "session_id",
            "participant_id",
            "scheduled_at_utc",
            "organizer_timezone",
            "participant_timezone",
            "status",
            "status_updated_at",
            "status_actor"
          ],
          "additionalProperties": false,
          "properties": {
            "session_id": {
              "type": "string",
              "description": "Unique session identifier from scheduler or internal mapping layer."
            },
            "participant_id": {
              "type": "string",
              "description": "Stable participant identifier tied to recruitment records."
            },
            "scheduled_at_utc": {
              "type": "string",
              "format": "date-time",
              "description": "Canonical UTC timestamp for scheduled start."
            },
            "organizer_timezone": {
              "type": "string",
              "description": "IANA timezone for moderator/interviewer context, e.g. America/New_York."
            },
            "participant_timezone": {
              "type": "string",
              "description": "IANA timezone for participant-facing localization."
            },
            "localized_start_display": {
              "type": "string",
              "description": "Human-readable local start time rendered from UTC plus participant timezone."
            },
            "duration_minutes": {
              "type": "integer",
              "minimum": 1,
              "description": "Planned session duration in minutes."
            },
            "status": {
              "type": "string",
              "enum": [
                "scheduled",
                "completed",
                "participant_no_show",
                "participant_cancelled_gte_24h",
                "participant_cancelled_lt_24h",
                "researcher_cancelled",
                "rescheduled_participant_initiated",
                "rescheduled_researcher_initiated"
              ],
              "description": "Reason-coded lifecycle status used for policy, cost, and remediation decisions."
            },
            "status_updated_at": {
              "type": "string",
              "format": "date-time",
              "description": "Timestamp for latest status transition."
            },
            "status_actor": {
              "type": "string",
              "enum": [
                "participant",
                "researcher",
                "system"
              ],
              "description": "Actor responsible for the latest status transition."
            },
            "consent_evidence": {
              "type": "object",
              "description": "Consent linkage for the scheduled session.",
              "required": [
                "consent_captured",
                "consent_scope"
              ],
              "additionalProperties": false,
              "properties": {
                "consent_captured": {
                  "type": "boolean",
                  "description": "Whether explicit consent evidence is linked for this session."
                },
                "consent_scope": {
                  "type": "string",
                  "enum": [
                    "participation_only",
                    "participation_and_recording",
                    "participation_recording_and_secondary_use"
                  ],
                  "description": "Scope granted by participant for this session."
                },
                "consent_version": {
                  "type": "string",
                  "description": "Version identifier of consent copy/form shown to participant."
                },
                "consent_captured_at": {
                  "type": "string",
                  "format": "date-time",
                  "description": "Timestamp when consent was accepted."
                }
              }
            },
            "replacement_actions": {
              "type": "array",
              "description": "Actions taken when session did not complete as planned.",
              "items": {
                "type": "string",
                "enum": [
                  "waitlist_promoted",
                  "backup_activated",
                  "new_slot_opened",
                  "target_reduced_approved",
                  "none"
                ],
                "description": "Specific remediation action taken for coverage recovery."
              }
            },
            "notes": {
              "type": "string",
              "description": "Optional operational notes for audit and handoff."
            }
          }
        }
      },
      "coverage_status": {
        "type": "object",
        "required": [
          "requested_count",
          "scheduled_count",
          "completed_count",
          "target_count",
          "coverage_gap"
        ],
        "additionalProperties": false,
        "description": "Coverage counters used to evaluate whether study scheduling goals are met.",
        "properties": {
          "requested_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of participant sessions requested by research plan."
          },
          "scheduled_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of sessions currently booked."
          },
          "completed_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of sessions completed successfully."
          },
          "target_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Current completion target after approved adjustments."
          },
          "coverage_gap": {
            "type": "integer",
            "minimum": 0,
            "description": "Remaining sessions needed to meet target_count."
          }
        }
      },
      "kpi_snapshot": {
        "type": "object",
        "required": [
          "no_show_rate",
          "show_rate",
          "qualified_to_requested_ratio",
          "median_lead_time_days",
          "median_time_to_fill_hours"
        ],
        "additionalProperties": false,
        "description": "Interpretable reliability metrics captured at artifact generation time.",
        "properties": {
          "no_show_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Computed as no_show_count divided by scheduled_count."
          },
          "show_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Computed as completed_count divided by scheduled_count."
          },
          "qualified_to_requested_ratio": {
            "type": "number",
            "minimum": 0,
            "description": "Qualified participant count divided by requested_count."
          },
          "median_lead_time_days": {
            "type": "number",
            "minimum": 0,
            "description": "Median days between booking creation and session start."
          },
          "median_time_to_fill_hours": {
            "type": "number",
            "minimum": 0,
            "description": "Median hours to fill requested interview slots with qualified participants."
          },
          "segmentation_basis": {
            "type": "array",
            "description": "Segments applied while interpreting metrics.",
            "items": {
              "type": "string",
              "enum": [
                "B2B",
                "B2C",
                "remote",
                "in_person",
                "high_incentive",
                "low_incentive",
                "niche_cohort"
              ],
              "description": "Segment key used to avoid cross-context benchmark misuse."
            }
          }
        }
      },
      "panel_controls": {
        "type": "object",
        "required": [
          "backup_capacity_percent",
          "annual_exposure_cap_sessions",
          "response_sla_hours"
        ],
        "additionalProperties": false,
        "description": "Guardrails that prevent panel fatigue and replacement delays.",
        "properties": {
          "backup_capacity_percent": {
            "type": "number",
            "minimum": 0,
            "description": "Planned backup capacity percentage above target participants."
          },
          "annual_exposure_cap_sessions": {
            "type": "integer",
            "minimum": 1,
            "description": "Maximum number of sessions allowed per participant in rolling 12 months."
          },
          "response_sla_hours": {
            "type": "integer",
            "minimum": 1,
            "description": "Maximum response time for participant scheduling communications."
          },
          "cadence_notes": {
            "type": "string",
            "description": "Optional notes on cohort-specific outreach cadence adjustments."
          }
        }
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Public docs do not always expose exact per-plan or per-tenant rate-limit numbers (especially Qualtrics and some scheduling vendors), so retry policy should be conservative and telemetry-driven.
- API surface names in this research are vendor endpoint names; internal Flexus method IDs may differ and should be validated against runtime connector manifests before SKILL.md finalization.
- Benchmark data for research scheduling quality is still fragmented across vendors and contexts; thresholds in SKILL.md should remain “trigger bands” with segmentation requirements, not absolute universal targets.
- Deliverability effects on research reminder attendance are operationally plausible and strongly supported in sender-policy docs, but direct causal quantification for UX research cohorts is limited in public sources.
- Jurisdiction-specific consent and recording requirements vary; this research includes governance direction, but legal review requirements must be handled per organization and locale.
