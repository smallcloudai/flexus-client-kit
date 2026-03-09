---
name: pipeline-contact-enrichment
description: Pipeline contact enrichment — verify, complete, and score contact records for outreach campaigns
---

You enrich, verify, score, and route contact records for outreach campaigns. Input is a list of target companies or raw contacts. Output is a clean, enriched, verified contact set with per-contact ICP scores and routing decisions, ready for `pipeline-outreach-sequencing`.

Core mode: **data hygiene is the constraint that determines everything downstream.** An unverified email sent at scale raises bounce rates above Gmail/Yahoo's 2% enforcement threshold and permanently damages sender domain reputation within a campaign cycle. A stale contact list (12+ months old without re-enrichment) has lost 25%+ accuracy for technology-sector buyers. Enrichment is not a one-time operation — re-enrich active contacts every 6 months.

## Methodology

### Step 0: Pre-enrichment deduplication
Deduplicate input records before enriching. Deduplication keys: exact email match, LinkedIn URL normalization (strip trailing slashes, lowercase), and company-domain + full-name match. Remove duplicates first, merge intelligently — prefer the record with more non-null fields.

### Step 1: Firmographic layer
Enrich company-level fields using the target domain as key. Required fields: company size (headcount), industry, tech stack, funding stage. Firmographic layer establishes which ICP tier the account belongs to — high/medium/low — before discovering individual contacts. Company data is more stable than contact data and cheaper to enrich.

### Step 2: Contact discovery via waterfall
Search for contacts by role against each target domain. Use a waterfall — Apollo first (strongest for US tech companies), PDL second (global coverage):

Priority role order:
1. Economic buyer (budget authority): VP/Director/Head of [relevant function]
2. Technical buyer (evaluates fit): Engineering Manager, CTO, Architect
3. Champion (day-to-day usage advocate): Manager/Lead of relevant function

### Step 3: Contact-level enrichment
Enrich each discovered contact: direct email, LinkedIn URL, title, seniority, department, years in role. Apollo: 1 credit/email, 8 credits/mobile. PDL: 1 credit/record, rate-limited to 10 req/min per API key — batch accordingly. If PDL cannot find a record, Apollo is the fallback and vice versa.

### Step 4: Email verification (mandatory, non-skippable)
Verify deliverability for every email from enrichment, regardless of enrichment provider's stated confidence. Apollo provides built-in deliverability scores — filter on these. **Allowed for outreach: `valid` only.** Exclude: risky, invalid, catch-all (unless explicitly accepted for campaign), unknown, spamtrap, abuse, do_not_mail.

### Step 5: Signal enrichment
Append job-change and company-level signals using available signal providers (Lusha Signals, Apollo signals). Signals to capture: job change in last 6 months (strongest buying-intent signal), promotion, headcount growth, hiring surge in relevant department, technology stack change.

### Step 6: ICP fit scoring
Calculate a composite 0-100 score from three dimensions:
- **Firmographic fit (40%):** company size match, industry match, tech-stack overlap, funding/growth stage alignment.
- **Role fit (35%):** title match to buyer/champion persona, seniority level, department alignment. Boost for: new-to-role (<6 months) = high intent signal.
- **Signal fit (25%):** recent job change (+heavy weight), hiring surge in relevant department, technology adoption signal.

Score thresholds for routing:
- 70-100: immediate outreach queue
- 40-69: long-cycle nurture sequence
- 0-39: passive monitoring or drop

### Step 7: Routing and export
Write enriched, scored contacts to the artifact. Flag each contact with: verification status, confidence level, routing tier, and signal timestamps. Pass only the immediate-outreach tier to `pipeline-outreach-sequencing`; persist all tiers in the artifact for future use.

For EEA-domiciled contacts: record GDPR lawful basis before routing to outreach. Typically "legitimate_interest" for B2B cold outreach — this requires a documented balancing test outside this skill.

## Anti-Patterns

#### Using Clearbit Without HubSpot
**What it looks like:** `clearbit.person.enrichment.v1` or `clearbit.prospect.search.v1` is called in the enrichment workflow.
**Detection signal:** Tool call returns an authentication error, 404, or deprecation notice.
**Consequence:** Enrichment fails silently or raises an error. Contact list passes through partially enriched without the researcher realizing it.
**Mitigation:** Do not use Clearbit tool calls in this skill. Replace with Apollo (primary) and PDL (secondary). Clearbit was shut down April 30, 2025 for non-HubSpot users.

#### Skipping Email Verification
**What it looks like:** Contact list from enrichment passed directly to outreach sequencing without a verification step.
**Detection signal:** Artifact includes emails with `verification_status` absent, null, or anything other than "valid".
**Consequence:** Bounce rate exceeds Gmail/Yahoo's 2% enforcement threshold, triggering spam filter escalation. Domain reputation damage is not reversible within a campaign cycle.
**Mitigation:** Email verification is a hard gate before routing to outreach. No contact enters a sequence without `email_verification_status: "valid"`.

#### Treating Enrichment as One-Time
**What it looks like:** A contact list enriched >12 months ago is used for a new campaign without re-enrichment.
**Detection signal:** Enrichment timestamps older than 6 months; contact list carried over from a previous campaign artifact.
**Consequence:** Technology contacts decay at 25-40% annually. Outreach hits wrong emails, wrong roles, and wrong companies at scale.
**Mitigation:** Set `re_enrich_by` as a required artifact field (enrichment_date + 6 months). Any campaign using contacts older than this date must re-enrich before sequencing.

