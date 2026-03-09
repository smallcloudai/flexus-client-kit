# Research: mvp-scope

**Skill path:** `strategist/skills/mvp-scope/`
**Bot:** strategist (researcher | strategist | executor)
**Research date:** 2026-03-04
**Status:** complete

---

## Context

`mvp-scope` defines the minimum viable feature set for validating a core product hypothesis with real users, while explicitly documenting what is excluded and why. The skill is used after hypothesis framing and before feasibility, validation criteria, and roadmap planning.

The core problem this skill solves is decision discipline under uncertainty: teams confuse "minimum to learn" with "minimum to launch," add non-critical features too early, and lose months before validating value. This research updates the skill with current (2024-2026) evidence on ruthless scope reduction, dependency-aware prioritization, interpretation quality (risk/effort/learning), and anti-pattern prevention.

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
- [x] No invented tool names, method IDs, or API endpoints - only verified references
- [x] Contradictions between sources are explicitly noted, not silently resolved
- [x] Volume: findings section is substantial and synthesized, not a source dump

---

## Research Angles

Each angle below was researched independently, then synthesized into unified recommendations for `SKILL.md`.

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

1) **Methodological split is now essential: `Experiment Scope` vs `Release Scope`.**  
Modern product literature still mixes "MVP test" (smallest learning artifact) and "MVP release" (smallest viable shippable product). Current public standards (e.g., Canada Digital Standards) define MVP as minimal feature set for critical user needs, while product-model experts (SVPG) keep stronger discovery-vs-delivery separation. For this skill, collapsing both leads to overbuild.  
Sources: https://www.canada.ca/en/government/system/digital-government/government-canada-digital-standards/iterate-improve-frequently.html (2025-01 update), https://www.svpg.com/minimum-viable-product/ (2011, **EVERGREEN**)

2) **AI-era execution speed increases scope risk unless batch size discipline is explicit.**  
DORA 2024 reports AI adoption improves documentation/code/review speed but correlates with lower throughput and stability when teams let changesets grow. For `mvp-scope`, this supports strict small-batch inclusion rules and explicit exclusion lists.  
Sources: https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report (2024-10), https://dora.dev/research/2024/dora-report/2024-dora-accelerate-state-of-devops-report.pdf (2024)

3) **Priority instability destroys delivery performance even in high-capability teams.**  
DORA 2024 highlights unstable priorities as a strong drag on productivity and developer outcomes. MVP scope therefore needs change-control rules and scope-freeze windows.  
Sources: https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report (2024), https://dora.dev/research/2024/dora-report/2024-dora-accelerate-state-of-devops-report.pdf (2024)

4) **Cross-functional co-scoping is still underused and should be mandatory.**  
Atlassian State of Product 2026 reports widespread concerns about product failure and weak early engineering involvement. This directly supports a skill rule that PM, design, and engineering must co-author MVP scope from the first pass.  
Sources: https://www.atlassian.com/software/jira/product-discovery/resources/state-of-product-2026 (2026 report page), https://www.atlassian.com/blog/announcements/state-of-product-2026 (2025/2026 report publication context)

5) **Most shipped features still concentrate value in a very small subset.**  
Pendo 2024 benchmark: ~6.4% of features drive 80% of clicks on average. For MVP scoping, this is quantitative support for aggressive feature exclusion and for explicit "manual workaround first" logic.  
Sources: https://www.pendo.io/pendo-blog/product-benchmarks/ (2024-06), https://www.pendo.io/product-benchmarks/ (2024 benchmark program)

6) **Decision latency is a hidden scoping cost.**  
Productboard 2024 research notes long lead times for key product decisions in larger orgs. This supports introducing explicit decision SLAs/timeboxes into the skill.  
Sources: https://www.productboard.com/lp/2024-product-excellence-report/ (2024)

7) **Operating-model preconditions matter as much as prioritization mechanics.**  
`TRANSFORMED` (2024) emphasizes product operating model transition: empowerment, ownership clarity, and discovery hygiene. MVP scoping without decision-right clarity degrades into backlog politics.  
Sources: https://www.oreilly.com/library/view/transformed/9781119697336/ (2024-03), https://www.svpg.com/books/transformed-moving-to-the-product-operating-model/ (2024 context)

8) **Contradiction to encode, not ignore:**  
Some teams treat MVP as "direct releasable slice," others treat it as "cheapest valid test." Both appear in modern practice. The skill should force explicit declaration of which mode is being executed each cycle.

**Sources:**
- https://www.canada.ca/en/government/system/digital-government/government-canada-digital-standards/iterate-improve-frequently.html
- https://www.svpg.com/minimum-viable-product/
- https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report
- https://dora.dev/research/2024/dora-report/2024-dora-accelerate-state-of-devops-report.pdf
- https://www.atlassian.com/software/jira/product-discovery/resources/state-of-product-2026
- https://www.atlassian.com/blog/announcements/state-of-product-2026
- https://www.pendo.io/pendo-blog/product-benchmarks/
- https://www.pendo.io/product-benchmarks/
- https://www.productboard.com/lp/2024-product-excellence-report/
- https://www.oreilly.com/library/view/transformed/9781119697336/
- https://www.svpg.com/books/transformed-moving-to-the-product-operating-model/

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

