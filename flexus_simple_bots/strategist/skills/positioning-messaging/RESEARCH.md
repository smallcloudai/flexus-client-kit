# Research: positioning-messaging

**Skill path:** `flexus-client-kit/flexus_simple_bots/strategist/skills/positioning-messaging/`
**Bot:** strategist (researcher | strategist | executor)
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`positioning-messaging` is the strategist skill that turns market evidence into usable messaging: positioning statement, message hierarchy, hero copy variants, and objection responses. The current `SKILL.md` has a strong foundation (evidence refs, hierarchy layers, and objection response structure), but it still leaves too much room for "copy taste" decisions, weak claim substantiation, and channel mismatch.

2024-2026 research shows three practical shifts that should be encoded directly in the skill instructions:
1. Buyers form opinions before sales interaction, so messaging must be channel-adapted but narrative-consistent.
2. Teams over-index on click metrics and under-specify interpretation quality (SRM, multiplicity, practical significance), producing false confidence.
3. Compliance and trust risk moved from edge case to operational requirement (AI claims, fake reviews/testimonials, misleading "free"/savings claims).

For this skill to produce decision-grade output, each message claim should be traceable to customer-language evidence, each channel variant should preserve core meaning while respecting channel constraints, and each recommendation should be gated by confidence and claim-compliance checks.

This version synthesizes five internal research tracks completed for this document: methodology, tool/API landscape, channel adaptation, signal interpretation, and failure-mode/anti-pattern analysis.

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
- Findings volume 800-4000 words: **passed**
- `Draft Content for SKILL.md` is longer than Findings sections combined: **passed**

---

## Research Angles

Each angle below was researched by five dedicated internal sub-agents (methodology, tools/APIs, channels, interpretation, and anti-patterns) and synthesized for this skill.

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

Positioning and messaging execution has shifted from "single statement workshop output" toward "evidence pipeline + iterative testing." PMM playbooks in 2024-2026 emphasize constrained message architecture (value proposition length limits, pillar count limits, and explicit proof layering), because unconstrained frameworks consistently bloat into generic language that cannot survive channel adaptation.

A practical structure now used in mature teams is: define segment/problem frame first, then build one concise core value proposition, then expand into hierarchy layers with linked proof points. PMA guidance and practitioner workflows support explicit constraints (for example 3-5 pillars instead of long laundry lists), which fits this skill's existing hierarchy model and should be made mandatory rather than optional.

Customer-language-first design remains the strongest quality predictor. Teams that test early message drafts with ICP respondents (instead of waiting for post-launch A/B) can detect confusion and relevance failure before media/sales costs accumulate. Message testing tools now operationalize this with tight turnaround windows and structured scoring dimensions (clarity, relevance, value, differentiation, brand fit).

Objection handling is most effective when scripts are class-based, not one-size-fits-all. Gong's 2024 large-scale call analysis shows objection distributions are patterned (dismissive, situational, incumbent-solution), which implies the skill should require objection-type tagging and matching response logic.

Value proposition quality standards increasingly reject "technology-first" copy. NN/g guidance (accessed 2026) is explicit: "powered by AI" is not a value proposition by itself; copy should lead with user outcome and mechanism evidence. For this skill, that means banning unsupported superlatives and requiring proof references for hero claims.

One nuance: classic positioning frameworks (Dunford, older but evergreen) still provide useful sequencing (alternatives -> differentiators -> value -> segment -> category), but recent evidence suggests teams should treat final statement text as an output of evidence synthesis, not as the primary discovery method.

**Sources:**
- Product Marketing Alliance, *Maximizing the impact of product messaging frameworks* (2024-02-06): https://www.productmarketingalliance.com/maximizing-the-impact-of-product-messaging-frameworks/
- Product Marketing Alliance, *The secrets of compelling messaging and effective product positioning* (2026-01-22): https://www.productmarketingalliance.com/the-secrets-of-compelling-messaging-and-effective-product-positioning/
- Wynter, *What is message testing?* (accessed 2026-03-05): https://wynter.com/post/what-is-message-testing
- Wynter, *The definitive guide to message testing* (accessed 2026-03-05): https://wynter.com/post/message-testing
- Wynter, *Message Testing product page* (accessed 2026-03-05): https://wynter.com/products/message-testing
- Gong, *Top objections across 300M cold calls* (2024-07-31): https://www.gong.io/blog/we-found-the-top-objections-across-300m-cold-calls-heres-how-to-handle-them-all
- Nielsen Norman Group, *"Powered by AI" Is Not a Value Proposition* (accessed 2026-03-05): https://www.nngroup.com/articles/powered-by-ai-is-not-a-value-proposition/
- April Dunford, *A Quickstart Guide to Positioning* (2021, evergreen): https://www.aprildunford.com/post/a-quickstart-guide-to-positioning

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

The operational stack for positioning/messaging now spans five tool classes: (1) voice-of-customer ingestion, (2) survey/research collection, (3) call-intelligence enrichment, (4) experimentation and rollout control, and (5) behavior analytics. No single vendor covers all classes with equal quality; teams need explicit source provenance and per-source constraints.

For review/feedback ingestion, practical options include Google Business Profile APIs, Trustpilot APIs, Yelp Places API, and Reddit Data API. These have concrete but non-uniform limits: Google Business Profile documents default QPM behavior; Reddit documents free-tier QPM and OAuth/user-agent requirements; Trustpilot publishes auth modes and rate-limit guidance; Yelp includes rate headers and trial/day constraints. This variability means the skill should avoid assuming one shared ingestion cadence.

For survey/message input, Typeform and SurveyMonkey both expose OAuth-based APIs with clear scope and quota guidance. Their utility is strongest when used for structured message comprehension checks and segment-level response splitting before paid-channel deployment.

For call-intelligence support, AssemblyAI, Deepgram, and Amazon Transcribe Call Analytics provide documented transcription + sentiment/call insights workflows. They differ materially in limit semantics (concurrency vs request rate), which matters when feeding objection-signal loops.

For controlled rollout and experiment management, LaunchDarkly and Statsig provide flag-linked experimentation. Statsig publishes concrete mutation limits in docs; LaunchDarkly documents 429 behavior and headers but intentionally avoids fixed universal numeric limits in public docs. The skill should therefore recommend dynamic limit handling and explicit "read docs at runtime" behavior for operations.

