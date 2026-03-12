# Research: experiment-learning

**Skill path:** `strategist/skills/experiment-learning/`
**Bot:** strategist (researcher | strategist | executor)
**Research date:** 2026-03-04
**Status:** complete

---

## Context

`experiment-learning` converts completed experiment outcomes into durable organizational knowledge, then updates the hypothesis stack. The skill's core problem is not "did variant B win," but "what mechanism did we learn, how certain are we, and what hypotheses should move next?" This matters because teams that document only winners lose rejected and inconclusive evidence, causing repeated mistakes, weak prioritization, and slow strategic convergence.

In practice, this skill is used after experiment readout and before strategy reprioritization. The user (typically PM, growth lead, data scientist, or strategist) needs a structured codification step that captures: decision logic, evidence quality, mechanism explanation, implications, and resulting hypothesis transitions. Research focus for this pass: robust methodology, real tool/API landscape, signal-quality interpretation, anti-pattern prevention, and schema-level recommendations that can be translated directly into `SKILL.md`.

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
- [x] No invented tool names, method IDs, or API endpoints; only verified references
- [x] Contradictions between sources are explicitly called out
- [x] Findings volume is within target range and synthesized (not shallow, not dump-only)

---

## Research Angles

Each angle was researched by a separate sub-agent, then synthesized.

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

1) **Codify a decision rule before interpreting outcomes.** Mature programs map metric outcomes to a deterministic ship/no-ship recommendation using metric classes (success, guardrail, deterioration, quality), not ad-hoc interpretation after the fact. This is directly applicable to `experiment-learning`: codification should include rule evaluation output, not only narrative explanation. Source: https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics

2) **Guardrails need different treatment than "multiple chances to win" metrics.** Recent risk-aware guidance shows alpha correction logic differs for guardrail non-inferiority; power/beta handling becomes central at decision-rule level. For this skill, storing only p-values is insufficient; it should preserve rule-level risk assumptions. Sources: https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics, https://arxiv.org/abs/2402.11609

3) **Pre-register interim analysis and allowed decision actions.** PRIAD-style planning reduces hindsight rationalization and improves cost-effectiveness of experimentation decisions. For this skill, include links to analysis plan and explicit deviation records. Source: https://ideas.repec.org/a/oup/jconrs/v51y2024i4p845-865..html

4) **When variance is uncertain, use precision-based stopping discipline.** Fixed-power designs (2024) provide a practical option between strict fixed-horizon and naive peeking. For codification, record stop design and stop reason so future analysts can assess validity. Sources: https://engineering.atspotify.com/2024/05/fixed-power-designs-its-not-if-you-peek-its-what-you-peek-at, https://arxiv.org/abs/2405.03487

5) **Separate monitoring events from inferential decisions.** Operational alerts (instrumentation, SRM, regressions) must be logged as quality blockers, not mixed into effect interpretation. This improves reproducibility and "why we trusted this readout" traceability. Source: https://www.statsig.com/blog/product-experimentation-best-practices

6) **Upgrade hypothesis updates from binary status to confidence transitions.** Vendor practice increasingly supports Bayesian priors/posteriors; practically, this enables richer handling of inconclusive outcomes than a strict validated/rejected split. Sources: https://blog.growthbook.io/bayesian-model-updates-in-growthbook-3-0/, https://www.statsig.com/updates/update/bayesian-priors

7) **Institutional learning requires a searchable experiment memory.** Meta-analysis and knowledge-base workflows show value compounding with experiment volume, including better metric sensitivity judgments and faster hypothesis generation. Source: https://www.statsig.com/blog/experimental-meta-analysis-and-knowledge-base

8) **Synthesize across batches, not only per experiment.** Once teams accumulate enough experiments, aggregate pattern synthesis (by lever, metric family, segment) becomes a first-class strategic process. Source: https://kameleoon.com/blog/how-to-use-meta-analysis-in-ab-testing

9) **Code-to-metric context improves mechanism quality.** Emerging practice links experiment outcomes with implementation context (flags, variants, code changes), reducing shallow "it moved" conclusions and strengthening causal explanations. Source: https://www.statsig.com/blog/knowledge-graph

**Contradictions noted in this angle:**
- **Sequential flexibility vs fixed-power discipline:** sequential approaches allow earlier looks, while fixed-power emphasizes stronger effect estimation discipline in many product contexts.
- **Bayesian "monitor anytime" messaging vs stopping-policy rigor:** practical implementations still need explicit stopping governance to avoid decision drift.
- **Strict centralized schema vs documentation burden:** richer templates improve reuse but can reduce compliance without automation/defaults.

**Sources:**
- https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics (2024)
- https://arxiv.org/abs/2402.11609 (2024)
- https://engineering.atspotify.com/2024/05/fixed-power-designs-its-not-if-you-peek-its-what-you-peek-at (2024)
- https://arxiv.org/abs/2405.03487 (2024)
- https://ideas.repec.org/a/oup/jconrs/v51y2024i4p845-865..html (2024)
- https://www.statsig.com/blog/product-experimentation-best-practices (2024)
- https://blog.growthbook.io/bayesian-model-updates-in-growthbook-3-0/ (2024)
- https://www.statsig.com/updates/update/bayesian-priors (2025)
- https://www.statsig.com/blog/experimental-meta-analysis-and-knowledge-base (2024)
- https://kameleoon.com/blog/how-to-use-meta-analysis-in-ab-testing (2025)
- https://www.statsig.com/blog/knowledge-graph (2026)

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

1) **The market splits into two planes:** experimentation control plane (assignment, metrics, analysis) and knowledge/decision plane (decision logs, hypothesis workflow, documentation). This split is now the de-facto architecture in 2024-2026 programs.

2) **Experimentation control plane options are concrete and API-accessible:** LaunchDarkly, Statsig, Optimizely Feature Experimentation, GrowthBook, PostHog, Eppo, and Amplitude all expose APIs for experiment/flag workflows, with different governance and data-model tradeoffs. Sources: https://docs.launchdarkly.com/home/experimentation/, https://docs.statsig.com/console-api/all-endpoints-generated, https://docs.developers.optimizely.com/feature-experimentation/reference/feature-experimentation-api-overview, https://docs.growthbook.io/api/, https://posthog.com/docs/api/flags, https://docs.geteppo.com/reference/api/, https://amplitude.com/docs/apis/experiment/experiment-management-api

3) **Knowledge/decision systems are usually external systems of record:** Notion, Jira, Confluence, GitHub Projects, Airtable are commonly used for codified learnings, rationale, and ownership transitions. Sources: https://developers.notion.com/reference/post-page, https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/, https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/, https://docs.github.com/en/rest/projects/items, https://support.airtable.com/docs/public-rest-api

4) **API-level operational constraints are real and must shape skill behavior.** Rate limits and key-scoping patterns differ by vendor; codification pipelines need idempotent writes, retry backoff, and write-audit traces. Sources: https://support.launchdarkly.com/hc/en-us/articles/22328238491803-Error-429-Too-Many-Requests-API-Rate-Limit, https://developers.notion.com/reference/request-limits, https://developer.atlassian.com/cloud/jira/platform/rate-limiting, https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api, https://support.airtable.com/docs/managing-api-call-limits-in-airtable

5) **Warehouse-native experimentation is now mainstream, not niche.** Statsig warehouse-native and Eppo patterns show direct warehouse integration becoming a default for data-mature organizations, improving reproducibility but increasing data engineering dependency. Sources: https://docs.statsig.com/statsig-warehouse-native/introduction, https://docs.geteppo.com/

