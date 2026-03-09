# Research: pain-alternatives-landscape

**Skill path:** `researcher/skills/pain-alternatives-landscape/`
**Bot:** researcher (researcher | strategist | executor)
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`pain-alternatives-landscape` maps everything customers currently use or consider when solving the problem your product addresses. This is not a competitive benchmarking exercise — it is a buyer-behavior research task. The output feeds `positioning-market-map` and `offer-design` in the strategist, and is also consumed by `segment-icp-scoring` when scoring accounts based on current-solution fit.

The current SKILL.md has a correct basic structure (review platforms, Reddit, tiered alternatives) but under-specifies: the JTBD-based framing of what counts as an "alternative," the win/loss interview methodology for extracting actual alternatives evaluated by real buyers, the non-consumption category (which is often the dominant "competitor" in early markets), and the data interpretation rules for distinguishing noise from switching signal.

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

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually map competitive alternatives in 2025-2026? What frameworks, mental models, step-by-step processes exist?

**Findings:**

Modern alternatives landscape mapping has diverged from feature-matrix competitive analysis into a buyer-behavior-first methodology. The core insight driving 2024-2026 practice: the relevant competitive set is defined by the buyer's job, not by the vendor's category. This means "what else did you consider?" surfaces a fundamentally different landscape than "who are your direct competitors?" [A1][A3]

**JTBD competitive framing (Evergreen, widely applied in 2024-2026):** The Jobs-to-be-Done framework organizes competitors not by product category but by the job they help customers execute. A Competitive Analysis Matrix maps: one axis = all solutions customers use for the same job (direct competitors, indirect substitutes, DIY approaches, and non-consumption); the other axis = steps in the job, scored by how well each solution performs each step. This reveals alternatives that feature matrices miss entirely — for example, "hire a consultant" or "use existing CRM reports" appear as legitimate competitors to a SaaS analytics tool when mapped against the job "understand which customers are about to churn." [A3][A5]

**Win/loss interview methodology (most reliable source for alternatives data):** The highest-signal source for alternatives data is structured win/loss interviews with recent buyers, not public review mining. The "what else did you consider" question — asked after establishing rapport and before discussing outcome — reliably surfaces the actual shortlist the buyer evaluated. Best practice in 2025: 20-30 minute interviews, conducted by someone other than the sales rep who worked the deal (to reduce social desirability bias), using the Five Whys and Laddering techniques to go beyond surface answers. Teams running systematic win/loss programs report a 17.6% increase in quota attainment and 14.2% higher win rates. McKinsey estimates a 10-20% win-rate lift translates to 4-12% topline growth. [A2]

**Practical interview question sequence for alternatives extraction:**
1. "Before you started evaluating us, what were you already doing to solve this problem?" → captures current state / status quo alternative
2. "What made you start looking for something different?" → captures switch trigger
3. "Who else did you look at seriously?" → captures direct shortlist
4. "Why did those options not make the cut?" → captures decision criteria and competitor weaknesses
5. "If we hadn't existed, what would you have done?" → captures fallback alternative, often reveals true "competitor zero" [A2][A4]

**Non-consumption is the most under-mapped alternative:** In early and emerging markets, the most common "alternative" is doing nothing, tolerating the pain, or using a fragmented set of existing tools that were never designed for this job. Most alternatives research ignores this because it is invisible (no brand, no G2 profile, no review data). Yet it is often the primary competitive force determining buyer urgency. [A3][A5]

**Tiering framework (widely used, stable):** Three-tier structure is standard practice:
- Tier 1: Direct competitors — same category, same target segment, head-to-head evaluation
- Tier 2: Adjacent substitutes — different category, solve the same underlying job with a different approach
- Tier 3: DIY/non-consumption — spreadsheets, internal builds, hiring a person, or doing nothing

Recommended scope for a useful output: 3-5 direct competitors, 2-3 adjacent substitutes, and at least one explicit non-consumption scenario. More dilutes focus; less misses strategic context. [A1]

