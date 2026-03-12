# Research: rtm-sales-playbook

**Skill path:** `strategist/skills/rtm-sales-playbook/`  
**Bot:** strategist  
**Research date:** 2026-03-05  
**Status:** complete

---

## Context

`rtm-sales-playbook` defines how the strategist bot should produce an operational B2B sales playbook from evidence, not brainstorming. The skill scope is discovery call structure, qualification criteria, objection handling scripts, and demo flow. The key constraint is that recommendations must come from real conversation artifacts (for example, call intelligence and pipeline outcomes), so the playbook reflects what closes in-market rather than generic sales advice.

Research focus for this pass: update methodology and structure using 2024-2026 evidence, map current tools/channels/data constraints, define interpretation quality thresholds (signal vs noise), and codify anti-pattern detection/mitigation. Older sources are only used where still operationally useful and are explicitly labeled Evergreen.

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
- [x] No invented tool names, method IDs, or API endpoints
- [x] Contradictions between sources are explicitly noted
- [x] Findings volume is within 800-4000 words

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

1. Discovery quality is strongly linked to disciplined dialogue rather than rep-dominant monologue. Gong’s 2025 analysis reported won calls around 57% rep talk vs 62% for lost calls, and winners asking fewer but better-targeted questions (roughly 15-16 vs ~20 for lost calls) [A1-S1]. This suggests the playbook should gate progression on balanced interaction and question quality, not just checklist completion.

2. Evergreen Gong benchmarks still matter, but they should be treated as directional: earlier datasets suggest strongest performance around 11-14 high-quality discovery questions and identification of multiple business problems [A1-S2][A1-S3]. Tension with newer data (15-16 on won calls) implies threshold bands should be team-calibrated, not fixed constants.

3. Modern BANT usage is multi-conversation and committee-aware, not a one-call interrogation. HubSpot’s 2025 updates emphasize ongoing qualification threads (budget, authority, need, timeline) that can be completed over time [A1-S4][A1-S5]. The playbook should require evidence-backed fields before stage advancement.

4. MEDDICC-style elements remain useful as strict stage gates in complex B2B deals: clear economic buyer, validated champion, and explicit decision criteria [A1-S6][A1-S7][A1-S8]. The methodology implication is to forbid proposal-stage progression when these are unknown in higher-ACV opportunities.

5. Buyer behavior data indicates reps often enter late in the journey and need immediate multi-threading. 6sense-reported findings (2024 coverage) indicate many buyers initiate first contact near ~70% through process, often with requirements and a preferred vendor already in mind [A1-S9][A1-S10]. Practical impact: early calls must map stakeholders and evaluation criteria immediately, not just run generic discovery.

6. Demo methodology should be a discovery-mirrored story arc, not a feature tour. Evergreen Gong demo analysis found stronger outcomes when demos follow discovery topic order and avoid long uninterrupted pitching (no won demo in that dataset with >76s monologue) [A1-S11]. This still maps well to current “problem -> workflow -> outcome -> next step” patterns.

7. Objection handling should be frequency-weighted and evidence-derived. Gong’s 2024 large-sample objection analysis found top objection clusters account for most objection volume [A1-S12]. This supports curating objection scripts by observed frequency/severity from call artifacts, not brainstormed edge cases.

8. Next-step discipline (Mutual Action Plan behavior) is a practical win-rate lever. Salesforce guidance and Outreach reporting show that explicit owner/date/outcome commitments improve execution and correlate with better win outcomes [A1-S13][A1-S14]. The playbook should include mandatory MAP fields in handoff and stage exit.

9. Follow-up coverage and speed are now foundational process controls, not optional productivity tips. Salesforce’s 2025 customer-zero case highlights measurable gains when lead response and re-engagement are operationalized with tight SLAs [A1-S15]. Discovery quality is weakened if qualified leads are not handled quickly and consistently.

**Sources:**
- [A1-S1] Gong Labs, "Mastering the talk-to-listen ratio in sales calls," 2025-08-21 (updated 2025-03-20): https://www.gong.io/resources/labs/talk-to-listen-conversion-ratio
- [A1-S2] Gong Labs (Evergreen), "Effective strategies for successful sales discovery calls," 2017-06-18: https://www.gong.io/resources/labs/nailing-your-sales-discovery-calls/
- [A1-S3] Gong Labs (Evergreen), "Mastering discovery calls to close deals effectively," 2017-07-05: https://www.gong.io/resources/labs/deal-closing-discovery-call/
- [A1-S4] HubSpot, "How I use BANT to qualify prospects," updated 2025-07-31: https://blog.hubspot.com/sales/bant
- [A1-S5] HubSpot, "Sales Qualification: Gauging Whether a Lead Aligns With Your Offering," updated 2025-03-18: https://blog.hubspot.com/sales/ultimate-guide-to-sales-qualification
- [A1-S6] MEDDICC, "Economic Buyer": https://meddicc.com/what-is-meddpicc/economic-buyer
- [A1-S7] MEDDICC, "Champion": https://meddicc.com/what-is-meddpicc/champion
- [A1-S8] MEDDICC, "Decision Criteria": https://meddicc.com/what-is-meddpicc/decision-criteria
- [A1-S9] Demand Gen Report (reporting 6sense findings), 2024-10-10: https://www.demandgenreport.com/industry-news/80-of-b2b-buyers-initiate-first-contact-once-theyre-70-through-their-buying-journey/48394/
- [A1-S10] 6sense (Evergreen article covering survey findings), "The Point of First Contact Constant": https://6sense.com/blog/dont-call-us-well-call-you-what-research-says-about-when-b2b-buyers-reach-out-to-sellers/
- [A1-S11] Gong Labs (Evergreen), "Effective strategies for conducting successful sales demos," 2017-09-14: https://www.gong.io/resources/labs/sales-demos/
- [A1-S12] Gong Labs, "Top objections across 300M cold calls," 2024-07-31: https://www.gong.io/resources/labs/we-found-the-top-objections-across-300m-cold-calls-heres-how-to-handle-them-all/
- [A1-S13] Salesforce, "A Guide to Using a Mutual Action Plan," 2024-04-12: https://www.salesforce.com/blog/mutual-action-plan/?bc=HA
- [A1-S14] Outreach, "How to improve win rates by 26% with a best-in-class mutual action plan," 2024-02-19: https://www.outreach.io/resources/blog/how-to-use-mutual-action-plans
- [A1-S15] Salesforce, "Agentic Sales: How Salesforce Found a Better Way To Sell," 2025-10-09: https://www.salesforce.com/blog/ai-for-lead-qualification/