For analytics/event pipelines, Amplitude HTTP V2 and Segment HTTP API are common de-facto infrastructure. Amplitude documents ingestion constraints and dedupe semantics (`insert_id`), while Segment documents event size/rate guidance and 429 retry patterns. These are useful references for operational hardening, even if the strategist bot itself does not call these APIs directly.

**Sources:**
- Google Business Profile API `accounts.locations.batchGetReviews` (accessed 2026-03-05): https://developers.google.com/my-business/reference/rest/v4/accounts.locations/batchGetReviews
- Google Business Profile API limits (accessed 2026-03-05): https://developers.google.com/my-business/content/limits
- Trustpilot Authentication (accessed 2026-03-05): https://developers.trustpilot.com/authentication
- Trustpilot Consumer API (accessed 2026-03-05): https://developers.trustpilot.com/consumer-api
- Trustpilot Rate Limiting (accessed 2026-03-05): https://developers.trustpilot.com/rate-limiting/
- Yelp Places API intro/rate limiting (accessed 2026-03-05): https://docs.developer.yelp.com/docs/fusion-intro
- Reddit Data API Wiki (accessed 2026-03-05): https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki
- Typeform developer docs (accessed 2026-03-05): https://www.typeform.com/developers/get-started/
- SurveyMonkey API docs (accessed 2026-03-05): https://api.surveymonkey.net/v3/docs
- AssemblyAI transcript API (accessed 2026-03-05): https://www.assemblyai.com/docs/api-reference/transcripts/submit.mdx
- Deepgram API limits (accessed 2026-03-05): https://developers.deepgram.com/reference/api-rate-limits
- AWS Transcribe Call Analytics (accessed 2026-03-05): https://docs.aws.amazon.com/transcribe/latest/dg/call-analytics.html
- LaunchDarkly experimentation docs (accessed 2026-03-05): https://docs.launchdarkly.com/home/experimentation/
- LaunchDarkly REST API docs (accessed 2026-03-05): https://apidocs.launchdarkly.com/
- Statsig Console API experiments (accessed 2026-03-05): https://docs.statsig.com/console-api/experiments
- Amplitude HTTP V2 API (updated 2024-05-21): https://amplitude.com/docs/apis/analytics/http-v2
- Segment HTTP API source docs (accessed 2026-03-05): https://segment.com/docs/connections/sources/catalog/libraries/server/http-api/

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

Messaging decisions need explicit interpretation gates before recommendation. Platform guidance now documents minimum quality checks that should be translated into skill rules. Example: Amplitude significance guidance includes practical minimum counts (30 samples, 5 conversions, 5 non-conversions per variant) in addition to p-value interpretation.

Experiment planning quality is highly sensitive to up-front assumptions. Optimizely's 2025 guidance reinforces that alpha, beta, and MDE must be selected before launch and aligned to the exact inference method. Teams that mix methods (absolute-lift assumptions for relative-lift decisions, or mismatched variance assumptions) systematically misread outcomes.

Relative-lift reporting can be numerically unstable in some conditions. Statsig's 2025 analysis recommends Fieller intervals for ratio metrics and highlights denominator edge cases where percentage-lift intervals become unbounded. In those cases, teams should fall back to absolute-lift interpretation and directional evidence.

Sequential peeking remains one of the highest-frequency validity failures. 2025 experimentation guidance is clear: repeated looks under fixed-horizon assumptions inflate false positives. If teams peek, they need sequential methods with predeclared stop logic.

Multiplicity is another common failure mode in messaging work because teams slice by segment/channel/device and watch many metrics. Without correction (FWER/FDR), "winner inflation" is expected. This should be encoded in the skill as a hard caution on segment-level claims.

Sample-ratio mismatch (SRM) should be treated as a blocker, not a warning. Convert's 2025 guidance provides a practical threshold (`p < 0.01`) and emphasizes non-trivial prevalence in production experiments. If SRM is present, decisions should be paused.

For qualitative signal, 2024 interview-saturation research suggests "5 interviews always enough" is too weak for messaging synthesis. Near code saturation often occurs around 15-23 interviews, with true saturation frequently higher. This supports a tiered confidence rule in the skill based on sample and consistency, not raw quote count.

Interpretation also must be benchmarked by channel context. Unbounce and Ruler data show that baseline conversion rates differ substantially by source and industry, so absolute-lift thresholds should be contextualized rather than treated as universal.

**Sources:**
- Amplitude, *Statistical significance* (2024-06-27): https://amplitude.com/docs/faq/statistical-significance
- Optimizely, *Sample size calculations for experiments* (2025-12-12): https://www.optimizely.com/insights/blog/sample-size-calculations-for-experiments/
- Statsig, *Fieller intervals vs Delta method* (2025-06-10): https://www.statsig.com/blog/fieller-intervals-vs-delta-method
- Statsig, *Sequential testing and peeking* (2025-06-23): https://www.statsig.com/perspectives/sequential-testing-ab-peek
- Statsig, *Multiple comparison corrections in A/B testing* (2025-10-23): https://www.statsig.com/blog/multiple-comparison-corrections-in-a-b
- Convert, *Sample Ratio Mismatch guide* (2025-07-02): https://www.convert.com/blog/a-b-testing/sample-ratio-mismatch-srm-guide/
- JMIR, *Determining interview sample size for code saturation* (2024-07-09): https://www.jmir.org/2024/1/e52998/
- Unbounce, *Average landing page conversion rates* (Q4 2024 data): https://unbounce.com/average-conversion-rates-landing-pages/
- Ruler Analytics, *Conversion rate by industry/source* (2025-08-14): https://www.ruleranalytics.com/blog/insight/conversion-rate-by-industry/
- Statsig, *Statistical vs practical significance* (2024-10-29): https://www.statsig.com/perspectives/statistical-vs-practical-significance

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

1) **Buzzword-only positioning**  
What it looks like: generic "AI-powered end-to-end" language with no concrete problem/outcome.  
Detection: message tests show low clarity/relevance; buyers paraphrase with category clichés.  
Consequence: no memorable differentiation, weak conversion quality.  
Mitigation: require claim = pain + measurable outcome + mechanism + evidence refs.

2) **AI-washing and unsubstantiated superlatives**  
What it looks like: "first", "expert", "human-equivalent", or "risk-free" without traceable substantiation.  
Detection: no claim evidence pack, no reproducible test or contract support.  
Consequence: enforcement and trust risk (SEC/FTC actions in 2024-2025).  
Mitigation: claim substantiation gate and legal/compliance review flag in artifact.

