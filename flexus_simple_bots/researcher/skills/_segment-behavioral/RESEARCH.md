# Research: segment-behavioral

**Skill path:** `flexus-client-kit/flexus_simple_bots/researcher/skills/segment-behavioral/`  
**Bot:** researcher  
**Research date:** 2026-03-05  
**Status:** complete

---

## Context

`segment-behavioral` is the researcher skill for behavioral intent and account intelligence: detecting which accounts are likely in-market now, then prioritizing them by combining intent with fit and trigger context.

The current `SKILL.md` is directionally strong (it already warns that intent is probabilistic and combines intent with fit/events), but it needs stronger 2024-2026 guidance in five areas:

1. methodology sequence and evidence contract,
2. tool landscape realism and integration constraints,
3. API/endpoints reality with explicit "known vs unknown" boundaries,
4. interpretation quality gates and confidence calibration,
5. anti-pattern prevention (operational + compliance + modeling).

This document is written so a future editor can update `SKILL.md` directly without inventing endpoints, method IDs, or confidence rules.

---

## Definition of Done

Research is complete when ALL of the following are satisfied:

- [x] At least 4 distinct research angles are covered (this doc covers 5)
- [x] Each finding has source URLs or named references
- [x] Methodology section is operational, not generic
- [x] Tool/API landscape is mapped with concrete options and caveats
- [x] Anti-patterns include explicit failure signatures and mitigations
- [x] Schema recommendations are grounded in real provider behavior
- [x] Gaps and uncertainties are listed honestly
- [x] Findings are 2024-2026 unless marked evergreen/historical

---

## Quality Gates

Before marking status `complete`, verify:

- No generic filler without concrete implications: **passed**
- No invented provider endpoints are presented as facts: **passed**
- Contradictions are explicit instead of silently resolved: **passed**
- Draft section is the largest and paste-ready: **passed**

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How should strong teams run account-level behavioral intent segmentation in 2024-2026?

**Findings:**

- Treat intent as a scoped workflow, not a dashboard number: lock product line, ICP slice, geography, and time window before reading any surge output.
- Manage topic taxonomy as a maintained asset (pain topics, competitor topics, category topics, role/persona topics), not ad hoc keyword lists.
- Use breadth + intensity rules for qualification (not one spiking topic only). Vendor guidance repeatedly combines score thresholds with topic-threshold logic.
- Keep evidence classes separate until late-stage synthesis: `fit` (firmographic/technographic), `intent` (research behavior), and `trigger` (events/actions).
- Encode recency windows explicitly by source class (weekly or daily feeds vary by provider and integration path).
- Require triangulation for high-priority routing: fit + intent + trigger should all be represented.
- Map account state to action and SLA (for example, now/7-day/nurture) instead of returning rank-only outputs.
- Enforce overlap/duplication controls for topic sets and score inflation risks.
- Treat multi-provider intent as useful only when incremental uniqueness is proven; more providers can add noise if overlap is high.
- Calibrate continuously with closed-loop conversion outcomes (rolling backtests) instead of static score assumptions.
- Bias interpretation to buying groups/account committees, not single-contact events.
- Keep confidence probabilistic and explanation-rich; model updates and source drift require explicit uncertainty notes.

**Contradictions/nuances to encode:**

- High intent activity can still be non-purchase research; surge is not commitment.
- Weekly data can be more stable but less responsive than near-real-time signals.
- Better coverage can still degrade precision if match quality and dedupe are weak.

**Sources:**

- [M1] Forrester: evaluating intent providers (2024) - https://www.forrester.com/blogs/how-to-evaluate-intent-data-providers/
- [M2] 6sense: 6QA logic and windows (Evergreen) - https://support.6sense.com/docs/6sense-qualified-accounts-6qas
- [M3] G2 Buyer Intent documentation (Evergreen) - https://documentation.g2.com/docs/buyer-intent
- [M4] Bombora topic selection guide (Historical/Evergreen mechanics) - https://customers.bombora.com/hubfs/CRC_Brand_Files%20and%20Videos/CRC_Company%20Surge/bombora-intent-topic-selection-guide-june-2020%20(1).pdf
- [M5] 6sense taxonomy docs (Evergreen) - https://support.6sense.com/docs/data-taxonomy
- [M6] 6sense keyword management (Evergreen) - https://support.6sense.com/docs/manage-keywords
- [M7] Bombora score thresholding (Evergreen) - https://customers.bombora.com/crc-coop/scoresthresholds
- [M8] 6sense scores overview (Evergreen) - https://support.6sense.com/docs/6sense-scores-overview
- [M9] Demandbase engagement points (Evergreen) - https://www.demandbase.com/resources/playbook/engagement-points-demandbase-intent/
- [M10] Demandbase intent interpretation (Evergreen) - https://support.demandbase.com/hc/en-us/articles/360056755791-Understanding-Demandbase-Intent
- [M11] Wappalyzer API FAQ (Evergreen) - https://www.wappalyzer.com/faq/api/
- [M12] Wappalyzer lookup behavior (Evergreen) - https://www.wappalyzer.com/docs/api/v2/lookup/
- [M13] Demandbase account scoring (Evergreen) - https://www.demandbase.com/blog/account-scoring/
- [M14] 6sense contact reach model (Evergreen) - https://support.6sense.com/docs/contact-reach-model
- [M15] 6sense predictive buying stages (Evergreen) - https://support.6sense.com/docs/predictive-buying-stages
- [M16] 6sense predictive model insights (Evergreen) - https://support.6sense.com/docs/predictive-model-insights-report
- [M17] Forrester state of business buying 2026 (2026) - https://www.forrester.com/blogs/state-of-business-buying-2026/
- [M18] Gartner B2B buying journey guidance (Evergreen) - https://www.gartner.com/en/sales/insights/b2b-buying-journey

