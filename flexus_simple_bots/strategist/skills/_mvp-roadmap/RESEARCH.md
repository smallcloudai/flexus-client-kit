# Research: mvp-roadmap

**Skill path:** `strategist/skills/mvp-roadmap/`  
**Bot:** strategist  
**Research date:** 2026-03-04  
**Status:** complete

---

## Context

`mvp-roadmap` is a strategist skill that turns MVP intent into a conditional, evidence-gated roadmap from pre-MVP to scale. The skill is used when a team already has a product hypothesis (or early MVP) and needs to sequence milestones, dependencies, and resource commitments without overcommitting to long-range plans before evidence exists.

The core problem this skill solves is roadmap false precision: teams commit to 12-18 month feature plans before confirming core value, retention, or delivery stability. Research from 2024-2026 shows that high-performing teams now bias toward outcome-led roadmaps, explicit gate criteria, and short replanning cadences, while weaker teams still run feature-factory roadmaps with weak experimentation and unstable priorities.

This research expands the current SKILL.md by grounding phase gates, sequencing logic, and risk interpretation in current evidence (2024-2026 priority, older sources explicitly marked evergreen).

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
- Volume: findings section is within 800-4000 words and synthesized (not copied source text)

Verification notes:
- Findings include explicit contradictions (outcome rhetoric vs execution reality; benchmark thresholds vs context baselines; qualitative risk matrices vs quantitative simulation).
- Tool section references real products and documented capabilities/tier constraints.
- Draft section is longer than findings and provides paste-ready SKILL content.

---

## Research Angles

### Angle 1: Domain Methodology and Best Practices
> How practitioners actually do MVP-to-scale sequencing in 2024-2026.

**Findings:**

