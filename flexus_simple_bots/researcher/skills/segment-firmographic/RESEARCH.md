# Research: segment-firmographic

**Skill path:** `flexus-client-kit/flexus_simple_bots/researcher/skills/segment-firmographic/`  
**Bot:** researcher  
**Research date:** 2026-03-05  
**Status:** complete

---

## Context

`segment-firmographic` is the researcher skill that enriches and profiles target accounts by firmographic and technographic attributes: company identity, industry classification, size, funding context, geography, and stack signals.

The current `SKILL.md` is directionally solid but too optimistic about data consistency. 2024-2026 evidence shows that enrichment quality is constrained by refresh cadence differences, source coverage asymmetry, identity ambiguity, and compliance risk if data provenance and purpose boundaries are weak.

This document follows the standard research template and includes:
- a concise implementation brief,
- source-backed findings across five angles,
- a large paste-ready `Draft Content for SKILL.md` section.

This version synthesizes five internal research tracks requested for this run:
1. methodology,
2. tools landscape,
3. API endpoint verification,
4. interpretation quality,
5. anti-patterns/failure modes.

---

## Definition of Done

Research is complete when ALL of the following are satisfied:

- [x] At least 4 distinct research angles are covered (5 included)
- [x] Each finding has source URLs or named references
- [x] Methodology section is practical and operational
- [x] Tool/API landscape includes concrete provider capabilities and constraints
- [x] At least one failure-mode / anti-pattern section is included
- [x] Output schema recommendations are grounded in observed data shapes
- [x] Gaps and uncertainties are explicitly listed
- [x] Findings prioritize 2024-2026 evidence; evergreen docs are marked
- [x] No invented provider endpoints are presented as facts

---

## Quality Gates

Before marking status `complete`, verify:

- No generic filler without source-backed operational implication: **passed**
- No invented API endpoints or provider capabilities: **passed**
- Official-doc ambiguities are labeled (not hidden): **passed**
- Contradictions between sources are explicit: **passed**
- `Draft Content for SKILL.md` is the largest section and paste-ready: **passed**

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How should firmographic segmentation and enrichment actually be run in 2024-2026, with quality and operational reliability?

**Findings:**

1. Firmographic enrichment should be treated as a **data quality system**, not a one-time append job. 2024 CRM data research ties low quality directly to revenue risk and operational drag, supporting explicit quality ownership, freshness policies, and recurring governance review.

2. Refresh strategy must be **field-aware**, not record-aware. Role and employment attributes decay faster than legal-entity attributes; labor churn data supports short refresh cycles for contact/role-relevant fields.

3. Monthly automated refresh plus controlled overwrite policy is now a practical baseline in modern CRM tooling. HubSpot explicitly separates automatic enrichment, continuous monthly refresh, and manual overwrite behavior.

4. Identity matching should be judged via **precision/recall/F1 on truth sets**, not by match-volume alone. AWS guidance and 2024 benchmark evidence reinforce that high match count is not equivalent to high match quality.

5. Provider confidence scales are real but **not cross-provider comparable**. PDL documents `likelihood` and threshold controls (`min_likelihood`) that can be used for provider-specific gating.

6. Missing values are expected even in high-quality enrichment pipelines. PDL explicitly returns `null` for unavailable fields; interpretation should classify these as `unknown`, not `false`.

7. Staleness handling should use explicit lag bands and max-age rules, not ad hoc judgment. OpenCorporates’ freshness model (including amber/red/offline concepts) is a practical template for field staleness policy design.

8. Taxonomy normalization is required before segmentation scoring. Industry labels should be mapped to a canonical taxonomy (for example NAICS), and size criteria should be context-aware rather than generic SMB/MM/ENT labels.

9. Multi-source triangulation is helpful but must include precedence rules. Vendor update cadences differ materially (monthly, quarterly, or near-real-time variants), so provider precedence should be field-specific.

10. A strong monthly operating loop for this skill is: ingest -> normalize -> triangulate -> score quality -> flag conflicts -> publish with confidence grade.

**Sources:**
- https://www.validity.com/wp-content/uploads/2024/05/The-State-of-CRM-Data-Management-in-2024.pdf (2024)
- https://knowledge.hubspot.com/records/get-started-with-data-enrichment (updated 2026)
- https://aws.amazon.com/blogs/industries/measuring-the-accuracy-of-rule-or-ml-based-matching-in-aws-entity-resolution/ (2024)
- https://docs.peopledatalabs.com/docs/reference-company-enrichment-api
- https://docs.peopledatalabs.com/docs/input-parameters-company-enrichment-api#min_likelihood
- https://docs.peopledatalabs.com/docs/output-response-company-enrichment-api
- https://docs.peopledatalabs.com/docs/company-schema
- https://blog.opencorporates.com/2025/03/05/how-to-check-data-coverage-in-opencorporates/ (2025)
- https://knowledge.opencorporates.com/knowledge-base/current-status-explained/
- https://knowledge.opencorporates.com/knowledge-base/delivery-latency-explained/
- https://www.census.gov/naics/ (Evergreen)
- https://www.federalregister.gov/documents/2024/09/12/2024-20228/small-business-size-standards-revised-size-standards-methodology (2024)
- https://www.bls.gov/news.release/archives/jolts_12032024.htm (2024)
- https://economicgraph.linkedin.com/content/dam/me/economicgraph/en-us/PDF/us-labor-market-churn-macro.pdf (2024)