---

### Angle 2: Tool Landscape (Intent + Technographic)
> Which tools are practical, and what constraints materially change output quality?

**Findings:**

- Bombora remains a core account-level third-party intent source, but practical use in downstream systems is often weekly cadence, not sub-daily alerting.
- 6sense is strong for integrated intent + predictive + activation workflows, but matching behavior, orchestration cadence, and entitlement gates matter.
- Demandbase combines native and partner intent, but source add-ons are license-gated and sync latency varies by source.
- G2 Buyer Intent is strong for high-intent evaluation behavior (pricing/compare/competitor interactions), but coverage is naturally bounded by G2 ecosystem behavior.
- ZoomInfo intent is useful when immediate contact/action workflows are required, but teams should validate freshness claims per use case.
- Wappalyzer is useful for technographic context and change detection, with tradeoffs between cached and live crawl modes.
- BuiltWith is strong for historical tech timelines and relationship graphing; rate/credit constraints and coverage exceptions need explicit handling.
- Cognism appears as a workflow layer in many stacks, but API-level intent mechanics are less transparent in public docs and need pilot validation.
- Multi-tool stacks should prioritize complementarity (unique signal contribution) over headline volume.

**Practical comparison notes (compact):**

Tool | Best at | Common failure mode | Operational caution  
Bombora | Topic surge intent | Over-trusting weekly spike | Validate topic overlap + lag  
6sense | Unified account intelligence | Match/routing assumptions | Audit country/domain match quality  
Demandbase | Native + partner orchestration | Add-on cost + source lag | Separate source-level confidence  
G2 | Late-stage buyer actions | Marketplace coverage bias | Use as high-intent corroboration  
ZoomInfo | Intent-to-outreach actioning | Cadence ambiguity | SLA test for alert latency  
Wappalyzer | Fast technographic checks | Cache staleness/live delays | Compare cached vs live on sample set  
BuiltWith | Historical tech evidence | Rate/credit and exclusion limits | Add manual verify path for top accounts

**Sources:**

- [T1] Bombora product overview (Evergreen) - https://bombora.com/products/company-surge/
- [T2] Bombora taxonomy guide (Evergreen) - https://bombora.com/core-concepts/the-complete-guide-to-bomboras-topics-and-taxonomy/
- [T3] 6sense intent data page (Evergreen marketing) - https://6sense.com/platform/intent-data/
- [T4] 6sense API docs (Evergreen) - https://api.6sense.com/docs
- [T5] 6sense FAQ using Bombora (Evergreen) - https://support.6sense.com/docs/faq-using-bombora-company-surge-data-within-6sense
- [T6] Demandbase intent docs (Evergreen) - https://support.demandbase.com/hc/en-us/articles/360056755791-Understanding-Demandbase-Intent
- [T7] Demandbase third-party intent setup (Evergreen) - https://support.demandbase.com/hc/en-us/articles/12043605367195-Understanding-Third-Party-Intent-in-Demandbase-One
- [T8] G2 buyer intent docs (Evergreen) - https://documentation.g2.com/docs/buyer-intent
- [T9] G2 buyer intent reference (Evergreen) - https://documentation.g2.com/docs/buyer-intent-data-reference
- [T10] ZoomInfo intent endpoint reference (Evergreen) - https://docs.zoominfo.com/reference/enrichinterface_enrichintent
- [T11] ZoomInfo release stream (2024-2026) - https://tech-docs-library.zoominfo.com/public-zoominfo-release-notes.pdf
- [T12] Wappalyzer API docs (Evergreen) - https://www.wappalyzer.com/docs/api/v2/lookup/
- [T13] Wappalyzer plan gating (Evergreen) - https://wappalyzer.com/pricing/
- [T14] BuiltWith Domain API (Evergreen) - https://api.builtwith.com/domain-api
- [T15] BuiltWith dataset fields (Evergreen) - https://kb.builtwith.com/datasets/builtwith-dataset-fields/
- [T16] Cognism intent overview (Evergreen marketing) - https://www.cognism.com/intent-data

---

### Angle 3: API Reality & Verified Endpoints
> Which endpoint facts are actually public and safe to document?

**Findings:**

- Endpoint shapes are heterogeneous across providers; one adapter style is not enough.
- Bombora's publicly available API docs are mostly historical (2019-2020 updates), so behavior should be contract-validated at runtime.
- Bombora intent retrieval is explicitly asynchronous (`Create` then `TryGetResult`) with stated processing latency.
- 6sense exposes multiple API hosts and versioned families; hardcoding one host pattern is fragile.
- 6sense limits are mixed: general rate caps plus endpoint-level throughput and quota semantics.
- Wappalyzer has mixed sync/async flows and explicit credit/rate governance in docs.
- BuiltWith has current versioned families (`v22`, `free1`, `lists12`, `trends/v6`) and separate legacy dedicated live guidance.
- Demandbase intent endpoint paths are not clearly exposed in the public pages reviewed; avoid claiming specific intent endpoints without tenant docs.
- TrustRadius intent API references exist publicly, but endpoint details are not clearly exposed in open pages.

