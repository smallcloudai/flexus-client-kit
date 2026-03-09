# Research: mvp-validation-criteria

**Skill path:** `strategist/skills/mvp-validation-criteria/`
**Bot:** strategist (researcher | strategist | executor)
**Research date:** 2026-03-04
**Status:** complete

---

## Context

`mvp-validation-criteria` is the strategist skill that defines the success bar for MVP validation before launch: what counts as PMF evidence, what fails validation, and which threshold combinations trigger `go`, `no-go`, or `rework`.

The current `SKILL.md` already captures core PMF signal categories (retention, engagement, satisfaction, expansion) and the principle of pre-defining thresholds. This research expands that baseline with 2024-2026 practice in four areas: pre-registered decision protocols, instrumentation and evidence quality gates, interpretation discipline (confidence, multiplicity, false positives), and explicit anti-pattern detection rules.

For references without explicit publication date (common in vendor docs), this document marks them as **Evergreen** and treats them as current documentation accessed on 2026-03-04.

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

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

1. **Modern MVP validation is stage-gated, not single-metric.**  
   2024-2026 practice shifts from one PMF proxy to a staged evidence flow: problem conviction -> behavior change -> commercial proof -> durability check. This pattern appears across venture/operator guidance and pilot-to-production frameworks, and reduces premature scaling decisions. [A6][A7][A8]

2. **Decision rules are pre-registered before exposure, not after first readout.**  
   Spotify's risk-aware framework formalizes decision logic across success, guardrail, deterioration, and quality metrics, requiring explicit decision policy before analysis. This directly fits the skill's core requirement to lock success criteria pre-launch. [A1][A2]

3. **Quality failures are hard blockers even when primary uplift looks positive.**  
   Current experimentation guidance treats quality checks (for example, data integrity conditions) as vetoes. Teams that ignore quality blockers create false `go` decisions and unstable PMF narratives. [A1][A2]

4. **When sample size is uncertain, acceptable adaptivity is precision/power-based stopping, not arbitrary peeking.**  
   2024 sequential design work emphasizes planned adaptive stopping to preserve inference quality while handling startup uncertainty in variance and recruitment speed. [A3][A4]

5. **Quant-only and qual-only approaches both underperform; mixed-method protocol is now standard.**  
   Recent experimentation practice stresses explicit integration rules: qualitative evidence defines and interprets user behavior, quantitative evidence validates prevalence and magnitude. Criteria artifacts should codify both, plus a tie-break policy for disagreement. [A5][A10]

6. **AI-native MVPs require retention rebasing and durability checks.**  
   AI products often show high early curiosity traffic ("tourists"), so teams should avoid declaring PMF from month-0 curves and instead inspect rebased retention and long-horizon stability before scaling spend. [A6][A7]

7. **Governance is compressing, but ownership is still human at commitment points.**  
   2025 product-process guidance suggests faster evidence loops and automation, while preserving explicit human gate decisions for strategic resource commitments. [A9]

8. **Practical implication for this skill:** the output artifact should represent a complete decision protocol, not only threshold numbers.  
   The artifact must contain gate structure, evidence requirements, invalid-test conditions, and escalation paths; otherwise thresholds can still be reinterpreted post hoc. [A1][A8][A9]

**Sources:**
- [A1] Spotify Engineering, "Risk-Aware Product Decisions in A/B Tests with Multiple Metrics" (2024-03): https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics/
- [A2] Schultzberg et al., arXiv "Risk-aware product decisions in A/B tests with multiple metrics" (2024-02): https://arxiv.org/abs/2402.11609
- [A3] Spotify Engineering, "Fixed-Power Designs: It's Not IF You Peek, It's WHAT You Peek at" (2024-05): https://engineering.atspotify.com/2024/05/fixed-power-designs-its-not-if-you-peek-its-what-you-peek-at
- [A4] Nordin and Schultzberg, arXiv "Precision-based designs for sequential randomized experiments" (2024-05): https://arxiv.org/abs/2405.03487
- [A5] Statsig Perspectives, "Mixed-method experimentation (Quantitative and qualitative)" (2024-11): https://www.statsig.com/perspectives/quantitative-and-qualitative-mixed-method-experimentation
- [A6] Andreessen Horowitz, "Retention Is All You Need" (2025-09): https://a16z.com/ai-retention-benchmarks/
- [A7] Reforge, "Product Market Fit Collapse" (2025-01): https://www.reforge.com/blog/product-market-fit-collapse
- [A8] GOV.UK, "Track 3: Pilot to Production Checklist" (2025): https://www.gov.uk/government/publications/unlocking-space-for-investment-growth-hub/track-3-pilot-to-production-checklist
- [A9] PDMA Knowledge Hub, "Stage-Gate Agentic: The Coming Revolution in the New Product Process" (2025-12): https://community.pdma.org/knowledgehub/bok/product-innovation-process/stage-gate-agentic-the-coming-revolution-in-the-new-product-process
- [A10] Statsig Perspectives, "Qualitative insights in quantitative experiments" (2024-11): https://www.statsig.com/perspectives/qualitative-insights-quantitative-experiments

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

1. **The de-facto MVP validation stack is multi-source, not single-tool.**  
   Product analytics, experimentation, survey, replay, billing, support, and warehouse layers each capture different PMF evidence and failure signals. Using one system alone creates blind spots. [B1][B3][B4][B8][B10]