6) **Evaluation and management APIs are often separated.** Several platforms separate runtime evaluation from administrative operations; skill design should avoid mixing these credentials/surfaces. Source: https://amplitude.com/docs/apis/experiment/experiment-evaluation-api

7) **Entity semantics are inconsistent across tools.** `flag`, `experiment`, `rule`, and `layer` can differ by platform; a canonical internal schema is required to avoid mapping errors during codification.

8) **De-facto integration standard:** always persist a cross-system join key set (`experiment_id`, `flag_key`, `hypothesis_id`, `metric_set_id`) in every record. This is the practical backbone of durable learning retrieval.

**Tool matrix (concise):**

| Tool | Core capability | Relevant API/integration surface | Key limitation | Source |
|---|---|---|---|---|
| LaunchDarkly | Feature flags + experimentation | REST API + experimentation guides | Rate limiting and enterprise complexity | https://docs.launchdarkly.com/guides/api/rest-api |
| Statsig | Experimentation and analytics platform | Console API, warehouse-native stack | Strong governance needed for metrics/keys | https://docs.statsig.com/console-api/all-endpoints-generated |
| Optimizely FE | Feature experimentation lifecycle | FE API for flags/rules/variations | API coverage can differ by object type | https://docs.developers.optimizely.com/feature-experimentation/reference/feature-experimentation-api-overview |
| GrowthBook | Open-source/cloud experimentation | REST API (`/api/v1`) + warehouse model | Self-hosting/ops overhead tradeoff | https://docs.growthbook.io/api/ |
| PostHog | Unified product analytics + experiments | Flags API + event ingestion APIs | Event volume/cost coupling | https://posthog.com/docs/api/flags |
| Eppo | Warehouse-native experimentation | REST API + warehouse connectors | Depends on warehouse maturity | https://docs.geteppo.com/reference/api/ |
| Amplitude Experiment | Management/evaluation split | Management API + evaluation API | Surface fragmentation risk | https://amplitude.com/docs/apis/experiment/experiment-management-api |

**Contradictions / fragmentation in this angle:**
- Some platforms present "all-in-one" workflows, while others require explicit multi-system architecture.
- API maturity differs by object type and plan tier; "has API" does not mean "full lifecycle API parity."
- Pricing/rate limits are often plan-dependent and not fully public, requiring implementation-time confirmation.

**Sources:**
- https://docs.launchdarkly.com/home/experimentation/ (2026)
- https://docs.launchdarkly.com/guides/api/rest-api (2026)
- https://docs.statsig.com/console-api/all-endpoints-generated (2026)
- https://docs.statsig.com/statsig-warehouse-native/introduction (2026)
- https://docs.developers.optimizely.com/feature-experimentation/reference/feature-experimentation-api-overview (2026)
- https://docs.growthbook.io/api/ (2026)
- https://posthog.com/docs/api/flags (2026)
- https://docs.geteppo.com/reference/api/ (2026)
- https://amplitude.com/docs/apis/experiment/experiment-management-api (2026)
- https://amplitude.com/docs/apis/experiment/experiment-evaluation-api (2026)
- https://developers.notion.com/reference/post-page (2026)
- https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/ (evergreen, accessed 2026)
- https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/ (evergreen, accessed 2026)
- https://docs.github.com/en/rest/projects/items (2026)
- https://support.airtable.com/docs/public-rest-api (evergreen, accessed 2026)

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

1) **SRM is a hard quality gate, not a soft warning.** If allocation mismatch is detected, causal interpretation is unsafe until assignment/exposure root cause is investigated. Platforms document SRM with formal testing (for example, Amplitude uses sequential chi-square with alpha 0.01). Sources: https://amplitude.com/docs/feature-experiment/troubleshooting/sample-ratio-mismatch, https://docs.geteppo.com/statistics/sample-ratio-mismatch/

2) **Threshold mismatch exists for SRM policies (`0.01` vs `0.001`).** Vendor and team standards differ; the key is policy consistency, explicitness, and logging threshold rationale in the learning artifact.

3) **Fixed-horizon and sequential inference cannot be mixed casually.** Peeking with fixed-horizon p-values inflates false positives; sequentially valid engines address this differently. Source: https://docs.statsig.com/experiments-plus/sequential-testing/

4) **Seasonality and exposure window effects are practical validity risks.** Teams should avoid early conclusions before sufficient cycle coverage (often at least one full week in product contexts). Source: https://www.statsig.com/blog/product-experimentation-best-practices

5) **Inconclusive is not one state; it needs subclassification.** Distinguish insufficient sensitivity, near-zero practical effect, and quality-invalidated runs. This distinction is essential for correct hypothesis-stack updates.

6) **Do not use p>0.05 as "safe/no harm."** For guardrails, non-inferiority/equivalence framing is stronger than "not significant." Source: https://www.optimizely.com/insights/blog/understanding-and-implementing-guardrail-metrics

7) **Multiplicity must be handled at the right layer.** Metric/segment/variant expansion increases false discovery risk; teams should classify segment findings as exploratory unless preplanned and corrected. Source: https://www.optimizely.com/hc/en-us/articles/4410283967245-False-discovery-rate-control

8) **Novelty and temporal drift can invert conclusions post-launch.** Time-profiled interpretation (for example, days-since-exposure) helps separate transient excitement from durable effect. Sources: https://www.statsig.com/blog/novelty-effects, https://research.atspotify.com/2024/05/estimating-long-term-outcome-of-algorithms

9) **CUPED improves precision but does not cure bad instrumentation.** Covariate adjustment helps variance, but data quality failures still invalidate conclusions. Sources: https://docs.statsig.com/stats-engine/methodologies/cuped/, https://www.statsig.com/blog/cuped

10) **Interpretation should be codified as a state machine.** Recommended transition logic: `quality gate -> inference mode gate -> sensitivity gate -> effect/guardrail gate -> learning verdict -> next hypotheses`. This makes output audit-ready and teachable.

**Contradictions noted in this angle:**
- SRM policy strictness differs by organization and platform.
- "Peeking is fine" and "never peek" are both oversimplifications; validity depends on chosen inferential design.
- Some practice guides still mention post-hoc power; statistical guidance increasingly favors CI + practical bound interpretation.

**Sources:**
- https://amplitude.com/docs/feature-experiment/troubleshooting/sample-ratio-mismatch (2024)
- https://docs.geteppo.com/statistics/sample-ratio-mismatch/ (2026, accessed)
- https://docs.statsig.com/experiments-plus/sequential-testing/ (2026, accessed)
- https://www.statsig.com/blog/product-experimentation-best-practices (2024)
- https://www.optimizely.com/insights/blog/understanding-and-implementing-guardrail-metrics (2025)
- https://www.optimizely.com/hc/en-us/articles/4410283967245-False-discovery-rate-control (evergreen, accessed 2026)
- https://www.statsig.com/blog/novelty-effects (2024)
- https://research.atspotify.com/2024/05/estimating-long-term-outcome-of-algorithms (2024)
- https://docs.statsig.com/stats-engine/methodologies/cuped/ (2026, accessed)
- https://www.statsig.com/blog/cuped (2024)
- https://arxiv.org/abs/1512.04922 (2016/2019, evergreen foundational optional-stopping reference)

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

