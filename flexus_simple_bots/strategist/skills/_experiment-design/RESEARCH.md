# Research: experiment-design

**Skill path:** `strategist/skills/experiment-design/`
**Bot:** strategist (researcher | strategist | executor)
**Research date:** 2026-03-04
**Status:** complete

---

## Context

`experiment-design` defines the pre-launch contract for a single experiment: control and variants, success and guardrail metrics, sample size, instrumentation, and decision timeline. The current `SKILL.md` already emphasizes pre-registration and warns against post-hoc decisions.

2024-2026 practice confirms that this is the right core principle, but it also shows that strong experiment specs now need explicit decision-rule semantics, quality gates (for example SRM and assignment/exposure integrity), and explicit statistical regime choice (fixed-horizon vs sequential frequentist vs Bayesian). Tooling has also shifted toward hybrid feature-flag + warehouse-native workflows, which creates stronger requirements for identity contracts and event schema correctness.

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
- [x] All findings are from 2024–2026 unless explicitly marked as evergreen

---

## Quality Gates

Before marking status `complete`, verify:

- Concrete source-backed findings are used; no generic filler statements.
- Tool names, endpoints, and methods are only included when verified in source docs.
- Contradictions are documented explicitly (methodology and interpretation sections).
- Findings sections are within target depth (approx. 2,000+ words combined; inside 800-4000 range).

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

Modern teams treat experiment design as a decision-system design problem, not just a hypothesis document. A 2024 Spotify methodology formalizes a single ship/no-ship decision rule across metric roles (success metrics, guardrails, and quality checks), which reduces ad-hoc interpretation at readout time. This is directly aligned with the skill's pre-registration principle and suggests the skill should require explicit decision-rule syntax, not only metric lists.

Pre-registration has become operationally specific: teams are expected to lock hypotheses, metric definitions, exclusion rules, and stop/decision criteria before outcome inspection. OSF guidance remains a practical checklist source for this lock process, even outside academic domains, because it forces explicit if/then contingencies and analysis choices ahead of data.

Power planning practice in product experimentation has become more scenario-based: instead of one MDE guess, practitioners model multiple MDE/runtime scenarios, then pick a business-feasible operating point. Statsig, GrowthBook, and Eppo guidance all reinforce this operational framing and emphasize population-matched assumptions (variance and baseline must match the actual target population).

Metric hierarchy is now treated as a design constraint. Optimizely and Statsig documentation make clear that too many secondary/monitoring metrics increase multiplicity burden and slow useful decisioning. Practical best practice is one primary decision metric (or a very small set), explicit guardrails with predeclared thresholds, and limited exploratory metrics.

Randomization design has become first-class in specs: randomization unit selection (user/device/account/company), stable assignment policy, and no mid-test reassignment without reset logic. This is consistently emphasized in platform best-practice docs because invalid assignment policy can break causal claims even if significance appears strong.

SRM is not just a "nice to check" diagnostic anymore. Platform and industry references position SRM as a hard quality gate that can fully invalidate readout interpretation if triggered, requiring diagnosis before any shipping decision.

A practical 2024 update is pre-registered interim analysis design (PRIAD), which aims to keep confirmatory rigor while reducing data collection costs in suitable settings. While not universal for all product experiments, it indicates a broader trend: teams are moving from rigid single-look workflows toward preplanned adaptive workflows.

