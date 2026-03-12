# Research: segment-voice-of-market

**Skill path:** `flexus-client-kit/flexus_simple_bots/researcher/skills/segment-voice-of-market/`
**Bot:** researcher
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`segment-voice-of-market` extracts market signal from app-store reviews for product direction, issue detection, and competitor positioning. The skill is used when teams need evidence from unsolicited customer feedback rather than survey-only or support-only channels.

This domain has changed materially in 2024-2026: both stores increased operational guidance around review quality and moderation, Apple launched LLM-generated review summaries, and policy/privacy expectations became stricter for AI-assisted processing and quote reuse. The skill therefore needs a stricter methodology than "read top negative reviews and summarize." It must enforce time windows, segmentation, confidence gates, and source/provenance guardrails.

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

Gate check result: passed.

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

1. **Release-anchored cadence is now the default operational model.** Teams that do this well do not use one reporting window. They run `T+24-72h` post-release triage, then `T+28d` stabilization, then `T+90d` trend confirmation. This aligns with Play's release-centered reporting and avoids overreacting to launch-day volatility.

2. **Recency matters more than lifetime averages.** Play explicitly frames displayed rating as weighted toward current quality and also notes publication lag for ratings/reviews. Practical implication: provisional conclusions in the first 24-48h, then confidence-upgraded verdicts once lagged data arrives.

3. **Version/locale/device segmentation is mandatory for valid attribution.** Both Apple and Google expose filters that make all-in-one averages methodologically weak. Teams should treat version, country/region, and language as first-class keys; otherwise they misattribute localized outages or release regressions as global trends.

4. **Theme extraction works best with a two-layer model.** Use store-native benchmark categories (for comparability) plus open clustering (for novel issue discovery). Fixed categories help trend comparability; open clustering finds emerging problems that taxonomy buckets miss.

5. **Sentiment should be explicit and formula-bound, not opaque.** Vendor workflows increasingly pair star trends with sentiment trend windows (often 30-60 day baselines and 24-72h post-release checks). The skill should force formula disclosure so outputs are auditable across tools.

6. **Review-reply operations are part of VoM signal, not only support workflow.** Google reports measurable rating uplift after replying to negative reviews; Apple also encourages response cadence around key updates. Response rate and response latency should be included in interpretation.

7. **Multilingual handling requires original-language QA on top themes.** Auto-translation is useful but insufficient for high-impact prioritization. A robust method preserves original text, translated text, and locale tags, then validates top negative themes in the source language.

8. **Competitive benchmarking should separate absolute quality from relative deltas.** Peer comparisons and competitor review mining are useful only if methodology is transparent (same time window, same segmentation, same filters). Raw quote cherry-picking is not acceptable evidence.

9. **Review-request quotas shape the data-generation process.** Apple and Google in-app review prompt rules limit prompt frequency and display behavior; analysts must treat this as a sampling constraint when interpreting changes in review mix.

10. **What changed recently (2024-2026):** more platform-native summarization and benchmark surfaces, stronger anti-manipulation enforcement language, and more practical emphasis on release-linked diagnostics rather than static monthly averages.

**Sources:**
- https://support.google.com/googleplay/android-developer/answer/7383463?hl=en
- https://support.google.com/googleplay/android-developer/answer/138230
- https://play.google.com/console/about/ratings
- https://developer.apple.com/help/app-store-connect/monitor-ratings-and-reviews/view-ratings-and-reviews
- https://developer.apple.com/help/app-store-connect/monitor-ratings-and-reviews/ratings-and-reviews-overview
- https://developer.apple.com/app-store/ratings-and-reviews/
- https://developer.apple.com/documentation/storekit/requesting_app_store_reviews
- https://developer.android.com/guide/playcore/in-app-review
- https://appfollow.io/blog/customer-sentiment-score
- https://www.apptweak.com/en/aso-blog/why-how-to-analyze-app-store-reviews

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

1. **Apple first-party review ingestion is mature and explicit.** App Store Connect API exposes real review resources (`/v1/apps/{id}/customerReviews`, `/v1/appStoreVersions/{id}/customerReviews`) and response lifecycle endpoints. This supports first-party ingestion and response tracking without scraping.

2. **Apple auth and limits are explicit.** JWT (`ES256`) plus key/role control is required; rate limits are discoverable via response headers and 429 behavior. This is strong for production-safe retry/backoff design.

3. **Apple's API surface continued changing in 2024-2026.** Release notes indicate ongoing expansion, including review-related resources and summarization capabilities. The skill should assume API surface evolution and avoid hard-coded assumptions.