**Sources:**
- [A1] RivalMatrix: Complete Guide to Competitive Analysis for SaaS 2025: https://rivalmatrix.draftforest.com/blog/competitive-analysis-guide-saas-2025
- [A2] iCanPreneur: Win/Loss Customer Interview Best Practices 2025: https://www.icanpreneur.com/blog/best-way-to-do-win-loss-customer-interviews-in-2025
- [A3] THRV: Jobs-to-be-Done Competitive Analysis Matrix (Evergreen): https://www.thrv.com/glossary/competitive-analysis-matrix
- [A4] Klue: How to Conduct Win-Loss Interviews 2025: https://klue.com/blog/win-loss-interviews
- [A5] Brian Rhea: Mapping the Competitive Landscape with JTBD (Evergreen): https://brianrhea.com/mapping-the-competitive-landscape-with-jtbd

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist? What are their actual capabilities, limitations, pricing?

**Findings:**

**G2 API v2:** Official programmatic access to G2 product, review, and competitive data. Rate limit: 100 requests per second; exceeding this blocks access for 60 seconds. Pagination: `page[size]` max 100 results, `page[number]` for offset. Filtering supports `updated_at_lt`, `updated_at_gt` for date ranges. Access requires authentication token from the G2 integrations page; some endpoints require enterprise account permissions — contact Account Executive to unlock. The API covers: product reviews, alternatives listings, product comparisons, buyer intent data, and categories. [T1][T2]

**G2 Scraper API (g2scraper.com):** Third-party programmatic access to G2 data without enterprise account requirement. Use cases: competitor analysis, pain point discovery, review sentiment, feature comparison. Useful when G2 official API is inaccessible due to account tier. [T3]

**Apify / ScraperAPI G2 scrapers:** Pay-per-usage scraping alternatives to G2's official API. Apify offers a dedicated G2 reviews scraper with API access. ScraperAPI provides G2 scraping as part of broader market research tooling. Both handle pagination and anti-scraping measures. Pricing: usage-based. [T4][T5]

**Reddit (direct API or tools):** Best source for authentic, unfiltered switching stories. Key search operators: `"[product] vs [competitor]"`, `"switched from [product] to"`, `"alternative to [product name]"`, `"cheaper than [product]"`. Sort by recency (software landscape changes fast). High-value subreddits for B2B SaaS alternatives research: r/SaaS (100K+ members), r/startups (1.2M+), r/Entrepreneur (1.5M+), plus function-specific: r/analytics, r/projectmanagement, r/sales, r/marketing. Tools built on Reddit data: GummySearch (competitive research), BillyBuzz (AI Reddit monitoring for competitor mentions), Reddily (subreddit discovery for research). [T6][T7]

**Similarweb Similar Sites API:** Returns top 40 most similar websites to a domain, with similarity scores. Cost: 1 hit per request or 2 data credits per result row. Desktop-only (no mobile comparison). Use for algorithmic discovery of alternatives the researcher hasn't thought of. Combined with manual review of returned domains, surfaces indirect competitors not found in G2 categories. [T8][T9]

**ProductHunt:** Alternatives pages are explicitly user-curated. Use the ProductHunt GraphQL API to query alternatives for a given product slug. Most useful for consumer SaaS and developer tools; less reliable for enterprise B2B. [T10]

**Amplemarket Intent Signals:** Monitors when competitors receive G2 reviews in real time. Treats incoming competitor reviews as buying signals — a prospect evaluating an alternative is actively in-market. Useful for pipeline intelligence as a secondary use case of alternatives mapping. [T11]

**Ahrefs / Semrush:** Used for SEO-based alternative discovery — find which keywords competitors rank for that you don't, and which "X vs Y" or "X alternative" queries drive traffic. These comparisons reveal alternatives buyers actively search for, which is a reliable signal of evaluation intent. [T12]

**Sources:**
- [T1] G2 API Documentation v2: https://data.g2.com/api/docs
- [T2] G2 API v2 Full Reference: https://data.g2.com/api/v2/docs/index.html
- [T3] G2 Scraper API: https://g2scraper.com/
- [T4] Apify G2 Reviews Scraper: https://apify.com/sovereigntaylor/g2-reviews-scraper/api
- [T5] ScraperAPI G2 Scraper: https://www.scraperapi.com/solutions/market-research-scraper/g2-scraper/
- [T6] PainOnSocial: Reddit Alternatives Discovery: https://painonsocial.com/blog/saas-alternatives-discussions-reddit
- [T7] Reddily: Best Subreddits for Competitor Research 2026: https://reddily.io/blog/best-subreddits-for-competitor-research
- [T8] Similarweb Similar Sites API Reference: https://developers.similarweb.com/reference/similar-sites
- [T9] Similarweb API Documentation: https://developers.similarweb.com/
- [T10] ProductHunt GraphQL API (Evergreen): https://api.producthunt.com/v2/docs
- [T11] Amplemarket Intent Signals: https://www.amplemarket.com/signals/competitors-g2-reviews
- [T12] GummySearch: Competitor Analysis Tools 2025: https://gummysearch.com/post/the-best-tools-for-competitor-analysis-in-2025-and-why-reddit-is-underrated/

