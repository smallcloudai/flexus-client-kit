---
name: pain-alternatives-landscape
description: Alternatives landscape mapping — how customers currently solve the problem, competitor positioning, switching patterns
---

You map the landscape of alternatives that customers use or consider when solving the problem your product addresses. This skill produces a structured competitor / alternative map that feeds positioning and offer design in the strategist.

Core mode: alternatives ≠ direct competitors only. Alternatives include: doing nothing, spreadsheets, internal tools, adjacent SaaS products, hiring a person to do it manually. Map all of them, not just named competitors.

## Methodology

### Alternative identification sources
1. Review platforms (g2, trustpilot, capterra): reviews often name what the customer switched FROM and why
2. Reddit discussions: users frequently ask "what are you using for X?" — these threads are goldmines
3. StackExchange / HN: technical audiences discuss tool comparisons explicitly
4. ProductHunt: alternatives pages are explicitly mapped
5. Similarweb "similar sites": algorithmic alternatives discovery

Pattern to extract from reviews:
- "I switched from X because..." → named alternative + switch trigger
- "I also tried X but..." → alternatives considered in same purchase cycle
- "I use X alongside this because..." → complementary tools that indicate a gap

### Competitive positioning analysis
For each identified alternative:
- What do they claim to do better? (pricing page, hero messaging, G2 profile)
- What problems do their reviewers complain about? (from `signal-reviews-voice`)
- Who are their top customers? (Clearbit logos or case studies)
- How are they growing? (Similarweb trends from `signal-competitive-web`)

### Switching pattern analysis
From interview corpus and CRM notes, extract:
- What drove the switch AWAY from each alternative?
- What caused people to choose the alternative initially?
- What would cause them to switch AGAIN?

### Alternative tiers
Tier 1: Direct competitors (same category, head-to-head)
Tier 2: Adjacent solutions (different category, address same job)
Tier 3: DIY alternatives (spreadsheet, custom build, hiring)

## Recording

```
write_artifact(artifact_type="alternatives_landscape", path="/pain/alternatives-landscape", data={...})
```

## Available Tools

```
g2(op="call", args={"method_id": "g2.products.alternatives.v1", "filter[product_id]": "product_id"})

producthunt(op="call", args={"method_id": "producthunt.graphql.posts.alternatives.v1", "slug": "product-slug"})

reddit(op="call", args={"method_id": "reddit.search.posts.v1", "q": "alternative to [product] OR vs [product]", "sort": "relevance", "t": "year"})

similarweb(op="call", args={"method_id": "similarweb.similar_sites.get.v1", "domain": "competitor.com"})

trustpilot(op="call", args={"method_id": "trustpilot.reviews.list.v1", "businessUnitId": "unit_id", "stars": [1, 2], "language": "en"})
```

## Artifact Schema

```json
{
  "alternatives_landscape": {
    "type": "object",
    "required": ["problem_space", "mapped_at", "alternatives", "switching_patterns", "positioning_gaps"],
    "additionalProperties": false,
    "properties": {
      "problem_space": {"type": "string"},
      "mapped_at": {"type": "string"},
      "alternatives": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["name", "tier", "category", "claimed_strengths", "known_weaknesses", "evidence_sources"],
          "additionalProperties": false,
          "properties": {
            "name": {"type": "string"},
            "tier": {"type": "string", "enum": ["tier1_direct", "tier2_adjacent", "tier3_diy"]},
            "category": {"type": "string"},
            "claimed_strengths": {"type": "array", "items": {"type": "string"}},
            "known_weaknesses": {"type": "array", "items": {"type": "string"}},
            "evidence_sources": {"type": "array", "items": {"type": "string"}}
          }
        }
      },
      "switching_patterns": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["direction", "trigger", "frequency_signal"],
          "additionalProperties": false,
          "properties": {
            "direction": {"type": "string", "description": "e.g. 'from [competitor] to us' or 'to [competitor] from us'"},
            "trigger": {"type": "string"},
            "frequency_signal": {"type": "string", "enum": ["high", "medium", "low"]}
          }
        }
      },
      "positioning_gaps": {"type": "array", "items": {"type": "string"}}
    }
  }
}
```
