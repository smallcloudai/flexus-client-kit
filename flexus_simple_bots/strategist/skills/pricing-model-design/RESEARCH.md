# Research: pricing-model-design

**Skill path:** `strategist/skills/pricing-model-design/`
**Bot:** strategist (researcher | strategist | executor)
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`pricing-model-design` chooses the charge architecture (flat subscription, per-seat, consumption/metered, outcome-based, or hybrid) that best matches customer value realization and business constraints. This skill is not about tier packaging details or setting final price points; it is about selecting the model logic that determines how revenue scales.

2024-2026 evidence shows this decision has become materially harder for AI and software products: buyer demand is moving toward value-aligned pricing, while CFO/procurement pressure for predictability remains high. At the same time, token and inference costs can vary significantly by model tier, so a model that looks commercially attractive can become margin-destructive without explicit guardrails. The upgraded skill should therefore use a staged decision process, explicit evidence quality controls, and anti-pattern detection before finalizing a pricing model recommendation.

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

- No generic filler ("it is important to...", "best practices suggest...") without concrete backing: **passed**
- No invented tool names, method IDs, or API endpoints - only verified real ones: **passed**
- Contradictions between sources are explicitly noted, not silently resolved: **passed**
- Volume: findings section should be 800-4000 words (too short = shallow, too long = unsynthesized): **passed**

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

The most consistent 2024-2026 pattern is a shift from "pick a model by analogy to competitors" toward a stage-gated design workflow. Leading pricing research for AI-era software emphasizes sequencing: first identify value metric candidates, then test measurability and customer auditability, then test cost variability and margin risk, and only then choose model type (seat, usage, outcome, hybrid). This sequence reduces premature model locking and avoids expensive rework later in quote-to-cash and billing operations [M1][M2][M3].

Outcome-based pricing is increasingly discussed as the "north star" for value alignment, but practical readiness remains the blocking factor in most organizations. Enterprise teams report recurring barriers: ambiguous outcome definitions, weak attribution boundaries, and discomfort with invoice unpredictability. Methodologically, this means outcome pricing should be treated as a maturity state reached after instrumentation, baseline definitions, and governance are strong, not as a default first move [M1][M4].

Hybrid model design (typically base subscription plus metered expansion) appears as the current operational center of gravity in software monetization. Market datasets differ in exact percentages, but they converge on a direction: pure seat and flat-only models are under pressure in AI-influenced categories, while hybrid arrangements are increasing because they balance buyer predictability with supplier cost exposure management [M3][M5][M6].

Value metric quality is still the decisive primitive. Across sources, robust value metrics share three requirements: they correlate with realized customer value, can be measured/verifiable by both sides, and are predictable enough for customer budgeting. Metrics that fail one of these criteria usually generate disputes, discounting pressure, or gaming behavior. This reinforces the need for an explicit value-metric rubric in the skill output [M1][M2][M4].

Guardrails are now treated as part of model architecture, not post-launch tuning. Sources repeatedly recommend embedding spend controls (caps, alerts, soft/hard limits, commitments, prepay options, fair-use boundaries) at design time when recommending usage or outcome components. The method implication is clear: a model recommendation without a guardrail plan is incomplete [M2][M3][M5].

Organizations adopting usage components at scale report that implementation maturity is as important as model choice. High adoption rates can coexist with execution failure when real-time metering, invoice traceability, and exception handling are weak. Therefore, pricing-model methodology should include an operational readiness gate before selecting complex models [M5][M6].

Recent practice also treats pricing model as a recurring operating decision instead of a one-time strategic artifact. As buyer behavior and AI unit economics change quickly, review cadence tied to renewals, expansion behavior, and margin telemetry is becoming standard. The skill should encode this as a mandatory review plan rather than optional follow-up [M5][M6].

**Sources:**
- [M1] BCG, "Rethinking B2B Software Pricing in the Era of AI" (2025): https://www.bcg.com/publications/2025/rethinking-b2b-software-pricing-in-the-era-of-ai - 2024-2026
- [M2] Simon-Kucher, "Best practices for Generative AI packaging and pricing" (2024): https://www.simon-kucher.com/en/insights/best-practices-generative-ai-packaging-and-pricing - 2024-2026
- [M3] Simon-Kucher, "The key to AI monetization for tech companies" (2025): https://www.simon-kucher.com/en/insights/key-ai-monetization-tech-companies - 2024-2026
- [M4] Andreessen Horowitz, "How 100 Enterprise CIOs Are Building and Buying Gen AI in 2025" (2025): https://a16z.com/ai-enterprise-2025/ - 2024-2026
- [M5] Metronome, "State of Usage-Based Pricing 2025 Report" (2025): https://metronome.com/state-of-usage-based-pricing-2025 - 2024-2026
- [M6] High Alpha + OpenView, "2024 SaaS Benchmarks Report" (2024): https://highalpha.com/saas-benchmarks/2024 - 2024-2026
- [M7] L.E.K. Consulting, "How Consumption-Based Pricing Reshapes Growth, Profitability and Value" (2025): https://www.lek.com/insights/tmt/us/ei/how-consumption-based-pricing-reshapes-growth-profitability-and-value - 2024-2026

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

