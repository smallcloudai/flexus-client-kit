# Research: positioning-market-map

**Skill path:** `flexus-client-kit/flexus_simple_bots/strategist/skills/positioning-market-map/`
**Bot:** strategist (researcher | strategist | executor)
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`positioning-market-map` builds an evidence-backed market map from alternatives data, JTBD outcomes, and demand signals so the strategist can identify defensible differentiation and avoid generic "we are better" claims. The current `SKILL.md` already has strong fundamentals (axis orthogonality, claimed vs perceived placement, and white-space caution), but it needs sharper 2024-2026 operating guidance around evidence quality, signal interpretation, and claim governance.

Recent research shows two practical shifts that should shape this skill. First, buying teams form preferences earlier and involve more stakeholders before seller interaction, which makes perception-led evidence and segment-specific mapping more important than one universal map. Second, data-provider methodology changes are frequent (for example in review/traffic ecosystems), which means map quality depends on explicit recency metadata and contradiction handling, not static snapshots.

For this skill to be decision-grade, the map must separate: (a) buyer perception signal, (b) capability/execution signal, and (c) demand validation. Empty quadrants are hypotheses, not opportunities, until demand and viability evidence confirms them.

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

---

## Research Angles

Each angle below was researched through dedicated internal sub-agents and then cross-checked against source pages.

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

Modern positioning work increasingly uses a dual-lens model: one lens for buyer perception and one for provider capability/execution. This is visible in how analyst frameworks and review ecosystems evolved in 2024-2026. Forrester's 2024 Wave changes increased explicit customer-feedback prominence in visual outputs, while G2 continues to separate satisfaction and market-presence dimensions through documented scoring methodology. For this skill, that means one 2x2 should not carry every strategic claim; at minimum, the artifact should explicitly label which lens each conclusion came from.

Axis design is moving from workshop intuition to evidence-first criteria. Practical, repeatable positioning workflows now start with customer decision criteria (interviews/JTBD) and only then construct map axes. Qualtrics guidance for correspondence/perceptual mapping makes this operational: same-option multi-answer structures, minimum attribute count, and minimum response volume before interpreting structure. This directly supports the existing `SKILL.md` guidance that axes must represent real tradeoffs and remain orthogonal.

Practitioners now treat map creation as an iterative cycle, not an annual deliverable. Evidence sources update at different cadences (reviews, traffic proxies, analyst snapshots, field interviews), and frameworks explicitly encourage method transparency and periodic reranking/reweighting. This matches the need to preserve "claimed vs perceived" gap tracking over time, rather than a one-time placement.

White-space discipline remains the largest practical differentiator between good and bad positioning output. Empty quadrants are frequently misread as opportunity. Better practice combines blue-ocean-style factor elimination/reconstruction (evergreen strategic framework) with explicit unmet-outcome validation (JTBD/ODI, evergreen). The quality threshold is simple: no demand signal, no opportunity claim.

Search-demand data should be interpreted as directional and comparative, not as standalone proof. Google Trends explicitly states normalization, sampling, and non-polling limits; therefore, market-map usage should be "signal support," not "primary evidence." This supports requiring triangulation with interviews, review themes, and alternatives evidence before strategic claims.

AI-assisted research synthesis is now accepted, but governance expectations rose in 2024-2025. Professional standards guidance emphasizes transparency, ethics, and human accountability when using AI in research workflows. For this skill, the practical implication is to include provenance in every conclusion and avoid synthetic "confidence theater."

Two contradictory tendencies need explicit handling:
1) stakeholders want simple 2x2 visuals, while rigorous evidence is multi-dimensional;
2) freshest data sources are often least stable/most sampled.
The right resolution is layered output: executive map plus method notes and confidence metadata.

**Sources:**
- Forrester, *Forrester Wave Methodology* (changes effective 2024-07-01): https://www.forrester.com/policies/forrester-wave-methodology/
- G2, *Research Scoring Methodologies* (accessed 2026): https://documentation.g2.com/docs/research-scoring-methodologies
- G2, *Updated algorithm and market presence source changes* (2024): https://company.g2.com/news/g2s-updated-algorithm-brings-more-accuracy-transparency-to-seller-scoring
- Qualtrics, *Correspondence Analysis Widget (perceptual mapping requirements)* (accessed 2026): https://www.qualtrics.com/support/brand-experience/bx-widgets/correspondence-analysis-widget-bx
- Google, *FAQ about Google Trends data* (accessed 2026): https://support.google.com/trends/answer/4365533?hl=en
- Google, *Compare Trends search terms* (accessed 2026): https://support.google.com/trends/answer/4359550?hl=en
- Google Trends, *Year in Search data methodology* (2025): https://trends.withgoogle.com/year-in-search/data-methodology/
- Forrester, *State of Business Buying 2024* (2024): https://www.forrester.com/blogs/state-of-business-buying-2024/
- 6sense (Business Wire), *2024 Buyer Experience Report release* (2024): https://www.businesswire.com/news/home/20241009142556/en/6sense-Launches-2024-Buyer-Experience-Report-Unveiling-Global-B2B-Buyer-Trends
- OECD/JRC, *Composite Indicators 10-Step Guide* (2025): https://knowledge4policy.ec.europa.eu/composite-indicators/toolkit_en/navigation-page/10-step-guide_en
- MRS, *AI Guidance and Related Technologies* (updated 2025): https://www.mrs.org.uk/standards/guidance-on-using-ai-and-related-technologies
- Blue Ocean Strategy (evergreen): https://www.blueoceanstrategy.com/books/blue-ocean-strategy-book/
- Outcome-Driven Innovation/JTBD (evergreen): https://jobs-to-be-done.com/outcome-driven-innovation-odi-is-jobs-to-be-done-theory-in-practice-2944c6ebc40e

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

