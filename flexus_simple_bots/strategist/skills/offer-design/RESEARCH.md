# Research: offer-design

**Skill path:** `strategist/skills/offer-design/`  
**Bot:** strategist (researcher | strategist | executor)  
**Research date:** 2026-03-05  
**Status:** complete

---

## Context

`offer-design` defines what customers actually receive: package structure, tier boundaries, explicit exclusions, and version/migration logic. It is the bridge between positioning and pricing.

The existing `SKILL.md` has good fundamentals (JTBD focus, feature categorization, packaging options), but 2024-2026 evidence shows the skill should include explicit controls for predictability, migration safety, interpretation quality, and trust/compliance constraints.

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
- No invented tool names, method IDs, or API endpoints - only verified real ones: **passed**
- Contradictions between sources are explicitly noted, not silently resolved: **passed**
- Findings sections are within 800-4000 words combined: **passed**
- `Draft Content for SKILL.md` is the largest section and paste-ready: **passed**

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

Offer design has shifted from annual tier refreshes to ongoing monetization operations. 2024-2026 sources show faster packaging iteration because AI-related costs and buyer expectations move quickly [M1][M4][M5].

The most practical sequence starts with value/cost/mission triage before tiers are written:
1. Value distribution by segment and persona.
2. Cost variability to serve each capability.
3. Mission role of each capability (core vs adjacent) [M1][M4].

Teams that skip this triage tend to over-bundle expensive capabilities into baseline plans or over-fragment with excessive add-ons.

Tier boundaries are increasingly workflow- and control-oriented, not feature-count-oriented. Better packages map to coherent job outcomes plus governance depth [M4][M6].

Hybrid structures are common in practice because they reconcile buyer predictability with vendor value capture (recurring anchor + variable expansion) [M3][M5][M8].

Outcome-based charging remains attractive but requires auditable outcome definitions and dispute-handling policies; otherwise execution risk erodes gains [M2][M4].

Migration design is now a first-class methodology step: cohort transitions, grandfathering windows, rollback triggers, and explicit customer communication plans [M4][M5][M7].

**Contradictions to preserve in skill logic:**
- Outcome-oriented pricing momentum vs enterprise predictability preferences -> resolved by bounded hybrid structures [M2][M3][M4].
- Bundle AI by default vs monetize AI separately -> resolved by value breadth, cost profile, and mission role [M1][M6][M8].

**Sources:**
- [M1] Andreessen Horowitz, "Pricing and Packaging Your B2B or Prosumer Generative AI Feature" (2024): https://a16z.com/pricing-packaging-ai-b2b-prosumer/
- [M2] Andreessen Horowitz, "AI Is Driving A Shift Towards Outcome-Based Pricing" (2024): https://a16z.com/newsletter/december-2024-enterprise-newsletter-ai-is-driving-a-shift-towards-outcome-based-pricing
- [M3] Andreessen Horowitz, "Customers Want Predictability in Usage-based Pricing..." (2024): https://a16z.com/customers-want-predictability-in-usage-based-pricing-heres-how-to-help-them-get-it/
- [M4] BCG, "Rethinking B2B Software Pricing in the Agentic AI Era" (2025): https://www.bcg.com/publications/2025/rethinking-b2b-software-pricing-in-the-era-of-ai
- [M5] Metronome, "State of Usage-Based Pricing 2025" (2025): https://metronome.com/state-of-usage-based-pricing-2025
- [M6] Bessemer, "The AI Pricing and Monetization Playbook" (2025): https://www.bvp.com/atlas/the-ai-pricing-and-monetization-playbook
- [M7] SBI / Price Intelligently, "State of B2B SaaS Pricing in 2024" (2024): https://sbigrowth.com/tools-and-solutions/pricing-benchmarks-report-2024
- [M8] Stripe, "The pricing model dilemma..." (2024): https://stripe.com/blog/the-pricing-model-dilemma-according-to-2000-subscription-business-leaders

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

