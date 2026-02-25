
### Stage 1: Opportunity Framing (Level 2)

#### 1.1 Opportunity signal intake

- Inputs: founder thesis, customer complaints, market shifts, competitor moves, regulatory changes.
- Execution: build a signal register grouped by demand, regulation, technology, channel, and cost signals.
- Output artifact: `Opportunity Signal Register`.
- Local evidence gate: at least 3 independent signal classes support the same opportunity direction.
- Fail-fast trigger: only internal opinion exists with no external signal confirmation.

#### 1.2 Job and outcome framing

- Inputs: interview notes, observed workflows, existing workaround documentation.
- Execution: define core job statements and desired outcomes using direction + metric + object + context format.
- Output artifact: `JTBD and Desired Outcomes Map`.
- Local evidence gate: top outcomes are measurable and solution-agnostic.
- Fail-fast trigger: statements contain solution bias ("build app", "add AI") instead of job outcomes.

#### 1.3 Problem-space boundaries

- Inputs: initial hypotheses, target segment candidates, operational constraints.
- Execution: define explicit in-scope, out-of-scope, and "not now" boundaries for segment, workflow, and use case.
- Output artifact: `Problem Boundary Specification`.
- Local evidence gate: clear exclusions are documented and testable.
- Fail-fast trigger: target definition is broad ("for everyone").

#### 1.4 Constraint envelope

- Inputs: team capacity, budget ceiling, compliance constraints, technical constraints.
- Execution: quantify resource envelope (time, budget, people, tools), including maximum acceptable downside.
- Output artifact: `Constraint Matrix and Risk Envelope`.
- Local evidence gate: each top hypothesis has a feasible test path inside current envelope.
- Fail-fast trigger: core hypotheses require resources outside allowed envelope.

#### 1.5 Opportunity statement and risk assumptions

- Inputs: signal register, JTBD map, boundaries, constraints.
- Execution: run assumption mapping and rank risks by impact x evidence confidence.
- Output artifact: `Risk-Ranked Hypothesis Backlog`.
- Local evidence gate: top risks have explicit validation method, threshold, and timebox.
- Fail-fast trigger: high-impact assumptions remain untestable.

### Stage 2: Problem and Segment Validation (Level 2)

#### 2.1 Segment map and beachhead selection

- Inputs: candidate segments, trigger events, accessibility notes, TAM assumptions.
- Execution: segment by firmographic/behavioral/trigger criteria and enforce beachhead tests (word of mouth, same sales process, same product).
- Output artifact: `Beachhead Decision Memo`.
- Local evidence gate: one beachhead selected and alternatives explicitly parked.
- Fail-fast trigger: selected segment requires multiple sales motions on day one.

#### 2.2 Problem interview execution

- Inputs: screener, interview script, candidate list.
- Execution: run interviews with past-behavior focus (not future promises), track saturation by theme.
- Output artifact: `Interview Corpus and Theme Coding`.
- Local evidence gate: pattern saturation reached for core themes in target segment.
- Fail-fast trigger: evidence is dominated by compliments and hypotheticals.

#### 2.3 Pain quantification

- Inputs: interview corpus, operational logs, proxy cost signals.
- Execution: quantify pain frequency, severity, cost of inaction, and switching friction (procedural, financial, relational).
- Output artifact: `Pain Economics Sheet`.
- Local evidence gate: top pains have numeric ranges and confidence level.
- Fail-fast trigger: no way to estimate business impact of pain.

#### 2.4 Alternative and status-quo mapping

- Inputs: user-described alternatives, competitor scans, internal process substitutes.
- Execution: map direct and indirect alternatives, including "do nothing" and manual workaround.
- Output artifact: `Alternative Landscape Matrix`.
- Local evidence gate: each alternative includes adoption reason and failure reason.
- Fail-fast trigger: analysis includes only named competitors and ignores status quo.

#### 2.5 Segment-problem fit verdict

- Inputs: segment data, pain economics, alternatives matrix.
- Execution: score evidence quality and issue explicit verdict (validated, weak, rejected).
- Output artifact: `Segment-Problem Fit Verdict`.
- Local evidence gate: decision references concrete evidence and confidence.
- Fail-fast trigger: all segments remain "possible" with no prioritization.

### Stage 3: Solution and Offer Hypothesis (Level 2)

#### 3.1 Value proposition design

- Inputs: validated pains/outcomes, segment insights.
- Execution: map jobs, pains, gains to pain relievers and gain creators; isolate top value claims.
- Output artifact: `Value Proposition Canvas per Beachhead`.
- Local evidence gate: top claims map directly to top validated pains.
- Fail-fast trigger: feature list exists without explicit customer value mapping.

#### 3.2 Positioning architecture

- Inputs: alternatives matrix, value claims, segment language.
- Execution: define competitive alternatives, unique attributes, proof points, target segment, category anchor.
- Output artifact: `Positioning Brief`.
- Local evidence gate: one sentence "why us now" is clear and testable.
- Fail-fast trigger: positioning depends on generic superlatives only.

#### 3.3 Offer packaging architecture

- Inputs: positioning brief, support constraints, delivery model.
- Execution: design offer boundary (core, optional, excluded), plus tier logic if needed.
- Output artifact: `Offer and Packaging Specification`.
- Local evidence gate: tiers differ by customer value and service level, not random feature splitting.
- Fail-fast trigger: every deal needs custom packaging.

#### 3.4 Pricing hypothesis system

- Inputs: value claims, alternatives pricing, budget signals.
- Execution: triangulate price corridor via willingness-to-pay methods and commitment tests (paid pilot/deposit/preorder).
- Output artifact: `Price Corridor and Packaging Hypothesis`.
- Local evidence gate: floor/target/ceiling and rationale are explicit.
- Fail-fast trigger: pricing is set only as "competitor minus percent".

