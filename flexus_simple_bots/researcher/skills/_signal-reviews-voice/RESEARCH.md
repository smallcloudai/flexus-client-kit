# Research: signal-reviews-voice

**Skill path:** `flexus_simple_bots/researcher/skills/signal-reviews-voice/`
**Bot:** researcher
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`signal-reviews-voice` detects voice-of-market signals from review platforms for one target scope per run (company, product, competitor set, or category). The skill should identify recurring pain themes, satisfaction gaps, and competitive weaknesses while staying evidence-first and explicit about uncertainty.

The current `SKILL.md` already has a useful baseline (provider selection, theme extraction, rating-distribution patterns, and artifact schema), but it still mixes internal wrapper method IDs with endpoint-like names and does not yet encode 2024-2026 policy/compliance and trust-signal constraints strongly enough. This research focuses on practical methodology, verified API/tool landscape, interpretation quality, and anti-pattern prevention so a future `SKILL.md` can be operationally safe and audit-ready.

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

- No generic filler without concrete backing: **passed**
- No invented tool names, method IDs, or API endpoints: **passed** (wrapper aliases are labeled as internal)
- Contradictions between sources are explicitly noted: **passed**
- Volume target met (Findings sections 800-4000 words): **passed**

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

- Mature review-intelligence workflows now put **policy/compliance gating before sentiment scoring**. 2024-2025 regulator and platform enforcement tightened expectations around fake reviews, suppression, and incentive misuse, so ingestion pipelines now need explicit exclusion rules and audit logs before any signal scoring.
- Method quality depends on **channel-specific solicitation logic**. There is a practical contradiction across ecosystems: some channels allow controlled invitation programs, while others (for example, Yelp) discourage asking for reviews directly. Effective practice is per-channel collection policy, not one solicitation workflow across providers.
- Practitioners increasingly require **source metadata as first-class evidence**, not optional context. High-quality outputs store provider, invite source, moderation status, recommendation status, and incentive disclosure status per record, then report source-mix alongside any aggregate conclusion.
- Cross-provider analytics is moving to a **two-layer scoring model**: keep platform-native metrics for operational context, then compute an internal normalized signal layer for cross-platform comparisons. This is required because platform scoring and moderation mechanics differ materially.
- Sample-size handling is operationalized as explicit decision rules. A practical baseline used in review-signal workflows is: `<10` reviews = insufficient evidence; `10-19` = directional only; `>=20` = reportable with confidence scoring. Low-N windows should use conservative shrinkage/interval logic rather than raw mean ranking.
- Practitioners separate **provisional vs settled data** because moderation lag can alter published review sets after collection. Trend alerts and strategic conclusions should run on settled windows, not latest-hour snapshots during active moderation.
- Fraud triage has shifted from sentiment-only checks to **pattern-based integrity checks**: sudden polarity spikes, duplicate/near-duplicate bursts, abnormal account behaviors, and media-triggered brigading windows all trigger hold states before narrative conclusions.
- Response operations now follow **severity-based SLAs** tied to low-star technical complaints and recency, with channel-specific mechanics respected (for example, one-public-reply constraints in some ecosystems).
- There is a real contradiction in AI-assisted response writing: some data suggests AI-style responses can be acceptable, but consumers still penalize generic templated replies. Operational resolution is AI draft + human personalization + periodic QA.
- Stronger teams segment before actioning: provider-level, region/language, review cohort (invited/organic), and account size where available. Unsegmented global averages are now considered weak evidence for roadmap or GTM decisions.
- 2025 compliance guidance (for example, UK CMA) moves from broad principles to explicit obligations: publish policies, assess risks, detect/investigate/remediate suspicious reviews, and evidence effectiveness. This should be treated as process design input, not legal footnote.
- An evergreen methodological spine remains useful: integrity, transparency, accuracy, and traceability principles (for example, ISO 20488), then layer 2024-2026 enforcement-specific controls on top.

**Contradictions to carry into skill logic:**

- **Solicitation contradiction:** structured invitation programs are allowed in some ecosystems; Yelp discourages asking for reviews. Resolution: provider-specific collection policy branch, never one-size-fits-all.
- **AI response contradiction:** efficiency gains from AI drafting vs trust loss from generic replies. Resolution: require human-in-the-loop finalization for all public responses.
- **Native score contradiction:** platform-native ratings are operationally useful but not cross-platform comparable. Resolution: retain native score and add normalized cross-provider signal layer.

