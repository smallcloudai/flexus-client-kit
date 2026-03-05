# Research: pricing-pilot-packaging

**Skill path:** `flexus_simple_bots/strategist/skills/pricing-pilot-packaging/`
**Bot:** strategist
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`pricing-pilot-packaging` defines commercial terms for the pilot phase: what the customer pays during evaluation, what measurable outcomes define success, and which conditions convert the pilot into standard commercial terms. This skill sits between offer design and full tier/pricing execution, so it must balance learning velocity, buyer risk reduction, and credible revenue conversion.

The current skill already captures core pilot structures (`free_loi`, `paid_discounted`, `success_based`, `poc_to_expansion`) and stresses measurable success criteria. This research extends it with 2024-2026 evidence on pilot governance, conversion pre-wiring, instrumentation quality gates, procurement/legal readiness, and tool constraints that frequently determine whether pilots convert or stall.

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
- Contradictions between sources are explicitly noted: **passed**
- Volume target met (Findings sections 800-4000 words): **passed**

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

- Pilot packaging has shifted from "run a trial and discuss later" to a pre-wired decision process. Stronger 2024-2026 operator guidance sets a conversion decision date at kickoff and frames pilot terms as a path to a definitive agreement, not open-ended discovery.
- For high-lift enterprise deployments, paid pilots are increasingly favored over free pilots because payment acts as commitment and aligns internal buyer stakeholders. Free/reverse-trial motions still make sense for PLG or low-implementation products, creating a real contradiction that should be resolved by GTM motion and implementation lift.
- Typical enterprise pilot windows are still bounded (commonly 30-90 days), with complex cross-functional pilots frequently running near three months. Duration should match integration and stakeholder complexity rather than defaulting to fixed trial windows.
- Success criteria quality is the key conversion driver. Sources repeatedly support defining baseline, target, measurement method, and data owner before kickoff. "Improve efficiency" style criteria underperform against specific KPI statements.
- KPI design is increasingly three-layered: (1) operational reliability and readiness, (2) adoption/behavior signals, (3) business-value outcomes. Teams that track only feature usage struggle to justify budget release for production.
- Pilot governance cadence is explicit in successful programs: frequent operating reviews (often weekly), periodic structured feedback loops, and broader roadmap/commercial checkpoints. This prevents "pilot drift" where scope and success definitions silently change mid-flight.
- Multi-stakeholder alignment from week 0 is now treated as a method requirement, not project management nice-to-have. Buyer champion support alone is insufficient in multi-department enterprise buying groups.
- Conversion triggers work better as contractual gates than subjective impressions: predefined metric thresholds plus production-readiness checks plus an expiry-bound commercial offer.
- Discounting/crediting patterns that preserve conversion urgency appear repeatedly: pilot fee credits applied to year-1 commitment, narrow windows for conversion incentives, and committed pre-purchase options when usage economics are uncertain.

**Contradictions to carry into skill logic:**

- **Paid-first vs free-first pilots:** enterprise/operator sources lean paid; PLG sources still support free/reverse-trial structures. Resolution should be rule-based by segment, implementation burden, and security/procurement depth.
- **Speed-first iteration vs governance-first rigor:** AI build guidance emphasizes fast iteration, while enterprise rollout guidance requires legal/security/procurement sequencing. Practical resolution is phased execution: move fast inside each phase, but do not skip control gates.

