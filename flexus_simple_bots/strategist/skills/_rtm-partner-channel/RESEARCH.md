# Research: rtm-partner-channel

**Skill path:** `strategist/skills/rtm-partner-channel/`
**Bot:** strategist (researcher | strategist | executor)
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`rtm-partner-channel` defines how to design and prioritize partner-led route-to-market motions (technology/integration partners, reseller/VAR, referral/affiliate, OEM/white-label), including incentive design, partner ICP, and target account prioritization.

The core problem this skill solves is execution realism. Most partner strategies fail because they stay at taxonomy level ("we will do reseller + referral") and do not specify partner economics, onboarding gates, channel-conflict rules, and measurement quality. 2024-2026 evidence shows partner programs are expanding, but many teams still operate with immature tooling and unclear incentive design, creating a gap between ambition and outcomes. This research upgrades the skill toward source-backed, operator-grade channel strategy outputs.

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

- [x] No generic filler ("it is important to...", "best practices suggest...") without concrete backing
- [x] No invented tool names, method IDs, or API endpoints - only verified real ones
- [x] Contradictions between sources are explicitly noted, not silently resolved
- [x] Volume: findings section is 800-4000 words (synthesized, not source dump)

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

1) **Use dual-horizon channel targets instead of one headline percentage.**  
Macro analyst framing still projects partner-dominant tech spend (often cited as ~70% through channel), but operator surveys show many teams in 2025 planning materially lower near-term channel contribution bands (most often 11-25% or 26-50%). The practical implication is to split planning into a 12-month realistic target and a 24-36 month expansion target rather than forcing one blended number. This reduces strategy theater and makes execution sequencing testable. Sources: [M13], [M3].

2) **Classify partners by activity mix (sell/service/build), not partner label alone.**  
IDC 2024 trend data indicates many partners run mixed models and multi-path monetization (direct customer billing plus ecosystem routes). A strategy that treats "VAR" or "SI" as fixed behavior classes will misprice incentives and assign wrong enablement. Better approach: score each target partner on `sell`, `service`, and `build` contribution and map go-to-market plays accordingly. Sources: [M1].

3) **Incentive design is shifting from activity payout to lifecycle outcomes.**  
TSIA and related channel research emphasize that XaaS partner value is now distributed across land/adopt/expand/renew motions, and sales-volume-only structures underperform in recurring models. Practical strategy upgrade: tie incentive design and enablement funding to lifecycle role and customer outcomes, not just closed-won initiation. Sources: [M2], [M11].

4) **Do not treat MDF as universally obsolete or universally sufficient.**  
There is a real contradiction in 2025 sources: one dataset says partners now prefer outcome/capability-based funding over MDF; another shows large portions of partner marketing budgets still funded by MDF/distributor programs; major hyperscalers continue MDF offerings in upper tiers. The skill should encode this contradiction directly: segment incentive portfolios by partner archetype instead of hard "MDF yes/no" rules. Sources: [M11], [M12], [M7].

5) **Recruitment and onboarding should be stage-gated with short activation clocks.**  
Partner activation benchmarks indicate many partnerships reach first activity quickly (median around days, majority within 10 days in one large network dataset). Practical implication: strategy artifacts should include Day 0-10 activation requirement, Day 30-90 proof milestones, and explicit promotion/deprioritization rules. Slow activation without evidence should be interpreted as risk, not "normal ramp." Sources: [M6], [M3].

6) **Program eligibility gates from hyperscalers are concrete and should inform readiness criteria.**  
Microsoft partner scoring and AWS tier requirements are explicit and measurable (certifications, opportunity counts, score thresholds). Even when your own channel is not hyperscaler-led, these programs provide an evidence-based pattern: define minimum capability gates before assigning high-priority partner status. Sources: [M8], [M7].

7) **Marketplace route planning is now a first-class channel design decision.**  
Google Cloud program updates and marketplace growth projections indicate channel planners must decide early when to route through marketplace transacting motions vs direct contracts. Marketplace facilitation is increasingly partner-mediated, so "marketplace path" should appear in partner type and target account planning, not as a later ops afterthought. Sources: [M9], [M10].

8) **Capacity realism must be explicit in strategy outputs.**  
Recent surveys show many partner teams are small, under-budgeted, and not fully integrated in tooling despite high growth expectations. Strategy quality improves when artifact includes explicit operating capacity assumptions (portfolio caps per partner manager, onboarding SLA gates, and freeze conditions for new partner intake). Sources: [M3], [M2].

**Sources:**
- [M1] https://www.idc.com/resource-center/blog/3-trends-that-will-shape-partnering-ecosystems-in-2024-25/ (2024; analyst source with survey-backed directional data)
- [M2] https://www.tsia.com/blog/state-of-xaas-channel-partnerships-2025 (updated 2025-04-08; industry association)
- [M3] https://cdn.prod.website-files.com/65ba9e265a8d0623ea182de2/68b1f2b9a429822a4f41767f_The%20State%20of%20Partnerships%202025%20-%20Results.pdf (2025; transparent sample, non-representative)
- [M6] https://partnerstack.com/resources/research-lab/charts/most-network-partners-have-a-median-time-of-2-days-to-joining-their-first-partnership (2024; vendor network telemetry)
- [M7] https://aws.amazon.com/partners/services-tiers/ (accessed 2026-03-05; first-party program requirements/benefits)
- [M8] https://learn.microsoft.com/en-us/partner-center/membership/partner-capability-score (updated 2026-01-26; first-party qualification model)
- [M9] https://cloud.google.com/blog/topics/partners/introducing-google-cloud-partner-network (2025-12-16; first-party program update)
- [M10] https://www.businesswire.com/news/home/20251006925215/en/Omdia-Hyperscaler-Cloud-Marketplace-Sales-to-Hit-%24163-Billion-by-2030 (2025-10-06; press release citing Omdia forecast)
- [M11] https://techaisle.com/blog/643-techaisle-research-why-4115-partners-say-mdf-is-obsolete-and-what-they-want-instead (2025-10-02; analyst blog with survey claims)
- [M12] https://www.thechannelco.com/article/state-of-partner-marketing-2025 (2025; industry media survey)
- [M13] https://channelpostmea.com/2024/11/29/canalys-it-spending-to-expand-8-in-2025-with-increased-role-for-channel-partners/ (2024-11-29; secondary reporting of analyst forecast)

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