2. **Event ingestion quality controls are critical at MVP stage.**  
   Amplitude HTTP V2 and Segment HTTP API both expose practical constraints (payload, throughput, dedupe patterns). Validation criteria must include ingestion-quality assumptions, not just output thresholds. [B1][B3]

3. **Warehouse exports require dedupe-aware and mutation-aware modeling.**  
   Amplitude, Mixpanel, and PostHog documentation all imply that downstream KPI tables need explicit deduplication and modeling policies to avoid false threshold outcomes from duplicate/backfilled records. [B2][B4][B5]

4. **Experiment attribution must be wired as a full path (variant exposure -> business outcome event).**  
   PostHog and Statsig docs show that feature/variant evaluation and outcome logging are separate steps. Missing linkage is a common reason for invalid conclusions. [B5][B7]

5. **Holdouts and guardrails improve interpretation quality for launch decisions.**  
   Statsig holdout guidance and LaunchDarkly experimentation docs reinforce maintaining non-treated comparison paths and decision risk views rather than relying on one "winner" readout. [B7][B8]

6. **Behavioral debugging is stronger when replay/frustration telemetry is linked to metrics.**  
   Mixpanel Session Replay and Fullstory rage-click instrumentation help explain "why" metrics move, which reduces false interpretation of aggregate numbers. [B4][B6]

7. **Revenue and payment-state signals are first-class PMF evidence.**  
   Stripe and Paddle webhook ecosystems provide recurring, trial, failure, and cancellation lifecycle events that can be tied directly to MVP `go/no-go` economics. [B9]

8. **Qualitative and support feeds have different latency semantics and reliability profiles.**  
   Typeform webhooks vs pull APIs, Delighted metrics APIs, and Zendesk CSAT endpoints each have different timeliness and access constraints, so criteria should define freshness and fallback windows. [B10][B11][B12]

9. **Instrumentation governance must be explicit (tracking plans, schema controls, observability).**  
   Segment protocols and RudderStack tracking-plan observability patterns show that schema drift and dropped events are measurable and should be formal validation gates. [B3][B13]

10. **Practical implication for this skill:** include a measurement stack contract in the artifact schema.  
    The artifact should name tools by role, required quality checks, and freshness expectations so decision confidence is auditable. [B1][B3][B13]

**Tool landscape (validation-focused):**

| Tool | Primary MVP validation use | Strength | Known limitation/risk | Source |
|---|---|---|---|---|
| Amplitude | Product analytics + event ingestion + export | Mature event ingestion and export docs | Needs dedupe-aware modeling downstream | [B1][B2] |
| Mixpanel | Behavioral analytics + session replay | Replay directly tied to product behavior | Requires explicit replay setup/sampling | [B4] |
| PostHog | Flags/experiments + event capture + export | End-to-end self-serve stack | Attribution can break if linkage incomplete | [B5] |
| Statsig | Experimentation + holdouts + event logging | Decision-focused experimentation tooling | Requires disciplined event logging and design | [B7] |
| LaunchDarkly | Experimentation + Bayesian/frequentist outputs | Mature release + experimentation governance | Method choice/interpretation must be explicit | [B8] |
| Segment | Collection + schema governance | Strong protocol and schema control model | Governance setup overhead at start | [B3] |
| Stripe | Billing/revenue lifecycle signals | Rich recurring revenue event taxonomy | Webhook operations quality is mandatory | [B9] |
| Typeform / Delighted | User sentiment and survey evidence | Fast qualitative signal collection | Delivery lag and response bias risks | [B10][B11] |
| Zendesk | Support friction/CSAT | Structured support sentiment API | Plan/access constraints | [B12] |
| RudderStack | Tracking-plan observability + activation | Data quality monitoring patterns | Needs clean source instrumentation | [B13] |

**Sources:**
- [B1] Amplitude Docs, "HTTP V2 API" (2024-05): https://amplitude.com/docs/apis/analytics/http-v2
- [B2] Amplitude Docs, "Google BigQuery destination" (2024-04): https://amplitude.com/docs/data/destination-catalog/google-bigquery
- [B3] Segment Docs, "Protocols Overview" (**Evergreen**): https://segment.com/docs/protocols/
- [B4] Mixpanel Docs, "Session Replay release/update" (2024-10): https://docs.mixpanel.com/changelogs/2024-09-11-session-replay
- [B5] PostHog Docs, "Capturing events" and "Flags API" (**Evergreen**): https://posthog.com/docs/product-analytics/capture-events and https://posthog.com/docs/api/flags
- [B6] Fullstory Developer Docs, "Rage Click event" (**Evergreen**): https://developer.fullstory.com/browser/rage-clicks/
- [B7] Statsig Docs, "Holdouts" and "Log custom events API" (**Evergreen**): https://docs.statsig.com/holdouts and https://docs.statsig.com/api-reference/events/log-custom-events
- [B8] LaunchDarkly Docs, "Bayesian experiment results" and experimentation docs (**Evergreen**): https://launchdarkly.com/docs/home/experimentation/bayesian-results
- [B9] Stripe Docs, "Using webhooks with subscriptions" and events reference (**Evergreen**, versioned API docs include 2025 previews): https://docs.stripe.com/billing/subscriptions/webhooks and https://docs.stripe.com/api/events/types
- [B10] Typeform Developers, "Webhooks" and "Responses API" (**Evergreen**): https://www.typeform.com/developers/webhooks/ and https://www.typeform.com/developers/responses/
- [B11] Delighted API Docs, "Getting metrics" and "Adding survey responses" (**Evergreen**): https://app.delighted.com/docs/api/getting-metrics and https://app.delighted.com/docs/api/adding-survey-responses
- [B12] Zendesk Developer Docs, "Processing CSAT responses" (**Evergreen**): https://developer.zendesk.com/documentation/ticketing/data-and-reporting/processing-csat/
- [B13] RudderStack Docs, "Tracking Plan Observability" (**Evergreen**): https://www.rudderstack.com/docs/data-governance/tracking-plans/observability/

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

