# Research: gtm-channel-strategy

**Skill path:** `strategist/skills/gtm-channel-strategy/`
**Bot:** strategist (researcher | strategist | executor)
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`gtm-channel-strategy` defines how the strategist bot should select and sequence channels based on ICP fit, stage, offer complexity, and CAC guardrails. The current `SKILL.md` has a solid backbone (fewer channels done well, stage-based sequencing, CAC formula), but it under-specifies modern 2024-2026 realities: pre-contact buyer behavior, buying-group complexity, causal measurement requirements, and recurring attribution failure modes.

This research expands the skill so future outputs are not only "plausible strategy" but operationally testable strategy: explicit channel hypotheses, scale gates, measurement standards, and anti-pattern detection criteria. Primary users are founders, GTM leaders, and strategy operators who need a practical, low-noise channel plan tied to unit economics and decision quality.

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
- Findings volume 800-4000 words: **passed** (within target range)

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

Modern B2B channel strategy is no longer "channel first, funnel later"; it is "buyer process first, channel sequence second." 6sense's 2024 buyer research indicates buyers are typically deep into evaluation before contacting sales, and many have already formed a vendor preference before first live interaction. That changes channel methodology: content, social proof, and category framing become pre-contact influence systems, while outbound and sales conversations are conversion accelerators in validation, not primary discovery engines [A1][A2].

Practitioners increasingly split execution into two operating zones: **Selection** (problem framing, shortlist creation, confidence-building) and **Validation** (risk reduction, implementation proof, commercial closure). The practical implication is channel-role clarity: thought leadership, SEO, communities, and targeted paid reach support Selection; demos, technical proof, references, and coordinated outbound support Validation [A2][A3].

Buying groups are larger and deals stall more often than many stage playbooks assume. Forrester and 6sense both report multi-stakeholder behavior as normal, with common deal stalls. Channel plans that stay single-threaded at the contact level degrade late-stage conversion because they fail the internal consensus process. A robust methodology therefore requires role-based messaging and channel touches across economic, technical, and user stakeholders [A1][A3].

Stage-gated sequencing remains best practice, but with a stronger efficiency overlay in 2024-2026. KeyBanc and ICONIQ data suggest teams remain efficiency-sensitive even as growth expectations recover. In practice: early stage teams should still prioritize high-learning channels (founder outbound, niche community, tightly scoped content), but scaling decisions must clear explicit payback and LTV:CAC gates before budget expansion [A4][A5].

Growth-stage teams should model channel portfolio shifts across net-new and expansion motions. ICONIQ's findings suggest expansion contribution can become relatively more important at scale; however, over-indexing on expansion can hide a weakening net-new engine. The recommended method is dual cadence: one channel operating rhythm for new-logo acquisition and a parallel one for expansion/retention [A5].

Channel motion should be selected by deal complexity and ACV, not team preference. Winning by Design's Bowtie framing remains useful in 2024 because it forces explicit operating motion choices (no-touch to dedicated-touch) and avoids the common anti-pattern of using one blended funnel for materially different sales motions [A6].

There is a real tension between "buyers self-direct before sales" and "phone/outbound still contributes strongly." Sales-development benchmarks show phone and outbound still matter; the contradiction resolves when outbound is used as precision conversion and multi-threading support after intent signals emerge, rather than high-volume interruption as a standalone demand engine [A1][A7].

Older but still relevant long-horizon demand guidance (95-5 principle) remains directionally useful in 2024-2026 because pre-contact preference formation has increased, not declined. Marked Evergreen due source age and publication context [A10].

**Sources:**
- [A1] 6sense 2024 Buyer Experience press release (Business Wire, 2024): https://www.businesswire.com/news/home/20241009142556/en/6sense-Launches-2024-Buyer-Experience-Report-Unveiling-Global-B2B-Buyer-Trends
- [A2] 6sense 2024 Buyer Experience Report landing page (2024): https://6sense.com/resources/buyer-experience-report/2024-b2b-buyer-experience-report
- [A3] Forrester, State of Business Buying (2024): https://www.forrester.com/blogs/state-of-business-buying-2024/
- [A4] KeyBanc + Sapphire Ventures private SaaS survey (2024): https://investor.key.com/press-releases/news-details/2024/PRIVATE-SAAS-COMPANY-SURVEY-REVEALS-SHIFT-TOWARDS-FUTURE-GROWTH-WITH-A-CONTINUED-FOCUS-ON-OPERATIONAL-EFFICIENCY-AND-PROFITABILITY/default.aspx
- [A5] ICONIQ Growth, Growth + Efficiency report (2024 PDF): https://cdn.prod.website-files.com/65e1d7fb19a3e64b5c36fb38/66db8652044a89416a0c78b6_ICONIQ%20Growth%20%2B%20Insights%20-%20Growth%20%26%20Efficiency%202024.pdf
- [A6] Winning by Design, Bowtie Proposed Standard (2024 PDF): https://winningbydesign.com/wp-content/uploads/2024/05/The-Bowtie-A-Proposed-Standard.pdf
- [A7] Orum, State of Sales Development (2024 PDF): https://8348499.fs1.hubspotusercontent-na1.net/hubfs/8348499/PDFs/State%20of%20Sales%20Report%202024%20-%20FINAL.pdf
- [A8] High Alpha + OpenView SaaS Benchmarks (2024): https://highalpha.com/saas-benchmarks/2024
- [A9] ChartMogul H1 2024 SaaS growth analysis (2024): https://chartmogul.com/blog/saas-growth-remains-slow-throughout-h1-2024
- [A10] LinkedIn B2B Institute 95-5 rule (Evergreen): https://www.linkedin.com/business/marketing/blog/research-and-insights/why-you-should-follow-the-95-5-rule

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

For channel strategy quality, the tool stack matters less by logo and more by **quota shape + interoperability + cost predictability**. Ad and analytics APIs are constrained by token/score/quota systems that can silently bias reporting freshness and test cadence if not designed correctly.

For paid media APIs, Google Ads, Meta Marketing API, and LinkedIn Marketing API remain core. Google Ads API has explicit operation quotas and mutate caps; Meta combines point-based throttling with mutation QPS constraints; LinkedIn enforces member/app daily limits and requires limit monitoring in its developer portal. Practical implication: channel reporting jobs must be quota-aware with batching and backoff, not naive high-frequency polling [T1][T2][T3].

Attribution and conversion quality increasingly depend on measurement plumbing details. GA4 Data API token budgets can become a bottleneck for complex multi-dimensional reporting, and GA4 BigQuery export has different constraints for daily batch versus streaming workflows. Meta CAPI deduplication (`event_name` + `event_id`) is now table stakes for client/server hybrid conversion capture. UTM taxonomy discipline remains fundamental and still frequently broken in practice [T4][T5][T6][T7].