**Sources:**
- [FTC final fake-reviews rule (2024)](https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials)
- [FTC reviews rule Q&A (2024)](https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers)
- [UK CMA fake-reviews guidance (2025)](https://www.gov.uk/government/publications/fake-reviews-cma208/short-guide-for-businesses-publishing-consumer-reviews-and-complying-with-consumer-protection-law)
- [Google Maps anti-abuse update (2024)](https://blog.google/products/maps/how-machine-learning-keeps-contributed-content-helpful)
- [Google Business Profile restrictions](https://support.google.com/business/answer/14114287?hl=en)
- [Trustpilot transparency report (2024)](https://assets.ctfassets.net/b7g9mrbfayuu/7p63VLqZ9vmU2TB65dVdnF/6e47d9ee81c145b5e3d1e16f81bba89a/Trustpilot_Transparency_Report_2024.pdf)
- [Trustpilot business guidelines (2026)](https://corporate.trustpilot.com/legal/for-businesses/guidelines-for-businesses/feb-2026)
- [Yelp do-not-ask policy](https://www.yelp-support.com/article/Don-t-Ask-for-Reviews%3Fl%3Den_US)
- [Yelp trust and safety report (2025)](https://trust.yelp.com/trust-and-safety-report/2025-report/)
- [G2 review validity](https://sell.g2.com/review-validity)
- [G2 review status and timelines](https://documentation.g2.com/help/docs/understanding-review-statuses-and-timelines)
- [BrightLocal review survey (2024)](https://www.brightlocal.com/research/local-consumer-review-survey-2024/)
- [BrightLocal review survey (2026)](https://www.brightlocal.com/research/local-consumer-review-survey)
- [NIST GenAI risk framework profile (2024)](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)
- [ISO 20488 (2018, evergreen)](https://www.iso.org/standard/68193.html)

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

- Real-world review signal stacks usually combine three layers: (1) review-source providers, (2) optional enrichment/NLP services, and (3) governance/normalization logic.
- Trustpilot, Yelp, Google Business Profile, G2, App Store Connect, and Google Play have documented retrieval/reply surfaces, but permissions and access models differ heavily.
- Cross-platform comparability fails when teams ignore provider constraints: partial review returns, plan-gated endpoints, owner-only APIs, moderation delays, and quota behavior.
- Text analytics APIs (AWS Comprehend, Google Cloud Natural Language, Azure AI Language) are useful for enrichment only; they are not review sources and should not be treated as independent market evidence.
- A key practical gap: publicly documented **Capterra review-retrieval endpoints** were not verified in official public docs in this pass. Treat Capterra connector methods as internal/private-contract dependent unless connector docs prove otherwise.
- Internal wrapper method IDs can be used safely only when paired with a verified vendor operation string (`HTTP method + URL/path`) and source URL.

| Platform | Verified operation examples | Auth/access pattern | Published limits/constraints | Practical use | Key limitation |
|---|---|---|---|---|---|
| Trustpilot | `GET https://api.trustpilot.com/v1/business-units/find`; `GET https://datasolutions.trustpilot.com/v1/business-units/{businessUnitId}/reviews` | API key + OAuth depending on API tier | Rate guidance documented; private APIs permissioned | B2B/B2C review retrieval and response workflows | Access tier and permission setup vary |
| Yelp Fusion | `GET https://api.yelp.com/v3/businesses/search`; `GET https://api.yelp.com/v3/businesses/{business_id_or_alias}/reviews` | Bearer API key | Plan/QPS constraints and endpoint permission caveats | Local/service competitor scan + excerpts | Reviews endpoint is limited and plan-gated |
| Google Business Profile | `GET https://mybusiness.googleapis.com/v4/{parent=accounts/*/locations/*}/reviews`; `PUT .../reviews/*/reply` | OAuth (`business.manage`) | Usage limits documented (`QPM`, edits/min) | Owner-managed location review monitoring and reply | Not a competitor-intel feed |
| Google Places API | `GET https://places.googleapis.com/v1/{name=places/*}` | API key or OAuth + field mask | Quota and billing by method/SKU | Supplemental public place context | Not moderation/reply management |
| G2 API v2 | `GET https://data.g2.com/api/v2/vendors`; `GET https://data.g2.com/api/v2/products/{product_id}/reviews` | Token + account permissions | Published rate limits and permission gating | B2B software review intelligence | Endpoint availability depends on account access |
| App Store Connect | `GET /v1/apps/{id}/customerReviews`; review response operations | JWT (ES256 private key) | Rolling rate-limit headers + role requirements | iOS app review ingestion/reply for owned apps | Not for competitor app internals |
| Google Play Developer API | `GET .../applications/{packageName}/reviews`; `POST .../{reviewId}:reply` | OAuth (`androidpublisher`) | Quota buckets by API family | Android app review ingestion/reply for owned apps | Owned app scope only |
| Bazaarvoice Conversations | `GET .../data/reviews.json` | API passkey | Rate-limit headers and key governance | Retail review retrieval (where contracted) | Contract and key governance required |
| AWS Comprehend | `DetectSentiment` | SigV4 | size/throttle constraints | Sentiment enrichment for review text | Not a source of review data |
| Google Cloud Natural Language | `POST https://language.googleapis.com/v1/documents:analyzeSentiment` | OAuth/API auth | quotas and content limits | Sentiment enrichment | Not a source of review data |
| Azure AI Language | `POST {Endpoint}/language/:analyze-text?api-version=2025-11-01` | Key or bearer | tier-based RPS/RPM limits | Sentiment/opinion enrichment | Not a source of review data |

**No official public API cases (explicit):**

- Capterra public products/reviews retrieval endpoint could not be verified in official public docs in this pass.
- For this skill, treat `capterra.*` as **connector-dependent** and require runtime connector documentation before use.
- If unavailable, record provider as `unsupported_or_unverifiable` and continue with Trustpilot/G2/Yelp plus limitations.

**Sources:**
- [Trustpilot Business Units API](https://developers.trustpilot.com/business-units-api-(public)/)
- [Trustpilot Data Solutions API](https://developers.trustpilot.com/data-solutions-api/)
- [Trustpilot authentication](https://developers.trustpilot.com/authentication)
- [Trustpilot rate limiting](https://developers.trustpilot.com/rate-limiting/)
- [Yelp business search endpoint](https://docs.developer.yelp.com/reference/v3_business_search)
- [Yelp business reviews endpoint](https://docs.developer.yelp.com/reference/v3_business_reviews)
- [Yelp rate limiting](https://docs.developer.yelp.com/docs/fusion-rate-limiting)
- [Google Business Profile reviews.list](https://developers.google.com/my-business/reference/rest/v4/accounts.locations.reviews/list)
- [Google Business Profile updateReply](https://developers.google.com/my-business/reference/rest/v4/accounts.locations.reviews/updateReply)
- [Google Business Profile limits](https://developers.google.com/my-business/content/limits)
- [Google Places place details](https://developers.google.com/maps/documentation/places/web-service/place-details)
- [G2 API v2 docs](https://data.g2.com/api/v2/docs/index.html)
- [G2 OpenAPI v2](https://data.g2.com/openapi/v2.yaml)
- [App Store Connect customer reviews](https://developer.apple.com/documentation/appstoreconnectapi/list_all_customer_reviews_for_an_app)
- [App Store Connect rate limits](https://developer.apple.com/documentation/appstoreconnectapi/identifying-rate-limits)
- [Google Play reviews.list](https://developers.google.com/android-publisher/api-ref/rest/v3/reviews/list)
- [Google Play reviews.reply](https://developers.google.com/android-publisher/api-ref/rest/v3/reviews/reply)
- [Google Play quotas](https://developers.google.com/android-publisher/quotas)
- [Bazaarvoice retrieve reviews](https://developers.bazaarvoice.com/v1.0-ConversationsAPI/reference/get_data-reviews-json)
- [AWS DetectSentiment](https://docs.aws.amazon.com/comprehend/latest/APIReference/API_DetectSentiment.html)
- [Google NLP analyzeSentiment](https://cloud.google.com/natural-language/docs/reference/rest/v1/documents/analyzeSentiment)
- [Azure analyze-text REST 2025-11-01](https://learn.microsoft.com/en-us/rest/api/language/analyze-text/analyze-text/analyze-text?view=rest-language-analyze-text-2025-11-01)
- [Gartner Digital Markets buyer discovery API](https://datainsights.gartner.com/api/buyerdiscovery/swagger/index.html)

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

- Interpretation quality now starts with a **hard integrity gate**: fake, manipulated, or policy-breaching reviews are excluded before sentiment/theme aggregation.
- Platform intervention states (warnings/restrictions/suspicious-activity states) should switch a target to **hold** for strategic conclusions; data can still be logged, but final signal claims are deferred.
- Trust strata matter: recommended/retained reviews and filtered/removed reviews should not carry equal weight. Even when exact weighting differs by team, weighting logic must be explicit.
- Raw mean shifts are weak for low-N segments. Confidence-aware methods (for example Wilson intervals for proportions) are preferred over naive average comparison.
- Trend quality improves with dual windows: short detection window (for fast anomaly detection) plus longer baseline window for stability.
- Review-bombing and brigading detection should include both numerical bursts and context cues (media events, policy disputes, coordinated posting patterns).
- De-duplication is mandatory before theme prevalence scoring; duplicate bursts otherwise inflate false certainty.
- Language handling affects reliability materially; multilingual segments should be analyzed separately before global roll-up. Low-resource language translation paths need explicit confidence downgrades.
- Cross-platform normalization should compare internal standardized changes (for example within-platform trend deltas) rather than direct star-average equivalence across providers.
- Selection bias remains large in reviews (including J-shaped distributions and participation effects), so outputs should report distribution shape and uncertainty, not just average rating.
- Practical confidence scoring should combine sample adequacy, source integrity, temporal stability, cross-source agreement, and language coverage.

**Signal vs noise guidance to encode directly:**

- **Signal:** recurring theme increases over two windows, cross-provider agreement, stable moderation state, and adequate sample.
- **Noise:** one-day polarity spike during active intervention state, duplicate bursts, or single-provider anomaly with no corroboration.
- **Do-not-conclude state:** intervention active, sample below threshold, unresolved source contradiction, or language/coverage gap.

**Sources:**
- [FTC reviews rule Q&A (2024)](https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers)
- [Federal Register final rule (2024)](https://www.federalregister.gov/documents/2024/08/22/2024-18519/trade-regulation-rule-on-the-use-of-consumer-reviews-and-testimonials)
- [UK CMA fake review guidance (2025)](https://www.gov.uk/government/publications/fake-reviews-cma208)
- [Google consumer alerts policy](https://support.google.com/contributionpolicy/answer/15178562?hl=en)
- [Yelp recommendation software](https://trust.yelp.com/recommendation-software/)
- [Yelp trust and safety report (2024)](https://trust.yelp.com/trust-and-safety-report/2024-report/)
- [Google Maps fake review update (2025)](https://blog.google/products/maps/google-business-profiles-ai-fake-reviews)
- [MAiDE-up multilingual deception dataset (2024)](https://arxiv.org/abs/2404.12938)
- [EACL cross-lingual translation reliability (2024)](https://aclanthology.org/2024.eacl-short.28/)
- [Review-bombing analysis (2024)](https://arxiv.org/abs/2405.06306)
- [Fake review detection survey (2024)](https://www.cambridge.org/core/journals/knowledge-engineering-review/article/recent-stateoftheart-of-fake-review-detection-a-comprehensive-review/F02E8339C43A62BA63EBD54A1608F785)
- [NIST control chart guidance (evergreen)](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc31.htm)
- [NIST modified z-score guidance (evergreen)](https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h.htm)
- [Wilson interval explainer (evergreen)](https://www.evanmiller.org/how-not-to-sort-by-average-rating.html)
- [J-shaped review distribution (evergreen)](https://cacm.acm.org/research/overcoming-the-j-shaped-distribution-of-product-reviews/)

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

- **Anti-pattern: Review gating and suppression.**
  - Detection signal: only promoter cohorts solicited, low variance after campaigns, or moderation actions correlated to negative sentiment rather than policy violation.
  - Consequence: distorted product/competitive conclusions plus legal risk.
  - Mitigation: ask-eligibility parity where channel allows, strict separation between abuse moderation and sentiment preference, and audit trails for removals.

- **Anti-pattern: Incentive-blind aggregation.**
  - Detection signal: sudden positive surges tied to incentives without explicit flags.
  - Consequence: inflated satisfaction signal and false PMF confidence.
  - Mitigation: tag and separate incentivized reviews; downweight or exclude from core confidence score.

- **Anti-pattern: Synthetic-review contamination.**
  - Detection signal: high text similarity bursts, account anomalies, improbable timing clusters.
  - Consequence: fake demand/pain narratives.
  - Mitigation: duplicate/fraud checks plus manual adjudication for high-impact claims.

- **Anti-pattern: Alert-ignorant interpretation.**
  - Detection signal: dashboards omit platform warning/restriction states.
  - Consequence: teams treat manipulated windows as clean market signal.
  - Mitigation: intervention state must be stored and considered a hard gate for strategic verdicts.

- **Anti-pattern: Policy drift blindness.**
  - Detection signal: no policy-diff review cadence, same ingestion policy across jurisdictions.
  - Consequence: compliance violations and unstable data ops.
  - Mitigation: scheduled policy reviews and jurisdiction flags per provider.

- **Anti-pattern: Single-platform truth.**
  - Detection signal: one provider drives all strategic claims.
  - Consequence: provider-specific moderation artifacts mistaken for market reality.
  - Mitigation: require at least two independent sources for strong claims.

- **Anti-pattern: One-number sentiment collapse.**
  - Detection signal: only overall sentiment score with no aspect/theme decomposition.
  - Consequence: misses actionable pain clusters.
  - Mitigation: aspect/theme-level outputs with representative evidence snippets.

- **Anti-pattern: LLM-only interpretation without calibration.**
  - Detection signal: no benchmark checks or human QA path.
  - Consequence: hidden misclassification with high-confidence language.
  - Mitigation: confidence labeling, disagreement checks, and human review for low-confidence high-impact themes.

- **Anti-pattern: Provenance-free reporting.**
  - Detection signal: inability to trace source/time/method for any score.
  - Consequence: no auditability, low stakeholder trust.
  - Mitigation: include source lineage fields in all output artifacts.

- **Anti-pattern: Enforcement-lag blindness.**
  - Detection signal: no re-check after platform removals/restrictions.
  - Consequence: stale contaminated signals remain in trend histories.
  - Mitigation: reconciliation jobs and rolling revalidation windows.

**Bad output vs good output (paired):**

1. **Bad:** "Users love Product X (4.8/5), no major issues."  
   **Good:** "Raw average is 4.8, but current window includes intervention flags and low-N segments; confidence is moderate and strongest pain theme is onboarding latency."

2. **Bad:** "Capterra and Yelp both show strong trend; market is clearly improving."  
   **Good:** "Yelp shows directional improvement with adequate sample; Capterra endpoint availability is unverifiable in this run, so cross-provider confidence remains limited."

3. **Bad:** "AI summary says support is excellent."  
   **Good:** "Aspect-level analysis shows positive product reliability but mixed support response-time sentiment; low-confidence sarcasm-heavy subset routed for manual review."

4. **Bad:** "All public reviews were scraped, so legal/compliance risk is low."  
   **Good:** "Collection paths are documented per provider with policy assumptions and unresolved legal constraints; unavailable APIs are marked explicitly."

**Sources:**
- [FTC fake-reviews rule press release (2024)](https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials)
- [FTC platform guidance](https://www.ftc.gov/tips-advice/business-center/guidance/featuring-online-customer-reviews-guide-platforms)
- [UK gov fake-reviews announcement (2025)](https://www.gov.uk/government/news/fake-reviews-and-sneaky-hidden-fees-banned-once-and-for-all)
- [CMA Amazon fake reviews undertakings (2025)](https://www.gov.uk/government/news/amazon-gives-undertakings-to-cma-to-curb-fake-reviews)
- [CMA Google fake reviews action (2025)](https://www.gov.uk/government/news/cma-secures-important-changes-from-google-to-tackle-fake-reviews)
- [Google fake-reviews policy page](https://support.google.com/contributionpolicy/answer/7400114)
- [Google business profile AI trust update (2025)](https://blog.google/products/maps/google-business-profiles-ai-fake-reviews)
- [Yelp guidelines](https://www.yelp.com/guidelines)
- [Yelp compensated-activity help page](https://www.yelp-support.com/article/What-if-I-m-offered-a-freebie-in-exchange-for-my-review?l=en_US)
- [Yelp consumer alerts quarterly report (2026 snapshot)](https://trust.yelp.com/consumer-alerts/quarterly-alerts/)
- [Trustpilot transparency report (2024)](https://press.trustpilot.com/transparency-report)
- [Reality check for sentiment analysis with LLMs (2024)](https://openreview.net/forum?id=FjXsarxoBG)

---

### Angle 5+: Endpoint Verification & Wrapper Safety
> Domain-specific angle: method ID realism and endpoint-safe SKILL authoring so `SKILL.md` never implies invented vendor endpoints.

**Findings:**

- Current method IDs in `SKILL.md` should be treated as **internal wrapper aliases**, not vendor-native endpoint names.
- `trustpilot.*`, `g2.vendors.list.v1`, `g2.reviews.list.v1`, and `yelp.*` are plausible wrapper aliases because official operations exist.
- `g2.categories.benchmark.v1` was not verified as a public vendor endpoint name in available docs; closest documented benchmark-like patterns are syndication distributions, not a direct `categories/benchmark` endpoint.
- `capterra.products.list.v1` and `capterra.reviews.list.v1` are currently **publicly unverifiable** in official docs reviewed here.
- Safe skill-authoring pattern: each wrapper call must include a `vendor_operation` string with verified `HTTP method + path` and an official source URL.

### Endpoint Verification Table

| Current method_id | Classification | Notes |
|---|---|---|
| `trustpilot.business_units.find.v1` | internal-wrapper-only | Vendor op verified: `GET https://api.trustpilot.com/v1/business-units/find` |
| `trustpilot.reviews.list.v1` | internal-wrapper-only | Vendor op verified via Trustpilot Data Solutions review list path |
| `g2.vendors.list.v1` | internal-wrapper-only | Vendor op verified: `GET https://data.g2.com/api/v2/vendors` |
| `g2.reviews.list.v1` | internal-wrapper-only | Vendor op verified: `GET https://data.g2.com/api/v2/products/{product_id}/reviews` |
| `g2.categories.benchmark.v1` | likely invented/unverifiable | No exact public vendor endpoint found with this name |
| `yelp.businesses.search.v1` | internal-wrapper-only | Vendor op verified: `GET https://api.yelp.com/v3/businesses/search` |
| `yelp.businesses.reviews.v1` | internal-wrapper-only | Vendor op verified: `GET https://api.yelp.com/v3/businesses/{business_id_or_alias}/reviews` |
| `capterra.products.list.v1` | unverifiable | No official public endpoint verified in reviewed docs |
| `capterra.reviews.list.v1` | unverifiable | No official public endpoint verified in reviewed docs |

### Replacement Mapping

| Wrapper method_id | Verified vendor operation to map | Guidance |
|---|---|---|
| `trustpilot.business_units.find.v1` | `GET https://api.trustpilot.com/v1/business-units/find` | Use for business unit lookup |
| `trustpilot.reviews.list.v1` | `GET https://datasolutions.trustpilot.com/v1/business-units/{businessUnitId}/reviews` | Use for review retrieval where connector supports Data Solutions |
| `g2.vendors.list.v1` | `GET https://data.g2.com/api/v2/vendors` | Use for candidate vendor discovery |
| `g2.reviews.list.v1` | `GET https://data.g2.com/api/v2/products/{product_id}/reviews` | Primary B2B review retrieval path |
| `g2.categories.benchmark.v1` | no verified direct equivalent | Deprecate from default flow unless connector docs prove exact mapping |
| `yelp.businesses.search.v1` | `GET https://api.yelp.com/v3/businesses/search` | Use for local candidate discovery |
| `yelp.businesses.reviews.v1` | `GET https://api.yelp.com/v3/businesses/{business_id_or_alias}/reviews` | Use for excerpt-level review signals |
| `capterra.*` | no verified public endpoint | Mark unsupported/unverifiable unless runtime connector docs are provided |

### Safe wording for SKILL.md

Use this exact phrasing in the skill:

> `method_id` values are internal connector aliases. They are not vendor-native endpoint names.  
> Every call must include a verified `vendor_operation` (`HTTP method + URL path`) and source URL in tool notes.  
> If a vendor operation cannot be verified in official docs, mark the provider as `unsupported_or_unverifiable` and do not synthesize substitute endpoint names.

**Sources:**
- [Trustpilot Business Units API](https://developers.trustpilot.com/business-units-api-(public)/)
- [Trustpilot Data Solutions API](https://developers.trustpilot.com/data-solutions-api/)
- [Yelp business search](https://docs.developer.yelp.com/reference/v3_business_search)
- [Yelp business reviews](https://docs.developer.yelp.com/reference/v3_business_reviews)
- [G2 API v2 docs](https://data.g2.com/api/v2/docs/index.html)
- [G2 OpenAPI v2](https://data.g2.com/openapi/v2.yaml)
- [G2 syndication docs](https://data.g2.com/api/docs)
- [Gartner Digital Markets buyer discovery docs](https://datainsights.gartner.com/api/buyerdiscovery/swagger/index.html)
- [Gartner Digital Markets reviews hub](https://digital-markets.gartner.com/reviews-hub-index)

---

## Synthesis

The core pattern across all angles is that review intelligence in 2024-2026 is no longer just a text analytics task; it is a governance problem plus an interpretation problem. If the skill does not explicitly encode legal/policy gating, moderation-state awareness, and source provenance, it will produce polished but unreliable outputs.

Methodologically, the strongest shift is from "collect and summarize" to "collect, validate, normalize, and then conclude." The contradiction between platform ecosystems (especially around solicitation rules and recommendation filters) means the skill must branch per provider rather than forcing one universal review workflow.

Tooling findings show that official operations exist for key providers, but wrapper aliases can hide endpoint realism issues. The skill should not imply vendor endpoint certainty where none exists (notably Capterra public retrieval in this pass). Explicit `vendor_operation` mapping and unsupported-provider states are necessary to avoid accidental hallucination.

Interpretation and anti-pattern findings reinforce the same point: confidence has to be earned by sample adequacy, source integrity, temporal stability, and cross-source agreement. The most actionable update is to make uncertainty explicit and to block high-confidence verdicts when integrity gates fail.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.
> Each item here has a corresponding draft in the section below.

- [x] Rewrite core mode to include compliance and integrity gating before any sentiment/theme analysis.
- [x] Replace current methodology with a staged evidence workflow: preflight -> collect -> normalize -> detect -> validate -> conclude.
- [x] Add provider-specific collection policy branching (especially solicitation and moderation constraints).
- [x] Add explicit sample-size gates and confidence policy for low-N windows.
- [x] Add cross-platform normalization rules and contradiction tracking.
- [x] Replace endpoint-like ambiguity with wrapper-alias safety pattern (`method_id` + verified `vendor_operation`).
- [x] Deprecate unverifiable default methods (for example, `g2.categories.benchmark.v1`) unless connector docs prove mapping.
- [x] Add unsupported-provider behavior for publicly unverifiable connectors (current Capterra case).
- [x] Expand anti-pattern section into named warning blocks with detection signal, consequence, and mitigation.
- [x] Expand artifact schema with source lineage, integrity checks, contradiction records, and confidence components.
- [x] Add output quality checklist and hard stop conditions for invalid/incomplete evidence.

---

## Draft Content for SKILL.md

> This is the most important section. For every recommendation above, write the actual text that should go into SKILL.md.

### Draft: Core mode rewrite (evidence and integrity contract)

---
You are detecting voice-of-market signals from review platforms for one target scope per run. Your primary rule is: **integrity before interpretation**.

Reviews are opinions, not facts. You must only produce strong conclusions when evidence quality passes all integrity gates. If integrity gates fail, your result must downgrade confidence, switch to a hold state, or return insufficient data.

Before analyzing any sentiment/theme, run this pre-analysis contract:

1. Confirm collection method is policy-compliant for each provider in scope.
2. Confirm no known fake/synthetic/manipulated records are included in core evidence.
3. Confirm source lineage (provider, time window, retrieval path) is recorded.
4. Confirm sample size gate per provider is met, or mark as directional only.
5. Confirm intervention/moderation state is checked for each provider window.

If any one of these fails and cannot be repaired during the run, you must not output a high-confidence recommendation.
---

### Draft: Methodology rewrite (staged workflow)

---
### Methodology

Use this exact sequence in every run.

#### Step 1: Scope and policy preflight

Before calling any provider tool, declare:
- target entity/category,
- geography and language scope,
- time window,
- provider list.

Then run a policy preflight:
- verify provider collection policy assumptions,
- verify whether solicitation restrictions affect interpretation,
- verify whether the provider is owner-managed only or competitor-observable,
- verify whether public endpoint mapping is known.

If a provider fails preflight, mark that provider as unavailable and continue only if remaining coverage is sufficient.

#### Step 2: Discover and resolve target identities

Map your target to provider-specific IDs (business unit ID, product ID, business alias, etc.) before fetching reviews.

Rules:
- Do not guess IDs from names alone when a lookup operation exists.
- If multiple candidates match, keep all candidates in a short-list and require disambiguation by domain/category context.
- If the ID cannot be resolved reliably, do not fake a fallback ID; mark provider unresolved.

#### Step 3: Collect review records with lineage

For each successful provider target:
- collect review records for the selected time window,
- store retrieval timestamp,
- store provider and retrieval path metadata,
- store moderation/intervention flags when available.

You should retain enough metadata to reproduce the run later. If reproducibility metadata is missing, confidence must be reduced.

#### Step 4: Normalize and quality-check

Normalize records into a common shape:
- provider,
- rating scale normalized to 1-5 if needed,
- timestamp,
- language,
- review text,
- invite/incentive flags (if available),
- moderation/recommendation status (if available).

Run quality checks:
- deduplicate exact and near-duplicate records,
- remove policy-invalid records from core evidence,
- separate provisional data from settled windows,
- label unknown fields explicitly rather than filling defaults silently.

#### Step 5: Extract themes and compute distributions

Compute:
- star distribution by provider and overall,
- low-star concentration (`1-2` share),
- high-star concentration (`4-5` share),
- recurring pain themes and satisfaction themes with evidence counts.

Theme extraction rules:
- require recurring language across multiple records before creating a theme,
- preserve representative evidence snippets,
- avoid creating themes from single outlier phrasing,
- keep confidence lower for mixed-language or low-text windows.

#### Step 6: Cross-provider comparison and trend analysis

Compare providers only after normalization.

Use two windows:
- short window for fresh movement detection,
- longer baseline window for trend stability.

Signal rules:
- classify shifts as directional only if sample gate is borderline,
- classify as strong only if multiple providers agree or one provider has very strong clean evidence with no intervention flags,
- track contradictions rather than hiding them.

#### Step 7: Confidence scoring and verdict

Build confidence from:
- sample adequacy,
- source integrity,
- temporal stability,
- cross-source agreement,
- language coverage.

Then output one of:
- `ok`,
- `ok_with_conflicts`,
- `insufficient_data`,
- `zero_results`,
- `policy_restricted`,
- `technical_failure`.

Do not output `ok` if any hard stop condition applies.

#### Step 8: Record limitations and next checks

Always include:
- what was not observable,
- which provider claims were unverifiable,
- which additional checks could raise confidence in the next run.

Do NOT:
- treat one provider as market truth,
- treat low-N averages as conclusive,
- ignore platform intervention states,
- hide contradictions between sources.
---

### Draft: Provider selection and sample policy

---
### Provider selection

Select providers by domain and visibility:

- B2B software: prioritize `g2` and `trustpilot` when available.
- Local/consumer service: prioritize `yelp` and `trustpilot`.
- Owned app products: use app-store specific skills and APIs (`App Store Connect`, `Google Play`) when in scope.
- Capterra-family signals: include only when connector endpoint mapping is verified at runtime; otherwise mark as unavailable.

### Minimum sample policy

Apply per-provider sample policy before strong conclusions:

- `<10` reviews in window: `insufficient_data` for provider-level claims.
- `10-19` reviews: directional only; no strong ranking claims.
- `>=20` reviews: eligible for provider-level reporting with confidence scoring.

For cross-provider conclusions:
- require at least two providers meeting minimum policy, or
- one provider with strong sample and no integrity flags, plus explicit limitation note.

### Source-mix policy

Always report source mix:
- provider share,
- invited/organic mix where available,
- incentivized/disclosed share where available,
- moderation/intervention status.

Never hide a provider with contradictory signal. Contradiction must be represented explicitly in output.
---

### Draft: Available Tools section rewrite (wrapper-safe, endpoint-verified)

---
## Available Tools

`method_id` values are internal connector aliases. They are not vendor-native endpoint names.

For every call, include a `vendor_operation` note in args or call commentary that specifies the verified vendor operation (`HTTP method + URL/path`). If you cannot provide a verified vendor operation from official docs, treat the provider as unavailable for this run.

### Trustpilot

```python
trustpilot(
  op="call",
  args={
    "method_id": "trustpilot.business_units.find.v1",
    "vendor_operation": "GET https://api.trustpilot.com/v1/business-units/find",
    "name": "company name"
  }
)
```

```python
trustpilot(
  op="call",
  args={
    "method_id": "trustpilot.reviews.list.v1",
    "vendor_operation": "GET https://datasolutions.trustpilot.com/v1/business-units/{businessUnitId}/reviews",
    "businessUnitId": "unit_id",
    "language": "en"
  }
)
```

### G2

```python
g2(
  op="call",
  args={
    "method_id": "g2.vendors.list.v1",
    "vendor_operation": "GET https://data.g2.com/api/v2/vendors",
    "filter[name]": "product name"
  }
)
```

```python
g2(
  op="call",
  args={
    "method_id": "g2.reviews.list.v1",
    "vendor_operation": "GET https://data.g2.com/api/v2/products/{product_id}/reviews",
    "filter[product_id]": "product_id",
    "page[size]": 25
  }
)
```

Do not use `g2.categories.benchmark.v1` unless your runtime connector docs explicitly map it to a verified vendor operation.

### Yelp

```python
yelp(
  op="call",
  args={
    "method_id": "yelp.businesses.search.v1",
    "vendor_operation": "GET https://api.yelp.com/v3/businesses/search",
    "term": "business type",
    "location": "New York"
  }
)
```

```python
yelp(
  op="call",
  args={
    "method_id": "yelp.businesses.reviews.v1",
    "vendor_operation": "GET https://api.yelp.com/v3/businesses/{business_id_or_alias}/reviews",
    "id": "business_id"
  }
)
```

### Capterra (connector-dependent)

```python
# Use only if connector documentation in your runtime environment
# proves a verified vendor operation mapping.
capterra(
  op="call",
  args={
    "method_id": "capterra.reviews.list.v1",
    "vendor_operation": "UNVERIFIABLE_PUBLIC_ENDPOINT",
    "productId": "product_id"
  }
)
```

If Capterra endpoint mapping is not verifiable, set provider status to `unsupported_or_unverifiable` and proceed with available providers.

### Call sequencing guidance

1. Resolve provider target IDs first.
2. Fetch reviews with explicit time window and language where supported.
3. Store provider-level metadata and retrieval lineage.
4. Run quality gates before aggregation.
5. Never infer endpoint behavior from wrapper name alone.
---

### Draft: Interpretation rubric and confidence scoring

---
### Data interpretation and signal quality

Use this rubric before concluding:

#### 1) Hard invalidity checks

If evidence violates integrity rules (fake/manipulated/undisclosed incentive abuse), exclude from core analysis.

#### 2) Intervention-state check

If provider intervention/warning/restriction state is active for the target window, switch to `hold` logic:
- collect and log evidence,
- avoid high-confidence strategic conclusions,
- require follow-up window.

#### 3) Sample adequacy check

Apply minimum sample policy and do not rank low-N windows as if stable.

#### 4) Distribution + theme agreement

Strong claims require both:
- distribution evidence (for example low-star concentration trend), and
- recurring theme evidence with representative snippets.

Do not rely on one signal family alone.

#### 5) Cross-source agreement

If provider signals disagree:
- record contradiction explicitly,
- downgrade confidence,
- avoid one-sided narrative.

#### 6) Confidence scoring model

Score each dimension from `0` to `1`:
- `sample_adequacy`,
- `source_integrity`,
- `temporal_stability`,
- `cross_source_agreement`,
- `language_coverage`.

Compute weighted confidence:

`confidence = (0.25 * sample_adequacy) + (0.25 * source_integrity) + (0.20 * temporal_stability) + (0.20 * cross_source_agreement) + (0.10 * language_coverage)`

Label:
- `high` when `>= 0.75`,
- `medium` when `0.55-0.74`,
- `low` when `< 0.55`.

You may adjust weights only when the run has explicit rationale; never hide weight changes.

#### 7) Signal-type interpretation guidance

- `pain_cluster`: require recurring low-star concentration plus recurring pain themes.
- `satisfaction_gap`: detect decreasing trend in satisfaction indicators and growing complaint themes.
- `competitor_weakness`: require provider evidence that competitor pain is concentrated in a specific feature/service area.
- `improving_trend` / `declining_trend`: require multi-window support; one burst window is not enough.
- `feature_gap`: require repeated "missing/wish/cannot" phrasing across independent records.

#### 8) Stop conditions

Do not conclude if:
- active intervention state and no settled follow-up,
- unresolved target ID ambiguity,
- insufficient sample across all providers,
- unresolved major contradiction with no tie-break evidence.
---

### Draft: Anti-pattern warning blocks

---
### Named anti-pattern warnings

#### Warning: Review Gating Bias
- **What it looks like:** only likely-happy users are invited; negative voices are under-collected.
- **Detection signal:** abnormal post-campaign positivity and low variance.
- **Consequence if missed:** false product confidence, legal exposure.
- **Mitigation:** apply channel-compliant broad eligibility; separate abuse moderation from sentiment preference.

#### Warning: Incentive Blindness
- **What it looks like:** incentivized records merged into core score without flags.
- **Detection signal:** positive spikes during incentive periods with missing metadata.
- **Consequence if missed:** inflated satisfaction signal.
- **Mitigation:** explicit incentive tagging and separate reporting lanes.

#### Warning: Wrapper-as-Endpoint Hallucination
- **What it looks like:** method IDs treated as proof of vendor endpoint existence.
- **Detection signal:** output references endpoint-like strings with no official docs.
- **Consequence if missed:** fabricated evidence chain.
- **Mitigation:** require `vendor_operation` mapping and source URL for each method.

#### Warning: Single-Provider Overreach
- **What it looks like:** one platform drives all market conclusions.
- **Detection signal:** no corroboration attempt, no cross-provider limitations.
- **Consequence if missed:** platform artifact mistaken for market truth.
- **Mitigation:** require multi-provider confirmation for strong claims.

#### Warning: Alert-Ignorant Trending
- **What it looks like:** trend claims published during moderation/intervention events.
- **Detection signal:** no intervention field in records or output.
- **Consequence if missed:** contaminated trend story.
- **Mitigation:** intervention-state gating and follow-up windows.

#### Warning: One-Score Sentiment Collapse
- **What it looks like:** only global sentiment without theme/aspect decomposition.
- **Detection signal:** no theme distribution and no evidence snippets.
- **Consequence if missed:** non-actionable insight.
- **Mitigation:** require theme clusters with prevalence and quotes/snippets.

#### Warning: Low-N Ranking
- **What it looks like:** ranking providers despite insufficient review counts.
- **Detection signal:** confidence language stronger than sample supports.
- **Consequence if missed:** unstable decisions.
- **Mitigation:** enforce `<10` insufficient, `10-19` directional policy.

#### Warning: Contradiction Erasure
- **What it looks like:** only supporting sources are shown in final narrative.
- **Detection signal:** missing contradiction fields despite mixed evidence.
- **Consequence if missed:** overconfident and brittle recommendations.
- **Mitigation:** add explicit contradiction records and resolution plan.
---

### Draft: Result-state policy and escalation rules

---
### Result state policy

Use these states exactly:

- `ok`: adequate evidence, no hard integrity blockers, contradictions manageable.
- `ok_with_conflicts`: useful evidence exists but contradictions materially reduce certainty.
- `zero_results`: provider queries succeeded but returned no records.
- `insufficient_data`: records exist but sample/quality gates not met.
- `policy_restricted`: evidence cannot be used safely because policy/integrity constraints dominate.
- `technical_failure`: retrieval or connector failure prevented reliable analysis.

### Escalation policy

If result is `ok_with_conflicts`, `insufficient_data`, `policy_restricted`, or `technical_failure`, always include:
- minimum next checks required,
- what missing evidence would change verdict,
- whether rerun window should be extended.

Never return strategic "strong signal" language when state is not `ok`.
---

### Draft: Schema additions

Write the following schema fragment into `SKILL.md` artifact schema section.

```json
{
  "signal_reviews_voice": {
    "type": "object",
    "required": [
      "target",
      "analysis_scope",
      "time_window",
      "result_state",
      "source_summary",
      "sources",
      "signals",
      "signal_quality",
      "limitations",
      "next_checks"
    ],
    "additionalProperties": false,
    "properties": {
      "target": {
        "type": "string",
        "description": "Company, product, competitor set, or category being analyzed."
      },
      "analysis_scope": {
        "type": "object",
        "required": [
          "mode",
          "region",
          "language"
        ],
        "additionalProperties": false,
        "properties": {
          "mode": {
            "type": "string",
            "enum": [
              "single_company",
              "single_product",
              "competitor_set",
              "category_scan"
            ],
            "description": "Scope mode for this run."
          },
          "region": {
            "type": "string",
            "description": "Primary geographic scope used for provider retrieval and interpretation."
          },
          "language": {
            "type": "string",
            "description": "Primary analysis language (for example en, fr, de)."
          }
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
            "type": "string",
            "description": "ISO date for window start."
          },
          "end_date": {
            "type": "string",
            "description": "ISO date for window end."
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
          "policy_restricted",
          "technical_failure"
        ],
        "description": "Overall run status reflecting data sufficiency and integrity."
      },
      "source_summary": {
        "type": "object",
        "required": [
          "providers_attempted",
          "providers_successful",
          "total_reviews_collected"
        ],
        "additionalProperties": false,
        "properties": {
          "providers_attempted": {
            "type": "integer",
            "minimum": 0,
            "description": "How many providers were attempted in the run."
          },
          "providers_successful": {
            "type": "integer",
            "minimum": 0,
            "description": "How many providers returned usable records."
          },
          "total_reviews_collected": {
            "type": "integer",
            "minimum": 0,
            "description": "Total raw reviews collected before dedup and filtering."
          }
        }
      },
      "sources": {
        "type": "array",
        "description": "Per-provider retrieval and lineage records.",
        "items": {
          "type": "object",
          "required": [
            "provider",
            "wrapper_method_id",
            "vendor_operation",
            "retrieval_state",
            "reviews_collected",
            "sample_class",
            "intervention_state"
          ],
          "additionalProperties": false,
          "properties": {
            "provider": {
              "type": "string",
              "enum": [
                "trustpilot",
                "g2",
                "yelp",
                "capterra",
                "other"
              ],
              "description": "Source provider name."
            },
            "wrapper_method_id": {
              "type": "string",
              "description": "Internal connector method alias used for retrieval."
            },
            "vendor_operation": {
              "type": "string",
              "description": "Verified vendor HTTP operation string (method + URL/path)."
            },
            "retrieval_state": {
              "type": "string",
              "enum": [
                "ok",
                "zero_results",
                "unsupported_or_unverifiable",
                "permission_denied",
                "rate_limited",
                "technical_failure"
              ],
              "description": "Provider retrieval outcome."
            },
            "reviews_collected": {
              "type": "integer",
              "minimum": 0,
              "description": "Raw count of collected reviews from this provider."
            },
            "sample_class": {
              "type": "string",
              "enum": [
                "organic",
                "invited",
                "incentivized_disclosed",
                "mixed_or_unknown"
              ],
              "description": "Best-known sampling class for this provider set in this run."
            },
            "intervention_state": {
              "type": "string",
              "enum": [
                "none_detected",
                "warning_present",
                "restriction_present",
                "unknown"
              ],
              "description": "Whether provider/platform intervention signals were detected in this window."
            }
          }
        }
      },
      "signals": {
        "type": "array",
        "description": "Detected market signals after quality gates.",
        "items": {
          "type": "object",
          "required": [
            "signal_type",
            "signal_summary",
            "strength",
            "confidence",
            "providers",
            "evidence_count",
            "themes"
          ],
          "additionalProperties": false,
          "properties": {
            "signal_type": {
              "type": "string",
              "enum": [
                "pain_cluster",
                "satisfaction_gap",
                "competitor_weakness",
                "improving_trend",
                "declining_trend",
                "feature_gap"
              ],
              "description": "Signal category."
            },
            "signal_summary": {
              "type": "string",
              "description": "One-paragraph explanation of what changed and why it matters."
            },
            "strength": {
              "type": "string",
              "enum": [
                "strong",
                "moderate",
                "weak"
              ],
              "description": "Signal strength label derived from evidence quality and agreement."
            },
            "confidence": {
              "type": "number",
              "minimum": 0,
              "maximum": 1,
              "description": "Numeric confidence score for this signal."
            },
            "providers": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "Providers contributing evidence for this signal."
            },
            "evidence_count": {
              "type": "integer",
              "minimum": 0,
              "description": "Number of contributing review records after dedup and filtering."
            },
            "themes": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "Theme tags supporting this signal (for example onboarding, pricing, reliability)."
            },
            "representative_snippets": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "Short evidence snippets used to justify the signal."
            }
          }
        }
      },
      "signal_quality": {
        "type": "object",
        "required": [
          "sample_adequacy",
          "source_integrity",
          "temporal_stability",
          "cross_source_agreement",
          "language_coverage",
          "overall_confidence_label"
        ],
        "additionalProperties": false,
        "properties": {
          "sample_adequacy": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Quality score for sample size sufficiency."
          },
          "source_integrity": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Quality score for policy/integrity cleanliness of included evidence."
          },
          "temporal_stability": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Quality score for trend stability across windows."
          },
          "cross_source_agreement": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Quality score for directional agreement across providers."
          },
          "language_coverage": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Quality score for language coverage and analysis reliability."
          },
          "overall_confidence_label": {
            "type": "string",
            "enum": [
              "high",
              "medium",
              "low"
            ],
            "description": "Human-readable confidence label derived from weighted scoring."
          }
        }
      },
      "contradictions": {
        "type": "array",
        "description": "Explicitly tracked conflicts between providers or evidence classes.",
        "items": {
          "type": "object",
          "required": [
            "topic",
            "source_a",
            "source_b",
            "impact",
            "resolution_plan"
          ],
          "additionalProperties": false,
          "properties": {
            "topic": {
              "type": "string",
              "description": "Contradiction topic (for example trend direction, theme prevalence)."
            },
            "source_a": {
              "type": "string",
              "description": "First contradictory evidence reference."
            },
            "source_b": {
              "type": "string",
              "description": "Second contradictory evidence reference."
            },
            "impact": {
              "type": "string",
              "description": "How the contradiction affects confidence and recommendations."
            },
            "resolution_plan": {
              "type": "string",
              "description": "What follow-up data or checks are required to resolve the conflict."
            }
          }
        }
      },
      "limitations": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Known limitations and blind spots for this run."
      },
      "next_checks": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Specific follow-up checks to increase confidence in the next pass."
      }
    }
  }
}
```

### Draft: Output quality checklist block

---
### Output quality checklist (required before artifact write)

Before writing `signal_reviews_voice`:

- Confirm at least one provider succeeded, or return `zero_results`/`technical_failure`.
- Confirm sample-size policy is applied per provider.
- Confirm all strong claims have evidence counts and provider lineage.
- Confirm contradictions are represented, not suppressed.
- Confirm unsupported/unverifiable providers are labeled explicitly.
- Confirm method aliases are not presented as vendor-native endpoints.
- Confirm limitations and next checks are specific and actionable.

If any checklist item fails, do not write `ok` state.
---

---

## Gaps & Uncertainties

- Publicly documented Capterra review/product retrieval endpoints were not verified in official public docs during this pass; connector-private mappings may exist but are uncertain.
- Exact provider-level weighting formulas for trust/recommendation/moderation signals are generally not fully disclosed, so weighting recommendations remain implementation-level heuristics.
- Some platform policy pages are undated but current as-of-access; where specific revision timestamps are missing, these are treated as evergreen operational references.
- Quantitative thresholds for fake-review detection are domain-specific and often proprietary; this research documents robust gating patterns but not a universal detector threshold.
- App-store review APIs are relevant for adjacent skills and owned-app contexts, but this specific skill may intentionally scope those out depending on bot architecture.