1. Outcome-led roadmapping is now mainstream language, but not consistently operationalized. ProductPlan 2024 reports broad movement toward outcome metrics in product planning, with strong investment intent in strategy and roadmapping workflows. Practical implication: this skill should require every phase to define outcome evidence before feature commitments.  
Source: [ProductPlan 2024 annual report](https://www.productplan.com/2024-state-of-product-management-annual-report), [ProductPlan 2024 guide](https://productplan.com/the-busy-product-managers-guide-to-the-state-of-product-2024)

2. Strategy and roadmap capacity is a bottleneck, not just methodology knowledge. Atlassian State of Product 2026 (published 2025) shows many teams lack time for strategic planning and roadmap development. Practical implication: cadence must be explicit in the skill, otherwise roadmap quality degrades into reactive backlog management.  
Source: [Atlassian State of Product 2026 PDF](https://dam-cdn.atl.orangelogic.com/AssetLink/iv3u81ou0u70gsy04ia61oci00d0h0je.pdf)

3. Experimentation discipline is uneven. Atlassian reports a split between teams that run rapid or structured experimentation and teams that run limited/no experimentation. Practical implication: phase transitions must be evidence-gated; "we shipped it" is not enough for GO decisions.  
Source: [Atlassian State of Product 2026 PDF](https://dam-cdn.atl.orangelogic.com/AssetLink/iv3u81ou0u70gsy04ia61oci00d0h0je.pdf)

4. Engineering is frequently involved too late. Atlassian indicates early engineering involvement at ideation is still low. Practical implication: dependency realism and capacity realism should be explicit preconditions for phase commitment in this skill.  
Source: [Atlassian State of Product 2026 PDF](https://dam-cdn.atl.orangelogic.com/AssetLink/iv3u81ou0u70gsy04ia61oci00d0h0je.pdf)

5. Product Ops is common, but maturity is uneven. Productboard 2025 reports high Product Ops penetration but low automation and inconsistent measurement. Practical implication: the skill should include a minimum instrumentation standard for roadmap evidence packs.  
Source: [Productboard State of Product Ops 2025](https://www.productboard.com/blog/the-state-of-product-ops-in-2025/)

6. Stage-gate thinking is not dead; it is hybridized with Agile and Lean approaches. A 2024 IEEE review highlights formal hybridization patterns and selection criteria. Practical implication: this skill should keep gate rigor while allowing iterative learning inside each phase.  
Source: [IEEE TEM hybrid stage-gate review (2024)](https://ui.adsabs.harvard.edu/abs/2024ITEM...71.6435C/abstract)

7. Cadence-based planning is used to balance predictability and adaptation. SAFe guidance (updated 2024-2025) defines PI cadence and multi-horizon roadmaps (committed near-term, forecast medium-term). Practical implication: roadmap output should separate committed next phase from conditional forecast phases.  
Source: [SAFe PI Planning](https://scaledagileframework.com/PI-planning), [SAFe Roadmap](https://scaledagileframework.com/roadmap)

8. There is a measurable gap between "outcome orientation" and actual digital outcome attainment. Gartner-reported 2024 survey results show less than half of digital initiatives meet/exceed targets, while top performers have stronger shared ownership models. Practical implication: gate ownership must be cross-functional, not product-only.  
Source: [Gartner survey coverage (Business Wire, 2024)](https://www.businesswire.com/news/home/20241022615512/en/Gartner-Survey-Reveals-That-Only-48-of-Digital-Initiatives-Meet-or-Exceed-Their-Business-Outcome-Targets)

9. Contradiction to preserve in SKILL text: teams claim outcome-led methods, but still underinvest in strategy time and experimental rigor. This contradiction should be represented as explicit anti-pattern checks, not ignored.

**Sources:**
- [ProductPlan 2024 annual report](https://www.productplan.com/2024-state-of-product-management-annual-report)
- [ProductPlan 2024 guide](https://productplan.com/the-busy-product-managers-guide-to-the-state-of-product-2024)
- [Atlassian State of Product 2026 PDF](https://dam-cdn.atl.orangelogic.com/AssetLink/iv3u81ou0u70gsy04ia61oci00d0h0je.pdf)
- [Productboard State of Product Ops 2025](https://www.productboard.com/blog/the-state-of-product-ops-in-2025/)
- [IEEE TEM hybrid stage-gate review (2024)](https://ui.adsabs.harvard.edu/abs/2024ITEM...71.6435C/abstract)
- [SAFe PI Planning](https://scaledagileframework.com/PI-planning)
- [SAFe Roadmap](https://scaledagileframework.com/roadmap)
- [Gartner survey coverage (Business Wire, 2024)](https://www.businesswire.com/news/home/20241022615512/en/Gartner-Survey-Reveals-That-Only-48-of-Digital-Initiatives-Meet-or-Exceed-Their-Business-Outcome-Targets)

---

### Angle 2: Tool and API Landscape
> Tools and data systems for sequencing, dependencies, and roadmap risk management.

**Findings:**

1. Jira Plans (Advanced Roadmaps) is one of the strongest practical backbones for roadmap sequencing because it supports capacity planning, cross-team dependencies, and scenario modeling in sandbox mode. This is directly relevant for conditional phase commitment workflows.  
Source: [Atlassian plans overview](https://atlassian.com/software/jira/guides/advanced-roadmaps/overview), [What is Advanced Roadmaps](https://support.atlassian.com/jira-software-cloud/docs/what-is-advanced-roadmaps/), [Jira scenarios](https://support.atlassian.com/jira-software-cloud/docs/what-are-scenarios-in-advanced-roadmaps)

2. Tier constraints are not a minor detail; they change what risk management is possible. Jira pricing indicates advanced planning and scenario modeling are tier-dependent. Practical implication: any roadmap method should include entitlement checks before promising dependency or what-if features.  
Source: [Jira pricing](https://www.atlassian.com/software/jira/pricing)

3. Jira dependency semantics are explicit enough for machine interpretation (incoming/outgoing links, conflict signals), supporting deterministic gate checks for blocked milestones.  
Source: [Dependencies in Advanced Roadmaps](https://confluence.atlassian.com/jirasoftware/dependencies-in-advanced-roadmaps-1688898866.html)

4. monday.com supports structured dependencies (FS/SS/FF/SF, lead/lag, strict/flexible modes), but capabilities vary by plan and some portfolio-risk features are enterprise-focused or rolling out gradually. Practical implication: dependency and risk workflows should degrade gracefully when enterprise features are absent.  
Source: [monday dependencies](https://support.monday.com/hc/en-us/articles/360007402599-Dependencies-on-monday-com), [monday plans](https://support.monday.com/hc/en-us/articles/115005320209-Available-plan-types-on-Work-Management), [monday pricing details](https://support.monday.com/hc/en-us/articles/4405633151634-Plans-and-pricing-for-monday-com)

5. Productboard gives strategic-layer strengths (objectives, prioritization context, delivery integrations) with practical constraints such as integration slot limits by tier. That matters when sequencing across many delivery streams.  
Source: [Productboard pricing](https://www.productboard.com/pricing/productboard/), [Productboard integrations](https://www.productboard.com/product/integrations/)

6. Aha! plus Jira integration can synchronize estimates and capacity context, but has setup and mode constraints (for example legacy mode and role requirements). Practical implication: "sync exists" does not mean "sync is production-safe" without governance rules.  
Source: [Aha-Jira capacity tracking](https://aha.io/support/roadmaps/integrations/jira/track-capacity-between-aha-and-jira), [Aha capacity planning](https://aha.io/support/develop/develop/aha-roadmaps/capacity-planning)

7. Asana and Smartsheet provide portfolio/capacity/baseline support with meaningful plan boundaries and governance controls (for example baseline ownership). These are viable alternatives, but each needs explicit limitations in planning playbooks.  
Source: [Asana pricing](https://asana.com/pricing), [Asana advanced plan](https://asana.com/plan/advanced), [Smartsheet baselines and critical path](https://help.smartsheet.com/learning-track/project-fundamentals-part-2-project-settings/baselines-and-critical-path), [Smartsheet pricing](https://www.smartsheet.com/pricing)

8. Roadmap risk quality improves when delivery tools are overlaid with release and experiment telemetry (feature flag states, experiment outcomes, behavior analytics). LaunchDarkly, Statsig, and Amplitude integrations with Jira/Productboard make this technically feasible.  
Source: [LaunchDarkly Jira docs](https://docs.launchdarkly.com/integrations/jira), [Statsig Jira docs](https://docs.statsig.com/integrations/jira/), [Amplitude Jira integration](https://amplitude.com/docs/data/integrate-jira), [Amplitude Productboard integration](https://amplitude.com/integrations/productboard)

9. Tool contradiction to preserve: documentation markets broad capability, but practical value is heavily entitlement-, setup-, and process-dependent. The SKILL draft should therefore avoid tool absolutism and encode fallback behavior.

**Sources:**
- [Atlassian plans overview](https://atlassian.com/software/jira/guides/advanced-roadmaps/overview)
- [What is Advanced Roadmaps](https://support.atlassian.com/jira-software-cloud/docs/what-is-advanced-roadmaps/)
- [Jira scenarios](https://support.atlassian.com/jira-software-cloud/docs/what-are-scenarios-in-advanced-roadmaps)
- [Jira pricing](https://www.atlassian.com/software/jira/pricing)
- [Dependencies in Advanced Roadmaps](https://confluence.atlassian.com/jirasoftware/dependencies-in-advanced-roadmaps-1688898866.html)
- [monday dependencies](https://support.monday.com/hc/en-us/articles/360007402599-Dependencies-on-monday-com)
- [monday plans](https://support.monday.com/hc/en-us/articles/115005320209-Available-plan-types-on-Work-Management)
- [monday pricing details](https://support.monday.com/hc/en-us/articles/4405633151634-Plans-and-pricing-for-monday-com)
- [Productboard pricing](https://www.productboard.com/pricing/productboard/)
- [Productboard integrations](https://www.productboard.com/product/integrations/)
- [Aha-Jira capacity tracking](https://aha.io/support/roadmaps/integrations/jira/track-capacity-between-aha-and-jira)
- [Aha capacity planning](https://aha.io/support/develop/develop/aha-roadmaps/capacity-planning)
- [Asana pricing](https://asana.com/pricing)
- [Asana advanced plan](https://asana.com/plan/advanced)
- [Smartsheet baselines and critical path](https://help.smartsheet.com/learning-track/project-fundamentals-part-2-project-settings/baselines-and-critical-path)
- [Smartsheet pricing](https://www.smartsheet.com/pricing)
- [LaunchDarkly Jira docs](https://docs.launchdarkly.com/integrations/jira)
- [Statsig Jira docs](https://docs.statsig.com/integrations/jira/)
- [Amplitude Jira integration](https://amplitude.com/docs/data/integrate-jira)
- [Amplitude Productboard integration](https://amplitude.com/integrations/productboard)

---

### Angle 3: Data Interpretation and Signal Quality
> How to decide whether milestones are valid, dependency risk is acceptable, and learning cadence is sufficient.

**Findings:**

1. Milestone validity is multi-signal, not single-metric. DORA guidance treats software delivery metrics as a system and warns against single metric interpretation. Practical implication: phase gates must require both progress and stability signals.  
Source: [DORA metrics guide](https://dora.dev/guides/dora-metrics-four-keys/), [DORA metrics history](https://dora.dev/guides/dora-metrics/history/)

2. Productivity proxy gains can hide stability regression. Google Cloud's 2024 DORA highlights show positive movement in some AI-related productivity/quality proxies while throughput and stability can decline. Practical implication: "faster output" should not be accepted as sufficient gate evidence.  
Source: [Google Cloud 2024 DORA highlights](https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report)

3. Contradiction to preserve: teams ask for universal thresholds, but DORA framing emphasizes contextual baselines and reference points. Skill logic should encode trend-vs-baseline checks instead of hard universal gates.  
Source: [DORA 2024 report page](https://dora.dev/research/2024/dora-report/)

4. CVSS is severity, not exploit likelihood. CISA notes that only a small portion of CVEs are exploited, but exploited vulnerabilities can be weaponized rapidly. Practical implication: dependency risk decisions should combine severity with exploitation evidence.  
Source: [CISA BOD 22-01 FAQ](https://www.cisa.gov/news-events/directives/bod-22-01-reducing-significant-risk-known-exploited-vulnerabilities)

5. CVSS v4 bins are useful for severity normalization, but cannot substitute threat context. NVD and FIRST guidance support this distinction.  
Source: [NVD CVSS metrics](https://nvd.nist.gov/cvss.cfm), [FIRST CVSS v4 spec](https://www.first.org/cvss/v4-0/specification-document)

6. EPSS thresholds are operating points, not universal standards. FIRST explicitly warns against hard-coded universal cutoff assumptions (for example, 10%). Practical implication: thresholds should be calibrated to risk appetite and remediation capacity.  
Source: [FIRST EPSS model](https://www.first.org/epss/model)

7. NIST LEV (2025) provides a practical composite ranking approach (`max(EPSS, KEV, LEV)`) and highlights that LEV supports prioritization but does not replace confirmed-exploited catalogs. Practical implication: skill-level dependency risk scoring can include this composite logic.  
Source: [NIST CSWP 41 LEV](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.41.pdf)

8. Time-window bias can distort risk interpretation. NIST LEV analysis shows expected exploitation prevalence changes significantly depending on cohort definitions. Practical implication: milestone risk comparisons must normalize observation windows.  
Source: [NIST CSWP 41 LEV](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.41.pdf)

9. Risk scoring methods materially affect ranking outcomes. Oracle Primavera documentation shows how method choices (for example highest impact vs average impact) can shift practical prioritization. Practical implication: risk scoring method must be explicit and stable for cross-phase comparisons.  
Source: [Oracle risk scoring](https://primavera.oraclecloud.com/help/en/user/186844.htm), [Oracle risk matrix template](https://docs.oracle.com/cd/E80480_01/English/user_guides/risk_management_user_guide/90763.htm)

10. Qualitative probability-impact matrices and quantitative simulation can disagree; recent 2024 research recommends quantitative methods (for example Monte Carlo simulation) for high-stakes schedule/cost decisions. Practical implication: gates with large budget or schedule impact should use quantitative validation.  
Source: [Nature portfolio risk paper (2024)](https://www.nature.com/articles/s41599-024-03180-5)

11. Evergreen cadence references remain useful. Scrum Guide (2020) and SAFe Inspect-and-Adapt cadence guidance are older but still canonical for short-loop learning and periodic replanning.  
Source (Evergreen): [Scrum Guide 2020 PDF](https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf), [SAFe Inspect and Adapt](https://scaledagileframework.com/inspect-and-adapt/)

**Sources:**
- [DORA metrics guide](https://dora.dev/guides/dora-metrics-four-keys/)
- [DORA metrics history](https://dora.dev/guides/dora-metrics/history/)
- [Google Cloud 2024 DORA highlights](https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report)
- [DORA 2024 report page](https://dora.dev/research/2024/dora-report/)
- [CISA BOD 22-01 FAQ](https://www.cisa.gov/news-events/directives/bod-22-01-reducing-significant-risk-known-exploited-vulnerabilities)
- [NVD CVSS metrics](https://nvd.nist.gov/cvss.cfm)
- [FIRST CVSS v4 spec](https://www.first.org/cvss/v4-0/specification-document)
- [FIRST EPSS model](https://www.first.org/epss/model)
- [NIST CSWP 41 LEV](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.41.pdf)
- [Oracle risk scoring](https://primavera.oraclecloud.com/help/en/user/186844.htm)
- [Oracle risk matrix template](https://docs.oracle.com/cd/E80480_01/English/user_guides/risk_management_user_guide/90763.htm)
- [Nature portfolio risk paper (2024)](https://www.nature.com/articles/s41599-024-03180-5)
- [Scrum Guide 2020 PDF](https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf) (Evergreen)
- [SAFe Inspect and Adapt](https://scaledagileframework.com/inspect-and-adapt/) (Evergreen)

---

### Angle 4: Failure Modes and Anti-Patterns
> What fails in real MVP roadmapping and how to detect/mitigate it early.

**Findings:**

1. Goal sprawl destroys roadmap focus. Atlassian State of Teams 2024 reports many teams feel pulled in too many directions. Practical detection signal: high parallel objective count with weak "mission-critical" concentration. Mitigation: force explicit top-priority outcome constraints per phase.  
Source: [Atlassian State of Teams 2024](https://www.atlassian.com/blog/state-of-teams-2024)

2. Feature-factory behavior is measurable. Pendo benchmarking shows usage concentration where a small fraction of features drives most clicks, meaning many shipped features add little product value. Detection signal: low concentration in core-feature adoption after release.  
Source: [Pendo product benchmarks 2024](https://www.pendo.io/pendo-blog/product-benchmarks/)

3. Discovery starvation creates late rework. ProductPlan 2024 data indicates many PM teams are delivery-heavy relative to discovery. Detection signal: high delivery effort with low pre-commit evidence quality.  
Source: [ProductPlan 2024 report PDF](https://assets.productplan.com/content/The-2024-State-of-Product-Management-Report.pdf)

4. Leadership-only prioritization weakens validation quality. ProductPlan data shows strong top-down influence patterns in many orgs. Detection signal: roadmap items lacking customer evidence attachments at gate review.  
Source: [ProductPlan 2024 report PDF](https://assets.productplan.com/content/The-2024-State-of-Product-Management-Report.pdf)

5. Weak triad research participation is a recurring feasibility trap. ProductPlan highlights low rates of PM + design + engineering joint research. Detection signal: milestone proposals without cross-functional feasibility notes.  
Source: [ProductPlan 2024 report PDF](https://assets.productplan.com/content/The-2024-State-of-Product-Management-Report.pdf)

6. Priority thrash correlates with productivity loss and burnout. DORA 2024 emphasizes instability costs. Detection signal: frequent re-prioritization outside planned windows and rising unplanned work.  
Source: [DORA 2024 report PDF](https://services.google.com/fh/files/misc/2024_final_dora_report.pdf)

7. Large-batch delivery increases instability and rework risk. DORA 2024 supports small-batch flow for better stability. Detection signal: larger change bundles with rising incident/churn rates.  
Source: [DORA 2024 report PDF](https://services.google.com/fh/files/misc/2024_final_dora_report.pdf)

8. Rollout gating can fail when risky paths are untested. Google Cloud's June 2025 incident describes broad disruption linked to rollout and validation gaps on specific execution paths. Detection signal: no canary evidence on risky code paths before full rollout.  
Source: [Google Cloud incident report (June 2025)](https://status.cloud.google.com/incidents/ow5i3PPK96RduMcb1SsW)

9. Validation-layer mismatch can bypass test pipelines. CrowdStrike's 2024 RCA documents parameter mismatch and testing blind spots with severe consequences. Detection signal: schema/validator/runtime assumptions are not asserted consistently in deployment checks.  
Source: [CrowdStrike RCA PDF 2024](https://www.crowdstrike.com/wp-content/uploads/2024/08/Channel-File-291-Incident-Root-Cause-Analysis-08.06.2024.pdf)

10. Unsafe configuration deployment sequencing causes avoidable outages and delays. GitHub 2024 availability reports include configuration/environment sequencing issues. Detection signal: config changes without strict environment guardrails or tested rollback paths.  
Source: [GitHub availability report March 2024](https://github.blog/2024-04-10-github-availability-report-march-2024/), [GitHub availability report September 2024](https://github.blog/news-insights/company-news/github-availability-report-september-2024)

11. GTM and integration readiness gaps can sink roadmap economics even with product progress. A 2026 founder postmortem describes feature expansion without viable distribution/unit economics. Detection signal: roadmap growth scope increases while channel economics remain unresolved.  
Source: [Founder postmortem 2026](https://glassboxmedicine.com/2026/02/21/why-i-shut-down-my-bootstrapped-health-ai-startup-after-7-years-a-founders-postmortem/)

**Sources:**
- [Atlassian State of Teams 2024](https://www.atlassian.com/blog/state-of-teams-2024)
- [Pendo product benchmarks 2024](https://www.pendo.io/pendo-blog/product-benchmarks/)
- [ProductPlan 2024 report PDF](https://assets.productplan.com/content/The-2024-State-of-Product-Management-Report.pdf)
- [DORA 2024 report PDF](https://services.google.com/fh/files/misc/2024_final_dora_report.pdf)
- [Google Cloud incident report (June 2025)](https://status.cloud.google.com/incidents/ow5i3PPK96RduMcb1SsW)
- [CrowdStrike RCA PDF 2024](https://www.crowdstrike.com/wp-content/uploads/2024/08/Channel-File-291-Incident-Root-Cause-Analysis-08.06.2024.pdf)
- [GitHub availability report March 2024](https://github.blog/2024-04-10-github-availability-report-march-2024/)
- [GitHub availability report September 2024](https://github.blog/news-insights/company-news/github-availability-report-september-2024)
- [Founder postmortem 2026](https://glassboxmedicine.com/2026/02/21/why-i-shut-down-my-bootstrapped-health-ai-startup-after-7-years-a-founders-postmortem/)

---

### Angle 5+: Governance and Operating Model Signals
> Domain-specific add-on: governance design that keeps conditional roadmaps actionable.

**Findings:**

1. Cross-functional ownership consistently appears in stronger outcome performance narratives, while single-function ownership underperforms.  
Source: [Gartner survey coverage (Business Wire, 2024)](https://www.businesswire.com/news/home/20241022615512/en/Gartner-Survey-Reveals-That-Only-48-of-Digital-Initiatives-Meet-or-Exceed-Their-Business-Outcome-Targets)

2. Product Ops coverage without measurement rigor leaves blind spots in roadmap quality assurance.  
Source: [Productboard State of Product Ops 2025](https://www.productboard.com/blog/the-state-of-product-ops-in-2025/)

3. Stable cadence governance (short execution loops + periodic replanning) is repeatedly represented as a predictor of better adaptation quality in both agile and scaled frameworks.  
Source: [SAFe PI Planning](https://scaledagileframework.com/PI-planning), [SAFe Inspect and Adapt](https://scaledagileframework.com/inspect-and-adapt/), [Scrum Guide 2020 PDF](https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf) (Evergreen)

4. Governance contradiction to preserve: heavy process can reduce responsiveness if not paired with explicit adaptation windows. Therefore, this skill should encode when re-planning is allowed and when scope changes are frozen.

**Sources:**
- [Gartner survey coverage (Business Wire, 2024)](https://www.businesswire.com/news/home/20241022615512/en/Gartner-Survey-Reveals-That-Only-48-of-Digital-Initiatives-Meet-or-Exceed-Their-Business-Outcome-Targets)
- [Productboard State of Product Ops 2025](https://www.productboard.com/blog/the-state-of-product-ops-in-2025/)
- [SAFe PI Planning](https://scaledagileframework.com/PI-planning)
- [SAFe Inspect and Adapt](https://scaledagileframework.com/inspect-and-adapt/)
- [Scrum Guide 2020 PDF](https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf) (Evergreen)

---

## Synthesis

The strongest conclusion is that modern MVP-to-scale roadmapping is less about producing a bigger plan and more about maintaining evidence quality under uncertainty. Sources across ProductPlan, Atlassian, and DORA align on the same practical pattern: teams are adopting outcome language, but many still struggle to allocate enough strategy/discovery time and maintain stable learning loops.

Tooling is mature enough to support high-quality sequencing, but only when teams account for entitlement and governance constraints. Jira Plans, monday, Productboard, Aha, Asana, and Smartsheet all provide relevant capabilities, yet each has tier boundaries and setup caveats that materially affect risk visibility. The skill should therefore encode capability checks and fallback logic, not "tool X always solves Y."

Risk interpretation quality is the most critical technical gap. Findings from DORA, CISA, FIRST, NIST LEV, Oracle, and 2024 quantitative risk research show that weak interpretation habits (single metric gates, CVSS-only decisions, unnormalized risk comparisons, qualitative-only matrices) create false confidence. This means gate decisions should explicitly require multi-signal evidence and method transparency.

Failure-mode evidence from incident reports and benchmark datasets is unusually actionable. Anti-patterns like goal sprawl, discovery starvation, large-batch releases, and validation-layer mismatch have clear detection signals and repeatable mitigation steps. Embedding these warning blocks directly in SKILL.md will materially improve output quality and reduce naive "feature list roadmap" behavior.

The biggest contradiction to keep visible in the final skill text is this: teams want predictability and adaptability at the same time. The practical answer in current evidence is a dual structure - committed near-term phases plus conditional forecast phases - with strict evidence gates and scheduled replanning windows.

---

## Recommendations for SKILL.md

> Concrete, actionable changes based on findings.

- [x] Add a strict conditional commitment policy: only one phase is committed at a time; downstream phases remain forecast until gate pass.
- [x] Add a mandatory gate evidence pack schema (outcome, delivery health, dependency risk, learning cadence) and GO/HOLD/NO_GO decisions.
- [x] Add explicit cadence instructions (execution loop and strategy review loop) with priority-freeze/replan windows.
- [x] Upgrade dependency risk interpretation from qualitative-only to method-explicit scoring with optional quantitative validation for high-stakes gates.
- [x] Add entitlement-aware tool guidance so roadmap quality does not depend on unavailable premium features.
- [x] Add anti-pattern warning blocks with detection signal, consequence, and mitigation steps.
- [x] Expand artifact schema to include gate decisions, evidence bundles, normalized risk metadata, and source references.
- [x] Require cross-functional gate ownership (product, engineering, design/business) for phase transition validity.

---

## Draft Content for SKILL.md

### Draft: Core operating principle (replace intro and core mode)

You build a conditional roadmap from MVP to scale-ready product. The roadmap is a sequence of bets, not a fixed feature list. A phase is committed only when the previous phase has passed gate criteria with evidence. If gate evidence is incomplete or contradictory, you do not commit the next phase.

Use this default commitment rule:
1. Commit exactly one active phase (the one currently funded and executed).
2. Keep the next one to two phases as forecast only.
3. Re-evaluate forecast phases at each gate review; do not treat forecast as commitment.
4. If pressure demands long-range certainty, surface uncertainty explicitly instead of fabricating confidence.

Roadmap quality is defined by evidence quality:
- Outcome signal quality (customer/business movement),
- Delivery health quality (stability + throughput trend),
- Dependency risk quality (method and assumptions explicit),
- Learning cadence quality (how often hypotheses are tested and decisions updated).

If any of these quality dimensions is weak, the roadmap is high risk even when milestone dates look clean.

### Draft: Methodology - Evidence-gated phase flow

Before drafting phase details, activate policy context and identify the active hypothesis stack. You should not author milestones before confirming what hypothesis each milestone is intended to test.

Method:
1. Define phase hypothesis.
   - For every phase, write one clear hypothesis in testable form.
   - Include expected customer or business movement and expected delivery constraints.
   - If the hypothesis is not falsifiable, rewrite it before planning.
2. Define gate criteria by signal type.
   - For each phase, include at least one leading indicator and one lagging indicator.
   - Include at least one delivery health check and one dependency risk check.
   - Do not accept a gate that only measures shipped output.
3. Define commitment and adaptation windows.
   - Commitment window: scope is stable except for risk mitigation.
   - Adaptation window: scope can be re-prioritized based on evidence.
   - Declare both windows in the roadmap artifact so stakeholders know when changes are allowed.
4. Run gate review and assign decision.
   - `go`: evidence meets threshold with no critical contradiction.
   - `hold`: evidence incomplete or contradictory; run focused learning actions.
   - `no_go`: evidence disproves hypothesis or risk is above accepted appetite.
5. Update downstream phases conditionally.
   - On `go`, refine next phase and keep farther phases as forecast.
   - On `hold`, preserve committed work and schedule targeted evidence collection.
   - On `no_go`, de-scope or pivot before any new commitment.

Decision rules you must apply:
- If you only have productivity/output gains but stability is worsening, do not call the milestone valid.
- If dependency risk is assessed with severity-only data (for example CVSS-only), mark risk evidence as insufficient and keep gate on hold.
- If risk scores across teams/phases use different methods, normalize or avoid direct comparison.
- If the team cannot explain why a threshold exists, treat it as provisional and request calibration from baseline data.

### Draft: Updated phase structure text

Use this phase model as default:

**Phase 0: Pre-MVP (optional but recommended for high-uncertainty ideas)**
- Objective: validate core problem-value hypothesis with minimal build.
- Typical mode: concierge/manual/fake-door/research prototype.
- Gate requirement: explicit go/no-go memo tied to customer evidence.

**Phase 1: MVP**
- Objective: prove that core job can be completed by target early users.
- Scope rule: must-have only, no growth optimizations unless required for validity.
- Gate requirement: initial validation criteria from `mvp_validation_criteria` plus minimum delivery-health checks.

**Phase 2: Validated MVP**
- Objective: remove top friction points and verify repeatable value for early paying users.
- Scope rule: prioritize retention and activation fixes before expansion features.
- Gate requirement: retention trend and dependency-risk profile support controlled expansion.

**Phase 3: Growth-ready**
- Objective: establish repeatable acquisition/onboarding and improve unit economics.
- Scope rule: expansion features only if they directly improve acquisition efficiency or retention depth.
- Gate requirement: stable delivery profile, controlled dependency risk, and positive evidence for growth mechanics.

**Phase 4: Scale**
- Objective: scale reliability, compliance, and multi-segment execution without losing economics.
- Scope rule: enterprise/compliance/globalization features are justified by validated demand and operational readiness.
- Gate requirement: economics and delivery stability remain acceptable under increased complexity.

Phase transition policy:
- You may define dates, but dates are conditional on gate pass.
- If stakeholders ask for unconditional date commitments beyond active phase, return a forecast range with uncertainty notes.

### Draft: Cadence and governance instructions

You must run two cadences in parallel:

1. Execution cadence (short loop):
   - Weekly to biweekly evidence updates for active phase.
   - Focus: signal movement, blocked dependencies, and delivery health drift.
2. Strategy cadence (longer loop):
   - 4-12 week roadmap review cycle.
   - Focus: gate decision, re-prioritization window, and forecast phase updates.

Governance rules:
- Gate decisions require cross-functional owners (at minimum product + engineering; include design/business as available).
- Re-prioritization outside adaptation windows is allowed only for critical risk mitigation.
- Every gate review must log assumptions that remain unvalidated.
- If assumptions accumulate without testing, reduce forward commitment horizon.

### Draft: Tool usage section (paste-ready, real method syntax)

Always load strategic inputs before writing the roadmap artifact:

```python
flexus_policy_document(op="activate", args={"p": "/strategy/mvp-scope"})
flexus_policy_document(op="activate", args={"p": "/strategy/mvp-validation-criteria"})
flexus_policy_document(op="activate", args={"p": "/strategy/mvp-feasibility"})
flexus_policy_document(op="activate", args={"p": "/strategy/hypothesis-stack"})
```

Then write the roadmap artifact with gate evidence, not only phase names and features:

```python
write_artifact(
    artifact_type="product_roadmap",
    path="/strategy/roadmap",
    data={
        "created_at": "2026-03-04T00:00:00Z",
        "product_name": "Example Product",
        "roadmap_mode": "conditional_only",
        "phases": [
            {
                "phase_id": "mvp",
                "phase_name": "MVP",
                "goal": "Validate core job completion for early users",
                "hypothesis": "If core flow is simplified, activation and repeat use improve",
                "duration_estimate_weeks": 8,
                "gate_decision": "hold",
                "gate_criteria": [],
                "evidence_bundle": {},
                "dependencies": [],
                "features": [],
                "resource_commitment": {
                    "budget_window_months": 3,
                    "team_fte": 4
                }
            }
        ]
    },
)
```

Tool usage guidance:
- Do not write `/strategy/roadmap` before all required policy docs are activated.
- If a required policy document is missing, explicitly mark related gate criteria as unknown and use `hold`.
- Re-write the artifact at each gate review; do not leave stale gate decisions in place.

### Draft: Entitlement-aware tool guidance block

If external roadmap systems are used as input signals (for example Jira Plans, monday, Productboard, Aha, Asana, Smartsheet), verify capability availability before interpreting missing data as "no risk."

Entitlement checks to apply:
- If scenario modeling or cross-project dependency views are tier-locked and unavailable, mark dependency confidence as reduced.
- If integration slots are limited, declare which streams are not represented in evidence.
- If capacity sync is partially configured, treat effort estimates as provisional.

When capability is missing:
1. Record the limitation in assumptions.
2. Reduce commitment horizon.
3. Increase gate review frequency until observability is restored.

### Draft: Anti-pattern warning blocks

> **WARNING: Goal Sprawl**
> - Detection signal: too many simultaneous objectives, weak concentration on mission-critical work.
> - Consequence: roadmap thrash and low milestone validity.
> - Mitigation: freeze net-new goals, re-rank by outcome impact, and resume only after explicit top-priority selection.

> **WARNING: Feature Factory Drift**
> - Detection signal: low concentration of usage in recently shipped features, poor adoption of "must-have" items.
> - Consequence: capacity consumed by low-value output and rising maintenance debt.
> - Mitigation: stop adding net-new features, run adoption diagnosis, remove low-signal scope from next phase.

> **WARNING: Discovery Starvation**
> - Detection signal: delivery work dominates while customer evidence is thin at gate review.
> - Consequence: late pivots, expensive rework, invalid phase commitments.
> - Mitigation: block phase exit until customer evidence and hypothesis test results are attached.

> **WARNING: Leadership-Only Prioritization**
> - Detection signal: milestone selection is mainly top-down with weak customer signal.
> - Consequence: roadmap confidence is political, not empirical.
> - Mitigation: require customer-backed evidence for every committed milestone.

> **WARNING: Priority Thrash**
> - Detection signal: frequent reprioritization outside declared adaptation windows.
> - Consequence: throughput collapse, burnout increase, unstable outcomes.
> - Mitigation: enforce freeze windows and allow exceptions only for critical risk containment.

> **WARNING: Large-Batch Milestone**
> - Detection signal: broad scope bundles with rising unplanned fixes and change-failure symptoms.
> - Consequence: unstable delivery and false confidence in progress.
> - Mitigation: split into smaller increments and tighten quality gates before next transition.

> **WARNING: CVSS-Only Dependency Risk**
> - Detection signal: dependency priority is based only on severity labels.
> - Consequence: real exploit risk is mis-ranked, urgent exposures can be missed.
> - Mitigation: combine severity with exploitation evidence and document scoring method.

> **WARNING: Rollout Path Untested**
> - Detection signal: high-risk code paths or config paths are not validated under staged rollout conditions.
> - Consequence: incident blast radius at launch.
> - Mitigation: require staged rollout evidence and rollback criteria before GO.

### Draft: Gate decision protocol block

Use this protocol for every phase gate:

1. Validate evidence completeness.
   - All required signal groups are present: outcome, delivery health, dependency risk, learning cadence.
   - Missing groups force `hold` unless explicit emergency override is justified.
2. Validate evidence quality.
   - Metrics include measurement window and source reference.
   - Risk method is declared (qualitative, quantitative, or hybrid).
3. Evaluate contradictions.
   - If leading and lagging indicators conflict, classify as unresolved contradiction and set `hold`.
4. Assign gate decision.
   - `go`: criteria met, contradictions resolved, no critical unresolved risk.
   - `hold`: partial signal quality or unresolved contradictions.
   - `no_go`: hypothesis disproven or risk above appetite.
5. Write decision rationale.
   - Capture why this decision was made and what evidence would change it.

### Draft: Schema additions

Use the following schema fragment to upgrade the `product_roadmap` artifact for evidence-gated planning:

```json
{
  "product_roadmap": {
    "type": "object",
    "required": [
      "created_at",
      "product_name",
      "roadmap_mode",
      "cadences",
      "phases"
    ],
    "additionalProperties": false,
    "properties": {
      "created_at": {
        "type": "string",
        "description": "ISO-8601 timestamp when this roadmap snapshot was produced."
      },
      "product_name": {
        "type": "string",
        "description": "Human-readable product name."
      },
      "roadmap_mode": {
        "type": "string",
        "enum": [
          "conditional_only"
        ],
        "description": "Planning mode. conditional_only means only active phase is committed."
      },
      "cadences": {
        "type": "object",
        "required": [
          "execution_review_weeks",
          "strategy_review_weeks",
          "replan_window_rule"
        ],
        "additionalProperties": false,
        "properties": {
          "execution_review_weeks": {
            "type": "integer",
            "minimum": 1,
            "maximum": 4,
            "description": "Frequency of evidence updates for active phase."
          },
          "strategy_review_weeks": {
            "type": "integer",
            "minimum": 4,
            "maximum": 12,
            "description": "Frequency of phase gate and roadmap replan decisions."
          },
          "replan_window_rule": {
            "type": "string",
            "description": "Text rule describing when reprioritization is allowed."
          }
        }
      },
      "phases": {
        "type": "array",
        "minItems": 1,
        "items": {
          "type": "object",
          "required": [
            "phase_id",
            "phase_name",
            "goal",
            "hypothesis",
            "duration_estimate_weeks",
            "gate_decision",
            "gate_criteria",
            "evidence_bundle",
            "dependencies",
            "features",
            "resource_commitment"
          ],
          "additionalProperties": false,
          "properties": {
            "phase_id": {
              "type": "string",
              "description": "Stable phase identifier."
            },
            "phase_name": {
              "type": "string",
              "description": "Readable phase label."
            },
            "goal": {
              "type": "string",
              "description": "Outcome-oriented objective for this phase."
            },
            "hypothesis": {
              "type": "string",
              "description": "Falsifiable statement tested by this phase."
            },
            "duration_estimate_weeks": {
              "type": "number",
              "minimum": 1,
              "description": "Estimated duration for phase execution."
            },
            "gate_decision": {
              "type": "string",
              "enum": [
                "go",
                "hold",
                "no_go",
                "not_reviewed"
              ],
              "description": "Most recent gate outcome for this phase."
            },
            "gate_criteria": {
              "type": "array",
              "minItems": 1,
              "items": {
                "type": "object",
                "required": [
                  "criterion_id",
                  "criterion_type",
                  "criterion",
                  "threshold",
                  "must_pass"
                ],
                "additionalProperties": false,
                "properties": {
                  "criterion_id": {
                    "type": "string",
                    "description": "Stable ID for traceability."
                  },
                  "criterion_type": {
                    "type": "string",
                    "enum": [
                      "outcome",
                      "delivery_health",
                      "dependency_risk",
                      "learning_cadence",
                      "commercial",
                      "compliance"
                    ],
                    "description": "Signal family this criterion belongs to."
                  },
                  "criterion": {
                    "type": "string",
                    "description": "Human-readable criterion definition."
                  },
                  "threshold": {
                    "type": "string",
                    "description": "Expected threshold expression or condition."
                  },
                  "must_pass": {
                    "type": "boolean",
                    "description": "Whether failing this criterion blocks GO."
                  }
                }
              }
            },
            "evidence_bundle": {
              "type": "object",
              "required": [
                "outcome_signals",
                "delivery_health",
                "dependency_risk",
                "learning_cadence"
              ],
              "additionalProperties": false,
              "properties": {
                "outcome_signals": {
                  "type": "array",
                  "minItems": 1,
                  "items": {
                    "type": "object",
                    "required": [
                      "metric_name",
                      "metric_type",
                      "current_value",
                      "target_value",
                      "measurement_window",
                      "source_ref"
                    ],
                    "additionalProperties": false,
                    "properties": {
                      "metric_name": {
                        "type": "string",
                        "description": "Name of outcome metric."
                      },
                      "metric_type": {
                        "type": "string",
                        "enum": [
                          "leading",
                          "lagging"
                        ],
                        "description": "Signal role for this metric."
                      },
                      "current_value": {
                        "type": "string",
                        "description": "Current measured value as reported."
                      },
                      "target_value": {
                        "type": "string",
                        "description": "Target required for gate."
                      },
                      "measurement_window": {
                        "type": "string",
                        "description": "Time window used for this measurement."
                      },
                      "source_ref": {
                        "type": "string",
                        "description": "Reference to source report or system."
                      }
                    }
                  }
                },
                "delivery_health": {
                  "type": "object",
                  "required": [
                    "throughput_trend",
                    "stability_trend",
                    "change_failure_signal"
                  ],
                  "additionalProperties": false,
                  "properties": {
                    "throughput_trend": {
                      "type": "string",
                      "enum": [
                        "improving",
                        "flat",
                        "degrading"
                      ],
                      "description": "Direction of delivery throughput vs baseline."
                    },
                    "stability_trend": {
                      "type": "string",
                      "enum": [
                        "improving",
                        "flat",
                        "degrading"
                      ],
                      "description": "Direction of stability vs baseline."
                    },
                    "change_failure_signal": {
                      "type": "string",
                      "description": "Narrative or metric summary for failure behavior."
                    }
                  }
                },
                "dependency_risk": {
                  "type": "object",
                  "required": [
                    "method",
                    "normalization_scope",
                    "risk_items"
                  ],
                  "additionalProperties": false,
                  "properties": {
                    "method": {
                      "type": "string",
                      "enum": [
                        "qualitative_matrix",
                        "quantitative_simulation",
                        "hybrid"
                      ],
                      "description": "Method used to rank dependency risks."
                    },
                    "normalization_scope": {
                      "type": "string",
                      "enum": [
                        "phase",
                        "program"
                      ],
                      "description": "Scope used to normalize comparable risk scores."
                    },
                    "risk_items": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "required": [
                          "risk_id",
                          "title",
                          "probability",
                          "impact_schedule",
                          "impact_cost",
                          "score",
                          "status",
                          "mitigation"
                        ],
                        "additionalProperties": false,
                        "properties": {
                          "risk_id": {
                            "type": "string",
                            "description": "Stable risk identifier."
                          },
                          "title": {
                            "type": "string",
                            "description": "Short risk title."
                          },
                          "probability": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "description": "Estimated probability (0..1)."
                          },
                          "impact_schedule": {
                            "type": "string",
                            "description": "Expected schedule impact if risk materializes."
                          },
                          "impact_cost": {
                            "type": "string",
                            "description": "Expected cost impact if risk materializes."
                          },
                          "score": {
                            "type": "number",
                            "description": "Calculated score based on declared method."
                          },
                          "status": {
                            "type": "string",
                            "enum": [
                              "open",
                              "watch",
                              "mitigating",
                              "closed"
                            ],
                            "description": "Current treatment status."
                          },
                          "mitigation": {
                            "type": "string",
                            "description": "Current mitigation plan."
                          }
                        }
                      }
                    }
                  }
                },
                "learning_cadence": {
                  "type": "object",
                  "required": [
                    "review_frequency_days",
                    "experiments_completed",
                    "decision_log_ref"
                  ],
                  "additionalProperties": false,
                  "properties": {
                    "review_frequency_days": {
                      "type": "integer",
                      "minimum": 1,
                      "description": "How often evidence is reviewed."
                    },
                    "experiments_completed": {
                      "type": "integer",
                      "minimum": 0,
                      "description": "Number of completed experiments in measurement window."
                    },
                    "decision_log_ref": {
                      "type": "string",
                      "description": "Reference to decision log or gate memo."
                    }
                  }
                }
              }
            },
            "dependencies": {
              "type": "array",
              "items": {
                "type": "object",
                "required": [
                  "dependency_id",
                  "kind",
                  "owner",
                  "status"
                ],
                "additionalProperties": false,
                "properties": {
                  "dependency_id": {
                    "type": "string",
                    "description": "Stable dependency identifier."
                  },
                  "kind": {
                    "type": "string",
                    "enum": [
                      "incoming",
                      "outgoing"
                    ],
                    "description": "Direction relative to this phase."
                  },
                  "owner": {
                    "type": "string",
                    "description": "Owning team or function."
                  },
                  "status": {
                    "type": "string",
                    "enum": [
                      "clear",
                      "at_risk",
                      "blocked"
                    ],
                    "description": "Current dependency health state."
                  }
                }
              }
            },
            "features": {
              "type": "array",
              "items": {
                "type": "object",
                "required": [
                  "feature",
                  "priority",
                  "rationale"
                ],
                "additionalProperties": false,
                "properties": {
                  "feature": {
                    "type": "string",
                    "description": "Feature or capability name."
                  },
                  "priority": {
                    "type": "string",
                    "enum": [
                      "must_have",
                      "should_have",
                      "nice_to_have"
                    ],
                    "description": "Priority class for phase execution."
                  },
                  "rationale": {
                    "type": "string",
                    "description": "Reason this item belongs in this phase."
                  }
                }
              }
            },
            "resource_commitment": {
              "type": "object",
              "required": [
                "budget_window_months",
                "team_fte"
              ],
              "additionalProperties": false,
              "properties": {
                "budget_window_months": {
                  "type": "number",
                  "minimum": 1,
                  "description": "Funding commitment window for this phase."
                },
                "team_fte": {
                  "type": "number",
                  "minimum": 0.5,
                  "description": "Planned full-time-equivalent team size."
                }
              }
            }
          }
        }
      },
      "source_references": {
        "type": "array",
        "description": "External or internal references used in gate decisions.",
        "items": {
          "type": "string"
        }
      }
    }
  }
}
```

### Draft: Short rationale block for the skill author (optional include)

This skill enforces evidence-gated roadmap progression because current product and engineering evidence shows a consistent failure pattern: teams overcommit scope before evidence quality is sufficient. By separating committed phases from forecast phases, requiring mixed signal quality at gates, and forcing explicit risk method declarations, you reduce false confidence and improve decision quality without abandoning delivery cadence.

---

## Gaps and Uncertainties

- Public sources provide strong directional evidence, but many benchmark metrics are self-reported and should be treated as guidance rather than universal thresholds.
- Several tool capability pages are living docs without explicit publication dates; they were prioritized only when functionality was directly documented and cross-checked.
- Incident postmortems are high-value for failure patterns but can overrepresent extreme events; additional medium-severity case studies would improve calibration.
- There is no single universal numeric gate threshold set that is valid across all product contexts; this is why the draft recommends baseline-relative thresholds and explicit calibration.
- More direct 2026 peer-reviewed research on product roadmap governance (outside platform/vendor reports) appears limited at the time of writing.