**Verified endpoint examples (documentation-backed):**

- Bombora:
  - `POST https://sentry.bombora.com/v4/Surge/Create`
  - `GET https://sentry.bombora.com/v2/Surge/TryGetResult?id={report_id}`
  - `GET https://sentry.bombora.com/v2/cmp/GetMyTopics`
- 6sense:
  - `GET https://epsilon.6sense.com/v3/company/details`
  - `POST https://api.6sense.com/v1/enrichment/company`
  - `POST https://api.6sense.com/v2/enrichment/people`
- Wappalyzer:
  - `GET https://api.wappalyzer.com/v2/lookup/`
  - `GET https://api.wappalyzer.com/v2/credits/balance/`
  - `POST https://api.wappalyzer.com/v2/lists`
- BuiltWith:
  - `GET https://api.builtwith.com/v22/api.{json|xml|csv}?KEY={key}&LOOKUP={domain}`
  - `POST https://api.builtwith.com/v22/domain/bulk?KEY={key}`
- Related public intent APIs:
  - `GET https://data.g2.com/api/v1/intent-history`
  - `POST https://api.zoominfo.com/gtm/data/v1/intent/search`

**Public endpoint details not clearly available from open docs reviewed:**

- Demandbase intent-specific endpoint paths (public developer pages do not clearly publish intent endpoint patterns in open view)
- TrustRadius intent endpoint patterns
- Cognism intent API internals

**Sources:**

- [A1] Bombora API index (Historical) - https://bombora-partners.atlassian.net/wiki/spaces/DOC/pages/1212420/Bombora+API
- [A2] Bombora Surge API (Historical) - https://bombora-partners.atlassian.net/wiki/spaces/DOC/pages/20381698/Surge%2BAPI
- [A3] Bombora Create report v4 (Historical) - https://bombora-partners.atlassian.net/wiki/spaces/DOC/pages/635240449/Create+Company+Surge+Report+v4
- [A4] 6sense API docs - https://api.6sense.com/docs
- [A5] 6sense API credits/tokens - https://support.6sense.com/docs/api-credits-api-tokens
- [A6] 6sense API segment settings - https://support.6sense.com/docs/api-settings-segments-and-score-configurations-for-apis
- [A7] 6sense release notes 2026-02-13 - https://support.6sense.com/docs/2026-02-13-product-release-notes
- [A8] Wappalyzer API basics - https://www.wappalyzer.com/docs/api/v2/basics
- [A9] Wappalyzer API lookup - https://www.wappalyzer.com/docs/api/v2/lookup
- [A10] Wappalyzer API lists - https://www.wappalyzer.com/docs/api/v2/lists/
- [A11] BuiltWith API home - https://api.builtwith.com/
- [A12] BuiltWith Domain API - https://api.builtwith.com/domain-api
- [A13] BuiltWith Free API - https://api.builtwith.com/free-api
- [A14] BuiltWith Lists API - https://api.builtwith.com/lists-api
- [A15] BuiltWith Trends API - https://api.builtwith.com/trends-api
- [A16] G2 API docs - https://data.g2.com/api/docs
- [A17] ZoomInfo auth docs - https://docs.zoominfo.com/docs/authentication
- [A18] ZoomInfo intent search reference - https://docs.zoominfo.com/reference/searchinterface_searchintent
- [A19] Demandbase developer hub (partial public detail) - https://developer.demandbase.com/
- [A20] Demandbase readme docs (partial public detail) - https://demandbase.readme.io/reference
- [A21] TrustRadius intent API entry point (partial public detail) - https://trustradius.freshdesk.com/support/solutions/articles/43000666829-trustradius-intent-api

---

### Angle 4: Data Interpretation & Signal Quality
> What is real signal vs noise in behavioral intent scoring?

**Findings:**

- Baseline context is required; surge without historical/account context is weak evidence.
- Use cluster-level corroboration (topic breadth + score) to reduce one-topic false positives.
- Keep `fit`, `in_market`, and `reach/engagement` as separate dimensions before total scoring.
- Normalize intent interpretation by account size band; raw researcher count is not directly comparable.
- Use stage + activity + recency together; one scalar score should not drive high-priority action alone.
- Require identity/match confidence labels when mapping signals to CRM accounts.
- Exclude or downweight noisy behavioral features where providers document known false-positive risk (for example, email-security scan artifacts).
- Treat bot/invalid-traffic hygiene as confidence input, not just a background hygiene task.
- Thresholds must be cost-based (FP/FN tradeoff), not fixed defaults.
- Calibration matters: ranking quality and probability calibration are different; both should be checked.
- Confidence policies should include caps for sparse, stale, ambiguous, or single-source evidence.

**Common misreads and corrections:**

- Misread: "High intent score means immediate buying intent."  
  Correction: It indicates elevated behavior; require fit + corroboration + recency before escalation.
- Misread: "Single topic spike is enough for high-priority routing."  
  Correction: Use topic breadth/cluster logic and secondary evidence.
- Misread: "Higher match rate means better identity quality."  
  Correction: Track precision/recall and uncertainty, not match-rate vanity alone.
- Misread: "Model score is calibrated probability."  
  Correction: Validate calibration and monitor drift explicitly.

**Confidence policy implications:**

- Keep both numeric confidence and grade (`high`, `medium`, `low`, `insufficient`).
- Cap confidence when evidence is single-source, single-contact, or low-quality.
- Add downgrade rules for unresolved contradictions, weak mapping, stale windows, and IVT risk.
- Backtest and recalibrate periodically using observed downstream outcomes.