1) **PRM platforms now compete on operability details, not just portal features.**  
Salesforce PRM publishes seat pricing and explicit API call allowances by tier, while PartnerStack emphasizes end-to-end partner motion workflows with public API and webhook docs but custom pricing. For SKILL design this means tool recommendations must include known limits/disclosures and explicitly flag pricing unknowns. Sources: [T1], [T2], [T3], [T4].

2) **Cloud marketplaces have explicit fee mechanics that materially affect partner economics.**  
AWS, Google, and Microsoft now publish concrete marketplace fee structures and private-offer mechanics. Partner-channel strategy outputs should therefore include a marketplace-route decision with fee assumptions documented; otherwise margin assumptions are frequently wrong. Sources: [T6], [T7], [T14], [T10].

3) **Co-sell programs are gated with measurable readiness requirements.**  
AWS ISV Accelerate, Microsoft co-sell, and Google reseller frameworks all require operational prerequisites (offer status, collateral, eligibility checks, capability thresholds). Treating co-sell as "join and start selling" is inaccurate; strategy outputs should include readiness status and missing prerequisites for each prioritized partner candidate. Sources: [T8], [T9], [T12], [T13].

4) **Ecosystem-overlap intelligence is now integration-native.**  
Crossbeam and similar ecosystem data platforms ingest CRM/warehouse data and push overlap signals back into CRM workflows. This supports a concrete workflow in skill outputs: overlap evidence should be data-derived and attachable to prioritized target rows, not narrative-only. Sources: [T15], [T16].

5) **Firmographic enrichment APIs remain useful but price transparency can be limited.**  
Crunchbase API package documentation is clear on capability families (fundamentals, insights, predictions), while public self-serve pricing is less clear than feature packaging. Skill instructions should explicitly separate "available data fields" from "commercial access assumptions." Sources: [T17], [T18].

6) **Attribution tooling is maturing toward sourced + influenced support.**  
PartnerStack integrations/webhooks, Crossbeam attribution connectors, and impact.com tracking tiers all indicate practitioner movement toward dual attribution pipelines. Strategy artifacts should carry attribution model metadata (first/last/multi-touch) and confidence labels rather than reporting one unqualified revenue number. Sources: [T4], [T15], [T19].

7) **App and marketplace governance standards are tightening.**  
HubSpot app listing and certification requirements are examples of stricter ecosystem quality controls (OAuth requirements, install thresholds, recertification standards). Channel strategy should include integration-governance readiness checks when selecting technology partners. Sources: [T20], [T21].

8) **De-facto technical pattern in 2025-2026: CRM-centered data contract with partner event ingestion.**  
Across PRM ecosystems, the common architecture is CRM as source of truth + API/webhook events from partner systems + explicit object-level status model for sourced vs influenced pipeline and partner stage progression. This pattern should be reflected directly in schema recommendations, even when the skill itself only has limited native tools. Sources: [T3], [T4], [T11], [T15].

**Sources:**
- [T1] https://www.salesforce.com/sales/partner-relationship-management/pricing/?bc=HA (accessed 2026-03-05; first-party pricing/limits)
- [T2] https://partnerstack.com/pricing (accessed 2026-03-05; first-party, custom pricing disclosure)
- [T3] https://docs.partnerstack.com/docs/partnerstack-api (accessed 2026-03-05; first-party API docs)
- [T4] https://docs.partnerstack.com/docs/partnerstack-webhooks (accessed 2026-03-05; first-party webhook docs)
- [T5] https://docs.partnerstack.com/docs/getting-started-with-the-integration-suite (accessed 2026-03-05)
- [T6] https://docs.aws.amazon.com/marketplace/latest/userguide/listing-fees.html (effective 2024-01-05; still active, evergreen fee reference)
- [T7] https://aws.amazon.com/about-aws/whats-new/2024/01/aws-marketplace-simplified-reduced-listing-fees/ (2024-01-05)
- [T8] https://aws.amazon.com/partners/programs/isv-accelerate/ (accessed 2026-03-05)
- [T9] https://learn.microsoft.com/en-us/partner-center/referrals/co-sell-requirements (updated 2025-09-25)
- [T10] https://learn.microsoft.com/en-us/partner-center/marketplace-offers/marketplace-commercial-transaction-capabilities-and-considerations (updated 2025-09-25)
- [T11] https://learn.microsoft.com/en-us/partner-center/marketplace-offers/transacting-commercial-marketplace (updated 2026-01-27)
- [T12] https://docs.cloud.google.com/marketplace/docs/partners/get-started (accessed 2026-03-05)
- [T13] https://docs.cloud.google.com/marketplace/docs/partners/resellers/resell (accessed 2026-03-05)
- [T14] https://cloud.google.com/terms/marketplace-revenue-share-schedule (effective 2025-04-21; updated 2025-03-10)
- [T15] https://www.crossbeam.com/how-it-works/integrations/ (accessed 2026-03-05)
- [T16] https://www.crossbeam.com/pricing/ (accessed 2026-03-05)
- [T17] https://data.crunchbase.com/docs/api-packages-overview (accessed 2026-03-05)
- [T18] https://about.crunchbase.com/products/data-enrichment/ (accessed 2026-03-05)
- [T19] https://impact.com/integrated-platform-prices/ (accessed 2026-03-05)
- [T20] https://developers.hubspot.com/docs/api/app-marketplace-listing-requirements (accessed 2026-03-05)
- [T21] https://developers.hubspot.com/docs/apps/developer-platform/list-apps/apply-for-certification/certification-requirements (accessed 2026-03-05)

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

1) **Sourced and influenced pipeline must be interpreted together.**  
Partner attribution guidance and analyst commentary show that sourced-only measurement systematically underestimates partner impact in co-sell and integration-heavy motions. Skill outputs should therefore require both measures with explicit denominators and attribution model declaration. Sources: [I1], [I8].

2) **Attribution method determines confidence class.**  
Reported usage patterns still show many teams on first-touch/last-touch frameworks while multi-touch adoption is incomplete. Decision implication: if model is not multi-touch or mixed with defined rules, influenced metrics should be tagged as directional rather than decision-grade. Sources: [I3], [I4].

