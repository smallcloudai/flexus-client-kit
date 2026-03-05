# Research: signal-search-seo

**Skill path:** `flexus_simple_bots/researcher/skills/signal-search-seo/`  
**Bot:** researcher  
**Research date:** 2026-03-05  
**Status:** complete

---

## Context

`signal-search-seo` is the researcher skill for search demand signal detection: keyword volume, trend direction, SERP shape, and competitor visibility for one query scope per run.

The current `SKILL.md` already has a strong evidence-first intent, but it needs deeper 2024-2026 operating guidance in five places:

1. Methodology sequencing (collect -> normalize -> triangulate -> classify -> verdict),
2. Tool/API constraints (quota, plan gating, endpoint style, and verification),
3. Interpretation quality gates (freshness, comparability, contradiction handling),
4. Explicit anti-pattern blocks for modern SERP behavior (AIO and zero-click effects),
5. Richer artifact schema for provenance, contradiction, and confidence auditability.

This document is written so a future editor can update `SKILL.md` directly without inventing missing policy text, endpoint assumptions, or schema fields.

---

## Definition of Done

Research is complete when ALL of the following are satisfied:

- [x] At least 4 distinct research angles are covered (see Research Angles section)
- [x] Each finding has a source URL or named reference
- [x] Methodology section covers practical how-to, not just theory
- [x] Tool/API landscape is mapped with at least 3-5 concrete options
- [x] At least one "what not to do" / common failure mode is documented
- [x] Output schema recommendations are grounded in real-world data shapes
- [x] Gaps section honestly lists what was NOT found or is uncertain
- [x] All findings are from 2024-2026 unless explicitly marked as evergreen

---

## Quality Gates

Before marking status `complete`, verify:

- No generic filler remains; each rule maps to at least one source or provider behavior: **passed**
- No invented tool names, method IDs, or provider endpoints are presented as facts: **passed**
- Contradictions between official and third-party narratives are explicit: **passed**
- Findings volume and Draft Content volume are both substantial; Draft is the largest section: **passed**

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do strong teams run search-demand signal detection in 2024-2026, and what changed with AI-heavy SERPs?

**Findings:**

- Practical teams now run SEO demand analysis as a **triangulation workflow**, not a one-tool query. The minimum stack is commonly: trend direction (Google Trends), planning/volume baseline (Google Ads Keyword Planner), and first-party outcomes (Search Console), with SERP capture context layered after that.
- Google Trends is explicitly a **relative, normalized, sampled index**, not absolute demand. This means trend-only inferences are weak without corroboration.
- Search Console remains the closest first-party demand/outcome surface, but query tables are not complete; anonymization and row limits can hide long-tail terms. Table-only interpretation is low confidence for market-sizing style claims.
- Modern query interpretation separates two questions: **(1) demand exists?** and **(2) capturable click opportunity exists?** This separation matters because SERP feature density can suppress click opportunity even when query demand is stable.
- Weekly refresh cadence is preferred over monthly-only workflows where volatility matters; short windows still need freshness gates and incident overlays before high-confidence verdicts.
- Quality workflows now require explicit segmentation: brand vs non-brand, geo, device, and search appearance. Blended totals often hide directional reversals.
- Strong teams now track a contradiction log by design (for example: official quality-click narrative vs independent CTR-loss studies), rather than forcing one narrative.
- Algorithm/update and incident overlays are now standard context layers. Movement during known rollout windows is handled as provisional unless corroborated by stable post-window data.
- Competitor visibility now requires two lenses: classic rank visibility and answer-surface presence (AIO/citation presence, SERP feature crowding).
- Breakout detection is handled as probabilistic unless persistence is shown across several periods and multiple sources.
- Third-party keyword difficulty and competitor traffic are still useful, but treated as modeled prioritization signals rather than final truth.
- Mature teams document source class on each signal (`direct`, `sampled`, `modeled`) before confidence assignment.

**Contradictions to carry into skill logic:**

- Google communications emphasize improved discovery and higher-quality clicks in AI-enabled search contexts, while third-party studies frequently report lower aggregate CTR for affected cohorts.
- AI Overview and feature prevalence changes are rapid across geographies and query classes; fixed assumptions decay quickly.
- Third-party traffic and difficulty metrics are useful directionally but differ in methodology; cross-tool numeric parity is not a quality requirement.

**Sources:**

- [A1] Google Trends FAQ (evergreen) - https://support.google.com/trends/answer/4365533?hl=en
- [A2] Search Console Performance report help (evergreen) - https://support.google.com/webmasters/answer/7576553?hl=en
- [A3] About Search Console data limitations (evergreen) - https://support.google.com/webmasters/answer/96568?hl=en
- [A4] Search Console API: getting all your data (evergreen) - https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data
- [A5] About Keyword Planner forecasts (evergreen) - https://support.google.com/google-ads/answer/3022575
- [A6] Google: New ways to connect to the web with AI Overviews (2024) - https://blog.google/products/search/new-ways-to-connect-to-the-web-with-ai-overviews/
- [A7] Google: AI in Search driving more queries and higher quality clicks (2025) - https://blog.google/products/search/ai-search-driving-more-queries-higher-quality-clicks/
- [A8] Google AI Overview expansion update (2025) - https://blog.google/products-and-platforms/products/search/ai-overview-expansion-may-2025-update/
- [A9] Google Search Status dashboard history (evergreen feed) - https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history
- [A10] Pew: users less likely to click links when AI summary appears (2025) - https://www.pewresearch.org/short-reads/2025/07/22/google-users-are-less-likely-to-click-on-links-when-an-ai-summary-appears-in-the-results/
- [A11] SparkToro zero-click study (2024) - https://sparktoro.com/blog/2024-zero-click-search-study-for-every-1000-us-google-searches-only-374-clicks-go-to-the-open-web-in-the-eu-its-360/
- [A12] Semrush AI Overviews study (2025) - https://www.semrush.com/blog/semrush-ai-overviews-study/
- [A13] Ahrefs: AI Overviews reduce clicks update (2025) - https://ahrefs.com/blog/ai-overviews-reduce-clicks-update/
- [A14] Seer: AIO impact on Google CTR update (2025) - https://www.seerinteractive.com/insights/aio-impact-on-google-ctr-september-2025-update