---

### Angle 2: Tool, Channel & Data Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

1. Call intelligence tooling is mature enough to support evidence-first playbook loops. Gong documents capture/transcribe/analyze workflows and 2025-2026 updates include AI features for pattern detection and extraction [A2-S1][A2-S2]. This makes recurring objection/theme mining feasible without full manual coding.

2. HubSpot and Salesloft provide concrete integration points for conversation and pipeline data, but with non-trivial technical constraints. HubSpot recording/transcription ingestion has strict media/transport requirements [A2-S3], while Salesloft documents conversation/transcription endpoints including “extensive” payloads [A2-S7][A2-S8][A2-S9]. Practical implication: ingestion QA must be part of the methodology.

3. Pipeline normalization is a prerequisite for interpretation quality. HubSpot’s pipeline and deal APIs, stage IDs, and history access require explicit ID mapping and stage discipline [A2-S4][A2-S5][A2-S6]. Without normalized stage taxonomy, signal comparisons and win/loss learning are unreliable.

4. Sales engagement telemetry can be misleading if semantics are ignored. Gong Engage export behavior has completion-state caveats [A2-S10], and Outreach metrics include aggregate/non-unique semantics in places [A2-S11][A2-S12]. You should not combine cross-platform activity metrics without a common metric dictionary.

5. Consent and retention controls vary materially by platform and jurisdiction. Gong exposes consent profile controls with provider dependencies [A2-S13]; Microsoft Teams policies include explicit consent/retention behaviors and default expiration controls [A2-S14]. This should be encoded as compliance guardrails in the playbook artifact, not external tribal knowledge.

6. Regulatory constraints influence data channels and usage permissions. ICO guidance (2025 update) emphasizes lawful basis/transparency/objector handling for direct marketing and related processing [A2-S15]. For EU/UK teams, this directly affects which call artifacts can be used for model and script optimization.

7. Vendor capabilities are often well-documented while pricing/rate limits are not. Salesloft and Outreach references provide endpoint/shape clarity but not complete public quota/pricing tables [A2-S7][A2-S11]. A safe research posture is “not publicly documented” rather than assumptions.

8. Win/loss enrichment loops are increasingly productized (for example, closed-won linked intent features) [A2-S16], but claims are often release-note level; teams still need local validation before hard-coding thresholds.

**Tool Matrix (compact):**

| Tool | Category | Strengths | Limitations | Sources |
|---|---|---|---|---|
| Gong | Call intelligence + analytics | Conversation capture, transcript analytics, AI pattern features | Some feature/plan boundaries not fully public | [A2-S1][A2-S2] |
| HubSpot | CRM + conversation ingestion | Structured pipelines/deals; explicit ingestion requirements | Data quality depends on media and stage ID discipline | [A2-S3][A2-S4][A2-S5][A2-S6] |
| Salesloft | Conversation API | Documented conversation/transcription endpoints | Pricing/rate limits not fully public | [A2-S7][A2-S8][A2-S9] |
| Outreach | Sales engagement API | Sequence/event primitives; activity telemetry | Metric semantics require care; pricing/rate limits not fully public | [A2-S11][A2-S12] |
| Microsoft Teams | Recording governance | Explicit consent and retention controls | Policy behavior requires tenant configuration | [A2-S14] |
| Gong Engage export | Channel-to-CRM data sync | Multi-channel activity capture | Export timing/state caveats | [A2-S10] |

**Sources:**
- [A2-S1] Gong Help, "Capture and analyze calls": https://help.gong.io/docs/capturing-and-analyzing-your-calls
- [A2-S2] Gong Help, "Our monthly updates" (2025-2026): https://help.gong.io/docs/our-monthly-updates
- [A2-S3] HubSpot Developers, "Call recordings and transcripts": https://developers.hubspot.com/docs/guides/apps/extensions/calling-extensions/recordings-and-transcriptions
- [A2-S4] HubSpot Developers, "CRM API | Pipelines": https://developers.hubspot.com/docs/api/crm/pipelines
- [A2-S5] HubSpot Knowledge Base, "Set up and manage object pipelines," updated 2026-01-27: https://knowledge.hubspot.com/object-settings/set-up-and-customize-your-deal-pipelines-and-deal-stages
- [A2-S6] HubSpot Developers, "CRM API | Deals": https://developers.hubspot.com/docs/api/crm/deals
- [A2-S7] Salesloft Developers, "Conversations": https://developers.salesloft.com/docs/api/conversations/
- [A2-S8] Salesloft Developers, "Fetch an extensive conversation": https://developers.salesloft.com/docs/api/conversations-find-one-extensive/
- [A2-S9] Salesloft Developers, "Fetch a transcription": https://developers.salesloft.com/docs/api/conversations-transcriptions-find-one-transcript/
- [A2-S10] Gong Help, "How Engage data is exported to your CRM": https://help.gong.io/docs/how-engage-exports-data-to-your-crm
- [A2-S11] Outreach Developers, "Common API patterns": https://developers.outreach.io/api/common-patterns
- [A2-S12] Outreach Developers, "Sequence Step API reference": https://developers.outreach.io/api/reference/tag/Sequence-Step/
- [A2-S13] Gong Help, "Call recording and consent settings": https://help.gong.io/docs/call-recording-and-consent-settings
- [A2-S14] Microsoft Learn, "Manage Teams recording policies," updated 2025-05-13: https://learn.microsoft.com/en-us/microsoftteams/meeting-recording?tabs=meeting-policy
- [A2-S15] ICO, direct marketing/live calls guidance, updated 2025-08-20: https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-on-direct-marketing-using-live-calls/what-else-do-we-need-to-consider
- [A2-S16] ZoomInfo Pipeline, "Q4 2024 release notes": https://pipeline.zoominfo.com/sales/zoominfo-q4-2024-release

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

1. Multithreading is a high-signal indicator, but thresholds vary by segment. Forrester reports large buying groups, Gong finds major uplift with higher contact coverage in larger deals, and Ebsta reports elite sellers with broader active stakeholder engagement [A3-S1][A3-S2][A3-S3]. Implication: enforce stakeholder coverage by ACV band, not one global target.

