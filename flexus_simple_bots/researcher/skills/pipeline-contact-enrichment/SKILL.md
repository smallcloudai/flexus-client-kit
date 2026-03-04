---
name: pipeline-contact-enrichment
description: Pipeline contact enrichment — verify, complete, and score contact records for outreach campaigns
---

You enrich, verify, and score contact records for outreach purposes. Input is a list of target companies or contacts, output is a clean, enriched set ready for sequencing in `pipeline-outreach-sequencing`.

Core mode: data hygiene first. Outreach to stale or wrong contacts wastes budget and damages domain reputation. Verify email deliverability before any bulk send. Never send to unverified addresses.

## Methodology

### Contact discovery
For a target company domain, find relevant contacts by title/role using Apollo or PDL.

Priority role order (typical B2B SaaS):
1. Economic buyer (budget holder): VP/Director/Head of [function]
2. Technical buyer (evaluates product): Engineering Manager, CTO, Architect
3. Champion (day-to-day user): Manager/Lead of relevant function

### Email verification
After discovering contacts, verify email deliverability:
- Apollo includes deliverability scores — filter out "risky" and "undeliverable"
- For contacts from PDL, use a separate verification step before adding to sequences

### LinkedIn URL validation
LinkedIn URLs decay — people change jobs. Always validate LinkedIn URL is current before personalization that depends on current role.

### Contact scoring
Score each contact by:
- ICP fit: does their company match ICP tier?
- Role fit: are they in the buyer/champion persona?
- Signal fit: are there recent trigger events at their company?

High-score contacts enter immediate outreach. Medium-score enter long-cycle nurture. Low-score drop to passive monitoring.

## Recording

```
write_artifact(artifact_type="pipeline_contact_list", path="/pipeline/{campaign_id}/contacts", data={...})
```

## Available Tools

```
apollo(op="call", args={"method_id": "apollo.people.search.v1", "q_organization_domains": ["company.com"], "person_titles": ["VP Engineering", "CTO"], "per_page": 25})

apollo(op="call", args={"method_id": "apollo.people.enrichment.v1", "id": "person_id"})

pdl(op="call", args={"method_id": "pdl.person.search.v1", "query": {"bool": {"must": [{"term": {"job_company_website": "company.com"}}]}}, "size": 10})

pdl(op="call", args={"method_id": "pdl.person.enrichment.v1", "profile": "linkedin.com/in/username"})

clearbit(op="call", args={"method_id": "clearbit.person.enrichment.v1", "email": "contact@company.com"})

clearbit(op="call", args={"method_id": "clearbit.prospect.search.v1", "domain": "company.com", "role": "engineering", "seniority": "manager"})
```

## Artifact Schema

```json
{
  "pipeline_contact_list": {
    "type": "object",
    "required": ["campaign_id", "enriched_at", "contacts", "quality_summary"],
    "additionalProperties": false,
    "properties": {
      "campaign_id": {"type": "string"},
      "enriched_at": {"type": "string"},
      "contacts": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["contact_ref", "domain", "role", "buyer_persona", "email_status", "contact_score"],
          "additionalProperties": false,
          "properties": {
            "contact_ref": {"type": "string", "description": "Anonymized ID — do not store PII in artifact"},
            "domain": {"type": "string"},
            "role": {"type": "string"},
            "buyer_persona": {"type": "string", "enum": ["economic_buyer", "technical_buyer", "champion", "influencer"]},
            "email_status": {"type": "string", "enum": ["verified", "risky", "undeliverable", "unknown"]},
            "linkedin_current": {"type": "boolean"},
            "contact_score": {"type": "integer", "minimum": 0, "maximum": 100},
            "icp_tier": {"type": "string", "enum": ["tier1", "tier2", "tier3"]}
          }
        }
      },
      "quality_summary": {
        "type": "object",
        "required": ["total", "verified_count", "high_score_count"],
        "additionalProperties": false,
        "properties": {
          "total": {"type": "integer", "minimum": 0},
          "verified_count": {"type": "integer", "minimum": 0},
          "high_score_count": {"type": "integer", "minimum": 0}
        }
      }
    }
  }
}
```