4. **Google official review API is intentionally narrow.** Core methods are `reviews.list`, `reviews.get`, and `reviews.reply`. Limitations matter: production-track scope, focus on review/comment records, and time-window constraints for modified/new records in API fetch patterns.

5. **Google quota controls are multi-layered.** There are review-specific quotas and broader bucket quotas. Any automated workflow needs queueing and per-app budget controls to avoid accidental throttling.

6. **Third-party tools fill historical and analytics gaps.** AppFollow, AppTweak, 42matters, and Appbot offer review analytics and enrichment, but differ materially in pricing model, access model, and historical depth.

7. **Third-party APIs are commonly credit-metered.** AppFollow and AppTweak expose credit/billing and rate-limit mechanics that can become the main operational constraint for broad competitor sweeps.

8. **Historical backfill is the main reason teams add data vendors.** Google first-party access constraints often require either console exports or paid providers for complete historical analysis.

9. **Tool capability mismatch is common.** Some tools optimize for response workflows, others for analytics depth or topic enrichment. A single provider rarely wins all use cases; a source-mapping matrix is required.

10. **De-facto architecture in 2025-2026:** first-party APIs for trusted operational data and replying, plus one enrichment vendor for cross-app analytics and history where needed.

**Sources:**
- https://developer.apple.com/documentation/appstoreconnectapi/list_all_customer_reviews_for_an_app
- https://developer.apple.com/documentation/appstoreconnectapi/get-v1-appstoreversions-_id_-customerreviews
- https://developer.apple.com/documentation/appstoreconnectapi/customer-review-responses
- https://developer.apple.com/documentation/appstoreconnectapi/identifying-rate-limits
- https://developer.apple.com/documentation/appstoreconnectapi/generating-tokens-for-api-requests
- https://developer.apple.com/documentation/appstoreconnectapi/app-store-connect-api-2-0-release-notes
- https://developer.apple.com/documentation/appstoreconnectapi/app-store-connect-api-4-0-release-notes
- https://developers.google.com/android-publisher/api-ref/rest/v3/reviews
- https://developers.google.com/android-publisher/reply-to-reviews
- https://developers.google.com/android-publisher/quotas
- https://docs.api.appfollow.io/reference/reviews_api_v2_reviews_get-1
- https://developers.apptweak.com/reference/app-reviews
- https://42matters.com/docs/app-market-data/android/apps/reviews
- https://support.appbot.co/help-docs/app-store-review-rating-api-for-google-play-ios

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

1. **Displayed rating and lifetime rating are different signals.** Play's displayed rating emphasizes recent quality, so interpretation should always include both current and lifetime context to avoid trend distortion.

2. **Do not claim release impact from day-zero shifts.** Play indicates publication delays and potential abuse-review holds; minimum 48h cooldown is needed before directional claim language.

3. **Use platform windows for consistency (`daily`, `7d`, `28d`) and role separation.** Daily is for incident triage, 7-day for short trend, 28-day for baseline comparison.

4. **Sample-size gates are required for directional claims.**  
   - 95% CI, +/-10 percentage points precision: around `n~97`  
   - 95% CI, +/-5 percentage points precision: around `n~385`  
   These are standard proportion-planning references and should be explicitly marked as **evergreen statistical guidance** when used.

5. **Wilson/Jeffreys intervals are preferred for sparse segments (evergreen statistical guidance).** Normal/Wald intervals can mislead for small `n` or extreme rates.

6. **Average star alone is vulnerable to self-selection bias (evergreen research finding).** Use full distribution and recurrence-weighted theme analysis rather than a mean-only dashboard.

7. **Structural breaks must be modeled explicitly.** Apple rating resets and platform moderation events break continuity; pre/post pooling without flags invalidates trend claims.

8. **Theme/sentiment coverage must disclose language and volume constraints.** Play benchmark summaries are constrained (for example language scope and minimum similarity volume behavior), and Apple summaries are generated through a filtered pipeline with anti-fraud/profanity handling.

9. **Fraud/manipulation risk is not theoretical in 2024-2026.** Policy updates and enforcement plus independent fraud reporting support adding suspicious-burst checks before theme prioritization.

10. **Reply effect can be measured, but causality claims should be conservative.** Cohort comparison (`with_reply` vs `without_reply`) is useful; causal language needs stronger design than correlation.

**Sources:**
- https://support.google.com/googleplay/android-developer/answer/138230
- https://play.google.com/about/comment-posting-policy.html
- https://play.google.com/console/about/ratings/
- https://developer.apple.com/help/app-store-connect/monitor-ratings-and-reviews/reset-an-app-overview-rating
- https://developer.apple.com/help/app-store-connect/monitor-ratings-and-reviews/ratings-and-reviews-overview
- https://machinelearning.apple.com/research/app-store-review
- https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials
- https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers
- https://www.itl.nist.gov/div898/handbook/prc/section2/prc242.htm (evergreen)
- https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm (evergreen)
- https://aisel.aisnet.org/misq/vol41/iss2/8/ (evergreen)

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

