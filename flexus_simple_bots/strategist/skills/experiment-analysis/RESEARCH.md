# Research: experiment-analysis

**Skill path:** `strategist/skills/experiment-analysis/`
**Bot:** strategist (researcher | strategist | executor)
**Research date:** 2026-03-04
**Status:** complete

---

## Context

`experiment-analysis` is the strategist skill for post-run experiment decisioning: read completed results, validate data quality, run statistical interpretation, and output a clear verdict (`ship`, `do_not_ship`, `inconclusive`, `blocked_by_guardrail`).

The current `SKILL.md` already enforces core discipline (pre-registered sample/date checks, no HARKing, significance + guardrails, structured artifact). This research expands it with 2024-2026 practitioner patterns: decision frameworks (not metric-only readouts), sequential-valid inference for continuous monitoring, Bayesian risk-aware interpretation, SRM-first trust gates, and cross-platform schema grounding from real APIs/docs.

For sources without explicit publication year, this document treats the referenced vendor docs as "current documentation accessed on 2026-03-04"; older non-current references are explicitly marked as evergreen.

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

- [x] No generic filler without concrete backing
- [x] No invented tool names, method IDs, or API endpoints — only verified real ones
- [x] Contradictions between sources are explicitly noted, not silently resolved
- [x] Volume: findings sections are within 800–4000 words combined
- [x] Volume: `Draft Content for SKILL.md` is longer than all Findings sections combined

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

1. **Mature teams now use explicit decision frameworks, not ad-hoc interpretation.**  
   Modern workflows encode outcomes such as `ship / rollback / review` with predeclared logic that combines primary metrics, guardrails, and quality checks. GrowthBook Decision Framework and Statsig ship decision guidance both reflect this operational style.  
   Sources: https://docs.growthbook.io/app/experiment-decisions, https://www.statsig.com/updates/update/ship-decision-framework

2. **A health/trust gate is typically run before any statistical interpretation.**  
   SRM, assignment integrity, multiple-exposure anomalies, and missing-data checks are treated as blocking conditions in several platforms. This means "analyze first, debug later" is no longer acceptable in robust experimentation programs.  
   Sources: https://docs.growthbook.io/app/experiment-results, https://docs.geteppo.com/quick-starts/analysis-integration/creating-experiment-analysis/

3. **Frequentist practice has shifted from p-value-only to effect-plus-uncertainty reporting.**  
   LaunchDarkly and Statsig documentation emphasize interval interpretation and effect direction; significance without practical magnitude is treated as insufficient for a product call.  
   Sources: https://docs.launchdarkly.com/home/experimentation/frequentist-results, https://docs.statsig.com/experiments/interpreting-results/read-results

4. **Power/MDE readiness is now an operational decision gate.**  
   Teams increasingly classify outcomes as "underpowered/inconclusive" if precision targets are not met, even when directional trends exist. This directly affects whether a winner call is allowed.  
   Sources: https://docs.geteppo.com/statistics/sample-size-calculator/mde, https://docs.growthbook.io/app/experiment-decisions

5. **Multiple testing control is first-class in frequentist production workflows.**  
   Optimizely describes tiered Benjamini-Hochberg FDR control and warns segmented reads are exploratory; Statsig provides BH methodology docs. This makes correction scope a required interpretation input, not an optional afterthought.  
   Sources: https://support.optimizely.com/hc/en-us/articles/4410283967245-False-discovery-rate-control, https://docs.statsig.com/stats-engine/methodologies/benjamini-hochberg-procedure

6. **Sequential monitoring is accepted only with always-valid/corrected inference.**  
   Vendor guidance converges on: continuous peeking is acceptable only when using sequential methods (e.g., mSPRT/GAVI-style) rather than fixed-horizon p-values.  
   Sources: https://docs.statsig.com/experiments/advanced-setup/sequential-testing, https://launchdarkly.com/docs/guides/statistical-methodology/methodology-frequentist

7. **Bayesian analysis in product tools is thresholded and increasingly risk-aware.**  
   Probability-to-win or probability-to-be-best is commonly shown, but leading practice also surfaces expected loss/downside risk to avoid over-shipping on probability alone.  
   Sources: https://docs.launchdarkly.com/home/experimentation/bayesian-results, https://docs.growthbook.io/app/experiment-results

8. **Guardrails are formalized as do-no-harm/non-inferiority constraints.**  
   Spotify's risk-aware framework and GrowthBook do-no-harm framing both support the same operational pattern: positive primary effect does not overrule materially degraded guardrails.  
   Sources: https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics, https://arxiv.org/abs/2402.11609, https://docs.growthbook.io/app/experiment-decisions

9. **Variance reduction (CUPED-family) is now mainstream and changes interpretation quality.**  
   GrowthBook and Statsig both document and evolve CUPED behavior; this materially impacts uncertainty width and time-to-decision, so analysis output should explicitly record whether VR was used.  
   Sources: https://blog.growthbook.io/bayesian-model-updates-in-growthbook-3-0/, https://docs.statsig.com/stats-engine/methodologies/cuped/, https://www.statsig.com/updates/update/cuped-for-ratio-metrics

**Sources:**
- https://docs.growthbook.io/app/experiment-decisions
- https://docs.growthbook.io/app/experiment-results
- https://www.statsig.com/updates/update/ship-decision-framework
- https://docs.statsig.com/experiments/interpreting-results/read-results
- https://docs.statsig.com/experiments/advanced-setup/sequential-testing
- https://docs.statsig.com/stats-engine/methodologies/benjamini-hochberg-procedure
- https://docs.statsig.com/stats-engine/methodologies/cuped/
- https://www.statsig.com/updates/update/cuped-for-ratio-metrics
- https://docs.launchdarkly.com/home/experimentation/frequentist-results
- https://docs.launchdarkly.com/home/experimentation/bayesian-results
- https://launchdarkly.com/docs/guides/statistical-methodology/methodology-frequentist
- https://support.optimizely.com/hc/en-us/articles/4410283967245-False-discovery-rate-control
- https://docs.geteppo.com/statistics/sample-size-calculator/mde
- https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics
- https://arxiv.org/abs/2402.11609
- https://blog.growthbook.io/bayesian-model-updates-in-growthbook-3-0/

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

1. **The de-facto stack is multi-vendor, with no single universal result model.**  
   Statsig, Optimizely, LaunchDarkly, Amplitude Experiment, GrowthBook, Eppo, PostHog, and VWO all expose experiment analysis, but with different statistical defaults and API surface depth.

2. **Statsig is strong on sequential + warehouse-native integration.**  
   Public docs show SPRT/sequential methodology, SRM checks, and API/warehouse export surfaces; some capabilities are plan-gated (notably advanced export paths).  
   Sources: https://docs.statsig.com/experiments/advanced-setup/sprt, https://docs.statsig.com/experiments/monitoring/srm, https://docs.statsig.com/console-api/experiments, https://docs.statsig.com/experiments/interpreting-results/access-whn

3. **Optimizely remains strong on mature frequentist engine and FDR controls, with caveats.**  
   Stats Engine and FDR controls are well documented, but segmented views are explicitly described as outside strict FDR guarantees; event export also has environment/region constraints.  
   Sources: https://support.optimizely.com/hc/en-us/articles/4410284008461-Stats-Engine, https://support.optimizely.com/hc/en-us/articles/4410283967245-False-discovery-rate-control, https://docs.developers.optimizely.com/experimentation-data/docs/experimentation-events-export

4. **LaunchDarkly supports both frequentist and Bayesian modes with SRM and CUPED, but API details are version-sensitive.**  
   Experimentation docs cover methodological options and health checks; experimentation API is documented with beta/versioning constraints in public references.  
   Sources: https://launchdarkly.com/docs/guides/statistical-methodology/methodology-frequentist, https://launchdarkly.com/docs/guides/statistical-methodology/methodology-bayesian, https://launchdarkly.com/docs/guides/statistical-methodology/sample-ratios, https://launchdarkly.com/docs/api/experiments

5. **Amplitude Experiment emphasizes sequential inference and broad API family, but result extraction may require composition.**  
   Docs provide management/evaluation/export APIs and SRM guidance, but users often need to join experiment management metadata with analytics export outputs for full reporting.  
   Sources: https://amplitude.com/docs/feature-experiment/under-the-hood/experiment-sequential-testing, https://www.docs.developers.amplitude.com/docs/apis/experiment/experiment-management-api, https://amplitude.com/docs/apis/analytics/export, https://amplitude.com/docs/feature-experiment/troubleshooting/sample-ratio-mismatch

