# Research: offer-validation

**Skill path:** `strategist/skills/offer-validation/`
**Bot:** strategist (researcher | strategist | executor)
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`offer-validation` is the strategist skill for testing whether an offer has real demand before full product build. The existing `SKILL.md` already centers the right principle: behavioral evidence beats stated intent, and stronger signals include payment, deposits, LOIs, and pilot commitments.

Research context expansion: 2024-2026 practice has become more operational and risk-aware. Teams now treat offer validation as a staged evidence ladder with explicit quality gates, legal/compliance constraints for pre-sales, and a clearer split between weak intent signals (clicks, signups) and high-friction commitments (non-refundable deposits, paid pilots, signed commercial steps). The strongest upgrade opportunity for this skill is to move from "method list + one conversion target" to a full decision protocol with quality blockers and evidence-strength semantics.

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

- [x] No generic filler without concrete backing
- [x] No invented tool names, method IDs, or API endpoints - only verified real ones
- [x] Contradictions between sources are explicitly noted, not silently resolved
- [x] Volume: findings sections are within 800-4000 words combined
- [x] Volume: `Draft Content for SKILL.md` is longer than all Findings sections combined

Verification notes:
- Endpoint syntax in this document is from vendor documentation links directly cited under each angle.
- Contradictions are explicitly called out in angles and reconciled in `Synthesis`.
- Undated docs are marked as **Evergreen** and used only where current vendor docs are the authoritative source.

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

1. **Behavior-first validation now uses an evidence ladder, not a binary pass/fail.**  
   Teams increasingly separate low-friction intent (views, clicks, signups) from medium-friction intent (confirmed signups, scheduled calls) and high-friction commitment (deposits, paid pilots, signed commercial docs). This directly addresses the "I would use it" bias by requiring progressive commitment for stronger claims. [A1][A2][A10][A11]

2. **Fake-door and painted-door tests are treated as triage mechanisms, not final proof.**  
   Current guidance emphasizes hypothesis pre-definition, realistic framing, and immediate post-click transparency. Practitioners use these tests to decide whether to run deeper commitment tests, not to justify full build alone. [A1][A2]

3. **Landing-page tests are run with stricter cadence and hygiene than older startup playbooks.**  
   Google Ads experiment guidance emphasizes split stability, controlled variable scope, and sufficient runtime for conversion cycles; this reduces false confidence from early noise or campaign churn. [A3][A4]

4. **Pre-launch signup programs are now explicitly modeled as launch predictors with caveats.**  
   Kickstarter reports strong pre-launch signal patterns (for example, higher conversion among pre-launch followers than post-launch followers), but this still represents intent-stage evidence unless paired with commitment. [A5][A6]

5. **Pre-sale/deposit methodology requires explicit payment-design and policy communication.**  
   Teams now define charge timing, refund/cancellation terms, and customer communication windows as part of experiment design itself. Payment mechanics are part of signal quality, not an implementation detail. [A7][A9]

6. **Legal feasibility is part of validation design for pre-sales.**  
   FTC Mail/Internet/Telephone Order Rule requirements (reasonable shipping basis, delay notices, consent/refund paths) affect whether a "demand test" is operationally valid and ethically acceptable. [A8]

7. **B2B offer validation is converging on paid pilot discipline.**  
   Recent SaaStr operator guidance consistently pushes paid pilots with narrow scopes, explicit success criteria, and named decision owners, because free pilots often inflate learning but under-predict conversion. [A10][A11]

8. **Pilot/POC planning quality strongly predicts conversion utility.**  
   AWS and Microsoft pilot guidance both stress bounded scope, explicit outcomes, checkpoint governance, and post-pilot decision criteria. In practice, these are methodology controls for avoiding pilot purgatory. [A12][A13]

9. **Decision quality is moving from single uplift metrics to risk-aware decision matrices.**  
   Spotify's risk-aware experimentation framework formalizes success, guardrails, deterioration, and quality checks. Offer validation guidance should mirror this structure to avoid over-weighting a single conversion metric. [A14][A15]

10. **Sequential monitoring is accepted, but only with method discipline.**  
    Teams increasingly monitor continuously with sequential approaches, yet still separate early directional reads from final commitment decisions requiring stronger precision. [A16][A17]

**Contradictions observed:**
- Signup momentum can be highly predictive for launches in creator ecosystems, but B2B commercialization sources treat unpaid intent as weak evidence. Practical resolution: stage conclusions by evidence tier instead of one global verdict. [A5][A6][A10][A11]
- Faster decisions via continuous monitoring conflict with fixed-horizon guidance for stable estimates. Practical resolution: define method upfront and use early calls for risk containment, not final pricing/roadmap commitment. [A3][A4][A16]

**Sources:**
- [A1] Amplitude, "Fake door testing" (2025): https://amplitude.com/explore/experiment/fake-door-testing
- [A2] Amplitude, "Painted door testing" (2025): https://amplitude.com/explore/experiment/painted-door-testing
- [A3] Google Ads Help, "Set up an experiment" (current, **Evergreen**): https://support.google.com/google-ads/answer/7281575?hl=en
- [A4] Google Ads Help, experimentation timing guidance (current, **Evergreen**): https://support.google.com/google-ads/answer/13826584?hl=en
- [A5] Kickstarter, "The anatomy of a great pre-launch page" (2025): https://updates.kickstarter.com/the-anatomy-of-a-great-kickstarter-prelaunch-page/
- [A6] Kickstarter, "How to maximize pre-launch sign ups" (2025): https://updates.kickstarter.com/how-to-maximize-pre-launch-sign-ups-for-your-kickstarter-campaign/
- [A7] Shopify, "How pre-orders work" (2025): https://www.shopify.com/blog/pre-orders
- [A8] FTC, Mail/Internet/Telephone Order Rule (current, **Evergreen**): https://www.ftc.gov/legal-library/browse/rules/mail-internet-or-telephone-order-merchandise-rule
- [A9] Stripe, "Deposit invoices 101" (2025): https://stripe.com/us/resources/more/deposit-invoices-101-what-they-are-and-how-to-use-them
- [A10] SaaStr, paid pilot guidance (2025): https://www.saastr.com/we-are-a-b2b-saas-startup-and-want-to-develop-our-product-in-pilots-with-customers-should-we-charge-for-the-pilots-and-how-much/
- [A11] SaaStr, pilot conversion and execution guidance (2025): https://www.saastr.com/dear-saastr-were-starting-a-big-paid-pilot-how-do-maximize-the-chances-of-success/
- [A12] AWS, "Conduct a proof of concept in Amazon Redshift" (2024): https://aws.amazon.com/blogs/big-data/successfully-conduct-a-proof-of-concept-in-amazon-redshift
- [A13] Microsoft Learn, "Pilot essentials" (current, **Evergreen**): https://learn.microsoft.com/en-us/microsoftteams/pilot-essentials
- [A14] Spotify Engineering, "Risk-aware product decisions in A/B tests" (2024): https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics/
- [A15] Statsig, "What are guardrail metrics in A/B tests?" (2025): https://www.statsig.com/blog/what-are-guardrail-metrics-in-ab-tests
- [A16] Statsig docs, sequential testing (current, **Evergreen**): https://docs.statsig.com/experiments/advanced-setup/sequential-testing
- [A17] Optimizely support, native global holdouts (2025): https://support.optimizely.com/hc/en-us/articles/41924760675981-Native-global-holdouts-in-Feature-Experimentation

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

1. **Stripe is the primary "hard commitment" stack for offer tests.**  
   Verified endpoints include `POST /v1/payment_intents` and `POST /v1/checkout/sessions`. Useful constraints are explicit: minimum amount floors, line-item caps, and known rate limits (global and endpoint-level). This makes Stripe suitable for deposit and paid-intent evidence with predictable integration contracts. [B1][B2][B3]

2. **PayPal Orders v2 supports deposit-style flows but requires adaptive traffic handling.**  
   Verified endpoints include `POST /v2/checkout/orders`, authorize, and capture operations. Rate-limit behavior is explicitly documented as dynamic rather than static quotas, so client design must include robust backoff, token reuse, and webhook-first updates. [B4][B5]

3. **Square Payments API is useful when idempotency and delayed capture are required.**  
   Verified endpoint: `POST /v2/payments`; requires `idempotency_key` and documents delayed capture windows and SCA tooling. This maps cleanly to pre-sale commitment evidence with lower double-charge risk. [B6]

4. **Waitlist and lead-capture tooling has strict anti-abuse quotas that can distort tests if ignored.**  
   HubSpot forms submission APIs enforce endpoint limits and short-window abuse protection. If traffic bursts are not handled, false "demand drop" can be self-inflicted by throttling rather than offer quality. [B7]

5. **Landing-page platforms are operationally viable but require explicit API key security and quota planning.**  
   Unbounce API provides page and lead management with documented requests/minute caps. This is enough for medium-scale fake-door operations but requires throttled ingestion and secure key handling. [B8]

6. **Scheduling APIs are part of validation stack quality when interviews/pilot calls are the commitment step.**  
   Cal.com v2 and Google Calendar APIs support booking orchestration with versioning/quota rules; missing version headers or quota handling can silently degrade downstream evidence volume. [B9][B10]

7. **Analytics ingestion APIs have payload and throughput caps that materially affect signal integrity.**  
   GA4 Measurement Protocol and Amplitude HTTP v2/Batch APIs publish per-request and throughput limits. Offer-validation SKILL guidance should include ingestion-quality checks (drop rates, malformed events, late arrivals) to avoid false readouts. [B11][B12]

8. **CRM/waitlist stores can bottleneck real-time tests despite generous monthly plans.**  
   Airtable's per-base throughput ceiling is fixed and can throttle bursty campaigns even when monthly call allowances remain. Integration architecture must include queueing and batch writes. [B13]

9. **Email nurture and re-engagement tools have both connection and queue constraints.**  
   Mailchimp documents simultaneous connection caps and batch queue limits. Offer tests that rely on nurture and reminder loops need batch scheduling strategy, not ad hoc API burst calls. [B14]

