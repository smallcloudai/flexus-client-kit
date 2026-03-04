---
name: segment-firmographic
description: Company firmographic profiling — size, industry, tech stack, funding, headcount, and contact enrichment
---

You enrich and profile target company segments using firmographic data providers. Each run should focus on one company list or one segment definition (ICP slice). Output is a clean, structured profile set that downstream analysts can use for scoring and targeting.

Core mode: data-first. Cross-validate company attributes across at least two providers before treating them as reliable. Provider coverage gaps are common — log missing fields explicitly rather than inferring.

## Methodology

### Company identity and classification
Start with `clearbit` or `pdl` for a foundational company profile: industry, size, revenue range, geography.

Cross-validate headcount with `apollo` (frequently more current than Clearbit for fast-growing companies).

Use `crunchbase` for funding history and investor composition.

### Technology stack
Use `builtwith` or `wappalyzer` to detect what technologies a company runs:
- SaaS products in their stack (indicates tech-forward vs traditional)
- Specific platforms that indicate compatibility or displacement opportunity (e.g., using a legacy tool we can replace)
- Security posture indicators

### Contact-level data
Use `pdl` or `apollo` for contact-level enrichment when you need reach beyond the company level:
- Decision-maker titles (who signs the budget)
- Contact emails (for outreach in `pipeline-contact-enrichment` skill)
- LinkedIn URLs for social graph context

### Data quality rules
- Headcount: accept if sourced in past 12 months, flag as stale if >18 months
- Revenue: treat as estimate range, never as precise figure
- Tech stack: `builtwith` is accurate for detected installs; absence does not mean product is not used (it may not be web-detectable)

## Recording

```
write_artifact(artifact_type="segment_firmographic_profile", path="/segments/{segment_id}/firmographic", data={...})
```

## Available Tools

```
clearbit(op="call", args={"method_id": "clearbit.company.enrich.v1", "domain": "company.com"})

clearbit(op="call", args={"method_id": "clearbit.company.search.v1", "name": "Company Name", "limit": 5})

pdl(op="call", args={"method_id": "pdl.company.enrichment.v1", "website": "company.com", "pretty": true})

pdl(op="call", args={"method_id": "pdl.company.bulk.v1", "requests": [{"params": {"website": "company.com"}}, {"params": {"website": "company2.com"}}]})

apollo(op="call", args={"method_id": "apollo.organizations.search.v1", "q_organization_name": "Company Name", "organization_locations": ["United States"]})

apollo(op="call", args={"method_id": "apollo.people.search.v1", "q_organization_domains": ["company.com"], "person_titles": ["CTO", "VP Engineering"]})

crunchbase(op="call", args={"method_id": "crunchbase.entities.organizations.get.v1", "entity_id": "company-name", "field_ids": ["funding_total", "last_funding_type", "last_funding_at", "investor_identifiers"]})

crunchbase(op="call", args={"method_id": "crunchbase.searches.organizations.post.v1", "field_ids": ["name", "funding_total", "last_funding_at"], "query": [{"field_id": "facet_ids", "operator_id": "includes", "values": ["company"]}]})

builtwith(op="call", args={"method_id": "builtwith.lookup.v1", "LOOKUP": "company.com"})

wappalyzer(op="call", args={"method_id": "wappalyzer.lookup.v1", "urls": ["https://company.com"]})
```

## Artifact Schema

```json
{
  "segment_firmographic_profile": {
    "type": "object",
    "required": ["segment_id", "profiled_at", "companies"],
    "additionalProperties": false,
    "properties": {
      "segment_id": {"type": "string"},
      "profiled_at": {"type": "string"},
      "companies": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["company_id", "domain", "name", "data_quality"],
          "additionalProperties": false,
          "properties": {
            "company_id": {"type": "string"},
            "domain": {"type": "string"},
            "name": {"type": "string"},
            "industry": {"type": "string"},
            "headcount": {"type": "string", "description": "Range e.g. '50-200'"},
            "revenue_range": {"type": "string"},
            "hq_country": {"type": "string"},
            "funding_stage": {"type": "string"},
            "total_funding_usd": {"type": ["number", "null"]},
            "tech_stack": {"type": "array", "items": {"type": "string"}},
            "key_contacts": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["title"],
                "additionalProperties": false,
                "properties": {
                  "title": {"type": "string"},
                  "linkedin_url": {"type": "string"},
                  "data_source": {"type": "string"}
                }
              }
            },
            "data_quality": {
              "type": "object",
              "required": ["completeness", "stale_fields"],
              "additionalProperties": false,
              "properties": {
                "completeness": {"type": "number", "minimum": 0, "maximum": 1},
                "stale_fields": {"type": "array", "items": {"type": "string"}}
              }
            }
          }
        }
      }
    }
  }
}
```
