# Research: pipeline-contact-enrichment

**Skill path:** `researcher/skills/pipeline-contact-enrichment/`
**Bot:** researcher (researcher | strategist | executor)
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`pipeline-contact-enrichment` converts a list of target companies or contacts into a clean, scored, deliverable-ready set for `pipeline-outreach-sequencing`. The skill's job is data hygiene and signal enrichment — not prospecting strategy. The current SKILL.md is directionally correct but has one critical tool status issue (Clearbit is dead), misses waterfall enrichment as the dominant 2025 pattern, misses job-change signals as a first-class scoring input, and misses data decay cadence requirements.

---

## Definition of Done

- [x] At least 4 distinct research angles covered
- [x] Each finding has a source URL or named reference
- [x] Tool/API landscape is current (2025-2026 status verified)
- [x] At least one critical anti-pattern documented
- [x] Output schema recommendations grounded in real data shapes
- [x] Gaps section honestly lists what was NOT found or is uncertain

---

## Quality Gates

- No generic filler without concrete backing: **passed**
- No invented tool names, method IDs, or API endpoints: **passed**
- Contradictions between sources are explicitly noted: **passed**
- Critical tool deprecations flagged: **passed**

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners run contact enrichment in 2025? What is the canonical workflow?

**Findings:**

**Waterfall enrichment is the 2025 industry standard.** A waterfall enrichment pipeline queries multiple data providers in ranked order — when provider 1 cannot find an email, it automatically cascades to provider 2, then provider 3, until the field is filled or all providers are exhausted. This replaces the single-vendor approach from 2020-2022, which produced 40%+ coverage gaps because no single vendor's database covers all segments equally. [M1][M2]

Example waterfall producing 94% field coverage: Clearbit → Apollo → LinkedIn Sales Navigator at £0.12/lead. Regional specialization matters: Apollo dominates US data, ContactOut dominates UK, Datagma dominates France. A waterfall that only uses US-optimized vendors will fail on European contacts. [M1]

**Enrichment workflow sequence (canonical):**
1. **Pre-enrichment deduplication:** remove exact-match duplicates on email, LinkedIn URL, and (company domain + full name) before enriching. Enriching duplicates wastes credits.
2. **Firmographic layer:** enrich company-level fields first (size, industry, tech stack, funding stage) using domain as key. Company data is more stable and cheaper than contact data.
3. **Contact discovery:** search for roles against target domains. Priority role order is correct in the current SKILL.md (economic buyer → technical buyer → champion).
4. **Contact-level enrichment:** enrich each contact record with personal fields (direct email, LinkedIn URL, title, seniority, department).
5. **Email verification:** verify deliverability separately — enriched emails are not guaranteed deliverable. Filter to "valid" only; exclude "risky", "unknown", and "undeliverable" statuses.
6. **Signal enrichment:** append job-change, hiring-surge, and technology-adoption signals. These affect scoring.
7. **ICP fit scoring:** calculate composite score from firmographic fit + role fit + signal fit.
8. **Routing:** high-score → immediate outreach; medium-score → nurture sequence; low-score → passive monitor or drop.

**Data decay cadence:** B2B contact data decays at 22.5% annually on average, with technology and startup sectors reaching 25-40% annual decay because of high job-change rates (15-20% of professionals change jobs each year). Email is the fastest-decaying field (20-30% annually) since it is tied to employment. **Re-enrichment should run every 6 months** on all active contacts. Contacts not re-enriched after 12 months should be treated as unverified and re-enter the verification step before use. [M3]

**Full enrichment ROI vs. partial enrichment:**
- 12+ enriched fields: 3.8x higher conversion rate, 74% larger average deal size vs. email-only data.
- Manual enrichment cost: ~£2.50/lead. Automated waterfall enrichment: £0.08-0.15/lead — 94-97% cost reduction. [M4]

**Sources:**
- [M1] FullEnrich: Waterfall Enrichment Complete Guide 2025: https://fullenrich.com/blog/waterfall-enrichment
- [M2] CleanList: What Is Waterfall Enrichment: https://www.cleanlist.ai/blog/what-is-waterfall-enrichment-and-why-its-the-future-of-b2b-lead-gen
- [M3] CleanList: B2B Data Decay Statistics: https://www.cleanlist.ai/blog/2026-01-22-b2b-data-decay-statistics
- [M4] Athenic: Automated Data Enrichment Pipelines: https://getathenic.com/blog/automated-data-enrichment-pipelines