---

### Angle 2: Tool & API Landscape (Verified Endpoints Only)
> What provider APIs are actually verifiable and operationally relevant for this skill?

**Findings:**

- This domain has heterogeneous API styles: query-string GET endpoints, REST entity/search APIs, and bulk async patterns.
- Provider limits are materially different and must influence orchestration (RPM ceilings, per-second caps, plan gating, credit models).
- A strict distinction is needed between:
  - **Connector method IDs** in `SKILL.md` (integration surface),
  - **Provider endpoints** (official external API surface).

| Provider | Verified endpoint examples (official docs) | Auth model | Limits / caveats |
|---|---|---|---|
| People Data Labs | `GET https://api.peopledatalabs.com/v5/company/enrich` ; `POST https://api.peopledatalabs.com/v5/company/enrich/bulk` ; company search APIs under `/v5/company/search` | `X-Api-Key` or query key | Free vs paid rate limit gap is large; per-match billing |
| Apollo | `GET https://api.apollo.io/api/v1/organizations/enrich` ; `POST https://api.apollo.io/api/v1/organizations/bulk_enrich` | Bearer (recommended) or API key | Fixed-window limits; plan-dependent; bulk endpoint has stricter per-minute behavior |
| Crunchbase | `GET .../api/v4/entities/organizations/{entity_id}` ; `POST .../api/v4/searches/organizations` | API key via header or query | 200 calls/min noted in docs; base path has migration nuance (`/data/`) |
| BuiltWith | `GET https://api.builtwith.com/v22/api.json?...` ; `POST /v22/domain/bulk` and job/result retrieval | API key in query | 8 concurrent + 10 req/sec documented; signature/detection uncertainty caveats |
| Wappalyzer | `GET https://api.wappalyzer.com/v2/lookup/` ; `GET /v2/credits/balance/` | `x-api-key` | 5 req/sec, up to 10 URLs/request; async crawl mode with callback behavior |
| ZoomInfo | `POST /data/v1/companies/enrich` (documented in OpenAPI) | API auth + account entitlements | credit model, output field gating by plan/access |
| HubSpot Breeze Intelligence | Product/KB capabilities verified; **public enrichment endpoint pattern not documented in retrieved official KB** | HubSpot account permissions/credits | Treat direct endpoint assumptions as unverified unless explicitly documented |
| Clearbit | Dashboard docs are not reliably accessible in this run for endpoint verification | historically key-based APIs | Treat endpoint claims as unverified unless doc is directly verified |

**Important contradiction to encode in skill logic:**

Crunchbase official materials show both:
- `https://api.crunchbase.com/api/v4/...`
- and migration guidance requiring `/v4/data/...` for new keys.

The skill should therefore avoid hardcoding one base path narrative without key/version context.

**Sources:**
- https://docs.peopledatalabs.com/docs/reference-company-enrichment-api
- https://docs.peopledatalabs.com/docs/bulk-company-enrichment-api
- https://docs.peopledatalabs.com/docs/reference-company-search-api
- https://docs.apollo.io/reference/organization-enrichment
- https://docs.apollo.io/reference/bulk-organization-enrichment
- https://docs.apollo.io/reference/rate-limits
- https://docs.apollo.io/reference/view-api-usage-stats
- https://data.crunchbase.com/docs/using-the-api
- https://data.crunchbase.com/docs/calling-api-endpoints
- https://api.builtwith.com/domain-api
- https://builtwith.com/terms
- https://www.wappalyzer.com/docs/api/v2/lookup
- https://www.wappalyzer.com/docs/api/v2/basics/
- https://docs.zoominfo.com/reference/enrichinterface_enrichcompany
- https://docs.zoominfo.com/docs/credit-usage-and-limits
- https://knowledge.hubspot.com/records/get-started-with-data-enrichment
- https://developers.hubspot.com/ai-tools
- https://dashboard.clearbit.com/docs (access/verification limited in this run)

---

### Angle 3: Data Interpretation & Signal Quality
> How should firmographic outputs be interpreted, scored, and bounded?

**Findings:**

1. There is no universal public threshold for "good enrichment." Quality is context-specific and should be evaluated against truth data and expected decision risk.

2. 2024 benchmarking guidance emphasizes evaluation against precision/recall/F1; match success rate alone can hide false-positive linkage.

3. BPID (EMNLP Industry 2024) reports non-trivial ambiguity in profile matching and a best benchmark F1 under perfect conditions that is materially below 1.0, reinforcing realistic confidence expectations.

4. Confidence scores must be interpreted provider-locally:
   - PDL `likelihood` score (1-10) supports explicit thresholding,
   - Other systems may expose different or non-comparable scoring semantics.

5. Missingness is structural, not exceptional. `null` should map to `unknown` and trigger completeness penalties, not negative assertions.

6. Freshness and coverage must be split:
   - a field can be present but stale,
   - a field can be fresh but low-confidence.

7. Bias risk is real in broker/profile datasets. 2024 evidence indicates coverage/accuracy disparities by socioeconomic profile in consumer-broker contexts; B2B teams should still perform fairness diagnostics where possible.

8. High-quality registry systems (for example LEI quality reporting) demonstrate robust quality frameworks, but those scores are not directly transferable to commercial prospect data.