#### 3.5 Falsifiable test plan

- Inputs: offer and pricing hypotheses, risk backlog.
- Execution: define experiments with primary metric, guardrails, threshold, minimum sample logic, stop conditions.
- Output artifact: `Experiment Card Set`.
- Local evidence gate: each card has pre-declared success/failure criteria.
- Fail-fast trigger: criteria are rewritten after seeing results.

### Stage 4: MVP or Proof-of-Value (Level 2)

#### 4.1 MVP pattern selection

- Inputs: top assumptions and experiment cards.
- Execution: select minimal pattern (concierge, Wizard-of-Oz, fake door, prototype, thin-slice) by risk type.
- Output artifact: `MVP Pattern Selection Note`.
- Local evidence gate: selected pattern is the cheapest path to test highest risk.
- Fail-fast trigger: full build starts before demand signal.

#### 4.2 Instrumentation and measurement design

- Inputs: experiment cards.
- Execution: define event schema, one primary metric, 2-3 guardrail metrics, attribution windows.
- Output artifact: `Measurement and Event Schema`.
- Local evidence gate: metrics are actionable, auditable, and tied to decision rule.
- Fail-fast trigger: only vanity metrics are tracked.

#### 4.3 Minimal implementation and assisted onboarding

- Inputs: selected MVP pattern, measurement schema.
- Execution: implement minimal user path to first value with manual assist where needed.
- Output artifact: `Testable MVP Artifact and Onboarding Script`.
- Local evidence gate: user can reach first value under defined time-to-value target.
- Fail-fast trigger: heavy integration work starts before proof of value.

#### 4.4 Real-user experiment run

- Inputs: MVP artifact, qualified users, runbook.
- Execution: run tests in bounded cohorts, maintain experiment integrity, document deviations.
- Output artifact: `Experiment Run Log and Raw Result Set`.
- Local evidence gate: sufficient directional reliability for decision (qual saturation or quant threshold).
- Fail-fast trigger: uncontrolled experiment changes without log.

#### 4.5 Decision loop

- Inputs: run logs, metric outcomes, guardrail outcomes.
- Execution: make explicit decision (pivot, refine, persevere, kill) against predeclared thresholds.
- Output artifact: `Decision Memo and Next-Hypothesis Queue`.
- Local evidence gate: decision rationale ties to threshold and evidence quality.
- Fail-fast trigger: continuation justified only by sunk cost.

### Stage 5: Early Commercial Validation (Level 2)

#### 5.1 Founder-led demand generation

- Inputs: ICP hypothesis, positioning brief, outreach scripts.
- Execution: run direct outreach and warm introductions with tight feedback capture loops.
- Output artifact: `Early Pipeline with Source and Response Data`.
- Local evidence gate: consistent meeting/response flow from target segment.
- Fail-fast trigger: dependence on accidental inbound before repeatable signal.

#### 5.2 Lead qualification and deal anatomy

- Inputs: active pipeline, discovery notes.
- Execution: apply lightweight qualification framework fit for ACV complexity, map buyer process and blockers.
- Output artifact: `Qualification Rubric and Deal Map`.
- Local evidence gate: each active deal has clear need, authority path, timeline, and risk notes.
- Fail-fast trigger: demo-heavy pipeline with unresolved qualification basics.

#### 5.3 Paid commitment and pilot structure

- Inputs: qualified opportunities, success criteria drafts.
- Execution: structure paid pilot with 30-90 day scope, 2-3 success metrics, and conversion terms.
- Output artifact: `Pilot Template and Commitment Terms`.
- Local evidence gate: pilot has explicit business outcome and conversion trigger.
- Fail-fast trigger: free pilot with no explicit strategic justification.

#### 5.4 First-customer success and references

- Inputs: signed pilot/customers, onboarding assets.
- Execution: run high-touch implementation to first value and capture proof artifacts.
- Output artifact: `First-Win Evidence Pack (results, quote, reference status)`.
- Local evidence gate: first value achieved within expected time band for segment.
- Fail-fast trigger: handoff gaps between sale and onboarding cause avoidable delays.

#### 5.5 Repeatability check to first ten customers

- Inputs: first-customer results, deal timeline data.
- Execution: compare deal patterns for repeatability in segment, motion, and offer.
- Output artifact: `Repeatability Report v1`.
- Local evidence gate: wins show recurring pattern, not isolated exceptions.
- Fail-fast trigger: each win requires unique custom process.

### Stage 6: Fit Consolidation (PMF-Level Evidence) (Level 2)

#### 6.1 Activation hardening

- Inputs: onboarding telemetry, support tickets, user session signals.
- Execution: remove activation friction in first-value path, refine guidance and defaults.
- Output artifact: `Activation Funnel and Friction Backlog`.
- Local evidence gate: activation step drop-offs are known and improving.
- Fail-fast trigger: major activation drop-offs remain unexplained.

#### 6.2 Cohort retention stabilization

- Inputs: cohort tables by signup period and segment.
- Execution: track return/usage behavior and diagnose cohort divergence.
- Output artifact: `Cohort Retention Review`.
- Local evidence gate: retention curves show stabilization or explicit recovery plan.
- Fail-fast trigger: aggregate retention hides failing recent cohorts.

#### 6.3 Revenue quality validation

- Inputs: expansion, contraction, churn, gross margin data.
- Execution: track GRR/NRR by segment and detect revenue quality risks.
- Output artifact: `Revenue Quality Dashboard`.
- Local evidence gate: retention and expansion dynamics align with target segment economics.
- Fail-fast trigger: growth is driven only by new logos while base leaks.

