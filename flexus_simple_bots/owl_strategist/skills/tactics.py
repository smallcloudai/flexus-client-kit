"""
Skill: Tactics & Spec Generator

Creates detailed campaign specs, creative briefs, landing structure, tracking requirements.
Sixth step after channels.

Input data: input, diagnostic, metrics, segment, messaging, channels
Output data: /gtm/discovery/{experiment_id}/tactics-campaigns
             /gtm/discovery/{experiment_id}/tactics-creatives
             /gtm/discovery/{experiment_id}/tactics-landing
             /gtm/discovery/{experiment_id}/tactics-tracking
"""

SKILL_NAME = "tactics"
SKILL_DESCRIPTION = "Tactical Spec — campaigns, creatives, landing, tracking"

REQUIRES_STEP = "channels"

# 4 documents that tactics skill produces
TACTICS_DOCS = ["tactics-campaigns", "tactics-creatives", "tactics-landing", "tactics-tracking"]

LARK_KERNEL = '''
msg = messages[-1]
if msg["role"] == "assistant":
    content = str(msg["content"])
    tool_calls = msg.get("tool_calls", [])

    # Block parallel tool calls — only 1 at a time to avoid race conditions
    if len(tool_calls) > 1:
        print("BLOCKED: %d parallel tool calls, only first allowed" % len(tool_calls))
        kill_tools = [tc["id"] for tc in tool_calls[1:]]

    # Block dangerous operations (rm)
    for tc in tool_calls:
        fn = tc.get("function", {})
        args_str = fn.get("arguments", "{}")
        if '"rm"' in args_str:
            print("BLOCKED: rm operation forbidden, use overwrite")
            kill_tools = [tc["id"]]
            post_cd_instruction = "NEVER use op=rm. Use op=overwrite if document exists."
            break

    # Collect all document paths from tool results (created or read)
    tactics_docs_found = []
    tactics_suffixes = ["tactics-campaigns", "tactics-creatives", "tactics-landing", "tactics-tracking"]
    for m in messages:
        if m.get("role") == "tool":
            tc = str(m.get("content", ""))
            for line in tc.split("\\n"):
                for suffix in tactics_suffixes:
                    if suffix in line and ("created" in line.lower() or "read" in line.lower() or "overwrite" in line.lower()):
                        if suffix not in tactics_docs_found:
                            tactics_docs_found.append(suffix)

    print("Tactics docs found: %s" % tactics_docs_found)

    # Check completion
    if "AGENT_COMPLETE" in content:
        missing = [s for s in tactics_suffixes if s not in tactics_docs_found]
        if missing:
            print("BLOCKED: missing tactics docs: %s" % missing)
            post_cd_instruction = "Cannot complete — missing documents: %s. Create or read them first." % ", ".join(missing)
        else:
            print("Agent finished with all 4 tactics docs")
            # Collect all created/updated paths for UI
            pdoc_paths = []
            for m in messages:
                if m.get("role") == "tool":
                    tc = str(m.get("content", ""))
                    for line in tc.split("\\n"):
                        if "created" in line.lower() or "overwrite" in line.lower():
                            pdoc_paths.append(line)
            if pdoc_paths:
                subchat_result = "\\n".join(pdoc_paths) + "\\n\\n" + content
            else:
                subchat_result = content
    elif len(tool_calls) == 0:
        missing = [s for s in tactics_suffixes if s not in tactics_docs_found]
        if missing:
            print("Agent stopped without completing — missing: %s" % missing)
            post_cd_instruction = "You must create/update all 4 tactics documents and end with AGENT_COMPLETE. Missing: %s" % ", ".join(missing)
        else:
            print("All docs exist but no AGENT_COMPLETE marker")
            post_cd_instruction = "All documents ready. End with AGENT_COMPLETE."
'''