The practical stack for market-map work now combines five source classes: review intelligence, buyer-intent/search signals, traffic context, company context, and reporting/visualization. No single provider is sufficient; map quality depends on explicit provenance and multi-source triangulation.

Review/perception sources:
- G2 provides a structured dataset with documented API constraints (for example, global request limits and category/report threshold logic). This is high-value for claimed-vs-perceived placement but still needs category-depth checks before interpretation.
- Trustpilot Data Solutions provides verified-review signals beyond software-only categories. Operationally, teams must handle pagination and endpoint window constraints rather than assuming single-call completeness.
- Reddit Data API can add current buyer-language signal, but free access has explicit QPM limits, OAuth requirements, and retention rules for deleted content; this is a high-context source, not a raw truth source.
- YouTube Data API can surface category narratives via comments and thread patterns, but quota management matters because daily unit budgets are finite.

Demand and search context sources:
- Google Search Console API is excellent for first-party demand context (especially your own domain) and has explicit per-site/per-user/per-project quota ceilings.
- Google Ads API keyword-planning paths can be useful for category term interpretation, but strict operation limits and per-method QPS controls require orchestration.
- DataForSEO and Semrush remain useful for broad SERP/keyword context, with documented rate limits, unit/credit systems, and endpoint-specific throttles that should be reflected in ingestion planning.
- Similarweb remains useful for directional market-motion context and large batch workflows, but modeled estimates, credit formulas, and 2024 methodology updates mean continuity and caveat fields are mandatory.

Company context sources:
- SEC EDGAR and Companies House provide high-trust company-state context with explicit fair-access/rate-limit policies.
- Crunchbase can add momentum/viability context where licensing permits, but should not be interpreted as direct buyer-perception truth.

Reporting and delivery surfaces:
- Power BI push models, Google Sheets API, and Looker connector workflows are practical output surfaces, each with concrete throughput and query constraints that affect refresh cadence and map operationalization.

De-facto implementation standard (2024-2026): combine (a) review/perception evidence, (b) search/traffic demand context, and (c) alternatives/JTBD evidence; then publish one executive map plus a traceable evidence table with confidence and caveats.

**Sources:**
- G2 API docs (accessed 2026): https://data.g2.com/api/docs
- G2 methodology docs (accessed 2026): https://documentation.g2.com/docs/research-scoring-methodologies
- Trustpilot Data Solutions API (accessed 2026): https://developers.trustpilot.com/data-solutions-how-to
- Trustpilot pricing (accessed 2026): https://business.trustpilot.com/pricing
- Gartner Digital Markets Buyer Discovery (accessed 2026): https://digital-markets.gartner.com/buyer-discovery
- Semrush API unit balance and limit notes (updated 2026-02-10): https://developer.semrush.com/api/basics/api-units-balance
- DataForSEO rate/request limits (accessed 2026): https://dataforseo.com/help-center/rate-limits-and-request-limits
- DataForSEO pricing (accessed 2026): https://dataforseo.com/pricing
- Similarweb API credit calculations (accessed 2026): https://docs.similarweb.com/api-v5/guides/data-credits-calculations.md
- Similarweb Batch API (accessed 2026): https://support.similarweb.com/hc/en-us/articles/22089634448413-Batch-API
- Crunchbase API usage docs (accessed 2026): https://data.crunchbase.com/docs/using-the-api
- Reddit Data API wiki and limits (accessed 2026): https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki
- YouTube Data API quota model (accessed 2026): https://developers.google.com/youtube/v3/determine_quota_cost
- Google Search Console API limits (accessed 2026): https://developers.google.com/webmaster-tools/limits
- Google Ads API quotas (accessed 2026): https://developers.google.com/google-ads/api/docs/best-practices/quotas
- SEC EDGAR access policy (updated 2024): https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data
- Companies House API rate limits (accessed 2026): https://developer-specs.company-information.service.gov.uk/guides/rateLimiting
- Power BI push semantic model limits (updated 2025): https://learn.microsoft.com/en-us/power-bi/developer/embedded/push-datasets-limitations
- Google Sheets API limits (accessed 2026): https://developers.google.com/workspace/sheets/api/limits
- Looker connector limits (accessed 2026): https://cloud.google.com/looker/docs/studio/limits-of-the-looker-connector

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

Interpretation quality is the core failure point in market maps. The highest-confidence pattern across sources is to separate three checks before any strategic claim: **transparency** (method is disclosed), **representativeness** (signal is fit for your scope), and **decision materiality** (difference is large enough to matter operationally).

Updated 2024-2026 heuristics that should become hard gates in `SKILL.md`:
- Perceptual/correspondence mapping should not be interpreted below practical structure thresholds (minimum three mapped attributes; roughly 50-100 responses as a display floor, with low-confidence treatment in the lower part of that range).
- Review-derived placement should be downgraded when review depth is below known platform threshold ranges (for example, product/category inclusion cutoffs in provider methodology docs).
- Traffic-estimate signals must be treated as directional context, not absolute market share, especially when providers explicitly note small-site visibility limits.
- Search-trend spikes must never be read as absolute demand size; normalized/sampled trend data is a corroboration source only.
- Weighted or modeled sources should still carry uncertainty language; weighting is not evidence that bias is eliminated.

Provider methodology updates are interpretation events. Similarweb's 2024 data-version update and G2's 2024 algorithm/market-presence changes are concrete examples where apparent movement may be methodological, not market-driven. For this skill, comparisons across a known method change require explicit re-baselining and caveats.