SEO and content-intelligence providers show major cost-structure differences. Semrush's API unit model can become expensive for broad pulls, while SerpAPI's public throughput-pricing transparency supports easier cost forecasting. For enrichment and prospecting, Hunter exposes both rate limits and transparent credit pricing; Apollo offers useful API capability but public numeric limit transparency is more limited and plan-specific, so implementation assumptions should be marked uncertain until verified per account [T8][T9][T10][T11][T12][T23][T24].

Lifecycle and outbound execution tooling remains split across email delivery, orchestration, and enrichment. Mailchimp API has concurrency/time-out constraints that matter for sync architecture; SendGrid exposes endpoint-specific rate behavior and announced tighter activity endpoint limits in late 2025; both require queueing/backoff patterns for stable ingestion. Zapier and Make are useful for low-code orchestration but have different billing mechanics (task-based vs credit/module-based) that directly affect total cost under multi-step workflows [T13][T14][T15][T16][T17][T18][T19].

Warehouse-first activation is now a de-facto standard for teams above basic maturity. Hightouch, Fivetran, and Segment reinforce a common pattern: warehouse for modeling and identity resolution, then sync to execution endpoints. This pattern improves consistency across channels but introduces new cost surfaces (active sync limits, MAR, MTU/throughput effects) that should be included in channel strategy assumptions [T20][T21][T22].

De-facto interoperability standards seen across sources:
1) CRM as operational system of record, warehouse as analytical model layer.
2) Mandatory UTM and campaign taxonomy governance.
3) Dual-path conversion capture (browser + server-side where applicable).
4) Rate-limit-aware extraction and sync design from day one [T3][T7][T20][T21][T22].

**Sources:**
- [T1] Google Ads API quotas: https://developers.google.com/google-ads/api/docs/best-practices/quotas
- [T2] Meta Marketing API rate limits: https://developers.facebook.com/docs/marketing-api/overview/rate-limiting/
- [T3] LinkedIn Marketing API rate limits (updated 2025-08-20): https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits
- [T4] GA4 Data API quotas: https://developers.google.com/analytics/devguides/reporting/data/v1/quotas
- [T5] GA4 BigQuery export limits: https://support.google.com/analytics/answer/9823238
- [T6] Meta CAPI deduplication docs: https://developers.facebook.com/docs/marketing-api/conversions-api/deduplicate-pixel-and-server-events
- [T7] Google Analytics UTM guidance: https://support.google.com/analytics/answer/10917952
- [T8] Semrush API basics (updated 2026-02-10): https://developer.semrush.com/api/basics/how-to-get-api/
- [T9] Semrush API units and cost behavior: https://developer.semrush.com/api/basics/api-units-balance
- [T10] SerpAPI pricing: https://serpapi.com/pricing
- [T11] Hunter API docs: https://hunter.io/api/docs
- [T12] Hunter pricing: https://hunter.io/pricing
- [T13] Twilio SendGrid API rate limits: https://www.twilio.com/docs/sendgrid/api-reference/how-to-use-the-sendgrid-v3-api/rate-limits
- [T14] SendGrid pricing: https://sendgrid.com/en-us/pricing
- [T15] SendGrid Email Activity rate-limit change (2025): https://www.twilio.com/en-us/changelog/rate-limit-change-for-the-twilio-sendgrid-email-activity-api
- [T16] Mailchimp Marketing API fundamentals: https://mailchimp.com/developer/marketing/docs/fundamentals/
- [T17] Mailchimp pricing plans: https://mailchimp.com/help/about-mailchimp-pricing-plans/
- [T18] Zapier pricing: https://zapier.com/pricing/
- [T19] Make pricing: https://www.make.com/en/pricing
- [T20] Hightouch self-serve pricing (2025): https://hightouch.com/docs/pricing/ss-pricing
- [T21] Fivetran pricing and billing docs (2025): https://fivetran.com/docs/usage-based-pricing/billing-and-plans
- [T22] Segment MTU and throughput billing model: https://segment.com/docs/guides/usage-and-billing/mtus-and-throughput/
- [T23] Apollo API rate limits docs: https://docs.apollo.io/reference/rate-limits
- [T24] Apollo pricing page: https://www.apollo.io/pricing

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

The strongest 2025 interpretation pattern is **triangulation**, not metric absolutism. Google's Meridian launch and related documentation explicitly position MMM, attribution, and incrementality as complementary methods. Attribution is best for directional, tactical optimization. Incrementality answers causal lift for specific interventions. MMM helps budget allocation with external controls and lag effects. Treating one method as complete truth is now an avoidable error [D1][D2][D3][D4][D5][D6].

Incrementality has become more accessible, with Google indicating lower spend barriers than historical assumptions for some test setups. This does not remove sample-size and variance constraints, but it means channel strategies should include explicit "when we start causal tests" gates instead of delaying experimentation until very large budgets [D2].

Efficiency interpretation should be stage- and ACV-aware. Benchmarkit reports median New CAC Ratio around $2.00 S&M per $1.00 new ARR in 2024 data, with materially worse lower quartiles. This supports hard caution thresholds, but not blind universalization; segment context still matters [D7].

Payback and LTV:CAC remain useful but are routinely misused. Recent finance guidance keeps 3:1 LTV:CAC and shorter payback as directional goals, while acknowledging these are not laws and can be distorted in early-stage or land-and-expand models. Therefore, channel decisions should combine payback, retention/NRR signals, and cohort maturity, rather than single-ratio gating [D8][D9][D10].

Down-funnel conversion quality by channel is more decision-useful than top-funnel volume. HockeyStack benchmark snapshots show channel differences can be large between MQL-stage and SQL/closed-won performance. Teams that optimize to MQL volume frequently overfund channels that look active but underperform in revenue creation [D11][D12].

External ad benchmarks remain broad directional checks, not direct targets. WordStream's 2024 cross-industry benchmarks show large CVR variance between industries and increasing CPL pressure, reinforcing the need to benchmark within vertical + intent class rather than against single global averages [D13].

Signal-vs-noise controls that should be explicit in the skill:
- seasonality and trend controls,
- lag/carryover (adstock),
- cohort maturity windows,
- channel interaction effects,
- minimum-power test design before winner/loser calls [D4][D5][D11][D12][D14][D16][D17].