**Sources:**

- [I1] Bombora thresholding guidance (Evergreen) - https://customers.bombora.com/crc-coop/scoresthresholds
- [I2] Bombora signal building (Evergreen) - https://customers.bombora.com/crc-brand/build-signal
- [I3] 6sense scores overview (Evergreen) - https://support.6sense.com/docs/6sense-scores-overview
- [I4] 6sense buying stages (Evergreen) - https://support.6sense.com/docs/predictive-buying-stages
- [I5] 6sense fit model docs (Evergreen) - https://support.6sense.com/docs/account-profile-fit-model
- [I6] Demandbase intent explanation (Evergreen) - https://support.demandbase.com/hc/en-us/articles/360056755791-Understanding-Demandbase-Intent
- [I7] Demandbase predictive setup guidance (Evergreen) - https://www.demandbase.com/resources/playbook/predictive-models-setup/
- [I8] G2 Buyer Intent docs (Evergreen) - https://documentation.g2.com/docs/buyer-intent
- [I9] G2 buyer intent data reference (Evergreen) - https://documentation.g2.com/docs/buyer-intent-data-reference
- [I10] G2 account mapping caveats (Evergreen) - https://documentation.g2.com/docs/mapping-g2-buyer-intent-data-to-salesforce-accounts-and-leads
- [I11] Google Analytics known bot exclusion (Evergreen) - https://support.google.com/analytics/answer/9888366?hl=en
- [I12] IAB spiders and bots list (Evergreen) - https://iabtechlab.com/software/iababc-international-spiders-and-bots-list/
- [I13] MRC IVT standards addendum (Evergreen) - https://mediaratingcouncil.org/sites/default/files/Standards/IVT%20Addendum%20Update%20062520.pdf
- [I14] NIST AI RMF playbook (Evergreen) - https://www.nist.gov/itl/ai-risk-management-framework/nist-ai-rmf-playbook
- [I15] Google ML thresholding guidance (Evergreen) - https://developers.google.com/machine-learning/crash-course/classification/thresholding
- [I16] scikit-learn calibration docs (Evergreen) - https://scikit-learn.org/dev/modules/calibration.html
- [I17] Forrester state of buying 2026 (2026) - https://www.forrester.com/press-newsroom/forrester-2026-the-state-of-business-buying/

---

### Angle 5: Failure Modes & Anti-Patterns
> What repeatedly fails in real operations, and how should the skill block it?

**Anti-pattern findings:**

- **Single-signal escalation**
  - Looks like: one spike auto-routes to outbound.
  - Consequence: false positive workload and poor seller trust.
  - Mitigation: require multi-signal, multi-contact corroboration.
- **No incrementality measurement**
  - Looks like: intent success claimed from raw pipeline lift.
  - Consequence: optimize to correlation instead of causal impact.
  - Mitigation: treatment/control or holdout design.
- **CRM hygiene debt**
  - Looks like: stale/duplicate account records feed scoring.
  - Consequence: wrong ownership and weak personalization.
  - Mitigation: freshness SLAs, dedupe, ownership rules.
- **Handoff ambiguity**
  - Looks like: no explicit marketing-to-sales routing criteria/SLA.
  - Consequence: stalled response and lead quality conflict.
  - Mitigation: codify handoff states and closed-loop feedback.
- **Deliverability-blind outreach spikes**
  - Looks like: intent list bursts without sender controls.
  - Consequence: inboxing deterioration and complaint risk.
  - Mitigation: enforce sender requirements + throttle by domain health.
- **Consent-chain failure**
  - Looks like: unclear consent propagation in ad-tech/activation.
  - Consequence: compliance exposure and policy breach risk.
  - Mitigation: granular consent, revocation propagation, disclosures.
- **Sensitive-data misuse**
  - Looks like: weak controls around sensitive location/behavioral data.
  - Consequence: regulatory enforcement and forced data deletion.
  - Mitigation: sensitive taxonomy + purpose limitation + strict sharing controls.
- **Identity over-merge**
  - Looks like: weak/shared identifiers treated as definitive matches.
  - Consequence: cross-account contamination and wrong activation.
  - Mitigation: confidence-scored matching + blocked-value rules.
- **Match-rate vanity**
  - Looks like: success measured by "% matched" only.
  - Consequence: hidden precision/recall failure.
  - Mitigation: evaluate precision/recall/F1 on ground truth.
- **Threshold/calibration drift neglect**
  - Looks like: static thresholds with no monitoring.
  - Consequence: silent quality decay and spend inefficiency.
  - Mitigation: continuous calibration/drift monitoring and retraining policy.

**Risk prioritization (highest first):**

1. Sensitive-data and consent-chain noncompliance
2. Identity quality failures
3. Calibration/drift neglect
4. CRM/orchestration quality debt
5. Causal mismeasurement of program impact

**Sources:**