1) **Prioritization scoring is practical only when formulas are explicit and auditable.**  
Jira Product Discovery supports custom formulas (RICE/ICE-like fields), but expression limitations and data hygiene issues can silently distort scores.  
Sources: https://support.atlassian.com/jira-product-discovery/docs/expression-based-formulas/ (accessed 2026-03), https://www.atlassian.com/software/jira/product-discovery/guides/fields/overview (current docs)

2) **Aha! supports advanced scorecards but advanced automation is plan-gated.**  
Equation-based scorecards and automated metrics exist; operationally useful, but enterprise plan constraints and migration caveats mean process controls are required.  
Sources: https://aha.io/support/roadmaps/strategic-roadmaps/customizations/create-aha-scorecards (current docs), https://aha.io/support/roadmaps/strategic-roadmaps/enterprise-functionality/automated-scorecard-metrics (current docs), https://aha.io/roadmaps/pricing

3) **Dependency mapping requires explicit graph discipline, not just list prioritization.**  
Jira Advanced Roadmaps, Airtable Gantt, and Linear each provide dependency visualization, but each has boundary constraints (plan inclusion, model limitations, relation-type constraints).  
Sources: https://support.atlassian.com/jira-software-cloud/docs/view-and-manage-dependencies-in-advanced-roadmaps/ , https://support.airtable.com/docs/gantt-view-milestones-dependencies-and-critical-paths , https://linear.app/docs/project-dependencies

4) **Experiment/analytics tools are now direct scoping inputs, but constraints differ materially.**  
Amplitude, Mixpanel, LaunchDarkly, and Statsig provide data for scope decisions, but instrumentation limits, pricing curves, and entitlement models can bias what teams choose to measure.  
Sources: https://amplitude.com/docs/faq/limits (2024-07 page), https://amplitude.com/pricing , https://docs.mixpanel.com/docs/pricing , https://mixpanel.com/pricing/ , https://launchdarkly.com/pricing , https://docs.launchdarkly.com/home/account/calculating-billing , https://www.statsig.com/pricing/

5) **AI planning assistants are useful for synthesis, not for authority.**  
Atlassian Rovo and similar features accelerate drafting/summarization but explicitly warn about output quality variability. Skill instructions should keep AI-generated scope suggestions as proposals, not accepted truth.  
Sources: https://support.atlassian.com/jira-product-discovery/docs/explore-atlassian-intelligence-in-jira-product-discovery/ , https://www.atlassian.com/software/jira/product-discovery/pricing

6) **No single tool resolves scope quality; process must define data contract.**  
Best practice is dual traceability: every in-scope feature references one hypothesis and one measurable validation signal, independent of tooling stack.

7) **Practical minimum stack for MVP scope decisions:**  
- one prioritization board with explicit formula fields,  
- one dependency graph view,  
- one experiment/usage evidence source,  
- one policy artifact record with inclusion/exclusion rationale.

8) **Tool-related contradiction:**  
"all-in-one PM suites" promise fewer handoffs, while warehouse-native experimentation stacks provide higher evidence rigor. Teams must choose based on decision criticality and data maturity.

**Sources:**
- https://support.atlassian.com/jira-product-discovery/docs/expression-based-formulas/
- https://www.atlassian.com/software/jira/product-discovery/guides/fields/overview
- https://www.atlassian.com/software/jira/product-discovery/pricing
- https://aha.io/support/roadmaps/strategic-roadmaps/customizations/create-aha-scorecards
- https://aha.io/support/roadmaps/strategic-roadmaps/enterprise-functionality/automated-scorecard-metrics
- https://aha.io/roadmaps/pricing
- https://support.atlassian.com/jira-software-cloud/docs/view-and-manage-dependencies-in-advanced-roadmaps/
- https://support.airtable.com/docs/gantt-view-milestones-dependencies-and-critical-paths
- https://linear.app/docs/project-dependencies
- https://amplitude.com/docs/faq/limits
- https://amplitude.com/pricing
- https://docs.mixpanel.com/docs/pricing
- https://mixpanel.com/pricing/
- https://launchdarkly.com/pricing
- https://docs.launchdarkly.com/home/account/calculating-billing
- https://www.statsig.com/pricing/
- https://support.atlassian.com/jira-product-discovery/docs/explore-atlassian-intelligence-in-jira-product-discovery/

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

1) **No ship/no-ship interpretation is valid without a predeclared evidence plan.**  
At minimum, `alpha`, `power`, and target `MDE` must be set before using experiment outcomes for scope escalation decisions.  
Sources: https://docs.statsig.com/experiments/power-analysis (current docs), https://docs.geteppo.com/statistics/sample-size-calculator/usage/ (current docs)

2) **Population mismatch can invalidate "good-looking" results.**  
If experiment sizing/interpretation uses broad population while exposure targets a subset, decision confidence is overstated.  
Source: https://docs.statsig.com/experiments/power-analysis

