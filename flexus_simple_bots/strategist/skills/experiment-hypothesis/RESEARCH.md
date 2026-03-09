# Research: experiment-hypothesis

**Skill path:** `strategist/skills/experiment-hypothesis/`
**Bot:** strategist (researcher | strategist | executor)
**Research date:** 2026-03-04
**Status:** complete

---

## Context

The `experiment-hypothesis` skill converts strategic assumptions into falsifiable hypotheses with explicit success and rejection criteria, then records them as a prioritized hypothesis stack. In practice, this skill sits at the front of the experimentation lifecycle: it determines whether teams test fatal assumptions first, choose measurable outcomes up front, and avoid post-hoc storytelling.

Research context expansion: in 2025-2026, mature experimentation programs treat hypothesis writing as part of an analysis protocol, not a standalone sentence template. Teams increasingly bind each hypothesis to an analysis plan (error control, minimum runtime/sample requirements, multiple-testing policy), guardrail metrics, and quality gates such as SRM checks before any ship/no-ship decision. This moves the skill from "idea formatting" to "decision governance."

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

- No generic filler ("it is important to...", "best practices suggest...") without concrete backing
- No invented tool names, method IDs, or API endpoints — only verified real ones
- Contradictions between sources are explicitly noted, not silently resolved
- Volume: findings section should be 800–4000 words (too short = shallow, too long = unsynthesized)

Verification notes:
- Findings are grounded in vendor docs, standards-style documentation, or peer-reviewed/archival sources.
- Contradictions are called out in Angle 1/2/3 and again synthesized in `Synthesis`.
- Findings volume is within target range.

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

Practitioner methodology has shifted from "write a hypothesis sentence" to "define a full decision protocol before data arrives." Contemporary guidance in Eppo, Statsig, GrowthBook, and Amplitude converges on a practical sequence:

1) define the causal claim and falsification condition,  
2) pre-define primary metric plus guardrails,  
3) choose analysis mode (fixed, sequential, Bayesian),  
4) set confidence/error control and minimum run requirements,  
5) decide rollout/rollback rules before exposure.

Two concrete operational upgrades stand out in 2025-2026:

- **Analysis-plan first governance:** Eppo formalizes experiment-level analysis plans (confidence method/level, multiple testing correction, minimum requirements, precision targets). This means hypotheses are evaluated under declared statistical assumptions instead of analyst discretion after launch.
- **Always-valid monitoring with explicit trade-offs:** sequential testing is now common in production tooling, but teams treat it as an operational choice rather than automatic superiority. Sequential monitoring helps safe peeking and earlier interventions, while fixed-horizon designs can retain stronger power under some constraints.

Methodology details that repeatedly appear in documentation:

- **Single decision owner metric + guardrails:** one primary metric determines hypothesis verdict; guardrails enforce do-no-harm constraints (latency, error rates, core trust metrics) with explicit thresholds.
- **MDE/power planned pre-launch:** teams estimate required runtime using realistic traffic population and expected effect ranges, then adjust design (traffic split, number of variants, metric scope) before starting.
- **Variance reduction and segmentation when signal is weak:** CUPED/CURE/stratification are used to improve sensitivity for noisy or low-volume contexts.
- **Protocol defaults at organization level:** mature teams define global defaults and allow local overrides only with explicit rationale, reducing "local p-hacking by configuration."

Contradiction explicitly observed:
- **"Fast decisions" vs "high precision":** sources agree sequential methods improve operational flexibility, but they also document precision/power trade-offs. Teams need separate decision states: early safety intervention vs final effect sizing confidence.

**Sources:**
- https://docs.geteppo.com/experiment-analysis/configuration/analysis-plans/
- https://docs.geteppo.com/experiment-analysis/configuration/protocols/
- https://docs.statsig.com/stats-engine
- https://docs.statsig.com/experiments-plus/sequential-testing
- https://docs.growthbook.io/statistics/sequential
- https://docs.growthbook.io/statistics/power
- https://docs.growthbook.io/statistics/cuped
- https://docs.statsig.com/experiments-plus/cure
- https://docs.statsig.com/experiments-plus/stratified-sampling
- https://help.amplitude.com/hc/en-us/articles/4403176829709-How-Amplitude-Experiment-uses-sequential-testing-for-statistical-inference
- https://support.optimizely.com/hc/en-us/articles/4410282998541-Design-an-effective-hypothesis *(evergreen)*
- https://engineering.atspotify.com/2023/03/choosing-sequential-testing-framework-comparisons-and-discussions/ *(evergreen)*

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

The tool ecosystem for hypothesis management is split across two layers:

- **Hypothesis repository/work management layer:** Jira Product Discovery, Notion, Airtable.
- **Experiment delivery + measurement layer:** GrowthBook, Amplitude Experiment, LaunchDarkly, Statsig, PostHog.

Concrete options and verified API characteristics:

