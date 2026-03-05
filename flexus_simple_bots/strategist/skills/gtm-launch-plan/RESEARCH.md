# Research: gtm-launch-plan

**Skill path:** `strategist/skills/gtm-launch-plan/`
**Bot:** strategist (researcher | strategist | executor)
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`gtm-launch-plan` turns strategy artifacts into operational execution for the first 90 days: owners, dates, milestones, and measurable outcomes. The current `SKILL.md` already enforces an important principle ("one owner per milestone"), but it still leaves major quality risks under-specified: launch readiness gates, modern cross-channel sequencing, signal interpretation in noisy early windows, and compliance/deliverability checks that can quietly invalidate outreach.

Research from 2024-2026 shows that launch execution now has to account for multi-channel buyer behavior, larger and more complex buying ecosystems, AI-mediated discovery, stricter outreach platform controls, and persistent attribution disagreement. This research package is designed so a future editor can upgrade the skill from a good checklist into a robust operating system for launch execution.

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

- No generic filler ("it is important to...", "best practices suggest...") without concrete backing: **passed**
- No invented tool names, method IDs, or API endpoints - only verified real ones: **passed**
- Contradictions between sources are explicitly noted, not silently resolved: **passed**
- Volume: findings section should be 800-4000 words (too short = shallow, too long = unsynthesized): **passed**

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

Modern launch methodology should be designed as omnichannel orchestration, not a one-channel campaign. McKinsey reports B2B buyers commonly use around 10 channels and expect seamless switching; fragmented journeys can trigger supplier switching. Practically, launch plans should include cross-channel handoff readiness as a pre-launch gate, not a postmortem topic [A1].

Practical sequencing starts earlier than many startup launch plans assume. HubSpot and Asana both emphasize a 6-8 week preparation window, and HubSpot includes early customer/prospect interviews (12-15) before finalizing messaging. This implies "messaging locked" should be evidence-backed, not a subjective status [A4][A5].

Task-level accountability discipline is still a hard requirement. Asana's RACI guidance reinforces one Responsible and one Accountable per deliverable. In launch operations, this maps directly to the skill's existing "one owner per milestone" rule and supports keeping that constraint as non-negotiable [A6].

Launch readiness should include commercial-speed gates, not only content/asset completion. LeanData reports substantial delays in first lead activity and opportunity creation among many teams; teams with better automation/reporting discipline perform materially better. This supports adding SLA gates for response/handoff speed before broad launch expansion [A3].

Buying environments now combine broad stakeholder influence with pressure for fast decision progress. Forrester reports high multi-department participation and frequent buying stalls, while G2 reports shifts toward smaller active decision cores in software. The practical resolution: map wide stakeholder influence, but run fast owner-led execution cells [A2][A7].

AI-mediated discovery behavior is a meaningful methodology change versus older playbooks. G2 reports stronger preference for later-stage seller engagement and more AI-assisted research initiation. This suggests launch-week operations should include proof assets (comparisons, FAQs, customer evidence) before assuming outbound can carry demand alone [A7][A8].

A strict 30/60/90 cadence is now table stakes for operational launches, not an optional reporting format. Sources converge on structured pre-launch preparation, launch-week execution, and recurring post-launch iteration windows. Treat day 90 as the first full learning horizon, not the finish line [A4][A5].

Another major shift is from lead-centric optimization to opportunity- and buying-group-centric execution. LeanData and McKinsey evidence points to higher complexity and stronger need for account-level orchestration. Launch plans should therefore include opportunity progression and buying-group coverage metrics, not only top-of-funnel volume [A1][A3].

**Sources:**
- [A1] McKinsey, "Five fundamental truths: How B2B winners keep growing" - https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/five-fundamental-truths-how-b2b-winners-keep-growing - 2024-09
- [A2] Forrester press release, "The State of Business Buying, 2024" - https://www.forrester.com/press-newsroom/forrester-the-state-of-business-buying-2024/ - 2024-12
- [A3] LeanData, "The 2024 State of Go-to-Market Efficiency Report" - https://www.leandata.com/wp-content/uploads/2024/06/LeanData-The-2024-State-GTM-Efficiency-Report.pdf - 2024-06
- [A4] HubSpot, "Product Launch Checklist" - https://blog.hubspot.com/marketing/product-launch-checklist - 2024-09
- [A5] Asana, "5 steps to successfully managing product launches" - https://asana.com/resources/successful-product-launch-marketing - 2025-10
- [A6] Asana, "RACI Charts: The Ultimate Guide" - https://asana.com/resources/raci-chart - 2025-12
- [A7] G2, "Buyer Behavior Report 2025" - https://learn.g2.com/hubfs/G2-2025-Buyer-Behavior-Report-AI-Always-Included.pdf?hsLang=en - 2025-04
- [A8] G2, "How AI is Redefining the Buyer Journey in 2025" - https://company.g2.com/news/buyer-behavior-in-2025 - 2025-05

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

For launch planning execution, tool quality should be judged by operational reliability under deadline pressure, not feature count. CRM, analytics, communication, and calendar systems all have quota/rate/latency behavior that can distort launch metrics or break automations if not considered up front.

HubSpot and Salesforce remain common CRM anchors for launch operations. HubSpot provides structured CRM object APIs and explicit rate-limit headers; Salesforce exposes API limit visibility and can enforce protection behavior when sustained limits are exceeded. Launch plans should include explicit API budget and retry strategy where workflow automation depends on CRM writes [T1][T2][T3].

Marketing automation and campaign channels require versioning and concurrency governance. Mailchimp enforces connection/time constraints; LinkedIn Marketing APIs require explicit version headers and sunset awareness. A launch plan should include a technical "API version freeze" decision in pre-launch readiness [T4][T19][T20].

Analytics systems differ materially in ingestion and quality failure modes. Amplitude documents EPS and payload constraints; Mixpanel documents hot-shard behavior tied to identifier design; PostHog applies endpoint and organization-level limits with separate public/private API expectations. These are not edge cases during launches; they are common causes of silent data quality degradation [T7][T8][T9].

GA4 should be interpreted with freshness and thresholding caveats. Intraday reporting and attribution updates can shift after processing windows, and privacy thresholding is system-defined. Launch dashboards should explicitly label "directional intraday" versus "decision-grade daily" views [T10][T11][T12].

