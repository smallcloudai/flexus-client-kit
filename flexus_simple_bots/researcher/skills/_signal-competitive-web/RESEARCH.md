# Research: signal-competitive-web

**Skill path:** `flexus-client-kit/flexus_simple_bots/researcher/skills/signal-competitive-web/`  
**Bot:** researcher (researcher | strategist | executor)  
**Research date:** 2026-03-05  
**Status:** complete

---

## Context

`signal-competitive-web` detects competitive traction signals using external web-traffic intelligence plus marketplace demand indicators. It is useful when a team needs directional answers to questions like "which competitor is accelerating," "which acquisition channels are fragile," and "is category demand rising or just rotating across sellers."

This skill is high-impact but high-risk for false certainty. Similarweb/Semrush traffic values are modeled estimates, not first-party analytics; marketplace indicators (Amazon BSR, eBay sold data proxies) are also partial views. Research in 2024-2026 consistently shows strong value for trend direction and relative movement, while also warning that absolute values, cross-provider mixing, and single-source interpretation create avoidable decision errors.

The practical goal of this research is to make SKILL instructions operationally safe: evidence-first collection, explicit confidence ranges, contradiction handling, policy/access constraints, and anti-pattern blocks that prevent common mistakes.

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

- No generic filler ("it is important to...", "best practices suggest...") without concrete backing
- No invented tool names, method IDs, or API endpoints - only verified real ones
- Contradictions between sources are explicitly noted, not silently resolved
- Volume: findings section should be 800-4000 words (too short = shallow, too long = unsynthesized)

Gate check for this file: passed. Contradictions are called out explicitly (accuracy claims, restricted API access vs public expectations, and leading vs lagging signal disagreements), and older references are marked evergreen.

---

## Research Angles

Each core angle was researched by a separate sub-agent, plus one additional domain-specific angle.

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

Practitioner consensus in 2024-2026 is to treat external traffic intelligence as directional context, not absolute truth. Similarweb and Semrush both document differences from Google Analytics and recommend relative trend analysis; practical workflow is "within-provider trend first, cross-provider triangulation second," not raw-number pooling.

Methodology updates in 2024 matter operationally. Similarweb's 2024 data-version update reran history with broader coverage and algorithm changes. This is a structural break risk: trend pipelines that do not mark July 2024 as a re-baseline point can interpret methodology change as market movement.

On Amazon, good practice separates high-frequency leading indicators from slower confirmation indicators. Best Sellers / Movers & Shakers can show near-real-time movement, while Search Query Performance/Search Catalog Performance reports in SP-API are period-bounded (`WEEK`, `MONTH`, `QUARTER`) and should be interpreted as lagged confirmation rather than same-day truth.

On eBay, Product Research/Terapeak-style sold-data views are higher-value demand evidence than active-listing search alone. Completed listings are short-window context; stronger demand inference uses sold-price and sell-through context where access is available.

Triangulation is not optional. Independent benchmark studies continue to show material deviation between modeled web-traffic estimates and first-party analytics. The robust workflow is to combine independent signal families (traffic direction + marketplace movement + price/offer behavior) and downgrade confidence when they diverge.