3) **Guardrails must be interpreted via non-inferiority logic, not "not significant = safe."**  
For MVP scaling decisions, positive primary movement does not override critical guardrail harm.  
Sources: https://docs.geteppo.com/statistics/sample-size-calculator/usage/ , https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics

4) **Peeking under fixed-horizon testing inflates false positives.**  
If teams require frequent checks, they must use sequential-valid methodology and predeclared stopping rules.  
Sources: https://www.statsig.com/blog/sequential-testing-on-statsig (2023, **EVERGREEN** method guidance), https://www.statsig.com/perspectives/sequential-vs-fixed-testing-methods-analysis (2025)

5) **Interpretation should distinguish intent: learning vs shipping.**  
Directional low-N evidence can be acceptable for learning pivots, but shipping/scale calls require stronger evidence tiers and explicit risk constraints.  
Sources: https://blog.superhuman.com/how-superhuman-built-an-engine-to-find-product-market-fit/ (2018, **EVERGREEN** for PMF signal practice), https://docs.statsig.com/experiments/power-analysis

6) **RICE and WSJF are complementary under uncertainty, not substitutes.**  
RICE offers confidence-weighted impact scoring, WSJF adds time criticality and risk-reduction logic. Rank divergence should trigger review, not arbitrary choice.  
Sources: https://productplan.com/glossary/rice-scoring-model/ (**EVERGREEN** secondary synthesis), https://scaledagileframework.com/wsjf/ (**EVERGREEN**)

7) **Stage-gate "scale or discontinue" logic improves uncertainty handling.**  
Recent OECD guidance supports time-bound experimentation and explicit scaling/discontinuation criteria, aligning with MVP phase gates.  
Source: https://www.oecd.org/content/dam/oecd/en/publications/reports/2024/12/how-to-best-use-sti-policy-experimentation-to-support-transitions_99ddf48f/7b246309-en.pdf (2024-12)

8) **Risk governance should be embedded before escalation.**  
NIST AI RMF and GenAI profile updates reinforce structured trust/risk dimensions before broader rollout of uncertain systems.  
Sources: https://www.nist.gov/itl/ai-risk-management-framework (2024 update context), https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence (2024-07)

9) **PMF threshold guidance can inform, but not replace, causal validation.**  
The Sean Ellis "very disappointed >= 40%" threshold remains useful as a directional signal; it is insufficient alone for major scope expansion decisions.  
Sources: https://blog.superhuman.com/how-superhuman-built-an-engine-to-find-product-market-fit/ (2018, **EVERGREEN**), https://www.oreilly.com/content/evaluate-a-productmarket-fit/ (2018, **EVERGREEN**)

**Sources:**
- https://docs.statsig.com/experiments/power-analysis
- https://docs.geteppo.com/statistics/sample-size-calculator/usage/
- https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics
- https://www.statsig.com/blog/sequential-testing-on-statsig
- https://www.statsig.com/perspectives/sequential-vs-fixed-testing-methods-analysis
- https://blog.superhuman.com/how-superhuman-built-an-engine-to-find-product-market-fit/
- https://productplan.com/glossary/rice-scoring-model/
- https://scaledagileframework.com/wsjf/
- https://www.oecd.org/content/dam/oecd/en/publications/reports/2024/12/how-to-best-use-sti-policy-experimentation-to-support-transitions_99ddf48f/7b246309-en.pdf
- https://www.nist.gov/itl/ai-risk-management-framework
- https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
- https://www.oreilly.com/content/evaluate-a-productmarket-fit/

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

1) **Discovery debt (build before validating demand).**  
Teams overinvest in product construction before validating the problem with the target buyer and willingness to pay.  
Sources: https://glassboxmedicine.com/2026/02/21/why-i-shut-down-my-bootstrapped-health-ai-startup-after-7-years-a-founders-postmortem/ (2026), https://medium.com/@martigouca/learnings-of-not-finding-product-market-fit-in-a-24-b2b-saas-startup-98911c9ee565 (2024)

2) **MVP inflation ("mini-V1" disguised as MVP).**  
Scope expands to include secondary jobs, causing long lead times and weak learning velocity.  
Sources: https://linear.app/blog/rethinking-the-startup-mvp-building-a-competitive-product (2024), https://medium.com/@martigouca/learnings-of-not-finding-product-market-fit-in-a-24-b2b-saas-startup-98911c9ee565

3) **Vanity validation (interest mistaken for willingness to pay).**  
Positive interviews/demos are treated as evidence of PMF without paid commitment tests.  
Sources: https://medium.com/@martigouca/learnings-of-not-finding-product-market-fit-in-a-24-b2b-saas-startup-98911c9ee565 , https://glassboxmedicine.com/2026/02/21/why-i-shut-down-my-bootstrapped-health-ai-startup-after-7-years-a-founders-postmortem/