6. **GrowthBook and Eppo are notably explicit in diagnostics and analysis controls.**  
   GrowthBook documents results, decision criteria, SRM checks, and results API. Eppo documents frequentist/always-valid/Bayesian options, diagnostics, and webhooks/API integration.  
   Sources: https://docs.growthbook.io/app/experiment-results, https://docs.growthbook.io/api/, https://docs.geteppo.com/statistics/, https://docs.geteppo.com/experiment-analysis/diagnostics/, https://docs.geteppo.com/reference/api

7. **PostHog and VWO are important alternatives with different strengths.**  
   PostHog leans heavily Bayesian in documentation and offers experiment API endpoints; VWO SmartStats positioning highlights Bayesian-powered sequential workflows and strong operational guardrails in product messaging/docs.  
   Sources: https://posthog.com/docs/experiments/statistics, https://posthog.com/docs/api/experiments, https://vwo.com/product-updates/enhanced-vwo-smartstats/, https://vwo.com/blog/new-stats-engine-and-enhanced-vwo-reports/

8. **Cross-platform reality: capabilities are often plan-gated and tenant-specific.**  
   API access breadth, export features, and monitoring depth can vary by plan/region/server setup; this must be represented explicitly in any skill-level tool recommendation.

**Comparative matrix (high-level):**

| Tool | Analysis paradigm | Guardrails | Monitoring/alerts | API/export | Noted limitations |
|---|---|---|---|---|---|
| Statsig | Frequentist + sequential (SPRT), CUPED | Supported | SRM, experiment health monitoring | Console API + warehouse-native exports | Some exports/features are plan-gated |
| Optimizely | Frequentist Stats Engine + FDR | Primary/secondary/monitoring structure | SRM/quality checks | APIs + events export | Segmented views not under strict FDR; export constraints by environment |
| LaunchDarkly | Frequentist + Bayesian + CUPED | Release guardrails/metric groups docs | SRM + health checks | Experiments API (versioned/beta nuances) | Endpoint behavior may vary by API version/tenant |
| Amplitude | Sequential-centric experimentation | Secondary/guarding metric usage | SRM troubleshooting and analysis tools | Mgmt API + eval API + analytics export | Full result reconstruction may require joins |
| GrowthBook | Frequentist + Bayesian + CUPEDps | Explicit guardrail handling | SRM and health checks | Results API documented | Some advanced methods/features plan dependent |
| Eppo | Frequentist + always-valid + Bayesian + CUPED++ | Supported | Diagnostics + alerting | REST API + webhooks | Warehouse integration workflow complexity |
| PostHog | Bayesian-first docs + practical result analysis | Secondary metrics pattern | Result interpretation views | Experiment CRUD APIs | Public docs less explicit on dedicated computed-result endpoint |
| VWO | Bayesian-powered sequential SmartStats (+ fixed horizon options) | Guardrail threshold workflows | Experiment vitals style checks | REST + storage integrations | Enterprise gating for some data export paths |

**Sources:**
- https://docs.statsig.com/experiments/advanced-setup/sprt
- https://docs.statsig.com/experiments/monitoring/srm
- https://docs.statsig.com/console-api/experiments
- https://docs.statsig.com/experiments/interpreting-results/access-whn
- https://support.optimizely.com/hc/en-us/articles/4410284008461-Stats-Engine
- https://support.optimizely.com/hc/en-us/articles/4410283967245-False-discovery-rate-control
- https://docs.developers.optimizely.com/experimentation-data/docs/experimentation-events-export
- https://launchdarkly.com/docs/guides/statistical-methodology/methodology-frequentist
- https://launchdarkly.com/docs/guides/statistical-methodology/methodology-bayesian
- https://launchdarkly.com/docs/guides/statistical-methodology/sample-ratios
- https://launchdarkly.com/docs/api/experiments
- https://amplitude.com/docs/feature-experiment/under-the-hood/experiment-sequential-testing
- https://amplitude.com/docs/feature-experiment/troubleshooting/sample-ratio-mismatch
- https://www.docs.developers.amplitude.com/docs/apis/experiment/experiment-management-api
- https://amplitude.com/docs/apis/analytics/export
- https://docs.growthbook.io/app/experiment-results
- https://docs.growthbook.io/api/
- https://docs.geteppo.com/statistics/
- https://docs.geteppo.com/experiment-analysis/diagnostics/
- https://docs.geteppo.com/reference/api
- https://posthog.com/docs/experiments/statistics
- https://posthog.com/docs/api/experiments
- https://vwo.com/product-updates/enhanced-vwo-smartstats/
- https://vwo.com/blog/new-stats-engine-and-enhanced-vwo-reports/

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

1. **p-value is an incompatibility measure, not "probability the hypothesis is true."**  
   The ASA statement remains foundational (evergreen), and modern product docs reinforce combining significance with effect size and uncertainty.  
   Sources: https://amstat.org/docs/default-source/amstat-documents/p-valuestatement.pdf (evergreen), https://docs.launchdarkly.com/home/experimentation/frequentist-results

2. **CI interpretation is operationally central in frequentist decisioning.**  
   In common product UIs, whether interval spans zero is more decision-useful than p-value alone; practical significance still must be checked separately.  
   Sources: https://docs.launchdarkly.com/home/experimentation/frequentist-results, https://www.itl.nist.gov/div898/handbook/prc/section2/prc221.htm (evergreen)

3. **Bayesian interpretation should include probability plus downside risk.**  
   Probability-to-be-best/beat-control is not enough by itself in multi-variant settings; expected loss/risk improves decision quality.  
   Sources: https://docs.launchdarkly.com/home/experimentation/bayesian-results, https://docs.launchdarkly.com/home/experimentation/analyze/

4. **Power and MDE planning define whether non-significance is interpretable.**  
   Without planned power, "no significance" often means insufficient information rather than true null effect.  
   Sources: https://www.optimizely.com/insights/blog/power-analysis-in-fixed-horizon-frequentist-ab-tests/, https://launchdarkly.com/docs/home/experimentation/size

5. **Practical significance is a separate gate from statistical significance.**  
   Teams should compare observed effect against business materiality thresholds, not merely against alpha.  
   Sources: https://www.optimizely.com/insights/blog/power-analysis-in-fixed-horizon-frequentist-ab-tests/, https://amstat.org/docs/default-source/amstat-documents/p-valuestatement.pdf (evergreen)

6. **Guardrails are interpreted as explicit risk constraints in mature frameworks.**  
   Spotify/Confidence formulations show that passing primary uplift does not justify shipping if guardrails violate non-inferiority or deterioration thresholds.  
   Sources: https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics/, https://confidence.spotify.com/blog/better-decisions-with-guardrails, https://arxiv.org/abs/2402.11609

7. **Multiple comparisons and segmentation strongly inflate false discoveries without correction.**  
   Practical docs provide concrete inflation examples; deep slicing should be treated as exploratory unless pre-registered/corrected.  
   Sources: https://docs.growthbook.io/using/experimentation-problems, https://docs.launchdarkly.com/guides/statistical-methodology/mcc, https://docs.growthbook.io/statistics/multiple-corrections

8. **SRM is a validity gate, not just another metric.**  
   Platform guidance converges on halting interpretation until mismatch causes are diagnosed; thresholding differs across ecosystems and should be standardized per org policy.  
   Sources: https://launchdarkly.com/docs/home/experimentation/health-checks, https://docs.launchdarkly.com/guides/statistical-methodology/sample-ratios, https://developer.harness.io/docs/feature-management-experimentation/experimentation/experiment-results/analyzing-experiment-results/sample-ratio-check, https://www.lukasvermeer.nl/srm/docs/faq/

**Practical thresholds & decision rules (source-backed, context-sensitive):**

| Topic | Common threshold/range | Caveat |
|---|---|---|
| Alpha (`alpha`) | 0.05 is common default | Not universal; set by risk tolerance |
| Power target | 80% commonly recommended | Requires realistic MDE and traffic estimates |
| CI significance heuristic | Interval excludes 0 | Must align with test mode and correction scope |
| Bayesian winner threshold | Often policy-defined (e.g., 90-95%) | No universal value; needs explicit risk policy |
| SRM alerting | Commonly strict (e.g., p<0.01 to p<0.001 ranges across docs) | Thresholds vary by platform/policy |
| Segment readouts | Exploratory unless pre-registered/corrected | High false-positive risk in post-hoc slicing |

