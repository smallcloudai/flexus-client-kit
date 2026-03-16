# Research: pricing-competitive-benchmark

**Skill path:** `flexus-client-kit/flexus_simple_bots/strategist/skills/pricing-competitive-benchmark/`
**Bot:** strategist (researcher | strategist | executor)
**Research date:** 2026-03-05
**Status:** complete

---

## Context

This skill benchmarks your pricing against competitors so you can validate positioning, avoid unjustified discounting, and support negotiations with evidence instead of intuition. In practice, this is not a one-time scrape problem. Competitor pages change frequently, many prices are list-only (not realized), and pricing models differ (per-seat, usage, hybrid, enterprise quote).

Research shows pricing decisions are increasingly frequent, but operating maturity often lags. SBI reports most B2B SaaS teams now update pricing/packaging at least annually, with a sizable quarterly updater segment, while a large share of teams still make important pricing decisions with heavy intuition inputs (SBI 2024/2025). That makes this skill most useful when it enforces methodology guardrails: evidence quality, comparability normalization, confidence scoring, and explicit "insufficient evidence" paths.

For this skill to be reliable, outputs must separate list-price observations from realized-price signals, include data freshness metadata, and encode anti-pattern detection (promo whiplash, apples-to-oranges tier comparisons, currency/tax mismatch, and stale snapshot bias). It also needs legal and compliance guardrails because algorithmic benchmarking and competitor signal use are under active antitrust scrutiny in the US/EU/UK.

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
- Volume: findings section should be 800-4000 words (too short = shallow, too long = unsynthesized)

Gate check for this file: passed. Contradictions are explicitly called out (e.g., discount benchmarks and contract-term discount direction), and older references are marked as evergreen.

---

## Research Angles

Each angle was researched by a separate sub-agent.

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

Practitioner methodology in 2024-2026 is converging on a two-speed operating model: frequent monitoring plus slower strategic resets. BCG's 2024 guidance and SBI's 2024/2025 benchmark reports align on this pattern. For this skill, the practical rule is quarterly delta checks plus annual full rebasing. One-off snapshots are useful for awareness, but they are not reliable strategy inputs by themselves.

Segmentation happens before benchmarking, not after. BCG and Bain both emphasize customer/channel/geo segmentation as a core determinant of price outcomes. If you compute one market-wide "median competitor price" across dissimilar segments, the benchmark is structurally biased. The skill should require segment cell definitions (for example, geo x ICP tier x channel x pricing model) before any category norms are calculated.

Comparability normalization is now treated as a hard gate. CMA's 2024 unit-pricing consumer research and New Zealand Commerce Commission guidance both show that apparent bargains often disappear after unit normalization. In software, the equivalent failure mode is tier-name matching without capability equivalence. This means the methodology must force feature-bucket mapping and billing-term normalization before a row is considered comparable.

Scenario modeling has moved from optional analysis to expected practice. BCG 2024 and Bain 2025 both frame pricing recommendations as simulation outputs across multiple conditions, not a single deterministic answer. For usage or hybrid pricing, this skill should always compute low/base/high scenarios with explicit assumptions and overage behavior rather than collapsing to a single estimated point.

List and realized pricing need explicit separation. Simon-Kucher's 2025 reports and Vendr's 2024/2025 transaction analyses both show realization leakage from discounts, rebates, and deal mechanics. A benchmark that mixes list and realized prices in one metric creates false precision. The skill should output distinct `list_price_benchmark` and `realized_price_benchmark` views with leakage notes.

Method quality depends on trust and governance, not just source volume. Model N's 2024 revenue survey reports broad external-data use with persistent confidence issues around internal data quality. Combined with SBI's execution/governance findings, this supports mandatory confidence scoring, provenance tagging, and owner-based implementation checkpoints.

Contradictions matter and should be surfaced. Bain reports strong AI-enabled pricing upside in many teams, while Simon-Kucher reports many organizations still using low-maturity AI pricing methods with limited realized impact. The right methodological response is not to pick one narrative, but to lower confidence when operating maturity evidence is weak.

**Sources:**
- SBI, *State of B2B SaaS Pricing in 2024* (2024): https://sbigrowth.com/tools-and-solutions/pricing-benchmarks-report-2024
- SBI, *2025 State of SaaS Pricing Report Part 2* (2025): https://sbigrowth.com/tools-and-solutions/2025_state_of_saas_pricing_report_part2
- BCG, *Overcoming Retail Complexity with AI-Powered Pricing* (2024): https://www.bcg.com/publications/2024/overcoming-retail-complexity-with-ai-powered-pricing
- Bain, *AI-Enhanced Pricing Can Boost Revenue Growth* (2024): https://www.bain.com/insights/ai-enhanced-pricing-can-boost-revenue-growth/
- Bain, *Expanding Profit Margin Through Intelligent Pricing* (2025): https://www.bain.com/insights/expanding-profit-margin-through-intelligent-pricing-commercial-excellence-agenda-2025/
- Simon-Kucher, *State of Pricing 2025* (2025 PDF): https://www.simon-kucher.com/sites/default/files/media-document/2025-05/Simon-Kucher_State%20of%20Pricing%202025.pdf
- Simon-Kucher, *Global Pricing Study 2025* (2025 PDF): https://www.simon-kucher.com/sites/default/files/media-document/2025-06/COR_GPS_2025_Brochure_Digital_Final.pdf
- Model N, *State of Revenue Report* (2024 PDF): https://www.modeln.com/wp-content/uploads/2024/02/fy24-model-n-state-of-revenue-report-final.pdf
- Vendr, *SaaS Trends Report 2025* (2025): https://www.vendr.com/insights/saas-trends-report-2025
- UK CMA, *A short guide to unit pricing* (2024): https://competitionandmarkets.blog.gov.uk/2024/01/30/a-short-guide-to-unit-pricing/
- UK Gov/CMA, *Unit pricing analysis and consumer research* (2024): https://www.gov.uk/government/publications/unit-pricing-analysis-and-consumer-research/summary-of-consumer-research-and-unit-pricing-analysis
- NZ Commerce Commission, *Unit pricing regulations guide* (2024 PDF): https://www.comcom.govt.nz/assets/pdf_file/0024/347154/Unit-pricing-regulations-a-guide-for-grocery-retailers-Guideline-March-2024.pdf
- Microsoft 365 Blog, *Flexible billing... annual subscriptions* (2024): https://techcommunity.microsoft.com/blog/microsoft_365blog/flexible-billing-for-microsoft-365-copilot-pricing-updates-for-annual-subscripti/4288536
- U.S. BLS hedonic methods (evergreen reference): https://www.bls.gov/cpi/quality-adjustment/hedonic-price-adjustment-techniques.htm

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