The tooling landscape for pricing-model design breaks into four practical layers: billing execution (Stripe, Paddle), experimentation and packaging controls (LaunchDarkly, Amplitude Experiment), telemetry and event normalization (Amplitude Analytics, Segment), and interoperability standards (OpenTelemetry OTLP, OpenFeature). Teams that collapse these layers into one vendor decision often miss operational constraints that later invalidate the intended pricing model [T1][T2][T3][T4][T5][T6][T7].

Stripe provides a concrete path for usage-based monetization via meter events and entitlement mapping. Relevant documented methods include usage ingestion at `POST /v1/billing/meter_events`, entitlement feature configuration (`POST /v1/entitlements/features`, product-feature links), and active entitlement reads per customer. Stripe also documents rate-limit behavior and billing-product commercial terms, making it viable for evidence-based feasibility checks when recommending usage/hybrid models [T1][T2][T3][T4].

Paddle exposes explicit APIs for subscription-side charging workflows with documented throttling details and immediate-charge constraints. The method `POST /subscriptions/{subscription_id}/charge` is directly relevant for hybrid and add-on strategies where recurring plans need non-recurring adjustments. Because limits are documented at multiple levels (IP, operation, subscription action), recommendation logic should include rate-limit assumptions explicitly instead of relying on a single global throughput estimate [T5][T6][T7].

LaunchDarkly is useful in pricing architecture where packaging/entitlement exposure must be tested safely. Documented REST patterns (`POST /api/v2/flags/{projectKey}`, `PATCH /api/v2/flags/{projectKey}/{key}`) support controlled rollouts and segmentation. However, numeric public API limits are not always fixed in docs; robust usage depends on reading response headers and handling `429` with `Retry-After` rather than hardcoded thresholds [T8][T9][T10].

Amplitude spans both event ingestion and experiment management, which is useful for connecting pricing hypotheses to downstream behavioral evidence. Key documented APIs include `POST https://api2.amplitude.com/2/httpapi` for analytics ingestion and `/api/1/experiments` for experiment management. Constraints around request size, event volume, and API quotas are explicitly documented and should be carried into model feasibility scoring [T11][T12][T13].

Segment remains a de-facto event gateway for teams that need consistent identity/event schemas across tools. Documented endpoints (`POST /v1/track`, `/v1/identify`, `/v1/batch`) and published size/rate guidance make Segment useful when pricing-model recommendations require a stable telemetry foundation across product, analytics, and warehouse destinations [T14][T15][T16].

At the standards layer, OTLP and OpenFeature represent interoperability guardrails. OTLP stabilizes telemetry transport conventions, while OpenFeature defines vendor-neutral feature-flag abstractions. This matters because monetization programs commonly outlive single-vendor contracts; portability reduces migration risk and avoids embedding pricing logic too deeply in one provider surface [T17][T18].

**Sources:**
- [T1] Stripe Docs, "Record usage for billing with the API": https://docs.stripe.com/billing/subscriptions/usage-based/recording-usage-api - Evergreen
- [T2] Stripe Docs, "Entitlements": https://docs.stripe.com/billing/entitlements - Evergreen
- [T3] Stripe Docs, "Rate limits": https://docs.stripe.com/rate-limits - Evergreen
- [T4] Stripe, "Billing pricing": https://stripe.com/billing/pricing - Evergreen
- [T5] Paddle Developer, "Rate limiting": https://developer.paddle.com/api-reference/about/rate-limiting - Evergreen
- [T6] Paddle Developer, "Create a one-time charge for a subscription": https://developer.paddle.com/api-reference/subscriptions/create-one-time-charge - Evergreen
- [T7] Paddle Developer Changelog, "Subscription immediate-charge limits" (2024): https://developer.paddle.com/changelog/2024/subscription-immediate-charge-limits - 2024-2026
- [T8] LaunchDarkly API docs: https://apidocs.launchdarkly.com/ - Evergreen
- [T9] LaunchDarkly Guide, "Using the REST API": https://docs.launchdarkly.com/guides/api/rest-api/ - Evergreen
- [T10] LaunchDarkly Support, "429 Too Many Requests": https://support.launchdarkly.com/hc/en-us/articles/22328238491803-Error-429-Too-Many-Requests-API-Rate-Limit - Evergreen
- [T11] Amplitude Docs, "HTTP V2 API": https://amplitude.com/docs/apis/analytics/http-v2 - 2024-2026
- [T12] Amplitude Docs, "Experiment Management API": https://amplitude.com/docs/apis/experiment/experiment-management-api - 2024-2026
- [T13] Amplitude Plus terms (2025): https://amplitude.com/plus-plan-terms/archive/2025-02 - 2024-2026
- [T14] Segment Docs, "HTTP API source": https://segment.com/docs/connections/sources/catalog/libraries/server/http-api/ - Evergreen
- [T15] Segment Docs, "Product limits / rate limits" (updated 2024): https://segment.com/docs/connections/rate-limits/ - 2024-2026
- [T16] Twilio Segment, "MTUs and throughput billing": https://www.twilio.com/docs/segment/guides/usage-and-billing/mtus-and-throughput - Evergreen
- [T17] OpenTelemetry OTLP specification: https://opentelemetry.io/docs/specs/otlp/ - Evergreen
- [T18] OpenFeature specification: https://openfeature.dev/specification - Evergreen

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

WTP survey outputs should be treated as directional unless behaviorally calibrated. A foundational meta-analysis reports systematic hypothetical bias (stated WTP above realized WTP in many settings), so survey-only evidence should not directly determine final model structure without pilot or behavioral validation. This is especially relevant when selecting between usage and outcome components that can create invoice volatility [D1 - EVERGREEN].