3) **Partner ecosystem maturity segmentation changes interpretation materially.**  
Crossbeam telemetry indicates average partner-involved win-rate lift can hide strong subgroup variance (including weak/negative cohorts in transition maturity bands). Strategy artifacts should include segmentation by connected-partner maturity, not only blended topline lift. Source: [I5].

4) **Leading indicators (adoption, workflow usage, alignment) must gate lagging revenue expectations.**  
Future of Revenue 2025 shows strong relationship between alignment and outcomes (target attainment likelihood, cycle time, loss rates), and partner research shows alignment-linked cycle compression. Practical rule: if enablement/adoption/alignment indicators are weak, down-rank forecast confidence even when early revenue signals appear positive. Sources: [I6], [I11].

5) **Healthy benchmark ranges are context-dependent and maturity-constrained.**  
2025 partnership survey bands and tooling maturity statistics suggest high channel-share forecasts without stack/process maturity should be flagged high risk. Skill outputs should present `base`, `stretch`, and `speculative` scenarios with confidence labels instead of one deterministic target. Source: [I7].

6) **Common misinterpretation: bookings-first scorecards are enough in XaaS.**  
TSIA framing indicates recurring-revenue partner models require adoption/retention success contribution and customer success collaboration metrics, not only initial bookings. Strategy schema should include at least one post-sale partner contribution metric class. Sources: [I9], [I10].

7) **Contradiction to keep explicit: available benchmark numbers are useful but not universal.**  
Many public benchmarks come from vendor-owned datasets or targeted samples. They are still actionable for default priors, but outputs should explicitly label evidence quality and transferability assumptions. Sources: [I1], [I5], [I7].

**Sources:**
- [I1] https://partnerstack.com/articles/partner-attribution-measure-sourced-vs-influenced-revenue (updated 2026-01-16; vendor guidance with definitions)
- [I3] https://partnerstack.com/resources/research-lab/charts/multi-touch-is-the-most-common-partner-tribution-method-for-senior-leaders-in-b2b-saas (2025; vendor survey chart)
- [I4] https://partnerstack.com/resources/research-lab/the-state-of-partnerships-in-gtm-2026 (2025 release for 2026 planning context)
- [I5] https://insider.crossbeam.com/entry/new-data-involving-partners-in-deals-increases-win-rate-for-nearly-every-ecosystem-size-and-type (2024-11-08; vendor telemetry with segmentation)
- [I6] https://www.joinpavilion.com/hubfs/Crossbeam-Pavilion-Future-of-Revenue-2025.pdf?hsLang=en (2025; survey report with methodology notes)
- [I7] https://cdn.prod.website-files.com/65ba9e265a8d0623ea182de2/68b1f2b9a429822a4f41767f_The%20State%20of%20Partnerships%202025%20-%20Results.pdf (2025; sample limitations explicitly stated)
- [I8] https://www.forrester.com/blogs/partner-attribution-is-broken-heres-why-b2b-executives-must-lead-the-fix/ (2025; analyst viewpoint)
- [I9] https://www.tsia.com/blog/the-state-of-xaas-channel-partnerships-2024 (updated 2024-04-16)
- [I10] https://www.tsia.com/blog/channel-partner-success-score (updated 2025-06-23)
- [I11] https://partnerstack.com/resources/research-lab/charts/partnerships-lead-to-higher-average-contracts-through-larger-initial-deals-upsells-and-renewels (2025; directional partner impact data)

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

1) **Anti-pattern: optimize payouts without validating partner unit economics.**  
What it looks like: strategy outputs define commission percentages but omit partner workload cost, services attach assumptions, and post-sale responsibilities. Consequence: activity spikes but weak renewals/adoption and partner churn. Detection signal: high recruited count + low active-revenue partners. Mitigation: require per-partner-archetype economics table and lifecycle incentive map. Sources: [F7], [F9], [F14].

2) **Anti-pattern: abrupt account ownership shifts create channel conflict shock.**  
Broadcom/VMware public reports in 2024 show ecosystem disruption when account/control rules changed abruptly with weak transition clarity. Detection signal: partner confusion over deal registration eligibility and account ownership. Mitigation: encode segmentation criteria, transition period, and protection logic directly in strategy artifact before policy rollout. Sources: [F1], [F2], [F4].

3) **Anti-pattern: deal registration policy exists on paper but fails operationally.**  
Microsoft program docs show concrete timing and eligibility constraints; failure to operationalize those details turns deal reg into rejection churn rather than conflict prevention. Detection signal: high rejection/escalation volume due to process or data quality. Mitigation: include pre-submit validation and exception path SLA in operating model. Sources: [F5], [F6].

4) **Anti-pattern: training-heavy onboarding without field execution path.**  
Recent channel preference data shows increased demand for co-sell and execution support. Training alone without first-opportunity milestones creates "certified but inactive" partners. Mitigation: bind onboarding to first joint opportunity deadlines and stage exit criteria. Sources: [F7], [F9].

5) **Anti-pattern: third-party compliance treated as one-time onboarding checkbox.**  
SEC enforcement and DOJ guidance emphasize continuous controls for intermediaries. Strategy outputs lacking ongoing due diligence and compensation reasonableness checks increase regulatory risk. Mitigation: include lifecycle compliance controls in partner operating model. Sources: [F10], [F11].

6) **Anti-pattern: margin-protection behavior crosses competition-law boundaries.**  
2024 competition enforcement in Europe highlights resale price maintenance and distribution pressure risk. Strategy should never encode implicit/explicit resale price control mechanics without legal review. Mitigation: include antitrust guardrails and jurisdictional legal review requirement. Sources: [F12], [F13 - evergreen legal baseline].

7) **Contradiction: partner consolidation can help or hurt depending on execution quality.**  
Some examples show severe backlash from abrupt consolidation, while others report cleaner partner focus with less disruption. Implication: "reduce partner count" is not inherently good or bad; artifact must justify consolidation criteria and transition safeguards. Sources: [F2], [F3], [F15].