#### 6.4 PMF confidence triangulation

- Inputs: retention behavior, referral signals, PMF survey signal.
- Execution: triangulate PMF from behavior + sentiment; avoid single-metric claims.
- Output artifact: `PMF Confidence Scorecard`.
- Local evidence gate: independent metrics point in the same direction.
- Fail-fast trigger: PMF claim is based only on survey sentiment.

#### 6.5 Failure closure loop

- Inputs: churn list, churn interviews, loss reasons.
- Execution: run structured churn interviews, cluster root causes, assign corrective owners.
- Output artifact: `Churn Root-Cause Backlog`.
- Local evidence gate: each top churn cause has owner, action, and verification metric.
- Fail-fast trigger: churn reason remains generic ("price") with no root-cause detail.

### Stage 7: GTM and Route-to-Market Fit (Level 2)

#### 7.1 ICP and exclusion lock

- Inputs: win/loss data, churn data, usage quality by segment.
- Execution: finalize ICP traits, buying triggers, and explicit exclusion criteria.
- Output artifact: `ICP v1 with Exclusion List`.
- Local evidence gate: GTM teams use one ICP definition and one exclusion policy.
- Fail-fast trigger: multiple inconsistent ICP definitions run in parallel.

#### 7.2 GTM motion selection

- Inputs: ACV bands, complexity profile, buyer process, onboarding load.
- Execution: choose primary motion (PLG, sales-led, hybrid) with clear handoff points.
- Output artifact: `Primary Motion Decision Memo`.
- Local evidence gate: one dominant motion is selected for current phase.
- Fail-fast trigger: mixed motions launched without ownership boundaries.

#### 7.3 Channel fit validation

- Inputs: candidate channels, cost and conversion data, message test results.
- Execution: run focused channel tests and choose one or two channel-motion winners.
- Output artifact: `Channel Scorecard and Priority Stack`.
- Local evidence gate: winning channels show consistent qualified pipeline generation.
- Fail-fast trigger: budget spread across many unproven channels.

#### 7.4 RTM architecture and conflict controls

- Inputs: motion model, partner model, pricing policy.
- Execution: define direct/indirect/hybrid roles, lead routing, deal registration, territory and parity rules.
- Output artifact: `RTM Rules of Engagement`.
- Local evidence gate: conflict resolution process and SLA are explicit.
- Fail-fast trigger: ownership overlap with no enforced rules.

#### 7.5 Unit economics readiness

- Inputs: CAC, gross margin, payback, conversion, retention data by segment.
- Execution: validate economics under scaled assumptions and stress scenarios.
- Output artifact: `Unit Economics Readiness Review`.
- Local evidence gate: payback and margin profile are inside target range for chosen segment.
- Fail-fast trigger: spend scaling starts while payback is unknown.

### Stage 8: First Scalable Actions (Level 2)

#### 8.1 Codification of winning motion

- Inputs: repeatable deal and onboarding patterns.
- Execution: codify scripts, qualification, handoffs, objection handling, and implementation playbooks.
- Output artifact: `Playbook Library v1`.
- Local evidence gate: new operator can execute from docs without founder intervention.
- Fail-fast trigger: critical steps exist only as founder tacit knowledge.

#### 8.2 Controlled volume expansion

- Inputs: validated channel-motion pairs, capacity constraints.
- Execution: expand throughput in bounded increments with pre/post quality checks.
- Output artifact: `Scale Increment Plan`.
- Local evidence gate: each increment has explicit rollback threshold.
- Fail-fast trigger: abrupt scale jumps without checkpoint review.

#### 8.3 Team and ownership scaling

- Inputs: operating bottleneck analysis, capacity plan.
- Execution: assign single owners for demand, conversion, onboarding, retention, and partner ops.
- Output artifact: `Operating Ownership Model`.
- Local evidence gate: each core KPI has one accountable owner.
- Fail-fast trigger: shared ownership with no clear accountability.

#### 8.4 Continuous optimization cadence

- Inputs: experiment backlog, operating scorecard.
- Execution: run weekly experiment cycle, monthly operating review, quarterly fit reassessment.
- Output artifact: `Optimization Cadence Calendar and Logs`.
- Local evidence gate: each cycle ends with concrete decision and owner.
- Fail-fast trigger: recurring meetings produce no decisions or actions.

#### 8.5 Risk and quality guardrails

- Inputs: conflict incidents, service quality incidents, pricing exceptions.
- Execution: enforce governance for pricing boundaries, channel conflict, SLA consistency, and exception paths.
- Output artifact: `Commercial Governance Charter`.
- Local evidence gate: exceptions are logged, reviewed, and auditable.
- Fail-fast trigger: repeated ad-hoc exceptions outside formal governance.


### Expert Card 01 - Signal and Boundary Analyst

- `fexp_name`: `signal_boundary_analyst`
- Mission: convert weak opportunity signals into a bounded, testable risk backlog.
- Owns Level 2 units: `1.1`, `1.3`, `1.4`, `1.5`
- Input contract:
  - `boss_task`: source=`user_directive`, ref=`current boss request`, freshness=`latest`
  - `prior_signal_register`: source=`artifact`, ref=`Opportunity Signal Register`, freshness=`latest revision`
  - `constraint_data`: source=`artifact`, ref=`Constraint Matrix and Risk Envelope`, freshness=`latest revision`
  - `external_signal_updates`: source=`tool_output`, ref=`web/tool research batch`, freshness=`<= current cycle`