Conjoint quality improves when incentive alignment is used in study design. A 2025 meta-analysis reports stronger predictive validity under incentive-aligned designs, which supports a practical interpretation rule: high-stakes model changes should require stronger evidence quality than exploratory packaging decisions [D2].

Retention interpretation must be segmented by business context rather than treated as one universal benchmark. Recent private B2B SaaS benchmarks show meaningful variation by ACV bands, while other benchmark providers using different segmentation logic report different medians. The implication is to compare against peers with similar ACV/ARPA and motion, not broad SaaS averages [D3][D4].

Gross and net retention/churn should be interpreted together. Net metrics can look healthy while gross churn still indicates leakage that eventually constrains expansion. For model decisions, this means "net is positive" is insufficient if gross retention degrades after pricing changes [D4].

A critical interpretation mistake is mixing price elasticity with payment-operations failure. Subscription datasets show involuntary churn and payment recovery dynamics can materially move churn outcomes independent of model fairness. Model redesign should therefore follow a decomposition: involuntary churn remediation first, true value/price mismatch second [D5][D6].

Hybridization trends should be interpreted carefully: high usage-based adoption signals do not automatically imply pure usage success. Multiple 2024-2026 sources indicate coexistence of subscription anchors with usage expansion, meaning a strategist should interpret "usage adoption" as "hybrid adoption" unless evidence explicitly says otherwise [D7][D8].

Definitions differ across providers (for example how reactivations are counted in net measures), so values from different systems are not directly comparable without a metric dictionary. SKILL instructions should require explicit formula declarations for any threshold used in model recommendation [D3][D4][D9].

**Sources:**
- [D1] University of Groningen / JAMS record, "Accurately measuring willingness to pay... hypothetical bias meta-analysis" (2020): https://research.rug.nl/en/publications/accurately-measuring-willingness-to-pay-for-consumer-goods-a-meta - **EVERGREEN**
- [D2] Marketing Letters, "Incentive alignment in conjoint analysis: a meta-analysis" (2025): https://link.springer.com/article/10.1007/s11002-025-09764-8 - 2024-2026
- [D3] SaaS Capital, "SaaS retention benchmarks for private B2B companies" (2025): https://www.saas-capital.com/research/saas-retention-benchmarks-for-private-b2b-companies/ - 2024-2026
- [D4] ChartMogul, "Revenue churn (net and gross) definitions and benchmarks": https://chartmogul.com/saas-metrics/revenue-churn/ - Evergreen
- [D5] RevenueCat, "State of Subscription Apps 2024": https://revenuecat.com/state-of-subscription-apps-2024/ - 2024-2026
- [D6] Recurly, "2025 State of Subscriptions (sneak peek)": https://recurly.com/blog/2025-state-of-subscriptions-sneak-peek/ - 2024-2026
- [D7] High Alpha + OpenView, "2024 SaaS Benchmarks Report": https://highalpha.com/saas-benchmarks/2024 - 2024-2026
- [D8] Stripe, "The pricing model dilemma (2,000+ leaders)" (2024): https://stripe.com/blog/the-pricing-model-dilemma-according-to-2000-subscription-business-leaders - 2024-2026
- [D9] Salesforce, "What is Net Revenue Retention?" (2025): https://www.salesforce.com/blog/net-revenue-retention/ - 2024-2026

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

**Anti-pattern 1: "Predictability blindness" in usage or outcome recommendations**  
What it looks like: recommendations optimize value alignment but omit spend controls, resulting in invoice volatility and procurement pushback.  
Detection signal: forecast-to-invoice variance increases, overage disputes rise, and enterprise deals stall on commercial terms despite product demand.  
Consequence if missed: model rejection at procurement, discounting pressure, or forced mid-cycle contract exceptions.  
Mitigation: require caps/alerts/commitment options and explicit spend-visibility mechanics in every usage/outcome recommendation [F1][F2][F3].

**Anti-pattern 2: "Seat lock-in" where seat count no longer tracks delivered value**  
What it looks like: AI automation increases output while seat counts flatten or decline, but monetization remains mostly seat-based.  
Detection signal: seat compression per account while automation-heavy feature usage rises; expansion relies on discounting instead of value capture.  
Consequence if missed: revenue decouples from value and margin risk increases as compute cost grows.  
Mitigation: move to hybrid architecture with subscription anchor plus auditable expansion meter tied to value events [F4][F5].

**Anti-pattern 3: "Outcome theater" (outcome pricing without outcome governance)**  
What it looks like: outcome pricing is announced without contractual clarity on baseline, attribution boundaries, or dispute resolution.  
Detection signal: elongated legal cycles, redlines on definitions, recurring invoice disputes about whether outcomes were achieved.  
Consequence if missed: delayed revenue realization and weak trust despite "innovative" model positioning.  
Mitigation: only recommend pure outcome models when measurement and attribution controls are demonstrably mature; otherwise use hybrid with fixed floor [F1][F2].

**Anti-pattern 4: "Infrastructure-last monetization"**  
What it looks like: model complexity increases before metering, entitlement, and invoice traceability are production-ready.  
Detection signal: manual invoice fixes, delayed launches, finance escalations, high exception processing.  
Consequence if missed: operational debt erases model advantages and degrades customer trust.  
Mitigation: pass/fail operational readiness gate before approving usage/outcome/hybrid complexity [F4][F6][F7].