10. **Experimentation/flag platforms expose robust APIs but numeric limits can be opaque.**  
    LaunchDarkly provides route/global rate-limit headers and API version pinning but does not publish full static numeric limits. This creates a contradiction between "enterprise-grade API" and deterministic throughput planning. [B15]

11. **API standards that matter in 2024-2026 stacks:**  
    webhook-first state handling, idempotent write primitives for money/booking actions, version pinning in headers, exponential backoff with jitter, and separation of control-plane vs runtime pipelines. These are now baseline requirements, not advanced best practices. [B3][B5][B6][B9][B15]

**Contradictions observed:**
- Vendor docs often claim flexible scale while withholding fixed rate ceilings (for example PayPal, LaunchDarkly), forcing conservative integration assumptions. [B5][B15]
- "200 OK accepted" does not always imply valid analytics interpretation (notably GA4 payload acceptance behavior), so ingestion acknowledgement and analytical validity must be separated. [B11]

**Sources:**
- [B1] Stripe API, create PaymentIntent (**Evergreen**): https://docs.stripe.com/api/payment_intents/create
- [B2] Stripe API, create Checkout Session (**Evergreen**): https://docs.stripe.com/api/checkout/sessions/create
- [B3] Stripe docs, rate limits (**Evergreen**): https://docs.stripe.com/rate-limits
- [B4] PayPal Orders v2 API (**Evergreen**): https://developer.paypal.com/docs/api/orders/v2/#orders_create
- [B5] PayPal API rate-limiting guide (current, **Evergreen**): https://docs.paypal.ai/developer/how-to/api/rate-limiting
- [B6] Square Payments API (2026 API version page): https://developer.squareup.com/reference/square/payments-api/create-payment
- [B7] HubSpot forms API limit updates (2021/2023, **Evergreen operational**): https://developers.hubspot.com/changelog/announcing-forms-submission-rate-limits and https://developers.hubspot.com/changelog/additional-rate-limit-protection-being-added-to-form-submissions-api
- [B8] Unbounce API docs (**Evergreen**): https://developer.unbounce.com/getting_started/ and https://developer.unbounce.com/api_reference/#tag/Pages
- [B9] Cal.com API v2 intro and bookings (2024-2026 active docs): https://cal.com/docs/api-reference/v2/introduction and https://cal.com/docs/api-reference/v2/bookings/get-all-bookings
- [B10] Google Calendar API quota and events insert (**Evergreen**): https://developers.google.com/workspace/calendar/api/guides/quota and https://developers.google.com/workspace/calendar/api/v3/reference/events/insert
- [B11] GA4 Measurement Protocol reference and limitations (**Evergreen**): https://developers.google.com/analytics/devguides/collection/protocol/ga4/reference and https://developers.google.com/analytics/devguides/collection/protocol/ga4/sending-events#limitations
- [B12] Amplitude HTTP v2 and batch ingest docs (**Evergreen**): https://amplitude.com/docs/apis/analytics/http-v2 and https://www.docs.developers.amplitude.com/analytics/apis/batch-event-upload-api/
- [B13] Airtable API call limits (**Evergreen**): https://support.airtable.com/docs/managing-api-call-limits-in-airtable
- [B14] Mailchimp Marketing API fundamentals and batch guide (**Evergreen**): https://mailchimp.com/developer/marketing/docs/fundamentals/ and https://mailchimp.com/developer/marketing/guides/run-async-requests-batch-endpoint/
- [B15] LaunchDarkly API docs and rate-limit support note (2025 support page): https://apidocs.launchdarkly.com/ and https://support.launchdarkly.com/hc/en-us/articles/22328238491803-Error-429-Too-Many-Requests-API-Rate-Limit

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

1. **Minimum data quality gates are now explicit before interpretation.**  
   Amplitude significance guidance requires minimum sample and event counts per variant for reliable significance outputs. Practically, this supports adding an explicit `invalid_test` state when sample/event floors are not met. [C1]

2. **Conversion benchmarks are source-dependent and highly variable.**  
   Unbounce 2024 benchmark data shows broad channel/category spread, so universal fake-door threshold claims are weak. Offer validation should compare against source-normalized baselines rather than one global pass line. [C2]

3. **CTR improvements alone are weak validation signals.**  
   WordStream 2024 benchmark reporting highlights how click behavior and downstream conversion can diverge. Interpretation should prioritize commitment funnel depth over top-funnel click rates. [C3]

4. **Statistical significance and practical significance must be separate checks.**  
   Platform guidance from LaunchDarkly/Statsig-style methods supports predefining MDE/power decisions; "statistically significant but too small to matter" should be treated as inconclusive or fail depending on business threshold. [C4][C5][C6]

5. **Peeking discipline remains a major quality separator.**  
   Sequential methods allow ongoing checks with valid inference if declared upfront. Fixed-horizon methods with ad hoc peeking should be downgraded because error rates inflate. [C5]

6. **Observed power is not a valid rescue for weak tests.**  
   2024 analyses show post-hoc observed-power extensions can distort Type I error and decision quality. Pre-launch power planning is the practical standard. [C7]

7. **Commitment friction fundamentally changes evidence strength.**  
   Refundable reservation counts can look large but represent weaker commitment than non-refundable deposit or paid pilot conversion. Offer-validation results should explicitly classify commitment tier. [C9][C10][C11]

8. **LOI evidence quality is highly dependent on drafting and process.**  
   Legal commentary shows non-binding labels alone do not fully determine enforceability or practical commitment. Stronger LOI evidence includes specific terms, authority, timeline, and follow-on path clarity. [C12]

9. **Validated/failed/inconclusive classification works best as a rubric, not a single threshold.**  
   Practical classification includes: quality gates, method validity, practical threshold, and commitment depth. Without all four, "validated" is overclaimed. [C1][C4][C5][C8]

**Common misinterpretations and corrections:**
- "p < 0.05 means validated demand" -> correction: require practical threshold and commitment-stage evidence.
- "One CTR threshold works everywhere" -> correction: normalize by channel and audience baseline.
- "Large reservation counts prove willingness to pay" -> correction: encode refundable vs non-refundable vs paid pilot as separate evidence tiers.
- "If observed power is low, just extend until it passes" -> correction: use predeclared power/sample rules only.

**Contradictions observed:**
- Some playbooks push simple threshold heuristics (for speed), while benchmark datasets show large heterogeneity; this tension is solved by using heuristics as priors only, then calibrating to channel-specific baselines. [C2][C3]
- Real-time sequential monitoring enables speed, but precision for strategic commitments still often needs longer windows; this should be encoded as separate "early directional" vs "final validation" checkpoints. [C5][C6]

**Sources:**
- [C1] Amplitude docs, statistical significance FAQ (**Evergreen**): https://amplitude.com/docs/faq/statistical-significance
- [C2] Unbounce, conversion benchmark methodology/report (2024): https://unbounce.com/conversion-benchmark-report/methodology/ and https://unbounce.com/average-conversion-rates-landing-pages
- [C3] WordStream, Google Ads benchmarks (2024): https://www.wordstream.com/blog/2024-google-ads-benchmarks
- [C4] LaunchDarkly docs, sample-size calculator/methodology (**Evergreen**): https://launchdarkly.com/docs/guides/experimentation/sample-size-calc
- [C5] Statsig docs, sequential testing (**Evergreen**): https://docs.statsig.com/experiments/advanced-setup/sequential-testing
- [C6] Statsig docs, power analysis (**Evergreen**): https://docs.statsig.com/experiments-plus/power-analysis
- [C7] Analytics-Toolkit, observed power in online A/B tests (2024): https://blog.analytics-toolkit.com/2024/observed-power-in-online-a-b-testing/
- [C8] Eppo docs, confidence intervals (**Evergreen**): https://docs.geteppo.com/statistics/confidence-intervals/
- [C9] PreProduct, pre-order payment models with transaction distribution (2025): https://preproduct.io/pre-order-payment-models-complete-guide-to-charge-later-deposits-installments-more-on-shopify/
- [C10] The Verge, Rivian reservation reporting (2024): https://www.theverge.com/2024/3/8/24094270/rivian-r2-reservation-number-price-refund
- [C11] PCMag, Tesla Cybertruck non-refundable deposit reporting (2024): https://www.pcmag.com/news/tesla-gets-serious-about-cybertruck-orders-with-non-refundable-1k-deposit
- [C12] Thompson Coburn, LOI lessons (2025): https://www.thompsoncoburn.com/insights/before-you-sign-four-lessons-for-using-letters-of-intent-102lx06/

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

1. **Vanity-demand trap (clicks without commitment).**  
   Signal: high CTA CTR but low confirmed signup/deposit/pilot conversion.  
   Consequence: roadmap overinvestment on shallow intent.  
   Mitigation: define a pre-registered full funnel and require at least one high-friction commitment metric for `validated`. [D1][D2]

2. **Fake-door misuse for complex workflows.**  
   Signal: first-click interest collapses after details; users report misunderstanding.  
   Consequence: false demand signal for offers that fail in real usage paths.  
   Mitigation: use concierge/manual workflow for multi-step value propositions. [D1][D2]

3. **Opaque or deceptive post-click flow.**  
   Signal: backlash/support complaints after "not actually available" screens.  
   Consequence: trust damage reduces future test quality and brand equity.  
   Mitigation: immediate disclosure and transparent in-development framing. [D2][D14]

4. **Pre-sale before fulfillment readiness.**  
   Signal: shipping delays, rising "where is my order?" tickets, high cancellation requests.  
   Consequence: refund burden, chargeback risk, enforcement exposure.  
   Mitigation: pre-sell only with fulfillment basis + delay/consent/refund workflow. [D3][D4]

5. **Delay/refund non-compliance in commerce-style validation tests.**  
   Signal: delayed orders without proper notices or consent options.  
   Consequence: legal action and forced refunds.  
   Mitigation: auditable delay notices, consent tracking, prompt refunds. [D3][D4]

6. **Deposit timing ambiguity (surprise capture).**  
   Signal: complaint/dispute spikes when charges occur unexpectedly.  
   Consequence: payment disputes and lower trust in future offers.  
   Mitigation: explicit payment timeline in checkout and pre-capture reminders. [D4][D5]