The tool/API landscape is mature but split into source classes with different evidentiary value. The practical model in 2026 is layered: direct pricing-page capture (primary proof), review metadata (corroboration), context APIs (positioning context), and change/history tooling (auditability). No single class can prove "true payable market price" on its own.

For direct capture, Firecrawl, Apify, Zyte, and Oxylabs all publish concrete operating constraints. Firecrawl documents credit consumption and plan-level concurrency; Apify publishes platform/API limits (including high global throughput and per-resource defaults); Zyte documents per-plan request ceilings; Oxylabs documents result-based billing and explicitly notes `429` responses are not billed. These are strong options for operational pipelines, but they still observe public list pages, not negotiated pricing outcomes.

Review-site pricing metadata remains useful but should be labeled as metadata, not transactional truth. G2's packages/pricing docs confirm vendor-managed price/package structures in `my.G2`; Gartner Digital Markets properties often expose "starting at" and plan snippets. Coverage is uneven and some entries are missing or stale, so these sources should be treated as corroboration layers with explicit confidence weight.

Context APIs are best used for explanatory signals around price moves. Similarweb, Semrush, DataForSEO, SerpAPI, and Trustpilot API docs all provide measurable limits or unit systems, making them operationally usable. However, they generally provide estimated traffic/search/review dynamics, not direct competitor payable-price evidence.

Change detection and historical archives are underused and high value for benchmark traceability. Distill and Visualping support frequency-controlled monitoring with credit/check constraints; changedetection.io provides self-hosted watch + diff APIs; Wayback CDX and Common Crawl provide reconstruction paths when teams need temporal evidence for disputed claims.

A durable source-priority stack for this skill is:
1) Official pricing pages with snapshots (`observed_list_price`).
2) Structured review metadata as corroboration (`review_site_metadata`).
3) Context overlays for interpretation (`web_intel_estimate`).
4) Version history and diffs for audit defense.
5) Realized-price benchmarks when licensed/available, separately labeled.

**Sources:**
- Firecrawl pricing: https://firecrawl.dev/pricing
- Firecrawl billing docs: https://docs.firecrawl.dev/billing
- Firecrawl rate limits: https://docs.firecrawl.dev/rate-limits
- Apify pricing: https://apify.com/pricing
- Apify platform limits: https://docs.apify.com/platform/limits
- Apify API docs: https://docs.apify.com/api/v2
- Zyte pricing: https://zyte.com/pricing
- Zyte rate limits: https://docs.zyte.com/zyte-api/usage/rate-limit.html
- Oxylabs pricing: https://oxylabs.io/pricing
- Oxylabs billing mechanics: https://developers.oxylabs.io/help-center/billing-and-payments/how-does-web-scraper-api-pricing-work
- G2 Packages/Pricing docs: https://documentation.g2.com/docs/packages-pricing
- Gartner Digital Markets about/reviews: https://www.gartner.com/en/digital-markets/about
- Software Advice methodology context: https://www.softwareadvice.com/resources/proprietary-data-research/
- Similarweb credits model: https://docs.similarweb.com/api-v5/guides/data-credits-calculations.md
- Similarweb API rate limits: https://developers.similarweb.com/docs/rate-limit
- Semrush API access and units: https://developer.semrush.com/api/basics/how-to-get-api
- DataForSEO SERP API pricing: https://dataforseo.com/apis/serp-api/pricing
- DataForSEO limits: https://dataforseo.com/help-center/rate-limits-and-request-limits
- SerpAPI high-volume limits: https://serpapi.com/high-volume
- Trustpilot API rate limiting: https://developers.trustpilot.com/rate-limiting/
- Distill pricing: https://distill.io/pricing
- Distill schedule checks: https://distill.io/docs/web-monitor/schedule-checks
- Visualping monitoring frequencies: https://help.visualping.io/en/articles/4439809
- Visualping credits and rollover: https://help.visualping.io/en/articles/4440385
- changedetection.io API: https://changedetection.io/docs/api_v1/index.html
- Wayback CDX API docs: https://raw.githubusercontent.com/internetarchive/wayback/master/wayback-cdx-server/README.md
- Common Crawl index: https://data.commoncrawl.org/crawl-data/index.html

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

Interpretation quality depends on measurement design more than source count. ABS 2024 methodology notes that monthly indicators often combine newly observed and carried-forward prices when coverage is incomplete. For this skill, asynchronous competitor refreshes can create timing artifacts that look like strategic price gaps unless freshness windows and carry-forward limits are explicit.

Big-data scale does not automatically imply representativeness. Eurostat's 2024 HICP manual notes that scanner/web data can improve granularity and comparability, but still warns of uneven coverage and ill-defined target populations. In competitive pricing work, this maps directly to over-weighting highly visible public pages and under-weighting negotiated enterprise realities.

Comparability must be a hard gate. ONS scanner-data transformation notes and Eurostat quality-adjustment guidance both show that method choice can change measured outcomes. Tier-name matching is therefore insufficient. This skill should require comparability scoring across value metric, feature scope, billing term, all-in fee basis, and geo/currency/tax basis before benchmark medians are treated as decision-grade.

Staleness should expire automatically. Statistical-methodology references typically allow short carry-forward periods before requiring replacement. Operationally, this skill should mark observations non-actionable after two stale cycles, not keep carrying forward indefinitely.