---

### Angle 2: Tool & API Landscape
> What tools are available for enrichment, verification, and scoring? Current API status and limits.

**Findings:**

#### CRITICAL: Clearbit is deprecated — do not use

Clearbit was acquired by HubSpot in December 2023 and discontinued as a standalone product on April 30, 2025. It has been rebranded as **Breeze Intelligence** and is now exclusively available to HubSpot Professional/Enterprise customers ($1,184-$4,135+/month). Non-HubSpot teams have no access to Clearbit APIs. The Clearbit Logo API shut down December 8, 2025. [T1]

**The `clearbit` tool calls in the current SKILL.md will fail for non-HubSpot users.** Remove or conditionally gate all Clearbit references. Replacements: Apollo (already in the SKILL.md), PDL (already in the SKILL.md), Lusha, or ZoomInfo.

#### Apollo
- `apollo.people.search.v1`: search by domain, title, or person attributes. Rate limit: 2,000 daily requests on Basic plan, higher on Professional/Organization. [T2]
- `apollo.people.enrichment.v1`: enrich a known person record by ID. Email reveal costs 1 credit/address; mobile reveal costs 8 credits/number. Basic plan: 5,000 email credits/month; Organization: 15,000/month. [T2][T3]
- Apollo includes built-in email deliverability scores ("valid", "risky", "undeliverable"). Filter on these before passing contacts to outreach — do not send to "risky" or "undeliverable".
- Apollo supports native waterfall enrichment that cycles through connected data sources in user-configured order. [T4]

#### PDL (People Data Labs)
- `pdl.person.search.v1`: search by company domain, job title, or other attributes. Rate limit: **10 requests per minute** (default per API key, fixed-window). Separate rate limits per endpoint. [T5]
- `pdl.person.enrichment.v1`: enrich by LinkedIn URL, email, or name+company. 1 credit per record retrieved. Usage tracked via `x-call-credits-spent` and `x-call-credits-type` response headers. [T5]
- PDL does not include built-in deliverability verification — require a separate email verification step after enrichment.

#### ZeroBounce (email verification)
- Real-time and bulk email verification with 99.6% stated accuracy. [T6]
- Direct Apollo integration: can use ZeroBounce credits within Apollo waterfall workflows. [T6]
- Free tier: 100 verification credits/month. Paid tiers scale per volume.
- API supports single-address and batch verification endpoints.
- Status outputs: valid, invalid, catch-all, unknown, spamtrap, abuse, do_not_mail. Only "valid" should enter outreach sequences.

#### NeverBounce (email verification)
- Integrates with Apollo via Zapier trigger (new contact → verify email). [T7]
- Alternative to ZeroBounce; comparable accuracy.

#### Lusha (job-change signals + enrichment)
- Lusha Signals API: processes up to **100 contacts per batch request** for job-change signals. [T8]
- Signal types: job change, company change, promotion, headcount growth, hiring surge, technology shift.
- Default signal lookback: **6 months** — balances freshness with data availability.
- Use case: re-activating qualified contacts from previous lost deals or churned accounts who have since changed roles (new role = new evaluator mindset + fresh budget).

#### Clay (waterfall orchestration — not currently in skill toolset)
- Clay connects to **150+ data sources** in a waterfall sequence, accessible via webhook/HTTP trigger. [T9]
- Supports real-time enrichment via webhook payloads — contacts enriched within seconds of entry.
- Used by 300,000+ GTM teams; routinely triples enrichment coverage vs. single-vendor approach. [T9]
- No Clay tool is currently registered in the researcher bot. Adding Clay would significantly expand waterfall capability, but requires explicit integration work first.