---

### Angle 2: Tool & API Landscape
> What APIs are real, what endpoints are verified, and what constraints change implementation quality?

**Findings:**

- Provider endpoint style is heterogeneous: Google Ads uses service methods (`googleAds:search`), DataForSEO uses task/live REST paths, Semrush mixes query-style report endpoints and newer API lanes, SerpApi uses engine-based `/search`, and Bing Webmaster uses `api.svc` protocol routing.
- Google Ads keyword-planning workflows are endpoint-verified and production-usable, but planning operations include explicit QPS and quota constraints; queueing and retry policy is required for stable automation.
- DataForSEO v3 is current; v2 is sunset (2026-05-05). Teams still referencing v2 endpoint patterns will accumulate avoidable failures.
- DataForSEO has both account-level and endpoint-level limits; live endpoints can be more constrained than broad account RPM assumptions.
- SerpApi has explicit status/error surfaces and plan-gated throughput/features; pipeline design should treat it as credit-constrained extraction infrastructure, not unlimited fetch.
- Semrush is not one API shape. Analytics API patterns (`type=...`) differ from Projects and Trends APIs; endpoint assumptions copied between lanes are a recurring source of integration errors.
- Semrush and other SEO data vendors are explicit that modeled/clickstream-assisted metrics are not identical to first-party logs; this should be encoded into confidence logic.
- Bing Webmaster API is site-owner scoped and useful for owned-domain query/rank insight; it is not a competitor-wide SERP scraping substitute.
- De-facto practical stack in this domain is hybrid: first-party baseline + trend layer + SERP extraction + competitor estimation.
- The safest skill-level policy is endpoint verification at runtime (`op="help"` for wrappers) plus official-provider endpoint map in docs for auditing.

| Provider | Verified capability lane | Verified endpoint/method examples | Key caveats |
|---|---|---|---|
| Google Ads API | Keyword planning + search query interface | `googleAds:search`, `googleAds:searchStream`, `GenerateKeywordIdeas`, `GenerateKeywordHistoricalMetrics` | Access-level and quota constraints |
| DataForSEO v3 | SERP + keywords data task/live APIs | `/v3/serp/google/organic/task_post`, `/v3/keywords_data/google_ads/search_volume/live` | Endpoint-level limits, v2 sunset |
| SerpApi | Search engine wrappers + archive | `GET /search?engine=google`, `GET /searches/{search_id}` | Plan/credit throughput limits |
| Semrush APIs | Analytics + Projects + Trends lanes | `https://api.semrush.com/?type=...`, `/management/v1/...`, `/analytics/ta/api/v3/...` | Multiple API lanes with different models |
| Bing Webmaster API | Owned-site query/rank and submission methods | `api.svc/json/GetQueryStats`, `GetRankAndTrafficStats`, `SubmitUrl` | Site-owner scope; not market-wide competitor dataset |

**Verified endpoint examples (real provider docs):**

- Google Ads REST search: `POST https://googleads.googleapis.com/v23/customers/{customerId}/googleAds:search`
- Google Ads REST searchStream: `POST https://googleads.googleapis.com/v23/customers/{customerId}/googleAds:searchStream`
- DataForSEO SERP endpoint discovery: `GET https://api.dataforseo.com/v3/serp/endpoints`
- DataForSEO keywords data endpoint discovery: `GET https://api.dataforseo.com/v3/keywords_data/endpoints`
- SerpApi search endpoint: `GET https://serpapi.com/search?engine=google`
- SerpApi archive endpoint: `GET https://serpapi.com/searches/{search_id}`
- Semrush analytics pattern: `GET https://api.semrush.com/?type=domain_organic&key=...`
- Semrush trends summary pattern: `GET https://api.semrush.com/analytics/ta/api/v3/summary?...`
- Bing protocol pattern: `https://ssl.bing.com/webmaster/api.svc/json/METHOD_NAME?apikey=...`

**Sources:**

- [T1] Google Ads REST search docs - https://developers.google.com/google-ads/api/rest/common/search
- [T2] Google Ads quotas - https://developers.google.com/google-ads/api/docs/best-practices/quotas
- [T3] Google Ads access levels - https://developers.google.com/google-ads/api/docs/access-levels
- [T4] Google Ads release notes - https://developers.google.com/google-ads/api/docs/release-notes
- [T5] KeywordPlanIdeaService `GenerateKeywordIdeas` - https://developers.google.com/google-ads/api/reference/rpc/v23/KeywordPlanIdeaService/GenerateKeywordIdeas
- [T6] KeywordPlanIdeaService `GenerateKeywordHistoricalMetrics` - https://developers.google.com/google-ads/api/reference/rpc/v23/KeywordPlanIdeaService/GenerateKeywordHistoricalMetrics
- [T7] DataForSEO SERP endpoints - https://docs.dataforseo.com/v3/serp-endpoints/
- [T8] DataForSEO keywords data endpoints - https://docs.dataforseo.com/v3/keywords_data/endpoints/
- [T9] DataForSEO rate limits - https://dataforseo.com/help-center/rate-limits-and-request-limits
- [T10] DataForSEO v2 sunset notice (2026) - https://dataforseo.com/update/dataforseo-api-v2-sunset-notice
- [T11] SerpApi Search API - https://serpapi.com/search-api
- [T12] SerpApi Search Archive API - https://serpapi.com/search-archive-api
- [T13] SerpApi status/error codes - https://serpapi.com/api-status-and-error-codes
- [T14] Semrush API intro - https://developer.semrush.com/api/basics/introduction/
- [T15] Semrush analytics tutorials - https://developer.semrush.com/api/basics/api-tutorials/analytics-api/
- [T16] Semrush trends API intro - https://developer.semrush.com/api/v3/trends/welcome-to-trends-api/
- [T17] Bing Webmaster API protocols - https://learn.microsoft.com/en-us/bingwebmaster/api-protocols
- [T18] Bing Webmaster getting access - https://learn.microsoft.com/en-us/bingwebmaster/getting-access
- [T19] Bing `GetQueryStats` method - https://learn.microsoft.com/en-us/dotnet/api/microsoft.bing.webmaster.api.interfaces.iwebmasterapi.getquerystats
- [T20] Bing URL submission guidance - https://www.bing.com/webmasters/help/url-submission-62f2860b

