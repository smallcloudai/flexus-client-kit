---
name: idea-to-first-money
description: End-to-end playbook for going from a raw product idea to a signed first paying customer — sequence of bots, skills, and integration providers required at each phase
---

This skill defines the canonical orchestration sequence for taking a B2B SaaS product idea from zero to first paid contract. Use this as the primary reference when a user asks to "start from scratch," "validate a new product," or "get first customers." Delegate work to Researcher, Strategist, and Executor bots in the order defined below. Each phase depends on the artifacts from the previous phase — do not skip or reorder phases.

The full journey spans 20 skills across 3 bots. Start with Phase 0 every time — no exceptions. A raw idea is not a valid input for research.

---

## Phase 0: Idea → Hypothesis
**Bot: Boss (clarification) → Strategist (formalization)**

Goal: before any research begins, convert the raw idea into a falsifiable, prioritized hypothesis stack. Research without a hypothesis produces data, not answers.

**Boss role:** ask the user 3 questions before handing off to Strategist:
1. What problem do you think exists, and for whom specifically?
2. What evidence (however weak) made you think this problem is real?
3. What would change your mind — what would "this is wrong" look like?

Do not accept vague answers. "B2B companies need better analytics" is not a hypothesis. "Mid-market RevOps teams at 50-200 person SaaS companies lose 6+ hours/week reconciling CRM and billing data manually, and would pay to eliminate that" is a hypothesis.

### experiment-hypothesis
**Bot: Strategist**

Formalize the raw idea into a structured, falsifiable hypothesis stack with P0-P3 priorities.
- **No external providers required** — this is a structured reasoning task
- **Key outputs:** market hypotheses (who has the problem and how badly), product hypotheses (what would solve it), channel hypotheses (how to reach them)
- **Standard format per hypothesis:** `We believe [claim]. We'll test by [method]. Validated if [metric ≥ threshold] by [date]. Rejected if [falsification condition].`
- **Rule:** P0 hypotheses are fatal-risk hypotheses — if false, the business doesn't exist. Test these first, cheapest, fastest.
- **Output:** `/strategy/hypothesis-stack`

**Handoff to Phase 1:** the hypothesis-stack must define the target segment hypothesis clearly enough to write a recruitment screener. If the segment is still "anyone who might be interested" — go back and sharpen it.

---

## Phase 1: Problem Discovery
**Bot: Researcher**

Goal: validate or reject the P0 market hypothesis through direct evidence from real buyers.

### discovery-recruitment
Recruit participants for interviews and surveys.
- **Providers:** Prolific (self-serve research panel), Cint (enterprise sample marketplace), MTurk (crowd panel), UserTesting (usability / reviewed access), User Interviews (Research Hub panel sync), Respondent (B2B interview recruiting), PureSpectrum (enterprise sample buying), Dynata (enterprise sample + respondent exchange), Lucid Marketplace (enterprise marketplace / consultant-led onboarding), Toloka (crowd-based validation)
- **Key methods:** screener design, quota management, pilot launch before full scale, anti-gaming checks
- **Output:** `/discovery/{study_id}/recruitment-plan`, `/discovery/{study_id}/recruitment-funnel`

### discovery-interview-capture
Capture and code interview transcripts using JTBD framework.
- **Providers:** Zoom, Gong, Fireflies, Dovetail, Fathom (recording + transcription)
- **Key methods:** JTBD event coding (struggle, workaround, trigger, decision_criteria, objection), saturation tracking (stop at <5% new codes), consent chain enforcement
- **Output:** `/discovery/{study_id}/corpus`, `/discovery/{study_id}/jtbd-outcomes`

### pain-alternatives-landscape
Map all alternatives buyers use or consider — including non-consumption.
- **Providers:** web browser (G2, Capterra, Reddit, ProductHunt, Similarweb)
- **Key methods:** four-tier framework (direct / adjacent / DIY / non-consumption), switch-to and switch-away trigger extraction from reviews and interviews
- **Output:** `/pain/alternatives-landscape`

### pain-wtp-research
Establish pricing boundaries before any strategy work.
- **Providers:** SurveyMonkey, Typeform (survey delivery)
- **Key methods:** Economic Value Estimation (EVE) first, then Van Westendorp PSM and/or Gabor-Granger; apply 30-50% hypothetical bias discount to all stated WTP
- **Prerequisite:** solution/problem fit must be confirmed before running WTP
- **Output:** `/pain/wtp-research-{YYYY-MM-DD}`

