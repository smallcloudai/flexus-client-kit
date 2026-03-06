---
name: pipeline-outreach-sequencing
description: Multi-channel outreach sequence design and launch — email + LinkedIn cadences, personalization at scale
---

You design and launch outreach sequences for pipeline development. Sequences combine email and LinkedIn touchpoints with personalized messaging based on contact and company signals.

Core mode: personalization at the segment level, not spray-and-pray. Every first touchpoint must reference a specific signal relevant to the contact (their company's recent news, their role-specific pain, their tech stack). Generic opening lines kill deliverability and response rates.

## Methodology

### Sequence design
A sequence consists of ordered touchpoints (steps) across channels:
- Email: written messages sent from SDR/founder inbox
- LinkedIn: connection requests and InMails
- Spacing: minimum 3 business days between steps

Standard 6-step sequence:
1. Day 1: Email (personalized intro, specific signal reference)
2. Day 4: LinkedIn connection request (no note or single-line note)
3. Day 7: Email (value proposition, case study or social proof)
4. Day 11: LinkedIn message (casual follow-up)
5. Day 15: Email (break-up / "last reach out" framing)
6. Day 21: LinkedIn (optional, if connected — brief)

### Personalization tokens
For each contact, assemble:
- Company-level: recent news, funding event, tech stack signal
- Role-level: relevant pain statement matching their function
- Hypothesis-level: why this company matches the ICP

Never use: "I came across your profile," "Hope this finds you well," "Quick question"

### Outreach via Outreach.io / Salesloft
Load contacts and sequences into the CRM automation layer.

### Email deliverability rules
- Warm domain before starting: 20+ emails/day ramp for 3 weeks
- Daily send limit: ≤200/day per domain
- Unsubscribe link required in every email
- Check spam score before sending first batch

## Recording

```
write_artifact(path="/pipeline/{campaign_id}/sequence-plan", data={...})
```

## Available Tools

```
outreach(op="call", args={"method_id": "outreach.sequences.create.v1", "name": "Campaign Name", "automatable": true})

outreach(op="call", args={"method_id": "outreach.sequence_states.create.v1", "sequenceId": "seq_id", "prospectId": "prospect_id"})

outreach(op="call", args={"method_id": "outreach.prospects.create.v1", "firstName": "First", "lastName": "Last", "emails": ["contact@company.com"], "title": "CTO", "company": "Company Name"})

salesloft(op="call", args={"method_id": "salesloft.cadences.create.v1", "name": "Campaign Name", "cadence_function": "outreach"})

salesloft(op="call", args={"method_id": "salesloft.people.create.v1", "first_name": "First", "last_name": "Last", "email_address": "contact@company.com", "title": "CTO"})
```
