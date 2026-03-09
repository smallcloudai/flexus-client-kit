# Research: discovery-recruitment

**Skill path:** `flexus-client-kit/flexus_simple_bots/researcher/skills/discovery-recruitment/`
**Bot:** researcher
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`discovery-recruitment` is responsible for recruiting the right participants for surveys, interviews, and usability studies, then keeping recruitment quality defensible from invite through completion. The existing `SKILL.md` has a useful baseline (inclusion/exclusion criteria, quota cells, funnel tracking, and platform-specific calls), but it needs stronger grounding in 2024-2026 operational guidance and official API realities.

The highest-risk failure in this domain is false signal from poor participant fit or contaminated sample quality. Recruitment success is not just speed or low CPI. It is the combination of feasibility realism, screener anti-gaming design, quota execution, live funnel monitoring, fraud resistance, and transparent approval/rejection logic.

This research synthesizes five angles: methodology, tool/provider landscape, API endpoint reality, funnel interpretation thresholds, and anti-patterns/compliance. The `Draft Content for SKILL.md` section is intentionally the largest section and written as paste-ready replacement text for future editing.

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

- Practitioners now run recruitment as a staged operations loop, not a single launch: `feasibility -> quota design -> screener hardening -> pilot -> scale -> live QA -> adjudication`.
- Feasibility checks are used before locking recruitment assumptions. Prolific eligibility counts and Cint feasibility estimates are operationally treated as planning constraints, not optional diagnostics.
- Quota design has become more explicit and structured. Prolific expanded quota controls in 2025 (including larger strata support), and Cint guidance emphasizes quota totals aligned with target completes and incidence assumptions.
- Screeners are now designed with anti-gaming tactics by default: non-leading wording, non-binary options where possible, no obvious "correct answer" hints, and occasional dummy-option validation in high-risk recruitment.
- Soft-launch/pilot expectations are explicit in multiple ecosystems: run small initial cohorts and validate end-to-end pathing before scaling spend.
- Incentives are treated as a quality control variable, not only an ethics decision. Underpayment increases low-effort behavior and fill instability; over-salient public incentives can attract fraud attacks.
- Real-time funnel telemetry is increasingly standard: teams track progression and quality status by source while field is live instead of postponing QA until after close.
- Repeat-participant controls are used to reduce conditioning and contamination in ongoing programs (for example freshness windows and exclusion filters for prior participation).
- Fraud prevention is layered; single controls are insufficient. 2024-2025 evidence repeatedly shows hybrid attacks can pass shallow checks.
- Moderated/interview planning incorporates no-show expectations in staffing math; recent analyses indicate conservative planning around ~10% remains practical.
- Sample-size recommendations vary materially by method and vendor context; best practice is method-specific targets and explicit tradeoff documentation, not one universal number.
- Contradiction handling should be explicit in methodology: faster fill and tighter quality controls are naturally in tension; the skill should encode this as a decision tradeoff, not a hidden side effect.