- [F1] HubSpot sales trends 2024 - https://www.hubspot.com/hubfs/HubSpots%202024%20Sales%20Trends%20Report.pdf
- [F2] Validity CRM data management 2024 - https://www.validity.com/wp-content/uploads/2024/05/The-State-of-CRM-Data-Management-in-2024.pdf
- [F3] Google Ads conversion lift (Evergreen) - https://support.google.com/google-ads/answer/12003020?hl=en
- [F4] Google sender guidelines (Evergreen) - https://support.google.com/a/answer/81126
- [F5] Google Customer Match policy (Evergreen) - https://support.google.com/adspolicy/answer/6299717
- [F6] Google customer data policies (Evergreen) - https://support.google.com/google-ads/answer/7475709?hl=en
- [F7] ICO B2B marketing guidance (Evergreen/updated) - https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/business-to-business-marketing
- [F8] ICO PECR rules (Evergreen/updated) - https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-on-the-use-of-storage-and-access-technologies/what-are-the-pecr-rules
- [F9] ICO consent operations (Evergreen/updated) - https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-on-the-use-of-storage-and-access-technologies/how-do-we-manage-consent-in-practice
- [F10] CJEU press release 44/24 (2024) - https://curia.europa.eu/jcms/upload/docs/application/pdf/2024-03/cp240044en.pdf
- [F11] FTC InMarket order (2024) - https://www.ftc.gov/news-events/news/press-releases/2024/05/ftc-finalizes-order-inmarket-prohibiting-it-selling-or-sharing-precise-location-data
- [F12] FTC Outlogic/X-Mode order (2024) - https://www.ftc.gov/news-events/news/press-releases/2024/04/ftc-finalizes-order-x-mode-successor-outlogic-prohibiting-it-sharing-or-selling-sensitive-location
- [F13] FTC PADFAA reminder (2026) - https://www.ftc.gov/news-events/news/press-releases/2026/02/ftc-reminds-data-brokers-their-obligations-comply-padfaa
- [F14] Twilio Segment identity onboarding (Evergreen) - https://www.twilio.com/docs/segment/unify/identity-resolution/identity-resolution-onboarding
- [F15] AWS entity resolution accuracy (Evergreen) - https://aws.amazon.com/blogs/industries/measuring-the-accuracy-of-rule-or-ml-based-matching-in-aws-entity-resolution/
- [F16] Vertex AI model monitoring (Evergreen) - https://docs.cloud.google.com/vertex-ai/docs/model-monitoring/overview
- [F17] SageMaker model monitor (Evergreen) - https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor.html
- [F18] Calibration reassessment preprint (2024) - https://arxiv.org/abs/2406.04068

---

## Synthesis

The strongest cross-angle conclusion is that `segment-behavioral` should act as an evidence-quality system, not a raw intent-score relay. In 2024-2026 practice, reliable prioritization requires scope lock, explicit source classes, endpoint/runtime verification, and contradiction-aware confidence handling.

The biggest operational risk is false confidence from one of three shortcuts: single-signal escalation, identity/matching ambiguity, or stale threshold/calibration policy. The correct behavior is confidence-capped output with explicit next checks, not forced certainty.

For implementation quality, API reality matters as much as analytics logic. Public endpoint visibility is uneven across providers, so the skill must separate:

- runtime wrapper discovery (`op="help"`),
- publicly documented provider endpoint facts,
- and "public endpoint details not available" cases.

---

## Recommendations for SKILL.md

> Concrete changes to make in `segment-behavioral/SKILL.md`.

- [x] Add explicit scope-lock and evidence-class contract before scoring.
- [x] Replace loose methodology with strict staged flow (`scope -> collect -> normalize -> triangulate -> gate -> classify -> act`).
- [x] Require topic breadth + intensity qualification (not single-topic score only).
- [x] Add tool/API guidance that starts with runtime method discovery (`op="help"`).
- [x] Add provider endpoint verification map and explicitly document unknown/publicly unavailable endpoint details.
- [x] Add interpretation quality gates (baseline, recency, fit separation, identity quality, calibration).
- [x] Add confidence caps and downgrade rules for sparse/ambiguous evidence.
- [x] Add anti-pattern warning blocks (operational, compliance, identity, model quality).
- [x] Expand schema with provenance, quality-gate results, contradictions, action SLA, and next checks.
- [x] Add pre-`write_artifact` checklist that blocks high-confidence outputs when hard gates fail.

---

## Draft Content for SKILL.md

> Paste-ready sections for direct insertion into `segment-behavioral/SKILL.md`.  
> This is intentionally the largest section.

### Draft: Mission Brief + Evidence Contract

---
You detect behavioral intent signals for account segments.

Core rule: **intent is probabilistic evidence, not purchase certainty**.

Before any prioritization, classify evidence into these classes:

- `fit`: firmographic + technographic match quality
- `intent`: third-party and first-party behavioral research activity
- `trigger`: events that increase readiness to act (evaluation, comparisons, stack changes, events)

Do not collapse these classes into one unlabeled score.

Output rules:

1. If evidence is weak, contradictory, stale, or ambiguous, confidence must be reduced.
2. If identity/account mapping is uncertain, confidence must be capped.
3. If hard quality gates fail, return `insufficient_data` or `ok_with_conflicts` instead of forcing certainty.
4. Never present one surge metric as "will buy."
---

### Draft: Methodology (Replacement)

---
## Methodology

Use this exact sequence:

### Step 0: Scope lock

Define one run scope before collection:
- segment objective,
- geo/market scope,
- time window,
- topic taxonomy scope.

If scope is broad or ambiguous, stop and request clarification.

### Step 1: Build topic set with taxonomy labels

Each monitored topic must be labeled:
- `pain_topic`,
- `category_topic`,
- `competitor_topic`,
- `persona_topic`.

Unmapped topics are allowed only with an explicit `unmapped_topic` flag and reduced confidence.

### Step 2: Collect evidence by class

Collect at least:
1. one intent source,
2. one fit source,
3. one trigger/adjacent corroboration source.