Offer design execution requires synchronized billing catalog, entitlements, rollout controls, and analytics. Most practical failures are cross-layer consistency failures, not missing APIs [T1][T6][T11][T14][T17].

**Stripe** endpoints commonly used for package operations:
- `POST /v1/products`
- `POST /v1/prices`
- `GET /v1/entitlements/active_entitlements`
- `POST /v1/subscription_schedules`

**Paddle** endpoints commonly used for package operations:
- `POST https://api.paddle.com/products`
- `POST https://api.paddle.com/prices`
- `GET https://api.paddle.com/prices`
- `PATCH https://api.paddle.com/subscriptions/{subscription_id}/preview`

**Chargebee** endpoints commonly used for package operations:
- `POST https://{site}.chargebee.com/api/v2/items`
- `POST https://{site}.chargebee.com/api/v2/item_prices`
- `POST https://{site}.chargebee.com/api/v2/customers/{customer-id}/subscription_for_items`

**LaunchDarkly** endpoints for rollout/control:
- `GET /api/v2/flags/{projectKey}/{key}`
- `PATCH /api/v2/flags/{projectKey}/{key}`

**Amplitude** ingestion endpoints:
- `POST https://api2.amplitude.com/2/httpapi`
- `POST https://api2.amplitude.com/batch`

Operational implications to encode in skill behavior:
1. Maintain one canonical `offer_version_id` across all systems.
2. Treat 429 handling as expected control flow.
3. Avoid in-place mutable package edits; version intentionally.
4. Validate telemetry reliability before interpreting package experiments.

**Sources:**
- [T1] Stripe API docs, "Create a product" (**Evergreen**): https://docs.stripe.com/api/products/create
- [T2] Stripe API docs, "Create a price" (**Evergreen**): https://docs.stripe.com/api/prices/create
- [T3] Stripe API docs, "List all active entitlements" (**Evergreen**): https://docs.stripe.com/api/entitlements/active-entitlement/list
- [T4] Stripe API docs, "Create a schedule" (**Evergreen**): https://docs.stripe.com/api/subscription_schedules/create
- [T5] Stripe docs, "Rate limits" (**Evergreen**): https://docs.stripe.com/rate-limits
- [T6] Paddle docs, "Create a product" (**Evergreen**): https://developer.paddle.com/api-reference/products/create-product
- [T7] Paddle docs, "Create a price" (**Evergreen**): https://developer.paddle.com/api-reference/prices/create-price
- [T8] Paddle docs, "List prices" (**Evergreen**): https://developer.paddle.com/api-reference/prices/list-prices
- [T9] Paddle docs, "Preview an update to a subscription" (**Evergreen**): https://developer.paddle.com/api-reference/subscriptions/preview-subscription
- [T10] Paddle docs, "Rate limiting" (**Evergreen**): https://developer.paddle.com/api-reference/about/rate-limiting
- [T11] Chargebee API docs, "Create an item" (**Evergreen**): https://apidocs.chargebee.com/docs/api/items/create-an-item
- [T12] Chargebee API docs, "Create an item price" (**Evergreen**): https://apidocs.chargebee.com/docs/api/item_prices/create-an-item-price
- [T13] Chargebee docs, API limits (**Evergreen**): https://www.chargebee.com/docs/billing/2.0/kb/platform/what-are-the-chargebee-api-limits
- [T14] LaunchDarkly REST API guide (**Evergreen**): https://docs.launchdarkly.com/guides/api/rest-api/
- [T15] LaunchDarkly API docs overview (**Evergreen**): https://apidocs.launchdarkly.com/
- [T16] LaunchDarkly API migration guide (2024): https://launchdarkly.com/docs/guides/api/api-migration-guide
- [T17] Amplitude docs, HTTP V2 API (2024-2026 active docs): https://amplitude.com/docs/apis/analytics/http-v2
- [T18] Amplitude docs, Batch Event Upload API (2024-2026 active docs): https://amplitude.com/docs/apis/analytics/batch-event-upload

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