- Output contract: `Opportunity Signal Register`, `Problem Boundary Specification`, `Risk-Ranked Hypothesis Backlog`
- Tool groups (concrete):
  - `TG-Market-Signal-Intel`: `Google Trends API`, `X/Twitter Search API`, `Reddit Search` -> collect demand shifts, topic spikes, and competitor signal mentions.
  - `TG-Web-Change-Monitor`: `Visualping` or `Diffbot` + URL watchlist -> detect competitor pricing and landing page changes.
  - `TG-Research-KB`: `Notion` or `Confluence` -> store evidence, assumptions, and citations.
  - `Blocked`: no campaign launch (`Meta Ads`, `Google Ads`), no CRM deal edits.
- Done-definition: top risks are ranked and each has explicit validation path.
- Failure path: if top risks are not testable inside constraints, escalate to boss with narrowed scope options.

### Expert Card 02 - JTBD and Interview Researcher

- `fexp_name`: `jtbd_interview_researcher`
- Mission: produce behavior-grounded job/outcome evidence and interview corpus quality.
- Owns Level 2 units: `1.2`, `2.2`
- Input contract:
  - `candidate_list`: source=`artifact`, ref=`Beachhead candidate pool`, freshness=`active cycle`
  - `interview_script`: source=`artifact`, ref=`Interview script current`, freshness=`latest`
  - `existing_notes`: source=`artifact`, ref=`Interview Corpus and Theme Coding`, freshness=`latest`
  - `survey_responses`: source=`api`, ref=`configured survey platform`, freshness=`<= 14 days`
- Output contract: `JTBD and Desired Outcomes Map`, updated `Interview Corpus and Theme Coding`
- Tool groups (concrete):
  - `TG-Survey-Collection`: `Typeform`, `Google Forms`, `SurveyMonkey` -> run JTBD/problem surveys and export structured responses.
  - `TG-Interview-Recording-Transcription`: `Zoom`, `Google Meet`, `Whisper/Otter` -> record and transcribe interviews for coding.
  - `TG-Qual-Repository`: `Airtable` or `Notion database` -> tag themes, track saturation, preserve evidence provenance.
  - `Blocked`: no ad spend changes, no pricing edits.
- Done-definition: outcome statements are measurable, solution-agnostic, and saturation is evidenced.
- Failure path: if interviews stay hypothetical/polite, reset script and sampling with boss approval.

### Expert Card 03 - Segment and Beachhead Strategist

- `fexp_name`: `segment_beachhead_strategist`
- Mission: select one beachhead with explicit reject/park rationale.
- Owns Level 2 units: `2.1`, `2.5`
- Input contract:
  - `segment_candidates`: source=`artifact`, ref=`segment map working file`, freshness=`latest`
  - `interview_evidence`: source=`expert_handoff`, ref=`jtbd_interview_researcher`, freshness=`current cycle`
  - `tam_estimates`: source=`artifact`, ref=`TAM assumptions sheet`, freshness=`latest`
  - `accessibility_signals`: source=`tool_output`, ref=`market/channel scans`, freshness=`<= current cycle`
- Output contract: `Beachhead Decision Memo`, `Segment-Problem Fit Verdict`
- Tool groups (concrete):
  - `TG-ICP-Enrichment`: `LinkedIn Sales Navigator`, `Clearbit`, `Crunchbase` -> enrich firmographic, technographic, and trigger fields.
  - `TG-Market-Sizing`: `Google Trends export`, industry datasets, spreadsheet model -> estimate TAM/SAM with explicit assumptions.
  - `TG-Decision-Scoring`: `Airtable` scoring model -> rank beachhead options against same-process, same-product, and word-of-mouth tests.
  - `Blocked`: no outreach sending, no campaign edits.
- Done-definition: one beachhead chosen with explicit evidence quality and parked alternatives.
- Failure path: if no segment clears minimum evidence, escalate with re-segmentation plan.

### Expert Card 04 - Pain and Alternatives Analyst

- `fexp_name`: `pain_alternative_analyst`
- Mission: quantify pain economics and map status-quo competition.
- Owns Level 2 units: `2.3`, `2.4`
- Input contract:
  - `interview_corpus`: source=`expert_handoff`, ref=`jtbd_interview_researcher`, freshness=`latest`
  - `ops_cost_proxies`: source=`api`, ref=`configured CRM/finance data`, freshness=`current quarter`
  - `competitor_observations`: source=`tool_output`, ref=`competitive scans`, freshness=`<= current cycle`
  - `workaround_logs`: source=`artifact`, ref=`customer workaround notes`, freshness=`latest`
- Output contract: `Pain Economics Sheet`, `Alternative Landscape Matrix`
- Tool groups (concrete):
  - `TG-CRM-Data-Extract`: `HubSpot API`, `Salesforce API` -> pull lead/deal notes and loss reasons.
  - `TG-Support-Data-Extract`: `Zendesk`, `Intercom` -> pull ticket categories, response latency, unresolved pain.
  - `TG-Alternative-Intelligence`: `G2`, `Capterra`, competitor pricing pages -> map status-quo and substitute alternatives.
  - `Blocked`: no outbound customer messaging, no campaign launch.
- Done-definition: top pains have numeric ranges and explicit uncertainty.
- Failure path: if economics cannot be quantified, escalate with minimum viable proxy set.

### Expert Card 05 - Offer and Positioning Architect

- `fexp_name`: `offer_positioning_architect`
- Mission: turn validated pains into positionable, packageable offer architecture.
- Owns Level 2 units: `3.1`, `3.2`, `3.3`
- Input contract:
  - `pain_economics`: source=`expert_handoff`, ref=`pain_alternative_analyst`, freshness=`latest`
  - `beachhead_verdict`: source=`expert_handoff`, ref=`segment_beachhead_strategist`, freshness=`latest`
  - `delivery_constraints`: source=`artifact`, ref=`Constraint Matrix and Risk Envelope`, freshness=`latest`
  - `voice_of_customer_terms`: source=`artifact`, ref=`Interview Corpus language excerpts`, freshness=`latest`