**Sources:**
- [TechTarget: How to run a successful IT pilot program (2024)](https://www.techtarget.com/searchcio/feature/How-to-run-a-successful-IT-pilot-program)
- [Microsoft Inside Track: Measuring Microsoft 365 Copilot rollout success (2024)](https://www.microsoft.com/insidetrack/blog/measuring-the-success-of-our-microsoft-365-copilot-rollout-at-microsoft/)
- [UK Government: Microsoft 365 Copilot cross-government findings report (2025)](https://www.gov.uk/government/publications/microsoft-365-copilot-experiment-cross-government-findings-report/microsoft-365-copilot-experiment-cross-government-findings-report-html)
- [Google Cloud: Prototype to production GenAI (2025)](https://cloud.google.com/transform/the-prompt-prototype-to-production-gen-ai)
- [Google Cloud: Beyond the pilot lessons (2026)](https://cloud.google.com/transform/beyond-the-pilot-five-hard-won-lessons-from-google-clouds-ai-transformation-strategy)
- [Google Cloud: KPIs for production AI agents (2026)](https://cloud.google.com/transform/the-kpis-that-actually-matter-for-production-ai-agents)
- [Common Paper: Pilot Agreement Standard Terms v1.1 (2025)](https://commonpaper.com/standards/pilot-agreement/1.1/)
- [Microsoft Copilot Credit Pre-Purchase Plan announcement (2025)](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/scale-your-agent-rollout-with-confidence-introducing-copilot-credit-pre-purchase-plan/)
- [Microsoft Learn: Copilot Credit P3 docs (2026)](https://learn.microsoft.com/en-us/azure/cost-management-billing/reservations/copilot-credit-p3)
- [SaaStr paid-pilot operator guidance (2023, evergreen)](https://www.saastr.com/we-are-a-b2b-saas-startup-and-want-to-develop-our-product-in-pilots-with-customers-should-we-charge-for-the-pilots-and-how-much/)
- [OpenView reverse trials (2022, evergreen)](https://openviewpartners.com/blog/your-guide-to-reverse-trials/)

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

- A practical pilot stack now has four layers: billing execution, quote/contract workflow, experimentation/measurement, and CRM handoff. Using one platform as a proxy for all four layers creates blind spots during pilot-to-contract conversion.
- Stripe remains a strong billing backbone for paid pilots and conversion ramping. Current docs and changelog guidance show meaningful migration work for teams on legacy usage billing, including newer meter-event paths and version-aware rollout constraints.
- Stripe migration details matter for pilot design: if pilot pricing assumes legacy usage semantics, conversion can fail later when implementation hits API-version or meter-model constraints.
- HubSpot added payable quote capabilities through its CRM quote APIs (2024 updates), making it viable for lighter-weight pilot checkout/approval flows. This is useful for pilot terms that need payment collection before full CPQ implementation.
- HubSpot line item modeling has association constraints that can cause quote/deal data integrity issues if objects are reused incorrectly; pilot packaging workflows should avoid shared line-item assumptions.
- Salesforce Industries CPQ and Salesforce Commerce APIs provide robust enterprise packaging and promotion controls, but API/governor/request size limits and licensing complexity should be considered before assuming fast pilot iteration.
- LaunchDarkly, Statsig, Amplitude, and PostHog all support pilot experimentation programs, but their constraints differ (event windows, quota behavior, region separation, or key management). Pilot governance should normalize these differences before comparing outputs.
- DocuSign and PandaDoc are practical contract-conversion surfaces. The friction points are usually operational: embedded flow security updates, expiring views, async document processing, and webhook reliability requirements.
- Contradictions exist in vendor positioning: some surfaces are marked "legacy" while still receiving updates; some platforms encourage API use while also recommending SDK-first patterns. Skill logic should require environment verification over static assumptions.

**Sources:**
- [Stripe changelog: usage billing v2 meter events (2024)](https://docs.stripe.com/changelog/acacia/2024-09-30/usage-based-billing-v2-meter-events-api?locale=en-GB)
- [Stripe legacy usage migration guide (2025 era docs)](https://docs.stripe.com/billing/subscriptions/usage-based-legacy/migration-guide)
- [HubSpot developer changelog April 2024 (payable quotes)](https://developers.hubspot.com/changelog/april-2024-rollup)
- [HubSpot Quotes API docs](https://developers.hubspot.com/docs/api/crm/quotes)
- [HubSpot line items and association constraints](https://developers.hubspot.com/docs/guides/api/crm/objects/line-items)
- [Salesforce Industries CPQ cart APIs](https://developer.salesforce.com/docs/industries/cme/guide/comms-cart-based-apis-for-industries-cpq.html)
- [Salesforce CPQ update cart items](https://developer.salesforce.com/docs/industries/cme/guide/std_comms-update-items-in-cart.html)
- [Salesforce Commerce pricing/promotions APIs](https://developer.salesforce.com/docs/commerce/salesforce-commerce/guide/b2b-d2c-comm-pricing-promotions-apis.html)
- [LaunchDarkly experimentation events](https://launchdarkly.com/docs/home/experimentation/events)
- [LaunchDarkly metrics API](https://launchdarkly.com/docs/api/metrics)
- [Statsig HTTP API docs](https://docs-legacy.statsig.com/http-api/)
- [Statsig events API reference](https://docs.statsig.com/api-reference/events/log-custom-events)
- [Amplitude Experiment Management API](https://amplitude.com/docs/apis/experiment/experiment-management-api)
- [PostHog flags API](https://posthog.com/docs/api/flags)
- [PostHog experiments API](https://posthog.com/docs/api/experiments-2)
- [DocuSign createEnvelope](https://developers.docusign.com/docs/esign-rest-api/reference/envelopes/envelopes/create/)
- [DocuSign createSenderView](https://developers.docusign.com/docs/esign-rest-api/reference/envelopes/envelopeviews/createsender/)
- [DocuSign embedded view update guidance (2024)](https://docusign.com/blog/developers/esignature-rest-api-embedded-correct-view-updated)
- [PandaDoc API changelog (2026 updates)](https://developers.pandadoc.com/changelog)
- [PandaDoc create-from-template](https://developers.pandadoc.com/reference/create-document-from-template)
- [PandaDoc webhook behavior and limits](https://developers.pandadoc.com/docs/webhooks)

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

- Pilot evidence quality should be treated as progression evidence, not final-proof evidence. Method literature and experimentation guidance support pre-registered progression thresholds (`go`, `amend`, `stop`) rather than retrospective storytelling.
- Precision-driven interpretation is more reliable than binary significance framing for pilot decisions. If confidence intervals around core metrics are wider than business tolerance, conversion confidence should be downgraded.
- Sample representativeness is a recurring risk. Pilot cohorts selected by friendly champions or narrow use cases can materially overstate scale performance; confidence should be explicitly lowered for non-representative cohorts.
- Sample Ratio Mismatch (SRM) is a hard validity gate in mature experimentation practice. If SRM fails, outcomes should be considered invalid for conversion decisions until instrumentation or randomization issues are resolved.
- Time-window bias remains common. Decisions made before full cycle coverage or before precision thresholds are met produce unstable conversion verdicts; runtime and quality gates should be mandatory.
- Buyer-champion enthusiasm is insufficient as conversion evidence in enterprise contexts where buying groups are large and cross-functional. Pilot interpretation should include stakeholder readiness and procurement path evidence.
- "Intent to expand" signals are useful but noisy. They should be secondary to observed behavior (adoption, retention, workflow completion quality, and economic owner validation).
- Weak usage and retention behavior can invalidate otherwise positive qualitative feedback. Benchmarks from enterprise product data suggest low feature adoption and early retention decay are common, so conversion criteria should include minimum behavior thresholds.
- Legal/procurement friction is often misread as product failure. Stronger interpretation frameworks split verdicts into two tracks: product-value signal and commercial-readiness signal.
- AI pilot narratives contain contradictions: positive ROI narratives coexist with high POC abandonment estimates. Practical interpretation requires dual gates: value proof plus operational/procurement readiness.

**Sources:**
- [BMJ: Pilot sample-size and progression criteria tutorial (2024)](https://www.bmj.com/content/390/bmj-2024-083405)
- [Microsoft ExP: Diagnosing SRM](https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/)
- [Eppo docs: SRM checks](https://docs.geteppo.com/statistics/sample-ratio-mismatch/)
- [Harness docs: sample ratio check](https://developer.harness.io/docs/feature-management-experimentation/experimentation/experiment-results/analyzing-experiment-results/sample-ratio-check)
- [GrowthBook: experiment decision framework](https://docs.growthbook.io/app/experiment-decisions)
- [Forrester: The State of Business Buying 2024](https://www.forrester.com/press-newsroom/forrester-the-state-of-business-buying-2024/)
- [Pendo: Enterprise product benchmarks (2024)](https://www.pendo.io/pendo-blog/enterprise-product-benchmarks/)
- [ACC 2024 Chief Legal Officers Survey](https://www.acc.com/sites/default/files/2024-01/ACC_2024_Chief_Legal_Officers_Survey_Report.pdf)
- [Deloitte State of Generative AI (2024)](https://www.deloitte.com/us/en/about/press-room/state-of-generative-ai.html)
- [Gartner press release: GenAI projects abandoned after POC (2024)](https://www.gartner.com/en/newsroom/press-releases/2024-07-29-gartner-predicts-30-percent-of-generative-ai-projects-will-be-abandoned-after-proof-of-concept-by-end-of-2025)
- [Common Paper contract benchmark Q1 2024](https://commonpaper.com/resources/contract-benchmark-2024-q1/)

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

- **Anti-pattern: Open-ended pilot with no conversion mechanics.**
  - Detection signal: no decision date, no named budget owner, no pre-agreed post-pilot contract path.
  - Consequence: pilot purgatory and low urgency.
  - Mitigation: include explicit go/no-go date and conversion clause in pilot terms.
- **Anti-pattern: Pilot economics disconnected from production economics.**
  - Detection signal: post-pilot requires entirely new pricing/legal/security package.
  - Consequence: conversion cycle effectively restarts after "successful" pilot.
  - Mitigation: pre-negotiate conversion envelope (pricing band, contract vehicle, security exhibits) in pilot agreement.
- **Anti-pattern: Vague or vanity success criteria.**
  - Detection signal: no baseline, no threshold, no owner; heavy reliance on subjective satisfaction language.
  - Consequence: impossible to defend production budget.
  - Mitigation: define measurable KPI thresholds and reporting cadence before kickoff.
- **Anti-pattern: Champion-only pilot governance.**
  - Detection signal: late-stage "need to involve legal/procurement/security" surprises.
  - Consequence: stalled buying despite product enthusiasm.
  - Mitigation: involve buying-group stakeholders from week 0 with explicit roles.
- **Anti-pattern: Legal/procurement/security track starts too late.**
  - Detection signal: redline churn and questionnaire bottlenecks in final pilot weeks.
  - Consequence: time-to-convert extends beyond momentum window.
  - Mitigation: parallel commercial-readiness track during pilot execution.
- **Anti-pattern: Data quality and instrumentation assumptions.**
  - Detection signal: metric restatements, missing telemetry, inability to reconcile usage with value outcomes.
  - Consequence: executives distrust pilot evidence.
  - Mitigation: require instrumentation readiness and metric lineage checks before and during pilot.
- **Anti-pattern: Governance bolted on after demo success.**
  - Detection signal: compliance/risk controls undefined at conversion checkpoint.
  - Consequence: blocked production deployment.
  - Mitigation: define governance and risk exit criteria as pilot entry requirements.
- **Anti-pattern: No pilot-to-production handoff owner.**
  - Detection signal: "successful" pilot closes with no funded implementation backlog or accountable owner.
  - Consequence: pilot attrition and low conversion rate.
  - Mitigation: enforce named owner, budget path, and implementation checklist at kickoff.

**Sources:**
- [Gartner press release on GenAI POC abandonment (2024)](https://www.gartner.com/en/newsroom/press-releases/2024-07-29-gartner-predicts-30-percent-of-generative-ai-projects-will-be-abandoned-after-proof-of-concept-by-end-of-2025)
- [Deloitte GenAI survey and scaling blockers (2024)](https://www.deloitte.com/ke/en/about/press-room/despite-increased-investment-and-early-enthusiasm-data-and-risk-remain-key-challenges-to-scaling-generative-ai-reveals-new-deloitte-survey.html)
- [Forrester business buying complexity (2024)](https://www.forrester.com/press-newsroom/forrester-the-state-of-business-buying-2024/)
- [Common Paper pilot agreement standard (2025)](https://commonpaper.com/standards/pilot-agreement/1.1/)
- [OpenTelemetry collector anti-patterns (2024)](https://opentelemetry.io/blog/2024/otel-collector-anti-patterns/)
- [Microsoft Inside Track Copilot measurement (2024)](https://www.microsoft.com/insidetrack/blog/measuring-the-success-of-our-microsoft-365-copilot-rollout-at-microsoft/)
- [AWS prescriptive guidance for GenAI POCs](https://docs.aws.amazon.com/prescriptive-guidance/latest/gen-ai-lifecycle-operational-excellence/dev-architecting.html)
- [AWS: Getting POCs to production](https://aws.amazon.com/blogs/enterprise-strategy/generative-ai-getting-proofs-of-concept-to-production/)
- [AWS: Beyond pilots framework](https://aws.amazon.com/blogs/machine-learning/beyond-pilots-a-proven-framework-for-scaling-ai-to-production/)

---

### Angle 5+: Commercial Contracting & Conversion Readiness
> Additional domain-specific angle: practical contracting and commercial-readiness patterns that influence pilot conversion outcomes.

**Findings:**

- Pilot terms are increasingly being standardized to evaluate suitability for a follow-on definitive agreement, including explicit conversion and termination mechanics.
- Procurement process duration variability is now a major pilot-planning input; conversion confidence should include legal/procurement readiness, not just product KPI outcomes.
- Contract benchmark data indicates signature speed on its own can be misleading; stalled enterprise purchases often fail earlier on buying-group and readiness alignment.
- Pre-purchase/commit structures in AI offerings demonstrate an emerging middle path between pure PAYG pilots and immediate full annual commitments.
- Teams should treat conversion as a two-lane deliverable: commercial lane (terms, approval path, budget owner) and product lane (value proof). Missing either lane decreases conversion reliability.
- A practical governance pattern is to require explicit commercial artifacts at kickoff: pilot MSA/order form path, security/privacy obligations, procurement owner, and renewal/conversion timeline.

**Sources:**
- [Common Paper Pilot Agreement v1.1 (2025)](https://commonpaper.com/standards/pilot-agreement/1.1/)
- [Common Paper contract benchmark Q1 2024](https://commonpaper.com/resources/contract-benchmark-2024-q1/)
- [Forrester State of Business Buying 2024](https://www.forrester.com/press-newsroom/forrester-the-state-of-business-buying-2024/)
- [Vertice procurement stage timing (updated 2026)](https://www.vertice.one/insights/procurement-process-stage-completion-times)
- [Microsoft Copilot pre-purchase plan announcement (2025)](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/scale-your-agent-rollout-with-confidence-introducing-copilot-credit-pre-purchase-plan/)
- [Microsoft Learn Copilot Credit P3 docs (2026)](https://learn.microsoft.com/en-us/azure/cost-management-billing/reservations/copilot-credit-p3)

---

## Synthesis

The central pattern across sources is that pilot packaging succeeds when it is designed as a conversion system, not an experiment in isolation. Mature teams pre-wire commercial terms, instrument success criteria before kickoff, and require a decision checkpoint with clear outcomes. This sharply contrasts with open-ended pilots that optimize for activity but not decisionability.

Second, interpretation discipline is now a differentiator. Evidence quality issues (sample bias, SRM, short windows, champion bias) can produce false confidence. The strongest approach is to use explicit validity gates and confidence labels so pilot outputs can be trusted by commercial stakeholders, not only product teams.

Third, tool and API constraints materially affect pilot design quality. Billing migration states, quote object constraints, experiment-window definitions, and contract workflow reliability can all break conversion even when product value is real. The skill should therefore encode operational constraints and readiness checks as first-class method steps.

Finally, the dominant failure mode is not usually poor product signal; it is missing handoff readiness between pilot and production. The most actionable updates for `SKILL.md` are: mandatory conversion pre-wire, measurable threshold-based criteria, dual-lane decisioning (value + readiness), and anti-pattern rejection rules that block low-quality pilot packages before they are written to artifacts.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.
> Each item here has a corresponding draft in the section below.

- [x] Replace current pilot method with an explicit staged workflow that ends in a formal conversion verdict (`convert`, `conditional_convert`, `do_not_convert`).
- [x] Add pilot-structure selection rules tied to implementation burden and GTM motion (paid-first for high-lift enterprise, free/reverse-trial only with strict conditions).
- [x] Add measurable success-criteria contract requiring baseline, threshold, owner, and data source for every criterion.
- [x] Add interpretation quality gates (cohort representativeness, SRM/instrumentation checks, duration/precision checks).
- [x] Add dual-lane decisioning logic: product-value signal and commercial-readiness signal must both pass.
- [x] Add explicit pilot-to-production pre-wire requirements (budget owner, legal/procurement path, conversion term envelope).
- [x] Expand anti-pattern section with named warning blocks, detection signals, consequences, and mitigation steps.
- [x] Update `## Available Tools` instructions to enforce evidence loading and explicit unresolved assumptions.
- [x] Expand artifact schema with decision framework, confidence labels, readiness status, and conversion-plan fields.

---

## Draft Content for SKILL.md

> This is the most important section. For every recommendation above, write the actual text that should go into SKILL.md.

### Draft: Core mode and operating principle

---
### Core mode

You are designing a pilot package that can convert to production, not just a temporary discount offer. Your output must reduce buyer risk while preserving a credible path to long-term commercial terms.

Before writing any pilot price, you must hold three principles together:

1. **Decisionability:** the pilot must produce a clear go/no-go decision by a fixed date.
2. **Measurability:** success criteria must be numerically testable with agreed data sources.
3. **Convertibility:** commercial and legal path to production must be pre-wired at kickoff.

If any of these is missing, the package is incomplete and should not be finalized.
---

### Draft: Methodology rewrite (staged workflow)

---
### Methodology

Use this required sequence for every pilot package:

1. **Load context and declare assumptions**
   - Activate relevant strategy artifacts and segment evidence first.
   - Write explicit assumptions for ICP, deployment complexity, integration dependencies, and buyer risk sensitivity.
   - If a critical assumption is unknown, mark it as unresolved and lower confidence in final recommendations.

2. **Choose pilot structure by risk and implementation burden**
   - Use `paid_discounted` as default for enterprise or high-lift pilots where implementation effort is material.
   - Use `free_loi` only when product maturity is low and reference learning is the main objective, and only with written commitment conditions.
   - Use `success_based` when product confidence is high and success criteria can be measured cleanly.
   - Use `poc_to_expansion` when initial scope is intentionally narrow and expansion path is explicit.
   - Do not choose a structure by habit; justify it using buyer risk and internal cost exposure.

3. **Define success criteria contract before kickoff**
   - For each criterion, define:
     - baseline value,
     - target threshold,
     - minimum acceptable threshold,
     - measurement method,
     - data source and owner,
     - review cadence.
   - Every criterion must be specific and auditable.
   - If a criterion cannot be measured reliably, replace it before proceeding.

4. **Set pilot economics and conversion envelope together**
   - Pilot economics must reference expected production economics.
   - Document whether pilot fees are credited toward conversion and under what expiry window.
   - Define the post-pilot price envelope and contract path early (for example annual commitment path, expansion path, or conversion discount boundaries).
   - Do not allow a "pricing later" placeholder for conversion terms.

5. **Build dual-lane governance plan**
   - Product-value lane: KPI measurement, adoption behavior, and business-outcome evidence.
   - Commercial-readiness lane: legal, procurement, privacy/security, budget owner alignment.
   - Assign named owners for each lane and schedule checkpoints across the pilot window.
   - If one lane passes and the other fails, output conditional conversion rather than full conversion.

6. **Apply interpretation quality gates before verdict**
   - Check representativeness of the pilot cohort.
   - Validate instrumentation and randomization quality where experiments are used.
   - Confirm sufficient runtime and precision for critical metrics.
   - Reject verdicts based purely on champion narrative or anecdotal satisfaction.

7. **Issue one of three verdicts with required next actions**
   - `convert`: both value and readiness lanes pass.
   - `conditional_convert`: value lane passes but one or more readiness blockers remain with explicit remediation timeline.
   - `do_not_convert`: core criteria below minimum thresholds or critical blockers unresolved.
   - Each verdict must include rationale and concrete next steps.

8. **Publish conversion plan and review cadence**
   - Include decision date, responsible executive owner, and transition timeline.
   - Add a post-conversion review checkpoint to verify expected outcomes in production.
   - If conversion does not happen, explicitly state whether to iterate pilot design or archive.

Do NOT:

- Run open-ended pilots with no conversion decision date.
- Use undefined criteria like "felt better" or "looked promising."
- Allow pilot terms that cannot map to production terms.
- Declare success without confirming commercial-readiness lane.
---

### Draft: Pilot structure selection rules

---
### Pilot structure decision rules

Use the following decision logic:

- If implementation burden is high and multiple stakeholder approvals are required, prefer `paid_discounted`.
- If product maturity is low and goal is validation/reference generation, `free_loi` can be used only with strict obligations and fixed decision date.
- If buyer demands risk transfer and success criteria are robustly measurable, use `success_based`.
- If early scope is intentionally narrow (single team/use case) with known expansion path, use `poc_to_expansion`.

Decision checks you must write explicitly:

1. Why this structure is appropriate for the target segment.
2. What buyer risk is reduced by this structure.
3. What seller risk is introduced and how it is controlled.
4. What condition flips the account from pilot terms to production terms.

If these four checks cannot be answered, the structure choice is incomplete.
---

### Draft: Success criteria and measurement contract

---
### Pilot success criteria design

Every success criterion must be entered in this format:

- `criterion_name`
- `baseline_value`
- `target_value`
- `minimum_value`
- `measurement_method`
- `data_source`
- `owner`
- `review_cadence`

Rules:

1. Use business-outcome criteria, not only product-usage criteria.
2. At least one criterion must represent operational readiness (for example reliability, supportability, or workflow quality).
3. At least one criterion must represent commercial value (for example time saved, cycle-time reduction, or measurable productivity gain).
4. At least one criterion must represent adoption quality (not raw signups).

Interpretation rules:

- If result is at or above target across critical criteria and no critical blockers exist, value lane passes.
- If result is between minimum and target, return conditional outcome with remediation plan.
- If result is below minimum on a critical criterion, do not convert.

Do not use criteria without baselines. Do not change thresholds mid-pilot unless both parties approve and change is recorded.
---

### Draft: Data interpretation quality gates

---
### Evidence and signal quality checks

Before final verdict, perform these checks:

1. **Representativeness check**
   - Confirm pilot participants reflect intended production user group.
   - If pilot is champion-heavy or narrow, lower confidence by one level.

2. **Instrumentation validity check**
   - Verify required telemetry exists for each criterion.
   - If core metrics cannot be computed reproducibly, verdict cannot be `convert`.

3. **Experiment integrity check (when randomized tests are used)**
   - Run sample-ratio and allocation sanity checks.
   - Treat integrity failures as hard-stop until fixed.

4. **Duration and precision check**
   - Ensure pilot runtime covers a meaningful work cycle and provides enough precision for decision metrics.
   - If intervals remain too wide for safe commercial decisioning, output conditional or no-convert.

5. **Narrative vs behavior check**
   - Do not let positive qualitative feedback override weak behavioral evidence.
   - Strong narrative with weak usage/retention is insufficient for full conversion.

Confidence labels:

- `high`: representative cohort, valid instrumentation, and strong threshold attainment across both lanes.
- `medium`: value signal is good but one material quality/readiness caveat remains.
- `low`: evidence quality issues or critical blockers prevent reliable conversion.
---

### Draft: Dual-lane conversion decisioning

---
### Conversion decision framework

You must score two lanes separately:

1. **Product-value lane**
   - Threshold attainment for core KPIs.
   - Adoption quality and behavioral consistency.
   - Evidence confidence level.

2. **Commercial-readiness lane**
   - Budget owner confirmed.
   - Legal/procurement path confirmed.
   - Security/privacy requirements cleared or fully scoped.
   - Contract conversion path defined.

Verdict rules:

- `convert`: both lanes pass.
- `conditional_convert`: product-value lane passes; readiness lane has remediable blockers with committed timeline.
- `do_not_convert`: value lane fails minimum thresholds, or readiness blockers are critical and unresolved.

Never collapse both lanes into a single score. A pilot can prove value and still fail readiness, and the output must make that distinction explicit.
---

### Draft: Conversion pre-wire and governance requirements

---
### Pilot-to-production pre-wire

Before pilot start, require:

- named executive sponsor,
- named economic buyer or budget owner,
- initial contract path (agreement vehicle and procurement route),
- security/privacy review owner and required artifacts,
- conversion decision date,
- post-pilot offer validity window.

During pilot, run governance cadence:

- weekly execution check,
- periodic stakeholder checkpoint (including non-product stakeholders),
- final decision session scheduled before pilot end.

If conversion requires net-new legal/procurement discovery after pilot completion, classify package as high conversion risk and downgrade readiness confidence.
---

### Draft: Anti-pattern warnings (paste-ready)

---
### Warning: Pilot Purgatory Design

**What it looks like:** pilot terms have no conversion deadline or pre-agreed next-step contract path.  
**Detection signal:** no decision date, no budget owner, no transition timeline in output.  
**Consequence:** pilot extends without decision; commercial momentum decays.  
**Mitigation:** require fixed decision date, named owner, and explicit conversion mechanics at kickoff.

### Warning: Vague Success Criteria

**What it looks like:** goals are subjective ("improve productivity") without baseline or threshold.  
**Detection signal:** criteria objects miss baseline/target/owner fields.  
**Consequence:** impossible to defend conversion recommendation to finance/procurement.  
**Mitigation:** reject package until all criteria are measurable, owned, and thresholded.

### Warning: Champion-Only Signal

**What it looks like:** one internal champion drives pilot while buying-group stakeholders remain unaligned.  
**Detection signal:** late-stage requests to add procurement/security/legal stakeholders.  
**Consequence:** purchase stalls after technical success.  
**Mitigation:** enforce stakeholder map and multi-functional checkpoints from week 0.

### Warning: Economics Disconnect

**What it looks like:** pilot pricing and production pricing have no defined bridge.  
**Detection signal:** post-pilot conversion requires re-negotiating pricing model from scratch.  
**Consequence:** conversion cycle resets and win rate drops.  
**Mitigation:** include conversion envelope, crediting logic, and expiry window in pilot package.

### Warning: Instrumentation Blindness

**What it looks like:** critical success metrics are missing or inconsistent at review time.  
**Detection signal:** metric restatements or unresolved telemetry gaps in final week.  
**Consequence:** low-confidence verdict and executive distrust.  
**Mitigation:** perform instrumentation readiness check before kickoff and recurring data-quality checks during pilot.

### Warning: Readiness-Lane Neglect

**What it looks like:** product metrics pass but legal/procurement/security lane is ignored.  
**Detection signal:** "successful pilot" with unresolved commercial blockers.  
**Consequence:** conversion failure despite positive product outcomes.  
**Mitigation:** use dual-lane verdict model; block `convert` until readiness lane passes.
---

### Draft: Available Tools section (updated, paste-ready)

---
## Available Tools

Use internal strategy artifacts before writing a pilot package:

```python
flexus_policy_document(op="activate", args={"p": "/strategy/pricing-tiers"})
flexus_policy_document(op="activate", args={"p": "/strategy/offer-design"})
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})
flexus_policy_document(op="list", args={"p": "/pain/"})
```

Usage rules:

1. Always load pricing tiers and offer design context before choosing pilot structure.
2. Always review relevant pain/WTP evidence before setting pilot discounts or success-based terms.
3. If evidence is weak or incomplete, lower confidence and output `conditional_convert` planning assumptions instead of forcing certainty.
4. Record unresolved assumptions explicitly in the artifact.

Write final output only after methodology and quality gates are complete:

```python
write_artifact(
    artifact_type="pilot_package",
    path="/strategy/pilot-package",
    data={...},
)
```
---

### Draft: Recording requirements

---
### Recording

When writing `/strategy/pilot-package`, include:

- selected pilot structure and rationale,
- pricing terms and conversion envelope,
- success criteria with baseline/target/minimum thresholds,
- evidence confidence and unresolved assumptions,
- dual-lane decision status,
- readiness blockers and remediation plan,
- stakeholder map and governance cadence,
- final verdict (`convert`, `conditional_convert`, `do_not_convert`) with next actions.

Do not write a `convert` verdict when either lane fails hard-stop criteria.
---

### Draft: Schema additions

```json
{
  "pilot_package": {
    "type": "object",
    "required": [
      "created_at",
      "target_segment",
      "pilot_structure",
      "pilot_duration_days",
      "pilot_hypothesis",
      "pricing_terms",
      "success_criteria",
      "measurement_plan",
      "stakeholder_map",
      "commercial_readiness",
      "conversion_terms",
      "decision_framework",
      "final_verdict",
      "confidence"
    ],
    "additionalProperties": false,
    "properties": {
      "created_at": {
        "type": "string",
        "description": "ISO-8601 UTC timestamp when the pilot package was generated."
      },
      "target_segment": {
        "type": "string",
        "description": "Primary customer segment this pilot package is designed for."
      },
      "pilot_structure": {
        "type": "string",
        "enum": [
          "free_loi",
          "paid_discounted",
          "success_based",
          "poc_to_expansion"
        ],
        "description": "Commercial structure used during pilot."
      },
      "pilot_duration_days": {
        "type": "integer",
        "minimum": 1,
        "description": "Planned pilot length in calendar days."
      },
      "pilot_hypothesis": {
        "type": "string",
        "description": "Clear statement of what value claim this pilot is testing."
      },
      "pricing_terms": {
        "type": "object",
        "required": [
          "pilot_price",
          "standard_price_reference",
          "discount_pct",
          "payment_timing",
          "credit_on_conversion"
        ],
        "additionalProperties": false,
        "properties": {
          "pilot_price": {
            "type": ["number", "string"],
            "description": "Commercial amount charged during pilot."
          },
          "standard_price_reference": {
            "type": "number",
            "description": "Reference production price used to compute pilot discounting."
          },
          "discount_pct": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Pilot discount fraction against standard price reference."
          },
          "payment_timing": {
            "type": "string",
            "description": "When payment is due (for example upfront, monthly, milestone-based)."
          },
          "credit_on_conversion": {
            "type": "object",
            "required": [
              "enabled",
              "credit_rule",
              "expiry_days"
            ],
            "additionalProperties": false,
            "properties": {
              "enabled": {
                "type": "boolean",
                "description": "Whether pilot fees are credited toward production conversion."
              },
              "credit_rule": {
                "type": "string",
                "description": "How and when pilot fees are credited if conversion occurs."
              },
              "expiry_days": {
                "type": "integer",
                "minimum": 0,
                "description": "Days after pilot end during which credit remains valid."
              }
            }
          }
        }
      },
      "success_criteria": {
        "type": "array",
        "minItems": 1,
        "items": {
          "type": "object",
          "required": [
            "criterion_name",
            "baseline_value",
            "target_value",
            "minimum_value",
            "measurement_method",
            "data_source",
            "owner",
            "review_cadence"
          ],
          "additionalProperties": false,
          "properties": {
            "criterion_name": {
              "type": "string",
              "description": "Name of the KPI or outcome being evaluated."
            },
            "baseline_value": {
              "type": ["number", "string"],
              "description": "Pre-pilot baseline used as comparison anchor."
            },
            "target_value": {
              "type": ["number", "string"],
              "description": "Threshold that indicates strong success for this criterion."
            },
            "minimum_value": {
              "type": ["number", "string"],
              "description": "Minimum acceptable threshold before conversion is blocked."
            },
            "measurement_method": {
              "type": "string",
              "description": "How the metric is calculated and validated."
            },
            "data_source": {
              "type": "string",
              "description": "System or report where metric data is pulled from."
            },
            "owner": {
              "type": "string",
              "description": "Role accountable for metric data quality and review."
            },
            "review_cadence": {
              "type": "string",
              "enum": [
                "weekly",
                "biweekly",
                "monthly",
                "end_of_pilot"
              ],
              "description": "How often criterion performance is formally reviewed."
            }
          }
        }
      },
      "measurement_plan": {
        "type": "object",
        "required": [
          "instrumentation_ready",
          "cohort_representative",
          "runtime_sufficient",
          "quality_notes"
        ],
        "additionalProperties": false,
        "properties": {
          "instrumentation_ready": {
            "type": "boolean",
            "description": "Whether required telemetry exists and is validated."
          },
          "cohort_representative": {
            "type": "boolean",
            "description": "Whether pilot participants reflect intended production users."
          },
          "runtime_sufficient": {
            "type": "boolean",
            "description": "Whether pilot runtime is sufficient for stable interpretation."
          },
          "quality_notes": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Quality caveats, data limitations, or interpretation risks."
          }
        }
      },
      "stakeholder_map": {
        "type": "object",
        "required": [
          "executive_sponsor",
          "economic_buyer",
          "product_owner",
          "security_owner",
          "procurement_owner",
          "legal_owner"
        ],
        "additionalProperties": false,
        "properties": {
          "executive_sponsor": {
            "type": "string",
            "description": "Named executive sponsor on customer side."
          },
          "economic_buyer": {
            "type": "string",
            "description": "Budget owner accountable for conversion approval."
          },
          "product_owner": {
            "type": "string",
            "description": "Owner of business workflow under pilot."
          },
          "security_owner": {
            "type": "string",
            "description": "Owner for security/privacy review and approvals."
          },
          "procurement_owner": {
            "type": "string",
            "description": "Owner of purchasing workflow and contracting route."
          },
          "legal_owner": {
            "type": "string",
            "description": "Owner of legal review and negotiation."
          }
        }
      },
      "commercial_readiness": {
        "type": "object",
        "required": [
          "contract_path_defined",
          "security_requirements_defined",
          "procurement_path_defined",
          "budget_confirmed",
          "blockers"
        ],
        "additionalProperties": false,
        "properties": {
          "contract_path_defined": {
            "type": "boolean",
            "description": "Whether conversion contract vehicle is known before pilot end."
          },
          "security_requirements_defined": {
            "type": "boolean",
            "description": "Whether required security/privacy artifacts are scoped."
          },
          "procurement_path_defined": {
            "type": "boolean",
            "description": "Whether procurement process and approvers are known."
          },
          "budget_confirmed": {
            "type": "boolean",
            "description": "Whether budget source for conversion has been identified."
          },
          "blockers": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Open commercial-readiness blockers at time of decision."
          }
        }
      },
      "conversion_terms": {
        "type": "object",
        "required": [
          "conversion_trigger",
          "conversion_price",
          "transition_timeline",
          "decision_date",
          "offer_expiry_days"
        ],
        "additionalProperties": false,
        "properties": {
          "conversion_trigger": {
            "type": "string",
            "description": "Primary trigger logic that initiates conversion."
          },
          "conversion_price": {
            "type": "number",
            "description": "Expected production pricing at conversion."
          },
          "transition_timeline": {
            "type": "string",
            "description": "Timeline from pilot completion to production terms."
          },
          "decision_date": {
            "type": "string",
            "description": "ISO-8601 date of formal conversion decision checkpoint."
          },
          "offer_expiry_days": {
            "type": "integer",
            "minimum": 0,
            "description": "Days conversion terms remain valid after pilot completion."
          }
        }
      },
      "decision_framework": {
        "type": "object",
        "required": [
          "value_lane_status",
          "readiness_lane_status",
          "decision_rationale",
          "next_actions"
        ],
        "additionalProperties": false,
        "properties": {
          "value_lane_status": {
            "type": "string",
            "enum": [
              "pass",
              "conditional",
              "fail"
            ],
            "description": "Status of product-value evidence lane."
          },
          "readiness_lane_status": {
            "type": "string",
            "enum": [
              "pass",
              "conditional",
              "fail"
            ],
            "description": "Status of commercial-readiness lane."
          },
          "decision_rationale": {
            "type": "string",
            "description": "Narrative explanation of verdict based on both lanes."
          },
          "next_actions": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Concrete follow-up actions required after verdict."
          }
        }
      },
      "final_verdict": {
        "type": "string",
        "enum": [
          "convert",
          "conditional_convert",
          "do_not_convert"
        ],
        "description": "Final pilot outcome recommendation."
      },
      "confidence": {
        "type": "object",
        "required": [
          "overall",
          "reason",
          "unresolved_assumptions"
        ],
        "additionalProperties": false,
        "properties": {
          "overall": {
            "type": "string",
            "enum": [
              "high",
              "medium",
              "low"
            ],
            "description": "Overall confidence in verdict quality."
          },
          "reason": {
            "type": "string",
            "description": "Why this confidence level was assigned."
          },
          "unresolved_assumptions": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Critical assumptions that remain unverified."
          }
        }
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Public, independent benchmark data on pilot-to-production conversion rates by pilot structure remains limited; many practical sources are operator or vendor narratives.
- Tool and API constraints (limits, quotas, endpoint behavior) change frequently; implementation teams must re-verify operational details at execution time.
- Cross-industry thresholds for "good" pilot KPIs are not standardized; many thresholds remain context-specific by segment, ACV range, and implementation complexity.
- Procurement timing datasets are unevenly distributed by region and company size; guidance should be treated as directional unless matched to target customer profile.
- Some AI pilot scaling claims rely on press releases or vendor surveys rather than peer-reviewed causal studies; confidence labeling remains important.
# Research: pricing-pilot-packaging

**Skill path:** `flexus-client-kit/flexus_simple_bots/strategist/skills/pricing-pilot-packaging/`
**Bot:** strategist
**Research date:** 2026-03-05
**Status:** complete

---

## Context

This skill designs commercial terms for early pilots: what the buyer pays before full production, what measurable outcomes define pilot success, and what commercial event converts the pilot into standard paid terms. It solves a high-friction transition problem: many pilots prove technical feasibility but fail to convert because the commercial path, evidence rules, legal path, and stakeholder ownership were not defined up front.

The existing `SKILL.md` already captures core pilot structures (`free_loi`, `paid_discounted`, `success_based`, `poc_to_expansion`) and emphasizes that pilot price is not final price. This research expands that foundation with 2024-2026 guidance on (1) conversion-first pilot design, (2) practical tool/API stacks, (3) signal-quality standards for interpreting pilot outcomes, and (4) failure patterns that trap teams in pilot purgatory.

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
- Volume: findings section is within the 800-4000 word target and synthesis is concise

Quality-gate result for this draft:
- Endpoint examples are limited to documented public APIs (Stripe, LaunchDarkly, PostHog, Segment, RudderStack, HubSpot, PandaDoc, Typeform).
- Contradictions are called out in Angles and Synthesis (paid vs free pilots, pilot duration norms, single KPI vs multi-KPI decisions).
- Findings volume is substantial; `Draft Content for SKILL.md` is intentionally the largest section.

---

## Research Angles

Each angle should be researched by a separate sub-agent. Add more angles if the domain requires it.

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

Pilot packaging guidance in 2024-2026 has shifted from "run a pilot and evaluate later" to "define commercial conversion conditions before kickoff." Practical playbooks now treat commercial trigger design as Gate 0: teams should pre-agree on the exact decision rule (for example baseline -> target -> date -> owner -> action). This shift appears repeatedly in enterprise AI pilot guidance and "pilot purgatory" analyses: technically successful pilots still fail commercially when no conversion path was contracted up front.

Methodologically, high-performing pilot motions now use a constrained scope formula: one primary use case, one accountable business owner, one fixed window, and a checkpoint cadence. Most guidance converges on time-boxing (often 30-90 days for enterprise motions), with extensions treated as explicit re-scoping events rather than silent continuation. This reduces drift, protects seller and buyer attention, and keeps legal/procurement momentum synchronized with pilot evidence collection.

Practitioner content in 2025 also emphasizes that pilot pricing model selection should be explicit and context-driven rather than doctrinal. Common options include paid-with-credit, reduced-scope paid pilot, success-based/refund structures, and POC-to-expansion transitions. The useful pattern is not "one right structure" but a decision tree based on implementation effort, buyer risk appetite, procurement friction, and confidence in measurable ROI during the pilot window.

Another key change is the rise of structured pilot contracting artifacts (not ad hoc redlines). Common Paper's 2025 pilot agreement standard and related commentary reflect a default architecture: evaluation scope, short period, "as-is" risk posture, clear termination rights, and a defined bridge to production terms. In parallel, CISA's secure-by-design procurement guidance makes security and software assurance requirements more explicit in acquisition workflows. Practically, this means pilot packaging now needs a parallel track for legal/security/procurement from day one.

A tension remains between "never run free pilots" sales advice and legal frameworks that support both free and paid pilot structures. The research suggests treating free pilots as a specific strategic instrument (reference customers, narrow scope, strict LOI + decision date), not as a default offer. In all cases, commitment quality is driven less by "free vs paid" alone and more by scope discipline, named decision ownership, and pre-committed conversion criteria.

**Sources:**
- https://nedllabs.com/blog/escaping-pilot-purgatory
- https://www.techtarget.com/searchcio/feature/How-to-run-a-successful-IT-pilot-program
- https://www.techtarget.com/searchcio/feature/Steps-to-design-an-effective-AI-pilot-project
- https://dowhatmatter.com/guides/pilot-pricing-seed-saas
- https://www.getmonetizely.com/articles/how-to-structure-enterprise-pilot-program-pricing-effective-proof-of-concept-strategies
- https://commonpaper.com/standards/pilot-agreement/
- https://commonpaper.com/standards/pilot-agreement/1.1/
- https://commonpaper.com/release-notes/common-paper-pilot-agreement-v1-1/
- https://www.cisa.gov/sites/default/files/2024-07/PDM24050%20Software%20Acquisition%20Guide%20for%20Government%20Enterprise%20ConsumersV2_508c.pdf
- https://www.bain.com/insights/updating-enterprise-technology-to-scale-to-ai-everywhere-tech-report-2024/
- https://www.bain.com/insights/executive-survey-ai-moves-from-pilots-to-production/
- https://www.deloitte.com/nl/en/about/press-room/state-of-ai-in-the-enterprise-2026.html

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

The strongest 2024-2026 pattern is a composable stack instead of monolithic "pricing platform" adoption. Teams usually combine feature flagging/entitlement controls, product analytics, billing/quotes, CRM, and proposal/feedback tooling. For pilot packaging, this allows account-specific offers and controlled migration to production terms without hard-coding one-off commercial logic.

For entitlement and pilot variant gating, LaunchDarkly and PostHog are practical options. Verified LaunchDarkly REST paths include `GET /api/v2/flags/{projectKey}`, `POST /api/v2/flags/{projectKey}`, and `GET /api/v2/flags/{projectKey}/{featureFlagKey}` via official OpenAPI. PostHog documents a public flag-evaluation endpoint at `POST https://{region}.i.posthog.com/flags?v=2` used for feature flags, experimentation, early-access gating, and survey display logic. OpenFeature has matured as a vendor-neutral standard layer to reduce lock-in risk when switching flag providers.

For pilot funnel instrumentation, Amplitude HTTP V2 and Segment/RudderStack HTTP ingestion are concrete standards. Amplitude documents `POST https://api2.amplitude.com/2/httpapi` (EU variant available), with event and payload constraints. Segment standard server endpoints include `POST /v1/track`, `POST /v1/identify`, and `POST /v1/batch`, with documented request-size and throughput guidance. RudderStack mirrors Segment-style ingestion (`/v1/track`, `/v1/identify`, `/v1/batch`) and is often selected for hosting/cost flexibility. A consistent event contract across tools is more important than vendor choice.

For commercial execution, Stripe is the dominant programmable billing layer in this research set: pricing setup (`POST /v1/prices`), quote and acceptance flow (`POST /v1/quotes`, `POST /v1/quotes/:id/finalize`, `POST /v1/quotes/:id/accept`), subscription lifecycle (`POST /v1/subscriptions`, `POST /v1/subscription_schedules`), and usage monetization (`POST /v1/billing/meter_events`). Stripe also documents global and endpoint-specific limits and strongly supports idempotency patterns for safe retries.

For pipeline and proposal ops, HubSpot CRM Deals API (`/crm/v3/objects/deals`) supports stage synchronization of pilot->quote->contract states, while PandaDoc APIs support proposal document generation/send workflows. Typeform responses APIs are commonly used for structured qualitative pilot feedback, but low per-second limits make webhooks or queued polling necessary for robust automation at volume.

Practical stack recommendation for this skill domain: (1) entitlement flags (LaunchDarkly or PostHog via OpenFeature abstraction), (2) event routing (Segment or RudderStack) into analytics, (3) billing/quote truth in Stripe, (4) CRM stage ownership in HubSpot, and (5) structured feedback capture (Typeform). The anti-pattern is direct point-to-point integrations without an event contract, which fragments analysis and breaks pilot decision confidence.

**Sources:**
- https://app.launchdarkly.com/api/v2/openapi.json
- https://support.launchdarkly.com/hc/en-us/articles/22328238491803-Error-429-Too-Many-Requests-API-Rate-Limit
- https://openfeature.dev/specification/
- https://openfeature.dev/docs/reference/concepts/provider/
- https://www.cncf.io/blog/2024/03/19/announcing-the-openfeature-web-sdk-v1/
- https://posthog.com/docs/api/flags
- https://posthog.com/docs/api
- https://amplitude.com/docs/apis/analytics/http-v2
- https://segment.com/docs/connections/sources/catalog/libraries/server/http-api/
- https://www.rudderstack.com/docs/sources/event-streams/http/
- https://docs.stripe.com/api/prices
- https://docs.stripe.com/api/quotes
- https://docs.stripe.com/api/subscriptions
- https://docs.stripe.com/api/subscription_schedules
- https://docs.stripe.com/billing/subscriptions/usage-based/recording-usage-api
- https://docs.stripe.com/rate-limits
- https://developers.hubspot.com/docs/api-reference/crm-deals-v3/guide
- https://developers.hubspot.com/docs/api/usage-details
- https://developers.pandadoc.com/reference/create-document
- https://developers.pandadoc.com/reference/limits
- https://www.typeform.com/developers/responses/reference/retrieve-responses/

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

The most practical 2024-2026 signal-quality lesson is that "pilot launched" is not a useful metric by itself. TestBox's 2024 dataset highlights a gating signal: many POCs are never meaningfully accessed, and non-accessed pilots should be treated as process failures rather than product-evidence failures. This supports a two-stage interpretation model: stage 1 verifies engagement reality (access + depth + stakeholder breadth), stage 2 interprets business outcomes.

Depth and breadth signals matter more than raw activity counts. Compared with closed-lost deals, closed-won pilot motions in the available datasets show stronger multi-session engagement and broader stakeholder participation. This means the skill should not declare success from a single champion's usage spike; it should require cross-functional engagement and repeat use across the agreed evaluation period.

Benchmarking requires segmentation and denominator discipline. Conversion benchmarks in 2026 reports vary substantially by motion (free trial vs freemium vs card-required) and by funnel denominator (visitor->signup vs signup->paid). Without explicit denominator and maturity window, teams can create false confidence or false pessimism. The skill should force explicit denominator, cohort maturity logic, and per-segment comparison before any pricing/package recommendation.

Experiment validity concerns from Statsig, Eppo, Optimizely, GrowthBook, and LaunchDarkly guidance are highly relevant to pilot packaging decisions. Underpowered samples inflate winner estimates; rare-event outcomes can demand much longer runtime; and multiple comparisons without correction raise false-positive risk. Practical implication: pilot evidence should be graded by methodological quality (power check, peeking control, multiple-testing control, segmentation) before being used to set production pricing.

Another important interpretation signal is concentration of value behavior. Pendo's benchmark finding that a small share of features typically drives most usage suggests that pilot package decisions should track adoption of core value workflows, not total click volume. This helps avoid over-valuing superficial engagement while under-valuing high-leverage outcomes tied to conversion readiness.

The combined implication for this skill: require an evidence score before commercial recommendation. If evidence quality is low, output should be "continue learning with scoped adjustment," not "set production price." This avoids overfitting pricing decisions to noisy pilot data.

**Sources:**
- https://www.testbox.com/post/poc-research
- https://chartmogul.com/reports/saas-conversion-report/
- https://help.chartmogul.com/article/219-chart-trial-to-paid-conversion-rate
- https://chartmogul.helpscoutdocs.com/article/225-making-trial-to-paid-conversion-rates-more-meaningful-with-cohorts
- https://docs.statsig.com/experiments-plus/power-analysis
- https://docs.geteppo.com/guides/advanced-experimentation/running-well-powered-experiments
- https://docs.geteppo.com/statistics/cuped/
- https://www.optimizely.com/insights/blog/sample-size-calculations-for-experiments/
- https://docs.growthbook.io/statistics/multiple-corrections
- https://launchdarkly.com/docs/guides/statistical-methodology/mcc
- https://amplitude.com/benchmarks/technology-b2b-saas
- https://www.pendo.io/pendo-blog/product-benchmarks/
- https://www.saas-capital.com/research/private-saas-company-growth-rate-benchmarks/
- https://www.saas-capital.com/research/saas-retention-benchmarks-for-private-b2b-companies/
- https://stripe.com/resources/more/pricing-experiments

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

A repeat failure mode is the "demo-success fallacy": teams report positive pilot sentiment, but there is no pre-agreed production action if criteria are met. This creates pilot purgatory where both parties wait for one another to define next steps. Detection signal: no signed conversion trigger, no named economic buyer commitment, and no scheduled decision meeting.

Another common failure is vague or activity-only success criteria ("users liked it", "engagement looked strong"). Without baseline, target, measurement method, and decision rule, the same data can be interpreted in opposing ways. Detection signal: the pilot brief has qualitative aspirations but no quantitative thresholds or no pre-committed owner for decision adjudication.

Late involvement of procurement/security/legal frequently kills otherwise successful pilots. Research and enterprise commentary in 2024-2026 repeatedly show scaling bottlenecks from governance, compliance, and commercial process lag. Detection signal: security questionnaire and MSA redlines start near pilot end instead of kickoff month.

Commercial anti-patterns also include open-ended free pilots, discount sprawl, and misaligned compensation incentives. If pilots can be extended indefinitely without decision pressure, stakeholder urgency drops and signal quality erodes. If reps close pilots through ad hoc discounts with no guardrails, transition to standard pricing becomes politically and operationally difficult.

A technical-commercial anti-pattern is missing the pilot-to-production economics model. Teams validate workflow outcomes but do not quantify production TCO (integration, support, migration, lock-in/exit cost), then stall during conversion. Detection signal: production budget owner is undefined; no documented estimate for post-pilot operating cost; no migration or termination assumptions.

Good output patterns therefore include: explicit commercial trigger language, MAP governance with owners/dates, risk-control checklist from day one, finite extension policy, and evidence-quality scoring before pricing recommendations. Bad outputs are narrative-heavy, criteria-light, and avoid hard conversion commitments.

**Sources:**
- https://www.bcg.com/press/24october2024-ai-adoption-in-2024-74-of-companies-struggle-to-achieve-and-scale-value
- https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027
- https://www2.deloitte.com/us/en/pages/about-deloitte/articles/press-releases/state-of-generative-ai.html
- https://aws.amazon.com/blogs/enterprise-strategy/generative-ai-getting-proofs-of-concept-to-production
- https://www.businesswire.com/news/home/20241009142556/en/6sense-Launches-2024-Buyer-Experience-Report-Unveiling-Global-B2B-Buyer-Trends
- https://www.outreach.io/resources/blog/mutual-action-plans
- https://www.salesforce.com/blog/mutual-action-plan/?bc=HA
- https://docs.github.com/en/enterprise-cloud@latest/copilot/tutorials/roll-out-at-scale/measure-success
- https://commonpaper.com/standards/pilot-agreement/
- https://www.morganlewis.com/blogs/sourcingatmorganlewis/2024/04/transitioning-from-traditional-software-licensing-to-saas-models-key-considerations-in-contracts-and-business-operations
- https://www.vendr.com/insights/saas-trends-report-2025
- https://www.simon-kucher.com/en/insights/our-top-5-takeaways-running-price-increase-campaigns-b2b-clients-2024

---

### Angle 5+: Contracting, Security, and Procurement Readiness
> Additional domain angle: pilot packaging in enterprise contexts fails when contract/security/procurement work is deferred. This angle focuses on transition readiness and compliance-aware packaging.

**Findings:**

Pilot terms are not a smaller version of production terms; they are a different contract shape with different risk posture. Common Paper's pilot standard (v1.1, 2025) reinforces this with evaluation-focused scope, short term, constrained liabilities, and easier termination. This is useful, but conversion readiness requires a companion transition rider so the parties do not restart contracting from zero at pilot end.

CISA's 2024 software acquisition guide provides a practical secure-by-demand model that can be translated into pilot packaging checkpoints: supplier attestation, control evidence requests, and explicit handling of gaps/remediation plans. For strategist output, this means the pilot package should include what assurance evidence is required by when, not only business KPI targets.

Enterprise legal commentary in 2024 also highlights transition risks from legacy licensing expectations to SaaS and AI service models. Key issue: if data rights, service levels, and post-termination assistance are not framed early, conversion cycles lengthen and may fail despite successful pilot outcomes.

The actionable result for this skill is a dual-track timeline: business-value evaluation and commercial-readiness execution in parallel. A pilot should not be considered "successful" unless both tracks clear minimum thresholds by the decision date.

**Sources:**
- https://commonpaper.com/standards/pilot-agreement/
- https://commonpaper.com/standards/pilot-agreement/1.1/
- https://commonpaper.com/release-notes/common-paper-pilot-agreement-v1-1/
- https://www.cisa.gov/sites/default/files/2024-07/PDM24050%20Software%20Acquisition%20Guide%20for%20Government%20Enterprise%20ConsumersV2_508c.pdf
- https://www.morganlewis.com/blogs/sourcingatmorganlewis/2024/04/transitioning-from-traditional-software-licensing-to-saas-models-key-considerations-in-contracts-and-business-operations

---

## Synthesis

Across sources, the strongest pattern is that pilot pricing and packaging is now treated as a conversion system, not a temporary discount exercise. Teams that pre-wire the commercial decision path (trigger, owner, timeline, contract bridge) outperform teams that only optimize pilot experience. This aligns with "pilot purgatory" analyses and enterprise AI scaling reports: conversion fails less from missing enthusiasm and more from missing decision architecture.

The tooling landscape supports this conversion-first posture. Instead of inventing bespoke systems, practitioners combine proven APIs: flags for entitlement control, analytics for evidence, billing for commercial truth, CRM for stage governance, and proposal/feedback systems for operational continuity. The technical detail that matters most is not any single vendor; it is a shared event contract and rate-limit-safe orchestration so commercial state is consistent across systems.

Signal quality is the largest blind spot in many pilot motions. Multiple sources warn that noisy or immature data can produce false confidence: denominator mistakes, underpowered samples, rare-event variance, and uncorrected multiple comparisons. The practical answer is to grade evidence quality before making pricing decisions. This skill should output explicit confidence states, not binary success claims from weak data.

The main contradiction is free vs paid pilot doctrine. Some sales operators push paid-only to preserve commitment; legal and contracting frameworks continue to support both free and paid structures. The synthesis resolution is contextual: free can work when highly scoped and tied to LOI + strict decision gates; paid is generally stronger for commitment but is not sufficient by itself. Another contradiction is pilot duration (short legal windows vs enterprise implementation windows), resolved by enforcing checkpointed time-boxes and explicit extension policies.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.
> Be specific: "Add X to methodology", "Replace Y tool with Z", "Add anti-pattern: ...", "Schema field X should be enum [...]".
> Each item here must have a corresponding draft in the section below.

- [x] Add a conversion-first "Gate 0" methodology section requiring pre-signed decision rules before pilot kickoff.
- [x] Add a pilot structure selection decision tree (free LOI vs paid discounted vs success-based vs POC-to-expansion) with context-based criteria.
- [x] Add a dual-track operating model: business evidence track and legal/security/procurement track running in parallel.
- [x] Add a signal-quality rubric (power check, denominator definition, segmentation, multiple-testing control) and confidence bands.
- [x] Expand Available Tools guidance with verified external API integration references and rate-limit/idempotency notes.
- [x] Add named anti-pattern warning blocks with detection signal, consequence, and mitigation steps.
- [x] Expand schema to include `success_plan`, `decision_governance`, `commercial_trigger`, `transition_plan`, `risk_controls`, and `evidence_quality`.
- [x] Add a strict output checklist requiring finite timelines, MAP ownership, and conversion/exit outcomes in every package.

---

## Draft Content for SKILL.md

> This is the most important section. For every recommendation above, write the **actual text** that should go into SKILL.md — as if you were writing it. Be verbose and comprehensive. The future editor will cut what they don't need; they should never need to invent content from scratch.
>
> Rules:
> - Write full paragraphs and bullet lists, not summaries
> - For methodology changes: write the actual instruction text in second person ("You should...", "Before doing X, always verify Y")
> - For schema changes: write the full JSON fragment with all fields, types, descriptions, enums, and `additionalProperties: false`
> - For anti-patterns: write the complete warning block including detection signal and mitigation steps
> - For tool recommendations: write the actual `## Available Tools` section text with real method syntax
> - Do not hedge or abbreviate - if a concept needs 3 paragraphs to explain properly, write 3 paragraphs
> - Mark sections with `### Draft: <topic>` headers so the editor can navigate

### Draft: Conversion-first methodology (Gate 0 + execution flow)

---
### Conversion-first pilot design

Before you design price numbers, define the conversion mechanism. A pilot is not successful when users "like it"; it is successful when both parties can execute a pre-agreed commercial decision with minimal ambiguity. If you skip this, you will produce attractive pilot terms that still fail to convert.

You must create a `Gate 0` decision record before pilot kickoff. `Gate 0` is complete only when the following are agreed in writing: (a) baseline and target metrics, (b) measurement method and data owner, (c) decision date, (d) required signatories for conversion, and (e) conversion action if targets are met (contract type, price path, transition timeline).

Step-by-step:
1. **Define one primary value thesis.** Write one measurable business outcome for the pilot window. Keep this singular; add guardrail metrics separately. If you add multiple primary outcomes, decision accountability collapses and every side can claim a different interpretation.
2. **Set baseline, target, and timeframe.** Record current baseline, target at pilot end, and observation window boundaries. If baseline is unavailable, the first pilot phase must be baseline capture, and you should not claim commercial success before baseline is established.
3. **Attach decision ownership.** Name the economic buyer, business owner, and decision meeting date at kickoff. If ownership is unresolved, mark package risk as high and recommend pilot deferral until ownership is explicit.
4. **Bind commercial action to evidence.** Define what happens if target is hit, partially hit, or missed. Include at least three branches: `convert`, `extend with narrowed scope`, `stop`.
5. **Time-box and checkpoint.** Use finite pilot duration and checkpoint cadence (for example weekly or bi-weekly). If the pilot needs extension, require a formal change order with new dates and revised scope.

If the buyer requests "run first, decide later," you should push back and explain that without pre-committed conversion logic, evidence loses decision value. If the buyer still declines commitment, recommend a narrowly scoped discovery pilot with explicit LOI expectations and lower confidence in conversion probability.

Do NOT:
- Start pilot execution without a signed decision rule.
- Allow open-ended extensions without fee/scope reset.
- Treat technical enablement milestones as substitutes for business conversion criteria.
---

### Draft: Pilot structure selection decision tree

---
### Selecting the pilot structure

You should choose pilot structure based on risk, effort, and procurement reality, not habit. Use this sequence every time:

1. **Assess implementation lift and customer switching cost.** If onboarding and integration effort are significant, default away from "free/no-commitment" because each party must fund real work. If effort is light and you need logo acquisition, a constrained free LOI structure can be acceptable.
2. **Assess measurement confidence.** If value can be measured clearly in the pilot window, `success_based` and `paid_discounted` models are viable. If value measurement is noisy or delayed, use `poc_to_expansion` with staged commitments and explicit re-evaluation.
3. **Assess procurement friction.** If buyer procurement can process paid pilots quickly, use paid structure to increase commitment quality. If procurement timing blocks near-term start, use a short, tightly scoped free LOI pilot with parallel procurement workstream and pre-scheduled paid conversion path.
4. **Assess strategic importance of account.** For lighthouse accounts, temporary concessions can be rational, but only with explicit expiry and standard-term transition plan.

Structure guidance:
- **`free_loi`**: allowed only with written LOI, strict scope, strict timeline, named decision date, and explicit conversion branch.
- **`paid_discounted`**: preferred default when measurement and procurement are feasible; include discount reference to standard price and expiration date.
- **`success_based`**: use only when metric instrumentation and dispute-resolution rules are clear; specify refund/credit mechanics in detail.
- **`poc_to_expansion`**: use when uncertainty is high; define phase boundaries and pricing uplift rule before phase 1 starts.

Do NOT choose structure solely to maximize pilot signature rate. The optimization target is conversion probability with defensible margin, not pilot count.
---

### Draft: Success criteria, signal quality, and interpretation rules

---
### Evidence standard and confidence grading

You must grade pilot evidence before recommending production pricing. A pilot with weak evidence quality should produce a learning recommendation, not a pricing decision.

Use this confidence rubric:
- **High confidence (85-100):** denominator and window are predeclared; power/MDE checked on target segment; multiple-testing control applied; segmentation complete; business impact linked.
- **Directional confidence (70-84):** evidence is mostly solid but one methodological element is weak (for example limited segmentation or marginal sample size).
- **Low confidence (50-69):** useful for hypothesis refinement only; do not lock long-term commercial terms.
- **Insufficient (<50):** decision should be defer/reshape/stop, not convert.

Required interpretation rules:
1. Always separate `pilot_accessed` accounts from `pilot_not_accessed` accounts before calculating success rates.
2. Report both `visitor->signup` and `signup->paid` denominators when relevant; never report one without defining denominator.
3. Use cohort maturity windows; do not treat immature cohorts as final conversion outcomes.
4. If multiple metrics or treatment paths are used for decisioning, apply explicit multiple-comparison control.
5. Segment analysis by ICP and commercial motion before recommending general pricing changes.

You should include a short narrative for each recommendation explaining whether observed outcomes likely reflect signal, noise, or mixed evidence. If uncertainty is high, specify what additional data would change the recommendation.

Do NOT:
- Infer broad willingness-to-pay from one champion's usage.
- Declare success from activity volume without core-value behavior evidence.
- Ignore denominator changes between cohorts.
---

### Draft: Dual-track execution (commercial + compliance readiness)

---
### Parallel workstreams required for conversion

You must run two tracks in parallel from kickoff:

1. **Value evidence track**: instrumentation, baseline capture, checkpoint reviews, KPI progress, qualitative stakeholder feedback.
2. **Commercial readiness track**: security review, legal redlines, procurement onboarding, paper process, contract transition prep.

Your package is incomplete if either track is missing. A technically successful pilot with unresolved commercial-readiness tasks is not conversion-ready.

Minimum commercial-readiness checklist:
- Security owner named and due date for review completion.
- Data classification and handling requirements documented.
- DPA/SLA requirements identified with owner and target completion date.
- Procurement workflow started with required vendor onboarding artifacts.
- Transition rider drafted with production contract pathway.

Decision rules:
- If value track passes and commercial track passes: recommend conversion with target terms.
- If value track passes but commercial track is blocked: recommend conditional conversion with explicit unblock plan and deadline.
- If value track fails but commercial track passes: recommend stop or narrow redesign; do not force conversion.
- If both fail: recommend stop, capture lessons, and avoid extension unless a materially different scope is defined.
---

### Draft: Available Tools section text (paste-ready)

---
## Available Tools

Use these internal policy and artifact tools first to ground your output in existing strategy context:

```python
flexus_policy_document(op="activate", args={"p": "/strategy/pricing-tiers"})
flexus_policy_document(op="activate", args={"p": "/strategy/offer-design"})
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})
write_artifact(artifact_type="pilot_package", path="/strategy/pilot-package", data={...})
```

When this skill is used in systems that integrate external commercial tooling, these verified API references are the practical defaults:

```http
# Stripe (quotes + conversion path)
POST https://api.stripe.com/v1/quotes
POST https://api.stripe.com/v1/quotes/{quote_id}/finalize
POST https://api.stripe.com/v1/quotes/{quote_id}/accept
POST https://api.stripe.com/v1/prices
POST https://api.stripe.com/v1/subscriptions
POST https://api.stripe.com/v1/subscription_schedules
POST https://api.stripe.com/v1/billing/meter_events
```

```http
# LaunchDarkly (pilot entitlement/offer flag management)
GET  https://app.launchdarkly.com/api/v2/flags/{projectKey}
POST https://app.launchdarkly.com/api/v2/flags/{projectKey}
GET  https://app.launchdarkly.com/api/v2/flags/{projectKey}/{featureFlagKey}
```

```http
# PostHog (runtime flag evaluation for offer variants)
POST https://{region}.i.posthog.com/flags?v=2
```

```http
# Segment and RudderStack (event contract ingestion)
POST https://api.segment.io/v1/track
POST https://api.segment.io/v1/identify
POST https://api.segment.io/v1/batch
POST https://<DATA_PLANE_URL>/v1/track
POST https://<DATA_PLANE_URL>/v1/identify
POST https://<DATA_PLANE_URL>/v1/batch
```

```http
# HubSpot deals and Typeform responses
POST https://api.hubapi.com/crm/v3/objects/deals
GET  https://api.hubapi.com/crm/v3/objects/deals/{dealId}
GET  https://api.typeform.com/forms/{form_id}/responses
```

Operational guidance:
- Respect provider rate limits and queue outbound writes for retry safety.
- Use idempotency keys where supported (especially billing writes).
- Keep one canonical event contract so pricing interpretation is consistent across analytics, CRM, and billing systems.
- Never let integration detail override decision clarity: commercial trigger definitions come first.
---

### Draft: Anti-pattern warning blocks (paste-ready)

---
### WARNING: Pilot Purgatory Design
**What it looks like:** pilot starts with broad goals, no signed decision trigger, and no named economic buyer commitment at kickoff.  
**Detection signal:** your package cannot answer "what exact contract action occurs on decision date if target is hit?"  
**Consequence if missed:** strong pilot sentiment but no conversion event; repeated "follow-up alignment" cycles; margin erosion from extensions.  
**Mitigation steps:**  
1. Create Gate 0 record (baseline, target, method, decision owner, decision date, commercial action).  
2. Require buyer sign-off on conversion branches (`convert`, `extend-narrow`, `stop`).  
3. Schedule conversion decision meeting at kickoff, not at pilot end.

### WARNING: Activity-only Success Criteria
**What it looks like:** success is defined as usage volume, demo completion, or subjective satisfaction without business KPI targets.  
**Detection signal:** no baseline-to-target mapping and no denominator definition in outcome metrics.  
**Consequence if missed:** contradictory interpretations and stalled pricing decisions; weak evidence is mistaken for willingness-to-pay.  
**Mitigation steps:**  
1. Define one primary business KPI plus guardrails.  
2. Require baseline, target, measurement method, and maturity window.  
3. Grade evidence confidence before any pricing recommendation.

### WARNING: Late Commercial Readiness
**What it looks like:** legal/security/procurement starts near pilot end after product value is already demonstrated.  
**Detection signal:** MSA, DPA, security review, or procurement onboarding has no kickoff owner/date.  
**Consequence if missed:** "successful" pilot fails to convert due to process lag and redline restart.  
**Mitigation steps:**  
1. Run value and commercial-readiness tracks in parallel from day one.  
2. Add milestone owners and due dates in a MAP.  
3. Treat unresolved commercial-readiness items as blocking conditions for conversion.

### WARNING: Discount Sprawl at Handoff
**What it looks like:** ad hoc pilot discounts close signatures but no documented transition to standard terms.  
**Detection signal:** high variance in discount depth, no expiration logic, no approval guardrails.  
**Consequence if missed:** difficult renewal conversations, inconsistent list-price credibility, comp-driven margin leakage.  
**Mitigation steps:**  
1. Document discount bands and exception approvals.  
2. Define expiry dates and conversion pricing formula before pilot starts.  
3. Include renewal escalation logic tied to standard packaging.

### WARNING: Underpowered Decisioning
**What it looks like:** pricing/package decisions based on small noisy cohorts or immature time windows.  
**Detection signal:** no power/MDE check, no cohort maturity rule, no multiple-comparison control despite many metrics.  
**Consequence if missed:** false-positive wins and overconfident production pricing.  
**Mitigation steps:**  
1. Add power check and MDE assumptions to package metadata.  
2. Declare denominator/window before analysis.  
3. Use segment-normalized interpretation and confidence grading.
---

### Draft: Output quality checklist for this skill

---
Before finalizing `pilot_package`, verify all of the following:
- You defined one primary value thesis and one named decision owner.
- You included explicit conversion and non-conversion branches.
- You time-boxed pilot duration and defined extension policy.
- You listed checkpoint cadence and MAP owners for each milestone.
- You specified baseline, target, denominator, and maturity window.
- You included evidence confidence and uncertainty notes.
- You documented security/legal/procurement readiness items and due dates.
- You recorded conversion pricing path with expiry and transition timeline.

If any item is missing, output should be marked incomplete and should include exactly what information is required next.
---

### Draft: Schema additions

> Write the full JSON Schema fragment for any new or modified artifact fields.
> Include field descriptions, enums, required arrays, and additionalProperties constraints.

```json
{
  "pilot_package": {
    "type": "object",
    "required": [
      "created_at",
      "target_segment",
      "pilot_structure",
      "pilot_duration_days",
      "pilot_scope",
      "pricing_terms",
      "success_plan",
      "decision_governance",
      "commercial_trigger",
      "conversion_terms",
      "transition_plan",
      "risk_controls",
      "evidence_quality"
    ],
    "additionalProperties": false,
    "properties": {
      "created_at": {
        "type": "string",
        "description": "ISO-8601 timestamp indicating when this pilot package was generated."
      },
      "target_segment": {
        "type": "string",
        "description": "Segment or ICP label this pilot package is designed for."
      },
      "pilot_structure": {
        "type": "string",
        "enum": [
          "free_loi",
          "paid_discounted",
          "success_based",
          "poc_to_expansion"
        ],
        "description": "Commercial structure used during pilot."
      },
      "pilot_duration_days": {
        "type": "integer",
        "minimum": 14,
        "maximum": 180,
        "description": "Planned pilot duration in days. Must be finite and explicitly time-boxed."
      },
      "pilot_scope": {
        "type": "object",
        "required": [
          "primary_use_case",
          "included_teams",
          "included_data_sources",
          "out_of_scope_items"
        ],
        "additionalProperties": false,
        "properties": {
          "primary_use_case": {
            "type": "string",
            "description": "Single highest-priority workflow the pilot is intended to validate."
          },
          "included_teams": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Teams explicitly in scope for pilot execution and measurement."
          },
          "included_data_sources": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Data systems approved for use during pilot."
          },
          "out_of_scope_items": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Explicitly excluded use cases or integrations to prevent scope creep."
          }
        }
      },
      "pricing_terms": {
        "type": "object",
        "required": [
          "pilot_price",
          "standard_price_reference",
          "discount_pct",
          "payment_timing",
          "fee_credit_policy"
        ],
        "additionalProperties": false,
        "properties": {
          "pilot_price": {
            "type": [
              "number",
              "string"
            ],
            "description": "Pilot fee amount or structured expression when scenario-based."
          },
          "standard_price_reference": {
            "type": "number",
            "description": "Reference production/list price used to calculate concession depth."
          },
          "discount_pct": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Pilot discount as decimal relative to standard price reference."
          },
          "payment_timing": {
            "type": "string",
            "enum": [
              "upfront",
              "milestone_split",
              "end_of_pilot",
              "on_success"
            ],
            "description": "When pilot fee is collected."
          },
          "fee_credit_policy": {
            "type": "string",
            "enum": [
              "no_credit",
              "partial_credit",
              "full_credit_on_conversion"
            ],
            "description": "Whether and how pilot fees credit toward production contract."
          }
        }
      },
      "success_plan": {
        "type": "object",
        "required": [
          "evaluation_window_start",
          "evaluation_window_end",
          "primary_business_kpi",
          "baseline_value",
          "target_value",
          "measurement_method",
          "decision_rule",
          "guardrails"
        ],
        "additionalProperties": false,
        "properties": {
          "evaluation_window_start": {
            "type": "string",
            "description": "ISO-8601 start timestamp for evidence collection window."
          },
          "evaluation_window_end": {
            "type": "string",
            "description": "ISO-8601 end timestamp for evidence collection window."
          },
          "primary_business_kpi": {
            "type": "string",
            "description": "Main business outcome metric used for pilot decision."
          },
          "baseline_value": {
            "type": "string",
            "description": "Pre-pilot baseline for the primary KPI."
          },
          "target_value": {
            "type": "string",
            "description": "Required KPI target for conversion branch."
          },
          "measurement_method": {
            "type": "string",
            "description": "How KPI is computed, including denominator and source system."
          },
          "decision_rule": {
            "type": "string",
            "description": "Explicit if/else rule that maps observed outcomes to convert/extend/stop."
          },
          "guardrails": {
            "type": "array",
            "items": {
              "type": "object",
              "required": [
                "metric",
                "threshold",
                "direction"
              ],
              "additionalProperties": false,
              "properties": {
                "metric": {
                  "type": "string",
                  "description": "Guardrail metric name (e.g., churn risk, support load, quality score)."
                },
                "threshold": {
                  "type": "string",
                  "description": "Allowed bound for this guardrail."
                },
                "direction": {
                  "type": "string",
                  "enum": [
                    "min",
                    "max"
                  ],
                  "description": "Whether metric must stay above minimum or below maximum threshold."
                }
              }
            },
            "description": "Non-primary metrics that can block conversion if violated."
          }
        }
      },
      "decision_governance": {
        "type": "object",
        "required": [
          "executive_sponsor",
          "economic_buyer",
          "security_owner",
          "legal_owner",
          "procurement_owner",
          "checkpoint_cadence",
          "decision_meeting_date"
        ],
        "additionalProperties": false,
        "properties": {
          "executive_sponsor": {
            "type": "string",
            "description": "Executive owner accountable for pilot sponsorship."
          },
          "economic_buyer": {
            "type": "string",
            "description": "Final commercial decision maker for conversion."
          },
          "security_owner": {
            "type": "string",
            "description": "Owner responsible for security/compliance review completion."
          },
          "legal_owner": {
            "type": "string",
            "description": "Owner responsible for contract/legal workflow."
          },
          "procurement_owner": {
            "type": "string",
            "description": "Owner responsible for purchase workflow and vendor onboarding."
          },
          "checkpoint_cadence": {
            "type": "string",
            "enum": [
              "weekly",
              "biweekly",
              "custom"
            ],
            "description": "Pilot checkpoint frequency."
          },
          "decision_meeting_date": {
            "type": "string",
            "description": "ISO-8601 date for formal pilot outcome decision."
          }
        }
      },
      "commercial_trigger": {
        "type": "object",
        "required": [
          "trigger_type",
          "trigger_condition",
          "target_contract_type",
          "price_at_conversion",
          "price_valid_until"
        ],
        "additionalProperties": false,
        "properties": {
          "trigger_type": {
            "type": "string",
            "enum": [
              "kpi_threshold",
              "milestone_completion",
              "joint_signoff"
            ],
            "description": "Primary trigger mode for production conversion."
          },
          "trigger_condition": {
            "type": "string",
            "description": "Concrete condition text for conversion trigger."
          },
          "target_contract_type": {
            "type": "string",
            "description": "Commercial contract type activated at conversion."
          },
          "price_at_conversion": {
            "type": "number",
            "description": "Production price that becomes active when trigger is satisfied."
          },
          "price_valid_until": {
            "type": "string",
            "description": "ISO-8601 expiration date for conversion price offer."
          }
        }
      },
      "conversion_terms": {
        "type": "object",
        "required": [
          "conversion_trigger",
          "conversion_price",
          "transition_timeline"
        ],
        "additionalProperties": false,
        "properties": {
          "conversion_trigger": {
            "type": "string",
            "description": "Human-readable summary of trigger rule for conversion."
          },
          "conversion_price": {
            "type": "number",
            "description": "Agreed commercial price once converted."
          },
          "transition_timeline": {
            "type": "string",
            "description": "Timing for moving from pilot terms to production terms."
          }
        }
      },
      "transition_plan": {
        "type": "object",
        "required": [
          "map_milestones",
          "security_track",
          "legal_track",
          "procurement_track"
        ],
        "additionalProperties": false,
        "properties": {
          "map_milestones": {
            "type": "array",
            "items": {
              "type": "object",
              "required": [
                "milestone",
                "owner",
                "due_date"
              ],
              "additionalProperties": false,
              "properties": {
                "milestone": {
                  "type": "string",
                  "description": "Named MAP milestone."
                },
                "owner": {
                  "type": "string",
                  "description": "Person accountable for milestone completion."
                },
                "due_date": {
                  "type": "string",
                  "description": "ISO-8601 due date for milestone."
                }
              }
            },
            "description": "Mutual action plan milestones governing pilot to production transition."
          },
          "security_track": {
            "type": "string",
            "description": "Status narrative for security/compliance workstream."
          },
          "legal_track": {
            "type": "string",
            "description": "Status narrative for legal workstream."
          },
          "procurement_track": {
            "type": "string",
            "description": "Status narrative for procurement workstream."
          }
        }
      },
      "risk_controls": {
        "type": "object",
        "required": [
          "data_classification",
          "dpa_required",
          "sla_required",
          "exit_plan_defined"
        ],
        "additionalProperties": false,
        "properties": {
          "data_classification": {
            "type": "string",
            "enum": [
              "public",
              "internal",
              "confidential",
              "regulated"
            ],
            "description": "Highest data sensitivity class involved in pilot execution."
          },
          "dpa_required": {
            "type": "boolean",
            "description": "Whether a data processing agreement is required for this pilot."
          },
          "sla_required": {
            "type": "boolean",
            "description": "Whether SLA commitments are required before conversion."
          },
          "exit_plan_defined": {
            "type": "boolean",
            "description": "Whether termination/transition assistance and exit assumptions are documented."
          }
        }
      },
      "evidence_quality": {
        "type": "object",
        "required": [
          "signal_score",
          "confidence_band",
          "power_check_status",
          "multiple_testing_control",
          "segment_normalization_applied",
          "notes"
        ],
        "additionalProperties": false,
        "properties": {
          "signal_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
            "description": "Aggregate evidence quality score used to determine recommendation confidence."
          },
          "confidence_band": {
            "type": "string",
            "enum": [
              "high",
              "directional",
              "low",
              "insufficient"
            ],
            "description": "Interpretation band derived from signal score and red-flag checks."
          },
          "power_check_status": {
            "type": "string",
            "enum": [
              "pass",
              "marginal",
              "fail",
              "not_applicable"
            ],
            "description": "Result of minimum sample/power adequacy review."
          },
          "multiple_testing_control": {
            "type": "string",
            "enum": [
              "none",
              "bonferroni",
              "holm",
              "fdr_bh"
            ],
            "description": "Correction method used when multiple metrics/treatments are evaluated."
          },
          "segment_normalization_applied": {
            "type": "boolean",
            "description": "Whether analysis was segmented/normalized by ICP or motion before recommendation."
          },
          "notes": {
            "type": "string",
            "description": "Short explanation of major uncertainty or caveat in evidence interpretation."
          }
        }
      },
      "customer_obligations": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Responsibilities the customer must fulfill during pilot."
      },
      "vendor_obligations": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Responsibilities the vendor must fulfill during pilot."
      }
    }
  }
}
```

---

## Gaps & Uncertainties

> Honest list of what was NOT found, what remains uncertain, what would require a second pass.

- Public, peer-reviewed benchmark data specifically for **pilot-package-to-production conversion** remains limited; many sources are practitioner/operator studies.
- Rate-limit and pricing-tier details for some APIs are account/plan dependent and can change; this research references documented values but implementation should re-verify before automation.
- Evidence-quality thresholds are practical heuristics synthesized from experimentation guidance, not a single canonical industry standard.
- Most detailed guidance is enterprise/B2B-weighted; SMB/PLG contexts can require lighter governance and shorter cycles.
- Jurisdiction-specific legal requirements (data transfer, regulated sectors) were not deeply mapped and need a dedicated legal pass per target market.
# Research: pricing-pilot-packaging

**Skill path:** `flexus_simple_bots/strategist/skills/pricing-pilot-packaging/`
**Bot:** strategist (researcher | strategist | executor)
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`pricing-pilot-packaging` defines the commercial design for early-phase customer adoption: what is charged during pilot, how success is measured, and what terms trigger conversion to full production pricing. The skill matters because pilot economics are not normal steady-state economics: buyers take higher risk, cross-functional stakeholders are heavily involved, and procurement/legal friction can erase technical wins if commercial transition is not pre-planned.

2024-2026 evidence indicates that pilot packaging quality is now a leading determinant of conversion quality. Trials and pilots strongly influence buying decisions, but conversion rates remain far from automatic, especially when success criteria are vague or when procurement, security, and commercial terms are deferred until late-stage review. The upgraded skill therefore needs a more explicit method for pilot structure selection, signal quality interpretation, anti-pattern detection, and contract-to-production handoff.

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

The strongest methodological pattern in 2024-2026 is that pilots should be treated as conversion architecture, not "temporary proof activity." Multiple sources show that trials/pilots are now highly influential in software purchases, but they still fail to convert frequently when commercial conditions, decision gates, and procurement path are not defined before kickoff [M1][M2]. This changes skill design priority: pilot terms are not a side note; they are core strategy.

Buying committees are larger and more process-heavy than in prior SaaS cycles. Forrester reports broad multi-stakeholder participation and meaningful procurement involvement in final decisions, which implies pilot packages must explicitly include legal/procurement and security tracks in addition to product validation [M2][M3]. A pilot that only proves product capability while ignoring buying-process readiness will often stall at conversion.

Near-term ROI expectation is compressed. G2 reporting indicates many buyers now expect value realization in roughly one quarter, and cloud providers emphasize tighter use-case focus and measurable impact during pilot-to-scale transitions [M4][M5][M6]. Method implication: pilot scorecards should center on time-bounded business outcomes with baseline, cadence, and owner, not "general strategic value" language.

Current practitioner guidance supports staged proof design: narrow use-case selection first, customer-data validation second, production readiness and commercial transition third [M5][M6][M7]. This staged approach reduces false positives from polished demos and improves conversion confidence because each stage has a clear gate.

Pricing method is also shifting toward hybrid and predictability-oriented structures for enterprise accounts. L.E.K. documents enterprise preference for spend predictability in consumption contexts, while BCG highlights pressure on pure seat economics plus practical barriers to pure outcome pricing [M8][M9]. Method implication: hybrid structures with explicit controls are often the most defensible default for pilots.

Another meaningful pattern is cadence. Benchmark-style pricing operations data (SBI/Price Intelligently) indicates frequent package updates (annual minimum, often quarterly), so pilot offers should include explicit review/expiry windows and pre-defined repricing checkpoints [M10]. This reduces unbounded custom pilots that never converge to repeatable offers.

Contradiction to encode: product trial importance is high, but conversion certainty is not. This should become a decision rule inside SKILL content: "high pilot engagement is necessary, not sufficient; conversion terms and decision gates must be contractually pre-modeled."

**Sources:**
- [M1] Gartner Digital Markets, "2025 Software Buying Trends" (accessed 2026-03-05): https://www.gartner.com/en/digital-markets/insights/2025-software-buying-trends - 2024-2026
- [M2] Forrester, "Forrester's 2026 Buyer Insights: GenAI Is Upending B2B Buying Leaders" (2026-01-21): https://investor.forrester.com/news-releases/news-release-details/forresters-2026-buyer-insights-genai-upending-b2b-buying-leaders/ - 2024-2026
- [M3] Forrester, "The State of Business Buying, 2026" (accessed 2026-03-05): https://www.forrester.com/blogs/state-of-business-buying-2026/ - 2024-2026
- [M4] G2 via Business Wire, "AI Fuels Software Spending, But Buyers Expect Fast ROI" (2024-06-12): https://www.businesswire.com/news/home/20240612200283/en/G2-Report-AI-Fuels-Software-Spending-But-Buyers-Expect-Fast-ROI - 2024-2026
- [M5] Google Cloud, "Scaling AI from experimentation to enterprise reality" (2026-02-03): https://cloud.google.com/transform/scaling-ai-from-experimentation-to-enterprise-reality-google - 2024-2026
- [M6] Google Cloud, "Beyond the pilot: Five hard-won lessons..." (2026-02-25): https://cloud.google.com/transform/beyond-the-pilot-five-hard-won-lessons-from-google-clouds-ai-transformation-strategy - 2024-2026
- [M7] AWS, "Beyond pilots: A proven framework for scaling AI to production" (accessed 2026-03-05): https://aws.amazon.com/blogs/machine-learning/beyond-pilots-a-proven-framework-for-scaling-ai-to-production/ - 2024-2026
- [M8] L.E.K. Consulting, "Navigating Consumption-Based Pricing Models for Enterprise Customers" (2024-03-22): https://www.lek.com/insights/tmt/us/ei/navigating-consumption-based-pricing-models-enterprise-customers - 2024-2026
- [M9] BCG, "Rethinking B2B Software Pricing in the Agentic AI Era" (2025 page, accessed 2026-03-05): https://www.bcg.com/publications/2025/rethinking-b2b-software-pricing-in-the-era-of-ai - 2024-2026
- [M10] SBI / Price Intelligently, "State of B2B SaaS Pricing in 2024" (accessed 2026-03-05): https://sbigrowth.com/tools-and-solutions/pricing-benchmarks-report-2024 - 2024-2026

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

The practical stack for pilot packaging decisions is multi-layered rather than single-vendor:
1) commercial/billing system of record,
2) experimentation and exposure control,
3) monetization analytics,
4) voice-of-customer and WTP research,
5) external benchmarks for calibration [T1][T2][T3][T4][T5][T6].

For billing and pilot commercialization, Stripe, Paddle, Chargebee, and Zuora all provide production-grade pathways but with materially different constraints:
- Stripe documents explicit global and endpoint limits and supports usage-based billing primitives plus meter events; meter processing is asynchronous, so "real-time invoice precision" assumptions are unsafe [T1][T2][T3][T4].
- Paddle provides merchant-of-record packaging with explicit rate limits and documented immediate-charge limits on subscription change frequency [T5][T6][T7].
- Chargebee supports recurring + usage + ramps, with published plan-tier API limits and constraints on usage-record shape/frequency [T8][T9][T10][T11].
- Zuora provides high-complexity enterprise modeling, but with explicit tenant and environment constraints that must be priced into implementation risk [T12][T13][T14].

For experimentation and pricing/package exposure control, LaunchDarkly, Statsig, PostHog, and Amplitude are common options with different operational characteristics:
- LaunchDarkly supports robust feature and experiment controls, but API throttling guidance emphasizes 429 handling and `Retry-After` rather than relying on fixed published rate numbers [T15][T16][T17].
- Statsig exposes explicit Console API limits and offers experimentation methods that can support pricing tests, with event-based pricing and tier boundaries to account for [T18][T19][T20].
- PostHog offers combined analytics, flags, and experiments with transparent billing, but account/product limits can affect data continuity and therefore evidence validity [T21][T22][T23][T24].
- Amplitude combines analytics and experimentation with documented limits and billing nuances that affect interpretation quality [T25][T26][T27].

For revenue outcomes and cohort-level monetization analysis, ChartMogul remains a pragmatic metric layer with published API throughput constraints and clean MRR/ARR/churn primitives [T28][T29].

For WTP and VOC research, Qualtrics, Conjointly, Typeform, and SurveyMonkey are common but differ strongly on method depth and limits:
- Qualtrics supports conjoint workflows with platform/API governance controls [T30][T31][T32][T33][T34].
- Conjointly provides direct access to Van Westendorp/Gabor-Granger/conjoint workflows with transparent plan gating [T35][T36].
- Typeform/SurveyMonkey are efficient for directional VOC but have explicit response and API throttling limits, making them weaker as sole pricing evidence in high-stakes pilot decisions [T37][T38][T39][T40][T41][T42].

External benchmark sources (High Alpha/OpenView, SaaS Capital) are useful as priors for expected performance ranges, but they are periodic reports rather than operational telemetry feeds [T43][T44][T45].

**Sources:**
- [T1] Stripe Docs, "Rate limits": https://docs.stripe.com/rate-limits - Evergreen
- [T2] Stripe Changelog, "Adds Meter Event v2 API endpoints" (2024-09-30): https://docs.stripe.com/changelog/acacia/2024-09-30/usage-based-billing-v2-meter-events-api - 2024-2026
- [T3] Stripe Docs, "Set up a pay-as-you-go pricing model": https://docs.stripe.com/billing/subscriptions/usage-based/implementation-guide - Evergreen
- [T4] Stripe, "Pricing": https://stripe.com/pricing - Evergreen
- [T5] Paddle Developer, "Rate limiting": https://developer.paddle.com/api-reference/about/rate-limiting - Evergreen
- [T6] Paddle Changelog, "Immediate charge limits" (2024): https://developer.paddle.com/changelog/2024/subscription-immediate-charge-limits - 2024-2026
- [T7] Paddle Changelog, "Preview prices/transactions rate limits" (2026): https://developer.paddle.com/changelog/2026/rate-limits-preview-prices-transactions - 2024-2026
- [T8] Chargebee API docs, "Error handling and rate limits": https://apidocs.chargebee.com/docs/api/error-handling - Evergreen
- [T9] Chargebee API docs, "Usages API": https://apidocs.chargebee.com/docs/api/usages - Evergreen
- [T10] Chargebee API docs, "Ramps API": https://apidocs.chargebee.com/docs/api/ramps - Evergreen
- [T11] Chargebee, "Pricing": https://www.chargebee.com/pricing/ - Evergreen
- [T12] Zuora Developer docs, "Rate limits": https://developer.zuora.com/docs/guides/rate-limits - Evergreen
- [T13] Zuora docs, "Sandbox limits policy" (updated 2025-11-06): https://docs.zuora.com/en/basics/environments/zuora-billing-testing-environments/limits-policy-for-api-sandbox-and-developer-sandbox-environments - 2024-2026
- [T14] Zuora docs, "Charge models - configure any pricing" (updated 2026-02-19): https://docs.zuora.com/en/zuora-billing/set-up-zuora-billing/build-product-and-prices/charge-models---configure-any-pricing - 2024-2026
- [T15] LaunchDarkly Support, "429 Too Many Requests": https://support.launchdarkly.com/hc/en-us/articles/22328238491803-Error-429-Too-Many-Requests-API-Rate-Limit - Evergreen
- [T16] LaunchDarkly docs, "Experimentation": https://docs.launchdarkly.com/home/experimentation/ - Evergreen
- [T17] LaunchDarkly, "Pricing": https://launchdarkly.com/pricing/ - Evergreen
- [T18] Statsig, "Pricing": https://www.statsig.com/pricing - Evergreen
- [T19] Statsig API reference sample (OpenAPI 20240601): https://docs.statsig.com/api-reference/gates/read-gate-rules - 2024-2026
- [T20] Statsig docs, "Warehouse Native intro": https://docs.statsig.com/statsig-warehouse-native/introduction - Evergreen
- [T21] PostHog, "Pricing": https://posthog.com/pricing - Evergreen
- [T22] PostHog docs, "API overview": https://posthog.com/docs/api - Evergreen
- [T23] PostHog docs, "Endpoint rate limits": https://posthog.com/docs/endpoints/rate-limits - Evergreen
- [T24] PostHog docs, "Common billing questions": https://posthog.com/docs/billing/common-questions - Evergreen
- [T25] Amplitude docs, "Limits" (2024-07-15): https://amplitude.com/docs/faq/limits - 2024-2026
- [T26] Amplitude docs, "MTU guide" (2024-09-11): https://amplitude.com/docs/admin/billing-use/mtu-guide - 2024-2026
- [T27] Amplitude, "Pricing": https://amplitude.com/pricing - Evergreen
- [T28] ChartMogul, "Pricing": https://chartmogul.com/pricing/ - Evergreen
- [T29] ChartMogul Developer docs, "Rate limits": https://dev.chartmogul.com/docs/rate-limits - Evergreen
- [T30] Qualtrics, "Common API questions": https://www.qualtrics.com/support/integrations/api-integration/common-api-questions-by-product/ - Evergreen
- [T31] Qualtrics, "Conjoint analysis reports": https://www.qualtrics.com/support/conjoint-project/conjoint-reports-tab/reports-choice-based/conjoint-analysis-reports-px/ - Evergreen
- [T32] Qualtrics, "Getting started with conjoint projects": https://www.qualtrics.com/support/conjoint-project/getting-started-conjoints/getting-started-choice-based/getting-started-with-conjoint-projects/ - Evergreen
- [T33] Qualtrics, "API usage threshold event": https://www.qualtrics.com/support/survey-platform/actions-page/events/api-usage-threshold-event/ - Evergreen
- [T34] Qualtrics, "Organization Settings (Public API)": https://www.qualtrics.com/support/survey-platform/sp-administration/organization-settings/#PublicAPI - Evergreen
- [T35] Conjointly, "Pricing": https://conjointly.com/pricing/ - Evergreen
- [T36] Conjointly, "Van Westendorp": https://conjointly.com/products/van-westendorp/ - Evergreen
- [T37] Typeform Developers, "Get started": https://www.typeform.com/developers/get-started/ - Evergreen
- [T38] Typeform, "Pricing": https://www.typeform.com/pricing - Evergreen
- [T39] Typeform Help, "Auto-upgrade response limits": https://help.typeform.com/hc/en-us/articles/4419735872660-Auto-upgrade-your-response-limits - Evergreen
- [T40] SurveyMonkey API docs, "Throttling": https://api.surveymonkey.com/v3/docs?shell#throttling - Evergreen
- [T41] SurveyMonkey Help, "Account response limits": https://help.surveymonkey.com/en/surveymonkey/billing/response-limits/ - Evergreen
- [T42] SurveyMonkey, "Pricing details": https://www.surveymonkey.com/pricing/details/ - Evergreen
- [T43] High Alpha + OpenView, "2024 SaaS Benchmarks Report": https://highalpha.com/saas-benchmarks/2024 - 2024-2026
- [T44] SaaS Capital, "Private B2B SaaS growth benchmarks" (2025): https://www.saas-capital.com/research/private-saas-company-growth-rate-benchmarks/ - 2024-2026
- [T45] SaaS Capital, "Retention benchmarks for private B2B companies" (2025-09-18): https://www.saas-capital.com/research/saas-retention-benchmarks-for-private-b2b-companies/ - 2024-2026

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

Evidence quality controls are non-optional for pilot pricing decisions. Standard experimentation defaults remain around alpha 0.05 and power 0.80, but this is often ignored in low-volume pilots where effect detection power is weak [D1][D2][D3].

A practical hard threshold appears in Amplitude guidance: inferential outputs for binary metrics are withheld until each arm has at least 25 conversions and 100 exposures, reinforcing that "early positive direction" is often too noisy to finalize pricing or conversion terms [D1].

Sequential-testing guidance is important because fixed-horizon peeking materially inflates false positives, while sequential frameworks preserve intended Type I error much better [D1][D4]. Method implication for SKILL: require predefined check cadence and no ad hoc winner calls.

Sample-size realities are especially severe in B2B pilots. Optimizely examples show that small detectable effects can require thousands of observations per variation; Statsig examples show that small groups only detect very large effects [D3][D2]. This should drive a labeling rule: low-volume pilot outcomes are often directional, not definitive.

Population mismatch is a recurring interpretation failure. If power assumptions use broad traffic while only a narrow funnel subset is exposed, MDE estimates and run-time expectations become invalid [D2]. For pilot packaging, this means success criteria should be defined on the actual exposed population and business segment.

Engagement depth is a strong conversion-quality signal. TestBox reports that POCs never accessed convert poorly, while accessed and deeper-engagement POCs convert at much higher rates [D5]. This supports adding engagement gating into pilot success design instead of relying on subjective "good feedback."

Conversion alone is weaker evidence than before in subscription markets. Recurly reports declining trial conversion and acquisition rates over recent years, so pilot success criteria should combine conversion signals with retention and expansion quality checks [D6].

Retention benchmarks must be segmented and definition-aware. SaaS Capital ACV-bucketed NRR benchmarks and ChartMogul scale-segment findings differ in absolute values because they segment differently; both are useful, but they are not interchangeable [D7][D8]. SKILL output should force formula/source declaration for every benchmark used.

Early usage persistence and value concentration metrics add useful noise filtering. Pendo benchmarks suggest many features see low adoption concentration, so pilot success should test whether priced features sit in the value core rather than the feature long tail [D9][D10].

Data-readiness risk is also a signal quality factor. Gartner expects significant AI project abandonment when data readiness is weak; pilot pricing recommendations should therefore include data/operational readiness checks before treating measured lift as scalable [D11].

**Sources:**
- [D1] Amplitude Docs, "Sequential testing for statistical inference" (2024-07-23): https://amplitude.com/docs/feature-experiment/under-the-hood/experiment-sequential-testing - 2024-2026
- [D2] Statsig Docs, "Power Analysis": https://docs.statsig.com/experiments-plus/power-analysis - Evergreen
- [D3] Optimizely, "Sample size calculations for experiments" (2025-12-12): https://www.optimizely.com/insights/blog/sample-size-calculations-for-experiments/ - 2024-2026
- [D4] Statsig Perspective, "Sequential testing and peeking" (2025): https://www.statsig.com/perspectives/sequential-testing-ab-peek - 2024-2026
- [D5] TestBox, "What we learned from analyzing 1,000+ POCs" (2024-03-26): https://www.testbox.com/post/poc-research - 2024-2026
- [D6] Recurly Press, "2025 Industry Report trends" (2025-01-16): https://recurly.com/press/retention-tops-trends-in-recurlys-2025-industry-report/ - 2024-2026
- [D7] SaaS Capital, "Retention benchmarks for private B2B companies" (2025-09-18): https://www.saas-capital.com/research/saas-retention-benchmarks-for-private-b2b-companies/ - 2024-2026
- [D8] ChartMogul, "SaaS retention report: the new normal" (2024 methodology period): https://chartmogul.com/reports/saas-retention-the-new-normal/ - 2024-2026
- [D9] Pendo, "User retention benchmarks 2025" (2025-01-13): https://www.pendo.io/pendo-blog/user-retention-rate-benchmarks/ - 2024-2026
- [D10] Pendo, "2024 software benchmarks" (2024-06-18): https://www.pendo.io/pendo-blog/product-benchmarks/ - 2024-2026
- [D11] Gartner Press, "Lack of AI-ready data puts projects at risk" (2025-02-26): https://www.gartner.com/en/newsroom/press-releases/2025-02-26-lack-of-ai-ready-data-puts-ai-projects-at-risk - 2024-2026

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

**Anti-pattern: Hype-first pilot with no business-value hypothesis**
- Looks like: pilot charter says "explore potential" but lacks quantified value hypothesis and owner.
- Detection signal: no baseline/target KPI model, weak finance check-ins.
- Consequence: pilot de-prioritized when cost/risk scrutiny rises.
- Mitigation: require quantified value thesis (baseline, target, time window, owner) before pilot launch [F1][F2].

**Anti-pattern: Undefined success criteria and no go/no-go gate**
- Looks like: teams plan to "evaluate later" without signed thresholds or decision date.
- Detection signal: no pre-agreed rubric, no conversion meeting date tied to procurement cycle.
- Consequence: technically positive pilots still fail to convert.
- Mitigation: encode hard criteria and explicit gate dates in pilot artifact and terms [F3][F4].

**Anti-pattern: Technical pass, commercial fail**
- Looks like: focus on product behavior/accuracy while omitting economic proof.
- Detection signal: satisfaction with product but weak evidence for cost/revenue impact.
- Consequence: budget owner declines scale approval.
- Mitigation: include both technical and economic KPIs in success criteria [F2][F5].

**Anti-pattern: Pilot sprawl**
- Looks like: too many disconnected pilots with no scale pathway.
- Detection signal: high pilot volume, low production conversion, no domain concentration.
- Consequence: activity without compounding value.
- Mitigation: cap active pilots and concentrate on highest-value use-case clusters [F2][F6][F7].

**Anti-pattern: Tool-only pilot with no workflow redesign**
- Looks like: inserts new tool into one step but leaves upstream/downstream process unchanged.
- Detection signal: local productivity lift but low monetizable impact.
- Consequence: conversion case remains weak despite user enthusiasm.
- Mitigation: include end-to-end workflow change plan and capacity redeployment logic [F5][F8].

**Anti-pattern: Missing executive sponsor with conversion authority**
- Looks like: pilot owned only by technical team, no executive accountable for scale decision.
- Detection signal: unresolved cross-functional blockers and unclear decision rights.
- Consequence: conversion stalls after technical success.
- Mitigation: assign executive sponsor and cross-functional owner at pilot start [F4][F8].

**Anti-pattern: Late legal/security/procurement involvement**
- Looks like: legal/procurement starts after technical success.
- Detection signal: post-pilot stall, repeated re-approvals, new stakeholders late in cycle.
- Consequence: lost momentum and delayed/canceled conversion.
- Mitigation: run legal/security/procurement tracks in parallel from kickoff [F3][F4][F9].

**Anti-pattern: No pilot-to-production contractual bridge**
- Looks like: pilot agreement lacks explicit transition mechanism.
- Detection signal: full commercial terms renegotiated from scratch at pilot end.
- Consequence: value proven but deal fails to close on timeline.
- Mitigation: define conversion trigger, pricing bridge, support/SLA transition, and timeline upfront [F10][F11].

**Anti-pattern: Free pilot for high-friction implementation**
- Looks like: major integration/process change asked with no paid commitment.
- Detection signal: low buyer urgency, low participation quality.
- Consequence: poor qualification and weak conversion reliability.
- Mitigation: prefer paid pilot or pre-signed opt-out structures for high-friction environments [F12][F13][F14-EVERGREEN].

**Anti-pattern: No scaling discipline after pilot**
- Looks like: ideation muscle is strong but replication/scale process is weak.
- Detection signal: many "successful" pilots, few production expansions.
- Consequence: learning fails to translate to recurring revenue.
- Mitigation: define incubation-to-scale playbook with governance milestones [F15-EVERGREEN].

**Sources:**
- [F1] Gartner Press, "30% of GenAI projects abandoned after POC by end of 2025" (2024-07-29): https://www.gartner.com/en/newsroom/press-releases/2024-07-29-gartner-predicts-30-percent-of-generative-ai-projects-will-be-abandoned-after-proof-of-concept-by-end-of-2025 - 2024-2026
- [F2] Deloitte, "State of Generative AI Q3 findings" (2024): https://www2.deloitte.com/us/en/pages/about-deloitte/articles/press-releases/state-of-generative-ai-Q3.html - 2024-2026
- [F3] Forrester Press, "State of Business Buying 2024" (2024-12): https://www.forrester.com/press-newsroom/forrester-the-state-of-business-buying-2024/ - 2024-2026
- [F4] TechTarget, "How to run a successful IT pilot program" (2024-11): https://www.techtarget.com/searchcio/feature/How-to-run-a-successful-IT-pilot-program - 2024-2026
- [F5] Bain, "Executive Survey: AI Moves from Pilots to Production" (2025-11): https://www.bain.com/insights/executive-survey-ai-moves-from-pilots-to-production/ - 2024-2026
- [F6] BCG Press, "74% struggle to achieve and scale AI value" (2024-10-24): https://www.bcg.com/press/24october2024-ai-adoption-in-2024-74-of-companies-struggle-to-achieve-and-scale-value - 2024-2026
- [F7] Bain, "Unsticking Your AI Transformation" (2025-06): https://www.bain.com/insights/unsticking-your-ai-transformation/ - 2024-2026
- [F8] Bain, "From Pilots to Payoff" (2025): https://www.bain.com/insights/from-pilots-to-payoff-generative-ai-in-software-development-technology-report-2025/ - 2024-2026
- [F9] TechTarget, "5 steps to design an effective AI pilot project" (2025-03): https://www.techtarget.com/searchCIO/feature/Steps-to-design-an-effective-AI-pilot-project - 2024-2026
- [F10] Common Paper, "Pilot Agreement v1.1" (2025-07): https://commonpaper.com/standards/pilot-agreement/1.1 - 2024-2026
- [F11] GOV.UK, "Pilot to Production Checklist" (2025): https://www.gov.uk/government/publications/unlocking-space-for-investment-growth-hub/track-3-pilot-to-production-checklist - 2024-2026
- [F12] Common Paper, "Contract Benchmark Report Q1 2024": https://commonpaper.com/resources/contract-benchmark-2024-q1/ - 2024-2026
- [F13] SaaStr, "Paid pilots and conversion guidance" (updated classic): https://www.saastr.com/what-is-the-typical-conversion-from-paid-pilot-to-annual-contract-in-b2b-saas-2/ - Evergreen
- [F14-EVERGREEN] SaaStr, "Should we charge for pilots and how much?" (updated classic): https://www.saastr.com/we-are-a-b2b-saas-startup-and-want-to-develop-our-product-in-pilots-with-customers-should-we-charge-for-the-pilots-and-how-much/ - Evergreen
- [F15-EVERGREEN] MIT Sloan Management Review, "The Missing Discipline Behind Failure to Scale" (2023-04): https://sloanreview.mit.edu/article/the-missing-discipline-behind-failure-to-scale/ - Evergreen

---

### Angle 5: Pricing Benchmarks, Contracting Friction, and Regulatory Gates
> Additional domain-specific angle: practical benchmark ranges, commercial transition patterns, and legal/regulatory constraints that materially affect pilot packaging design.

**Findings:**

Contract benchmark data suggests pilot-adjacent discounting can be substantial and structured, not ad hoc. Common Paper's 2024 benchmark reports frequent design-partner discount usage and repeated discount-level patterns, indicating that "discounted transition economics" is normal market practice rather than exceptional concession [B1].

Paid early-stage structures are also common enough to treat as default option in higher-friction pilots, rather than assuming free pilots maximize conversion quality [B1]. This supports a structure rule: if implementation friction or buyer effort is high, require economic commitment or equivalent commitment mechanism.

Duration norms vary by agreement type (for example, 30/90-day evaluation terms in public templates vs multi-month design-partner terms), which implies SKILL output should include explicit duration rationale by pilot structure [B2][B3][B4][B5].

Success-based commercial patterns are increasingly visible in AI/services-hybrid markets (for example go-live/outcome-linked models and per-successful-resolution constructs), but they are context-dependent and require strict measurability and attribution guardrails [B6][B7].

Pilot-to-production transition risk remains substantial across AI-focused datasets, though reported rates vary by source and cohort. 2024-2026 sources show a wide band from difficult conversion environments to improving production movement, so benchmarks should be used as directional ranges rather than deterministic expectations [B8][B9][B10][B11].

Procurement friction is a first-order timeline variable. Vendr reports longer buying cycles and additional drag in AI categories, which reinforces that pilot terms should include procurement timeline assumptions and fallback decision windows [B12].

Upmarket legal hardening (insurance/security/SLA clauses) is common and should be modeled earlier in pilot packaging for enterprise segments [B1]. Non-binding LOIs can be useful in long procurement environments but should not replace concrete pilot-to-conversion commercial design [B13][B14].

Regulatory obligations can become conversion blockers if treated as post-pilot paperwork. EU AI Act rollout milestones, CISA software assurance guidance, and UK DPIA requirements indicate that regulated segments need compliance readiness embedded in pilot design and transition criteria [B15][B16][B17][B18].

**Sources:**
- [B1] Common Paper, "Contract Benchmark Report Q1 2024": https://commonpaper.com/resources/contract-benchmark-2024-q1/ - 2024-2026
- [B2] HashiCorp, "Terms of Evaluation for HashiCorp Software": https://www.hashicorp.com/en/terms-of-evaluation - Evergreen
- [B3] Digitate (TCS), "Software/SaaS Evaluation Terms" (2025-04-01 release): https://digitate.com/evaluation-agreement-current/ - 2024-2026
- [B4] Juro, "US Evaluation Terms" (updated 2026-01-15): https://juro.com/terms/us-evaluation-terms - 2024-2026
- [B5] Promon, "Pilot Agreement Terms and Conditions": https://promon.io/legal/pilot-agreement-terms-and-conditions - Evergreen
- [B6] HighRadius, "Outcome-Based Pricing Model": https://www.highradius.com/outcome-based-pricing/ - Evergreen
- [B7] L.E.K. Consulting, "Rise of Outcome-Based Pricing in SaaS" (2024-09-13): https://www.lek.com/insights/tmt/us/ei/rise-outcome-based-pricing-saas-aligning-value-cost - 2024-2026
- [B8] Deloitte, "Scaling Generative AI: 13 elements..." (2024): https://www2.deloitte.com/content/dam/Deloitte/us/Documents/consulting/us-ai-institute-scaling-GenAI-final.pdf - 2024-2026
- [B9] BCG Press, "AI adoption 2024": https://www.bcg.com/press/24october2024-ai-adoption-in-2024-74-of-companies-struggle-to-achieve-and-scale-value/ - 2024-2026
- [B10] CIO, "88% of AI pilots fail to reach production..." (2025-03-25): https://www.cio.com/article/3850763/88-of-ai-pilots-fail-to-reach-production-but-thats-not-all-on-it.html - 2024-2026
- [B11] Lenovo Press, "AI paying off but CIOs not ready for what comes next" (2026-01-27): https://news.lenovo.com/pressroom/press-releases/research-reveals-ai-is-paying-off-cios-arent-ready/ - 2024-2026
- [B12] Vendr, "SaaS Trends Report Q2 2024": https://vendr.com/insights/saas-trends-report-q2-2024 - 2024-2026
- [B13] Common Paper blog, "What is an LOI?": https://commonpaper.com/blog/what-is-an-loi/ - Evergreen
- [B14] DealLawyers, "Delaware exclusivity LOI case commentary" (2024-08): https://www.deallawyers.com/blog/2024/08/letters-of-intent-del-chancery-dismisses-allegations-of-breach-of-exclusivity.html - 2024-2026
- [B15] European Commission AI Act Service Desk, "Timeline for implementation": https://ai-act-service-desk.ec.europa.eu/en/ai-act/timeline/timeline-implementation-eu-ai-act - 2024-2026
- [B16] CISA, "Secure Software Development Attestation Form" (2024-03): https://www.cisa.gov/resources-tools/resources/secure-software-development-attestation-form - 2024-2026
- [B17] CISA, "Software Acquisition Guide for Government Enterprise Consumers" (2024-08-01): https://www.cisa.gov/resources-tools/resources/software-acquisition-guide-government-enterprise-consumers-software-assurance-cyber-supply-chain - 2024-2026
- [B18] UK ICO, "When do we need to do a DPIA?": https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/accountability-and-governance/data-protection-impact-assessments-dpias/when-do-we-need-to-do-a-dpia - Evergreen

---

## Synthesis

Across methodology, tools, interpretation, and anti-pattern data, the core finding is that pilot packaging is a governance problem more than a discounting problem. Teams over-index on pilot price level but under-specify decision gates, commercial transition, and cross-functional buying-path readiness. This is why many technically positive pilots do not become repeatable revenue.

A second synthesis is that "pilot influence" and "pilot conversion" are different constructs. Evidence from Gartner/Forrester/G2 and others supports the view that pilots are now often required in buying processes, but they do not guarantee a close. Conversion quality depends on pre-committed success criteria, procurement/legal parallelization, and explicit bridge terms from pilot to production.

Third, tool and data landscape findings show that operational constraints can silently invalidate otherwise sound packaging logic. Rate limits, metering lag, response caps, and experimentation defaults are not implementation trivia; they shape what can be measured and therefore what can be sold credibly. SKILL instructions should therefore force evidence quality labels and "directional vs definitive" classification.

Finally, contradictions across sources suggest a practical default posture: use benchmark ranges and market narratives as priors, but require local telemetry and explicit confidence marking before finalizing conversion commitments. This supports a SKILL upgrade centered on stage gates, anti-pattern blocks, and stronger artifact schema fields for evidence, readiness, and conversion governance.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.
> Each item below has corresponding draft text in the next section.

- [x] Replace current methodology with a commercially-gated pilot workflow that starts with conversion architecture, not pilot discounting.
- [x] Add pilot structure selection rules (`free_loi`, `paid_discounted`, `success_based`, `poc_to_expansion`) with explicit decision criteria and boundary conditions.
- [x] Add strict success-criteria design requirements (baseline, target, owner, measurement source, decision date, and pass/fail semantics).
- [x] Add pilot-to-production transition rules covering procurement/security/legal path in parallel with product validation.
- [x] Add interpretation quality controls for pilot evidence (minimum signal checks, directional vs definitive labels, confidence scoring).
- [x] Add anti-pattern warning blocks with concrete detection signals, consequences, and mitigations.
- [x] Expand `## Available Tools` usage text with explicit activation sequence and artifact write discipline.
- [x] Expand `pilot_package` schema to include governance, decision gates, evidence log, and risk controls with `additionalProperties: false`.
- [x] Add explicit review/expiry cadence so pilot offers do not become unmanaged long-tail custom contracts.

---

## Draft Content for SKILL.md

> This is the most important section. For every recommendation above, this section provides paste-ready SKILL content.

### Draft: Replace Core Mode and Method Intent

---
### Core mode

You are designing pilot commercial architecture, not final steady-state pricing. Your objective is to maximize high-quality conversion to production terms while preserving trust, budget predictability, and learning quality.

Treat pilot packaging as a conversion system with three simultaneous goals:
1. **De-risk adoption for the customer** (commercially and operationally),
2. **Generate decision-grade evidence** (not just positive anecdotes),
3. **Create a clean transition path** to production contract terms.

A pilot that closes to production is worth materially more than a pilot that looks good in isolation but dies at legal/procurement review. Do not optimize for short-term pilot revenue at the expense of conversion quality [M1][M2][M4].
---

### Draft: Methodology (Commercially-Gated Pilot Design)

---
### Methodology

Before outputting any pilot package, run this sequence in order. You must not skip steps.

1. **Frame conversion before pricing**
   - Define target production motion now: expected contract shape, buying committee owner, and likely procurement/security path.
   - If conversion path is undefined, do not finalize pilot pricing. Return a blocking note and request conversion-path inputs first.
   - Rationale: trials influence buying, but without conversion architecture many pilots fail to close [M1][M2][M3].

2. **Select pilot structure using risk-fit rules**
   - Evaluate implementation friction, buyer commitment level, and proof burden.
   - Use this decision logic:
     - If product proof and trust are both low and reference generation is primary objective, consider `free_loi` with written process obligations.
     - If buyer has budget owner and implementation effort is non-trivial, prefer `paid_discounted` to validate willingness to pay and urgency.
     - If vendor confidence in measurable outcomes is high and attribution is controllable, consider `success_based` with explicit refund/credit mechanics.
     - If the first step is narrow team proof with planned expansion path, use `poc_to_expansion` with pre-defined expansion triggers.
   - Do not choose structure by habit. Tie it to risk profile and decision context [M8][B1][B7].

3. **Define price mechanics and predictability controls**
   - For any variable or usage-sensitive pilot design, include customer spend predictability controls:
     - usage visibility cadence,
     - threshold alerts,
     - cap behavior,
     - overage or true-up logic.
   - If these controls are absent, downgrade recommendation confidence and mark as incomplete.
   - Rationale: enterprise buyers prioritize budget predictability even when using flexible models [M8][M9].

4. **Create decision-grade success criteria**
   - Every criterion must include:
     - baseline value,
     - target value,
     - measurement method and data source,
     - owner (customer + vendor),
     - observation window,
     - pass/fail semantics.
   - Prohibit vague criteria like "improve efficiency."
   - Rationale: unclear criteria are a common pilot failure signature [F3][F4][F5].

5. **Run parallel non-product workstreams**
   - During pilot execution, run legal/security/procurement track in parallel with product-value track.
   - Define checkpoints (for example: security packet complete, legal redlines resolved, procurement budget path confirmed).
   - Do not defer these tracks until pilot end; that pattern reliably delays conversion [F3][F4][F9][B12].

6. **Set gate events and conversion clock**
   - Define a mid-pilot gate (evidence quality review) and final gate (conversion decision).
   - Include gate dates, participants, and required evidence packet.
   - If final gate is missed, auto-trigger one of: extend with explicit rationale, convert, or terminate.
   - Avoid open-ended pilots with no hard decision date [F4][F10][F11].

7. **Label evidence quality before making verdict**
   - Classify pilot readout as `directional` or `definitive`.
   - Use `directional` when volume is small, signals are noisy, or criteria are partially observed.
   - Use `definitive` only when criteria are fully measured and decision thresholds are met.
   - Rationale: pilot sample constraints often make early "wins" unstable [D1][D2][D3].

8. **Publish transition and repricing plan**
   - Define conversion terms: trigger, production price logic, timeline, and handoff actions.
   - Define pilot-offer expiry/review cadence to avoid unmanaged custom-term drift.
   - Minimum: annual review; preferred: quarterly in fast-changing categories [M10].
---

### Draft: Pilot Structure Selection Matrix

---
### Pilot pricing structures

Use this matrix when selecting `pilot_structure`:

#### `free_loi`
- Use when:
  - strong need for references,
  - low product trust,
  - buyer cannot yet fund a paid pilot.
- Required safeguards:
  - written LOI/process commitment,
  - named customer stakeholders,
  - fixed pilot window,
  - pre-scheduled final decision meeting.
- Do NOT use when implementation effort is high and customer has no commitment obligations.

#### `paid_discounted`
- Use when:
  - buyer has budget owner,
  - pilot requires meaningful onboarding/integration,
  - you need willingness-to-pay validation.
- Design guidance:
  - tie discount to bounded pilot scope and duration,
  - include explicit production price reference and conversion timeline.
- This is frequently stronger than free pilots for commitment quality in high-friction B2B settings [B1][F12][F13].

#### `success_based`
- Use when:
  - outcome is measurable and attributable,
  - both sides agree on calculation and disputes process.
- Mandatory:
  - precise outcome definition,
  - baseline lock,
  - exception handling and data-source arbitration.
- Do not use if attribution is weak or data quality is unstable [M9][B7].

#### `poc_to_expansion`
- Use when:
  - narrow proof can be run with one team or limited environment first,
  - expansion path is known and can be pre-modeled.
- Required:
  - explicit expansion trigger conditions,
  - pre-negotiated pricing bridge to production.
- Avoid "POC-only" structures that restart negotiation from scratch after success [F10][F11].
---

### Draft: Success Criteria and Decision Gates

---
### Pilot success criteria design

Before pilot start, create 3-7 jointly agreed criteria. Each criterion must contain:

- `criterion`: concrete business or operational outcome statement,
- `baseline_value`: pre-pilot measurement value,
- `target_value`: value that constitutes success,
- `measurement_method`: exact computation logic,
- `data_source`: system/report origin,
- `owner_vendor` and `owner_customer`: accountable reviewers,
- `measurement_window_days`: fixed window length,
- `pass_rule`: how pass/fail is determined.

Quality requirements:

1. Criteria must be specific and measurable.
2. Criteria must mix technical and economic outcomes.
3. Criteria must be time-bound and jointly signed.
4. Criteria must include evidence-readiness checks (data completeness and interpretation confidence).

Decision gates:

- **Mid-pilot gate**: verify data quality, check for early anti-patterns, confirm non-product tracks are on plan.
- **Final gate**: one of `convert`, `extend_with_scope_change`, `terminate`.

Do NOT accept "it felt better" as conversion proof. If criteria are incomplete, classify verdict as non-definitive and block conversion decision pending corrective data [F4][F5][D1][D2].
---

### Draft: Pilot-to-Production Commercial Transition Rules

---
### Conversion terms

Your conversion section must be explicit enough that procurement and legal can execute without restarting from zero.

Required fields:

- `conversion_trigger`: exact condition set for conversion eligibility,
- `conversion_price`: production pricing logic or referenced production package,
- `transition_timeline`: specific dates or elapsed-time milestones,
- `procurement_track_status`: readiness state for procurement/legal/security,
- `contract_bridge_terms`: what terms carry forward vs change at conversion.

Transition rules:

1. Security/legal/procurement milestones must be tracked during pilot, not after.
2. If pilot success is reached but procurement track is incomplete, trigger a time-bounded closure plan.
3. If pilot success is not reached but evidence quality is low, allow scoped extension with revised criteria.
4. If both success and evidence quality are low, terminate and record lessons.

For enterprise segments, include compliance-readiness checks where relevant (for example jurisdictional AI governance and DPIA/security assurance steps) before final conversion commitment [B15][B16][B17][B18].
---

### Draft: Interpretation Quality and Confidence Rules

---
### Evidence interpretation rules

You must classify every pilot verdict by confidence:
- `high`: criteria complete, data quality strong, thresholds met.
- `medium`: criteria mostly complete, some signal uncertainty remains.
- `low`: incomplete criteria, low volume, or unresolved interpretation issues.

Signal-quality controls:

1. **Minimum data sufficiency check**
   - Require minimum exposure/conversion sufficiency before inferential claims.
   - If sufficiency not met, report directional findings only [D1][D3].

2. **No peeking verdicts**
   - Do not declare winners from ad hoc interim looks unless sequential method is defined [D1][D4].

3. **Population alignment**
   - Ensure measured cohort matches the cohort used in success criteria and threshold assumptions [D2].

4. **Multi-metric interpretation**
   - Do not rely on conversion alone. Read conversion with retention/expansion and engagement depth signals [D5][D6][D7][D8].

5. **Benchmark discipline**
   - Benchmarks are priors, not proof. Always label source context and segmentation caveats [D7][D8][T43][T44].

If confidence is `low`, output must include a remediation plan (instrumentation fixes, window extension, or narrowed scope) before any production commitment.
---

### Draft: Anti-pattern Warning Blocks

---
### Anti-patterns to actively detect

#### Warning: Vague Success Criteria
- **Looks like:** "improve productivity" without baseline, target, or measurement owner.
- **Detection signal:** criteria cannot be scored objectively at gate date.
- **Consequence:** pilot appears successful to one side and unsuccessful to the other.
- **Mitigation:** rewrite criteria with baseline/target/data source/owner before launch.

#### Warning: Technical Pass, Commercial Fail
- **Looks like:** product metrics are positive but no economic impact readout exists.
- **Detection signal:** final review deck has no quantified cost/revenue implication.
- **Consequence:** budget owner declines conversion.
- **Mitigation:** require at least one business KPI and one economic KPI in signed criteria.

#### Warning: Late Procurement Track
- **Looks like:** legal/security/procurement starts after pilot value proof.
- **Detection signal:** final decision delayed by new redlines and security requests.
- **Consequence:** momentum loss and higher no-decision rate.
- **Mitigation:** run procurement/legal/security milestones in parallel from week one.

#### Warning: Free Pilot with High Implementation Friction
- **Looks like:** significant integration requested with zero buyer commitment.
- **Detection signal:** low stakeholder participation, low urgency, weak adoption behavior.
- **Consequence:** noisy evidence and weak conversion reliability.
- **Mitigation:** use paid-discounted structure or equivalent commitment mechanism.

#### Warning: Open-Ended Pilot
- **Looks like:** no hard final decision date and no structured extension policy.
- **Detection signal:** pilot continues without clear gate outcomes.
- **Consequence:** resources consumed without conversion or definitive learning.
- **Mitigation:** enforce mid-gate and final-gate dates with explicit outcomes.
---

### Draft: Available Tools (paste-ready replacement)

---
## Available Tools

Activate strategy context before designing terms:

```python
flexus_policy_document(op="activate", args={"p": "/strategy/pricing-tiers"})
flexus_policy_document(op="activate", args={"p": "/strategy/offer-design"})
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})
flexus_policy_document(op="list", args={"p": "/strategy/"})
```

Usage discipline:

1. Activate pricing tier and offer documents first.
2. Pull segment context before setting pilot structure.
3. If upstream documents are missing or contradictory, explicitly state assumption risk before writing artifact.
4. Write artifact only after success criteria and conversion gates are fully specified.

Record output as:

```python
write_artifact(
    artifact_type="pilot_package",
    path="/strategy/pilot-package",
    data={...},
)
```

Do not invent tools, method IDs, or external endpoints inside this skill.
---

### Draft: Recording Requirements

---
### Recording

Write one `pilot_package` artifact that is audit-ready and conversion-ready.

Minimum artifact quality contract:

- Pilot structure and rationale are explicit.
- Pricing terms include predictability controls where relevant.
- Success criteria are measurable and gate-ready.
- Conversion terms include timeline and contractual bridge logic.
- Evidence confidence and source traceability are captured.
- Anti-pattern checks are explicitly passed or flagged.

If confidence is low, do not write forced certainty. Write uncertainty explicitly and include required next actions.
---

### Draft: Schema additions

> Full schema fragment extending the existing `pilot_package` artifact with governance, evidence quality, and decision-gate controls.

```json
{
  "pilot_package": {
    "type": "object",
    "required": [
      "created_at",
      "target_segment",
      "pilot_structure",
      "pilot_duration_days",
      "pricing_terms",
      "success_criteria",
      "decision_gates",
      "conversion_terms",
      "customer_obligations",
      "vendor_obligations",
      "confidence",
      "evidence_log",
      "review_cadence_days"
    ],
    "additionalProperties": false,
    "properties": {
      "created_at": {
        "type": "string",
        "description": "ISO-8601 timestamp when the pilot package was generated."
      },
      "target_segment": {
        "type": "string",
        "description": "Primary customer segment this pilot package is designed for."
      },
      "pilot_structure": {
        "type": "string",
        "enum": [
          "free_loi",
          "paid_discounted",
          "success_based",
          "poc_to_expansion"
        ],
        "description": "Selected pilot commercial structure."
      },
      "pilot_duration_days": {
        "type": "integer",
        "minimum": 1,
        "description": "Planned duration of pilot in days."
      },
      "pricing_terms": {
        "type": "object",
        "required": [
          "pilot_price",
          "standard_price_reference",
          "discount_pct",
          "payment_timing",
          "spend_visibility",
          "cap_policy"
        ],
        "additionalProperties": false,
        "properties": {
          "pilot_price": {
            "type": ["number", "string"],
            "description": "Pilot charge amount or textual pricing expression if non-numeric."
          },
          "standard_price_reference": {
            "type": "number",
            "description": "Reference full-production price used to anchor pilot economics."
          },
          "discount_pct": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Pilot discount as decimal fraction of standard price."
          },
          "payment_timing": {
            "type": "string",
            "enum": [
              "upfront",
              "monthly_in_arrears",
              "milestone_based",
              "on_success",
              "deferred_to_conversion"
            ],
            "description": "When pilot charges are invoiced and collected."
          },
          "spend_visibility": {
            "type": "string",
            "enum": [
              "none",
              "weekly_report",
              "self_serve_dashboard"
            ],
            "description": "How customer can monitor pilot spend trajectory."
          },
          "cap_policy": {
            "type": "string",
            "enum": [
              "none",
              "soft_cap_with_alerts",
              "hard_cap",
              "grace_then_cap"
            ],
            "description": "Behavior when pilot usage reaches planned limits."
          }
        }
      },
      "success_criteria": {
        "type": "array",
        "minItems": 1,
        "items": {
          "type": "object",
          "required": [
            "criterion",
            "baseline_value",
            "target_value",
            "measurement_method",
            "data_source",
            "owner_vendor",
            "owner_customer",
            "measurement_window_days",
            "pass_rule"
          ],
          "additionalProperties": false,
          "properties": {
            "criterion": {
              "type": "string",
              "description": "Concrete outcome statement being evaluated."
            },
            "baseline_value": {
              "type": "string",
              "description": "Pre-pilot baseline used for comparison."
            },
            "target_value": {
              "type": "string",
              "description": "Target threshold that indicates success."
            },
            "measurement_method": {
              "type": "string",
              "description": "Exact method/formula used to compute criterion value."
            },
            "data_source": {
              "type": "string",
              "description": "System/report used as source of truth."
            },
            "owner_vendor": {
              "type": "string",
              "description": "Vendor-side owner accountable for reporting criterion."
            },
            "owner_customer": {
              "type": "string",
              "description": "Customer-side owner accountable for validating criterion."
            },
            "measurement_window_days": {
              "type": "integer",
              "minimum": 1,
              "description": "Observation window length for this criterion."
            },
            "pass_rule": {
              "type": "string",
              "enum": [
                "greater_than_or_equal",
                "less_than_or_equal",
                "within_range",
                "binary_met"
              ],
              "description": "How criterion pass/fail is computed."
            }
          }
        }
      },
      "decision_gates": {
        "type": "object",
        "required": [
          "mid_pilot_gate_day",
          "final_gate_day",
          "required_participants",
          "allowed_final_decisions"
        ],
        "additionalProperties": false,
        "properties": {
          "mid_pilot_gate_day": {
            "type": "integer",
            "minimum": 1,
            "description": "Day number for interim quality/evidence review."
          },
          "final_gate_day": {
            "type": "integer",
            "minimum": 1,
            "description": "Day number for final conversion decision."
          },
          "required_participants": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Roles required to attend decision gates."
          },
          "allowed_final_decisions": {
            "type": "array",
            "items": {
              "type": "string",
              "enum": [
                "convert",
                "extend_with_revised_scope",
                "terminate"
              ]
            },
            "description": "Permitted outcomes at final gate."
          }
        }
      },
      "customer_obligations": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Customer responsibilities required for pilot validity and execution."
      },
      "vendor_obligations": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Vendor responsibilities for delivery, reporting, and support."
      },
      "conversion_terms": {
        "type": "object",
        "required": [
          "conversion_trigger",
          "conversion_price",
          "transition_timeline",
          "procurement_track_status",
          "contract_bridge_terms"
        ],
        "additionalProperties": false,
        "properties": {
          "conversion_trigger": {
            "type": "string",
            "description": "Exact condition under which conversion can proceed."
          },
          "conversion_price": {
            "type": "number",
            "description": "Production price amount or anchor used at conversion."
          },
          "transition_timeline": {
            "type": "string",
            "description": "Timeline from pilot close to production contract effective date."
          },
          "procurement_track_status": {
            "type": "string",
            "enum": [
              "not_started",
              "in_progress",
              "ready_for_signature",
              "blocked"
            ],
            "description": "Status of procurement/legal/security conversion track."
          },
          "contract_bridge_terms": {
            "type": "string",
            "description": "Summary of terms that carry forward versus change at conversion."
          }
        }
      },
      "confidence": {
        "type": "object",
        "required": [
          "overall",
          "signal_classification",
          "reason"
        ],
        "additionalProperties": false,
        "properties": {
          "overall": {
            "type": "string",
            "enum": [
              "low",
              "medium",
              "high"
            ],
            "description": "Overall confidence in pilot package recommendation."
          },
          "signal_classification": {
            "type": "string",
            "enum": [
              "directional",
              "definitive"
            ],
            "description": "Whether evidence quality supports directional or definitive decisioning."
          },
          "reason": {
            "type": "string",
            "description": "Explanation for confidence and signal classification."
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
              "description": "Claim used in pilot packaging recommendation."
            },
            "source_title": {
              "type": "string",
              "description": "Human-readable source title."
            },
            "source_url": {
              "type": "string",
              "description": "URL where source can be verified."
            },
            "source_year": {
              "type": "integer",
              "description": "Publication year for source."
            },
            "confidence": {
              "type": "string",
              "enum": [
                "low",
                "medium",
                "high"
              ],
              "description": "Confidence level for this specific claim."
            },
            "is_evergreen": {
              "type": "boolean",
              "description": "True if source is older but remains structurally valid."
            }
          }
        },
        "description": "Traceable evidence records backing major claims."
      },
      "review_cadence_days": {
        "type": "integer",
        "minimum": 1,
        "description": "Days until pilot package should be re-reviewed or expired."
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Public, high-quality benchmarks for paid pilot conversion by segment and ACV are still sparse; most available numbers are vendor/operator datasets, not standardized cross-industry panels.
- Several high-value operational docs (billing limits, pricing pages, experimentation defaults) are evergreen references that can change quickly; implementation teams should re-check live docs before hard-coding thresholds.
- Source disagreement on pilot-to-production rates is material because cohorts and definitions differ. Use ranges and confidence labels instead of single-point claims.
- Jurisdiction-specific legal and AI governance obligations vary significantly; enterprise and public-sector packages require local legal validation beyond generic pattern guidance.