**Anti-pattern 5: "Compliance-as-afterthought" for recurring and AI contracts**  
What it looks like: cancellation or recurring terms are designed for conversion optimization while legal and consumer-rights constraints are deferred.  
Detection signal: mismatch between signup and cancellation friction, rising complaints, legal review bottlenecks late in launch process.  
Consequence if missed: regulatory risk, forced emergency policy changes, brand damage.  
Mitigation: include cancellation parity and recurring disclosure requirements as non-negotiable design constraints [F8][F9].

**Anti-pattern 6: "Frankenpricing complexity"**  
What it looks like: too many meters, add-ons, and exceptions are introduced at once in hybrid design.  
Detection signal: long pricing clarification cycles, poor quote velocity, increased support tickets about billing logic.  
Consequence if missed: lower conversion and higher support burden despite potentially better theoretical value alignment.  
Mitigation: set a complexity budget (max core meters, max add-on classes), require invoice simulation, and simplify before scaling [F4][F10][F11].

**Sources:**
- [F1] BCG, "Rethinking B2B Software Pricing in the Era of AI" (2025): https://www.bcg.com/publications/2025/rethinking-b2b-software-pricing-in-the-era-of-ai - 2024-2026
- [F2] Andreessen Horowitz, "AI enterprise buying 2025": https://a16z.com/ai-enterprise-2025/ - 2024-2026
- [F3] Andreessen Horowitz, "Customers want predictability in usage-based pricing" (2024): https://a16z.com/customers-want-predictability-in-usage-based-pricing-heres-how-to-help-them-get-it/ - 2024-2026
- [F4] Bain, "Per-seat software pricing isn't dead..." (2025): https://www.bain.com/insights/per-seat-software-pricing-isnt-dead-but-new-models-are-gaining-steam/ - 2024-2026
- [F5] High Alpha + OpenView, "2024 SaaS Benchmarks Report": https://highalpha.com/saas-benchmarks/2024 - 2024-2026
- [F6] Metronome, "State of Usage-Based Pricing 2025": https://metronome.com/state-of-usage-based-pricing-2025 - 2024-2026
- [F7] L.E.K. Consulting, "How Consumption-Based Pricing Reshapes..." (2025): https://www.lek.com/insights/tmt/us/ei/how-consumption-based-pricing-reshapes-growth-profitability-and-value - 2024-2026
- [F8] FTC, "Final click-to-cancel rule" (2024): https://www.ftc.gov/news-events/news/press-releases/2024/10/federal-trade-commission-announces-final-click-cancel-rule-making-it-easier-consumers-end-recurring - 2024-2026
- [F9] FTC Business Guidance, "Click to Cancel rule explanation" (2024): https://www.ftc.gov/business-guidance/blog/2024/10/click-cancel-ftcs-amended-negative-option-rule-what-it-means-your-business - 2024-2026
- [F10] SBI / Price Intelligently, "State of B2B SaaS Pricing in 2024": https://sbigrowth.com/hubfs/1-Research%20Reports/11.2024%20State%20of%20B2B%20SaaS%20Pricing%20Price%20Intelligently/SBI_StateofB2BSaaSPricing2024.pdf - 2024-2026
- [F11] Simon-Kucher, "Best practices for Generative AI packaging and pricing" (2024): https://www.simon-kucher.com/en/insights/best-practices-generative-ai-packaging-and-pricing - 2024-2026

---

### Angle 5+: AI Token Economics, Commercial Guardrails, and Regulatory Signals
> Additional domain-specific angle: how AI cost structures, contract design patterns, and 2025-2026 policy changes should shape pricing-model selection.

**Findings:**

AI pricing decisions are increasingly constrained by model cost dispersion. Public API pricing pages show that high-capability model tiers can be multiple orders of magnitude more expensive than mini tiers, so a flat-fee recommendation without model-routing constraints can destroy contribution margin. For strategist-grade guidance, this means model choice and model-routing policy must be treated as part of pricing-model design, not only product architecture [A1][A2].

Caching and batch pathways are now explicit commercial levers, not implementation trivia. Vendor pricing documentation (OpenAI, Anthropic) includes meaningful discounts for cached reads and batch processing paths, which implies that asynchronous workflows can support lower per-unit pricing while preserving margin. Pricing-model recommendations should include these operational levers when evaluating usage vs subscription expansion economics [A1][A3][A4].

Committed-capacity options (for example pre-purchased token units with SLA framing) remain an important middle lane between pure PAYG and broad enterprise custom contracts. This supports a three-lane strategy in the skill: PAYG lane for low-commitment adoption, committed/prepaid lane for predictability and discounts, and enterprise-custom lane for regulated or high-throughput buyers [A2][A5].

Visible market examples continue to show subscription anchors plus controlled overage structures rather than pure output pricing in most categories. Public pricing pages for leading AI tools commonly combine baseline plans with included usage quotas and explicit expansion charges, which reinforces a practical default toward hybrid design [A3][A5][A6].

Regulatory and compliance context is now directly relevant to model economics, not just legal review. EU guidance for GPAI obligations (effective period 2025-2026) and enterprise demand for data residency/privacy controls can require region-specific delivery constraints and additional operational overhead. Recommendations should therefore include a compliance-adjusted cost lens when comparing model options for enterprise segments [A7][A8][A9].