- Output contract: `Value Proposition Canvas per Beachhead`, `Positioning Brief`, `Offer and Packaging Specification`
- Tool groups (concrete):
  - `TG-Message-Library`: competitor sites, review quotes, interview quotes -> compile wording options and proof points.
  - `TG-Message-Test-Lab`: `Wynter`, landing-page smoke tests, small ad-copy tests -> validate clarity, relevance, differentiation.
  - `TG-Offer-Blueprint-Docs`: `Notion` or `Confluence` templates -> structure package tiers and scope boundaries.
  - `Blocked`: no media buying execution.
- Done-definition: top claims map to validated pains and are framed against status quo alternatives.
- Failure path: if positioning remains generic, escalate with forced category and exclusion choices.

### Expert Card 06 - Pricing and Commitment Designer

- `fexp_name`: `pricing_commitment_designer`
- Mission: produce a falsifiable price corridor and commitment logic.
- Owns Level 2 units: `3.4`
- Input contract:
  - `offer_spec`: source=`expert_handoff`, ref=`offer_positioning_architect`, freshness=`latest`
  - `budget_signals`: source=`artifact`, ref=`discovery budget notes`, freshness=`latest`
  - `commitment_events`: source=`api`, ref=`configured billing/checkout or pilot-signing system`, freshness=`current cycle`
  - `pilot_outcomes`: source=`artifact`, ref=`Pilot Template and Commitment Terms`, freshness=`latest`
- Output contract: `Price Corridor and Packaging Hypothesis`
- Tool groups (concrete):
  - `TG-Pricing-Survey`: `Van Westendorp`, `Gabor-Granger` survey flows -> derive acceptable price corridor.
  - `TG-Commitment-Evidence`: `Stripe Checkout`, preorder/deposit links, pilot invoice logs -> capture real willingness-to-pay.
  - `TG-Deal-Terms`: `DocuSign` and LOI repository -> track signed commercial commitment quality.
  - `Blocked`: no ad-account operations.
- Done-definition: floor, target, ceiling and confidence are explicit and evidence-backed.
- Failure path: if commitment evidence contradicts stated willingness-to-pay, escalate with repricing options.

### Expert Card 07 - Experiment Method Designer

- `fexp_name`: `experiment_method_designer`
- Mission: design minimum-cost experiments with decision integrity.
- Owns Level 2 units: `3.5`, `4.1`
- Input contract:
  - `risk_backlog`: source=`artifact`, ref=`Risk-Ranked Hypothesis Backlog`, freshness=`latest`
  - `price_hypothesis`: source=`expert_handoff`, ref=`pricing_commitment_designer`, freshness=`latest`
  - `offer_hypothesis`: source=`expert_handoff`, ref=`offer_positioning_architect`, freshness=`latest`
  - `historical_test_log`: source=`artifact`, ref=`Experiment Run Log and Raw Result Set`, freshness=`latest`
- Output contract: `Experiment Card Set`, `MVP Pattern Selection Note`
- Tool groups (concrete):
  - `TG-Experiment-Registry`: `Airtable` or `Notion` experiment board -> define hypothesis, metric, guardrails, thresholds.
  - `TG-Stats-Toolkit`: sample-size and MDE calculators -> validate reliability before launch.
  - `TG-Flag-Plan`: `LaunchDarkly` or feature-flag plan -> scope safe exposure for test rollout.
  - `Blocked`: no production rollout approvals.
- Done-definition: each experiment has primary metric, guardrails, thresholds, stop conditions.
- Failure path: if thresholds cannot be predefined, experiment is rejected and re-scoped.

### Expert Card 08 - MVP and Telemetry Operator

- `fexp_name`: `mvp_telemetry_operator`
- Mission: execute MVP tests with instrumentation and clean decision logs.
- Owns Level 2 units: `4.2`, `4.3`, `4.4`, `4.5`
- Input contract:
  - `experiment_cards`: source=`expert_handoff`, ref=`experiment_method_designer`, freshness=`latest approved`
  - `event_schema`: source=`artifact`, ref=`Measurement and Event Schema`, freshness=`latest`
  - `test_user_pool`: source=`artifact`, ref=`qualified user cohort list`, freshness=`current cycle`
  - `runtime_events`: source=`event_stream`, ref=`configured product analytics stream`, freshness=`near-real-time`
- Output contract: `Measurement and Event Schema`, `Experiment Run Log and Raw Result Set`, `Decision Memo and Next-Hypothesis Queue`
- Tool groups (concrete):
  - `TG-Prototype-and-Staging`: `Webflow`, `Framer`, staging app environments -> ship minimal testable flow.
  - `TG-Product-Analytics`: `Mixpanel`, `Amplitude`, `GA4` -> collect activation and conversion events.
  - `TG-Behavior-Replay`: `Hotjar`, `FullStory` -> inspect user friction and validate event interpretation.
  - `Blocked`: no paid-channel budget changes.
- Done-definition: decision is made against predefined thresholds with auditable logs.
- Failure path: if guardrails break during run, pause test and escalate with mitigation options.

### Expert Card 09 - Outreach and Qualification Operator

- `fexp_name`: `outreach_qualification_operator`
- Mission: build qualified early pipeline and map real buying paths.
- Owns Level 2 units: `5.1`, `5.2`
- Input contract:
  - `icp_hypothesis`: source=`artifact`, ref=`ICP working definition`, freshness=`latest`
  - `positioning_brief`: source=`expert_handoff`, ref=`offer_positioning_architect`, freshness=`latest`
  - `contact_pool`: source=`api`, ref=`configured CRM/prospecting source`, freshness=`current cycle`
  - `outreach_results`: source=`api`, ref=`configured email/call engagement system`, freshness=`daily`