2. Early economic-buyer/champion involvement is a stronger signal than “friendly user engagement.” Ebsta’s findings point to substantial performance differences when decision-maker access happens earlier [A3-S3][A3-S4]. Playbook interpretation should treat delayed EB access as risk escalation.

3. Stage velocity and meeting cadence are practical warning signals. Ebsta benchmark reporting ties long inactivity/slippage to materially lower outcomes [A3-S4]. Interpretation policy should include inactivity thresholds and slippage bands that trigger reset/re-qualification.

4. Next-step quality outperforms “calendar next step” as a predictor. MAP-driven execution correlates with better outcomes in Outreach reporting [A3-S5]. Interpretation should score next steps for owner/date/outcome/stakeholder specificity.

5. Talk/listen metrics are useful but easy to overfit. Gong’s newer data shows modest won/lost average differences while consistency and interaction quality matter more [A3-S6]. Avoid rigid single-number coaching.

6. AI adoption claims are noisy without data readiness context. Salesforce and Clari show that AI usage can correlate with growth while many teams still miss targets and report low trust/readiness in core revenue data [A3-S7][A3-S8]. Interpretation must gate playbook changes on data quality checks.

7. Robust playbook updates require validation discipline: cohort slicing, recent win/loss feedback, and scorer calibration. Clari/Gong/Klue references support larger-sample, freshness-aware, and method-aware interpretation approaches [A3-S8][A3-S9][A3-S10][A3-S11]. This should become an explicit “change approval” protocol.

8. Source disagreement is common and should be handled procedurally, not rhetorically. Stakeholder benchmarks and talk-ratio guidance differ by source and population [A3-S2][A3-S3][A3-S6]. Resolve by local baselineing and requiring confirmation from both conversation and pipeline data before changing scripts.

**Practical Thresholds / Decision Rules:**

- Treat single-threaded opportunities as high risk; use segment-specific stakeholder minimums informed by ACV and motion complexity [A3-S1][A3-S2][A3-S3].
- Require economic buyer identified before proposal in complex deals; require champion evidence before forecast commit [A3-S3][A3-S4].
- Flag opportunities with >7 days meeting gap or stale weekly progress as “re-qualify required” [A3-S4].
- Use slippage bands to trigger escalation and pipeline hygiene checks [A3-S4].
- Use talk ratio as a band + consistency check (not a universal golden ratio) [A3-S6].
- Require structured MAP fields before high-confidence stage advancement [A3-S5].
- Apply a data readiness gate before script updates (coverage/trust/completeness checks) [A3-S7][A3-S8].
- Require monthly (or faster) win/loss freshness reviews for all major playbook edits [A3-S10].

**Sources:**
- [A3-S1] Forrester press release, "The State Of Business Buying, 2024," 2024-12-04: https://www.forrester.com/press-newsroom/forrester-the-state-of-business-buying-2024/
- [A3-S2] Gong Labs, "Top reps orchestrate with AI," 2025-04-28: https://www.gong.io/blog/data-shows-top-reps-dont-just-sell-they-orchestrate-with-ai
- [A3-S3] Ebsta, "What sets elite sellers apart," 2025-02-18 (updated 2025-08-27): https://www.ebsta.com/blog/what-sets-elite-sellers-apart/
- [A3-S4] Ebsta, "GTM Benchmark Report 2025: Sales Efficiency": https://benchmarks.ebsta.com/hubfs/V3%202025%20Benchmark%20Report/2025_gtm_digest_-_sales_efficiency.pdf?hsLang=en
- [A3-S5] Outreach, "How to improve win rates by 26% with MAP," 2024-02-19: https://www.outreach.io/resources/blog/how-to-use-mutual-action-plans
- [A3-S6] Gong Labs, "Talk-to-listen ratio," 2025 update: https://www.gong.io/resources/labs/talk-to-listen-conversion-ratio
- [A3-S7] Salesforce News, sales AI statistics, 2024-07-25: https://www.salesforce.com/news/stories/sales-ai-statistics-2024/?bc=HA
- [A3-S8] Clari press release, 2026-01-14: https://www.clari.com/press/new-clari-labs-research-reveals-enterprises-missed-revenue-targets-in-2025/
- [A3-S9] Gong Labs, "State of Revenue AI 2026" report PDF: https://www.gong.io/files/gong-labs-state-of-revenue-ai-2026.pdf
- [A3-S10] Klue, "2025 Win-Loss Trends Report": https://klue.com/win-loss-trends-report
- [A3-S11] Gong Help, "All about scorecards": https://help.gong.io/docs/all-about-scorecards

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

1. **Playbook shelfware:** teams publish playbooks but do not instrument coaching/adoption, leading to inconsistent execution [A4-S1].
   - Detection signal: no measurable coaching loops, no adoption KPI trend, no behavior consistency checks.
   - Consequence: weak rep consistency and poor transfer to outcomes.
   - Mitigation: build recurring reinforcement cycles tied to observed call and pipeline behavior.

2. **Premature pitching in discovery:** reps pivot to product too early.
   - Detection signal: talk-share drift toward lost-call profile and low buyer participation [A4-S4].
   - Consequence: poor problem diagnosis and weaker conversion.
   - Mitigation: enforce diagnose-first stage exit criteria.

3. **Checklist interrogation:** question-volume spikes without context.
   - Detection signal: high question count with low problem-depth capture [A4-S4][A4-S5].
   - Consequence: buyer fatigue and noisy qualification data.
   - Mitigation: quality-weighted questioning with explicit intent per question.

4. **Fake qualification (box-checking):** “BANT complete” but weak fit/value proof.
   - Detection signal: late-stage losses tagged poor fit/value [A4-S3].
   - Consequence: forecast pollution and wasted demo/proposal effort.
   - Mitigation: evidence-gated qualification with disqualifier rules.

5. **Script recitation for objections:** reps answer before diagnosing objection class.
   - Detection signal: transactional buyer feedback and weak trust signals [A4-S2].
   - Consequence: lower persuasion and more discount pressure.
   - Mitigation: pause -> clarify -> respond -> confirm -> pivot protocol.

6. **Discount-first reflex:** immediate price concession.
   - Detection signal: repeated value-for-money loss reasons and pricing-heavy late demos [A4-S3][A4-S6].
   - Consequence: margin erosion without solving value proof gaps.
   - Mitigation: value-first sequence, pricing only after quantified outcome framing.

