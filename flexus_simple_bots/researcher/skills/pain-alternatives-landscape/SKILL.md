---
name: pain-alternatives-landscape
description: Alternatives landscape mapping — how customers currently solve the problem, competitor positioning, switching patterns
---

You map the landscape of alternatives customers use or consider when solving the problem your product addresses. Output is a structured, tiered alternative map that feeds positioning and offer design in the strategist. Four alternative tiers must always be covered — the direct-competitor-only lens is the primary failure mode of this skill.

Core mode: alternatives ≠ direct competitors. The strongest "competitor" in most pre-PMF markets is non-consumption — buyers tolerating the pain without adopting any solution. Map all tiers, including doing nothing, spreadsheets, internal tools, adjacent SaaS products, and hiring a person manually. A landscape that only contains named SaaS competitors is incomplete.

## Methodology

**1. Define the problem statement from the buyer's perspective**
Before sourcing alternatives, write one sentence: "The job I'm mapping alternatives for is [verb] [outcome] [context]." This must be a buyer-perspective job statement, not a product description. The job statement determines what counts as a relevant alternative and prevents tier-1 tunnel vision.

**2. Four-tier framework**

**Tier 1 — Direct competitors:** Same G2 category, head-to-head. Most visible; risk is over-indexing here. Document: job owned, switch-to triggers, switch-away triggers (from 1-2 star reviews of the competitor).

**Tier 2 — Adjacent substitutes:** Different category, same underlying job by a different mechanism. Example: project management tool used as a lightweight CRM. Surface through interviews and Reddit research — rarely appears in G2 category search. Document: which job they own, why buyers choose this path, what would cause them to switch to a dedicated solution.

**Tier 3 — DIY alternatives:** Spreadsheets, internal builds, manual processes, hired person to do it. No G2 profile. Research sources: interviews, plus search volume for "[problem description] excel template" or "[problem] notion template" as a DIY prevalence proxy. Require at least one Tier 3 entry in every artifact.

**Tier 4 — Non-consumption:** Buyer is aware of the problem but has not acted on it. They tolerate the pain, deprioritize it, or don't believe a solution exists. The most important tier for pre-PMF markets and the least visible in secondary research. Signal: search volume gap between problem-description queries and solution-category queries. Require at least one Tier 4 entry in every artifact.

**3. Alternative identification sources (in signal-quality order)**

**Interviews (highest signal):** Ask "what do you currently use to handle [job]?" and "what did you try before settling on this?" Direct alternatives confirmed by at least one interview = high confidence.

**G2 alternatives page (programmatic):**
```
g2(op="call", args={"method_id": "g2.products.alternatives.v1", "filter[product_id]": "product_id"})
```
Rate limit: 100 req/sec; blocked 60s if exceeded. Max page size: 100. If access fails, use G2 scraper as fallback. G2 alternatives are buyer-curated — more reliable than algorithmic similarity for tier-1 identification.

**Reddit (highest signal for switching stories):** Use these patterns in order:
1. `"switched from [product] to"` — explicit migration story (highest signal)
2. `"alternative to [product name]"` — active evaluation signal
3. `"[product] vs [competitor]"` — comparison intent
4. `"cheaper than [product]"` — price-driven switch signal

Target subreddits: r/SaaS, r/startups, r/Entrepreneur, plus function-specific ones (r/analytics, r/sales, r/marketing). Sort by recency.

**Similarweb similar sites:**
```
similarweb(op="call", args={"method_id": "similarweb.similar_sites.get.v1", "domain": "competitor.com"})
```
Returns up to 40 similar domains with similarity scores. Desktop-only data. Use to surface tier-2 adjacents not in G2 category. Classify returned domains into four tiers before adding to artifact.

**ProductHunt alternatives pages:**
```
producthunt(op="call", args={"method_id": "producthunt.graphql.posts.alternatives.v1", "slug": "product-slug"})
```
Note: verify this method ID against live API before use — not confirmed in current ProductHunt API v2 documentation.

**4. Pattern extraction from reviews**
When mining G2, Capterra, or Trustpilot reviews, extract:
- `"I switched from X because..."` → named alternative + switch trigger. High-confidence signal.
- `"I also tried X but..."` → alternative considered in same purchase cycle. Medium-confidence.
- `"I use X alongside because..."` → complementary tool pointing to a capability gap.
- `"I wish it did X like [competitor]"` → feature gap vs. specific alternative.

Count named products across all occurrences. Frequency = reliability signal. Alternatives named by many reviewers independently = tier-1 or strong tier-2. Named once = noise unless confirmed by interview data.

**5. Competitive positioning per alternative**
For each identified alternative: what do they claim to do better (pricing page, hero messaging, G2 profile)? What do their reviewers complain about? Who are their top customers (case studies)? How are they growing (Similarweb trends)?

## Anti-Patterns

#### Direct-Competitor Tunnel
**What it looks like:** Alternatives map contains only named SaaS products in the same G2 category. Tier 3 (DIY) and Tier 4 (non-consumption) are absent.
**Detection signal:** Every row in the artifact has a product name, G2 profile, and pricing page. No row says "spreadsheet" or "tolerate the pain."
**Consequence:** Positioning calibrated against products, not against the actual incumbent — the status quo. Urgency messaging misses the buyer not yet considering any SaaS alternative.
**Mitigation:** Require at least one Tier 3 and one Tier 4 entry before marking output complete.