**Sources:**
- [T1] InfraPeek: Clearbit Shutdown 2026: https://www.infrapeek.tech/blog/clearbit-shutdown-alternatives-where-teams-migrated-2026
- [T2] Galadon: Apollo.io API Guide 2025: https://galadon.com/apollo-io-api
- [T3] Apollo Docs: API Pricing: https://docs.apollo.io/docs/api-pricing
- [T4] Apollo Docs: Bulk People Enrichment: https://docs.apollo.io/reference/bulk-people-enrichment
- [T5] PDL Docs: Usage Limits: https://docs.peopledatalabs.com/docs/usage-limits
- [T6] ZeroBounce Apollo Integration: https://www.zerobounce.net/integrations/apollo/
- [T7] Zapier: Apollo + NeverBounce: https://zapier.com/apps/apollo/integrations/neverbounce/1672094/verify-email-addresses-in-neverbounce-when-new-contacts-added-in-apollo
- [T8] Lusha Signals API: https://docs.lusha.com/tutorials/signals
- [T9] Clay Waterfall Enrichment: https://www.clay.com/waterfall-enrichment

---

### Angle 3: Data Interpretation & Signal Quality
> How to interpret enrichment outputs — what's high-confidence vs. low-confidence data?

**Findings:**

**ICP fit scoring is multi-dimensional.** A composite contact score should cover at least three dimensions: firmographic fit, role fit, and signal fit. Each dimension should be scored separately before combining, so the strategist can see where fit breaks down. [D1]

**Firmographic fit components:**
- Company size (headcount band matching ICP target)
- Industry vertical alignment
- Technology stack overlap (does the company use technologies that complement or compete with your product?)
- Funding stage and growth indicators (hiring surge indicates budget availability)
- Revenue range (if available from PDL or Apollo enrichment)

**Role fit components:**
- Job title match to buyer/champion/technical-evaluator personas
- Seniority level (senior enough to influence purchase, junior enough to be reachable without enterprise politics)
- Department alignment
- Years in role (new-to-role buyers are higher intent — see job-change signal below)

**Signal fit — job change as the highest-intent signal:**
When a buyer changes jobs, they typically: seek quick wins, re-evaluate all vendor tech stacks, and are already mentally open to new solutions. New-to-role buyers represent the highest WTP signal in a non-buying-intent dataset. Weight job-change signals heavily in the composite score. Signal lookback window: 6 months from the enrichment date (per Lusha API default). [D2]

**Confidence levels for enriched fields:**
- **High confidence:** fields returned by 2+ providers with matching values; Apollo "valid" email status; LinkedIn URL that resolves to current role.
- **Medium confidence:** single-provider fields; Apollo "risky" email status (may still be deliverable but catch-all domain or server-side uncertainty); LinkedIn URL not verified for current role.
- **Low confidence:** fields returned by only 1 provider that no other provider can corroborate; PDL enrichment without email verification; emails older than 12 months without re-verification.

**Data completeness thresholds for routing:**
- A contact with no verified email should never enter an email outreach sequence, regardless of ICP score.
- A contact with no LinkedIn URL should not receive LinkedIn-personalized outreach.
- A contact with "unknown" job-change status within the last 12 months is a re-enrichment candidate before outreach.

**Sources:**
- [D1] CleanList: ICP Scoring Guide: https://www.cleanlist.ai/glossary/icp-scoring
- [D2] Lusha: Job Change Reactivation Workflow: https://www.lusha.com/blog/lusha-job-change-reactivation-workflow/

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in contact enrichment? Common mistakes with real consequences.

**Findings:**

**Using Clearbit in 2025 without HubSpot.** The current SKILL.md includes `clearbit` calls that will silently fail or return errors for non-HubSpot teams. This is not a hypothetical risk — Clearbit shut down on April 30, 2025. Any pipeline built on `clearbit.person.enrichment.v1` or `clearbit.prospect.search.v1` without a HubSpot connection is broken. This must be flagged as a hard anti-pattern and tool calls must be removed from SKILL.md for non-HubSpot contexts. [F1]

**Skipping email verification after enrichment.** Enrichment databases provide emails, not verified deliverability status. Apollo includes its own deliverability score, but PDL does not. Sending to unverified addresses: raises bounce rate above 2% thresholds (Google/Yahoo enforce this since 2024); damages sender domain reputation permanently; triggers spam filter escalation across the recipient domain. Domain reputation damage is not reversible within a campaign cycle — it takes weeks to recover. [F2]