Interpretation quality starts with cohort discipline. Retention benchmarks vary significantly by segment/ACV context, so package decisions should not be based on universal thresholds [D1][D2].

NRR and GRR should always be interpreted together. NRR can remain healthy while GRR deterioration reveals leakage and boundary mismatch [D1][D2][D12].

Feature interaction is concentrated, so tier logic should align to high-value behavior clusters rather than equalizing feature count [D3][D4].

Churn should be decomposed (voluntary vs involuntary) before intervention selection. Otherwise teams may misdiagnose payment-operations issues as package-fit issues [D5][D6].

Buying-process complexity can obscure package quality signals; stage-specific interpretation is necessary [D7][D8].

SRM validity checks should be mandatory when experiment outputs drive package changes [D10][D11].

**Sources:**
- [D1] SaaS Capital retention benchmarks (2025): https://www.saas-capital.com/research/saas-retention-benchmarks-for-private-b2b-companies/
- [D2] SaaS Capital bootstrapped metrics (2025): https://www.saas-capital.com/blog-posts/benchmarking-metrics-for-bootstrapped-saas-companies/
- [D3] Pendo feature adoption benchmark (2024): https://www.pendo.io/pendo-blog/feature-adoption-benchmarking/
- [D4] Pendo enterprise product benchmarks (2024): https://www.pendo.io/pendo-blog/enterprise-product-benchmarks/
- [D5] Churnkey voluntary churn benchmark (2025): https://churnkey.co/blog/voluntary-churn-benchmarks/
- [D6] Churnkey involuntary churn benchmark (2025): https://churnkey.co/blog/involuntary-churn-benchmarks/
- [D7] Forrester State of Business Buying 2024 (2024): https://www.forrester.com/press-newsroom/forrester-the-state-of-business-buying-2024/
- [D8] Common Paper Contract Benchmark Q1 2024 (2024): https://commonpaper.com/resources/contract-benchmark-2024-q1/
- [D9] GrowthBook experiment decision framework (**Evergreen**): https://docs.growthbook.io/app/experiment-decisions
- [D10] Harness sample ratio check (**Evergreen**): https://developer.harness.io/docs/feature-management-experimentation/experimentation/experiment-results/analyzing-experiment-results/sample-ratio-check
- [D11] Microsoft ExP diagnosing SRM (**Evergreen methodology**): https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/
- [D12] Stripe net revenue retention resource (**Evergreen**): https://stripe.com/resources/more/net-revenue-retention
- [D13] BMJ pilot sample size tutorial (2025): https://www.bmj.com/content/390/bmj-2024-083405

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

Common anti-patterns (2024-2026 evidence):

1. **Metric whiplash** - abrupt metric shifts without transition support.
2. **Forced rebundling** - reducing modularity during migration.
3. **Hidden material terms** - poor visibility of cancellation/termination implications.
4. **Cancellation asymmetry** - easy signup, difficult cancellation.
5. **Big-bang migration** - full cutover before parity confidence.
6. **No rollback path** - no controlled retreat if launch quality drops.
7. **Low-context communication** - weak migration rationale and examples.
8. **Grandfathering ambiguity** - unclear treatment of existing cohorts.
9. **Fairness/portability blind spots** - terms perceived as anti-choice.

For each warning in skill output, include: what it looks like, detection signal, consequence, and mitigation.