1. **Jira Product Discovery + Jira Cloud API**  
   JPD ideas can be managed through Jira issue APIs (`/rest/api/3/issue*`) and connected to delivery tickets. This supports hypothesis backlog workflow continuity from discovery to execution.  
   Constraint: dynamic JPD formula fields are not uniformly exposed through standard issue payloads.

2. **Notion API**  
   Useful for structured hypothesis capture/evidence references (`POST /v1/pages`, data source query API).  
   Constraints: integration permissions and request limits (~3 req/s baseline, payload/property limits) require retry-aware ingestion.

3. **Airtable Web API**  
   Good structured schema and pagination model for hypothesis stacks.  
   Constraints: hard per-base rate limits (5 req/s), token-level limits, plan-dependent monthly API caps.

4. **GrowthBook**  
   Provides experiment/feature APIs (`/api/v1/experiments`, `/api/v1/features`), SDK delivery endpoint, and documented power/sequential tooling.  
   Constraint: management API rate limits; SDK endpoints are intentionally scoped for runtime evaluation.

5. **Amplitude Experiment**  
   Management API for flags/experiments/deployments plus evaluation endpoints; explicit per-project limits (100 req/s, 100k/day) are documented.

6. **LaunchDarkly**  
   Strong flag+experimentation integration with documented Experiments API and OpenAPI spec.  
   Constraint: some experiments API capabilities are beta-gated via API version header.

7. **Statsig**  
   Integrates feature gates, experimentation, and events (`POST /v1/log_event`), with explicit key scopes and plan-based usage constraints.

8. **PostHog**  
   Unifies flags and experiments via API endpoints and event capture model, good for full-loop product analytics.

De-facto standards observed across tools:

- **Feature flags as experiment delivery primitive** (not separate systems).
- **Control-plane vs runtime split:** admin APIs for setup and distinct SDK/runtime evaluation endpoints with different keys.
- **Evidence via exposure/event streams:** conclusions rely on assignment + behavior events, not UI summary metrics alone.

Contradictions explicitly observed:
- **Marketing "free/unlimited" language vs operational quotas:** several tools advertise generous plans but still enforce strict request/event/MAU constraints.
- **Availability vs maturity mismatch:** experimentation APIs may exist but remain beta-scoped or capability-limited by plan.

**Sources:**
- Atlassian/JPD + Jira API:
  - https://www.atlassian.com/software/jira/product-discovery/pricing
  - https://www.atlassian.com/software/jira/product-discovery/guides/integrations/overview
  - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/
- Notion:
  - https://developers.notion.com/reference/post-page
  - https://developers.notion.com/reference/query-a-data-source
  - https://developers.notion.com/reference/request-limits
  - https://www.notion.com/pricing
- Airtable:
  - https://support.airtable.com/docs/getting-started-with-airtables-web-api
  - https://support.airtable.com/docs/managing-api-call-limits-in-airtable
  - https://support.airtable.com/docs/airtable-plans
- GrowthBook:
  - https://docs.growthbook.io/api/
  - https://docs.growthbook.io/app/api
  - https://docs.growthbook.io/feature-flag-experiments
  - https://www.growthbook.io/pricing
- Amplitude:
  - https://amplitude.com/docs/apis/experiment/experiment-management-api
  - https://amplitude.com/docs/apis/experiment/experiment-management-api-flags
  - https://amplitude.com/docs/apis/experiment/experiment-evaluation-api
  - https://amplitude.com/pricing
- LaunchDarkly:
  - https://launchdarkly.com/docs/api
  - https://launchdarkly.com/docs/api/experiments
  - https://app.launchdarkly.com/api/v2/openapi.json
  - https://launchdarkly.com/docs/home/account/plans
  - https://launchdarkly.com/pricing/archive-apr2025
- Statsig:
  - https://docs.statsig.com/api-reference/events/log-custom-events
  - https://docs.statsig.com/sdk-keys/api-keys
  - https://docs.statsig.com/guides/feature-flags
  - https://www.statsig.com/pricing
- PostHog:
  - https://posthog.com/docs/api/flags
  - https://posthog.com/docs/api/experiments
  - https://posthog.com/docs/feature-flags/cutting-costs

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

Signal-quality practice in modern experimentation has three layers: design thresholds, live quality diagnostics, and decision interpretation.

**Design thresholds before launch**
- A frequent default remains `alpha=0.05`, `power=0.8`, with MDE used as a design dial for runtime/sample planning rather than a post-hoc pass/fail threshold.
- Multiple comparisons require explicit error control (often Benjamini-Hochberg FDR in multi-metric/multi-variant scorecards), especially when teams scale concurrent hypotheses.

**Live diagnostics during run**
- Sequential frameworks are widely used to monitor safely during runtime, but peeking without valid sequential handling is still a known false-positive amplifier.
- SRM (sample ratio mismatch) is treated as a hard trust alarm. Example production guidance uses strict SRM alpha levels (e.g., 0.001 in Eppo diagnostics), because assignment imbalance often indicates randomization/logging defects.