1. **Optional stopping without sequential correction inflates false positives.**  
   Frequent dashboard peeking with fixed-horizon assumptions creates invalid inference. Sequential methods are acceptable only if interpretation uses adjusted intervals/statistics. [C1][C2][C3]

2. **Sequential methods trade speed for stricter evidence accounting.**  
   They are useful for continuous monitoring and early safety stops, but teams must expect more conservative confidence behavior compared with naive peeking. [C1][C2]

3. **Confidence intervals and effect size are decision-grade; p-values alone are not.**  
   Decision criteria should include lower/upper bound interpretation and practical significance thresholds, not only binary significance labels. [C4][C8]

4. **Power, MDE, runtime, and traffic are tightly coupled.**  
   If the required detectable effect is very small, sample and duration increase substantially. A "non-significant" result without power planning is often inconclusive, not negative evidence. [C5]

5. **Multiplicity controls are required when many metrics/slices are inspected.**  
   Without correction, false discovery risk grows quickly. BH/FDR or stricter alternatives should be declared in advance for confirmatory decisions. [C6][C7]

6. **Guardrails are no-harm constraints, not optional context metrics.**  
   A primary-metric win does not override meaningful degradation in safety, reliability, churn, or economics guardrails. [C7][C8][C11]

7. **Leading indicators need explicit linkage to lagging business outcomes.**  
   Fast metrics are useful for early readouts, but PMF-level decisions require confirmation against lagging retention/economic effects. [C9]

8. **Survey-only PMF calls are fragile.**  
   Practitioner guidance around PMF scores (including Sean Ellis-style proxies) repeatedly warns that sentiment signals need retention/economic confirmation to avoid false `go` decisions. [C10]

9. **SRM (sample ratio mismatch) is a hard validity gate.**  
   If assignment proportions are unexpectedly skewed, effect estimates can be biased and should not be used for launch decisions until resolved. [C3]

10. **Practical implication for this skill:** encode "invalid test" as an explicit decision state.  
    This avoids forcing binary `go/no-go` decisions from broken evidence and reduces pressure to rationalize noisy outcomes. [C1][C3][C6]

**Common false-positive traps and mitigations:**

- **Trap:** optional stopping / peek-and-ship.  
  **Detection:** significance appears briefly then disappears; no predeclared stop rule.  
  **Mitigation:** fixed horizon or sequential-adjusted methodology only. [C1][C2]

- **Trap:** metric/slice fishing after initial readout.  
  **Detection:** "winning" insights only appear in secondary segments discovered post hoc.  
  **Mitigation:** pre-register confirmatory slices and apply multiplicity control. [C6][C7]

- **Trap:** interpreting PMF from one sentiment proxy.  
  **Detection:** high sentiment score but unstable retention or poor payback.  
  **Mitigation:** require combined survey + behavioral + economic evidence. [C9][C10]

**Sources:**
- [C1] Statsig Docs, "Frequentist Sequential Testing" (**Evergreen**): https://docs.statsig.com/experiments/advanced-setup/sequential-testing
- [C2] LaunchDarkly Docs, "Choosing a statistical methodology" (**Evergreen**): https://launchdarkly.com/docs/guides/statistical-methodology/choosing
- [C3] Amplitude Docs, "Sample Ratio Mismatch troubleshooting" (2024-06): https://amplitude.com/docs/feature-experiment/troubleshooting/sample-ratio-mismatch
- [C4] Statsig Docs, "Confidence Intervals" (**Evergreen**): https://docs.statsig.com/experiments/statistical-methods/confidence-intervals
- [C5] Statsig Docs, "Power Analysis" (**Evergreen**): https://docs.statsig.com/experiments/power-analysis
- [C6] Harness Docs, "Multiple comparison correction" (**Evergreen**): https://developer.harness.io/docs/feature-management-experimentation/experimentation/key-concepts/multiple-comparison-correction
- [C7] Optimizely Support, "False discovery rate control" (**Evergreen**): https://support.optimizely.com/hc/en-us/articles/4410283967245-False-discovery-rate-control
- [C8] Statsig Perspectives, "Statistical vs practical significance" (2024-10): https://www.statsig.com/perspectives/statistical-vs-practical-significance
- [C9] Statsig Perspectives, "Leading vs. lagging indicators" (2024-10): https://www.statsig.com/perspectives/leading-vs-lagging-indicators
- [C10] PostHog Founders, "How to measure product-market fit" (2023, **Evergreen**): https://posthog.com/founders/measure-product-market-fit
- [C11] Statsig Perspectives, "What are guardrail metrics in A/B tests?" (2025): https://www.statsig.com/perspectives/what-are-guardrail-metrics-in-ab-tests

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

1. **Post-hoc threshold rewriting is one of the most damaging anti-patterns.**  
   Teams move the success bar after seeing data ("close enough"), producing inflated success rates and weak reproducibility. Criteria artifacts must enforce change-control logging for threshold edits. [D1][D2]