Attribution recovery tooling (for example enhanced conversions for leads) is increasingly relevant in first-party data environments, but requires exact implementation details (terms acceptance, hashing normalization, partial-failure handling, delayed visibility expectations). Launch plans that assume immediate perfect matching will overreact to early noise [T13][T14].

Project/calendar orchestration tools (Asana and Google Calendar APIs) are useful, but quota and retry discipline are mandatory under high event mutation patterns. Push-based sync and controlled backoff patterns are safer than high-frequency polling during launch week [T5][T6].

Slack and LinkedIn community/social integration is often constrained by method-specific or app-status-specific limits. Teams should treat community data ingestion as sampled operational input, not a guaranteed full-fidelity telemetry stream [T15][T16][T17][T18].

De-facto standards across sources:
1) One operational source of truth for owners/tasks (CRM or PM system),
2) explicit API rate-limit handling with retries,
3) clear distinction between directional and decision-grade metrics,
4) version/change management for APIs used in launch workflows.

**Practical Tooling Matrix**

| category | common options | what data you get | major caveat |
|---|---|---|---|
| CRM | HubSpot, Salesforce | Contacts/accounts/deals, ownership, lifecycle progression | Rate and daily API usage constraints can break high-volume automation [T1][T3] |
| Marketing automation / outreach | Mailchimp, HubSpot workflows, LinkedIn lead flows | Campaign events, audience state, lead sync data | Concurrency/timeouts and API version sunsets can interrupt launch [T4][T19] |
| Product analytics | Amplitude, Mixpanel, PostHog | Event streams, user behavior, feature usage | Identifier design and throttling rules can distort early metrics [T7][T8][T9] |
| Web analytics | GA4 | Session/source/conversion trend data | Freshness and thresholding caveats affect daily interpretation [T10][T12] |
| Attribution / conversion recovery | GA4 attribution settings, Google Ads enhanced conversions | Attribution model outputs, click-to-conversion matching | Model/lookback changes alter comparability over time [T11][T13][T14] |
| PM/calendar orchestration | Asana, Google Calendar API | Owners, due dates, launch event schedules | Quota and retry constraints matter under frequent updates [T5][T6] |
| Community/social operations | Slack, LinkedIn | Community activity and paid social outcomes | Method-specific throttling and app-policy changes [T15][T16][T18] |

**Sources:**
- [T1] HubSpot Developers, "API usage guidelines and limits" - https://developers.hubspot.com/docs/api/usage-details - 2026-03
- [T2] HubSpot Developers, "CRM API | Contacts" - https://developers.hubspot.com/docs/api-reference/crm-contacts-v3/guide - 2026-03
- [T3] Salesforce Developers Blog, "API Limits and Monitoring Your API Usage" - https://developer.salesforce.com/blogs/2024/11/api-limits-and-monitoring-your-api-usage - 2024-11
- [T4] Mailchimp Developer, "Fundamentals" - https://mailchimp.com/developer/marketing/docs/fundamentals/ - 2026-03
- [T5] Asana Developers, "Rate limits" - https://developers.asana.com/docs/rate-limits - 2026-03
- [T6] Google for Developers, "Manage quotas (Calendar API)" - https://developers.google.com/calendar/api/guides/quota - 2026-03
- [T7] Amplitude Docs, "HTTP V2 API" - https://amplitude.com/docs/apis/analytics/http-v2 - 2024-05
- [T8] Mixpanel Docs, "Hot Shard Limits" - https://docs.mixpanel.com/docs/tracking-best-practices/hot-shard-limits - 2026-03
- [T9] PostHog Docs, "API overview" - https://posthog.com/docs/api/overview - 2026-03
- [T10] Google Analytics Help, "Data freshness" - https://support.google.com/analytics/answer/11198161 - 2026-03
- [T11] Google Analytics Help, "Select attribution settings" - https://support.google.com/analytics/answer/10597962 - 2026-03
- [T12] Google Analytics Help, "About data thresholds" - https://support.google.com/analytics/answer/9383630 - 2026-03
- [T13] Google for Developers, "Enhanced conversions for leads overview" - https://developers.google.com/google-ads/api/docs/conversions/enhanced-conversions/overview - 2026-03
- [T14] Google for Developers, "ConversionUploadService.UploadClickConversions" - https://developers.google.com/google-ads/api/reference/rpc/v23/ConversionUploadService/UploadClickConversions - 2026-03
- [T15] Slack Developer Docs, "Web API rate limits" - https://docs.slack.dev/apis/web-api/rate-limits/ - 2025-05
- [T16] Slack Developer Docs changelog, "Rate limit changes for non-Marketplace apps" - https://docs.slack.dev/changelog/2025/05/29/rate-limit-changes-for-non-marketplace-apps - 2025-05
- [T17] Slack Developer Docs, "`conversations.history`" - https://docs.slack.dev/reference/methods/conversations.history/ - 2025-05
- [T18] Microsoft Learn (LinkedIn), "API Rate Limiting" - https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits - 2025-08
- [T19] Microsoft Learn (LinkedIn), "Marketing API Versioning" - https://learn.microsoft.com/en-us/linkedin/marketing/versioning?view=li-lms-2025-10 - 2026-02
- [T20] Microsoft Learn (LinkedIn), "Recent Marketing API Changes" - https://learn.microsoft.com/en-us/linkedin/marketing/integrations/recent-changes?view=li-lms-2026-02 - 2026-02

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

Early launch interpretation should prioritize click/reply/progression quality over open-rate optics. 2024-2025 benchmark reports show opens can move opposite to clicks and CTOR due privacy and platform behavior changes. A launch plan that treats open-rate drop as immediate channel failure will often make the wrong decision [D1][D2].

Benchmarks must be segmented by industry, region, and motion. Public averages hide large spreads; for example landing page conversion differs materially by channel and vertical, and cold outreach productivity is heavily skewed between average and top performers. Use segmented references and include confidence notes in recommendations [D3][D4].

Copy and sequence structure can be the dominant lever in early outbound performance. If reply rates are weak, fixing email structure and message framing can produce larger gains than prematurely abandoning ICP/channel hypotheses [D3].