---

### Angle 3: Data Interpretation & Signal Quality
> What is signal vs noise in modern SEO demand interpretation, and how should confidence be assigned?

**Findings:**

- Trends index values are relative and sampled; direct conversion to absolute volume is invalid without external calibration.
- Search Console recent data is often provisional; high-confidence decisions from freshest slices are risky.
- GSC query tables can omit anonymized/rare terms and show aggregate/table mismatches by design; hidden-tail effects should be treated as a known uncertainty class.
- GT extraction stability is an empirical concern in 2024-2025 research; replication/smoothing improves reliability in some use cases.
- Keyword Planner and vendor search-volume surfaces are modeled and rounded, often with close-variant grouping; literal interpretation as exact demand is overconfident.
- Cross-source directional agreement is usually more reliable than numeric equivalence across heterogeneous data-generation methods.
- Comparability controls (same geo/language/device/search-type/window definitions) are mandatory for trend claims.
- Seasonality and update/incident overlays are required for causal claims; otherwise ordinary periodic movement can be misread as structural shift.
- SERP context is a first-class interpretation variable. Rank/position with no feature context is insufficient for capture-opportunity claims.
- No universal public threshold defines "strong/moderate/weak" demand signal for all markets. Strong teams use explicit local policies and annotate confidence.
- Interpretation quality should include contradiction handling: unresolved conflicts reduce confidence even when one source appears compelling.
- Distinguishing source classes (`direct`, `sampled`, `modeled`) is one of the highest-value controls for reducing false confidence.

**Common misinterpretations and corrections:**

- Misread: "Google Trends 100 means high absolute search count."  
  Correction: `100` is normalized peak interest in the selected window/location.
- Misread: "GSC query table is complete."  
  Correction: anonymized and long-tail query effects can hide rows; table-only analysis is partial.
- Misread: "Vendor traffic estimate is exact competitor truth."  
  Correction: modeled data is directional and should be cross-validated where possible.
- Misread: "Short-window spike means durable breakout."  
  Correction: require persistence and corroboration across windows/sources.
- Misread: "Rank flat means opportunity flat."  
  Correction: SERP layout changes can alter clicks independently of rank.

**Sources:**

- [D1] Google Trends FAQ (evergreen) - https://support.google.com/trends/answer/4365533?hl=en
- [D2] Search Console Performance report help (evergreen) - https://support.google.com/webmasters/answer/7576553?hl=en
- [D3] About Search Console data limitations (evergreen) - https://support.google.com/webmasters/answer/96568
- [D4] Search Console API all-data guide (evergreen) - https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data
- [D5] Search Console BigQuery/table guidance (evergreen) - https://support.google.com/webmasters/answer/12917991
- [D6] Cebrian & Domenech: addressing Google Trends inconsistencies (2024) - https://riunet.upv.es/server/api/core/bitstreams/7ae0cdeb-6719-4425-9874-8fe8e4e79d52/content
- [D7] Djorno et al.: restoring GT forecasting power with preprocessing (2025) - https://arxiv.org/html/2504.07032v2
- [D8] Semrush: where data comes from (evergreen, updated continuously) - https://www.semrush.com/kb/998-where-does-semrush-data-come-from
- [D9] Ahrefs glossary: search volume caveats (evergreen) - https://ahrefs.com/seo/glossary/search-volume
- [D10] BLS seasonal-adjustment methodology (updated 2026) - https://www.bls.gov/cpi/seasonal-adjustment/methodology.htm
- [D11] Google Search Status dashboard history - https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history

---

### Angle 4: Failure Modes & Anti-Patterns
> What repeatedly goes wrong in operational SEO demand analysis, and how should the skill block it?

**Findings:**

- **Data-class conflation:** mixed dashboards that merge relative index, modeled volume, and first-party outcomes without labels.
  - Detection signal: same chart compares unlike units with no provenance.
  - Consequence: wrong strategic prioritization and false confidence.
  - Mitigation: enforce `evidence_class` and confidence downgrade rules.
- **Trend absolutism:** treating GT spikes as absolute market growth.
  - Detection signal: breakout claims based only on relative index movement.
  - Consequence: resource misallocation to non-durable topics.
  - Mitigation: persistence window + independent corroboration required.
- **Anonymized-tail blindness:** assuming GSC query tables fully represent demand.
  - Detection signal: aggregate/table mismatch ignored.
  - Consequence: underestimation of long-tail opportunities and risks.
  - Mitigation: API/BigQuery strategy plus explicit hidden-tail caveat.