---

### Angle 3: Data Interpretation & Signal Quality
> How to interpret alternatives data, what counts as signal vs noise, thresholds that matter.

**Findings:**

**Review platform authority is high but review volume doesn't predict quality:** G2 and Capterra collectively command 84% of review-platform citations in ChatGPT and AI-assisted research. Presence on either is an inclusion threshold for being discovered in AI-assisted evaluation flows. However, review count and rankings show weak correlation (–0.16 to –0.21 Pearson), meaning a competitor with 500 reviews is not necessarily better-positioned than one with 80 high-quality ones. Volume is a poor proxy for competitive strength. [D1]

**Review platform intent signal increases through the funnel:** G2 and Capterra citation frequency increases from 7.4% at discovery intent to 13.2% at evaluation intent. This means a competitor appearing heavily on review platforms is more likely to be encountered by buyers in active evaluation — a stronger competitive signal than organic brand discovery. Prioritize alternatives with strong G2 presence when the ICP is an active evaluator. [D2]

**Switching signal extraction from reviews — what patterns matter:**
- `"I switched from X because..."` → named alternative + switch trigger. High-confidence signal.
- `"I also tried X but..."` → alternative considered in same purchase cycle. Medium-confidence; may not have been a serious contender.
- `"I use X alongside this because..."` → complementary tool indicating a capability gap. This often surfaces adjacents that would not appear in direct competitor searches.
- `"I wish it did X like [competitor] does"` → feature-level competitive comparison. Useful for positioning but not for alternatives mapping.
The first pattern is the most actionable for alternatives research. Extract named products from all occurrences and map frequency — the most-named switch sources are the most important alternatives. [D3][D4]

**Non-consumption signal is invisible in review data and must come from interviews:** Review data captures only customers who chose a product. Customers who chose to do nothing, or to cobble together spreadsheets, do not leave reviews anywhere. The only reliable source for non-consumption data is direct interviews. When interview data is unavailable, proxy signals include: "how long has this problem existed before they started evaluating?" (long timelines suggest tolerance of non-consumption), and search volume for the problem description vs. the solution category (high problem search, low solution search = large non-consumption pool). [D5]

**Sources:**
- [D1] Quoleady: G2 and Capterra review influence research 2025: https://www.quoleady.com/llmo-research/
- [D2] G2: Review platforms and funnel intent research: https://learn.g2.com/do-software-review-platforms-show-up-more-in-the-bottom-of-the-funnel
- [D3] Future of Prospecting: Discovery questions from G2/Capterra reviews: https://futureofprospecting.substack.com/p/i-found-my-best-discovery-question
- [D4] ReviewPower: G2 + Capterra analytics platform: https://eliteai.tools/tool/reviewpower
- [D5] Brian Rhea: Mapping the Competitive Landscape with JTBD (Evergreen): https://brianrhea.com/mapping-the-competitive-landscape-with-jtbd

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What does bad alternatives research look like?

**Findings:**

**Direct-competitor tunnel:** The most common failure — research maps only named SaaS competitors in the same category and calls it done. This produces a landscape that looks thorough but misses the two most dangerous alternatives: adjacent substitutes that solve the same job (and could reposition to take the whole market) and non-consumption (which tells you how urgent the pain actually is). Product positioning built on this incomplete map will be outflanked. [F1][F2]

**"Mirror not a map" — knowing WHAT without knowing WHY:** Founders collect pricing pages, feature lists, and G2 profiles, then believe they understand competitors. What they've actually built is a snapshot of surface signals without causal understanding of why customers choose each alternative. Strategic decisions require knowing why: what job is each alternative hired for, why buyers choose it initially, and what would cause them to leave. Knowing features without knowing jobs produces positioning that sounds competitive but doesn't resonate with actual buyers. [F1]