**Sources:**
- https://amstat.org/docs/default-source/amstat-documents/p-valuestatement.pdf (evergreen)
- https://www.itl.nist.gov/div898/handbook/prc/section2/prc221.htm (evergreen)
- https://docs.launchdarkly.com/home/experimentation/frequentist-results
- https://docs.launchdarkly.com/home/experimentation/bayesian-results
- https://docs.launchdarkly.com/home/experimentation/analyze/
- https://launchdarkly.com/docs/home/experimentation/size
- https://docs.launchdarkly.com/guides/statistical-methodology/mcc
- https://docs.launchdarkly.com/guides/statistical-methodology/sample-ratios
- https://launchdarkly.com/docs/home/experimentation/health-checks
- https://www.optimizely.com/insights/blog/power-analysis-in-fixed-horizon-frequentist-ab-tests/
- https://docs.growthbook.io/statistics/multiple-corrections
- https://docs.growthbook.io/using/experimentation-problems
- https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics/
- https://confidence.spotify.com/blog/better-decisions-with-guardrails
- https://arxiv.org/abs/2402.11609
- https://developer.harness.io/docs/feature-management-experimentation/experimentation/experiment-results/analyzing-experiment-results/sample-ratio-check
- https://www.lukasvermeer.nl/srm/docs/faq/

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

1. **Peeking/optional stopping remains a top false-positive driver under fixed-horizon methods.**  
   Continuous checking without sequential-valid inference inflates Type I error and creates fake winners.  
   Sources: https://optimizely.com/insights/blog/statistics-for-the-internet-age-the-story-behind-optimizelys-new-stats-engine (evergreen), https://www.statsig.com/perspectives/sequential-testing-ab-peek

2. **Longitudinal "peeking problem 2.0" is distinct from classic optional stopping.**  
   Open-ended metrics can still break nominal error control unless covariance/information accrual is modeled correctly.  
   Sources: https://engineering.atspotify.com/2023/07/bringing-sequential-testing-to-experiments-with-longitudinal-data-part-1-the-peeking-problem-2-0 (evergreen), https://engineering.atspotify.com/2023/07/bringing-sequential-testing-to-experiments-with-longitudinal-data-part-2-sequential-testing (evergreen)

3. **P-hacking/HARKing are governance failures, not just statistical accidents.**  
   Pre-analysis plans and strict confirmatory vs exploratory separation are practical controls; recent evidence on prevalence is mixed by context.  
   Sources: https://econpapers.repec.org/paper/zbwi4rdps/101.htm, https://doi.org/10.1287/isre.2024.0872, https://pubmed.ncbi.nlm.nih.gov/15647155/ (evergreen)

4. **SRM often indicates deep validity issues (assignment, execution, logging, interference).**  
   Industry case studies show SRM can completely reverse conclusions after root-cause fixes.  
   Sources: https://exp-platform.com/Documents/2019_KDDFabijanGupchupFuptaOmhoverVermeerDmitriev.pdf (evergreen), https://docs.statsig.com/guides/srm

5. **Metric definition drift causes contradictory decisions across teams/tools.**  
   When metric semantics diverge (filters, denominator definitions, stale transformations), statistically "correct" analyses can still be decision-wrong.  
   Sources: https://www.uber.com/en-GB/blog/umetric/, https://docs.geteppo.com/experiment-analysis/configuration/protocols/

6. **Instrumentation/telemetry issues can mimic treatment effects.**  
   Logging reliability asymmetry can create pseudo-lift or pseudo-regression; A/A monitoring remains an important guardrail.  
   Sources: https://arxiv.org/abs/1903.12470 (evergreen), https://docs.statsig.com/experiments/types/aa-test, https://www.exp-platform.com/Documents/puzzlingOutcomesInControlledExperiments.pdf (evergreen)

7. **Novelty/primacy and survivorship can distort early and long-run interpretations.**  
   Early swings often regress; long-term attrition can bias cohort-level reads if not modeled/diagnosed.  
   Sources: https://support.optimizely.com/hc/en-us/articles/4410289544589-How-and-why-statistical-significance-changes-over-time-in-Optimizely-Experimentation, https://www.exp-platform.com/Documents/2016%20IEEEBigDataLongRunningControlledExperiments.pdf (evergreen)

8. **Simpson's paradox and allocation drift can invert aggregate conclusions.**  
   Segment-weight imbalance over time may reverse observed direction; this requires weighted or epoch-aware interpretation.  
   Sources: https://support.optimizely.com/hc/en-us/articles/5326213705101-History-of-how-Optimizely-Experimentation-controls-Simpson-s-Paradox-in-experiments-with-Stats-Accelerator-enabled, https://medium.com/homeaway-tech-blog/simpsons-paradox-in-a-b-testing-93af7a2f3307 (evergreen)

9. **Bad output format is itself an anti-pattern.**  
   Reports that omit trust gates, predeclared criteria, uncertainty context, and exploratory labeling invite post-hoc cherry-picking.

**Anti-pattern -> detection -> mitigation:**

| Anti-pattern | Detection | Mitigation |
|---|---|---|
| Peeking / optional stopping | Frequent interim checks with unstable p-values | Sequential-valid tests + preregistered stopping rules |
| P-hacking | Post-hoc metric switching and threshold chasing | Locked analysis plan + correction policy + audits |
| HARKing | Hypothesis changes after results | Timestamped hypothesis artifacts + explicit exploratory labels |
| SRM ignored | Split imbalance alerts dismissed | Mandatory SRM gate before verdict |
| Metric drift | Conflicting metric values across systems | Versioned metric catalog + owner/governance |
| Instrumentation bugs | Variant-specific logging anomalies | A/A canaries + telemetry parity checks |
| Segment cherry-picking | Post-hoc slices used for release calls | Exploratory label + confirmatory rerun requirement |

**Sources:**
- https://www.statsig.com/perspectives/sequential-testing-ab-peek
- https://optimizely.com/insights/blog/statistics-for-the-internet-age-the-story-behind-optimizelys-new-stats-engine (evergreen)
- https://engineering.atspotify.com/2023/07/bringing-sequential-testing-to-experiments-with-longitudinal-data-part-1-the-peeking-problem-2-0 (evergreen)
- https://engineering.atspotify.com/2023/07/bringing-sequential-testing-to-experiments-with-longitudinal-data-part-2-sequential-testing (evergreen)
- https://docs.statsig.com/guides/srm
- https://exp-platform.com/Documents/2019_KDDFabijanGupchupFuptaOmhoverVermeerDmitriev.pdf (evergreen)
- https://arxiv.org/abs/1903.12470 (evergreen)
- https://www.exp-platform.com/Documents/puzzlingOutcomesInControlledExperiments.pdf (evergreen)
- https://www.exp-platform.com/Documents/2016%20IEEEBigDataLongRunningControlledExperiments.pdf (evergreen)
- https://www.uber.com/en-GB/blog/umetric/
- https://docs.geteppo.com/experiment-analysis/configuration/protocols/
- https://support.optimizely.com/hc/en-us/articles/4410289544589-How-and-why-statistical-significance-changes-over-time-in-Optimizely-Experimentation
- https://support.optimizely.com/hc/en-us/articles/5326213705101-History-of-how-Optimizely-Experimentation-controls-Simpson-s-Paradox-in-experiments-with-Stats-Accelerator-enabled
- https://medium.com/homeaway-tech-blog/simpsons-paradox-in-a-b-testing-93af7a2f3307 (evergreen)
- https://econpapers.repec.org/paper/zbwi4rdps/101.htm
- https://doi.org/10.1287/isre.2024.0872
- https://pubmed.ncbi.nlm.nih.gov/15647155/ (evergreen)

---

### Angle 5+: Output Schema & Interoperability (domain-specific)
> Canonical experiment result schema grounded in real API/data shapes across tools.

**Findings:**

1. **Real result APIs are nested (`experiment -> metrics -> per-variant results`), not flat.**  
   Optimizely result docs show metric objects containing per-variation maps with sample and variance-related fields.  
   Source: https://docs.developers.optimizely.com/feature-experimentation/reference/get_experiment_results

2. **Primary/secondary/monitoring metric roles are often implicit in vendor payloads.**  
   A canonical schema should make role explicit (e.g., `metric_role`) rather than relying on index position.  
   Source: https://docs.developers.optimizely.com/feature-experimentation/reference/get_experiment_results

3. **Frequentist and Bayesian outputs must be represented conditionally.**  
   Frequentist requires p-value/significance/CI; Bayesian requires posterior probability and risk/loss style fields where available.  
   Sources: https://docs.statsig.com/experiments/statistical-methods/p-value, https://docs.growthbook.io/app/experiment-results, https://docs.geteppo.com/experiment-analysis/

4. **Guardrail and SRM should be first-class structured blocks.**  
   Both are decision gates in modern workflows and should not be buried in free-text recommendation fields.  
   Sources: https://docs.growthbook.io/app/experiment-decisions, https://docs.statsig.com/guides/srm/, https://developer.harness.io/docs/feature-management-experimentation/experimentation/experiment-results/analyzing-experiment-results/sample-ratio-check

5. **Decision metadata must be stored separately from metric calculations.**  
   Real systems expose explicit outcomes/states; schema should preserve decision traceability (`outcome`, `reason_codes`, `decided_at`, policy context).  
   Sources: https://docs.developers.optimizely.com/web-experimentation/reference/get_experiment_report, https://docs.growthbook.io/app/experiment-decisions