1. **Low-volume panic:** acting on tiny post-release spikes without sample-size gates.
   - Detection: release claim made in first 24h or with very small `n`.
   - Consequence: roadmap churn and false hotfixes.
   - Mitigation: require cooldown + minimum sample + crash/uninstall corroboration.

2. **Causality overreach:** assuming star shift directly caused retention/LTV changes.
   - Detection: no cohort design, no confound checks, only narrative linkage.
   - Consequence: wrong optimization target.
   - Mitigation: treat ratings as observational; pair with retention/churn cohorts.

3. **Competitor cherry-picking:** selecting dramatic reviews without denominator.
   - Detection: no peer cohort, no symmetric date/version/locale filters.
   - Consequence: biased competitive strategy.
   - Mitigation: enforce declared sampling frame and parity rules.

4. **No version segmentation:** mixing all-time reviews for release decisions.
   - Detection: missing version key in report.
   - Consequence: hidden regression root causes.
   - Mitigation: mandatory version slices in all conclusions.

5. **No territory/language segmentation:** global average used as "market truth."
   - Detection: no regional breakdown for major claims.
   - Consequence: local failures are invisible.
   - Mitigation: require region/language view for each major finding.

6. **PII leakage in quote handling:** raw quote reuse in tickets/prompts/marketing.
   - Detection: names, contact data, or identifiable details in exported quote sets.
   - Consequence: legal and trust risk.
   - Mitigation: redact, limit access, and permission-gate external quote usage.

7. **Fake-review contamination:** no authenticity filter before clustering.
   - Detection: unusual burst/duplicate pattern and polarity anomalies.
   - Consequence: contaminated theme ranking.
   - Mitigation: suspiciousness scoring and sensitivity reruns excluding flagged reviews.

8. **Automation hallucination:** LLM themes without quote-level provenance.
   - Detection: output cannot map to source review IDs or confidence is absent.
   - Consequence: fabricated insight and misprioritized roadmap actions.
   - Mitigation: require source trace, confidence, and abstain behavior.

**Sources:**
- https://support.google.com/googleplay/android-developer/answer/138230
- https://support.google.com/googleplay/android-developer/answer/7383463?hl=en
- https://support.google.com/googleplay/android-developer/answer/9842755?hl=en
- https://support.google.com/googleplay/android-developer/answer/10771707?hl=en
- https://developer.apple.com/help/app-store-connect/monitor-ratings-and-reviews/view-ratings-and-reviews
- https://developer.apple.com/app-store/ratings-and-reviews/
- https://doubleverify.com/blog/web/verify/the-hidden-threat-of-ai-powered-fake-app-reviews
- https://www.reuters.com/technology/sonos-ceo-promises-reforms-after-may-app-release-failure-leaders-forgo-bonuses-2024-10-01/
- https://aclanthology.org/2025.findings-naacl.293/
- https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence

---

### Angle 5+: Policy, Compliance & Governance Constraints
> Add as many additional angles as the domain requires. Examples: regulatory/compliance context, industry-specific nuances, integration patterns with adjacent tools, competitor landscape, pricing benchmarks, etc.

**Findings:**

1. **Official collection paths are preferred and lower risk; scraping is high risk.** Apple and Google provide official mechanisms for review data and replies; terms materially restrict unauthorized scraping/redistribution behavior.

2. **Reply policies are explicit and enforceable.** Both platforms require respectful, non-manipulative responses and discourage disclosure of personal/confidential user information.

3. **Apple quote reuse is specifically permission-gated for marketing.** Apple allows accurate rating references but requires reviewer permission for using customer review quotes in marketing contexts.

4. **Review text is potentially personal data when combined with metadata.** Storage and downstream sharing (especially to third-party AI processors) must respect disclosure, minimization, and retention/deletion controls.

5. **AI governance obligations are increasing (2024-2026).** Google now has explicit AI content policy framing; EU AI Act timing introduces phased obligations including transparency/governance requirements.

6. **Allowed-vs-risky use should be encoded in artifact fields, not only process docs.** The skill output should carry provenance, usage-rights notes, and redistribution scope so downstream automation cannot accidentally violate constraints.

7. **Jurisdiction and copyright nuance remains a real uncertainty area.** Public review visibility does not remove all legal constraints; use conservative defaults where rights are ambiguous.

