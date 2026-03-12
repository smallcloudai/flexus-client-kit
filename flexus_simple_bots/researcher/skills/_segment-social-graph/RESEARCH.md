# Research: segment-social-graph

**Skill path:** `flexus-client-kit/flexus_simple_bots/researcher/skills/segment-social-graph/`  
**Bot:** researcher  
**Research date:** 2026-03-05  
**Status:** complete

---

## Context

`segment-social-graph` maps professional influence networks for target segments: decision-maker identification, influence-path discovery, and contact-level enrichment for business prospecting workflows.

This research was generated from template + brief + current `SKILL.md` context, using five internal sub-research angles: methodology, tools, API endpoint reality, interpretation, and anti-patterns/compliance. The target outcome is a safer `SKILL.md` that is source-backed (2024-2026 priority), explicit about uncertainty, and strict about not inventing endpoints.

---

## Definition of Done

- [x] At least 4 distinct research angles are covered
- [x] Each finding has source URLs or named references
- [x] Methodology includes practical execution rules
- [x] Tool/API landscape includes concrete options and caveats
- [x] Failure modes and anti-patterns are explicit
- [x] Schema recommendations map to realistic data shapes
- [x] Gaps/uncertainties are explicit
- [x] Findings prioritize 2024-2026 (older references marked evergreen when used)

---

## Quality Gates

- No generic filler without backing: **passed**
- No invented tool names, method IDs, or API endpoints: **passed**
- Contradictions and caveats explicitly stated: **passed**
- `Draft Content for SKILL.md` is the largest section: **passed**
- Internal sub-research angles >= 4: **passed** (5 used)

---

## Research Angles

### Angle 1: Domain Methodology and Best Practices

**Findings:**

- Relationship mapping is now a first-class operating workflow, not a CRM side note. LinkedIn Sales Navigator Relationship Maps explicitly support role classification (`Decision Maker`, `Champion`, `Evaluator`, `Procurement`, `Influencer`) and stale-contact detection.
- Warm-intro pathing should be explicit and ranked. TeamLink is documented as a "best path in" mechanism, but coverage depends on subscription and TeamLink settings.
- Relationship Explorer is a discovery accelerator, not full account truth: it surfaces up to eight relevant unsaved leads and excludes already-saved leads.
- Mapping quality is materially improved by multi-threading the account map: one-thread account plans are brittle when contacts move or go dark.
- 2024 buyer-process data from Forrester indicates large buying groups (average ~13 participants), frequent stalls, and high dissatisfaction with final provider choice. This supports mandatory stakeholder plurality in mapping.
- 2025 hidden-buyer evidence (Edelman x LinkedIn) indicates significant influence from stakeholders with low direct seller interaction; influence detection cannot rely only on visible meeting participants.
- Use "staleness" and role-change checks as a hard gate before high-confidence recommendations.
- CRM-connected workflows (e.g., Dynamics integration with Sales Navigator controls) show practical value in preserving people-relationship context alongside account records.
- Decision-maker mapping should separate role criticality from relationship accessibility. Senior title alone does not guarantee reachable influence.
- Social graph work should include alternative route planning (direct path, TeamLink path, shared-experience path) to avoid single-intro fragility.
- Evidence age should be scored. Interaction recency and role freshness should have explicit decay behavior.
- Output should preserve unresolved gaps instead of forcing complete org charts.

**Contradictions / nuances to encode:**

- "Closer connection" does not always equal "best path"; intro willingness and context can dominate pure graph distance.
- A missing visible path is ambiguous: it can mean true absence, settings limitations, or stale account records.
- Publicly visible role signals are not complete buying-group truth.

**Sources:**