**Decision interpretation**
- Teams increasingly avoid binary "significant/non-significant only" decisions. Better practice combines effect size, confidence/credible intervals, guardrail non-inferiority checks, and diagnostic health.
- For portfolios with many hypotheses over time, online FDR approaches (e.g., LOND/LORD/SAFFRON/ADDIS families) are relevant in principle, though product implementation details vary by platform.

Common misinterpretations and corrections:

1. **Misread MDE as an observed-effect cutoff.**  
   Correction: MDE is pre-data planning sensitivity; observed effects below MDE can still be informative depending on uncertainty and practical impact.

2. **Treat non-significance as proof of no effect.**  
   Correction: it often means insufficient information under current design; confidence should degrade to uncertainty, not absolute rejection.

3. **Read raw p-values under multiplicity as decision-ready.**  
   Correction: apply and document family definition and correction method.

Important practical benchmark from risk-aware decision research:
- As guardrail count rises, joint power to "pass all checks" can collapse without explicit non-inferiority design and realistic margins; this affects hypothesis prioritization economics.

**Sources:**
- https://docs.statsig.com/experiments/power-analysis
- https://docs.growthbook.io/statistics/power
- https://amplitude.com/docs/feature-experiment/experiment-theory/experiment-set-mde
- https://blog.analytics-toolkit.com/2024/what-if-the-observed-effect-is-smaller-than-the-mde/
- https://docs.statsig.com/experiments/statistical-methods/methodologies/benjamini-hochberg-procedure
- https://www.statsig.com/blog/controlling-type-i-errors-bonferroni-benjamini-hochberg
- https://support.optimizely.com/hc/en-us/articles/4410283967245-False-discovery-rate-control
- https://docs.statsig.com/experiments/advanced-setup/sequential-testing
- https://amplitude.com/docs/feature-experiment/under-the-hood/experiment-sequential-testing
- https://docs.geteppo.com/statistics/sample-ratio-mismatch
- https://amplitude.com/docs/feature-experiment/troubleshooting/sample-ratio-mismatch
- https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics
- https://arxiv.org/abs/2402.11609
- https://confidence.spotify.com/blog/better-decisions-with-guardrails
- https://www.bioconductor.org/packages/release/bioc/vignettes/onlineFDR/inst/doc/onlineFDR.html
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12624209/

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

Failure patterns cluster into four classes: hypothesis integrity failures, statistical governance failures, data-quality failures, and portfolio-learning failures.

1. **HARKing (hypothesis after results known)**  
   - Bad output: hypothesis rewritten to fit observed uplift direction.  
   - Good output: pre-registered confirmatory claim; exploratory findings labeled separately.

2. **Retroactive or non-transparent pre-registration**  
   - Bad output: registry/protocol changes make a trial appear prospectively registered after the fact.  
   - Good output: immutable timestamps + change log and explicit disclosure of post-start edits.

3. **p-hacking / multiplicity abuse**  
   - Bad output: many cuts tested, only winning slice reported.  
   - Good output: pre-analysis family definition + full correction + full tested-comparison disclosure.

4. **Optional stopping with fixed-horizon inference**  
   - Bad output: repeated dashboard peeking until significance appears.  
   - Good output: sequentially valid design and pre-defined stop boundaries.

5. **SRM ignored at decision time**  
   - Bad output: ship decision despite severe assignment mismatch.  
   - Good output: hard gate that blocks interpretation until assignment/logging root cause is closed.

6. **Survivorship/attrition bias in outcome interpretation**  
   - Bad output: only retained users analyzed without attrition diagnostics.  
   - Good output: ITT-aligned framing, attrition reasons by arm, sensitivity analyses.

7. **Metric gaming / Goodhart failure**  
   - Bad output: proxy KPI improves while true objective or quality degrades.  
   - Good output: constrained optimization with guardrails and periodic direct-outcome validation.

8. **Interference/spillover ignored in networked systems**  
   - Bad output: standard A/B interpretation under violated independence assumptions.  
   - Good output: cluster/network-aware randomization and estimators.

9. **Selective publication ("file drawer")**  
   - Bad output: only positive experiments become visible in portfolio memory.  
   - Good output: mandatory result publication SLA including negative/inconclusive outcomes.

Case-style evidence in source set includes: retroactive-prospective registration analysis, SRM diagnosis literature, and publication-completeness audits.

**Sources:**
- https://pmc.ncbi.nlm.nih.gov/articles/PMC11335400/
- https://doi.org/10.1098/rsos.231744
- https://trialsjournal.biomedcentral.com/articles/10.1186/s13063-024-08029-5
- https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0303262
- https://www.nature.com/articles/s41562-025-02313-3
- https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0307999
- https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.3002345
- https://arxiv.org/abs/1512.04922 *(evergreen)*
- https://www.lukasvermeer.nl/srm/docs/faq/
- https://www.kdd.org/kdd2019/accepted-papers/view/diagnosing-sample-ratio-mismatch-in-online-controlled-experiments-a-taxonom *(evergreen)*
- https://ideas.repec.org/a/eee/econom/v241y2024i2s0304407624000836.html
- https://catalogofbias.org/biases/attrition-bias/ *(evergreen)*
- https://proceedings.iclr.cc/paper_files/paper/2024/file/6ad68a54eaa8f9bf6ac698b02ec05048-Paper-Conference.pdf
- https://openai.com/index/measuring-goodharts-law/ *(evergreen)*
- https://jmlr.org/papers/v25/22-0192.html
- https://arxiv.org/abs/2404.10547
- https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2813519