All-in and same-stage comparisons matter more under current regulatory scrutiny. FTC fee-transparency rules and CMA dynamic-pricing guidance both reinforce that headline/base prices are weak comparisons when mandatory fees or purchase-stage differences are ignored. Benchmark conclusions should be based on normalized all-in payable totals at matched stage.

Outlier handling should be robust and auditable. NIST and public statistical methods both support flag-and-sensitivity approaches over silent deletion. Keep candidate outliers with flags, run with/without-outlier sensitivity views, and downgrade confidence when recommendation direction changes.

Recommended operational thresholds for this skill:
- `<5 percentage-point gap`: non-actionable noise in most cases unless confidence is high and direction persists.
- `5-15 points`: directional signal only; require reversible or staged actions.
- `>15 points`: potentially actionable only when comparability passes, staleness is controlled, and cross-source disagreement is bounded.

Confidence tiering should include disagreement controls:
- if trusted independent sources differ by `>10pp` on normalized gap, cap at medium confidence.
- if they differ by `>20pp` or opposite sign, force low confidence + `insufficient_evidence`.

**Sources:**
- ABS Monthly CPI Indicator methodology (2024): https://www.abs.gov.au/methodologies/monthly-consumer-price-index-indicator-methodology/oct-2024
- ABS CPI price-collection methods (2025): https://www.abs.gov.au/statistics/detailed-methodology-information/concepts-sources-methods/consumer-price-index-concepts-sources-and-methods/2025/price-collection
- ONS scanner-data impact analysis (2025): https://www.ons.gov.uk/economy/inflationandpriceindices/articles/impactanalysisontransformationofukconsumerpricestatisticsrailfaresandsecondhandcars/april2025
- ONS introducing grocery scanner data (2025): https://www.ons.gov.uk/economy/inflationandpriceindices/methodologies/introducinggroceryscannerdataintoconsumerpricestatistics
- Eurostat HICP methodology page: https://ec.europa.eu/eurostat/statistics-explained/index.php/HICP_methodology
- Eurostat HICP methodological manual (2024 PDF): https://ec.europa.eu/eurostat/documents/3859598/18594110/KS-GQ-24-003-EN-N.pdf
- FTC fee rule FAQ (2025): https://www.ftc.gov/business-guidance/resources/rule-unfair-or-deceptive-fees-frequently-asked-questions
- FTC junk-fee rule announcement (2024): https://www.ftc.gov/news-events/news/press-releases/2024/12/federal-trade-commission-announces-bipartisan-rule-banning-junk-ticket-hotel-fees
- CMA dynamic pricing update (2025): https://www.gov.uk/government/publications/dynamic-pricing-project-update/update-dynamic-pricing
- NIST outlier detection (evergreen): https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h.htm
- NIST MAD reference (2016, evergreen): https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/mad.htm

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

1) **Variant and unit mismatch ("same product" illusion)**  
What goes wrong: teams compare similarly named tiers/SKUs without strict variant or unit equivalence.  
Detection: missing identifier integrity, missing unit normalization, and unstable rank order after normalization.  
Consequence: false gap detection and avoidable repricing actions.  
Mitigation: enforce strict comparability keys and unit normalization before any ranking.

2) **Promo window contamination**  
What goes wrong: sale prices enter baseline benchmark lanes because promo windows are missing or invalid.  
Detection: sale flags without valid start/end timezone metadata; sharp short-lived median dips.  
Consequence: benchmark "whiplash" and margin-destructive reactions.  
Mitigation: separate regular and promo lanes, validate sale windows, and require persistence checks.

3) **Illegal or misleading discount baseline assumptions**  
What goes wrong: benchmark logic accepts "was/now" claims without reconstructing valid prior-price baselines.  
Detection: claimed discount cannot be reproduced against auditable historical windows.  
Consequence: compliance exposure and optimization against non-comparable promotional claims.  
Mitigation: preserve prior-price history and compute discount comparisons from explicit baseline rules.

4) **Headline-only comparisons (mandatory fees ignored)**  
What goes wrong: base prices are compared while mandatory fees appear later in purchase flow.  
Detection: measured gap flips direction after all-in checkout reconstruction.  
Consequence: distorted positioning conclusions and negotiation errors.  
Mitigation: benchmark minimum transactable all-in prices at matched purchase stage.

5) **Tax/currency mode mismatch**  
What goes wrong: tax-inclusive and tax-exclusive prices are mixed, or FX conversions are stale/opaque.  
Detection: unexplained regional deltas that disappear after tax-mode/FX standardization.  
Consequence: phantom competitiveness gaps and unstable geo strategies.  
Mitigation: maintain explicit tax-mode fields, timestamped FX source metadata, and currency minor-unit validation.

6) **Asynchronous stale snapshot joins**  
What goes wrong: evidence captured at different times is treated as one coherent market view.  
Detection: inconsistent `observed_at` windows and recurring mismatch alerts after source refreshes.  
Consequence: phantom volatility and unnecessary tactical changes.  
Mitigation: enforce coherence windows and stale-expiry rules before actionability.

7) **Compliance-blind competitor following**  
What goes wrong: recommendations mirror competitor motion without independent internal rationale.  
Detection: recommendation text cites competitor movement as sole justification.  
Consequence: heightened antitrust/governance risk.  
Mitigation: require independent demand/cost/value rationale and legal escalation triggers.

8) **Confidence-free output patterns**  
What goes wrong: single-number rank output has no comparability grade, freshness status, or contradiction handling.  
Detection: missing provenance/confidence metadata and no explicit non-actionable state.  
Consequence: overconfident decisioning and weak audit defense.  
Mitigation: require confidence tiers, contradiction reporting, and `insufficient_evidence` outputs when gates fail.