**Sources:**
- [Spotify engineering: risk-aware multi-metric decisions (2024)](https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics)
- [Risk-aware decision rules paper (2024)](https://arxiv.org/abs/2402.11609)
- [OSF pre-registration templates (updated 2026)](https://help.osf.io/article/229-select-a-registration-template)
- [Eppo analysis plans](https://docs.geteppo.com/experiment-analysis/configuration/analysis-plans/) (Evergreen)
- [Optimizely metric roles](https://support.optimizely.com/hc/en-us/articles/4410283160205-Primary-metrics-secondary-metrics-and-monitoring-goals) (Evergreen)
- [Statsig experiment setup docs](https://docs.statsig.com/experiments/create-new) (Evergreen)
- [Statsig power analysis docs](https://docs.statsig.com/experiments/power-analysis) (Evergreen)
- [GrowthBook power guidance](https://docs.growthbook.io/statistics/power) (Evergreen)
- [Eppo SRM guidance](https://docs.geteppo.com/statistics/sample-ratio-mismatch) (Evergreen)
- [PRIAD article metadata (2024)](https://ideas.repec.org/a/oup/jconrs/v51y2024i4p845-865..html)

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

The 2024-2026 tooling landscape converges around two architecture families: (1) integrated feature-flag + experimentation suites (LaunchDarkly, Statsig, Optimizely FE, PostHog, Amplitude) and (2) warehouse-native experimentation layers (GrowthBook, Eppo, Statsig Warehouse Native). Both require a strong event/identity contract to produce valid results.

LaunchDarkly provides experimentation APIs and published statistical methodology docs, but important API details are plan-gated and some experiment API surfaces are marked beta. It publishes 429 handling guidance and retry headers, but does not publish numeric API limits publicly; orchestration logic should therefore assume conservative backoff.

Statsig exposes a concrete Console API surface for experiments (`/console/v1/experiments` family), with explicit auth/version headers and documented mutation throttles. It also provides rich warehouse-native modes and explicit Segment/warehouse integration docs, making it strong for teams needing both product-native and warehouse-native patterns.

GrowthBook provides explicit API base/auth conventions and publishes a concrete 429 limit in docs (`60 requests/min` for the management API docs). It is strongly warehouse-centric and has very concrete assignment/exposure data-shape expectations (`user_id`, `timestamp`, `experiment_id`, `variation_id` style fields). This is valuable for schema design in `experiment_spec`.

Amplitude Experiment has a clear split between management APIs and evaluation APIs, with explicit management API rate limits and region endpoint conventions. It also documents key separation between deployment/evaluation keys and management keys. This supports robust governance if encoded in skill guidance.

PostHog documentation is unusually explicit about API classes and experimentation statistics docs (frequentist and Bayesian), including exposure-event expectations. It is operationally attractive for teams wanting one integrated product analytics + experimentation stack, but still requires strict exposure instrumentation discipline.

Optimizely FE has mature experimentation/stats support, but API usability includes caveats (for example FE "List Experiments" behavior differences and beta holdout surfaces). This means generated plans should include endpoint-level validation steps, not assume uniform API parity across product areas.

Eppo emphasizes warehouse-native governance and local-evaluation SDK patterns, with strong warehouse setup docs (BigQuery/Snowflake) and API key separation guidance. Public pricing detail is less explicit than some competitors in reviewed docs.

Cross-tool integration pattern: CDPs/warehouses (Segment, BigQuery, Snowflake) are now common and require strict identity mapping (anonymous/user/custom IDs). Missing or inconsistent identity contracts are one of the most common hidden failure sources.

**Sources:**
- [LaunchDarkly experiments API](https://launchdarkly.com/docs/api/experiments)
- [LaunchDarkly REST API guide](https://docs.launchdarkly.com/guides/api/rest-api/)
- [LaunchDarkly 429 guidance](https://support.launchdarkly.com/hc/en-us/articles/22328238491803-Error-429-Too-Many-Requests-API-Rate-Limit)
- [LaunchDarkly Bayesian methodology](https://launchdarkly.com/docs/guides/statistical-methodology/methodology-bayesian)
- [Statsig Console API overview](https://docs.statsig.com/console-api/experiments)
- [Statsig experiments API reference](https://docs.statsig.com/api-reference/experiments/list-experiments)
- [Statsig warehouse native experiment config](https://docs.statsig.com/statsig-warehouse-native/features/configure-an-experiment/)
- [Statsig Segment integration](https://docs.statsig.com/integrations/data-connectors/segment)
- [GrowthBook API docs](https://docs.growthbook.io/api/)
- [GrowthBook event forwarder contract](https://docs.growthbook.io/app/event-forwarder)
- [GrowthBook data sources schema expectations](https://docs.growthbook.io/app/datasources/)
- [GrowthBook pricing](https://www.growthbook.io/pricing)
- [Amplitude Experiment management API (updated 2026)](https://amplitude.com/docs/apis/experiment/experiment-management-api)
- [Amplitude evaluation API](https://amplitude.com/docs/apis/experiment/experiment-evaluation-api)
- [PostHog API docs](https://posthog.com/docs/api)
- [PostHog experiments exposure docs](https://posthog.com/docs/experiments/exposures)
- [PostHog frequentist methodology](https://posthog.com/docs/experiments/statistics-frequentist)
- [Optimizely FE API reference example](https://docs.developers.optimizely.com/feature-experimentation/reference/list_experiments)
- [Optimizely FE holdout endpoint](https://docs.developers.optimizely.com/feature-experimentation/reference/create_holdout)
- [Eppo warehouse connectors](https://docs.geteppo.com/data-management/connecting-dwh/bigquery)
- [Eppo REST API reference](https://docs.geteppo.com/reference/api/)

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

The largest interpretation error source remains regime confusion: teams mix fixed-horizon rules, sequential frequentist logic, and Bayesian interpretation in the same decision flow. Current vendor methodology docs are clear that these regimes have different guarantees and stopping semantics. The skill should require explicit regime selection before launch.

Fixed-horizon frequentist tests require predeclared stopping points for valid nominal error control. If teams continuously peek and stop on first significance without correction, false positives can increase materially. Sequential frequentist methods are designed for continuous monitoring but may trade off precision or power under some scenarios.

Baseline defaults in current practice remain stable (alpha near 0.05, power near 0.80, confidence near 95%), but 2024-2026 docs stress that these are defaults, not universal truth. High-stakes experiments may justify stricter settings with explicit runtime cost acceptance.

MDE selection is a business-statistics tradeoff, not a pure statistical preference. In practice, halving target effect size usually requires roughly 4x data/time. Teams that ignore this relationship either run indefinitely or interpret underpowered negative results incorrectly.

SRM and assignment-quality checks are core signal-validity gates. Platform docs expose concrete threshold policies (for example, strict chi-square thresholds or alert-tier logic) and recommend stopping interpretation until diagnosis if SRM/crossover anomalies appear.

Multiplicity from many metrics or many segments is still a frequent source of false discovery. Current docs and support content recommend explicit correction policies (FDR/FWER families) and predeclared segment analyses. Segment "wins" without multiplicity control should be treated as exploratory.

CUPED/CUPAC-style variance reduction remains high-impact but has eligibility assumptions: enough pre-period data, valid pre-treatment covariates, and no treatment leakage into predictors. Teams that treat CUPED/CUPAC as universal can introduce hidden bias.

Temporal dynamics matter: novelty effects and seasonality can create early uplift that decays. Practical guidance repeatedly recommends running at least one full business cycle and inspecting time-based stability before final ship/no-ship calls.

**Sources:**
- [LaunchDarkly choosing methodology](https://docs.launchdarkly.com/guides/statistical-methodology/choosing)
- [LaunchDarkly frequentist methodology](https://docs.launchdarkly.com/guides/statistical-methodology/methodology-frequentist)
- [LaunchDarkly sample size calculator guidance](https://docs.launchdarkly.com/guides/experimentation/sample-size-calc)
- [Eppo analysis methods](https://docs.geteppo.com/statistics/confidence-intervals/analysis-methods/)
- [Eppo analysis plans](https://docs.geteppo.com/experiment-analysis/configuration/analysis-plans/)
- [Statsig power analysis](https://docs.statsig.com/experiments/power-analysis)
- [Statsig differential impact detection](https://docs.statsig.com/experiments-plus/differential-impact-detection)
- [Statsig CUPED methodology](https://docs.statsig.com/stats-engine/methodologies/cuped/)
- [Eppo multiple testing](https://docs.geteppo.com/statistics/multiple-testing/)
- [Eppo SRM docs](https://docs.geteppo.com/statistics/sample-ratio-mismatch/)
- [PostHog Bayesian methodology docs](https://posthog.com/docs/experiments/statistics-bayesian)
- [Optimizely significance and time behavior](https://support.optimizely.com/hc/en-us/articles/4410289544589-How-and-why-statistical-significance-changes-over-time)
- [Always-valid inference (Evergreen, foundational)](https://arxiv.org/abs/1512.04922)
- [Statsig novelty effects (2024)](https://www.statsig.com/blog/novelty-effects)

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

**1) SRM ignored at readout time**
- Detection signal: realized split diverges from expected allocation, often with segment/time asymmetry.
- Prevention control: hard-stop rule for interpretation; mandatory SRM root-cause analysis first.
- Bad output: "Variant is significant, ship."
- Good output: "SRM failed; inference invalid pending assignment diagnostics."

**2) Assignment-exposure telemetry mismatch**
- Detection signal: assignment logs indicate one variant but exposure/render events do not align.
- Prevention control: assignment-vs-exposure reconciliation and A/A telemetry validation before launch.
- Bad output: "Cookie assignment is enough evidence."
- Good output: "Exposure pipeline mismatch detected; pause decision."

**3) Optional stopping without compatible statistics**
- Detection signal: frequent peeking and stop-on-first-significance behavior.
- Prevention control: either strict fixed-horizon stop or true sequential method chosen in advance.
- Bad output: "p<0.05 on day 2, done."
- Good output: "Decision follows predeclared stopping framework."

**4) Post-hoc hypothesis switching / metric cherry-picking**
- Detection signal: primary metric changes after seeing data; only favorable slices reported.
- Prevention control: immutable preregistration log and separation of confirmatory vs exploratory claims.
- Bad output: "Primary flat, but one secondary positive, so winner."
- Good output: "Primary decision failed; exploratory leads are follow-up hypotheses."

**5) Underpowered design interpreted as negative evidence**
- Detection signal: wide intervals, low exposure, and binary no-effect conclusions.
- Prevention control: prospective power/MDE checks and explicit "inconclusive" state in readout schema.
- Bad output: "No significance means no effect."
- Good output: "Result inconclusive at planned sensitivity."

**6) Interference and contamination ignored (marketplaces/networks)**
- Detection signal: estimates shift substantially between individual vs cluster/two-sided analyses.
- Prevention control: interference risk screening and alternative randomization strategies where needed.
- Bad output: "User-level randomization always works."
- Good output: "Design adjusted due to spillover risk."

**7) Novelty spikes mistaken for durable impact**
- Detection signal: large early uplifts decay over days since exposure.
- Prevention control: minimum runtime and stability checks by time slice before final decision.
- Bad output: "Day-2 spike proves long-term gain."
- Good output: "Decision deferred until stabilization window."

**8) Allocation-history blindness (dynamic ramp artifacts, Simpson-like reversals)**
- Detection signal: aggregate effect diverges from epoch-stratified effect after allocation changes.
- Prevention control: readout with allocation-aware/epoch-aware framing and restart rules after major allocation changes.
- Bad output: "Aggregate number is enough."
- Good output: "Allocation shifts accounted for before causal interpretation."

**Sources:**
- [LinkedIn variant assignment and SSRM causes](https://www.linkedin.com/blog/engineering/ab-testing-experimentation/a-b-testing-variant-assignment)
- [Lukas Vermeer SRM FAQ](https://www.lukasvermeer.nl/srm/docs/faq/)
- [CandyJapan case: invalidated A/B due to cookie issue](https://www.candyjapan.com/behind-the-scenes/previous-ab-test-results-invalidated) (Evergreen case study)
- [Statsig sequential testing](https://www.statsig.com/blog/sequential-testing-on-statsig)
- [Early stopping and repeated significance (2024)](https://arxiv.org/abs/2408.00908)
- [Automatic detection of biased online experiments (Evergreen)](https://arxiv.org/abs/1808.00114)
- [Spotify risk-aware decisions (2024)](https://arxiv.org/abs/2402.11609)
- [Airbnb cluster randomization interference evidence (2024)](https://business.columbia.edu/sites/default/files-efs/citation_file_upload/holtz-et-al-2024-reducing-interference-bias-in-online-marketplace-experiments-using-cluster-randomization-evidence-from%20(2).pdf)
- [Ranking interference bias evidence (2024)](https://ideas.repec.org/a/inm/ormksc/v43y2024i3p590-614.html)
- [Optimizely on Simpson's paradox controls](https://support.optimizely.com/hc/en-us/articles/5326213705101-History-of-how-Optimizely-Experimentation-controls-Simpson-s-Paradox-in-experiments-with-Stats-Accelerator-enabled)
- [Statsig novelty effects (2024)](https://www.statsig.com/blog/novelty-effects)

---

### Angle 5+: Program-Level Governance & Portfolio Impact
> Beyond single-test correctness, what improves long-run experimentation program outcomes?

**Findings:**

2024-2026 research and industry writing increasingly argues that local test significance is insufficient for program-level value management. Teams need a portfolio view that tracks cumulative impact, winner's-curse exposure, replication outcomes, and decision-rule quality over time.

A practical implication is to separate two questions in reporting: "Was this specific test statistically valid?" and "How well does our decision policy perform across many tests?" Spotify's 2024 work and newer portfolio-focused commentary both point to this distinction.

Replication and confirmation discipline is still necessary. External replication literature and experimentation-platform commentary both suggest one-off wins can overstate true long-run effect; staged rollout with confirmation checkpoints reduces false confidence.

Program governance also needs explicit language controls: causal claims should only appear when design assumptions hold, and exploratory segment findings should be labeled clearly to avoid accidental institutionalization of noise.

For the skill, this means adding metadata that supports portfolio learning: confidence tags, validity-gate outcomes, and follow-up requirements (replication, holdout, or extended monitoring) rather than single binary winner labels.

**Sources:**
- [Spotify risk-aware decisions (2024)](https://arxiv.org/abs/2402.11609)
- [Spotify engineering summary (2024)](https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics)
- [Eppo on cumulative impact pitfalls (2025)](https://www.geteppo.com/blog/rethinking-measuring-experimental-impact)
- [Nature Human Behaviour replication project (2024)](https://www.nature.com/articles/s41562-024-02062-9)

---

## Synthesis

The strongest cross-source agreement is that modern experiment design must be precommitted and operationally explicit. "Pre-registration" now means more than hypothesis text: it must include metric role definitions, stop/decision logic, multiplicity handling policy, and quality-gate checks. This aligns tightly with the current skill direction, but the existing skill should be expanded from a checklist to a stricter decision contract.

There is a real contradiction in stopping guidance across methods, but it is a methodological contradiction, not a source-quality problem. Fixed-horizon frequentist, sequential frequentist, and Bayesian approaches are each internally coherent but produce different guarantees and decision semantics. The skill should resolve this by forcing the author to pick exactly one statistical regime per experiment spec and blocking regime mixing.

A second important nuance is multiplicity and guardrails. Some modern decision-rule frameworks argue against blanket alpha correction for specific guardrail semantics, while platform defaults often apply broader correction controls. This should be surfaced as an explicit design choice in the skill: declare whether guardrails are strict non-inferiority constraints, exploratory monitors, or part of corrected family-wise inference.

Tooling findings show that API capability alone is not enough: identity schema, exposure logging, and governance modes (approval workflows, plan-gated APIs, undocumented limits) often decide whether a design can be executed safely. Therefore `experiment_spec` should carry integration-quality fields (assignment unit, exposure event schema, identity keys, API constraints/unknowns), not just statistical inputs.

The failure-mode evidence is consistent: the biggest practical risks are not advanced statistics errors first; they are validity failures (SRM, telemetry mismatch, contamination, optional stopping misuse). Strong quality gates and "inconclusive" outputs should be treated as first-class outcomes, not edge cases.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.
> Be specific: "Add X to methodology", "Replace Y tool with Z", "Add anti-pattern: ...", "Schema field X should be enum [...]".

- [x] Add a mandatory `statistical_regime` field with enum: `fixed_horizon_frequentist | sequential_frequentist | bayesian`; require matching stopping/interpretation policy. (See `Draft: Statistical Regime Selection and Stop Rules` + `Draft: Schema additions`)
- [x] Add a required `decision_rule` object that explicitly encodes primary-metric success, guardrail non-inferiority thresholds, and quality-gate pass criteria. (See `Draft: Decision Rule Contract and Readout States` + `Draft: Schema additions`)
- [x] Add required `validity_checks` fields in artifact schema: `srm_check`, `assignment_exposure_parity_check`, `contamination_check`, each with status and notes. (See `Draft: Quality-Gate Order` + `Draft: Schema additions`)
- [x] Expand sample-size planning from single MDE to scenario array (`conservative/base/aggressive`) and require runtime implications per scenario. (See `Draft: Power and MDE Scenario Planning` + `Draft: Schema additions`)
- [x] Add explicit multiplicity policy field (`none_with_justification | fdr | fwer | custom`) plus rationale text. (See `Draft: Multiplicity and Segment Discipline` + `Draft: Schema additions`)
- [x] Add instrumentation contract fields: randomization unit, exposure event name, identity keys, and warehouse join keys. (See `Draft: Instrumentation Contract and Tool Syntax`)
- [x] Add readout-state semantics beyond win/lose: `win | loss | inconclusive | invalid_due_to_quality`. (See `Draft: Decision Rule Contract and Readout States` + `Draft: Schema additions`)
- [x] Add anti-pattern guardrails section with hard failures (SRM fail, post-hoc metric switch, non-predeclared stop rule). (See `Draft: Anti-Pattern Guardrails`)
- [x] Add optional portfolio metadata fields: `replication_required`, `confirmation_window`, `confidence_tag`. (See `Draft: Portfolio Metadata and Follow-up Discipline`)

---

## Draft Content for SKILL.md

> Paste-ready content below is intentionally verbose and sectioned for direct insertion into `SKILL.md`. Each section is written in second person and maps to at least one recommendation item above.

### Draft: Quality-Gate Order

Before you interpret any outcome metric, you must run quality gates in a fixed order. You do not have statistical evidence until quality gates pass, because broken assignment, missing exposure logging, or contamination can produce confident-looking but invalid readouts.

You must execute gates in this sequence:
1. **Assignment integrity gate**: verify that randomization configuration, targeting, and traffic split match the pre-registered spec.
2. **SRM gate**: verify observed split vs expected split with a formal SRM test.
3. **Assignment-exposure parity gate**: verify that assigned users are actually exposed and exposure events are logged with correct variant identity.
4. **Contamination gate**: verify no major cross-variant contamination, spillover, or switching artifacts.
5. **Metric-join integrity gate**: verify primary/guardrail metrics can be joined with assignment and exposure keys for the full analysis window.

You must treat this as a hard dependency chain: if any blocking gate fails, you must output `invalid_due_to_quality` and stop interpretation until root cause is fixed. You must never override this gate with a significant p-value or high posterior probability. This rule is supported by current SRM and diagnostics guidance in Eppo, GrowthBook, Statsig, and Harness docs.

Source basis:
- https://docs.geteppo.com/statistics/sample-ratio-mismatch/
- https://docs.geteppo.com/experiment-analysis/diagnostics/
- https://docs.growthbook.io/app/experiment-results
- https://docs.statsig.com/experiments/monitoring/srm
- https://developer.harness.io/docs/feature-management-experimentation/experimentation/experiment-results/analyzing-experiment-results/sample-ratio-check

### Draft: Statistical Regime Selection and Stop Rules

You must declare exactly one statistical regime before launch: `fixed_horizon_frequentist`, `sequential_frequentist`, or `bayesian`. You must not mix regime semantics in one decision. If your readout uses frequentist p-values and Bayesian probabilities interchangeably, the decision is methodologically invalid.

Choose regime with this decision logic:
- Choose **fixed-horizon frequentist** when you can commit to one planned decision horizon and you need stable effect-size estimation across a metric set.
- Choose **sequential frequentist** when you need valid interim monitoring and potential early decisions under continuous looks.
- Choose **bayesian** when your team has explicit prior and risk-threshold policy and can govern posterior probability plus downside risk jointly.

You must pre-register stop rules aligned to the chosen regime:
- **Fixed-horizon**: no directional verdict before planned horizon.
- **Sequential frequentist**: allow interim verdicts only with sequentially adjusted inference.
- **Bayesian**: define probability threshold and downside-loss threshold together; probability-only criteria are insufficient.

If you switch regimes after seeing data, the result becomes exploratory and cannot be treated as confirmatory. This follows current methodology guidance across LaunchDarkly, Statsig, and Spotify risk-aware decision frameworks.

Source basis:
- https://docs.launchdarkly.com/guides/statistical-methodology/choosing
- https://docs.launchdarkly.com/guides/statistical-methodology/methodology-frequentist
- https://docs.launchdarkly.com/guides/statistical-methodology/methodology-bayesian
- https://docs.statsig.com/experiments-plus/sequential-testing/
- https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics
- https://arxiv.org/abs/2402.11609

### Draft: Power and MDE Scenario Planning

You must not plan sample size from a single MDE guess. You must create at least three pre-registered MDE scenarios (`conservative`, `base`, `aggressive`) and estimate runtime for each. The selected launch scenario must be justified by business materiality, not convenience.

For each MDE scenario, you must register:
- Expected absolute lift and relative lift.
- Baseline metric value and expected variance assumptions.
- Target power and alpha (or Bayesian equivalent risk threshold).
- Estimated sample size per variant.
- Estimated runtime under realistic traffic.
- Business interpretation of what that MDE means (for example, conversion points, revenue per user, retention points).

You must explicitly state tradeoff logic: smaller MDE requires materially more traffic/time; larger MDE speeds runtime but risks missing economically meaningful effects. If runtime assumptions are weak or traffic is unstable, you must mark the plan as uncertainty-sensitive and pre-register what triggers redesign.

You must treat underpowered outcomes as `inconclusive`, not as evidence of no effect. This is consistent with current platform documentation and recent interpretation guidance.

Source basis:
- https://docs.statsig.com/experiments/power-analysis
- https://docs.growthbook.io/statistics/power
- https://posthog.com/docs/experiments/sample-size-running-time
- https://docs.launchdarkly.com/guides/experimentation/sample-size-calc
- https://blog.analytics-toolkit.com/2024/comprehensive-guide-to-observed-power-post-hoc-power/

### Draft: Multiplicity and Segment Discipline

You must declare multiplicity policy before launch because metric families and segment slicing can inflate false discoveries. You cannot correct this retroactively with narrative judgment.

Use this policy:
- If you have one primary metric and no confirmatory segment family, you may use `none_with_justification` only when explicitly justified.
- If you have multiple decision-driving metrics or segment families, use `fdr` by default.
- Use `fwer` for high-risk decisions where any false positive is costly.
- Use `custom` only with explicit formula and reviewer sign-off.

You must pre-register confirmatory segments. Post-hoc segment wins are exploratory unless they are re-tested in a confirmatory follow-up design with correction applied.

You must separate metric roles:
- **Primary metric(s)**: defines success.
- **Guardrails**: safety and non-inferiority constraints.
- **Exploratory metrics**: hypothesis generation only.

Source basis:
- https://docs.geteppo.com/statistics/multiple-testing/
- https://docs.growthbook.io/statistics/multiple-corrections
- https://docs.statsig.com/stats-engine/methodologies/benjamini-hochberg-procedure
- https://developer.harness.io/docs/feature-management-experimentation/experimentation/key-concepts/multiple-comparison-correction
- https://support.optimizely.com/hc/en-us/articles/4410283967245-False-discovery-rate-control

### Draft: Decision Rule Contract and Readout States

You must pre-register one `decision_rule` object that binds statistical evidence, guardrails, and quality gates into one deterministic verdict. You must not allow free-text interpretation at readout time.

Decision contract requirements:
1. Define **primary success condition** (for example, effect threshold and confidence/probability rule).
2. Define **guardrail non-inferiority condition** (for example, maximum tolerated degradation and confidence rule).
3. Define **quality pass condition** (all blocking validity checks pass).
4. Define **materiality condition** (effect must exceed minimum business-relevant threshold, not only statistical detectability).
5. Define **readout state mapping** into exactly one state.

You must use these readout states:
- `win`: quality passes, guardrails pass, success + materiality criteria pass.
- `loss`: quality passes, but primary or guardrail indicates meaningful harm/failure.
- `inconclusive`: quality passes but uncertainty remains too high for decision.
- `invalid_due_to_quality`: one or more blocking quality checks fail.

You must include the `triggered_by` explanation in every readout state to show which rule decided the outcome. This allows auditability and reduces post-hoc interpretation drift.

Source basis:
- https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics
- https://arxiv.org/abs/2402.11609
- https://docs.geteppo.com/experiment-analysis/diagnostics/
- https://docs.statsig.com/experiments/interpreting-results/read-results

### Draft: Instrumentation Contract and Tool Syntax

You must pre-register instrumentation as an explicit contract. Assignment and exposure data are not interchangeable; both must be observable and joinable to outcome metrics.

Your instrumentation contract must include:
- Randomization unit (`user`, `device`, `account`, `cluster`, or `session`).
- Assignment event source and field names.
- Exposure event name and payload requirements.
- Identity keys (`subject_id`, optional `device_id`, optional `account_id`).
- Warehouse join keys and timestamp policy.
- De-duplication key policy (for replay safety).

Use real, verifiable syntax when integrating with external experimentation platforms.

**Flexus-native recording syntax**
```text
write_artifact(
  artifact_type="experiment_spec",
  path="/experiments/{experiment_id}/spec",
  data={...}
)
```

**Flexus policy context activation**
```text
flexus_policy_document(op="activate", args={"p": "/strategy/hypothesis-stack"})
flexus_policy_document(op="list", args={"p": "/experiments/"})
```

**Statsig evaluation + event syntax**
```bash
curl -X POST 'https://api.statsig.com/v1/check_gate' \
  -H 'statsig-api-key: client-xyz' \
  -H 'Content-Type: application/json' \
  -d '{ "gateName": "new_user_onboarding", "user": { "userID": "user-123" } }'
```

```bash
curl -X POST 'https://events.statsigapi.net/v1/log_event' \
  -H 'statsig-api-key: client-xyz' \
  -H 'Content-Type: application/json' \
  -d '{ "events": [ { "eventName": "add_to_cart", "user": { "userID": "user-123" }, "time": 1730000000000 } ] }'
```

**GrowthBook JavaScript tracking callback syntax**
```javascript
import { GrowthBook } from "@growthbook/growthbook";

const gb = new GrowthBook({
  apiHost: "https://cdn.growthbook.io",
  clientKey: "sdk-abc123",
  attributes: { id: "123", country: "US" },
  trackingCallback: (experiment, result) => {
    console.log("Experiment Viewed", { experimentId: experiment.key, variationId: result.key });
  },
});

await gb.init();
const enabled = gb.isOn("my-feature");
```

**LaunchDarkly evaluation and event syntax**
```javascript
const value = await client.boolVariation("example-flag-key", context, false);
client.track("example-event-key", context);
```

**Amplitude Experiment assignment + manual exposure syntax**
```bash
curl --request GET \
  --url 'https://api.lab.amplitude.com/v1/vardata?user_id=user123&flag_keys=my-flag' \
  --header 'Authorization: Api-Key YOUR_DEPLOYMENT_KEY'
```

```bash
curl --request POST \
  --url 'https://api2.amplitude.com/2/httpapi' \
  --header 'Content-Type: application/json' \
  --data '{"api_key":"YOUR_API_KEY","events":[{"event_type":"$exposure","user_id":"u1","event_properties":{"flag_key":"checkout_redesign","variant":"treatment"}}]}'
```

**PostHog flags and exposure event syntax**
```bash
curl -H "Content-Type: application/json" \
  -d '{"api_key":"<ph_project_token>","distinct_id":"user-123"}' \
  "https://us.i.posthog.com/flags?v=2"
```

```bash
curl -H "Content-Type: application/json" \
  -d '{"api_key":"<ph_project_token>","event":"$feature_flag_called","distinct_id":"user-123","properties":{"$feature_flag":"checkout_test","$feature_flag_response":"variant_a"}}' \
  "https://us.i.posthog.com/i/v0/e/"
```

**Optimizely JS decision + conversion syntax**
```javascript
const user = optimizely.createUserContext("user123", { logged_in: true });
const decision = user.decide("checkout_redesign");
user.trackEvent("purchase", {
  revenue: 10000,
  value: 100.0,
});
```

**Eppo Python assignment syntax**
```python
import eppo_client

client = eppo_client.get_instance()
variant = client.get_string_assignment(
    "flag-key-123",
    "user-123",
    {"country": "US"},
    "version-a",
)
```

You must declare rate-limit uncertainty when vendor docs do not publish hard numeric limits. In those cases, rely on `429` handling, retry headers, and conservative backoff rather than assumptions.

Source basis:
- https://docs.statsig.com/api-reference/feature-gates/check-feature-gates
- https://docs.statsig.com/api-reference/events/log-custom-events
- https://docs.statsig.com/api-reference/experiments/get-experiment
- https://docs.growthbook.io/api
- https://docs.growthbook.io/lib/js
- https://launchdarkly.com/docs/sdk/features/evaluating
- https://docs.launchdarkly.com/sdk/features/events
- https://launchdarkly.com/docs/api
- https://amplitude.com/docs/apis/experiment/experiment-evaluation-api
- https://amplitude.com/docs/apis/analytics/http-v2
- https://amplitude.com/docs/feature-experiment/track-exposure
- https://posthog.com/docs/api/flags
- https://posthog.com/docs/api/capture
- https://docs.developers.optimizely.com/feature-experimentation/docs/optimizelyusercontext-for-the-javascript-sdk-v6
- https://docs.developers.optimizely.com/feature-experimentation/docs/track-event-for-the-javascript-sdk
- https://docs.geteppo.com/sdks/server-sdks/python/assignments

### Draft: Anti-Pattern Guardrails

Use the following blocks as mandatory warnings in `SKILL.md`.

**Anti-pattern: SRM ignored**
- Signal: SRM diagnostic fails or split deviates materially from expected allocation.
- Consequence: treatment effect is not interpretable; ship/no-ship decision can reverse after fix.
- Mitigation: stop interpretation immediately, diagnose assignment/logging root cause, relaunch only after SRM passes.

**Anti-pattern: Assignment-exposure mismatch**
- Signal: users appear in assignment logs but not in exposure logs (or vice versa) beyond allowed threshold.
- Consequence: effect dilution and biased denominator; false negatives and false positives both possible.
- Mitigation: enforce assignment-exposure parity check, fix exposure emission point, rerun integrity test before readout.

**Anti-pattern: Optional stopping abuse**
- Signal: repeated peeking with fixed-horizon inference and early stop on first significant result.
- Consequence: inflated Type I error and unstable effect sizes.
- Mitigation: either commit to fixed horizon with no early verdicts, or switch to pre-registered sequential frequentist design before launch.

**Anti-pattern: Post-hoc metric switching**
- Signal: primary metric is changed after data observation or deck emphasizes non-preregistered winners.
- Consequence: selection bias and non-reproducible wins.
- Mitigation: freeze primary metrics pre-launch, label post-hoc findings as exploratory, require confirmatory rerun.

**Anti-pattern: Underpowered null overclaim**
- Signal: non-significant result with wide intervals and unmet sample/runtime assumptions.
- Consequence: meaningful effects incorrectly classified as absent.
- Mitigation: classify as `inconclusive`, extend runtime or redesign MDE/power assumptions.

**Anti-pattern: Interference and contamination ignored**
- Signal: treatment can plausibly affect control via network, marketplace, or ranking interactions.
- Consequence: naive A/B estimates are biased and may have wrong sign.
- Mitigation: screen for interference at design time, choose cluster/switchback/two-sided alternatives where needed.

**Anti-pattern: Novelty spike treated as durable**
- Signal: large early uplift that decays by days-since-exposure or calendar time.
- Consequence: short-term adoption effect misread as durable product improvement.
- Mitigation: enforce minimum runtime over at least one business cycle and inspect temporal stability before decision.

**Anti-pattern: Allocation-history blindness**
- Signal: traffic ramps, rollbacks, or reallocation changes occur during run but analysis treats all periods as exchangeable.
- Consequence: pooled estimate is confounded by rollout epoch effects.
- Mitigation: pre-register ramp policy, stratify analysis by epoch after major allocation changes, rerun if continuity breaks.

Source basis:
- https://docs.geteppo.com/statistics/sample-ratio-mismatch/
- https://docs.geteppo.com/experiment-analysis/diagnostics/
- https://docs.statsig.com/feature-flags/multiple-rollout-stages
- https://docs.statsig.com/experiments-plus/sequential-testing/
- https://www.statsig.com/blog/novelty-effects
- https://docs.growthbook.io/using/experimentation-problems
- https://www.linkedin.com/blog/engineering/ab-testing-experimentation/a-b-testing-variant-assignment
- https://business.columbia.edu/sites/default/files-efs/citation_file_upload/holtz-et-al-2024-reducing-interference-bias-in-online-marketplace-experiments-using-cluster-randomization-evidence-from%20(2).pdf

### Draft: Schema additions

```json
{
  "experiment_spec": {
    "type": "object",
    "description": "Pre-registered contract for one experiment design. This schema encodes statistical regime, quality gates, instrumentation contract, and deterministic decision logic.",
    "required": [
      "experiment_id",
      "hypothesis_ref",
      "experiment_type",
      "control",
      "variants",
      "primary_metric",
      "guardrail_metrics",
      "statistical_regime",
      "sample_size_per_variant",
      "mde_scenarios",
      "significance_threshold",
      "power",
      "decision_rule",
      "multiplicity_policy",
      "validity_checks",
      "instrumentation_contract",
      "readout_semantics",
      "launch_date",
      "decision_date"
    ],
    "additionalProperties": false,
    "properties": {
      "experiment_id": {
        "type": "string",
        "description": "Unique experiment identifier used in storage paths and dashboards."
      },
      "hypothesis_ref": {
        "type": "string",
        "description": "Pointer to the hypothesis artifact that this experiment operationalizes."
      },
      "experiment_type": {
        "type": "string",
        "description": "Execution topology for assignment and analysis planning.",
        "enum": ["ab_test", "holdout", "pre_post", "bayesian"]
      },
      "control": {
        "type": "object",
        "description": "Current baseline experience and baseline assumptions.",
        "required": ["description", "current_baseline_rate"],
        "additionalProperties": false,
        "properties": {
          "description": {
            "type": "string",
            "description": "Human-readable description of the control experience."
          },
          "current_baseline_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Expected baseline value for the primary metric before treatment."
          }
        }
      },
      "variants": {
        "type": "array",
        "description": "Treatment variants with explicit change documentation and traffic allocation.",
        "minItems": 1,
        "items": {
          "type": "object",
          "required": ["variant_id", "description", "change_description", "traffic_split"],
          "additionalProperties": false,
          "properties": {
            "variant_id": {
              "type": "string",
              "description": "Stable variant key used in assignment and readout."
            },
            "description": {
              "type": "string",
              "description": "Short summary of the variant."
            },
            "change_description": {
              "type": "string",
              "description": "Exact change relative to control; must isolate causal change intent."
            },
            "traffic_split": {
              "type": "number",
              "minimum": 0,
              "maximum": 1,
              "description": "Planned allocation share for this variant."
            }
          }
        }
      },
      "primary_metric": {
        "type": "string",
        "description": "Single decision-driving metric identifier."
      },
      "guardrail_metrics": {
        "type": "array",
        "description": "Safety/non-inferiority metrics that can block launch despite primary gain.",
        "items": {
          "type": "string"
        }
      },
      "statistical_regime": {
        "type": "string",
        "description": "One inference regime selected before launch. Regime mixing is not allowed in confirmatory decisioning.",
        "enum": [
          "fixed_horizon_frequentist",
          "sequential_frequentist",
          "bayesian"
        ]
      },
      "sample_size_per_variant": {
        "type": "integer",
        "minimum": 1,
        "description": "Target sample per variant for the selected base planning scenario."
      },
      "minimum_detectable_effect": {
        "type": "number",
        "description": "Legacy single-MDE field for backward compatibility. Prefer mde_scenarios for planning."
      },
      "mde_scenarios": {
        "type": "array",
        "description": "Scenario-based planning for runtime and detectability tradeoffs.",
        "minItems": 3,
        "items": {
          "type": "object",
          "required": [
            "scenario_id",
            "absolute_mde",
            "relative_mde",
            "estimated_sample_per_variant",
            "estimated_runtime_days",
            "business_materiality_note"
          ],
          "additionalProperties": false,
          "properties": {
            "scenario_id": {
              "type": "string",
              "enum": ["conservative", "base", "aggressive"],
              "description": "Planning profile label."
            },
            "absolute_mde": {
              "type": "number",
              "description": "Absolute effect-size threshold in metric units."
            },
            "relative_mde": {
              "type": "number",
              "description": "Relative effect-size threshold as fraction (for example 0.03 for 3%)."
            },
            "estimated_sample_per_variant": {
              "type": "integer",
              "minimum": 1,
              "description": "Projected sample needed per variant for this scenario."
            },
            "estimated_runtime_days": {
              "type": "number",
              "minimum": 0,
              "description": "Projected runtime under expected traffic and eligibility."
            },
            "business_materiality_note": {
              "type": "string",
              "description": "Business interpretation of why this MDE is decision-relevant."
            }
          }
        }
      },
      "significance_threshold": {
        "type": "number",
        "description": "Alpha-like threshold used in frequentist planning, if applicable."
      },
      "power": {
        "type": "number",
        "description": "Target statistical power for frequentist planning."
      },
      "decision_rule": {
        "type": "object",
        "description": "Deterministic launch decision logic with explicit success, guardrail, and quality pass criteria.",
        "required": [
          "primary_success_rule",
          "guardrail_rules",
          "quality_gate_policy",
          "materiality_rule",
          "state_mapping"
        ],
        "additionalProperties": false,
        "properties": {
          "primary_success_rule": {
            "type": "string",
            "description": "Machine- and human-readable statement for primary success logic."
          },
          "guardrail_rules": {
            "type": "array",
            "description": "Blocking and warning rules for each guardrail metric.",
            "items": {
              "type": "object",
              "required": ["metric", "rule", "severity"],
              "additionalProperties": false,
              "properties": {
                "metric": {
                  "type": "string",
                  "description": "Guardrail metric identifier."
                },
                "rule": {
                  "type": "string",
                  "description": "Non-inferiority or degradation constraint."
                },
                "severity": {
                  "type": "string",
                  "enum": ["blocking", "warning"],
                  "description": "Whether this guardrail blocks launch."
                }
              }
            }
          },
          "quality_gate_policy": {
            "type": "string",
            "description": "Rule text specifying that all blocking validity checks must pass before interpretation."
          },
          "materiality_rule": {
            "type": "string",
            "description": "Business threshold that prevents shipping statistically tiny but irrelevant gains."
          },
          "state_mapping": {
            "type": "object",
            "required": ["win", "loss", "inconclusive", "invalid_due_to_quality"],
            "additionalProperties": false,
            "properties": {
              "win": {
                "type": "string",
                "description": "Condition expression that maps to win."
              },
              "loss": {
                "type": "string",
                "description": "Condition expression that maps to loss."
              },
              "inconclusive": {
                "type": "string",
                "description": "Condition expression that maps to inconclusive."
              },
              "invalid_due_to_quality": {
                "type": "string",
                "description": "Condition expression that maps to invalid due to failed quality gates."
              }
            }
          }
        }
      },
      "multiplicity_policy": {
        "type": "object",
        "description": "Multiple testing policy used for confirmatory claims.",
        "required": ["mode", "rationale"],
        "additionalProperties": false,
        "properties": {
          "mode": {
            "type": "string",
            "enum": ["none_with_justification", "fdr", "fwer", "custom"],
            "description": "Correction mode for confirmatory metric and segment families."
          },
          "rationale": {
            "type": "string",
            "description": "Reason this correction mode matches experiment risk profile."
          },
          "custom_definition": {
            "type": "string",
            "description": "Required when mode is custom; include exact formula and scope."
          }
        }
      },
      "validity_checks": {
        "type": "object",
        "description": "Quality gates that determine whether readout is valid for interpretation.",
        "required": [
          "srm_check",
          "assignment_exposure_parity_check",
          "contamination_check"
        ],
        "additionalProperties": false,
        "properties": {
          "srm_check": {
            "type": "object",
            "required": ["status", "threshold", "notes"],
            "additionalProperties": false,
            "properties": {
              "status": {
                "type": "string",
                "enum": ["pass", "warn", "fail"],
                "description": "SRM gate outcome."
              },
              "threshold": {
                "type": "string",
                "description": "Configured SRM decision threshold (for example p<0.001)."
              },
              "notes": {
                "type": "string",
                "description": "Root-cause notes or validation comments."
              }
            }
          },
          "assignment_exposure_parity_check": {
            "type": "object",
            "required": ["status", "threshold", "notes"],
            "additionalProperties": false,
            "properties": {
              "status": {
                "type": "string",
                "enum": ["pass", "warn", "fail"],
                "description": "Parity gate outcome for assignment and exposure records."
              },
              "threshold": {
                "type": "string",
                "description": "Configured mismatch tolerance and comparison window."
              },
              "notes": {
                "type": "string",
                "description": "Investigation details if mismatch appears."
              }
            }
          },
          "contamination_check": {
            "type": "object",
            "required": ["status", "threshold", "notes"],
            "additionalProperties": false,
            "properties": {
              "status": {
                "type": "string",
                "enum": ["pass", "warn", "fail"],
                "description": "Contamination/interference gate outcome."
              },
              "threshold": {
                "type": "string",
                "description": "Configured contamination tolerance."
              },
              "notes": {
                "type": "string",
                "description": "Diagnostics, assumptions, and remediation notes."
              }
            }
          }
        }
      },
      "instrumentation_contract": {
        "type": "object",
        "description": "Pre-registered telemetry contract for assignment, exposure, and outcome joins.",
        "required": [
          "randomization_unit",
          "assignment_event_name",
          "exposure_event_name",
          "identity_keys",
          "warehouse_join_keys"
        ],
        "additionalProperties": false,
        "properties": {
          "randomization_unit": {
            "type": "string",
            "enum": ["user", "device", "account", "cluster", "session"],
            "description": "Unit used for randomization and analysis."
          },
          "assignment_event_name": {
            "type": "string",
            "description": "Event or log stream name that records variant assignment."
          },
          "exposure_event_name": {
            "type": "string",
            "description": "Event emitted when user is truly exposed to variant logic."
          },
          "identity_keys": {
            "type": "array",
            "description": "Ordered identifiers used for event joins (for example subject_id, account_id, device_id).",
            "minItems": 1,
            "items": {
              "type": "string"
            }
          },
          "warehouse_join_keys": {
            "type": "array",
            "description": "Warehouse fields used to join assignment/exposure/outcome records.",
            "minItems": 1,
            "items": {
              "type": "string"
            }
          },
          "dedupe_key_field": {
            "type": "string",
            "description": "Event-level unique key used to remove duplicates in replay or retry scenarios."
          },
          "api_constraints_note": {
            "type": "string",
            "description": "Rate-limit and endpoint caveats, including unknown numeric limits."
          }
        }
      },
      "readout_semantics": {
        "type": "object",
        "description": "Allowed readout states and blocking behavior.",
        "required": ["allowed_states", "blocking_states"],
        "additionalProperties": false,
        "properties": {
          "allowed_states": {
            "type": "array",
            "description": "Canonical state set used in all experiment readouts.",
            "items": {
              "type": "string",
              "enum": ["win", "loss", "inconclusive", "invalid_due_to_quality"]
            }
          },
          "blocking_states": {
            "type": "array",
            "description": "States that block ship decisions and require remediation.",
            "items": {
              "type": "string",
              "enum": ["loss", "invalid_due_to_quality"]
            }
          },
          "inconclusive_policy": {
            "type": "string",
            "description": "Follow-up action required when state is inconclusive."
          }
        }
      },
      "portfolio_metadata": {
        "type": "object",
        "description": "Optional program-level governance fields for replication and confidence tracking.",
        "required": ["replication_required", "confirmation_window", "confidence_tag"],
        "additionalProperties": false,
        "properties": {
          "replication_required": {
            "type": "boolean",
            "description": "Whether a follow-up confirmatory run is required before broad rollout."
          },
          "confirmation_window": {
            "type": "string",
            "description": "Time window for confirmation or post-launch holdout monitoring."
          },
          "confidence_tag": {
            "type": "string",
            "enum": ["high", "medium", "low"],
            "description": "Human-readable confidence label based on quality and uncertainty profile."
          }
        }
      },
      "launch_date": {
        "type": "string",
        "description": "Planned launch date in ISO-8601 format."
      },
      "decision_date": {
        "type": "string",
        "description": "Planned first confirmatory decision date in ISO-8601 format."
      },
      "instrumentation_plan": {
        "type": "array",
        "description": "Legacy textual checklist retained for backward compatibility.",
        "items": {
          "type": "string"
        }
      }
    }
  }
}
```

### Draft: Portfolio Metadata and Follow-up Discipline

You should track portfolio-level metadata even for single experiments because local significance does not guarantee durable portfolio value. You should require replication or holdout confirmation for high-impact launches, especially when novelty effects, interference risk, or regime complexity is high.

You should set:
- `replication_required = true` when decision relies on borderline evidence, unstable temporal profile, or high business risk.
- `confirmation_window` to one full business cycle at minimum for behavior-sensitive outcomes.
- `confidence_tag` from a documented rule combining quality-gate outcomes and uncertainty profile.

You should treat this metadata as an execution control, not a retrospective annotation. If the experiment is marked high impact and confidence is not high, do not allow unconditional full rollout in one step.

Source basis:
- https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics
- https://www.geteppo.com/blog/rethinking-measuring-experimental-impact
- https://www.nature.com/articles/s41562-024-02062-9

---

## Gaps & Uncertainties

- Several vendor docs are "living documentation" without clear publication date; these were marked evergreen where date precision is missing.
- Numeric API rate limits are not publicly disclosed for some platforms (for example, some LaunchDarkly and Split/Harness limits). Specs should include conservative pacing when limits are unknown.
- Cross-platform methodology labels are not perfectly comparable (for example, "Bayesian" implementations differ in priors and reporting semantics), so one-to-one policy mapping remains approximate.
- Interference-aware design guidance is strong in recent literature, but production-ready decision thresholds are still context-dependent and not standardized across vendors.
- Portfolio-level optimization methods are emerging quickly (2024-2026); some evidence is still preprint-stage and should be treated as promising rather than settled default practice.