Common misinterpretations observed across sources:
1) "Attributed ROAS equals incrementality." It does not [D1][D2][D6].
2) "One quarter is enough to call channel trend." Often false due lag and seasonality [D4][D5][D11].
3) "3:1 LTV:CAC means strategy is healthy." Not without retention and cash timing [D8][D9].
4) "Non-significant tests prove no effect." Often underpowered design [D14][D16][D17].
5) "MQL growth means channel quality." Must validate down-funnel conversion and revenue [D11][D12].

**Sources:**
- [D1] Google Meridian launch (2025): https://blog.google/products/ads-commerce/meridian-marketing-mix-model-open-to-everyone/
- [D2] Google Ads incrementality improvements (2025): https://support.google.com/google-ads/answer/16719772
- [D3] Meridian ROI priors and calibration: https://developers.google.com/meridian/docs/advanced-modeling/roi-priors-and-calibration
- [D4] Meridian model specification: https://developers.google.com/meridian/docs/advanced-modeling/model-spec
- [D5] Meridian media saturation and lagging: https://developers.google.com/meridian/docs/advanced-modeling/media-saturation-lagging
- [D6] Meridian paid search modeling and confounders: https://developers.google.com/meridian/docs/advanced-modeling/paid-search-modeling
- [D7] Benchmarkit SaaS benchmarks (2025): https://benchmarkit.ai/2025benchmarks
- [D8] Drivetrain CAC payback guidance (published 2024, updated 2025): https://www.drivetrain.ai/strategic-finance-glossary/cac-payback-period-formula-benchmarks-and-how-to-reduce-it
- [D9] Burkland LTV:CAC interpretation (2024): https://burklandassociates.com/2024/01/02/ltvcac-an-important-but-often-misunderstood-saas-metric/
- [D10] ForEntrepreneurs SaaS Metrics 2.0 definitions (Evergreen): https://www.forentrepreneurs.com/saas-metrics-2-definitions-2/
- [D11] HockeyStack Q1 2024 recap benchmarks: https://www.hockeystack.com/labs/q1-2024-recap-benchmarks
- [D12] HockeyStack Q2 2024 recap benchmarks: https://www.hockeystack.com/lab-blog-posts/q2-2024-recap-benchmarks
- [D13] WordStream Google Ads benchmarks 2024: https://www.wordstream.com/blog/2024-google-ads-benchmarks
- [D14] Statsig power analysis docs: https://docs.statsig.com/experiments-plus/power-analysis
- [D15] Statsig sample size calculator: https://statsig.com/calculator
- [D16] Optimizely power analysis pitfalls (2025): https://www.optimizely.com/insights/blog/power-analysis-in-fixed-horizon-frequentist-ab-tests/
- [D17] Optimizely sample-size tradeoffs (2025): https://www.optimizely.com/insights/blog/sample-size-calculations-for-experiments/

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

The highest-frequency failure mode is still **lead-volume theater**: channel plans optimize for form fills and MQL counts while ignoring account-level buying signals and downstream conversion quality. This is especially costly in current B2B buying environments where buyers self-educate heavily before direct contact [F1][F2][F5].

A second recurring failure is **single-threaded opportunity management** in multi-stakeholder deals. Plans that do not encode buying-group depth and role-specific engagement are structurally fragile, regardless of channel mix. This tends to show up as "mysterious late-stage stalls" [F1][F2][F3].

A third failure is **motion sprawl**: simultaneously running inbound, outbound, ABM, paid, and partnerships without one orchestration owner, explicit handoffs, or stage exit criteria. Teams interpret poor performance as "channel mismatch" when the root cause is operating model fragmentation [F3].

Attribution illusions are a major anti-pattern cluster:
- blended brand + non-brand paid search reports hide weak non-brand economics,
- retargeting/display touches get over-credited in last-touch models,
- branded paid search can cannibalize organic demand while still looking efficient in platform ROAS [F7][F8][F9][F10][F11].

Partnership motions introduce additional failure modes when scaled before attribution and conflict governance are mature. PartnerStack and channel reports indicate attribution maturity varies widely and channel conflict remains common when deal registration and compensation rules are under-specified [F12][F13][F14][F15].

High-value anti-patterns to encode in SKILL outputs:
1) Form-volume trap.
2) Single-threaded selling.
3) Motion sprawl without orchestration.
4) Blended search reporting.
5) Underpowered channel experiments.
6) Partner channel scaling without conflict governance.

Each should include a detection signal, consequence, and mitigation in the artifact to force practical risk handling (not only strategic aspiration).

**Sources:**
- [F1] 6sense Buyer Experience report release (2024): https://www.businesswire.com/news/home/20241009142556/en/6sense-Launches-2024-Buyer-Experience-Report-Unveiling-Global-B2B-Buyer-Trends
- [F2] 6sense Buyer Identification Benchmark (2024): https://6sense.com/research/b2b-buyer-identification-benchmark/
- [F3] LeanData State of GTM Efficiency report (2024 PDF): https://www.leandata.com/wp-content/uploads/2024/06/LeanData-The-2024-State-GTM-Efficiency-Report.pdf
- [F4] Pipeline360 alignment survey release (2024): https://www.prweb.com/releases/pipeline360-survey-finds-sales-marketing-alignment-and-branded-demand-increase-b2b-marketing-goal-achievement-by-60-302269723.html
- [F5] MarketingCharts summary of Pipeline360/Demand Metric findings (2024): https://www.marketingcharts.com/customer-centric/lead-generation-and-management-234412
- [F6] Dreamdata GTM benchmarks (2024): https://dreamdata.io/blog/b2b-go-to-market-benchmarks-2024
- [F7] Dreamdata branded vs non-branded search in B2B (2024): https://dreamdata.io/blog/branded-vs-non-branded-google-search-ads-b2b
- [F8] HockeyStack self-reported attribution report (2024): https://www.hockeystack.com/lab-blog-posts/hockeystacks-sra-report-2024
- [F9] More Than Media branded-search incrementality case (2025): https://www.morethanmediamarketing.com/p/case-study-branded-search-incrementality-test
- [F10] LiftLab branded search geo-experiment case: https://liftlab.com/case-studies/saas-company-experiments-with-google-branded-search/
- [F11] Seer Interactive branded-search cannibalization (2025): https://www.seerinteractive.com/insights/are-you-cannibalizing-your-own-branded-search
- [F12] PartnerStack State of Partnerships in GTM (2026): https://partnerstack.com/resources/research-lab/the-state-of-partnerships-in-gtm-2026
- [F13] PartnerStack chart: partner attribution methods (2025): https://partnerstack.com/resources/research-lab/charts/multi-touch-is-the-most-common-partner-tribution-method-for-senior-leaders-in-b2b-saas
- [F14] PartnerStack chart: partnership alignment and cycle speed (2025): https://partnerstack.com/resources/research-lab/charts/partnerships-lead-to-higher-average-contracts-through-larger-initial-deals-upsells-and-renewels
- [F15] Channelnomics channel conflict analysis (2024): https://www.channelnomics.com/insights/the-changing-face-of-channel-conflict