7. **Feature-tour demos:** broad product tour disconnected from discovery priorities.
   - Detection signal: demo order does not map to discovery pain rank [A4-S6].
   - Consequence: low relevance perception.
   - Mitigation: discovery-mirrored demo narrative with one core workflow.

8. **Monologue-heavy demos:**
   - Detection signal: long uninterrupted pitch segments (Evergreen benchmark >76s risk marker) [A4-S6].
   - Consequence: reduced interaction and weak next-step commitments.
   - Mitigation: short explanation bursts with explicit interaction checkpoints.

9. **Consent blind spots in call recording/transcription:**
   - Detection signal: no auditable consent trail or jurisdiction-aware routing [A4-S7][A4-S10].
   - Consequence: legal/regulatory risk (TCPA/all-party contexts).
   - Mitigation: explicit consent capture policy + audit log requirements.

10. **Data minimization failure (hoarding transcripts/PII):**
    - Detection signal: indefinite retention and unclear lawful basis [A4-S8][A4-S9].
    - Consequence: elevated enforcement and breach exposure.
    - Mitigation: minimization, purpose limitation, retention boundaries, and lawful-basis documentation.

**Bad vs Good Output Patterns:**

- `Discovery`: Bad = pitch-first; Good = diagnose-first with interaction discipline [A4-S4][A4-S5]
- `Qualification`: Bad = checkbox progression; Good = evidence-gated advancement [A4-S3]
- `Objections`: Bad = canned rebuttal; Good = diagnosis-driven response [A4-S2]
- `Demo`: Bad = feature dump + long monologues; Good = discovery-linked story + short interactive blocks [A4-S6]
- `Compliance`: Bad = blanket recording; Good = jurisdiction-aware consent and retention controls [A4-S7][A4-S8][A4-S9][A4-S10]

**Sources:**
- [A4-S1] Highspot, "State of Sales Enablement Report 2024": https://www.highspot.com/resource/state-of-sales-enablement-report-2024/
- [A4-S2] Salesforce, "Sales statistics," 2024: https://www.salesforce.com/in/blog/15-sales-statistics/
- [A4-S3] HubSpot, "State of Sales Report," updated 2025-08-29: https://blog.hubspot.com/sales/hubspot-sales-strategy-report
- [A4-S4] Gong Labs, "Talk-to-listen ratio," 2025: https://www.gong.io/resources/labs/talk-to-listen-conversion-ratio
- [A4-S5] Gong Labs (Evergreen), "Discovery calls," 2017: https://www.gong.io/resources/labs/nailing-your-sales-discovery-calls/
- [A4-S6] Gong Labs (Evergreen), "Sales demos," 2017: https://www.gong.io/resources/labs/sales-demos/
- [A4-S7] FCC, "FCC 24-17 Declaratory Ruling," 2024-02-08: https://docs.fcc.gov/public/attachments/FCC-24-17A1.pdf
- [A4-S8] CPPA, "Enforcement Advisory No. 2024-01," 2024-04-02: https://cppa.ca.gov/pdf/enfadvisory202401.pdf
- [A4-S9] EDPB, "Guidelines 1/2024 on Article 6(1)(f)," 2024-10: https://www.edpb.europa.eu/our-work-tools/documents/public-consultations/2024/guidelines-12024-processing-personal-data-based_en
- [A4-S10] Kilpatrick Townsend, "Wiretap Laws in the United States," 2024-07-29: https://ktslaw.com/Blog/globalprivacy%20and%20cybersecuritylaw/2024/7/wiretap%20laws%20in%20the%20united%20states

---

### Angle 5+: Regulatory & Governance Context for Conversation-Derived Playbooks
> Compliance constraints can invalidate otherwise strong playbook logic if evidence collection/use is non-compliant.

**Findings:**

1. AI/artificial voice treatment under TCPA received explicit FCC attention in 2024, which raises risk for scripted outreach and automated objection-handling contexts if consent assumptions are weak [A5-S1].

2. US wiretap/recording consent obligations are jurisdiction-sensitive (for example, all-party consent states), and cross-state calls increase policy complexity [A5-S2]. The skill should instruct conservative defaults and legal review triggers for uncertain jurisdictions.

3. UK/EU-style lawful basis and balancing tests are not optional formalities for call transcript reuse; they determine whether secondary analytical use is allowed [A5-S3]. For multinational teams, this means transcript usage policy must be codified as part of playbook generation.

4. Data minimization enforcement priorities (2024) show that over-collection and indefinite retention are active risk areas [A5-S4]. The playbook should include data retention and evidence minimization fields in the artifact schema.

5. Platform policy controls (for example, Teams recording retention/expiration) can enforce guardrails technically [A5-S5]. Methodology should treat these controls as requirements, not post-hoc recommendations.

**Sources:**
- [A5-S1] FCC, "FCC 24-17 Declaratory Ruling," 2024-02-08: https://docs.fcc.gov/public/attachments/FCC-24-17A1.pdf
- [A5-S2] Kilpatrick Townsend, "Wiretap Laws in the United States," 2024-07-29: https://ktslaw.com/Blog/globalprivacy%20and%20cybersecuritylaw/2024/7/wiretap%20laws%20in%20the%20united%20states
- [A5-S3] EDPB, "Guidelines 1/2024 on Article 6(1)(f)," 2024-10: https://www.edpb.europa.eu/our-work-tools/documents/public-consultations/2024/guidelines-12024-processing-personal-data-based_en
- [A5-S4] CPPA, "Enforcement Advisory No. 2024-01," 2024-04-02: https://cppa.ca.gov/pdf/enfadvisory202401.pdf
- [A5-S5] Microsoft Learn, "Manage Teams recording policies," updated 2025-05-13: https://learn.microsoft.com/en-us/microsoftteams/meeting-recording?tabs=meeting-policy

---

## Synthesis

Recent evidence supports the current skill’s core principle (evidence over hypotheticals), but the methodology needs sharper operating gates. The biggest update from 2024-2026 data is not a brand-new framework; it is stricter instrumentation of discovery quality, qualification evidence, and stage progression. Discovery and demo outcomes still track with conversational quality and narrative relevance, but rigid “one-number” metrics are risky without segment context [A1-S1][A3-S6].