2. **Peek-and-ship behavior remains common under time pressure.**  
   Without predeclared stopping policy, repeated checks create noisy false wins and unstable launch quality. [D1][D3]

3. **SRM blindness invalidates seemingly strong uplifts.**  
   Industry experimentation literature shows SRM as a recurring operational issue, and unresolved SRM can destroy causal validity. [D4][D5]

4. **Triggered-subset analyses can fabricate "wins."**  
   Result narratives often look positive only inside filtered cohorts while the overall population is flat or negative. Criteria should require unfiltered sanity views and trigger-definition audits. [D4]

5. **Single-proxy PMF is fragile (especially NPS-only).**  
   Customer sentiment is useful but insufficient for launch commitment when retention and revenue quality do not confirm the signal. [D6][D7]

6. **Static thresholds become stale as market baselines shift.**  
   2024 benchmarks indicate large retention and performance variability by category and company profile, so fixed universal thresholds can misclassify outcomes. [D8][D9]

7. **Instrumentation debt creates false confidence.**  
   Data quality and observability gaps are now a top-reported challenge in analytics teams; MVP criteria should include explicit data quality pass/fail gates. [D10][D11]

8. **Qualitative bias (leading questions) inflates positive feedback.**  
   Interview and survey wording can nudge responses and mask real demand risk; scripts need neutrality checks before fieldwork starts. [D12]

9. **Underpowered pilots with post-hoc sample chasing waste runway.**  
   Teams that repeatedly resize after peeking often increase noise and delay decision clarity. [D3]

10. **Guardrail misuse has two forms: absent guardrails or guardrail overload.**  
    Missing guardrails hides collateral damage; too many weak guardrails create alert fatigue and indecision. A small high-impact set is preferred. [C11][D13][D14]

**Bad artifact signals vs good artifact signals:**

- **Bad signals**
  - Thresholds editable after first readout without formal approval trail.
  - No `invalid_test` state when quality gates fail.
  - No SRM check, schema-violation check, or event-loss threshold.
  - One blended metric used for `go` without cohort/segment breakdown.
  - PMF declared from a single sentiment proxy.

- **Good signals**
  - Versioned pre-analysis protocol with explicit change log.
  - Mandatory quality gates before business interpretation.
  - Separate decision states: `go`, `no_go`, `rework`, `invalid_test`.
  - Combined evidence logic (behavior + retention + economics + sentiment).
  - Segment-aware pass criteria and periodic threshold refresh cadence.

**Sources:**
- [D1] ICML/PMLR, "Peeking with PEAK: Sequential, Nonparametric Composite Hypothesis Tests..." (2024): https://proceedings.mlr.press/v235/cho24a.html
- [D2] Journal of Political Economy Microeconomics (working-paper listing), "Do Pre-Registration and Pre-Analysis Plans Reduce p-Hacking..." (2024): https://ideas.repec.org/p/zbw/glodps/1147pre.html
- [D3] Analytics-Toolkit, "Using Observed Power in Online A/B Tests" (2024): https://blog.analytics-toolkit.com/2024/observed-power-in-online-a-b-testing/
- [D4] Fabijan et al., KDD, "Diagnosing Sample Ratio Mismatch..." (2019, **Evergreen**): https://exp-platform.com/Documents/2019_KDDFabijanGupchupFuptaOmhoverVermeerDmitriev.pdf
- [D5] LaunchDarkly Docs, "Sample ratio mismatch" (**Evergreen**): https://launchdarkly.com/docs/guides/statistical-methodology/sample-ratios
- [D6] Forrester, "US and Canadian 2024 Net Promoter Score Results" (2024): https://www.forrester.com/blogs/us-and-canadian-2024-nps-results-another-year-of-decline/
- [D7] MSI, "The Net Promoter Score (NPS) Fails to Predict Revenue Growth" (2023, **Evergreen**): https://www.msi.org/working-paper/the-net-promoter-score-nps-fails-to-predict-revenue-growth/
- [D8] Mixpanel Blog, "The 2024 Mixpanel Benchmarks Report is here" (2024): https://mixpanel.com/blog/2024-mixpanel-benchmarks-report/
- [D9] High Alpha/OpenView, "2024 SaaS Benchmarks Report" (2024): https://highalpha.com/saas-benchmarks/2024
- [D10] dbt Labs, "2024 State of Analytics Engineering" (2024): https://www.getdbt.com/resources/reports/state-of-analytics-engineering-2024
- [D11] RudderStack Docs, "Tracking Plan Observability" (**Evergreen**): https://www.rudderstack.com/docs/data-governance/tracking-plans/observability/
- [D12] Maze Blog, "How to avoid leading questions in UX research" (2024): https://maze.co/blog/leading-questions/
- [D13] Optimizely Blog, "Understanding and implementing guardrail metrics" (2025): https://www.optimizely.com/insights/blog/understanding-and-implementing-guardrail-metrics
- [D14] PostHog, "Guardrail metrics for A/B tests, explained" (2023, **Evergreen**): https://posthog.com/product-engineers/guardrail-metrics

---

## Synthesis

The strongest cross-angle pattern is that MVP validation quality now depends less on selecting one "best" PMF metric and more on designing a robust decision protocol before launch. Methodology sources and experimentation sources converge on the same operational idea: pre-register your decision logic, separate validity checks from business outcome interpretation, and block decisions when integrity conditions fail.