1) **Survivorship bias:** teams archive wins and lose null/negative outcomes, creating false confidence and repeated mistakes. Mitigation: mandatory all-outcomes registry with denominator metrics. Sources: https://pmc.ncbi.nlm.nih.gov/articles/PMC11962440/, https://www.statsig.com/blog/experimental-meta-analysis-and-knowledge-base

2) **Untracked rejected hypotheses (required):** if rejection reasons are not stored, teams rerun failed ideas under new names. Mitigation: preregistered hypothesis IDs and required rejection rationale fields. Source: https://www.socialscienceregistry.org/site/instructions

3) **Local overfitting / winner's curse (required):** selecting top uplift estimates overstates expected impact in production. Mitigation: shrinkage or Bayesian adjustment plus confirmatory follow-up. Sources: https://www.amazon.science/publications/overcoming-the-winners-curse-leveraging-bayesian-inference-to-improve-estimates-of-the-impact-of-features-launched-via-a-b-tests, https://arxiv.org/abs/2411.18569

4) **Proxy ratio trap:** ratio improvements can hide denominator collapse (for example, sessions down). Mitigation: enforce numerator/denominator decomposition before verdict. Source: https://www.statsig.com/blog/product-experimentation-best-practices

5) **Premature stopping on significance:** early "wins" often regress with full horizon. Mitigation: precommitted stopping design, with explicit prohibition of ad-hoc stop-on-green. Source: https://engineering.atspotify.com/2024/05/fixed-power-designs-its-not-if-you-peek-its-what-you-peek-at

6) **Multiple comparisons without correction:** large test families inflate false positives and create fragile roadmaps. Mitigation: family-level correction policy and primary-metric discipline. Source: https://www.statsig.com/perspectives/multiple-comparisons-abtests-care

7) **Ignoring SRM and identity contamination:** variant jumping, changed allocations, or exposure logging defects can invalidate inference. Mitigation: "no ship under SRM" and assignment/exposure diagnostics as hard blockers. Sources: https://amplitude.com/docs/feature-experiment/troubleshooting/sample-ratio-mismatch, https://launchdarkly.com/docs/guides/statistical-methodology/sample-ratios

8) **Incident-to-policy debt:** emergency protections can outlive intent and degrade normal users if lifecycle governance is weak. Mitigation: temporary-by-default controls, owner, expiry, and cleanup SLA. Source: https://github.blog/engineering/infrastructure/when-protections-outlive-their-purpose-a-lesson-on-managing-defense-systems-at-scale/

9) **Rollout false positives in safety systems:** dry runs can miss production false positive classes. Mitigation: staged rollout plus explicit false-positive corpus and kill-switch criteria. Source: https://blog.railway.com/p/incident-report-february-11-2026

10) **Retry amplification and control-plane fragility:** infrastructure instability in flag systems can distort experiment operations and interpretation cadence. Mitigation: bounded retries, right-sizing, and dependency isolation. Source: https://posthog.com/handbook/company/post-mortems/2025-10-21-feature-flags-recurring-outages

**Bad vs good output patterns:**
- **Bad:** "Win rate is high" without denominator including null/negative experiments. **Good:** win/loss/inconclusive denominator and reasons.
- **Bad:** "Rejected, moving on" with no causal explanation. **Good:** rejected hypothesis includes wrong prediction, evidence, and next hypothesis.
- **Bad:** "Significant at day 2, ship." **Good:** decision references planned stopping design and quality checks.
- **Bad:** "Guardrail not significant, so safe." **Good:** explicit non-inferiority criterion and margin handling.
- **Bad:** "One strong segment proves effect." **Good:** exploratory segment flagged for confirmatory follow-up.

**Sources:**
- https://pmc.ncbi.nlm.nih.gov/articles/PMC11962440/ (2025)
- https://www.statsig.com/blog/experimental-meta-analysis-and-knowledge-base (2024)
- https://www.socialscienceregistry.org/site/instructions (evergreen registry standard)
- https://www.amazon.science/publications/overcoming-the-winners-curse-leveraging-bayesian-inference-to-improve-estimates-of-the-impact-of-features-launched-via-a-b-tests (2024)
- https://arxiv.org/abs/2411.18569 (2024)
- https://www.statsig.com/blog/product-experimentation-best-practices (2024)
- https://engineering.atspotify.com/2024/05/fixed-power-designs-its-not-if-you-peek-its-what-you-peek-at (2024)
- https://www.statsig.com/perspectives/multiple-comparisons-abtests-care (2025)
- https://amplitude.com/docs/feature-experiment/troubleshooting/sample-ratio-mismatch (2024)
- https://launchdarkly.com/docs/guides/statistical-methodology/sample-ratios (evergreen, accessed 2026)
- https://blog.railway.com/p/incident-report-february-11-2026 (2026)
- https://github.blog/engineering/infrastructure/when-protections-outlive-their-purpose-a-lesson-on-managing-defense-systems-at-scale/ (2026)
- https://posthog.com/handbook/company/post-mortems/2025-10-21-feature-flags-recurring-outages (2025)

---

### Angle 5+: Schema Design, Provenance, and Interoperability
> Domain-specific angle: which data shapes make experiment learnings durable, queryable, and auditable across systems?

**Findings:**

1) **Use a 3-entity chain:** `experiment_result -> learning_artifact -> hypothesis_update/decision_log`. This prevents conflating statistical output with strategic decision and enables traceable updates.

2) **Separate assignment and exposure fields explicitly.** Real platforms distinguish assignment and exposure events; codification should preserve both timestamps and policy. Sources: https://posthog.com/docs/experiments/exposures, https://amplitude.com/docs/feature-experiment/under-the-hood/event-tracking

3) **Add integrity block fields:** `srm_detected`, `srm_p_value`, `multi_variant_exposure`, `attribution_policy`. These fields determine whether inference is trusted or blocked. Source: https://amplitude.com/docs/feature-experiment/troubleshooting/sample-ratio-mismatch

4) **Store feature-evaluation provenance:** `flag_key`, `variant`, `provider`, `ruleset_version`, and context identifier; otherwise mechanism explanations are hard to reproduce. Sources: https://openfeature.dev/specification/sections/flag-evaluation/, https://opentelemetry.io/docs/specs/semconv/feature-flags/feature-flags-events/

5) **Promote confidence to structured object, not free text.** Include method, effect size, interval/posterior, guardrail failures, and confidence level so downstream systems can query quality and uncertainty.

6) **Decision log should be first-class schema object.** Include `decision`, `decided_by`, `decided_at`, `rationale`, and blockers; this bridges analytics and product governance.

7) **Evidence links should be typed and verifiable.** Instead of plain URLs, store `type`, `uri`, `relation`, `captured_at`, optional checksum for integrity.

8) **Version schema aggressively.** Add `schema_version` and `record_version`; use modern JSON Schema features for controlled evolution (`if/then/else`, `unevaluatedProperties`, composition). Source: https://json-schema.org/draft/2020-12

9) **Capture lineage/provenance metadata.** OpenLineage-style concepts (parent run, dataset version, source code ref) increase auditability of learning claims. Source: https://openlineage.io/docs/spec/

10) **For event-driven interoperability, support CloudEvents envelope (evergreen).** This reduces integration friction for publishing/consuming learning events across systems. Sources: https://raw.githubusercontent.com/cloudevents/spec/v1.0/spec.md, https://learn.microsoft.com/en-us/azure/event-grid/cloud-event-schema