9. Recommended interpretation contract for this skill:
   - score coverage, freshness, consistency separately,
   - compute overall confidence from those dimensions,
   - downgrade output tier when contradictions are unresolved.

**Sources:**
- https://aws.amazon.com/blogs/industries/measuring-the-accuracy-of-rule-or-ml-based-matching-in-aws-entity-resolution/ (2024)
- https://docs.aws.amazon.com/entityresolution/latest/userguide/what-is-service.html
- https://docs.aws.amazon.com/entityresolution/latest/userguide/glossary.html
- https://aclanthology.org/2024.emnlp-industry.40.pdf (2024)
- https://docs.peopledatalabs.com/docs/output-response-company-enrichment-api
- https://docs.peopledatalabs.com/docs/input-parameters-company-enrichment-api#min_likelihood
- https://docs.peopledatalabs.com/docs/company-data-overview
- https://blog.opencorporates.com/2025/03/05/how-to-check-data-coverage-in-opencorporates/ (2025)
- https://www.ccs.neu.edu/home/amislove/publications/Deserts-ManageSci24.pdf (2024)
- https://www.gleif.org/lei-data/gleif-data-quality-management/quality-reports/download-data-quality-report-january-2026/2026-02-06-lei-data-quality-report-january-2026.pdf (2026)

---

### Angle 4: Failure Modes & Anti-Patterns
> What repeatedly goes wrong in firmographic enrichment practice?

**Findings:**

1. **Lead-centric scoring in committee-led buying:** one-contact qualification is treated as account readiness, causing stage stalls in multi-stakeholder deals.

2. **Deck-only segmentation:** segmentation strategy exists in slides but is not encoded in CRM automation/routing/scoring.

3. **Stale data optimism:** annual or ad hoc refresh policy is used despite continuous labor movement and title churn.

4. **Null-as-false logic:** missing values are interpreted as negative signals instead of unknowns.

5. **One-provider truth assumption:** teams treat one dataset as authoritative and skip contradiction handling.

6. **Over-collection without purpose:** enrichment fields are collected because available, not because tied to a defined processing purpose.

7. **Weak lawful-basis documentation:** direct marketing/profiling is run on generic legal basis assumptions without formal necessity/balancing records.

8. **Broker ingestion without provenance controls:** purchased records are loaded without source lineage, rights handling, or suppression propagation plan.

9. **Sensitive-location/attribute misuse:** audience construction uses or depends on sensitive-location derived signals, creating severe enforcement risk.

10. **Retention creep:** profile retention windows are undefined or auto-extended indefinitely.

11. **Outbound compliance blind spots:** enrichment-enabled outreach ignores deliverability and consent regime updates.

12. **Deletion-right breakage in vendor chains:** records deleted in one system reappear on next vendor sync.

**Sources:**
- https://www.forrester.com/press-newsroom/forrester-the-state-of-business-buying-2024/ (2024)
- https://www.bain.com/about/media-center/press-releases/20252/70-of-companies-struggle-to-integrate-their-sales-plays-into-crm-and-revenue-technologies-finds-bain--company-survey/ (2025)
- https://www.validity.com/wp-content/uploads/2024/05/The-State-of-CRM-Data-Management-in-2024.pdf (2024)
- https://www.bls.gov/news.release/archives/jolts_12032024.htm (2024)
- https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/direct-marketing-guidance/collect-information-and-generate-leads/
- https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/purpose-limitation/
- https://www.edpb.europa.eu/system/files/2024-10/edpb_guidelines_202401_legitimateinterest_en.pdf (2024)
- https://www.ftc.gov/news-events/news/press-releases/2024/04/ftc-finalizes-order-x-mode-successor-outlogic-prohibiting-it-sharing-or-selling-sensitive-location (2024)
- https://www.ftc.gov/news-events/news/press-releases/2024/05/ftc-finalizes-order-inmarket-prohibiting-it-selling-or-sharing-precise-location-data (2024)
- https://www.ftc.gov/news-events/news/press-releases/2025/01/ftc-finalizes-order-banning-mobilewalla-selling-sensitive-location-data (2025)
- https://privacy.ca.gov/2024/10/cppas-enforcement-division-to-review-data-broker-compliance-with-the-delete-act/ (2024)
- https://privacy.ca.gov/drop/how-drop-works/
- https://docs.fcc.gov/public/attachments/FCC-24-24A1.pdf (2024)
- https://support.google.com/a/answer/81126
- https://support.google.com/a/answer/14229414
- https://senders.yahooinc.com/best-practices/
- https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

---

### Angle 5+: Governance, Consent, and Regulatory Drift
> What changed in 2024-2026 that should affect how this skill is written?

**Findings:**

- Data broker and sensitive-location enforcement intensified in 2024-2026, including explicit restrictions on sale/use of sensitive location data.
- Legitimate-interest usage in profiling/direct marketing requires explicit three-part analysis (interest, necessity, balancing), not generic invocation.
- Data minimization and purpose limitation are now practical controls for enrichment scope, not legal footnotes.
- Deletion/right propagation and suppression hygiene became harder requirements with broker-focused state enforcement.
- Outreach workflows must align with updated sender, consent, and unsubscribe expectations to avoid downstream deliverability and regulatory failures.