**Sources:**
- https://developer.apple.com/documentation/appstoreconnectapi/list_all_customer_reviews_for_an_app
- https://developers.google.com/android-publisher/reply-to-reviews
- https://www.apple.com/legal/internet-services/itunes/us/terms.html
- https://developers.google.com/terms
- https://developers.google.com/android-publisher/terms
- https://developer.apple.com/app-store/review/guidelines/
- https://developer.apple.com/app-store/ratings-and-reviews/
- https://support.google.com/googleplay/android-developer/answer/9888076
- https://support.google.com/googleplay/android-developer/answer/13985936
- https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai

---

## Synthesis

The strongest cross-source pattern is that mature app-review VoM programs are moving from static "monthly sentiment summaries" toward release-aware operational analytics. Across Apple guidance, Google console/API behavior, and practitioner playbooks, the practical standard is now multi-window analysis (post-release pulse, stabilization window, trend window), version-aware segmentation, and explicit confidence language.

A second consistent pattern is that first-party APIs are necessary but not sufficient. Apple and Google official sources are the trust anchor for ingestion and response workflows, but each has constraints that drive supplemental workflows (for example historical depth, enrichment, and cross-app benchmarking). This is why most production setups combine first-party data collection with selective third-party enrichment.

The most important contradiction is speed versus validity. Some operational guides push very fast reaction SLAs, while platform mechanics (review publication lag, moderation holds, version rollout dynamics) argue for stronger evidence gates before directional claims. The correct synthesis is not "slow down everything"; it is "separate fast triage from high-confidence decisioning."

A second contradiction is comparability versus discovery. Fixed taxonomies and benchmark categories improve longitudinal tracking, but open clustering is required for novel issue discovery. The skill should support both and require explicit disclosure of which layer produced each conclusion.

Most surprising in 2024-2026 is how quickly policy and governance concerns became first-class for this domain: fake-review enforcement, AI summarization safety expectations, and legal/contractual quote-usage constraints now materially affect how a "simple review analysis" system must be built and audited.

---

## Recommendations for SKILL.md

- [ ] Add a mandatory tri-window analysis cadence (`T+72h`, `T+28d`, `T+90d`) and distinguish provisional vs directional claims.
- [ ] Add explicit minimum evidence gates (`n` thresholds + confidence interval method) before writing directional conclusions.
- [ ] Add required segmentation fields for every claim: `app_version`, `country_region`, `language`, and `platform`.
- [ ] Add dual-layer theme extraction instructions: benchmark taxonomy + open clustering, with provenance labels.
- [ ] Expand tool guidance to include official endpoint references, quota/rate-limit behavior, and when to use first-party vs third-party sources.
- [ ] Add anti-pattern warning blocks with detection signals and exact mitigations.
- [ ] Add response-effect analysis instructions (with-reply vs without-reply cohorts, no default causal language).
- [ ] Add compliance/provenance rules for quote reuse, AI processing disclosure, and redistribution scope.
- [ ] Extend artifact schema with `source_provenance`, `quality_signals`, `coverage`, and `compliance` objects (`additionalProperties: false`).

---

## Draft Content for SKILL.md

> This is the most important section. For every recommendation above, write the **actual text** that should go into SKILL.md - as if you were writing it. Be verbose and comprehensive. The future editor will cut what they don't need; they should never need to invent content from scratch.
>
> Rules:
> - Write full paragraphs and bullet lists, not summaries
> - For methodology changes: write the actual instruction text in second person ("You should...", "Before doing X, always verify Y")
> - For schema changes: write the full JSON fragment with all fields, types, descriptions, enums, and `additionalProperties: false`
> - For anti-patterns: write the complete warning block including detection signal and mitigation steps
> - For tool recommendations: write the actual `## Available Tools` section text with real method syntax
> - Do not hedge or abbreviate - if a concept needs 3 paragraphs to explain properly, write 3 paragraphs
> - Mark sections with `### Draft: <topic>` headers so the editor can navigate

### Draft: Methodology - Analysis Cadence and Evidence Discipline

---
### Analysis cadence (required)

You must run app-store voice-of-market analysis in three distinct windows. Do not collapse these windows into one score:

1. `T+24-72h` after a release: triage window. Use this window to identify urgent regressions and support load changes. Treat conclusions as provisional because platform publication/moderation behavior can delay visible rating/review movement.
2. `T+28d` after a release: stabilization window. Use this window for directional claims about release impact and recurring pain themes.
3. `T+90d` rolling: trend window. Use this window for strategy-level calls, persistent differentiation themes, and competitive positioning.