**One-time analysis treated as checkbox:** Many teams do alternatives research once, put it in a strategy doc, and never update it. Software markets shift fast — new entrants appear, incumbents reposition, pricing changes. An alternatives map older than 6 months in a fast-moving SaaS category is likely to have meaningful gaps. The alternative landscape should be treated as a living document updated on a regular cadence, not a one-time deliverable. [F2][F3]

**Chasing competitor features instead of own job:** Once alternatives are mapped, a common failure is using the research to justify reactive feature development — "Competitor X has Y, so we need it too." This leads to fragmented product roadmaps, diluted identity, and the Vine antipattern (Vine had 200M users, mimicked Instagram/Snapchat features instead of doubling down on short-form loops, and shut down). The correct use of alternatives research is to understand what job each alternative owns, then identify jobs that are underserved or owned by weak alternatives. [F3]

**Ignoring the "fallback alternative" question:** In win/loss interviews, the question "If we hadn't existed, what would you have done?" is routinely skipped because it feels hypothetical. In practice, this question surfaces the most honest competitive threat — the alternative a buyer would default to if the product disappeared tomorrow. This is often a tier-3 DIY or a larger platform with a feature that roughly covers the job, not a named direct competitor. [F4]

**Sources:**
- [F1] Octopus CI: How Founders Screw Up Competitive Intelligence: https://octopuscompetitiveintelligence.substack.com/p/how-founders-are-screwing-up-competitive
- [F2] Charisol: 8 Mistakes in Competitor Analysis: https://charisol.io/8-mistakes-to-avoid-in-competitor-analysis/
- [F3] Itamar Novick: Startup Anti-Pattern — Chasing the Competition: https://www.itamarnovick.com/startup-anti-pattern-6-chasing-the-competition/
- [F4] Klue: Win-Loss Interview Methodology 2025: https://klue.com/blog/win-loss-interviews

---

## Synthesis

The highest-value update for this skill is the methodological shift from "list what competitors do" to "map what job each alternative owns and why buyers choose it." Multiple sources converge on the same finding: surface-level review of competitor websites and pricing pages produces a mirror (what they look like), not a map (why buyers choose them). The research methodology needs a primary source — win/loss interviews with actual buyers — and secondary sources (review mining, Reddit, Similarweb) to triangulate the primary findings.

The second key finding is that non-consumption must be treated as an explicit alternative tier, not an afterthought. In pre-PMF or early-stage markets, the most common competitive outcome is not "buyer chose competitor X" but "buyer kept doing what they were doing." Review platforms and API tools cannot surface this; only direct interview data can. The SKILL.md currently lists three tiers but doesn't give the researcher enough operational guidance on how to research non-consumption specifically.

The tool landscape is broader than the current SKILL.md suggests. G2's API is real and usable but requires attention to rate limits (100 req/sec) and may require enterprise account access for some endpoints — third-party scrapers are a practical fallback. Reddit is genuinely one of the highest-signal sources for authentic switching stories, and specific search patterns ("switched from X to") dramatically improve signal quality over general queries. Similarweb's Similar Sites API is useful for algorithmic alternative discovery but is limited to 40 results per request and desktop-only data.

There is a tension between the JTBD purist view (switch interviews are the gold standard) and the practical critique of switch interviews (rear-view mirror, hard to translate into product decisions). This resolves pragmatically: switch interview questions embedded in win/loss interviews are the best way to surface alternatives evaluated in real purchase cycles, while the JTBD job-step mapping is the right framework for understanding which tier each alternative occupies. Neither alone is sufficient.

---

## Recommendations for SKILL.md

- Add win/loss interview methodology as the primary source for alternatives data, with the specific 5-question sequence for extracting alternatives evaluated.
- Add non-consumption as an explicit fourth tier with guidance on how to research it (interview signals, proxy indicators).
- Expand the current "Tier 1/2/3" classification to include the job-based framing: what job does each alternative own, not just what category it sits in.
- Update the G2 tool entry with actual API rate limits and fallback options.
- Add Reddit search operator patterns explicitly.
- Add anti-patterns section: direct-competitor tunnel, one-time-analysis trap, chasing features instead of jobs.
- Add schema: artifact should require `tier`, `job_owned`, `switch_triggers`, `switch_away_triggers`, and `evidence_source` per alternative.