**Proposed schema deltas for `experiment-learning`:**
- Rename `hypothesis_ref` -> `source_hypothesis_id`
- Expand `new_hypotheses_generated` into `hypothesis_updates[]` with operation type (`create`, `reprioritize`, `invalidate`, `merge`)
- Add `source_result_ref` (`artifact_path`, `analysis_run_id`, `analyzed_at`, `result_hash`)
- Add `assignment_integrity` object
- Add `decision_log` object
- Add `confidence` object (method + uncertainty + confidence level)
- Add typed `evidence_links[]`
- Add `lineage` object (`parent_learning_ids`, `dataset_versions`, `source_code_ref`)
- Replace rigid `implications.for_*` with extensible `implications[]` entries (`domain`, `summary`, `confidence`)
- Add `schema_version` and `record_version`

**Sources:**
- https://posthog.com/docs/experiments/exposures (2026)
- https://amplitude.com/docs/feature-experiment/under-the-hood/event-tracking (2024)
- https://amplitude.com/docs/feature-experiment/troubleshooting/sample-ratio-mismatch (2024)
- https://openfeature.dev/specification/sections/flag-evaluation/ (evergreen, accessed 2026)
- https://opentelemetry.io/docs/specs/semconv/feature-flags/feature-flags-events/ (evergreen, accessed 2026)
- https://openlineage.io/docs/spec/ (evergreen, accessed 2026)
- https://json-schema.org/draft/2020-12 (2022, evergreen standard)
- https://raw.githubusercontent.com/cloudevents/spec/v1.0/spec.md (evergreen standard)
- https://learn.microsoft.com/en-us/azure/event-grid/cloud-event-schema (2026)

---

## Synthesis

Across all angles, the central pattern is clear: teams no longer treat experiment readout as a one-off statistical report; they treat it as a decision system with explicit risk controls, quality gates, and durable knowledge capture. The most actionable takeaway for this skill is to convert "learning extraction" into a structured state machine with explicit checkpoints: quality validity, inferential validity, decision-rule evaluation, mechanism codification, and hypothesis transitions.

A key cross-angle connection is that methodology quality and schema quality are inseparable. If the artifact schema does not represent assignment integrity, stopping design, confidence structure, and decision rationale, then even good analysis is not reusable. Conversely, over-rich schemas can fail in practice if tool integrations are brittle. This creates a practical requirement: a strict minimum required core, plus optional enrichments where automation exists.

There are also explicit contradictions that should remain visible in the skill instead of being hidden: sequential flexibility vs fixed-power discipline, SRM strictness thresholds, and varying interpretations of guardrail safety. The correct response is not to pick one universal rule; it is to encode policy parameters explicitly in artifacts so future readers can reconstruct why a conclusion was trusted.

Failure-mode research reinforces that organizational learning breaks more often from process debt than from pure statistical ignorance: survivorship bias, missing rejected hypotheses, and incident-era shortcuts that outlive their purpose are recurring causes of poor strategic memory. Therefore, anti-pattern checks must be first-class outputs of this skill, not optional commentary.

Finally, tool landscape findings suggest that this skill should remain tool-agnostic but schema-strict: integrations will vary (LaunchDarkly/Statsig/GrowthBook/PostHog/Eppo/etc.), while durable learning requires stable canonical IDs, typed evidence links, and explicit decision logs regardless of platform choice.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.

- [ ] Add a mandatory `decision_rule_evaluation` step (success/guardrail/deterioration/quality -> recommendation) before hypothesis-stack update.
- [ ] Add `quality_gate_status` with explicit blockers (`srm_detected`, instrumentation issues, variant jumping) and rule "no final verdict if quality gate fails."
- [ ] Split `inconclusive` into operational subclasses (`insufficient_sensitivity`, `practically_null`, `quality_invalid`).
- [ ] Extend schema with `source_result_ref`, `assignment_integrity`, `decision_log`, and structured `confidence`.
- [ ] Replace status-only hypothesis updates with `hypothesis_updates[]` operations and confidence delta.
- [ ] Require `rejection_reason` and `next_hypothesis` for rejected outcomes to prevent untracked rejected hypotheses.
- [ ] Add anti-pattern checklist section: survivorship bias, local overfitting/winner's curse, ratio trap, multiplicity, and stop-on-significance.
- [ ] Add pattern-synthesis cadence requirement (for example, every 5+ experiments or monthly portfolio review) with cross-experiment metrics.
- [ ] Require canonical join keys in every artifact: `experiment_id`, `source_hypothesis_id`, `flag_key` (if applicable), `metric_set_id`.
- [ ] Add schema versioning (`schema_version`, `record_version`) and evidence typing (`evidence_links[]`) for long-term interoperability.

---

## Draft Content for SKILL.md

> Paste-ready content fragments for `SKILL.md`. This section is intentionally verbose so the editor can cut down without inventing missing logic.
> Coverage: every recommendation in the previous section has a matching draft block here.

### Draft: Core Operating Mode and Decision State Machine

You run this skill in learning-first mode. You do not optimize for fast shipping if confidence, validity, or interpretation quality is weak. Your job is to convert one experiment result into durable organizational memory that updates the hypothesis stack with traceable logic.

You always follow this state machine and you do not skip states:

1. **Input activation** -> activate result, spec, and current hypothesis stack documents.
2. **Quality gate** -> validate assignment/exposure integrity before any effect interpretation.
3. **Inference gate** -> identify the inference mode used in analysis (sequential, fixed-horizon, Bayesian) and confirm decisions are consistent with that mode.
4. **Decision-rule evaluation** -> evaluate success metrics, guardrails, deterioration metrics, and quality status against explicit policy.
5. **Outcome classification** -> classify as `validated`, `rejected`, or `inconclusive` with an explicit subclass if inconclusive.
6. **Mechanism extraction** -> document why the observed outcome happened, not only what moved.
7. **Hypothesis stack update** -> apply explicit operations (`create`, `reprioritize`, `invalidate`, `merge`) with confidence deltas.
8. **Artifact persistence** -> write both experiment-level learnings and updated stack artifacts with canonical join keys and evidence links.
9. **Portfolio synthesis trigger** -> mark whether this artifact must be included in the next batch synthesis review.

You must block final strategic conclusions if quality checks fail. In this case, you still write a learning artifact, but it must be marked as `inconclusive` with reason `quality_invalid` and include corrective actions before rerun.

Source basis:
- https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics
- https://engineering.atspotify.com/2024/05/fixed-power-designs-its-not-if-you-peek-its-what-you-peek-at
- https://amplitude.com/docs/feature-experiment/troubleshooting/sample-ratio-mismatch
- https://docs.geteppo.com/statistics/sample-ratio-mismatch/
- https://docs.statsig.com/experiments-plus/sequential-testing/

### Draft: Mandatory Workflow (Second-Person Procedure)

Before you codify any conclusion, you activate required context and verify that the experiment result is decision-ready. If any required context is missing, you stop and write a blocked record instead of inventing assumptions.

**Step 1 - Activate required artifacts**

You activate:
- experiment results document,
- experiment specification document,
- current hypothesis stack document.

If any activation fails or returns missing content, you do not continue with verdict logic.

**Step 2 - Run quality gate as a hard blocker**

You check for:
- sample ratio mismatch and allocation anomalies,
- instrumentation gaps and missing event coverage,
- exposure/assignment inconsistencies,
- identity contamination or variant jumping.

If any blocker is present, set:
- `quality_gate_status.is_valid = false`,
- `experiment_verdict = "inconclusive"`,
- `inconclusive_reason = "quality_invalid"`.

You then record mitigation actions and rerun preconditions.