- **SERP-feature blindness:** ignoring snippets/AIO/PAA/ad density in opportunity scoring.
  - Detection signal: rank + volume-only opportunity models.
  - Consequence: CTR overestimation and unrealistic forecasts.
  - Mitigation: mandatory SERP context capture and capture-risk scoring.
- **Update-window overreaction:** strategy pivots during unresolved update windows.
  - Detection signal: one-week drops during known rollout become structural narrative.
  - Consequence: oscillating strategy and confounded attribution.
  - Mitigation: update overlay + post-window confirmation policy.
- **Competitor-estimate literalism:** treating estimated competitor traffic as exact.
  - Detection signal: no uncertainty language around modeled outputs.
  - Consequence: overconfident benchmarking.
  - Mitigation: directional use + confidence bands + triangulation.
- **Brand/non-brand leakage:** unvalidated term classification.
  - Detection signal: abrupt narrative shifts after manual query checks.
  - Consequence: false acquisition-quality claims.
  - Mitigation: explicit brand dictionary + QA sample loop.
- **Geo/device blending:** global blended verdict without segmentation.
  - Detection signal: one headline score despite divergent segment behavior.
  - Consequence: hidden local or device-specific demand shifts.
  - Mitigation: segmented comparisons with like-for-like windows.
- **Fresh-window escalation:** final claims from provisional data.
  - Detection signal: incident alerts from 24-48h windows.
  - Consequence: panic changes and trust loss.
  - Mitigation: freshness gate and deferred certainty policy.

**Case-style examples (2024-2025):**

- During major rollout periods, teams often misread temporary visibility turbulence as strategy failure. Without rollout-aware controls, they confound search-system movement with product/content decisions.
- AI summary adoption caused mixed outcome narratives across sources (quality-click narrative vs aggregate CTR pressure), creating high risk if teams select only one source family.

**Sources:**

- [F1] Search Console Performance report help - https://support.google.com/webmasters/answer/7576553?hl=en
- [F2] Search Console + Search Appearance segmentation guidance - https://support.google.com/webmasters/answer/7042828?hl=en
- [F3] Search Console data and table limitations - https://support.google.com/webmasters/answer/12918484
- [F4] Search Console API query method - https://developers.google.com/webmaster-tools/v1/searchanalytics/query
- [F5] Google Trends FAQ - https://support.google.com/trends/answer/4365533
- [F6] Google Search Status incidents feed - https://status.search.google.com/incidents.json
- [F7] Pew AI summary click behavior (2025) - https://www.pewresearch.org/short-reads/2025/07/22/google-users-are-less-likely-to-click-on-links-when-an-ai-summary-appears-in-the-results/
- [F8] Semrush data source/method notes - https://www.semrush.com/kb/998-where-does-semrush-data-come-from
- [F9] Ahrefs traffic estimation caveats - https://ahrefs.com/blog/traffic-estimations-accuracy/
- [F10] Similarweb methodology - https://support.similarweb.com/hc/en-us/articles/360001631538-Similarweb-Data-Methodology
- [F11] Advanced Web Ranking SERP features CTR studies - https://advancedwebranking.com/blog/serp-features-ctr

---

### Angle 5+: SERP Shift Economics (AIO + Zero-Click)
> Additional domain-specific angle: modern SERP behavior can decouple query demand from traffic capture.

**Findings:**

- Query demand and traffic capture should be tracked as separate dimensions.
- Zero-click behavior remains structurally high in many query classes, and AI answer surfaces can further compress click opportunity.
- Official sources emphasize improved discovery and quality in AI search experiences, while independent studies often report lower aggregate outbound click rates on affected cohorts.
- Practical resolution is dual reporting: **quality indicators + aggregate capture indicators**, with confidence penalties when unresolved conflict remains.
- In 2025, AI summary coverage and language/region scope expanded, making market-specific assumptions mandatory.
- SERP opportunity models should be scenario-based (`base`, `upside`, `downside`) rather than single-point forecasts.

**Sources:**

- [C1] Google AI Overviews update (2024) - https://blog.google/products/search/ai-overviews-update-may-2024
- [C2] Google AI search quality-click framing (2025) - https://blog.google/products/search/ai-search-driving-more-queries-higher-quality-clicks/
- [C3] Google AI Overviews expansion update (2025) - https://blog.google/products-and-platforms/products/search/ai-overview-expansion-may-2025-update/
- [C4] Pew AI summary click behavior (2025) - https://www.pewresearch.org/short-reads/2025/07/22/google-users-are-less-likely-to-click-on-links-when-an-ai-summary-appears-in-the-results/
- [C5] SparkToro zero-click study (2024) - https://sparktoro.com/blog/2024-zero-click-search-study-for-every-1000-us-google-searches-only-374-clicks-go-to-the-open-web-in-the-eu-its-360/
- [C6] Semrush AI Overviews study (2025) - https://www.semrush.com/blog/semrush-ai-overviews-study/
- [C7] Ahrefs AIO clicks study update (2025) - https://ahrefs.com/blog/ai-overviews-reduce-clicks-update/
- [C8] Seer AIO CTR analysis update (2025) - https://www.seerinteractive.com/insights/aio-impact-on-google-ctr-september-2025-update

---

## Synthesis

The strongest cross-angle conclusion is that `signal-search-seo` should behave like an evidence-validation system, not a convenience wrapper over SEO APIs. In 2024-2026 search environments, demand signals are materially shaped by data-source class differences, SERP feature changes, and rapid AI surface evolution. Any skill update that keeps "collect then summarize" behavior without explicit quality gates will produce unstable conclusions.

The most important contradiction to preserve is AI search impact framing. Official narratives and independent measurement are not fully aligned, and both are plausible under different metrics. The right skill behavior is contradiction-aware reporting with confidence penalties and required next checks, not forced certainty.