Composite scoring and opportunity ranking need sensitivity checks before prioritization. OECD/JRC and AQuA guidance align here: if materially different weights reorder top opportunities, confidence should be capped and recommendations should be conditional.

Common misreads and required corrections:
1) **Misread:** "High response rate means low bias."  
   **Correction:** residual-bias and representativeness checks still apply.
2) **Misread:** "Weighted output is fully corrected."  
   **Correction:** keep uncertainty bands and caveats.
3) **Misread:** "Traffic or trend proxies prove demand."  
   **Correction:** use proxies as directional signals and triangulate.
4) **Misread:** "Any measured delta is strategically meaningful."  
   **Correction:** require materiality relative to decision impact.
5) **Misread:** "One source contradiction can be ignored."  
   **Correction:** log contradiction, lower confidence, and provide scenario output.

**Sources:**
- AAPOR, *Resources and guidance on 2024 pre-election polling* (2024): https://aapor.org/news-releases/aapor-resources-and-guidance-on-2024-pre-election-polling/
- AAPOR, *Polling Accuracy resources* (accessed 2026): https://aapor.org/polling-accuracy/
- Statistics Canada, *A Bias Evaluation for Probabilistic Web Panels* (2025): https://www150.statcan.gc.ca/n1/pub/11-522-x/2025001/article/00009-eng.pdf
- Qualtrics correspondence analysis requirements (accessed 2026): https://www.qualtrics.com/support/brand-experience/bx-widgets/correspondence-analysis-widget-bx
- Google Trends FAQ (accessed 2026): https://support.google.com/trends/answer/4365533?hl=en
- Google Trends Year in Search methodology (2025): https://trends.withgoogle.com/year-in-search/data-methodology/
- Similarweb data accuracy article (updated with 2024 small-site notes): https://support.similarweb.com/hc/en-us/articles/360002219177-Similarweb-s-Data-Accuracy
- Similarweb 2024 data version update (2024): https://support.similarweb.com/hc/en-us/articles/18876356573725-Everything-you-need-to-know-about-Similarweb-s-2024-Data-Version-Update
- SparkToro traffic-estimate comparison (2022, evergreen): https://sparktoro.com/blog/which-3rd-party-traffic-estimate-best-matches-google-analytics
- OECD/JRC 10-step composite-indicator guidance (2025): https://knowledge4policy.ec.europa.eu/composite-indicators/toolkit_en/navigation-page/10-step-guide_en
- UK Government, *The Aqua Book* (2025): https://www.gov.uk/government/publications/the-aqua-book-guidance-on-producing-quality-analysis-for-government
- G2 category/report threshold docs (accessed 2026): https://documentation.g2.com/docs/research-scoring-methodologies
- Forrester Wave methodology update details (2024): https://www.forrester.com/policies/forrester-wave-methodology/

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

1) **Inside-out axis selection**  
What it looks like: axes describe internal pride points, not buyer decision criteria.  
Detection: win/loss and interview evidence explains choice using different factors than map axes.  
Consequence: strong-looking map, weak market relevance.  
Mitigation: derive axes from JTBD + alternatives evidence first, then test against real buyer language.

2) **Average-customer map collapse**  
What it looks like: one map for all segments/geographies.  
Detection: contradictory placement feedback across segments.  
Consequence: diluted positioning and noisy GTM direction.  
Mitigation: maintain segment-specific map views with explicit scope metadata.

3) **Low-N perceptual mapping**  
What it looks like: correspondence/perceptual interpretation from sparse data structure.  
Detection: fewer than three mapped attributes or response volume below practical floor.  
Consequence: unstable placements that look precise but are not reproducible.  
Mitigation: mark output as exploratory-only and block recommendation-grade use until thresholds are met.

4) **Empty quadrant = opportunity fallacy**  
What it looks like: unoccupied space treated as validated white space.  
Detection: low demand corroboration, weak conversion in validation tests.  
Consequence: costly strategy drift into non-viable market space.  
Mitigation: label empty spaces as hypotheses until demand and attainability checks pass.

5) **Snapshot bias**  
What it looks like: one-time scrape/report drives strategic repositioning.  
Detection: no recency metadata, no rolling update logic.  
Consequence: reactive overcorrection.  
Mitigation: monthly delta checks and explicit stale thresholds.

6) **Source monoculture**  
What it looks like: one external data provider determines placement.  
Detection: no triangulation table and no contradiction section.  
Consequence: hidden model bias in final strategy.  
Mitigation: require at least two signal families for placement and three for white space.

7) **Search-proxy overreach**  
What it looks like: trend spikes used as direct market-demand proof.  
Detection: conclusions depend on trend charts without independent corroboration.  
Consequence: strategy follows volatility rather than durable demand.  
Mitigation: use trend/search signals only as directional context and triangulate with interviews/reviews.

8) **Traffic-estimate literalism**  
What it looks like: modeled traffic estimates treated as precise market share.  
Detection: small-site caveats ignored and first-party mismatch unexplained.  
Consequence: incorrect competitor placement and false "market presence" narratives.  
Mitigation: mark as estimated signal class and forbid single-source coordinate assignment.

9) **Methodology-break blindness**  
What it looks like: trend inflections interpreted without provider method-change context.  
Detection: shifts coincide with documented vendor data-version or scoring updates.  
Consequence: phantom repositioning decisions.  
Mitigation: add breakpoints and re-baseline before comparison.

10) **Claim inflation / AI-washing style differentiation**  
What it looks like: "AI-powered" or "best-in-class" claims without evidence.  
Detection: claim has no linked proof artifact or customer outcome.  
Consequence: trust, legal, and brand risk.  
Mitigation: claim-substantiation requirement with source owner and timestamp.

