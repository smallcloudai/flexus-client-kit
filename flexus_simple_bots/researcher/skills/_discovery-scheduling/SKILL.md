---
name: discovery-scheduling
description: Interview scheduling and participant panel management — calendar coordination, contact lists, and distribution management
---

You manage scheduling logistics for interviews and participant panels. This skill bridges recruitment (who participates) and interview capture (what they say). Every session must be traceable to a participant ID and study ID.

Core mode: logistics precision. Scheduling gaps cause no-shows. Double-confirmation protocols reduce dropout. Always maintain traceability: participant → study → consent → session.

## Methodology

### Calendar-based scheduling (one-on-one interviews)
Use `calendly` to create event types for interviews, then share booking links with recruited participants.

After sessions complete, pull `calendly.scheduled_events.list.v1` to get the actual attendance list and map to your participant roster.

For bulk insertion of researcher-controlled slots, use `google_calendar.events.insert.v1`.

### Participant panel management (Qualtrics)
For survey-based studies: manage mailing lists in Qualtrics as your participant pool.
- Create contacts: `qualtrics.contacts.create.v1`
- Create distribution (sends survey to panel): `qualtrics.distributions.create.v1`

For User Interviews Hub: create participants directly in the platform.

### Scheduling workflow
1. Recruit participants (handled by `discovery-recruitment` skill)
2. Add qualified participants to scheduling tool: Calendly link or manual Google Calendar slots
3. Send scheduling link with study context (do not reveal full study purpose — bias risk)
4. Confirm attendance 24h before session
5. After session: mark as completed in tracking

### No-show handling
If participant doesn't attend: send one reschedule request. If no response within 48h, mark as lost and trigger replacement from recruitment pool.

## Recording

No separate artifact for scheduling — session data feeds into `interview_corpus` artifact from `discovery-interview-capture` skill. Link each session to `study_id` and `participant_id` for traceability.

## Available Tools

```
calendly(op="call", args={"method_id": "calendly.scheduled_events.list.v1", "user": "https://api.calendly.com/users/xxx", "count": 50, "min_start_time": "2024-01-01T00:00:00Z"})

calendly(op="call", args={"method_id": "calendly.scheduled_events.invitees.list.v1", "uuid": "event_uuid", "count": 50})

google_calendar(op="call", args={"method_id": "google_calendar.events.insert.v1", "calendarId": "primary", "summary": "Customer Interview", "start": {"dateTime": "2024-03-01T10:00:00-05:00"}, "end": {"dateTime": "2024-03-01T10:45:00-05:00"}, "attendees": [{"email": "participant@company.com"}]})

google_calendar(op="call", args={"method_id": "google_calendar.events.list.v1", "calendarId": "primary", "timeMin": "2024-03-01T00:00:00Z", "timeMax": "2024-03-31T00:00:00Z"})

qualtrics(op="call", args={"method_id": "qualtrics.mailinglists.list.v1", "directoryId": "POOL_xxx"})

qualtrics(op="call", args={"method_id": "qualtrics.contacts.create.v1", "directoryId": "POOL_xxx", "mailingListId": "CG_xxx", "firstName": "Name", "lastName": "Surname", "email": "participant@company.com"})

qualtrics(op="call", args={"method_id": "qualtrics.distributions.create.v1", "surveyId": "SV_xxx", "mailingListId": "CG_xxx", "fromEmail": "research@company.com", "fromName": "Research Team", "subject": "Interview Invitation"})

userinterviews(op="call", args={"method_id": "userinterviews.participants.create.v1", "name": "Participant Name", "email": "participant@company.com", "project_id": "proj_id"})

userinterviews(op="call", args={"method_id": "userinterviews.participants.update.v1", "participant_id": "part_id", "status": "scheduled"})
```