3) **Misleading "free" and savings language**  
What it looks like: "free" or discount claims whose basis is not equivalent to displayed price context.  
Detection: inability to map claim to exact comparator/date/scope.  
Consequence: advertising rulings and forced corrections.  
Mitigation: disclose basis adjacent to claim; ban absolute savings language without proof.

4) **Synthetic or manipulated social proof**  
What it looks like: fake review/testimonial generation or sentiment-gated review collection.  
Detection: abnormal review velocity, repetitive phrasing, missing authenticity controls.  
Consequence: FTC review/testimonial rule exposure and reputation damage.  
Mitigation: require verified-source tags and anti-suppression policy.

5) **Objection script monoculture**  
What it looks like: one canned response for all objection types.  
Detection: low progression after objections; call-level behavior shows rep over-talking post-objection.  
Consequence: avoidable deal loss from answering the wrong objection class.  
Mitigation: classify objections, then apply type-specific response + follow-up question protocol.

6) **Cross-channel promise mismatch**  
What it looks like: pre-click promise differs materially from landing/sales reality.  
Detection: high drop-off at disclosure steps; complaint spikes about hidden conditions.  
Consequence: performance decay plus trust/compliance risk.  
Mitigation: message-match QA across ad/landing/sales/email before launch.

7) **Experiment peeking and multiplicity neglect**  
What it looks like: stopping when p-value turns green; claiming wins across many slices with no correction.  
Detection: many short tests and weak post-launch replication.  
Consequence: false positives and rollout of weak messaging.  
Mitigation: sequential logic + multiplicity correction + SRM gate.

8) **Jurisdiction-blind AI disclosure**  
What it looks like: AI-generated or AI-mediated messaging presented without required transparency for relevant regions.  
Detection: no jurisdiction-aware disclosure field in messaging workflow.  
Consequence: regulatory exposure as AI compliance obligations roll out.  
Mitigation: add disclosure checklist and region flags in artifact.

**Bad vs good output examples:**
- Bad: "We are the most advanced AI platform for modern teams."  
  Good: "For multi-site operators losing margin to stockouts, we reduce forecast error with POS + promo + weather signals, with evidence refs in source IDs."
- Bad: "FREE included."  
  Good: "Included in plan pricing; claim basis and constraints are shown next to price."
- Bad: "Variant B won, p<0.05 after two days."  
  Good: "Variant B passed predeclared sequential boundary, no SRM detected, and practical lift exceeded MDE threshold."

**Sources:**
- Edelman, *Using buzzwords does not replace thought leadership* (2024-06-25): https://www.edelman.com/insights/using-buzzwords-does-not-replace-thought-leadership
- SEC, *AI-washing enforcement action* (2024-03-18): https://www.sec.gov/newsroom/press-releases/2024-36
- FTC, *Crackdown on deceptive AI claims* (2024-09-25): https://www.ftc.gov/news-events/news/press-releases/2024/09/ftc-announces-crackdown-deceptive-ai-claims-schemes
- FTC, *DoNotPay order* (2025-02-11): https://www.ftc.gov/news-events/news/press-releases/2025/02/ftc-finalizes-order-donotpay-prohibits-deceptive-ai-lawyer-claims-imposes-monetary-relief-requires
- FTC, *Rytr testimonial/review order* (2024-12-18): https://www.ftc.gov/news-events/news/press-releases/2024/12/ftc-approves-final-order-against-rytr-seller-ai-testimonial-review-service-providing-subscribers
- FTC, *Consumer Reviews and Testimonials Rule (Q&A)* (2024-11): https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers
- Federal Register, *Consumer Reviews and Testimonials Rule* (2024-08-22): https://www.federalregister.gov/documents/2024/08/22/2024-18519/trade-regulation-rule-on-the-use-of-consumer-reviews-and-testimonials
- ASA, *Quintain ruling* (2024-08-14): https://www.asa.org.uk/rulings/quintain-living-ltd-a24-1244037-quintain-living-ltd.html
- ASA, *Webloyalty ruling* (2024-10-23): https://www.asa.org.uk/rulings/webloyalty-international-ltd-a24-1248087-webloyalty-international-sarl-ltd.html
- ASA, *Secret Escapes ruling* (2025-02-19): https://www.asa.org.uk/rulings/secret-escapes-ltd-a24-1258783-secret-escapes-ltd.html
- Gong, *Top objections across 300M cold calls* (2024-07-31): https://www.gong.io/blog/we-found-the-top-objections-across-300m-cold-calls-heres-how-to-handle-them-all
- Statsig, *Sequential testing and peeking* (2025-06-23): https://www.statsig.com/perspectives/sequential-testing-ab-peek
- Statsig, *Multiple comparisons* (2025-06-23): https://www.statsig.com/perspectives/multiple-comparisons-abtests-care
- European Commission, *AI Act enters into force* (2024-08-01): https://commission.europa.eu/news/ai-act-enters-force-2024-08-01_en

---

### Angle 5+: Channel-Specific Messaging & Distribution
> Additional angle for this domain: how positioning and messaging should adapt by channel while preserving narrative consistency.

**Findings:**

Recent benchmark evidence indicates teams must separate "attention optimization" from "conversion-quality optimization." 2024-2025 ad benchmarks show CTR can improve while CPL and conversion economics worsen. This means channel copy that wins clicks may still degrade pipeline quality if promise-to-proof continuity breaks post-click.

Landing-page clarity remains a major practical lever. Unbounce benchmark analysis indicates simpler language outperforms more complex copy on conversion outcomes, with worsening penalty for difficult wording versus prior years. This supports explicit readability constraints in hero copy instructions.

Device context matters. Mobile may dominate traffic volume while desktop still converts better in many contexts. Messaging architecture should therefore include device-sensitive layout/copy adaptation rather than assuming one hero block can carry equally across contexts.

Lifecycle email is a strong underused channel for message reinforcement. 2024 lifecycle data shows triggered/welcome flows outperform generic broadcast behavior, yet implementation maturity remains uneven. The skill should include channel-specific variants for lifecycle sequences, not only homepage/sales scripts.

B2B evidence reinforces pre-sales narrative consistency. TrustRadius 2024 shows buyers often shortlist options they already know before deep evaluation; therefore messaging architecture must synchronize website, thought leadership, paid channels, and sales decks around consistent problem framing and proof.