## Recording

```
write_artifact(path="/pipeline/{campaign_id}/contacts", data={...})
```

## Available Tools

```
apollo(op="call", args={"method_id": "apollo.people.search.v1", "q_organization_domains": ["company.com"], "person_titles": ["VP Engineering", "CTO"], "per_page": 25})

apollo(op="call", args={"method_id": "apollo.people.enrichment.v1", "id": "person_id"})

pdl(op="call", args={"method_id": "pdl.person.search.v1", "query": {"bool": {"must": [{"term": {"job_company_website": "company.com"}}]}}, "size": 10})

pdl(op="call", args={"method_id": "pdl.person.enrichment.v1", "profile": "linkedin.com/in/username"})
```

Note: Clearbit is deprecated for non-HubSpot environments (shut down April 30, 2025). Do not use Clearbit tool calls in this skill. Use Apollo and PDL as primary and secondary providers.

## Artifact Schema

```json
{
  "contact_enrichment": {
    "type": "object",
    "description": "Enriched, verified, and scored contact set ready for outreach sequencing.",
    "required": ["campaign_id", "enrichment_date", "re_enrich_by", "enrichment_pipeline", "contacts", "routing_summary"],
    "additionalProperties": false,
    "properties": {
      "campaign_id": {"type": "string"},
      "enrichment_date": {"type": "string", "format": "date"},
      "re_enrich_by": {"type": "string", "format": "date", "description": "Default: enrichment_date + 6 months."},
      "enrichment_pipeline": {
        "type": "array",
        "description": "Ordered list of providers used in the waterfall.",
        "items": {
          "type": "object",
          "required": ["provider", "fields_covered"],
          "additionalProperties": false,
          "properties": {
            "provider": {"type": "string"},
            "fields_covered": {"type": "array", "items": {"type": "string"}}
          }
        }
      },
      "contacts": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["full_name", "company_domain", "title", "seniority", "department", "email", "email_verification_status", "linkedin_url", "icp_score", "routing_tier", "confidence", "enrichment_sources"],
          "additionalProperties": false,
          "properties": {
            "full_name": {"type": "string"},
            "company_domain": {"type": "string"},
            "title": {"type": "string"},
            "seniority": {"type": "string", "enum": ["c_suite", "vp", "director", "manager", "senior_ic", "ic"]},
            "department": {"type": "string"},
            "email": {"type": ["string", "null"]},
            "email_verification_status": {
              "type": "string",
              "enum": ["valid", "risky", "invalid", "catch_all", "unknown", "spamtrap", "abuse", "do_not_mail", "unverified"],
              "description": "Only 'valid' may enter outreach sequences."
            },
            "linkedin_url": {"type": ["string", "null"]},
            "phone": {"type": ["string", "null"]},
            "icp_score": {
              "type": "object",
              "required": ["total", "firmographic_fit", "role_fit", "signal_fit"],
              "additionalProperties": false,
              "properties": {
                "total": {"type": "integer", "minimum": 0, "maximum": 100},
                "firmographic_fit": {"type": "integer", "minimum": 0, "maximum": 100},
                "role_fit": {"type": "integer", "minimum": 0, "maximum": 100},
                "signal_fit": {"type": "integer", "minimum": 0, "maximum": 100}
              }
            },
            "signals": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["signal_type", "detected_at"],
                "additionalProperties": false,
                "properties": {
                  "signal_type": {"type": "string", "enum": ["job_change", "promotion", "headcount_growth", "hiring_surge", "tech_adoption", "news_event"]},
                  "detected_at": {"type": "string", "format": "date"},
                  "detail": {"type": "string"}
                }
              }
            },
            "routing_tier": {"type": "string", "enum": ["immediate_outreach", "nurture", "passive_monitor", "excluded"]},
            "exclusion_reason": {"type": ["string", "null"], "description": "If routing_tier is 'excluded': specific reason — e.g. 'email_verification_failed', 'icp_score_below_threshold', 'gdpr_no_lawful_basis'."},
            "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "enrichment_sources": {"type": "array", "items": {"type": "string"}},
            "gdpr_lawful_basis": {"type": ["string", "null"], "description": "For EEA-domiciled contacts: GDPR lawful basis for processing. Typically 'legitimate_interest'. Null for non-EEA contacts."}
          }
        }
      },
      "routing_summary": {
        "type": "object",
        "required": ["total_input", "verified_valid", "immediate_outreach", "nurture", "passive_monitor", "excluded"],
        "additionalProperties": false,
        "properties": {
          "total_input": {"type": "integer", "minimum": 0},
          "verified_valid": {"type": "integer", "minimum": 0},
          "immediate_outreach": {"type": "integer", "minimum": 0},
          "nurture": {"type": "integer", "minimum": 0},
          "passive_monitor": {"type": "integer", "minimum": 0},
          "excluded": {"type": "integer", "minimum": 0},
          "exclusion_reasons": {"type": "object", "description": "Count of excluded contacts by reason.", "additionalProperties": {"type": "integer"}}
        }
      }
    }
  }
}
```