Benchmark caveat: many public benchmark claims in AI monetization are directional rather than population-representative. VC and vendor datasets are useful for trend detection but not definitive thresholds; the skill should require confidence labeling for each benchmark used in model rationale [A10][A11][A12].

**Sources:**
- [A1] OpenAI, "API pricing": https://openai.com/api/pricing/ - 2024-2026
- [A2] OpenAI, "Scale Tier for API customers": https://openai.com/api-scale-tier/ - 2024-2026
- [A3] Anthropic, "Claude pricing": https://claude.com/pricing#api - 2024-2026
- [A4] Anthropic, "Prompt caching": https://www.anthropic.com/news/prompt-caching - 2024-2026
- [A5] GitHub, "Copilot plans": https://github.com/features/copilot/plans - 2024-2026
- [A6] Intercom, "Fin pricing page": https://www.intercom.com/fin - 2024-2026
- [A7] European Commission, "Guidelines for providers of GPAI models" (2025): https://digital-strategy.ec.europa.eu/en/news/learn-more-about-guidelines-providers-general-purpose-ai-models - 2024-2026
- [A8] OpenAI, "Business data privacy and compliance": https://openai.com/business-data/ - 2024-2026
- [A9] OpenAI, "ChatGPT pricing": https://openai.com/chatgpt/pricing/ - 2024-2026
- [A10] Bessemer Venture Partners, "State of AI 2025": https://www.bvp.com/atlas/the-state-of-ai-2025 - 2024-2026
- [A11] Stripe, "Pricing model dilemma (2,000+ leaders)" (2024): https://stripe.com/blog/the-pricing-model-dilemma-according-to-2000-subscription-business-leaders - 2024-2026
- [A12] PricingSaaS benchmark press release (2024): https://www.prweb.com/releases/pricingsaas-releases-2024-q1-b2b-saas-pricing-benchmarks-302173945.html - 2024-2026 (lower-confidence benchmark source)

---

## Synthesis

The strongest cross-source signal is methodological, not ideological: the "right" pricing model is less about choosing the most modern label (usage, outcome, hybrid) and more about whether value metric quality, operational readiness, and customer predictability constraints are jointly satisfied. Where teams sequence these checks explicitly, model transitions are more durable and less likely to require emergency concessions.

A second synthesis point is that market direction and implementation reality are not the same thing. Sources converge on rising usage/hybrid adoption, but they also converge on significant execution drag from metering, billing complexity, and attribution ambiguity. This is why outcome-based and advanced usage designs should be treated as readiness-dependent states, not default recommendations.

Interpretation quality is a structural gap in many pricing processes. WTP evidence quality, retention metric definition drift, and involuntary churn confounds can all produce confident but wrong model conclusions. A robust skill should enforce evidence grading and formula transparency before accepting benchmark-based claims.

The most actionable update for `SKILL.md` is to convert the current guidance into an explicit decision system: stage-gated model selection, guardrail-by-default requirements, anti-pattern detection blocks, and a richer output schema capturing evidence confidence and operational feasibility. Contradictions between sources (for example "outcome is ideal" vs "outcome is hard to operationalize") should be encoded as decision rules rather than treated as unresolved noise.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.

- [x] Add a stage-gated methodology that forces value metric validation, readiness checks, and model selection in sequence.
- [x] Add an explicit value metric rubric (correlation, observability, budgetability) and reject weak metrics before model choice.
- [x] Add a model-decision rule set that defaults to hybrid when evidence is mixed and predictability is a buyer requirement.
- [x] Add mandatory guardrails for any usage/outcome component (caps, alerts, commitments, spend visibility).
- [x] Add an operational readiness gate covering metering, billing traceability, entitlement control, and dispute handling.
- [x] Add evidence interpretation rules: WTP calibration requirement, gross+net retention co-analysis, involuntary churn decomposition.
- [x] Add anti-pattern warning blocks with detection signals, consequences, and mitigation steps.
- [x] Expand `## Available Tools` to include stricter internal tool usage guidance and reference-only external API evidence checks.
- [x] Expand artifact schema to include evidence quality, readiness scores, confidence, and review cadence.
- [x] Add an explicit review cadence requirement (e.g., 90-day or renewal-cycle reassessment) to prevent stale model lock-in.

---

## Draft Content for SKILL.md

> This is the most important section. For every recommendation above, write the actual text that should go into SKILL.md.

### Draft: Replace Core Mode and Decision Principle

---
### Core mode

You are selecting the **pricing model architecture**, not the price number and not tier packaging details. Your output must answer: "What unit of value should we charge on, and what commercial structure keeps that unit fair to customers and viable to operate?"

You must optimize for three constraints at once:
1. **Value alignment:** customers pay more when they get more value.
2. **Customer predictability:** buyers can budget and govern spend.
3. **Supplier operability:** metering, billing, and margin exposure are manageable.

If one constraint fails, the model is not ready even if the other two look attractive.
---

### Draft: Methodology - Stage-Gated Model Selection Workflow

---
### Methodology

Before recommending any model, run this stage-gated sequence in order. You may not skip a stage.

**Stage 1 - Candidate value metrics**
You must define 2-4 candidate value metrics from customer outcomes and usage behavior. For each candidate, score:
- **Correlation to customer value realization** (does higher metric value actually mean the customer is getting more value?),
- **Observability/auditability** (can both vendor and customer verify the number?),
- **Budgetability** (can finance/procurement forecast spend before invoice).

