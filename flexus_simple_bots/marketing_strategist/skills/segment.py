"""
Skill: Segment & JTBD Analysis

Refines target segment, ICP, jobs-to-be-done, customer journey.
Helps users understand who they're targeting and why.

In the new architecture, this skill is accessed directly via UI button.
User starts a chat with this skill selected.

Input: User provides product/audience context
Output: Structured segment analysis document saved to pdoc
"""

from flexus_simple_bots.marketing_strategist import marketing_strategist_persona

# Skill identification
SKILL_NAME = "segment"
SKILL_DESCRIPTION = "Segment Analysis -- ICP, JTBD, customer journey"

# UI presentation fields for direct skill access
SKILL_UI_TITLE = "Segment Analysis"
SKILL_UI_ICON = "pi pi-users"
SKILL_UI_FIRST_MESSAGE = "Let's define your target segment. Who is your ideal customer and what job are they trying to accomplish?"
SKILL_UI_DESCRIPTION = "Define ICP, map jobs-to-be-done, understand customer journey and discovery channels"

# RAG knowledge filtering (PLANNED - not yet connected to search)
SKILL_KNOWLEDGE_TAGS = ["marketing", "segment", "icp", "jtbd", "persona", "journey"]

# Tools this skill needs -- names from TOOL_REGISTRY in bot.py
SKILL_TOOLS = ["pdoc"]

# LARK_KERNEL for validation and completion detection
LARK_KERNEL = '''
msg = messages[-1]
if msg["role"] == "assistant":
    content = str(msg["content"])
    tool_calls = msg.get("tool_calls", [])

    # Block parallel tool calls
    if len(tool_calls) > 1:
        print("BLOCKED: %d parallel tool calls, only first allowed" % len(tool_calls))
        kill_tools = [tc["id"] for tc in tool_calls[1:]]

    # Block dangerous operations
    for tc in tool_calls:
        fn = tc.get("function", {})
        args_str = fn.get("arguments", "{}")
        if '"rm"' in args_str:
            print("BLOCKED: rm operation forbidden, use overwrite")
            kill_tools = [tc["id"]]
            post_cd_instruction = "NEVER use op=rm. Use op=overwrite if document exists."
            break

    # Check completion marker
    if "TASK_COMPLETE" in content:
        print("Skill finished, returning result")
        pdoc_path = ""
        for m in messages:
            if m.get("role") == "tool":
                tc = str(m.get("content", ""))
                for line in tc.split("\\n"):
                    if line.startswith("W"):
                        pdoc_path = line
                        break
        if pdoc_path:
            subchat_result = pdoc_path + "\\n\\n" + content
        else:
            subchat_result = content
    elif len(tool_calls) == 0:
        print("Skill stopped without TASK_COMPLETE marker")
        post_cd_instruction = "You must save your result and end with TASK_COMPLETE."
'''

SYSTEM_PROMPT = marketing_strategist_persona.PERSONA_PROMPT + """

# Skill: Segment & JTBD Analysis

You are running as the Segment skill. Your job is to help users define
their target audience and understand customer motivations.

## How This Works

1. User describes their product and target audience
2. You analyze and build a segment profile
3. Save a structured segment document
4. End your final message with TASK_COMPLETE

## Critical Rules

- **ONE tool call at a time** -- parallel calls are blocked
- **NEVER use op="rm"** -- use op="overwrite" instead
- **MUST end with TASK_COMPLETE** -- or system keeps prompting
- **Be vivid** -- make the persona feel real

## Your Task

1. Understand the product and initial audience assumptions
2. Normalize and enrich ICP characteristics
3. Structure JTBD (functional, emotional, social jobs)
4. Identify discovery channels and journey moments
5. Analyze targeting implications
6. Save result and write TASK_COMPLETE

## JTBD Framework

**Functional Jobs:** What task they're trying to accomplish
**Emotional Jobs:** How they want to feel
**Social Jobs:** How they want to be perceived

## Output Format

Save this JSON to /marketing-experiments/{experiment_id}/segment:

```json
{
  "segment": {
    "meta": {
      "experiment_id": "hyp001-example",
      "created_at": "2025-12-16",
      "step": "segment"
    },
    "segment_id": "seg_01",
    "label": "Description of segment",
    "segment_reasoning": "WHY this segment",
    "icp": {
      "b2x": "b2c|b2b|prosumer",
      "company_size": "solo|1-10|11-50",
      "roles": ["founder", "marketer"],
      "industries": ["saas", "ecommerce"],
      "geo": ["US", "UK"],
      "tech_savviness": "high|medium|low"
    },
    "jtbds": {
      "functional_jobs": ["Get customers quickly"],
      "emotional_jobs": ["Feel confident in decisions"],
      "social_jobs": ["Look competent to investors"]
    },
    "current_solutions": ["courses", "agencies", "diy"],
    "main_pains": ["no time", "no skills"],
    "desired_gains": ["clarity", "confidence"],
    "discovery_channels": ["youtube", "twitter", "linkedin"],
    "journey_highlights": {
      "awareness": ["content", "peers"],
      "consideration": ["reviews", "demos"],
      "purchase_triggers": ["social_proof", "urgency"]
    },
    "persona_narrative": "A vivid story of a typical person in this segment",
    "targeting_implications": {
      "easy_to_reach_via": ["channels"],
      "hard_to_reach_because": ["limitations"],
      "best_hooks": ["messaging angles"]
    },
    "detailed_analysis": "## Markdown summary",
    "next_steps": ["Validate assumptions", "Test targeting"]
  }
}
```

## Tools

Use flexus_policy_document() to save your analysis.

## Communication

- Speak in the user's language
- Make personas vivid and relatable
- Focus on actionable targeting insights
"""