8) **Bad output shape vs good output shape.**  
Bad: "launch partner program, offer MDF, recruit top 20 partners." Good: segmented economics, explicit ownership/deal-reg policy, activation milestones, attribution confidence policy, and compliance guardrails. This distinction should be encoded as quality checklist in SKILL draft content. Sources: [F5], [F6], [F9], [F11].

**Sources:**
- [F1] https://www.crn.com/news/virtualization/2024/broadcom-takes-top-vmware-accounts-direct-effective-immediately (2024; trade reporting with policy details)
- [F2] https://www.crn.com/news/virtualization/2024/scared-angry-and-terminated-vmware-partners-unload-on-broadcom (2024; partner sentiment evidence)
- [F3] https://www.crn.com/news/virtualization/2024/broadcom-ceo-hock-tan-old-vmware-model-created-channel-chaos-and-conflict-in-the-marketplace (2024; executive framing)
- [F4] https://www.theregister.com/2024/01/10/broadcom_ends_vmware_partner_program (2024-01-10; independent tech reporting)
- [F5] https://learn.microsoft.com/en-us/partner-center/referrals/co-sell-requirements (updated 2025-09-25; first-party requirements)
- [F6] https://learn.microsoft.com/en-us/partner-center/register-deals (updated 2025-08-29; first-party process rules)
- [F7] https://futurumgroup.com/press-release/co-sell-support-jumps-14-6-points-to-39-2-displacing-developer-tools-as-channel-partners-1-vendor-priority/ (2026-03-04; analyst press release)
- [F9] https://www.tsia.com/blog/the-state-of-xaas-channel-partnerships-2024 (updated 2024-04-16)
- [F10] https://www.sec.gov/newsroom/press-releases/2024-4 (2024-01-10; primary enforcement source)
- [F11] https://www.justice.gov/criminal/criminal-fraud/page/file/937501/dl?inline (DOJ ECCP guidance, updated 2024-09; primary)
- [F12] https://autoritedelaconcurrence.fr/en/press-release/autorite-imposes-fines-eu611-million-10-manufacturers-and-2-distributors-household (2024-12-19; primary regulator)
- [F13] https://competition-policy.ec.europa.eu/antitrust/legislation/vertical-block-exemptions_en (2022, evergreen legal baseline) and https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=oj:JOC_2022_248_R_0001
- [F14] https://www.computerweekly.com/microscope/news/366632557/Canalys-The-spotlight-falls-on-partner-programmes (2025-10-10; trade source citing analyst context)
- [F15] https://www.crn.com/news/networking/2024/riverbed-simplifies-channel-program-focuses-only-on-partners-on-the-journey-that-we-re-on (2024; alternate consolidation outcome)

---

### Angle 5+: Marketplace & Program-Gating Integration Patterns
> Domain-specific angle: how partner-channel strategy should integrate marketplace/compliance/program-gating constraints so recommendations are executable, not abstract.

**Findings:**

1) Marketplace economics should be a first-class field in channel strategy artifacts, not a side note, because fee schedules and private-offer mechanics change net margin materially. Sources: [T6], [T14], [T10].

2) Co-sell readiness and partner-tier eligibility are operational constraints that should be represented as explicit "readiness gaps" per prioritized target. Sources: [T8], [T9], [M8].

3) Program policy complexity (deal registration, transacting constraints, reseller authorization) creates predictable execution risk; strategy artifacts should include "policy dependency" and "owner" fields for each critical constraint. Sources: [F5], [F6], [T13].

4) Legal/compliance controls should be embedded in channel strategy output from day one, because channel growth can scale risk through third parties as fast as it scales revenue. Sources: [F10], [F11], [F12].

5) Contradiction to encode: strong growth narratives for ecosystem channels can coexist with immature tooling and governance reality; therefore confidence scoring must be mandatory in final strategy output. Sources: [M3], [I7], [M10].

**Sources:**
- [T6] https://docs.aws.amazon.com/marketplace/latest/userguide/listing-fees.html
- [T8] https://aws.amazon.com/partners/programs/isv-accelerate/
- [T9] https://learn.microsoft.com/en-us/partner-center/referrals/co-sell-requirements
- [T10] https://learn.microsoft.com/en-us/partner-center/marketplace-offers/marketplace-commercial-transaction-capabilities-and-considerations
- [T13] https://docs.cloud.google.com/marketplace/docs/partners/resellers/resell
- [T14] https://cloud.google.com/terms/marketplace-revenue-share-schedule
- [M3] https://cdn.prod.website-files.com/65ba9e265a8d0623ea182de2/68b1f2b9a429822a4f41767f_The%20State%20of%20Partnerships%202025%20-%20Results.pdf
- [M8] https://learn.microsoft.com/en-us/partner-center/membership/partner-capability-score
- [M10] https://www.businesswire.com/news/home/20251006925215/en/Omdia-Hyperscaler-Cloud-Marketplace-Sales-to-Hit-%24163-Billion-by-2030
- [I7] https://cdn.prod.website-files.com/65ba9e265a8d0623ea182de2/68b1f2b9a429822a4f41767f_The%20State%20of%20Partnerships%202025%20-%20Results.pdf
- [F10] https://www.sec.gov/newsroom/press-releases/2024-4
- [F11] https://www.justice.gov/criminal/criminal-fraud/page/file/937501/dl?inline
- [F12] https://autoritedelaconcurrence.fr/en/press-release/autorite-imposes-fines-eu611-million-10-manufacturers-and-2-distributors-household

---

## Synthesis

The strongest 2024-2026 signal is that partner-channel strategy quality is now determined less by partner type taxonomy and more by operating discipline: lifecycle incentives, onboarding gates, conflict governance, and attribution quality. High-level channel ambition is widespread, but many teams still run with limited infrastructure and incomplete measurement contracts. That gap is exactly where low-quality strategy artifacts fail.

There are two critical contradictions that should remain explicit in the skill: first, macro forecasts about partner-dominant spend do not mean near-term channel share targets should be aggressive without maturity evidence; second, MDF cannot be treated as either universally outdated or universally sufficient. The right strategy is segmented and evidence-driven, not doctrinal.