**Step 3 - Validate inference mode before interpretation**

You identify whether the underlying readout used:
- frequentist sequential testing,
- frequentist fixed-horizon design,
- Bayesian decision outputs.

You do not mix interpretation rules across modes. For example, you do not treat Bayesian posterior outputs as if they were fixed-horizon p-values.

**Step 4 - Evaluate explicit decision rule**

You evaluate:
- success metrics against predeclared success criteria,
- guardrails with non-inferiority/no-harm logic,
- deterioration metrics for explicit regression risks,
- quality status from Step 2.

You produce one recommendation:
- `rollout`,
- `do_not_rollout`,
- `discuss`.

You record recommendation rationale in plain language with references to metric evidence.

**Step 5 - Classify outcome with required inconclusive subclass**

If recommendation is positive and guardrails pass, classify `validated`.
If recommendation is negative or harm is detected, classify `rejected`.
If decision is unresolved, classify `inconclusive` and force one reason:
- `insufficient_sensitivity`,
- `practically_null`,
- `quality_invalid`.

You never leave an experiment in a generic untyped inconclusive state.

**Step 6 - Extract mechanism and generalizable learning**

You write:
- mechanism explanation (what causal behavior likely drove outcome),
- generalizable learning claims with confidence levels,
- scope boundaries (where this learning probably does or does not transfer).

If mechanism is weak or speculative, you say so explicitly and reduce confidence.

**Step 7 - Update hypothesis stack with explicit operations**

You create `hypothesis_updates[]` entries with one of:
- `create`,
- `reprioritize`,
- `invalidate`,
- `merge`.

Each entry includes rationale, confidence delta, and evidence links.

If verdict is `rejected`, you must include:
- `rejection_reason`,
- at least one `next_hypothesis` direction (embedded in `hypothesis_updates`).

**Step 8 - Persist artifacts and set synthesis hint**

You write:
- experiment-level learnings artifact,
- updated hypothesis stack artifact.

You include canonical join keys: `experiment_id`, `source_hypothesis_id`, `flag_key` (if available), `metric_set_id`.

You set `pattern_synthesis_hint.include_in_next_portfolio_review` based on learning significance and novelty.

Source basis:
- https://docs.statsig.com/exp-templates/decision-framework
- https://docs.geteppo.com/experiment-analysis/configuration/protocols/
- https://www.statsig.com/blog/product-experimentation-best-practices
- https://launchdarkly.com/docs/guides/statistical-methodology/sample-ratios
- https://www.statsig.com/updates/update/related-experiments

### Draft: Tool Usage Syntax (Real Methods Only)

Use only documented runtime methods shown in existing strategist skills.

#### Activate required context

```python
flexus_policy_document(op="activate", args={"p": "/experiments/{experiment_id}/results"})
flexus_policy_document(op="activate", args={"p": "/experiments/{experiment_id}/spec"})
flexus_policy_document(op="activate", args={"p": "/strategy/hypothesis-stack"})
```

You call these before any verdict. If one call fails or returns missing content, you record a blocked codification outcome instead of continuing.

#### Discover related experiments for synthesis context

```python
flexus_policy_document(op="list", args={"p": "/experiments/"})
```

You use this to support portfolio pattern synthesis and to avoid duplicate hypothesis restarts that ignore previously rejected evidence.

#### Write experiment-level learning artifact

```python
write_artifact(
  artifact_type="experiment_learnings",
  path="/experiments/{experiment_id}/learnings",
  data={...}
)
```

You write exactly one canonical learning artifact per codification pass. If you rerun codification, increment `record_version` and preserve lineage in the artifact payload.

#### Write updated hypothesis stack artifact

```python
write_artifact(
  artifact_type="experiment_hypothesis_stack",
  path="/strategy/hypothesis-stack",
  data={...}
)
```

You write this after learning codification and only after `hypothesis_updates[]` are computed from evidence.

#### Tool usage discipline

You do not invent methods, endpoints, or hidden operations. You only use:
- `flexus_policy_document(op="activate", ...)`,
- `flexus_policy_document(op="list", ...)`,
- `write_artifact(...)`.

If persistence fails transiently, you retry according to platform policy; if it fails deterministically, you emit a blocked state and stop instead of silently dropping updates.

Source basis:
- Existing skill runtime usage in strategist and executor skill files
- https://developers.notion.com/reference/request-limits
- https://developer.atlassian.com/cloud/jira/platform/rate-limiting/
- https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
- https://support.airtable.com/docs/managing-api-call-limits-in-airtable

### Draft: Decision Rule and Outcome Taxonomy

You evaluate decision readiness with explicit policy logic. You do not reduce outcomes to win/loss only.

#### Decision rule skeleton

- If quality is invalid -> recommendation `do_not_rollout`, verdict `inconclusive`, reason `quality_invalid`.
- Else if success criteria pass and all guardrails pass no-harm criteria -> recommendation `rollout`, verdict `validated`.
- Else if deterioration is detected or guardrail harm fails policy -> recommendation `do_not_rollout`, verdict `rejected`.
- Else -> recommendation `discuss`, verdict `inconclusive`, reason either `insufficient_sensitivity` or `practically_null`.

#### Inconclusive subclass policy

You must assign one inconclusive reason:
- `insufficient_sensitivity`: sample or runtime is not enough to resolve planned effect.
- `practically_null`: estimate and interval indicate negligible business impact.
- `quality_invalid`: integrity failure blocks interpretation regardless of effect size.

You then define the next action:
- increase power / rerun,
- close as low-priority neutral,
- fix instrumentation and rerun.

This keeps inconclusive outcomes actionable instead of becoming dead-end records.

Source basis:
- https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics
- https://www.optimizely.com/insights/blog/understanding-and-implementing-guardrail-metrics
- https://docs.statsig.com/experiments-plus/sequential-testing/
- https://www.statsig.com/blog/product-experimentation-best-practices

### Draft: Organizational Learning and Portfolio Synthesis

You run this skill as part of a recurring operating system, not one-off reporting.

You execute two cadences:
- **weekly or bi-weekly closure cadence**: close open experiment learnings and apply hypothesis stack updates,
- **monthly portfolio synthesis cadence**: aggregate cross-experiment patterns, decide strategic reallocations, and prune stale hypotheses.

For monthly synthesis, you include:
- denominator metrics (`validated/rejected/inconclusive` counts),
- quality-invalid rate,
- repeated mechanism patterns by segment/channel/product area,
- recurring anti-pattern incidence,
- backlog recycle rate (how often rejected ideas reappear),
- median planned-vs-actual experiment duration.

You mark any experiment with high strategic novelty for mandatory inclusion in next monthly synthesis via `pattern_synthesis_hint`.

You preserve rejected outcomes as first-class evidence. A rejected hypothesis with clear mechanism evidence is a valid strategic asset and must be searchable.

Source basis:
- https://handbook.gitlab.com/handbook/product/groups/growth/#how-growth-launches-experiments
- https://docs.statsig.com/experimentation/meta-analysis
- https://www.statsig.com/updates/update/meta-analysisv0
- https://www.statsig.com/blog/experimental-meta-analysis-and-knowledge-base
- https://docs.geteppo.com/experiment-analysis/reporting/knowledge-base/

### Draft: Anti-Pattern Warning Blocks

#### Warning: Survivorship bias (file-drawer pattern)
- **Signal:** Archive mostly contains winners; null and rejected outcomes are missing or weakly documented.
- **Consequence:** You overestimate expected win rate and keep repeating previously disproven ideas.
- **Mitigation:** Require all-outcomes registry with denominator metrics before any strategic summary.