4) **ICP sprawl and positioning drift.**  
Teams expand scope for multiple personas before proving one primary workflow.  
Sources: https://techcrunch.com/2024/01/12/instagram-co-founders-news-aggregation-startup-artifact-to-shut-down/ (2024), https://linear.app/blog/rethinking-the-startup-mvp-building-a-competitive-product

5) **Investor-led roadmap distortion.**  
Scope follows fundraising narrative instead of validated user evidence.  
Sources: https://techcrunch.com/2024/04/03/openai-backed-ghost-autonomy-shuts-down/ (2024), https://medium.com/@martigouca/learnings-of-not-finding-product-market-fit-in-a-24-b2b-saas-startup-98911c9ee565

6) **Scope creep via incremental "one more thing" additions.**  
Each addition looks reasonable alone; together they erase MVP constraints and delay learning.  
Sources: https://blog.logrocket.com/product-management/4-practical-lessons-from-dealing-with-feature-creep/ (2025), https://linear.app/blog/rethinking-the-startup-mvp-building-a-competitive-product

7) **Feature preservation bias.**  
Teams keep low-value features because sunk cost feels like evidence.  
Source: https://www.infobip.com/engineering/we-killed-a-key-feature-from-our-mvp-and-built-a-better-product (2024)

8) **Workflow-external MVP design.**  
Product sits outside the user's real system-of-record workflow, creating low sustained adoption.  
Source: https://glassboxmedicine.com/2026/02/21/why-i-shut-down-my-bootstrapped-health-ai-startup-after-7-years-a-founders-postmortem/

9) **Custom development trap.**  
One large customer request consumes MVP team capacity and delays generalizable product validation.  
Source: https://glassboxmedicine.com/2026/02/21/why-i-shut-down-my-bootstrapped-health-ai-startup-after-7-years-a-founders-postmortem/

10) **Unit economics mirage.**  
Adoption signals are interpreted as success while margins/payback remain structurally unsustainable.  
Sources: https://techcrunch.com/2024/09/12/cohost-the-x-rival-founded-with-an-anti-big-tech-manifesto-is-running-out-of-money-and-will-shut-down/ (2024), https://glassboxmedicine.com/2026/02/21/why-i-shut-down-my-bootstrapped-health-ai-startup-after-7-years-a-founders-postmortem/

11) **Launch theater (marketing scale before learning scale).**  
Teams maximize launch optics before meeting reliability, retention, and usage thresholds.  
Sources: https://arstechnica.com/gadgets/2024/06/report-humane-ai-pin-did-7-million-in-sales-wants-to-sell-for-1-billion/ (2024), https://techcrunch.com/2020/06/23/what-went-wrong-with-quibi/ (2020, **EVERGREEN**), https://www.npr.org/transcripts/525310236 (2017, **EVERGREEN**)

**Sources:**
- https://glassboxmedicine.com/2026/02/21/why-i-shut-down-my-bootstrapped-health-ai-startup-after-7-years-a-founders-postmortem/
- https://medium.com/@martigouca/learnings-of-not-finding-product-market-fit-in-a-24-b2b-saas-startup-98911c9ee565
- https://linear.app/blog/rethinking-the-startup-mvp-building-a-competitive-product
- https://techcrunch.com/2024/01/12/instagram-co-founders-news-aggregation-startup-artifact-to-shut-down/
- https://techcrunch.com/2024/04/03/openai-backed-ghost-autonomy-shuts-down/
- https://blog.logrocket.com/product-management/4-practical-lessons-from-dealing-with-feature-creep/
- https://www.infobip.com/engineering/we-killed-a-key-feature-from-our-mvp-and-built-a-better-product
- https://techcrunch.com/2024/09/12/cohost-the-x-rival-founded-with-an-anti-big-tech-manifesto-is-running-out-of-money-and-will-shut-down/
- https://arstechnica.com/gadgets/2024/06/report-humane-ai-pin-did-7-million-in-sales-wants-to-sell-for-1-billion/
- https://techcrunch.com/2020/06/23/what-went-wrong-with-quibi/
- https://www.npr.org/transcripts/525310236

---

### Angle 5+: Adjacent Skill Contract and Dependency Fit
> Domain-specific angle: how `mvp-scope` should interoperate with adjacent strategist skills (`mvp-feasibility`, `mvp-validation-criteria`, `mvp-roadmap`) so that outputs are decision-usable end-to-end.

**Findings:**

1) `mvp-feasibility` expects explicit risk/dependency inventory, so `mvp-scope` should emit dependency-criticality metadata per in-scope feature.  
Named reference: `strategist/skills/mvp-feasibility/SKILL.md`

2) `mvp-validation-criteria` requires measurable PMF signals and thresholds, so `mvp-scope` should bind each in-scope feature to a primary measurement signal and intended decision type (`explore` vs `ship`).  
Named reference: `strategist/skills/mvp-validation-criteria/SKILL.md`

3) `mvp-roadmap` is phase-gated and conditional, so `mvp-scope` should explicitly encode what evidence triggers progression and what evidence triggers de-scope/pivot.  
Named reference: `strategist/skills/mvp-roadmap/SKILL.md`

