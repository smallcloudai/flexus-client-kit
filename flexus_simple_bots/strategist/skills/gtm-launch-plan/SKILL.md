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
write_artifact(path="/strategy/gtm-launch-plan", data={...})
```

## Available Tools

```
flexus_policy_document(op="activate", args={"p": "/strategy/gtm-channel-strategy"})
flexus_policy_document(op="activate", args={"p": "/strategy/pricing-pilot-packaging"})
flexus_policy_document(op="activate", args={"p": "/strategy/mvp-validation-criteria"})
google_calendar(op="call", args={"method_id": "google_calendar.events.insert.v1", "calendarId": "primary", "summary": "GTM Launch Day", "start": {"date": "2024-03-01"}})
```