6. **Time and freshness fields are necessary for reproducibility.**  
   Analysis window plus `analyzed_at`/staleness semantics are needed to prevent stale-result misinterpretation.  
   Sources: https://docs.developers.optimizely.com/feature-experimentation/reference/get_experiment_results, https://docs.developers.optimizely.com/web-experimentation/reference/get_experiment_report

7. **Interoperable schema standards should be explicit (JSON Schema/OpenAPI + RFC3339).**  
   This reduces ambiguity in required fields, enums, and date-time formatting for downstream integrations.  
   Sources: https://spec.openapis.org/oas/v3.1.2.html, https://json-schema.org/draft/2020-12, https://json-schema.org/draft/2020-12/draft-bhutton-json-schema-validation-01.html, https://www.rfc-editor.org/rfc/rfc3339

**Sources:**
- https://docs.developers.optimizely.com/feature-experimentation/reference/get_experiment_results
- https://docs.developers.optimizely.com/web-experimentation/reference/get_experiment_report
- https://docs.statsig.com/experiments/interpreting-results/read-results
- https://docs.statsig.com/experiments/statistical-methods/p-value
- https://docs.statsig.com/guides/srm/
- https://docs.growthbook.io/app/experiment-results
- https://docs.growthbook.io/app/experiment-decisions
- https://docs.geteppo.com/experiment-analysis/
- https://developer.harness.io/docs/feature-management-experimentation/experimentation/experiment-results/analyzing-experiment-results/sample-ratio-check
- https://spec.openapis.org/oas/v3.1.2.html
- https://json-schema.org/draft/2020-12
- https://json-schema.org/draft/2020-12/draft-bhutton-json-schema-validation-01.html
- https://www.rfc-editor.org/rfc/rfc3339

---

## Synthesis

The strongest cross-source signal remains a shift from "statistical readout" to "explicit decision system." The 2024-2026 material strengthens this pattern: experiment quality now depends on hard trust gates (SRM and instrumentation integrity), policy-explicit multiplicity handling, and codified guardrail doctrine, not only on p-values or posterior probability. This confirms that `experiment-analysis` should orchestrate a strict pipeline (validity -> inference -> risk -> decision) with machine-checkable blockers.

Methodologically, there is convergence on three valid paths with different operating assumptions: fixed-horizon frequentist (best efficiency when you do not need continuous looks), sequential-valid frequentist (safe for continuous monitoring with wider intervals at equal sample), and Bayesian risk-aware decisioning (probability + expected loss, not probability alone). The right implementation is not one "best method"; it is an explicit method branch with branch-specific required outputs and prohibition of mixed semantics in one verdict.

A key contradiction still exists around guardrail multiplicity doctrine. Some ecosystems emphasize broad BH/FDR controls over many decision surfaces; risk-aware decision-rule work (for non-inferiority guardrails) emphasizes not simply alpha-correcting every guardrail while still preserving overall decision power. This must be made explicit as policy in the skill output (`guardrail_multiplicity_policy`) instead of being silently implied.

Tool/API findings from this pass add practical interoperability constraints: data comes from heterogeneous surfaces (true result endpoints, report-download endpoints, and event-import-only APIs), with strong provider-specific limits and lifecycle semantics (`202`/`204`, rate headers, tenant/plan gates). Therefore schema normalization and provenance capture are mandatory for reproducible analysis in multi-platform stacks.

Recent uncertainty guidance also reinforces language discipline: "non-significant" is not "no effect," and "high posterior probability" is not automatically "safe to ship." CI/CrI bounds, practical effect thresholds, expected loss, and guardrail veto must be present in every decision packet. This aligns with the anti-pattern evidence: peeking, post-hoc segmentation, HARKing, and ignored SRM remain common failure sources unless explicitly encoded as risk flags and blockers.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.

- [x] Add a mandatory **Decision Quality Gate** before any winner call: SRM status, assignment integrity, instrumentation parity, metric-definition integrity.
- [x] Split methodology into explicit branches: `frequentist_fixed`, `frequentist_sequential`, `bayesian`; require branch-specific required outputs.
- [x] Require reporting of correction policy: `multiple_testing_method`, `correction_scope`, `alpha_global`, and segmentation doctrine (`confirmatory` vs `exploratory`).
- [x] Add method-aware uncertainty fields: confidence interval or credible interval with explicit `interval_kind`, interval level, and practical threshold relation.
- [x] Add Bayesian risk fields where available: `prob_beats_control`/`prob_best`, `expected_loss`, and `credible_interval`.
- [x] Expand guardrail policy from "check all guardrails" to explicit blocking logic (`non_inferiority_margin`, `degradation_threshold`, `guardrail_block_reason`).
- [x] Upgrade inconclusive guidance: exploratory slices cannot directly justify shipping; they can only generate follow-up confirmatory hypotheses.
- [x] Extend artifact schema with reproducibility metadata: `analysis_method`, `analysis_window`, `analyzed_at`, `result_freshness`, `hypothesis_ref`, `source_provenance`.
- [x] Add anti-pattern risk flags in artifact output: peeking, p-hacking, HARKing, SRM ignored, metric drift, instrumentation mismatch, trigger bias, novelty misread.
- [x] Add explicit `guardrail_multiplicity_policy` to resolve framework contradiction via declared policy (not implied behavior).
- [x] Add a provider-aware `## Available Tools` section with real syntax and rate-limit/error-handling guidance for ingestion surfaces.
- [x] Add standardized decision text template to enforce consistent output language and avoid overclaiming from uncertain results.

---

## Draft Content for SKILL.md

> Paste-ready SKILL content for each recommendation. This section is intentionally verbose so the editor can cut down without inventing missing logic.

### Draft: Decision Quality Gate (Mandatory Pre-Verdict Block)

Before you compute or interpret any winner signal, you must run a Decision Quality Gate. You are not allowed to produce `ship` or `do_not_ship` from raw metric deltas until this gate passes. The purpose is simple: statistical methods can only protect you when the data-generation process is trustworthy. If assignment is broken, exposure logging is inconsistent, or metric definitions drifted during runtime, your p-values and posterior probabilities are formally precise but operationally wrong.

You must evaluate these checks in order:

1. **Pre-registration integrity**
   - Confirm pre-registered sample-size and decision-date constraints.
   - Confirm hypothesis and metric roles were not changed post-launch.
   - If scope changed materially (traffic split, variant set, bucketing behavior), mark analysis as contaminated and require restart/new experiment key.

2. **Traffic/assignment integrity**
   - Confirm observed allocation is consistent with designed split.
   - Run SRM check (or provider SRM health equivalent).
   - If SRM fails and root cause is unresolved, stop and output `blocked_by_guardrail` (or `invalid_for_inference` if your policy supports that state).

3. **Instrumentation integrity**
   - Confirm assignment->exposure funnel parity across variants and key segments (platform/app version/region when available).
   - Confirm no variant-specific event loss, delayed ingestion, or schema mismatch.
   - If parity fails, block verdict and request instrumentation fix + rerun window.

4. **Metric-definition integrity**
   - Confirm metric filters, denominators, time windows, and inclusion rules match pre-registered definitions.
   - Confirm no post-hoc metric substitution for confirmatory verdicts.

5. **Guardrail readiness**
   - Confirm guardrail thresholds are present and measurable before reading primary success metrics.
   - If any critical guardrail is missing or stale, block final verdict as `inconclusive`.

Decision rule for this block:

- If **any blocker** check fails -> `checklist_passed=false`, do not run winner logic, and output blocker reasons.
- If checks pass with warnings -> continue with explicit warning annotations in final recommendation.
- If all checks pass cleanly -> run method-specific inference branch.

Source basis: https://docs.statsig.com/experiments/monitoring/srm, https://docs.statsig.com/stats-engine/methodologies/srm-checks, https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/, https://amplitude.com/docs/feature-experiment/troubleshooting/sample-ratio-mismatch

### Draft: Method Selection and Branching Logic

You must choose one analysis method branch before statistical interpretation:

- `frequentist_fixed`
- `frequentist_sequential`
- `bayesian`

You must not mix branch semantics in one verdict sentence. For example, do not report a frequentist p-value and then justify shipping with a Bayesian probability threshold unless your policy explicitly defines how to combine them. Each branch has its own guarantees, stopping logic, and required fields.

Use this method selector:

1. If your decision time is fixed and interim peeking is not allowed -> choose `frequentist_fixed`.
2. If you need continuous monitoring or potential early stop -> choose `frequentist_sequential`.
3. If policy requires probability-of-win plus risk framing -> choose `bayesian`.

Branch-specific minimum reporting:

- **frequentist_fixed**
  - test family and p-value
  - confidence interval
  - practical-threshold comparison (MEI/MDE)
  - correction method/scope

- **frequentist_sequential**
  - sequential method identifier used by provider (or confidence-sequence semantics)
  - anytime-valid p-value or sequential confidence interval
  - stopping condition reached
  - correction method/scope

- **bayesian**
  - posterior probability metric (`prob_beats_control` or `prob_best`)
  - expected loss/downside metric
  - credible interval
  - prior policy note if informative priors were used

If branch requirements are incomplete, output `inconclusive` and explain exactly which required fields were missing. This avoids fake certainty from partially observed pipelines.

Source basis: https://docs.launchdarkly.com/guides/statistical-methodology/methodology-frequentist, https://docs.launchdarkly.com/home/experimentation/bayesian-results, https://docs.statsig.com/experiments/advanced-setup/sequential-testing, https://experienceleague.adobe.com/en/docs/journey-optimizer/using/content-management/content-experiment/technotes/experiment-calculations

### Draft: Frequentist Fixed-Horizon Analysis Instructions

When you run `frequentist_fixed`, you must behave as if the analysis endpoint is fixed at design time. You do not repeatedly evaluate significance and stop when numbers look favorable. You run your pre-registered sample/date gate, then compute and interpret once for the decision.

For binary metrics:
- Use two-proportion z-test (or provider-equivalent frequentist binary test).

For continuous metrics:
- Use Welch's t-test (or provider-equivalent unequal-variance frequentist test).

Interpretation requirements:

1. Report p-value and confidence interval together.
2. State whether interval excludes zero (or another null threshold), but also compare against practical threshold (`MEI`/`MDE`).
3. Never write "`p > alpha` therefore there is no effect." Correct wording: evidence is insufficient for the pre-registered claim at current precision.
4. For multi-metric or multi-variant analysis, apply declared correction and state scope.

Frequentist fixed decision rule:

- If primary metric is significant **and** practical threshold is met **and** no guardrail blocker -> `ship`.
- If significance is absent but interval still includes practically meaningful gains and losses -> `inconclusive`.
- If significant harm on primary or guardrails -> `do_not_ship` or `blocked_by_guardrail` depending on role.

Recommended final sentence pattern:

`Variant A produced <relative_lift>% vs control on <metric> (p=<p_value>, <interval_level>% <interval_kind>: [<low>, <high>]). Under <correction_method> at scope <correction_scope>, and with guardrails passing, recommendation is <verdict>.`

Source basis: https://docs.launchdarkly.com/home/experimentation/frequentist-results, https://www.optimizely.com/insights/blog/power-analysis-in-fixed-horizon-frequentist-ab-tests/, https://amstat.org/docs/default-source/amstat-documents/p-valuestatement.pdf

### Draft: Frequentist Sequential Analysis Instructions

When you run `frequentist_sequential`, you must use a sequential-valid method from the underlying platform or methodology. You cannot simulate sequential safety by repeatedly checking fixed-horizon p-values. If your monitoring cadence is daily or continuous, this branch is preferred for validity, but you must disclose the precision trade-off (intervals are often wider at equal sample vs fixed horizon).

Execution steps:

1. Confirm sequential mode was configured before launch (or at least before interpretation).
2. Use provider sequential outputs (for example, sequential p-values or confidence-sequence style intervals).
3. Record stopping reason:
   - planned stop reached
   - early efficacy stop
   - early harm stop
   - maximum duration reached without decision
4. Apply multiplicity doctrine consistently with sequential branch.
5. Keep guardrail veto active exactly as in fixed branch.

Interpretation rule:

- If sequential evidence threshold reached with practical effect and guardrails pass -> `ship`.
- If sequential harm threshold reached on primary or guardrail -> `do_not_ship` or `blocked_by_guardrail`.
- If maximum monitoring window reached without stable conclusion -> `inconclusive` with explicit uncertainty statement.

You must include this warning line in the final report:
`Sequential monitoring was used; interval width and stopping behavior reflect anytime-valid inference rather than fixed-horizon precision.`

Source basis: https://docs.statsig.com/experiments/advanced-setup/sequential-testing, https://docs.growthbook.io/statistics/sequential, https://confidence.spotify.com/blog/smaller-sample-experiments, https://projecteuclid.org/journals/annals-of-statistics/volume-52/issue-6/Time-uniform-central-limit-theory-and-asymptotic-confidence-sequences/10.1214/24-AOS2408.short

### Draft: Bayesian Analysis with Risk Controls

When you run `bayesian`, you must report probability and risk together. A high probability-to-win alone is not enough for shipping decisions. You require the combined gate: posterior win signal, downside risk (expected loss), and guardrail safety.

Required Bayesian outputs:

- `prob_beats_control` (or `prob_best` for multi-variant)
- `expected_loss` (or closest provider downside proxy)
- `credible_interval` at declared level
- prior policy note:
  - default/weakly-informative priors, or
  - informative prior with governance record

Bayesian decision rule:

- If `prob_beats_control >= ship_probability_threshold`
  **and** `expected_loss <= max_expected_loss`
  **and** credible interval is consistent with acceptable downside
  **and** guardrails pass -> `ship`.

- If posterior probability is high but expected loss is above threshold -> `inconclusive` or limited rollout with explicit risk note.

- If guardrails fail non-inferiority/degradation threshold -> `blocked_by_guardrail` even when posterior win signal is strong.

Informative prior governance:

- You must pre-register prior source and rationale.
- You must report raw estimate and prior-adjusted estimate side-by-side when possible.
- If prior provenance is missing, downgrade to default prior mode and mark output with governance warning.

Source basis: https://docs.launchdarkly.com/home/experimentation/bayesian-results, https://posthog.com/docs/experiments/statistics, https://www.statsig.com/blog/informed-bayesian-ab-testing, https://docs.statsig.com/experiments-plus/bayesian

### Draft: Multiple Testing and Segmentation Policy

You must define the hypothesis family and correction scope before analysis output. "We corrected p-values" is insufficient unless you specify what family was corrected.

Required fields:

- `multiple_testing_method` (for example: `none`, `bonferroni`, `benjamini_hochberg`, `bayesian_fdr`)
- `correction_scope` (`primary_only`, `decision_family`, `all_reported`)
- `alpha_global` (or Bayesian equivalent risk target)
- `segmentation_policy` (`confirmatory_only`, `exploratory_labeled`, `hybrid`)

Operational policy:

1. Confirmatory claims must come only from pre-registered scopes.
2. Exploratory slices can generate hypotheses, but cannot directly authorize shipping.
3. If exploratory result is business-critical, require a dedicated confirmatory rerun.
4. Explicitly annotate uncorrected or weakly corrected outputs as exploratory.

Recommended language:
`Segment-level uplift is exploratory and not used for shipping authorization under current correction scope.`

Source basis: https://docs.statsig.com/stats-engine/methodologies/benjamini-hochberg-procedure, https://support.optimizely.com/hc/en-us/articles/4410283967245-False-discovery-rate-control, https://docs.launchdarkly.com/guides/statistical-methodology/mcc, https://docs.growthbook.io/statistics/multiple-corrections

### Draft: Guardrail Doctrine and Blocking Logic

You must formalize guardrails as hard risk constraints, not as informational side metrics. A positive primary effect does not override a failed critical guardrail.

Guardrail requirement set:

- each guardrail has:
  - `metric_name`
  - `direction` (`higher_is_worse` or `lower_is_worse`)
  - `degradation_threshold`
  - optional `non_inferiority_margin`
  - significance or posterior risk check

Blocking rule:

- If any critical guardrail breaches declared threshold under declared uncertainty policy -> `blocked_by_guardrail`.
- If guardrail signal is noisy but risk cannot be ruled out -> `inconclusive` unless policy allows limited, monitored rollout.

Multiplicity doctrine field:

- `guardrail_multiplicity_policy` enum:
  - `alpha_corrected`
  - `beta_corrected_decision_rule`
  - `policy_exception_documented`

You must choose one doctrine and state it in the report. Do not silently mix frameworks.

Source basis: https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics, https://arxiv.org/abs/2402.11609, https://docs.growthbook.io/app/experiment-decisions, https://support.optimizely.com/hc/en-us/articles/4410283160205-Primary-metrics-secondary-metrics-and-monitoring-goals

### Draft: Inconclusive Outcome Handling

When the outcome is inconclusive, you must avoid binary over-interpretation. "Not significant" is not proof of "no effect." Your next step should depend on uncertainty geometry and business context.

Inconclusive decision tree:

1. If interval still includes both meaningful gain and meaningful harm:
   - keep verdict `inconclusive`
   - choose between larger sample, longer runtime, or cleaner targeting/triggering.