7. **Recurring offer cancellation friction.**  
   Signal: cancellation complaints and dispute growth around renewal windows.  
   Consequence: invalid retention signal and regulatory risk.  
   Mitigation: clear cancellation path and consent records. [D5]

8. **Synthetic/fabricated social proof.**  
   Signal: suspicious review bursts, undisclosed incentives, or AI-generated testimonial patterns.  
   Consequence: enforcement + severe trust loss.  
   Mitigation: prohibit fabricated reviews and verify review provenance. [D6][D7]

9. **Concierge false positive from unsustainable manual effort.**  
   Signal: high manual minutes per user and deteriorating service as cohort grows.  
   Consequence: "validated" claim fails once automation is attempted.  
   Mitigation: track manual cost-to-serve and automate highest-load step before scale. [D8][D9]

10. **Pilot proposal without conversion architecture.**  
    Signal: no executive sponsor, no budget path, no signed success criteria.  
    Consequence: successful pilots that never convert to paid rollout.  
    Mitigation: pre-agree KPI outcomes, procurement path, and commercial transition conditions. [D8][D9]

11. **Stated intent over-weighting despite known hypothetical bias.**  
    Signal: enthusiastic interviews/surveys but weak payment behavior.  
    Consequence: demand overestimation and poor pricing decisions.  
    Mitigation: prioritize observed behavior and include a confidence downgrade for intent-only evidence. [D13]

**Case-style signals (2024):**
- FTC order against GOAT for Mail Order Rule violations included over $2M for refunds, illustrating direct downside when pre-sale operations and communications are mishandled. [D3]
- Public reporting on startup pre-sale failures (for example crowdfunding non-delivery disputes) shows legal and trust damage when payment is captured without fulfillment reliability. [D11][D12]

**Sources:**
- [D1] PostHog tutorial, fake door test (current, **Evergreen**): https://posthog.com/tutorials/fake-door-test
- [D2] Amplitude, fake door testing (2025): https://amplitude.com/explore/experiment/fake-door-testing
- [D3] FTC press release, GOAT final order (2024-12): https://www.ftc.gov/news-events/news/press-releases/2024/12/ftc-order-requires-online-retailer-goat-pay-more-2-million-consumers-mail-order-rule-violations
- [D4] FTC business guide, Mail Order Rule (**Evergreen**): https://ftc.gov/business-guidance/resources/business-guide-ftcs-mail-internet-or-telephone-order-merchandise-rule
- [D5] FTC final "Click to Cancel" rule announcement (2024-10): https://www.ftc.gov/news-events/news/press-releases/2024/10/federal-trade-commission-announces-final-click-cancel-rule-making-it-easier-consumers-end-recurring
- [D6] FTC fake reviews/testimonials final rule announcement (2024-08): https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials
- [D7] FTC final order against Rytr testimonial/review service (2024-12): https://www.ftc.gov/news-events/news/press-releases/2024/12/ftc-approves-final-order-against-rytr-seller-ai-testimonial-review-service-providing-subscribers
- [D8] Gartner press release on GenAI production conversion barriers (2024): https://www.gartner.com/en/newsroom/press-releases/2024-05-07-gartner-survey-finds-generative-ai-is-now-the-most-frequently-deployed-ai-solution-in-organizations
- [D9] UK Government, pilot-to-production checklist (2025): https://www.gov.uk/government/publications/unlocking-space-for-investment-growth-hub/track-3-pilot-to-production-checklist
- [D10] SFGate coverage of Forward shutdown (2024): https://www.sfgate.com/tech/article/forward-shuts-down-doctors-office-19917488.php
- [D11] Electrek, Delfast non-delivery lawsuit report (2024): https://electrek.co/2024/07/05/crowdfunding-gone-wrong-customer-sues-delfast-for-e-bike-non-delivery-and-wins/
- [D12] Time Extension, SuperSega pre-order charging confusion report (2024): https://timeextension.com/news/2024/11/confusion-reigns-as-supersega-pre-orders-get-charged-for-the-full-amount
- [D13] Research article, hypothetical bias meta-analysis (2024): https://research.rug.nl/en/publications/accurately-measuring-willingness-to-pay-for-consumer-goods-a-meta
- [D14] NNGroup ethics article (**Evergreen**): https://www.nngroup.com/articles/ethical-dilemmas/

---

### Angle 5+: Regulatory, Ethics, and Trust Constraints
> Add as many additional angles as the domain requires. Examples: regulatory/compliance context, industry-specific nuances, integration patterns with adjacent tools, competitor landscape, pricing benchmarks, etc.

**Findings:**

1. **Offer validation methods that involve payment commitments are regulated operational behaviors, not just experiments.**  
   If a team runs pre-order or deposit tests, shipping basis, delay handling, cancellation path, and refund execution become part of method validity, not legal afterthoughts. [E1][E2]

2. **Trust-preserving design is now part of experimental quality.**  
   Fake-door tests that hide reality or mislead users can poison future learning loops. Transparent "in development" messaging and immediate disclosure are now viewed as practical quality controls. [E4]

3. **Synthetic social proof is explicitly restricted and high-risk.**  
   FTC fake reviews/testimonials actions in 2024 mean teams should treat testimonial evidence provenance as a quality gate in offer validation outputs. [E3]

4. **Compliance maturity changes interpretation confidence.**  
   Two offer tests with identical conversion can carry different decision quality if one has auditable consent/refund/comms logs and the other does not.

5. **Practical implication:** add `legal_compliance_status` and `trust_risk_notes` to schema and block `validated` when unresolved compliance risk exists for payment-based tests.

**Sources:**
- [E1] FTC Mail/Internet/Telephone Order Rule (**Evergreen**): https://www.ftc.gov/legal-library/browse/rules/mail-internet-or-telephone-order-merchandise-rule
- [E2] FTC Click-to-Cancel final rule announcement (2024): https://www.ftc.gov/news-events/news/press-releases/2024/10/federal-trade-commission-announces-final-click-cancel-rule-making-it-easier-consumers-end-recurring
- [E3] FTC fake reviews/testimonials final rule (2024): https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials
- [E4] NNGroup ethical dilemmas guidance (**Evergreen**): https://www.nngroup.com/articles/ethical-dilemmas/

---

## Synthesis

The strongest cross-angle pattern is that modern offer validation is not one test and one conversion number; it is a decision system with staged evidence, quality gates, and commitment semantics. Teams that only track top-funnel responses are increasingly seen as running screening experiments, not true validation.

The second major pattern is that tooling and methodology now force operational maturity earlier. Payment and analytics APIs provide enough precision to run high-quality tests, but their limits, versioning rules, and throttling behavior can quietly degrade evidence integrity if not explicitly modeled.

A meaningful contradiction remains between speed and rigor. Sequential and always-on practices accelerate decisions, while fixed-horizon and practical-significance guidance warns against early overconfidence. The practical resolution is to separate "directional early signal" from "final validation claim" in method and schema.

A final cross-cutting insight is that trust/compliance is no longer peripheral for pre-sale style tests. Regulatory and public case evidence shows that a strong conversion signal can still be a bad strategic decision if it is obtained or executed in ways that trigger refund friction, disputes, or enforcement risk.

---

## Recommendations for SKILL.md

- [x] Add an explicit **evidence ladder** in methodology: intent -> soft commitment -> hard commitment, and require stronger tiers for `validated`.
- [x] Add a **pre-registered decision protocol** section: hypothesis, success threshold, practical threshold, runtime/sample gates, and quality gates before verdict.
- [x] Add a fourth decision state **`invalid_test`** for broken evidence quality (sample, instrumentation, bot/fraud, or compliance failure).
- [x] Upgrade metric guidance from single conversion target to **funnel + commitment depth + guardrail interpretation**.
- [x] Expand tool guidance with internal workflow calls and source-of-truth references for external evidence systems.
- [x] Add named anti-pattern warning blocks with **detection signal, consequence, mitigation, and hard rules**.
- [x] Extend schema with **commitment evidence fields**, **quality gates**, and **compliance/trust status**.
- [x] Add an explicit interpretation rule that **intent-only evidence cannot yield `validated`**.

---

## Draft Content for SKILL.md

### Draft: Validation Philosophy and Evidence Ladder

You must treat offer validation as an evidence ladder, not a binary reaction to signup volume. Before you call an offer validated, classify what type of evidence you have:

1. **Intent evidence**: views, clicks, page engagement, raw email submissions.
2. **Soft commitment evidence**: confirmed email opt-in, scheduled discovery call, signed but non-commercial LOI.
3. **Hard commitment evidence**: non-refundable deposit, paid pilot agreement, purchase event, or signed commercial commitment with accountable owner.

Your conclusion strength must match evidence tier:

- If evidence is intent-only, you may classify as `promising` or `inconclusive`, but not `validated`.
- If evidence reaches soft commitment with clean quality gates, you may classify as `directional_validation`.
- Use `validated` only when hard commitment evidence exists and quality/compliance gates pass.

Do not collapse these tiers into one conversion metric. A high click-through rate and a high non-refundable deposit conversion are not equivalent evidence. Always report both volume and friction level of the action.

---

### Draft: Methodology - Pre-Registered Offer Validation Protocol

Before running any test, you must pre-register the protocol in your artifact:

1. **Hypothesis contract**
   - Write: `If [segment] sees [offer statement], at least [threshold] will complete [target action] within [window]`.
   - Include both statistical and practical thresholds.
   - Include explicit falsification condition.

2. **Method selection**
   - Use `fake_door` or `landing_page_test` for early intent screening.
   - Use `presale_deposit` or `paid_pilot` when you need willingness-to-pay evidence.
   - Use `concierge` when the value proposition depends on multi-step operational delivery.
   - Use `pilot_proposal` for B2B account-level conversion proof.

3. **Decision method declaration**
   - Set `decision_method` to `fixed_horizon` or `sequential_adjusted` before launch.
   - If `fixed_horizon`, do not make final decision before predeclared window/sample is reached.
   - If `sequential_adjusted`, ensure interpretation uses method-consistent confidence logic.

