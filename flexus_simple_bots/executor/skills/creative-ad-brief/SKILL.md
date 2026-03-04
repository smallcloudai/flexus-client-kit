---
name: creative-ad-brief
description: Ad creative brief design — creative strategy, format specifications, copy framework, and visual direction for paid campaigns
---

You produce structured creative briefs for paid ad campaigns. A brief converts a campaign strategy into actionable instructions for creative production. Without a brief, creative is disconnected from audience and messaging.

Core mode: every brief must be anchored to a specific audience segment and a specific pain/desire from research. "Broad audience, general benefit messaging" is not a brief — it's a placeholder.

## Methodology

### Brief components
A complete brief answers:
1. **Who are we talking to?** — ICP persona, pain state, awareness level (problem-aware, solution-aware, product-aware)
2. **What do we want them to feel or do?** — Single primary outcome (click, sign up, request demo)
3. **What's the one thing we're saying?** — Single message (not 3 benefits at once)
4. **Why should they believe it?** — Social proof, data point, or demonstration that removes doubt
5. **What's the hook?** — Opening frame that earns attention in first 3 seconds (video) or first glance (static)

### Awareness level calibration
Ads to cold audiences (problem-unaware):
- Lead with the pain or outcome, NOT the product
- "Are you still using [painful workaround]?" — calls out current state
- Never start with company name or feature list

Ads to warm audiences (retargeting, product-aware):
- Can reference the product by name
- Use social proof and risk reduction
- Urgency or offer can be explicit

### Format selection
Match format to platform and budget:
- Meta: video (9:16 or 1:1), static image, carousel
- LinkedIn: static + caption, video (shorter), lead gen form
- Google: search (text only), performance max (various), display
- TikTok: video only (native UGC style outperforms polished)

### Hook framework
For video: first 3 seconds must stop the scroll. Options:
- Shocking stat: "73% of [ICP] report [pain] weekly"
- Pain mirror: "If you've ever [painful experience]..."
- Disruption: unexpected visual that creates curiosity
- Pattern interrupt: break format expectations

## Recording

```
write_artifact(artifact_type="ad_creative_brief", path="/campaigns/{campaign_id}/creative-brief", data={...})
```

## Available Tools

```
flexus_policy_document(op="activate", args={"p": "/strategy/messaging"})
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})
flexus_policy_document(op="activate", args={"p": "/strategy/gtm-channel-strategy"})
```

## Artifact Schema

```json
{
  "ad_creative_brief": {
    "type": "object",
    "required": ["campaign_id", "created_at", "audience", "campaign_objective", "primary_message", "proof_point", "formats", "hook_options"],
    "additionalProperties": false,
    "properties": {
      "campaign_id": {"type": "string"},
      "created_at": {"type": "string"},
      "audience": {
        "type": "object",
        "required": ["persona", "awareness_level", "pain_state", "platform"],
        "additionalProperties": false,
        "properties": {
          "persona": {"type": "string"},
          "awareness_level": {"type": "string", "enum": ["problem_unaware", "problem_aware", "solution_aware", "product_aware", "most_aware"]},
          "pain_state": {"type": "string"},
          "platform": {"type": "string", "enum": ["meta", "google", "linkedin", "tiktok", "x"]}
        }
      },
      "campaign_objective": {"type": "string", "enum": ["awareness", "lead_gen", "conversion", "retargeting"]},
      "primary_message": {"type": "string"},
      "proof_point": {"type": "string"},
      "formats": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["format_type", "aspect_ratio", "duration_seconds"],
          "additionalProperties": false,
          "properties": {
            "format_type": {"type": "string", "enum": ["video", "static_image", "carousel", "lead_gen_form", "text_search"]},
            "aspect_ratio": {"type": "string"},
            "duration_seconds": {"type": ["integer", "null"]},
            "copy_limits": {"type": "object"}
          }
        }
      },
      "hook_options": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["hook_text", "hook_type"],
          "additionalProperties": false,
          "properties": {
            "hook_text": {"type": "string"},
            "hook_type": {"type": "string", "enum": ["shocking_stat", "pain_mirror", "disruption", "pattern_interrupt", "social_proof"]}
          }
        }
      },
      "do_list": {"type": "array", "items": {"type": "string"}},
      "dont_list": {"type": "array", "items": {"type": "string"}}
    }
  }
}
```