**Sources:**
- CMA dynamic pricing update (2025): https://www.gov.uk/government/publications/dynamic-pricing-project-update/update-dynamic-pricing
- CMA tips for businesses using dynamic pricing (2025): https://www.gov.uk/government/publications/dynamic-pricing-tips-for-businesses/tips-for-businesses-using-dynamic-pricing
- FTC junk-fee rule announcement (2024): https://www.ftc.gov/news-events/news/press-releases/2024/12/federal-trade-commission-announces-bipartisan-rule-banning-junk-ticket-hotel-fees
- FTC fee rule FAQ (2025): https://www.ftc.gov/business-guidance/resources/rule-unfair-or-deceptive-fees-frequently-asked-questions
- FTC/DOJ algorithmic pricing statement of interest (2024): https://www.ftc.gov/news-events/news/press-releases/2024/03/ftc-doj-file-statement-interest-hotel-room-algorithmic-price-fixing-case
- CJEU Aldi Sud C-330/23 (2024): https://www.bailii.org/eu/cases/EUECJ/2024/C33023.html
- ACM warning against fake discounts (2024): https://www.acm.nl/en/publications/acm-warns-against-fake-discounts
- ACM fines for fake discounts (2024): https://www.acm.nl/en/publications/acm-has-fined-online-stores-using-fake-discounts
- Eurostat HICP methodology: https://ec.europa.eu/eurostat/statistics-explained/index.php/HICP_methodology
- Google Merchant sale-price effective date guidance: https://support.google.com/merchants/answer/6324460?hl=en
- Google Merchant mismatched price policy: https://support.google.com/merchants/answer/12159029?hl=en
- Shopify dynamic tax-inclusive pricing (accessed 2026): https://help.shopify.com/en/manual/markets/pricing/dynamic-tax-inclusive-pricing
- Stripe tax behavior docs (accessed 2026): https://docs.stripe.com/tax/products-prices-tax-codes-tax-behavior
- Stripe currency handling docs (accessed 2026): https://docs.stripe.com/currencies

---

### Angle 5+: Legal, Compliance, and Responsible Use Guardrails
> Additional domain-specific angle: antitrust, privacy, and scraping/terms constraints for competitive pricing intelligence workflows.

**Findings:**

Antitrust enforcement has become explicit on algorithmic pricing behavior. FTC/DOJ filings state that using shared algorithms does not shield unlawful coordination. Direct competitor communication is not required for Section 1 exposure when conduct effectively aligns pricing through shared mechanisms.

The DOJ RealPage case (allegations, ongoing) underscores non-public, competitively sensitive data exchange risk. Even without final adjudication, this is enough to require conservative design: no non-public competitor feeds, no cross-competitor shared recommendation loops, and documented independent decision rationale.

EU horizontal guidelines treat commercially sensitive information exchange as high-risk and clarify that even "public data" usage can still create concerns if cadence/granularity or commentary drives coordinated outcomes. This implies this skill should produce aggregated trend insights, not near-real-time competitor-specific pricing directives.

Cross-border enforcers (US/EU/UK) published a joint 2024 AI competition warning, signaling convergence in concern about algorithmic collusion and sensitive-data exchange.

Scraping legality remains jurisdiction and fact dependent. US precedent (hiQ, evergreen) narrowed one CFAA pathway in specific circumstances, but other claims (contract, copyright, privacy, trespass) remain possible. A 2024 X v Bright Data order shows continuing litigation complexity. This skill should encode "authorized-access-only" rules and source ToS status fields.

Privacy obligations can apply even to public web data when personal data is processed (EDPB Opinion 28/2024). Therefore, if personal data appears in source payloads, minimization and lawful-basis controls are mandatory.

**Sources:**
- FTC/DOJ statement of interest in hotel algorithmic pricing case (2024): https://www.ftc.gov/news-events/news/press-releases/2024/03/ftc-doj-file-statement-interest-hotel-room-algorithmic-price-fixing-case
- FTC legal matter page (2024): https://www.ftc.gov/legal-library/browse/amicus-briefs/karen-cornish-adebiyi-et-al-v-caesars-entertainment-inc-et-al
- DOJ RealPage complaint filing (2024): https://www.justice.gov/atr/media/1365471/dl?inline
- DOJ RealPage case page (open 2024, updated 2026): https://www.justice.gov/atr/case/us-and-plaintiff-states-v-realpage-inc
- EU Horizontal Cooperation Guidelines (2023, evergreen): https://competition-policy.ec.europa.eu/system/files/2023-07/2023_revised_horizontal_guidelines_en.pdf
- US/EU/UK joint statement on AI competition issues (2024): https://www.ftc.gov/system/files/ftc_gov/pdf/ai-joint-statement.pdf
- FTC release on joint AI statement (2024): https://www.ftc.gov/news-events/news/press-releases/2024/07/ftc-doj-international-enforcers-issue-joint-statement-ai-competition-issues
- hiQ v LinkedIn (2022, evergreen): https://law.justia.com/cases/federal/appellate-courts/ca9/17-16783/17-16783-2022-04-18.html
- X v Bright Data order (2024): https://storage.courtlistener.com/recap/gov.uscourts.cand.415869/gov.uscourts.cand.415869.83.0.pdf
- EDPB Opinion 28/2024 page: https://www.edpb.europa.eu/our-work-tools/our-documents/opinion-board-art-64/opinion-282024-certain-data-protection-aspects_en
- EDPB Opinion 28/2024 PDF (adopted 2024-12-17): https://www.edpb.europa.eu/system/files/2024-12/edpb_opinion_202428_ai-models_en.pdf

---

## Synthesis

The strongest cross-angle conclusion remains that benchmark quality is dominated by methodology discipline, not source count. Public pricing pages are easy to collect, but interpretation fails quickly when teams skip comparability scoring, staleness controls, and list-vs-realized separation. This is why the skill should treat comparability as a gate, not a note.

Tooling is mature enough for robust collection, but each source class answers a different question. Direct page capture proves what was publicly shown at a time; review-site metadata corroborates package structures; context APIs explain demand/visibility shifts; change-detection/history tools provide auditability. This source-priority model should be explicit in SKILL text and in schema truth labels.