4. **Quality gates**
   - Define minimum sample requirements.
   - Define instrumentation integrity requirement.
   - Define bot/fraud traffic tolerance.
   - Define legal/compliance status requirement for payment-based tests.
   - If any critical gate fails, set result to `invalid_test` and stop business interpretation.

5. **Commitment evidence plan**
   - Define primary commitment event in advance (for example, non-refundable deposit or paid pilot acceptance).
   - Define fallback commitment event if primary is unavailable.
   - Record friction level of each commitment event.

6. **Guardrail plan**
   - Add at least one trust/brand guardrail (complaints, cancellation friction, refund spikes, support burden).
   - Guardrail breach blocks `validated` even when primary conversion improves.

You should never run a payment-based offer test without explicit charge timing, cancellation rules, and refund behavior defined before launch.

---

### Draft: Methodology - Execution and Interpretation Workflow

Run this step-by-step workflow every time:

1. **Activate context**
   - Pull current offer design, messaging, and segment context before writing or updating a validation artifact.
   - If context is missing, stop and gather it first.

2. **Launch test with one primary commitment objective**
   - You can track secondary metrics, but exactly one primary commitment metric determines verdict logic.
   - Do not swap primary metric after data is visible.

3. **Collect full-funnel evidence**
   - Track exposures -> CTA clicks -> submissions -> confirmed submissions -> commitment actions.
   - Record both absolute counts and rates.
   - Segment by traffic source and ICP cohort.

4. **Run quality gates before metric interpretation**
   - If sample floor is not reached, verdict is `inconclusive` or `invalid_test` depending on severity.
   - If instrumentation is degraded, verdict is `invalid_test`.
   - If bot/fraud share exceeds tolerance, verdict is `invalid_test`.
   - If compliance process fails for payment-based tests, verdict is `invalid_test`.

5. **Interpret with commitment-weighted logic**
   - `validated`: hard commitment threshold met, quality gates pass, no severe guardrail breach.
   - `failed`: enough clean data and hard commitment materially below threshold.
   - `inconclusive`: data quality acceptable but insufficient power, mixed commitments, or conflicting segment signals.
   - `invalid_test`: quality/compliance failure prevents valid interpretation.

6. **Decide next action explicitly**
   - If `validated`, specify whether to advance to MVP build or expanded pilot.
   - If `failed`, specify whether to stop or redesign value proposition.
   - If `inconclusive`, specify required follow-up test with changed method/traffic.
   - If `invalid_test`, specify remediation steps before rerun.

Do NOT:
- use click-rate-only wins as final validation,
- keep peeking and stop when a temporary uplift appears,
- claim willingness to pay from refundable/no-obligation reservations alone,
- mark `validated` when compliance status is unresolved on paid tests.

---

### Draft: Available Tools (paste-ready)

Use policy context first, then persist evidence:

```python
flexus_policy_document(op="activate", args={"p": "/strategy/offer-design"})
flexus_policy_document(op="activate", args={"p": "/strategy/messaging"})
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})
```

Persist your result artifact:

```python
write_artifact(
  artifact_type="offer_validation_results",
  path="/strategy/offer-validation-{date}",
  data={...}
)
```

Operational usage rules:

1. You must activate at least one offer context and one segment context artifact before writing validation output.
2. You must include evidence references for every high-impact claim (commitment conversion, payment signal, pilot acceptance).
3. You must write full artifact snapshots, not partial updates, so downstream skills can audit the decision path.
4. If external system evidence is cited (for example Stripe or GA4 exports), include stable IDs and retrieval timestamps in `evidence_refs`.

Reference external API endpoints you may encounter in source evidence (do not invent alternatives):

```text
Stripe: POST /v1/payment_intents
Stripe: POST /v1/checkout/sessions
PayPal: POST /v2/checkout/orders
Square: POST /v2/payments
GA4 Measurement Protocol: POST https://www.google-analytics.com/mp/collect
Amplitude HTTP v2: POST https://api2.amplitude.com/2/httpapi
```

If these references are unavailable or unverifiable in your environment, mark the related evidence as low confidence instead of guessing.

---

### Draft: Anti-Pattern Warning Blocks (paste-ready)

#### Warning: Vanity Demand (CTR without commitment)

**What it looks like in practice:**  
Top-funnel engagement rises but confirmed signups, deposits, or paid pilot actions remain flat.

**Detection signal:**  
`cta_ctr` exceeds target while `hard_commitment_rate` misses by a wide margin.

**Consequence if missed:**  
You over-invest in messaging resonance that does not convert into business value.

**Mitigation steps:**  
1. Require one hard-commitment metric for `validated`.  
2. Segment by traffic source to remove low-intent channel inflation.  
3. Downgrade verdict to `inconclusive` when commitment depth is weak.

**Hard rule:**  
Do not set `conclusion=validated` when evidence tier is `intent_only`.

#### Warning: Post-hoc metric swapping

**What it looks like in practice:**  
Primary success metric changes after data arrives.

**Detection signal:**  
Artifact revision shows changed `primary_commitment_metric` after `start_at`.

**Consequence if missed:**  
Increased false positives and non-reproducible decisions.

**Mitigation steps:**  
1. Lock primary metric before launch.  
2. Log exploratory findings separately.  
3. Create a new follow-up experiment for any post-hoc discovery.

**Hard rule:**  
Metric swap after launch forces `inconclusive` unless rerun under new protocol.

#### Warning: Peeking under fixed-horizon method

**What it looks like in practice:**  
Team stops test at first favorable snapshot under a fixed-horizon design.

**Detection signal:**  
Decision timestamp is earlier than predeclared horizon with no sequential method declaration.

**Consequence if missed:**  
Error inflation and unstable post-launch outcomes.

**Mitigation steps:**  
1. Keep fixed-horizon discipline, or  
2. Switch to sequential-adjusted protocol before launch in the next run.

**Hard rule:**  
Do not mark `validated` if stop decision violated declared method.

#### Warning: Compliance-blind pre-sale

**What it looks like in practice:**  
Payment is captured without clear delay/refund communication path.

**Detection signal:**  
Missing consent records, late delay notices, refund complaints, or dispute spikes.

**Consequence if missed:**  
Regulatory risk, forced refunds, and trust damage.

**Mitigation steps:**  
1. Add compliance checklist for payment-based tests.  
2. Track delay notice, consent, and refund execution fields.  
3. Block final verdict when compliance status is not `pass`.

**Hard rule:**  
`legal_compliance_status=fail` must force `conclusion=invalid_test`.

#### Warning: Concierge heroics mistaken for scalable demand

**What it looks like in practice:**  
Manual team effort hides weak productized value delivery.

**Detection signal:**  
Manual cost-to-serve and time-per-user rise quickly with cohort size.

**Consequence if missed:**  
False positive validation and failed transition to product.

**Mitigation steps:**  
1. Track manual effort as a required metric.  
2. Cap concierge cohort size and define automation handoff threshold.  
3. Require stable delivery outcomes at low manual overhead before claiming validation.

---

### Draft: Schema additions

Use this schema fragment to replace or extend `offer_validation_results`.