Tooling has matured materially (PRM APIs, marketplace fee schedules, co-sell programs, ecosystem overlap platforms), but tooling alone does not remove interpretation risk. The same revenue number can mean very different things depending on attribution model, maturity segment, and lifecycle context. Therefore the skill should require attribution metadata and confidence labeling as part of the artifact, not as optional narrative.

Failure mode evidence is consistent: abrupt ownership changes, weak deal-reg operations, training-only onboarding, and missing compliance controls produce partner distrust or legal risk. These are not edge cases. They should be encoded as mandatory anti-pattern checks with detection signals and mitigation fields, so the strategy artifact can be audited before execution.

Most actionable outcome: upgrade `rtm-partner-channel` from descriptive planning to execution-grade contract. The upgraded draft content below provides concrete methodology steps, hard decision rules, tool usage guidance constrained to verified methods, warning blocks, and a stricter schema that supports downstream handoff and governance.

---

## Recommendations for SKILL.md

Concrete, actionable changes for `rtm-partner-channel/SKILL.md`:

- [x] Add a staged methodology that forces dual-horizon targets (`12-month realistic` and `24-36 month expansion`) with confidence labeling.
- [x] Replace pure partner-type taxonomy with activity-mix profiling (`sell/service/build`) and lifecycle role mapping.
- [x] Add incentive design rules that distinguish recurring lifecycle outcomes from simple upfront payout.
- [x] Add onboarding stage gates with activation windows and promotion/deprioritization rules.
- [x] Add channel conflict operating rules (account ownership policy + deal registration controls + transition policy).
- [x] Add measurement interpretation contract: sourced vs influenced, attribution model, leading vs lagging indicators, confidence class.
- [x] Add anti-pattern warning blocks with detection signal, consequence, and mitigation.
- [x] Expand available-tools guidance using only verified existing tool syntax and explicitly flag non-available data as unknown.
- [x] Expand artifact schema with marketplace route, readiness gaps, attribution policy, risk controls, and quality checks.
- [x] Add a completion checklist that blocks artifact write when critical evidence/governance fields are missing.

---

## Draft Content for SKILL.md

### Draft: Core mode rewrite

---
### Core mode

You are designing a partner channel strategy that can be executed, measured, and governed. Do not stop at naming partner types. Your output must prove five things:

1. Why each partner motion is selected for this segment and time horizon.
2. Why the economics work for both sides (partner and vendor).
3. How partner activation moves from signed to productive.
4. How channel conflict and compliance risks are controlled.
5. How success is measured with explicit signal quality rules.

If any of these five areas are vague, the strategy is incomplete.

---

### Draft: Methodology section replacement

---
### Methodology

#### Step 1: Set horizon and ambition realism before partner selection

Before selecting partner types, define two explicit channel-share targets:

- `months_12_target`: realistic near-term contribution based on current operating capacity and stack maturity.
- `months_24_36_target`: expansion target assuming successful capability buildout.

Decision rules:

1. If current tooling/process maturity is low (manual spreadsheets, weak integration, no reliable attribution), keep the 12-month target conservative and mark confidence as `low` or `medium`.
2. If target exceeds your evidence-supported maturity, include required capability investments and date-bound milestones; otherwise downgrade the target to `stretch` not `base`.
3. Never publish one single channel-percentage target without confidence class and assumptions.

Rationale: 2025 surveys and operator data show ambition frequently outpaces infrastructure, creating predictable forecast error.

#### Step 2: Profile partner archetypes by behavior, not labels

For each candidate partner, score contribution across:

- `sell`: pipeline creation / deal progression contribution,
- `service`: implementation, onboarding, managed services capability,
- `build`: integration/product extension capability.

Then assign partner motion:

- `technology_integration` when build + influence is strong,
- `reseller_var` when sell + service economics are strong,
- `referral_affiliate` when lightweight demand transfer is strong,
- `oem_whitelabel` when distribution leverage outweighs brand control.

Do not classify partner motion from brand/category labels alone. Category labels hide mixed behaviors and lead to bad incentive design.

#### Step 3: Design partner value proposition before commission

For each partner motion, write a partner-first value proposition:

- What partner pain or growth objective this motion solves.
- What monetization route exists for partner (license margin, services attach, co-sell leverage, retention uplift).
- What capability requirement partner must meet to realize that value.

Rule: "we pay 20% commission" is not a value proposition. Commission is one instrument. The proposition is partner business improvement.

#### Step 4: Build lifecycle incentive map (land/adopt/expand/renew)

Define incentives by lifecycle stage:

1. `Land`: lead generation, opportunity creation, deal progression.
2. `Adopt`: onboarding quality, activation speed, implementation outcomes.
3. `Expand`: upsell/cross-sell participation and attach growth.
4. `Renew`: retention support and renewal-risk reduction.

Design guidance:

- Keep commission structures transparent and easy to compute.
- Add capability funding where partner enablement bottlenecks block scale.
- Do not apply one global MDF policy; segment by partner archetype and proof of impact.
- If incentives only reward initial bookings, your recurring model is misaligned.

#### Step 5: Enforce onboarding stage gates and activation windows

For each signed partner, define required exit criteria by stage:

- `recruited` -> `enabled`: contractual + technical + commercial setup complete.
- `enabled` -> `active`: first meaningful joint action (registered deal, qualified referral, integration milestone) within defined days.
- `active` -> `productive`: measurable pipeline or delivery contribution within defined 30-90 day window.

Decision rules:

1. If partner misses activation window, assign `at_risk` status and trigger remediation plan.
2. If partner misses productivity gate after remediation, deprioritize from high-touch investment pool.
3. Do not continue unlimited onboarding with no activity evidence.

#### Step 6: Encode channel conflict policy before go-live

The strategy must include:

- account ownership segmentation criteria,
- deal registration policy and eligibility checks,
- exception handling path and SLA,
- transition policy for changed ownership rules.

Do not defer this section to "sales operations later." Missing conflict policy is one of the fastest paths to partner distrust.

#### Step 7: Add attribution and interpretation contract

For each reporting period, require:

- `partner_sourced_pipeline`
- `partner_influenced_pipeline`
- attribution model declaration (`first_touch`, `last_touch`, `multi_touch`, `hybrid`)
- confidence class (`directional`, `decision_grade`)

Interpretation rules:

1. If attribution model is single-touch only, influenced metrics default to `directional`.
2. If leading indicators (activation, partner tool adoption, co-sell participation) are weak, downgrade confidence in lagging revenue projections.
3. Segment outcomes by partner maturity band to avoid blended-metric distortion.

#### Step 8: Add compliance and legal guardrails

Include explicit controls for:

- third-party due diligence lifecycle (onboarding + monitoring),
- compensation reasonableness checks,
- anti-corruption policy compliance,
- competition-law review for pricing/channel governance terms.

Do not encode resale price controls or punitive pricing enforcement behavior without legal approval.

#### Step 9: Final quality gate before artifact write

Before writing artifact, verify all mandatory areas are present:

1. dual-horizon targets + confidence
2. partner activity profile + value proposition
3. lifecycle incentives + economics
4. onboarding gates + conflict policy
5. attribution contract + risk controls

If any area is missing, do not write final artifact.

---

### Draft: Available Tools section rewrite

```text
## Available Tools

flexus_policy_document(op="activate", args={"p": "/strategy/gtm-channel-strategy"})
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})

crunchbase(
  op="call",
  args={
    "method_id": "crunchbase.searches.organizations.post.v1",
    "field_ids": ["name", "categories", "funding_total"],
    "query": []
  }
)

write_artifact(
  artifact_type="partner_channel_strategy",
  path="/strategy/rtm-partner-channel",
  data={...}
)
```

Tool usage guidance:

- Always activate `/strategy/gtm-channel-strategy` before selecting partner motions; this anchors channel strategy to the current GTM context.
- Use `/segments/{segment_id}/icp-scorecard` to validate market overlap and avoid partner selection based on intuition-only fit.
- Use `crunchbase.searches.organizations.post.v1` to gather candidate company evidence (category and funding context), but do not infer partner readiness from firmographics alone.
- Do not invent additional Crunchbase method IDs or undocumented endpoints.
- If required data is unavailable in current tools (for example, private pricing terms, partner certification status, or legal risk details), record it as a gap in the artifact instead of fabricating.

---

### Draft: Anti-pattern warning blocks

### Warning: Commission-Only Strategy

**What it looks like in practice**  
Your strategy describes payout percentages but does not model partner workload cost, services attach assumptions, or post-sale responsibilities.

**Detection signal**  
Partner recruitment count increases, but active revenue-contributing partner share remains low beyond the first onboarding cycle.

**Consequence if missed**  
High top-of-funnel activity with weak adoption/renewals, declining partner trust, and low retained channel value.

**Mitigation steps**  
1. Add partner economics per archetype (`expected margin`, `services opportunity`, `time-to-value`).  
2. Add lifecycle incentive map across land/adopt/expand/renew.  
3. Add a policy that deprioritizes partner types where economics are structurally unattractive even with incentives.

### Warning: Conflict Policy Deferred

**What it looks like in practice**  
You define partner tiers and target list but leave account ownership, deal registration exceptions, and transition rules undefined.

**Detection signal**  
Frequent disputes around account entitlement, deal registration rejections, and "who owns this customer" escalations.

**Consequence if missed**  
Partner frustration, slowed co-sell motions, and increased churn to competitor ecosystems.

**Mitigation steps**  
1. Publish segmentation criteria and conflict resolution workflow before launch.  
2. Add pre-submit deal-reg validation checks and rejection reason taxonomy.  
3. Add explicit transition window and protection policy for account ownership changes.

### Warning: Training-Only Onboarding

**What it looks like in practice**  
Program success is measured by certification completions or content consumption, not field execution outcomes.

**Detection signal**  
High enablement completion but low first-opportunity creation and weak 30-90 day productivity.

**Consequence if missed**  
"Certified but inactive" partner population and poor channel ROI.

**Mitigation steps**  
1. Define mandatory first-opportunity milestone deadlines.  
2. Tie onboarding completion to executed joint actions, not course completion alone.  
3. Create remediation and deprioritization policies for missed stage gates.

### Warning: Sourced-Only Measurement

**What it looks like in practice**  
Reporting and compensation rely only on partner-sourced pipeline/revenue.

**Detection signal**  
Influence-heavy partners appear low value despite significant contribution to deal progression and expansion outcomes.

**Consequence if missed**  
Systematic under-crediting of strategic partners and distorted budget/investment decisions.

**Mitigation steps**  
1. Require sourced and influenced metrics together.  
2. Require attribution model declaration and confidence class in every report.  
3. Mark single-touch influenced figures as directional, not decision-grade.

### Warning: Compliance as Onboarding Checkbox

**What it looks like in practice**  
You run one-time due diligence at contract signature and assume contractual language is sufficient.

**Detection signal**  
No periodic third-party monitoring cadence, no compensation reasonableness review, weak documentation controls.

**Consequence if missed**  
Elevated anti-corruption and regulatory exposure as partner network scales.

**Mitigation steps**  
1. Add continuous due-diligence and review cadence.  
2. Add controls for partner compensation rationale and approval traceability.  
3. Add jurisdiction-aware legal review path for channel policy changes.

---

### Draft: Partner economics and measurement thresholds block

Use these as default calibration ranges, not universal truths:

- Near-term channel contribution planning commonly clusters in lower bands (for example 11-50% in 2025 survey distributions); treat high targets as `stretch` unless maturity evidence is strong.
- Referral commissions commonly appear in 20-40% ranges in partner-network benchmark sources; use this as initial calibration, then validate against your unit economics.
- Activation velocity matters: absence of meaningful first action in early onboarding windows is a risk signal requiring remediation, not passive waiting.

Interpretation instructions:

1. Do not import benchmark percentages blindly across motions, geographies, and ACV profiles.
2. Every threshold used in strategy must include: source, applicability assumptions, and confidence class.
3. If assumptions are weak or source is non-representative, mark threshold as directional.

---

### Draft: Artifact schema additions

The JSON schema fragment below is a complete replacement proposal for `partner_channel_strategy`. It preserves existing core fields while adding execution-grade structures for planning horizon, attribution quality, readiness gaps, and risk controls.