Qualification frameworks (BANT/MEDDICC families) are still useful, but best teams run them as decision gates over multiple interactions rather than one-call scripts. This aligns with buyer behavior data showing later seller entry and larger buying groups, which increases the importance of stakeholder mapping and economic-buyer/champion proof early in cycle [A1-S4][A1-S9][A3-S1][A3-S3]. In practice, the playbook should explicitly prevent progression when mandatory evidence is missing.

A strong contradiction appears in metric interpretation: some sources imply actionable benchmark thresholds (talk ratio, stakeholder counts, slippage bands), while newer analyses warn that consistency and local baselines matter more than universal targets [A1-S1][A3-S6]. The right synthesis is to use benchmarks as guardrails and require local validation (conversation + pipeline confirmation) before changing scripts or gates.

Tooling is adequate for evidence loops, but data quality and governance are the practical bottlenecks. API/docs can provide transcript and stage-history access, but metric semantics, consent policy, retention windows, and lawful-basis constraints can invalidate downstream analysis if ignored [A2-S3][A2-S10][A2-S14][A5-S3]. The most important improvement to SKILL.md is therefore an explicit interpretation/compliance layer plus schema fields that force evidence provenance and change-control metadata.

---

## Recommendations for SKILL.md

- [x] Add an explicit **Evidence Standard & Update Cadence** section with minimum sample, freshness window, and dual-source validation (conversation + pipeline) before changing playbook rules.
- [x] Upgrade **Discovery Framework** with quality gates (interaction balance, targeted question quality, problem-depth capture) and explicit no-advance conditions.
- [x] Replace soft qualification language with **hard stage-exit decision gates** combining BANT and MEDDICC evidence, especially for higher-ACV deals.
- [x] Expand **Objection Handling** into a diagnosis-first protocol with required evidence citations and discount-control rules.
- [x] Expand **Demo Structure** into a discovery-mirrored narrative with monologue guardrails and mandatory mutual next-step commitments.
- [x] Add **Handoff + MAP requirements** so SDR/AE transition and next steps are measurable and rejectable when incomplete.
- [x] Add **Interpretation Quality** guidance (signal/noise rules, benchmark caveats, contradiction handling, and re-validation protocol).
- [x] Add a named **Anti-Patterns** block library with detection signals, consequences, and mitigations.
- [x] Extend artifact schema with `evidence_ledger`, `stage_exit_rules`, `interpretation_policy`, `handoff_protocol`, and `compliance_guardrails`.

---

## Draft Content for SKILL.md

### Draft: Evidence Standard & Operating Mode

You must build this playbook from observed evidence, never from hypothetical objection lists or generic sales templates. Before writing any rule (question, disqualifier, objection response, demo step), you should confirm that rule from at least one conversation-derived artifact and one pipeline outcome signal. If the conversation signal says a behavior is good but pipeline conversion does not improve (or worsens), treat the rule as unproven and keep it out of the default playbook.

Use this evidence standard:

1. **Minimum evidence volume:** collect a meaningful set of recent calls before changing baseline rules. If recent volume is low, label confidence as low and avoid hard thresholds.
2. **Freshness window:** default to recent evidence first; if recent coverage is insufficient, expand window and explicitly label the confidence tradeoff.
3. **Dual-source confirmation:** do not ship a behavior rule from call patterns alone. Confirm in opportunity progression or win/loss trend by segment.
4. **Segment discipline:** do not mix SMB, mid-market, and enterprise patterns into one rule unless evidence shows consistency across segments.
5. **Contradiction logging:** if credible sources disagree, document the disagreement and choose a local policy rule (for example: “band, not fixed value”) instead of pretending certainty.

Do not write “best practice” rules without evidence references. A valid rule in this skill should include `why this exists` plus `what evidence supports it` and `when it should not be used`.

### Draft: Discovery Call Framework (Evidence-Gated)

The discovery call has one job: determine whether this prospect should advance, based on evidence of need, fit, and next-step feasibility. You should run discovery as a structured diagnostic conversation, not an interview script and not a product pitch.

Use this sequence:

1. **Opener (2-3 min):** state why this call exists now, grounded in a known signal. Set expectation that the first goal is diagnosis, not a feature walkthrough.
2. **Problem exploration (12-18 min):** ask targeted questions tied to JTBD outcomes and downstream impact. You should prioritize depth over question count. If you are asking many questions but capturing shallow evidence, stop and reframe.
3. **Qualification evidence capture (5-8 min):** gather budget/authority/need/timeline evidence and stakeholder map. If a field is unknown, mark unknown explicitly; do not infer.
4. **Conditional mini-pitch (3-5 min):** only if qualification floor is met. Keep this to outcome framing and one relevant workflow; do not start full demo.
5. **Next-step commitment (3-5 min):** secure a specific owner/date/outcome commitment. “We will follow up” is not a valid next step.

Apply these discovery quality guardrails:

- Keep conversation interactive and buyer-centered. If the call trends toward rep-dominant monologue, pause and return to diagnosis.
- Optimize for high-quality targeted questions, not maximum volume.
- Capture at least multiple concrete problem statements with downstream business impact before advancing.
- Log evidence quotes and source references for each major qualification claim.

No-advance conditions from discovery:

- You cannot articulate the prospect’s current-state workflow and failure modes.
- Need evidence is generic (“they want efficiency”) with no concrete business impact.
- Stakeholder landscape is unknown for multi-stakeholder deals.
- No mutually agreed next step with owner/date/outcome.

### Draft: Qualification Decision Gates (BANT + MEDDICC Logic)

You should use BANT as a living evidence thread and MEDDICC elements as hard gates for complex opportunities. Treat qualification as a set of stage-exit criteria, not a checklist completed in one meeting.

**BANT evidence rules:**

- **Budget:** record concrete budget signal (allocated, range, procurement path, or validated spend authority). If budget is unknown, keep stage at risk and define a discovery action to resolve.
- **Authority:** identify real decision roles, not just active participants. Document who can approve, who can block, and who influences.
- **Need:** map need to specific JTBD pain and measurable consequence.
- **Timeline:** capture decision timing and trigger event; treat open-ended timelines as risk.

**MEDDICC gate rules for higher-complexity opportunities:**

- Require identified economic buyer before proposal/commit stage.
- Require validated champion (influence + motivation + organizational access), not “friendly contact.”
- Require explicit decision criteria and proof plan aligned to buyer process.

Decision rule:

- If any mandatory gate is missing, do not advance stage. Instead, write a qualification recovery plan with owner/date and exact data needed.
- If qualification evidence is contradictory (for example, strong champion but unknown buying authority), mark confidence reduced and avoid forecast optimism.

Do not mark deals “qualified” because fields are syntactically filled. Qualification is valid only when evidence quality is high enough that another seller could audit and reach the same conclusion.

### Draft: Objection Handling Protocol (Evidence-Cited, Diagnosis-First)

You must build objection scripts from real objection instances observed in conversation artifacts. For each objection class, include: trigger phrase pattern, diagnosis questions, response options, proof asset, and pivot step.

Use this sequence every time:

1. **Pause:** do not immediately rebut.
2. **Clarify objection type:** isolate whether this is budget, timing, fit, risk, incumbent preference, or internal priority conflict.
3. **Confirm consequence:** ask what happens if this concern is not resolved.
4. **Respond with evidence:** use concise response tied to relevant proof.
5. **Pivot to decision movement:** ask for a concrete next action tied to this resolved concern.

Script quality rules:

- Every script must include `evidence_source` from real artifacts.
- Every script must define `use_when` and `do_not_use_when` conditions.
- If the objection is price-related, do not default to discounting. Re-anchor on value and decision criteria first.
- Retire scripts that repeatedly fail to move next-step commitment.

Bad pattern to avoid:

- Rebuttal monologue that ignores the buyer’s specific concern category.

Good pattern to enforce:

- Diagnostic questioning + short evidence-backed response + explicit next-step proposal.

### Draft: Demo Structure (Discovery-Mirrored Story, Not Feature Tour)

You should structure demos as a narrative that mirrors discovery priorities. Start with the most painful confirmed problem, show one complete workflow that resolves it, and end with quantified after-state plus next-step commitment.

Recommended flow:

1. **Scene set:** restate the agreed problem and decision criteria.
2. **Before state:** show current process friction in concrete terms.
3. **Core workflow:** demonstrate one end-to-end path that resolves priority pain.
4. **Proof point:** highlight one “aha” moment tied to the buyer’s stated outcome.
5. **After state:** summarize expected business effect and implementation reality.
6. **Mutual next step:** define owner/date/success criterion.

Delivery guardrails:

- Avoid long uninterrupted pitching; design deliberate interaction checkpoints.
- Do not “save best for last” if discovery already identified highest-priority pain.
- Do not add unrelated feature branches unless requested.
- If a critical stakeholder is absent, avoid commitment-heavy close behavior and schedule stakeholder-complete follow-up.

No-advance conditions from demo:

- Demo order does not map to discovery priorities.
- No explicit outcome linkage from shown workflow to buyer criteria.
- No buyer-side owner/date commitment at close.

### Draft: Handoff Protocol and Mutual Action Plan (MAP)

You must treat SDR-to-AE (or initial-to-advanced seller) handoff as a qualification gate, not an administrative transfer. A handoff is valid only if required evidence is complete and auditable.

Required handoff payload:

- Prospect context and trigger event
- Confirmed pain statements and business impact
- Stakeholder map (decision, influence, blockers)
- Qualification status with known unknowns
- Objections encountered + response outcomes
- Proposed next meeting objective
- Draft mutual action plan entries (owner/date/outcome)

Handoff rejection rules:

- Reject if required fields are missing.
- Reject if “qualified” status exists without supporting evidence references.
- Reject if next-step commitment is vague or buyer-agnostic.

MAP instruction:

You should create and maintain a mutual action plan for opportunities beyond initial qualification. MAP entries must include both seller and buyer owners, due dates, dependency notes, and success criteria. A calendar invite without explicit expected outcome does not count as MAP progress.

### Draft: Interpretation Quality and Playbook Update Cadence

You should update this playbook on a fixed cadence and only after passing interpretation checks. Do not update scripts after isolated anecdotal wins/losses.

Update protocol:

1. **Collect:** aggregate recent calls, objections, stage movement, and closed outcomes by segment.
2. **Score signal quality:** verify sample adequacy, freshness, and data completeness.
3. **Compare cohorts:** evaluate winners vs losers across conversation behavior and qualification completeness.
4. **Test candidate change:** apply one change at a time where possible; monitor stage conversion and next-step quality.
5. **Promote or rollback:** keep changes that improve outcomes and maintain compliance; retire those that do not.

Signal/noise rules:

- Treat stakeholder breadth and stage velocity as stronger leading signals than isolated talk-ratio values.
- Use talk ratio as a contextual band plus consistency check, not a universal target.
- Require both conversation evidence and pipeline outcome support before making a hard playbook change.
- If source benchmarks conflict, prefer local segment baselines and annotate uncertainty.

Quality gate for any playbook edit:

- Evidence references attached
- Contradictions logged
- Compliance impact reviewed
- Confidence level labeled

### Draft: Anti-Pattern Warning Blocks

#### Warning: Discovery Pitch-First Drift

- **What it looks like:** You start product explanation before diagnosing pain and workflow.
- **Detection signal:** Rep-dominant call behavior and shallow pain evidence capture.
- **Consequence if missed:** You progress deals with weak problem clarity and low relevance.
- **Mitigation:** Pause demo behavior, run diagnostic question sequence, re-establish pain map before solution discussion.

#### Warning: Qualification Checkbox Illusion

- **What it looks like:** BANT/MEDDICC fields are present but unsupported by evidence.
- **Detection signal:** Late-stage losses citing fit/value mismatch despite “qualified” status.
- **Consequence if missed:** Forecast inflation and wasted late-stage resources.
- **Mitigation:** Enforce evidence-cited fields and stage rejection on missing gate criteria.

#### Warning: Objection Rebuttal Without Diagnosis

- **What it looks like:** You deliver canned responses immediately.
- **Detection signal:** High objection recurrence and low next-step conversion after objections.
- **Consequence if missed:** Trust erosion and discount pressure.
- **Mitigation:** Force pause/clarify/respond/pivot sequence and script use-conditions.

#### Warning: Feature Tour Demo

- **What it looks like:** Demo covers many features but not the buyer’s priority pains.
- **Detection signal:** Demo order diverges from discovery ranking; weak buyer interaction.
- **Consequence if missed:** Low perceived fit and weak buying momentum.
- **Mitigation:** Rebuild demo around one core workflow tied to top-priority outcome.

#### Warning: Compliance-Oblivious Evidence Capture