```json
{
  "offer_validation_results": {
    "type": "object",
    "required": [
      "experiment_id",
      "offer_id",
      "method",
      "stage",
      "hypothesis",
      "success_threshold",
      "design",
      "results",
      "quality_gates",
      "commitment_evidence",
      "conclusion",
      "next_action",
      "evidence_refs",
      "updated_at"
    ],
    "additionalProperties": false,
    "properties": {
      "experiment_id": {
        "type": "string",
        "description": "Stable identifier for this validation run."
      },
      "offer_id": {
        "type": "string",
        "description": "Stable identifier for the offer variant being tested."
      },
      "method": {
        "type": "string",
        "enum": [
          "fake_door",
          "landing_page_test",
          "presale_deposit",
          "concierge",
          "paid_pilot",
          "pilot_proposal",
          "loi_outreach"
        ],
        "description": "Validation method selected before launch."
      },
      "stage": {
        "type": "string",
        "enum": ["intent", "soft_commitment", "hard_commitment"],
        "description": "Evidence stage this run is intended to validate."
      },
      "hypothesis": {
        "type": "object",
        "required": [
          "target_segment",
          "offer_statement",
          "target_action",
          "expected_rate",
          "falsification_condition"
        ],
        "additionalProperties": false,
        "properties": {
          "target_segment": {
            "type": "string",
            "description": "ICP or segment being tested."
          },
          "offer_statement": {
            "type": "string",
            "description": "Offer proposition shown to the audience."
          },
          "target_action": {
            "type": "string",
            "description": "Primary commitment behavior expected from this segment."
          },
          "expected_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Expected conversion rate for the target action."
          },
          "falsification_condition": {
            "type": "string",
            "description": "Condition under which the hypothesis is considered falsified."
          }
        }
      },
      "success_threshold": {
        "type": "object",
        "required": ["primary_metric", "operator", "value", "practical_minimum"],
        "additionalProperties": false,
        "properties": {
          "primary_metric": {
            "type": "string",
            "description": "Metric used to determine success."
          },
          "operator": {
            "type": "string",
            "enum": [">", ">=", "<", "<=", "between"],
            "description": "Threshold operator for primary metric."
          },
          "value": {
            "type": "number",
            "description": "Threshold value used in success decision."
          },
          "upper_value": {
            "type": "number",
            "description": "Upper bound when operator is between."
          },
          "practical_minimum": {
            "type": "number",
            "description": "Minimum practical effect threshold required for business significance."
          }
        }
      },
      "design": {
        "type": "object",
        "required": [
          "traffic_source",
          "channel",
          "decision_method",
          "min_sample_size",
          "minimum_runtime_days",
          "start_at"
        ],
        "additionalProperties": false,
        "properties": {
          "traffic_source": {
            "type": "string",
            "description": "Source of audience traffic (ads, outbound, existing users, etc.)."
          },
          "channel": {
            "type": "string",
            "description": "Primary channel for offer exposure."
          },
          "decision_method": {
            "type": "string",
            "enum": ["fixed_horizon", "sequential_adjusted"],
            "description": "Inference method declared before launch."
          },
          "alpha": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Type I error budget for the chosen method."
          },
          "target_power": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Target power used in pre-launch planning."
          },
          "min_sample_size": {
            "type": "integer",
            "minimum": 1,
            "description": "Minimum planned sample size before final verdict."
          },
          "minimum_runtime_days": {
            "type": "integer",
            "minimum": 1,
            "description": "Minimum runtime before final verdict is allowed."
          },
          "start_at": {
            "type": "string",
            "description": "ISO-8601 timestamp when the run started."
          },
          "end_at": {
            "type": "string",
            "description": "ISO-8601 timestamp when the run ended."
          },
          "guardrail_metrics": {
            "type": "array",
            "description": "Metrics that can block validation despite primary metric uplift.",
            "items": {
              "type": "object",
              "required": ["metric_name", "max_allowed_degradation"],
              "additionalProperties": false,
              "properties": {
                "metric_name": {
                  "type": "string",
                  "description": "Guardrail metric name."
                },
                "max_allowed_degradation": {
                  "type": "number",
                  "description": "Maximum allowed negative movement before blocking validation."
                }
              }
            }
          }
        }
      },
      "results": {
        "type": "object",
        "required": [
          "total_exposures",
          "unique_visitors",
          "cta_clicks",
          "signups",
          "confirmed_signups",
          "conversion_rate",
          "commitment_rate"
        ],
        "additionalProperties": false,
        "properties": {
          "total_exposures": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of total offer exposures."
          },
          "unique_visitors": {
            "type": "integer",
            "minimum": 0,
            "description": "Unique visitors exposed to the offer."
          },
          "cta_clicks": {
            "type": "integer",
            "minimum": 0,
            "description": "Users who clicked primary CTA."
          },
          "signups": {
            "type": "integer",
            "minimum": 0,
            "description": "Raw signup submissions captured."
          },
          "confirmed_signups": {
            "type": "integer",
            "minimum": 0,
            "description": "Double-opt-in or otherwise confirmed signups."
          },
          "deposits_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of deposit transactions completed."
          },
          "paid_pilot_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of paid pilots accepted."
          },
          "lois_signed_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of LOIs signed."
          },
          "conversion_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Primary conversion rate from exposure to target action."
          },
          "commitment_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Rate of hard commitment actions among exposed users or qualified leads."
          },
          "revenue_evidence": {
            "type": "string",
            "description": "Summary of payment-backed evidence observed in this run."
          }
        }
      },
      "quality_gates": {
        "type": "object",
        "required": [
          "sample_size_status",
          "instrumentation_status",
          "bot_traffic_status",
          "legal_compliance_status"
        ],
        "additionalProperties": false,
        "properties": {
          "sample_size_status": {
            "type": "string",
            "enum": ["pass", "fail"],
            "description": "Whether minimum sample requirements were satisfied."
          },
          "instrumentation_status": {
            "type": "string",
            "enum": ["healthy", "degraded", "unknown"],
            "description": "Telemetry integrity for relevant events and properties."
          },
          "bot_traffic_status": {
            "type": "string",
            "enum": ["pass", "fail", "unknown"],
            "description": "Whether bot/fraud traffic remained below acceptable threshold."
          },
          "legal_compliance_status": {
            "type": "string",
            "enum": ["pass", "fail", "not_applicable"],
            "description": "Compliance status for payment/fulfillment/cancellation obligations in this run."
          },
          "quality_gate_notes": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Operational notes explaining any gate concerns."
          }
        }
      },
      "commitment_evidence": {
        "type": "object",
        "required": ["evidence_tier", "payment_model", "revenue_captured"],
        "additionalProperties": false,
        "properties": {
          "evidence_tier": {
            "type": "string",
            "enum": ["intent_only", "soft_commitment", "hard_commitment"],
            "description": "Strongest evidence tier achieved in this run."
          },
          "payment_model": {
            "type": "string",
            "enum": [
              "none",
              "refundable_reservation",
              "non_refundable_deposit",
              "full_prepay",
              "paid_pilot"
            ],
            "description": "Payment commitment model used, if any."
          },
          "revenue_captured": {
            "type": "number",
            "minimum": 0,
            "description": "Actual revenue captured during the validation window."
          },
          "refund_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Refund ratio for captured commitments in this run."
          },
          "chargeback_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Charge disputes linked to this validation run."
          }
        }
      },
      "anti_patterns_detected": {
        "type": "array",
        "description": "Detected anti-patterns that reduced confidence in the verdict.",
        "items": {
          "type": "string",
          "enum": [
            "vanity_demand",
            "metric_swapping",
            "peek_and_stop",
            "compliance_blind_presale",
            "concierge_heroics",
            "misleading_fake_door"
          ]
        }
      },
      "conclusion": {
        "type": "string",
        "enum": ["validated", "failed", "inconclusive", "invalid_test"],
        "description": "Final decision state after applying thresholds and quality gates."
      },
      "confidence": {
        "type": "string",
        "enum": ["low", "medium", "high"],
        "description": "Confidence in the conclusion after quality and evidence-strength checks."
      },
      "key_learnings": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Most important transferable learnings from this validation run."
      },
      "next_action": {
        "type": "string",
        "enum": [
          "advance_to_mvp_build",
          "run_followup_commitment_test",
          "iterate_messaging",
          "iterate_offer_terms",
          "fix_instrumentation_and_rerun",
          "stop_offer"
        ],
        "description": "Required next action chosen from standardized workflow outcomes."
      },
      "evidence_refs": {
        "type": "array",
        "minItems": 1,
        "items": {"type": "string"},
        "description": "References to dashboards, payment reports, call logs, or source artifacts."
      },
      "updated_at": {
        "type": "string",
        "description": "ISO-8601 timestamp for last update to this artifact."
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Some high-value operator data on offer validation (especially real conversion benchmarks by vertical) is private or paywalled; public benchmarks should be treated as directional priors.
- Several API docs are evergreen and frequently updated without explicit versioned changelog detail, so exact limits can change by plan, region, or account state.
- Public case reports on startup pilot/pre-sale failures are often journalistic summaries rather than full postmortems; use them as risk signals, not precise prevalence estimates.
- B2B paid-pilot conversion rates are context-dependent (deal size, procurement complexity, security/legal requirements) and should not be hard-coded as universal thresholds.
- LOI legal strength varies heavily by jurisdiction and drafting style; schema should capture LOI quality metadata rather than binary "LOI exists" status.
# Research: offer-validation

**Skill path:** `flexus_simple_bots/strategist/skills/offer-validation/`
**Bot:** strategist (researcher | strategist | executor)
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`offer-validation` is the pre-build demand validation skill for testing whether a specific offer gets meaningful behavioral commitment from the target segment. The skill already has the right core stance: behavioral evidence beats stated intent. This research expands that stance with 2024-2026 evidence on segmented benchmarking, experiment reliability, signal quality, and compliance/trust constraints for fake-door and presale workflows.

The main practical gap in the current `SKILL.md` is not method coverage (it already includes fake door, presale, concierge, and pilot proposal), but decision quality: one global threshold, weak confidence framing, and minimal anti-pattern detection can produce false positives or false negatives. The updated guidance below keeps the existing methods, then adds stronger interpretation gates and explicit failure/compliance controls.

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
- Volume: findings section is within 800-4000 words and draft content is longer than findings

Status check:
- Concrete findings include benchmark ranges, confidence rules, and platform constraints
- Tool/API references use documented vendors and known endpoint patterns
- Contradictions are called out in Angle 1, Angle 3, and Synthesis
- Draft content section is intentionally the largest section and paste-ready

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

1. Universal cold-traffic thresholds are weaker than segmented baselines. Recent landing-page reports show wide conversion spread by industry and channel, so a single `>=5%` rule should be fallback only, not a primary go/no-go gate.
2. Channel mix and device mix materially change interpretation. Paid social, paid search, email, desktop, and mobile often show different conversion behavior; pooled rates hide signal quality and can inflate false confidence.
3. Copy complexity affects conversion in measurable ways. Simplified copy often converts better in broad audiences, while some verticals with high-risk buying (for example finance) can reward more professional detail. Message quality should be tested before concluding "offer failed."
4. Practitioners now pair fake-door tests with downstream quality checks (nurture engagement, qualification, payment intent) because top-of-funnel conversion alone is frequently noisy.
5. Presale/deposit validation must account for payment mechanics, especially authorization windows and capture constraints, otherwise "commitment evidence" may be technically invalid.
6. Pilot and concierge validation quality improves when teams define entry/exit criteria before execution and require cost-to-scale checks before calling an offer validated.
7. A practical 2025-2026 shift is from "one KPI test" to "evidence ladder tests": click/signup is weak evidence, financial/legal commitment is strong evidence, and final verdicts combine both.

**Sources:**
- https://unbounce.com/conversion-benchmark-report/
- https://unbounce.com/average-conversion-rates-landing-pages
- https://www.wordstream.com/blog/2024-google-ads-benchmarks
- https://localiq.com/blog/search-advertising-benchmarks/
- https://klaviyo.com/products/email-marketing/benchmarks
- https://docs.stripe.com/payments/place-a-hold-on-a-payment-method
- https://docs.stripe.com/disputes/measuring
- https://docs.aws.amazon.com/prescriptive-guidance/latest/opensearch-service-migration/stage-2-poc.html
- https://docs.aws.amazon.com/redshift/latest/dg/proof-of-concept-playbook.html

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

1. For landing pages and fake doors, Webflow and Unbounce remain common choices. Webflow provides CMS/data APIs and clear per-plan rate limits; Unbounce is conversion-focused with lead/page APIs and generous request limits.
2. Framer Server API is useful for teams that want scripted publish/deploy workflows for experiments; this is valuable when tests are run frequently and need reproducible deploy automation.
3. Stripe Checkout remains a standard choice for willingness-to-pay evidence because it supports hosted checkout, wide payment method coverage, and documentation on rate limits, disputes, and authorization behaviors.
4. Paddle and Lemon Squeezy are strong alternatives when merchant-of-record behavior and international compliance overhead are constraints from day one; both provide documented transaction/checkout APIs and rate-limit details.
5. GA4 Measurement Protocol, PostHog capture endpoints, and Amplitude HTTP V2 are practical event ingestion options for server-side conversion evidence and funnel instrumentation.
6. Statsig exposes experiment-management APIs with documented project-level request limits, making it suitable when the workflow includes repeated controlled tests and formal experiment governance.
7. HubSpot contacts API, Typeform webhooks, and Airtable API are common handoff layers for qualification and sales follow-through, which is critical for B2B pilot validation.
8. Ad-channel APIs (Meta Marketing API, Google Ads API, LinkedIn Marketing APIs) are the practical traffic acquisition control plane for fake-door tests, but quota and versioning constraints differ by platform.
9. De-facto stacks in 2025-2026 commonly combine ad platform + landing page + payment evidence + analytics + CRM rather than using a single all-in-one product.

**Sources:**
- https://developers.webflow.com/data/docs/working-with-the-cms
- https://developers.webflow.com/data/reference/rate-limits
- https://developer.unbounce.com/getting_started/
- https://developer.unbounce.com/api_reference/
- https://www.framer.com/developers/server-api-quick-start
- https://docs.stripe.com/api/checkout/sessions/create?lang=curl
- https://docs.stripe.com/rate-limits
- https://developer.paddle.com/api-reference/transactions/create-transaction
- https://developer.paddle.com/api-reference/about/rate-limiting
- https://docs.lemonsqueezy.com/api/checkouts/create-checkout
- https://developers.google.com/analytics/devguides/collection/protocol/ga4/reference
- https://posthog.com/docs/api/capture
- https://amplitude.com/docs/apis/analytics/http-v2
- https://docs.statsig.com/api-reference/experiments/create-experiment
- https://developers.hubspot.com/docs/api/crm/contacts
- https://www.typeform.com/developers/webhooks/reference/create-or-update-webhook/
- https://support.airtable.com/docs/managing-api-call-limits-in-airtable
- https://developers.facebook.com/docs/marketing-api/reference/ad-account/campaigns/
- https://developers.google.com/google-ads/api/rest/common/search
- https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaigns?view=li-lms-2026-01

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

1. Benchmarks are context-heavy. Landing-page and ad benchmarks vary significantly by industry, audience intent, and funnel stage, so benchmark use must normalize definitions before comparison (`visit->signup` is not comparable to `click->lead->sale` without adjustment).
2. CTR and top-funnel conversion are insufficient as standalone validation evidence. A practical interpretation stack is: top-funnel response + downstream quality + commitment evidence.
3. Confidence interval and power framing are now standard for decision quality in experimentation tooling. If CI crosses zero (or crosses the practical threshold), results should default to inconclusive.
4. Predefined alpha, power, and minimum detectable effect (MDE) prevent post-hoc rationalization and underpowered conclusions. Common defaults are alpha `0.05` and power `0.8`, with MDE tied to business value.
5. Early peeking is a major reliability failure mode. Many practitioners treat first-24h reads as directional diagnostics only, then wait for planned duration and sample size before final verdicts.
6. Low-sample conditions require explicit caution flags. When effective sample is small and uncertainty is high, "no signal" often means "not enough data," not "offer failed."
7. Multiple comparisons and segment slicing increase false discovery risk. Deep segment wins should be treated as exploratory unless replicated.
8. For B2B pilot/proposal flows, interpretation improves when you combine acceptance rates with stakeholder depth (for example number of engaged reviewers, signature progression, and close velocity).

**Sources:**
- https://unbounce.com/conversion-benchmark-report/
- https://unbounce.com/conversion-benchmark-report/methodology/
- https://localiq.com/blog/search-advertising-benchmarks/
- https://contentsquare.com/blog/2025-digital-experience-benchmarks
- https://docs.statsig.com/experiments/statistical-methods/confidence-intervals
- https://docs.statsig.com/experiments/power-analysis
- https://docs.statsig.com/experiments-plus/read-results
- https://www.statsig.com/perspectives/ab-test-sample-size
- https://www.statsig.com/perspectives/mde-calculate-use-ab-tests
- https://support.optimizely.com/hc/en-us/articles/4410289598989-Why-Stats-Engine-controls-for-false-discovery-instead-of-false-positives
- https://support.optimizely.com/hc/en-us/articles/4410289544589-How-and-why-statistical-significance-changes-over-time-in-Optimizely-Experimentation
- https://www.proposify.com/state-of-proposals-2024
- https://www.proposify.com/hubfs/State%20of%20Proposals%202025/The%20State%20of%20Proposals%202025.pdf

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

1. Vanity-click validation: teams mark success on clicks or signups without checking downstream commitment quality.
2. Sample ratio mismatch (SRM) blindness: allocation drift or instrumentation defects produce biased experiment results that are still interpreted as valid.
3. Underpowered peeking: tests are stopped early or read too often, then interpreted as conclusive despite unstable uncertainty.
4. Audience mismatch: the experiment reaches the wrong cohort, producing false positive demand from non-buyers or non-ICP users.
5. Opaque fake doors: users encounter a dead end after clicking a fake feature with no disclosure, causing trust erosion and support blowback.
6. Asymmetric consent and manipulative design patterns can introduce compliance risk and invalidate "consent-like" signals.
7. Fake social proof or synthetic urgency in validation pages can violate deceptive-practice rules and poison experiment quality.
8. Presale promise debt: taking payment without delivery-readiness controls, delay consent, and refund flow creates dispute/legal risk.
9. Concierge-to-product cliff: manual delivery succeeds because of human over-service, then collapses during automation because the tested value was not operationally reproducible.

**Sources:**
- https://www.statsig.com/blog/top-8-common-experimentation-mistakes-how-to-fix
- https://docs.statsig.com/guides/srm
- https://amplitude.com/docs/feature-experiment/troubleshooting/sample-ratio-mismatch
- https://amplitude.com/explore/experiment/fake-door-testing
- https://www.ftc.gov/news-events/news/press-releases/2024/07/ftc-icpen-gpen-announce-results-review-use-dark-patterns-affecting-subscription-services-privacy
- https://www.icpen.org/sites/default/files/2024-07/Public%20Report%20ICPEN%20Dark%20Patterns%20Sweep.pdf
- https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials
- https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-465/section-465.2
- https://www.ftc.gov/business-guidance/resources/business-guide-ftcs-mail-internet-or-telephone-order-merchandise-rule (evergreen)
- https://blog.logrocket.com/product-management/concierge-wizard-of-oz-mvp

---

### Angle 5+: Regulatory, Consent, and Trust Constraints
> Offer-validation methods are technically simple, but legal/compliance and trust constraints can invalidate both process and outcomes if ignored.

**Findings:**

1. Regulators are converging on anti-manipulation and meaningful user choice, but strictness differs by jurisdiction and context.
2. EU EDPB 2024 guidance on "consent or pay" for large platforms is materially stricter than UK ICO 2025 guidance, which allows compliant implementations when conditions are met.
3. California CPPA guidance emphasizes that dark-pattern analysis focuses on effect on user choice, not intent of the designer.
4. Fake-door experiments should include immediate disclosure and easy exit paths; "realistic test" does not justify misleading flows.
5. For presales, delay-consent and refund controls are not optional operational niceties; they are key legal/trust safeguards.
6. Compliance differences across regions mean global one-size-fits-all validation playbooks are risky; regional deployment constraints should be explicitly tracked.

**Sources:**
- https://www.edpb.europa.eu/our-work-tools/our-documents/opinion-board-art-64/opinion-082024-valid-consent-context-consent-or_en
- https://www.edpb.europa.eu/system/files/2024-04/edpb_opinion_202408_consentorpay_en.pdf
- https://www.edpb.europa.eu/news/news/2024/edpb-consent-or-pay-models-should-offer-real-choice_en
- https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/online-tracking/consent-or-pay/about-this-guidance/
- https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/online-tracking/consent-or-pay/privacy-by-design
- https://cppa.ca.gov/pdf/enfadvisory202402.pdf
- https://cppa.ca.gov/regulations/pdf/cppa_regs.pdf

---

## Synthesis

The strongest cross-angle pattern is that `offer-validation` should shift from a single-threshold mindset to an evidence-ladder mindset. In 2024-2026 data, conversion outcomes vary too much by channel, segment, and device for a global benchmark to be reliable. A universal `>=5%` can still be useful as a temporary floor, but only until segment-relevant baselines are available.

A second pattern is that practitioners increasingly separate "attention signal" from "commitment signal." CTR and signup are useful diagnostics, but they are not durable demand evidence by themselves. Payment/deposit behavior, signed commitments, and qualified stakeholder progression produce materially stronger validation evidence, especially in B2B pilots and presale contexts.

A third pattern is methodological maturity in interpretation. Experiment platforms and modern guidance emphasize predefining alpha/power/MDE, watching confidence intervals, and explicitly handling SRM, multiplicity, and underpowered conditions. Without these controls, teams overfit to noise and mislabel outcomes.

Finally, trust/compliance constraints are now operationally relevant to fake-door and presale tests. There is a real tension between realistic demand testing and non-manipulative user experience. Source disagreement (for example EU vs UK posture on consent-or-pay patterns) means the skill should codify conservative defaults and jurisdiction-aware risk flags rather than claiming universal legal rules.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.

- [ ] Replace the universal smoke-test threshold with a segmented benchmark policy (channel x industry x device), keeping `>=5%` only as temporary fallback.
- [ ] Add an explicit evidence ladder and require at least one hard commitment signal before verdict `validated`.
- [ ] Add experiment reliability gates: alpha/power/MDE declaration, minimum cycle duration, and SRM checks.
- [ ] Add a formal interpretation rubric for `validated`, `inconclusive`, and `failed` to reduce subjective verdicts.
- [ ] Expand anti-pattern coverage with detection signals and mitigations (vanity clicks, peeking, SRM, audience mismatch, promise debt, concierge cliff).
- [ ] Add compliance/trust guardrails for fake-door and presale tests (transparent disclosure, easy opt-out, no fake social proof, delay-consent/refund controls).
- [ ] Expand `Available Tools` instructions with concrete operational flow (policy activation -> run experiment -> record artifact).
- [ ] Replace the artifact schema with a richer structure capturing benchmark basis, confidence, funnel quality, and hard-signal evidence.

---

## Draft Content for SKILL.md

> This is the most important section. For every recommendation above, write the actual text that should go into SKILL.md.

### Draft: Validation standard and evidence ladder

---
### Validation standard

You are not validating opinions. You are validating behavior under real trade-offs.

Treat offer validation as an evidence ladder:

1. **Attention evidence (weak):** clicks, page engagement, email signup.
2. **Intent evidence (moderate):** qualified follow-up actions (demo booked, problem interview accepted, detailed response with buying context).
3. **Commitment evidence (strong):** payment method saved, deposit paid, signed LOI, signed/paid pilot.

A result is **never** `validated` using only attention evidence. You must have at least one strong commitment signal, or a multi-step intent pattern that is historically equivalent for that segment and offer type.

Use this hard rule:
- If you only have top-of-funnel response, conclusion is `inconclusive` even when conversion looks high.
- If commitment evidence exists but audience fit is weak or quality metrics collapse downstream, conclusion is `inconclusive` or `failed` depending on severity.
- If commitment evidence exists and quality metrics remain healthy, you may conclude `validated`.
---

### Draft: Method selection and segmented threshold policy

---
### Validation method selection

Choose the method by uncertainty and commitment needed:

1. **`fake_door`** for message-demand screening before build.
2. **`presale`** for willingness-to-pay proof before full product readiness.
3. **`concierge` / `manual_delivery`** for job-to-be-done realism and fulfillment learning.
4. **`pilot_proposal`** for B2B commitment and stakeholder depth.

### Threshold policy (critical)

Do not use one universal conversion target across all experiments. Instead, set thresholds in this order:

1. **Segment baseline first:** channel + industry + device comparable benchmark.
2. **Historical baseline second:** your prior experiments with the same audience and traffic quality.
3. **Absolute fallback last:** if no reliable baseline exists, use `>=5%` visitor-to-signup only as temporary fallback for cold-traffic fake-door tests.

You must document which basis you used. A threshold without basis is invalid.

### Channel and device normalization

Before verdict:
- Split conversion by acquisition channel (`paid_search`, `paid_social`, `email`, `referral`, etc.).
- Split conversion by device (`mobile`, `desktop`).
- Explain major deltas before concluding.

Do not pool channels and devices into one number and call that validation.

### Suggested method-specific success logic

- **Fake door:** requires segment-normalized conversion plus post-signup quality signal (for example follow-up engagement).
- **Presale:** requires payment/deposit evidence and operational refund/delay controls.
- **Concierge/manual:** requires repeatable value delivery and preliminary unit-economics realism.
- **Pilot proposal:** requires qualified stakeholder engagement and commitment progression, not just proposal send count.
---

### Draft: Experiment design and reliability gates

---
### Experiment design (required fields)

Before launching any validation run, define:

- **Hypothesis** in this format:  
  `If [target segment] sees [offer + message], at least [threshold] will take [specific action] within [time window].`
- **Primary metric** (single go/no-go metric).
- **Guardrail metrics** (quality checks that can override apparent success).
- **Success threshold basis** (segment benchmark, historical baseline, or temporary fallback).
- **Duration plan** (minimum one full business cycle; never decide from same-day read).
- **Reliability plan** (`alpha`, `power`, `MDE`, planned sample).

### Statistical reliability gates

Use these default settings unless justified otherwise:
- `alpha = 0.05`
- `power = 0.8`
- `MDE` must reflect practical business value, not vanity uplift

If your confidence interval crosses zero or your practical threshold, mark the result `inconclusive`.

Do not ship decisions from underpowered tests. If sample is too small to detect your chosen MDE, report the experiment as underpowered and request either longer runtime or stronger-signal method (for example presale instead of signup-only).

### Peeking and stopping rules

You may monitor health metrics during execution, but you must not finalize verdicts before:

1. Planned minimum runtime is complete.
2. Planned minimum sample is reached or a pre-registered stop condition triggers.
3. SRM checks pass for assigned vs observed allocation.

If SRM fails, invalidate the run and relaunch after instrumentation fix.
---

### Draft: Data interpretation rubric and contradiction handling

---
### Interpretation rubric

Use this rubric exactly:

#### `validated`
- Primary metric clears threshold with acceptable uncertainty.
- At least one hard commitment signal exists (deposit/payment/signed commitment).
- Guardrail metrics do not show severe downstream quality loss.

#### `inconclusive`
- Directional lift exists but uncertainty remains high.
- Evidence is mostly attention/intent with weak commitment.
- Sample/runtime/reliability constraints prevent strong conclusion.

#### `failed`
- Primary metric materially misses threshold with confidence.
- Guardrails indicate quality collapse.
- Commitment evidence is absent or clearly weak after adequate exposure.

### Contradiction handling

When benchmarks disagree across sources, do not pick one silently. Do this instead:

1. Normalize metric definitions (for example `visit->signup` vs `click->lead`).
2. Compare only within same funnel stage.
3. Segment by intent and channel.
4. Record why a source was selected as primary benchmark.

If contradictions remain unresolved, keep verdict `inconclusive` and capture uncertainty explicitly in artifact fields.
---

### Draft: Available tools section (operational workflow)

---
## Available Tools

Activate supporting strategy documents before experiment design:

```python
flexus_policy_document(op="activate", args={"p": "/strategy/offer-design"})
flexus_policy_document(op="activate", args={"p": "/strategy/messaging"})
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})
```

After execution, persist full evidence using:

```python
write_artifact(
  artifact_type="offer_validation_results",
  path="/strategy/offer-validation-{date}",
  data={...}
)
```

### Optional external stack references (for analyst verification and integrations)

Use only when your execution environment supports these systems; otherwise skip.

- Stripe Checkout session creation (willingness-to-pay evidence): `POST https://api.stripe.com/v1/checkout/sessions`
- GA4 Measurement Protocol ingestion (server-side event confirmation): `POST https://www.google-analytics.com/mp/collect?...`
- HubSpot contact upsert/create handoff: `POST https://api.hubapi.com/crm/v3/objects/contacts`
- PostHog capture ingestion: `POST https://us.i.posthog.com/i/v0/e/`