Operationally, the biggest quality gains come from three upgrades:

1. provenance and comparability controls,
2. endpoint and quota-aware tool handling,
3. explicit anti-pattern blocks that prevent common interpretation failures.

The artifact schema should encode these controls so downstream users can audit confidence, not just consume a single recommendation line.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in `SKILL.md` based on research.
> Each item below has corresponding paste-ready text in the Draft section.

- [x] Replace loose pattern guidance with a strict staged workflow (`collect -> normalize -> triangulate -> classify -> verdict`).
- [x] Add source-provenance classes (`direct`, `sampled`, `modeled`) and confidence penalties when classes conflict.
- [x] Add interpretation quality gates for freshness, comparability, cross-source agreement, contradiction handling, and SERP context.
- [x] Add explicit demand-vs-capture separation and AIO/feature-aware capture-risk logic.
- [x] Expand anti-pattern handling into warning blocks with detection signal, consequence, and mitigation.
- [x] Harden tool guidance to require runtime method discovery (`op="help"`) and official endpoint verification references.
- [x] Expand schema with quality gate results, contradiction records, evidence class, and confidence grade.
- [x] Add output checklist rules that block high-confidence claims from weak evidence.
- [x] Keep existing wrapper method IDs usable, but require explicit verification before each run.

---

## Draft Content for SKILL.md

> This is the most important section. For every recommendation above, this section provides paste-ready text a future editor can insert into `SKILL.md`.
>
> Draft writing rules used here:
> - Full instruction text in second person
> - No invented provider endpoint facts
> - Clear warning blocks with detection + mitigation
> - Complete JSON schema fragment with `additionalProperties: false`

### Draft: Core operating principle and evidence contract

---
You are detecting search demand signals for exactly one query scope per run.

Your operating rule is: **evidence quality before verdict quality**.

Before you output any signal, classify every evidence source into one of three classes:

- `direct`: first-party observed data (for example Search Console for verified properties),
- `sampled`: normalized/sampled index data (for example trend index surfaces),
- `modeled`: estimated volume/traffic/competition from third-party models.

You must preserve source class labels in output. You must not merge unlike classes into one implied "truth metric."

If evidence quality is weak, contradictory, stale, or sparse, your verdict must be weak, deferred, or marked as insufficient. Never force a confident recommendation from low-quality evidence.

Result-state policy:

- `ok`: quality gates pass and contradictions are minor or resolved.
- `ok_with_conflicts`: useful evidence exists but material contradictions remain.
- `zero_results`: provider(s) returned valid empty result for scoped query.
- `insufficient_data`: evidence exists but cannot support a defensible verdict.
- `technical_failure`: collection failed due to tool/runtime/provider failure.

Non-negotiable rules:

1. Never infer durable demand direction from one short window.
2. Never treat sampled trend index as absolute volume.
3. Never treat modeled competitor traffic as exact truth.
4. Never hide source contradictions; record them explicitly.
---

### Draft: Methodology replacement text

---
## Methodology

Use this exact sequence for each run:

### Step 0: Scope lock

Define one query scope:
- primary query (required),
- allowed related terms (optional),
- target geo/language (required),
- analysis window (required).

If scope is ambiguous, stop and request clarification.

### Step 1: Collect baseline evidence

Collect at least:
1. one trend-oriented signal,
2. one volume/planning-oriented signal,
3. one SERP context snapshot.

Add first-party observed data when available.  
Single-source runs are allowed only with explicit confidence cap and strong limitations.

### Step 2: Normalize for comparability

Before interpretation:
- align geography, language, and time-window across providers,
- align segment dimensions (device/search type) where possible,
- mark mismatch in `limitations` if alignment is imperfect.

Do not compare unaligned windows as if they were equivalent.

### Step 3: Triangulate direction

Compare direction, not exact counts:
- growth,
- decline,
- breakout,
- seasonal pattern,
- ambiguous/mixed.

When sources disagree, add contradiction records and reduce confidence.

### Step 4: Capture-opportunity adjustment

Separate:
- `demand_exists` (query interest signal), and
- `capture_opportunity` (click opportunity under current SERP structure).

If SERP is feature-heavy (AIO/snippet/PAA/ads), downgrade capture confidence even when demand direction is positive.

### Step 5: Apply interpretation quality gates

Run all gates:
1. Freshness gate,
2. Comparability gate,
3. Cross-source gate,
4. Contradiction gate,
5. SERP context gate,
6. Segmentation gate.

If a hard gate fails, do not produce high-confidence signals.

### Step 6: Classify signal strength

- `strong`: multi-source directional support + no hard-gate failures.
- `moderate`: plausible direction, one meaningful unresolved caveat.
- `weak`: single-source or contradictory evidence not yet resolved.

### Step 7: Confidence assignment

Use numeric `confidence` (0-1) and categorical `confidence_grade`.
If contradictions remain unresolved, confidence must be penalized.

### Step 8: Record and explain uncertainty

Always output:
- limitations,
- contradictions (if any),
- next checks that would improve confidence.

If uncertainty is high, mark `insufficient_data` or `ok_with_conflicts` instead of pretending certainty.
---

### Draft: Signal taxonomy and decision rules

---
Use these signal categories:

- `demand_growth`
- `demand_decline`
- `demand_breakout`
- `seasonal_pattern`
- `serp_competition_high`
- `serp_competition_low`
- `competitor_traffic_shift`
- `related_demand_cluster`
- `capture_risk_high`
- `capture_risk_moderate`
- `capture_risk_low`

Signal-strength rules:

1. A `strong` label requires at least two independent providers agreeing on direction.
2. A `strong` label is blocked if freshness or comparability hard gates fail.
3. A `weak` label is mandatory when only one provider family is available.

Demand vs capture rules:

- You may emit `demand_growth` with `capture_risk_high` simultaneously.
- You may not emit a single "net opportunity" claim without both dimensions.

Conflict rules:

- If official and third-party narratives diverge (for example on AIO click impact), include both in contradictions and lower confidence.
- Do not collapse contradictory sources into one sentence.
---

### Draft: Interpretation quality gates and confidence policy

---
## Interpretation Quality Gates

Before assigning any `strong` signal, all hard gates must pass.

### Gate 1: Freshness gate (hard)

- Check whether provider docs mark freshest slices as preliminary/lag-prone.
- If freshness is uncertain, keep signal at `moderate` or below.

### Gate 2: Comparability gate (hard)

- Confirm alignment of geo/language/time-window and key segmentation dimensions.
- If misaligned, confidence penalty is required.

### Gate 3: Cross-source gate (hard for strong claims)

- Require directional agreement from at least two independent sources for `strong`.
- One-source runs are capped at `confidence <= 0.60`.

### Gate 4: Contradiction gate (hard for high confidence)

- Record source conflicts explicitly.
- If unresolved contradiction has major impact, cap confidence at `0.75`.

### Gate 5: SERP context gate (hard for capture claims)

- You cannot claim strong capture opportunity without SERP context evidence.

### Gate 6: Segmentation gate (warning or hard by use case)

- Avoid blended geo/device verdicts where segment divergence is likely.
- If segmentation unavailable, add limitation and confidence penalty.

Confidence scoring guidance:

- Start `confidence = 0.50`.
- Add `+0.10` for each passed hard gate (max +0.40).
- Add `+0.05` if segmentation checks are complete.
- Subtract `-0.10` per unresolved major contradiction.
- Subtract `-0.10` if all evidence is sampled/modeled and no direct data exists.
- Cap at `0.60` for single-provider runs.

Confidence grades:

- `high`: `0.80-1.00`
- `medium`: `0.60-0.79`
- `low`: `0.40-0.59`
- `insufficient`: `<0.40`

No universal public threshold exists across all verticals; this policy is a practical, explicit framework for consistent decisions.
---

### Draft: Available tools section text

---
## Available Tools

Use tools in this order and verify methods at runtime before any call.

### 1) Discover real methods first

```python
dataforseo(op="help", args={})
google_ads(op="help", args={})
serpapi(op="help", args={})
semrush(op="help", args={})
bing_webmaster(op="help", args={})
```

If a method is not listed in `op="help"` output, do not call it.

### 2) Run baseline collection

```python
# Trend direction
dataforseo(op="call", args={"method_id": "dataforseo.trends.explore.live.v1", "keywords": ["your query"], "location_code": 2840, "language_code": "en"})

# Regional split (optional but recommended for geo-sensitive topics)
dataforseo(op="call", args={"method_id": "dataforseo.trends.subregion_interests.live.v1", "keywords": ["your query"], "location_code": 2840})

# Volume/planning baseline
google_ads(op="call", args={"method_id": "google_ads.keyword_planner.generate_historical_metrics.v1", "keywords": ["your query"], "geo_targets": ["US"]})

# Optional idea expansion
google_ads(op="call", args={"method_id": "google_ads.keyword_planner.generate_keyword_ideas.v1", "seed_keywords": ["your query"]})
```

### 3) Capture SERP context

```python
serpapi(op="call", args={"method_id": "serpapi.search.google.v1", "q": "your query", "gl": "us", "hl": "en"})

# Optional trends comparison via provider wrapper
serpapi(op="call", args={"method_id": "serpapi.search.google_trends.v1", "q": "your query", "date": "today 12-m"})
```

### 4) Add competitor visibility context

```python
semrush(op="call", args={"method_id": "semrush.analytics.keyword_reports.v1", "phrase": "your query", "database": "us"})
semrush(op="call", args={"method_id": "semrush.trends.traffic_summary.v1", "targets": ["competitor.com"]})
```

### 5) Add Bing owned-site context when relevant

```python
bing_webmaster(op="call", args={"method_id": "bing_webmaster.get_page_query_stats.v1", "siteUrl": "https://yoursite.com"})
```

Tool usage rules:

1. Use `op="help"` before calling unfamiliar methods.
2. Keep wrapper method IDs as runtime-verified values, not assumptions.
3. If provider calls fail due to limits, continue with remaining evidence and downgrade confidence.
4. Never claim provider endpoint support that you did not verify.

Official endpoint verification map (for documentation and audits):

- Google Ads: `googleAds:search`, `googleAds:searchStream`, keyword planning service methods.
- DataForSEO v3: `/v3/serp/...`, `/v3/keywords_data/...` endpoint families.
- SerpApi: `/search`, `/searches/{search_id}`.
- Semrush: query-style analytics (`type=`) + dedicated Trends/Projects API paths.
- Bing Webmaster: `api.svc/json/METHOD_NAME` protocol pattern.
---

### Draft: Anti-pattern warning blocks

---
### WARNING: Source-Class Conflation

**What it looks like:**  
You merge direct, sampled, and modeled metrics into one conclusion with no provenance labels.

**Detection signal:**  
Signal entries contain numbers but do not specify evidence class.

**Consequence if missed:**  
False confidence and unstable prioritization decisions.

**Mitigation steps:**  
1. Require `evidence_class` on every signal.  
2. Disallow strong claims from single class/source families.  
3. Penalize confidence when class conflict is unresolved.
---

### WARNING: Trend Absolutism

**What it looks like:**  
You convert normalized trend movement into absolute demand claims.

**Detection signal:**  
Output states "volume doubled" from trend index only.

**Consequence if missed:**  
Inflated TAM and topic overcommitment.