4) Current `mvp-scope` schema captures inclusion/exclusion but not confidence quality and dependency severity, which creates handoff ambiguity for downstream skills.  
Named references: `strategist/skills/mvp-scope/SKILL.md`, `strategist/skills/mvp-feasibility/SKILL.md`

5) A minimal interoperability upgrade is to add optional (not initially required) fields for `decision_intent`, `evidence_tier`, `dependency_severity`, and `measurement_link`. This preserves compatibility and improves downstream automation quality.

**Sources:**
- `strategist/skills/mvp-scope/SKILL.md`
- `strategist/skills/mvp-feasibility/SKILL.md`
- `strategist/skills/mvp-validation-criteria/SKILL.md`
- `strategist/skills/mvp-roadmap/SKILL.md`

---

## Synthesis

The dominant 2024-2026 signal is that MVP scoping fails less from "bad prioritization formula choice" and more from missing operating discipline: unstable priorities, weak evidence gates, and failure to separate learning scope from shipping scope. Quantitative benchmarks (DORA, Pendo) and operator postmortems converge on one point: teams overbuild before validating the core hypothesis.

There is a real contradiction to preserve explicitly in the skill: some sources describe MVP as minimal releasable product, while others define an MVP test as a pre-release learning artifact. Instead of picking one side, the skill should force users to declare mode per cycle (`experiment scope` or `release scope`) and apply different evidence thresholds accordingly.

Tooling has matured but does not remove judgment risk. Prioritization platforms can produce precise-looking scores from poor inputs, and analytics stacks can produce significant-looking results from weak interpretation design. Therefore, `mvp-scope` should include both input quality controls (co-scoping, dependency mapping, manual workaround economics) and interpretation quality controls (decision intent, evidence tier, guardrail logic).

Failure-mode evidence from recent shutdown/postmortem material is consistent: discovery debt, vanity validation, ICP drift, scope creep, and unit economics blindness recur across categories. The practical implication is to encode anti-pattern detection signals directly in the skill output schema, not just as narrative warnings.

The most actionable upgrade is an end-to-end contract: `mvp-scope` should emit richer, still backward-compatible fields that downstream skills can consume without reinterpretation. This creates a coherent chain from hypothesis -> scope -> feasibility -> validation criteria -> roadmap.

---

## Recommendations for SKILL.md

> Concrete changes to add to `mvp-scope/SKILL.md`.

- [x] Add explicit `Scope Mode` declaration (`experiment_scope` vs `release_scope`) and explain why both are not interchangeable.
- [x] Add a strict step-by-step scoping workflow with decision gates and timeboxes.
- [x] Add evidence quality guardrails (`decision_intent`, `evidence_tier`, `confidence_level`) for each in-scope feature.
- [x] Add dependency severity + manual workaround economics fields per feature.
- [x] Add cross-functional co-scoping requirement (PM + design + engineering).
- [x] Add explicit scope-freeze/change-control rule for MVP cycle.
- [x] Add anti-pattern warning blocks with detection signals and exact mitigation playbooks.
- [x] Expand `Available Tools` section with evidence-gathering syntax blocks (without invented methods).
- [x] Expand artifact schema with optional interoperability fields consumed by adjacent skills.
- [x] Add explicit "Do not escalate to roadmap phase planning until criteria are met" instruction.

---

## Draft Content for SKILL.md

### Draft: Core framing and operating mode

---
### Core mode: scope to learn, not to impress

You are defining MVP scope to maximize validated learning per unit time, not to maximize feature completeness. Your default stance is exclusion. Every included feature must carry one burden of proof: **without this feature, the core hypothesis cannot be validly tested**.

Before writing in-scope features, declare one operating mode:

- `experiment_scope`: smallest implementation that can validate/disprove the core hypothesis with acceptable confidence.
- `release_scope`: smallest user-facing release that can deliver the core job safely enough for pilot commitments.

Do not blend these modes. If you blend them, you lose both speed (experiment quality drops) and reliability (release quality is under-specified).

If you cannot explain in one sentence why this cycle is `experiment_scope` or `release_scope`, pause and resolve that ambiguity first.
---

### Draft: Methodology rewrite (step-by-step with decision gates)

---
### Step 1 - Lock the hypothesis and decision intent

Before feature discussion, activate and read current strategic context:

```text
flexus_policy_document(op="activate", args={"p": "/strategy/hypothesis-stack"})
flexus_policy_document(op="activate", args={"p": "/strategy/offer-design"})
flexus_policy_document(op="activate", args={"p": "/discovery/{study_id}/jtbd-outcomes"})
```

Then define:

1. `core_hypothesis_ref`: one P0 hypothesis ID.
2. `decision_intent`: `explore` or `ship`.
3. `scope_mode`: `experiment_scope` or `release_scope`.

Rules:

- If `decision_intent=ship`, you must use `release_scope`.
- If `scope_mode=experiment_scope`, at least one major capability may be intentionally manual or simulated.
- If multiple P0 hypotheses appear, split into separate MVP cycles. Never optimize one scope for multiple independent unknowns.