**Sources:**
- [Prolific eligibility count](https://docs.prolific.com/api-reference/filters/get-eligible-count)
- [Prolific quota distribution with filters](https://docs.prolific.com/api-reference/filters/study-distribution-quotas-with-filters)
- [Prolific product update (2025 quotas/screening/quality)](https://www.prolific.com/resources/what-s-new-expanded-quotas-in-study-screening-and-smarter-quality-controls)
- [Cint creating a survey](https://help.cint.com/docs/creating-a-new-survey)
- [Cint launching a study](https://help.cint.com/docs/launching-a-study)
- [UserTesting screener best practices](https://help.usertesting.com/hc/articles/11880418598557-Screener-questions-Best-practices)
- [UserTesting avoid impostor participants](https://help.usertesting.com/hc/en-us/articles/13523886870429-Avoid-and-handle-impostor-participants-UserTesting)
- [UserTesting best practices](https://help.usertesting.com/hc/en-us/articles/11880426022813-UserTesting-best-practices)
- [UserTesting recruiting difficulties](https://help.usertesting.com/hc/en-us/articles/11880395269917-Solutions-for-participant-recruiting-difficulties)
- [UserTesting Fresh Eyes/repeat controls](https://help.usertesting.com/hc/en-us/articles/11880451613341-Fresh-eyes-and-test-filters-to-manage-repeat-participants)
- [MeasuringU no-show rate analysis (2024)](https://measuringu.com/typical-no-show-rate-for-moderated-studies/)
- [MTurk best practices (evergreen)](https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMechanicalTurkRequester/IntroBestPractices.html)

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

- Prolific is strong for high-control survey and experiment recruiting with explicit filtering, screener support, and quota logic. Public pricing and pay-floor guidance are clear.
- Cint is strong for high-volume/global panel operations with advanced qualification and reconciliation processes, but operational complexity is higher and buyer setup quality matters.
- MTurk remains cost-flexible and programmable but pushes more quality risk and QA burden onto the requester.
- UserTesting is strongest for usability testing operations (moderated/unmoderated plus participant network modes), with plan/meter constraints that affect screener and capacity behavior.
- User Interviews and Respondent are useful interview-centric complements (especially B2B/professional recruiting) with transparent session-fee framing.
- Provider fit changes by study type: survey-heavy runs usually favor Prolific/Cint; interview recruiting often favors User Interviews/Respondent; usability workflows generally favor UserTesting.
- Cost comparisons can be misleading when QA overhead is ignored. Low platform fee does not guarantee lower total study cost.
- Vendor docs increasingly distinguish workflow convenience from sample-control depth; selecting providers by convenience alone can reduce evidence quality.

**Provider comparison (operational view):**

| Provider | Best for | Strength | Limitation | Public cost signal |
|---|---|---|---|---|
| Prolific | Structured survey/experiment recruit | Filters, quota controls, custom screening, transparent pay guidance | Platform fee can be higher than budget marketplaces | Platform fee + participant reward model published |
| Cint | Large/global quota-heavy studies | Broad panel reach, profiling/qualification depth, reconciliation framework | Setup complexity; stricter operational discipline required | CPI and dynamic pricing terms |
| MTurk | Cost-sensitive large-volume tasks/surveys | Flexible qualification and assignment controls | Requester must own stronger QA and fraud controls | Fee schedule publicly documented |
| UserTesting | Usability studies | Built-in UX testing workflows and networks | Plan/session-unit constraints, tier-dependent limits | Quote-based plus documented session-unit behavior |
| User Interviews | Interview recruiting | Scheduling + incentive workflows, B2B options | Session fee + incentive economics can rise quickly | Public session pricing and support docs |
| Respondent | Professional interview recruiting | Interview-centric sourcing and payout flow | Less public depth on some operational internals | Public plan/session pricing |

**Sources:**
- [Prolific pricing](https://www.prolific.com/pricing)
- [Prolific calculator](https://www.prolific.com/calculator)
- [Prolific update (2025)](https://www.prolific.com/resources/what-s-new-expanded-quotas-in-study-screening-and-smarter-quality-controls)
- [Cint profiling guide](https://help.cint.com/docs/marketplace-profiling-guide)
- [Cint reconciliation policy](https://legal.cint.com/docs/cint-exchange-reconciliation-policy)
- [Cint dynamic pricing terms (v2025/01)](https://legal.cint.com/docs/cint-exchange-dynamic-pricing-terms-v2025-01)
- [MTurk requester pricing](https://requester.mturk.com/pricing)
- [MTurk qualification management (evergreen)](https://docs.aws.amazon.com/AWSMechTurk/latest/RequesterUI/ManagingQualificationTypes.html)
- [UserTesting participant recruitment options](https://help.usertesting.com/hc/en-us/articles/11880367247773-Participant-recruitment-options)
- [UserTesting contributor networks comparison](https://help.usertesting.com/hc/en-us/articles/11880363907613-Contributor-networks-comparison-table)
- [UserTesting screener limits for surveys](https://help.usertesting.com/hc/en-us/articles/17801359137565-Screener-questions-for-UserTesting-surveys)
- [UserTesting session rate card](https://help.usertesting.com/hc/en-us/articles/11880342055965-Session-rate-card)
- [User Interviews pricing](https://www.userinterviews.com/pricing)
- [User Interviews subscription pricing update (2026)](https://www.userinterviews.com/support/subscription-pricing)
- [Respondent pricing](https://www.respondent.io/pricing)

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

- Incidence rate (`started -> qualified`) is a first-order feasibility signal. Recent guidance provides explicit IR bands and links lower IR with higher cost, slower fielding, and representativeness pressure.
- Completion health needs explicit monitoring thresholds. Quality platforms and practitioner docs provide practical non-completion risk bands and suggest evaluating after enough completed volume exists.
- Instrument design materially changes completion behavior. Length and early question format influence dropout and should be incorporated into forecasted recruitment load.
- Speeding and careless-response detection should use multiple checks, not a single threshold. Sources show both statistical and practical thresholding approaches.
- Over-cleaning is itself a failure mode: strict exclusion can remove large portions of data with limited benchmark gains while introducing demographic skew.
- Duplicate participation and cross-source overlap remain realistic operational risks; absence of topline movement does not remove inference risk from non-independence.
- Quota imbalance should be tested, not eyeballed. SRM-style diagnostics can be adapted to recruitment assignment and quota distribution anomalies.
- Subgroup claims from opt-in samples require caution, especially for rare/sensitive items. Strong-looking subgroup results can still be artifacts of sample construction.

**Practical threshold defaults (source-backed starting points):**

| Metric | Practical default | Interpretation |
|---|---:|---|
| Incidence rate | `1-5%` very low, `10-30%` low, `40-60%` medium, `70-100%` high | `<=30%` means feasibility risk and likely slower/more expensive fill |
| Non-completion risk | `1-9%` minor, `10-20%` moderate, `>=21%` severe (24h view) | Escalate UX/screener review when moderate or severe |
| Speeder detection | >2 SD faster than median (one common operational rule); `<60%` of median LOI used in other QA frameworks | Flag for review in combination with other quality indicators |
| Straightlining | >=80% matrix-table straightlining across at least 3 matrices (one platform rule) | Treat as disengagement quality signal |
| Duplicate risk | Any measurable repeated-entry cluster is actionable | Add dedupe controls and source-level monitoring |
| Quota mismatch | SRM-style chi-square alarms (`alpha .01` or stricter operational variants) | Pause strong inference until assignment bias is investigated |

**Misinterpretations to avoid:**

- "Quota fill completed" does not imply high quality.
- "Topline stable" does not imply duplicates/fraud are harmless.
- "Aggressive cleaning always improves quality" is false; it can increase bias.
- "One threshold works for every provider/study type" is false; thresholds require context.

**Sources:**
- [Kantar incidence rate guidance (2025)](https://www.kantar.com/inspiration/research-services/understanding-incidence-rate-in-market-research-pf)
- [Qualtrics response quality](https://www.qualtrics.com/support/survey-platform/survey-module/survey-checker/response-quality)
- [SurveyMonkey completion analysis](https://www.surveymonkey.com/learn/survey-best-practices/tips-increasing-survey-completion-rates/)
- [Gallup opt-in panel quality issues part 1 (2024)](https://news.gallup.com/opinion/methodology/653993/data-quality-issues-opt-panels-part.aspx)
- [Gallup opt-in panel quality issues part 2 (2024)](https://news.gallup.com/opinion/methodology/654494/data-quality-issues-opt-panels-part-two.aspx)
- [Gallup supplemental threshold details (2024)](https://news.gallup.com/file/poll/653996/OptIn%20Methodology%20Blog%20Part%201%20Supplemental%20Materials.pdf)
- [Harris Poll duplicate-response deck (2024)](https://theharrispoll.com/wp-content/uploads/2024/05/Double-Dipping.pdf)
- [Pew opt-in subgroup risk note (2024)](https://www.pewresearch.org/short-reads/2024/03/05/online-opt-in-polls-can-produce-misleading-results-especially-for-young-people-and-hispanic-adults/)
- [Amplitude sample ratio mismatch](https://amplitude.com/docs/feature-experiment/troubleshooting/sample-ratio-mismatch)
- [Eppo sample ratio mismatch](https://docs.geteppo.com/statistics/sample-ratio-mismatch)
- [Prolific data quality approach](https://www.prolific.com/protocol-data-quality)

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

- Real-world 2024-2025 evidence shows recruitment can appear successful by speed while failing by validity (for example, high invalid rates after verification).
- Fraud attacks are often hybrid and adaptive; single control reliance fails frequently.
- Poorly designed screeners leak answer keys and increase ineligible pass-through.
- Delayed QA (post-close only) increases rework and contamination risk.
- Incentive mispricing (too low or overly salient public reward signals) can worsen quality.
- Quota completion can hide subgroup distortion, especially in opt-in contexts.
- Provider/source mixing without source-level QA dashboards creates hidden drift.
- Weak dedupe and identity controls permit repeated participation.
- Missing escalation paths for fraud/disputes causes inconsistent approvals and trust loss.
- Over-collection of sensitive screener data creates unnecessary legal and reputational risk.

**Named anti-patterns (operational format):**

- **Open-Link Incentive Bait**
  - Detection: sudden clustered starts after broad public posting.
  - Consequence: fraud influx and contaminated funnel.
  - Mitigation: controlled links, less revealing criteria, fast anomaly pause/relaunch.

- **Screener Answer-Key Leakage**
  - Detection: unusually high qualify rate with patterned answers.
  - Consequence: ineligible participants entering field.
  - Mitigation: non-leading screeners, hidden critical criteria, concordance checks.

- **Single-Guardrail Security**
  - Detection: fraud persists despite one anti-fraud feature.
  - Consequence: false confidence in sample quality.
  - Mitigation: layered controls plus human escalation.

- **Passive Funnel Monitoring**
  - Detection: large invalid share discovered only at close.
  - Consequence: avoidable budget loss and timeline delay.
  - Mitigation: daily monitoring of speed, inconsistency, and source anomalies.

- **Incentive Mispricing**
  - Detection: speeders, disputes, low-effort content, or suspicious surges.
  - Consequence: lower data quality and participation bias.
  - Mitigation: fair-pay policy and clear payout/rejection terms.

- **Quota Illusion**
  - Detection: implausible subgroup rates despite full quotas.
  - Consequence: biased decision input.
  - Mitigation: benchmark sanity checks and explicit uncertainty flags.

- **Provider-Mix Drift**
  - Detection: quality pass/fail divergence by source.
  - Consequence: unstable reproducibility.
  - Mitigation: source-level quality dashboards and stop-loss policies.

- **Data-Hungry Screeners**
  - Detection: sensitive data collection without clear necessity or basis.
  - Consequence: compliance risk and participant trust erosion.
  - Mitigation: minimization, lawful basis declaration, retention limits.

**Sources:**
- [Bots and fake participants case study (2024)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12331143/)
- [Recruitment/fraud controls in internet interventions (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11953592/)
- [Pew opt-in caution (2024)](https://www.pewresearch.org/short-reads/2024/03/05/online-opt-in-polls-can-produce-misleading-results-especially-for-young-people-and-hispanic-adults/)
- [User Interviews fraud deterrence](https://www.userinterviews.com/support/how-does-user-interviews-deter-fraud-on-the-platform)
- [User Interviews participant quality](https://www.userinterviews.com/support/participant-quality)
- [User Interviews anti-fraud blog (2025)](https://www.userinterviews.com/blog/outsmarting-fraud)
- [AAPOR disclosure standards (evergreen)](https://aapor.org/standards-and-ethics/disclosure-standards/)
- [AAPOR best practices (evergreen)](https://aapor.org/standards-and-ethics/best-practices/)
- [ICO lawful basis guide](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/a-guide-to-lawful-basis)
- [ICO special-category data](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/special-category-data/what-is-special-category-data/)
- [GOV.UK participant privacy](https://www.gov.uk/service-manual/user-research/managing-user-research-data-participant-privacy)

---

### Angle 5+: API Endpoint Reality & Integration Constraints
> Domain-specific angle: exact endpoint/operation verification for Prolific, Cint, MTurk, and UserTesting-related surfaces, plus what is not publicly verifiable.

**Findings:**

- Prolific has officially documented REST endpoints for study creation and submission operations, including approve transitions and bulk approve.
- Cint Demand API docs are versioned and require explicit headers and auth; feasibility and launch are async-style operations and feasibility is documented as `POST` calculations (not `GET`).
- MTurk official API is operation-based (`CreateHIT`, `ListAssignmentsForHIT`) rather than modern resource-path style; these map to the skill's intended create/list behavior.
- UserTesting public developer docs clearly expose results retrieval endpoints and auth flow; test-creation endpoint visibility is limited in public docs and appears access-scoped/legacy-sensitive.
- Existing skill method IDs for Cint feasibility (`...get...`) and UserTesting test creation should be treated as connector abstraction assumptions unless runtime `help` confirms exact mapping.
- Safe implementation pattern: distinguish "officially documented endpoint/operation" from "connector alias not externally verifiable."

**Verified endpoint/operation map:**

| Platform | Verified operation |
|---|---|
| Prolific | `POST /api/v1/studies/` |
| Prolific | `GET /api/v1/submissions/` |
| Prolific | `GET /api/v1/studies/{id}/submissions/` |
| Prolific | `POST /api/v1/submissions/{id}/transition/` (`APPROVE` action available) |
| Prolific | `POST /api/v1/submissions/bulk-approve/` |
| Cint | `POST /demand/accounts/{account_id}/projects` |
| Cint | `POST /demand/accounts/{account_id}/target-groups/calculate-feasibility` |
| Cint | `POST /demand/accounts/{account_id}/projects/{project_id}/target-groups/{target_group_id}/calculate-feasibility` |
| Cint | `POST /demand/accounts/{account_id}/projects/{project_id}/target-groups/{target_group_id}/fielding-run-jobs/launch-from-draft` |
| MTurk | `CreateHIT` |
| MTurk | `ListAssignmentsForHIT` |
| UserTesting | `GET /api/v2/sessionResults` |
| UserTesting | `GET /api/v2/sessionResults/{SESSION_ID}` |
| UserTesting | `GET /api/v2/sessionResults/{SESSION_ID}/transcript` |
| UserTesting | `GET /api/v2/sessionResults/{SESSION_ID}/videoDownloadUrl` |

**Unverifiable/public-gap notes:**

- Public verification of a dedicated UserTesting "create test" API endpoint was not found in retrieved official docs.
- Some internal connector method IDs may still be valid as private/legacy mappings, but they should not be treated as externally verified API facts unless confirmed via runtime tool introspection.

**Sources:**
- [Prolific create study](https://docs.prolific.com/api-reference/studies/create-study)
- [Prolific list submissions](https://docs.prolific.com/api-reference/submissions/get-submissions)
- [Prolific list study submissions](https://docs.prolific.com/api-reference/studies/get-study-submissions)
- [Prolific transition submission](https://docs.prolific.com/api-reference/submissions/transition-submission)
- [Prolific bulk approve submissions](https://docs.prolific.com/api-reference/submissions/bulk-approve-submissions)
- [Cint API overview (2025-12-18)](https://developer.cint.com/demand/docs/2025-12-18/getting-started/fundamentals/api-overview)
- [Cint authentication](https://developer.cint.com/demand/docs/2025-12-18/getting-started/fundamentals/authentication)
- [Cint create project](https://developer.cint.com/demand/docs/2025-12-18/reference/create-project)
- [Cint calculate feasibility](https://developer.cint.com/demand/docs/2025-12-18/reference/calculate-target-group-feasibility)
- [Cint calculate feasibility by id](https://developer.cint.com/demand/docs/2025-12-18/reference/calculate-target-group-feasibility-by-id)
- [Cint launch fielding run](https://developer.cint.com/demand/docs/2025-12-18/reference/create-launch-fielding-run-from-draft-job)
- [MTurk CreateHIT](https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_CreateHITOperation.html)
- [MTurk ListAssignmentsForHIT](https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_ListAssignmentsForHITOperation.html)
- [UserTesting developer docs home](https://developer.usertesting.com/)
- [UserTesting v2 getting started](https://developer.usertesting.com/v2.0/docs/getting-started)
- [UserTesting v2 authorization](https://developer.usertesting.com/v2.0/docs/authorization)
- [UserTesting API tutorial with v2 calls](https://developer.usertesting.com/docs/bulk-test-classification)

---

## Synthesis

The strongest pattern across all angles is that recruitment quality fails upstream, not downstream. Teams that skip feasibility realism, rush screener design, or optimize only for speed are the ones that later discover invalid participants, unstable subgroup conclusions, and expensive closeout disputes. Modern practice in 2024-2026 is explicit: treat recruitment as a monitored funnel with quality gates at every stage.

The second pattern is tradeoff transparency. Speed and strict quality controls pull in opposite directions. Low incidence, narrow quotas, and heavy screeners improve fit but slow fill and raise cost. The correct response is not to hide the tradeoff; it is to encode decision rules (what to relax first, when to pause, when to downgrade confidence) so operators can make defensible choices.

The third pattern is API reality over wishful abstractions. Prolific, Cint, and MTurk have verifiable official operation surfaces, while some UserTesting creation flows are not publicly documented in the same way. This means the skill should explicitly separate "officially documented external API facts" from "internal connector aliases." The Cint feasibility `GET` naming in the current skill is a concrete mismatch with documented `POST` feasibility operations.

Finally, interpretation quality now requires stronger anti-pattern defenses: over-cleaning bias, duplicate contamination, opt-in subgroup distortion, and fraud adaptation are all documented risks in 2024-2025 evidence. High-quality recruitment output therefore needs confidence labeling, source-level caveats, and compliance-aware data handling rather than binary "good/bad sample" claims.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.
> Each item here has corresponding draft content below.

- [x] Replace current high-level methodology with an explicit staged workflow (`feasibility -> design -> pilot -> scale -> monitor -> adjudicate`).
- [x] Add provider-routing guidance by study type and risk profile (survey vs interview vs usability).
- [x] Add strict screener design and anti-gaming rules with practical examples.
- [x] Add incentive policy language grounded in fairness and data-quality outcomes.
- [x] Add funnel interpretation thresholds and trigger bands for action.
- [x] Add named anti-pattern warning blocks with detection signals, consequences, and mitigations.
- [x] Add API reality section separating verified official endpoints from connector-only assumptions.
- [x] Update `## Available Tools` guidance to require runtime method introspection and operation mapping validation.
- [x] Expand artifact schema with feasibility, quality, source-level monitoring, adjudication, and confidence metadata.
- [x] Add pre-write quality/compliance checklist before `write_artifact`.

---

## Draft Content for SKILL.md

> This is the primary deliverable. Each subsection below is paste-ready draft text for updating `SKILL.md`.

### Draft: Core operating principle

---
You run participant recruitment as a quality-controlled pipeline, not a one-shot launch.

Your primary rule is **fit and validity before speed**. If participant fit is uncertain, funnel quality is unstable, or source behavior is suspicious, you must downgrade output confidence and state why.

Recruitment goals are not complete when a target `N` is reached. Recruitment is complete only when:
- participants match inclusion criteria,
- quota cells are filled without hidden skew,
- quality checks are passed,
- approval/rejection decisions are documented and reproducible.

If a study can fill quickly only by loosening critical eligibility or removing quality controls, that is not successful recruitment. It is degraded evidence and must be reported as such.
---

### Draft: Study-type routing and provider selection

---
### Study type selection

Choose provider strategy based on study type, sample complexity, and operational risk.

1. **Survey (quantitative)**
   - Default to high-control panel providers with strong screening and quota controls.
   - Use Prolific when you need explicit filter and quota handling with transparent participant-pay framing.
   - Use Cint when you need larger/global volume and can support stricter setup and monitoring discipline.
   - Use MTurk when budget pressure is primary and you can run stronger requester-managed QA.

2. **Interview recruiting (qualitative, especially B2B)**
   - Use recruiting workflows that support stronger participant verification and scheduling.
   - If interviews are the core method, treat interview-focused providers as primary sources, and hand off scheduling to the dedicated scheduling skill once candidates are validated.

3. **Usability testing**
   - Use UserTesting network/custom/invite modes when you need built-in usability workflow mechanics.
   - Adjust by plan/tier limits, screener limits, and session-capacity constraints.

Provider switching rule:
- If feasibility remains poor after one controlled relaxation pass, switch provider or source mix instead of repeatedly weakening core screening criteria.
---

### Draft: End-to-end recruitment workflow

---
### Methodology

Run these stages in order every time:

1. **Preflight and scope lock**
   - Define study type, target segment, and critical inclusion/exclusion criteria.
   - Define quota cells before launch.
   - Define funnel metrics to track: `invited -> started -> qualified -> completed`.
   - If key criteria are ambiguous, pause and resolve before fielding.

2. **Feasibility and incidence check**
   - Run provider feasibility/eligibility checks before finalizing budget and timeline.
   - Use feasibility outputs to estimate likely incidence and expected time-to-fill.
   - If estimated incidence is low (`<=30%` as a practical warning band), increase buffer for timeline and quality review capacity.

3. **Quota architecture**
   - Encode quota cells with explicit minimum `N` and criteria per cell.
   - Keep cell complexity realistic for panel supply. Overly narrow interlocked criteria increase fill failure risk.
   - Do not launch until quota totals match target completes and each cell has a feasible path.

4. **Screener hardening**
   - Use non-leading questions.
   - Avoid obvious yes/no pass keys.
   - Include options that reduce forced guessing (`none`, `other`, `not sure`) where appropriate.
   - For high-risk studies, add consistency checks (for example, role/experience concordance).
   - Do not reveal all critical qualifying logic in public recruitment copy.

5. **Pilot launch**
   - Launch a small pilot first and validate end-to-end flow.
   - Confirm that completion, termination, and quality-routing paths work.
   - Validate redirect/status handling and logging fields before scale.

6. **Scale launch with live monitoring**
   - Scale only after pilot quality gate passes.
   - Monitor funnel stages and source-level behavior daily.
   - Trigger review when quality-failure signatures cluster (speeding, duplicate patterns, unexpected source spikes, quota imbalance).

7. **Adjudication and closeout**
   - Approve only submissions that meet quality requirements.
   - Reject with explicit reason categories when failure is clear and policy-compliant.
   - Preserve transparent audit trail for approval, rejection, and reversal decisions.

8. **Post-run learning**
   - Record which criteria or cells caused most friction.
   - Record which source channels generated highest valid-completion rates.
   - Use these observations to tune next-run defaults.

Fail-fast rules:
- If feasibility is clearly below required level and cannot be recovered by minor scope adjustment, stop and return planning alternatives.
- If fraud/invalid patterns surge and cannot be contained quickly, pause fieldwork and re-open only after control changes.
---

### Draft: Screening and anti-gaming rules

---
### Screening

You must design screeners to measure fit, not to reward test-taking tactics.

Required screener rules:

1. **No leading prompts**
   - Do not signal the "right" profile in question wording.
   - Avoid phrasing that makes eligibility obvious.

2. **Use structured but non-binary logic**
   - Prefer multi-option questions when behavior/experience has gradation.
   - Avoid yes/no-only sequences for critical eligibility checks.

3. **Use non-overlapping ranges**
   - Ensure income/tenure/frequency bands are mutually exclusive.
   - Overlapping options create ambiguity and gaming opportunities.

4. **Check internal consistency**
   - For critical profiles, use at least one corroborating follow-up.
   - If self-described role and behavior history conflict, flag for review.

5. **Control answer-key leakage**
   - Keep public recruitment copy high-level.
   - Do not publish exact disqualifying criteria that can be memorized.

6. **Handle screen-outs ethically**
   - If using in-study screen-outs, define payment handling and slot logic upfront.
   - Keep participant-facing expectations clear and consistent with platform policy.

Do not:
- accept borderline profiles just to fill a hard cell quickly,
- remove critical screeners as first response to slow fill,
- treat screener pass as equivalent to quality pass.
---

### Draft: Incentive policy and participant fairness

---
### Incentive policy

Incentives are part of data-quality control and participant trust, not just budget.

Rules:
- Set compensation aligned to expected burden and time.
- Keep participant-facing payout terms explicit.
- Avoid manipulative framing that overemphasizes rewards in broad public channels.
- Increase compensation for long or high-cognitive-load sessions instead of expecting the same quality at flat pay.

Operational interpretation:
- Underpayment can increase low-effort responses, disputes, and no-show risk.
- Over-salient broad incentives can increase fraud pressure and identity-masking attempts.
- If quality drops while completion speed spikes, review incentive and channel strategy immediately.

If incentive adjustments are needed:
1. Adjust compensation first.
2. Re-run a controlled pilot sample.
3. Compare quality pass rate before full relaunch.
---

### Draft: Funnel monitoring and interpretation thresholds

---
### Funnel monitoring

Track each provider and each quota cell at minimum:
- `invited`
- `started`
- `qualified`
- `completed`
- `quality_terminated`
- `over_quota_terminated`
- `approval_rate`
- `rejection_rate`

You must monitor source-level quality, not just aggregate totals.

Practical trigger bands (starting defaults):
- Incidence warning: treat `started -> qualified <=30%` as feasibility/criteria risk.
- Completion risk: treat rising non-completion toward `>=10%` as moderate risk and `>=21%` as severe risk in operational monitoring contexts.
- Speed risk: flag sessions with extreme completion-time deviations for quality review (use platform-appropriate thresholds).
- Quota imbalance risk: if quota allocations drift significantly from intended distribution, pause strong inference and investigate assignment logic.

Interpretation rules:
- High completion count with high quality termination is not success.
- Fast fill with unstable quality signals is at-risk, not on-track.
- Stable quality with slower fill can be acceptable if timeline and budget remain within plan.

Confidence policy:
- Increase confidence when multiple sources and cells show consistent quality behavior.
- Decrease confidence when key cells are underfilled, low-incidence segments are forced, or quality failures cluster by source.
---

### Draft: Named anti-pattern warning blocks

---
### WARNING: Open-Link Incentive Bait
**What it looks like:** Broad public calls with visible reward and weak gating.  
**Detection signal:** Sudden high-velocity starts and low validation rate.  
**Consequence:** Fraud-heavy funnel and invalid completions.  
**Mitigation:** Controlled links, tighter entry gating, rapid anomaly pause-and-restart.

### WARNING: Screener Answer-Key Leakage
**What it looks like:** Leading screeners reveal pass conditions.  
**Detection signal:** Unusually high pass rates with patterned responses.  
**Consequence:** Ineligible participants enter and contaminate evidence.  
**Mitigation:** Non-leading design, hidden critical criteria, consistency checks.

### WARNING: Single-Guardrail Security
**What it looks like:** Reliance on one anti-fraud mechanism.  
**Detection signal:** Fraud persists while one control appears "green."  
**Consequence:** False confidence and costly post-field cleanup.  
**Mitigation:** Layered checks plus escalation workflow.

### WARNING: Passive Funnel Monitoring
**What it looks like:** Quality review postponed until field close.  
**Detection signal:** Major invalid share discovered too late.  
**Consequence:** Rework, delays, avoidable payout waste.  
**Mitigation:** Daily live monitoring and immediate intervention thresholds.

### WARNING: Quota Illusion
**What it looks like:** Full quotas interpreted as representativeness proof.  
**Detection signal:** Implausible subgroup rates or source-specific anomalies.  
**Consequence:** Biased downstream decisions.  
**Mitigation:** Benchmark checks, subgroup sanity review, explicit caveats.

### WARNING: Over-Cleaning Bias
**What it looks like:** Very aggressive exclusion removes large sample share.  
**Detection signal:** Removal rate spikes and demographic composition shifts sharply.  
**Consequence:** Smaller sample, possible new bias with marginal quality gain.  
**Mitigation:** Multi-signal targeted exclusions and composition audits.

### WARNING: Provider-Mix Drift
**What it looks like:** Multiple sources are blended without source-level QA.  
**Detection signal:** Quality pass rates diverge by source/time but aggregate hides it.  
**Consequence:** Unstable reproducibility and hidden source bias.  
**Mitigation:** Source-level dashboards, caps, and stop-loss rules.

### WARNING: Data-Hungry Screeners
**What it looks like:** Sensitive data collection without clear necessity.  
**Detection signal:** Special-category fields with weak lawful-basis documentation.  
**Consequence:** Compliance and trust risk.  
**Mitigation:** Minimization, lawful basis declaration, strict retention controls.
---

### Draft: API reality section and connector verification policy

---
### API and integration reality

Use only verified API facts in decision logic. Do not assume connector aliases are equivalent to official API definitions.

Officially documented operations include:

- **Prolific**
  - `POST /api/v1/studies/`
  - `GET /api/v1/submissions/`
  - `GET /api/v1/studies/{id}/submissions/`
  - `POST /api/v1/submissions/{id}/transition/`
  - `POST /api/v1/submissions/bulk-approve/`

- **Cint (Demand API)**
  - `POST /demand/accounts/{account_id}/projects`
  - `POST /demand/accounts/{account_id}/target-groups/calculate-feasibility`
  - `POST /demand/accounts/{account_id}/projects/{project_id}/target-groups/{target_group_id}/calculate-feasibility`
  - `POST /demand/accounts/{account_id}/projects/{project_id}/target-groups/{target_group_id}/fielding-run-jobs/launch-from-draft`

- **MTurk**
  - `CreateHIT`
  - `ListAssignmentsForHIT`

- **UserTesting (publicly verifiable in retrieved docs)**
  - `GET /api/v2/sessionResults`
  - `GET /api/v2/sessionResults/{SESSION_ID}`
  - `GET /api/v2/sessionResults/{SESSION_ID}/transcript`
  - `GET /api/v2/sessionResults/{SESSION_ID}/videoDownloadUrl`

If a connector method ID is not publicly verifiable from official docs:
1. Treat it as connector-local abstraction.
2. Verify it at runtime using connector help/introspection before use.
3. Do not assert external endpoint claims without a source.

Important correction:
- If internal naming suggests Cint feasibility is a `GET`, update or annotate that official Cint feasibility operations are documented as `POST`.
---

### Draft: Available Tools section text

---
## Available Tools

Use only methods that are both:
1) present in runtime connector help, and  
2) mappable to verified official operations.

```python
# Always inspect what your runtime exposes first.
prolific(op="help")
cint(op="help")
mturk(op="help")
usertesting(op="help")

# Prolific (connector aliases should map to official endpoints)
prolific(
  op="call",
  args={
    "method_id": "prolific.studies.create.v1",
    "name": "Study Name",
    "internal_name": "study_id",
    "description": "...",
    "external_study_url": "https://...",
    "prolific_id_option": "url_parameters",
    "completion_code": "COMPLETE123",
    "completion_option": "url",
    "total_available_places": 50,
    "estimated_completion_time": 15,
    "reward": 225
  }
)

prolific(
  op="call",
  args={
    "method_id": "prolific.submissions.list.v1",
    "study_id": "study_id"
  }
)

prolific(
  op="call",
  args={
    "method_id": "prolific.submissions.approve.v1",
    "study_id": "study_id",
    "submission_ids": ["sub_id1", "sub_id2"]
  }
)

# Cint and MTurk: use only method IDs present in runtime help, and ensure
# they map to official operations documented in this skill's API reality notes.
cint(op="call", args={"method_id": "<runtime_verified_cint_method>", "...": "..."})
mturk(op="call", args={"method_id": "<runtime_verified_mturk_method>", "...": "..."})

# UserTesting: public docs in this research verify results retrieval surfaces.
# Treat creation/listing methods as runtime-verified connector aliases unless
# official endpoint docs are available for your access tier.
usertesting(op="call", args={"method_id": "<runtime_verified_usertesting_method>", "...": "..."})
```

Tool-call policy:
- If runtime help and official mapping disagree, stop and resolve before launch.
- If a needed method is unavailable, do not invent fallback endpoint syntax.
- Record any unresolved method uncertainty in artifact `limitations`.
---

### Draft: Recording and quality checklist

---
### Recording

Write at least:

```python
write_artifact(
  artifact_type="participant_recruitment_plan",
  path="/discovery/{study_id}/recruitment-plan",
  data={...}
)

write_artifact(
  artifact_type="recruitment_funnel_snapshot",
  path="/discovery/{study_id}/recruitment-funnel",
  data={...}
)

write_artifact(
  artifact_type="recruitment_quality_audit",
  path="/discovery/{study_id}/recruitment-quality-audit",
  data={...}
)
```

Before writing any artifact, verify all checks:

1. Feasibility was run and documented before scale launch.
2. Quota cells were defined and tracked separately.
3. Screener logic was non-leading and anti-gaming checks were applied.
4. Pilot launch was executed (or explicit reason documented if skipped).
5. Funnel metrics include quality and over-quota terminations, not just completions.
6. Source-level anomalies were reviewed and addressed.
7. Approval/rejection logic and reason categories are explicit.
8. Confidence and limitations are internally consistent.
9. Data-minimization and lawful-basis constraints are documented for sensitive fields.

If any mandatory check fails, do not mark run `on_track` or high-confidence. Return `at_risk` or `blocked` with concrete next actions.
---

### Draft: Schema additions

> Full JSON Schema fragment for recommended updates/additions.

```json
{
  "participant_recruitment_plan": {
    "type": "object",
    "required": [
      "study_id",
      "study_type",
      "target_segment",
      "quota_cells",
      "channels",
      "inclusion_criteria",
      "exclusion_criteria",
      "incentive_policy",
      "timeline",
      "feasibility",
      "quality_controls"
    ],
    "additionalProperties": false,
    "properties": {
      "study_id": {
        "type": "string",
        "description": "Unique study identifier used across providers and artifacts."
      },
      "study_type": {
        "type": "string",
        "enum": [
          "survey",
          "interview",
          "usability_test",
          "mixed"
        ],
        "description": "Primary study method that determines provider and recruitment strategy."
      },
      "target_segment": {
        "type": "string",
        "description": "Human-readable description of intended participant profile."
      },
      "quota_cells": {
        "type": "array",
        "description": "Recruitment cells with explicit criteria and target counts.",
        "minItems": 1,
        "items": {
          "type": "object",
          "required": [
            "cell_id",
            "target_n",
            "criteria",
            "priority",
            "incidence_assumption"
          ],
          "additionalProperties": false,
          "properties": {
            "cell_id": {
              "type": "string",
              "description": "Stable cell identifier for tracking fill and quality."
            },
            "target_n": {
              "type": "integer",
              "minimum": 1,
              "description": "Required completes for this quota cell."
            },
            "criteria": {
              "type": "object",
              "description": "Eligibility filters for the cell (role, company size, etc.).",
              "additionalProperties": true
            },
            "priority": {
              "type": "string",
              "enum": [
                "critical",
                "high",
                "normal"
              ],
              "description": "Priority for intervention when fill risk appears."
            },
            "incidence_assumption": {
              "type": "number",
              "minimum": 0,
              "maximum": 1,
              "description": "Expected qualifying proportion used for planning and feasibility."
            },
            "relaxation_order": {
              "type": "array",
              "description": "Ordered list of non-critical criteria that may be relaxed if fill stalls.",
              "items": {
                "type": "string"
              }
            }
          }
        }
      },
      "channels": {
        "type": "array",
        "description": "Recruitment sources/providers used for this run.",
        "items": {
          "type": "string",
          "enum": [
            "prolific",
            "cint",
            "mturk",
            "usertesting",
            "userinterviews",
            "respondent",
            "internal_panel",
            "other"
          }
        }
      },
      "inclusion_criteria": {
        "type": "array",
        "description": "Must-have participant attributes.",
        "items": {
          "type": "string"
        }
      },
      "exclusion_criteria": {
        "type": "array",
        "description": "Disqualifying participant attributes or conflicts.",
        "items": {
          "type": "string"
        }
      },
      "incentive_policy": {
        "type": "object",
        "required": [
          "currency",
          "amount_range",
          "payout_terms",
          "fair_pay_note"
        ],
        "additionalProperties": false,
        "properties": {
          "currency": {
            "type": "string",
            "description": "ISO currency code used for incentive calculations."
          },
          "amount_range": {
            "type": "string",
            "description": "Human-readable range of participant compensation."
          },
          "payout_terms": {
            "type": "string",
            "description": "How and when payment is issued and under what approval conditions."
          },
          "fair_pay_note": {
            "type": "string",
            "description": "Rationale that compensation is aligned with burden/time and provider policy."
          }
        }
      },
      "timeline": {
        "type": "object",
        "required": [
          "launch_date",
          "target_close_date"
        ],
        "additionalProperties": false,
        "properties": {
          "launch_date": {
            "type": "string",
            "description": "Planned launch date (ISO date preferred)."
          },
          "target_close_date": {
            "type": "string",
            "description": "Planned close date (ISO date preferred)."
          },
          "pilot_required": {
            "type": "boolean",
            "description": "Whether a pilot gate is required before scale launch."
          },
          "pilot_sample_n": {
            "type": "integer",
            "minimum": 0,
            "description": "Pilot participant count before full launch."
          }
        }
      },
      "feasibility": {
        "type": "object",
        "required": [
          "checked_at",
          "provider_estimates",
          "overall_risk"
        ],
        "additionalProperties": false,
        "properties": {
          "checked_at": {
            "type": "string",
            "description": "Timestamp when feasibility was last computed."
          },
          "provider_estimates": {
            "type": "array",
            "description": "Per-provider feasibility and fill assumptions.",
            "items": {
              "type": "object",
              "required": [
                "provider",
                "estimated_available",
                "estimated_incidence"
              ],
              "additionalProperties": false,
              "properties": {
                "provider": {
                  "type": "string",
                  "description": "Provider identifier."
                },
                "estimated_available": {
                  "type": "integer",
                  "minimum": 0,
                  "description": "Estimated available participants for the defined criteria."
                },
                "estimated_incidence": {
                  "type": "number",
                  "minimum": 0,
                  "maximum": 1,
                  "description": "Estimated qualification rate for planning."
                },
                "notes": {
                  "type": "string",
                  "description": "Assumptions and caveats for this estimate."
                }
              }
            }
          },
          "overall_risk": {
            "type": "string",
            "enum": [
              "low",
              "medium",
              "high"
            ],
            "description": "Overall feasibility risk from incidence and provider constraints."
          }
        }
      },
      "quality_controls": {
        "type": "object",
        "required": [
          "anti_fraud_layers",
          "dedupe_strategy",
          "screener_hardening",
          "live_monitoring_frequency"
        ],
        "additionalProperties": false,
        "properties": {
          "anti_fraud_layers": {
            "type": "array",
            "description": "List of active fraud controls used in the run.",
            "items": {
              "type": "string"
            }
          },
          "dedupe_strategy": {
            "type": "string",
            "description": "How duplicate participation is detected and handled."
          },
          "screener_hardening": {
            "type": "array",
            "description": "Screener anti-gaming design measures applied.",
            "items": {
              "type": "string"
            }
          },
          "live_monitoring_frequency": {
            "type": "string",
            "enum": [
              "hourly",
              "twice_daily",
              "daily"
            ],
            "description": "How often funnel and quality checks are reviewed during field."
          }
        }
      }
    }
  },
  "recruitment_funnel_snapshot": {
    "type": "object",
    "required": [
      "study_id",
      "snapshot_ts",
      "provider_breakdown",
      "overall_status",
      "dropoff_reasons",
      "quality_summary",
      "confidence"
    ],
    "additionalProperties": false,
    "properties": {
      "study_id": {
        "type": "string",
        "description": "Study identifier linked to the recruitment plan."
      },
      "snapshot_ts": {
        "type": "string",
        "description": "Timestamp for this funnel snapshot."
      },
      "provider_breakdown": {
        "type": "array",
        "description": "Per-provider recruitment and quality progression metrics.",
        "items": {
          "type": "object",
          "required": [
            "provider",
            "invited",
            "started",
            "qualified",
            "completed",
            "quality_terminated",
            "over_quota_terminated",
            "approval_rate"
          ],
          "additionalProperties": false,
          "properties": {
            "provider": {
              "type": "string",
              "description": "Provider/source name."
            },
            "invited": {
              "type": "integer",
              "minimum": 0,
              "description": "Participants invited or exposed to the recruitment entry point."
            },
            "started": {
              "type": "integer",
              "minimum": 0,
              "description": "Participants who began screening or study flow."
            },
            "qualified": {
              "type": "integer",
              "minimum": 0,
              "description": "Participants who passed screening criteria."
            },
            "completed": {
              "type": "integer",
              "minimum": 0,
              "description": "Participants with valid completion status."
            },
            "quality_terminated": {
              "type": "integer",
              "minimum": 0,
              "description": "Participants terminated due to quality/fraud criteria."
            },
            "over_quota_terminated": {
              "type": "integer",
              "minimum": 0,
              "description": "Participants terminated because quota was already filled."
            },
            "approval_rate": {
              "type": "number",
              "minimum": 0,
              "maximum": 1,
              "description": "Approved submissions divided by reviewed submissions."
            },
            "median_completion_minutes": {
              "type": "number",
              "minimum": 0,
              "description": "Median completion time used for speeder diagnostics."
            },
            "estimated_incidence": {
              "type": "number",
              "minimum": 0,
              "maximum": 1,
              "description": "Observed started-to-qualified rate estimate for this provider."
            },
            "notes": {
              "type": "string",
              "description": "Provider-specific caveats, issues, or corrective actions."
            }
          }
        }
      },
      "overall_status": {
        "type": "string",
        "enum": [
          "on_track",
          "at_risk",
          "blocked"
        ],
        "description": "Overall recruitment health at snapshot time."
      },
      "dropoff_reasons": {
        "type": "array",
        "description": "Primary reasons for participant loss across the funnel.",
        "items": {
          "type": "string"
        }
      },
      "quality_summary": {
        "type": "object",
        "required": [
          "duplicate_risk_level",
          "speeder_risk_level",
          "screener_inconsistency_rate"
        ],
        "additionalProperties": false,
        "properties": {
          "duplicate_risk_level": {
            "type": "string",
            "enum": [
              "low",
              "medium",
              "high"
            ],
            "description": "Assessed risk of duplicate participation in current snapshot."
          },
          "speeder_risk_level": {
            "type": "string",
            "enum": [
              "low",
              "medium",
              "high"
            ],
            "description": "Assessed risk from abnormally fast completions."
          },
          "screener_inconsistency_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Share of records flagged for screener/profile inconsistency."
          },
          "source_anomaly_notes": {
            "type": "array",
            "description": "Source-level anomalies that affect confidence.",
            "items": {
              "type": "string"
            }
          }
        }
      },
      "confidence": {
        "type": "number",
        "minimum": 0,
        "maximum": 1,
        "description": "Confidence in current funnel health assessment."
      },
      "confidence_notes": {
        "type": "array",
        "description": "Explicit reasons for confidence level and any downgrades.",
        "items": {
          "type": "string"
        }
      }
    }
  },
  "recruitment_quality_audit": {
    "type": "object",
    "required": [
      "study_id",
      "audit_ts",
      "review_scope",
      "findings",
      "actions",
      "compliance_flags"
    ],
    "additionalProperties": false,
    "properties": {
      "study_id": {
        "type": "string",
        "description": "Study identifier for this quality audit."
      },
      "audit_ts": {
        "type": "string",
        "description": "Timestamp of audit completion."
      },
      "review_scope": {
        "type": "array",
        "description": "What dimensions were reviewed (fraud, screeners, quotas, approvals, etc.).",
        "items": {
          "type": "string"
        }
      },
      "findings": {
        "type": "array",
        "items": {
          "type": "object",
          "required": [
            "category",
            "severity",
            "finding",
            "evidence"
          ],
          "additionalProperties": false,
          "properties": {
            "category": {
              "type": "string",
              "enum": [
                "fraud",
                "screening",
                "quota",
                "incentives",
                "provider",
                "compliance"
              ],
              "description": "Audit category for the finding."
            },
            "severity": {
              "type": "string",
              "enum": [
                "low",
                "medium",
                "high"
              ],
              "description": "Finding severity level."
            },
            "finding": {
              "type": "string",
              "description": "Plain-language description of the issue."
            },
            "evidence": {
              "type": "string",
              "description": "Observed evidence supporting the finding."
            }
          }
        }
      },
      "actions": {
        "type": "array",
        "description": "Concrete corrective actions and owners.",
        "items": {
          "type": "object",
          "required": [
            "action",
            "owner",
            "due"
          ],
          "additionalProperties": false,
          "properties": {
            "action": {
              "type": "string",
              "description": "Specific mitigation task."
            },
            "owner": {
              "type": "string",
              "description": "Responsible role or person."
            },
            "due": {
              "type": "string",
              "description": "Due date or timestamp for action completion."
            }
          }
        }
      },
      "compliance_flags": {
        "type": "array",
        "description": "Data-protection or policy flags requiring review.",
        "items": {
          "type": "string"
        }
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Public documentation for UserTesting creation endpoints is not as clear as results retrieval endpoints in the sources reviewed. Connector methods may exist, but public endpoint verification remains limited.
- Provider-specific thresholds (especially quality filters and anti-fraud rules) are often implementation-specific; defaults in this research should be treated as starting points, then calibrated with live data.
- Some key practice guidance is evergreen rather than explicitly dated 2024-2026 (for example AWS MTurk operation docs and AAPOR standards). These are marked as evergreen where used.
- Jurisdiction-specific compliance obligations can vary materially by study context (children, health, special-category data, employment contexts). Legal review may still be required for production policy decisions.
- Public pricing pages can change frequently; cost and fee assumptions should be rechecked at implementation time.