- Output contract: `Early Pipeline with Source and Response Data`, `Qualification Rubric and Deal Map`
- Tool groups (concrete):
  - `TG-Prospecting`: `Apollo`, `LinkedIn Sales Navigator`, firmographic filters -> build ICP-aligned contact pools.
  - `TG-Outreach-Execution`: `Gmail API`, `Outreach`, `Lemlist` -> run controlled outbound sequences.
  - `TG-CRM-Qualification`: `HubSpot` or `Salesforce` stages and custom fields -> log authority, timeline, pain, blocker map.
  - `Blocked`: no pricing governance changes, no RTM policy edits.
- Done-definition: qualified pipeline exists with explicit buyer process and blockers.
- Failure path: if conversion remains noise-level with qualified ICP, escalate for ICP/positioning reset.

### Expert Card 10 - Creative and Ads Operator

- `fexp_name`: `creative_ads_operator`
- Mission: generate creatives and run bounded ad tests for message-channel fit.
- Owns Level 2 units: supports `3.2`, `5.1`, `7.3` as execution doer.
- Input contract:
  - `positioning_brief`: source=`expert_handoff`, ref=`offer_positioning_architect`, freshness=`latest`
  - `experiment_card`: source=`expert_handoff`, ref=`experiment_method_designer`, freshness=`latest approved`
  - `creative_history`: source=`artifact`, ref=`message and creative test archive`, freshness=`latest`
  - `ad_metrics`: source=`api`, ref=`configured ad platform`, freshness=`daily`
- Output contract: `Creative Variant Pack`, `Ad Test Result Sheet`, `Message Fit Learnings`
- Tool groups (concrete):
  - `TG-Creative-Production`: `Figma`, `Canva`, `CapCut/Runway` -> produce static and video ad creatives with controlled variants.
  - `TG-Meta-Ads-Integration`: `Meta Marketing API (Facebook/Instagram)` -> create campaigns, ad sets, creatives, and capped budgets.
  - `TG-Google-Ads-Integration`: `Google Ads API` -> run search/display tests and export creative performance.
  - `TG-X-Account-Search`: `X/Twitter Search API` -> find relevant accounts, creators, and conversation clusters for targeting.
  - `TG-Google-Trends-Export`: `Google Trends query export` -> validate seasonality and regional demand before ad push.
  - `Blocked`: no budget-cap override, no unapproved channel expansion.
- Done-definition: winning message variants are identified with guardrail-safe performance.
- Failure path: if CPA or guardrail breaches threshold, stop spend and escalate with next-test set.

### Expert Card 11 - Pilot and First-Value Manager

- `fexp_name`: `pilot_first_value_manager`
- Mission: convert qualified deals into paid pilots and first-value evidence.
- Owns Level 2 units: `5.3`, `5.4`, `5.5`
- Input contract:
  - `qualified_deals`: source=`expert_handoff`, ref=`outreach_qualification_operator`, freshness=`current pipeline`
  - `pilot_template`: source=`artifact`, ref=`Pilot Template and Commitment Terms`, freshness=`latest`
  - `onboarding_assets`: source=`artifact`, ref=`Testable MVP Artifact and Onboarding Script`, freshness=`latest`
  - `usage_and_value_events`: source=`event_stream`, ref=`configured activation telemetry`, freshness=`near-real-time`
- Output contract: `Pilot Template and Commitment Terms`, `First-Win Evidence Pack`, `Repeatability Report v1`
- Tool groups (concrete):
  - `TG-Pilot-Contracting`: `DocuSign`, MSA/SOW templates -> issue and track paid pilot agreements.
  - `TG-Onboarding-Delivery`: `Asana` or `Jira` + onboarding checklist -> execute implementation milestones to first value.
  - `TG-Usage-Verification`: `Mixpanel/Amplitude` and account dashboards -> prove first-value achievement against pilot criteria.
  - `Blocked`: no channel architecture decisions.
- Done-definition: paid commitment and first-value evidence are both achieved.
- Failure path: if pilots do not convert despite first value, escalate to pricing/positioning review.

### Expert Card 12 - Retention and PMF Analyst

- `fexp_name`: `retention_pmf_analyst`
- Mission: stabilize activation/retention and produce PMF confidence score.
- Owns Level 2 units: `6.1`, `6.2`, `6.3`, `6.4`
- Input contract:
  - `activation_events`: source=`event_stream`, ref=`configured product analytics`, freshness=`near-real-time`
  - `revenue_events`: source=`api`, ref=`configured billing/subscription system`, freshness=`daily`
  - `cohort_tables`: source=`artifact`, ref=`Cohort Retention Review`, freshness=`weekly`
  - `pmf_survey_data`: source=`api`, ref=`configured PMF survey tool`, freshness=`current cycle`
- Output contract: `Activation Funnel and Friction Backlog`, `Cohort Retention Review`, `Revenue Quality Dashboard`, `PMF Confidence Scorecard`
- Tool groups (concrete):
  - `TG-Cohort-Analytics`: `BigQuery` or `Snowflake` + SQL models -> compute retention cohorts and activation lag.
  - `TG-Revenue-Quality`: `Stripe` or `Chargebee` + CRM account tiers -> compute GRR/NRR, expansion, contraction signals.
  - `TG-PMF-Survey`: `Typeform` or `SurveyMonkey` PMF instrument -> track Sean Ellis score and qualitative reasons.
  - `Blocked`: no direct campaign execution.
- Done-definition: PMF confidence is triangulated from behavior and sentiment, not one metric.
- Failure path: if metrics diverge (sentiment high, behavior weak), escalate with corrective experiment plan.