Before writing any directional statement, verify that your claim is anchored to one of these windows and that your evidence meets minimum sample requirements. If evidence is insufficient, explicitly output `claim_strength="descriptive"` and state what additional data is required.

### Evidence thresholds (required)

You must attach sample size and confidence information to every proportion-style claim (for example, "1-star share increased" or "theme X now dominates"). At minimum:

- If `n < 30`, output only descriptive observations; do not output directional language.
- If you need +/-10 percentage-point precision at 95% confidence, target approximately `n>=97`.
- If you need +/-5 percentage-point precision at 95% confidence, target approximately `n>=385`.
- Use Wilson interval as default CI method for sparse or imbalanced segments.

These thresholds are statistical planning defaults, not absolutes. If your method uses different assumptions, state them explicitly.

### Claim-strength rules (required)

For each major conclusion, set:

- `descriptive`: pattern observed, confidence low or sample insufficient.
- `directional`: movement likely, some uncertainty remains.
- `supported`: movement supported by sample/interval quality and confirmed across at least one secondary signal (for example crash trend, uninstall trend, or sustained recurrence across windows).

Do not output causal language (for example "this caused retention drop") unless causal design requirements are met.
---

### Draft: Methodology - Segmentation, Theme Extraction, and Interpretation

---
### Mandatory segmentation keys

Before extracting insights, you must segment by:

- `platform` (ios/android)
- `app_version`
- `country_region`
- `language`
- `rating_bucket` (1-2, 3, 4-5)

If one of these keys is unavailable, include that limitation in output and reduce claim strength.

### Theme extraction model

You must use a two-layer model:

1. **Comparable taxonomy layer:** classify reviews into stable categories (for example stability/performance/usability/pricing/support/privacy) so trends can be compared across windows.
2. **Discovery layer:** run open clustering to detect emerging issues not covered by fixed categories.

Every theme in output must include:

- `theme_name`
- `theme_layer` (`taxonomy` or `discovery`)
- `support_count`
- `support_share`
- `example_quote_ids`
- `confidence`

Never publish a theme without source traceability. If you cannot map a theme to source review IDs, drop it.

### Multilingual handling

When translation is used, preserve both original text and translated text references. For top negative themes that influence prioritization, validate with original-language samples before final ranking. If language coverage is partial, output `coverage_status="partial_language_coverage"` and list excluded segments.

### Interpretation rules

You must report both rating distribution and textual theme evidence. Do not treat average rating as sufficient evidence. For every major claim, provide:

- the time window,
- the sample size,
- the segment scope,
- the quality notes (for example moderation lag, low volume, translation risk).
---

### Draft: Available Tools - Practical Usage with Real API Anchors

---
### Tool usage strategy

Use first-party APIs as the trust anchor for operational review analysis. Use third-party providers only when you need capabilities that first-party sources do not provide (for example historical backfill, cross-competitor enrichment, or topic APIs).

#### First-party references (official API anchors)

- Apple review list: `GET /v1/apps/{id}/customerReviews`
- Apple version review list: `GET /v1/appStoreVersions/{id}/customerReviews`
- Apple response create/update: `POST /v1/customerReviewResponses`
- Google review list: `GET /androidpublisher/v3/applications/{packageName}/reviews`
- Google review get: `GET /androidpublisher/v3/applications/{packageName}/reviews/{reviewId}`
- Google reply: `POST /androidpublisher/v3/applications/{packageName}/reviews/{reviewId}:reply`

#### Internal connector calls (use existing verified methods)

```python
appstoreconnect(op="call", args={
  "method_id": "appstoreconnect.customerreviews.list.v1",
  "app_id": "123456789",
  "filter[rating]": [1, 2, 3, 4, 5],
  "sort": "-createdDate",
  "limit": 100,
})

google_play(op="call", args={
  "method_id": "google_play.reviews.list.v1",
  "packageName": "com.example.app",
  "translationLanguage": "en",
  "maxResults": 100,
})

google_play(op="call", args={
  "method_id": "google_play.reviews.get.v1",
  "packageName": "com.example.app",
  "reviewId": "gp:AOqpTOExample",
})
```

### Rate-limit and quota behavior

You must assume quota constraints and design your run as a bounded queue:

- prioritize newest reviews first,
- paginate deterministically,
- back off on quota/rate-limit signals,
- record partial completion rather than failing silently,
- emit `limitations` entries when quota limits reduce coverage.

### Source selection decision rule

- Use first-party only when analyzing your own app and recent operational changes.
- Add third-party provider when you need historical backfill or competitor-scale coverage.
- When combining sources, annotate provenance per record and do not merge records without source identity.
---

### Draft: Competitive Comparison Framework

---
### Competitor comparison protocol (required)

