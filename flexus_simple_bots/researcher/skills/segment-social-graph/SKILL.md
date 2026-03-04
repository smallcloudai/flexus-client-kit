---
name: segment-social-graph
description: Professional social graph profiling — decision-maker mapping, influence network analysis, and contact-level enrichment
---

You map professional influence networks and enrich contact-level profiles for target segments. Social graph data reveals who has decision authority, who influences them, and what path-to-champion looks like inside a target account.

Core mode: professional context only. Do not use personal social data (non-LinkedIn). Enrich only for legitimate business prospecting. PII compliance: never store full names + emails together in artifact output. Use anonymized IDs referencing source systems.

## Methodology

### Decision-maker mapping
For a target company, identify: economic buyer, technical buyer, user champion, influencer.
Use `pdl.person.enrichment.v1` with role filtering to find contacts at specific titles.
Cross-validate with `apollo.people.search.v1` for current role verification.

### LinkedIn org structure
Use `linkedin.organization.posts.list.v1` to understand what topics the organization publicly discusses — this reveals what the leadership team cares about.

Use `clearbit.person.enrichment.v1` to enrich known contacts with LinkedIn URL, bio, and prior company history.

### Influence network patterns
- Shared board members or investors between companies: signals shared values/priorities
- Mutual connections: can be leveraged for warm introductions
- Employee-to-employee referral network at target company: maps who knows who

### Alumni networks
People who have worked at a company in the past are often still influential in buying decisions at former employers. Check prior company history in PDL person data.

## Recording

```
write_artifact(artifact_type="segment_social_graph_profile", path="/segments/{segment_id}/social-graph", data={...})
```

## Available Tools

```
linkedin(op="call", args={"method_id": "linkedin.organization.posts.list.v1", "organizationId": "urn:li:organization:12345", "count": 20})

linkedin(op="call", args={"method_id": "linkedin.organization.followers.stats.v1", "organizationId": "urn:li:organization:12345"})

pdl(op="call", args={"method_id": "pdl.person.enrichment.v1", "profile": "linkedin.com/in/username", "pretty": true})

pdl(op="call", args={"method_id": "pdl.person.search.v1", "query": {"bool": {"must": [{"term": {"job_company_website": "company.com"}}, {"term": {"job_title_role": "engineering"}}]}}, "size": 10})

apollo(op="call", args={"method_id": "apollo.people.search.v1", "q_organization_domains": ["company.com"], "person_titles": ["CTO", "VP Engineering", "Head of Product"], "per_page": 25})

clearbit(op="call", args={"method_id": "clearbit.person.enrichment.v1", "email": "contact@company.com"})
```

## Artifact Schema

```json
{
  "segment_social_graph_profile": {
    "type": "object",
    "required": ["segment_id", "profiled_at", "accounts"],
    "additionalProperties": false,
    "properties": {
      "segment_id": {"type": "string"},
      "profiled_at": {"type": "string"},
      "accounts": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["domain", "decision_makers", "influence_paths"],
          "additionalProperties": false,
          "properties": {
            "domain": {"type": "string"},
            "decision_makers": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["contact_ref", "buyer_role", "seniority"],
                "additionalProperties": false,
                "properties": {
                  "contact_ref": {"type": "string", "description": "Anonymized ID referencing CRM or source system"},
                  "buyer_role": {"type": "string", "enum": ["economic_buyer", "technical_buyer", "champion", "influencer", "gatekeeper"]},
                  "seniority": {"type": "string", "enum": ["c_level", "vp", "director", "manager", "ic"]}
                }
              }
            },
            "influence_paths": {"type": "array", "items": {"type": "string"}},
            "org_topics": {"type": "array", "items": {"type": "string"}}
          }
        }
      }
    }
  }
}
```