**Mitigation steps:**  
1. Label trend data as relative direction only.  
2. Corroborate with volume/planning or first-party evidence.  
3. Keep confidence low/moderate until corroborated.
---

### WARNING: SERP Feature Blindness

**What it looks like:**  
You score opportunity from rank + volume while ignoring AIO/snippets/PAA/ads.

**Detection signal:**  
No SERP feature context fields in output.

**Consequence if missed:**  
Systematic overestimation of capturable traffic.

**Mitigation steps:**  
1. Capture SERP context explicitly.  
2. Emit capture-risk signal separately from demand signal.  
3. Penalize confidence when SERP context is missing.
---

### WARNING: Update-Window Overreaction

**What it looks like:**  
You change strategic direction during unresolved major update windows.

**Detection signal:**  
Large recommendations based on short periods that overlap known status events.

**Consequence if missed:**  
Noise-chasing and confounded attribution.

**Mitigation steps:**  
1. Overlay status/incident timelines in interpretation.  
2. Use pre/during/post windows.  
3. Defer strong verdicts until stabilization.
---

### WARNING: Competitor Estimate Literalism

**What it looks like:**  
Modeled competitor traffic is treated as exact truth.

**Detection signal:**  
High-confidence exact-count claims from modeled datasets.

**Consequence if missed:**  
Overconfident benchmarking and incorrect bet sizing.

**Mitigation steps:**  
1. Use directional language.  
2. Add uncertainty caveats.  
3. Cross-check with independent evidence where possible.
---

### WARNING: Brand/Non-Brand Leakage

**What it looks like:**  
Brand and non-brand terms are mixed without QA.

**Detection signal:**  
Narrative reverses after small manual query review.

**Consequence if missed:**  
Misleading acquisition-quality conclusions.

**Mitigation steps:**  
1. Maintain explicit brand dictionary.  
2. QA sampled queries before final verdict.  
3. Record unresolved classification risk in limitations.
---

### WARNING: Fresh-Window Escalation

**What it looks like:**  
Final claims are produced from freshest provisional data.

**Detection signal:**  
Incident-level recommendation made from incomplete recent slices.

**Consequence if missed:**  
Panic changes and stakeholder trust erosion.

**Mitigation steps:**  
1. Use freshness gates.  
2. Mark provisional windows explicitly.  
3. Delay strong claims until stable window availability.
---

### Draft: Output checklist block

---
Before calling `write_artifact`, verify all checks:

- At least two provider families used (unless unavailable and explained).
- Every signal includes `provider`, `method_id`, and `evidence_class`.
- Demand and capture opportunity are reported separately.
- Contradictions are recorded when present.
- Quality gates are evaluated and included in output.
- Confidence and confidence grade are consistent.
- Limitations and next checks are concrete and actionable.

If any mandatory item fails, do not mark run as high-confidence.
---

### Draft: Artifact schema additions