Do not invent endpoints or methods. If a referenced API method cannot be verified in official docs at run time, remove it from the plan and mark the gap.
---

### Draft: Anti-pattern warning blocks

---
### Anti-pattern: Vanity Click Validation

**What it looks like:** You call a fake-door test successful based on high CTR or signup count alone.  
**Detection signal:** Strong top-funnel response but weak downstream engagement, qualification, or commitment evidence.  
**Consequence if missed:** You build offers that attract curiosity rather than buyers.  
**Mitigation steps:** Require at least one downstream quality metric and one hard-signal checkpoint before `validated`.

### Anti-pattern: Underpowered Peeking

**What it looks like:** You repeatedly inspect results and finalize early based on unstable movement.  
**Detection signal:** Verdict changes day to day; CI remains wide; sample plan not reached.  
**Consequence if missed:** False positives/negatives drive roadmap mistakes.  
**Mitigation steps:** Pre-register stopping rules, enforce minimum runtime/sample, and default to `inconclusive` when reliability gates fail.

### Anti-pattern: Sample Ratio Mismatch (SRM) Blindness

**What it looks like:** Allocation intended as 50/50 appears as materially skewed exposure and is still interpreted.  
**Detection signal:** Assignment and observed exposure ratios diverge beyond expected random variation.  
**Consequence if missed:** Biased lift estimates and invalid verdicts.  
**Mitigation steps:** Stop interpretation, fix assignment/logging, rerun the test.