If no candidate passes all three criteria, do not force model selection. Return `needs_more_research` and request improved instrumentation or discovery evidence.

**Stage 2 - Evidence quality check**
You must classify evidence inputs before using them:
- WTP surveys or conjoint without behavioral validation = `medium` confidence.
- WTP evidence with behavioral calibration (pilot, holdout, or live conversion evidence) = `high` confidence.
- Anecdotal benchmark/blog-only evidence = `low` confidence unless supported by independent dataset.

If a core decision depends on `low` confidence evidence, output must include a risk note and a validation plan.

**Stage 3 - Model fit scoring**
Score each model candidate (`flat_subscription`, `per_seat`, `consumption_metered`, `outcome_based`, `hybrid`) against:
- value alignment score,
- predictability score,
- operational readiness score,
- margin robustness score.

Use a weighted score, but never auto-select from score alone. Confirm that top model has no red-flag failures in Stages 4-5.

**Stage 4 - Operational readiness gate**
Before selecting `consumption_metered`, `outcome_based`, or complex `hybrid`, verify:
- metering event schema exists and is stable,
- entitlement/packaging control exists,
- invoice traceability from meter to line-item exists,
- exception/dispute flow exists,
- finance can simulate invoice impact from historical usage.

If two or more checks fail, route to a simpler interim model and document remediation milestones.

**Stage 5 - Guardrail design**
For usage/outcome components, include a mandatory predictability block:
- customer spend alerts,
- soft and hard caps,
- commitment/prepay option,
- overage policy with explicit rate card,
- fair-use or abuse constraints.

A recommendation without this block is invalid.

**Stage 6 - Review cadence**
Define review cadence now (for example quarterly or renewal-driven) with trigger events:
- material margin deviation,
- increasing forecast-to-invoice variance,
- seat compression with rising automation usage,
- expansion slowdown with stable product engagement.

Pricing model is not one-and-done. You must provide the next review trigger and owner.
---

### Draft: Value Metric Selection Rubric

---
### Value metric selection

Use this rubric for each candidate metric:

1. **Customer value correlation**  
Describe the customer job-to-be-done and show why this metric increases when customer outcomes improve. If correlation is weak or indirect, reject.

2. **Measurement integrity**  
Describe how the metric is measured, deduplicated, and audited. If the customer cannot independently verify the unit, reject or downgrade confidence.

3. **Budget predictability**  
Estimate spend volatility under realistic usage bands. If forecast-to-invoice variance is likely high and no controls exist, require guardrails or reject.

4. **Behavioral incentive check**  
Test whether the metric encourages healthy behavior. If it incentivizes hiding usage, suppressing adoption, or gaming low-value events, reject.

5. **Margin sensitivity check**  
Estimate whether cost-to-serve variability can make the metric margin-destructive at high adoption. If yes, require model-routing rules or surcharge logic.

Decision rule:
- If 4-5 criteria pass: candidate can be primary value metric.
- If 2-3 criteria pass: candidate can be secondary metric in hybrid only.
- If 0-1 criteria pass: do not use this metric.
---

### Draft: Model Decision Rules (if/then logic)

---
### Model type selection rules

Use these decision rules after value-metric scoring:

- If value is mostly team collaboration and seat count still tracks realized value, choose `per_seat` or `hybrid` with seat anchor.
- If value scales with auditable consumption and customer usage variability is high, choose `consumption_metered` or `hybrid`.
- If outcome is measurable, attributable, and contract-governable, consider `outcome_based`; otherwise choose `hybrid` with fixed floor.
- If evidence is mixed and buyer predictability is a hard requirement, default to `hybrid` (base subscription + included usage + explicit expansion).
- If billing/metering readiness is weak, do not choose pure usage or pure outcome. Choose transitional model and document readiness milestones.

Tie-breaker hierarchy:
1. Reject models that fail operational readiness.
2. Reject models that fail customer predictability.
3. Prefer model with stronger value correlation and margin robustness.

Do not select model by competitor mimicry alone. Competitor model can be context, never primary proof.
---

### Draft: Predictability and Margin Guardrail Block

---
### Predictability and margin guardrails (required for usage/outcome/hybrid)

When the selected model contains variable charges, include this block in the artifact:

- **Customer controls:** real-time usage visibility, threshold alerts, soft cap default, optional hard cap, and clear overage schedule.
- **Commercial options:** prepaid credits/commitment plan and true-up rules.
- **Internal controls:** model-routing policy (allowed model classes by tier), per-account cost watchlist, and escalation threshold.
- **Contract clarity:** explicit definitions for billable events, exclusions, and dispute window.

Detection triggers for guardrail failure:
- repeated overage disputes,
- high forecast-to-invoice variance,
- enterprise procurement delays on pricing terms,
- gross margin degradation at high-usage accounts.

If two or more triggers are active, recommend guardrail redesign before changing base model again.
---

### Draft: Evidence Interpretation and Signal Quality Rules

---
### Evidence interpretation rules

You must annotate each evidence input with `confidence` and `source_type`.

Use these interpretation rules:

1. **WTP evidence calibration**
Treat survey/conjoint-only WTP as directional. Require behavioral calibration for high-confidence model changes.

2. **Retention metric discipline**
Evaluate both gross and net retention/churn. Net alone can hide leakage.