Channel mix changes can mimic execution changes. When traffic mix shifts toward lower-converting channels, blended CVR can fall even if each channel remains stable. Launch scorecards should include both blended and channel-normalized views [D4].

Stage-level funnel diagnosis is higher signal than single end-to-end conversion numbers. Where benchmark ranges are available, use them to identify leak stage before recommending broad strategy pivots. Without stage decomposition, interventions tend to be expensive and unfocused [D5].

CAC/payback targets are useful but should be interpreted as context-dependent guardrails, not universal constants. Segment differences are large; early-stage decisions should use directional thresholding plus trend stability, not one static number [D6].

Early product activation and time-to-value (TTV) can be stronger leading indicators than user-count growth in the first 60 days. If activation is weak, scaling acquisition often increases waste and masks root-cause onboarding/product issues [D7][D8].

Attribution disagreement is common and is itself a warning signal. If tools disagree materially, launch plans should reduce decision aggressiveness and require triangulation before major budget reallocation [D9][D10].

Opportunity-creation lag means closed-won outcomes are too delayed to be the only decision basis in first-90-day windows. Use leading indicators for near-term decisions, then validate with lagging outcomes as cohorts mature [D11].

**Decision Rules for 30/60/90**

- **30-day rule:** If opens move but clicks/CTOR and qualified responses do not confirm, treat as signal conflict and fix creative/targeting before channel reallocation [D1][D2].
- **30-day rule:** If outbound reply is weak and emails are long/pitch-heavy, rewrite to concise, value-first sequence before changing ICP assumptions [D3].
- **60-day rule:** If one funnel stage underperforms benchmark bands while others are stable, target that stage (handoff, qualification, offer) instead of rewriting whole launch plan [D5].
- **60-day rule:** If activation/TTV underperforms while top-funnel is healthy, pause scale and focus on onboarding/product value delivery [D7][D8].
- **90-day rule:** If attribution systems disagree, require at least two independent methods before major budget shifts [D9][D10].
- **90-day rule:** If opportunity creation is lagging but leading indicators are improving and incubation windows are still open, extend observation rather than forcing full GTM reset [D11].

**Contradictions / Context Dependence**

- Opens can decline while clicks/replies improve; interpretation changes by metric layer [D1][D2].
- Email can look highly efficient for certain LP cohorts while cold outbound productivity remains harsh at average-rep level [D3][D4].
- Agency-derived benchmark sources are useful directional references but should be marked medium confidence for universalization [D5][D6].
- Last-touch attribution can over-credit short-cycle channels versus broader incrementality outcomes [D10].

**Sources:**
- [D1] Zeta Global, "Q2 2024 Email Marketing Benchmark Report" - https://zetaglobal.com/wp-content/uploads/2024/09/24Q2-Email-Benchmark-Report.pdf - 2024-09
- [D2] MailerLite, "Email benchmarks by industry and region for 2026" - https://www.mailerlite.com/blog/compare-your-email-performance-metrics-industry-benchmarks - 2025-12
- [D3] Gong Labs, "Does cold email even work any more?" - https://www.gong.io/resources/labs/does-cold-email-even-work-any-more-heres-what-the-data-says/ - 2025-07
- [D4] Unbounce, "Average landing page conversion rates (Q4 2024)" - https://unbounce.com/average-conversion-rates-landing-pages - 2024-12
- [D5] First Page Sage, "B2B SaaS Funnel Conversion Benchmarks" - https://firstpagesage.com/seo-blog/b2b-saas-funnel-conversion-benchmarks-fc/ - 2025-06
- [D6] First Page Sage, "SaaS CAC Payback Benchmarks: 2025 Report" - https://firstpagesage.com/reports/saas-cac-payback-benchmarks/ - 2024-06
- [D7] Mind the Product, "Introducing our product benchmarking report" - https://www.mindtheproduct.com/introducing-our-product-benchmarking-report - 2024-06
- [D8] Pendo, "Product Benchmarks for Top Teams" - https://pendo.io/product-benchmarks - 2024-06
- [D9] MMA Global, "State of Attribution: 8th Annual Marketer Benchmark Report" - https://www.mmaglobal.com/matt/state-of-attribution - 2024-06
- [D10] MarketingCharts, "Attribution models biased to short-term effects" - https://www.marketingcharts.com/customer-centric/analytics-automated-and-martech-234337 - 2024-11
- [D11] Gradient Works, "The sales incubation period" - https://www.gradient.works/blog/the-sales-incubation-period-outbounds-overlooked-metric - 2025-05

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

1) **Pattern:** Budget-agnostic launch planning.  
**Detection signal:** Plan lists channels and tasks, but no spend guardrails, efficiency thresholds, or stop rules.  
**Consequence:** Mid-cycle cuts and reactive pivots that break launch sequencing.  
**Mitigation:** Add channel-level efficiency guardrails and pre-agreed pause/scale triggers [F1][F2].

2) **Pattern:** Awareness-first with no proof-of-value milestones.  
**Detection signal:** 30/60/90 plan lacks time-to-first-value or measurable customer outcome targets.  
**Consequence:** Early churn, buyer skepticism, and stalled opportunities.  
**Mitigation:** Require concrete value proof milestones in weeks 2-8 [F2][F3].

3) **Pattern:** Late legal/security/procurement alignment.  
**Detection signal:** Opportunities advance commercially but stall in compliance/contracting.  
**Consequence:** Forecast misses and avoidable late-stage losses.  
**Mitigation:** Front-load legal/security artifacts in pre-launch checklist [F3][F1].

4) **Pattern:** Scale motions on weak data quality.  
**Detection signal:** Low trust in CRM and high manual reporting burden.  
**Consequence:** Mis-targeting, unreliable forecasting, and misread channel performance.  
**Mitigation:** Add data readiness sprint and hygiene SLAs before launch [F4][F1].

5) **Pattern:** Build-first, PMF-later launch.  
**Detection signal:** Product shipped, but usage/value signals remain weak or non-repeatable.  
**Consequence:** Burn without durable revenue progression.  
**Mitigation:** Gate scale by repeatable validation milestones (problem proof -> paid pilot -> repeatable conversion) [F5][F6].