**Sources:**
- https://www.edpb.europa.eu/system/files/2024-10/edpb_guidelines_202401_legitimateinterest_en.pdf (2024)
- https://commission.europa.eu/law/law-topic/data-protection/reform/rules-business-and-organisations/principles-gdpr/how-much-data-can-be-collected_en
- https://www.ftc.gov/news-events/news/press-releases/2024/04/ftc-finalizes-order-x-mode-successor-outlogic-prohibiting-it-sharing-or-selling-sensitive-location
- https://www.ftc.gov/news-events/news/press-releases/2025/01/ftc-finalizes-order-banning-mobilewalla-selling-sensitive-location-data
- https://privacy.ca.gov/2024/10/cppas-enforcement-division-to-review-data-broker-compliance-with-the-delete-act/
- https://docs.fcc.gov/public/attachments/FCC-24-24A1.pdf
- https://support.google.com/a/answer/81126

---

## Synthesis

The most important cross-angle conclusion is that `segment-firmographic` should operate as an evidence-governed enrichment system, not a convenience wrapper around data providers.

Three system-level upgrades matter most:

1. **Quality explicitness**  
   Every critical attribute should carry source provenance, freshness metadata, and confidence.

2. **Provider realism**  
   Endpoint behavior, plan limits, and cadence differences must be encoded as first-class operating rules.

3. **Governance by design**  
   Purpose limitation, lawful basis, suppression, and retention rules must be embedded in workflow and schema.

Contradictions in available sources are mostly operational, not conceptual:
- multi-provider triangulation improves robustness but increases complexity,
- high enrichment volume can still yield low confidence without quality gates,
- high-profile enforcement risk increasingly sits in data-use behavior, not just collection mechanics.

---

## Recommendations for SKILL.md

> Concrete updates that should be made to `segment-firmographic/SKILL.md`.

- [x] Add a strict evidence contract: source, freshness, confidence per critical field.
- [x] Add provider precedence and contradiction-resolution policy.
- [x] Add quality scoring dimensions (`coverage`, `freshness`, `consistency`) and output confidence grade.
- [x] Add staleness handling rules with field-level windows and stale-field flags.
- [x] Add explicit method discovery (`op="help"`) before unknown connector calls.
- [x] Keep connector method IDs as integration surface, but include verified provider endpoint map for audit.
- [x] Add anti-pattern warning blocks with detection and mitigation.
- [x] Add governance and lawful-use requirements (purpose limitation, suppression, retention).
- [x] Expand schema with provenance, confidence, conflicts, and limitations.
- [x] Add output checklist that blocks high-confidence publication on unresolved hard failures.

---

## Draft Content for SKILL.md

> Paste-ready text for a future edit of `segment-firmographic/SKILL.md`.  
> This section is intentionally the largest section in this research file.

### Draft: Replace top-level operating contract

---
You enrich and profile target company segments using firmographic and technographic data from multiple providers.

You run one segment scope per execution.

Your core operating rule is: **do not publish high-confidence profile outputs without explicit field-level evidence quality.**

Every critical attribute must include:
- `source_provider`,
- `captured_at`,
- `freshness_status`,
- `confidence`.

If a field is unavailable, store it as unknown and include it in missingness diagnostics. Do not infer or silently impute core firmographic values.

Result-state policy:
- `ok`: quality gates pass, no unresolved high-impact conflicts.
- `ok_with_conflicts`: usable output with unresolved contradictions.
- `insufficient_data`: not enough quality evidence to support profiling.
- `technical_failure`: provider/tooling failure prevented run completion.
---

### Draft: Methodology replacement text

---
## Methodology

Use this exact sequence for each run:

### Step 0: Scope lock

Define and store:
- `segment_id`,
- target geography,
- segment inclusion rules,
- time window for this profiling pass.

If scope is ambiguous, stop and request clarification.

### Step 1: Build canonical company identity list

For each company candidate, establish canonical identity:
- normalized domain,
- legal/trade name,
- canonical company ID used in artifact.

Use at least two providers when possible for identity confirmation.

### Step 2: Collect core firmographics

Collect these core attributes:
- industry classification,
- headcount or employee range,
- revenue range or proxy,
- HQ country/region,
- funding stage and total funding (if available).

For each attribute, retain source + timestamp + confidence.

### Step 3: Collect technographics

Collect technology stack evidence using web-detection providers.
Record:
- detected technologies,
- detection recency,
- caveats (for example, non-web-detectable tools may be missing).

### Step 4: Cross-provider triangulation

When multiple providers disagree:
1. record both values,
2. apply provider precedence policy by field type,
3. lower confidence when unresolved.

Do not silently overwrite contradictory values.

### Step 5: Freshness and completeness scoring

Compute quality dimensions:
- `coverage_score` (required fields present),
- `freshness_score` (critical fields within acceptable age),
- `consistency_score` (cross-provider agreement),
- `overall_confidence` (derived from the three dimensions).

### Step 6: Governance checks

Before publishing:
- confirm purpose alignment for stored fields,
- ensure no disallowed sensitive inferences,
- ensure suppression/deletion controls are respected for downstream use.

### Step 7: Final classification and recording

Assign result state:
- `ok`,
- `ok_with_conflicts`,
- `insufficient_data`,
- `technical_failure`.

Then write one artifact for the run.