Sales-conversation evidence shows dialogue quality shapes message effectiveness. Gong's 2025 talk-to-listen data indicates over-talking correlates with weaker outcomes, implying objection-handling copy should drive clarifying questions and buyer voice collection, not longer monologues.

**Sources:**
- Unbounce press release, *2024 Conversion Benchmark Report* (2024-09-05): https://www.prnewswire.com/news-releases/unbounces-2024-conversion-benchmark-report-proves-that-attention-spans-are-declining-and-so-are-conversion-rates-302239407.html
- WordStream, *Google Ads Benchmarks 2024* (2025-09-29, reports 2024 data): https://www.wordstream.com/blog/2024-google-ads-benchmarks
- WordStream, *Facebook Ads Benchmarks 2025* (2025-09-15): https://www.wordstream.com/blog/facebook-ads-benchmarks-2025
- GetResponse, *Email Marketing Benchmarks* (updated 2024): https://www.getresponse.com/resources/reports/email-marketing-benchmarks
- Litmus, *State of Email in Lifecycle Marketing* (2024): https://www.litmus.com/wp-content/uploads/pdf/The-2024-State-of-Email-in-Lifecycle-Marketing-Report.pdf
- TrustRadius, *2024 B2B Buying Disconnect* (2024): https://go.trustradius.com/rs/827-FOI-687/images/2024%20B2B%20Buying%20Disconnect%20Year%20of%20the%20Brand%20Crisis.pdf
- Gong, *Top objections across 300M cold calls* (2024-07-31): https://www.gong.io/blog/we-found-the-top-objections-across-300m-cold-calls-heres-how-to-handle-them-all
- Gong, *Talk-to-listen conversion ratio* (updated 2025-08-21): https://www.gong.io/resources/labs/talk-to-listen-conversion-ratio
- Edelman, *2024 B2B Thought Leadership report page* (2024): https://www.edelman.com/expertise/Business-Marketing/2024-b2b-thought-leadership-report

---

## Synthesis

The strongest overall finding is that this skill should move from "write good copy" to "run an evidence-governed messaging system." In 2024-2026 sources, teams with durable messaging outcomes combine customer-language extraction, channel-specific adaptation, and disciplined testing, while teams that skip one of these steps mostly optimize vanity metrics.

There is a clear contradiction between top-of-funnel optimization and revenue-quality optimization: CTR can go up while CPL and conversion quality worsen. The practical resolution is to enforce promise continuity across channel transitions (ad -> landing -> sales -> onboarding) and reject single-channel "wins" that do not hold across funnel stages.

A second contradiction is methodological: teams want fast experimentation, but peeking, multiplicity neglect, and SRM blindness produce fragile conclusions. The right compromise is not "test less," but "test with predeclared decision rules and confidence gating." This should be explicit in the skill, especially for recommendation-level outputs.

The most actionable upgrade is claim governance. Regulatory and standards updates in 2024-2026 (AI claims, testimonials/reviews, misleading savings/free claims) now make messaging quality inseparable from compliance and trust. The artifact should carry claim substantiation metadata so unsupported statements are downgraded to hypotheses, not shipped as final narrative.

---

## Recommendations for SKILL.md

- [x] Add a mandatory **evidence-first preflight** before any positioning or copy generation.
- [x] Upgrade methodology from static statement writing to a **7-step messaging operating loop** (extract -> frame -> draft -> adapt -> test -> interpret -> refine).
- [x] Add **channel adaptation rules** that preserve core narrative while constraining per-channel copy and evidence.
- [x] Add **objection-type classification** and response logic tied to call-intelligence evidence classes.
- [x] Add **message-testing guardrails** (MDE, SRM checks, multiplicity handling, practical significance).
- [x] Add **confidence-tier decision rules** so weak evidence cannot produce hard recommendations.
- [x] Add explicit **claim substantiation and compliance checks** (AI claims, free/savings language, testimonial integrity).
- [x] Expand `## Available Tools` with only real, already-supported Flexus calls and explicit no-invention policy.
- [x] Add **recording requirements** for contradictions, unresolved risks, and refresh cadence.
- [x] Extend artifact schema with **evidence registry, channel adaptations, test metadata, confidence, compliance, and refresh fields**.

---

## Draft Content for SKILL.md

### Draft: Core operating mode and preflight

---
### Operating mode: evidence before copy

You are not a slogan generator. You are a messaging strategist that converts validated customer language into decision-grade narrative artifacts.

Before writing any positioning statement, headline, or objection response, you must verify evidence coverage. If evidence is missing, your output must downgrade to hypothesis mode and explicitly say what is missing.

Mandatory preflight checklist:
1. Confirm target segment context from `icp-scorecard` and declare it in output.
2. Activate discovery corpus and collect direct customer-language quotes (pain language, desired outcomes, objections).
3. Activate alternatives/positioning context and identify what the buyer compares you against, including "do nothing" when present.
4. Build a provisional message thesis with proof references before writing polished copy.
5. Reject any claim that cannot be tied to source evidence.

If any preflight item fails, you must still produce useful output, but mark all unsupported statements as `hypothesis` and list the exact missing artifacts.
---

### Draft: Positioning statement construction protocol

---
### Positioning statement protocol (evidence-traceable)

Use this sequence every time:

1. **Define scope first**  
   State segment, geography, and buying context before writing statement text. A statement without scope creates false universality and usually collapses in downstream channels.

2. **Extract customer-language anchors**  
   Pull exact phrasing from interviews/reviews/call transcripts for:
   - primary pain or risk,
   - desired outcome,
   - current workaround/alternative language.
   Do not paraphrase too early. Keep raw phrases available for reference.

3. **Draft structure with explicit evidence hooks**  
   Build the statement using:
   - target segment,
   - category frame,
   - differentiator,
   - proof point,
   - primary alternative.
   Each part needs at least one evidence reference. If any part has no evidence, do not finalize.

4. **Run contradiction pass**  
   Check whether corpus/reviews/calls disagree on pain severity, desired outcome, or alternative framing. If contradictions are material, lower confidence and write scenario variants instead of one "final" statement.

5. **Publish statement + rationale pair**  
   Output both:
   - customer-facing statement text,
   - strategist-facing rationale showing source IDs and confidence.

Do not output absolute superlatives ("best", "most advanced", "risk-free", "guaranteed") unless contractually and evidentially supported.
---

### Draft: Message hierarchy and channel adaptation