11) **Synthetic proof abuse (reviews/testimonials)**  
What it looks like: manipulated social proof as positioning evidence.  
Detection: unverifiable/inauthentic review patterns.  
Consequence: regulatory exposure and strategic misread of market trust.  
Mitigation: verified evidence only; explicitly reject unsupported testimonial signals.

12) **Uncertainty suppression ("confidence theater")**  
What it looks like: clean executive map with no assumptions/caveats/contradictions.  
Detection: no uncertainty notes, no confidence rationale, no contradiction log.  
Consequence: decision-makers over-trust fragile conclusions.  
Mitigation: make uncertainty and contradiction fields mandatory for recommendation-grade outputs.

13) **Buying-group blindness**  
What it looks like: map optimized for one user persona only.  
Detection: high preference at user level, late-stage stalls in committee deals.  
Consequence: poor conversion despite strong demos.  
Mitigation: include decision-role perspective in evidence review (economic, technical, operational).

14) **Insight starvation under budget pressure**  
What it looks like: map remains static while market evidence collection shrinks.  
Detection: stale references and no refresh history.  
Consequence: strategy decay and weak differentiation over time.  
Mitigation: lightweight recurring evidence loop with minimum monthly/quarterly updates.

**Bad vs good output examples:**

- Bad: "We are top-right in AI sophistication and innovation."  
  Good: "For regulated mid-market teams, we are strongest on deployment speed vs governance burden, supported by interview and review evidence."
- Bad: "No competitor in this quadrant, therefore blue ocean."  
  Good: "Quadrant is unoccupied; marked as hypothesis until demand and attainability checks are validated."
- Bad: "Traffic spike proves category shift toward us."  
  Good: "Traffic signal is directional only; placement updated only after corroborating interview/review/alternatives evidence."
- Bad: "Positioning claim copied from sales deck taglines."  
  Good: "Each claim references source IDs, recency, and confidence tier."

**Sources:**
- Forrester, *State of Business Buying 2024* (2024): https://www.forrester.com/blogs/state-of-business-buying-2024/
- 6sense Buyer Experience report release (2024): https://www.businesswire.com/news/home/20241009142556/en/6sense-Launches-2024-Buyer-Experience-Report-Unveiling-Global-B2B-Buyer-Trends
- SEC, *AI washing enforcement action* (2024): https://www.sec.gov/newsroom/press-releases/2024-36
- FTC, *Final rule banning fake reviews/testimonials* (2024): https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials
- European Parliament, *Ban on greenwashing/misleading product info* (2024): https://www.europarl.europa.eu/news/en/press-room/20240112IPR16772/meps-adopt-new-law-banning-greenwashing-and-misleading-product-information
- Similarweb data version update (2024): https://support.similarweb.com/hc/en-us/articles/18876356573725-Everything-you-need-to-know-about-Similarweb-s-2024-Data-Version-Update
- Similarweb data accuracy notes (accessed 2026): https://support.similarweb.com/hc/en-us/articles/360002219177-Similarweb-s-Data-Accuracy
- Qualtrics correspondence mapping requirements (accessed 2026): https://www.qualtrics.com/support/brand-experience/bx-widgets/correspondence-analysis-widget-bx
- Google Trends FAQ (accessed 2026): https://support.google.com/trends/answer/4365533?hl=en
- AAPOR transparency and polling guidance (2024): https://aapor.org/news-releases/aapor-resources-and-guidance-on-2024-pre-election-polling/
- SparkToro traffic-estimate comparison (2022, evergreen): https://sparktoro.com/blog/which-3rd-party-traffic-estimate-best-matches-google-analytics
- Gartner CMO budget pressure release (2024): https://www.gartner.com/en/newsroom/press-releases/2024-05-13-gartner-cmo-survey-reveals-marketing-budgets-have-dropped-to-seven-point-seven-percent-of-overall-company-revenue-in-2024

---

### Angle 5+: Evidence Governance, Claim Integrity, and Responsible Positioning
> Domain-specific angle: how to keep differentiation claims legally and methodologically defensible when output is used in GTM messaging.

**Findings:**

Positioning outputs are increasingly reused as public claims, so research quality and claim governance cannot be separated. 2024 enforcement and policy updates across US/EU show that misleading or unsubstantiated claims (including AI-related and testimonial-related) are active regulatory targets, not theoretical risk.

For this skill, the practical implication is to require claim provenance in the artifact itself. If a differentiation statement cannot be traced to timestamped evidence and confidence level, it should be downgraded to hypothesis language and blocked from "final recommendation" status.

Research standards communities updated AI-usage guidance in 2025 to emphasize legality, transparency, and ethics for AI-assisted analysis. This aligns with adding a simple but strict output rule: the artifact must disclose where evidence came from, what is inferred, and where uncertainty remains.

A second implication is review/testimonial hygiene. If market-map conclusions rely on manipulated or low-trust social proof, downstream GTM decisions inherit that risk. Therefore, evidence registry fields must distinguish verified vs unverified signal classes.

**Sources:**
- SEC AI-related enforcement (2024): https://www.sec.gov/newsroom/press-releases/2024-36
- FTC fake reviews final rule (2024): https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials
- European Parliament greenwashing/misleading-info directive update (2024): https://www.europarl.europa.eu/news/en/press-room/20240112IPR16772/meps-adopt-new-law-banning-greenwashing-and-misleading-product-information
- MRS AI guidance update (2025): https://www.mrs.org.uk/standards/guidance-on-using-ai-and-related-technologies
- AAPOR transparency guidance (2024): https://aapor.org/news-releases/aapor-resources-and-guidance-on-2024-pre-election-polling/

---

## Synthesis