If only one class is available, cap confidence and return specific next checks.

### Step 3: Normalize for comparability

Before scoring:
- align time windows as closely as possible,
- record each provider's freshness cadence,
- record whether values are account-level, contact-level, or aggregated.

### Step 4: Triangulate

For each account:
- evaluate intent intensity,
- evaluate intent breadth,
- evaluate fit quality,
- evaluate trigger presence.

High-priority escalation requires multi-signal corroboration, not single spikes.

### Step 5: Apply quality gates

Run all gates:
1. Baseline-context gate
2. Breadth gate
3. Fit gate
4. Recency gate
5. Identity/match gate
6. Data-quality gate
7. Cross-source gate
8. Calibration-policy gate

If any hard gate fails, block `high` confidence.

### Step 6: Score and classify

Use dimension-level scores and clear tiering:
- `high`,
- `medium`,
- `low`,
- `watch`.

Always include rationale for top-tier accounts.

### Step 7: Assign action + SLA

Every prioritized account must include:
- recommended action (`route_to_sales_now`, `route_within_7d`, `monitor`, `nurture`, `collect_more_data`)
- SLA recommendation (for example `24h`, `7d`, `next cycle`)

### Step 8: Explain uncertainty

Always include:
- contradictions,
- limitations,
- concrete next checks to improve confidence.
---

### Draft: Available Tools (Runtime-Verified)

---
## Available Tools

Always verify available methods first:

```python
bombora(op="help", args={})
sixsense(op="help", args={})
wappalyzer(op="help", args={})
```

Use existing verified wrapper methods from this skill:

```python
bombora(op="call", args={
  "method_id": "bombora.surging.accounts.v1",
  "topics": ["topic_name"],
  "location": "US",
  "size": 50
})

bombora(op="call", args={
  "method_id": "bombora.company.intent.v1",
  "domain": "company.com",
  "topics": ["topic_name"]
})

sixsense(op="call", args={
  "method_id": "sixsense.accounts.details.v1",
  "account_domain": "company.com"
})

sixsense(op="call", args={
  "method_id": "sixsense.accounts.segment.v1",
  "segment_id": "seg_id",
  "limit": 100
})

wappalyzer(op="call", args={
  "method_id": "wappalyzer.bulk_lookup.v1",
  "urls": ["https://company1.com", "https://company2.com"]
})
```

Tool rules:

1. Never call unknown method IDs without `op="help"` confirmation.
2. If one provider fails, continue with remaining evidence and downgrade confidence.
3. Store provider/method provenance for each signal.
4. Avoid claiming provider endpoint support that is not verified in docs.
---

### Draft: Provider Endpoint Verification Notes

---
### Provider endpoint verification notes (audit reference)

Use this only as documentation context. Runtime calls should still use wrapper methods.

Verified public examples:

- Bombora: `/v4/Surge/Create`, `/v2/Surge/TryGetResult`, `/v2/cmp/GetMyTopics`
- 6sense: `/v3/company/details`, `/v1/enrichment/company`, `/v2/enrichment/people`
- Wappalyzer: `/v2/lookup`, `/v2/credits/balance`, `/v2/lists`
- BuiltWith: `/v22/api`, `/v22/domain/bulk`, `/free1/api`, `/lists12/api`, `/trends/v6/api`

Public endpoint details not clearly available in open docs reviewed:

- Demandbase intent-specific endpoint paths
- TrustRadius intent endpoint paths
- Cognism intent API internals

If endpoint details are not publicly documented, do not invent them in analysis output.
---

### Draft: Signal Strength, Quality Gates, and Confidence

---
## Interpretation Quality Gates

Before assigning `high` confidence, all hard gates must pass.

### Gate 1: Baseline-context gate (hard)
- Intent movement must be interpreted against account baseline or cohort baseline.

### Gate 2: Breadth gate (hard)
- Require topic breadth/corroboration for top-tier routing.

### Gate 3: Fit gate (hard)
- High intent with poor fit cannot be top-priority.

### Gate 4: Recency gate (hard)
- Signals outside valid freshness windows are downgraded.

### Gate 5: Identity/match gate (hard for routing)
- Uncertain account mapping caps confidence.

### Gate 6: Data-quality gate (hard for strong claims)
- Known noisy behaviors or IVT risk must reduce confidence.

### Gate 7: Cross-source gate (hard for high confidence)
- Require at least two evidence classes for high-confidence escalation.

### Gate 8: Calibration-policy gate (warning/hard by use case)
- Threshold rationale must be documented; default thresholds without cost logic are downgraded.

Confidence default policy:

- Start `confidence = 0.50`.
- `+0.10` each for passed baseline, breadth, fit, recency, cross-source (max +0.50).
- `+0.05` for explicit calibration/backtest note.
- `-0.10` per unresolved contradiction.
- `-0.15` if identity/match gate fails.
- `-0.10` if data-quality gate fails.
- cap at `0.60` when only one evidence class is present.

Confidence grades:

- `high`: 0.80-1.00
- `medium`: 0.60-0.79
- `low`: 0.40-0.59
- `insufficient`: <0.40
---

### Draft: Anti-Pattern Warning Blocks

---
### WARNING: Intent-Score Literalism

**What it looks like:** one score is treated as purchase certainty.  
**Consequence:** false positive prioritization.  
**Mitigation:** require fit + breadth + trigger corroboration.

### WARNING: Single-Signal Escalation