---

## Synthesis

The strongest cross-source signal is that "good hypothesis writing" in 2025-2026 is inseparable from experiment governance. The same hypothesis statement can produce opposite product decisions depending on whether teams pre-commit analysis settings, error control, guardrails, and minimum run criteria. In other words, hypothesis quality now includes operational and statistical design quality, not only linguistic clarity.

A second pattern is architectural: tooling ecosystems have standardized around a control-plane/runtime split. Hypothesis objects typically live in planning systems (Jira/Notion/Airtable), while validation evidence is generated in flag/experiment platforms (GrowthBook/Statsig/Amplitude/LaunchDarkly/PostHog). This reinforces the need for a schema that links hypothesis IDs to experiment IDs, assignment events, and evidence references across systems.

Two contradictions matter operationally. First, sequential testing is promoted for speed and safe monitoring, but several sources document precision/power trade-offs relative to fixed-horizon assumptions. Second, vendors often market generous/free plans while imposing strict quotas or plan gates that can silently shape workflow design. Skill guidance should therefore force explicit method and capacity assumptions up front.

The most actionable implication for this skill: confidence is not a static label (`low|medium|high`) but an update process gated by diagnostics (SRM/data quality), multiplicity policy, and guardrail status. A hypothesis stack that does not encode these fields will drift toward subjective confidence inflation and inconsistent prioritization.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.
> Be specific: "Add X to methodology", "Replace Y tool with Z", "Add anti-pattern: ...", "Schema field X should be enum [...]".

- [x] Add a mandatory **analysis_plan** object per hypothesis: `method` (`fixed_horizon|sequential|bayesian`), `confidence_level`, `multiple_testing_method` (`none|bonferroni|benjamini_hochberg|other`), `minimum_runtime_days`, `minimum_sample_per_variant`.
- [x] Add explicit **metric roles** to schema: `primary_metric`, `guardrail_metrics[]`, `secondary_metrics[]`, each with pre-declared decision logic (including guardrail non-inferiority margin where applicable).
- [x] Extend confidence handling from static enum to **confidence_update_log[]** with evidence-based transitions (timestamp, evidence_ref, rationale, from_confidence, to_confidence).
- [x] Add a **quality_gates** block to each hypothesis: `srm_check` (`pass|fail|not_applicable`), `instrumentation_status`, `assignment_logging_status`; block `validated` status when critical gate fails.
- [x] Add a **power_design** block: `alpha`, `target_power`, `mde`, `estimated_runtime_days`, `population_assumption_ref`; require this before status can move to `in_progress`.
- [x] Add anti-pattern guardrails in methodology text: forbid HARKing, post-hoc metric switching, and ship decisions under unresolved SRM.
- [x] Add cross-tool linkage fields: `experiment_platform`, `experiment_id`, `feature_flag_key`, `assignment_event_ref`, `result_dashboard_ref` to preserve evidence lineage across planning and execution systems.

---

## Draft Content for SKILL.md

> The blocks below are written as paste-ready material for `SKILL.md`. They are intentionally verbose so the editor can cut down if needed without inventing missing logic.

### Draft: Methodology - Hypothesis Contract and Decision Governance

You convert assumptions into decision contracts, not sentence templates. A valid hypothesis is only accepted when you can prove three things before any experiment starts: (1) what would count as confirmation, (2) what would count as rejection, and (3) what quality failures would block interpretation even if metrics look positive.

You must always write hypotheses in causal and falsifiable form:

1. **Causal claim:** what change causes what behavior shift.
2. **Mechanism clause:** why you expect that behavior shift.
3. **Test design:** how assignment and measurement happen.
4. **Success criterion:** exact threshold and time window for confirmation.
5. **Rejection criterion:** exact condition that falsifies the claim.
6. **Decision owner:** who can call `validated`, `rejected`, or `inconclusive`.

Use this minimum structure:

```text
We believe that [specific causal claim].
Because [behavioral/product mechanism].
We will test this with [experiment design and assignment unit].
We will validate if [primary metric threshold and direction] while [all guardrails remain within limits] by [decision date].
We will reject if [falsification condition].
If quality gates fail (SRM/instrumentation/assignment integrity), verdict is blocked regardless of metric lift.
```

Before you mark any hypothesis as `in_progress`, complete this pre-analysis protocol:

1. **Choose analysis method explicitly.**  
   You must set `fixed_horizon`, `sequential`, or `bayesian` before launch. If you cannot name the analysis mode, you are not ready to run the test.
2. **Set multiple-testing policy explicitly.**  
   You must declare whether correction is `none`, `bonferroni`, or `benjamini_hochberg`, and define correction scope (for example, by primary metrics only, or by all decision-driving metrics).
3. **Set minimum runtime and sample floors.**  
   You must define `minimum_runtime_days` and `minimum_sample_per_variant` to prevent "stop on first green dashboard" behavior.
4. **Declare metric roles before launch.**  
   You must define exactly one primary metric and explicit guardrails. Secondary metrics can inform learning but cannot overrule a failing guardrail.
5. **Declare power assumptions before launch.**  
   You must set `alpha`, `target_power`, `mde`, and a population assumption reference so inconclusive results can be interpreted honestly.
6. **Declare quality gates before launch.**  
   You must define how SRM, instrumentation status, and assignment logging status are checked and how each gate can block decisioning.

Decision state machine you must follow:

- If any critical quality gate fails (`srm_check=fail` or instrumentation/assignment logging is `degraded`), set status to `blocked` and do not call the hypothesis validated or rejected.
- If quality gates pass and success criteria are met without guardrail breach, set status to `validated`.
- If quality gates pass and falsification criteria are met, set status to `rejected`.
- If quality gates pass but neither success nor falsification criteria are met by planned horizon, set status to `inconclusive`.
- If new exploratory signal appears that was not pre-registered, log it as exploratory only and create a new confirmatory hypothesis instead of rewriting the current one.

Research basis for this draft:
- https://docs.geteppo.com/experiment-analysis/configuration/analysis-plans/
- https://docs.geteppo.com/experiment-analysis/configuration/protocols/
- https://docs.statsig.com/exp-templates/decision-framework
- https://docs.growthbook.io/app/experiment-decisions
- https://launchdarkly.com/blog/introducing-guardrail-metrics
- https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics

### Draft: Methodology - Metric Roles, Guardrails, and Confidence Updates

You must treat metrics as role-based evidence, not a flat list. Every hypothesis must include one and only one primary metric, one or more guardrails, and optional secondary metrics. If you cannot assign a role, the metric is not decision-relevant.

How to use metric roles:

1. **Primary metric:** determines whether the hypothesis claim is supported.
2. **Guardrail metrics:** enforce do-no-harm constraints; they can block shipping even if the primary metric improves.
3. **Secondary metrics:** provide mechanism and transferability context; they cannot convert a failed primary metric into a win.

Guardrail decision rule:

- You must define guardrail non-inferiority or degradation thresholds in advance.
- If any guardrail breaches threshold under your chosen inference policy, you must not mark the hypothesis `validated`.
- If guardrail breach is operationally tolerated, you must record an explicit override rationale and owner, then downgrade confidence until follow-up confirms safety.

Confidence is an update process, not a static label:

1. Start with prior confidence (`low|medium|high`) based on pre-existing evidence quality.
2. After each analysis checkpoint, append a `confidence_update_log` entry with:
   - timestamp,
   - evidence reference,
   - quality gate snapshot,
   - rationale,
   - transition from old confidence to new confidence.
3. Never update confidence when critical quality gates fail.
4. Never increase confidence from exploratory-only findings without confirmatory follow-up.

Interpretation policy:

- `high` confidence requires passing quality gates, pre-registered criteria met, and no unresolved guardrail conflict.
- `medium` confidence allows directional signal with residual uncertainty (for example, underpowered but clean diagnostics).
- `low` confidence is default when data quality is uncertain, signals conflict, or conclusions depend on exploratory slicing.

Research basis for this draft:
- https://docs.statsig.com/experiments/advanced-setup/sequential-testing
- https://docs.statsig.com/experiments/statistical-methods/methodologies/benjamini-hochberg-procedure
- https://support.optimizely.com/hc/en-us/articles/4410283967245-False-discovery-rate-control
- https://docs.geteppo.com/statistics/sample-ratio-mismatch
- https://confidence.spotify.com/blog/better-decisions-with-guardrails
- https://amplitude.com/docs/feature-experiment/troubleshooting/sample-ratio-mismatch

### Draft: Available Tools (expanded and paste-ready)

You should collect evidence from internal strategy documents first, then link downstream experiment evidence before writing final hypothesis status. Use these tools exactly as shown:

```text
flexus_policy_document(op="list", args={"p": "/strategy/"})
flexus_policy_document(op="activate", args={"p": "/strategy/positioning-map"})
flexus_policy_document(op="activate", args={"p": "/strategy/offer-validation-{date}"})
flexus_policy_document(op="activate", args={"p": "/discovery/{study_id}/jtbd-outcomes"})
flexus_policy_document(op="activate", args={"p": "/experiments/{experiment_id}/spec"})
flexus_policy_document(op="activate", args={"p": "/experiments/{experiment_id}/results"})
write_artifact(artifact_type="experiment_hypothesis_stack", path="/strategy/hypothesis-stack", data={...})
```