```json
{
  "signal_search_seo": {
    "type": "object",
    "required": [
      "query",
      "time_window",
      "geo_language",
      "result_state",
      "evidence_summary",
      "quality_gates",
      "signals",
      "confidence",
      "confidence_grade",
      "limitations",
      "contradictions",
      "next_checks"
    ],
    "additionalProperties": false,
    "properties": {
      "query": {
        "type": "string",
        "description": "Primary keyword or query scope analyzed in this run."
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
            "type": "string",
            "description": "ISO date window start (YYYY-MM-DD)."
          },
          "end_date": {
            "type": "string",
            "description": "ISO date window end (YYYY-MM-DD)."
          },
          "freshness_note": {
            "type": "string",
            "description": "Optional note about preliminary or delayed data behavior."
          }
        }
      },
      "geo_language": {
        "type": "object",
        "required": [
          "location_code",
          "language_code"
        ],
        "additionalProperties": false,
        "properties": {
          "location_code": {
            "type": "integer",
            "description": "Primary location identifier used in provider calls."
          },
          "language_code": {
            "type": "string",
            "description": "Primary language code used in provider calls."
          },
          "market_label": {
            "type": "string",
            "description": "Human-readable market label for reporting."
          }
        }
      },
      "result_state": {
        "type": "string",
        "enum": [
          "ok",
          "ok_with_conflicts",
          "zero_results",
          "insufficient_data",
          "technical_failure"
        ],
        "description": "Run completeness and quality state."
      },
      "evidence_summary": {
        "type": "object",
        "required": [
          "providers_used",
          "evidence_classes_covered",
          "serp_snapshot_included"
        ],
        "additionalProperties": false,
        "properties": {
          "providers_used": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Provider namespaces used in this run."
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
                "provider": {
                  "type": "string"
                },
                "reason": {
                  "type": "string"
                }
              }
            },
            "description": "Optional failures encountered by provider."
          },
          "evidence_classes_covered": {
            "type": "array",
            "items": {
              "type": "string",
              "enum": [
                "direct",
                "sampled",
                "modeled"
              ]
            },
            "description": "Distinct evidence classes represented in run."
          },
          "serp_snapshot_included": {
            "type": "boolean",
            "description": "Whether SERP context was captured."
          },
          "ai_surface_exposed": {
            "type": [
              "boolean",
              "null"
            ],
            "description": "Whether AI summary/answer surface appeared in observed SERP context."
          }
        }
      },
      "quality_gates": {
        "type": "object",
        "required": [
          "freshness_gate",
          "comparability_gate",
          "cross_source_gate",
          "contradiction_gate",
          "serp_context_gate",
          "segmentation_gate"
        ],
        "additionalProperties": false,
        "properties": {
          "freshness_gate": {
            "type": "string",
            "enum": [
              "pass",
              "warn",
              "fail"
            ]
          },
          "comparability_gate": {
            "type": "string",
            "enum": [
              "pass",
              "warn",
              "fail"
            ]
          },
          "cross_source_gate": {
            "type": "string",
            "enum": [
              "pass",
              "warn",
              "fail"
            ]
          },
          "contradiction_gate": {
            "type": "string",
            "enum": [
              "pass",
              "warn",
              "fail"
            ]
          },
          "serp_context_gate": {
            "type": "string",
            "enum": [
              "pass",
              "warn",
              "fail"
            ]
          },
          "segmentation_gate": {
            "type": "string",
            "enum": [
              "pass",
              "warn",
              "fail"
            ]
          },
          "notes": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        }
      },
      "signals": {
        "type": "array",
        "minItems": 0,
        "items": {
          "type": "object",
          "required": [
            "signal_type",
            "description",
            "strength",
            "provider",
            "method_id",
            "evidence_class",
            "evidence_value",
            "window",
            "captured_at"
          ],
          "additionalProperties": false,
          "properties": {
            "signal_type": {
              "type": "string",
              "enum": [
                "demand_growth",
                "demand_decline",
                "demand_breakout",
                "seasonal_pattern",
                "serp_competition_high",
                "serp_competition_low",
                "competitor_traffic_shift",
                "related_demand_cluster",
                "capture_risk_high",
                "capture_risk_moderate",
                "capture_risk_low"
              ]
            },
            "description": {
              "type": "string"
            },
            "strength": {
              "type": "string",
              "enum": [
                "strong",
                "moderate",
                "weak"
              ]
            },
            "provider": {
              "type": "string"
            },
            "method_id": {
              "type": "string",
              "description": "Runtime wrapper method identifier used to gather this signal."
            },
            "evidence_class": {
              "type": "string",
              "enum": [
                "direct",
                "sampled",
                "modeled"
              ]
            },
            "evidence_value": {
              "type": "string",
              "description": "Key numeric or qualitative evidence snippet as observed."
            },
            "window": {
              "type": "string",
              "description": "Window reference used for this signal (for example 12m, 90d)."
            },
            "direction": {
              "type": "string",
              "enum": [
                "up",
                "down",
                "flat",
                "mixed",
                "unknown"
              ]
            },
            "serp_context": {
              "type": "array",
              "items": {
                "type": "string",
                "enum": [
                  "ai_overview",
                  "featured_snippet",
                  "people_also_ask",
                  "ads_top",
                  "ads_bottom",
                  "local_pack",
                  "shopping_results",
                  "video_results",
                  "discussion_forums",
                  "news_cluster"
                ]
              }
            },
            "source_refs": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "Optional source IDs or URLs tied to interpretation note."
            },
            "captured_at": {
              "type": "string",
              "description": "ISO-8601 timestamp when evidence was captured."
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
            "source_a",
            "source_b",
            "impact_on_confidence",
            "status"
          ],
          "additionalProperties": false,
          "properties": {
            "topic": {
              "type": "string"
            },
            "source_a": {
              "type": "string"
            },
            "source_b": {
              "type": "string"
            },
            "impact_on_confidence": {
              "type": "string",
              "enum": [
                "none",
                "minor",
                "moderate",
                "major"
              ]
            },
            "status": {
              "type": "string",
              "enum": [
                "resolved",
                "unresolved"
              ]
            },
            "resolution_plan": {
              "type": "string"
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
      "decision_summary": {
        "type": "object",
        "required": [
          "demand_verdict",
          "capture_verdict",
          "recommended_action"
        ],
        "additionalProperties": false,
        "properties": {
          "demand_verdict": {
            "type": "string",
            "enum": [
              "growth",
              "decline",
              "breakout",
              "seasonal",
              "ambiguous"
            ]
          },
          "capture_verdict": {
            "type": "string",
            "enum": [
              "favorable",
              "mixed",
              "constrained",
              "unknown"
            ]
          },
          "recommended_action": {
            "type": "string",
            "enum": [
              "prioritize_now",
              "monitor",
              "defer",
              "collect_more_data"
            ]
          }
        }
      }
    }
  }
}
```

### Draft: Recording guidance block

---
## Recording

After gathering and interpreting evidence, call:

```python
write_artifact(
  artifact_type="signal_search_seo",
  path="/signals/search-seo-{YYYY-MM-DD}",
  data={...}
)
```

One artifact per query scope per run. Do not output raw JSON in chat.

Before writing:
1. Verify `result_state` matches actual evidence quality.
2. Verify confidence/grade alignment.
3. Verify all `strong` signals passed hard quality gates.
4. Verify contradictions are recorded (if present).
5. Verify limitations and next checks are concrete.
---

### Draft: Contradiction handling block

---
### Contradiction handling

When credible sources disagree, never suppress one side.

Use this sequence:
1. Name both claims explicitly.
2. Define where each can be valid (metric/context/query class/geo/time window).
3. Reduce confidence according to unresolved impact.
4. Define next check needed to resolve contradiction.

Example:
- Claim A: AI-enabled search can improve click quality/discovery.
- Claim B: AI summary presence can reduce aggregate outbound click rate.
- Skill behavior: report both with confidence penalty, then request cohort-specific validation.
---

## Gaps & Uncertainties

- Public official documentation does not provide a single universal "SEO signal strength threshold" standard; confidence policy remains implementation-level.
- Google Trends is officially a normalized/sampled index, but extraction-stability guidance is still mostly research-driven rather than product-prescriptive.
- Some provider limits and feature availability are contract-plan specific and can change; runtime discovery and revalidation are required.
- AI search impact studies use different query sets and methodologies; exact percentages are not directly interchangeable.
- Wrapper `method_id` values in `SKILL.md` represent integration-specific surfaces; provider endpoint verification should be maintained separately to avoid false equivalence.