When comparing against competitors, you must declare your sampling frame before analysis:

- peer app list,
- date range,
- segment parity rules (version/country/language),
- inclusion and exclusion rules.

Never compare your 90-day window against a competitor 7-day window. Never compare one locale against global competitor averages without an explicit limitation note.

### Comparison output structure

For each peer, report:

- volume (`review_count`)
- rating distribution (not only average)
- top negative themes with support share
- top positive themes with support share
- notable change since prior window

Then produce a `relative_delta` view for your target app:

- themes where target is worse than peer median,
- themes where target is better than peer median,
- uncertainty flags for low-volume segments.

### Decision guidance

A competitor theme should become a product-priority candidate only when:

1. it appears in at least one target-app segment,
2. it has non-trivial support share in target data,
3. evidence holds in the stabilization or trend window.

Do not prioritize competitor-only complaints that do not appear in your own user feedback unless strategic context explicitly requires anticipatory action.
---

### Draft: Anti-Patterns and Guardrails

---
### Warning: Low-Volume Panic

**What it looks like:** You escalate roadmap actions from very small post-release spikes.
**Detection signal:** Claim made in first 24h or with low `n` and no interval disclosure.
**Consequence:** False urgency, wasted engineering cycles.
**Mitigation:**
1. Enforce cooldown before directional claims.
2. Enforce minimum sample thresholds.
3. Require a corroborating signal before high-priority action.

### Warning: Causality Overreach

**What it looks like:** "Rating drop caused retention drop."
**Detection signal:** No cohort design, no confound handling, only temporal correlation.
**Consequence:** Wrong causal narrative and misallocated effort.
**Mitigation:**
1. Label ratings as observational by default.
2. Add cohort comparison for retention/churn by version and region.
3. Prohibit causal verbs unless explicit causal method is used.

### Warning: Competitor Cherry-Picking

**What it looks like:** Selecting dramatic competitor quotes without denominator.
**Detection signal:** Missing declared sample frame and parity rules.
**Consequence:** Biased strategy conclusions.
**Mitigation:**
1. Require symmetric sampling rules.
2. Require support-share reporting with each quote.
3. Reject outputs that include quote-only claims.

### Warning: Theme Hallucination

**What it looks like:** AI-generated themes with no source review linkage.
**Detection signal:** No quote IDs, no confidence, no abstain behavior.
**Consequence:** Fabricated signal and poor prioritization.
**Mitigation:**
1. Enforce provenance per theme.
2. Include confidence and abstain thresholds.
3. Require human review before publishing strategic recommendations.

### Warning: Privacy Leakage in Quote Reuse

**What it looks like:** Verbatim quotes exported to broad audiences with identifiable detail.
**Detection signal:** PII in quote payloads; unknown permissions for external reuse.
**Consequence:** Policy/legal risk and trust damage.
**Mitigation:**
1. Redact and minimize.
2. Restrict access to raw text.
3. Gate external quote usage on explicit permission and rights notes.
---

### Draft: Compliance, Provenance, and Usage Rights Rules

---
### Compliance baseline

You must treat app-review text as governed data, not free text. For each run, record:

- where data came from,
- what terms/policies apply,
- what downstream use is allowed.

Use official APIs/console exports whenever possible. Avoid scraping-based ingestion paths for production workflows.

### Quote reuse and redistribution

Do not publish verbatim review quotes externally unless usage rights are explicitly confirmed. For Apple-origin quotes, treat marketing reuse as permission-gated. If rights are unknown, default to internal analytics use only.

### AI processing controls

If review text is sent to AI systems, record:

- whether third-party AI was used,
- which processor handled the text,
- what user/policy disclosures apply,
- whether moderation/flagging is enabled for generated summaries.

If any of the above cannot be established, downgrade claim strength and add a limitation note.

### Retention and deletion

Store only fields needed for analysis. Set retention TTL and deletion workflow references. Preserve auditable provenance while minimizing personal-data exposure.
---

### Draft: Reporting Template Text for Final Analyst Output

---
### Required analyst narrative structure

Your final `competitive_summary` and related narrative must follow this order:

1. **Scope and confidence:** define window, segments, and claim strength.
2. **What changed:** list direction and magnitude for key themes/ratings.
3. **Why you believe it:** show supporting evidence counts, intervals, and quote-backed themes.
4. **What is uncertain:** list limitations (coverage gaps, quota impacts, language gaps, potential fraud noise).
5. **Action implications:** recommend next actions with confidence tags.

### Good output example style

"Android US, v9.4, 28-day window: performance-related 1-2 star share rose from 9.8% to 13.1% (Wilson 95% CI does not overlap prior estimate). Claim strength is `directional` because non-English segment coverage is partial. This pattern also appears in competitor delta where target underperforms peer median on stability themes."