### Expert Card 13 - Churn Root-Cause Operator

- `fexp_name`: `churn_rootcause_operator`
- Mission: convert churn into actionable retention fixes.
- Owns Level 2 units: `6.5`
- Input contract:
  - `churn_list`: source=`api`, ref=`configured CRM/billing churn feed`, freshness=`weekly`
  - `exit_interviews`: source=`api`, ref=`configured interview/survey repository`, freshness=`current cycle`
  - `support_history`: source=`api`, ref=`configured support system`, freshness=`latest account state`
  - `pmf_confidence`: source=`expert_handoff`, ref=`retention_pmf_analyst`, freshness=`latest`
- Output contract: `Churn Root-Cause Backlog`
- Tool groups (concrete):
  - `TG-Churn-Trigger-Feed`: billing + CRM cancellation webhooks -> produce weekly churn queue.
  - `TG-Exit-Interview-Ops`: calendar scheduling + interview transcript capture -> run structured churn interviews.
  - `TG-Support-Root-Cause`: `Zendesk/Intercom` history and escalation data -> connect churn to service breakdowns.
  - `Blocked`: no direct pricing edits.
- Done-definition: top churn causes have owner, fix action, and verification metric.
- Failure path: if churn reason remains generic, require second-pass interviews before closure.

### Expert Card 14 - RTM and Unit-Economics Architect

- `fexp_name`: `rtm_unit_economics_architect`
- Mission: lock ICP/motion/channel/RTM with economic viability.
- Owns Level 2 units: `7.1`, `7.2`, `7.3`, `7.4`, `7.5`
- Input contract:
  - `repeatability_report`: source=`expert_handoff`, ref=`pilot_first_value_manager`, freshness=`latest`
  - `pmf_scorecard`: source=`expert_handoff`, ref=`retention_pmf_analyst`, freshness=`latest`
  - `channel_results`: source=`expert_handoff`, ref=`creative_ads_operator`, freshness=`latest cycle`
  - `cost_revenue_data`: source=`api`, ref=`configured finance/CRM/ads systems`, freshness=`monthly close + current run-rate`
- Output contract: `ICP v1 with Exclusion List`, `Primary Motion Decision Memo`, `Channel Scorecard and Priority Stack`, `RTM Rules of Engagement`, `Unit Economics Readiness Review`
- Tool groups (concrete):
  - `TG-Unit-Econ-Modeling`: finance warehouse + BI (`Looker/Metabase`) -> model CAC payback, margin, and stress scenarios.
  - `TG-Channel-Performance-Feeds`: `Meta`, `Google Ads`, `LinkedIn Ads` APIs -> compare channel-motion viability by cost and conversion.
  - `TG-RTM-Policy-Design`: route rules docs + deal-routing schemas -> define direct/partner ownership and conflict guardrails.
  - `Blocked`: no creative/content production tasks.
- Done-definition: one dominant motion and one to two winning channel-motion pairs are selected with viable economics.
- Failure path: if payback or margin profile fails target, freeze scale-up and escalate with redesign options.

### Expert Card 15 - Partner Lifecycle Operator (B2B2C/B2B2B)

- `fexp_name`: `partner_lifecycle_operator`
- Mission: operationalize recruit -> onboard -> enable -> activate -> optimize partner lifecycle.
- Owns Level 2 units: overlay on `7.4`, `8.2`, `8.5` for partner-led models.
- Input contract:
  - `rtm_rules`: source=`expert_handoff`, ref=`rtm_unit_economics_architect`, freshness=`latest approved`
  - `partner_pool`: source=`api`, ref=`configured PRM/partner registry`, freshness=`current cycle`
  - `deal_registration_log`: source=`api`, ref=`configured PRM/deal registration system`, freshness=`daily`
  - `shared_cx_feedback`: source=`api`, ref=`configured partner/customer feedback channel`, freshness=`weekly`
- Output contract: `Partner Lifecycle Plan`, `Partner Activation Scorecard`, `Channel Conflict Incident Log`
- Tool groups (concrete):
  - `TG-PRM-Core`: `PartnerStack`, `Impartner`, `Allbound` -> manage partner onboarding, tiers, and enablement status.
  - `TG-Deal-Registration-and-Lead-Routing`: PRM/CRM sync -> protect partner-sourced deals and assign ownership.
  - `TG-Partner-Enablement-LMS`: partner training, certification, playbook distribution -> improve time-to-first-deal.
  - `TG-MDF-Governance`: MDF request workflow and spend tracking -> control incentives and co-funded campaigns.
  - `Blocked`: no unilateral price overrides.
- Done-definition: partner activation and conflict governance are both measurable and operating.
- Failure path: if channel conflict repeats without closure, escalate with route ownership reset proposal.

### Expert Card 16 - Scale and Governance Operator

- `fexp_name`: `scale_governance_operator`
- Mission: codify winning motion, scale in controlled increments, enforce commercial guardrails.
- Owns Level 2 units: `8.1`, `8.2`, `8.3`, `8.4`, `8.5`
- Input contract:
  - `rtm_readiness`: source=`expert_handoff`, ref=`rtm_unit_economics_architect`, freshness=`latest`
  - `playbook_inputs`: source=`expert_handoff`, ref=`outreach_qualification_operator` and `pilot_first_value_manager`, freshness=`latest`
  - `operating_metrics`: source=`event_stream`, ref=`cross-functional KPI streams`, freshness=`weekly`
  - `exception_events`: source=`api`, ref=`configured governance/approval log`, freshness=`real-time`