**Sources:**
- [F1] Unity runtime-fee cancellation support post (2024): https://support.unity.com/hc/en-us/articles/30322080156692-Cancellation-of-the-Runtime-Fee-and-Pricing-Changes/
- [F2] Reuters Unity pricing rollback coverage (2024): https://www.reuters.com/technology/unity-software-scraps-runtime-fee-pricing-policy-introduces-price-hikes-2024-09-12/
- [F3] FTC Adobe subscription allegations press release (2024): https://www.ftc.gov/news-events/news/press-releases/2024/06/ftc-takes-action-against-adobe-executives-hiding-fees-preventing-consumers-easily-cancelling
- [F4] Reuters Adobe lawsuit coverage (2024): https://www.reuters.com/technology/us-sues-adobe-over-subscription-plan-disclosures-2024-06-17/
- [F5] Sonos app update statement (2024): https://www.sonos.com/en-us/blog/update-on-the-sonos-app
- [F6] Reuters Sonos app failure coverage (2024): https://www.reuters.com/technology/sonos-ceo-promises-reforms-after-may-app-release-failure-leaders-forgo-bonuses-2024-10-01/
- [F7] Reuters Broadcom/VMware licensing scrutiny (2024): https://www.reuters.com/technology/broadcom-questioned-by-eu-over-vmware-licensing-changes-2024-04-15/
- [F8] Reuters Broadcom licensing criticism coverage (2024): https://www.reuters.com/technology/broadcoms-critics-reject-its-cloud-licensing-changes-2024-04-22/
- [F9] Reuters CISPE legal challenge coverage (2025): https://www.reuters.com/legal/litigation/europes-cispe-challenges-broadcoms-69-billion-vmware-deal-eu-court-2025-07-24/
- [F10] TechCrunch Canva Teams pricing coverage (2024): https://techcrunch.com/2024/09/03/canva-has-increased-prices-for-its-teams-product/
- [F11] The Verge Canva walkback coverage (2024): https://www.theverge.com/2024/10/9/24266269/canva-is-walking-back-some-of-its-pricing-changes
- [F12] FTC click-to-cancel fact sheet (2024): https://www.ftc.gov/system/files/ftc_gov/pdf/NegOptions-1page-Oct2024-v2.pdf
- [F13] FTC click-to-cancel business guidance (2024): https://www.ftc.gov/business-guidance/blog/2024/10/click-cancel-ftcs-amended-negative-option-rule-what-it-means-your-business

---

### Angle 5+: Regulatory, Trust, and Governance Constraints
> Additional domain-specific angle: recurring-subscription and AI governance requirements that affect package architecture and migration design.

**Findings:**

Recurring package design now has direct cancellation/disclosure risk implications. FTC click-to-cancel direction strengthens expectations around cancellation parity and recurring-term clarity [G1][G2].

EU GPAI obligations began applying in 2025. AI tier claims should map to operational governance reality, not marketing-only claims [G3][G4].

NIST GenAI profile guidance is increasingly used in enterprise trust conversations and should inform AI-tier transparency expectations [G5].

UK DMCCA subscription provisions reinforce multi-jurisdiction pressure for clearer recurring terms and cancellation behavior [G6].

**Sources:**
- [G1] FTC final click-to-cancel press release (2024): https://www.ftc.gov/news-events/news/press-releases/2024/10/federal-trade-commission-announces-final-click-cancel-rule-making-it-easier-consumers-end-recurring
- [G2] FTC business guidance (2024): https://www.ftc.gov/business-guidance/blog/2024/10/click-cancel-ftcs-amended-negative-option-rule-what-it-means-your-business
- [G3] European Commission GPAI provider guidelines (2025): https://digital-strategy.ec.europa.eu/en/policies/guidelines-gpai-providers
- [G4] European Commission GPAI obligations start notice (2025): https://digital-strategy.ec.europa.eu/en/news/eu-rules-general-purpose-ai-models-start-apply-tomorrow-bringing-more-transparency-safety-and
- [G5] NIST AI RMF GenAI profile (2024): https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
- [G6] UK DMCCA 2024 subscription provisions: https://www.legislation.gov.uk/ukpga/2024/13/part/4/chapter/2

---

## Synthesis

Offer design now behaves like a recurring operations function, not a one-time pricing artifact. Quality depends on coupling methodology, tooling, interpretation, and migration trust controls.

The most persistent contradiction is strategic value-alignment versus buyer predictability. In practice, hybrid structures with explicit guardrails often resolve this tension.

The most expensive failure modes are migration and trust failures, not isolated pricing math mistakes. This is why `SKILL.md` should require migration policy, quality gates, confidence labels, and anti-pattern checks before writing artifacts.