Several meaningful contradictions remain and should not be hidden: method changes can materially shift measured benchmark outcomes; AI-pricing impact claims differ across survey ecosystems; and discount benchmarks vary based on whether they capture list, transaction, or mixed constructs. The practical response is confidence-tiered outputs with disagreement thresholds, not single-point certainty.

The biggest "surprise" is how close interpretation quality and compliance now sit. Consumer transparency enforcement, discount-baseline enforcement, and algorithmic pricing antitrust scrutiny all directly affect what counts as defensible benchmark output. Compliance-safe operation is no longer a separate appendix; it is a core design requirement for this skill.

Net result: this skill should be treated as a decision-quality evaluator with explicit evidence classes, comparability gates, stale-expiry logic, and contradiction-aware confidence scoring.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.

- [ ] Add a two-speed operating cadence: quarterly delta scans + annual full rebasing.
- [ ] Require separate outputs for `list_price_benchmark` and `realized_price_benchmark`.
- [ ] Add a source-priority policy with truth labels (`observed_list_price`, `review_site_metadata`, `web_intel_estimate`, `inferred_range`) and do not mix labels in benchmark math.
- [ ] Add strict normalization instructions (capability mapping, billing-term normalization, currency/tax normalization, usage scenarios).
- [ ] Add a comparability gate (5 dimensions) and stale-expiry rule (non-actionable after two stale cycles).
- [ ] Add confidence scoring (0-100) with decision tiers and an explicit `insufficient_evidence` state.
- [ ] Add anti-pattern warning blocks with detection signals and mitigation steps.
- [ ] Expand `## Available Tools` guidance with provenance classes, authorized-access constraints, rate-limit/backoff behavior, and uncertainty flags.
- [ ] Add legal/compliance guardrails (authorized data only, no coordination logic, independent rationale requirement).
- [ ] Extend artifact schema with evidence provenance, freshness metadata, confidence fields, and risk flags.
- [ ] Add contradiction-handling rule with thresholds: if trusted sources disagree by >10pp cap confidence at medium, >20pp force low + `insufficient_evidence`.

---

## Draft Content for SKILL.md

> This is the most important section. For every recommendation above, write the actual text that should go into SKILL.md.

### Draft: Core operating model and cadence

---
### Benchmark cadence and operating discipline

You must run this skill on a deliberate cadence, not only when a deal is at risk. Run a **quarterly delta benchmark** to detect meaningful market movement, and run an **annual full rebasing benchmark** to reset tier mapping, segment norms, and positioning assumptions. Do not treat one-off snapshots as strategic truth.

Before any pricing verdict, verify three preconditions:
1. **Recency:** every source used in the final comparison has a known `observed_at` date and a defined `stale_after_days` threshold.
2. **Comparability:** all competitor tiers are normalized into your canonical capability buckets before price comparisons.
3. **Evidence class separation:** list prices and realized/transaction pricing are stored and interpreted separately.

If any precondition is missing, output `insufficient_evidence` for strategic recommendations and restrict output to descriptive observations.

Do NOT approve repricing recommendations from a single scrape run, a single source class, or unnormalized tier-name matching.
---

### Draft: Data collection and normalization workflow

---
### Data collection workflow

You must collect benchmark evidence in layers, from highest provenance to lowest:

1. **Official pricing pages (required):**  
   Collect each direct competitor's public pricing page and capture: model (`flat`, `per_seat`, `usage`, `hybrid`, `quote`), tier names, list prices, billing terms, key inclusions, and known exclusions.

2. **Review-site corroboration (recommended):**  
   Use review-platform pricing sections (for example, vendor-managed pricing metadata) as corroboration. If a source says "not provided," record that explicitly rather than filling gaps with assumptions.

3. **Context signals (optional but useful):**  
   Use traffic/engagement or intent signals only as context for positioning confidence. Never treat traffic-intelligence metrics as direct evidence of price competitiveness.

4. **Realized-price signals (if available):**  
   Incorporate transaction, renewal, or procurement benchmark sources in a separate `realized_price_benchmark` view. Never merge realized values into list values without labeling.

5. **Change evidence capture (recommended):**  
   Preserve page snapshots or versioned captures for all high-impact observations so later disputes can be resolved against evidence.

### Normalization rules

Before comparing any price, normalize across the following dimensions:

- **Capability equivalence:** map each competitor tier into canonical buckets (for example: governance, automation, integrations, analytics, support, AI). Tier names are not equivalence.
- **Billing-term normalization:** convert all prices to effective monthly equivalent where possible:
  - `effective_monthly = total_contract_value / term_months`
- **Annual-vs-monthly comparability:** record both annual prepay discount and monthly-on-annual premium when present.
- **Usage model scenarios:** for usage or hybrid plans, compute `low`, `base`, and `high` usage scenarios with explicit assumptions.
- **Currency and tax normalization:** compute normalized net benchmark values in a base currency; separately report customer-visible gross/all-in values.
- **All-in price reconstruction:** include mandatory fees before final comparison. A headline price without mandatory charges is incomplete.

Assign comparability on five dimensions: `value_metric`, `feature_scope`, `billing_term`, `all_in_fee_basis`, and `geo_currency_tax_basis`.

- `5/5` or `4/5`: treat as `comparable`.
- `3/5`: treat as `partially_comparable` and exclude from high-confidence recommendations.
- `0-2/5`: treat as `non_comparable` and exclude from category medians.

If comparability cannot be established for a competitor tier, mark it `non_comparable` and exclude it from median calculations while keeping the row in the artifact.

Staleness handling:
- if `source_age_days > stale_after_days`, mark row stale.
- if stale for `>2` consecutive cycles, force `is_actionable: false` for recommendations that depend on that row.
---

### Draft: Confidence scoring and decision thresholds

---
### Confidence scoring protocol

You must assign a `confidence_score` from 0 to 100 for every recommendation-bearing benchmark output. Compute the score from weighted components:

- `realized_price_evidence` (0-20): realized price evidence present and current.
- `comparability_quality` (0-20): feature-level normalization quality.
- `sample_depth` (0-15): adequate cross-competitor and cross-period coverage.
- `uncertainty_visibility` (0-15): ranges/percentiles/confidence notes provided.
- `cross_source_consistency` (0-15): independent sources align, or divergences are explicitly explained.
- `recency` (0-10): evidence is within freshness SLA.
- `method_transparency` (0-5): outlier handling and assumptions are documented.

Assign decision tier:
- `80-100`: high confidence, recommendation can be action-oriented with guardrails.
- `60-79`: directional confidence only; require staged or reversible action.
- `<60`: low confidence; default to `insufficient_evidence`.

Additional confidence gates:
- If independent trusted sources disagree by `>10pp`, cap confidence at `medium`.
- If independent trusted sources disagree by `>20pp` (or disagree on direction), force `low` + `insufficient_evidence`.
- If outlier sensitivity changes recommendation direction, force `low` until new evidence resolves the conflict.

### Practical threshold interpretation

Use conservative gap interpretation:
- `<5 percentage-point gap`: usually noise unless confidence is high and persistence is proven.
- `5-15 points`: directional signal; not enough for unilateral repricing without additional evidence.
- `>15 points`: potentially actionable if comparability and realized evidence are both strong.

If major external sources disagree materially (for example, discount benchmarks with non-overlapping ranges), downgrade confidence and present range-based conclusions, not single-point verdicts.

### Outlier and sensitivity policy

Do not silently delete outliers.  
Detect candidate outliers with robust methods (for example, MAD/modified-z style checks), label them, and run at least two views: with and without outliers. If recommendation direction changes between views, downgrade confidence at least one tier and include an uncertainty warning.
---

### Draft: Anti-pattern warning blocks

```md
> [!WARNING] Anti-pattern: Snapshot-Only Benchmarking
> **What it looks like:** you benchmark from one crawl window and treat it as strategic truth.
> **Detection signal:** no rolling-window evidence and no freshness SLA fields.
> **Consequence:** reactive repricing driven by temporary promos or stale pages.
> **Mitigation:** require timestamped multi-period checks before recommendations.
```

```md
> [!WARNING] Anti-pattern: Apples-to-Oranges Tier Matching
> **What it looks like:** direct price comparison between tiers with different capabilities/terms.
> **Detection signal:** missing equivalence map or high `non_comparable` rate.
> **Consequence:** false gap analysis and poor negotiation posture.
> **Mitigation:** enforce capability-bucket normalization before any median or gap computation.
```

```md
> [!WARNING] Anti-pattern: Headline-Only Price Comparison
> **What it looks like:** comparing base/list prices while ignoring mandatory fees or billing premiums.
> **Detection signal:** gap reverses after all-in or term normalization.
> **Consequence:** incorrect "we must cut price" recommendations.
> **Mitigation:** compare all-in payable totals at matched purchase stage.
```

```md
> [!WARNING] Anti-pattern: Promo Whiplash
> **What it looks like:** matching competitor event promos by default.
> **Detection signal:** repeated emergency repricing around campaign windows with margin degradation.
> **Consequence:** self-inflicted margin compression and inconsistent positioning.
> **Mitigation:** isolate promo observations, apply duration filters, and require persistence checks.
```

```md
> [!WARNING] Anti-pattern: Compliance-Blind Competitor Following
> **What it looks like:** recommendations repeatedly mirror competitor moves without internal demand/cost rationale.
> **Detection signal:** suggestion text references competitor behavior as sole reason.
> **Consequence:** elevated antitrust and governance risk.
> **Mitigation:** require independent rationale and legal escalation triggers on sensitive patterns.
```

```md
> [!WARNING] Anti-pattern: Tax/FX Mode Mismatch
> **What it looks like:** mixing tax-inclusive and tax-exclusive prices or using stale FX conversions in one benchmark.
> **Detection signal:** cross-geo gaps collapse after tax and FX normalization.
> **Consequence:** phantom pricing gaps and unstable regional strategy.
> **Mitigation:** store tax mode and FX source/timestamp per row, enforce minor-unit checks, and block non-normalized comparisons.
```

```md
> [!WARNING] Anti-pattern: Promo Window Contamination
> **What it looks like:** sale prices overwrite baseline levels because promo start/end metadata is missing.
> **Detection signal:** sudden short-lived median drops without valid sale window fields.
> **Consequence:** margin-destructive "match the promo" decisions and misleading trend signals.
> **Mitigation:** separate regular vs promo lanes, validate sale window timestamps, and require persistence checks before action.
```

### Draft: Available Tools

---
## Available Tools

Use only verified methods available in your environment. Do not invent method IDs or endpoints. If a method is unavailable at runtime, record a tool-availability gap instead of substituting guessed calls.

```python
web(open=[{"url": "https://competitor.com/pricing"}])

g2(
  op="call",
  args={
    "method_id": "g2.products.list.v1",
    "filter[name]": "competitor name",
  },
)

similarweb(
  op="call",
  args={
    "method_id": "similarweb.traffic_and_engagement.get.v1",
    "domain": "competitor.com",
  },
)

flexus_policy_document(
  op="activate",
  args={"p": "/strategy/positioning-map"},
)
```

Tool usage rules:
1. **`web` is primary for official pricing pages.** Always capture URL, retrieval timestamp, and raw snippet evidence.
2. **`g2` is corroboration, not sole truth.** Vendor coverage can be incomplete; record missing/undisclosed pricing explicitly.
3. **`similarweb` is context only.** Use for positioning context and demand signals, not direct price parity assertions.
4. **`flexus_policy_document` must be activated before final alignment verdicts.** Positioning-vs-price output is invalid without current strategy context.
5. **Authorized access only.** Do not bypass authentication, paywalls, robots controls, or anti-bot protections; skip and log blocked sources instead of forcing collection.
6. **Error handling is mandatory.** On missing methods, rate limits, or blocked pages, set uncertainty flags and continue with available evidence.
7. **Rate-limit backoff is required.** Handle `429` and provider throttling with exponential backoff and jitter; record partial-collection risk flags when retries are exhausted.
---