---

## Phase 2: Market Intelligence
**Bot: Researcher**

Goal: identify and score the best-fit accounts before strategy is built.

### signal-search-seo
Detect search demand signals to validate market size and growth direction.
- **Providers:** Ahrefs or SEMrush (keyword volume, trends), Similarweb (traffic estimation)
- **Key methods:** classify every source as direct/sampled/modeled; never conflate; run quality gates (freshness, comparability, SRM, SERP context)
- **Output:** `/signals/search-seo-{YYYY-MM-DD}`

### segment-firmographic
Enrich and profile target company segments with field-level evidence quality.
- **Providers:** Apollo (primary), PDL / People Data Labs (secondary); Clearbit deprecated as of April 30, 2025 — do not use outside HubSpot environments
- **Key methods:** cross-validate across 2+ providers; freshness gate (6-month max); technographics via BuiltWith signals; never impute null fields
- **Output:** `/segments/{segment_id}/firmographic`

### segment-icp-scoring
Score and tier accounts from firmographic + signal + engagement data.
- **Providers:** uses artifacts from segment-firmographic and signal skills (no new external providers)
- **Key methods:** three subscores (fit_score 40%, intent_score 35%, engagement_score 25%), recency decay on intent signals, tier assignment (T1 ≥75, T2 ≥50)
- **Output:** `/segments/{segment_id}/icp-scorecard`

---

## Phase 3: Strategy
**Bot: Strategist**

Goal: convert research artifacts into a defensible go-to-market strategy, offer design, pricing, and MVP scope.

### positioning-market-map
Build a competitive positioning map with two explicit lenses: buyer perception and capability/execution.
- **Providers:** web browser (G2, competitor sites, review sites) to validate competitor placement
- **Inputs required:** `/pain/alternatives-landscape`, `/discovery/{study_id}/jtbd-outcomes`
- **Output:** `/strategy/positioning-map`

### positioning-messaging
Convert validated customer language into a positioning statement, message hierarchy, and objection responses.
- **Providers:** no external API calls; uses research artifacts only
- **Key rule:** steal language from customer quotes — never invent; no absolute superlatives without evidence
- **Output:** `/strategy/messaging`

### offer-design
Design the packaging model and tier structure.
- **Providers:** no external API calls; uses research + WTP artifacts
- **Key decision:** choose packaging model (good/better/best, base+modules, single, freemium) with documented rejection rationale for alternatives
- **Output:** `/strategy/offer-design`

### pricing-model-design
Select the pricing model architecture (subscription, per-seat, usage-based, outcome-based).
- **Providers:** no external API calls; uses WTP and offer artifacts
- **Key gates:** value alignment + customer predictability + supplier operability must all pass
- **Output:** `/strategy/pricing-model`

### pricing-pilot-packaging
Design pilot commercial terms: structure, success criteria, conversion conditions.
- **Providers:** no external API calls; uses WTP and offer artifacts
- **Key rule:** pilot price optimizes for conversion quality, not pilot revenue; commercial paperwork (legal/security/procurement) tracked as parallel workstream from Day 1 of the pilot
- **Output:** `/strategy/pilot-package`

### gtm-channel-strategy
Select 1-2 acquisition channels for the go-to-market motion.
- **Providers:** web browser (competitor ads, LinkedIn, channel research), Ahrefs/SEMrush (SEO demand data)
- **Key rule:** no more than 2 channels in parallel; channel must match buyer behavior and segment reachability
- **Output:** `/strategy/gtm-channels`

### mvp-scope
Define minimum feature set anchored to one P0 hypothesis.
- **Providers:** no external API calls; uses hypothesis-stack and JTBD artifacts
- **Key rule:** declare scope_mode (experiment_scope vs. release_scope) before feature discussion; exclusion-first logic
- **Output:** `/strategy/mvp-scope`

### mvp-validation-criteria
Pre-register success/failure thresholds before any pilot starts.
- **Providers:** no external API calls; uses mvp-scope and ICP artifacts
- **Key rule:** lock criteria before launch; post-hoc threshold changes must be formally logged; quality gates (SRM, schema violations, event drops) are veto constraints
- **Output:** `/strategy/mvp-validation-criteria`