---

## Recommendations for SKILL.md

- [x] Add a required offer-design operating loop (triage -> model choice -> tier boundary -> predictability -> migration -> interpretation -> review cadence).
- [x] Add explicit packaging-model if/then decision logic.
- [x] Require tier outputs to include inclusions, exclusions, and key limits.
- [x] Add mandatory predictability controls for variable charging.
- [x] Add mandatory migration policy fields (effective date, cohorts, grandfathering, rollback, communication).
- [x] Add interpretation quality gates (segment normalization, NRR+GRR, churn decomposition, SRM checks).
- [x] Add confidence labeling and unresolved-assumption handling.
- [x] Expand anti-pattern blocks with detection signals and mitigation.
- [x] Update tool-usage guidance to force evidence activation before package writing.
- [x] Expand artifact schema to include evidence logs and trust/compliance checks.

---

## Draft Content for SKILL.md

> This section is intentionally the largest and paste-ready.

### Draft: Core mode

---
### Core mode

You design offers as operational systems, not static feature bundles. A valid offer recommendation is one that buyers can understand, operations can execute, and teams can migrate safely.

Before finalizing any offer recommendation, verify:
1. One target segment and one primary job are explicit.
2. Cost variability of key capabilities is known or explicitly assumed.
3. Migration and cancellation implications are explicitly addressed.

If one of these is missing, lower confidence and publish unresolved assumptions.
---

### Draft: Methodology

---
### Methodology

Use this required sequence for every `offer-design` output:

1. **Activate context artifacts first**
   - Load messaging, positioning, segment scorecard, and pain/WTP evidence.
   - If critical evidence is missing, write assumptions and confidence impact.

2. **Run value-cost-mission triage**
   - Classify each capability by value breadth, cost variability, and mission role.
   - Use this to decide `core`, `value_add`, or `segment_specific`.

3. **Select packaging model with if/then logic**
   - `good_better_best`: clear maturity segmentation and self-serve clarity.
   - `base_modules`: high workflow variance and enterprise tailoring.
   - `single_with_volume`: stable core value and clear scaling dimension.
   - `freemium`: only when free-tier economics and conversion path are controlled.
   - `single_offer`: only when segment and workflow variance are low.

4. **Define tier boundaries by workflow coherence**
   - Each tier must represent a coherent job outcome, not list-size inflation.
   - Each tier must include explicit inclusions, exclusions, and key limits.

5. **Add predictability controls**
   - Allowance design, overage policy, visibility surface, alert policy, budget owner.
   - If variable charging exists and spend is not forecastable, return `needs_rework`.

6. **Add migration policy before launch recommendation**
   - Effective date, cohort plan, grandfathering, rollback triggers, communication plan.
   - No migration recommendation is valid without these fields.

7. **Run interpretation quality gates**
   - Segment-normalized benchmark check.
   - NRR + GRR co-read.
   - Voluntary/involuntary churn split.
   - SRM validity checks for experiment-based conclusions.
   - Confidence label + unresolved assumptions.

8. **Publish version notes and review cadence**
   - Explicitly separate current version vs roadmap.
   - Set default review cadence and out-of-cycle triggers.

Do NOT:
- Propose packages without exclusions.
- Recommend migration without rollback triggers.
- Treat NRR alone as sufficient package evidence.
- Ignore experiment validity failures.
---

### Draft: Tier writing standard

---
### Tier writing standard

For each tier you must provide:
- `tier_name`
- `target_persona`
- `core_job_served`
- `included_features`
- `excluded_features`
- `key_limits`
- `upgrade_triggers`

Rules:
1. Adjacent tiers differ by workflow depth/control, not cosmetic feature count.
2. Every tier has at least one explicit exclusion and one explicit limit.
3. Upgrade triggers must reference observable usage conditions.
4. If a capability moves up-tier, migration policy must define treatment for existing cohorts.
---

### Draft: Predictability and migration controls

---
### Predictability controls

Required object:
- allowance design
- overage policy
- visibility surface
- alert policy
- budget owner