2. If interval excludes meaningful harm but does not show strong gain:
   - classify as "safe but unproven"
   - consider limited rollout only if business policy allows.

3. If interval excludes meaningful gain:
   - classify as low-priority hypothesis
   - archive or redesign based on opportunity cost.

4. If exploratory segment signal appears:
   - do not ship from that signal alone
   - register a follow-up confirmatory experiment.

Required final language:
`Result is inconclusive at current precision and policy thresholds; follow-up path is <path> with required sample/time estimate <estimate>.`

Source basis: https://pmc.ncbi.nlm.nih.gov/articles/PMC11049675/, https://pmc.ncbi.nlm.nih.gov/articles/PMC11995452/, https://www.optimizely.com/insights/blog/power-analysis-in-fixed-horizon-frequentist-ab-tests/, https://launchdarkly.com/docs/home/experimentation/size

### Draft: Available Tools (Real Syntax, Provider-Aware)

Use internal Flexus tools for policy retrieval and artifact recording. Use provider APIs only for ingestion/reference where upstream data collection is needed and permitted.

#### Internal tools (primary in-skill interface)

```python
flexus_policy_document(op="activate", args={"p": "/experiments/{experiment_id}/spec"})
flexus_policy_document(op="list", args={"p": "/experiments/"})
write_artifact(
  artifact_type="experiment_results",
  path="/experiments/{experiment_id}/results",
  data={...},
)
```

Internal tool usage guidance:

- Always activate experiment spec before analysis to lock hypothesis, metric roles, and thresholds.
- If spec is missing or incomplete, return `inconclusive` and request policy completion.
- Write artifact once per final decision packet; include method branch and quality-gate status.

#### External provider API syntax references (for ingestion/orchestration layers)

Statsig report URL retrieval:

```bash
curl -H "STATSIG-API-KEY: $STATSIG_API_KEY" \
  "https://statsigapi.net/console/v1/reports?type=pulse_daily&date=2024-09-01"
```

Statsig experiment metadata:

```bash
curl -H "STATSIG-API-KEY: $STATSIG_API_KEY" \
  "https://statsigapi.net/console/v1/experiments/{experiment_id}"
```

GrowthBook experiment results:

```bash
curl "https://api.growthbook.io/api/v1/experiments/{experiment_id}/results" \
  -u "secret_xxx:"
```

GrowthBook snapshot refresh before pull:

```bash
curl -X POST "https://api.growthbook.io/api/v1/experiments/{experiment_id}/snapshot" \
  -u "secret_xxx:"
```

Optimizely Web Experimentation results:

```bash
curl -H "Authorization: Bearer $OPTIMIZELY_TOKEN" \
  "https://api.optimizely.com/v2/experiments/{experiment_id}/results"
```

LaunchDarkly event-data import (for metric event ingestion):

```bash
curl -X POST \
  "https://events.launchdarkly.com/v2/event-data-import/{projectKey}/{environmentKey}" \
  -H "Authorization: $LD_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[{"kind":"custom","key":"checkout_completed","contextKeys":{"user":"u-123"},"creationDate":1735689600000}]'
```

Amplitude Experiment Evaluation API:

```bash
curl --request GET \
  "https://api.lab.amplitude.com/v1/vardata?user_id=u-123" \
  --header "Authorization: Api-Key $AMPLITUDE_DEPLOYMENT_KEY"
```

Provider reliability notes you must encode in orchestration:

- GrowthBook public limit: 60 req/minute; handle `429` with backoff.
- Optimizely results endpoint can return `202` (processing) and `204` (no data yet); this is a lifecycle state, not necessarily an error.
- LaunchDarkly import has strict payload and timing constraints; honor `Retry-After` on rate limits.
- Statsig and other providers may have plan/tenant/version constraints; capture API version and provenance in artifact metadata.

Source basis: https://docs.statsig.com/api-reference/reports/get-reports, https://docs.statsig.com/api-reference/experiments/get-experiment, https://api.growthbook.io/api/v1/openapi.yaml, https://docs.developers.optimizely.com/web-experimentation/reference/get_experiment_results, https://launchdarkly.com/docs/home/metrics/import-events, https://amplitude.com/docs/apis/experiment/experiment-evaluation-api, https://developers.vwo.com/reference/api-rate-limits-1

### Draft: Anti-Pattern Warning Blocks

#### Warning: Peeking / Optional Stopping
- **Signal:** frequent dashboard checks in fixed-horizon mode, with decision made at first favorable point.
- **Consequence:** inflated false positives and unstable winner calls.
- **Mitigation:** either enforce fixed analysis date/sample or move to sequential-valid branch; log stopping rule in artifact.

#### Warning: Mid-Run Design Changes
- **Signal:** traffic split or variant set changed after launch; sticky bucketing policy changed.
- **Consequence:** contamination/carryover bias; invalid cross-variant comparability.
- **Mitigation:** restart experiment with clean randomization; mark old run as non-confirmatory.

#### Warning: P-Hacking / Metric Shopping
- **Signal:** post-hoc swapping of primary metric, filters, or windows to obtain significance.
- **Consequence:** high chance of non-replicable false discoveries.
- **Mitigation:** lock analysis contract pre-launch; separate confirmatory and exploratory outputs.

#### Warning: HARKing
- **Signal:** final narrative hypothesis differs from pre-registered hypothesis without explicit label.
- **Consequence:** misleading confidence and broken causal interpretation discipline.
- **Mitigation:** force "exploratory hypothesis" label and require follow-up confirmatory experiment.

#### Warning: SRM Ignored
- **Signal:** SRM warning/fail present but result still interpreted as trustworthy.
- **Consequence:** assignment mismatch can invert or magnify observed effects.
- **Mitigation:** SRM failure is a blocker until root cause is resolved and data regenerated if needed.

#### Warning: Trigger Selection Bias
- **Signal:** trigger condition is influenced by treatment or trigger-rate diverges by variant.
- **Consequence:** post-randomization selection bias.
- **Mitigation:** use pre-treatment trigger criteria; verify trigger parity across variants.

#### Warning: Overtracking Dilution
- **Signal:** large share of analyzed users cannot be exposed to treatment effect.
- **Consequence:** diluted effect size and large uncertainty; slower decisions.
- **Mitigation:** tighten eligibility/triggering and analyze exposure-relevant population.

#### Warning: Guardrail Blindness
- **Signal:** primary uplift used to justify shipping despite guardrail degradation.
- **Consequence:** local gain with systemic product risk (latency/churn/cost/reliability).
- **Mitigation:** guardrail veto policy with explicit thresholds and blocking reasons.

#### Warning: Novelty Misread
- **Signal:** early uplift spike decays rapidly across days-since-exposure.
- **Consequence:** shipping transient novelty instead of durable impact.
- **Mitigation:** inspect temporal stability and, when possible, validate with holdout windows.

#### Warning: Instrumentation Mismatch
- **Signal:** assignment-to-exposure funnel differs across variants or key segments.
- **Consequence:** pseudo-treatment effect from logging asymmetry.
- **Mitigation:** parity checks, native exposure events where possible, and unresolved mismatch as blocker.

#### Warning: CUPED Leakage
- **Signal:** covariate likely influenced by treatment or pre-period contamination detected.
- **Consequence:** biased adjusted estimates and false confidence.
- **Mitigation:** only pre-treatment covariates; fallback to non-CUPED estimate when integrity is uncertain.

Source basis: https://docs.statsig.com/experiments/advanced-setup/sequential-testing, https://docs.growthbook.io/using/experimentation-problems, https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/, https://confidence.spotify.com/blog/trigger-analysis, https://booking.ai/overtracking-and-trigger-analysis-how-to-reduce-sample-sizes-and-increase-the-sensitivity-of-71755bad0e5f, https://www.statsig.com/blog/novelty-effects, https://launchdarkly.com/docs/guides/statistical-methodology/cuped

### Draft: Artifact Schema Additions (JSON Schema Fragments)

Use the following schema fragment to replace or extend current `experiment_results`. Every field has explicit descriptions, and all nested objects are closed with `additionalProperties: false` to prevent silent drift.