---

### Angle 5+: Measurement Architecture & Operating Cadence
> Domain-specific angle: how to turn channel strategy into a repeatable operating system with governance, not a one-time memo.

**Findings:**

Strong channel strategy artifacts increasingly include a **measurement architecture decision** as part of the strategy itself, not as downstream analytics work. Sources across Google Meridian docs and GTM efficiency reports indicate this shift is necessary to avoid strategy drift and untestable channel choices [D1][D2][D4][F3].

The most robust pattern is a three-layer measurement stack:
1) Attribution for day-to-day tactical optimization.
2) Incrementality tests for causal validation of material channel spend.
3) MMM or MMM-like periodic budget calibration for medium-term allocation [D1][D2][D3][D6].

Operational cadence matters as much as model choice. Teams benefit from fixed review windows (for example, biweekly tactical and monthly strategic reviews) with predefined scale/hold/exit gates per channel. This avoids overreacting to noisy short windows and aligns with lag and cohort maturity caveats documented in measurement sources [D5][D11][D12][D16].

Strategy artifacts should encode data hygiene requirements (UTM naming, brand/non-brand split, event deduplication approach), because these details directly determine whether channel comparisons are trustworthy [T6][T7][F7].

A final pattern is explicit uncertainty tracking: assumptions should carry confidence levels and evidence references. This prevents false precision when source quality is mixed (e.g., vendor benchmarks, account-specific API limits) and improves decision hygiene across future strategy revisions [T23][T24][F8][F10].

**Sources:**
- [D1] Google Meridian launch (2025): https://blog.google/products/ads-commerce/meridian-marketing-mix-model-open-to-everyone/
- [D2] Google Ads incrementality updates (2025): https://support.google.com/google-ads/answer/16719772
- [D3] Meridian ROI calibration docs: https://developers.google.com/meridian/docs/advanced-modeling/roi-priors-and-calibration
- [D4] Meridian model spec docs: https://developers.google.com/meridian/docs/advanced-modeling/model-spec
- [D5] Meridian lagging docs: https://developers.google.com/meridian/docs/advanced-modeling/media-saturation-lagging
- [D6] Meridian paid-search modeling docs: https://developers.google.com/meridian/docs/advanced-modeling/paid-search-modeling
- [D11] HockeyStack Q1 benchmarks (2024): https://www.hockeystack.com/labs/q1-2024-recap-benchmarks
- [D12] HockeyStack Q2 benchmarks (2024): https://www.hockeystack.com/lab-blog-posts/q2-2024-recap-benchmarks
- [F3] LeanData GTM efficiency report (2024): https://www.leandata.com/wp-content/uploads/2024/06/LeanData-The-2024-State-GTM-Efficiency-Report.pdf
- [T6] Meta CAPI dedup docs: https://developers.facebook.com/docs/marketing-api/conversions-api/deduplicate-pixel-and-server-events
- [T7] UTM guidance: https://support.google.com/analytics/answer/10917952
- [F7] Dreamdata branded/non-branded search analysis (2024): https://dreamdata.io/blog/branded-vs-non-branded-google-search-ads-b2b
- [T23] Apollo API rate-limit docs: https://docs.apollo.io/reference/rate-limits
- [T24] Apollo pricing: https://www.apollo.io/pricing
- [F8] HockeyStack self-reported attribution report (2024): https://www.hockeystack.com/lab-blog-posts/hockeystacks-sra-report-2024
- [F10] LiftLab case study (source-type caveat): https://liftlab.com/case-studies/saas-company-experiments-with-google-branded-search/

---

## Synthesis

The highest-confidence update for this skill is methodological: channel strategy in 2024-2026 must be built around buyer progression before seller engagement, not just channel affordances. Multiple sources converge on deep pre-contact buying behavior and larger buying groups, which means channel plans need explicit Selection vs Validation roles and buying-group coverage logic, not only channel lists [A1][A2][A3].

A second synthesis is about evidence quality. Tool availability is no longer the bottleneck; interpretation quality is. The landscape now supports attribution, causal tests, and MMM in combinations that were previously too expensive or hard to run at smaller spend levels. The skill should therefore require triangulated evidence and predeclared scale gates, instead of allowing strategy conclusions from a single metric view [D1][D2][D3][D6].

The main contradiction in sources is that buyers self-direct heavily before sales contact, yet outbound/phone still shows meaningful contribution. This is not a true conflict when channels are sequenced correctly: pre-contact channels create awareness and preference; outbound and sales execution convert intent and multi-thread stakeholders during validation [A1][A7]. Another tension is efficiency pressure versus growth optimism; this resolves through staged budget release tied to hard unit-economics gates [A4][A5].

What is most actionable for `SKILL.md` is to make bad output harder to produce. The current skill should add explicit anti-pattern blocks (form-volume trap, blended search reporting, underpowered tests, motion sprawl) and schema fields that force assumptions, confidence, and measurement plans to be recorded. Without those constraints, channel strategy artifacts can remain articulate but untestable [F3][F7][D16].

---

## Recommendations for SKILL.md

- Add a formal **Selection vs Validation** methodology and require every selected channel to have a declared role in one or both phases.
- Add a **stage-gated channel operating model** with explicit scale/hold/exit thresholds (LTV:CAC, payback, confidence/sample criteria).
- Add a **triangulated measurement standard**: attribution for tactical optimization, incrementality for causal checks, MMM-style calibration for budget allocation.
- Add mandatory **anti-pattern warning blocks** with detection signal, consequence, and mitigation steps.
- Expand the **Artifact Schema** to include assumptions/confidence, measurement plan, scale gates, anti-pattern monitors, and decision log.
- Update `## Available Tools` guidance to include strict sequencing of `flexus_policy_document(...)` activations before channel decisions and `write_artifact(...)` persistence after validation.

---

## Draft Content for SKILL.md

### Draft: Core Channel Strategy Principles

Use this section near the top of `SKILL.md` to replace generic strategy framing with evidence-driven operating rules.

---
### Core operating principles

You are not choosing channels in isolation. You are designing a sequence that matches how buyers actually buy in 2024-2026: buyers self-educate deeply before contacting sales, and most opportunities involve multiple stakeholders with different concerns [A1][A2][A3]. Because of this, every channel you choose must have a clear role in either **Selection** (preference formation before direct contact) or **Validation** (risk reduction and consensus building before purchase).