If this object cannot explain how customers forecast spend, the recommendation is incomplete.

### Migration policy

Required object:
- effective date
- cohort plan
- grandfathering policy
- rollback triggers
- communication plan

If migration policy is missing, confidence cannot exceed `medium`.
---

### Draft: Interpretation policy

---
### Evidence interpretation policy

Before final recommendation:

1. Normalize benchmarks by segment/ACV context.
2. Evaluate NRR and GRR together.
3. Split churn into voluntary and involuntary causes.
4. Require SRM/allocation validity for experiment-based conclusions.
5. Assign confidence (`high`, `medium`, `low`) with reasons.
6. Record unresolved assumptions and their confidence impact.

Block these misreads:
- "NRR > 100 means healthy package."
- "Top-funnel lift proves package quality."
- "Single churn number implies one fix."
- "Roughly balanced traffic implies valid experiment."
---

### Draft: Anti-pattern warning blocks

---
### Warning: Metric Whiplash
**What it looks like:** abrupt billing-metric change without transition support.  
**Detection signal:** forecast confusion and renewal friction.  
**Consequence:** trust shock and rollback pressure.  
**Mitigation:** parallel-run metrics and stage migration.

### Warning: Forced Rebundling
**What it looks like:** modular options removed during migration.  
**Detection signal:** lock-in objections and conversion friction.  
**Consequence:** slower adoption and higher scrutiny risk.  
**Mitigation:** transitional options and explicit entitlement mapping.

### Warning: Hidden Material Terms
**What it looks like:** cancellation/termination implications are low-visibility.  
**Detection signal:** surprise-fee disputes.  
**Consequence:** enforcement/litigation/refund risk.  
**Mitigation:** plain-language key-terms disclosure adjacent to consent.

### Warning: Big-bang Migration
**What it looks like:** full cutover before parity confidence.  
**Detection signal:** severe post-launch incidents.  
**Consequence:** expensive remediation and trust damage.  
**Mitigation:** phased cohorts, parity checklist, rollback triggers.

### Warning: Grandfathering Ambiguity
**What it looks like:** unclear existing-customer rights and timing.  
**Detection signal:** inconsistent support answers and exception growth.  
**Consequence:** churn pressure and trust erosion.  
**Mitigation:** dated grandfather matrix per cohort.
---

### Draft: Input/Tools/Recording sections

---
## Input artifacts to load

```python
flexus_policy_document(op="activate", args={"p": "/strategy/messaging"})
flexus_policy_document(op="activate", args={"p": "/strategy/positioning-map"})
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})
flexus_policy_document(op="list", args={"p": "/pain/"})
flexus_policy_document(op="activate", args={"p": "/pain/wtp-research-{date}"})
```

## Available Tools

```python
flexus_policy_document(op="activate", args={"p": "/strategy/messaging"})
flexus_policy_document(op="activate", args={"p": "/strategy/positioning-map"})
flexus_policy_document(op="list", args={"p": "/pain/"})
```

Tool rules:
1. Activate context before package design.
2. Do not finalize boundaries from memory-only assumptions.
3. Record unresolved assumptions in artifact output.

## Recording

```python
write_artifact(
    artifact_type="offer_design",
    path="/strategy/offer-design",
    data={...},
)
```

Before writing:
- verify packaging rationale
- verify tier inclusions/exclusions/limits
- verify predictability controls
- verify migration policy
- verify confidence and unresolved assumptions
---

### Draft: Artifact Schema additions