```json
{
  "experiment_results": {
    "type": "object",
    "description": "Canonical decision packet for post-run experiment analysis. Includes quality gates, method-specific inference fields, risk controls, and final recommendation.",
    "required": [
      "experiment_id",
      "hypothesis_ref",
      "analyzed_at",
      "analysis_method",
      "analysis_window",
      "quality_gate",
      "decision_policy",
      "primary_metric_result",
      "guardrail_results",
      "multiple_testing",
      "anti_pattern_risks",
      "verdict",
      "recommendation",
      "hypothesis_verdict",
      "source_provenance",
      "result_freshness"
    ],
    "additionalProperties": false,
    "properties": {
      "experiment_id": {
        "type": "string",
        "description": "Stable experiment identifier from the policy document and provider system."
      },
      "hypothesis_ref": {
        "type": "string",
        "description": "Reference to pre-registered hypothesis/version used for this analysis."
      },
      "analyzed_at": {
        "type": "string",
        "format": "date-time",
        "description": "RFC3339 timestamp when the decision packet was produced."
      },
      "analysis_method": {
        "type": "string",
        "enum": [
          "frequentist_fixed",
          "frequentist_sequential",
          "bayesian"
        ],
        "description": "Inference branch chosen before interpretation."
      },
      "analysis_window": {
        "type": "object",
        "description": "Time window of data included in this analysis.",
        "required": [
          "start_at",
          "end_at"
        ],
        "additionalProperties": false,
        "properties": {
          "start_at": {
            "type": "string",
            "format": "date-time",
            "description": "Inclusive start of analysis data window."
          },
          "end_at": {
            "type": "string",
            "format": "date-time",
            "description": "Inclusive end of analysis data window."
          }
        }
      },
      "result_freshness": {
        "type": "string",
        "enum": [
          "fresh",
          "stale",
          "unknown"
        ],
        "description": "Freshness status of source data at analysis time."
      },
      "quality_gate": {
        "type": "object",
        "description": "Mandatory trust-gate checks executed before any winner logic.",
        "required": [
          "checklist_passed",
          "preregistered_sample_reached",
          "preregistered_decision_date_reached",
          "metric_definition_integrity",
          "srm_status",
          "assignment_integrity_status",
          "instrumentation_integrity_status",
          "blocker_reasons"
        ],
        "additionalProperties": false,
        "properties": {
          "checklist_passed": {
            "type": "boolean",
            "description": "True only if all blocking checks pass."
          },
          "preregistered_sample_reached": {
            "type": "boolean",
            "description": "Whether pre-registered sample requirement was reached."
          },
          "preregistered_decision_date_reached": {
            "type": "boolean",
            "description": "Whether pre-registered decision date/time requirement was reached."
          },
          "metric_definition_integrity": {
            "type": "boolean",
            "description": "Whether metric definitions and filters match the pre-registered contract."
          },
          "srm_status": {
            "type": "string",
            "enum": [
              "pass",
              "warning",
              "fail",
              "not_run"
            ],
            "description": "Sample Ratio Mismatch check status."
          },
          "srm_p_value": {
            "type": [
              "number",
              "null"
            ],
            "description": "SRM test p-value when available; null when provider does not expose it."
          },
          "assignment_integrity_status": {
            "type": "string",
            "enum": [
              "pass",
              "warning",
              "fail"
            ],
            "description": "Status of assignment and split integrity checks."
          },
          "instrumentation_integrity_status": {
            "type": "string",
            "enum": [
              "pass",
              "warning",
              "fail"
            ],
            "description": "Status of event logging and exposure parity checks."
          },
          "blocker_reasons": {
            "type": "array",
            "description": "Human-readable reasons that blocked or nearly blocked interpretation.",
            "items": {
              "type": "string"
            }
          }
        }
      },
      "decision_policy": {
        "type": "object",
        "description": "Declared statistical and risk policy used for this verdict.",
        "required": [
          "alpha_global",
          "multiple_testing_method",
          "correction_scope",
          "segmentation_policy",
          "guardrail_multiplicity_policy",
          "ship_probability_threshold",
          "max_expected_loss",
          "decision_rule_version"
        ],
        "additionalProperties": false,
        "properties": {
          "alpha_global": {
            "type": "number",
            "description": "Global frequentist alpha target for confirmatory decisions."
          },
          "multiple_testing_method": {
            "type": "string",
            "enum": [
              "none",
              "bonferroni",
              "benjamini_hochberg",
              "bayesian_fdr"
            ],
            "description": "Multiplicity method applied to the declared hypothesis family."
          },
          "correction_scope": {
            "type": "string",
            "enum": [
              "primary_only",
              "decision_family",
              "all_reported"
            ],
            "description": "Family scope over which multiplicity correction was applied."
          },
          "segmentation_policy": {
            "type": "string",
            "enum": [
              "confirmatory_only",
              "exploratory_labeled",
              "hybrid"
            ],
            "description": "Policy for using segment-level results in decisioning."
          },
          "guardrail_multiplicity_policy": {
            "type": "string",
            "enum": [
              "alpha_corrected",
              "beta_corrected_decision_rule",
              "policy_exception_documented"
            ],
            "description": "Declared doctrine for guardrail multiplicity handling."
          },
          "ship_probability_threshold": {
            "type": "number",
            "description": "Bayesian minimum posterior probability threshold for shipping when Bayesian branch is used."
          },
          "max_expected_loss": {
            "type": "number",
            "description": "Maximum tolerated expected downside for Bayesian shipping decisions."
          },
          "decision_rule_version": {
            "type": "string",
            "description": "Version identifier of the policy rule set used to produce this verdict."
          }
        }
      },
      "primary_metric_result": {
        "type": "object",
        "description": "Primary metric effect and uncertainty for decisioning.",
        "required": [
          "metric_name",
          "control_value",
          "variant_values",
          "relative_lift",
          "interval_kind",
          "interval_level",
          "interval_low",
          "interval_high",
          "practical_threshold",
          "practical_threshold_met",
          "p_value",
          "is_significant"
        ],
        "additionalProperties": false,
        "properties": {
          "metric_name": {
            "type": "string",
            "description": "Canonical primary metric identifier."
          },
          "control_value": {
            "type": "number",
            "description": "Observed control value in analysis window."
          },
          "variant_values": {
            "type": "object",
            "description": "Map from variant key to observed metric value.",
            "additionalProperties": {
              "type": "number"
            }
          },
          "relative_lift": {
            "type": "number",
            "description": "Relative effect size of selected variant vs control (fractional units)."
          },
          "interval_kind": {
            "type": "string",
            "enum": [
              "confidence_interval",
              "credible_interval",
              "confidence_sequence"
            ],
            "description": "Type of uncertainty interval reported for this metric."
          },
          "interval_level": {
            "type": "number",
            "description": "Interval confidence/credibility level in [0,1], for example 0.95."
          },
          "interval_low": {
            "type": "number",
            "description": "Lower bound of uncertainty interval on effect scale."
          },
          "interval_high": {
            "type": "number",
            "description": "Upper bound of uncertainty interval on effect scale."
          },
          "practical_threshold": {
            "type": "number",
            "description": "Minimum practical effect threshold (MEI/MDE-aligned) used in decisioning."
          },
          "practical_threshold_met": {
            "type": "boolean",
            "description": "Whether observed effect and uncertainty satisfy practical threshold requirement."
          },
          "p_value": {
            "type": [
              "number",
              "null"
            ],
            "description": "Frequentist p-value when applicable; null for pure Bayesian outputs."
          },
          "is_significant": {
            "type": [
              "boolean",
              "null"
            ],
            "description": "Frequentist significance flag under declared correction policy; null when not applicable."
          }
        }
      },
      "guardrail_results": {
        "type": "array",
        "description": "Per-guardrail risk outcomes and blocking status.",
        "items": {
          "type": "object",
          "required": [
            "metric_name",
            "direction",
            "degradation_threshold",
            "is_degraded",
            "p_value",
            "non_inferiority_margin",
            "blocked"
          ],
          "additionalProperties": false,
          "properties": {
            "metric_name": {
              "type": "string",
              "description": "Guardrail metric identifier."
            },
            "direction": {
              "type": "string",
              "enum": [
                "higher_is_worse",
                "lower_is_worse"
              ],
              "description": "Direction that constitutes degradation for this guardrail."
            },
            "degradation_threshold": {
              "type": "number",
              "description": "Absolute or relative threshold beyond which degradation is considered unacceptable."
            },
            "is_degraded": {
              "type": "boolean",
              "description": "Whether this guardrail currently indicates unacceptable deterioration."
            },
            "p_value": {
              "type": [
                "number",
                "null"
              ],
              "description": "Frequentist p-value for degradation test when available."
            },
            "non_inferiority_margin": {
              "type": [
                "number",
                "null"
              ],
              "description": "Non-inferiority margin used for this guardrail when policy applies."
            },
            "blocked": {
              "type": "boolean",
              "description": "True when this guardrail alone is sufficient to block shipping."
            }
          }
        }
      },
      "multiple_testing": {
        "type": "object",
        "description": "Correction metadata applied to family-wise interpretation.",
        "required": [
          "method",
          "scope",
          "hypothesis_count",
          "adjusted_alpha"
        ],
        "additionalProperties": false,
        "properties": {
          "method": {
            "type": "string",
            "description": "Applied multiplicity correction method."
          },
          "scope": {
            "type": "string",
            "description": "Declared family scope used for correction."
          },
          "hypothesis_count": {
            "type": "integer",
            "minimum": 1,
            "description": "Number of hypotheses included in correction family."
          },
          "adjusted_alpha": {
            "type": [
              "number",
              "null"
            ],
            "description": "Adjusted alpha used for frequentist interpretation; null if not applicable."
          }
        }
      },
      "bayesian_summary": {
        "type": [
          "object",
          "null"
        ],
        "description": "Bayesian uncertainty and risk summary. Required when analysis_method is bayesian.",
        "required": [
          "prob_beats_control",
          "prob_best",
          "expected_loss",
          "credible_interval_low",
          "credible_interval_high",
          "prior_policy"
        ],
        "additionalProperties": false,
        "properties": {
          "prob_beats_control": {
            "type": "number",
            "description": "Posterior probability that selected variant outperforms control."
          },
          "prob_best": {
            "type": [
              "number",
              "null"
            ],
            "description": "Posterior probability that selected variant is best among all variants."
          },
          "expected_loss": {
            "type": "number",
            "description": "Expected downside from shipping selected variant."
          },
          "credible_interval_low": {
            "type": "number",
            "description": "Lower bound of Bayesian credible interval on effect scale."
          },
          "credible_interval_high": {
            "type": "number",
            "description": "Upper bound of Bayesian credible interval on effect scale."
          },
          "prior_policy": {
            "type": "string",
            "enum": [
              "default_prior",
              "weakly_informative",
              "informative_pre_registered"
            ],
            "description": "Prior policy used for Bayesian estimation."
          }
        }
      },
      "anti_pattern_risks": {
        "type": "object",
        "description": "Structured anti-pattern risk flags observed during analysis.",
        "required": [
          "peeking",
          "p_hacking",
          "harking",
          "srm_ignored",
          "metric_drift",
          "instrumentation_mismatch",
          "trigger_selection_bias",
          "novelty_misread"
        ],
        "additionalProperties": false,
        "properties": {
          "peeking": { "$ref": "#/$defs/riskFlag" },
          "p_hacking": { "$ref": "#/$defs/riskFlag" },
          "harking": { "$ref": "#/$defs/riskFlag" },
          "srm_ignored": { "$ref": "#/$defs/riskFlag" },
          "metric_drift": { "$ref": "#/$defs/riskFlag" },
          "instrumentation_mismatch": { "$ref": "#/$defs/riskFlag" },
          "trigger_selection_bias": { "$ref": "#/$defs/riskFlag" },
          "novelty_misread": { "$ref": "#/$defs/riskFlag" }
        }
      },
      "verdict": {
        "type": "string",
        "enum": [
          "ship",
          "do_not_ship",
          "inconclusive",
          "blocked_by_guardrail"
        ],
        "description": "Final decision outcome under declared policy."
      },
      "recommendation": {
        "type": "string",
        "description": "Human-readable recommendation sentence suitable for stakeholders."
      },
      "hypothesis_verdict": {
        "type": "string",
        "enum": [
          "validated",
          "rejected",
          "inconclusive"
        ],
        "description": "Hypothesis-level interpretation under declared method and policy."
      },
      "next_action": {
        "type": "object",
        "description": "Structured follow-up plan for inconclusive or blocked outcomes.",
        "required": [
          "action_type",
          "rationale"
        ],
        "additionalProperties": false,
        "properties": {
          "action_type": {
            "type": "string",
            "enum": [
              "ship",
              "rollback",
              "rerun_larger_sample",
              "confirmatory_followup",
              "instrumentation_fix_then_rerun",
              "archive_hypothesis"
            ],
            "description": "Operational next step after this analysis."
          },
          "rationale": {
            "type": "string",
            "description": "Concise reason this next action is required."
          }
        }
      },
      "source_provenance": {
        "type": "object",
        "description": "Provider and endpoint lineage for reproducibility.",
        "required": [
          "platform",
          "endpoint",
          "retrieved_at"
        ],
        "additionalProperties": false,
        "properties": {
          "platform": {
            "type": "string",
            "description": "Source platform identifier (for example statsig, optimizely, growthbook, launchdarkly)."
          },
          "endpoint": {
            "type": "string",
            "description": "API endpoint or report source used to fetch analysis inputs."
          },
          "retrieved_at": {
            "type": "string",
            "format": "date-time",
            "description": "RFC3339 timestamp when source data was retrieved."
          },
          "api_version": {
            "type": [
              "string",
              "null"
            ],
            "description": "Version header or API revision used when available."
          }
        }
      }
    },
    "$defs": {
      "riskFlag": {
        "type": "object",
        "description": "Risk-flag object for a specific anti-pattern.",
        "required": [
          "level",
          "signal",
          "consequence",
          "mitigation"
        ],
        "additionalProperties": false,
        "properties": {
          "level": {
            "type": "string",
            "enum": [
              "none",
              "watch",
              "high",
              "blocker"
            ],
            "description": "Severity level for this anti-pattern in current run."
          },
          "signal": {
            "type": "string",
            "description": "Observed signal indicating this anti-pattern may be present."
          },
          "consequence": {
            "type": "string",
            "description": "Decision-quality consequence if the anti-pattern is ignored."
          },
          "mitigation": {
            "type": "string",
            "description": "Immediate mitigation action required before shipping."
          }
        }
      }
    },
    "allOf": [
      {
        "if": {
          "properties": {
            "analysis_method": { "const": "bayesian" }
          }
        },
        "then": {
          "required": [ "bayesian_summary" ]
        }
      },
      {
        "if": {
          "properties": {
            "analysis_method": {
              "enum": [
                "frequentist_fixed",
                "frequentist_sequential"
              ]
            }
          }
        },
        "then": {
          "properties": {
            "bayesian_summary": { "type": "null" }
          }
        }
      }
    ]
  }
}
```