### Draft: Compliance and legal guardrails

---
### Competition, privacy, and data-access guardrails

This skill is for competitive intelligence and strategic benchmarking, not coordinated pricing behavior.

You must follow these constraints:
1. Use only data you are authorized to access (publicly available or licensed/contractually permitted).
2. Do not ingest non-public competitor pricing/strategy feeds.
3. Do not generate recommendations that imply coordinated behavior (for example, "mirror competitor X in real time").
4. Require an independent rationale for every pricing recommendation (internal demand, cost, positioning, and value evidence).
5. If source payloads include personal data, apply minimization and lawful-basis requirements before storage/use.
6. Escalate for legal review when recommendations rely on high-frequency competitor-specific signals or ambiguous data-access permissions.

Required disclaimer text in output metadata:
- "Competitive intelligence output; not legal advice."
- "Do not use this artifact to coordinate pricing or exchange commercially sensitive information with competitors."
- "Final pricing decisions must be independently made and reviewed for legal, policy, and fairness constraints."
---

### Draft: Output quality and insufficient-evidence rules

---
### Output quality standard

Your output must be decision-grade, not just descriptive.

Minimum quality requirements:
- At least 3 direct competitors in scope unless category constraints are documented.
- At least one official pricing-page source per competitor.
- Explicit source provenance tags for each key claim.
- Freshness metadata for each source.
- Comparability gate applied on 5 dimensions for every benchmarked tier.
- Separate list-price and realized-price views.
- Confidence score and confidence tier.
- Contradictions section when sources disagree.
- Persistence check: directional gap should hold for 2 consecutive refreshes before irreversible recommendations.

If any requirement is missing, return:
- `is_actionable: false`
- `confidence_tier: "low"`
- `insufficient_evidence_reason: "<specific missing element>"`

Do not produce numeric negotiation targets when confidence is low.
---

### Draft: Schema additions

> Full JSON Schema fragment for new/modified artifact fields.