---

## Draft Content for SKILL.md

### Draft: Updated role statement and core mode

You map the full landscape of alternatives customers use or seriously consider when solving the problem your product addresses. This includes named competitors, adjacent tools, DIY approaches, and non-consumption — the last of which is often the largest "competitor" in early markets and the hardest to detect.

Core mode: alternatives research is buyer-behavior research, not product benchmarking. The question is not "what features do competitors have?" but "why do buyers choose each alternative, and what would cause them to stop?" A landscape map without switch triggers and job-ownership is a list of names, not a strategy input.

---

### Draft: Methodology — win/loss interview as primary source

Before mining any secondary source (reviews, Reddit, G2), determine whether interview data from recent buyers is available. If it is, this is your primary source. Secondary sources triangulate and expand what interviews surface — they don't replace them.

**Win/loss interview question sequence for alternatives extraction:**

Use these questions in order. Do not skip ahead. Each question builds context for the next.

1. "Before you started evaluating us, what were you already doing to solve this problem?" — Captures the status quo alternative. This is the "competitor zero": what the buyer was already paying for or doing. If the answer is "nothing," probe: "What did that look like in practice — spreadsheets, manual work, a different team handling it?"

2. "What made you start looking for something different?" — Captures the switch trigger: the specific event or accumulation that made the status quo unacceptable. This is one of the most valuable data points in the artifact because it tells you when buyers become in-market, not just which alternatives they considered.

3. "Who else did you look at seriously?" — Captures the actual shortlist. "Seriously" is a critical qualifier — filter out alternatives mentioned as passing thoughts vs. alternatives that received a trial, a demo, or a procurement review.

4. "Why did those options not make the cut?" — Captures competitor weaknesses from the buyer's perspective, which are more reliable than your own analysis of competitor gaps.

5. "If we hadn't existed, what would you have done?" — Captures the fallback alternative. This is often a tier-3 DIY or a larger platform with rough feature coverage. It reveals what the buyer's true ceiling of pain tolerance is, which directly informs positioning urgency.

Interview logistics: 20-30 minutes, conducted by a researcher or product manager (not the sales rep who worked the deal — the social relationship creates bias). Use Five Whys or Laddering techniques when answers are surface-level ("it was too expensive" → "what specifically triggered the cost concern?").

---

### Draft: Updated alternative tiers with job framing

Map each alternative to one of four tiers. For each, document the job it owns — the specific outcome buyers hire it to deliver — not just its product category.

**Tier 1 — Direct competitors:** Same category, same target segment, evaluated head-to-head. Buyer has typically demoed or trialed both. Document: job owned, pricing tier, key strengths from buyer-reported data, key weaknesses from review data.

**Tier 2 — Adjacent substitutes:** Different product category, but solves the same underlying job by a different mechanism. Example: a project management tool used as a lightweight CRM. These are harder to identify through G2 category browsing and almost always surface through interviews or Reddit research. Document: job owned (which is identical to or overlapping with tier 1), why buyers choose this path, what would cause them to switch to a dedicated solution.

**Tier 3 — DIY alternatives:** Spreadsheets, internal builds, manual processes, or hiring a person to do the job. No G2 profile. Research sources: interviews only, or search for "[problem description] excel template" / "[problem] notion template" as a proxy signal for DIY prevalence.

**Tier 4 — Non-consumption:** Buyer is aware of the problem but has not acted on it. They tolerate the pain, deprioritize it, or don't believe a solution exists. This is the most important tier for pre-PMF markets and the least visible in secondary research. Research sources: interviews (ask "how long has this been a problem before you started looking?"), and proxy: search volume gap between problem-description queries and solution-category queries. A large gap indicates a non-consumption market.

---

### Draft: Updated alternative identification sources

Secondary sources to use after interviews:

**G2 API (programmatic access):**
```
g2(op="call", args={"method_id": "g2.products.alternatives.v1", "filter[product_id]": "product_id"})
```
Rate limit: 100 requests per second; blocked for 60 seconds if exceeded. Pagination: `page[size]` max 100. Enterprise account may be required for some endpoints — if access fails, use G2 Scraper API (g2scraper.com) as fallback. G2's alternatives pages are buyer-curated, making them more reliable than algorithmic similarity. Extract: product names, category tags, and use these to identify tier-1 and tier-2 alternatives systematically.