Rationale: mixed intent is one of the fastest ways to over-scope and stall validation.
---

### Step 2 - Feature candidate intake with explicit exclusion-first logic

For each candidate feature, answer in order:

1. Does this feature directly enable the core job for the primary persona?
2. Without it, can we still measure the primary decision metric?
3. Can a manual workaround provide equivalent learning for first pilots?
4. Is this feature for the primary persona, or for a secondary persona?

Decision:

- Include only if answers are: `yes`, `no`, `no`, `primary persona`.
- Exclude if any answer indicates secondary value, delayed impact, or workaround viability.

Do not write "might be useful later" in in-scope rationale. That belongs in `out_of_scope_features` with future milestone notes.
---

### Step 3 - Dependency and critical-path pressure test

For each candidate in-scope feature, document:

- hard dependencies,
- dependency severity (`critical|high|medium|low`),
- fallback if dependency fails,
- whether fallback preserves learning quality.

If any feature has unresolved `critical` dependency with no fallback, either:

- de-scope the feature, or
- convert cycle to `experiment_scope` with a manual/simulated workaround.

Do not accept ambiguous "we will figure this dependency out later." That language predicts timeline slips and fake confidence.
---

### Step 4 - Evidence contract per feature

Each included feature must define:

- one primary success signal,
- at least one guardrail signal,
- expected direction,
- minimum practical effect needed for progression decision.

If `decision_intent=ship`, require stronger evidence tier and guardrail pass condition before escalation.

If `decision_intent=explore`, directional evidence is acceptable, but output must explicitly state confidence limitations.
---

### Step 5 - Scope freeze and change-control

After initial inclusion/exclusion is documented, freeze scope for the current cycle window.

Allowed scope changes during freeze:

- blocker discovered that invalidates core test design,
- critical compliance/safety issue,
- hard dependency failure with no viable workaround.

Not allowed during freeze:

- stakeholder preference shifts without new evidence,
- "one more feature" additions,
- roadmap alignment arguments not tied to the cycle hypothesis.

Every approved change must append:

- change reason,
- evidence link,
- expected delay impact,
- expected learning impact.
---

### Step 6 - Output with downstream interoperability

Record `mvp_scope` so downstream skills can consume without reinterpretation:

```text
write_artifact(artifact_type="mvp_scope", path="/strategy/mvp-scope", data={...})
```

Before finalizing, run a final check:

- Can `mvp-feasibility` directly evaluate technical and dependency risk from this artifact?
- Can `mvp-validation-criteria` directly derive measurable thresholds?
- Can `mvp-roadmap` use this artifact to define phase gate preconditions?

If any answer is no, revise schema fields and rationale granularity before write.
---

### Draft: Evidence quality instructions and thresholds

---
### Evidence quality policy

Use evidence tiers to avoid mixing weak learning signals with strong shipping decisions:

- `T1`: qualitative signal (interviews, user narratives, directional feedback).
- `T2`: directional quantitative signal (small N, trend-level confidence).
- `T3`: decision-grade quantitative signal with predeclared measurement plan.

Rules:

- `decision_intent=explore` allows `T1` or `T2`.
- `decision_intent=ship` requires `T3` plus guardrail pass.
- If evidence tier is below required threshold, output must force `defer` or `continue_learning` recommendation.

Recommended defaults (adapt per domain):

- PMF directional threshold: `very_disappointed >= 40%` can support learning direction, but does not alone justify scale commitment (Evergreen source: Superhuman PMF framework).
- For experiment-grade decisions, predeclare `alpha`, `power`, and target effect size; do not retrofit after seeing results.
- If fixed-horizon inference is used, prohibit peeking-based decisioning.

Sources for these rules should be attached in rationale metadata where applicable:
- DORA 2024 (batch size and stability implications),
- Statsig/Eppo power and guardrail guidance,
- PMF directional benchmark references.
---

### Draft: Available Tools (syntax blocks)

```text
## Available Tools

flexus_policy_document(op="activate", args={"p": "/strategy/hypothesis-stack"})
flexus_policy_document(op="activate", args={"p": "/strategy/offer-design"})
flexus_policy_document(op="activate", args={"p": "/discovery/{study_id}/jtbd-outcomes"})

write_artifact(artifact_type="mvp_scope", path="/strategy/mvp-scope", data={...})
```

```text
## Optional research context checks (external references)

web(open=[{"url": "https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report"}])
web(open=[{"url": "https://www.pendo.io/pendo-blog/product-benchmarks/"}])
web(open=[{"url": "https://www.canada.ca/en/government/system/digital-government/government-canada-digital-standards/iterate-improve-frequently.html"}])
web(open=[{"url": "https://www.atlassian.com/software/jira/product-discovery/resources/state-of-product-2026"}])
```

Tool usage guidance:

- Use `flexus_policy_document` first; never scope features without current hypothesis and JTBD context.
- Use external `web(...)` sources only to calibrate methodology and thresholds, not to override local product context.
- Do not cite unsourced or AI-generated summaries as evidence. Use direct references only.