- [Relationship Maps in Sales Navigator](https://www.linkedin.com/help/sales-navigator/answer/a456397)
- [TeamLink in Sales Navigator](https://www.linkedin.com/help/sales-navigator/answer/a101027)
- [Relationship Explorer in Sales Navigator](https://www.linkedin.com/help/sales-navigator/answer/a1421128)
- [Integrate LinkedIn Sales Navigator with Dynamics 365 Sales (11/04/2024)](https://learn.microsoft.com/en-us/dynamics365/sales/linkedin/integrate-sales-navigator)
- [Forrester: The State of Business Buying, 2024 (12/04/2024)](https://www.forrester.com/press-newsroom/forrester-the-state-of-business-buying-2024/)
- [Edelman: The Rise of the Hidden Buyer (06/26/2025)](https://www.edelman.com/insights/hidden-buyer-b2b)

---

### Angle 2: Tool and API Landscape

**Findings:**

- The practical stack for this skill is hybrid: LinkedIn for organization/professional context signals plus dedicated enrichment APIs for contact-level data operations.
- LinkedIn platform access is tiered and vetted. Community Management access requires app review and use-case screening; access expectations must be modeled as constraints, not assumptions.
- LinkedIn API operations are version-sensitive: monthly release cadence, sunset windows, and required version headers materially affect production stability.
- LinkedIn rate limits are endpoint-specific and not fully published as static global values; operational monitoring must use Developer Portal analytics.
- PDL offers deterministic enrich/search endpoint separation with explicit status semantics (`200` match, `404` no match for enrichment) and documented endpoint-level limits.
- Apollo separates search and enrichment and documents fixed-window rate limits; key endpoints require master API key.
- Clearbit naming persists in many stacks, but public 2025 HubSpot updates confirm service transitions (e.g., free Logo API sunset); endpoint assumptions must be revalidated.
- For relationship-state persistence, CRM graph primitives (associations/identity links) are strategically important, but this skill can stay connector-first and artifact-centric.
- Plan/tier drift is common across vendors; docs should be treated as current-state references, not permanent guarantees.

| Provider | Primary strength | Practical limitation | Operational note |
|---|---|---|---|
| LinkedIn Community/Marketing surfaces | Official org and social context for professional network analysis | Access vetting + scope/tier constraints | Treat as policy-first source; version header discipline required |
| LinkedIn Sales Navigator surfaces | Relationship and warm-path discovery workflows | Product-tier and settings-dependent visibility | Useful for route hypotheses, not full graph completeness |
| People Data Labs | Strong person/company enrichment and search APIs | Credit and endpoint-level rate constraints | Use explicit match/no-match semantics in pipeline logic |
| Apollo | Fast discover->enrich workflow, broad sales API ecosystem | Master-key requirements and plan-dependent access | Distinguish search output from enrichment output |
| Clearbit/HubSpot transition context | Legacy ecosystem continuity and known brand footprint | Public endpoint visibility is uneven; free logo API sunset | Treat clearbit-* assumptions as potentially stale; verify before rollout |

**Sources:**

- [LinkedIn Marketing API access tiers (updated 2026)](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/marketing-tiers?view=li-lms-2024-11)
- [Community Management App Review (updated 2026)](https://learn.microsoft.com/en-us/linkedin/marketing/community-management-app-review)
- [LinkedIn API Rate Limiting (updated 2025)](https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits)
- [PDL Person Enrichment API](https://docs.peopledatalabs.com/docs/reference-person-enrichment-api)
- [PDL Person Search API](https://docs.peopledatalabs.com/docs/reference-person-search-api)
- [PDL Usage Limits](https://docs.peopledatalabs.com/docs/usage-limits)
- [Apollo People API Search](https://docs.apollo.io/reference/people-api-search)
- [Apollo People Enrichment](https://docs.apollo.io/reference/people-enrichment)
- [Apollo Rate Limits](https://docs.apollo.io/reference/rate-limits)
- [Apollo API Pricing](https://docs.apollo.io/docs/api-pricing)
- [HubSpot changelog: Clearbit free Logo API sunset (2025)](https://developers.hubspot.com/changelog/upcoming-sunset-of-clearbits-free-logo-api)

---

### Angle 3: API Endpoint Reality and Integration Constraints

**Findings:**

- LinkedIn Marketing APIs are explicitly versioned; `Linkedin-Version: YYYYMM` is required for versioned API calls.
- LinkedIn posts and social surfaces are in migration overlap: Posts API is current, while related social detail surfaces may span social actions/reactions/metadata endpoints.
- Organization lookup/follower/account role endpoints are stable core primitives for organization-side social graph context.
- Organization follower total-count retrieval has shifted to `networkSizes` instead of old follower-stat payload assumptions.
- LinkedIn migration docs confirm aggressive deprecation cadence; endpoint strategy must include scheduled migration maintenance.
- PDL public docs provide explicit endpoint paths and billing/rate semantics for person/company enrichment/search.
- Apollo public OpenAPI definitions expose endpoint paths (base `https://api.apollo.io/api/v1`) and endpoint-level access/rate behavior.
- Clearbit full modern endpoint verification is partially constrained by gated docs; keep endpoint claims conservative.

**Verified endpoint map (official/publicly documented):**

| Surface | Endpoint | Purpose | Status |
|---|---|---|---|
| LinkedIn Posts | `POST /rest/posts` | Create posts | verified |
| LinkedIn Posts finder | `GET /rest/posts?...&q=author` | Retrieve posts by author | verified |
| LinkedIn Org ACL | `GET /rest/organizationAcls?q=roleAssignee` / `q=organization` | Check org roles/admin access | verified |
| LinkedIn Org follower stats | `GET /rest/organizationalEntityFollowerStatistics?q=organizationalEntity...` | Follower trend + demographics | verified |
| LinkedIn Network size | `GET /rest/networkSizes/urn:li:organization:{id}?edgeType=COMPANY_FOLLOWED_BY_MEMBER` | Organization follower count | verified |
| LinkedIn Org lookup | `GET /rest/organizations/{id}` and finder variants | Organization retrieval/discovery | verified |
| PDL person enrich | `GET https://api.peopledatalabs.com/v5/person/enrich` | One-to-one person enrichment | verified |
| PDL person search | `GET https://api.peopledatalabs.com/v5/person/search` | Segment search | verified |
| PDL company enrich | `GET https://api.peopledatalabs.com/v5/company/enrich` | One-to-one company enrichment | verified (public docs) |
| Apollo people search | `POST /api/v1/mixed_people/api_search` | Net-new people search | verified (OpenAPI/docs) |
| Apollo people enrich | `POST /api/v1/people/match` | Person enrichment | verified (OpenAPI/docs) |
| Apollo org enrich | `GET /api/v1/organizations/enrich` | Organization enrichment | verified (OpenAPI examples/docs) |
| Apollo usage/rate introspection | `POST /api/v1/usage_stats/api_usage_stats` | Per-endpoint limit and usage visibility | verified |
| Clearbit paid endpoints | (full modern public path set) | Person/company enrichment | partially verified (public visibility limited) |

**Do-not-claim list:**

- Do not claim undocumented LinkedIn or enrichment-provider endpoints.
- Do not treat old and new `networkSizes edgeType` values as universally interchangeable.
- Do not imply broad availability of restricted scopes (for example, `r_member_social`) without app-level approval proof.
- Do not claim full public verification of current paid Clearbit endpoint set.

**Sources:**

- [LinkedIn Marketing API versioning (updated 2026)](https://learn.microsoft.com/en-us/linkedin/marketing/versioning?view=li-lms-2026-01)
- [LinkedIn migrations status (updated 2026)](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/migrations?view=li-lms-2026-01#api-migration-status)
- [LinkedIn Posts API (updated 2026)](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api?view=li-lms-2025-10)
- [Organization Access Control by Role](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/organization-access-control-by-role?view=li-lms-2025-10)
- [Organization Follower Statistics](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/follower-statistics?view=li-lms-2026-01)
- [Organization Lookup API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/organization-lookup-api?view=li-lms-2026-01)
- [PDL Person Enrichment API](https://docs.peopledatalabs.com/docs/reference-person-enrichment-api)
- [PDL Person Search API](https://docs.peopledatalabs.com/docs/reference-person-search-api)
- [Apollo People API Search](https://docs.apollo.io/reference/people-api-search)
- [Apollo People Enrichment](https://docs.apollo.io/reference/people-enrichment)
- [Apollo View API Usage Stats and Rate Limits](https://docs.apollo.io/reference/view-api-usage-stats)

---

### Angle 4: Data Interpretation and Signal Quality

**Findings:**

- Authority, influence, and accessibility are different dimensions and should not collapse into a single opaque score.
- Buying groups are large and distributed (Forrester 2024), so single-contact inference is structurally weak.
- Hidden-buyer effects (Edelman 2025) imply low-observability stakeholders can still materially affect outcomes.
- Relationship signals should be confidence-weighted by freshness and corroboration count.
- Role-change risk is non-trivial in fast-changing labor environments; stale role assumptions degrade social graph quality.
- Warm-path availability should increase actionability score, not authority score.
- Contact enrichment output and social-graph interpretation should be explicitly separated to avoid overfitting narrative certainty.
- Confidence should decrease when evidence is one-source, stale, or contradictory.
- "No visible path" should map to uncertainty, not negative proof.
- Strong conclusions should require at least two independent evidence dimensions (role evidence + path evidence, or role evidence + activity evidence).

**Misinterpretations to avoid:**

- Senior title => decision authority (always)
- Existing connection => willing and credible intro path
- One active contact => complete buying-group representation
- No route discovered => no influence channel exists
- Fresh engagement snapshot => durable relationship strength

**Practical defaults (heuristics, not official platform cutoffs):**

- Maintain three scores per target contact: `authority_score`, `influence_score`, `accessibility_score`.
- Use recency decay: interaction signals decay faster than role/title signals.
- Cap confidence at medium when only one organization or one stakeholder class is observed.
- Require explicit contradiction notes for mixed evidence.

**Sources:**

- [Forrester: The State of Business Buying, 2024](https://www.forrester.com/press-newsroom/forrester-the-state-of-business-buying-2024/)
- [Edelman: The Rise of the Hidden Buyer (2025)](https://www.edelman.com/insights/hidden-buyer-b2b)
- [Relationship Maps in Sales Navigator](https://www.linkedin.com/help/sales-navigator/answer/a456397)
- [Relationship Explorer in Sales Navigator](https://www.linkedin.com/help/sales-navigator/answer/a1421128)
- [LinkedIn Work Change Snapshot (2024)](https://economicgraph.linkedin.com/content/dam/me/economicgraph/en-us/PDF/Work-Change-Snapshot.pdf)

---

### Angle 5: Failure Modes, Anti-Patterns, and Compliance

**Findings:**

- Unauthorized scraping/automation remains a high-impact failure mode for social graph workstreams.
- LinkedIn Marketing member data has strict restrictions; specific sales/recruiting CRM enrichment uses are explicitly disallowed for those data classes.
- Retention violations are easy to create if pipeline stores mixed member/activity/org data without field-level TTL controls.
- Over-collection creates compliance risk and often no analytic value.
- Identity stitching without confidence gates causes false links and harmful recommendations.
- "Publicly visible" does not equal unrestricted lawful processing for any downstream purpose.
- Regulatory posture in 2024-2025 continues to harden around scraping, profiling, and deceptive social proof.

**Anti-pattern blocks:**

- **Unauthorized scraping and botting**
  - Detection: non-approved ingestion paths, anti-abuse events, abnormal automated interaction patterns
  - Consequence: account restrictions, access loss, trust/legal risk
  - Mitigation: API-only allowlist, crawler deny policy, kill-switch for unapproved collectors
- **Restricted member-data misuse**
  - Detection: member social/profile data flowing into lead enrichment or audience generation
  - Consequence: explicit terms violation risk
  - Mitigation: purpose-tag enforcement, blocked joins/exports, policy checks pre-deploy
- **Retention drift**
  - Detection: no per-field TTL, stale member data beyond documented windows
  - Consequence: storage-requirement non-compliance
  - Mitigation: retention-as-code + deletion fanout
- **Unverifiable identity linking**
  - Detection: low-confidence merges and collision-heavy identity graph
  - Consequence: wrong recommendations and deletion/DSAR failure risk
  - Mitigation: deterministic-first matching, confidence floor, quarantine low-confidence links

**Risk prioritization:**

1. Unauthorized scraping/access bypass  
2. Restricted member-data misuse  
3. Retention/deletion non-compliance  
4. Unverifiable identity linking  
5. Over-collection and opaque profiling assumptions

**Sources:**

- [Restricted Uses of LinkedIn Marketing APIs and Data (updated 2025)](https://learn.microsoft.com/en-us/linkedin/marketing/restricted-use-cases?view=li-lms-2026-01)
- [LinkedIn Marketing API Data Storage Requirements (updated 2026)](https://learn.microsoft.com/en-us/linkedin/marketing/data-storage-requirements?view=li-lms-2026-01)
- [LinkedIn Marketing API Terms](https://www.linkedin.com/legal/l/marketing-api-terms)
- [LinkedIn API Terms of Use](https://www.linkedin.com/legal/l/api-terms-of-use)
- [LinkedIn User Agreement](https://www.linkedin.com/legal/user-agreement)
- [Prohibited software and extensions (LinkedIn Help)](https://www.linkedin.com/help/linkedin/answer/a1341387/prohibited-software-and-extensions?lang=en)
- [ICO joint statement follow-up on scraping (10/28/2024)](https://ico.org.uk/about-the-ico/media-centre/news-and-blogs/2024/10/global-privacy-authorities-issue-follow-up-joint-statement-on-data-scraping-after-industry-engagement/)
- [EDPB Opinion 28/2024](https://www.edpb.europa.eu/our-work-tools/our-documents/opinion-board-art-64/opinion-282024-certain-data-protection-aspects_en)
- [FTC final rule on fake reviews/testimonials (08/14/2024)](https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials)

---

## Synthesis

The central synthesis is that social graph segmentation quality is now constrained more by evidence discipline and policy discipline than by raw data volume. In 2024-2026 references, both buying behavior and platform governance moved in ways that punish naive single-thread mapping and permissive data handling.

For this skill, the best upgrade is to convert from "enrich contacts + infer influence" into a governed evidence pipeline:

1. Role map and path map separately.  
2. Score authority, influence, accessibility separately.  
3. Force freshness and corroboration gates before strong claims.  
4. Keep LinkedIn data-use restrictions explicit in execution logic.  
5. Publish limitations and contradictions instead of smoothing them away.

---

## Recommendations for SKILL.md

- [x] Add a strict evidence contract separating role authority, influence, and accessibility.
- [x] Add staged methodology with explicit quality gates (coverage, freshness, corroboration).
- [x] Keep `Available Tools` examples limited to known method IDs currently used by this skill.
- [x] Add explicit API reality notes (versioning, endpoint drift, scope/tier checks).
- [x] Add confidence and contradiction policy.
- [x] Add named anti-pattern warning blocks.
- [x] Add compliance guardrails for restricted member data and retention windows.
- [x] Expand schema for provenance, confidence decomposition, and conflict tracking.
- [x] Add pre-`write_artifact` quality checklist.

---

## Draft Content for SKILL.md

### Draft: Core operating contract

Use professional social graph profiling for business contexts only.  
Your goal is to produce a **defensible influence map**, not a complete org-chart fantasy.

Core rules:

- Keep `authority`, `influence`, and `accessibility` as separate signals.
- Do not convert uncertain role/path evidence into high-confidence conclusions.
- Prefer transparent `limitations` over forced certainty.
- Never invent method IDs, endpoints, or hidden data access.
- Never store full names + emails together in artifact output. Use source references or anonymized contact IDs.

Evidence classes:

- `observed`: directly retrieved from tool output
- `derived`: computed from observed fields with explicit formula
- `hypothesized`: informed inference requiring downstream validation

Only `observed` + `derived` evidence may support `strong` recommendations.

---

### Draft: Methodology sequence (must run in order)

1. **Scope lock**
   - Confirm one segment scope per run.
   - Define target account list or target-domain list before enrichment calls.
   - Record query boundaries in `run_metadata`.

2. **Preflight and tool health**
   - Check connector availability first.
   - If key connector unavailable, continue with partial path but cap confidence.

3. **Initial role candidate extraction**
   - Use PDL + Apollo searches for role/title candidates by domain/company.
   - Enrich candidates with available profile fields from approved sources.
   - Normalize title variants into role buckets (`economic_buyer`, `technical_buyer`, `champion`, `influencer`, `procurement`, `gatekeeper`).

4. **Organization context collection**
   - Pull org-level topical context from LinkedIn organization posts.
   - Use org context as relevance context only; do not infer member-level authority solely from org posting patterns.

5. **Path and accessibility estimation**
   - Add known route hints (shared context, known relationship references, TeamLink-like route indicators when available to user environment).
   - Mark route quality as `direct`, `warm_possible`, `unknown`, not binary yes/no.

6. **Freshness and churn checks**
   - Identify stale profiles and potential role changes.
   - Penalize stale nodes in confidence scoring.

7. **Influence graph assembly**
   - Build account-level map with explicit node/edge evidence refs.
   - Keep missing nodes explicit (`unknown placeholder`) instead of hiding gaps.

8. **Quality gates before classification**
   - Coverage gate: no single-thread graph for strong recommendations.
   - Freshness gate: stale core contacts prevent high confidence.
   - Corroboration gate: at least two independent evidence dimensions for strong claims.

9. **Classification + confidence**
   - Emit role and path recommendations with confidence + caveats.
   - Record contradictions and unresolved assumptions.

10. **Artifact write**
    - Write one artifact for one segment scope.
    - Include `limitations`, `contradictions`, and `next_checks` every run.

---

### Draft: Available Tools (known skill method IDs only)

```python
linkedin_b2b(
  op="call",
  args={
    "method_id": "linkedin_b2b.organization_posts.list.v1",
    "organization_id": "12345",
    "count": 20
  }
)

pdl(
  op="call",
  args={
    "method_id": "pdl.person.enrichment.v1",
    "profile": "linkedin.com/in/username",
    "pretty": True
  }
)

pdl(
  op="call",
  args={
    "method_id": "pdl.person.search.v1",
    "query": {
      "bool": {
        "must": [
          {"term": {"job_company_website": "company.com"}},
          {"term": {"job_title_role": "engineering"}}
        ]
      }
    },
    "size": 10
  }
)

apollo(
  op="call",
  args={
    "method_id": "apollo.people.search.v1",
    "q_organization_domains": ["company.com"],
    "person_titles": ["CTO", "VP Engineering", "Head of Product"],
    "per_page": 25
  }
)

clearbit(
  op="call",
  args={
    "method_id": "clearbit.person.enrichment.v1",
    "email": "contact@company.com"
  }
)
```

Call-order default:

1. role candidate search (`pdl.person.search.v1`, `apollo.people.search.v1`)  
2. candidate enrichment (`pdl.person.enrichment.v1`, `clearbit.person.enrichment.v1`)  
3. org context (`linkedin_b2b.organization_posts.list.v1`)  
4. graph assembly + scoring + artifact write

---

### Draft: API reality notes (must-follow)

- LinkedIn Marketing APIs are versioned and require `Linkedin-Version: YYYYMM` in direct API integrations.
- LinkedIn rate limits are endpoint-specific and read from Developer Portal analytics, not static docs.
- LinkedIn Community/Marketing access is use-case gated and tier-gated.
- LinkedIn member-data restrictions are strict for certain use classes (especially sales/recruiting CRM enrichment from member data in restricted contexts).
- Keep "official endpoint" and "provider wrapper" evidence classes separate.
- PDL and Apollo endpoint semantics are explicit in public docs; still treat plan/rate details as tenant-dependent.
- Clearbit legacy naming can remain in workflows, but endpoint assumptions should be validated due ecosystem transition.

---

### Draft: Interpretation policy and confidence scoring

Scoring dimensions per contact:

- `authority_score` (formal role influence on decision)
- `influence_score` (ability to move internal consensus)
- `accessibility_score` (practical path-to-conversation likelihood)

Do not collapse these into one hidden score before reporting.

Default weighted aggregate (heuristic):

`composite_score = 0.45*authority_score + 0.35*influence_score + 0.20*accessibility_score`

Confidence model (heuristic):

- Start at `0.50`
- `+0.10` if role evidence corroborated by >=2 sources
- `+0.10` if path evidence includes explicit warm-route indicator
- `+0.10` if evidence freshness is within policy window
- `+0.10` if account map has multi-role coverage
- `-0.10` for each unresolved contradiction
- `-0.10` if only one source family is available
- `-0.15` if key connector failure prevents required evidence

Confidence tiers:

- `high`: `0.80-1.00`
- `medium`: `0.60-0.79`
- `low`: `0.40-0.59`
- `insufficient`: `<0.40`

Strong recommendation gate:

- requires at least 2 evidence dimensions
- cannot be based on a single stale contact
- cannot pass with unresolved major contradiction

---

### Draft: Anti-pattern warning blocks

#### WARNING: Single-threaded account map
**What it looks like:** Only one meaningful stakeholder is mapped.  
**Detection signal:** `decision_makers` has one contact and no alternate route.  
**Consequence:** High fragility and false confidence.  
**Mitigation:** Require at least 3 role buckets or return `insufficient_data`.

#### WARNING: Title equals authority shortcut
**What it looks like:** Seniority/title is used as sole authority evidence.  
**Detection signal:** `authority_score` has no corroborating evidence refs.  
**Consequence:** Mis-prioritized outreach.  
**Mitigation:** Require corroboration from at least one additional source signal.

#### WARNING: Path certainty inflation
**What it looks like:** "Warm intro available" from weak or stale path hints.  
**Detection signal:** path marked `direct` without evidence timestamp.  
**Consequence:** Action failure and trust loss.  
**Mitigation:** Track path freshness and downgrade to `warm_possible` when uncertain.

#### WARNING: Restricted member-data misuse
**What it looks like:** LinkedIn member data repurposed for prohibited prospecting flows.  
**Detection signal:** member-social/profile data exported into CRM lead append workflows.  
**Consequence:** terms/compliance risk.  
**Mitigation:** purpose-limited processing, blocked transfers, explicit data-use controls.

#### WARNING: Retention drift
**What it looks like:** No TTL rules for restricted data fields.  
**Detection signal:** field-level age exceeds policy windows.  
**Consequence:** policy and audit failures.  
**Mitigation:** retention-as-code with automated purge jobs.

---

### Draft: Compliance and data handling guardrails

Before run:

- Confirm data sources are approved APIs or approved imported systems.
- Reject scraping-style collection paths.

During run:

- Keep LinkedIn-sourced member data in policy-safe bounds.
- Keep organization-level and member-level data classes separate.
- Store only fields needed for the current skill outcome.

After run:

- Apply field-level retention and deletion policies.
- Keep lineage metadata for every evidence item.
- If requested use case appears restricted, return transparent limitation instead of workaround collection.

---

### Draft: Result-state policy

Use these states:

- `ok`: sufficient coherent evidence
- `ok_with_conflicts`: useful evidence exists but material contradictions remain
- `zero_results`: no relevant candidates despite valid execution
- `insufficient_data`: data present but too sparse/noisy for safe recommendation
- `technical_failure`: tool/connector errors blocked core analysis
- `auth_required`: required source authentication missing

When conflicts exist:

- keep evidence-backed partial insights
- record conflict and confidence impact
- avoid binary overclaims

---

### Draft: Expanded artifact schema (paste-ready)

```json
{
  "segment_social_graph_profile": {
    "type": "object",
    "required": [
      "segment_id",
      "profiled_at",
      "result_state",
      "accounts",
      "confidence",
      "confidence_grade",
      "limitations",
      "next_checks"
    ],
    "additionalProperties": false,
    "properties": {
      "segment_id": {
        "type": "string"
      },
      "profiled_at": {
        "type": "string",
        "description": "ISO timestamp for run completion."
      },
      "result_state": {
        "type": "string",
        "enum": [
          "ok",
          "ok_with_conflicts",
          "zero_results",
          "insufficient_data",
          "technical_failure",
          "auth_required"
        ]
      },
      "accounts": {
        "type": "array",
        "minItems": 1,
        "items": {
          "type": "object",
          "required": [
            "domain",
            "decision_makers",
            "influence_paths",
            "coverage_state"
          ],
          "additionalProperties": false,
          "properties": {
            "domain": {
              "type": "string"
            },
            "coverage_state": {
              "type": "string",
              "enum": [
                "multi_threaded",
                "single_threaded",
                "sparse"
              ]
            },
            "decision_makers": {
              "type": "array",
              "items": {
                "type": "object",
                "required": [
                  "contact_ref",
                  "buyer_role",
                  "authority_score",
                  "influence_score",
                  "accessibility_score",
                  "confidence",
                  "evidence_refs"
                ],
                "additionalProperties": false,
                "properties": {
                  "contact_ref": {
                    "type": "string",
                    "description": "Anonymized reference to source-system contact."
                  },
                  "buyer_role": {
                    "type": "string",
                    "enum": [
                      "economic_buyer",
                      "technical_buyer",
                      "champion",
                      "influencer",
                      "procurement",
                      "gatekeeper",
                      "unknown"
                    ]
                  },
                  "seniority": {
                    "type": "string",
                    "enum": [
                      "c_level",
                      "vp",
                      "director",
                      "manager",
                      "ic",
                      "unknown"
                    ]
                  },
                  "authority_score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                  },
                  "influence_score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                  },
                  "accessibility_score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                  },
                  "composite_score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                  },
                  "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                  },
                  "confidence_grade": {
                    "type": "string",
                    "enum": [
                      "high",
                      "medium",
                      "low",
                      "insufficient"
                    ]
                  },
                  "freshness_days": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Age of most recent corroborating evidence."
                  },
                  "evidence_refs": {
                    "type": "array",
                    "items": {
                      "type": "string"
                    },
                    "minItems": 1
                  },
                  "contradiction_flags": {
                    "type": "array",
                    "items": {
                      "type": "string"
                    }
                  }
                }
              }
            },
            "influence_paths": {
              "type": "array",
              "items": {
                "type": "object",
                "required": [
                  "from_contact_ref",
                  "to_contact_ref",
                  "path_type",
                  "path_quality",
                  "evidence_refs"
                ],
                "additionalProperties": false,
                "properties": {
                  "from_contact_ref": {
                    "type": "string"
                  },
                  "to_contact_ref": {
                    "type": "string"
                  },
                  "path_type": {
                    "type": "string",
                    "enum": [
                      "direct",
                      "teamlink_like",
                      "shared_context",
                      "unknown"
                    ]
                  },
                  "path_quality": {
                    "type": "string",
                    "enum": [
                      "high",
                      "medium",
                      "low",
                      "unknown"
                    ]
                  },
                  "evidence_refs": {
                    "type": "array",
                    "items": {
                      "type": "string"
                    }
                  }
                }
              }
            },
            "org_topics": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "Organization-level context from public company activity."
            }
          }
        }
      },
      "confidence": {
        "type": "number",
        "minimum": 0,
        "maximum": 1
      },
      "confidence_grade": {
        "type": "string",
        "enum": [
          "high",
          "medium",
          "low",
          "insufficient"
        ]
      },
      "confidence_components": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "source_diversity": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          },
          "freshness": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          },
          "coverage": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          },
          "contradiction_penalty": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          }
        }
      },
      "limitations": {
        "type": "array",
        "items": {
          "type": "string"
        }
      },
      "contradictions": {
        "type": "array",
        "items": {
          "type": "object",
          "required": [
            "topic",
            "note",
            "impact"
          ],
          "additionalProperties": false,
          "properties": {
            "topic": {
              "type": "string"
            },
            "note": {
              "type": "string"
            },
            "impact": {
              "type": "string",
              "enum": [
                "minor",
                "moderate",
                "major"
              ]
            }
          }
        }
      },
      "next_checks": {
        "type": "array",
        "items": {
          "type": "string"
        }
      },
      "run_metadata": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "sources_used": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "time_window": {
            "type": "object",
            "required": [
              "start_date",
              "end_date"
            ],
            "additionalProperties": false,
            "properties": {
              "start_date": {
                "type": "string"
              },
              "end_date": {
                "type": "string"
              }
            }
          }
        }
      }
    }
  }
}
```

---

### Draft: Recording and quality checklist

```python
write_artifact(
  artifact_type="segment_social_graph_profile",
  path="/segments/{segment_id}/social-graph",
  data={...}
)
```

Pre-write checklist:

1. All emitted contacts have anonymized `contact_ref` (no full name + email pair in output).
2. Role, influence, and accessibility are scored separately.
3. Strong recommendations pass coverage/freshness/corroboration gates.
4. Contradictions are recorded, not hidden.
5. Confidence score and confidence grade are internally consistent.
6. Limitations and next checks are concrete.
7. Data handling follows source restrictions and retention requirements.

If any check fails, downgrade confidence and/or set `result_state` to `insufficient_data`.

---

## Gaps and Uncertainties

- LinkedIn Help pages often provide relative freshness labels ("x months ago"), not absolute publish timestamps.
- Sales Navigator features and visibility differ by license tier and org-level configuration; run-time entitlement can vary.
- Clearbit paid endpoint verification is partially constrained by gated docs; endpoint assumptions should remain conservative.
- Public benchmark numbers for social influence and engagement are methodological references, not universal constants.
- This research is operational guidance, not legal advice; production policy decisions should include legal/compliance review.