- **What it looks like:** Call recording/transcription runs without auditable consent and retention boundaries.
- **Detection signal:** Missing consent artifacts, undefined jurisdiction policy, indefinite data retention.
- **Consequence if missed:** Regulatory and legal exposure; evidence may become unusable.
- **Mitigation:** Apply jurisdiction-aware consent defaults, retention rules, and lawful-basis documentation.

### Draft: Available Tools (Operational Usage Guidance)

Use the following tools to ground the playbook in active policy and discovery artifacts.

```python
flexus_policy_document(op="activate", args={"p": "/strategy/messaging"})
```

Call this before drafting discovery and objection language so positioning and value claims align with approved messaging.

```python
flexus_policy_document(op="activate", args={"p": "/discovery/{study_id}/jtbd-outcomes"})
```

Call this before writing qualification need evidence and demo flow. You should map discovery questions and demo storyline to documented JTBD outcomes.

```python
flexus_policy_document(op="list", args={"p": "/pipeline/"})
```

Call this to inspect available pipeline artifacts and choose which stage/outcome evidence can validate playbook changes. Do not infer unavailable pipeline fields.

```python
write_artifact(
  artifact_type="sales_playbook",
  path="/strategy/rtm-sales-playbook",
  data={...},
)
```

Write only after all mandatory evidence and stage gate fields are complete. If required fields are missing, do not write partial “final” output.

### Draft: Schema additions