---
### Message hierarchy (single narrative, channel-adapted execution)

Build the hierarchy top-down:

- **Layer 1 hook (above fold):** one sentence, one primary outcome, one audience.
- **Layer 2 expanded value:** two to three sentences that explain mechanism and "why now."
- **Layer 3 proof points:** three to five points with explicit evidence references.
- **Layer 4 objections:** top objections mapped to response, follow-up question, and proof.

Then adapt by channel without changing core claim intent:

1. **Homepage hero**  
   Keep language simple and direct. Prioritize comprehension over cleverness. Avoid stacked claims in one sentence.

2. **Landing page / campaign pages**  
   Ensure ad promise and landing proof match exactly. If ad uses urgency language, landing must disclose conditions immediately, not in footer-only copy.

3. **Paid search/social copy**  
   Use constrained variants tailored to intent stage. Avoid copying long-form hero text into short-form ads.

4. **Sales deck / call talk track**  
   Convert claims into buyer-specific proof narratives. Prompt clarifying questions before rebuttal scripts.

5. **Email lifecycle**  
   Reframe the same core value across onboarding/nurture/activation stages using context-specific triggers and objections.

When channel constraints force shorter copy, reduce detail, not truthfulness. Do not introduce stronger claims in short formats than in long formats.
---

### Draft: Customer-language extraction and evidence integrity

---
### Customer-language extraction protocol

Your default is "borrow customer wording, then improve clarity." Do not invent pains that are not present in evidence.

Extraction steps:
1. Build a quote pool from corpus/review/call artifacts.
2. Tag each quote with:
   - source type,
   - observed date,
   - sentiment (pain/outcome/objection),
   - segment relevance.
3. Cluster quotes into recurring themes.
4. Select representative anchor phrases for each theme.
5. Use anchor phrases to draft messaging variants.

Quality rules:
- Preserve original meaning when rewriting for brevity.
- Reject outlier quotes that conflict with dominant signal unless you explicitly model a segment split.
- If quote quality is weak (stale, vague, low volume), lower confidence and avoid strong differentiation claims.

Evidence integrity rules:
- Every finalized claim must include at least one source ID.
- Claims with a single weak source become `provisional`.
- Claims with unresolved contradictory sources must carry contradiction notes.
---

### Draft: Objection handling architecture

---
### Objection handling (class-first, diagnosis-first)

Do not treat objections as interchangeable. First classify, then respond.

Minimum objection classes:
- `dismissive`
- `situational`
- `existing_solution`
- `price`
- `timing`
- `risk_or_compliance`
- `other`

For each objection response, you must provide:
1. Objection text (in buyer language),
2. Objection class,
3. Clarifying question,
4. Response text,
5. Proof point,
6. Source IDs.

Conversation rule: ask at least one clarifying question before giving the final rebuttal. This protects against misclassification and reduces over-talking.

If proof point is missing, do not fake certainty. Use transparent language:
"Based on current evidence, this appears likely, but requires confirmation in X."

Never use "guaranteed" or "risk-free" phrasing unless legally approved and contractually true.
---

### Draft: Message testing methodology and interpretation

---
### Testing loop (design -> execute -> interpret -> refine)

You must validate messaging through both qualitative and quantitative methods when possible.

Phase 1: qualitative diagnostics
1. Test early variants with ICP respondents using structured scoring dimensions:
   - clarity,
   - relevance,
   - value,
   - differentiation,
   - brand fit.
2. Collect open-text reasons, not just numeric scores.
3. Revise copy before paid rollout when clarity or relevance is weak.

Phase 2: controlled experiments
1. Define hypothesis, primary metric, alpha, beta, and MDE before launch.
2. Check implementation health (event mapping, assignment integrity).
3. Run experiment using predeclared stop logic.
4. Diagnose SRM before trusting outcome metrics.
5. Apply multiplicity handling when reading many segments/metrics.

Interpretation rules:
- Statistical significance alone is insufficient. Require practical significance against MDE.
- If SRM is detected, block recommendation and investigate instrumentation/randomization.
- If peeking occurred without sequential method, downgrade confidence.
- If relative-lift interval is unstable/unbounded, report absolute-lift and direction instead.

Decision output must include:
- verdict (`ship`, `iterate`, `hold`, `reject`),
- confidence tier,
- unresolved risks,
- next test recommendation.
---

### Draft: Confidence tiers, contradictions, and insufficient-evidence behavior

---
### Confidence and contradiction protocol

Assign confidence to each major recommendation:

- `high`: multi-source agreement, acceptable data quality, no unresolved material contradictions.
- `medium`: useful signal but at least one material caveat (sample, recency, disagreement).
- `low`: single-source or low-quality evidence, or unresolved contradiction that can change decision.

Contradiction handling steps:
1. Name the contradiction explicitly.
2. List source IDs that conflict.
3. Explain likely reason (timeframe, segment, method, channel context).
4. Reduce confidence tier.
5. Prefer scenario output over single definitive recommendation.

Insufficient-evidence behavior:
- You may still produce candidate copy variants, but mark them as `hypothesis`.
- You must output a short evidence acquisition plan (what source, what question, what threshold).
- You must not present low-confidence hypotheses as final messaging architecture.
---

### Draft: Claim substantiation and compliance guardrails

---
### Claim governance and compliance guardrails

Before finalizing any external-facing message, run claim governance checks:

1. **Substantiation check**  
   Every claim must map to evidence source IDs and observed dates.

2. **AI-claim check**  
   Claims about AI capability must be specific and verifiable. Avoid broad competence claims without measurable proof.

3. **Savings/free-language check**  
   "Free", "discount", and savings claims must include clear basis and comparable reference conditions.

4. **Review/testimonial integrity check**  
   Do not use synthetic or manipulated testimonials. Do not use sentiment-gated social proof patterns.

5. **Jurisdiction disclosure check**  
   If channel/context requires AI disclosure or special claim treatment, mark requirement and include compliant language variant.

If any check fails:
- set claim status to `unverified`,
- block recommendation from `actionable` status,
- include remediation steps.
---

### Draft: Anti-pattern warning blocks

```md
> [!WARNING] Anti-pattern: Buzzword Positioning
> **What it looks like:** generic "AI-powered end-to-end" language with no segment-specific pain/outcome.
> **Detection signal:** low clarity/relevance in message tests; buyers restate copy in generic category terms.
> **Consequence:** weak differentiation and low message recall.
> **Mitigation:** rewrite as pain + measurable outcome + mechanism + evidence refs.
```