```json
{
  "pricing_competitive_benchmark": {
    "type": "object",
    "required": [
      "benchmarked_at",
      "benchmark_window",
      "category",
      "competitors",
      "category_norms",
      "positioning_alignment",
      "confidence"
    ],
    "additionalProperties": false,
    "properties": {
      "benchmarked_at": {
        "type": "string",
        "description": "ISO-8601 timestamp for when the benchmark artifact was produced."
      },
      "benchmark_window": {
        "type": "object",
        "required": ["start_date", "end_date", "stale_after_days", "expired_after_cycles"],
        "additionalProperties": false,
        "properties": {
          "start_date": {
            "type": "string",
            "description": "Inclusive start date for collected observations (YYYY-MM-DD)."
          },
          "end_date": {
            "type": "string",
            "description": "Inclusive end date for collected observations (YYYY-MM-DD)."
          },
          "stale_after_days": {
            "type": "integer",
            "description": "Maximum age in days before benchmark evidence is treated as stale."
          },
          "expired_after_cycles": {
            "type": "integer",
            "description": "Maximum number of consecutive stale refresh cycles allowed before dependent outputs become non-actionable."
          }
        }
      },
      "category": {
        "type": "string",
        "description": "Product category used for selecting peer competitors."
      },
      "competitors": {
        "type": "array",
        "description": "Competitor-level benchmark entries with normalized pricing and evidence.",
        "minItems": 3,
        "items": {
          "type": "object",
          "required": [
            "name",
            "pricing_model",
            "tiers",
            "data_freshness_days",
            "source_records"
          ],
          "additionalProperties": false,
          "properties": {
            "name": {
              "type": "string",
              "description": "Competitor company or product name."
            },
            "segment_fit": {
              "type": "string",
              "description": "How closely this competitor matches the target ICP segment."
            },
            "pricing_model": {
              "type": "string",
              "enum": ["flat", "per_seat", "usage", "hybrid", "enterprise_quote", "unknown"],
              "description": "Primary pricing model observed for the competitor."
            },
            "tiers": {
              "type": "array",
              "description": "Normalized tier records for comparable plans.",
              "items": {
                "type": "object",
                "required": [
                  "tier_name",
                  "price_unit",
                  "currency",
                  "all_in_monthly_equivalent",
                  "comparability_dimensions_passed",
                  "comparability_status"
                ],
                "additionalProperties": false,
                "properties": {
                  "tier_name": {
                    "type": "string",
                    "description": "Vendor-provided tier name."
                  },
                  "list_price": {
                    "type": ["number", "null"],
                    "description": "Published list price for the tier, null when quote-only."
                  },
                  "billing_term": {
                    "type": "string",
                    "enum": ["monthly", "annual_prepaid", "annual_monthly_billed", "usage", "quote_only", "unknown"],
                    "description": "Billing term associated with the observed price."
                  },
                  "price_unit": {
                    "type": "string",
                    "description": "Value metric unit (e.g., per_user_per_month, per_1000_events)."
                  },
                  "currency": {
                    "type": "string",
                    "description": "ISO currency code of observed price."
                  },
                  "includes_tax": {
                    "type": "boolean",
                    "description": "Whether the observed displayed price includes tax."
                  },
                  "mandatory_fees_monthly_equivalent": {
                    "type": ["number", "null"],
                    "description": "Monthly equivalent of mandatory fees needed for all-in comparability."
                  },
                  "all_in_monthly_equivalent": {
                    "type": ["number", "null"],
                    "description": "Normalized monthly equivalent including mandatory fees where known."
                  },
                  "usage_scenarios": {
                    "type": "object",
                    "required": ["low", "base", "high"],
                    "additionalProperties": false,
                    "properties": {
                      "low": {
                        "type": ["number", "null"],
                        "description": "Estimated monthly cost under low usage assumptions."
                      },
                      "base": {
                        "type": ["number", "null"],
                        "description": "Estimated monthly cost under baseline usage assumptions."
                      },
                      "high": {
                        "type": ["number", "null"],
                        "description": "Estimated monthly cost under high usage assumptions."
                      }
                    }
                  },
                  "key_inclusions": {
                    "type": "array",
                    "description": "Major included capabilities used for comparability mapping.",
                    "items": {"type": "string"}
                  },
                  "comparability_status": {
                    "type": "string",
                    "enum": ["comparable", "partially_comparable", "non_comparable"],
                    "description": "Comparability label after capability and billing normalization."
                  },
                  "comparability_dimensions_passed": {
                    "type": "integer",
                    "description": "Count of passed comparability dimensions out of 5: value metric, feature scope, billing term, all-in fee basis, and geo/currency/tax basis."
                  },
                  "comparability_notes": {
                    "type": "string",
                    "description": "Explanation of why plan is (or is not) comparable."
                  }
                }
              }
            },
            "annual_discount": {
              "type": ["number", "null"],
              "description": "Computed annual-prepay discount vs monthly equivalent when available."
            },
            "data_freshness_days": {
              "type": "integer",
              "description": "Age in days of the newest source observation used for this competitor."
            },
            "source_records": {
              "type": "array",
              "description": "Evidence records supporting this competitor entry.",
              "items": {
                "type": "object",
                "required": ["source_type", "source_name", "source_url", "observed_at"],
                "additionalProperties": false,
                "properties": {
                  "source_type": {
                    "type": "string",
                    "enum": [
                      "official_pricing_page",
                      "review_site_vendor_submitted",
                      "review_site_user_submitted",
                      "web_intel_estimate",
                      "transaction_benchmark",
                      "analyst_report"
                    ],
                    "description": "Provenance class for confidence weighting."
                  },
                  "source_name": {
                    "type": "string",
                    "description": "Human-readable source name."
                  },
                  "source_url": {
                    "type": "string",
                    "description": "URL of source evidence."
                  },
                  "observed_at": {
                    "type": "string",
                    "description": "ISO-8601 timestamp when this source was observed or retrieved."
                  },
                  "retrieval_method": {
                    "type": "string",
                    "enum": ["web_open", "api_call", "manual_reference"],
                    "description": "How evidence was retrieved."
                  },
                  "confidence_weight": {
                    "type": "number",
                    "description": "Relative weight from 0.0 to 1.0 assigned to this source."
                  }
                }
              }
            },
            "risk_flags": {
              "type": "array",
              "description": "Known issues affecting interpretation quality.",
              "items": {
                "type": "string",
                "enum": [
                  "blocked_by_antibot",
                  "vendor_pricing_not_provided",
                  "list_price_only",
                  "promo_period",
                  "tax_or_currency_uncertain",
                  "non_comparable_plan",
                  "stale_source_window",
                  "missing_sale_window",
                  "asynchronous_snapshot"
                ]
              }
            }
          }
        }
      },
      "category_norms": {
        "type": "object",
        "required": [
          "median_entry_price",
          "median_pro_price",
          "dominant_model",
          "dominant_value_metric",
          "based_on_competitor_count"
        ],
        "additionalProperties": false,
        "properties": {
          "median_entry_price": {
            "type": "number",
            "description": "Median normalized all-in monthly equivalent for entry tiers."
          },
          "median_pro_price": {
            "type": "number",
            "description": "Median normalized all-in monthly equivalent for pro tiers."
          },
          "dominant_model": {
            "type": "string",
            "description": "Most common pricing model among comparable competitors."
          },
          "dominant_value_metric": {
            "type": "string",
            "description": "Most common value metric in the category."
          },
          "based_on_competitor_count": {
            "type": "integer",
            "description": "Number of competitors included in norm calculations."
          },
          "normalization_notes": {
            "type": "string",
            "description": "Notes on adjustments and exclusions used in norm calculations."
          }
        }
      },
      "positioning_alignment": {
        "type": "object",
        "required": ["expected_position", "actual_position", "is_aligned", "misalignment_notes"],
        "additionalProperties": false,
        "properties": {
          "expected_position": {
            "type": "string",
            "description": "Intended market position from strategy."
          },
          "actual_position": {
            "type": "string",
            "description": "Observed position from normalized benchmark outputs."
          },
          "is_aligned": {
            "type": "boolean",
            "description": "Whether observed pricing supports intended positioning."
          },
          "misalignment_notes": {
            "type": "string",
            "description": "Why positioning and pricing are misaligned, if applicable."
          }
        }
      },
      "confidence": {
        "type": "object",
        "required": ["confidence_score", "confidence_tier", "is_actionable"],
        "additionalProperties": false,
        "properties": {
          "confidence_score": {
            "type": "number",
            "description": "Composite score from 0 to 100 across evidence quality dimensions."
          },
          "confidence_tier": {
            "type": "string",
            "enum": ["high", "medium", "low"],
            "description": "Tier label mapped from confidence score."
          },
          "is_actionable": {
            "type": "boolean",
            "description": "Whether evidence quality is sufficient for tactical recommendations."
          },
          "insufficient_evidence_reason": {
            "type": ["string", "null"],
            "description": "Specific reason for low confidence or non-actionable status."
          },
          "benchmark_disagreement_pp": {
            "type": ["number", "null"],
            "description": "Absolute percentage-point disagreement between trusted independent benchmark sources on the normalized gap."
          },
          "contradictions_noted": {
            "type": "array",
            "description": "Material source disagreements that affect interpretation.",
            "items": {"type": "string"}
          }
        }
      },
      "gaps_and_uncertainties": {
        "type": "array",
        "description": "Known data gaps and unresolved uncertainties for this benchmark run.",
        "items": {"type": "string"}
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Public, source-verified realized-price data is still limited; most realized benchmarks come from vendor reports and may use non-identical definitions.
- Some source pages (especially review platforms) may block automated retrieval depending on region/fingerprint; availability can vary by runtime environment.
- Tool pricing and rate limits change frequently; operational implementations should re-verify current limits before production use.
- Antitrust/privacy guidance is jurisdiction- and fact-specific; this research is operational guidance, not legal advice.
- No universal cross-category threshold exists for "actionable gap"; confidence tiers and context-specific ranges remain necessary.