#### Warning: Missing rejected hypotheses
- **Signal:** `rejection_reason` is absent and rejected items later return under new labels.
- **Consequence:** Organizational memory erodes and experimentation velocity is wasted.
- **Mitigation:** Make `rejection_reason` and next hypothesis direction mandatory for all rejected outcomes.

#### Warning: Winner's curse (local overfitting)
- **Signal:** Largest observed uplifts systematically shrink during rollout or replication.
- **Consequence:** You over-allocate roadmap capacity to noisy winners.
- **Mitigation:** Apply shrinkage-aware interpretation and require confirmatory follow-up for top-impact claims.

#### Warning: Optional stopping / stop-on-significance
- **Signal:** Teams stop early after temporary significance in fixed-horizon designs.
- **Consequence:** False positives rise and effect sizes are inflated.
- **Mitigation:** Enforce predeclared stopping policy and record stop reason (`precision_reached`, `horizon_completed`, or policy-valid equivalent).

#### Warning: Multiplicity and segment fishing
- **Signal:** Many metric/segment comparisons produce isolated significant hits without correction.
- **Consequence:** Discovery false positive rate increases and roadmap quality drops.
- **Mitigation:** Treat non-preplanned segment findings as exploratory and require confirmatory reruns.

#### Warning: Ratio metric denominator trap
- **Signal:** Ratio looks improved while numerator or denominator dynamics hide deterioration.
- **Consequence:** Harmful changes can be shipped under misleading KPI movement.
- **Mitigation:** Always decompose ratio metrics into numerator and denominator behavior before verdict.

#### Warning: Guardrail misinterpretation
- **Signal:** "Guardrail not significant" is interpreted as "safe."
- **Consequence:** Silent harm slips into rollout decisions.
- **Mitigation:** Use explicit non-inferiority/no-harm criteria and require guardrail pass in decision rule.

#### Warning: SRM and assignment integrity ignored
- **Signal:** Sample ratio mismatch alerts or exposure anomalies are present but treated as minor.
- **Consequence:** Causal interpretation is invalid regardless of apparent uplift.
- **Mitigation:** Treat integrity failures as hard blockers and rerun only after root-cause fix.

#### Warning: HARKing and post-hoc hypothesis rewriting
- **Signal:** Hypothesis statement is modified after results are known without explicit annotation.
- **Consequence:** Learning appears stronger than evidence and cannot be audited.
- **Mitigation:** Preserve original hypothesis reference and log all post-hoc reinterpretations as exploratory.

#### Warning: Novelty effect and temporal drift
- **Signal:** Early uplift decays across days-since-exposure or time windows.
- **Consequence:** Short-term excitement is misread as durable impact.
- **Mitigation:** Record time-profile interpretation and include long-term risk notes for rollout decisions.

Source basis:
- https://www.statsig.com/blog/experimental-meta-analysis-and-knowledge-base
- https://www.amazon.science/publications/overcoming-the-winners-curse-leveraging-bayesian-inference-to-improve-estimates-of-the-impact-of-features-launched-via-a-b-tests
- https://arxiv.org/abs/2411.18569
- https://engineering.atspotify.com/2024/05/fixed-power-designs-its-not-if-you-peek-its-what-you-peek-at
- https://www.statsig.com/perspectives/multiple-comparisons-abtests-care
- https://www.optimizely.com/insights/blog/understanding-and-implementing-guardrail-metrics
- https://amplitude.com/docs/feature-experiment/troubleshooting/sample-ratio-mismatch
- https://www.statsig.com/blog/novelty-effects

### Draft: Decision Override Governance

You allow recommendation overrides only with explicit governance metadata. If your final decision differs from decision-rule recommendation, you must capture:
- who approved the override,
- why the override was necessary,
- which risk was accepted,
- what follow-up validation is required.

You never allow silent overrides. Silent overrides destroy comparability across experiments and make portfolio learning unreliable.

You mark override decisions for mandatory follow-up review in the next portfolio synthesis cycle.

Source basis:
- https://docs.statsig.com/exp-templates/decision-framework
- https://docs.geteppo.com/administration/recommended-decisions
- https://www.statsig.com/blog/organization-experiment-policy

### Draft: JSON Schema Fragment (Experiment Learnings v2)