### Draft: Anti-pattern warning blocks

### Warning: Discovery Debt

**What it looks like:** MVP scope drafted from internal assumptions, with limited direct buyer evidence.  
**Detection signal:** no paid commitment signal, low count of target-persona interviews, scope includes many "should-have" items.  
**Consequence if missed:** long build cycle that validates little.  
**Mitigation:** pause scope, run focused discovery sprint, require at least one monetary commitment signal before resuming.

### Warning: Mini-V1 Disguised as MVP

**What it looks like:** multiple workflows, broad persona coverage, extensive polishing in first cycle.  
**Detection signal:** feature count grows while hypothesis count remains unchanged; timeline drifts from weeks to quarters.  
**Consequence if missed:** delayed learning and high burn.  
**Mitigation:** enforce one-core-workflow rule; move all secondary workflows to explicit out-of-scope list.

### Warning: Vanity Validation

**What it looks like:** positive sentiment or usage anecdotes treated as PMF proof.  
**Detection signal:** low conversion to paid pilots despite high interest.  
**Consequence if missed:** false-positive confidence and bad capital allocation.  
**Mitigation:** add willingness-to-pay check and explicit cash-evidence criterion to acceptance logic.

### Warning: Scope Creep by Increment

**What it looks like:** frequent "small" additions justified as low effort.  
**Detection signal:** scope changes without new hypothesis evidence.  
**Consequence if missed:** unstable priorities and delivery risk.  
**Mitigation:** scope freeze policy with strict change admission criteria.

### Warning: Workflow-External Scope

**What it looks like:** MVP assumes users will switch context manually across tools/systems.  
**Detection signal:** core action depends on repetitive copy/paste or non-owner roles.  
**Consequence if missed:** poor real-world adoption despite apparent pilot interest.  
**Mitigation:** prioritize system-of-record integration or operational workaround that removes friction from core job execution.

### Draft: Decision rubric fragment for feature inclusion

Use this rubric per candidate feature:

- `core_job_criticality` (0-5)
- `measurement_criticality` (0-5)
- `manual_workaround_feasibility` (0-5, high means workaround is easy)
- `dependency_risk` (0-5)
- `learning_yield` (0-5)
- `effort_weeks` (number)

Decision rule:

- Include if `core_job_criticality >= 4` AND `measurement_criticality >= 4` AND `manual_workaround_feasibility <= 2`.
- Exclude if `manual_workaround_feasibility >= 4` unless legal/safety constraints prohibit workaround.
- Escalate for review if `dependency_risk >= 4` and fallback is missing.

For tie-breaking between similar features:

1. Prefer higher `learning_yield`.
2. Prefer lower `dependency_risk`.
3. Prefer lower `effort_weeks`.

This keeps scope decisions test-centric and defensible.

### Draft: Schema additions

The fragment below is designed to be backward-compatible with current `mvp_scope` shape: existing required fields stay intact; new fields are added with explicit descriptions and strict object boundaries.