6) **Pattern:** Pricing disconnected from pain intensity.  
**Detection signal:** Demo interest but repeated drop-off at pricing/procurement stages.  
**Consequence:** Active-looking pipeline with low monetization.  
**Mitigation:** Tie price to quantified pain and run paid design-partner tests [F6][F5].

7) **Pattern:** Deliverability treated as optional technical detail.  
**Detection signal:** Missing SPF/DKIM/DMARC, poor unsubscribe handling, rising complaint risk.  
**Consequence:** Outreach enters spam pathways, causing false "messaging failed" diagnosis.  
**Mitigation:** Include deliverability as hard launch blocker with ongoing monitoring [F7][F8].

8) **Pattern:** Transactional/promotional policy mixing.  
**Detection signal:** Promotional language in transactional streams or deceptive headers/subjects.  
**Consequence:** Legal exposure and deliverability deterioration.  
**Mitigation:** Separate governance for transactional vs marketing streams [F7][F13].

9) **Pattern:** "Consent theater."  
**Detection signal:** Front-end opt-out accepted but backend trackers/data sharing continue.  
**Consequence:** Regulatory enforcement and remediation overhead.  
**Mitigation:** Test consent propagation end-to-end and run recurring tracker audits [F9][F10][F11].

10) **Pattern:** One-time compliance checklist with no monitoring cadence.  
**Detection signal:** No periodic review despite active regulatory changes and enforcement activity.  
**Consequence:** Plan drifts out of compliance during first 90 days.  
**Mitigation:** Add monthly regulatory delta review tied to GTM backlog updates [F15][F10].

**Bad vs Good Output Signatures**

- **Bad:** task list with dates but no owner accountability model beyond team labels; **Good:** one named owner per deliverable plus escalation owner.
- **Bad:** launch plan with activity metrics only; **Good:** includes value, conversion, and efficiency guardrails tied to decisions.
- **Bad:** "consent banner installed" as privacy proof; **Good:** consent propagation and tracker audit evidence.
- **Bad:** outbound volume targets without deliverability gates; **Good:** SPF/DKIM/DMARC + complaint controls before scale.
- **Bad:** single blended paid search KPI; **Good:** explicit segmentation and caveat notes for attribution confidence.

**Sources:**
- [F1] Gartner, "CMO Survey 2024" - https://www.gartner.com/en/newsroom/press-releases/2024-05-13-gartner-cmo-survey-reveals-marketing-budgets-have-dropped-to-7-7-percent-of-overall-company-revenue-in-2024 - 2024-05
- [F2] G2, "Buyer Behavior in 2024" - https://company.g2.com/news/buyer-behavior-in-2024 - 2024-06
- [F3] G2, "2024 Buyer Behavior Report" - https://research.g2.com/hubfs/2024-buyer-behavior-report.pdf - 2024-06
- [F4] Salesforce, "Sales Teams Using AI" - https://www.salesforce.com/news/stories/sales-ai-statistics-2024/?bc=HA - 2024-07
- [F5] Basis Robotics postmortem - https://basisrobotics.tech/2025/01/08/postmortem/ - 2025-01
- [F6] Niko Noll, "Lessons from a 1.5 year SaaS journey" - https://www.nikonoll.com/p/post-mortem-lessons-from-a-15-year - 2024-11
- [F7] Google Workspace Help, "Email sender guidelines" - https://support.google.com/mail/answer/81126 - 2024-02
- [F8] Yahoo Sender Hub, "Sender Best Practices" - https://senders.yahooinc.com/best-practices - 2024-02
- [F9] California DOJ, "Largest CCPA settlement (Healthline)" - https://oag.ca.gov/news/press-releases/attorney-general-bonta-announces-largest-ccpa-settlement-date-secures-155 - 2025-07
- [F10] CPPA, "Joint investigative privacy sweep (GPC)" - https://cppa.ca.gov/announcements/2025/20250909.html - 2025-09
- [F11] IAPP, "Opt-out functionality enforcement analysis" - https://iapp.org/news/a/gaps-in-website-opt-out-functionality-under-the-microscope-in-privacy-enforcement - 2025-12
- [F12] EDPB, "Opinion 08/2024 on consent or pay models" - https://www.edpb.europa.eu/system/files/2024-04/edpb_opinion_202408_consentorpay_en.pdf - 2024-04
- [F13] FTC, "CAN-SPAM Compliance Guide" - https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business - 2023-08 **[Evergreen]**
- [F14] EUR-Lex, "C-252/21 Meta v Bundeskartellamt" - https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:62021CA0252 - 2023-07 **[Evergreen]**
- [F15] IAPP, "Retrospective: 2025 in state privacy law" - https://iapp.org/news/a/retrospective-2025-in-state-data-privacy-law/ - 2025-11

---

### Angle 5+: Regulatory, Compliance, and Deliverability Constraints
> Domain-specific angle: launch plans fail operationally when outreach and analytics controls are treated as legal afterthoughts rather than execution prerequisites.

**Findings:**

Deliverability controls became stricter in 2024 and should be encoded as launch gates. Gmail/Yahoo sender requirements raised the floor for authentication and complaint management. Without these controls, outbound metrics become invalid because delivery quality is unstable [C1][C2].

Consent enforcement has shifted toward implementation verification, not policy text. 2025 California enforcement signals focus on whether user choices propagate to actual tracking/data-sharing behavior. Launch plans that only track "banner present" are no longer sufficient [C3][C4].

"Consent or pay" and related platform consent patterns remain contested and context-dependent in EU guidance. If the launch includes behaviorally targeted acquisition in regulated regions, explicit legal review should be built into pre-launch readiness and weekly post-launch checks [C5][C6].

Email compliance remains an evergreen requirement, but practical risk management must be operationalized with owner/date/status fields, just like product milestones. Compliance controls should be represented as tracked tasks, not static policy notes [C7].

Regulatory drift is now normal. A fixed compliance review at T-30 is insufficient for a 90-day launch window; teams need recurring review cadence and change-triggered backlog updates [C4][C8].