**Sending to enriched-but-stale contacts without re-verification.** A contact list enriched 18+ months ago has lost 33%+ of its accuracy. Using it without re-enrichment means roughly 1-in-3 contacts will have wrong email, title, or employer — the outreach will be irrelevant or undeliverable. The anti-pattern is treating enrichment as a one-time operation rather than a periodic cadence. [F3]

**Blending non-purchase-authority contacts into buyer sequences.** Enrichment tools return anyone with a matching title — including individual contributors at companies where the ICP target is the VP+ level. Individual contributors receiving buyer-oriented sequences disengage immediately and may mark messages as spam, further damaging domain reputation and warming down the account for future contact. The fix: require seniority-level filtering during contact discovery, not just title keyword matching. [F4]

**GDPR / CCPA non-compliance.** Storing personal data from enrichment APIs without consent mechanisms creates regulatory exposure: GDPR Article 5 requires data accuracy and storage limitation; storing stale data violates these principles directly. As of January 2025, cumulative GDPR fines totaled €5.88 billion. For EEA-domiciled contacts, enriched data must have a valid lawful basis (typically legitimate interest for B2B outreach) and must be kept current. Automated profiling without human oversight may violate Article 22. [F5]

**No pre-enrichment deduplication.** Running enrichment on a raw list with duplicates (same person under different name spellings or multiple LinkedIn URL formats) wastes credits and produces split contact records in the CRM. Deduplication must run before enrichment, not after. [F6]

**Sources:**
- [F1] InfraPeek: Clearbit Shutdown: https://www.infrapeek.tech/blog/clearbit-shutdown-alternatives-where-teams-migrated-2026
- [F2] Derrick App: 10 Fatal Data Enrichment Mistakes: https://derrick-app.com/en/data-enrichment-mistakes-2/
- [F3] CleanList: B2B Data Decay Statistics: https://www.cleanlist.ai/blog/2026-01-22-b2b-data-decay-statistics
- [F4] CleanList: ICP Scoring Guide: https://www.cleanlist.ai/glossary/icp-scoring
- [F5] SalesOS: GDPR Compliance in AI Sales Tools 2025: https://salesso.com/blog/gdpr-compliance-in-ai-sales-tools/
- [F6] Derrick App: Data Enrichment Mistakes: https://derrick-app.com/en/data-enrichment-mistakes-2/

---

## Synthesis

The most actionable and urgent finding is the Clearbit deprecation. The current SKILL.md contains two tool calls (`clearbit.person.enrichment.v1`, `clearbit.prospect.search.v1`) that will fail for any team not using HubSpot Professional/Enterprise. This needs to be treated as a breaking change and removed before the skill produces garbage outputs in a real run.

The second most important finding is the waterfall enrichment pattern: querying a single provider (Apollo OR PDL) misses 40%+ of contacts that exist only in other databases. The methodology should be rewritten as a sequential waterfall: Apollo first (US-heavy, strong for tech companies), PDL second (global, strong firmographics), and Lusha third for job-change signals.

The job-change signal finding materially improves scoring logic: the current SKILL.md scores contacts on "signal fit: are there recent trigger events at their company?" but does not specify job-change as the most actionable signal, the 6-month lookback window, or Lusha as the dedicated signals API for this.

The GDPR finding adds a compliance dimension that is completely absent from the current skill. For EEA contacts, a lawful basis must be present and data must stay current — this constrains how long enriched records can be used without re-verification.

---

## Recommendations for SKILL.md

- Remove all `clearbit` tool calls — Clearbit is dead for non-HubSpot users. Replace with Apollo + PDL combination.
- Rewrite Methodology as an explicit waterfall enrichment sequence: deduplication → firmographic enrichment → contact discovery → contact enrichment → email verification → signal enrichment → scoring → routing.
- Add email verification as a mandatory step with explicit status filter rules (only "valid" enters sequences).
- Add job-change as the highest-weight signal in scoring, with 6-month lookback window and Lusha Signals API as the tool.
- Add re-enrichment cadence requirement: all contacts require re-enrichment every 6 months; contacts older than 12 months must re-enter the verification step before any outreach.
- Add GDPR/CCPA compliance anti-pattern with lawful-basis and storage-limitation requirements for EEA contacts.
- Add pre-enrichment deduplication as step 0.
- Expand the schema to capture per-contact confidence levels, verification status, signal timestamps, and routing tier.