Tool usage rules:

1. You must `activate` at least one upstream strategy/discovery source before creating or editing a hypothesis.
2. When a hypothesis is tied to an executed experiment, you must activate both experiment spec and result artifacts before changing status.
3. You must write the full hypothesis stack artifact after updates; partial in-memory updates are not considered durable.
4. You should include stable references (`experiment_id`, dashboard/evidence refs) so later analysis and learning skills can trace the decision.

External integration note for cross-tool lineage:

If your organization uses Jira/Notion/Airtable for planning and GrowthBook/Statsig/Amplitude/LaunchDarkly/PostHog for execution, you should preserve a stable join key (`hypothesis_id`) across planning object, experiment object, assignment evidence, and result dashboard reference. Do not rely on title matching.

Research basis for this draft:
- https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/
- https://developers.notion.com/reference/post-page
- https://docs.growthbook.io/api/
- https://docs.statsig.com/api-reference/events/log-custom-events
- https://amplitude.com/docs/apis/experiment/experiment-management-api
- https://launchdarkly.com/docs/api/experiments
- https://posthog.com/docs/api/experiments

### Draft: Anti-pattern Warnings (paste-ready blocks)

#### Draft: Anti-pattern - HARKing and post-hoc metric switching

**Signal:**  
Hypothesis statement, primary metric, or success threshold changed after outcome data was already visible.

**Consequence:**  
You inflate false positives, corrupt portfolio learning, and create non-reproducible "wins."

**Mitigation:**  
Lock hypothesis contract before launch, separate confirmatory vs exploratory findings in output, and require a new follow-up hypothesis for any post-hoc discovery.

**Hard rule:**  
If this signal is present, you must not label the original hypothesis as `validated`. At most, set it to `inconclusive` with exploratory notes and create a new confirmatory hypothesis.

#### Draft: Anti-pattern - Optional stopping under fixed-horizon analysis

**Signal:**  
Team repeatedly checks dashboard and stops when significance first appears, while test has not reached pre-registered runtime/sample requirements.