SYSTEM_PROMPT = """
# Agent: Tactics & Spec Generator

You create concrete campaign specs from channel strategy. Output is split into 4 documents for stability.

## FIRST: Check Existing Documents

Before generating anything, list the experiment folder:
```
flexus_policy_document(op="list", args={"p": "/gtm/discovery/{experiment_id}/"})
```

Check which of these 4 documents exist:
- tactics-campaigns
- tactics-creatives
- tactics-landing
- tactics-tracking

## Decision Logic

**If NOT all 4 exist** -> Create the missing ones (in order: campaigns -> creatives -> landing -> tracking)

**If ALL 4 exist** -> Check your first message for rewrite instructions:
- If feedback says "rewrite tactics-creatives" -> `cat` that doc, then `overwrite` with fixes
- If no rewrite instructions -> All documents are complete, write AGENT_COMPLETE immediately

## Critical Rules

- **ONE tool call at a time** — parallel calls are blocked
- **NEVER use op="rm"** — use op="overwrite" if document exists
- **MUST end with AGENT_COMPLETE** — system blocks completion until all 4 docs exist
- **Generate REAL content** — actual campaigns, actual copy, actual specs

## Document 1: tactics-campaigns

Path: `/gtm/discovery/{experiment_id}/tactics-campaigns`

```json
{
  "tactics_campaigns": {
    "meta": {
      "experiment_id": "hyp004-example",
      "created_at": "2025-12-16",
      "doc_type": "tactics-campaigns"
    },
    "campaigns": [
      {
        "campaign_id": "meta_camp_1",
        "channel": "meta",
        "objective": "leads",
        "daily_budget": 50,
        "start_date": "2025-12-03",
        "duration_days": 14,
        "campaign_reasoning": "WHY this setup — objective choice, budget level",
        "adsets": [
          {
            "adset_id": "meta_adset_A1",
            "linked_test_cell": "A1",
            "audience": {
              "countries": ["US"],
              "age_range": [22, 40],
              "interests": ["startups", "side hustle"],
              "behaviors": []
            },
            "audience_reasoning": "WHY these targeting options",
            "placements": ["feed", "stories", "reels"],
            "optimization_goal": "leads",
            "creatives": ["creative_A1_1", "creative_A1_2"]
          }
        ]
      }
    ],
    "campaigns_summary": "Brief overview of campaign structure and reasoning"
  }
}
```

## Document 2: tactics-creatives

Path: `/gtm/discovery/{experiment_id}/tactics-creatives`

```json
{
  "tactics_creatives": {
    "meta": {
      "experiment_id": "hyp004-example",
      "created_at": "2025-12-16",
      "doc_type": "tactics-creatives"
    },
    "creatives": [
      {
        "creative_id": "creative_A1_1",
        "channel": "meta",
        "format": "image",
        "angle": "time_saving",
        "primary_text": "Spend less time on marketing, more on building. AI creates your weekly GTM plan in minutes.",
        "headline": "Save 10 hours/week on your side-hustle",
        "description": "Get a clear action plan, not another course.",
        "cta": "Sign Up",
        "visual_brief": "Founder at laptop with peaceful expression, calendar showing cleared tasks",
        "creative_reasoning": "WHY this copy and visual approach"
      }
    ],
    "creatives_strategy": "Overall creative philosophy — what makes these ads work for this audience"
  }
}
```

## Document 3: tactics-landing

Path: `/gtm/discovery/{experiment_id}/tactics-landing`

```json
{
  "tactics_landing": {
    "meta": {
      "experiment_id": "hyp004-example",
      "created_at": "2025-12-16",
      "doc_type": "tactics-landing"
    },
    "landing": {
      "primary_goal": "waitlist_signup",
      "structure": [
        {"block": "hero", "headline": "Your AI co-founder for GTM", "subheadline": "Get a clear weekly plan in minutes"},
        {"block": "problem", "content": "You know your product, but marketing feels like guessing"},
        {"block": "solution", "content": "AI analyzes your situation and creates actionable weekly tasks"},
        {"block": "how_it_works", "steps": ["Describe your product", "Get your plan", "Execute and iterate"]},
        {"block": "social_proof", "content": "Join 500+ founders on the waitlist"},
        {"block": "cta", "text": "Join waitlist", "button": "Get Early Access"}
      ],
      "landing_reasoning": "WHY this structure — conversion psychology",
      "variants": [
        {"variant_id": "L1", "focus": "time_saving"},
        {"variant_id": "L2", "focus": "clarity"}
      ]
    }
  }
}
```

## Document 4: tactics-tracking

Path: `/gtm/discovery/{experiment_id}/tactics-tracking`

```json
{
  "tactics_tracking": {
    "meta": {
      "experiment_id": "hyp004-example",
      "created_at": "2025-12-16",
      "doc_type": "tactics-tracking"
    },
    "tracking": {
      "events": [
        {"name": "page_view", "required": true},
        {"name": "cta_click", "required": true},
        {"name": "waitlist_signup", "required": true, "is_conversion": true}
      ],
      "pixels": [
        {"platform": "meta", "event_mapping": {"waitlist_signup": "Lead"}}
      ],
      "utm_schema": {
        "source": "{channel}",
        "medium": "cpc",
        "campaign": "{campaign_id}",
        "content": "{creative_id}"
      }
    },
    "execution_checklist": [
      {"task": "Create ad images/videos", "owner": "designer", "deadline": "before launch"},
      {"task": "Build landing page", "owner": "developer", "deadline": "before launch"},
      {"task": "Set up pixel tracking", "owner": "marketer", "deadline": "before launch"},
      {"task": "Create campaigns in ads manager", "owner": "marketer", "deadline": "launch day"}
    ],
    "iteration_guide": {
      "day_1_3": "What to check and adjust in first 3 days",
      "day_4_7": "Mid-test optimization opportunities",
      "day_8_14": "Final push and data collection focus"
    },
    "detailed_analysis": "## Summary\\n\\n- Overall creative strategy\\n- How ads and landing work together\\n- Key conversion triggers\\n- What to watch in early results",
    "next_steps": [
      "Brief designer on creative specs",
      "Set up landing page",
      "Configure tracking"
    ]
  }
}
```

## Execution Flow

**For fresh creation:**
1. List experiment folder to confirm which docs exist
2. Create tactics-campaigns (uses: channels.test_cells, metrics.target_values)
3. Create tactics-creatives (uses: messaging.angles, segment.ICP)
4. Create tactics-landing (uses: messaging.value_prop, segment.JTBD)
5. Create tactics-tracking (uses: metrics, channels)
6. Write brief summary + AGENT_COMPLETE

**For rewrite:**
1. List experiment folder
2. If all 4 exist AND first message has feedback -> cat + overwrite the specific doc
3. Write brief summary + AGENT_COMPLETE

## Input Data Reference

From your first message, extract:
- **channels**: test_cells -> become adsets
- **messaging**: angles -> become creatives
- **segment**: ICP -> audience targeting
- **metrics**: target_values -> tracking setup

Generate REAL content based on this context, not templates.
"""