---

## Phase 4: Execution — Pipeline to First Money
**Bot: Executor**

Goal: reach the right people, run the pilot, convert to a signed contract.

### pipeline-contact-enrichment
Enrich, verify, and score contacts before any outreach.
- **Providers:** Apollo (search + enrichment), PDL (secondary enrichment), Lusha (job-change signals)
- **Email verification:** Apollo built-in deliverability score; only `valid` status enters outreach — no exceptions
- **Key rule:** re-enrich every 6 months; no outreach to unverified emails (damages domain reputation above Gmail/Yahoo 2% bounce threshold)
- **Output:** `/pipeline/{campaign_id}/contacts`

### pilot-onboarding
Manage kick-off and first-value delivery for each pilot customer.
- **Providers:** Calendly or Google Calendar (scheduling), Zendesk (task tracking)
- **Key milestones:** Mutual Action Plan drafted before kick-off (not during); aha moment ≤48 hours; first login check at 72 hours; health score weekly (40% usage + 30% milestone + 30% satisfaction)
- **Required kick-off attendees:** champion + economic buyer + IT contact (if integrations)
- **Output:** `/pilots/{account_id}/onboarding`

### pilot-success-tracking
Track success criteria progress and run the parallel commercial track.
- **Providers:** SurveyMonkey or Typeform (structured surveys), Zendesk (ticket tracking), Google Calendar (review scheduling), Salesforce (opportunity stage management)
- **Key rule:** baseline must be captured at Day 1 using the same measurement source used at end; commercial track (legal/security/procurement) starts no later than Day 15 of a 30-day pilot
- **Escalation triggers:** P0 criterion at risk by mid-point, customer silent >5 days, LOB budget owner not engaged by mid-point
- **Output:** `/pilots/{account_id}/status-{date}`

### pilot-conversion
Facilitate the success review and drive to signed contract.
- **Providers:** PandaDoc or DocuSign (contract generation + e-signature), Salesforce (opportunity stage)
- **Critical rule:** Salesforce stage = `contract_sent` when document is sent; `closed_won` ONLY after signature confirmed — never at send time
- **Objection playbook:** budget objection → quantify ROI before any discount; "need more time" → force specificity + milestone-based off-ramp; "missing stakeholder" → schedule multi-party call, never relay via champion alone
- **Expansion plan documented at conversion:** seat expansion trigger (80% utilization), feature upsell (90-day QBR), adjacent use case, next QBR date
- **Output:** `/pilots/{account_id}/conversion-summary`

---

## Integration Provider Summary

| Category | Providers |
|---|---|
| Interview / recording | Zoom, Gong, Fireflies, Dovetail, Fathom |
| Research panels | Prolific, Cint, MTurk, UserTesting, User Interviews, Respondent, PureSpectrum, Dynata, Lucid Marketplace, Toloka |
| Survey | SurveyMonkey, Typeform |
| SEO / demand signals | Ahrefs, SEMrush, Similarweb |
| Web research | browser (G2, Capterra, Reddit, ProductHunt, LinkedIn) |
| Contact enrichment | Apollo, PDL |
| Buying signals | Lusha |
| Calendar / scheduling | Google Calendar, Calendly |
| Support / ticketing | Zendesk |
| CRM | Salesforce |
| Contract / e-signature | PandaDoc, DocuSign |
| **Not registered (gap)** | ZeroBounce/NeverBounce (email verification), Mixpanel/Amplitude/Segment (product analytics for health scoring) |

## Critical Sequencing Rules

1. **Never skip Phase 0.** A raw idea is not a valid research brief. Hypothesis stack must exist before recruitment screener is written.
2. **Never start Phase 3 without Phase 1 complete.** Strategy built on assumptions, not interviews, is fiction.
3. **Never run WTP research before problem/solution fit is confirmed.** Invalid data is worse than no data.
4. **Never start Phase 4 outreach before Phase 3 pilot package is defined.** Undefined success criteria guarantee pilot purgatory.
5. **Never start Salesforce Closed Won before contract signature confirmed.** Revenue recognition must follow legal completion.
6. **Commercial track in pilot-success-tracking must start Day 15 at latest.** Starting after the success review creates 3-6 month delays.