```json
{
  "offer_design": {
    "type": "object",
    "required": [
      "product_name",
      "created_at",
      "method_version",
      "target_segment",
      "primary_job",
      "packaging_model",
      "packaging_rationale",
      "tiers",
      "core_features",
      "exclusions",
      "predictability_controls",
      "migration_policy",
      "interpretation_policy",
      "evidence_log",
      "anti_patterns_checked",
      "trust_compliance_checks",
      "version_notes",
      "confidence",
      "unresolved_assumptions"
    ],
    "additionalProperties": false,
    "properties": {
      "product_name": { "type": "string", "description": "Offer name." },
      "created_at": { "type": "string", "description": "ISO-8601 UTC timestamp." },
      "method_version": { "type": "string", "enum": ["offer_design_v2_2026"], "description": "Method version." },
      "target_segment": { "type": "string", "description": "Primary segment." },
      "primary_job": { "type": "string", "description": "Primary job-to-be-done." },
      "packaging_model": {
        "type": "string",
        "enum": ["good_better_best", "base_modules", "single_with_volume", "freemium", "single_offer"],
        "description": "Chosen package architecture."
      },
      "packaging_rationale": {
        "type": "object",
        "required": ["value_distribution", "cost_variability", "mission_role", "chosen_for", "rejected_options"],
        "additionalProperties": false,
        "properties": {
          "value_distribution": { "type": "string", "enum": ["broad", "mixed", "concentrated"], "description": "How widely value is distributed." },
          "cost_variability": { "type": "string", "enum": ["low", "medium", "high"], "description": "Cost-to-serve variability." },
          "mission_role": { "type": "string", "enum": ["core_mission", "adjacent_enhancement", "experimental_extension"], "description": "Role in product promise." },
          "chosen_for": { "type": "array", "items": { "type": "string" }, "description": "Reasons selected model is appropriate." },
          "rejected_options": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["model", "reason_rejected"],
              "additionalProperties": false,
              "properties": {
                "model": { "type": "string", "enum": ["good_better_best", "base_modules", "single_with_volume", "freemium", "single_offer"], "description": "Alternative model considered." },
                "reason_rejected": { "type": "string", "description": "Why alternative was rejected." }
              }
            },
            "description": "Alternatives evaluated during model selection."
          }
        }
      },
      "tiers": {
        "type": "array",
        "minItems": 1,
        "maxItems": 5,
        "items": {
          "type": "object",
          "required": ["tier_name", "target_persona", "core_job_served", "included_features", "excluded_features", "key_limits", "upgrade_triggers"],
          "additionalProperties": false,
          "properties": {
            "tier_name": { "type": "string", "description": "Tier label." },
            "target_persona": { "type": "string", "description": "Primary persona for tier." },
            "core_job_served": { "type": "string", "description": "Workflow outcome this tier completes." },
            "included_features": { "type": "array", "items": { "type": "string" }, "description": "Capabilities included." },
            "excluded_features": { "type": "array", "items": { "type": "string" }, "description": "Capabilities excluded." },
            "key_limits": { "type": "object", "additionalProperties": true, "description": "Usage limits." },
            "upgrade_triggers": { "type": "array", "items": { "type": "string" }, "description": "Observable upgrade signals." }
          }
        },
        "description": "Ordered tier definitions."
      },
      "core_features": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["feature", "category", "rationale"],
          "additionalProperties": false,
          "properties": {
            "feature": { "type": "string", "description": "Capability name." },
            "category": { "type": "string", "enum": ["core", "value_add", "segment_specific"], "description": "Capability category." },
            "rationale": { "type": "string", "description": "Evidence-based categorization rationale." }
          }
        },
        "description": "Capability categorization for package design."
      },
      "exclusions": { "type": "array", "items": { "type": "string" }, "description": "Global exclusions." },
      "predictability_controls": {
        "type": "object",
        "required": ["allowance_design", "overage_policy", "visibility_surface", "alert_policy", "budget_owner"],
        "additionalProperties": false,
        "properties": {
          "allowance_design": { "type": "string", "description": "Included quantity/unit design." },
          "overage_policy": { "type": "string", "description": "Behavior when allowance exceeded." },
          "visibility_surface": { "type": "string", "description": "Where usage/spend is shown." },
          "alert_policy": { "type": "string", "description": "Alert thresholds and recipients." },
          "budget_owner": { "type": "string", "description": "Owner responsible for spend predictability." }
        }
      },
      "migration_policy": {
        "type": "object",
        "required": ["effective_date", "cohort_plan", "grandfathering_policy", "rollback_triggers", "communication_plan"],
        "additionalProperties": false,
        "properties": {
          "effective_date": { "type": "string", "description": "Migration start date." },
          "cohort_plan": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["cohort_name", "transition_date", "treatment"],
              "additionalProperties": false,
              "properties": {
                "cohort_name": { "type": "string", "description": "Cohort label." },
                "transition_date": { "type": "string", "description": "Scheduled transition date." },
                "treatment": { "type": "string", "description": "Transition treatment." }
              }
            },
            "description": "Phased migration plan."
          },
          "grandfathering_policy": { "type": "string", "description": "Legacy rights and expiration terms." },
          "rollback_triggers": { "type": "array", "items": { "type": "string" }, "description": "Objective rollback/pause conditions." },
          "communication_plan": { "type": "array", "items": { "type": "string" }, "description": "Required migration communications." }
        }
      },
      "interpretation_policy": {
        "type": "object",
        "required": ["primary_metrics", "quality_gates", "benchmark_caveats", "confidence_label"],
        "additionalProperties": false,
        "properties": {
          "primary_metrics": { "type": "array", "items": { "type": "string" }, "description": "Core interpretation metrics." },
          "quality_gates": { "type": "array", "items": { "type": "string" }, "description": "Validity checks before interpretation." },
          "benchmark_caveats": { "type": "array", "items": { "type": "string" }, "description": "Benchmark portability caveats." },
          "confidence_label": { "type": "string", "enum": ["high", "medium", "low"], "description": "Confidence after quality checks." }
        }
      },
      "evidence_log": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["claim", "evidence_strength", "source_refs", "notes"],
          "additionalProperties": false,
          "properties": {
            "claim": { "type": "string", "description": "Decision claim." },
            "evidence_strength": { "type": "string", "enum": ["strong", "moderate", "weak"], "description": "Strength of support." },
            "source_refs": { "type": "array", "items": { "type": "string" }, "description": "Supporting source IDs." },
            "notes": { "type": "string", "description": "Interpretation caveats." }
          }
        },
        "description": "Traceable evidence ledger."
      },
      "anti_patterns_checked": {
        "type": "array",
        "items": {
          "type": "string",
          "enum": ["metric_whiplash", "forced_rebundling", "hidden_terms", "cancellation_asymmetry", "big_bang_migration", "no_rollback", "low_context_communication", "grandfathering_ambiguity", "fairness_portability_blind_spot"]
        },
        "description": "Anti-pattern checks completed."
      },
      "trust_compliance_checks": {
        "type": "object",
        "required": ["recurring_terms_clarity", "cancellation_parity", "ai_claim_transparency", "jurisdiction_notes"],
        "additionalProperties": false,
        "properties": {
          "recurring_terms_clarity": { "type": "string", "description": "Clarity of recurring terms and fees." },
          "cancellation_parity": { "type": "string", "description": "Parity between signup and cancellation effort." },
          "ai_claim_transparency": { "type": "string", "description": "Whether AI claims match operational controls." },
          "jurisdiction_notes": { "type": "array", "items": { "type": "string" }, "description": "Region-specific compliance notes." }
        }
      },
      "version_notes": { "type": "string", "description": "Current version vs roadmap boundaries." },
      "confidence": { "type": "string", "enum": ["high", "medium", "low"], "description": "Overall recommendation confidence." },
      "unresolved_assumptions": { "type": "array", "items": { "type": "string" }, "description": "Critical unresolved assumptions." }
    }
  }
}
```

---

## Gaps & Uncertainties

- Public case coverage rarely includes audited long-term churn/LTV impact after migration backlash.
- Some vendor pricing pages are dynamic and may change without stable publication timestamps.
- API docs vary in explicit numeric limits; runtime headers/backoff remain necessary.
- Benchmark portability is limited across segments and verticals.
- Regulatory interpretation evolves; legal review remains necessary before production rollout.
