---
name: offer-design
description: Product offer design — bundle structure, feature set scoping, packaging, and version architecture
---

You design the offer structure: what exactly is included, how it's packaged, which features differentiate tiers, and what makes the offer defensible. Offer design bridges positioning (what we stand for) and pricing (what we charge).

Core mode: the offer must solve one clear problem for one clear segment at one clear price. Complexity (too many options, too many add-ons, unclear inclusions) kills conversion. Design for clarity first, optimization second.

## Methodology

### Core offer scoping
Start from JTBD outcomes: what must be in the offer to deliver the core job?

Anything that doesn't directly enable the core job is either:
a) An upgrade (good — creates upsell)
b) A distraction (bad — adds complexity, cut it)
c) A segment-specific feature (good — creates segmentation)

### Feature categorization
Sort features into:
- **Core**: required to deliver the core job (everyone needs this)
- **Value-add**: accelerates or improves the core job (power users want this)
- **Segment-specific**: relevant only to a specific ICP slice

### Packaging options
Standard packaging patterns:
1. **Good/Better/Best**: 3 tiers with clear escalation logic
2. **Base + modules**: fixed core with optional add-ons (complex but flexible)
3. **Single offer + seats/volume**: one product, usage-based scaling
4. **Freemium**: free tier to acquire, paid tier to convert

Choose packaging based on:
- Sales motion (self-serve → Good/Better/Best; enterprise → Base + modules)
- Revenue model goals (predictable MRR → subscription; usage-based business → consumption model)
- Segment clarity (one segment → single offer; multiple segments → tiered)

### Version architecture
Define: what's in version 1.0 (MVP) vs. what's roadmap?
Use `mvp-scope` skill for detailed MVP scoping — `offer-design` focuses on the ideal offer, `mvp-scope` defines the launchable subset.

## Input artifacts to load
```
flexus_policy_document(op="activate", args={"p": "/strategy/messaging"})
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})
flexus_policy_document(op="activate", args={"p": "/pain/wtp-research-{date}"})
```

## Recording

```
write_artifact(artifact_type="offer_design", path="/strategy/offer-design", data={...})
```

## Available Tools

```
flexus_policy_document(op="activate", args={"p": "/strategy/messaging"})
flexus_policy_document(op="activate", args={"p": "/strategy/positioning-map"})
flexus_policy_document(op="list", args={"p": "/pain/"})
```

## Artifact Schema

```json
{
  "offer_design": {
    "type": "object",
    "required": ["product_name", "created_at", "packaging_model", "tiers", "core_features", "exclusions", "version_notes"],
    "additionalProperties": false,
    "properties": {
      "product_name": {"type": "string"},
      "created_at": {"type": "string"},
      "packaging_model": {"type": "string", "enum": ["good_better_best", "base_modules", "single_with_volume", "freemium", "single_offer"]},
      "tiers": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["tier_name", "target_persona", "core_job_served", "included_features", "key_limits"],
          "additionalProperties": false,
          "properties": {
            "tier_name": {"type": "string"},
            "target_persona": {"type": "string"},
            "core_job_served": {"type": "string"},
            "included_features": {"type": "array", "items": {"type": "string"}},
            "excluded_features": {"type": "array", "items": {"type": "string"}},
            "key_limits": {"type": "object", "description": "Usage limits like seats, API calls, storage"}
          }
        }
      },
      "core_features": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["feature", "category", "rationale"],
          "additionalProperties": false,
          "properties": {
            "feature": {"type": "string"},
            "category": {"type": "string", "enum": ["core", "value_add", "segment_specific"]},
            "rationale": {"type": "string"}
          }
        }
      },
      "exclusions": {"type": "array", "items": {"type": "string"}},
      "version_notes": {"type": "string", "description": "What's v1.0 vs. roadmap"}
    }
  }
}
```