### Anti-pattern: Audience Mismatch

**What it looks like:** Offer is tested on broad traffic that does not match ICP purchase reality.  
**Detection signal:** High response from low-fit users, poor conversion to qualified next step.  
**Consequence if missed:** False demand signal and poor post-build conversion.  
**Mitigation steps:** Segment traffic up front, score audience fit, and report segment-level outcomes.

### Anti-pattern: Opaque Fake Door

**What it looks like:** User clicks an unavailable feature and hits a dead end with no explanation.  
**Detection signal:** confusion events, repeat clicks, support complaints.  
**Consequence if missed:** Trust damage and elevated deceptive-design risk.  
**Mitigation steps:** immediate plain-language disclosure, clear next step (waitlist or alternative), and easy exit path.

### Anti-pattern: Presale Promise Debt

**What it looks like:** Payment is taken before delivery readiness or without delay/refund controls.  
**Detection signal:** delivery slips, refund backlog, dispute increase.  
**Consequence if missed:** legal exposure, payment disputes, and brand damage.  
**Mitigation steps:** add delivery-window assumptions, consented delay workflow, and automatic refund process before taking presale funds.

### Anti-pattern: Concierge-to-Product Cliff

**What it looks like:** Concierge pilot succeeds because humans overcompensate for missing product capability.  
**Detection signal:** high manual effort per account and weak automation parity.  
**Consequence if missed:** false PMF and churn when automation is introduced.  
**Mitigation steps:** test progressive automation, measure value retention as manual effort decreases, and re-scope offer if parity fails.
---

### Draft: Compliance and trust safeguards

---
### Compliance and trust safeguards

You must run fake-door and presale validation with transparent user treatment:

1. Disclose unavailable features immediately after click using plain language.
2. Keep refusal/exit paths as easy as acceptance paths.
3. Do not use fabricated social proof, fabricated urgency, or unsubstantiated claim language.
4. For presale, set and communicate delivery assumptions, delay-consent workflow, and refund policy before payment collection.
5. Add jurisdiction risk notes when running across regions with different regulatory posture.

Regulatory sources disagree in strictness in some areas (for example EU vs UK interpretation of consent-or-pay patterns). When strictness is uncertain, apply conservative defaults and record the unresolved jurisdiction question in `risk_flags`.
---

### Draft: Schema additions

> Full JSON Schema fragment for `offer_validation_results` with stronger reliability and interpretation metadata.