```json
{
  "experiment_learnings": {
    "type": "object",
    "description": "Canonical codified learning artifact created after experiment readout and used for strategic memory.",
    "required": [
      "schema_version",
      "record_version",
      "experiment_id",
      "codified_at",
      "source_hypothesis_id",
      "source_result_ref",
      "decision_rule_evaluation",
      "quality_gate_status",
      "experiment_verdict",
      "mechanism_explanation",
      "generalizable_learnings",
      "hypothesis_updates",
      "decision_log",
      "confidence",
      "implications",
      "evidence_links",
      "lineage"
    ],
    "additionalProperties": false,
    "properties": {
      "schema_version": {
        "type": "string",
        "description": "Schema contract version for compatibility and migration policy."
      },
      "record_version": {
        "type": "integer",
        "minimum": 1,
        "description": "Monotonic version number of this artifact record for reruns and corrections."
      },
      "experiment_id": {
        "type": "string",
        "description": "Stable experiment identifier from the experimentation control plane."
      },
      "codified_at": {
        "type": "string",
        "format": "date-time",
        "description": "Timestamp when learning codification was completed."
      },
      "source_hypothesis_id": {
        "type": "string",
        "description": "Identifier of the hypothesis that originated this experiment."
      },
      "flag_key": {
        "type": ["string", "null"],
        "description": "Feature flag key when experiment is tied to a flag; null when not applicable."
      },
      "metric_set_id": {
        "type": ["string", "null"],
        "description": "Reference to the metric set/policy used for decision evaluation."
      },
      "source_result_ref": {
        "type": "object",
        "description": "Pointer to analysis outputs used as evidence for codification.",
        "required": [
          "artifact_path",
          "analysis_run_id",
          "analyzed_at"
        ],
        "additionalProperties": false,
        "properties": {
          "artifact_path": {
            "type": "string",
            "description": "Path to the result artifact consumed during codification."
          },
          "analysis_run_id": {
            "type": "string",
            "description": "Identifier of the specific analysis execution."
          },
          "analyzed_at": {
            "type": "string",
            "format": "date-time",
            "description": "Timestamp when the source analysis was generated."
          },
          "result_hash": {
            "type": ["string", "null"],
            "description": "Optional checksum to detect source-result mutation."
          }
        }
      },
      "decision_rule_evaluation": {
        "type": "object",
        "description": "Structured outcome of decision policy evaluation across metric classes.",
        "required": [
          "inference_mode",
          "recommendation",
          "recommendation_rationale"
        ],
        "additionalProperties": false,
        "properties": {
          "inference_mode": {
            "type": "string",
            "enum": [
              "frequentist_sequential",
              "frequentist_fixed_horizon",
              "bayesian",
              "mixed"
            ],
            "description": "Inference framework used to interpret this result; prevents cross-mode misreads."
          },
          "recommendation": {
            "type": "string",
            "enum": [
              "rollout",
              "do_not_rollout",
              "discuss"
            ],
            "description": "Decision-rule recommendation before human override."
          },
          "recommendation_rationale": {
            "type": "string",
            "description": "Human-readable rationale grounded in metric and quality evidence."
          },
          "success_metrics_summary": {
            "type": "array",
            "description": "Per-success-metric summary needed for downstream audit and synthesis.",
            "items": {
              "type": "object",
              "required": [
                "metric_id",
                "direction",
                "effect_estimate"
              ],
              "additionalProperties": false,
              "properties": {
                "metric_id": {
                  "type": "string",
                  "description": "Metric identifier from experiment configuration."
                },
                "direction": {
                  "type": "string",
                  "enum": [
                    "improved",
                    "neutral",
                    "regressed"
                  ],
                  "description": "Observed directional movement under policy interpretation."
                },
                "effect_estimate": {
                  "type": "number",
                  "description": "Estimated relative effect used for recommendation."
                },
                "interval_lower": {
                  "type": ["number", "null"],
                  "description": "Lower confidence/credible interval bound when available."
                },
                "interval_upper": {
                  "type": ["number", "null"],
                  "description": "Upper confidence/credible interval bound when available."
                },
                "p_value": {
                  "type": ["number", "null"],
                  "description": "Adjusted p-value when frequentist outputs are available."
                }
              }
            }
          },
          "guardrail_metrics_summary": {
            "type": "array",
            "description": "Per-guardrail no-harm or non-inferiority status used in decision policy.",
            "items": {
              "type": "object",
              "required": [
                "metric_id",
                "status"
              ],
              "additionalProperties": false,
              "properties": {
                "metric_id": {
                  "type": "string",
                  "description": "Guardrail metric identifier."
                },
                "status": {
                  "type": "string",
                  "enum": [
                    "pass",
                    "fail",
                    "unknown"
                  ],
                  "description": "Policy status of guardrail under configured no-harm rule."
                },
                "notes": {
                  "type": ["string", "null"],
                  "description": "Optional explanation of edge-case interpretation."
                }
              }
            }
          }
        }
      },
      "quality_gate_status": {
        "type": "object",
        "description": "Integrity checks that determine whether causal interpretation is valid.",
        "required": [
          "is_valid",
          "blockers",
          "srm_detected"
        ],
        "additionalProperties": false,
        "properties": {
          "is_valid": {
            "type": "boolean",
            "description": "True only when all quality gates pass."
          },
          "blockers": {
            "type": "array",
            "description": "List of integrity blockers discovered during codification.",
            "items": {
              "type": "string",
              "enum": [
                "sample_ratio_mismatch",
                "instrumentation_error",
                "variant_jumping",
                "exposure_mismatch",
                "missing_tracking",
                "identity_contamination",
                "other"
              ]
            }
          },
          "srm_detected": {
            "type": "boolean",
            "description": "Whether SRM was detected by platform checks or internal diagnostics."
          },
          "srm_p_value": {
            "type": ["number", "null"],
            "description": "SRM test p-value when available; null when not computed."
          },
          "notes": {
            "type": ["string", "null"],
            "description": "Optional details about quality diagnostics and remediation."
          }
        }
      },
      "experiment_verdict": {
        "type": "string",
        "enum": [
          "validated",
          "rejected",
          "inconclusive"
        ],
        "description": "Final codified verdict after applying quality and decision rules."
      },
      "inconclusive_reason": {
        "type": ["string", "null"],
        "enum": [
          "insufficient_sensitivity",
          "practically_null",
          "quality_invalid",
          null
        ],
        "description": "Required subclass when verdict is inconclusive; null otherwise."
      },
      "mechanism_explanation": {
        "type": "string",
        "description": "Explanation of likely causal mechanism behind the observed outcome."
      },
      "generalizable_learnings": {
        "type": "array",
        "description": "Transferable learning claims derived from this experiment.",
        "items": {
          "type": "object",
          "required": [
            "statement",
            "scope",
            "confidence"
          ],
          "additionalProperties": false,
          "properties": {
            "statement": {
              "type": "string",
              "description": "Concrete learning statement suitable for reuse."
            },
            "scope": {
              "type": "string",
              "description": "Where the learning is expected to apply, including known boundaries."
            },
            "confidence": {
              "type": "string",
              "enum": [
                "high",
                "medium",
                "low"
              ],
              "description": "Confidence level assigned to this learning claim."
            }
          }
        }
      },
      "rejection_reason": {
        "type": ["string", "null"],
        "description": "Required explanation when verdict is rejected; null otherwise."
      },
      "hypothesis_updates": {
        "type": "array",
        "description": "Operations applied to the hypothesis stack as a result of codified learning.",
        "items": {
          "type": "object",
          "required": [
            "operation",
            "hypothesis_id",
            "statement",
            "category",
            "priority_after",
            "confidence_delta",
            "rationale"
          ],
          "additionalProperties": false,
          "properties": {
            "operation": {
              "type": "string",
              "enum": [
                "create",
                "reprioritize",
                "invalidate",
                "merge"
              ],
              "description": "Type of hypothesis stack transition."
            },
            "hypothesis_id": {
              "type": "string",
              "description": "Identifier of affected hypothesis (new or existing)."
            },
            "statement": {
              "type": "string",
              "description": "Hypothesis text after this operation."
            },
            "category": {
              "type": "string",
              "enum": [
                "market",
                "product",
                "channel",
                "pricing"
              ],
              "description": "Hypothesis domain category for stack organization."
            },
            "priority_before": {
              "type": ["string", "null"],
              "enum": [
                "p0",
                "p1",
                "p2",
                "p3",
                null
              ],
              "description": "Priority before operation; null for newly created hypotheses."
            },
            "priority_after": {
              "type": "string",
              "enum": [
                "p0",
                "p1",
                "p2",
                "p3"
              ],
              "description": "Priority after operation."
            },
            "confidence_delta": {
              "type": "number",
              "description": "Signed change in confidence resulting from evidence in this experiment."
            },
            "rationale": {
              "type": "string",
              "description": "Reason for this update linked to experiment evidence."
            }
          }
        }
      },
      "decision_log": {
        "type": "object",
        "description": "First-class decision record bridging analysis output and execution governance.",
        "required": [
          "decision",
          "decided_by",
          "decided_at",
          "override_of_recommendation"
        ],
        "additionalProperties": false,
        "properties": {
          "decision": {
            "type": "string",
            "enum": [
              "rollout",
              "hold",
              "do_not_rollout",
              "rerun"
            ],
            "description": "Final human decision after considering recommendation and constraints."
          },
          "decided_by": {
            "type": "array",
            "description": "Identifiers of decision owners/approvers.",
            "items": {
              "type": "string"
            }
          },
          "decided_at": {
            "type": "string",
            "format": "date-time",
            "description": "Timestamp of final decision."
          },
          "override_of_recommendation": {
            "type": "boolean",
            "description": "True when final decision differs from policy recommendation."
          },
          "override_reason": {
            "type": ["string", "null"],
            "description": "Mandatory explanation when override_of_recommendation is true."
          }
        }
      },
      "confidence": {
        "type": "object",
        "description": "Structured uncertainty representation to support downstream filtering and governance.",
        "required": [
          "level",
          "method",
          "interval_summary"
        ],
        "additionalProperties": false,
        "properties": {
          "level": {
            "type": "string",
            "enum": [
              "high",
              "medium",
              "low"
            ],
            "description": "Final confidence label used for prioritization and synthesis."
          },
          "method": {
            "type": "string",
            "enum": [
              "frequentist",
              "bayesian",
              "mixed"
            ],
            "description": "Uncertainty framework used to derive confidence."
          },
          "interval_summary": {
            "type": "string",
            "description": "Compact interval interpretation supporting audit and human review."
          },
          "chance_to_beat_control": {
            "type": ["number", "null"],
            "description": "Bayesian posterior probability of outperforming control when available."
          },
          "expected_loss": {
            "type": ["number", "null"],
            "description": "Bayesian expected loss under rollout when available."
          },
          "notes": {
            "type": ["string", "null"],
            "description": "Optional context on confidence caveats."
          }
        }
      },
      "implications": {
        "type": "array",
        "description": "Actionable implications split by domain for strategic planning.",
        "items": {
          "type": "object",
          "required": [
            "domain",
            "summary",
            "confidence"
          ],
          "additionalProperties": false,
          "properties": {
            "domain": {
              "type": "string",
              "enum": [
                "strategy",
                "product",
                "go_to_market",
                "measurement",
                "operations"
              ],
              "description": "Business domain affected by this learning."
            },
            "summary": {
              "type": "string",
              "description": "Concrete implication statement for this domain."
            },
            "confidence": {
              "type": "string",
              "enum": [
                "high",
                "medium",
                "low"
              ],
              "description": "Confidence in this implication."
            }
          }
        }
      },
      "evidence_links": {
        "type": "array",
        "description": "Typed evidence references used to support and audit codified learning.",
        "items": {
          "type": "object",
          "required": [
            "type",
            "uri",
            "relation",
            "captured_at"
          ],
          "additionalProperties": false,
          "properties": {
            "type": {
              "type": "string",
              "enum": [
                "result_dashboard",
                "spec_doc",
                "analysis_notebook",
                "decision_record",
                "postmortem",
                "external_reference"
              ],
              "description": "Evidence artifact class."
            },
            "uri": {
              "type": "string",
              "format": "uri",
              "description": "Location of evidence artifact."
            },
            "relation": {
              "type": "string",
              "enum": [
                "supports",
                "contradicts",
                "context"
              ],
              "description": "How this evidence relates to the codified claim."
            },
            "captured_at": {
              "type": "string",
              "format": "date-time",
              "description": "Timestamp when evidence reference was captured."
            },
            "checksum_sha256": {
              "type": ["string", "null"],
              "description": "Optional checksum for immutable evidence validation."
            }
          }
        }
      },
      "lineage": {
        "type": "object",
        "description": "Lineage metadata connecting this learning artifact to upstream and sibling records.",
        "required": [
          "parent_learning_ids",
          "dataset_versions"
        ],
        "additionalProperties": false,
        "properties": {
          "parent_learning_ids": {
            "type": "array",
            "description": "Identifiers of prior learning artifacts directly referenced in synthesis.",
            "items": {
              "type": "string"
            }
          },
          "dataset_versions": {
            "type": "array",
            "description": "Version identifiers for datasets used in upstream analysis.",
            "items": {
              "type": "string"
            }
          },
          "source_code_ref": {
            "type": ["string", "null"],
            "description": "Optional code revision reference for reproducibility."
          }
        }
      },
      "pattern_synthesis_hint": {
        "type": "object",
        "description": "Metadata that helps schedulers include this artifact in batch learning reviews.",
        "required": [
          "include_in_next_portfolio_review"
        ],
        "additionalProperties": false,
        "properties": {
          "include_in_next_portfolio_review": {
            "type": "boolean",
            "description": "True when this learning should be reviewed in the immediate next synthesis cycle."
          },
          "reason": {
            "type": ["string", "null"],
            "description": "Optional reason for forced inclusion."
          }
        }
      }
    }
  }
}
```