Your default posture is constraint-first: run fewer channels with higher measurement quality, not many channels with shallow attribution. If you cannot explain channel role, success criteria, and failure criteria before execution, you are not ready to run that channel.

You must separate:
1. **Net-new acquisition system** (creating and capturing new demand).
2. **Expansion/retention system** (growing and protecting existing revenue).

As company stage changes, budget share across these systems changes, but both systems must stay healthy. Do not use expansion strength to hide a weak net-new engine [A5].

---

### Draft: Methodology (Step-by-Step Execution)

Use this as the primary `## Methodology` replacement.

---
### Methodology

Before choosing any channel, activate and review the relevant policy documents (`ICP scorecard`, `positioning map`, `pricing tiers`, `hypothesis stack`). Your channel choices are invalid if they are not grounded in those upstream constraints.

Then execute this sequence:

1. **Classify buying motion and deal complexity first.**  
   Determine ACV band, implementation complexity, and buying-group complexity. If ACV is high and implementation risk is meaningful, bias toward higher-touch channels and multi-threaded engagement. If ACV is low and onboarding is simple, prioritize low-touch/no-touch channels first [A6].  
   You must write this classification explicitly before selecting channels.

2. **Map channel roles to Selection vs Validation.**  
   For each candidate channel, declare whether it primarily contributes to Selection, Validation, or both.  
   - Selection examples: educational content, SEO, category messaging, targeted paid awareness, communities.  
   - Validation examples: outbound to in-market accounts, technical demos, references, partner co-sell proof.  
   If a channel has no clear phase role, remove it from the active plan [A2][A3].

3. **Start with 1-2 channels to saturation.**  
   Early execution should minimize motion sprawl. Use one primary and one secondary channel until you have stable conversion, CAC behavior, and enough signal for causal validation.  
   Add a third channel only after primary channels pass scale gates for two consecutive review windows. This avoids false negatives caused by spreading effort too thin [F3].

4. **Define stage-appropriate sequencing.**  
   - `pre_pmf`: founder-led outbound + warm network + focused community presence.  
   - `post_pmf_early`: systematized outbound + focused content + one partner motion.  
   - `growth`: add paid channels with strict measurement controls and causal testing cadence.  
   - `scale`: optimize portfolio mix, including expansion channels, while preserving net-new throughput [A4][A5].  
   This sequence is a default; adjust only with explicit evidence.

5. **Set economics and confidence gates before launch.**  
   For every channel, predefine:
   - target CAC (channel-specific),
   - target payback window,
   - target LTV:CAC range,
   - minimum sample criteria,
   - decision rule (scale / hold / stop).  
   Do not "discover" success criteria after results arrive [D7][D8][D16].

6. **Instrument measurement as a three-layer system.**  
   Use attribution for day-to-day tactical optimization, incrementality for causal lift on material spend, and MMM-style calibration for budget allocation in longer windows [D1][D2][D3].  
   If these methods disagree, do not average them blindly. Diagnose by horizon, lag, and confounders first [D4][D5][D6].

7. **Run an anti-pattern review before final recommendation.**  
   Explicitly test for known traps: form-volume bias, blended brand/non-brand reporting, underpowered tests, single-threaded deals, and motion sprawl.  
   If any trap is detected, downgrade confidence and include mitigation steps in the strategy artifact [F7][F8][D16].

Decision rule:
- If channel evidence clears economics + confidence gates in two consecutive windows -> scale.
- If economics pass but confidence is low -> hold and run targeted incrementality or sample-size extension.
- If economics fail and no credible leading indicators improve -> stop and reallocate.

Do NOT:
- launch 4+ channels simultaneously in early stage without orchestration owner,
- treat MQL volume as sufficient success evidence,
- report paid search as a single blended line without brand/non-brand split [F3][F7].

---

### Draft: Channel Scoring and Sequencing Rules

Use this to replace lightweight scoring with explicit weighted criteria and evidence quality checks.

---
### Channel scoring framework

Score candidate channels using weighted criteria. Keep scores numeric and evidence-linked.

| Criterion | Weight | Scoring Guidance |
|---|---:|---|
| ICP concentration | 25% | Can you consistently reach the target buying group? |
| Time to first meaningful signal | 15% | How quickly can you observe reliable leading indicators? |
| Time to first customer outcome | 15% | How quickly can channel produce first closed-won or equivalent proof? |
| CAC predictability | 15% | Is CAC estimable with available benchmarks and current funnel data? |
| Measurement readiness | 15% | Are attribution, conversion events, and test design feasible now? |
| Scalability potential | 10% | Can spend/effort scale without immediate diminishing returns? |
| Execution burden | 5% | Do current team/process constraints allow high-quality execution? |

Scoring rules:
- Use 0-10 scores per criterion.
- Any channel with `measurement_readiness < 5` cannot be primary until instrumentation is fixed.
- Any channel with `CAC predictability < 5` must be launched as a bounded experiment, not a scale motion.

Sequencing rules:
1. Choose one primary channel with highest weighted score.
2. Choose one secondary channel that complements phase coverage (if primary is Selection-heavy, secondary should help Validation, and vice versa).
3. Define next-channel trigger as an explicit condition, not a date (for example: "primary channel reaches 2 consecutive windows with CAC <= target and payback <= threshold").

---

### Draft: Measurement and Interpretation Guardrails

Use this section to harden output quality against weak signal interpretation.

---
### Measurement guardrails (mandatory)

You must evaluate channel performance with a triangulated evidence model:

1. **Attribution view (tactical):**  
   Use this for optimization decisions like creative, audience, and messaging iteration. Attribution answers "where touches occurred," not "what caused lift."

2. **Incrementality view (causal):**  
   Use controlled tests for channels/campaigns with material spend. Start once practical test budgets and conversion volume support interpretable results (Google has lowered barriers, but variance still matters) [D2].

3. **Model-based budget view (allocation):**  
   Use MMM-style modeling for medium-term budget allocation and to account for lag, seasonality, and cross-channel interaction effects [D1][D4][D5].

Interpretation rules:
- Never use one metric in isolation.
- Separate branded and non-branded search in all reporting.
- Pair CAC/payback with retention and cohort maturity.
- Require predeclared sample size and power targets for experiment-based claims [D14][D16][D17].

Default threshold guidance (directional, not universal laws):
- LTV:CAC target: around 3:1 or better (context-dependent) [D9][D10].
- Payback: prefer shorter windows, but interpret by ACV/motion and retention quality [D8].
- New CAC Ratio: if performance approaches lower-quartile ranges in your segment, treat as scale risk [D7].

If attribution and incrementality disagree:
1. Check instrumentation quality (UTM consistency, event dedup, conversion windows).
2. Check lag/seasonality window alignment.
3. Check whether branded demand is inflating paid efficiency.
4. Prefer causal evidence for scale decisions when tactical attribution conflicts [T6][T7][F7].