```md
> [!WARNING] Anti-pattern: Unsupported Superlatives
> **What it looks like:** "best", "most advanced", "risk-free", "guaranteed" without substantiation.
> **Detection signal:** no source IDs or legal/compliance evidence for claim.
> **Consequence:** compliance risk and trust loss.
> **Mitigation:** downgrade to hypothesis language or remove claim until validated.
```

```md
> [!WARNING] Anti-pattern: Channel Promise Mismatch
> **What it looks like:** ad promise is materially stronger than landing/sales proof.
> **Detection signal:** high click-through but weak downstream conversion and complaint spikes.
> **Consequence:** poor funnel economics and credibility decay.
> **Mitigation:** enforce message-match QA from first claim exposure through conversion path.
```

```md
> [!WARNING] Anti-pattern: Objection Script Monoculture
> **What it looks like:** one canned response reused for all objection classes.
> **Detection signal:** low progression after objections and increased rep monologue time.
> **Consequence:** avoidable deal loss and lower buyer trust.
> **Mitigation:** classify objection type first; require clarifying question before rebuttal.
```

```md
> [!WARNING] Anti-pattern: Experiment Peeking and Slice Fishing
> **What it looks like:** stopping tests when p-value turns green or claiming wins across many slices without correction.
> **Detection signal:** many short-lived "wins" that fail to replicate post-launch.
> **Consequence:** false positives and unstable messaging decisions.
> **Mitigation:** use predeclared sequential methods, multiplicity correction, and SRM gating.
```

### Draft: Available Tools (real methods only)

---
## Input artifacts to load

Always activate required evidence artifacts before messaging work:

```python
flexus_policy_document(op="activate", args={"p": "/strategy/positioning-map"})
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})
flexus_policy_document(op="activate", args={"p": "/discovery/{study_id}/corpus"})
flexus_policy_document(op="activate", args={"p": "/pain/alternatives-landscape"})
```

Use list calls to discover relevant studies and strategy artifacts:

```python
flexus_policy_document(op="list", args={"p": "/discovery/"})
flexus_policy_document(op="list", args={"p": "/strategy/"})
```

When output is ready:

```python
write_artifact(
  artifact_type="messaging_architecture",
  path="/strategy/messaging",
  data={...},
)
```

Tool usage rules:
1. Do not invent method names or paths.
2. If activation fails for a required artifact, continue in hypothesis mode and record missing evidence.
3. Do not write final-actionable recommendations when confidence is low.
4. Log contradictions and unresolved compliance risks in artifact output.
---

### Draft: Recording and acceptance checklist

---
### Recording requirements

A complete messaging artifact must include:
- declared scope (segment, geography, funnel stage, time window),
- positioning statement with evidence links,
- channel adaptations for key channels,
- objection responses with class and proof,
- test metadata and interpretation outcomes,
- confidence tier and contradictions,
- claim compliance flags,
- refresh cadence.

If any of these sections are missing, output is incomplete and should be treated as draft.

### Acceptance checklist

Before marking the artifact `actionable`, verify:
- every major claim has evidence refs,
- no unsupported superlatives,
- no unresolved SRM/methodology blockers in tests,
- no unresolved contradiction that can flip recommendation,
- no compliance-critical flag left unchecked.
---

### Draft: Schema additions