The main conclusion is that this skill should evolve from "draw a 2x2" into "produce a defensible positioning decision artifact." Sources strongly support dual-lens logic (buyer perception plus provider capability) and triangulated evidence over single-feed mapping.

The biggest contradiction is between executive need for simplicity and methodological reality. A single clean map is useful communication, but a single-layer map hides uncertainty, source limitations, and segment variation. The practical resolution is not more complexity in the visual itself; it is stronger metadata and confidence handling behind it.

Another contradiction is speed vs reliability. Fresh web/review/traffic signals are useful for rapid updates but are also most sensitive to methodology drift, sampling effects, and small-site limitations. This implies strict recency fields, break-point notes, and explicit contradiction reporting before recommendations.

Most actionable improvement: force white-space and differentiation claims through evidence gates. If a space is empty but demand is unproven, label it hypothesis. If a claim is strong but provenance is weak, downgrade confidence. This single discipline reduces the majority of observed anti-patterns.

---

## Recommendations for SKILL.md

- [x] Add a **dual-lens methodology**: one lens for buyer perception and one for supplier capability/execution, with explicit labeling in outputs.
- [x] Add **axis validation and input quality gates** (minimum attribute/response expectations, orthogonality checks, and segment scope declaration).
- [x] Add a **triangulation rule** for placement and white-space claims (multi-source requirement + contradiction logging).
- [x] Add **confidence tiers and insufficient-evidence behavior** before final differentiation recommendations.
- [x] Add explicit **recency and refresh cadence rules** (monthly delta + quarterly synthesis).
- [x] Add **method-version and breakpoint controls** so pre/post methodology shifts are not interpreted as market movement.
- [x] Add named **anti-pattern warning blocks** with detection signals and mitigation steps.
- [x] Expand `## Available Tools` with real call syntax only, plus source-provenance and rate-limit hygiene expectations.
- [x] Extend the artifact schema with **evidence registry, confidence, contradictions, refresh policy, and method-change log** fields.
- [x] Add **claim-governance guardrails** so unsubstantiated positioning statements remain hypotheses.

---

## Draft Content for SKILL.md

### Draft: Core methodology upgrade

---
### Positioning operating model (dual-lens, evidence-first)

You must build market positioning maps using two explicit lenses:
1. **Buyer perception lens**: how buyers actually perceive options.
2. **Capability/execution lens**: what providers can reliably deliver.

Do not merge these lenses into one implicit score. If you combine them without labeling, you hide contradictions and produce false clarity.

Before you place any competitor:

1. Declare map scope in plain language:
   - target segment,
   - geography,
   - time window,
   - decision context (selection, replacement, expansion, or category entry).
2. State which lens each conclusion uses.
3. Record at least one direct source for each lens.

If lens signals disagree, you must keep the disagreement visible in output. Do not average conflicting signals into one coordinate without notes.

Do NOT write conclusions like "we are best" or "top-right means winner." Positioning is relative and context-dependent.
---

### Draft: Axis selection and evidence gates

---
### Axis selection

Choose axes that represent buyer-relevant tradeoffs, not internal slogans.

Axis requirements:
1. Each axis must be tied to observed buyer criteria from JTBD and alternatives evidence.
2. Axes must be clearly non-duplicative (avoid semantic overlap like "easy" vs "intuitive").
3. Each axis must include low/high endpoint definitions that can be interpreted by another strategist without extra context.

Minimum quality checks before axis lock:
- Use at least three mapped attributes when using correspondence/perceptual workflows.
- Do not interpret sparse respondent data; if data volume is weak, downgrade confidence and continue as hypothesis only.
- If review/category evidence does not meet minimum viability thresholds, mark that source class as weak and do not let it dominate placement.

If you cannot justify axis relevance with evidence, replace the axis. Do not continue with "best guess" axis labels.

### Competitor placement protocol

For each competitor, collect and compare:
1. Claimed positioning (marketing narrative),
2. Perceived positioning (review/interview signal),
3. Execution evidence (capability delivery or viability context),
4. Recency metadata.

Then assign:
- x/y placement,
- placement confidence,
- source references.

If claimed and perceived positions diverge, preserve both and explain the delta.

Do NOT collapse divergence into one polished sentence. Divergence is often the most actionable finding.
---

### Draft: White-space validation protocol

---
### White-space identification and validation

Treat every empty quadrant as a hypothesis until validated.

Use this sequence:
1. Identify empty or weakly populated region.
2. Check demand evidence from signals and customer pain.
3. Check attainability (can your team credibly deliver this position in the planning horizon?).
4. Check economic/segment viability.
5. Assign status:
   - `hypothesis` (insufficient validation),
   - `validated` (demand and attainability supported),
   - `rejected` (evidence indicates non-viable space).

If demand signal is weak or contradictory, keep status `hypothesis`.
If demand appears strong but attainability is weak, do not recommend immediate positioning shift; propose staged tests instead.

Never label white space as blue-ocean opportunity from map geometry alone.
---

### Draft: Interpretation, confidence, and contradiction handling

---
### Signal interpretation and confidence rules

You must evaluate signal quality before strategic interpretation.

Interpretation principles:
1. Transparency is required but not sufficient.
2. Weighted or modeled sources can still contain residual bias.
3. Traffic/search/review proxies are directional unless corroborated.
4. Methodology changes in source systems can create synthetic trend shifts.

Confidence assignment:
- `high`: multi-source agreement, recent evidence, and no unresolved major contradictions.
- `medium`: partial agreement, moderate uncertainty, or one material caveat.
- `low`: single-source dependence, stale evidence, or unresolved contradiction that can change decision direction.

If confidence is low:
- output must remain descriptive,
- no hard differentiation verdict,
- no priority recommendation without follow-up evidence plan.