**What it looks like:** one topic spike auto-routes account to sales.  
**Consequence:** low trust and wasted outbound capacity.  
**Mitigation:** require multi-signal, multi-contact evidence.

### WARNING: Fit-Blind Prioritization

**What it looks like:** high intent outranks poor ICP fit.  
**Consequence:** pipeline quality degradation.  
**Mitigation:** hard fit gate before top-tier routing.

### WARNING: Identity Over-Merge

**What it looks like:** weak/shared identifiers create confident account merges.  
**Consequence:** wrong account actions and contamination.  
**Mitigation:** confidence-scored matching + manual review for uncertain cases.

### WARNING: Match-Rate Vanity

**What it looks like:** quality judged mainly by "% matched".  
**Consequence:** hidden precision/recall failure.  
**Mitigation:** evaluate precision/recall/F1 on sampled truth sets.

### WARNING: Consent-Chain Failure

**What it looks like:** unclear consent lineage and revocation propagation.  
**Consequence:** compliance risk and potential enforcement exposure.  
**Mitigation:** explicit consent metadata, suppression propagation, and purpose limits.

### WARNING: Deliverability-Blind Outreach Bursts

**What it looks like:** large intent-triggered sends without sender health controls.  
**Consequence:** inbox placement deterioration.  
**Mitigation:** sender-authentication checks + rate governance by domain health.

### WARNING: Threshold Drift Neglect

**What it looks like:** static thresholds used despite model/data drift.  
**Consequence:** silent prioritization decay.  
**Mitigation:** periodic calibration and drift monitoring with rollback rules.
---

### Draft: Output Checklist

---
Before calling `write_artifact`, verify:

- Scope lock is recorded (`segment`, `geo`, `window`, `taxonomy`).
- At least two evidence classes are present for strong claims.
- Every signal has `provider`, `method_id`, `evidence_class`, and `captured_at`.
- Fit and intent are scored separately before total score.
- Quality gates are evaluated and stored.
- Contradictions are explicit when present.
- Confidence and confidence grade are consistent.
- Recommended action and SLA are included for prioritized accounts.
- Limitations and next checks are concrete.

If any hard gate fails, do not emit `high` confidence.
---

### Draft: Artifact Schema Additions