---

### Draft: Anti-Pattern Warning Blocks

Use these warning blocks verbatim or adapted. Keep all four fields: what it looks like, detection signal, consequence, mitigation.

---
#### Warning: Form-Volume Trap
**What it looks like:** Strategy recommends channels because they generate high lead/form counts.  
**Detection signal:** MQLs rise while SQL-to-close or revenue conversion stagnates; account-level buying signals remain thin [F1][F2][F5].  
**Consequence if missed:** Budget shifts toward low-quality demand capture, CAC increases, and sales cycles lengthen.  
**Mitigation:** Re-anchor success metrics to qualified pipeline and closed-won quality. Require account-level and buying-group evidence before channel scale.

#### Warning: Blended Search Illusion
**What it looks like:** Paid search reported as one aggregate line item.  
**Detection signal:** Brand terms carry efficiency while non-brand underperforms; aggregate ROAS still appears healthy [F7][F11].  
**Consequence if missed:** Overinvestment in low-incremental spend and false channel confidence.  
**Mitigation:** Split brand vs non-brand in all scorecards; run periodic holdouts/geo tests on branded spend [F9][F10].

#### Warning: Underpowered Channel Tests
**What it looks like:** Winner/loser decisions after short tests with low event volume.  
**Detection signal:** No predeclared minimum detectable effect, sample-size plan, or power target; frequent "non-significant means no effect" conclusions [D14][D16].  
**Consequence if missed:** Good channels are killed early, weak channels scale on noise.  
**Mitigation:** Require pre-launch test plan with alpha/power assumptions and stop rules. Extend test windows when underpowered.

#### Warning: Motion Sprawl Without Orchestration
**What it looks like:** Multiple motions launched simultaneously (outbound, paid, partner, content) without clear ownership and handoff rules.  
**Detection signal:** Rising activity but slow opportunity creation and inconsistent follow-up SLAs [F3].  
**Consequence if missed:** Channel cannibalization, pipeline leakage, and attribution confusion.  
**Mitigation:** Assign one orchestration owner, define stage SLAs and handoff criteria, and delay adding motions until existing ones pass scale gates.

#### Warning: Single-Threaded Deal Coverage
**What it looks like:** One contact drives most opportunity engagement.  
**Detection signal:** Buying-group depth is not tracked while opportunities stall late [A3][F2].  
**Consequence if missed:** Internal customer consensus fails; forecast reliability degrades.  
**Mitigation:** Require role-based multi-thread engagement plans for opportunities above predefined deal size/complexity.

---

### Draft: Available Tools

Use this as the rewritten `## Available Tools` section.

---
### Available Tools

Before drafting channel recommendations, you must activate policy documents in this order so channel choices are constrained by upstream strategy:

```python
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})
flexus_policy_document(op="activate", args={"p": "/strategy/positioning-map"})
flexus_policy_document(op="activate", args={"p": "/strategy/pricing-tiers"})
flexus_policy_document(op="activate", args={"p": "/strategy/hypothesis-stack"})
```

After you finish channel selection, sequencing, measurement plan, and anti-pattern checks, persist the final artifact:

```python
write_artifact(
  artifact_type="gtm_channel_strategy",
  path="/strategy/gtm-channel-strategy",
  data={...}
)
```

Tool usage rules:
- Do not call `write_artifact` until all required schema fields are complete.
- If upstream policy documents conflict, note the conflict in `assumptions` and reduce confidence rather than forcing a single unsupported conclusion.
- If a channel recommendation is based on low-confidence or vendor-only evidence, include explicit uncertainty in `decision_log`.

---

### Draft: Recording Requirements

Use this block to clarify what complete output looks like.

---
### Recording

Your artifact must be executable by another strategist without hidden context. Record:
- explicit assumptions and confidence levels,
- why each chosen channel is in Selection/Validation/Expansion role,
- economic targets and scale thresholds,
- measurement method selection and known limitations,
- anti-patterns being monitored and mitigation plan,
- clear exclusions with reasons.

A strategy artifact is incomplete if it only lists channels and budget without decision gates and evidence quality notes.

---

### Draft: Schema additions

Use this JSON Schema fragment to replace the current artifact schema. It keeps existing core fields but adds evidence quality, measurement, and governance structure.

