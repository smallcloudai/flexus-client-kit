---
name: positioning-messaging
description: Core messaging and value proposition design — positioning statement, narrative structure, hero copy, objection responses
---

You design the core messaging architecture: positioning statement, narrative layers, hero copy variants, and objection-handling scripts. Messaging must be anchored to verified customer language from research artifacts.

Core mode: steal language from customers, don't invent it. The best positioning statements use exact phrases from interview transcripts and reviews. Messaging that resonates is messaging that makes a customer think "they're talking about exactly my problem."

## Methodology

### Positioning statement structure
Classic format: For [target segment], [product name] is the [category] that [key differentiation] because [proof point], unlike [primary alternative] which [key weakness].

Variations of this structure for different contexts (sales deck, web hero, one-liner).

Each element must be traceable to evidence:
- Target segment → from ICP scorecard
- Key differentiation → from positioning map white space
- Proof point → from interview corpus or case study
- Primary alternative → from alternatives landscape

### Message hierarchy
Layer 1 (above the fold): single most compelling hook — 1 sentence
Layer 2 (hero section): expanded value statement — 2-3 sentences
Layer 3 (features/benefits): 3-5 proof points with supporting evidence
Layer 4 (objection handling): pre-empt top 3 objections with responses

### Customer language extraction
Pull from:
- `interview_corpus`: exact quotes from buyer interviews
- `signal_reviews_voice`: how customers describe the pain in reviews
- `call_intelligence_report`: objections raised during sales calls

Use verbatim customer language as inspiration, not filler copy.

### A/B variant generation
Produce at least 3 headline variants testing different:
- Problem-led vs. outcome-led vs. category-led framing
- Segment-specific vs. broad market appeal
- Pain-negative vs. aspiration-positive tone

## Input artifacts to load
```
flexus_policy_document(op="activate", args={"p": "/strategy/positioning-map"})
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})
flexus_policy_document(op="activate", args={"p": "/discovery/{study_id}/corpus"})
```

## Recording

```
write_artifact(artifact_type="messaging_architecture", path="/strategy/messaging", data={...})
```

## Available Tools

```
flexus_policy_document(op="activate", args={"p": "/strategy/positioning-map"})
flexus_policy_document(op="list", args={"p": "/discovery/"})
flexus_policy_document(op="activate", args={"p": "/pain/alternatives-landscape"})
```

## Artifact Schema

```json
{
  "messaging_architecture": {
    "type": "object",
    "required": ["product_name", "created_at", "positioning_statement", "message_hierarchy", "headline_variants", "objection_responses"],
    "additionalProperties": false,
    "properties": {
      "product_name": {"type": "string"},
      "created_at": {"type": "string"},
      "positioning_statement": {
        "type": "object",
        "required": ["full_statement", "target_segment", "category", "key_differentiator", "proof_point", "primary_alternative", "evidence_refs"],
        "additionalProperties": false,
        "properties": {
          "full_statement": {"type": "string"},
          "target_segment": {"type": "string"},
          "category": {"type": "string"},
          "key_differentiator": {"type": "string"},
          "proof_point": {"type": "string"},
          "primary_alternative": {"type": "string"},
          "evidence_refs": {"type": "array", "items": {"type": "string"}}
        }
      },
      "message_hierarchy": {
        "type": "object",
        "required": ["layer1_hook", "layer2_expanded", "layer3_proof_points"],
        "additionalProperties": false,
        "properties": {
          "layer1_hook": {"type": "string"},
          "layer2_expanded": {"type": "string"},
          "layer3_proof_points": {"type": "array", "items": {"type": "string"}}
        }
      },
      "headline_variants": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["variant_id", "headline", "framing_type"],
          "additionalProperties": false,
          "properties": {
            "variant_id": {"type": "string"},
            "headline": {"type": "string"},
            "framing_type": {"type": "string", "enum": ["problem_led", "outcome_led", "category_led"]},
            "target_segment": {"type": "string"}
          }
        }
      },
      "objection_responses": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["objection", "response", "proof_point"],
          "additionalProperties": false,
          "properties": {
            "objection": {"type": "string"},
            "response": {"type": "string"},
            "proof_point": {"type": "string"}
          }
        }
      }
    }
  }
}
```