**Sources:**
- Similarweb, *Similarweb vs Google Analytics* (2025): [https://www.similarweb.com/blog/daas/data-basics/similarweb-vs-google-analytics](https://www.similarweb.com/blog/daas/data-basics/similarweb-vs-google-analytics)
- Similarweb support, *2024 Data Version Update* (2024): [https://support.similarweb.com/hc/en-us/articles/18876356573725-Everything-you-need-to-know-about-Similarweb-s-2024-Data-Version-Update](https://support.similarweb.com/hc/en-us/articles/18876356573725-Everything-you-need-to-know-about-Similarweb-s-2024-Data-Version-Update)
- Semrush KB, *Traffic & Market vs GA* (evergreen vendor doc): [https://www.semrush.com/kb/924-traffic-analytics-google-analytics](https://www.semrush.com/kb/924-traffic-analytics-google-analytics)
- Semrush KB, *How traffic intelligence is modeled* (evergreen vendor doc): [https://www.semrush.com/kb/1211-how-semrush-turns-traffic-data-into-traffic-intelligence](https://www.semrush.com/kb/1211-how-semrush-turns-traffic-data-into-traffic-intelligence)
- Amazon SP-API changelog, new BA report types (2025): [https://developer-docs.amazon.com/sp-api/changelog/update-added-new-search-query-performance-and-search-catalog-performance-analytics-report-types](https://developer-docs.amazon.com/sp-api/changelog/update-added-new-search-query-performance-and-search-catalog-performance-analytics-report-types)
- Amazon SP-API analytics report-type values (evergreen API reference): [https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics)
- Amazon Best Sellers (live 2026): [https://www.amazon.com/bestsellers](https://www.amazon.com/bestsellers)
- Amazon Movers & Shakers (live 2026): [https://www.amazon.com/gp/movers-and-shakers/](https://www.amazon.com/gp/movers-and-shakers/)
- Amazon seller blog, BSR interpretation (2025): [https://sell.amazon.com/blog/amazon-best-sellers-rank](https://sell.amazon.com/blog/amazon-best-sellers-rank)
- eBay help, Terapeak/Product Research (updated live, 2024-2026 use): [https://www.ebay.com/help/selling/selling-tools/terapeak-research?id=4853&locale=en-US](https://www.ebay.com/help/selling/selling-tools/terapeak-research?id=4853&locale=en-US)
- Springer ICANTCI study on GA vs Similarweb (2025): [https://link.springer.com/chapter/10.1007/978-3-031-86072-0_5](https://link.springer.com/chapter/10.1007/978-3-031-86072-0_5)
- PLOS/PubMed traffic comparison (2022, evergreen): [https://pubmed.ncbi.nlm.nih.gov/35622858/](https://pubmed.ncbi.nlm.nih.gov/35622858/)

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

The core stack for this skill is still valid: Similarweb for web-traffic intelligence, Amazon SP-API for catalog and offer context, and eBay APIs for listing discovery plus restricted marketplace-sales intelligence. The key update is that access and interpretation constraints are more important than adding more vendors.

Similarweb API V5 remains active with ongoing changelog activity in 2024-2026. It provides website traffic/engagement and related capabilities, but with plan-gated access, metric-credit billing, and documented rate/concurrency constraints. Practical implication: query planning and metric budget discipline are required in production.

Amazon SP-API gives strong building blocks for marketplace demand context, but not "web traffic." Verified operation families relevant here include Catalog Items (`searchCatalogItems`, `getCatalogItem`) and Product Pricing operations (`getItemOffers`, batch variants). Usage plans are operation-specific and often low by default; deprecations/removals continued through 2024-2026, so version pinning is mandatory.

eBay Browse `search` is strong for active listing surface discovery but is not a full sold-history analytics endpoint. eBay Marketplace Insights is materially more relevant for transaction-style intelligence, but access is restricted and governed by stricter licensing terms. This creates a frequent pipeline pattern: open Browse for broad coverage, restricted Insights where entitled.

Adjacent alternatives (Semrush Trends API, DataForSEO clickstream) are useful for triangulation and geo/keyword demand context, but they do not replace marketplace sold-item intelligence. The best use is as corroboration when primary providers are missing coverage.

**Capability matrix (practical summary):**

- Similarweb API: strong for web trend direction and channel/geo mix; weak for transaction-ground-truth.
- Amazon SP-API: strong for catalog/offer/marketplace context; weak for direct competitor web traffic.
- eBay Browse: strong for active listing inventory signals; weak for historical sold-depth.
- eBay Marketplace Insights: strong for richer market insight where approved; weak in availability due restrictions.
- Semrush/DataForSEO: strong for supplemental trend triangulation; weak as sole decision basis.

**Sources:**
- Similarweb developer docs: [https://developers.similarweb.com/docs/similarweb-web-traffic-api](https://developers.similarweb.com/docs/similarweb-web-traffic-api)
- Similarweb changelog: [https://developers.similarweb.com/changelog](https://developers.similarweb.com/changelog)
- Similarweb data credits model: [https://docs.similarweb.com/api-v5/guides/data-credits-calculations](https://docs.similarweb.com/api-v5/guides/data-credits-calculations)
- Similarweb pricing/packages: [https://www.similarweb.com/corp/pricing/](https://www.similarweb.com/corp/pricing/) and [https://www.similarweb.com/packages/marketing/](https://www.similarweb.com/packages/marketing/)
- Amazon SP-API usage plans/rate limits (evergreen API reference): [https://developer-docs.amazon.com/sp-api/docs/usage-plans-and-rate-limits](https://developer-docs.amazon.com/sp-api/docs/usage-plans-and-rate-limits)
- Amazon SP-API Catalog Items v2022-04-01 reference (evergreen API reference): [https://developer-docs.amazon.com/sp-api/docs/catalog-items-api-v2022-04-01-reference](https://developer-docs.amazon.com/sp-api/docs/catalog-items-api-v2022-04-01-reference)
- Amazon SP-API `searchCatalogItems`: [https://developer-docs.amazon.com/sp-api/reference/searchcatalogitems](https://developer-docs.amazon.com/sp-api/reference/searchcatalogitems)
- Amazon SP-API `getCompetitiveSummary` (pricing family): [https://developer-docs.amazon.com/sp-api/reference/getcompetitivesummary](https://developer-docs.amazon.com/sp-api/reference/getcompetitivesummary)
- Amazon deprecations + 2025 reminder: [https://developer-docs.amazon.com/sp-api/docs/sp-api-deprecations](https://developer-docs.amazon.com/sp-api/docs/sp-api-deprecations), [https://developer-docs.amazon.com/sp-api/changelog/deprecation-reminders-february-26-2025](https://developer-docs.amazon.com/sp-api/changelog/deprecation-reminders-february-26-2025)
- eBay Browse `search`: [https://developer.ebay.com/api-docs/buy/browse/resources/item_summary/methods/search](https://developer.ebay.com/api-docs/buy/browse/resources/item_summary/methods/search)
- eBay API call limits: [https://developer.ebay.com/develop/get-started/api-call-limits](https://developer.ebay.com/develop/get-started/api-call-limits)
- eBay Marketplace Insights overview: [https://developer.ebay.com/api-docs/buy/marketplace-insights/overview.html](https://developer.ebay.com/api-docs/buy/marketplace-insights/overview.html)
- eBay API License Agreement (2025): [https://developer.ebay.com/join/api-license-agreement](https://developer.ebay.com/join/api-license-agreement)
- Semrush API basics (updated 2026): [https://developer.semrush.com/api/basics/how-to-get-api](https://developer.semrush.com/api/basics/how-to-get-api)
- Semrush Trends API overview: [https://developer.semrush.com/api/v3/trends/welcome-to-trends-api/](https://developer.semrush.com/api/v3/trends/welcome-to-trends-api/)
- DataForSEO clickstream overview and limits: [https://docs.dataforseo.com/v3/keywords_data/clickstream_data/overview/](https://docs.dataforseo.com/v3/keywords_data/clickstream_data/overview/) and [https://dataforseo.com/help-center/rate-limits-and-request-limits](https://dataforseo.com/help-center/rate-limits-and-request-limits)

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

Interpretation quality is mostly about comparability and sample adequacy. Similarweb explicitly signals higher confidence above larger monthly-visit bases and warns about low-traffic instability. In practice, signals from very small domains are often unusable for hard decisions unless corroborated.

Google Trends is frequently misused in this domain. Its values are normalized (`0-100`) within each query context and are not absolute demand. "Breakout" is a specific >5000% growth label in rising related queries; it can be a useful spike detector but is noisy without confirmation from independent data.

GA4 anomaly detection guidance is useful as a general interpretation pattern even when analyzing external datasets: meaningful anomalies require adequate historical windows and sufficient segment size. The documented training windows (2 weeks hourly, 90 days daily, 32 weeks weekly) are a practical reminder to avoid overreacting to short, uncontextualized windows.

Seasonality and event effects remain a top source of false positives. Prime Day/holiday windows can generate large but temporary movement; consistent methodology compares same-period year-over-year or multi-period smoothed baselines before claiming structural demand change.

Cross-provider disagreement is expected, not exceptional. Vendor docs emphasize model quality, while independent studies continue to show material variance from first-party systems. The correct response is a confidence rubric with explicit contradiction penalties rather than choosing one provider as absolute truth.

**Signal vs noise heuristics (operational):**

- Robust: multi-period direction agreement across at least two independent signal families.
- Robust: marketplace movement with consistent price/availability context.
- Noisy: one-period spikes, low-sample domains, un-rebased post-methodology-change jumps.
- Noisy: mixed provider absolute numbers presented as directly comparable.

**Sources:**
- Similarweb data accuracy and confidence notes (evergreen vendor docs): [https://support.similarweb.com/hc/en-us/articles/360002219177](https://support.similarweb.com/hc/en-us/articles/360002219177) and [https://support.similarweb.com/hc/en-us/articles/360002329778-Similarweb-vs-Direct-Measurement](https://support.similarweb.com/hc/en-us/articles/360002329778-Similarweb-vs-Direct-Measurement)
- Similarweb 2024 methodology refresh: [https://support.similarweb.com/hc/en-us/articles/18876356573725-Everything-you-need-to-know-about-Similarweb-s-2024-Data-Version-Update](https://support.similarweb.com/hc/en-us/articles/18876356573725-Everything-you-need-to-know-about-Similarweb-s-2024-Data-Version-Update)
- Google Trends data FAQ (evergreen): [https://support.google.com/trends/answer/4365533?hl=en](https://support.google.com/trends/answer/4365533?hl=en)
- Google Trends breakout definition (evergreen): [https://support.google.com/trends/answer/4355000?hl=en](https://support.google.com/trends/answer/4355000?hl=en)
- Google Analytics 4 anomaly detection (evergreen GA4 doc): [https://support.google.com/analytics/answer/9517187](https://support.google.com/analytics/answer/9517187)
- Google Analytics 4 trend-change detection: [https://support.google.com/analytics/answer/12207035?hl=en](https://support.google.com/analytics/answer/12207035?hl=en)
- Semrush data source methodology (evergreen vendor doc with 2026 stats context): [https://www.semrush.com/kb/998-where-does-semrush-data-come-from](https://www.semrush.com/kb/998-where-does-semrush-data-come-from)
- Reuters + Adobe Prime Day signal context (2024): [https://www.reuters.com/business/retail-consumer/amazon-prime-day-boosts-us-online-sales-142-bln-adobe-says-2024-07-18/](https://www.reuters.com/business/retail-consumer/amazon-prime-day-boosts-us-online-sales-142-bln-adobe-says-2024-07-18/)
- Springer ICANTCI study (2025): [https://link.springer.com/chapter/10.1007/978-3-031-86072-0_5](https://link.springer.com/chapter/10.1007/978-3-031-86072-0_5)
- PLOS/PubMed comparison study (2022, evergreen): [https://pubmed.ncbi.nlm.nih.gov/35622858/](https://pubmed.ncbi.nlm.nih.gov/35622858/)

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

1) **Cross-provider raw-number mixing**  
Detection: dashboards that combine Similarweb visits, Semrush visits, and search-traffic proxies as if same unit.  
Consequence: false rank ordering and noisy strategic actions.  
Mitigation: compare within-provider indexed trends, then triangulate direction only.

2) **Point-estimate absolutism**  
Detection: one "true traffic number" without confidence range or source caveats.  
Consequence: overconfident recommendations from estimated data.  
Mitigation: always include uncertainty bands and confidence tier.

3) **BSR as direct demand truth**  
Detection: statements mapping BSR movement directly to stable unit demand.  
Consequence: demand overstatement during event windows.  
Mitigation: combine BSR movement with offer, price, and period-aligned context.

4) **Ignoring seasonality/event windows**  
Detection: Prime Day/Cyber period interpreted as structural baseline shift.  
Consequence: over-forecasting and post-event whiplash.  
Mitigation: event-aware baseline plus same-period YoY checks.

5) **Bot/referral spike blindness**  
Detection: sharp traffic spikes with weak engagement/marketplace corroboration.  
Consequence: phantom-demand interpretation.  
Mitigation: add hygiene checks and corroboration requirement.

6) **Normalized-index misuse**  
Detection: Google Trends `0-100` treated as absolute volume; separate query windows compared as equal scales.  
Consequence: distorted TAM and trend strength claims.  
Mitigation: preserve consistent query context and use Trends as directional only.

7) **Policy/access blind spots**  
Detection: 403/429/schema changes interpreted as market signals.  
Consequence: false decline/volatility conclusions.  
Mitigation: classify collection artifacts separately (`access_artifact`, `throttle_artifact`, `schema_change_artifact`).

8) **Review/social proxy contamination**  
Detection: review/follower spikes detached from independent market signals.  
Consequence: manipulated-demand false positives.  
Mitigation: cross-signal corroboration and integrity-risk flags.

**Bad output vs good output examples (short):**

- Bad: "A is 2x bigger than B because one provider shows 2x visits."  
  Good: "Provider estimates are directional; both providers show A accelerating vs B in the same period."
- Bad: "BSR up means permanent demand increase."  
  Good: "BSR improvement is a leading signal; confidence stays medium until multi-period confirmation."
- Bad: "Traffic spike proves channel-market fit."  
  Good: "Spike is flagged as potential bot/referral artifact until engagement and marketplace evidence align."

**Sources:**
- Similarweb methodology and direct-measurement caveats: [https://support.similarweb.com/hc/en-us/articles/360001631538-Similarweb-Data-Methodology](https://support.similarweb.com/hc/en-us/articles/360001631538-Similarweb-Data-Methodology), [https://support.similarweb.com/hc/en-us/articles/360002329778-Similarweb-vs-Direct-Measurement](https://support.similarweb.com/hc/en-us/articles/360002329778-Similarweb-vs-Direct-Measurement)
- Semrush clickstream explainer (2025): [https://www.semrush.com/blog/what-is-clickstream-data/](https://www.semrush.com/blog/what-is-clickstream-data/)
- Amazon BSR explainer (2025): [https://sell.amazon.com/blog/amazon-best-sellers-rank](https://sell.amazon.com/blog/amazon-best-sellers-rank)
- Amazon Movers & Shakers (live 2026): [https://www.amazon.com/gp/movers-and-shakers](https://www.amazon.com/gp/movers-and-shakers)
- Google Trends FAQ: [https://support.google.com/trends/answer/4365533?hl=en](https://support.google.com/trends/answer/4365533?hl=en)
- Imperva Bad Bot Report (2024): [https://www.imperva.com/resources/resource-library/reports/2024-bad-bot-report/](https://www.imperva.com/resources/resource-library/reports/2024-bad-bot-report/)
- FTC fake review final rule (2024): [https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials](https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials)
- eBay API limits and restricted API governance: [https://developer.ebay.com/develop/get-started/api-call-limits](https://developer.ebay.com/develop/get-started/api-call-limits), [https://developer.ebay.com/join/api-license-agreement](https://developer.ebay.com/join/api-license-agreement)
- SparkToro comparison study (older, evergreen): [https://sparktoro.com/blog/which-3rd-party-traffic-estimate-best-matches-google-analytics/](https://sparktoro.com/blog/which-3rd-party-traffic-estimate-best-matches-google-analytics/)
- Ahrefs estimate-accuracy study (older, evergreen): [https://ahrefs.com/blog/traffic-estimations-accuracy/](https://ahrefs.com/blog/traffic-estimations-accuracy/)

---

### Angle 5+: Policy, Access, and Compliance Constraints
> Additional domain-specific angle: legal and platform-policy constraints that affect data collection validity, interpretation, and output safety.

**Findings:**

Amazon SP-API policy boundaries are tighter than many "competitive intel" assumptions. AUP and policy docs restrict certain data-use patterns, while restricted operations require explicit role approval and restricted-data tokens. Skill instructions must fail closed on entitlement uncertainty rather than silently producing partial outputs.

eBay's 2025 API License Agreement materially emphasizes restricted APIs and use constraints for market/pricing behavior data. This is operationally important for Marketplace Insights: entitlement must be explicit, and downstream redistribution/derived-analysis use needs policy-aware checks.

Data-handling and schema-change policy events can mimic market events. eBay's 2025 data-handling update (jurisdiction-dependent field behavior changes) is a concrete example of why schema-change detectors belong in signal pipelines.

Similarweb's legal/terms framing reinforces that traffic values are estimated and license-governed. This does not reduce value for directional analysis, but it requires explicit "estimated" labeling, uncertainty communication, and controlled data-sharing behavior.

Regulatory enforcement hardened in 2024-2026 against fake reviews and deceptive social proof (FTC final rule and UK/CMA actions). Any demand signal pipeline that consumes reviews/social cues should include integrity-risk flags and corroboration requirements.

**Sources:**
- Amazon SP-API policies/agreements index: [https://developer-docs.amazon.com/sp-api/docs/policies-and-agreements](https://developer-docs.amazon.com/sp-api/docs/policies-and-agreements)
- Amazon restricted data token guide: [https://developer-docs.amazon.com/sp-api/docs/authorization-with-the-restricted-data-token](https://developer-docs.amazon.com/sp-api/docs/authorization-with-the-restricted-data-token)
- Amazon AUP: [https://sellercentral.amazon.com/mws/static/policy?documentType=AUP&locale=en_US](https://sellercentral.amazon.com/mws/static/policy?documentType=AUP&locale=en_US)
- Amazon DPP: [https://sellercentral.amazon.com/mws/static/policy?documentType=DPP&locale=en_US](https://sellercentral.amazon.com/mws/static/policy?documentType=DPP&locale=en_US)
- eBay API License Agreement (Sept 2025): [https://developer.ebay.com/join/api-license-agreement](https://developer.ebay.com/join/api-license-agreement)
- eBay data-handling update (effective Sept 2025): [https://developer.ebay.com/api-docs/static/data-handling-update.html](https://developer.ebay.com/api-docs/static/data-handling-update.html)
- Similarweb Terms (updated 2025): [https://www.similarweb.com/corp/legal/terms/](https://www.similarweb.com/corp/legal/terms/)
- FTC fake reviews final rule (2024): [https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials](https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials)
- Federal Register final rule publication (2024): [https://www.federalregister.gov/documents/2024/08/22/2024-18519/trade-regulation-rule-on-the-use-of-consumer-reviews-and-testimonials](https://www.federalregister.gov/documents/2024/08/22/2024-18519/trade-regulation-rule-on-the-use-of-consumer-reviews-and-testimonials)
- UK fake reviews/hidden fees enforcement (2025): [https://www.gov.uk/government/news/fake-reviews-and-sneaky-hidden-fees-banned-once-and-for-all](https://www.gov.uk/government/news/fake-reviews-and-sneaky-hidden-fees-banned-once-and-for-all)
- CMA undertakings with Google/Amazon on fake reviews (2025): [https://www.gov.uk/government/news/cma-secures-important-changes-from-google-to-tackle-fake-reviews](https://www.gov.uk/government/news/cma-secures-important-changes-from-google-to-tackle-fake-reviews), [https://www.gov.uk/government/news/amazon-gives-undertakings-to-cma-to-curb-fake-reviews](https://www.gov.uk/government/news/amazon-gives-undertakings-to-cma-to-curb-fake-reviews)

---

## Synthesis

Across sources, the strongest pattern is that this skill should optimize for decision quality, not data volume. In 2024-2026, external web-traffic and marketplace signals became easier to access, but also more likely to be misinterpreted if methodology changes, policy constraints, and cross-source disagreement are not explicitly modeled.

The key contradiction is not "which provider is right," but "which provider is fit for which claim." Vendor documentation highlights robust estimation capability; independent and comparative studies show meaningful deviation from first-party analytics. These two statements can both be true. The operational consequence is a confidence system with contradiction penalties, not provider absolutism.

A second important contradiction is lead-vs-lag signal timing. Amazon Best Sellers/Movers can move quickly, while periodized analytics and some marketplace evidence arrive slower. Teams that do not separate leading and confirming indicators overreact to transient movement. The best practice is two-speed interpretation with persistence checks.

The research also shows policy/access as a first-class modeling concern. Restricted API entitlement, deprecations, dynamic limits, and legal use boundaries are not administrative footnotes; they directly affect whether apparent signal shifts are market reality or collection artifacts. This must be encoded in SKILL methodology and schema.

Net result: SKILL.md should move from "tool list + heuristics" to a rigorous evidence protocol: preflight access checks, triangulation workflow, explicit confidence rubric, anti-pattern detection blocks, and structured artifact metadata for provenance, contradictions, and policy-distortion flags.

---

## Recommendations for SKILL.md

- [ ] Add an explicit triangulation protocol (traffic direction + marketplace demand + offer/price context) with mandatory persistence checks before verdicts.
- [ ] Replace inaccurate tool argument examples with verified method syntax used by current integrations (`query`/`asin` for Amazon and eBay wrappers).
- [ ] Add a preflight step (`status` / `list_methods`) and entitlement-awareness guidance before data collection.
- [ ] Add a structural-break rule for provider model updates (especially Similarweb Jul 2024) and require re-baselining.
- [ ] Add a confidence rubric (0-1) with bins and contradiction penalties.
- [ ] Add signal-vs-noise heuristics, including low-sample safeguards and seasonality/event controls.
- [ ] Add anti-pattern warning blocks with detection signal, consequence, mitigation.
- [ ] Add policy/access guardrails for restricted APIs, ToS constraints, and fake-review contamination risk.
- [ ] Expand output quality requirements: explicit estimated labels, source provenance, data freshness, contradiction section, and `insufficient_data` handling.
- [ ] Extend artifact schema with evidence references, freshness metadata, comparability context, and policy-distortion flags.

---

## Draft Content for SKILL.md

> This is the most important section. For every recommendation above, write the actual text that should go into SKILL.md.

### Draft: Core mode and evidence policy

---
### Core mode: evidence-first triangulation

You are detecting competitive traction signals from **estimated external data**, not first-party truth. Every claim must be tied to at least one concrete data point and at least one named provider. You must never present estimated traffic numbers as ground truth.

Your default evidence rule is:
1. **Collect directional web-traffic evidence** (trend, channel mix, geography) from Similarweb.
2. **Collect marketplace demand evidence** (catalog/offer movement for Amazon and listing/sales context for eBay).
3. **Triangulate direction** across signal families before final classification.

A signal is actionable only when it persists across at least two observation points in the same direction, or when one strong signal is corroborated by an independent signal family. If signals conflict, you downgrade confidence and explicitly describe the conflict instead of forcing a single answer.

Always label modeled values with `estimated` and provider name (for example: `"2.4M visits/mo estimated (Similarweb)"`).
---

### Draft: Data collection workflow

---
### Collection workflow (must follow in order)

Before collecting any signal data, run a preflight:
1. Confirm tool availability and method names with provider `status`/`list_methods` calls.
2. Confirm time window, geography, and category scope for this run.
3. Confirm you can retrieve at least one traffic source and one marketplace source.

Then execute this sequence:

1. **Web traffic baseline**
   - Pull traffic and engagement for each target domain.
   - Pull traffic sources and geography in the same date window.
   - Pull similar-sites to discover adjacent competitors only after primary competitors are analyzed.
   - Compute directional changes (MoM or rolling period trend) rather than relying on absolute values.

2. **Amazon marketplace context**
   - Use catalog search to discover ASINs for the category and competitor-relevant products.
   - Resolve critical ASIN details when needed.
   - Pull offer snapshots for selected ASINs to understand price/offer pressure context.
   - Treat BSR changes as leading indicators, not standalone demand proof.

3. **eBay marketplace context**
   - Use Browse search for active listing inventory and price context.
   - Use Marketplace Insights sold-item search where entitled; if access is blocked, explicitly record restricted-access limitation.
   - Never treat missing restricted API access as demand decline.

4. **Triangulation and classification**
   - If traffic trend and marketplace trend agree for two consecutive checks: classify as stronger traction signal.
   - If they disagree: classify as mixed signal and downgrade confidence.
   - If data is sparse, low-sample, or rate-limited: return directional-only output with explicit limitations.

Do not skip directly from a single provider response to a final "market pull" verdict.
---

### Draft: Interpretation rules and confidence scoring

---
### Data interpretation rules

Use these interpretation rules for every run:

1. **Cross-provider comparability**
   - Compare direction within each provider first.
   - Do not compare raw absolute values across different providers as equivalent units.
   - If cross-provider direction conflicts, explain both and lower confidence.

2. **Sample and quality safeguards**
   - Treat low-volume domains as lower-confidence signals (Similarweb small-site caveat).
   - Require a second source for any unusually large jump.
   - Mark post-methodology-update periods as potential structural breaks until re-baselined.

3. **Seasonality and event controls**
   - Flag known event windows (for example, Prime Day, holiday periods).
   - Prefer same-period comparisons (YoY or equivalent seasonal window) before claiming structural demand change.
   - Single-period spikes are provisional by default.

4. **Marketplace signal interpretation**
   - Amazon BSR movement indicates rank movement, not direct unit volume.
   - eBay active listing counts indicate supply pressure, not guaranteed sell-through.
   - Marketplace Insights sold data (if available) is stronger demand evidence than listing-only signals.

### Confidence rubric (0 to 1)

Score confidence using weighted evidence:

- `source_quality` (0.00-0.30): first-party-like marketplace evidence > modeled external estimates.
- `cross_signal_agreement` (0.00-0.25): independent signal families agree on direction.
- `temporal_persistence` (0.00-0.20): signal persists over at least two periods.
- `scope_alignment` (0.00-0.10): geo/time/category scope is consistent.
- `data_freshness` (0.00-0.10): evidence is recent within run window.
- `methodology_stability` (0.00-0.05): no unresolved provider model-break effects.

Apply penalties:
- `-0.15` if unresolved cross-provider contradiction remains.
- `-0.10` if one core signal family is missing.
- `-0.10` if restricted-access or rate-limit artifacts materially reduce coverage.

Confidence bins:
- `0.85-1.00`: high confidence.
- `0.65-0.84`: moderate confidence.
- `0.45-0.64`: directional only.
- `<0.45`: low confidence; avoid strong recommendations.

If confidence is below `0.45`, use `result_state="insufficient_data"` unless a high-impact signal is independently corroborated.
---

### Draft: Available Tools

---
## Available Tools

Use only verified method IDs. Do not invent methods or endpoint names. Always prefer `op="status"` and `op="list_methods"` when uncertain.

```python
# Similarweb: traffic direction and channel composition
similarweb(
  op="call",
  args={
    "method_id": "similarweb.traffic_and_engagement.get.v1",
    "domain": "competitor.com",
    "start_date": "2025-01",
    "end_date": "2025-12",
    "country": "us",
    "granularity": "monthly"
  }
)

similarweb(
  op="call",
  args={
    "method_id": "similarweb.traffic_sources.get.v1",
    "domain": "competitor.com",
    "start_date": "2025-01",
    "end_date": "2025-12",
    "country": "us"
  }
)

similarweb(
  op="call",
  args={
    "method_id": "similarweb.traffic_geography.get.v1",
    "domain": "competitor.com",
    "start_date": "2025-01",
    "end_date": "2025-12"
  }
)

similarweb(
  op="call",
  args={
    "method_id": "similarweb.similar_sites.get.v1",
    "domain": "competitor.com"
  }
)

# Amazon integration wrappers (verified local method syntax)
amazon(op="status")
amazon(op="list_methods")

amazon(
  op="call",
  args={
    "method_id": "amazon.catalog.search_items.v1",
    "query": "product category",
    "limit": 10
  }
)

amazon(
  op="call",
  args={
    "method_id": "amazon.catalog.get_item.v1",
    "asin": "B0EXAMPLE123"
  }
)

amazon(
  op="call",
  args={
    "method_id": "amazon.pricing.get_item_offers_batch.v1",
    "asin": "B0EXAMPLE123"
  }
)

amazon(
  op="call",
  args={
    "method_id": "amazon.pricing.get_listing_offers_batch.v1",
    "asin": "B0EXAMPLE123"
  }
)

# eBay integration wrappers (verified local method syntax)
ebay(op="status")
ebay(op="list_methods")

ebay(
  op="call",
  args={
    "method_id": "ebay.browse.search.v1",
    "query": "product category",
    "limit": 25
  }
)

ebay(
  op="call",
  args={
    "method_id": "ebay.marketplace_insights.item_sales_search.v1",
    "query": "product category",
    "limit": 25
  }
)
```

Tool usage rules:
1. Use Similarweb for directional trends and channel/geo patterns, not transaction truth.
2. Use Amazon methods for catalog and offer context; these are marketplace signals, not direct web traffic.
3. Use eBay Browse for active listing context; use Marketplace Insights sold data only when access is approved.
4. If a method returns `403`, `429`, or provider auth failure, record that as a collection limitation and continue with available sources.
5. Do not replace missing methods with guessed equivalents.
---

### Draft: Anti-pattern warning blocks

```md
> [!WARNING] Anti-pattern: Cross-Provider Raw Number Mixing
> **What it looks like:** direct comparison of Similarweb totals vs other provider totals as equivalent units.
> **Detection signal:** final narrative says "A is 2x B" using mixed-provider absolute numbers.
> **Consequence:** false ranking and unstable strategy decisions.
> **Mitigation:** compare direction inside each provider first, then triangulate agreement/disagreement.
```

```md
> [!WARNING] Anti-pattern: One-Period Spike Overreaction
> **What it looks like:** single weekly spike labeled as "market pull."
> **Detection signal:** no persistence check, no event-window annotation.
> **Consequence:** tactical overreaction to temporary events.
> **Mitigation:** require two-period persistence or independent corroboration before strong claims.
```

```md
> [!WARNING] Anti-pattern: BSR Equals Demand
> **What it looks like:** BSR movement converted directly into demand magnitude.
> **Detection signal:** BSR cited as sole marketplace evidence.
> **Consequence:** demand overstatement, especially during event windows.
> **Mitigation:** pair BSR with offer context, price movement, and additional marketplace indicators.
```

```md
> [!WARNING] Anti-pattern: Policy-Blind Missing Data Interpretation
> **What it looks like:** restricted-access failures treated as market decline.
> **Detection signal:** sudden null/empty fields coincide with 403/entitlement changes.
> **Consequence:** fabricated decline signals and incorrect recommendations.
> **Mitigation:** classify as access artifact and lower confidence; do not infer demand from missing restricted data.
```

```md
> [!WARNING] Anti-pattern: Review/Social Proxy Contamination
> **What it looks like:** review/follower spikes used as direct demand proof.
> **Detection signal:** review signal diverges from marketplace and traffic direction.
> **Consequence:** manipulated-demand false positives.
> **Mitigation:** add integrity-risk flag and require independent corroboration before inclusion.
```

### Draft: Compliance and access guardrails

---
### Policy, legal, and entitlement guardrails

You must use only data and APIs that are authorized for this use case. If entitlement is unknown or restricted, fail closed and log the limitation.

Required guardrails:
1. Run entitlement preflight before restricted endpoints (especially eBay Marketplace Insights and any restricted Amazon operations).
2. Keep data-use within provider terms and license constraints; do not assume redistribution or AI-training rights.
3. Treat policy-induced schema changes and masking changes as non-market artifacts.
4. Avoid personal data ingestion where possible; if unavoidable, apply minimization and retention constraints.
5. Include an explicit disclaimer in output metadata:
   - "Estimated external intelligence; not first-party ground truth."
   - "Output is for competitive intelligence, not legal advice."
   - "Respect platform terms and restricted API licenses."

If compliance/entitlement status cannot be verified, downgrade to descriptive analysis only and avoid strong recommendations.
---

### Draft: Output quality and insufficient-data rules

---
### Output quality standard

Minimum quality bar for every run:
- At least one traffic evidence item and one marketplace evidence item per target.
- Explicit provider names and `estimated` labels on modeled metrics.
- Time-window and geography scope stated in output.
- Confidence score and confidence tier included.
- At least one listed limitation when confidence is below high.
- Contradictions section included when signals disagree.

When to use each `result_state`:
- `ok`: enough evidence for directional interpretation and confidence assignment.
- `zero_results`: query returned valid but empty result set.
- `insufficient_data`: coverage, consistency, or quality is too weak for reliable conclusions.
- `technical_failure`: provider/tool failure prevented core data retrieval.

Use `insufficient_data` when:
- key sources are missing after retries,
- contradictions remain unresolved,
- access restrictions materially reduce evidence quality,
- or low-sample instability dominates the run.
---

### Draft: Schema additions

> Full JSON Schema fragment for updated/expanded artifact fields.

```json
{
  "signal_competitive_web": {
    "type": "object",
    "required": [
      "targets",
      "time_window",
      "result_state",
      "signals",
      "confidence",
      "confidence_tier",
      "limitations",
      "next_checks",
      "source_evidence",
      "contradictions",
      "policy_flags"
    ],
    "additionalProperties": false,
    "properties": {
      "targets": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Competitor domains or product categories analyzed in this run."
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
            "description": "Inclusive run start date (YYYY-MM-DD or YYYY-MM)."
          },
          "end_date": {
            "type": "string",
            "description": "Inclusive run end date (YYYY-MM-DD or YYYY-MM)."
          }
        }
      },
      "result_state": {
        "type": "string",
        "enum": [
          "ok",
          "zero_results",
          "insufficient_data",
          "technical_failure"
        ],
        "description": "Final run status after collection and quality checks."
      },
      "signals": {
        "type": "array",
        "description": "Structured signal claims produced for this run.",
        "items": {
          "type": "object",
          "required": [
            "signal_type",
            "description",
            "strength",
            "target",
            "provider",
            "data_point",
            "evidence_refs",
            "freshness_days",
            "is_estimated"
          ],
          "additionalProperties": false,
          "properties": {
            "signal_type": {
              "type": "string",
              "enum": [
                "competitor_traffic_growth",
                "competitor_traffic_decline",
                "channel_concentration",
                "new_competitor_emerging",
                "marketplace_demand_growing",
                "marketplace_demand_declining",
                "price_compression",
                "similar_sites_active"
              ],
              "description": "Normalized signal category used for downstream filtering."
            },
            "description": {
              "type": "string",
              "description": "Human-readable explanation of the signal and why it matters."
            },
            "strength": {
              "type": "string",
              "enum": [
                "strong",
                "moderate",
                "weak"
              ],
              "description": "Signal strength assigned after triangulation and quality checks."
            },
            "target": {
              "type": "string",
              "description": "Domain, brand, or category to which this signal applies."
            },
            "provider": {
              "type": "string",
              "description": "Primary provider used for this signal (for example Similarweb, Amazon, eBay)."
            },
            "data_point": {
              "type": "string",
              "description": "Key metric with units and estimate label, e.g. '2.4M visits/mo estimated (Similarweb)'."
            },
            "evidence_refs": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "IDs of source_evidence records that support this signal."
            },
            "freshness_days": {
              "type": "integer",
              "minimum": 0,
              "description": "Age of the underlying evidence in days at time of artifact creation."
            },
            "is_estimated": {
              "type": "boolean",
              "description": "True when metric is modeled/estimated rather than first-party observed."
            }
          }
        }
      },
      "confidence": {
        "type": "number",
        "minimum": 0,
        "maximum": 1,
        "description": "Composite confidence score for the overall run."
      },
      "confidence_tier": {
        "type": "string",
        "enum": [
          "high",
          "moderate",
          "directional",
          "low"
        ],
        "description": "Confidence bin derived from confidence score and contradiction penalties."
      },
      "source_evidence": {
        "type": "array",
        "description": "Evidence records with provenance and access metadata.",
        "items": {
          "type": "object",
          "required": [
            "evidence_id",
            "provider",
            "method_id",
            "captured_at",
            "scope",
            "access_level"
          ],
          "additionalProperties": false,
          "properties": {
            "evidence_id": {
              "type": "string",
              "description": "Stable ID referenced by signals.evidence_refs."
            },
            "provider": {
              "type": "string",
              "description": "Data provider name."
            },
            "method_id": {
              "type": "string",
              "description": "Tool method used to retrieve this evidence."
            },
            "captured_at": {
              "type": "string",
              "description": "ISO-8601 timestamp when evidence was collected."
            },
            "scope": {
              "type": "object",
              "required": [
                "geo",
                "period"
              ],
              "additionalProperties": false,
              "properties": {
                "geo": {
                  "type": "string",
                  "description": "Geography scope used for this evidence."
                },
                "period": {
                  "type": "string",
                  "description": "Time scope used for this evidence (e.g., 2025-01..2025-12)."
                }
              }
            },
            "access_level": {
              "type": "string",
              "enum": [
                "public",
                "standard_api",
                "restricted_api"
              ],
              "description": "Access tier used for retrieval, useful for entitlement auditing."
            }
          }
        }
      },
      "contradictions": {
        "type": "array",
        "description": "Explicitly logged source disagreements affecting confidence.",
        "items": {
          "type": "object",
          "required": [
            "topic",
            "sources",
            "impact"
          ],
          "additionalProperties": false,
          "properties": {
            "topic": {
              "type": "string",
              "description": "Short contradiction topic label."
            },
            "sources": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "Provider/source names involved in the disagreement."
            },
            "impact": {
              "type": "string",
              "enum": [
                "low",
                "medium",
                "high"
              ],
              "description": "Estimated impact of this contradiction on recommendation reliability."
            }
          }
        }
      },
      "policy_flags": {
        "type": "array",
        "description": "Policy and access artifacts that could bias interpretation.",
        "items": {
          "type": "string",
          "enum": [
            "throttle_or_access_artifact",
            "schema_change_artifact",
            "restricted_api_unavailable",
            "review_integrity_risk",
            "ad_attribution_bias",
            "methodology_break_window"
          ]
        }
      },
      "limitations": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Human-readable limitations affecting interpretation."
      },
      "next_checks": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Concrete follow-up checks to resolve uncertainty in future runs."
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Public, up-to-date, independent 2026 benchmarks quantifying error distributions by provider and vertical are limited; most robust comparisons remain vendor-authored or older peer-reviewed work (marked evergreen when used).
- eBay Marketplace Insights endpoint-level behavior is less transparently documented for non-approved developers; entitlement and payload shape can vary by account and contract.
- There is no official deterministic conversion formula from Amazon BSR to unit sales; any mapping remains model-based and should be treated as inference.
- Similarweb and Semrush methodology pages are living docs; for production SKILL instructions, model-update checkpoints should be revisited quarterly.
- Some policy/terms pages are undated live documents; they should be re-validated before strict policy assertions in production policy text.