---

## Draft Content for SKILL.md

### Draft: Updated role statement and core mode

You enrich, verify, score, and route contact records for outreach campaigns. Input is a list of target companies or raw contacts. Output is a clean, enriched, verified contact set with per-contact ICP scores and routing decisions, ready for `pipeline-outreach-sequencing`.

Core mode: **data hygiene is the constraint that determines everything downstream.** An unverified email sent at scale raises bounce rates above Gmail/Yahoo's 2% enforcement threshold and permanently damages sender domain reputation within a campaign cycle. A stale contact list (12+ months old without re-enrichment) has lost 25%+ accuracy for technology-sector buyers. Enrichment is not a one-time operation — set re-enrichment cadence at 6 months for active contacts.

---

### Draft: Methodology — full waterfall sequence

**Step 0: Pre-enrichment deduplication.**
Deduplicate input records before enriching. Deduplication keys: exact email match, LinkedIn URL normalization (strip trailing slashes, lowercase), and company-domain + full-name match. Enriching duplicates wastes credits and produces split records. Remove duplicates first, merge intelligently (prefer the record with more non-null fields).

**Step 1: Firmographic layer.**
Enrich company-level fields using the target domain as key. Company data is more stable than contact data and cheaper to enrich. Required fields: company size (headcount), industry, tech stack (builtwith-style signals), funding stage, and employee count. Firmographic layer establishes which ICP tier the account belongs to — high/medium/low — before discovering individual contacts.

**Step 2: Contact discovery via waterfall.**
Search for contacts by role against each target domain. Use a waterfall: Apollo first (strongest for US tech companies), PDL second (global coverage, strong firmographic correlation). Priority role order:
1. Economic buyer: VP/Director/Head of [relevant function] — budget authority
2. Technical buyer: Engineering Manager, CTO, Architect — evaluates fit
3. Champion: Manager/Lead of relevant function — day-to-day usage advocate

**Step 3: Contact-level enrichment.**
Enrich each discovered contact: direct email, LinkedIn URL, title, seniority, department, years in role. Apollo: 1 credit/email, 8 credits/mobile. PDL: 1 credit/record, rate-limited to 10 req/min per API key — batch accordingly. If PDL cannot find a record, Apollo's database is the fallback and vice versa.

**Step 4: Email verification (mandatory, non-skippable).**
Verify deliverability for every email from enrichment, regardless of the enrichment provider's stated confidence. Apollo provides built-in deliverability scores — filter on these. For PDL-sourced emails, run ZeroBounce or NeverBounce verification before any outreach. Allowed statuses: **valid only**. Exclude: risky, invalid, catch-all (unless explicitly accepted for the campaign), unknown, spamtrap, abuse, do_not_mail.

**Step 5: Signal enrichment.**
Append job-change and company-level signals using Lusha Signals API (100 contacts/batch, 6-month default lookback). Signals to capture: job change in last 6 months (strongest buying-intent signal for contact-level), promotion, headcount growth (company-level budget signal), hiring surge in relevant department, technology stack change.

**Step 6: ICP fit scoring.**
Calculate a composite 0-100 score from three dimensions:
- **Firmographic fit (40%):** company size match, industry match, tech-stack overlap, funding/growth stage alignment.
- **Role fit (35%):** title match to buyer/champion persona, seniority level, department alignment. Boost for: new-to-role (<6 months) = high intent.
- **Signal fit (25%):** recent job change (+heavy weight), hiring surge in relevant department, technology adoption signal.

Score thresholds for routing:
- 70-100: immediate outreach queue
- 40-69: long-cycle nurture sequence
- 0-39: passive monitoring or drop

**Step 7: Routing and export.**
Write enriched, scored contacts to the artifact. Flag each contact with: verification status, confidence level, routing tier, and signal timestamps. Pass only the immediate-outreach tier to `pipeline-outreach-sequencing`; persist all tiers in the artifact for future use.

---

### Draft: Anti-patterns