**Sources:**
- [C1] Google Workspace Help, "Email sender guidelines" - https://support.google.com/mail/answer/81126 - 2024-02
- [C2] Yahoo Sender Hub, "Sender Best Practices" - https://senders.yahooinc.com/best-practices - 2024-02
- [C3] California DOJ, CCPA settlement announcement - https://oag.ca.gov/news/press-releases/attorney-general-bonta-announces-largest-ccpa-settlement-date-secures-155 - 2025-07
- [C4] CPPA announcement, GPC privacy sweep - https://cppa.ca.gov/announcements/2025/20250909.html - 2025-09
- [C5] EDPB Opinion 08/2024 - https://www.edpb.europa.eu/system/files/2024-04/edpb_opinion_202408_consentorpay_en.pdf - 2024-04
- [C6] EUR-Lex C-252/21 ruling text - https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:62021CA0252 - 2023-07 **[Evergreen]**
- [C7] FTC CAN-SPAM guide - https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business - 2023-08 **[Evergreen]**
- [C8] IAPP, state privacy law retrospective - https://iapp.org/news/a/retrospective-2025-in-state-data-privacy-law/ - 2025-11

---

## Synthesis

The strongest consensus across angles is that a GTM launch plan in 2026 must behave like an execution operating system, not a campaign checklist. Sources align on complexity growth (more channels, larger stakeholder influence, AI-mediated discovery) and on the need for explicit owner-and-gate discipline [A1][A2][A7].

A second conclusion is that tool availability is not the hard part; interpretation quality is. Organizations can assemble CRM, automation, and analytics stacks quickly, but first-90-day decisions still fail when teams over-trust single metrics, ignore latency/attribution caveats, or do not segment by channel context [T10][D1][D4][D9].

The major contradiction in research is apparent team-size and process tension: broad buying influence remains real, but active decision cells can be smaller and faster. The practical reconciliation is to keep wide stakeholder mapping while assigning single-thread execution ownership per milestone and phase [A2][A6][A7].

Most actionable for `SKILL.md`: force explicit decision logic into the artifact itself. The skill should require launch gates, interpretation guardrails, anti-pattern monitoring, and compliance/deliverability checks as first-class fields, so weak plans become structurally difficult to produce.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.

- [ ] Expand `## Methodology` from phase checklist to decision-gated operating sequence (pre-launch, launch-week, 30/60/90) with explicit scale/hold/stop rules.
- [ ] Add a mandatory launch readiness gate section with commercial-speed, data-readiness, and compliance/deliverability criteria, not only product/payment checks.
- [ ] Add `## Metrics Interpretation Rules` with channel-normalized and stage-level diagnosis logic, including explicit handling for attribution disagreement.
- [ ] Add named anti-pattern warning blocks (pattern, detection signal, consequence, mitigation) so outputs include failure prevention, not just activity planning.
- [ ] Update `## Available Tools` guidance to enforce activation order, artifact-write timing, and conflict-handling behavior.
- [ ] Expand artifact schema with decision evidence, risk register, compliance checks, measurement plan, and decision log fields.
- [ ] Add explicit "no-go" conditions where launch should be delayed despite calendar pressure.

---

## Draft Content for SKILL.md

> This section is paste-ready draft language for the future `SKILL.md` editor.

### Draft: Core Operating Mandate

Use this near the top of `SKILL.md` after the short description.

---
You produce the operational launch plan for the first 90 days after launch: who does what, by when, with what evidence threshold, and what decision happens if outcomes miss target.

A launch plan is invalid if it lacks:
- one named owner per milestone,
- a due date,
- a measurable success signal,
- and a predeclared decision rule (scale, hold, or stop).

You are not writing a wish list. You are writing an execution system under uncertainty. When evidence quality is low, you must lower confidence and tighten scope rather than inflating certainty.
---

### Draft: Methodology

Use this to replace the current methodology section.

---
### Methodology

Before drafting the launch plan, activate upstream strategy documents and extract constraints from each:
- channel priorities and exclusions,
- pilot/pricing constraints,
- MVP validation criteria.

If those inputs conflict, do not silently pick one. Record the conflict in assumptions and continue with reduced confidence.

#### Step 1: Define launch objective and no-go conditions

Write one objective sentence with a measurable 90-day outcome (for example: "Reach 3 paid pilots with onboarding complete by day 90").  
Then define no-go conditions. You must delay launch if any no-go condition is true, regardless of timeline pressure.

Minimum no-go examples:
1. Core job-to-be-done not validated with at least one live user.
2. Payment/invoicing path not operational.
3. No accountable owner for support escalations.
4. Required privacy/compliance controls not active.
5. Outreach deliverability controls (SPF/DKIM/DMARC + unsubscribe handling) not verified.

#### Step 2: Build pre-launch readiness plan (T-30 to T-0)

Create a pre-launch checklist where every item includes owner, due date, status, and proof evidence.

Required readiness categories:
1. **Market and message readiness:** target account/prospect list finalized, positioning approved, objection handling prepared.
2. **Execution readiness:** outreach sequence loaded, calendar blocks scheduled, meeting routing tested, escalation owner defined.
3. **Data readiness:** event tracking validated, dashboard ownership assigned, source-of-truth documented.
4. **Compliance and deliverability readiness:** consent and opt-out flows tested end-to-end; sender authentication and policy checks complete.

Do not mark "ready" based on verbal confirmation. Require objective proof (artifact link, screenshot, QA note, or test record).

#### Step 3: Run launch week as a controlled execution window (T-0 to T+7)

Launch week is not "do everything fast." It is a controlled test of the operating plan.

For each day, define:
- activities by owner,
- expected leading indicators,
- escalation condition if metrics degrade.

Required launch-week motions:
1. first outreach wave to highest-fit accounts,
2. direct network/community announcement (if relevant),
3. daily signal review with one decision owner.

If deliverability or response quality fails hard thresholds, execute mitigation before increasing volume.

#### Step 4: Manage day 0-30 for evidence quality, not vanity velocity

Focus on leading indicators and stage progression:
- qualified responses,
- meetings booked,
- proposal progression,
- onboarding starts.

Do not overreact to opens alone. Prefer click, reply, and downstream progression signals for early decisions.