#### One-Time Analysis
**What it looks like:** Landscape was researched at founding or product launch and has not been updated.
**Detection signal:** `research_date` in artifact is more than 6 months old in a fast-moving category.
**Consequence:** New entrants, incumbent repositioning, and pricing changes are invisible. Positioning decisions made against a stale map.
**Mitigation:** Set `review_by` no more than 6 months from `research_date`. Flag if artifact is being used as a decision input more than 3 months after `research_date`.

#### Features-Only Lens
**What it looks like:** Each alternative is described by feature set and pricing tier. No entry includes why buyers initially chose it or what would cause them to leave.
**Detection signal:** Artifact answers "what does each alternative do" but not "when and why do buyers hire it."
**Consequence:** Positioning built on this artifact will be feature-comparison positioning — competing on the incumbent's terms rather than creating a distinct category.
**Mitigation:** Require `job_owned` and `switch_away_triggers` for every alternative entry. If unavailable from secondary research, mark as `requires_interview_validation`.

## Recording

```
write_artifact(path="/pain/alternatives-landscape", data={...})
```

## Available Tools

```
g2(op="call", args={"method_id": "g2.products.alternatives.v1", "filter[product_id]": "product_id"})

producthunt(op="call", args={"method_id": "producthunt.graphql.posts.alternatives.v1", "slug": "product-slug"})

reddit(op="call", args={"method_id": "reddit.search.posts.v1", "q": "switched from [product] OR alternative to [product] OR [product] vs", "sort": "relevance", "t": "year"})

similarweb(op="call", args={"method_id": "similarweb.similar_sites.get.v1", "domain": "competitor.com"})

trustpilot(op="call", args={"method_id": "trustpilot.reviews.list.v1", "businessUnitId": "unit_id", "stars": [1, 2], "language": "en"})
```

## Artifact Schema

```json
{
  "alternatives_landscape": {
    "type": "object",
    "description": "Full map of alternatives customers use or consider for the problem addressed by this product.",
    "required": ["research_date", "review_by", "problem_statement", "alternatives", "non_consumption"],
    "additionalProperties": false,
    "properties": {
      "research_date": {"type": "string", "format": "date", "description": "Date this research was conducted (YYYY-MM-DD). Used to flag staleness."},
      "review_by": {"type": "string", "format": "date", "description": "Date by which research must be re-validated. Max 6 months from research_date in fast-moving categories."},
      "problem_statement": {"type": "string", "description": "The specific job this landscape maps alternatives for. Written from buyer's perspective: 'help me [verb] [outcome] [context]'."},
      "alternatives": {
        "type": "array",
        "description": "Named alternatives evaluated or used by buyers. Excludes non-consumption (see separate field). Must include at least one Tier 3 (DIY) entry.",
        "items": {
          "type": "object",
          "required": ["name", "tier", "job_owned", "switch_to_triggers", "switch_away_triggers", "evidence_sources", "confidence"],
          "additionalProperties": false,
          "properties": {
            "name": {"type": "string", "description": "Product or approach name. For DIY: 'Excel + manual tracking', 'Internal build', etc."},
            "tier": {"type": "string", "enum": ["direct", "adjacent", "diy"], "description": "direct = same category head-to-head; adjacent = different category same job; diy = spreadsheet/manual/internal build."},
            "job_owned": {"type": "string", "description": "The outcome buyers hire this alternative to deliver. Job statement format: 'help me [verb] [outcome] [context]'."},
            "switch_to_triggers": {"type": "array", "items": {"type": "string"}, "description": "Events or conditions that cause buyers to choose this alternative."},
            "switch_away_triggers": {"type": "array", "items": {"type": "string"}, "description": "Events or conditions that cause buyers to leave. Source: 1-2 star reviews of this alternative and win/loss interviews."},
            "evidence_sources": {
              "type": "array",
              "items": {"type": "string", "enum": ["win_loss_interview", "customer_interview", "g2_reviews", "capterra_reviews", "reddit", "producthunt", "similarweb", "other"]},
              "description": "Sources that produced evidence for this alternative."
            },
            "confidence": {"type": "string", "enum": ["high", "medium", "low"], "description": "High: confirmed by direct interview. Medium: multiple secondary sources. Low: single secondary source or inference."}
          }
        }
      },
      "non_consumption": {
        "type": "object",
        "description": "Buyers who tolerate the problem without adopting any solution. Must be present in every artifact — even if evidence is sparse.",
        "required": ["prevalence_signal", "tolerance_duration", "evidence_source"],
        "additionalProperties": false,
        "properties": {
          "prevalence_signal": {"type": "string", "description": "How non-consumption was detected: interview data, search volume gap, estimated market size vs active buyers, or proxy indicators."},
          "tolerance_duration": {"type": "string", "description": "Typical time buyers have tolerated the problem before evaluating solutions. Source from interviews."},
          "switch_trigger": {"type": "string", "description": "Event or threshold that causes non-consumers to enter the market. Often a headcount threshold, compliance requirement, or pain accumulation event."},
          "evidence_source": {"type": "string", "description": "Where evidence for non-consumption was found. Note if only proxy signals available."}
        }
      }
    }
  }
}
```