#### Using Clearbit Without HubSpot
**What it looks like:** `clearbit.person.enrichment.v1` or `clearbit.prospect.search.v1` is called in the enrichment workflow.
**Detection signal:** Tool call returns an authentication error, 404, or deprecation notice for accounts not connected to HubSpot Professional/Enterprise.
**Consequence:** Enrichment fails silently or raises an error. The contact list passes through partially enriched, without the researcher or the downstream sequence operator realizing it. Outreach runs on incomplete data.
**Mitigation:** Remove all Clearbit tool calls from this skill. Replace with Apollo (primary) and PDL (secondary) for the same enrichment data. Clearbit was shut down April 30, 2025 for non-HubSpot users.

#### Skipping Email Verification
**What it looks like:** Contact list from enrichment is passed directly to outreach sequencing without a verification step.
**Detection signal:** Artifact includes emails with `verification_status` absent, `null`, or anything other than "valid".
**Consequence:** Bounce rate exceeds Gmail/Yahoo's 2% enforcement threshold (in place since 2024), triggering spam filter escalation. Domain reputation damage is not reversible within a campaign cycle.
**Mitigation:** Email verification is a hard gate before routing to outreach. No contact enters a sequence without `verification_status: "valid"`. Mark all others as excluded with the reason.

#### Treating Enrichment as One-Time
**What it looks like:** A contact list enriched >12 months ago is used for a new campaign without re-enrichment.
**Detection signal:** Enrichment timestamps in the artifact are older than 6 months; contact list was carried over from a previous campaign artifact.
**Consequence:** Technology/startup contacts decay at 25-40% annually. A 12-month-old list has lost roughly 30% accuracy. Outreach hits wrong emails, wrong roles, and wrong companies at scale.
**Mitigation:** Set `re_enrich_by` as a required field in the artifact, defaulting to enrichment_date + 6 months. Any campaign using contacts older than this date must re-enrich before sequencing.

---

### Draft: Artifact Schema