### Contradiction protocol

If two credible sources disagree materially:
1. Name the contradiction explicitly.
2. Explain likely reason (scope, method, timeframe, population, or provider methodology update).
3. Reduce confidence tier.
4. Prefer range- or scenario-based guidance over single-point claims.

Do NOT silently choose one source and suppress the disagreement.
---

### Draft: Signal quality gates and method-break controls

---
### Signal quality gates (hard requirements)

Before you assign recommendation-grade placement, pass all applicable gates:

1. **Perceptual structure gate**
   - If using correspondence/perceptual evidence, require at least three mapped attributes.
   - If response volume is below practical floor (around 50), block recommendation-grade interpretation.
   - If response volume is in low-confidence range (about 50-100), allow exploratory use only with explicit caveat.

2. **Review depth gate**
   - If review base is below platform threshold ranges for meaningful category interpretation, downgrade confidence.
   - Do not let sparse review data dominate coordinates or white-space claims.

3. **Traffic and trend gate**
   - Treat modeled traffic and normalized trend data as directional signals only.
   - Never use trend spikes as standalone proof of market demand or winner status.

4. **Triangulation gate**
   - Competitor placement requires at least two independent signal families.
   - White-space recommendation requires at least three signal families including one non-modeled source class.

5. **Materiality gate**
   - A measurable delta is not enough; require that the delta is decision-relevant in your GTM context.

If any gate fails, downgrade confidence and output hypothesis language instead of final recommendation language.

### Method-break protocol

When a provider changes scoring, coverage, or data methodology:
1. Mark the break event with date and source.
2. Split analysis into pre-break and post-break windows.
3. Re-baseline trend comparisons.
4. Lower confidence until consistency is re-established with independent sources.

Do NOT narrate structural provider changes as market behavior without re-baselining.
---

### Draft: Anti-pattern warning blocks

```md
> [!WARNING] Anti-pattern: Inside-Out Axes
> **What it looks like:** axis labels mirror internal product pride, not buyer decision criteria.
> **Detection signal:** win/loss reasons do not match axis logic.
> **Consequence:** positioning appears differentiated but fails in market selection.
> **Mitigation:** derive axes from JTBD + alternatives evidence, then revalidate with buyer language.
```

```md
> [!WARNING] Anti-pattern: Empty Quadrant = Opportunity
> **What it looks like:** unoccupied map area is treated as validated white space.
> **Detection signal:** no demand proof, weak willingness-to-pay evidence, low conversion in tests.
> **Consequence:** strategy shifts into low-viability territory.
> **Mitigation:** mark as hypothesis and require demand + attainability validation before recommendation.
```

```md
> [!WARNING] Anti-pattern: Snapshot Positioning
> **What it looks like:** one-time data pull drives durable positioning decision.
> **Detection signal:** missing recency metadata and no refresh cadence.
> **Consequence:** overreaction to temporary signal noise or provider methodology artifacts.
> **Mitigation:** enforce monthly delta checks and quarterly synthesis before strategic changes.
```

```md
> [!WARNING] Anti-pattern: Source Monoculture
> **What it looks like:** one external source controls placement and conclusions.
> **Detection signal:** no triangulation table and no contradiction log.
> **Consequence:** hidden source bias becomes strategy bias.
> **Mitigation:** require multiple independent signal families and explicit contradiction handling.
```

```md
> [!WARNING] Anti-pattern: Unsubstantiated Differentiation Claims
> **What it looks like:** claims such as "AI-powered", "most trusted", or "eco" without linked evidence.
> **Detection signal:** claim has no source ID, no owner, or no timestamp.
> **Consequence:** trust, compliance, and execution risk.
> **Mitigation:** enforce claim registry and downgrade unsupported claims to hypothesis status.
```

### Draft: Available Tools

---
## Available Tools

Use only methods that are explicitly available. Do not invent method names, endpoints, or artifact paths.

```python
flexus_policy_document(op="activate", args={"p": "/pain/alternatives-landscape"})
flexus_policy_document(op="activate", args={"p": "/discovery/{study_id}/jtbd-outcomes"})
flexus_policy_document(op="list", args={"p": "/signals/"})
flexus_policy_document(op="list", args={"p": "/strategy/"})
```

After completing map construction and quality checks:

```python
write_artifact(
  artifact_type="market_positioning_map",
  path="/strategy/positioning-map",
  data={...},
)
```

Tool usage rules:
1. Activate required policy docs before mapping.
2. If required evidence is unavailable, return low-confidence output with explicit gaps.
3. Record where each placement came from; do not output coordinates without source notes.
4. If a tool call fails or data is blocked, log the gap and continue with available validated evidence.
5. For external source evidence, record retrieval timestamp and any known provider method/version context.
6. Respect documented source limits (rate, quota, credit) in your evidence plan; do not assume unlimited pull capacity.
7. If source recency or coverage is weak, lower confidence and keep claim language conditional.
8. Never introduce unverified endpoints or methods in guidance text.
---

### Draft: Recording and output quality requirements

---
### Recording

A complete output is not just a chart. You must record:
- map scope (segment, geography, time window),
- lens type for each major conclusion,
- evidence references for each placement and claim,
- white-space status (`hypothesis`/`validated`/`rejected`),
- confidence tier and unresolved contradictions,
- refresh policy and stale threshold.

If this metadata is missing, the artifact is incomplete and should not be treated as action-ready.

### Decision rules

- If placement confidence is low or contradictions are unresolved: do not recommend hard positioning shift.
- If white space is not validated: keep as exploration hypothesis.
- If differentiation claim has weak provenance: mark as provisional and require additional evidence.

Do NOT produce definitive positioning language when evidence quality is medium/low.
---