```json
{
  "partner_channel_strategy": {
    "type": "object",
    "required": [
      "created_at",
      "planning_horizon",
      "channel_mix_targets",
      "partner_types",
      "partner_economics",
      "partner_icp",
      "onboarding_stages",
      "attribution_policy",
      "measurement_framework",
      "risk_controls",
      "prioritized_targets"
    ],
    "additionalProperties": false,
    "properties": {
      "created_at": {
        "type": "string",
        "description": "ISO-8601 timestamp when strategy was generated."
      },
      "planning_horizon": {
        "type": "object",
        "required": ["months_12_target", "months_24_36_target", "assumptions"],
        "additionalProperties": false,
        "properties": {
          "months_12_target": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Near-term channel revenue share target as fraction of total revenue."
          },
          "months_24_36_target": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Expansion horizon channel revenue share target as fraction of total revenue."
          },
          "assumptions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Critical assumptions required for targets to remain valid."
          }
        }
      },
      "channel_mix_targets": {
        "type": "object",
        "required": ["base_case", "stretch_case", "confidence_level"],
        "additionalProperties": false,
        "properties": {
          "base_case": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Most likely channel-share outcome given current maturity."
          },
          "stretch_case": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Ambitious but plausible channel-share outcome requiring additional investments."
          },
          "confidence_level": {
            "type": "string",
            "enum": ["low", "medium", "high"],
            "description": "Overall confidence in target realism based on operating readiness and evidence quality."
          }
        }
      },
      "partner_types": {
        "type": "array",
        "items": {
          "type": "object",
          "required": [
            "type",
            "rationale",
            "priority",
            "value_prop_to_partner",
            "activity_mix",
            "lifecycle_role",
            "marketplace_route"
          ],
          "additionalProperties": false,
          "properties": {
            "type": {
              "type": "string",
              "enum": [
                "technology_integration",
                "reseller_var",
                "referral_affiliate",
                "oem_whitelabel"
              ],
              "description": "Primary channel motion archetype."
            },
            "rationale": {
              "type": "string",
              "description": "Evidence-backed reason this partner motion is selected."
            },
            "priority": {
              "type": "string",
              "enum": ["high", "medium", "low"],
              "description": "Execution priority for this motion."
            },
            "value_prop_to_partner": {
              "type": "string",
              "description": "Partner-first value proposition, beyond commission."
            },
            "activity_mix": {
              "type": "object",
              "required": ["sell_score", "service_score", "build_score"],
              "additionalProperties": false,
              "properties": {
                "sell_score": {
                  "type": "number",
                  "minimum": 0,
                  "maximum": 5,
                  "description": "Relative strength of partner in pipeline creation/progression."
                },
                "service_score": {
                  "type": "number",
                  "minimum": 0,
                  "maximum": 5,
                  "description": "Relative strength in implementation, onboarding, and managed-service delivery."
                },
                "build_score": {
                  "type": "number",
                  "minimum": 0,
                  "maximum": 5,
                  "description": "Relative strength in integration or product-extension capability."
                }
              }
            },
            "lifecycle_role": {
              "type": "array",
              "items": {
                "type": "string",
                "enum": ["land", "adopt", "expand", "renew"]
              },
              "description": "Customer lifecycle stages where this partner type is expected to contribute."
            },
            "marketplace_route": {
              "type": "string",
              "enum": ["none", "aws_marketplace", "microsoft_marketplace", "google_marketplace", "multi_marketplace"],
              "description": "Primary marketplace transacting route expected for this partner type."
            }
          }
        }
      },
      "partner_economics": {
        "type": "object",
        "required": [
          "revenue_share_pct",
          "deal_registration_policy",
          "minimum_deal_size",
          "target_partner_margin_pct_min",
          "lifecycle_incentives"
        ],
        "additionalProperties": false,
        "properties": {
          "revenue_share_pct": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Baseline revenue share as fraction of contract value."
          },
          "recurring_vs_onetime": {
            "type": "string",
            "enum": ["recurring", "onetime", "hybrid"],
            "description": "Payout structure shape."
          },
          "deal_registration_policy": {
            "type": "string",
            "description": "Summary of registration ownership and approval policy."
          },
          "minimum_deal_size": {
            "type": "number",
            "minimum": 0,
            "description": "Minimum deal size for standard partner economics to apply."
          },
          "target_partner_margin_pct_min": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Minimum expected partner gross margin required for motion viability."
          },
          "lifecycle_incentives": {
            "type": "object",
            "required": ["land", "adopt", "expand", "renew"],
            "additionalProperties": false,
            "properties": {
              "land": {"type": "string", "description": "Incentive design for initial deal acquisition."},
              "adopt": {"type": "string", "description": "Incentive design for onboarding and active usage outcomes."},
              "expand": {"type": "string", "description": "Incentive design for upsell/cross-sell contribution."},
              "renew": {"type": "string", "description": "Incentive design for retention/renewal contribution."}
            }
          },
          "marketplace_fee_assumptions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Fee assumptions used when marketplace routes are selected."
          }
        }
      },
      "partner_icp": {
        "type": "object",
        "required": [
          "market_overlap_min",
          "competitive_exclusion",
          "capacity_requirements",
          "fit_evidence_requirements"
        ],
        "additionalProperties": false,
        "properties": {
          "market_overlap_min": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Minimum required customer overlap between partner base and target ICP."
          },
          "competitive_exclusion": {
            "type": "string",
            "description": "Rules for excluding direct competitive conflicts."
          },
          "capacity_requirements": {
            "type": "string",
            "description": "Minimum sales/technical capacity required to execute the motion."
          },
          "fit_evidence_requirements": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Evidence types required to validate partner fit (overlap proof, category match, prior delivery examples)."
          }
        }
      },
      "onboarding_stages": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["stage", "max_days", "exit_criteria", "failure_action"],
          "additionalProperties": false,
          "properties": {
            "stage": {
              "type": "string",
              "enum": ["recruited", "enabled", "active", "productive"],
              "description": "Partner progression stage."
            },
            "max_days": {
              "type": "integer",
              "minimum": 1,
              "description": "Maximum days allowed in stage before escalation."
            },
            "exit_criteria": {
              "type": "array",
              "items": {"type": "string"},
              "description": "Objective criteria required to move to next stage."
            },
            "failure_action": {
              "type": "string",
              "enum": ["remediate", "deprioritize", "exit"],
              "description": "Action if stage exit criteria are not met in time."
            }
          }
        }
      },
      "attribution_policy": {
        "type": "object",
        "required": [
          "model",
          "sourced_definition",
          "influenced_definition",
          "confidence_rules"
        ],
        "additionalProperties": false,
        "properties": {
          "model": {
            "type": "string",
            "enum": ["first_touch", "last_touch", "multi_touch", "hybrid"],
            "description": "Attribution model used for partner impact reporting."
          },
          "sourced_definition": {
            "type": "string",
            "description": "Definition of partner-sourced pipeline/revenue used in this strategy."
          },
          "influenced_definition": {
            "type": "string",
            "description": "Definition of partner-influenced pipeline/revenue used in this strategy."
          },
          "confidence_rules": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Rules mapping attribution method and data completeness to confidence class."
          }
        }
      },
      "measurement_framework": {
        "type": "object",
        "required": ["leading_indicators", "lagging_indicators", "review_cadence"],
        "additionalProperties": false,
        "properties": {
          "leading_indicators": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Early indicators such as activation speed, co-sell participation, enablement completion, and partner workflow adoption."
          },
          "lagging_indicators": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Outcome indicators such as sourced pipeline, influenced pipeline, win rate, expansion, and renewal contribution."
          },
          "review_cadence": {
            "type": "string",
            "enum": ["weekly", "biweekly", "monthly", "quarterly"],
            "description": "Cadence for reviewing partner program performance and policy adjustments."
          },
          "maturity_segmentation": {
            "type": "string",
            "description": "How metrics are segmented by ecosystem maturity to avoid blended-signal distortion."
          }
        }
      },
      "risk_controls": {
        "type": "object",
        "required": [
          "channel_conflict_policy",
          "compliance_controls",
          "competition_law_guardrail",
          "anti_pattern_checks"
        ],
        "additionalProperties": false,
        "properties": {
          "channel_conflict_policy": {
            "type": "object",
            "required": ["account_segmentation_rules", "deal_registration_rules", "exception_sla"],
            "additionalProperties": false,
            "properties": {
              "account_segmentation_rules": {
                "type": "string",
                "description": "How accounts are assigned between direct and partner-led motions."
              },
              "deal_registration_rules": {
                "type": "string",
                "description": "Operational rules for eligibility, approvals, and ownership."
              },
              "exception_sla": {
                "type": "string",
                "description": "Resolution SLA for registration disputes and ownership conflicts."
              }
            }
          },
          "compliance_controls": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Third-party risk controls for onboarding and ongoing monitoring."
          },
          "competition_law_guardrail": {
            "type": "string",
            "description": "Explicit policy to require legal review for pricing/distribution terms with antitrust sensitivity."
          },
          "anti_pattern_checks": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["name", "status", "detection_signal", "mitigation"],
              "additionalProperties": false,
              "properties": {
                "name": {"type": "string", "description": "Anti-pattern label."},
                "status": {
                  "type": "string",
                  "enum": ["clear", "warning", "triggered"],
                  "description": "Current risk status for the anti-pattern."
                },
                "detection_signal": {
                  "type": "string",
                  "description": "Observed signal suggesting this anti-pattern may be present."
                },
                "mitigation": {
                  "type": "string",
                  "description": "Required mitigation action."
                }
              }
            }
          }
        }
      },
      "prioritized_targets": {
        "type": "array",
        "items": {
          "type": "object",
          "required": [
            "company_name",
            "partner_type",
            "overlap_evidence",
            "status",
            "readiness_gaps",
            "next_action"
          ],
          "additionalProperties": false,
          "properties": {
            "company_name": {"type": "string", "description": "Partner candidate company name."},
            "partner_type": {
              "type": "string",
              "enum": [
                "technology_integration",
                "reseller_var",
                "referral_affiliate",
                "oem_whitelabel"
              ],
              "description": "Selected partner motion for this target."
            },
            "overlap_evidence": {
              "type": "string",
              "description": "Evidence of customer/segment overlap supporting prioritization."
            },
            "status": {
              "type": "string",
              "enum": ["identified", "approached", "in_discussion", "signed", "inactive"],
              "description": "Current progression status."
            },
            "readiness_gaps": {
              "type": "array",
              "items": {"type": "string"},
              "description": "Known gating gaps (capability, program eligibility, legal/compliance, technical integration)."
            },
            "marketplace_path": {
              "type": "string",
              "enum": ["none", "aws_marketplace", "microsoft_marketplace", "google_marketplace", "multi_marketplace"],
              "description": "Expected marketplace transacting route for this target."
            },
            "next_action": {
              "type": "string",
              "description": "Most important next execution step for this target."
            }
          }
        }
      }
    }
  }
}
```