**Consequence:**  
Type I error inflation and effect-size overestimation (winner's curse).

**Mitigation:**  
Either (a) keep fixed-horizon discipline and wait for planned horizon, or (b) switch to a sequentially valid protocol before launch with explicit stopping logic.

**Hard rule:**  
Do not set `validated` when stop decision violated pre-registered analysis method.

#### Draft: Anti-pattern - Unresolved SRM

**Signal:**  
SRM check fails (for example, very low SRM p-value) and root cause is unresolved.

**Consequence:**  
Assignment integrity is compromised; measured lift may be invalid or sign-flipped.

**Mitigation:**  
Block decisioning, investigate assignment/exposure/logging paths, fix root cause, and rerun or re-evaluate only after quality gate passes.

**Hard rule:**  
`srm_check=fail` must block `validated` and `rejected` verdicts until resolved.

#### Draft: Anti-pattern - Guardrail bypass

**Signal:**  
Primary metric improves but one or more guardrails degrade past declared limits, and the team still attempts to ship.

**Consequence:**  
Local optimization damages system health (latency, reliability, trust, or unit economics).

**Mitigation:**  
Use pre-declared guardrail thresholds, enforce blocking logic, and require explicit override owner plus follow-up risk test if exception is made.

**Hard rule:**  
Without an approved override and mitigation plan, set status to `blocked_by_guardrail` instead of `validated`.

Research basis for anti-pattern drafts:
- https://docs.geteppo.com/statistics/sample-ratio-mismatch
- https://www.lukasvermeer.nl/srm/docs/faq/
- https://docs.launchdarkly.com/guides/statistical-methodology/mcc
- https://docs.launchdarkly.com/guides/statistical-methodology/sample-ratios/
- https://support.optimizely.com/hc/en-us/articles/4410283967245-False-discovery-rate-control
- https://engineering.atspotify.com/2024/05/fixed-power-designs-its-not-if-you-peek-its-what-you-peek-at

### Draft: Schema additions - full JSON fragment

```json
{
  "experiment_hypothesis_stack": {
    "type": "object",
    "required": ["created_at", "product_name", "hypotheses"],
    "additionalProperties": false,
    "properties": {
      "created_at": {
        "type": "string",
        "description": "RFC3339 timestamp when this stack snapshot is written."
      },
      "product_name": {
        "type": "string",
        "description": "Human-readable product or initiative name for this hypothesis portfolio."
      },
      "hypotheses": {
        "type": "array",
        "description": "Prioritized list of hypotheses with governance metadata required for decision quality.",
        "items": {
          "type": "object",
          "required": [
            "hypothesis_id",
            "category",
            "statement",
            "validation_method",
            "success_condition",
            "rejection_condition",
            "priority",
            "risk_level",
            "current_confidence",
            "status",
            "analysis_plan",
            "metric_roles",
            "power_design",
            "quality_gates",
            "confidence_update_log",
            "lineage",
            "evidence_refs"
          ],
          "additionalProperties": false,
          "properties": {
            "hypothesis_id": {
              "type": "string",
              "description": "Stable unique identifier used across planning, experimentation, and learning artifacts."
            },
            "category": {
              "type": "string",
              "enum": ["market", "product", "channel", "pricing"],
              "description": "Hypothesis class used for sequencing and prioritization logic."
            },
            "statement": {
              "type": "string",
              "description": "Falsifiable causal claim in plain language."
            },
            "validation_method": {
              "type": "string",
              "description": "Planned validation mechanism (for example A/B test, interview, or pricing test)."
            },
            "success_condition": {
              "type": "string",
              "description": "Pre-registered condition that confirms the hypothesis."
            },
            "rejection_condition": {
              "type": "string",
              "description": "Pre-registered falsification condition that rejects the hypothesis."
            },
            "priority": {
              "type": "string",
              "enum": ["p0", "p1", "p2", "p3"],
              "description": "Execution priority where p0 is highest urgency."
            },
            "risk_level": {
              "type": "string",
              "enum": ["fatal", "high", "medium", "low"],
              "description": "Business risk if the hypothesis is wrong."
            },
            "current_confidence": {
              "type": "string",
              "enum": ["low", "medium", "high"],
              "description": "Current confidence snapshot derived from the latest confidence update entry."
            },
            "status": {
              "type": "string",
              "enum": [
                "queued",
                "in_progress",
                "validated",
                "rejected",
                "inconclusive",
                "blocked",
                "invalidated_by_prior"
              ],
              "description": "Lifecycle state of this hypothesis after applying quality and decision rules."
            },
            "analysis_plan": {
              "type": "object",
              "required": [
                "method",
                "confidence_level",
                "multiple_testing_method",
                "correction_scope",
                "minimum_runtime_days",
                "minimum_sample_per_variant"
              ],
              "additionalProperties": false,
              "properties": {
                "method": {
                  "type": "string",
                  "enum": ["fixed_horizon", "sequential", "bayesian"],
                  "description": "Inference family selected before launch."
                },
                "confidence_level": {
                  "type": "number",
                  "description": "Declared confidence level used for interval-based decisions (for example 0.95)."
                },
                "multiple_testing_method": {
                  "type": "string",
                  "enum": ["none", "bonferroni", "benjamini_hochberg", "other"],
                  "description": "Correction policy used when multiple metrics, variants, or slices are interpreted."
                },
                "correction_scope": {
                  "type": "string",
                  "description": "Definition of the comparison family where correction is applied."
                },
                "minimum_runtime_days": {
                  "type": "integer",
                  "description": "Minimum runtime floor before final verdict is allowed."
                },
                "minimum_sample_per_variant": {
                  "type": "integer",
                  "description": "Minimum sample floor for each compared variant."
                }
              }
            },
            "metric_roles": {
              "type": "object",
              "required": ["primary_metric", "guardrail_metrics", "secondary_metrics"],
              "additionalProperties": false,
              "properties": {
                "primary_metric": {
                  "type": "object",
                  "required": ["metric_name", "expected_direction"],
                  "additionalProperties": false,
                  "properties": {
                    "metric_name": {
                      "type": "string",
                      "description": "Single primary metric used for confirmatory decision."
                    },
                    "expected_direction": {
                      "type": "string",
                      "enum": ["increase", "decrease"],
                      "description": "Direction that supports the hypothesis claim."
                    }
                  }
                },
                "guardrail_metrics": {
                  "type": "array",
                  "description": "Safety metrics that can block a positive primary metric decision.",
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
                        "description": "Maximum tolerated negative movement before guardrail blocks validation."
                      },
                      "non_inferiority_margin": {
                        "type": "number",
                        "description": "Optional non-inferiority margin where applicable."
                      }
                    }
                  }
                },
                "secondary_metrics": {
                  "type": "array",
                  "description": "Contextual metrics for mechanism interpretation, not primary decision override.",
                  "items": {
                    "type": "string"
                  }
                }
              }
            },
            "power_design": {
              "type": "object",
              "required": ["alpha", "target_power", "mde", "estimated_runtime_days", "population_assumption_ref"],
              "additionalProperties": false,
              "properties": {
                "alpha": {
                  "type": "number",
                  "description": "Type I error budget for planned decision policy."
                },
                "target_power": {
                  "type": "number",
                  "description": "Desired true-positive detection power under planned effect assumptions."
                },
                "mde": {
                  "type": "number",
                  "description": "Minimum detectable effect used for planning runtime/sample expectations."
                },
                "estimated_runtime_days": {
                  "type": "integer",
                  "description": "Estimated days needed to satisfy power assumptions."
                },
                "population_assumption_ref": {
                  "type": "string",
                  "description": "Reference to traffic/population assumptions used for power planning."
                }
              }
            },
            "quality_gates": {
              "type": "object",
              "required": ["srm_check", "instrumentation_status", "assignment_logging_status"],
              "additionalProperties": false,
              "properties": {
                "srm_check": {
                  "type": "string",
                  "enum": ["pass", "fail", "not_applicable"],
                  "description": "Sample ratio mismatch gate result at latest decision checkpoint."
                },
                "instrumentation_status": {
                  "type": "string",
                  "enum": ["healthy", "degraded", "unknown"],
                  "description": "Telemetry integrity state for metrics used in decisioning."
                },
                "assignment_logging_status": {
                  "type": "string",
                  "enum": ["healthy", "degraded", "unknown"],
                  "description": "Integrity status for treatment assignment and exposure logging."
                },
                "gate_notes": {
                  "type": "array",
                  "description": "Short notes describing detected quality issues or confirmations.",
                  "items": {
                    "type": "string"
                  }
                }
              }
            },
            "confidence_update_log": {
              "type": "array",
              "description": "Chronological confidence transitions with evidence and rationale.",
              "items": {
                "type": "object",
                "required": [
                  "updated_at",
                  "from_confidence",
                  "to_confidence",
                  "evidence_ref",
                  "rationale"
                ],
                "additionalProperties": false,
                "properties": {
                  "updated_at": {
                    "type": "string",
                    "description": "RFC3339 timestamp for this confidence transition."
                  },
                  "from_confidence": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Confidence level before applying current evidence."
                  },
                  "to_confidence": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Confidence level after applying current evidence."
                  },
                  "evidence_ref": {
                    "type": "string",
                    "description": "Reference to experiment result, report, or supporting artifact."
                  },
                  "rationale": {
                    "type": "string",
                    "description": "Reason for confidence change, including uncertainty notes."
                  },
                  "quality_gate_snapshot": {
                    "type": "string",
                    "description": "Optional short summary of gate status at update time."
                  }
                }
              }
            },
            "lineage": {
              "type": "object",
              "required": [
                "experiment_platform",
                "experiment_id",
                "feature_flag_key",
                "assignment_event_ref",
                "result_dashboard_ref"
              ],
              "additionalProperties": false,
              "properties": {
                "experiment_platform": {
                  "type": "string",
                  "description": "Platform where validation run is executed (for example statsig, growthbook, launchdarkly, amplitude, posthog)."
                },
                "experiment_id": {
                  "type": "string",
                  "description": "Platform-specific experiment identifier linked to this hypothesis."
                },
                "feature_flag_key": {
                  "type": "string",
                  "description": "Flag key or allocation object used to assign variants."
                },
                "assignment_event_ref": {
                  "type": "string",
                  "description": "Reference to assignment/exposure event stream used for quality validation."
                },
                "result_dashboard_ref": {
                  "type": "string",
                  "description": "Reference or URL to analysis dashboard/report used for decision traceability."
                }
              }
            },
            "evidence_refs": {
              "type": "array",
              "description": "List of source artifacts that support current hypothesis status.",
              "items": {
                "type": "string"
              }
            }
          }
        }
      }
    }
  }
}
```

### Draft: Status transition constraints (paste-ready)

You must enforce status transitions with machine-checkable gates:

1. `queued -> in_progress` requires non-empty `analysis_plan`, `metric_roles`, and `power_design`.
2. `in_progress -> validated` requires `quality_gates.srm_check=pass`, healthy instrumentation/assignment logging, success condition met, and no guardrail breach beyond declared limits.
3. `in_progress -> rejected` requires quality gates pass and rejection condition met.
4. `in_progress -> inconclusive` requires quality gates pass and planned horizon reached without success/rejection condition.
5. Any critical quality gate failure forces `status=blocked` until resolved.

You must never overwrite prior evidence when status changes. Append confidence updates and evidence references so downstream learning can reconstruct the decision path.

Research basis for this draft:
- https://docs.growthbook.io/app/experiment-decisions
- https://docs.statsig.com/exp-templates/decision-framework
- https://docs.geteppo.com/statistics/sample-ratio-mismatch
- https://launchdarkly.com/docs/guides/statistical-methodology/sample-ratios/

---

## Gaps & Uncertainties

- Vendor documentation quality is uneven for exact endpoint stability, beta scope, and long-term pricing; some API constraints may change without strong versioned changelogs.
- Several anti-pattern sources come from clinical/social-science domains; principles are transferable, but effect-size magnitudes and operational prevalence in SaaS product experimentation vary by context.
- Online FDR methods (LOND/LORD/SAFFRON/ADDIS) are well established academically, but direct, fully transparent implementation details in commercial product experimentation platforms are not always publicly documented.
- Sequential vs fixed-horizon trade-off guidance differs by platform assumptions (traffic predictability, peeking policy, objective function); this is a genuine methodological tension, not a resolvable doc inconsistency.
- Public docs often omit practical integration failure rates (event loss, schema drift, late event arrival), so recommended quality gates are grounded in known diagnostics rather than universal quantitative benchmarks.