### Bad output example style

"Users hate the latest release and competitors are doing much better."
---

### Draft: Schema additions

> Write the full JSON Schema fragment for any new or modified artifact fields.
> Include field descriptions, enums, required arrays, and additionalProperties constraints.

```json
{
  "segment_voice_of_market": {
    "type": "object",
    "required": [
      "target",
      "time_window",
      "result_state",
      "analysis_cadence",
      "methodology",
      "source_provenance",
      "app_snapshots",
      "competitive_summary",
      "quality_signals",
      "coverage",
      "compliance",
      "limitations"
    ],
    "additionalProperties": false,
    "properties": {
      "target": {
        "type": "string",
        "description": "Primary app or segment target being analyzed."
      },
      "time_window": {
        "type": "object",
        "required": [
          "start_date",
          "end_date",
          "window_type"
        ],
        "additionalProperties": false,
        "properties": {
          "start_date": {
            "type": "string",
            "description": "ISO-8601 start date for analysis window."
          },
          "end_date": {
            "type": "string",
            "description": "ISO-8601 end date for analysis window."
          },
          "window_type": {
            "type": "string",
            "enum": ["post_release_72h", "stabilization_28d", "trend_90d", "custom"],
            "description": "Named analysis window type used for this run."
          }
        }
      },
      "result_state": {
        "type": "string",
        "enum": ["ok", "zero_results", "insufficient_data", "technical_failure"],
        "description": "Overall execution state for this artifact."
      },
      "analysis_cadence": {
        "type": "object",
        "required": [
          "release_cooldown_hours",
          "baseline_window_days",
          "comparison_window_days"
        ],
        "additionalProperties": false,
        "properties": {
          "release_cooldown_hours": {
            "type": "integer",
            "minimum": 0,
            "description": "Hours waited post-release before directional claims."
          },
          "baseline_window_days": {
            "type": "integer",
            "minimum": 1,
            "description": "Days in baseline window used for comparison."
          },
          "comparison_window_days": {
            "type": "integer",
            "minimum": 1,
            "description": "Days in current comparison window."
          }
        }
      },
      "methodology": {
        "type": "object",
        "required": [
          "claim_strength",
          "ci_method",
          "sentiment_formula",
          "theme_extraction_mode"
        ],
        "additionalProperties": false,
        "properties": {
          "claim_strength": {
            "type": "string",
            "enum": ["descriptive", "directional", "supported"],
            "description": "Confidence class for major conclusions."
          },
          "ci_method": {
            "type": "string",
            "enum": ["wilson", "jeffreys", "other"],
            "description": "Confidence interval method used for proportion claims."
          },
          "sentiment_formula": {
            "type": "string",
            "description": "Exact sentiment computation formula used in this run."
          },
          "theme_extraction_mode": {
            "type": "array",
            "items": {
              "type": "string",
              "enum": ["taxonomy", "discovery_clustering"]
            },
            "description": "Theme extraction layers used by analysis."
          }
        }
      },
      "source_provenance": {
        "type": "array",
        "description": "Per-source provenance and policy references for ingested review data.",
        "items": {
          "type": "object",
          "required": [
            "platform",
            "collection_method",
            "endpoint_or_report",
            "collected_at",
            "terms_url"
          ],
          "additionalProperties": false,
          "properties": {
            "platform": {
              "type": "string",
              "enum": ["apple_app_store", "google_play", "third_party"],
              "description": "Data source platform."
            },
            "collection_method": {
              "type": "string",
              "enum": ["official_api", "console_export", "vendor_api"],
              "description": "How data was collected."
            },
            "endpoint_or_report": {
              "type": "string",
              "description": "API endpoint or export report identifier."
            },
            "collected_at": {
              "type": "string",
              "description": "ISO-8601 timestamp of collection."
            },
            "terms_url": {
              "type": "string",
              "description": "Policy/terms URL governing source usage."
            }
          }
        }
      },
      "app_snapshots": {
        "type": "array",
        "items": {
          "type": "object",
          "required": [
            "app_name",
            "platform",
            "avg_rating",
            "review_count",
            "rating_distribution",
            "pain_themes",
            "value_themes"
          ],
          "additionalProperties": false,
          "properties": {
            "app_name": {
              "type": "string",
              "description": "Human-readable app name."
            },
            "platform": {
              "type": "string",
              "enum": ["ios", "android", "both"],
              "description": "Store platform context."
            },
            "avg_rating": {
              "type": "number",
              "minimum": 1,
              "maximum": 5,
              "description": "Average rating in selected window."
            },
            "review_count": {
              "type": "integer",
              "minimum": 0,
              "description": "Number of reviews included in snapshot."
            },
            "rating_trend": {
              "type": "string",
              "enum": ["improving", "stable", "declining", "unknown"],
              "description": "Directional trend label for rating movement."
            },
            "rating_distribution": {
              "type": "object",
              "required": ["one_star", "two_star", "three_star", "four_star", "five_star"],
              "additionalProperties": false,
              "properties": {
                "one_star": {"type": "number", "minimum": 0, "maximum": 1, "description": "Share of 1-star ratings."},
                "two_star": {"type": "number", "minimum": 0, "maximum": 1, "description": "Share of 2-star ratings."},
                "three_star": {"type": "number", "minimum": 0, "maximum": 1, "description": "Share of 3-star ratings."},
                "four_star": {"type": "number", "minimum": 0, "maximum": 1, "description": "Share of 4-star ratings."},
                "five_star": {"type": "number", "minimum": 0, "maximum": 1, "description": "Share of 5-star ratings."}
              }
            },
            "pain_themes": {
              "type": "array",
              "items": {"type": "string"},
              "description": "Most frequent negative themes."
            },
            "value_themes": {
              "type": "array",
              "items": {"type": "string"},
              "description": "Most frequent positive themes."
            },
            "representative_quotes": {
              "type": "array",
              "items": {"type": "string"},
              "description": "Redacted review quotes for context."
            }
          }
        }
      },
      "competitive_summary": {
        "type": "string",
        "description": "Narrative summary of relative position and notable deltas."
      },
      "quality_signals": {
        "type": "object",
        "required": [
          "sample_size_n",
          "ci_95",
          "moderation_pause_flag",
          "suspicious_burst_flag"
        ],
        "additionalProperties": false,
        "properties": {
          "sample_size_n": {
            "type": "integer",
            "minimum": 0,
            "description": "Total sample count supporting key claim."
          },
          "ci_95": {
            "type": "string",
            "description": "95% confidence interval summary for key proportion claims."
          },
          "moderation_pause_flag": {
            "type": "boolean",
            "description": "True when platform moderation/publish delays may distort short-window interpretation."
          },
          "suspicious_burst_flag": {
            "type": "boolean",
            "description": "True when review burst pattern indicates possible manipulation/noise."
          }
        }
      },
      "coverage": {
        "type": "object",
        "required": [
          "language_scope",
          "country_scope",
          "excluded_segments"
        ],
        "additionalProperties": false,
        "properties": {
          "language_scope": {
            "type": "string",
            "description": "Language coverage statement, such as english_only or multilingual_partial."
          },
          "country_scope": {
            "type": "string",
            "description": "Country/region coverage description."
          },
          "excluded_segments": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Segments excluded due to low volume, quota, or data quality limits."
          }
        }
      },
      "compliance": {
        "type": "object",
        "required": [
          "allowed_use_scope",
          "redistribution_allowed",
          "usage_rights_note",
          "third_party_ai_shared",
          "quote_permission_status"
        ],
        "additionalProperties": false,
        "properties": {
          "allowed_use_scope": {
            "type": "string",
            "enum": ["internal_analytics", "product_feature", "public_marketing"],
            "description": "Permitted downstream usage scope for this output."
          },
          "redistribution_allowed": {
            "type": "boolean",
            "description": "Whether verbatim quote redistribution is allowed under current rights context."
          },
          "usage_rights_note": {
            "type": "string",
            "description": "Human-readable rights and restrictions note."
          },
          "third_party_ai_shared": {
            "type": "boolean",
            "description": "Whether review text was shared with third-party AI processors."
          },
          "quote_permission_status": {
            "type": "string",
            "enum": ["not_needed", "unknown", "requested", "granted", "denied"],
            "description": "Permission status for external quote use."
          }
        }
      },
      "limitations": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Known limitations, uncertainty notes, and data gaps."
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- There is limited public, app-store-specific consensus on one universal minimum sample threshold for each type of thematic claim; statistical thresholds are adapted from broader proportion-estimation practice (marked evergreen where used).
- Third-party pricing/credit/rate-limit details change frequently and may require verification at implementation time.
- Some legal constraints (especially quote rights outside Apple's explicit guidance) remain jurisdiction-specific and context-dependent; legal review may be needed for public-marketing use cases.
- Public evidence on fake/AI-generated review prevalence is still mixed by category and market; suspicious-burst controls should be treated as risk mitigation rather than definitive fraud classification.
- Apple and Google product/API surfaces continue to evolve quickly; endpoint capabilities and policy language should be revalidated before major skill revisions.