3. **Definition transparency**
For every benchmark threshold, include formula definition and provider source. Do not mix incomparable definitions silently.

4. **Involuntary churn decomposition**
Before concluding "price too high," quantify payment-failure and recovery dynamics. If involuntary churn dominates, prioritize billing ops fixes first.

5. **Benchmark confidence labeling**
Label benchmark evidence as `high` (independent broad dataset), `medium` (vendor/operator benchmark), or `low` (anecdotal case set).

6. **Decision confidence requirement**
If selected model depends on mostly `low` confidence evidence, set overall decision confidence to `low` and include a validation plan with explicit stop/go criteria.
---

### Draft: Anti-Pattern Warning Blocks

---
### Anti-pattern warnings

#### Warning: Predictability Blindness
- **What it looks like:** recommendation uses variable billing but omits caps/alerts/commitment options.
- **Detection signal:** rising overage disputes and large forecast-to-invoice variance.
- **Consequence:** procurement rejects model or forces heavy discounting.
- **Mitigation:** add spend controls and transparent usage reporting before rollout.

#### Warning: Seat Lock-In During Automation Shift
- **What it looks like:** seat pricing remains primary while automation output rises and seat growth stalls.
- **Detection signal:** account value expands without seat expansion.
- **Consequence:** value capture decouples from delivered outcomes.
- **Mitigation:** move to hybrid with auditable expansion meter.

#### Warning: Outcome Theater
- **What it looks like:** "pay for outcomes" is proposed without baseline or attribution protocol.
- **Detection signal:** legal redlines and invoice disputes on what counts as outcome.
- **Consequence:** delayed revenue and trust erosion.
- **Mitigation:** use hybrid fixed floor + outcome variable until governance is mature.

#### Warning: Infrastructure-Last Monetization
- **What it looks like:** complex model selected before metering and invoice traceability are ready.
- **Detection signal:** manual corrections and billing escalations.
- **Consequence:** operations debt erases strategic benefit.
- **Mitigation:** enforce readiness gate; use simpler interim model if gate fails.

#### Warning: Frankenpricing Complexity
- **What it looks like:** too many meters/add-ons/exceptions introduced in one launch.
- **Detection signal:** slow quoting and high billing explanation tickets.
- **Consequence:** conversion loss and support burden.
- **Mitigation:** set complexity budget and require invoice simulation.
---

### Draft: Available Tools (updated section text)

---
## Available Tools

Use internal Flexus artifacts first. Activate relevant strategy context before any recommendation:

```python
flexus_policy_document(op="activate", args={"p": "/pain/wtp-research-{date}"})
flexus_policy_document(op="activate", args={"p": "/strategy/offer-design"})
flexus_policy_document(op="activate", args={"p": "/strategy/positioning-map"})
flexus_policy_document(op="list", args={"p": "/pain/"})
```

Record final decision only after methodology and guardrail checks are complete:

```python
write_artifact(
    artifact_type="pricing_model",
    path="/strategy/pricing-model",
    data={...},
)
```

Reference-only external validation endpoints (not called directly by this skill, but valid for evidence checks):
- Stripe usage: `POST /v1/billing/meter_events`
- Paddle charge: `POST /subscriptions/{subscription_id}/charge`
- LaunchDarkly flags: `POST /api/v2/flags/{projectKey}`
- Amplitude ingestion: `POST https://api2.amplitude.com/2/httpapi`
- Segment events: `POST /v1/track`

Do not invent tools, methods, or endpoints. If an external method cannot be verified in official docs, do not cite it.
---

### Draft: Recording and Artifact Quality Contract

---
### Recording requirements

When writing `/strategy/pricing-model`, always include:
- selected model and rationale,
- value metric scoring summary,
- alternatives considered and rejection reasons,
- guardrail design,
- operational readiness pass/fail details,
- evidence log with confidence labels,
- next review cadence and owner.

Do not write a "final" model if core evidence is weak. Use explicit uncertainty and validation steps instead of forced certainty.
---

### Draft: Schema additions