A major contradiction is speed versus rigor. 2025 process discussions encourage compressed loops and automation, while statistical guidance warns against shortcut interpretation (peeking, post-hoc slicing, threshold drift). The practical resolution is not to slow everything down, but to automate evidence collection and keep human gate ownership only for high-commitment decisions.

Another contradiction is universal benchmarks versus segment-specific realities. Benchmarks are useful for sanity-checking target ranges, but they are not portable truth across ICP, monetization model, or product category. This is why criteria artifacts should encode segment-aware rules and a refresh cadence instead of fixed one-size-fits-all numbers.

The most actionable upgrade for `SKILL.md` is to move from "threshold list" to "decision system": gate structure, quality blockers, confidence policy, mixed-method arbitration, anti-pattern detectors, and explicit `invalid_test` semantics. This change directly reduces false-positive PMF calls and makes the final strategist artifact auditable.

---

## Recommendations for SKILL.md

- [x] Add a pre-registered validation protocol section with staged gates and immutable pre-launch decision policy.
- [x] Add explicit `invalid_test` conditions (for example SRM/data quality failures) that block `go/no-go`.
- [x] Add a mixed-method evidence matrix and arbitration rules when qualitative and quantitative signals conflict.
- [x] Add interpretation rules for confidence, practical significance, MDE/power, and multiplicity correction.
- [x] Add AI-specific retention rebasing and PMF durability review guidance.
- [x] Expand Available Tools guidance with syntax blocks for policy activation and artifact writing workflow.
- [x] Add named anti-pattern warning blocks with detection signals and mitigation steps.
- [x] Extend artifact schema with decision protocol, measurement stack, quality gates, and evidence manifest fields.

---

## Draft Content for SKILL.md

### Draft: Validation Philosophy and Non-Negotiables

You must treat MVP validation criteria as a **pre-registered decision contract**, not as a post-launch narrative. Before any pilot starts, lock the definitions of success, failure, and invalid evidence states. Your objective is to reduce false confidence, not to maximize the probability of a `go` verdict.

Do not collapse PMF into one number. PMF is a composite claim that requires aligned evidence across behavior, retention, economics, and user-reported value. If these signals disagree, your output must preserve that disagreement and resolve it through explicit arbitration rules, not intuition.

You must separate:

1. **Evidence validity** (is the measurement trustworthy?),
2. **Effect direction and magnitude** (did the metric move, and by how much?),
3. **Decision policy** (does that movement pass predeclared business and risk constraints?).

If evidence validity fails, stop and return `invalid_test` or `rework` even if top-line metrics look positive.

---

### Draft: Methodology - Pre-Registered MVP Validation Workflow

Before producing criteria, activate required strategy documents and anchor context to scope, hypothesis, and ICP evidence.

```python
flexus_policy_document(op="activate", args={"p": "/strategy/mvp-scope"})
flexus_policy_document(op="activate", args={"p": "/strategy/hypothesis-stack"})
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})
```

Then execute this sequence:

1. **Lock the validation window and decision checkpoints.**  
   Define `validation_window_days` and checkpoint cadence (for example weekly evidence checks plus final decision checkpoint). You are allowed to monitor continuously, but final decision logic must be declared before first exposure.

2. **Define signal families and minimum evidence per family.**  
   You must include at least retention, engagement, satisfaction, and expansion. Add economics and qualitative evidence when monetization or workflow replacement is central to the hypothesis. For each signal, define the metric, cohort, observation window, and minimum sample/evidence requirement.

3. **Declare decision policy parameters.**  
   Set methodology mode (`fixed_horizon` or `sequential_adjusted`), confidence policy, practical significance floor, and multiplicity control policy. If you do not define these, your result is not decision-grade.

4. **Define quality gates that run before interpretation.**  
   Include at minimum SRM pass/fail, schema violation tolerance, event drop tolerance, and minimum observation depth. If any quality gate fails, mark the test invalid for `go/no-go`.

5. **Define gate-based outcomes, not one final threshold string.**  
   Create explicit `go_rule`, `no_go_rule`, and `recycle_rule` conditions that combine multiple signal families and quality constraints. Rules must be machine-readable enough for downstream automation and human-auditable enough for leadership review.

6. **Add mixed-method arbitration.**  
   If quant passes but qual indicates unresolved core-value mismatch, return `rework` with required follow-up evidence. If qual enthusiasm is strong but retention/economics fail, return `no_go` or `rework` depending on severity and runway.

7. **Add durability review before scale decision.**  
   Especially for AI-native MVPs, require a short durability check (retention stability after early curiosity cohort decay, channel dependency risk, and expected baseline drift risk) before committing scale budget.

8. **Write artifact and include evidence references.**  
   Store criteria with clear source references and contradiction notes.

```python
write_artifact(
  artifact_type="mvp_validation_criteria",
  path="/strategy/mvp-validation-criteria",
  data={...}
)
```

Do NOT:

- change thresholds after first readout without recording a formal protocol revision,
- accept a `go` when quality gates fail,
- treat one sentiment proxy as sufficient PMF evidence,
- collapse segment-specific behavior into one blended pass condition.

---

### Draft: Interpretation Rules (Thresholds, Confidence, and False Positives)

Use the following interpretation policy text directly:

1. **Predeclare confidence and practical significance.**  
   You must define both statistical confidence policy and minimum practical effect required for business relevance. Statistical significance alone is not sufficient for a `go` call.