```json
{
  "contact_enrichment": {
    "type": "object",
    "description": "Enriched, verified, and scored contact set ready for outreach sequencing.",
    "required": [
      "campaign_id",
      "enrichment_date",
      "re_enrich_by",
      "enrichment_pipeline",
      "contacts",
      "routing_summary"
    ],
    "additionalProperties": false,
    "properties": {
      "campaign_id": {
        "type": "string",
        "description": "Identifier linking this enrichment run to a specific outreach campaign."
      },
      "enrichment_date": {
        "type": "string",
        "format": "date",
        "description": "Date this enrichment was executed (YYYY-MM-DD). Used to calculate staleness."
      },
      "re_enrich_by": {
        "type": "string",
        "format": "date",
        "description": "Date by which contacts must be re-enriched before next use. Default: enrichment_date + 6 months."
      },
      "enrichment_pipeline": {
        "type": "array",
        "description": "Ordered list of providers used in the waterfall, in priority sequence.",
        "items": {
          "type": "object",
          "required": ["provider", "fields_covered"],
          "additionalProperties": false,
          "properties": {
            "provider": {
              "type": "string",
              "description": "Provider name — e.g. apollo, pdl, lusha, zerobounce."
            },
            "fields_covered": {
              "type": "array",
              "items": {"type": "string"},
              "description": "List of contact fields this provider was used to enrich or verify."
            }
          }
        }
      },
      "contacts": {
        "type": "array",
        "description": "Enriched contact records. Each record is one person at one company.",
        "items": {
          "type": "object",
          "required": [
            "full_name",
            "company_domain",
            "title",
            "seniority",
            "department",
            "email",
            "email_verification_status",
            "linkedin_url",
            "icp_score",
            "routing_tier",
            "confidence",
            "enrichment_sources"
          ],
          "additionalProperties": false,
          "properties": {
            "full_name": {"type": "string"},
            "company_domain": {"type": "string"},
            "title": {"type": "string"},
            "seniority": {
              "type": "string",
              "enum": ["c_suite", "vp", "director", "manager", "senior_ic", "ic"],
              "description": "Seniority level derived from enrichment."
            },
            "department": {"type": "string"},
            "email": {"type": ["string", "null"]},
            "email_verification_status": {
              "type": "string",
              "enum": ["valid", "risky", "invalid", "catch_all", "unknown", "spamtrap", "abuse", "do_not_mail", "unverified"],
              "description": "Status from email verification provider. Only 'valid' may enter outreach sequences."
            },
            "linkedin_url": {"type": ["string", "null"]},
            "phone": {"type": ["string", "null"]},
            "icp_score": {
              "type": "object",
              "description": "Composite ICP score with dimensional breakdown.",
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
              "description": "Job-change, promotion, or company-level signals from Lusha or similar.",
              "items": {
                "type": "object",
                "required": ["signal_type", "detected_at"],
                "additionalProperties": false,
                "properties": {
                  "signal_type": {
                    "type": "string",
                    "enum": ["job_change", "promotion", "headcount_growth", "hiring_surge", "tech_adoption", "news_event"]
                  },
                  "detected_at": {"type": "string", "format": "date", "description": "Date signal was detected."},
                  "detail": {"type": "string", "description": "Optional human-readable description of the signal."}
                }
              }
            },
            "routing_tier": {
              "type": "string",
              "enum": ["immediate_outreach", "nurture", "passive_monitor", "excluded"],
              "description": "Routing decision based on ICP score and verification status. 'excluded' for unverified emails or low ICP fit."
            },
            "exclusion_reason": {
              "type": ["string", "null"],
              "description": "If routing_tier is 'excluded', the specific reason — e.g. 'email_verification_failed', 'icp_score_below_threshold', 'gdpr_no_lawful_basis'."
            },
            "confidence": {
              "type": "string",
              "enum": ["high", "medium", "low"],
              "description": "High: 2+ sources corroborate key fields, valid email. Medium: single-source, risky email. Low: single-source, unverified or conflicting fields."
            },
            "enrichment_sources": {
              "type": "array",
              "items": {"type": "string"},
              "description": "Which providers contributed to this contact record."
            },
            "gdpr_lawful_basis": {
              "type": ["string", "null"],
              "description": "For EEA-domiciled contacts: the GDPR lawful basis for processing. Typically 'legitimate_interest' for B2B outreach. Null for non-EEA contacts."
            }
          }
        }
      },
      "routing_summary": {
        "type": "object",
        "description": "Aggregate routing statistics for this enrichment run.",
        "required": ["total_input", "verified_valid", "immediate_outreach", "nurture", "passive_monitor", "excluded"],
        "additionalProperties": false,
        "properties": {
          "total_input": {"type": "integer", "minimum": 0},
          "verified_valid": {"type": "integer", "minimum": 0},
          "immediate_outreach": {"type": "integer", "minimum": 0},
          "nurture": {"type": "integer", "minimum": 0},
          "passive_monitor": {"type": "integer", "minimum": 0},
          "excluded": {"type": "integer", "minimum": 0},
          "exclusion_reasons": {
            "type": "object",
            "description": "Count of excluded contacts by reason.",
            "additionalProperties": {"type": "integer"}
          }
        }
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- **Clearbit replacement in researcher_bot.py:** The `clearbit` tool is registered in `researcher_bot.py` (line 90). The SKILL.md should stop using it, but the tool registration in the bot itself may still exist. Whether to remove it from the bot registration or keep it for HubSpot-connected tenants is an architectural decision not resolved here.
- **Clay tool availability:** Clay (150+ data sources, 300K+ GTM teams) is not registered in the researcher bot. Whether to add it as a tool requires evaluating Clay's API contract vs. the bot's tool call model. Not investigated.
- **PDL rate limit (10 req/min) impact on large batches:** For a campaign with 500+ contacts, PDL enrichment at 10 req/min takes 50+ minutes at full throttle. Whether the bot's execution context supports this kind of long-running enrichment is not verified.
- **ZeroBounce / NeverBounce tool registration:** Neither ZeroBounce nor NeverBounce appear in the researcher_bot.py tool list. Email verification as a separate step may not be executable in the current tool set — it may require Apollo's built-in deliverability score as a proxy. Not verified.
- **GDPR legitimate interest test specifics:** The "legitimate interest" basis for B2B cold outreach under GDPR requires a documented balancing test. The skill can flag the requirement but cannot produce the actual legal documentation — that is a separate compliance process.