```json
{
  "segment_behavioral_intent": {
    "type": "object",
    "required": [
      "segment_id",
      "evaluated_at",
      "result_state",
      "scope_lock",
      "intent_model",
      "evidence_summary",
      "quality_gates",
      "account_scores",
      "confidence",
      "confidence_grade",
      "limitations",
      "next_checks"
    ],
    "additionalProperties": false,
    "properties": {
      "segment_id": {
        "type": "string",
        "description": "Target segment identifier for this behavioral evaluation run."
      },
      "evaluated_at": {
        "type": "string",
        "description": "ISO-8601 timestamp when scoring was finalized."
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
        ],
        "description": "Overall run quality/completeness state."
      },
      "scope_lock": {
        "type": "object",
        "required": [
          "segment_objective",
          "geo_scope",
          "time_window",
          "topic_taxonomy_version"
        ],
        "additionalProperties": false,
        "properties": {
          "segment_objective": {
            "type": "string",
            "description": "Primary prioritization objective for this run."
          },
          "geo_scope": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "List of markets/countries covered."
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
              },
              "window_label": {
                "type": "string",
                "description": "Human-readable window label (for example 30d, 90d)."
              }
            }
          },
          "topic_taxonomy_version": {
            "type": "string",
            "description": "Version or label of topic taxonomy used."
          }
        }
      },
      "intent_model": {
        "type": "object",
        "required": [
          "topics_monitored",
          "scoring_dimensions",
          "tier_policy"
        ],
        "additionalProperties": false,
        "properties": {
          "topics_monitored": {
            "type": "array",
            "items": {
              "type": "object",
              "required": [
                "topic",
                "taxonomy_label"
              ],
              "additionalProperties": false,
              "properties": {
                "topic": {
                  "type": "string"
                },
                "taxonomy_label": {
                  "type": "string",
                  "enum": [
                    "pain_topic",
                    "category_topic",
                    "competitor_topic",
                    "persona_topic",
                    "unmapped_topic"
                  ]
                }
              }
            }
          },
          "scoring_dimensions": {
            "type": "array",
            "items": {
              "type": "object",
              "required": [
                "dimension",
                "max_points"
              ],
              "additionalProperties": false,
              "properties": {
                "dimension": {
                  "type": "string",
                  "enum": [
                    "intent_fit",
                    "firmographic_fit",
                    "technographic_fit",
                    "trigger_event",
                    "data_quality"
                  ]
                },
                "max_points": {
                  "type": "integer",
                  "minimum": 0
                }
              }
            }
          },
          "tier_policy": {
            "type": "object",
            "required": [
              "high_min_score",
              "medium_min_score"
            ],
            "additionalProperties": false,
            "properties": {
              "high_min_score": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100
              },
              "medium_min_score": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100
              },
              "watch_min_score": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100
              }
            }
          }
        }
      },
      "evidence_summary": {
        "type": "object",
        "required": [
          "providers_used",
          "evidence_classes_covered",
          "provider_windows"
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
          "evidence_classes_covered": {
            "type": "array",
            "items": {
              "type": "string",
              "enum": [
                "fit",
                "intent",
                "trigger"
              ]
            }
          },
          "provider_windows": {
            "type": "array",
            "items": {
              "type": "object",
              "required": [
                "provider",
                "window_label"
              ],
              "additionalProperties": false,
              "properties": {
                "provider": {
                  "type": "string"
                },
                "window_label": {
                  "type": "string"
                },
                "freshness_note": {
                  "type": "string"
                }
              }
            }
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
            }
          }
        }
      },
      "quality_gates": {
        "type": "object",
        "required": [
          "baseline_context_gate",
          "breadth_gate",
          "fit_gate",
          "recency_gate",
          "identity_match_gate",
          "data_quality_gate",
          "cross_source_gate",
          "calibration_policy_gate"
        ],
        "additionalProperties": false,
        "properties": {
          "baseline_context_gate": {
            "type": "string",
            "enum": [
              "pass",
              "warn",
              "fail"
            ]
          },
          "breadth_gate": {
            "type": "string",
            "enum": [
              "pass",
              "warn",
              "fail"
            ]
          },
          "fit_gate": {
            "type": "string",
            "enum": [
              "pass",
              "warn",
              "fail"
            ]
          },
          "recency_gate": {
            "type": "string",
            "enum": [
              "pass",
              "warn",
              "fail"
            ]
          },
          "identity_match_gate": {
            "type": "string",
            "enum": [
              "pass",
              "warn",
              "fail"
            ]
          },
          "data_quality_gate": {
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
          "calibration_policy_gate": {
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
      "account_scores": {
        "type": "array",
        "items": {
          "type": "object",
          "required": [
            "domain",
            "total_score",
            "intent_tier",
            "dimension_scores",
            "signals",
            "match_confidence",
            "recommended_action",
            "sla"
          ],
          "additionalProperties": false,
          "properties": {
            "domain": {
              "type": "string"
            },
            "total_score": {
              "type": "integer",
              "minimum": 0,
              "maximum": 100
            },
            "intent_tier": {
              "type": "string",
              "enum": [
                "high",
                "medium",
                "low",
                "watch"
              ]
            },
            "dimension_scores": {
              "type": "object",
              "required": [
                "intent_fit",
                "firmographic_fit",
                "technographic_fit",
                "trigger_event",
                "data_quality"
              ],
              "additionalProperties": false,
              "properties": {
                "intent_fit": {
                  "type": "number"
                },
                "firmographic_fit": {
                  "type": "number"
                },
                "technographic_fit": {
                  "type": "number"
                },
                "trigger_event": {
                  "type": "number"
                },
                "data_quality": {
                  "type": "number"
                }
              }
            },
            "signals": {
              "type": "array",
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
                  "captured_at"
                ],
                "additionalProperties": false,
                "properties": {
                  "signal_type": {
                    "type": "string",
                    "enum": [
                      "intent_surge",
                      "intent_breadth",
                      "technographic_change",
                      "fit_confirmation",
                      "trigger_event",
                      "negative_signal"
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
                    "description": "Wrapper method ID used at runtime."
                  },
                  "evidence_class": {
                    "type": "string",
                    "enum": [
                      "fit",
                      "intent",
                      "trigger"
                    ]
                  },
                  "evidence_value": {
                    "type": "string"
                  },
                  "window": {
                    "type": "string"
                  },
                  "captured_at": {
                    "type": "string"
                  }
                }
              }
            },
            "match_confidence": {
              "type": "string",
              "enum": [
                "high",
                "medium",
                "low",
                "unknown"
              ],
              "description": "Confidence that signals correctly map to this account."
            },
            "recommended_action": {
              "type": "string",
              "enum": [
                "route_to_sales_now",
                "route_within_7d",
                "monitor",
                "nurture",
                "collect_more_data"
              ]
            },
            "sla": {
              "type": "string",
              "description": "Suggested response window (for example 24h, 7d, next cycle)."
            },
            "rationale": {
              "type": "string"
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
      "contradictions": {
        "type": "array",
        "items": {
          "type": "object",
          "required": [
            "topic",
            "conflict_note",
            "impact_on_confidence",
            "status"
          ],
          "additionalProperties": false,
          "properties": {
            "topic": {
              "type": "string"
            },
            "conflict_note": {
              "type": "string"
            },
            "impact_on_confidence": {
              "type": "string",
              "enum": [
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
      "limitations": {
        "type": "array",
        "items": {
          "type": "string"
        }
      },
      "next_checks": {
        "type": "array",
        "items": {
          "type": "string"
        }
      }
    }
  }
}
```

### Draft: Recording Guidance

---
## Recording

After analysis, call:

```python
write_artifact(
  artifact_type="segment_behavioral_intent",
  path="/segments/{segment_id}/behavioral-intent",
  data={...}
)
```

Do not dump raw JSON in chat.

Before writing:

1. Verify hard quality gates.
2. Verify confidence and confidence grade alignment.
3. Verify top-priority accounts include rationale + action + SLA.
4. Verify contradictions, limitations, and next checks are explicit.
5. If endpoint/method uncertainty existed, include that in limitations.
---

## Gaps & Uncertainties

- Public API detail depth is uneven across providers; some vendor docs are entitlement-gated or incomplete in open view.
- Bombora public endpoint docs are mostly historical (2019-2020 updates); endpoint behavior can differ by contract/version.
- Independent, open, apples-to-apples cross-vendor benchmark datasets for intent precision/recall remain limited.
- Some strategic sources (Forrester/Gartner) are partially paywalled; public summaries were used where full methodology tables are not open.
- Compliance obligations vary by jurisdiction and data category; production deployments should pair this guidance with legal policy in target regions.
