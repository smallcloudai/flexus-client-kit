# Research: pricing-tier-design

**Skill path:** `flexus_simple_bots/strategist/skills/pricing-tier-design/`
**Bot:** strategist
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`pricing-tier-design` defines concrete price points, tier names, feature fences, upgrade triggers, and upsell architecture after upstream strategy work is done. It consumes the pricing model choice, offer design decisions, and willingness-to-pay evidence, then produces a structured `pricing_tier_structure` artifact.

The skill currently has a strong WTP-first stance and practical baseline guidance (PSM anchoring, feature fences, and trigger mapping). This research expands it into a more complete 2024-2026-ready operating method: multi-method evidence stacking (not PSM-only), explicit confidence and migration governance, AI-era hybrid monetization guardrails, and stricter anti-pattern detection that can be encoded into schema and generation checks.

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
- No invented tool names, method IDs, or API endpoints: **passed**
- Contradictions between sources explicitly noted: **passed**
- Volume target met (Findings sections 800-4000 words): **passed**

---

## Research Angles

Each angle should be researched by a separate sub-agent. Add more angles if the domain requires it.

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

- Pricing teams are increasingly designing a full monetization system, not isolated price points. Reforge's 2025 framing (`Scale`, `What`, `Amount`, `When`) is useful because it forces value metric, package structure, and payment cadence to be decided together instead of independently.
- For B2B SaaS, 3-4 plans remains a common baseline and Good-Better-Best remains prevalent in benchmark data, making it a reasonable default prior unless segment evidence justifies a different architecture.
- Pricing process cadence has shifted to recurring operations: 2024-2025 benchmark studies show most teams update at least annually and a large share updates quarterly, which implies this skill should output review cadence and ownership metadata, not one-off recommendations.
- In AI-influenced SaaS pricing, hybrid models (seat + usage or seat + AI meter) are increasing faster than pure usage/outcome models. Multiple 2024-2025 strategy sources describe transition to hybrid as the practical near-term path.
- Separately priced AI add-ons can under-convert in many contexts (reported low attach rates in 2025 survey data), so defaulting to separate AI add-ons without explicit segment/cost evidence is risky.
- Feature packaging quality improves when features are role-tagged by value contribution and willingness-to-pay impact (for example, leader/filler/add-on style role mapping), then distributed intentionally across tiers to create valid upgrade pathways.
- Usage meter selection guidance has converged: meter must map to customer-perceived value, remain explainable to non-technical buyers, and preserve spend predictability with included usage, alerts, and guardrails.
- Migration is now a first-class methodology step. Current billing docs and public pricing change announcements show that versioned plans, staged migration rules, and grandfathering/renewal policies are necessary to avoid churn and support load during tier redesign.
- WTP evidence should be triangulated. 2024 IJRM evidence supports closed direct WTP prompts over open-ended prompts in some innovation contexts, while meta-analysis evidence (older but still relevant) reinforces hypothetical bias risk if no behavioral validation is done.
- PSM remains useful for initial range-finding, especially in earlier-stage contexts, but practical guidance favors conjoint/choice methods plus behavioral experiments for final pricing decisions and trade-off resolution.