### Step 8: Required run notes

Always include:
- unresolved conflicts,
- stale critical fields,
- provider failures,
- next refresh recommendation.
---

### Draft: Field quality and confidence policy

---
## Data Quality Policy

Do not treat quality as binary. Score each company profile on:

1. **Coverage score** (`0-1`)  
   Share of required fields present.

2. **Freshness score** (`0-1`)  
   Share of critical fields updated within allowed windows.

3. **Consistency score** (`0-1`)  
   Degree of agreement across available providers.

4. **Overall confidence** (`0-1`)  
   Weighted composite of coverage, freshness, and consistency.

Suggested default weights:
- coverage: `0.35`
- freshness: `0.35`
- consistency: `0.30`

Confidence grades:
- `high`: `>=0.80`
- `medium`: `0.60-0.79`
- `low`: `<0.60`

Hard downgrade rules:
- if less than 2 provider families are available for core fields, cap at `medium`,
- if unresolved high-impact conflicts remain, cap at `medium`,
- if >30% of required fields are unknown, cap at `low`.

Missingness rules:
- `null` means unknown, not false,
- unknown core fields must be listed in `missing_fields`,
- unknown core fields reduce coverage and confidence.

Staleness policy (default; override with rationale):
- highly volatile fields (employee count/contact-linked context): warn after 90 days, stale after 180 days,
- medium volatility fields (funding/news-linked fields): warn after 120 days, stale after 240 days,
- low volatility fields (legal entity basics): warn after 180 days, stale after 365 days.
---

### Draft: Provider precedence and conflict handling

---
## Provider Precedence and Conflict Handling

Define precedence per field group:

- **Identity + legal basics**: providers with strongest deterministic identifiers first.
- **Funding fields**: funding-specialist data prioritized over generic enrichment.
- **Technographic fields**: detection providers first, but include detection caveats.
- **Headcount/revenue estimates**: treat as ranges; never present as precise facts.

Conflict protocol:
1. keep all observed values in evidence log,
2. choose displayed value by precedence policy,
3. add `conflict` entry when disagreement exceeds tolerance,
4. lower confidence for unresolved conflicts.

Never delete conflict evidence from artifact output.
---

### Draft: Available tools (connector + verification policy)

---
## Available Tools

Use connector methods from this environment, but verify unknown methods first.

### Step A: Discover connector methods before unfamiliar calls

```python
clearbit(op="help", args={})
pdl(op="help", args={})
apollo(op="help", args={})
crunchbase(op="help", args={})
builtwith(op="help", args={})
wappalyzer(op="help", args={})
```

If a method is not listed in connector help output, do not call it.

### Step B: Core calls

```python
clearbit(op="call", args={"method_id": "clearbit.company.enrich.v1", "domain": "company.com"})

clearbit(op="call", args={"method_id": "clearbit.company.search.v1", "name": "Company Name", "limit": 5})

pdl(op="call", args={"method_id": "pdl.company.enrichment.v1", "website": "company.com", "pretty": true})

pdl(op="call", args={"method_id": "pdl.company.bulk.v1", "requests": [{"params": {"website": "company.com"}}]})

apollo(op="call", args={"method_id": "apollo.organizations.search.v1", "q_organization_name": "Company Name"})

apollo(op="call", args={"method_id": "apollo.people.search.v1", "q_organization_domains": ["company.com"], "person_titles": ["CTO", "VP Engineering"]})

crunchbase(op="call", args={"method_id": "crunchbase.entities.organizations.get.v1", "entity_id": "company-name"})

crunchbase(op="call", args={"method_id": "crunchbase.searches.organizations.post.v1", "field_ids": ["name", "funding_total", "last_funding_at"], "query": [{"field_id": "facet_ids", "operator_id": "includes", "values": ["company"]}]})

builtwith(op="call", args={"method_id": "builtwith.lookup.v1", "LOOKUP": "company.com"})

wappalyzer(op="call", args={"method_id": "wappalyzer.lookup.v1", "urls": ["https://company.com"]})
```

### Step C: Official endpoint verification map (reference only)

These are provider docs references for auditability. They are not a replacement for connector method IDs.

- PDL company enrich: `GET https://api.peopledatalabs.com/v5/company/enrich`
- PDL company bulk enrich: `POST https://api.peopledatalabs.com/v5/company/enrich/bulk`
- Apollo org enrich: `GET https://api.apollo.io/api/v1/organizations/enrich`
- Apollo org bulk enrich: `POST https://api.apollo.io/api/v1/organizations/bulk_enrich`
- Crunchbase entity lookup: `GET .../api/v4/entities/organizations/{entity_id}` (path variant can include `/v4/data/` based on key migration context)
- Crunchbase search orgs: `POST .../api/v4/searches/organizations`
- BuiltWith domain lookup: `GET https://api.builtwith.com/v22/api.json?...`
- BuiltWith bulk domain: `POST https://api.builtwith.com/v22/domain/bulk?...`
- Wappalyzer lookup: `GET https://api.wappalyzer.com/v2/lookup/`
- Wappalyzer credits: `GET https://api.wappalyzer.com/v2/credits/balance/`
- ZoomInfo companies enrich: `POST /data/v1/companies/enrich` (documented in ZoomInfo OpenAPI docs)

### Unverified / ambiguous items policy