2. **Control false positives from repeated looks and multiple comparisons.**  
   If you monitor results continuously, use a sequential-adjusted interpretation mode. If you evaluate many metrics or slices, define multiplicity control (for example Benjamini-Hochberg for confirmatory sets). Post-hoc metric fishing is invalid.

3. **Treat guardrails as veto constraints.**  
   A primary metric improvement does not override meaningful degradation in guardrails such as reliability, churn risk, support burden, or payment failure rates. Guardrail deterioration triggers `no_go` or `rework` according to declared harm thresholds.

4. **Use `invalid_test` for trust failures.**  
   If SRM or instrumentation integrity checks fail, do not force a binary go/no-go interpretation. Return `invalid_test`, fix instrumentation/randomization issues, and rerun.

5. **Require lagging confirmation for PMF-level decisions.**  
   Leading indicators can support early directionality, but scale decisions require lagging confirmation (retention durability and economic quality where applicable).

6. **Apply segment-aware criteria.**  
   Do not let blended averages hide segment collapse. If your strategy is segment-specific, define minimum pass thresholds per target segment and fail if segment composition drift invalidates comparison.

---

### Draft: Available Tools (Operational Usage Section)

Use these tools to gather required policy context before writing criteria:

```python
flexus_policy_document(op="activate", args={"p": "/strategy/mvp-scope"})
flexus_policy_document(op="activate", args={"p": "/strategy/hypothesis-stack"})
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})
```

Use this tool to persist the final criteria artifact:

```python
write_artifact(
  artifact_type="mvp_validation_criteria",
  path="/strategy/mvp-validation-criteria",
  data={
    "created_at": "2026-03-04T12:00:00Z",
    "validation_window_days": 42,
    "decision_protocol": {...},
    "pmf_signals": [...],
    "quality_gates": {...},
    "go_rule": {...},
    "no_go_rule": {...},
    "recycle_rule": {...},
    "failure_modes": [...],
    "evidence_manifest": [...]
  }
)
```

Tool usage requirements:

- Always activate source strategy documents before authoring criteria.
- Always include source-backed evidence references in the artifact.
- Never write criteria with missing quality gates or missing decision protocol fields.

---

### Draft: Anti-Pattern Warning Blocks

#### Warning: Post-hoc Threshold Rewriting

What this looks like in practice:  
You redefine success after seeing data ("we almost hit target, let's relax the threshold").

Detection signal:  
Thresholds in decision notes differ from thresholds in the pre-launch criteria version.

Consequence if missed:  
False `go` rates increase and retrospective narratives become non-reproducible.

Mitigation steps:
1. Freeze initial thresholds in a versioned protocol section.
2. If changes are truly needed, record change reason, timestamp, approver, and affected metrics.
3. Force result labels to include "protocol_changed_post_launch" so downstream decisions cannot ignore the deviation.

#### Warning: Peek-and-Ship

What this looks like in practice:  
You check results repeatedly and launch at the first favorable snapshot.

Detection signal:  
No predeclared stopping logic; significance appears early and disappears later.

Consequence if missed:  
Inflated false positives and unstable post-launch performance.

Mitigation steps:
1. Predeclare methodology mode (`fixed_horizon` or `sequential_adjusted`).
2. If using sequential mode, interpret only adjusted confidence outputs.
3. Block final `go` until declared decision checkpoint criteria are met.

#### Warning: SRM Blindness

What this looks like in practice:  
You interpret uplift despite assignment ratio mismatch alerts.

Detection signal:  
Observed variant allocation materially deviates from expected split.

Consequence if missed:  
Biased effect estimates and incorrect launch decisions.

Mitigation steps:
1. Add SRM as mandatory quality gate.
2. Return `invalid_test` when SRM gate fails.
3. Diagnose assignment, exposure, and logging path before rerun.

#### Warning: Proxy PMF (Single-Metric Dependence)

What this looks like in practice:  
You declare PMF from one sentiment or top-funnel metric.

Detection signal:  
Proxy improves while retention or economics degrade.

Consequence if missed:  
Premature scaling and capital misallocation.

Mitigation steps:
1. Require at least one behavioral, one retention, and one value/economic signal in decision rule.
2. Encode minimum pass set in `go_rule`.
3. Mark output `rework` when evidence families disagree.

#### Warning: Segment Drift Hidden by Blended Averages

What this looks like in practice:  
Overall average passes while target ICP segment underperforms.

Detection signal:  
Segment composition shifts across validation window and segment-level outcomes diverge.

Consequence if missed:  
False confidence for target market readiness.

Mitigation steps:
1. Define segment-specific pass conditions for primary ICP.
2. Track composition drift and block comparison if drift exceeds tolerance.
3. Report both blended and target-segment verdicts.

#### Warning: Instrumentation Debt

What this looks like in practice:  
Thresholds are evaluated on events with schema drift, drop spikes, or ownership ambiguity.

Detection signal:  
Schema violation rates or dropped-event rates exceed declared limits.

Consequence if missed:  
`go/no-go` decision quality collapses because measurements are unreliable.

Mitigation steps:
1. Declare explicit schema/event-drop quality gates.
2. Add observability summary to `evidence_manifest`.
3. Block business interpretation until quality gates pass.

---

### Draft: Decision Output Semantics

Use this decision semantics block directly in the skill:

- **`go`**: all mandatory quality gates pass, primary evidence families meet thresholds, and guardrails remain within allowed harm bounds.
- **`no_go`**: one or more disqualifying conditions are met (for example primary failure and/or severe guardrail breach) under valid evidence.
- **`rework`**: evidence is valid but contradictory or incomplete; additional work is required before commitment.
- **`invalid_test`**: evidence validity fails (for example SRM, instrumentation integrity, or insufficient exposure quality); no business verdict is allowed.

Decision policy:

1. Evaluate quality gates first.
2. If quality fails -> `invalid_test`.
3. If quality passes, evaluate `go_rule`.
4. If `go_rule` fails, evaluate `no_go_rule`.
5. If neither clearly applies -> `rework` with required next evidence.

---

### Draft: Schema additions

Use this schema fragment to replace or extend the current `mvp_validation_criteria` schema.

```json
{
  "mvp_validation_criteria": {
    "type": "object",
    "required": [
      "created_at",
      "version",
      "validation_window_days",
      "decision_protocol",
      "pmf_signals",
      "quality_gates",
      "go_rule",
      "no_go_rule",
      "recycle_rule",
      "failure_modes",
      "evidence_manifest"
    ],
    "additionalProperties": false,
    "properties": {
      "created_at": {
        "type": "string",
        "description": "ISO-8601 timestamp when criteria were authored."
      },
      "version": {
        "type": "integer",
        "minimum": 1,
        "description": "Monotonic version to detect post-launch threshold changes."
      },
      "validation_window_days": {
        "type": "integer",
        "minimum": 1,
        "description": "Planned duration of MVP validation window."
      },
      "decision_protocol": {
        "type": "object",
        "required": [
          "methodology_mode",
          "alpha",
          "power",
          "mde_fraction",
          "practical_significance_fraction",
          "multiplicity_control",
          "guardrail_policy",
          "invalid_test_blockers"
        ],
        "additionalProperties": false,
        "properties": {
          "methodology_mode": {
            "type": "string",
            "enum": ["fixed_horizon", "sequential_adjusted"],
            "description": "Statistical decision mode used for interpretation."
          },
          "alpha": {
            "type": "number",
            "minimum": 0,
            "maximum": 0.2,
            "description": "Type-I error budget for confirmatory decisions."
          },
          "power": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Target test power for planned effect size."
          },
          "mde_fraction": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Minimum detectable effect as relative fraction."
          },
          "practical_significance_fraction": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Minimum business-meaningful effect size threshold."
          },
          "multiplicity_control": {
            "type": "string",
            "enum": ["none", "benjamini_hochberg", "bonferroni"],
            "description": "Correction policy when multiple metrics/slices are confirmatory."
          },
          "guardrail_policy": {
            "type": "string",
            "enum": ["non_inferiority_required", "degradation_threshold"],
            "description": "How guardrail constraints are enforced."
          },
          "invalid_test_blockers": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "string",
              "enum": [
                "srm_detected",
                "schema_violation_exceeded",
                "event_drop_exceeded",
                "insufficient_sample",
                "instrumentation_missing"
              ]
            },
            "description": "Conditions that force invalid_test state."
          }
        }
      },
      "measurement_stack": {
        "type": "array",
        "description": "Optional but recommended declaration of data sources/tools used for evidence generation.",
        "items": {
          "type": "object",
          "required": [
            "tool_name",
            "role",
            "dataset_or_stream",
            "quality_checks"
          ],
          "additionalProperties": false,
          "properties": {
            "tool_name": {
              "type": "string",
              "enum": [
                "amplitude",
                "mixpanel",
                "posthog",
                "statsig",
                "launchdarkly",
                "segment",
                "stripe",
                "paddle",
                "zendesk",
                "typeform",
                "delighted",
                "fullstory",
                "rudderstack",
                "other"
              ],
              "description": "Named measurement platform."
            },
            "role": {
              "type": "string",
              "enum": [
                "event_collection",
                "experimentation",
                "survey",
                "session_replay",
                "billing",
                "support",
                "warehouse",
                "activation"
              ],
              "description": "Primary role of this tool in MVP validation."
            },
            "dataset_or_stream": {
              "type": "string",
              "description": "Dataset, stream, or event family used for criteria metrics."
            },
            "quality_checks": {
              "type": "array",
              "minItems": 1,
              "items": {
                "type": "string",
                "enum": [
                  "deduplication",
                  "schema_validation",
                  "event_drop_monitoring",
                  "identity_resolution",
                  "freshness_monitoring",
                  "srm_monitoring"
                ]
              },
              "description": "Data quality controls required for this source."
            }
          }
        }
      },
      "pmf_signals": {
        "type": "array",
        "minItems": 4,
        "items": {
          "type": "object",
          "required": [
            "signal_id",
            "signal_type",
            "metric",
            "measurement_method",
            "cohort_definition",
            "measurement_window",
            "target_threshold",
            "weight"
          ],
          "additionalProperties": false,
          "properties": {
            "signal_id": {
              "type": "string",
              "description": "Stable signal identifier."
            },
            "signal_type": {
              "type": "string",
              "enum": [
                "retention",
                "engagement",
                "satisfaction",
                "expansion",
                "economics",
                "qualitative"
              ],
              "description": "Evidence family represented by this signal."
            },
            "metric": {
              "type": "string",
              "description": "Metric name or KPI definition."
            },
            "measurement_method": {
              "type": "string",
              "description": "How the metric is measured (query rule, survey method, or event path)."
            },
            "cohort_definition": {
              "type": "string",
              "description": "Population/cohort to which threshold applies."
            },
            "measurement_window": {
              "type": "string",
              "description": "Time window for evaluating the metric."
            },
            "target_threshold": {
              "type": "object",
              "required": ["operator", "value"],
              "additionalProperties": false,
              "properties": {
                "operator": {
                  "type": "string",
                  "enum": [">", ">=", "<", "<=", "between"],
                  "description": "Threshold operator."
                },
                "value": {
                  "type": "number",
                  "description": "Primary threshold value."
                },
                "upper_value": {
                  "type": "number",
                  "description": "Upper bound when operator is between."
                }
              }
            },
            "weight": {
              "type": "number",
              "minimum": 0,
              "maximum": 1,
              "description": "Relative contribution to aggregate decision logic."
            }
          }
        }
      },
      "quality_gates": {
        "type": "object",
        "required": [
          "srm_required",
          "event_drop_rate_max_fraction",
          "schema_violation_rate_max_fraction",
          "minimum_sample_size_per_variant",
          "minimum_observation_days",
          "stop_on_quality_fail"
        ],
        "additionalProperties": false,
        "properties": {
          "srm_required": {
            "type": "boolean",
            "description": "Whether SRM check is mandatory before interpretation."
          },
          "event_drop_rate_max_fraction": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Maximum tolerated dropped-event fraction."
          },
          "schema_violation_rate_max_fraction": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Maximum tolerated schema violation fraction."
          },
          "minimum_sample_size_per_variant": {
            "type": "integer",
            "minimum": 1,
            "description": "Minimum required observations per variant/cohort."
          },
          "minimum_observation_days": {
            "type": "integer",
            "minimum": 1,
            "description": "Minimum days before a business verdict is allowed."
          },
          "stop_on_quality_fail": {
            "type": "boolean",
            "description": "If true, business interpretation is blocked on quality failure."
          }
        }
      },
      "go_rule": {
        "type": "object",
        "required": ["conditions", "description"],
        "additionalProperties": false,
        "properties": {
          "conditions": {
            "type": "array",
            "minItems": 1,
            "items": { "type": "string" },
            "description": "Machine-readable condition clauses for go verdict."
          },
          "description": {
            "type": "string",
            "description": "Human-readable summary of go logic."
          }
        }
      },
      "no_go_rule": {
        "type": "object",
        "required": ["conditions", "description"],
        "additionalProperties": false,
        "properties": {
          "conditions": {
            "type": "array",
            "minItems": 1,
            "items": { "type": "string" }
          },
          "description": {
            "type": "string"
          }
        }
      },
      "recycle_rule": {
        "type": "object",
        "required": ["conditions", "description"],
        "additionalProperties": false,
        "properties": {
          "conditions": {
            "type": "array",
            "minItems": 1,
            "items": { "type": "string" }
          },
          "description": {
            "type": "string"
          }
        }
      },
      "failure_modes": {
        "type": "array",
        "items": {
          "type": "object",
          "required": [
            "mode",
            "indicators",
            "detection_signal",
            "consequence",
            "recommended_response",
            "mitigation_steps"
          ],
          "additionalProperties": false,
          "properties": {
            "mode": {
              "type": "string",
              "enum": [
                "wrong_icp",
                "wrong_solution",
                "wrong_channel",
                "wrong_timing",
                "threshold_drift",
                "instrumentation_gap",
                "proxy_pmf"
              ]
            },
            "indicators": {
              "type": "array",
              "items": { "type": "string" }
            },
            "detection_signal": {
              "type": "string",
              "description": "Observable signal that the anti-pattern is occurring."
            },
            "consequence": {
              "type": "string",
              "description": "Expected decision risk if unmitigated."
            },
            "recommended_response": {
              "type": "string"
            },
            "mitigation_steps": {
              "type": "array",
              "minItems": 1,
              "items": { "type": "string" }
            }
          }
        }
      },
      "evidence_manifest": {
        "type": "array",
        "minItems": 1,
        "items": {
          "type": "object",
          "required": [
            "evidence_id",
            "source_type",
            "reference",
            "collected_at",
            "confidence"
          ],
          "additionalProperties": false,
          "properties": {
            "evidence_id": {
              "type": "string",
              "description": "Stable identifier for evidence entry."
            },
            "source_type": {
              "type": "string",
              "enum": [
                "quantitative",
                "qualitative",
                "benchmark",
                "pilot",
                "interview",
                "support",
                "billing"
              ]
            },
            "reference": {
              "type": "string",
              "description": "URL, document path, or system query reference."
            },
            "collected_at": {
              "type": "string",
              "description": "ISO-8601 timestamp when evidence was captured."
            },
            "confidence": {
              "type": "string",
              "enum": ["high", "medium", "low"],
              "description": "Confidence in evidence reliability after quality-gate checks."
            },
            "contradiction_note": {
              "type": "string",
              "description": "Optional note when evidence conflicts with other sources."
            }
          }
        }
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Several vendor docs are intentionally undated; they are treated as evergreen current docs, but point-in-time behavior can still vary by plan, region, or product version.
- Public benchmark reports vary in methodology and denominator definitions; threshold portability across ICPs remains uncertain without local baseline data.
- Public PMF survey thresholds are useful directional signals but not universally predictive across business models; stronger domain-specific retention/economics evidence is still required.
- Some high-value practitioner content (for example private newsletters or paywalled analyses) is only partially accessible; findings based on these were not used as sole decision anchors.