```json
{
  "mvp_scope": {
    "type": "object",
    "required": [
      "created_at",
      "core_hypothesis_ref",
      "target_persona",
      "core_job",
      "in_scope_features",
      "out_of_scope_features",
      "manual_workarounds",
      "acceptance_criteria",
      "exclusion_rationale"
    ],
    "additionalProperties": false,
    "properties": {
      "created_at": {
        "type": "string",
        "description": "ISO timestamp when the scope artifact was generated."
      },
      "core_hypothesis_ref": {
        "type": "string",
        "description": "Reference ID of the single P0 hypothesis this MVP cycle validates."
      },
      "target_persona": {
        "type": "string",
        "description": "Primary persona this MVP is scoped for. Secondary personas must be excluded."
      },
      "core_job": {
        "type": "string",
        "description": "The primary job-to-be-done that must be delivered in this cycle."
      },
      "scope_mode": {
        "type": "string",
        "enum": ["experiment_scope", "release_scope"],
        "description": "Declares whether this cycle optimizes for fastest valid learning or minimal releasable pilot value."
      },
      "decision_intent": {
        "type": "string",
        "enum": ["explore", "ship"],
        "description": "Defines evidence bar for decisions. Explore accepts directional evidence; ship requires stronger quantitative support."
      },
      "evidence_tier_target": {
        "type": "string",
        "enum": ["T1", "T2", "T3"],
        "description": "Minimum evidence quality expected before escalating beyond current MVP cycle."
      },
      "scope_freeze_window_days": {
        "type": "integer",
        "minimum": 1,
        "description": "Number of days during which scope additions are blocked unless explicit exception criteria are met."
      },
      "change_control_policy": {
        "type": "object",
        "required": ["allowed_reasons", "blocked_reasons", "log_required_fields"],
        "additionalProperties": false,
        "properties": {
          "allowed_reasons": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Reasons that can justify scope changes during freeze (e.g., blocker, compliance issue)."
          },
          "blocked_reasons": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Reasons that cannot justify scope changes (e.g., preference-only additions)."
          },
          "log_required_fields": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Mandatory metadata fields for each approved scope change."
          }
        }
      },
      "in_scope_features": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["feature", "rationale", "acceptance_criteria"],
          "additionalProperties": false,
          "properties": {
            "feature": {
              "type": "string",
              "description": "Feature name expressed as user-visible capability."
            },
            "rationale": {
              "type": "string",
              "description": "Evidence-backed reason this feature is necessary for core hypothesis validation."
            },
            "acceptance_criteria": {
              "type": "string",
              "description": "Minimum user-facing completion criteria for this feature in the current cycle."
            },
            "quality_floor": {
              "type": "string",
              "description": "Minimum non-negotiable quality bar for pilot viability."
            },
            "primary_signal": {
              "type": "string",
              "description": "Primary metric or observable behavior used to evaluate this feature's value contribution."
            },
            "guardrail_signals": {
              "type": "array",
              "items": {"type": "string"},
              "description": "Non-negotiable risk metrics that must not degrade beyond tolerated bounds."
            },
            "dependency_severity": {
              "type": "string",
              "enum": ["critical", "high", "medium", "low"],
              "description": "Severity of dependency risk for this feature in the MVP timeline."
            },
            "fallback_plan": {
              "type": "string",
              "description": "Action to preserve learning if dependency fails."
            },
            "learning_yield_score": {
              "type": "number",
              "minimum": 0,
              "maximum": 5,
              "description": "Estimated contribution of this feature to reducing core uncertainty."
            },
            "effort_estimate_weeks": {
              "type": "number",
              "minimum": 0,
              "description": "Estimated engineering effort in weeks for MVP-quality implementation."
            }
          }
        }
      },
      "out_of_scope_features": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["feature", "exclusion_reason"],
          "additionalProperties": false,
          "properties": {
            "feature": {
              "type": "string",
              "description": "Feature deferred from current MVP cycle."
            },
            "exclusion_reason": {
              "type": "string",
              "description": "Concrete reason for exclusion (secondary persona, workaround exists, weak evidence, etc.)."
            },
            "future_milestone": {
              "type": "string",
              "description": "Tentative milestone when reconsideration is allowed."
            },
            "reentry_trigger": {
              "type": "string",
              "description": "Evidence condition that must become true before this feature can be reconsidered."
            }
          }
        }
      },
      "manual_workarounds": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["capability_gap", "workaround_description", "cost_per_customer"],
          "additionalProperties": false,
          "properties": {
            "capability_gap": {
              "type": "string",
              "description": "Missing product capability replaced manually during MVP."
            },
            "workaround_description": {
              "type": "string",
              "description": "Exact manual process used to preserve test validity."
            },
            "cost_per_customer": {
              "type": "string",
              "description": "Estimated per-customer operational cost for workaround execution."
            },
            "max_customers_supported": {
              "type": "integer",
              "minimum": 1,
              "description": "Operational capacity limit for this workaround before automation becomes mandatory."
            }
          }
        }
      },
      "acceptance_criteria": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Global MVP-level completion criteria for this cycle."
      },
      "exclusion_rationale": {
        "type": "string",
        "description": "Summary explanation of exclusion strategy and tradeoffs."
      },
      "anti_pattern_checks": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["name", "status", "detection_signal", "mitigation"],
          "additionalProperties": false,
          "properties": {
            "name": {
              "type": "string",
              "description": "Anti-pattern label checked during scoping (e.g., Discovery Debt, Scope Creep)."
            },
            "status": {
              "type": "string",
              "enum": ["clear", "warning", "triggered"],
              "description": "Current observed risk state."
            },
            "detection_signal": {
              "type": "string",
              "description": "Observed indicator suggesting this anti-pattern is present."
            },
            "mitigation": {
              "type": "string",
              "description": "Action committed to reduce or remove the risk."
            }
          }
        }
      }
    }
  }
}
```

### Draft: Final instruction block to append near the end of SKILL.md

Use this policy every cycle:

1. One hypothesis, one scope mode, one decision intent.
2. Exclusion list must be as explicit as inclusion list.
3. No feature is in scope without measurable decision value.
4. No scope expansion during freeze without logged evidence.
5. If confidence is low, learn faster; do not build broader.

If these five conditions are not met, the artifact is not complete and should not be handed off to feasibility or roadmap planning.

---

## Gaps & Uncertainties

- Public 2024-2026 sources provide strong operational guidance but limited peer-reviewed, universal numeric thresholds for MVP feature-level inclusion decisions.
- Several tool capabilities/pricing constraints are plan- or tenant-specific and can change quickly; implementation-time verification remains mandatory.
- Postmortem evidence is often self-reported and may contain hindsight bias; patterns are useful but should not be treated as deterministic.
- Atlassian report detail is partly distributed across resource pages/blog/webinar collateral, so direct PDF-level metric extraction should be revalidated during final SKILL editing.
- Some evergreen references (SVPG, PMF heuristics) remain practically useful but are older; they should stay explicitly marked as evergreen to avoid recency confusion.