**Reddit (highest signal for authentic switching stories):**
```
reddit(op="call", args={"method_id": "reddit.search.posts.v1", "q": "switched from [product] OR alternative to [product] OR [product] vs", "sort": "relevance", "t": "year"})
```
Use these search patterns in order of signal quality:
1. `"switched from [product] to"` — highest signal, explicit migration story
2. `"alternative to [product name]"` — active evaluation signal
3. `"[product] vs [competitor]"` — comparison intent
4. `"cheaper than [product]"` — price-driven switch signal

Target subreddits: r/SaaS, r/startups, r/Entrepreneur. For function-specific alternatives: r/analytics, r/projectmanagement, r/sales, r/marketing. Sort by recency; software alternatives change faster than annual cycles.

**Similarweb Similar Sites (algorithmic discovery):**
```
similarweb(op="call", args={"method_id": "similarweb.similar_sites.get.v1", "domain": "competitor.com"})
```
Returns up to 40 similar sites with similarity scores. Desktop-only data. Use to surface alternatives you haven't explicitly searched for — review the returned domains and classify each into the four tiers. Not a substitute for interview-sourced alternatives, but reliably catches tier-2 adjacents that don't appear in G2 category searches.

**Pattern extraction from review text:**
When mining reviews on G2, Capterra, or Trustpilot, extract these specific patterns:
- `"I switched from X because..."` → tier-1 or tier-2 alternative + switch trigger. High-confidence signal.
- `"I also tried X but..."` → alternative considered in same cycle. Medium-confidence.
- `"I use X alongside because..."` → complementary tool pointing to a capability gap. Surfaces tier-2 adjacents.
- `"I wish it did X like [competitor]"` → feature gap vs. specific alternative. Use for positioning, not for tiering.

Count named products across all pattern occurrences. Frequency is a reliability signal: alternatives named by many reviewers independently are tier-1 or strong tier-2; alternatives named once are noise unless confirmed by interview data.

---

### Draft: Anti-patterns

#### Direct-Competitor Tunnel
**What it looks like:** The alternatives map contains only named SaaS products in the same G2 category. Tier 3 (DIY) and Tier 4 (non-consumption) are absent.
**Detection signal:** Every row in the artifact has a product name, a G2 profile, and a pricing page. No row says "spreadsheet" or "manual process" or "tolerate the pain."
**Consequence:** Positioning is calibrated against products, not against the actual incumbent — the status quo. Urgency messaging misses the buyer who is not considering any SaaS alternative yet.
**Mitigation:** Require at least one Tier 3 and one Tier 4 entry in the artifact before marking the skill output complete. If interview data is unavailable, search for "[problem] excel template" and report search volume as a DIY prevalence proxy.

#### One-Time Analysis
**What it looks like:** The alternatives landscape was researched at founding or product launch and has not been updated.
**Detection signal:** `research_date` in the artifact is more than 6 months old in a fast-moving category.
**Consequence:** New entrants, incumbent repositioning, and pricing changes are invisible. Positioning decisions are made against a stale map.
**Mitigation:** When producing the artifact, set a `review_by` date no more than 6 months out. Flag in the artifact if it is being used as a decision input more than 3 months after `research_date`.

#### Features-Only Lens
**What it looks like:** Each alternative is described by its feature set and pricing tier. No entry includes why buyers initially chose this alternative or what would cause them to leave.
**Detection signal:** The artifact answers "what does each alternative do" but not "when and why do buyers hire it."
**Consequence:** Positioning built on this artifact will be feature-comparison positioning, which competes on the incumbent's terms rather than creating a distinct category.
**Mitigation:** Require `job_owned` and `switch_away_triggers` fields in each alternative entry. If these cannot be populated from secondary research, mark as `requires_interview_validation`.

---

### Draft: Schema additions