### Draft: Final quality-check block for end of SKILL.md

Use this completion check before final `write_artifact` call:

1. **Target realism check:** dual-horizon targets exist and include assumptions + confidence.
2. **Incentive alignment check:** lifecycle incentive map exists and partner economics are viable.
3. **Activation check:** onboarding stages include timed exit criteria and failure actions.
4. **Conflict/governance check:** account segmentation + deal registration + exception SLA are documented.
5. **Signal quality check:** sourced and influenced definitions + attribution model + confidence rules are explicit.
6. **Risk check:** compliance controls and legal guardrails are present.
7. **Evidence check:** prioritized targets include overlap evidence and readiness gaps.

If any check fails, output `needs-revision` rationale instead of writing a finalized channel strategy.

---

## Gaps & Uncertainties

- Many benchmark figures are from vendor-owned datasets and non-representative samples; they are useful as priors, not universal constants.
- Several vendor programs expose requirements clearly but not all commercial terms publicly (for example, negotiated pricing and custom tiers), so some economics assumptions must remain provisional.
- Public data on long-run partner channel contribution by segment/ACV remains fragmented; a second pass with proprietary analyst datasets would improve precision.
- Legal guidance is jurisdiction-dependent; this research includes high-level guardrails but does not replace country-specific counsel for pricing/distribution policy.
- Some growth forecasts are sourced via press summaries rather than full analyst reports; where this occurs, confidence should be treated as medium unless primary report access is obtained.