At day 30, choose one decision:
1. **Scale:** if leading indicators and economics pass thresholds.
2. **Hold and iterate:** if engagement quality is mixed but improving.
3. **Pause and redesign:** if both engagement quality and progression fail with no positive trend.

#### Step 5: Manage day 30-60 for conversion reliability

Shift focus from activity counts to conversion quality:
- discovery-to-proposal rate,
- proposal-to-pilot rate,
- pilot onboarding completion.

Diagnose by stage. If one stage leaks, fix that stage first (handoff, offer, qualification, onboarding) before changing the full launch strategy.

#### Step 6: Manage day 60-90 for repeatability and economics

By day 90, evaluate whether the launch motion is repeatable:
- multiple pilots running in parallel,
- onboarding reliability,
- early payback or efficiency signal trend,
- clear evidence on which channels and messages produce durable progression.

Only scale budget/volume when repeatability and evidence quality are both acceptable.

#### Step 7: Weekly operating cadence (mandatory)

Run a weekly 30-minute launch review with fixed agenda:
1. status by phase and owner,
2. top risks and blocker status,
3. metric trend and interpretation caveats,
4. decision log updates,
5. next-week changes.

If a decision is made, log rationale and evidence refs in the artifact.

Do NOT:
- assign milestones to teams without one named person,
- treat launch-day completion as success,
- report only blended metrics without stage/channel breakdown,
- continue outreach scale if deliverability or compliance gates fail.
---

### Draft: Launch Day Blockers (Pre-flight Checklist)

Use this to replace and expand the existing blocker checklist.

---
### Launch day blockers (hard gates)
Must be complete before any scaled outreach:

- [ ] Core product delivers primary user job in live use
- [ ] Payment/invoicing flow tested end-to-end
- [ ] Support SLA and escalation owner documented
- [ ] Privacy/data handling controls reviewed and signed off
- [ ] Consent/opt-out flow tested from UI to downstream systems
- [ ] Sender authentication configured (SPF/DKIM/DMARC) and verified
- [ ] Unsubscribe and complaint-handling flow tested
- [ ] Launch dashboard owner assigned with source-of-truth documented
- [ ] Meeting routing and scheduling path tested
- [ ] Legal/security/procurement packet prepared for likely objections

If any blocker is unresolved, launch status is `delayed` and outreach scale must not proceed.
---

### Draft: Metrics Interpretation Rules

Add this as a standalone section before Recording.

---
### Metrics interpretation rules (30/60/90)

You must interpret launch metrics by signal quality tier:

1. **Directional leading indicators:** opens, clicks, replies, early traffic shifts.  
2. **Operational progression indicators:** meetings booked, proposals sent, pilots signed, onboarding starts.  
3. **Economic indicators:** CAC trend, payback trend, channel efficiency by cohort.

Rules:
- Do not use a single metric as launch verdict.
- If open-rate and click/reply trends conflict, prioritize click/reply and downstream progression.
- If blended conversion drops, inspect channel mix before declaring strategy failure.
- If attribution tools disagree, reduce decision confidence and require triangulation before large reallocation.
- If lagging outcomes are delayed but leading indicators improve within expected incubation windows, extend observation before full reset.

Decision rubric:
- **Scale** when indicator tiers 2 and 3 trend positive with acceptable confidence.
- **Hold** when tier-1 is positive but tier-2/3 evidence is not yet stable.
- **Stop/Pivot** when tier-2/3 remain negative for consecutive windows and mitigation fails.
---

### Draft: Anti-Pattern Warnings

Use these warning blocks as mandatory output components.

---
#### Warning: Budget-Agnostic Launch Plan
**What it looks like:** Channel tasks and spend exist, but no efficiency guardrails or stop rules.  
**Detection signal:** Missing CAC/payback thresholds and no weekly budget decision logic.  
**Consequence:** Reactive cuts and plan instability mid-cycle.  
**Mitigation:** Add channel-level guardrails and explicit stop/scale triggers before execution.

#### Warning: Activity Theater
**What it looks like:** Plan optimizes outreach volume and impressions only.  
**Detection signal:** No linkage from activity to qualified progression milestones.  
**Consequence:** High activity, weak conversion, false success narratives.  
**Mitigation:** Re-anchor to stage progression and value outcomes.

#### Warning: Deliverability Blindness
**What it looks like:** Outreach scale starts without sender/authentication checks.  
**Detection signal:** Missing SPF/DKIM/DMARC verification and unsubscribe QA.  
**Consequence:** Spam placement and incorrect messaging-quality diagnosis.  
**Mitigation:** Treat deliverability as hard launch gate; block scale until complete.

#### Warning: Consent Theater
**What it looks like:** Consent UI present, but backend tracking/sharing unchanged.  
**Detection signal:** Network/telemetry shows continued data flow after opt-out.  
**Consequence:** Regulatory risk and forced remediation during launch window.  
**Mitigation:** Add recurring consent propagation audits and owner accountability.

#### Warning: Single-Threaded Execution
**What it looks like:** Milestones assigned to groups or no accountable person.  
**Detection signal:** Blockers persist with no clear escalation path.  
**Consequence:** Delays and unresolved dependencies.  
**Mitigation:** One accountable person per milestone plus escalation owner.

#### Warning: Premature Strategy Reset
**What it looks like:** Full GTM pivot after short noisy windows.  
**Detection signal:** No incubation/lag consideration in decision rationale.  
**Consequence:** Abandons potentially viable motion before signal matures.  
**Mitigation:** Use tiered metric rules and minimum observation windows.
---

### Draft: Available Tools

Use this to update the tools guidance text.

---
### Available Tools

Before planning execution, activate prerequisite strategy documents:

```python
flexus_policy_document(op="activate", args={"p": "/strategy/gtm-channel-strategy"})
flexus_policy_document(op="activate", args={"p": "/strategy/pricing-pilot-packaging"})
flexus_policy_document(op="activate", args={"p": "/strategy/mvp-validation-criteria"})
```

Use calendar scheduling for launch milestones and named-owner reminders:

```python
google_calendar(
  op="call",
  args={
    "method_id": "google_calendar.events.insert.v1",
    "calendarId": "primary",
    "summary": "GTM Launch Milestone",
    "start": {"date": "2026-03-15"}
  }
)
```