### Draft: Schema additions

> Full JSON Schema fragment for an upgraded `market_positioning_map` artifact.

```json
{
  "market_positioning_map": {
    "type": "object",
    "required": [
      "problem_space",
      "mapped_at",
      "mapping_scope",
      "map_lenses",
      "axis_x",
      "axis_y",
      "competitors",
      "white_spaces",
      "differentiation_opportunities",
      "evidence_registry",
      "confidence",
      "contradictions",
      "refresh_policy",
      "method_change_log"
    ],
    "additionalProperties": false,
    "properties": {
      "problem_space": {
        "type": "string",
        "description": "Short description of the market/problem area this map evaluates."
      },
      "mapped_at": {
        "type": "string",
        "description": "ISO-8601 timestamp when the map was produced."
      },
      "mapping_scope": {
        "type": "object",
        "required": ["segment", "geography", "time_window"],
        "additionalProperties": false,
        "properties": {
          "segment": {
            "type": "string",
            "description": "Target customer segment used for this map (for example: mid-market regulated ops)."
          },
          "geography": {
            "type": "string",
            "description": "Primary geographic scope represented in evidence and placements."
          },
          "time_window": {
            "type": "object",
            "required": ["start_date", "end_date"],
            "additionalProperties": false,
            "properties": {
              "start_date": {
                "type": "string",
                "description": "Inclusive start date for evidence considered (YYYY-MM-DD)."
              },
              "end_date": {
                "type": "string",
                "description": "Inclusive end date for evidence considered (YYYY-MM-DD)."
              }
            }
          }
        }
      },
      "map_lenses": {
        "type": "array",
        "description": "Lenses used to construct and interpret map conclusions.",
        "minItems": 1,
        "items": {
          "type": "string",
          "enum": ["buyer_perception", "capability_execution"]
        }
      },
      "axis_x": {
        "type": "object",
        "required": [
          "label",
          "low_description",
          "high_description",
          "evidence_basis",
          "selection_evidence"
        ],
        "additionalProperties": false,
        "properties": {
          "label": {
            "type": "string",
            "description": "Axis label that describes a buyer-relevant tradeoff."
          },
          "low_description": {
            "type": "string",
            "description": "Meaning of low-end position on the axis."
          },
          "high_description": {
            "type": "string",
            "description": "Meaning of high-end position on the axis."
          },
          "evidence_basis": {
            "type": "string",
            "description": "Plain-language explanation of evidence used to select this axis."
          },
          "selection_evidence": {
            "type": "array",
            "description": "Source IDs supporting axis relevance and interpretability.",
            "items": {
              "type": "string"
            }
          }
        }
      },
      "axis_y": {
        "type": "object",
        "required": [
          "label",
          "low_description",
          "high_description",
          "evidence_basis",
          "selection_evidence"
        ],
        "additionalProperties": false,
        "properties": {
          "label": {
            "type": "string",
            "description": "Axis label that describes a buyer-relevant tradeoff."
          },
          "low_description": {
            "type": "string",
            "description": "Meaning of low-end position on the axis."
          },
          "high_description": {
            "type": "string",
            "description": "Meaning of high-end position on the axis."
          },
          "evidence_basis": {
            "type": "string",
            "description": "Plain-language explanation of evidence used to select this axis."
          },
          "selection_evidence": {
            "type": "array",
            "description": "Source IDs supporting axis relevance and interpretability.",
            "items": {
              "type": "string"
            }
          }
        }
      },
      "competitors": {
        "type": "array",
        "description": "Competitor placements with claimed/perceived comparison and evidence links.",
        "items": {
          "type": "object",
          "required": [
            "name",
            "x_score",
            "y_score",
            "claimed_position",
            "perceived_position",
            "evidence",
            "placement_confidence",
            "source_ids",
            "last_verified_at"
          ],
          "additionalProperties": false,
          "properties": {
            "name": {
              "type": "string",
              "description": "Competitor or alternative name."
            },
            "x_score": {
              "type": "number",
              "minimum": 0,
              "maximum": 10,
              "description": "Placement score on x-axis (0-10) for this map scope."
            },
            "y_score": {
              "type": "number",
              "minimum": 0,
              "maximum": 10,
              "description": "Placement score on y-axis (0-10) for this map scope."
            },
            "claimed_position": {
              "type": "string",
              "description": "Position implied by the competitor's own messaging."
            },
            "perceived_position": {
              "type": "string",
              "description": "Position implied by external perception signals."
            },
            "evidence": {
              "type": "string",
              "description": "Short narrative justifying placement and notable caveats."
            },
            "placement_confidence": {
              "type": "string",
              "enum": ["high", "medium", "low"],
              "description": "Confidence in this competitor placement given evidence quality and consistency."
            },
            "source_ids": {
              "type": "array",
              "description": "Evidence source IDs supporting this placement.",
              "items": {
                "type": "string"
              }
            },
            "last_verified_at": {
              "type": "string",
              "description": "ISO-8601 timestamp of last evidence verification for this competitor."
            }
          }
        }
      },
      "white_spaces": {
        "type": "array",
        "description": "Potential opportunity spaces with explicit validation state.",
        "items": {
          "type": "object",
          "required": [
            "description",
            "demand_evidence",
            "viability",
            "status",
            "viability_confidence",
            "source_ids"
          ],
          "additionalProperties": false,
          "properties": {
            "description": {
              "type": "string",
              "description": "Description of the potential space in buyer/problem terms."
            },
            "demand_evidence": {
              "type": "string",
              "description": "Summary of demand signals supporting or weakening this space."
            },
            "viability": {
              "type": "string",
              "enum": ["confirmed", "likely", "speculative"],
              "description": "Legacy viability label retained for backward compatibility."
            },
            "status": {
              "type": "string",
              "enum": ["hypothesis", "validated", "rejected"],
              "description": "Validation state after demand and attainability checks."
            },
            "viability_confidence": {
              "type": "string",
              "enum": ["high", "medium", "low"],
              "description": "Confidence in viability decision for this space."
            },
            "source_ids": {
              "type": "array",
              "description": "Evidence source IDs used to evaluate this white-space candidate.",
              "items": {
                "type": "string"
              }
            }
          }
        }
      },
      "differentiation_opportunities": {
        "type": "array",
        "description": "Prioritized differentiation options with demand/underserved/attainability logic.",
        "items": {
          "type": "object",
          "required": [
            "opportunity",
            "demand_score",
            "underserved_score",
            "attainability_score",
            "priority",
            "evidence"
          ],
          "additionalProperties": false,
          "properties": {
            "opportunity": {
              "type": "string",
              "description": "Concise differentiation statement tied to a specific segment context."
            },
            "demand_score": {
              "type": "number",
              "minimum": 0,
              "maximum": 1,
              "description": "Normalized demand evidence score (0-1)."
            },
            "underserved_score": {
              "type": "number",
              "minimum": 0,
              "maximum": 1,
              "description": "Normalized score for how underserved this need appears in the target segment."
            },
            "attainability_score": {
              "type": "number",
              "minimum": 0,
              "maximum": 1,
              "description": "Normalized score for practical ability to deliver and defend this position."
            },
            "priority": {
              "type": "string",
              "enum": ["high", "medium", "low"],
              "description": "Priority tier after combining demand, underserved level, and attainability."
            },
            "evidence": {
              "type": "string",
              "description": "Short rationale that cites strongest evidence and key caveats."
            }
          }
        }
      },
      "evidence_registry": {
        "type": "array",
        "description": "Central source catalog used by this artifact for traceability and auditability.",
        "items": {
          "type": "object",
          "required": [
            "source_id",
            "source_type",
            "source_name",
            "source_url",
            "observed_at",
            "recency_days",
            "reliability_tier",
            "source_method_version"
          ],
          "additionalProperties": false,
          "properties": {
            "source_id": {
              "type": "string",
              "description": "Stable identifier referenced by other fields in this artifact."
            },
            "source_type": {
              "type": "string",
              "enum": [
                "customer_interview",
                "review_platform",
                "traffic_intel",
                "search_signal",
                "analyst_framework",
                "internal_artifact",
                "other"
              ],
              "description": "Source class used for confidence weighting and interpretation context."
            },
            "source_name": {
              "type": "string",
              "description": "Human-readable source name."
            },
            "source_url": {
              "type": "string",
              "description": "Canonical URL or internal path for the source."
            },
            "observed_at": {
              "type": "string",
              "description": "ISO-8601 timestamp when this source was observed/retrieved."
            },
            "recency_days": {
              "type": "integer",
              "minimum": 0,
              "description": "Age of source in days at artifact generation time."
            },
            "reliability_tier": {
              "type": "string",
              "enum": ["high", "medium", "low"],
              "description": "Practical reliability assessment based on methodology transparency and fit."
            },
            "source_method_version": {
              "type": "string",
              "description": "Provider-declared algorithm/model/method version where applicable."
            },
            "notes": {
              "type": "string",
              "description": "Optional caveats (for example: modeled estimate, low coverage, or method update period)."
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
            "description": "Composite confidence score for this map output."
          },
          "tier": {
            "type": "string",
            "enum": ["high", "medium", "low"],
            "description": "Mapped confidence tier for decision use."
          },
          "is_actionable": {
            "type": "boolean",
            "description": "Whether evidence quality is sufficient for strategic recommendations."
          },
          "insufficient_evidence_reason": {
            "type": ["string", "null"],
            "description": "Specific reason when confidence is not sufficient for action."
          }
        }
      },
      "contradictions": {
        "type": "array",
        "description": "Material source contradictions that may change interpretation or decision priority.",
        "items": {
          "type": "string"
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
            "description": "Intended refresh rhythm for this map."
          },
          "stale_after_days": {
            "type": "integer",
            "minimum": 1,
            "description": "Maximum source age in days before the artifact should be treated as stale."
          },
          "next_review_at": {
            "type": "string",
            "description": "ISO-8601 timestamp for next planned review."
          }
        }
      },
      "method_change_log": {
        "type": "array",
        "description": "Known external source methodology changes that can affect trend continuity.",
        "items": {
          "type": "object",
          "required": ["source_name", "change_date", "change_summary", "impact_assessment"],
          "additionalProperties": false,
          "properties": {
            "source_name": {
              "type": "string",
              "description": "Name of the source provider with a documented methodology change."
            },
            "change_date": {
              "type": "string",
              "description": "ISO-8601 date when the source change took effect."
            },
            "change_summary": {
              "type": "string",
              "description": "Brief description of the methodology or data-model change."
            },
            "impact_assessment": {
              "type": "string",
              "enum": ["high", "medium", "low", "unknown"],
              "description": "Estimated impact of this change on trend comparability and interpretation."
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

- Publicly accessible, universally comparable market-map benchmark datasets remain limited; many high-value sources are contract-gated or category-specific.
- Several source pages expose operational limits and methodology but not full sampling internals, so some confidence assignments remain partially heuristic.
- Perceptual-map response volume guidance is practical rather than universal; required sample sizes vary by category complexity and segmentation depth.
- Independent third-party traffic-quality studies are still limited in scale and age; they are useful directional caution, not definitive calibration standards.
- Regulatory references here support claim-governance guardrails, but this document is operational guidance and not legal advice.