```json
{
  "alternatives_landscape": {
    "type": "object",
    "description": "Full map of alternatives customers use or consider for the problem addressed by this product.",
    "required": ["research_date", "review_by", "problem_statement", "alternatives", "non_consumption"],
    "additionalProperties": false,
    "properties": {
      "research_date": {
        "type": "string",
        "format": "date",
        "description": "Date this research was conducted (YYYY-MM-DD). Used to flag staleness."
      },
      "review_by": {
        "type": "string",
        "format": "date",
        "description": "Date by which this research should be re-validated. Set no more than 6 months from research_date in fast-moving categories."
      },
      "problem_statement": {
        "type": "string",
        "description": "The specific job or problem this landscape maps alternatives for. Must be written from the buyer's perspective, not the product's perspective."
      },
      "alternatives": {
        "type": "array",
        "description": "Named alternatives evaluated or used by buyers. Excludes non-consumption (see separate field).",
        "items": {
          "type": "object",
          "required": ["name", "tier", "job_owned", "switch_to_triggers", "switch_away_triggers", "evidence_sources", "confidence"],
          "additionalProperties": false,
          "properties": {
            "name": {
              "type": "string",
              "description": "Product or approach name. For DIY: use descriptive label like 'Excel + manual tracking' or 'Internal build'."
            },
            "tier": {
              "type": "string",
              "enum": ["direct", "adjacent", "diy"],
              "description": "Tier classification: direct = same category head-to-head; adjacent = different category same job; diy = spreadsheet, manual process, internal build."
            },
            "job_owned": {
              "type": "string",
              "description": "The specific outcome buyers hire this alternative to deliver. Written as a job statement: 'help me [verb] [outcome] [context]'. Not a feature description."
            },
            "switch_to_triggers": {
              "type": "array",
              "items": {"type": "string"},
              "description": "Events or conditions that cause buyers to choose this alternative. Source from interviews or review patterns ('switched from X to Y because...')."
            },
            "switch_away_triggers": {
              "type": "array",
              "items": {"type": "string"},
              "description": "Events or conditions that cause buyers to leave this alternative. Source from competitor reviews (1-2 star reviews of this alternative) and win/loss interviews."
            },
            "evidence_sources": {
              "type": "array",
              "items": {
                "type": "string",
                "enum": ["win_loss_interview", "customer_interview", "g2_reviews", "capterra_reviews", "reddit", "producthunt", "similarweb", "other"]
              },
              "description": "Sources that produced evidence for this alternative. Determines confidence level."
            },
            "confidence": {
              "type": "string",
              "enum": ["high", "medium", "low"],
              "description": "High: confirmed by at least one direct interview. Medium: sourced from multiple secondary sources. Low: single secondary source or inference."
            }
          }
        }
      },
      "non_consumption": {
        "type": "object",
        "description": "Characterization of buyers who tolerate the problem without adopting any solution. Often the dominant competitive force in early markets.",
        "required": ["prevalence_signal", "tolerance_duration", "evidence_source"],
        "additionalProperties": false,
        "properties": {
          "prevalence_signal": {
            "type": "string",
            "description": "How non-consumption was detected: interview data, search volume gap, estimated market size vs active buyers, or proxy indicators."
          },
          "tolerance_duration": {
            "type": "string",
            "description": "Typical time buyers have tolerated the problem before starting to evaluate solutions. Source from interviews ('how long has this been a problem?')."
          },
          "switch_trigger": {
            "type": "string",
            "description": "The event or threshold that causes non-consumers to enter the market. Often a specific business milestone, headcount threshold, compliance requirement, or pain accumulation event."
          },
          "evidence_source": {
            "type": "string",
            "description": "Where evidence for non-consumption patterns was found. Usually interview data; note if only proxy signals available."
          }
        }
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- G2 API pricing for enterprise access is not publicly documented. Implementers should contact G2 sales or plan to use third-party scrapers (g2scraper.com, Apify) as fallback. Assumption that enterprise account is required for full API access should be verified per account.
- ProductHunt API capabilities for alternatives queries were not verified with current API v2 documentation — the method ID in the SKILL.md (`producthunt.graphql.posts.alternatives.v1`) should be validated against live API before use.
- Similarweb Similar Sites API returning desktop-only data is a meaningful limitation for mobile-first products or markets — no mobile-equivalent API endpoint was found.
- Non-consumption research methodology is under-documented in the literature; the proxy signals described (search volume gap, DIY template search volume) are logical but not validated against controlled research.
- Win/loss interview availability depends on company stage: pre-launch companies have no buyers to interview. For this case, the skill needs a fallback path using only secondary research — this is not specified in either the current SKILL.md or this research.