- If endpoint docs are inaccessible or ambiguous (for example Clearbit/Breeze public endpoint patterns in this run), mark as `unverified` and do not claim exact endpoint paths as facts.
- Do not invent endpoint names or URL patterns.
---

### Draft: Anti-pattern warning blocks

```md
> [!WARNING] Anti-pattern: One-Provider Truth
> **What it looks like:** a single enrichment source is treated as authoritative for all fields.
> **Detection signal:** no contradiction records despite multi-source calls.
> **Consequence:** hidden errors and overconfident ICP targeting.
> **Mitigation:** require triangulation for core fields and log conflicts explicitly.
```

```md
> [!WARNING] Anti-pattern: Null-as-Negative
> **What it looks like:** `null` values are interpreted as "does not exist."
> **Detection signal:** unknown fields silently converted into negative scoring.
> **Consequence:** false disqualification and segment bias.
> **Mitigation:** classify null as unknown and apply completeness penalties instead.
```

```md
> [!WARNING] Anti-pattern: Stale-Data Certainty
> **What it looks like:** old firmographic fields are treated as current truth.
> **Detection signal:** no `as_of` / `last_verified` metadata on critical fields.
> **Consequence:** routing to wrong personas and wasted outreach.
> **Mitigation:** enforce field-level freshness status and stale-field flags.
```

```md
> [!WARNING] Anti-pattern: Deck-Only Segmentation
> **What it looks like:** ICP tiers exist in strategy docs but not CRM workflows.
> **Detection signal:** high manual override rate and inconsistent qualification outcomes.
> **Consequence:** strategy-execution gap and low ROI from enrichment spend.
> **Mitigation:** encode segment tiers into workflow rules, ownership, and audit logs.
```

```md
> [!WARNING] Anti-pattern: Purpose Creep
> **What it looks like:** enrichment data collected for one purpose is reused broadly without compatibility checks.
> **Detection signal:** missing lawful-basis and purpose-mapping records.
> **Consequence:** compliance risk and potential enforcement exposure.
> **Mitigation:** enforce purpose limitation and maintain auditable processing purpose metadata.
```

```md
> [!WARNING] Anti-pattern: Broker Blind Ingestion
> **What it looks like:** purchased data is imported without provenance or rights controls.
> **Detection signal:** missing lineage, opt-out provenance, and suppression sync fields.
> **Consequence:** recurring deletion-right failures and complaint escalation.
> **Mitigation:** gate ingestion on provenance checklist + suppression propagation checks.
```

```md
> [!WARNING] Anti-pattern: Sensitive-Signal Segmentation
> **What it looks like:** segmentation uses sensitive-location or equivalent high-risk inferred attributes.
> **Detection signal:** segment definitions include sensitive place-derived cohorts.
> **Consequence:** severe regulatory and reputational risk.
> **Mitigation:** maintain hard denylist and compliance review for risky attributes.
```

```md
> [!WARNING] Anti-pattern: Compliance-Unsafe Outbound Activation
> **What it looks like:** enriched lists activated without sender/auth/consent hygiene.
> **Detection signal:** no one-click unsubscribe, poor sender auth, weak consent mapping.
> **Consequence:** deliverability failures and legal exposure.
> **Mitigation:** apply outbound preflight checks before activation.
```

### Draft: Recording guidance

---
## Recording

After quality and governance checks, write one artifact per run:

```python
write_artifact(
  artifact_type="segment_firmographic_profile",
  path="/segments/{segment_id}/firmographic",
  data={...}
)
```

Before `write_artifact`, verify:
1. all core fields include source and freshness metadata,
2. unresolved conflicts are recorded,
3. confidence grade matches quality dimensions,
4. stale and missing fields are explicit,
5. limitations and next refresh actions are concrete.
---

### Draft: Output checklist block

---
Before marking run output as high confidence:

- [ ] At least two provider families contributed to core firmographics (unless impossible and documented)
- [ ] Core fields include source and `captured_at`
- [ ] Missing fields are tracked as unknown, not inferred
- [ ] Stale fields are flagged
- [ ] Contradictions are logged
- [ ] Governance checks passed
- [ ] Confidence score and grade are consistent

If any hard requirement fails, downgrade confidence or mark `insufficient_data`.
---

### Draft: Artifact schema replacement