```json
{
  "pricing_model": {
    "type": "object",
    "required": [
      "created_at",
      "selected_model",
      "value_metric",
      "model_rationale",
      "constraints",
      "risks",
      "operational_readiness",
      "predictability_controls",
      "evidence_log",
      "decision_confidence",
      "review_plan"
    ],
    "additionalProperties": false,
    "properties": {
      "created_at": {
        "type": "string",
        "description": "ISO-8601 UTC timestamp when recommendation was generated."
      },
      "selected_model": {
        "type": "string",
        "enum": [
          "flat_subscription",
          "per_seat",
          "consumption_metered",
          "freemium",
          "outcome_based",
          "hybrid"
        ],
        "description": "Selected pricing model architecture."
      },
      "value_metric": {
        "type": "object",
        "required": [
          "metric",
          "unit",
          "rationale",
          "evidence_basis",
          "correlation_score",
          "observability_score",
          "budgetability_score"
        ],
        "additionalProperties": false,
        "properties": {
          "metric": {
            "type": "string",
            "description": "Primary metric name, e.g., seats, API calls, resolved tickets."
          },
          "unit": {
            "type": "string",
            "description": "Billable unit label used in contracts and invoices."
          },
          "rationale": {
            "type": "string",
            "description": "Why this metric best aligns with customer value."
          },
          "evidence_basis": {
            "type": "string",
            "description": "Summary of empirical evidence supporting this metric choice."
          },
          "correlation_score": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5,
            "description": "Score for value correlation strength."
          },
          "observability_score": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5,
            "description": "Score for measurement transparency and auditability."
          },
          "budgetability_score": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5,
            "description": "Score for customer spend predictability."
          }
        }
      },
      "model_rationale": {
        "type": "string",
        "description": "Narrative explaining why selected model outperforms alternatives under current constraints."
      },
      "constraints": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Known constraints affecting model viability (sales motion, legal, margin, billing stack)."
      },
      "risks": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Principal risks if this model is implemented now."
      },
      "alternatives_considered": {
        "type": "array",
        "items": {
          "type": "object",
          "required": [
            "model",
            "rejection_reason"
          ],
          "additionalProperties": false,
          "properties": {
            "model": {
              "type": "string",
              "description": "Alternative model assessed."
            },
            "rejection_reason": {
              "type": "string",
              "description": "Why this model was not selected at this stage."
            }
          }
        },
        "description": "Alternatives and explicit rejection logic."
      },
      "operational_readiness": {
        "type": "object",
        "required": [
          "metering_ready",
          "entitlements_ready",
          "invoice_traceability_ready",
          "dispute_flow_ready",
          "finance_simulation_ready",
          "readiness_notes"
        ],
        "additionalProperties": false,
        "properties": {
          "metering_ready": {
            "type": "boolean",
            "description": "Whether billable events are instrumented and stable."
          },
          "entitlements_ready": {
            "type": "boolean",
            "description": "Whether packaging and feature access controls are operational."
          },
          "invoice_traceability_ready": {
            "type": "boolean",
            "description": "Whether invoices can be reconciled from billable events."
          },
          "dispute_flow_ready": {
            "type": "boolean",
            "description": "Whether support/finance workflow exists for billing disputes."
          },
          "finance_simulation_ready": {
            "type": "boolean",
            "description": "Whether historical usage can be replayed to estimate invoice impact."
          },
          "readiness_notes": {
            "type": "string",
            "description": "Short explanation of failed checks and remediation steps."
          }
        }
      },
      "predictability_controls": {
        "type": "object",
        "required": [
          "usage_alerts",
          "soft_cap",
          "hard_cap_option",
          "commitment_option",
          "overage_policy",
          "customer_visibility"
        ],
        "additionalProperties": false,
        "properties": {
          "usage_alerts": {
            "type": "boolean",
            "description": "Whether proactive spend/usage alerts are included."
          },
          "soft_cap": {
            "type": "boolean",
            "description": "Whether soft cap behavior is defined."
          },
          "hard_cap_option": {
            "type": "boolean",
            "description": "Whether hard cap can be enabled for strict-budget buyers."
          },
          "commitment_option": {
            "type": "boolean",
            "description": "Whether prepaid/committed usage option is available."
          },
          "overage_policy": {
            "type": "string",
            "description": "Human-readable overage rule and rate-card behavior."
          },
          "customer_visibility": {
            "type": "string",
            "enum": [
              "none",
              "periodic_report",
              "self_serve_dashboard"
            ],
            "description": "How customers can view spend trajectory during billing period."
          }
        }
      },
      "evidence_log": {
        "type": "array",
        "minItems": 3,
        "items": {
          "type": "object",
          "required": [
            "claim",
            "source_title",
            "source_url",
            "source_year",
            "confidence",
            "is_evergreen"
          ],
          "additionalProperties": false,
          "properties": {
            "claim": {
              "type": "string",
              "description": "Specific claim used in the recommendation."
            },
            "source_title": {
              "type": "string",
              "description": "Human-readable source title."
            },
            "source_url": {
              "type": "string",
              "description": "Source URL used for verification."
            },
            "source_year": {
              "type": "integer",
              "description": "Publication year of source."
            },
            "confidence": {
              "type": "string",
              "enum": [
                "low",
                "medium",
                "high"
              ],
              "description": "Confidence in this claim for decision-making."
            },
            "is_evergreen": {
              "type": "boolean",
              "description": "True if source is older but considered foundational."
            }
          }
        },
        "description": "Traceable evidence entries supporting major claims."
      },
      "decision_confidence": {
        "type": "string",
        "enum": [
          "low",
          "medium",
          "high"
        ],
        "description": "Overall confidence in selected model given current evidence quality."
      },
      "review_plan": {
        "type": "object",
        "required": [
          "cadence",
          "owner_role",
          "triggers"
        ],
        "additionalProperties": false,
        "properties": {
          "cadence": {
            "type": "string",
            "enum": [
              "monthly",
              "quarterly",
              "per_renewal_cycle"
            ],
            "description": "Planned reassessment cadence."
          },
          "owner_role": {
            "type": "string",
            "description": "Role accountable for model reassessment."
          },
          "triggers": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Trigger events that force early reassessment."
          }
        }
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Independent, open-methodology benchmark datasets for AI pricing model performance remain limited; many sources are vendor or advisory datasets.
- Public sources often disagree on definitions (especially retention variants), making threshold portability imperfect without formula normalization.
- Public benchmark evidence for annual discount norms and overage patterns in AI tools is still mostly directional and anecdotal.
- Regulatory guidance is evolving quickly (especially AI obligations by region), so compliance-related cost assumptions require periodic refresh.
- Some tool limits/pricing details are plan-dependent or change frequently; implementation teams must re-verify docs at execution time.