Persist the final plan only after all required schema fields are complete:

```python
write_artifact(
  artifact_type="gtm_launch_plan",
  path="/strategy/gtm-launch-plan",
  data={...}
)
```

Tool usage rules:
- Do not write artifact before blockers and metrics sections are complete.
- If source documents conflict, record assumptions and lower confidence.
- Never omit owner/date fields to "move faster."
---

### Draft: Recording

Use this to replace the current short recording section.

---
### Recording

Your artifact must be executable by another operator without hidden context. Record:

1. launch objective and no-go conditions,
2. pre-launch checklist with proof evidence,
3. phase plan with milestones, owners, dependencies, and exit criteria,
4. success metrics with leading/lagging types and decision thresholds,
5. measurement caveats and interpretation confidence,
6. risk register with mitigations and owner,
7. compliance/deliverability checks and status,
8. decision log entries for every scale/hold/stop choice.

A launch plan is incomplete if it only lists activities and dates without decision logic.
---

### Draft: Schema additions

Use this JSON Schema fragment to replace the current artifact schema.

```json
{
  "gtm_launch_plan": {
    "type": "object",
    "description": "Operational GTM launch plan for first 90 days with owners, milestones, evidence, risks, and decision logic.",
    "required": [
      "created_at",
      "launch_date",
      "launch_objective",
      "assumptions",
      "no_go_conditions",
      "pre_launch_checklist",
      "phases",
      "success_metrics",
      "measurement_plan",
      "risk_register",
      "compliance_checks",
      "communication_plan",
      "decision_log"
    ],
    "additionalProperties": false,
    "properties": {
      "created_at": {
        "type": "string",
        "format": "date-time",
        "description": "ISO-8601 UTC timestamp when the launch plan was generated."
      },
      "launch_date": {
        "type": "string",
        "format": "date",
        "description": "Planned launch date in YYYY-MM-DD."
      },
      "launch_objective": {
        "type": "string",
        "description": "Single measurable 90-day objective statement."
      },
      "assumptions": {
        "type": "array",
        "description": "Critical assumptions used to build this plan.",
        "items": {
          "type": "object",
          "required": ["assumption", "confidence", "evidence_refs"],
          "additionalProperties": false,
          "properties": {
            "assumption": {
              "type": "string",
              "description": "Declarative assumption affecting scope, timeline, or economics."
            },
            "confidence": {
              "type": "string",
              "enum": ["low", "medium", "high"],
              "description": "Confidence level for this assumption."
            },
            "evidence_refs": {
              "type": "array",
              "description": "References to source docs, dashboards, or research IDs.",
              "items": {
                "type": "string"
              }
            }
          }
        }
      },
      "no_go_conditions": {
        "type": "array",
        "description": "Conditions that force launch delay if unresolved.",
        "items": {
          "type": "object",
          "required": ["condition", "status", "owner"],
          "additionalProperties": false,
          "properties": {
            "condition": {
              "type": "string",
              "description": "Hard gate condition (for example deliverability ready, compliance check complete)."
            },
            "status": {
              "type": "string",
              "enum": ["pass", "fail", "unknown"],
              "description": "Current state of this no-go condition."
            },
            "owner": {
              "type": "string",
              "description": "Person accountable for resolving this condition."
            }
          }
        }
      },
      "pre_launch_checklist": {
        "type": "array",
        "description": "T-30 to T-0 readiness checklist.",
        "items": {
          "type": "object",
          "required": ["item", "owner", "due_date", "status", "evidence"],
          "additionalProperties": false,
          "properties": {
            "item": {
              "type": "string",
              "description": "Specific readiness task."
            },
            "owner": {
              "type": "string",
              "description": "Single accountable person."
            },
            "due_date": {
              "type": "string",
              "format": "date",
              "description": "Due date in YYYY-MM-DD."
            },
            "status": {
              "type": "string",
              "enum": ["done", "in_progress", "blocked", "not_started"],
              "description": "Current status of the checklist item."
            },
            "evidence": {
              "type": "string",
              "description": "Proof artifact reference (doc link, test note, QA record, or screenshot path)."
            }
          }
        }
      },
      "phases": {
        "type": "array",
        "description": "Execution phases from pre-launch through day 90.",
        "items": {
          "type": "object",
          "required": ["phase_name", "start_day", "end_day", "owner", "milestones", "exit_criteria"],
          "additionalProperties": false,
          "properties": {
            "phase_name": {
              "type": "string",
              "enum": ["pre_launch", "launch_week", "day_0_30", "day_30_60", "day_60_90"],
              "description": "Canonical phase identifier."
            },
            "start_day": {
              "type": "integer",
              "description": "Relative day offset from launch date."
            },
            "end_day": {
              "type": "integer",
              "description": "Relative day offset from launch date."
            },
            "owner": {
              "type": "string",
              "description": "Phase owner accountable for delivery and reporting."
            },
            "milestones": {
              "type": "array",
              "description": "Milestones for this phase.",
              "items": {
                "type": "object",
                "required": ["milestone_id", "milestone", "owner", "due_day", "status", "success_metric", "target"],
                "additionalProperties": false,
                "properties": {
                  "milestone_id": {
                    "type": "string",
                    "description": "Unique milestone identifier used for dependency references."
                  },
                  "milestone": {
                    "type": "string",
                    "description": "Milestone description."
                  },
                  "owner": {
                    "type": "string",
                    "description": "Single accountable owner."
                  },
                  "due_day": {
                    "type": "integer",
                    "description": "Relative day offset when milestone is due."
                  },
                  "status": {
                    "type": "string",
                    "enum": ["done", "in_progress", "blocked", "not_started"],
                    "description": "Milestone status."
                  },
                  "success_metric": {
                    "type": "string",
                    "description": "Metric used to evaluate milestone completion quality."
                  },
                  "target": {
                    "type": "string",
                    "description": "Target value/range for success metric."
                  },
                  "dependency_ids": {
                    "type": "array",
                    "description": "IDs of milestones that must complete first.",
                    "items": {
                      "type": "string"
                    }
                  }
                }
              }
            },
            "exit_criteria": {
              "type": "array",
              "description": "Conditions required to move to next phase.",
              "items": {
                "type": "string"
              }
            }
          }
        }
      },
      "success_metrics": {
        "type": "array",
        "description": "Core launch metrics with targets by horizon and decision threshold.",
        "items": {
          "type": "object",
          "required": [
            "metric",
            "metric_type",
            "data_source",
            "baseline",
            "target_30d",
            "target_60d",
            "target_90d",
            "decision_threshold"
          ],
          "additionalProperties": false,
          "properties": {
            "metric": {
              "type": "string",
              "description": "Metric name."
            },
            "metric_type": {
              "type": "string",
              "enum": ["leading", "lagging", "economic", "quality"],
              "description": "Signal tier for interpretation."
            },
            "data_source": {
              "type": "string",
              "description": "System of record for this metric."
            },
            "baseline": {
              "type": "string",
              "description": "Baseline value before launch execution."
            },
            "target_30d": {
              "type": "string",
              "description": "Target by day 30."
            },
            "target_60d": {
              "type": "string",
              "description": "Target by day 60."
            },
            "target_90d": {
              "type": "string",
              "description": "Target by day 90."
            },
            "decision_threshold": {
              "type": "string",
              "description": "Threshold that triggers scale/hold/stop action."
            }
          }
        }
      },
      "measurement_plan": {
        "type": "object",
        "description": "How launch data is collected, interpreted, and caveated.",
        "required": ["source_of_truth", "dashboard_cadence", "interpretation_rules", "attribution_note", "data_latency_expectation"],
        "additionalProperties": false,
        "properties": {
          "source_of_truth": {
            "type": "string",
            "description": "Primary reporting system for decision-making."
          },
          "dashboard_cadence": {
            "type": "string",
            "enum": ["daily", "weekly"],
            "description": "Update cadence for launch dashboard reviews."
          },
          "interpretation_rules": {
            "type": "array",
            "description": "Explicit metric interpretation rules used in reviews.",
            "items": {
              "type": "string"
            }
          },
          "attribution_note": {
            "type": "string",
            "description": "Known attribution caveats and reconciliation rules."
          },
          "data_latency_expectation": {
            "type": "string",
            "description": "Expected freshness/latency limits for key systems."
          }
        }
      },
      "risk_register": {
        "type": "array",
        "description": "Launch risks with owner and mitigation.",
        "items": {
          "type": "object",
          "required": ["risk", "signal", "impact", "mitigation", "owner", "status"],
          "additionalProperties": false,
          "properties": {
            "risk": {
              "type": "string",
              "description": "Named risk."
            },
            "signal": {
              "type": "string",
              "description": "Detection signal that risk is materializing."
            },
            "impact": {
              "type": "string",
              "description": "Business consequence if unresolved."
            },
            "mitigation": {
              "type": "string",
              "description": "Concrete mitigation plan."
            },
            "owner": {
              "type": "string",
              "description": "Person accountable for mitigation."
            },
            "status": {
              "type": "string",
              "enum": ["open", "watching", "mitigating", "resolved"],
              "description": "Current risk status."
            }
          }
        }
      },
      "compliance_checks": {
        "type": "object",
        "description": "Operational compliance and deliverability checks tied to launch readiness.",
        "required": ["privacy_opt_out_flow_verified", "email_sender_auth_verified", "policy_owner", "last_review_date"],
        "additionalProperties": false,
        "properties": {
          "privacy_opt_out_flow_verified": {
            "type": "boolean",
            "description": "Whether opt-out/consent preferences are verified to propagate to downstream systems."
          },
          "email_sender_auth_verified": {
            "type": "boolean",
            "description": "Whether sender authentication setup has been verified."
          },
          "policy_owner": {
            "type": "string",
            "description": "Accountable owner for compliance checks."
          },
          "last_review_date": {
            "type": "string",
            "format": "date",
            "description": "Most recent compliance review date."
          }
        }
      },
      "communication_plan": {
        "type": "object",
        "description": "Cadence and audience for launch communication.",
        "required": ["internal_cadence", "stakeholders", "update_format"],
        "additionalProperties": false,
        "properties": {
          "internal_cadence": {
            "type": "string",
            "enum": ["daily_launch_week", "weekly"],
            "description": "Primary internal update cadence."
          },
          "stakeholders": {
            "type": "array",
            "description": "Stakeholders who receive updates.",
            "items": {
              "type": "string"
            }
          },
          "update_format": {
            "type": "string",
            "description": "Format for recurring launch updates."
          }
        }
      },
      "decision_log": {
        "type": "array",
        "description": "Chronological record of major launch decisions.",
        "items": {
          "type": "object",
          "required": ["date", "decision", "rationale", "confidence_after", "next_review_date"],
          "additionalProperties": false,
          "properties": {
            "date": {
              "type": "string",
              "format": "date",
              "description": "Decision date."
            },
            "decision": {
              "type": "string",
              "enum": ["scale", "hold", "pause", "pivot", "delay_launch"],
              "description": "Decision type."
            },
            "rationale": {
              "type": "string",
              "description": "Evidence-backed reason for the decision."
            },
            "confidence_after": {
              "type": "string",
              "enum": ["low", "medium", "high"],
              "description": "Confidence level after decision."
            },
            "evidence_refs": {
              "type": "array",
              "description": "References to metrics, docs, or notes supporting the decision.",
              "items": {
                "type": "string"
              }
            },
            "next_review_date": {
              "type": "string",
              "format": "date",
              "description": "Date for decision re-evaluation."
            }
          }
        }
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Public benchmark ranges for launch metrics vary heavily by industry, ACV, and channel mix; hard universal thresholds remain weak and should be treated as directional.
- Some evidence in failure-mode research comes from vendor reports or operator postmortems rather than controlled comparative studies; these are useful for risk patterning but should be marked medium confidence.
- Public API limit details are uneven across tools and sometimes plan/account dependent; implementation must verify account-specific limits before automation-heavy launch workflows.
- We did not find one cross-vendor standard taxonomy for "qualified launch success" that spans all B2B/B2C contexts; the skill should require explicit metric definitions in every artifact.
- Regulatory expectations continue to shift at jurisdiction level; monthly compliance review cadence is recommended, but exact scope must be tailored to launch geography and data flows.