**Sources:**
- [How to Price Your AI Product or Feature (Reforge)](https://www.reforge.com/blog/how-to-price-your-ai-product) - 2025
- [Per-Seat Software Pricing Isn't Dead, but New Models Are Gaining Steam (Bain)](https://www.bain.com/insights/per-seat-software-pricing-isnt-dead-but-new-models-are-gaining-steam/) - 2025
- [AI-Enhanced Pricing Can Boost Revenue Growth (Bain)](https://www.bain.com/insights/ai-enhanced-pricing-can-boost-revenue-growth/) - 2024
- [2024 SaaS Benchmarks (High Alpha + OpenView)](https://highalpha.com/saas-benchmarks/2024) - 2024
- [State of B2B SaaS Pricing 2024 (SBI)](https://sbigrowth.com/hubfs/1-Research%20Reports/11.2024%20State%20of%20B2B%20SaaS%20Pricing%20Price%20Intelligently/SBI_StateofB2BSaaSPricing2024.pdf) - 2024
- [2025 State of SaaS Pricing (SBI)](https://sbigrowth.com/tools-and-solutions/2025_state_of_saas_pricing_report) - 2025
- [How to Monetize Generative AI Features in SaaS (Simon-Kucher)](https://www.simon-kucher.com/en/insights/how-monetize-generative-ai-features-saas) - 2024
- [Best Practices for Generative AI Packaging and Pricing (Simon-Kucher)](https://www.simon-kucher.com/en/insights/best-practices-generative-ai-packaging-and-pricing) - 2024
- [Hitting the Bullseye: Measuring WTP for Innovations (IJRM)](https://ideas.repec.org/a/eee/ijrema/v41y2024i2p383-402.html) - 2024
- [Accurately Measuring WTP: Hypothetical Bias Meta-Analysis (JAMS)](https://research.rug.nl/en/publications/accurately-measuring-willingness-to-pay-for-consumer-goods-a-meta) - 2020 (**evergreen**)
- [Van Westendorp Pricing Model (Sawtooth)](https://sawtoothsoftware.com/resources/blog/posts/van-westendorp-pricing-sensitivity-meter) - undated vendor methodology doc, accessed 2026 (**evergreen**)

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

- Stripe Billing is a strong API-native option for implementing tier catalogs and entitlement-aware packaging. Public docs cover pricing, limits, and operational constraints that directly affect pricing architecture rollouts.
- Stripe's 2025 changelog indicates migration away from legacy usage-billing patterns (meter attachment requirements and removed legacy fields), which matters if historical tier logic depended on deprecated usage primitives.
- Paddle remains a practical merchant-of-record option where tax/compliance burden reduction is more important than maximum billing API flexibility.
- Paddle publishes concrete API rate limits and explicit subscription-update caps for immediate chargeable updates; these constraints should inform any auto-upgrade/seat-mutation logic in downstream execution workflows.
- Chargebee provides broad catalog model support (flat/per-unit/tiered/volume/stairstep/package) and publishes rate/concurrency limits, but public pricing transparency is less direct than Stripe/Paddle and often requires sales confirmation.
- PostHog provides experimentation and feature-flag infrastructure with usage-based billing mechanics for flag checks. This is useful for paywall and packaging experiments but requires cost guardrails due to request-based billing behavior.
- Statsig provides modern experimentation capabilities (including higher-tier statistical methods), but documentation and pricing pages can differ on free-tier quotas; any hardcoded quota assumptions should be validated at implementation time.
- Apify, Bright Data, and SerpApi provide competitor-pricing and market collection options with public throughput/pricing docs. They differ meaningfully in cost shape, legal/compliance posture, and operational constraints.
- Similarweb APIs add market-context signals (traffic/channel trends) but with credit and rate constraints; these are directional context signals, not direct willingness-to-pay evidence.
- A practical stack split emerges: (1) billing execution platform, (2) experimentation/in-product telemetry platform, (3) external competitive/market data platform. Mixing these concerns in one tool leads to blind spots.

**Sources:**
- [Stripe Billing Pricing](https://stripe.com/billing/pricing) - accessed 2026
- [Stripe Rate Limits](https://docs.stripe.com/rate-limits) - accessed 2026
- [Stripe Billing APIs](https://docs.stripe.com/billing/billing-apis) - accessed 2026
- [Stripe Changelog: Removes Legacy Usage-Based Billing](https://docs.stripe.com/changelog/basil/2025-03-31/deprecate-legacy-usage-based-billing) - 2025
- [Paddle Pricing](https://www.paddle.com/pricing) - accessed 2026
- [Paddle API Rate Limiting](https://developer.paddle.com/api-reference/about/rate-limiting) - accessed 2026
- [Paddle Changelog: Preview Rate Limits](https://developer.paddle.com/changelog/2026/rate-limits-preview-prices-transactions) - 2026
- [Chargebee API Limits](https://www.chargebee.com/docs/2.0/site-configuration/articles-and-faq/what-are-the-chargebee-api-limits.html) - accessed 2026
- [Chargebee API Error Handling and Limits](https://apidocs.chargebee.com/docs/api/error-handling) - accessed 2026
- [Chargebee Plans Catalog Docs](https://www.chargebee.com/docs/billing/2.0/product-catalog/plans) - accessed 2026
- [PostHog Pricing Philosophy](https://posthog.com/pricing/philosophy) - accessed 2026
- [PostHog Feature Flag Cost Controls](https://posthog.com/docs/feature-flags/cutting-costs) - accessed 2026
- [Statsig Pricing](https://www.statsig.com/pricing) - accessed 2026
- [Statsig Experimentation Program Guide](https://docs.statsig.com/guides/experimentation-program) - accessed 2026
- [Apify Pricing](https://apify.com/pricing) - accessed 2026
- [Apify Platform Limits](https://docs.apify.com/platform/limits) - accessed 2026
- [Bright Data Web Scraper Pricing](https://brightdata.com/pricing/web-scraper) - accessed 2026
- [Bright Data Scraper Overview](https://docs.brightdata.com/datasets/scrapers/scrapers-library/overview) - accessed 2026
- [SerpApi Pricing](https://serpapi.com/pricing) - accessed 2026
- [SerpApi Google Shopping API](https://serpapi.com/google-shopping-api) - accessed 2026
- [Similarweb Rate Limits](https://developers.similarweb.com/docs/rate-limit) - accessed 2026

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

- PSM should be interpreted as an early boundary signal, not final pricing truth. Vendor methodology guidance explicitly cautions against treating line-crossing outputs as behavior-equivalent decision endpoints.
- PSM data quality checks matter: logical response validation and segment filtering reduce noisy/inconsistent responses; without these gates, "optimal" points can be artifacts of invalid input.
- Practical minimum sample guidance differs by method and source, but conjoint/CBC guidance repeatedly emphasizes level-appearance sufficiency and subgroup adequacy, not just one total sample count.
- Experiment platforms use different defaults (for example, confidence levels and minimum sample/conversion floors). If teams compare results across tools without normalizing these defaults, "winner" labels become inconsistent.
- Minimum duration should combine business-cycle coverage and statistical power. Multiple practitioner sources warn that fixed 7-day minimums alone are insufficient for pricing tests.
- Frequent peeking without sequential methods can dramatically inflate false positives; sequential frameworks or pre-declared stop rules should be mandatory when continuous monitoring is used.
- Sample Ratio Mismatch (SRM) should be treated as a hard validity gate, not a warning. If SRM is present, effect estimates can be invalid regardless of apparent lift.
- Segment mining after the fact increases false discovery risk. Segment slices used for decisioning should be pre-registered whenever possible.
- Pricing decision quality improves when conversion is interpreted together with revenue, expansion, and retention signals, not conversion alone.
- Retention interpretation should include both NRR and GRR and cohort definition matching. Benchmarks can diverge widely by segment definition, ACV bucket, B2B/B2C mix, and time windows.

**Sources:**
- [Van Westendorp Pricing Model (Sawtooth)](https://sawtoothsoftware.com/resources/blog/posts/van-westendorp-pricing-sensitivity-meter) - accessed 2026 (**evergreen**)
- [SurveyMonkey Van Westendorp Guidance](https://help.surveymonkey.com/en/surveymonkey/solutions/van-westendorp/) - accessed 2026
- [Conjointly Sample Size Guidance](https://conjointly.com/faq/guidance-on-sample-size) - accessed 2026
- [Sawtooth CBC Sample Size Rule of Thumb](https://sawtoothsoftware.com/resources/blog/posts/sample-size-rules-of-thumb) - accessed 2026 (**evergreen**)
- [Optimizely Statistical Significance](https://support.optimizely.com/hc/en-us/articles/4410284003341-Statistical-significance) - accessed 2026
- [Optimizely Test Duration Guidance](https://support.optimizely.com/hc/en-us/articles/4410283969165-How-long-to-run-an-experiment) - accessed 2026
- [Amplitude Statistical Significance FAQ](https://amplitude.com/docs/faq/statistical-significance) - 2024
- [Amplitude Statistical Preferences](https://amplitude.com/docs/feature-experiment/workflow/finalize-statistical-preferences) - 2024
- [Statsig Sequential Testing Perspective](https://www.statsig.com/perspectives/sequential-testing-ab-peek) - 2025
- [Statsig Monitor Docs](https://docs-legacy.statsig.com/experiments-plus/monitor/) - accessed 2026
- [Microsoft ExP on SRM](https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/) - 2019 (**evergreen**)
- [Stripe Pricing Experiments Guide](https://stripe.com/resources/more/pricing-experiments) - 2024
- [SaaS Capital Retention Benchmarks 2025](https://www.saas-capital.com/research/saas-retention-benchmarks-for-private-b2b-companies/) - 2025
- [ChartMogul SaaS Retention 2025](https://chartmogul.com/reports/saas-retention-the-ai-churn-wave/) - 2025
- [ChartMogul Retention Report](https://chartmogul.com/reports/saas-retention-report/) - 2023 (**evergreen**)

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

- **Anti-pattern: Tier sprawl.**
  - Detection signal: 5+ self-serve tiers with overlapping features and no clear persona mapping.
  - Consequence: Buyer confusion, slower decision cycles, lower conversion.
  - Mitigation: Cap self-serve tiers by default and require explicit rationale for exceptions.
- **Anti-pattern: Ambiguous names and ordering.**
  - Detection signal: Plan names that do not encode buyer type or maturity and trigger frequent "which plan is for me?" questions.
  - Consequence: Mis-selection and conversion leakage into sales-assisted channels.
  - Mitigation: Require each tier to include target persona and explicit "not for" guidance.
- **Anti-pattern: Weak adjacent fences.**
  - Detection signal: Tier differences are mostly cosmetic; users consume high value while staying in low tier.
  - Consequence: Monetization leakage and repeated packaging churn.
  - Mitigation: Require capability + usage + commercial fence deltas for every adjacent tier pair.
- **Anti-pattern: Repricing shock without migration.**
  - Detection signal: Large one-step increases and no grandfathering/cutover policy.
  - Consequence: Churn spikes, support burden, trust damage.
  - Mitigation: Add staged migration plan with renewal-based cutover and communication checkpoints.
- **Anti-pattern: Overuse of "Contact Sales" for non-enterprise tiers.**
  - Detection signal: No public numeric anchors for self-serve offers.
  - Consequence: Early funnel friction and delayed buyer qualification.
  - Mitigation: Require list price or at least starting range for non-enterprise tiers.
- **Anti-pattern: Seat-only metric for usage-heavy AI value delivery.**
  - Detection signal: Value/COGS scale with usage while seat count remains flat.
  - Consequence: Margin compression and ACV stagnation despite product adoption.
  - Mitigation: Use hybrid base + usage or outcome-linked components where value metric fit is proven.
- **Anti-pattern: Metered pricing without spend safety.**
  - Detection signal: No alert thresholds, no hard/soft caps, overage discovered only at invoice.
  - Consequence: Bill shock disputes and renewal risk.
  - Mitigation: Encode alert policy, cap policy, and committed usage option in pricing design.
- **Anti-pattern: Repackaging without entitlement migration mapping.**
  - Detection signal: Sales/support cannot answer "who moves when to what price/entitlement."
  - Consequence: Inconsistent exceptions, account confusion, failed renewals.
  - Mitigation: Require machine-readable old->new mapping and timeline in artifact.

**Sources:**
- [State of B2B SaaS Pricing Benchmarks 2024 (SBI)](https://sbigrowth.com/tools-and-solutions/pricing-benchmarks-report-2024) - 2024
- [Tracking 443 SaaS Pricing Pages (Growth Unhinged)](https://www.growthunhinged.com/p/state-of-saas-pricing-changes-2024) - 2024
- [G2 Pricing Transparency Analysis](https://learn.g2.com/software-pricing-transparency?hsLang=en) - 2025
- [SaaS Trends Report Q1 2024 (Vendr)](https://www.vendr.com/insights/saas-trends-report-2024-q1) - 2024
- [BVP AI Pricing and Monetization Playbook](https://www.bvp.com/atlas/the-ai-pricing-and-monetization-playbook) - 2025
- [Clouded Judgement Seat-Based Pricing Analysis](https://cloudedjudgement.substack.com/p/clouded-judgement-61424-is-seat-based) - 2024
- [Stripe AI Pricing Framework](https://stripe.com/blog/a-framework-for-pricing-ai-products) - 2025
- [Zendesk AI Automated Resolutions Pricing Model](https://support.zendesk.com/hc/en-us/articles/5352026794010-About-automated-resolutions-for-AI-agents) - accessed 2026
- [Slack 2025 Pricing and Packaging Announcement](https://slack.com/blog/news/june-2025-pricing-and-packaging-announcement) - 2025
- [Slack 2025 Plan Availability and Pricing Update](https://slack.com/help/articles/39264531104275-Updates-to-feature-availability-and-pricing-for-Slack-plans) - 2025

---

### Angle 5: Pricing Benchmarks, Contracting, and Transparency Operations
> Additional domain-specific angle: practical commercial design patterns that influence tier decisions (term length, discounting, transparency, and rollout policy).

**Findings:**

- Monthly + annual availability remains the practical baseline for self-serve and mid-market motions; forcing long-term commitments too early can slow conversion and increase negotiation friction.
- Multi-year commitments still appear in enterprise motions, but public 2024-2025 commercial analyses suggest discounts should be tied to value/volume certainty, not term length alone.
- Pricing transparency remains low in many B2B categories, but strong evidence from buyer-side analysis shows transparency improves early qualification and trust for non-enterprise tiers.
- Publicly communicated migration mechanics (renewal timing, grandfathering, entitlement changes) are now observable best practice in major pricing-package updates and should be required in artifact output.
- Contract-term strategy should be modeled as risk management: longer terms improve revenue predictability but can reduce repricing agility; this trade-off should be explicit in recommendations.
- This angle reinforces that tier architecture is not complete until commercial policy details are specified (term options, annual discount band rationale, migration and communication rules).

**Sources:**
- [SaaS Trends Report Q1 2024 (Vendr)](https://www.vendr.com/insights/saas-trends-report-2024-q1) - 2024
- [Recurly 2025 Industry Report Press Release](https://recurly.com/press/retention-tops-trends-in-recurlys-2025-industry-report/) - 2025
- [Recurly 2025 Subscription Trends Sneak Peek](https://recurly.com/blog/2025-state-of-subscriptions-sneak-peek/) - 2025
- [G2 Pricing Transparency](https://learn.g2.com/software-pricing-transparency?hsLang=en) - 2025
- [Mostly Metrics Multi-Year Deal Analysis](https://www.mostlymetrics.com/p/your-guide-to-negotiating-multi-year-deals) - 2025
- [Paddle/ProfitWell Contract Length Study](https://www.paddle.com/studios/shows/profitwell-report/contract-length) - 2019 (**evergreen**)
- [Slack 2025 Packaging Update](https://slack.com/blog/news/june-2025-pricing-and-packaging-announcement) - 2025

---

## Synthesis

The strongest cross-source conclusion is that pricing-tier design is now an operating system problem, not a one-off arithmetic exercise. Teams that perform well are continuously iterating packaging and pricing at a governance cadence, and they explicitly connect value metric choice, feature fences, price levels, and migration plans. This aligns with both practitioner frameworks and current SaaS benchmark narratives.

Second, WTP anchoring is necessary but insufficient by itself. The evidence supports keeping PSM for early boundary framing, but major decisions should be triangulated with conjoint/choice evidence and behavioral test data before finalizing tier price points. The key practical implication for this skill is to produce confidence scores and evidence provenance fields, rather than outputting deterministic prices with no uncertainty metadata.

Third, tool landscape findings show that implementation constraints are no longer optional detail. Billing platform limits, meter changes, and experimentation defaults can directly invalidate a theoretically sound pricing design if ignored. A "best" tier design on paper is operationally weak unless it includes plan versioning/migration rules, spend guardrails for usage components, and experiment interpretation standards.

Finally, anti-pattern research shows repeated failure signatures: too many tiers, weak fences, ambiguous plan names, hidden pricing overuse, and repricing without migration logic. These are detectable and can be encoded as schema guardrails. The most actionable upgrade is to make these anti-pattern checks explicit reject conditions in the skill's method and artifact requirements.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.
> Each item here has a corresponding draft in the section below.

- [x] Replace current methodology with an explicit 8-step workflow that includes migration and governance outputs.
- [x] Add a tier-count and architecture prior (default 3-4 tiers, Good-Better-Best baseline, exception justification required).
- [x] Add a WTP evidence stack policy: PSM for boundaries, closed direct WTP + conjoint + behavioral validation for final pricing.
- [x] Add confidence scoring and contradiction handling rules for pricing recommendations.
- [x] Add feature-fence strength tests for each adjacent tier pair (capability + usage + commercial fence minimum).
- [x] Add experiment interpretation rules (confidence normalization, SRM hard stop, minimum sample/conversion floors, duration rules).
- [x] Add usage safety requirements for any metered/overage model (alerts, caps, committed option).
- [x] Add migration/rollout requirements (grandfathering, renewal cutover logic, entitlement map, comms checkpoints).
- [x] Update `## Available Tools` guidance with explicit internal tool sequence and evidence checks.
- [x] Expand artifact schema with governance, evidence, confidence, migration, and guardrail fields.

---

## Draft Content for SKILL.md

> This is the most important section. For every recommendation above, write the actual text that should go into SKILL.md.

### Draft: Methodology overhaul (8-step workflow)

---
### Methodology

You design pricing tiers as a system, not as isolated prices. Before setting any number, you must lock four decisions in order: value scale (what grows customer value), package structure (what each tier includes/excludes), amount (price levels), and payment timing (monthly/annual/other cadence). If these are decided independently, your output can look coherent while still producing weak upgrade motion and poor revenue quality.

Use this mandatory 8-step sequence:

1. **Load upstream strategy artifacts and declare assumptions.**  
   Activate `/strategy/pricing-model` and `/strategy/offer-design`, then list WTP evidence under `/pain/`. Start by writing explicit assumptions: ICP scope, deployment model, and whether AI/usage costs are material. If one of these assumptions is unknown, mark it as unresolved and lower confidence in final recommendations. Do not proceed with silent assumptions.

2. **Define segment map and buyer jobs.**  
   For each target segment, define the primary job-to-be-done, budget authority pattern, and expected maturity level. Your tiers must map to segment progression, not internal org chart labels. If two segments have different value drivers but are forced into one tier path, you create avoidable leakage and churn risk.

3. **Select monetization architecture and value metric.**  
   Start with a default architecture of 3 self-serve/mid-market tiers plus an enterprise path. Deviate only with explicit evidence. If customer value and cost-to-serve both scale with usage (common in AI-heavy workflows), use hybrid monetization (base fee plus usage/meter) unless evidence strongly supports another model. If value is stable and seat count tracks value, seat-led structure can remain primary.

4. **Build feature-role map before assigning tiers.**  
   Classify candidate features by monetization role: core adoption drivers, differentiation drivers, and premium controls. Then distribute features so each adjacent tier pair has meaningful progression. Do not build tiers by copying full product capability into top tier and trimming randomly; that pattern creates weak fences and poor self-selection.

5. **Design fences with explicit strength checks.**  
   Every adjacent tier transition must include: (a) one capability fence, (b) one usage fence, and (c) one commercial fence. Capability fence example: advanced governance/security controls. Usage fence example: included monthly processing volume. Commercial fence example: SLA/support entitlements. If any adjacent pair lacks this trio, revise before pricing.

6. **Derive price levels from evidence stack, not single method.**  
   Use PSM and direct WTP to define a defensible range, then refine with conjoint/choice evidence and behavioral test plans. PSM is boundary input, not final truth. For final price recommendation, include an evidence score that states whether behavior-based validation exists. If no behavioral signal exists yet, output a "provisional" price band and required validation experiment.

7. **Define upgrade triggers and buyer timeline.**  
   Map each trigger to observable behavior and expected timing: usage threshold reached, collaborator invited, governance requirement activated, or reporting/export demand. Each trigger must map from source tier to destination tier and include expected timeline assumptions. If trigger timing is unknown, specify what telemetry is needed to validate.

8. **Publish migration and governance plan with review cadence.**  
   Every tier recommendation must include migration treatment for existing customers, renewal cutover logic, and owner/review interval. Minimum cadence is annual; quarterly review is preferred in dynamic products. If migration plan is missing, the recommendation is incomplete and should not be finalized.
---

### Draft: Evidence policy and confidence scoring

---
### Price Point Derivation from WTP and Behavioral Signals

You must use an evidence stack with three layers:

1. **Boundary layer (stated preference):** PSM / direct WTP data to define floor/ceiling plausibility.
2. **Trade-off layer (choice modeling):** conjoint/CBC or equivalent to quantify willingness to trade features vs price.
3. **Behavior layer (observed behavior):** live experiment, pilot conversion, expansion, and retention signals.

If you only have layer 1, you may propose a provisional range but not a finalized point estimate. If you have layers 1 and 2 but no behavior layer, mark confidence as medium and require test plan before rollout. Finalized recommendations require either behavioral validation or a documented operational reason for deferral.

Use this confidence rubric:

- **High:** multi-method evidence including behavioral validation in target segment.
- **Medium:** multi-method stated-preference evidence with quality controls but no behavioral confirmation yet.
- **Low:** single-method stated preference or low-quality/contradictory data.

When sources conflict, do not silently average. Write a contradiction note and choose the conservative interpretation for rollout while defining what data would resolve the contradiction.
---

### Draft: Interpretation quality gates

---
### Data Interpretation Rules (Signal vs Noise)

Before accepting any pricing conclusion, enforce these rules:

1. **PSM quality gate:** validate response logic and segment fit before computing intersections. Invalid ordering responses and out-of-ICP respondents must be excluded from primary decision output.
2. **Conjoint adequacy gate:** do not report segment-level pricing conclusions unless subgroup sample sufficiency is met and per-level exposure is adequate for stable utilities.
3. **Experiment comparability gate:** normalize confidence/error assumptions across tools before comparing outcomes. You must not compare a 90% confidence "win" in one platform with a 95% confidence "non-win" in another without harmonization.
4. **Minimum evidence floor:** require both sample and conversion floors before declaring a winner. If platform thresholds differ, apply the stricter rule for pricing decisions because downside risk is asymmetric.
5. **Duration rule:** run at least one full business cycle and continue until pre-declared power targets are reached. "7 days complete" is not sufficient by itself.
6. **Peeking rule:** if results are checked continuously, use sequential testing methods and pre-declared stop logic. Otherwise review only at planned checkpoints.
7. **SRM hard stop:** if sample ratio mismatch is detected, block decisioning and diagnose instrumentation/routing before interpreting effects.
8. **Multi-metric readout:** do not optimize on conversion alone. Read conversion, revenue/ARPA, and retention/expansion together, segmented by ICP where possible.

If any gate fails, output must explicitly state "insufficient evidence for final price lock" and provide remediation actions.
---

### Draft: Feature fencing and upgrade trigger standards

---
### Feature Fencing Logic

Your fence design must create natural upgrade pressure without making lower tiers unusable.

For each adjacent tier pair:

- Include one **capability fence** (admin/security/analytics or other role-specific capability).
- Include one **usage fence** (projects/seats/transactions/credits or other value-aligned meter).
- Include one **commercial fence** (support SLA, onboarding, procurement terms, legal/security posture).

Weak fence patterns you must reject:

- Cosmetic differences only ("more of everything" without functional breakpoints).
- Arbitrary scarcity that does not correspond to value or cost.
- Core workflow crippled in lowest paid tier to force upgrade.

### Upgrade Trigger Design

Every trigger must include:

- `trigger_behavior` (what user does),
- `signal_metric` (what you observe),
- `threshold` (where action occurs),
- `from_tier` and `to_tier`,
- `expected_timeline`,
- `risk_if_ignored`.

Trigger types you should prioritize:

1. Usage threshold reached.
2. Collaboration/team workflow initiated.
3. Governance/compliance requirement appears.
4. Advanced reporting/export need appears.

If trigger relies on telemetry not currently instrumented, mark it as speculative and add instrumentation requirement.
---

### Draft: Anti-pattern warning blocks

---
### Warning: Tier Sprawl

**What it looks like:** You output more than four self-serve tiers with overlapping value propositions and no clean self-selection path.  
**Detection signal:** Multiple tiers target the same persona/job; feature matrix has high overlap and low unique value per step.  
**Consequence if missed:** Buyers stall at decision step, conversion falls, and sales receives avoidable qualification load.  
**Mitigation:** Reduce to a 3-4 tier default, force one-sentence tier identity per plan, and require non-overlapping progression rationale.

### Warning: Weak Adjacent Fences

**What it looks like:** Adjacent tiers differ by minor limits or UI conveniences rather than real capability, usage, and commercial distinctions.  
**Detection signal:** High-value users remain in lower tiers while consuming meaningful value; repeated package edits occur to patch leakage.  
**Consequence if missed:** Revenue leakage and abrupt repricing pressure later.  
**Mitigation:** Enforce capability+usage+commercial fence checks for every adjacent pair before output approval.

### Warning: Seat-Only Metric Misfit

**What it looks like:** Pricing remains seat-only while customer value and cost-to-serve scale with usage/automation.  
**Detection signal:** Value metrics rise without seat growth; margins compress due to unpriced usage.  
**Consequence if missed:** Under-monetization and worsening gross margin profile.  
**Mitigation:** Introduce hybrid base+usage component, plus spend predictability controls.

### Warning: Metered Billing Without Safety Controls

**What it looks like:** Overage-only design with no alerts, no cap policy, and no committed usage option.  
**Detection signal:** Users discover overages only at invoice; disputes rise.  
**Consequence if missed:** Bill shock, trust damage, and renewal risk.  
**Mitigation:** Require alert thresholds, cap behavior, overage policy clarity, and optional committed tier.

### Warning: Repricing Without Migration Policy

**What it looks like:** New prices/features published without explicit old->new mapping and renewal cutover rules.  
**Detection signal:** Support/sales cannot answer "who changes when and to what terms."  
**Consequence if missed:** Escalations, inconsistent exceptions, and churn spikes.  
**Mitigation:** Include migration cohort map, grandfathering window, entitlement diff, and communication checkpoints.
---

### Draft: Available Tools section (updated, paste-ready)

---
## Available Tools

Use internal strategy documents first, then write one structured artifact. Do not invent external API calls inside this skill.

```python
flexus_policy_document(op="activate", args={"p": "/strategy/pricing-model"})
flexus_policy_document(op="activate", args={"p": "/strategy/offer-design"})
flexus_policy_document(op="list", args={"p": "/pain/"})
```

Usage rules:

1. Always activate pricing-model and offer-design documents before deriving any tier.
2. Always list `/pain/` and consume the most relevant WTP evidence artifacts before setting price levels.
3. If WTP evidence is missing or low quality, output provisional ranges and include a required validation step.

Write the final output as:

```python
write_artifact(
    artifact_type="pricing_tier_structure",
    path="/strategy/pricing-tiers",
    data={...},
)
```
---

### Draft: Schema additions

Use this JSON Schema fragment to extend and tighten `pricing_tier_structure`:

```json
{
  "pricing_tier_structure": {
    "type": "object",
    "required": [
      "created_at",
      "currency",
      "billing_period",
      "methodology_version",
      "confidence",
      "evidence_stack",
      "tiers",
      "upgrade_triggers",
      "wtp_anchoring",
      "usage_safety",
      "migration_plan",
      "pricing_governance"
    ],
    "additionalProperties": false,
    "properties": {
      "created_at": {
        "type": "string",
        "description": "ISO-8601 timestamp when this tier design artifact was generated."
      },
      "currency": {
        "type": "string",
        "description": "ISO currency code used for all monetary values in this artifact."
      },
      "billing_period": {
        "type": "string",
        "enum": ["monthly", "annually", "one_time", "per_seat_monthly"],
        "description": "Primary billing cadence used for displayed plan prices."
      },
      "methodology_version": {
        "type": "string",
        "description": "Version tag of the pricing-tier methodology applied (for auditability and future comparisons)."
      },
      "confidence": {
        "type": "object",
        "required": ["overall", "reason", "contradictions_noted"],
        "additionalProperties": false,
        "properties": {
          "overall": {
            "type": "string",
            "enum": ["high", "medium", "low"],
            "description": "Overall confidence score based on evidence quality and behavioral validation depth."
          },
          "reason": {
            "type": "string",
            "description": "Narrative reason explaining why this confidence level was assigned."
          },
          "contradictions_noted": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "List of unresolved source or signal contradictions that influenced confidence."
          }
        }
      },
      "evidence_stack": {
        "type": "object",
        "required": ["boundary_methods", "tradeoff_methods", "behavior_methods", "sources"],
        "additionalProperties": false,
        "properties": {
          "boundary_methods": {
            "type": "array",
            "items": {
              "type": "string",
              "enum": ["psm", "direct_wtp_closed", "direct_wtp_open", "gabor_granger", "other"]
            },
            "description": "Methods used to set plausible price boundaries."
          },
          "tradeoff_methods": {
            "type": "array",
            "items": {
              "type": "string",
              "enum": ["cbc_conjoint", "choice_modeling", "none", "other"]
            },
            "description": "Methods used to estimate trade-offs between price and feature bundles."
          },
          "behavior_methods": {
            "type": "array",
            "items": {
              "type": "string",
              "enum": ["ab_test", "pilot_offer", "historical_conversion", "historical_expansion", "none", "other"]
            },
            "description": "Observed behavioral data sources used for validation."
          },
          "sources": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Source IDs or URLs tied to the evidence methods."
          }
        }
      },
      "tiers": {
        "type": "array",
        "minItems": 2,
        "items": {
          "type": "object",
          "required": [
            "tier_name",
            "target_persona",
            "not_for_persona",
            "price",
            "price_unit",
            "value_metric",
            "key_limits",
            "key_features",
            "feature_gates",
            "fence_strength"
          ],
          "additionalProperties": false,
          "properties": {
            "tier_name": {
              "type": "string",
              "description": "Customer-facing plan name."
            },
            "target_persona": {
              "type": "string",
              "description": "Primary persona or segment this tier is designed for."
            },
            "not_for_persona": {
              "type": "string",
              "description": "Persona segment this tier is intentionally not optimized for."
            },
            "price": {
              "type": "number",
              "minimum": 0,
              "description": "Displayed plan price in the artifact currency."
            },
            "price_unit": {
              "type": "string",
              "description": "Commercial unit for the listed price (for example per month, per seat, per 1k events)."
            },
            "value_metric": {
              "type": "string",
              "description": "Primary metric that best maps monetization to customer value creation."
            },
            "key_limits": {
              "type": "object",
              "additionalProperties": {
                "type": ["string", "number", "boolean"]
              },
              "description": "Machine-readable usage and capability limits that define this tier boundary."
            },
            "key_features": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "Most important included features for this tier."
            },
            "feature_gates": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "Features intentionally reserved for higher tiers."
            },
            "fence_strength": {
              "type": "object",
              "required": ["capability_fence", "usage_fence", "commercial_fence"],
              "additionalProperties": false,
              "properties": {
                "capability_fence": {
                  "type": "string",
                  "description": "Primary capability progression to next tier."
                },
                "usage_fence": {
                  "type": "string",
                  "description": "Primary usage progression to next tier."
                },
                "commercial_fence": {
                  "type": "string",
                  "description": "Primary commercial/procurement progression to next tier."
                }
              }
            }
          }
        }
      },
      "upgrade_triggers": {
        "type": "array",
        "items": {
          "type": "object",
          "required": [
            "trigger",
            "signal_metric",
            "threshold",
            "from_tier",
            "to_tier",
            "expected_timeline"
          ],
          "additionalProperties": false,
          "properties": {
            "trigger": {
              "type": "string",
              "description": "Behavioral event that indicates upgrade intent or need."
            },
            "signal_metric": {
              "type": "string",
              "description": "Tracked metric used to detect the trigger."
            },
            "threshold": {
              "type": "string",
              "description": "Concrete threshold or condition that activates the trigger."
            },
            "from_tier": {
              "type": "string",
              "description": "Current tier before upgrade."
            },
            "to_tier": {
              "type": "string",
              "description": "Recommended destination tier."
            },
            "expected_timeline": {
              "type": "string",
              "description": "Expected time window in which this trigger appears for typical users."
            }
          }
        }
      },
      "wtp_anchoring": {
        "type": "object",
        "required": ["psm_optimal", "psm_stress_point", "applied_discount"],
        "additionalProperties": false,
        "properties": {
          "psm_optimal": {
            "type": "number",
            "description": "PSM-derived central reference point used as initial boundary input."
          },
          "psm_stress_point": {
            "type": "number",
            "description": "Upper stress boundary from PSM or equivalent WTP boundary method."
          },
          "applied_discount": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Calibration factor applied to stated-preference values before behavioral validation."
          }
        }
      },
      "usage_safety": {
        "type": "object",
        "required": ["alerts_enabled", "alert_thresholds", "hard_cap_policy", "overage_policy", "committed_usage_option"],
        "additionalProperties": false,
        "properties": {
          "alerts_enabled": {
            "type": "boolean",
            "description": "Whether proactive usage alerts are designed into the pricing experience."
          },
          "alert_thresholds": {
            "type": "array",
            "items": {
              "type": "number",
              "minimum": 0,
              "maximum": 1
            },
            "description": "Fractional usage checkpoints (for example 0.8, 0.9, 1.0) that trigger customer notifications."
          },
          "hard_cap_policy": {
            "type": "string",
            "enum": ["none", "soft_cap_with_overage", "hard_stop", "grace_then_stop"],
            "description": "Behavior when included usage is exhausted."
          },
          "overage_policy": {
            "type": "string",
            "description": "How overage is billed and communicated."
          },
          "committed_usage_option": {
            "type": "boolean",
            "description": "Whether customers can choose committed/prepaid usage for predictability."
          }
        }
      },
      "migration_plan": {
        "type": "object",
        "required": ["required", "grandfathering_policy", "renewal_cutover_rule", "entitlement_mapping_status", "customer_comms_checkpoints"],
        "additionalProperties": false,
        "properties": {
          "required": {
            "type": "boolean",
            "description": "Whether migration handling is required for this tier redesign."
          },
          "grandfathering_policy": {
            "type": "string",
            "description": "Policy for maintaining old terms for existing customers during transition."
          },
          "renewal_cutover_rule": {
            "type": "string",
            "description": "Rule defining when existing contracts move to new pricing/package terms."
          },
          "entitlement_mapping_status": {
            "type": "string",
            "enum": ["defined", "partial", "missing"],
            "description": "Completeness status of old-tier to new-tier entitlement mapping."
          },
          "customer_comms_checkpoints": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Named communication milestones before and during migration."
          }
        }
      },
      "pricing_governance": {
        "type": "object",
        "required": ["owner", "review_interval", "next_review_due", "exception_process"],
        "additionalProperties": false,
        "properties": {
          "owner": {
            "type": "string",
            "description": "Function or role accountable for ongoing tier health and updates."
          },
          "review_interval": {
            "type": "string",
            "enum": ["quarterly", "semi_annual", "annual"],
            "description": "Scheduled interval for pricing/package health review."
          },
          "next_review_due": {
            "type": "string",
            "description": "ISO-8601 date for next planned review."
          },
          "exception_process": {
            "type": "string",
            "description": "How exceptions and discount deviations are approved and logged."
          }
        }
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Public 2025-2026 data on AI add-on attach rates and hybrid model performance is still heavily concentrated in consulting/vendor datasets rather than peer-reviewed longitudinal datasets.
- Vendor documentation for limits/pricing (Stripe, Paddle, PostHog, Statsig, etc.) changes frequently; any production implementation should re-validate exact numbers before enforcement.
- Some experimentation-platform documentation differs from pricing-page language (for example free-tier quota details), so quota-specific guidance should be treated as environment-verified, not static truth.
- There is limited public causal evidence isolating tier naming impact independent of other page/design changes; naming guidance remains strongly practice-based rather than experimentally universal.
- Older foundational references used here are explicitly marked evergreen, but newer replication studies would improve confidence on method-level quantitative assumptions.