```json
{
  "segment_firmographic_profile": {
    "type": "object",
    "required": [
      "segment_id",
      "profiled_at",
      "result_state",
      "run_meta",
      "companies",
      "quality_summary",
      "limitations"
    ],
    "additionalProperties": false,
    "properties": {
      "segment_id": {
        "type": "string"
      },
      "profiled_at": {
        "type": "string",
        "description": "ISO-8601 timestamp when profiling completed."
      },
      "result_state": {
        "type": "string",
        "enum": [
          "ok",
          "ok_with_conflicts",
          "insufficient_data",
          "technical_failure"
        ]
      },
      "run_meta": {
        "type": "object",
        "required": [
          "geo_scope",
          "time_window",
          "providers_attempted",
          "provider_failures",
          "evidence_classes"
        ],
        "additionalProperties": false,
        "properties": {
          "geo_scope": {
            "type": "string"
          },
          "time_window": {
            "type": "object",
            "required": [
              "start_date",
              "end_date"
            ],
            "additionalProperties": false,
            "properties": {
              "start_date": {"type": "string"},
              "end_date": {"type": "string"}
            }
          },
          "providers_attempted": {
            "type": "array",
            "items": {"type": "string"}
          },
          "provider_failures": {
            "type": "array",
            "items": {
              "type": "object",
              "required": [
                "provider",
                "reason"
              ],
              "additionalProperties": false,
              "properties": {
                "provider": {"type": "string"},
                "reason": {"type": "string"}
              }
            }
          },
          "evidence_classes": {
            "type": "array",
            "description": "Used evidence classes in this run.",
            "items": {
              "type": "string",
              "enum": [
                "direct",
                "modeled",
                "detected",
                "registry"
              ]
            }
          }
        }
      },
      "companies": {
        "type": "array",
        "items": {
          "type": "object",
          "required": [
            "company_id",
            "domain",
            "name",
            "firmographic",
            "technographic",
            "data_quality",
            "evidence"
          ],
          "additionalProperties": false,
          "properties": {
            "company_id": {
              "type": "string"
            },
            "domain": {
              "type": "string"
            },
            "name": {
              "type": "string"
            },
            "firmographic": {
              "type": "object",
              "required": [
                "industry",
                "headcount",
                "revenue_range",
                "hq_country",
                "funding_stage",
                "total_funding_usd"
              ],
              "additionalProperties": false,
              "properties": {
                "industry": {
                  "type": "object",
                  "required": [
                    "value",
                    "source_provider",
                    "captured_at",
                    "confidence"
                  ],
                  "additionalProperties": false,
                  "properties": {
                    "value": {"type": "string"},
                    "normalized_taxonomy": {"type": "string"},
                    "source_provider": {"type": "string"},
                    "source_ref": {"type": "string"},
                    "captured_at": {"type": "string"},
                    "freshness_status": {
                      "type": "string",
                      "enum": ["fresh", "warning", "stale", "unknown"]
                    },
                    "confidence": {
                      "type": "number",
                      "minimum": 0,
                      "maximum": 1
                    }
                  }
                },
                "headcount": {
                  "type": "object",
                  "required": [
                    "value",
                    "source_provider",
                    "captured_at",
                    "confidence"
                  ],
                  "additionalProperties": false,
                  "properties": {
                    "value": {"type": "string"},
                    "source_provider": {"type": "string"},
                    "source_ref": {"type": "string"},
                    "captured_at": {"type": "string"},
                    "freshness_status": {
                      "type": "string",
                      "enum": ["fresh", "warning", "stale", "unknown"]
                    },
                    "confidence": {
                      "type": "number",
                      "minimum": 0,
                      "maximum": 1
                    }
                  }
                },
                "revenue_range": {
                  "type": "object",
                  "required": [
                    "value",
                    "source_provider",
                    "captured_at",
                    "confidence"
                  ],
                  "additionalProperties": false,
                  "properties": {
                    "value": {"type": "string"},
                    "is_modeled": {"type": "boolean"},
                    "source_provider": {"type": "string"},
                    "source_ref": {"type": "string"},
                    "captured_at": {"type": "string"},
                    "freshness_status": {
                      "type": "string",
                      "enum": ["fresh", "warning", "stale", "unknown"]
                    },
                    "confidence": {
                      "type": "number",
                      "minimum": 0,
                      "maximum": 1
                    }
                  }
                },
                "hq_country": {
                  "type": "object",
                  "required": [
                    "value",
                    "source_provider",
                    "captured_at",
                    "confidence"
                  ],
                  "additionalProperties": false,
                  "properties": {
                    "value": {"type": "string"},
                    "source_provider": {"type": "string"},
                    "source_ref": {"type": "string"},
                    "captured_at": {"type": "string"},
                    "freshness_status": {
                      "type": "string",
                      "enum": ["fresh", "warning", "stale", "unknown"]
                    },
                    "confidence": {
                      "type": "number",
                      "minimum": 0,
                      "maximum": 1
                    }
                  }
                },
                "funding_stage": {
                  "type": "object",
                  "required": [
                    "value",
                    "source_provider",
                    "captured_at",
                    "confidence"
                  ],
                  "additionalProperties": false,
                  "properties": {
                    "value": {"type": "string"},
                    "source_provider": {"type": "string"},
                    "source_ref": {"type": "string"},
                    "captured_at": {"type": "string"},
                    "freshness_status": {
                      "type": "string",
                      "enum": ["fresh", "warning", "stale", "unknown"]
                    },
                    "confidence": {
                      "type": "number",
                      "minimum": 0,
                      "maximum": 1
                    }
                  }
                },
                "total_funding_usd": {
                  "type": "object",
                  "required": [
                    "value",
                    "source_provider",
                    "captured_at",
                    "confidence"
                  ],
                  "additionalProperties": false,
                  "properties": {
                    "value": {
                      "type": [
                        "number",
                        "null"
                      ]
                    },
                    "source_provider": {"type": "string"},
                    "source_ref": {"type": "string"},
                    "captured_at": {"type": "string"},
                    "freshness_status": {
                      "type": "string",
                      "enum": ["fresh", "warning", "stale", "unknown"]
                    },
                    "confidence": {
                      "type": "number",
                      "minimum": 0,
                      "maximum": 1
                    }
                  }
                }
              }
            },
            "technographic": {
              "type": "object",
              "required": [
                "detected_stack",
                "detection_coverage_notes"
              ],
              "additionalProperties": false,
              "properties": {
                "detected_stack": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "required": [
                      "technology",
                      "provider",
                      "captured_at",
                      "confidence"
                    ],
                    "additionalProperties": false,
                    "properties": {
                      "technology": {"type": "string"},
                      "provider": {"type": "string"},
                      "captured_at": {"type": "string"},
                      "first_detected": {"type": "string"},
                      "last_detected": {"type": "string"},
                      "confidence": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1
                      }
                    }
                  }
                },
                "detection_coverage_notes": {
                  "type": "array",
                  "items": {"type": "string"}
                }
              }
            },
            "key_contacts": {
              "type": "array",
              "items": {
                "type": "object",
                "required": [
                  "title",
                  "source_provider"
                ],
                "additionalProperties": false,
                "properties": {
                  "title": {"type": "string"},
                  "contact_ref": {
                    "type": "string",
                    "description": "Anonymized pointer to source/CRM identity."
                  },
                  "linkedin_url": {"type": "string"},
                  "source_provider": {"type": "string"},
                  "captured_at": {"type": "string"}
                }
              }
            },
            "data_quality": {
              "type": "object",
              "required": [
                "coverage_score",
                "freshness_score",
                "consistency_score",
                "overall_confidence",
                "confidence_grade",
                "missing_fields",
                "stale_fields",
                "conflicts"
              ],
              "additionalProperties": false,
              "properties": {
                "coverage_score": {
                  "type": "number",
                  "minimum": 0,
                  "maximum": 1
                },
                "freshness_score": {
                  "type": "number",
                  "minimum": 0,
                  "maximum": 1
                },
                "consistency_score": {
                  "type": "number",
                  "minimum": 0,
                  "maximum": 1
                },
                "overall_confidence": {
                  "type": "number",
                  "minimum": 0,
                  "maximum": 1
                },
                "confidence_grade": {
                  "type": "string",
                  "enum": ["high", "medium", "low"]
                },
                "missing_fields": {
                  "type": "array",
                  "items": {"type": "string"}
                },
                "stale_fields": {
                  "type": "array",
                  "items": {"type": "string"}
                },
                "conflicts": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "required": [
                      "field",
                      "values_observed",
                      "resolution_status"
                    ],
                    "additionalProperties": false,
                    "properties": {
                      "field": {"type": "string"},
                      "values_observed": {
                        "type": "array",
                        "items": {"type": "string"}
                      },
                      "resolution_status": {
                        "type": "string",
                        "enum": ["resolved", "unresolved"]
                      },
                      "resolution_note": {"type": "string"}
                    }
                  }
                }
              }
            },
            "evidence": {
              "type": "object",
              "required": [
                "source_records"
              ],
              "additionalProperties": false,
              "properties": {
                "source_records": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "required": [
                      "provider",
                      "reference",
                      "captured_at"
                    ],
                    "additionalProperties": false,
                    "properties": {
                      "provider": {"type": "string"},
                      "method_id": {"type": "string"},
                      "reference": {"type": "string"},
                      "captured_at": {"type": "string"},
                      "notes": {"type": "string"}
                    }
                  }
                }
              }
            }
          }
        }
      },
      "quality_summary": {
        "type": "object",
        "required": [
          "company_count",
          "high_confidence_count",
          "medium_confidence_count",
          "low_confidence_count",
          "avg_coverage_score",
          "avg_freshness_score",
          "avg_consistency_score"
        ],
        "additionalProperties": false,
        "properties": {
          "company_count": {"type": "integer", "minimum": 0},
          "high_confidence_count": {"type": "integer", "minimum": 0},
          "medium_confidence_count": {"type": "integer", "minimum": 0},
          "low_confidence_count": {"type": "integer", "minimum": 0},
          "avg_coverage_score": {"type": "number", "minimum": 0, "maximum": 1},
          "avg_freshness_score": {"type": "number", "minimum": 0, "maximum": 1},
          "avg_consistency_score": {"type": "number", "minimum": 0, "maximum": 1}
        }
      },
      "governance": {
        "type": "object",
        "required": [
          "purpose_context",
          "suppression_checked",
          "retention_policy_ref"
        ],
        "additionalProperties": false,
        "properties": {
          "purpose_context": {"type": "string"},
          "suppression_checked": {"type": "boolean"},
          "retention_policy_ref": {"type": "string"},
          "compliance_notes": {
            "type": "array",
            "items": {"type": "string"}
          }
        }
      },
      "limitations": {
        "type": "array",
        "items": {"type": "string"}
      },
      "next_refresh_actions": {
        "type": "array",
        "items": {"type": "string"}
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Public documentation quality is uneven across providers; some endpoint/docs pages are dynamic and difficult to snapshot consistently.
- Clearbit/Breeze official endpoint exposure is not consistently verifiable from publicly accessible docs in this run; this is intentionally marked as unverified.
- Some high-volume vendor benchmarks are not peer-reviewed; these are useful operationally but should not be treated as independent scientific consensus.
- There is no global standard confidence threshold for enrichment quality; recommended thresholds are implementation-level and should be calibrated to local truth data.
- Regulatory obligations vary by jurisdiction and use case; this document provides operational guidance, not legal advice.