```json
{
  "offer_validation_results": {
    "type": "object",
    "required": [
      "experiment_id",
      "experiment_date",
      "segment_id",
      "method",
      "hypothesis",
      "primary_metric",
      "success_threshold",
      "traffic_sources",
      "duration_days_planned",
      "duration_days_actual",
      "results",
      "confidence",
      "commitment_evidence",
      "conclusion",
      "conclusion_reason",
      "next_action"
    ],
    "additionalProperties": false,
    "properties": {
      "experiment_id": {
        "type": "string",
        "description": "Unique experiment identifier for audit and cross-run comparison."
      },
      "experiment_date": {
        "type": "string",
        "format": "date",
        "description": "ISO date (YYYY-MM-DD) representing experiment start date."
      },
      "segment_id": {
        "type": "string",
        "description": "Target segment identifier used to evaluate ICP fit and benchmark relevance."
      },
      "method": {
        "type": "string",
        "enum": [
          "fake_door",
          "presale",
          "concierge",
          "pilot_proposal",
          "manual_delivery"
        ],
        "description": "Validation method used in this experiment."
      },
      "hypothesis": {
        "type": "string",
        "description": "Testable if-then statement including segment, offer, action, and time window."
      },
      "primary_metric": {
        "type": "string",
        "enum": [
          "visitor_to_signup_rate",
          "deposit_conversion_rate",
          "payment_conversion_rate",
          "proposal_to_paid_pilot_rate",
          "manual_delivery_paid_conversion_rate"
        ],
        "description": "Single decision metric used for go/no-go judgment."
      },
      "success_threshold": {
        "type": "object",
        "required": [
          "target_value",
          "comparison_basis",
          "minimum_practical_lift"
        ],
        "additionalProperties": false,
        "properties": {
          "target_value": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Primary threshold value as a normalized rate from 0 to 1."
          },
          "comparison_basis": {
            "type": "string",
            "enum": [
              "segment_benchmark",
              "historical_baseline",
              "absolute_fallback"
            ],
            "description": "Basis used to set threshold; absolute_fallback is temporary when better baselines are unavailable."
          },
          "minimum_practical_lift": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Smallest absolute lift considered meaningful for business decisions."
          }
        },
        "description": "Threshold definition including value and rationale basis."
      },
      "traffic_sources": {
        "type": "array",
        "minItems": 1,
        "items": {
          "type": "string",
          "enum": [
            "paid_search",
            "paid_social",
            "email",
            "referral",
            "community",
            "direct",
            "outbound"
          ]
        },
        "description": "Acquisition sources included in this experiment."
      },
      "duration_days_planned": {
        "type": "integer",
        "minimum": 1,
        "description": "Planned experiment duration in whole days."
      },
      "duration_days_actual": {
        "type": "integer",
        "minimum": 1,
        "description": "Actual runtime in whole days."
      },
      "results": {
        "type": "object",
        "required": [
          "total_exposures",
          "conversions",
          "conversion_rate",
          "channel_breakdown",
          "device_breakdown",
          "funnel",
          "revenue_evidence"
        ],
        "additionalProperties": false,
        "properties": {
          "total_exposures": {
            "type": "integer",
            "minimum": 0,
            "description": "Count of qualified exposures used as denominator for primary metric."
          },
          "conversions": {
            "type": "integer",
            "minimum": 0,
            "description": "Count of primary-metric conversions."
          },
          "conversion_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Primary conversion metric as conversions / total_exposures."
          },
          "channel_breakdown": {
            "type": "array",
            "items": {
              "type": "object",
              "required": [
                "channel",
                "exposures",
                "conversions",
                "conversion_rate"
              ],
              "additionalProperties": false,
              "properties": {
                "channel": {
                  "type": "string",
                  "description": "Traffic channel label used for segmented interpretation."
                },
                "exposures": {
                  "type": "integer",
                  "minimum": 0,
                  "description": "Exposures for this channel."
                },
                "conversions": {
                  "type": "integer",
                  "minimum": 0,
                  "description": "Conversions for this channel."
                },
                "conversion_rate": {
                  "type": "number",
                  "minimum": 0,
                  "maximum": 1,
                  "description": "Channel conversion rate."
                }
              }
            },
            "description": "Per-channel breakdown required for source-normalized interpretation."
          },
          "device_breakdown": {
            "type": "array",
            "items": {
              "type": "object",
              "required": [
                "device",
                "exposures",
                "conversions",
                "conversion_rate"
              ],
              "additionalProperties": false,
              "properties": {
                "device": {
                  "type": "string",
                  "enum": [
                    "mobile",
                    "desktop",
                    "tablet",
                    "other"
                  ],
                  "description": "Device class used in conversion split."
                },
                "exposures": {
                  "type": "integer",
                  "minimum": 0,
                  "description": "Exposures for this device class."
                },
                "conversions": {
                  "type": "integer",
                  "minimum": 0,
                  "description": "Conversions for this device class."
                },
                "conversion_rate": {
                  "type": "number",
                  "minimum": 0,
                  "maximum": 1,
                  "description": "Device conversion rate."
                }
              }
            },
            "description": "Per-device breakdown to detect hidden channel-device artifacts."
          },
          "funnel": {
            "type": "object",
            "required": [
              "cta_click_rate",
              "signup_rate",
              "qualified_next_step_rate",
              "commitment_rate"
            ],
            "additionalProperties": false,
            "properties": {
              "cta_click_rate": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Fraction of exposures that clicked CTA."
              },
              "signup_rate": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Fraction of exposures that completed signup form."
              },
              "qualified_next_step_rate": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Fraction of signups that complete a qualified next action (for example demo booked or detailed intent response)."
              },
              "commitment_rate": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Fraction of exposures that reach hard commitment evidence."
              }
            },
            "description": "Multi-step funnel needed to distinguish curiosity from commitment."
          },
          "revenue_evidence": {
            "type": "string",
            "description": "Narrative summary of direct monetary evidence (deposit, payment, paid pilot)."
          }
        },
        "description": "Observed performance metrics and segmented breakdowns."
      },
      "confidence": {
        "type": "object",
        "required": [
          "alpha",
          "power",
          "mde",
          "ci_lower",
          "ci_upper",
          "sample_size_planned",
          "sample_size_actual",
          "srm_check"
        ],
        "additionalProperties": false,
        "properties": {
          "alpha": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Type-I error threshold used for interpretation."
          },
          "power": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Statistical power target for detecting chosen MDE."
          },
          "mde": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Minimum detectable effect as absolute rate lift."
          },
          "ci_lower": {
            "type": "number",
            "description": "Lower bound of confidence interval for effect estimate."
          },
          "ci_upper": {
            "type": "number",
            "description": "Upper bound of confidence interval for effect estimate."
          },
          "sample_size_planned": {
            "type": "integer",
            "minimum": 0,
            "description": "Planned sample size used in reliability planning."
          },
          "sample_size_actual": {
            "type": "integer",
            "minimum": 0,
            "description": "Observed sample size at decision time."
          },
          "srm_check": {
            "type": "string",
            "enum": [
              "pass",
              "fail",
              "not_applicable"
            ],
            "description": "Sample ratio mismatch status for allocation validity."
          }
        },
        "description": "Reliability metadata required for statistically defensible conclusions."
      },
      "commitment_evidence": {
        "type": "object",
        "required": [
          "evidence_type",
          "count",
          "amount_usd"
        ],
        "additionalProperties": false,
        "properties": {
          "evidence_type": {
            "type": "string",
            "enum": [
              "none",
              "waitlist_only",
              "payment_method_saved",
              "deposit_paid",
              "signed_loi",
              "signed_pilot",
              "paid_pilot"
            ],
            "description": "Strongest evidence class observed in this run."
          },
          "count": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of commitment events observed."
          },
          "amount_usd": {
            "type": "number",
            "minimum": 0,
            "description": "Total commitment amount in USD-equivalent for financial evidence."
          }
        },
        "description": "Hard-signal evidence used by evidence-ladder verdict logic."
      },
      "source_benchmarks": {
        "type": "array",
        "items": {
          "type": "object",
          "required": [
            "source_name",
            "source_url",
            "published_year",
            "metric_name",
            "metric_value",
            "segment_notes"
          ],
          "additionalProperties": false,
          "properties": {
            "source_name": {
              "type": "string",
              "description": "Human-readable source label (for example Unbounce Conversion Benchmark Report)."
            },
            "source_url": {
              "type": "string",
              "description": "Direct URL used for threshold grounding."
            },
            "published_year": {
              "type": "string",
              "description": "Publication year or 'evergreen' when older but still applicable."
            },
            "metric_name": {
              "type": "string",
              "description": "Benchmark metric name being used for comparison."
            },
            "metric_value": {
              "type": "string",
              "description": "Benchmark value in source-native format (number, range, or percentile)."
            },
            "segment_notes": {
              "type": "string",
              "description": "Context explaining why this benchmark is comparable to the tested audience."
            }
          }
        },
        "description": "External benchmark references used to justify threshold selection."
      },
      "risk_flags": {
        "type": "array",
        "items": {
          "type": "string",
          "enum": [
            "srm_detected",
            "underpowered",
            "high_dispute_risk",
            "audience_mismatch",
            "compliance_review_required",
            "contradictory_benchmarks"
          ]
        },
        "description": "Known reliability, operational, or compliance risks requiring explicit acknowledgment."
      },
      "conclusion": {
        "type": "string",
        "enum": [
          "validated",
          "failed",
          "inconclusive"
        ],
        "description": "Final decision state derived from threshold, confidence, and commitment evidence."
      },
      "conclusion_reason": {
        "type": "string",
        "description": "Short explanation linking verdict to evidence and reliability checks."
      },
      "key_learnings": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Top insights that should change offer, segment, or messaging strategy."
      },
      "next_action": {
        "type": "string",
        "description": "Concrete next step (iterate message, rerun with better segment, move to pilot, pause, or stop)."
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Public 2024-2026 benchmark data for high-ticket B2B pilot conversion is still sparse relative to SMB/ecommerce datasets.
- Cross-source metric definitions differ (landing-page conversion, ad conversion, proposal close), so direct numeric comparisons remain imperfect even with normalization.
- Jurisdictional compliance posture is not fully harmonized (EU, UK, California, US federal), so global policy should retain a conservative mode and explicit legal-review flags.
- Tool documentation clarity varies by vendor (especially detailed rate-limit policy and dynamic docs), so API-level operational plans still require pre-run verification.