```json
{
  "messaging_architecture": {
    "type": "object",
    "required": [
      "product_name",
      "created_at",
      "artifact_scope",
      "positioning_statement",
      "message_hierarchy",
      "headline_variants",
      "objection_responses",
      "channel_adaptations",
      "message_tests",
      "evidence_registry",
      "confidence",
      "contradictions",
      "claim_compliance",
      "refresh_policy"
    ],
    "additionalProperties": false,
    "properties": {
      "product_name": {
        "type": "string",
        "description": "Name of the product or offering this messaging architecture describes."
      },
      "created_at": {
        "type": "string",
        "description": "ISO-8601 timestamp when this artifact was created."
      },
      "artifact_scope": {
        "type": "object",
        "required": ["segment_id", "geography", "funnel_stage", "time_window"],
        "additionalProperties": false,
        "properties": {
          "segment_id": {
            "type": "string",
            "description": "Segment identifier used for this messaging output."
          },
          "geography": {
            "type": "string",
            "description": "Primary geographic context for the messaging recommendations."
          },
          "funnel_stage": {
            "type": "string",
            "enum": ["awareness", "consideration", "evaluation", "purchase", "expansion"],
            "description": "Primary funnel stage this messaging architecture is optimized for."
          },
          "time_window": {
            "type": "object",
            "required": ["start_date", "end_date"],
            "additionalProperties": false,
            "properties": {
              "start_date": {
                "type": "string",
                "description": "Inclusive start date for source evidence (YYYY-MM-DD)."
              },
              "end_date": {
                "type": "string",
                "description": "Inclusive end date for source evidence (YYYY-MM-DD)."
              }
            }
          }
        }
      },
      "positioning_statement": {
        "type": "object",
        "required": [
          "full_statement",
          "target_segment",
          "category",
          "key_differentiator",
          "proof_point",
          "primary_alternative",
          "evidence_refs",
          "claim_status"
        ],
        "additionalProperties": false,
        "properties": {
          "full_statement": {
            "type": "string",
            "description": "Final positioning statement text."
          },
          "target_segment": {
            "type": "string",
            "description": "Human-readable target segment phrasing used in the statement."
          },
          "category": {
            "type": "string",
            "description": "Category frame used to make the offering understandable in-market."
          },
          "key_differentiator": {
            "type": "string",
            "description": "Primary differentiation claim being made."
          },
          "proof_point": {
            "type": "string",
            "description": "Concrete proof used to support the differentiation claim."
          },
          "primary_alternative": {
            "type": "string",
            "description": "Main alternative buyers compare against (including status quo if relevant)."
          },
          "evidence_refs": {
            "type": "array",
            "description": "Source IDs from evidence_registry supporting this statement.",
            "minItems": 1,
            "items": {
              "type": "string"
            }
          },
          "claim_status": {
            "type": "string",
            "enum": ["verified", "provisional", "hypothesis"],
            "description": "Verification state for the statement based on evidence quality."
          }
        }
      },
      "message_hierarchy": {
        "type": "object",
        "required": [
          "layer1_hook",
          "layer2_expanded",
          "layer3_proof_points",
          "layer4_objection_bridge"
        ],
        "additionalProperties": false,
        "properties": {
          "layer1_hook": {
            "type": "string",
            "description": "Primary one-sentence hook used above the fold."
          },
          "layer2_expanded": {
            "type": "string",
            "description": "Expanded 2-3 sentence value articulation."
          },
          "layer3_proof_points": {
            "type": "array",
            "description": "Proof points that substantiate the core value proposition.",
            "minItems": 1,
            "items": {
              "type": "object",
              "required": ["point", "source_ids"],
              "additionalProperties": false,
              "properties": {
                "point": {
                  "type": "string",
                  "description": "Proof statement used in messaging."
                },
                "source_ids": {
                  "type": "array",
                  "description": "Evidence source IDs supporting this proof point.",
                  "minItems": 1,
                  "items": {
                    "type": "string"
                  }
                }
              }
            }
          },
          "layer4_objection_bridge": {
            "type": "string",
            "description": "Transitional message connecting value proof to objection-handling context."
          }
        }
      },
      "headline_variants": {
        "type": "array",
        "description": "Headline variants used for testing and channel adaptation.",
        "minItems": 3,
        "items": {
          "type": "object",
          "required": [
            "variant_id",
            "headline",
            "framing_type",
            "target_segment",
            "channel_fit",
            "evidence_refs"
          ],
          "additionalProperties": false,
          "properties": {
            "variant_id": {
              "type": "string",
              "description": "Stable ID for the variant."
            },
            "headline": {
              "type": "string",
              "description": "Headline text."
            },
            "subheadline": {
              "type": "string",
              "description": "Optional supporting subheadline text.",
              "default": ""
            },
            "framing_type": {
              "type": "string",
              "enum": ["problem_led", "outcome_led", "category_led", "proof_led"],
              "description": "Primary framing strategy used by the variant."
            },
            "target_segment": {
              "type": "string",
              "description": "Segment label this variant is intended for."
            },
            "channel_fit": {
              "type": "array",
              "description": "Channels where this variant is approved for use.",
              "minItems": 1,
              "items": {
                "type": "string",
                "enum": [
                  "homepage_hero",
                  "landing_page",
                  "paid_search",
                  "paid_social",
                  "sales_deck",
                  "sales_call",
                  "email_lifecycle"
                ]
              }
            },
            "evidence_refs": {
              "type": "array",
              "description": "Source IDs supporting this variant framing.",
              "minItems": 1,
              "items": {
                "type": "string"
              }
            }
          }
        }
      },
      "objection_responses": {
        "type": "array",
        "description": "Objection-response records with class, response, and proof.",
        "items": {
          "type": "object",
          "required": [
            "objection",
            "objection_type",
            "clarifying_question",
            "response",
            "proof_point",
            "source_ids"
          ],
          "additionalProperties": false,
          "properties": {
            "objection": {
              "type": "string",
              "description": "Original objection phrasing in buyer language."
            },
            "objection_type": {
              "type": "string",
              "enum": [
                "dismissive",
                "situational",
                "existing_solution",
                "price",
                "timing",
                "risk_or_compliance",
                "other"
              ],
              "description": "Objection class used for routing response logic."
            },
            "clarifying_question": {
              "type": "string",
              "description": "Question used to diagnose context before rebuttal."
            },
            "response": {
              "type": "string",
              "description": "Recommended objection response."
            },
            "proof_point": {
              "type": "string",
              "description": "Concrete proof used in the response."
            },
            "source_ids": {
              "type": "array",
              "description": "Evidence source IDs supporting this response strategy.",
              "minItems": 1,
              "items": {
                "type": "string"
              }
            }
          }
        }
      },
      "channel_adaptations": {
        "type": "array",
        "description": "Channel-specific message versions that preserve core narrative.",
        "minItems": 1,
        "items": {
          "type": "object",
          "required": [
            "channel",
            "primary_message",
            "constraints",
            "evidence_refs",
            "risk_notes"
          ],
          "additionalProperties": false,
          "properties": {
            "channel": {
              "type": "string",
              "enum": [
                "homepage_hero",
                "landing_page",
                "paid_search",
                "paid_social",
                "sales_deck",
                "sales_call",
                "email_lifecycle"
              ],
              "description": "Channel this adaptation is designed for."
            },
            "primary_message": {
              "type": "string",
              "description": "Approved channel-specific message text."
            },
            "constraints": {
              "type": "array",
              "description": "Channel constraints considered in the adaptation (length, disclosure, CTA, etc.).",
              "items": {
                "type": "string"
              }
            },
            "evidence_refs": {
              "type": "array",
              "description": "Source IDs supporting this adaptation choice.",
              "minItems": 1,
              "items": {
                "type": "string"
              }
            },
            "risk_notes": {
              "type": "array",
              "description": "Known risks for this adaptation (for example overpromising, compliance caveats).",
              "items": {
                "type": "string"
              }
            }
          }
        }
      },
      "message_tests": {
        "type": "array",
        "description": "Test records used to validate message variants.",
        "items": {
          "type": "object",
          "required": [
            "test_id",
            "method",
            "hypothesis",
            "primary_metric",
            "sample_size",
            "statistical_significance",
            "practical_significance",
            "srm_check",
            "decision"
          ],
          "additionalProperties": false,
          "properties": {
            "test_id": {
              "type": "string",
              "description": "Stable identifier for the test."
            },
            "method": {
              "type": "string",
              "enum": [
                "qual_message_test",
                "ab_test",
                "multivariate_test",
                "sales_call_review"
              ],
              "description": "Testing method used."
            },
            "hypothesis": {
              "type": "string",
              "description": "Predeclared hypothesis for this test."
            },
            "primary_metric": {
              "type": "string",
              "description": "Primary success metric used in decisioning."
            },
            "sample_size": {
              "type": "integer",
              "minimum": 1,
              "description": "Total analyzed sample size for the test."
            },
            "statistical_significance": {
              "type": "object",
              "required": ["alpha", "p_value", "is_significant"],
              "additionalProperties": false,
              "properties": {
                "alpha": {
                  "type": "number",
                  "description": "Significance threshold set before test launch (for example 0.05)."
                },
                "p_value": {
                  "type": "number",
                  "description": "Observed p-value for the primary comparison."
                },
                "is_significant": {
                  "type": "boolean",
                  "description": "Whether p-value crossed alpha under the defined method."
                }
              }
            },
            "practical_significance": {
              "type": "object",
              "required": ["mde", "observed_lift", "meets_threshold"],
              "additionalProperties": false,
              "properties": {
                "mde": {
                  "type": "number",
                  "description": "Minimum detectable effect defined before launch."
                },
                "observed_lift": {
                  "type": "number",
                  "description": "Observed lift on primary metric."
                },
                "meets_threshold": {
                  "type": "boolean",
                  "description": "Whether observed lift meets or exceeds practical threshold."
                }
              }
            },
            "srm_check": {
              "type": "object",
              "required": ["checked", "srm_detected"],
              "additionalProperties": false,
              "properties": {
                "checked": {
                  "type": "boolean",
                  "description": "Whether sample ratio mismatch check was performed."
                },
                "srm_detected": {
                  "type": "boolean",
                  "description": "Whether SRM was detected."
                },
                "notes": {
                  "type": "string",
                  "description": "Optional notes about SRM diagnostics."
                }
              }
            },
            "decision": {
              "type": "string",
              "enum": ["ship", "iterate", "hold", "reject"],
              "description": "Decision taken after interpretation of test evidence."
            }
          }
        }
      },
      "evidence_registry": {
        "type": "array",
        "description": "Source catalog for all evidence used in this artifact.",
        "minItems": 1,
        "items": {
          "type": "object",
          "required": [
            "source_id",
            "source_type",
            "source_name",
            "source_ref",
            "observed_at",
            "reliability_tier"
          ],
          "additionalProperties": false,
          "properties": {
            "source_id": {
              "type": "string",
              "description": "Stable ID referenced elsewhere in this artifact."
            },
            "source_type": {
              "type": "string",
              "enum": [
                "interview_corpus",
                "review_signal",
                "call_intelligence",
                "icp_artifact",
                "positioning_map",
                "alternatives_landscape",
                "experiment_output",
                "other"
              ],
              "description": "Evidence source category used for interpretation and confidence."
            },
            "source_name": {
              "type": "string",
              "description": "Readable source name."
            },
            "source_ref": {
              "type": "string",
              "description": "Internal artifact path or URL pointer for traceability."
            },
            "observed_at": {
              "type": "string",
              "description": "ISO-8601 timestamp when this evidence was observed."
            },
            "reliability_tier": {
              "type": "string",
              "enum": ["high", "medium", "low"],
              "description": "Reliability assessment based on source quality and fit."
            },
            "quote_or_excerpt": {
              "type": "string",
              "description": "Optional direct quote/excerpt used in message construction."
            }
          }
        }
      },
      "confidence": {
        "type": "object",
        "required": ["overall_score", "tier", "is_actionable"],
        "additionalProperties": false,
        "properties": {
          "overall_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Composite confidence score for this messaging architecture."
          },
          "tier": {
            "type": "string",
            "enum": ["high", "medium", "low"],
            "description": "Decision confidence tier."
          },
          "is_actionable": {
            "type": "boolean",
            "description": "Whether evidence quality supports production use."
          },
          "insufficient_evidence_reason": {
            "type": ["string", "null"],
            "description": "Reason output is not actionable when confidence is insufficient."
          }
        }
      },
      "contradictions": {
        "type": "array",
        "description": "Material source contradictions that can affect messaging decisions.",
        "items": {
          "type": "object",
          "required": ["topic", "source_ids", "impact", "resolution_status"],
          "additionalProperties": false,
          "properties": {
            "topic": {
              "type": "string",
              "description": "Short title for the contradiction."
            },
            "source_ids": {
              "type": "array",
              "description": "Conflicting source IDs.",
              "minItems": 2,
              "items": {
                "type": "string"
              }
            },
            "impact": {
              "type": "string",
              "enum": ["high", "medium", "low"],
              "description": "Potential decision impact if unresolved."
            },
            "resolution_status": {
              "type": "string",
              "enum": ["open", "partially_resolved", "resolved"],
              "description": "Current contradiction resolution state."
            },
            "resolution_notes": {
              "type": "string",
              "description": "How this contradiction was resolved or why it remains open."
            }
          }
        }
      },
      "claim_compliance": {
        "type": "object",
        "required": [
          "reviewed",
          "ai_claims_present",
          "savings_claims_present",
          "testimonial_claims_present",
          "requires_legal_review",
          "unsupported_claims"
        ],
        "additionalProperties": false,
        "properties": {
          "reviewed": {
            "type": "boolean",
            "description": "Whether claim compliance review was completed."
          },
          "ai_claims_present": {
            "type": "boolean",
            "description": "Whether messaging includes AI capability claims."
          },
          "savings_claims_present": {
            "type": "boolean",
            "description": "Whether messaging includes savings/free/discount claims."
          },
          "testimonial_claims_present": {
            "type": "boolean",
            "description": "Whether messaging includes testimonial/review-derived claims."
          },
          "requires_legal_review": {
            "type": "boolean",
            "description": "Whether legal/compliance approval is required before publish."
          },
          "unsupported_claims": {
            "type": "array",
            "description": "List of claims that failed substantiation and must not ship.",
            "items": {
              "type": "string"
            }
          }
        }
      },
      "refresh_policy": {
        "type": "object",
        "required": ["cadence", "stale_after_days"],
        "additionalProperties": false,
        "properties": {
          "cadence": {
            "type": "string",
            "enum": ["monthly_delta", "quarterly", "semiannual"],
            "description": "Recommended refresh cadence for this messaging architecture."
          },
          "stale_after_days": {
            "type": "integer",
            "minimum": 1,
            "description": "Maximum age of evidence before messaging is treated as stale."
          },
          "next_review_at": {
            "type": "string",
            "description": "ISO-8601 timestamp for next planned review."
          }
        }
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Public benchmark quality for channel messaging is uneven; several high-volume datasets come from vendor analyses with limited methodological disclosure.
- Many API documentation pages are evergreen and do not provide clear historical change logs for 2024-2026 deltas; operational constraints should be revalidated at implementation time.
- Strong public, cross-industry thresholds for "good" messaging lift remain scarce; most practical thresholds still require domain-specific baseline calibration.
- Regulatory sources indicate clear risk categories, but operational policy translation is jurisdiction-specific and should not be treated as legal advice.
- Objection and call-conversation datasets are strongest in sales-heavy contexts; transferability to purely PLG/self-serve journeys requires caution.