- Output contract: `Playbook Library v1`, `Scale Increment Plan`, `Operating Ownership Model`, `Optimization Cadence Calendar and Logs`, `Commercial Governance Charter`
- Tool groups (concrete):
  - `TG-Playbook-Repository`: `Notion`, `Confluence`, versioned SOP docs -> codify repeatable motion.
  - `TG-Workflow-Automation`: `Zapier`, `Make`, internal orchestrators -> enforce handoffs and SLA alerts.
  - `TG-Governance-and-Approvals`: `Jira Service Management` or approval workflows -> log exceptions and decisions.
  - `TG-KPI-Operations-Dashboard`: cross-functional BI dashboards -> monitor scale increments and rollback triggers.
  - `Blocked`: no bypass of formal exception workflow.
- Done-definition: scaling increments, ownership, cadence, and exception governance are all auditable.
- Failure path: if scale increment breaks guardrails, trigger rollback to previous stable profile and escalate.

## Level 3 Expert Acceptance Criteria

Expert layer is accepted only when:

- each Level 2 unit is owned by exactly one primary expert;
- each expert has explicit input provenance rules;
- each expert has explicit output contract and done-definition;
- each expert has one explicit success path (done-definition) and one failure-path escalation;
- doers for research, creatives, ads, pilots, and governance are explicitly visible.

## Bot Integration Footprint Rule

- Bot-level integrations are the union of `TG-*` groups from experts included in that bot.
- If two experts require different access to the same platform, apply the stricter permission profile.
- `Blocked` rules from any included expert remain blocked at bot scope unless boss explicitly overrides.
- Before bot assembly, export a per-bot matrix: `integration`, `purpose`, `access mode`, `owning expert`.

## SMB Model Overlays (B2B, B2C, B2B2C, B2B2B)

These overlays adjust execution logic without changing the 8-stage backbone.

### B2B

- More weight on buying committee mapping, proof artifacts, and implementation trust.
- Stage 5-7 require explicit commercial motion design (sales cycle and ROI narrative).

### B2C

- More weight on activation speed, funnel leakage, and repeated behavior signals.
- Stage 4-6 prioritize conversion/retention loops before heavy sales structures.

### B2B2C

- Requires dual validation: intermediary partner economics + end-consumer experience.
- Stage 7-8 must include partner enablement and shared CX consistency governance.

### B2B2B

- Requires partner lifecycle discipline: recruit -> onboard -> enable -> activate -> optimize.
- Stage 7-8 require lead routing, incentive alignment, and channel conflict controls early.

## Reliability Notes (For Next Decomposition Steps)

- Prefer explicit pass/fail thresholds for each substage before resource expansion.
- Keep outputs artifact-driven to reduce orchestration ambiguity later in bot design.
- Avoid parallel channel sprawl until one channel-motion pair shows repeatability.
- Treat partner operations as first-class system design in B2B2C/B2B2B cases.

## Notes

- This is a living document and should be expanded by depth levels.
- This version adds Level 3 (one step deeper than Level 2).

## Source Pack (Used For This Version)

### Opportunity and Discovery

- https://www.jpattonassociates.com/opportunity-canvas/
- https://www.alexandercowan.com/customer-discovery-handbook/
- https://steveblank.com/2009/09/17/the-path-of-warriors-and-winners/
- https://web.stanford.edu/class/me113/d_thinking.html
- https://dschool.stanford.edu/resources/the-bootcamp-bootleg

### Validation, MVP, and Early Sales

- https://blog.logrocket.com/product-management/concierge-wizard-of-oz-mvp
- https://stripe.com/blog/atlas-starting-sales
- https://www.d-eship.com/step2/
- https://www.d-eship.com/step4/
- https://www.oreilly.com/library/view/the-startup-owners/9781119690689/c10.xhtml

### PMF and Fit Consolidation

- https://www.reforge.com/guides/measure-product-market-fit-with-retention-and-growth
- https://learningloop.io/plays/product-market-fit-survey
- https://www.reforge.com/blog/four-fits-growth-framework
- https://jobs-to-be-done.com/outcome-driven-innovation-odi-is-jobs-to-be-done-theory-in-practice-2944c6ebc40e

### GTM, RTM, and Scaling

- https://www.oxx.vc/go-to-market-fit/introduction-to-go-to-market-fit/
- https://www.oxx.vc/go-to-market-fit/
- https://medium.com/@yegg/the-bullseye-framework-for-getting-traction-ef49d05bfd7e
- https://medium.com/@yegg/the-19-channels-you-can-use-to-get-traction-93c762d19339
- https://amplitude.com/blog/pirate-metrics-framework
- https://en.wikipedia.org/wiki/Crossing_the_Chasm

### Partner-Led and B2B2X Execution

- https://demandzen.com/b2b-channel-partner-lifecycle-guide/
- https://www.journeybee.io/resources/partner-lifecycle-management
- https://www.forrester.com/blogs/shared-customer-experience-what-happens-when-your-cx-depends-on-partners/
- https://umbrex.com/resources/frameworks/marketing-frameworks/channel-conflict-management-framework/

### Additional Sources Used For Level 2 and Level 3

- https://brianbalfour.com/essays/channel-model-fit-for-user-acquisition
- https://brianbalfour.com/four-fits-growth-framework
- https://review.firstround.com/0-5m-how-to-nail-founder-led-sales/
- https://www.nngroup.com/articles/success-rate-the-simplest-usability-metric/
- https://measuringu.com/task-completion/
- https://mixpanel.com/blog/guardrail-metrics
- https://support.google.com/google-ads/answer/6167129?hl=en
- https://www.klue.com/blog/churn-interviews
- https://umbrex.com/resources/frameworks/marketing-frameworks/route-to-market-design-framework/
- https://learningloop.io/plays/product-market-fit-survey