Schema usage guidance:

- You should keep `additionalProperties: false` to force explicit schema evolution.
- You should require `source_provenance` so future re-analysis can reproduce exact input lineage.
- You should keep anti-pattern risk fields as structured objects, not plain booleans, so remediation logic is auditable.
- You should use `allOf` method conditionals to prevent partially mixed branch payloads.

Source basis: https://json-schema.org/draft/2020-12, https://json-schema.org/draft/2020-12/draft-bhutton-json-schema-validation-01.html, https://spec.openapis.org/oas/v3.1.2.html, https://www.rfc-editor.org/rfc/rfc3339

### Draft: Final Decision Output Text Template

Use this exact narrative pattern in your recommendation block to avoid overclaiming:

1. **Validity statement**
   - `Decision quality gate: <passed_with_warnings|passed|failed>; blockers: <list or none>.`

2. **Method statement**
   - `Analysis method: <frequentist_fixed|frequentist_sequential|bayesian>; multiplicity: <method/scope>.`

3. **Primary effect statement**
   - Frequentist example:
     - `Primary metric <metric>: lift <x>% vs control (p=<p>, <level>% <interval_kind> [<low>, <high>]).`
   - Bayesian example:
     - `Primary metric <metric>: P(variant>control)=<p>, expected loss=<loss>, <level>% credible interval [<low>, <high>].`

4. **Guardrail statement**
   - `Guardrails: <pass|failed>; blocking metric(s): <list>.`

5. **Verdict and next action**
   - `Verdict: <ship|do_not_ship|inconclusive|blocked_by_guardrail>.`
   - `Next action: <action_type> because <rationale>.`

If outcome is inconclusive, you must include concrete next-step sizing guidance (sample increase or follow-up design) and explicitly mark any segment insight as exploratory unless pre-registered.

Source basis: https://pmc.ncbi.nlm.nih.gov/articles/PMC11996237/, https://pmc.ncbi.nlm.nih.gov/articles/PMC11995452/, https://docs.launchdarkly.com/home/experimentation/analyze/

---

## Gaps & Uncertainties

- Pricing and plan entitlements are highly variable by contract/region/tenant; this research captures capability presence and known gating patterns, not definitive commercial matrices.
- Public docs for some vendors are versioned/beta/fragmented; endpoint availability can differ from tenant reality and requires environment-level validation.
- Guardrail multiplicity doctrine is not standardized across ecosystems; teams must select and codify one policy rather than mixing assumptions.
- SRM threshold recommendations vary (`p<0.01` vs `p<0.001` style strictness). A single global threshold cannot be justified without organization-specific false-alarm tolerance.
- Evidence on p-hacking prevalence is mixed in newer studies; risk controls remain necessary even when a specific platform study reports low observed manipulation.
- Several high-value methodological papers are preprints (2024-2025) and should be treated as directional until peer-reviewed or adopted in vendor production docs.
- Some provider docs expose endpoint behavior but not complete hard numeric rate limits; integration layers should treat `429`/retry headers as source of truth at runtime.