### Draft: JSON Schema Fragment (Hypothesis Stack v2)

```json
{
  "experiment_hypothesis_stack": {
    "type": "object",
    "description": "Current strategic hypothesis stack updated by experiment learning operations.",
    "required": [
      "schema_version",
      "updated_at",
      "hypotheses"
    ],
    "additionalProperties": false,
    "properties": {
      "schema_version": {
        "type": "string",
        "description": "Schema version for hypothesis stack artifact."
      },
      "updated_at": {
        "type": "string",
        "format": "date-time",
        "description": "Timestamp of most recent stack update."
      },
      "hypotheses": {
        "type": "array",
        "description": "Active and archived hypotheses with evidence-backed status and priority.",
        "items": {
          "type": "object",
          "required": [
            "hypothesis_id",
            "statement",
            "category",
            "status",
            "priority",
            "last_updated_at",
            "evidence_refs"
          ],
          "additionalProperties": false,
          "properties": {
            "hypothesis_id": {
              "type": "string",
              "description": "Stable identifier for hypothesis traceability."
            },
            "statement": {
              "type": "string",
              "description": "Current hypothesis statement used for planning."
            },
            "category": {
              "type": "string",
              "enum": [
                "market",
                "product",
                "channel",
                "pricing"
              ],
              "description": "Hypothesis domain category."
            },
            "status": {
              "type": "string",
              "enum": [
                "active",
                "validated",
                "rejected",
                "archived"
              ],
              "description": "Current lifecycle status of the hypothesis."
            },
            "priority": {
              "type": "string",
              "enum": [
                "p0",
                "p1",
                "p2",
                "p3"
              ],
              "description": "Current execution priority in strategic backlog."
            },
            "last_updated_at": {
              "type": "string",
              "format": "date-time",
              "description": "Timestamp of last evidence-backed update."
            },
            "evidence_refs": {
              "type": "array",
              "description": "List of learning artifact IDs supporting this hypothesis status.",
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

Source basis:
- https://json-schema.org/draft/2020-12
- https://openlineage.io/docs/spec/
- https://raw.githubusercontent.com/cloudevents/spec/v1.0/spec.md
- https://opentelemetry.io/docs/specs/semconv/feature-flags/feature-flags-events/
- https://openfeature.dev/specification/sections/flag-evaluation/

### Draft: "Do Not Do This" Rules (Paste-Ready)

You do not do any of the following:

- You do not publish a final verdict when `quality_gate_status.is_valid` is false.
- You do not treat `p > 0.05` on guardrails as equivalent to "safe."
- You do not collapse all unresolved outcomes into one generic `inconclusive` label.
- You do not drop rejected hypotheses without storing explicit rejection mechanism and follow-up direction.
- You do not update hypothesis priorities without evidence links and rationale.
- You do not archive only wins; all valid outcomes must be retained for portfolio memory.
- You do not introduce undocumented methods or hidden tool calls in this skill.

If any of these violations occur, you write the learning artifact as policy-invalid and require remediation before strategic use.

---

## Gaps & Uncertainties

- No single public industry standard defines the exact minimum number of experiments required before meta-analysis is reliable; guidance varies by context and metric volatility.
- Vendor documentation quality is high for platform usage but uneven for deep statistical internals; some implementation details remain black-box.
- Public benchmarks for non-inferiority margin selection in product guardrails are sparse; margin policy is usually domain-specific.
- Cross-platform entity semantics remain inconsistent (`experiment`, `flag`, `rule`, `layer`), so internal canonical mapping design still requires local decisions.
- Open-source/public case studies are biased toward notable incidents and may overrepresent failure extremes relative to normal operations.
- Several standards used in schema recommendations (CloudEvents, JSON Schema 2020-12) are older than 2024; they are intentionally included as evergreen interoperability foundations.
- There is no universal policy mapping for Bayesian outputs (for example, expected loss thresholds) into a single cross-industry ship/no-ship rule; local policy is still required.
- Several source-backed operational constraints (rate limits, write behavior) vary by plan tier and require implementation-time confirmation in the target workspace.