```json
{
  "sales_playbook": {
    "type": "object",
    "required": [
      "created_at",
      "target_segment",
      "qualification_criteria",
      "discovery_framework",
      "objection_scripts",
      "demo_structure",
      "stage_exit_rules",
      "evidence_ledger",
      "interpretation_policy",
      "handoff_protocol",
      "compliance_guardrails"
    ],
    "additionalProperties": false,
    "properties": {
      "created_at": {
        "type": "string",
        "format": "date-time",
        "description": "ISO-8601 timestamp when this playbook artifact was generated."
      },
      "target_segment": {
        "type": "string",
        "description": "Segment this playbook applies to (for example: SMB, mid-market, enterprise, or named ICP slice)."
      },
      "qualification_criteria": {
        "type": "object",
        "required": [
          "budget_signal",
          "authority_roles",
          "need_evidence",
          "timeline_max_days",
          "disqualifiers",
          "economic_buyer_required",
          "champion_required"
        ],
        "additionalProperties": false,
        "properties": {
          "budget_signal": {
            "type": "string",
            "description": "Concrete budget evidence format, such as allocated range, approved budget line, or procurement path."
          },
          "authority_roles": {
            "type": "array",
            "description": "Decision and influence roles that satisfy authority criteria for this segment.",
            "items": {
              "type": "string"
            }
          },
          "need_evidence": {
            "type": "array",
            "description": "Observed JTBD pain statements and impacts that must be present to qualify.",
            "items": {
              "type": "string"
            }
          },
          "timeline_max_days": {
            "type": "integer",
            "minimum": 0,
            "description": "Maximum acceptable decision window in days before opportunity is considered low-priority or nurture."
          },
          "disqualifiers": {
            "type": "array",
            "description": "Hard no-go conditions that block progression.",
            "items": {
              "type": "string"
            }
          },
          "economic_buyer_required": {
            "type": "boolean",
            "description": "Whether economic buyer identification is mandatory before proposal/commit stages."
          },
          "champion_required": {
            "type": "boolean",
            "description": "Whether a validated internal champion is required for advancement."
          }
        }
      },
      "discovery_framework": {
        "type": "array",
        "description": "Ordered discovery phases with operational goals, prompts, and exit evidence.",
        "items": {
          "type": "object",
          "required": [
            "phase",
            "duration_min",
            "goal",
            "questions",
            "exit_evidence"
          ],
          "additionalProperties": false,
          "properties": {
            "phase": {
              "type": "string",
              "description": "Discovery phase name."
            },
            "duration_min": {
              "type": "integer",
              "minimum": 0,
              "description": "Recommended duration for this phase in minutes."
            },
            "goal": {
              "type": "string",
              "description": "Operational purpose of this phase."
            },
            "questions": {
              "type": "array",
              "description": "Question prompts used in this phase.",
              "items": {
                "type": "string"
              }
            },
            "exit_evidence": {
              "type": "array",
              "description": "Evidence that must be captured before leaving the phase.",
              "items": {
                "type": "string"
              }
            }
          }
        }
      },
      "objection_scripts": {
        "type": "array",
        "description": "Evidence-backed objection handling modules.",
        "items": {
          "type": "object",
          "required": [
            "objection_type",
            "trigger_phrase",
            "response",
            "pivot",
            "evidence_source",
            "use_when",
            "do_not_use_when",
            "last_verified_at"
          ],
          "additionalProperties": false,
          "properties": {
            "objection_type": {
              "type": "string",
              "description": "Normalized objection class (for example budget, timing, incumbent, risk)."
            },
            "trigger_phrase": {
              "type": "string",
              "description": "Representative objection statement from calls."
            },
            "response": {
              "type": "string",
              "description": "Primary evidence-backed response text."
            },
            "pivot": {
              "type": "string",
              "description": "Next-step question or action that advances decision process."
            },
            "evidence_source": {
              "type": "string",
              "description": "Reference to conversation artifact(s) supporting this script."
            },
            "use_when": {
              "type": "array",
              "description": "Conditions where this script is recommended.",
              "items": {
                "type": "string"
              }
            },
            "do_not_use_when": {
              "type": "array",
              "description": "Conditions where this script should be avoided.",
              "items": {
                "type": "string"
              }
            },
            "last_verified_at": {
              "type": "string",
              "format": "date-time",
              "description": "Timestamp of latest validation against recent outcomes."
            }
          }
        }
      },
      "demo_structure": {
        "type": "array",
        "description": "Ordered demo scenes linked to discovery evidence and expected buyer outcome.",
        "items": {
          "type": "object",
          "required": [
            "scene",
            "duration_min",
            "key_message",
            "wow_moment",
            "proof_asset",
            "linked_discovery_evidence"
          ],
          "additionalProperties": false,
          "properties": {
            "scene": {
              "type": "string",
              "description": "Scene identifier (before-state, core workflow, after-state, etc.)."
            },
            "duration_min": {
              "type": "integer",
              "minimum": 0,
              "description": "Target scene duration in minutes."
            },
            "key_message": {
              "type": "string",
              "description": "Primary message to communicate in this scene."
            },
            "wow_moment": {
              "type": "boolean",
              "description": "Whether this scene is the intended high-impact moment."
            },
            "proof_asset": {
              "type": "string",
              "description": "Evidence or artifact used to substantiate this scene."
            },
            "linked_discovery_evidence": {
              "type": "array",
              "description": "Discovery evidence references that justify showing this scene.",
              "items": {
                "type": "string"
              }
            }
          }
        }
      },
      "stage_exit_rules": {
        "type": "object",
        "required": [
          "discovery_exit",
          "qualification_exit",
          "demo_exit",
          "no_advance_if_missing"
        ],
        "additionalProperties": false,
        "properties": {
          "discovery_exit": {
            "type": "array",
            "description": "Conditions that must be true to leave discovery stage.",
            "items": {
              "type": "string"
            }
          },
          "qualification_exit": {
            "type": "array",
            "description": "Conditions that must be true to leave qualification stage.",
            "items": {
              "type": "string"
            }
          },
          "demo_exit": {
            "type": "array",
            "description": "Conditions that must be true to leave demo stage.",
            "items": {
              "type": "string"
            }
          },
          "no_advance_if_missing": {
            "type": "array",
            "description": "Global hard blockers that prevent stage progression when unresolved.",
            "items": {
              "type": "string"
            }
          }
        }
      },
      "evidence_ledger": {
        "type": "array",
        "description": "Auditable list of evidence snippets used to justify playbook rules.",
        "items": {
          "type": "object",
          "required": [
            "evidence_id",
            "source_type",
            "source_ref",
            "call_date",
            "segment",
            "deal_outcome",
            "quote",
            "supports"
          ],
          "additionalProperties": false,
          "properties": {
            "evidence_id": {
              "type": "string",
              "description": "Unique identifier for this evidence entry."
            },
            "source_type": {
              "type": "string",
              "enum": [
                "call_transcript",
                "call_summary",
                "crm_opportunity",
                "win_loss_note",
                "other"
              ],
              "description": "Source category for the evidence entry."
            },
            "source_ref": {
              "type": "string",
              "description": "Pointer to the underlying artifact path or external identifier."
            },
            "call_date": {
              "type": "string",
              "format": "date",
              "description": "Date of the related call or event."
            },
            "segment": {
              "type": "string",
              "description": "Segment label for this evidence (must align with target segmentation rules)."
            },
            "deal_outcome": {
              "type": "string",
              "enum": [
                "won",
                "lost",
                "open",
                "unknown"
              ],
              "description": "Observed opportunity outcome at time of extraction."
            },
            "quote": {
              "type": "string",
              "description": "Verbatim or near-verbatim snippet that supports a playbook element."
            },
            "supports": {
              "type": "array",
              "description": "Playbook areas this evidence supports.",
              "items": {
                "type": "string",
                "enum": [
                  "discovery",
                  "qualification",
                  "objections",
                  "demo",
                  "handoff"
                ]
              }
            }
          }
        }
      },
      "interpretation_policy": {
        "type": "object",
        "required": [
          "review_cadence_days",
          "min_calls_for_change",
          "freshness_window_days",
          "require_dual_source_validation",
          "contradiction_resolution_rule"
        ],
        "additionalProperties": false,
        "properties": {
          "review_cadence_days": {
            "type": "integer",
            "minimum": 1,
            "description": "How often this playbook must be reviewed and potentially updated."
          },
          "min_calls_for_change": {
            "type": "integer",
            "minimum": 1,
            "description": "Minimum number of relevant calls required before approving a new rule."
          },
          "freshness_window_days": {
            "type": "integer",
            "minimum": 1,
            "description": "Preferred evidence freshness window for change decisions."
          },
          "require_dual_source_validation": {
            "type": "boolean",
            "description": "Whether playbook changes require both conversation and pipeline confirmation."
          },
          "contradiction_resolution_rule": {
            "type": "string",
            "description": "How to decide when sources disagree (for example: segment baseline overrides global benchmark)."
          }
        }
      },
      "handoff_protocol": {
        "type": "object",
        "required": [
          "mandatory_fields",
          "reject_if_missing",
          "map_required"
        ],
        "additionalProperties": false,
        "properties": {
          "mandatory_fields": {
            "type": "array",
            "description": "Fields that must be present for SDR-to-AE or stage handoff acceptance.",
            "items": {
              "type": "string"
            }
          },
          "reject_if_missing": {
            "type": "array",
            "description": "Blocking conditions that force handoff rejection.",
            "items": {
              "type": "string"
            }
          },
          "map_required": {
            "type": "boolean",
            "description": "Whether a mutual action plan is mandatory at handoff."
          }
        }
      },
      "compliance_guardrails": {
        "type": "object",
        "required": [
          "recording_consent_policy",
          "retention_window_days",
          "lawful_basis_note",
          "jurisdiction_handling_rule"
        ],
        "additionalProperties": false,
        "properties": {
          "recording_consent_policy": {
            "type": "string",
            "description": "Operational policy for obtaining and storing consent for call recording/transcription."
          },
          "retention_window_days": {
            "type": "integer",
            "minimum": 1,
            "description": "Maximum retention period for call-derived evidence before review/deletion."
          },
          "lawful_basis_note": {
            "type": "string",
            "description": "Documented lawful basis or legal rationale for processing conversation data."
          },
          "jurisdiction_handling_rule": {
            "type": "string",
            "description": "How to apply stricter consent/processing standards across mixed jurisdictions."
          }
        }
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Public sources provide uneven transparency on pricing, hard API rate limits, and plan-level feature access for major revenue tools; these should be validated in tenant-specific docs before operational commitments.
- Some highly cited behavior benchmarks (especially conversation micro-patterns) still rely on Evergreen analyses; they are directionally useful but should be validated against current team data before hard-coding numeric thresholds.
- Several benchmark claims come from vendor-led research and may include methodology bias; this is why local validation gates are recommended before playbook changes.
- Jurisdiction-specific compliance requirements (US state-by-state, EU member-state overlays, non-UK/EU geographies) were not exhaustively mapped in this pass and may require legal review for deployment beyond a single region.
- Not all “AI impact” claims isolate causal effects; correlations should not be interpreted as guaranteed uplift without controlled implementation and data-quality checks.