```json
{
  "gtm_channel_strategy": {
    "type": "object",
    "description": "Channel strategy plan with sequencing, economic guardrails, measurement standards, and risk controls.",
    "required": [
      "created_at",
      "analysis_window",
      "stage",
      "assumptions",
      "primary_channels",
      "channel_sequence",
      "budget_allocation",
      "cac_targets",
      "measurement_plan",
      "scale_gates",
      "anti_patterns_to_monitor",
      "exclusions",
      "decision_log"
    ],
    "additionalProperties": false,
    "properties": {
      "created_at": {
        "type": "string",
        "format": "date-time",
        "description": "ISO-8601 UTC timestamp indicating when this strategy artifact was generated."
      },
      "analysis_window": {
        "type": "object",
        "description": "Date range used to evaluate historical performance and benchmark context for this strategy.",
        "required": ["start_date", "end_date"],
        "additionalProperties": false,
        "properties": {
          "start_date": {
            "type": "string",
            "format": "date",
            "description": "Inclusive start date (YYYY-MM-DD) of the data window used for analysis."
          },
          "end_date": {
            "type": "string",
            "format": "date",
            "description": "Inclusive end date (YYYY-MM-DD) of the data window used for analysis."
          }
        }
      },
      "stage": {
        "type": "string",
        "enum": ["pre_pmf", "post_pmf_early", "growth", "scale"],
        "description": "Business maturity stage that determines default channel sequencing and risk tolerance."
      },
      "assumptions": {
        "type": "array",
        "description": "Explicit assumptions used in channel decisions, each with confidence and evidence references.",
        "items": {
          "type": "object",
          "required": ["assumption", "confidence", "evidence_refs"],
          "additionalProperties": false,
          "properties": {
            "assumption": {
              "type": "string",
              "description": "Single declarative assumption affecting strategy (for example: sales cycle length, target ACV band, or conversion lag)."
            },
            "confidence": {
              "type": "string",
              "enum": ["low", "medium", "high"],
              "description": "Confidence in this assumption based on evidence quality and recency."
            },
            "evidence_refs": {
              "type": "array",
              "description": "List of source identifiers or internal document references supporting the assumption.",
              "items": {
                "type": "string"
              }
            }
          }
        }
      },
      "primary_channels": {
        "type": "array",
        "description": "Selected channels for current planning cycle with role, economics, and risk details.",
        "items": {
          "type": "object",
          "required": [
            "channel",
            "role_in_funnel",
            "rationale",
            "icp_fit_score",
            "time_to_first_result_weeks",
            "expected_payback_months",
            "cac_target",
            "measurement_readiness",
            "scalability",
            "risks"
          ],
          "additionalProperties": false,
          "properties": {
            "channel": {
              "type": "string",
              "enum": [
                "founder_outbound",
                "sdr_outbound",
                "inbound_seo",
                "paid_search_brand",
                "paid_search_nonbrand",
                "paid_social",
                "product_led",
                "community",
                "partnerships",
                "events",
                "email_lifecycle"
              ],
              "description": "Normalized channel identifier."
            },
            "role_in_funnel": {
              "type": "array",
              "description": "Funnel phase roles this channel is expected to serve.",
              "minItems": 1,
              "items": {
                "type": "string",
                "enum": ["selection", "validation", "expansion"]
              }
            },
            "rationale": {
              "type": "string",
              "description": "Why this channel is selected for the current stage and ICP, including strategic fit and expected edge."
            },
            "icp_fit_score": {
              "type": "number",
              "minimum": 0,
              "maximum": 10,
              "description": "0-10 score for how directly the channel reaches the target ICP and buying group."
            },
            "time_to_first_result_weeks": {
              "type": "integer",
              "minimum": 0,
              "description": "Expected weeks to first meaningful signal (qualified meeting, SQL, or equivalent)."
            },
            "expected_payback_months": {
              "type": "number",
              "minimum": 0,
              "description": "Expected CAC payback in months for this channel under baseline assumptions."
            },
            "cac_target": {
              "type": "number",
              "minimum": 0,
              "description": "Target customer acquisition cost for this channel in account currency."
            },
            "measurement_readiness": {
              "type": "number",
              "minimum": 0,
              "maximum": 10,
              "description": "0-10 score for instrumentation quality (tracking completeness, attribution reliability, and test feasibility)."
            },
            "scalability": {
              "type": "string",
              "enum": ["high", "medium", "low"],
              "description": "Expected ability to increase volume efficiently after validation."
            },
            "risks": {
              "type": "array",
              "description": "Known channel-specific risks (for example attribution bias, saturation, or compliance constraints).",
              "items": {
                "type": "string"
              }
            }
          }
        }
      },
      "channel_sequence": {
        "type": "array",
        "description": "Execution phases with explicit entry and exit conditions.",
        "items": {
          "type": "object",
          "required": ["phase", "channels", "entry_criteria", "exit_trigger", "owner"],
          "additionalProperties": false,
          "properties": {
            "phase": {
              "type": "string",
              "description": "Human-readable phase name (for example: discovery, validate, scale)."
            },
            "channels": {
              "type": "array",
              "description": "Channels active in this phase.",
              "items": {
                "type": "string"
              }
            },
            "entry_criteria": {
              "type": "string",
              "description": "Condition required before starting this phase."
            },
            "exit_trigger": {
              "type": "string",
              "description": "Condition that must be met to progress to the next phase."
            },
            "owner": {
              "type": "string",
              "description": "Role accountable for phase execution and reporting."
            }
          }
        }
      },
      "budget_allocation": {
        "type": "object",
        "description": "Budget split by strategic intent for current planning horizon.",
        "required": ["period", "allocation_percent"],
        "additionalProperties": false,
        "properties": {
          "period": {
            "type": "string",
            "enum": ["monthly", "quarterly"],
            "description": "Cadence used for budget planning and review."
          },
          "allocation_percent": {
            "type": "object",
            "description": "Percent allocation across demand creation, demand capture, and retention/expansion.",
            "required": ["demand_creation", "demand_capture", "retention_expansion"],
            "additionalProperties": false,
            "properties": {
              "demand_creation": {
                "type": "number",
                "minimum": 0,
                "maximum": 100,
                "description": "Percent of budget for out-market influence and preference creation."
              },
              "demand_capture": {
                "type": "number",
                "minimum": 0,
                "maximum": 100,
                "description": "Percent of budget for in-market conversion channels."
              },
              "retention_expansion": {
                "type": "number",
                "minimum": 0,
                "maximum": 100,
                "description": "Percent of budget for customer expansion and retention motions."
              }
            }
          }
        }
      },
      "cac_targets": {
        "type": "object",
        "description": "Economic targets used as viability and scale gates.",
        "required": [
          "max_blended_cac",
          "ltv_assumption",
          "target_ltv_to_cac_ratio",
          "target_payback_months",
          "cac_per_channel"
        ],
        "additionalProperties": false,
        "properties": {
          "max_blended_cac": {
            "type": "number",
            "minimum": 0,
            "description": "Maximum blended CAC allowed across active acquisition channels."
          },
          "ltv_assumption": {
            "type": "number",
            "minimum": 0,
            "description": "Assumed customer lifetime value used for initial CAC viability checks."
          },
          "target_ltv_to_cac_ratio": {
            "type": "number",
            "minimum": 0,
            "description": "Target LTV:CAC ratio for strategic viability (for example, around 3.0 depending on context)."
          },
          "target_payback_months": {
            "type": "number",
            "minimum": 0,
            "description": "Target CAC payback in months used for scale decisions."
          },
          "cac_per_channel": {
            "type": "object",
            "description": "Per-channel CAC targets keyed by channel identifier.",
            "additionalProperties": {
              "type": "number",
              "minimum": 0
            }
          }
        }
      },
      "measurement_plan": {
        "type": "object",
        "description": "Measurement architecture combining tactical, causal, and allocation views.",
        "required": [
          "attribution_model",
          "incrementality_plan",
          "mmm_plan",
          "kpis",
          "reporting_cadence",
          "data_hygiene"
        ],
        "additionalProperties": false,
        "properties": {
          "attribution_model": {
            "type": "string",
            "enum": ["multi_touch", "position_based", "first_touch", "last_touch", "custom"],
            "description": "Primary tactical attribution view used for day-to-day optimization."
          },
          "incrementality_plan": {
            "type": "object",
            "description": "How and when causal tests are run before channel scale-up.",
            "required": ["required_for_channels", "minimum_test_budget", "decision_rule"],
            "additionalProperties": false,
            "properties": {
              "required_for_channels": {
                "type": "array",
                "description": "Channels that require incrementality testing before material budget expansion.",
                "items": {
                  "type": "string"
                }
              },
              "minimum_test_budget": {
                "type": "number",
                "minimum": 0,
                "description": "Minimum budget allocated to an incrementality test for interpretable signal."
              },
              "decision_rule": {
                "type": "string",
                "description": "Rule for deciding scale, hold, or stop after causal test results."
              }
            }
          },
          "mmm_plan": {
            "type": "object",
            "description": "Model-based budget calibration approach for medium-term allocation decisions.",
            "required": ["enabled", "refresh_cadence", "notes"],
            "additionalProperties": false,
            "properties": {
              "enabled": {
                "type": "boolean",
                "description": "Whether MMM (or equivalent model-based calibration) is active."
              },
              "refresh_cadence": {
                "type": "string",
                "enum": ["monthly", "quarterly"],
                "description": "How often model-based calibration is refreshed."
              },
              "notes": {
                "type": "string",
                "description": "Implementation notes, including known limitations or confounders."
              }
            }
          },
          "kpis": {
            "type": "array",
            "description": "Primary performance indicators with targets and guardrails.",
            "items": {
              "type": "object",
              "required": ["metric", "target", "guardrail", "window_days"],
              "additionalProperties": false,
              "properties": {
                "metric": {
                  "type": "string",
                  "description": "Metric name (for example: CAC, payback, SQL-to-CW conversion, branded search share)."
                },
                "target": {
                  "type": "string",
                  "description": "Target value or range."
                },
                "guardrail": {
                  "type": "string",
                  "description": "Failure threshold that triggers mitigation or rollback."
                },
                "window_days": {
                  "type": "integer",
                  "minimum": 1,
                  "description": "Lookback window used to evaluate this KPI."
                }
              }
            }
          },
          "reporting_cadence": {
            "type": "object",
            "description": "Cadence for tactical and strategic channel reviews.",
            "required": ["tactical", "strategic"],
            "additionalProperties": false,
            "properties": {
              "tactical": {
                "type": "string",
                "enum": ["weekly", "biweekly"],
                "description": "Cadence for operational optimization reviews."
              },
              "strategic": {
                "type": "string",
                "enum": ["monthly", "quarterly"],
                "description": "Cadence for budget and channel-portfolio decisions."
              }
            }
          },
          "data_hygiene": {
            "type": "object",
            "description": "Tracking quality constraints required for trustworthy comparisons.",
            "required": ["utm_naming_convention", "brand_vs_nonbrand_split", "deduplication_method"],
            "additionalProperties": false,
            "properties": {
              "utm_naming_convention": {
                "type": "string",
                "description": "UTM naming standard applied consistently across channels."
              },
              "brand_vs_nonbrand_split": {
                "type": "boolean",
                "description": "Whether paid-search reporting separates branded and non-branded traffic."
              },
              "deduplication_method": {
                "type": "string",
                "description": "Method used to avoid duplicate conversion counting across client/server or multi-source events."
              }
            }
          }
        }
      },
      "scale_gates": {
        "type": "array",
        "description": "Explicit gate checks that must pass before increasing channel investment.",
        "items": {
          "type": "object",
          "required": [
            "channel",
            "gate_name",
            "metric",
            "threshold",
            "minimum_sample_size",
            "lookback_window_days",
            "action_if_failed"
          ],
          "additionalProperties": false,
          "properties": {
            "channel": {
              "type": "string",
              "description": "Channel this gate applies to."
            },
            "gate_name": {
              "type": "string",
              "description": "Short name for the gate check."
            },
            "metric": {
              "type": "string",
              "description": "Metric evaluated by this gate."
            },
            "threshold": {
              "type": "string",
              "description": "Pass threshold expressed as a value or range."
            },
            "minimum_sample_size": {
              "type": "integer",
              "minimum": 1,
              "description": "Minimum number of observations required before evaluating this gate."
            },
            "lookback_window_days": {
              "type": "integer",
              "minimum": 1,
              "description": "Number of days included in gate evaluation window."
            },
            "action_if_failed": {
              "type": "string",
              "enum": ["hold", "decrease_budget", "stop_and_reallocate"],
              "description": "Action to take if gate fails."
            }
          }
        }
      },
      "anti_patterns_to_monitor": {
        "type": "array",
        "description": "Known failure modes tracked during execution with mitigation ownership.",
        "items": {
          "type": "object",
          "required": ["name", "detection_signal", "consequence", "mitigation"],
          "additionalProperties": false,
          "properties": {
            "name": {
              "type": "string",
              "description": "Anti-pattern name."
            },
            "detection_signal": {
              "type": "string",
              "description": "Observable indicator that the anti-pattern is occurring."
            },
            "consequence": {
              "type": "string",
              "description": "Expected business impact if not corrected."
            },
            "mitigation": {
              "type": "string",
              "description": "Concrete response plan to reduce or remove risk."
            }
          }
        }
      },
      "exclusions": {
        "type": "array",
        "description": "Channels intentionally excluded from the current cycle with rationale.",
        "items": {
          "type": "object",
          "required": ["channel", "reason"],
          "additionalProperties": false,
          "properties": {
            "channel": {
              "type": "string",
              "description": "Excluded channel identifier."
            },
            "reason": {
              "type": "string",
              "description": "Why the channel is excluded now (for example: poor fit, low readiness, or unit economics risk)."
            }
          }
        }
      },
      "decision_log": {
        "type": "array",
        "description": "Chronological record of major strategy decisions, confidence shifts, and rationale updates.",
        "items": {
          "type": "object",
          "required": ["timestamp", "decision", "reason", "confidence_after"],
          "additionalProperties": false,
          "properties": {
            "timestamp": {
              "type": "string",
              "format": "date-time",
              "description": "ISO-8601 UTC timestamp when the decision was made."
            },
            "decision": {
              "type": "string",
              "description": "Decision taken (for example: scale paid_search_nonbrand, pause events, start incrementality test)."
            },
            "reason": {
              "type": "string",
              "description": "Evidence-backed rationale for the decision."
            },
            "confidence_after": {
              "type": "string",
              "enum": ["low", "medium", "high"],
              "description": "Overall confidence level after this decision."
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

- Public, universally fixed numeric rate limits are not fully published for all tools (notably LinkedIn endpoint specifics and many Apollo plan-level quotas); implementation should treat these as account-specific until verified [T3][T23][T24].
- Several anti-pattern examples rely on vendor or agency case studies rather than peer-reviewed causal studies; useful for pattern detection, but confidence should be marked medium unless replicated internally [F9][F10][F11].
- Benchmarks for conversion rates and CAC efficiency vary heavily by segment (industry, ACV, geography, sales cycle length). The skill should enforce context-specific calibration rather than fixed global thresholds [D7][D13].
- We did not find a single authoritative cross-vendor standard for B2B multi-touch attribution definitions; teams should document their chosen model assumptions explicitly in the artifact to avoid false comparability across periods.
