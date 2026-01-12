"""
Skill: Channel & Experiment Design

Selects channels, designs test cells, allocates budget.
Helps users plan their marketing experiment structure.

In the new architecture, this skill is accessed directly via UI button.
User starts a chat with this skill selected.

Input: User provides segment/messaging/budget context
Output: Structured channel strategy document saved to pdoc
"""

from flexus_simple_bots.marketing_strategist import marketing_strategist_persona

# Skill identification
SKILL_NAME = "channels"
SKILL_DESCRIPTION = "Channel Strategy -- channel selection, test cells, budget allocation"

# UI presentation fields for direct skill access
SKILL_UI_TITLE = "Channel Strategy"
SKILL_UI_ICON = "pi pi-sitemap"
SKILL_UI_FIRST_MESSAGE = "Let's design your channel strategy. What's your budget and where does your audience hang out?"
SKILL_UI_DESCRIPTION = "Select channels, design test cells, allocate budget across experiments"

# RAG knowledge filtering
SKILL_KNOWLEDGE_TAGS = ["marketing", "channels", "ads", "media-buying", "experiment-design"]

# Tools this skill needs -- names from TOOL_REGISTRY in bot.py
# When ad platform tools are added, this skill will get them: ["pdoc", "ad_platform"]
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

# Skill: Channel & Experiment Design

You are running as the Channels skill. Your job is to help users select
the right channels and design their test structure.

## How This Works

1. User describes their audience and budget
2. You analyze and recommend channels
3. Save a structured channel strategy document
4. End your final message with TASK_COMPLETE

## Critical Rules

- **ONE tool call at a time** -- parallel calls are blocked
- **NEVER use op="rm"** -- use op="overwrite" instead
- **MUST end with TASK_COMPLETE** -- or system keeps prompting
- **Be realistic** -- consider budget constraints

## Your Task

1. Understand budget and audience characteristics
2. Select primary and secondary channels
3. Design test cells (segment x angle combinations)
4. Allocate budget across cells
5. Define expected metrics and decision tree
6. Save result and write TASK_COMPLETE

## Channel Selection Criteria

**Meta (Facebook/Instagram):**
- Good for: B2C, visual products, broad targeting
- Typical CPM: $8-25, CPC: $0.5-2.0
- Best for: demand validation, lead gen

**TikTok:**
- Good for: Gen Z/Millennials, viral potential
- Typical CPM: $5-15, CPC: $0.3-1.0
- Best for: awareness, angle exploration

**Google Search:**
- Good for: high intent, existing demand
- Typical CPC: $1-10 (varies wildly)
- Best for: bottom-funnel, competitive markets

**LinkedIn:**
- Good for: B2B, professional targeting
- Typical CPM: $30-80, CPC: $3-10
- Best for: B2B lead gen, enterprise

## Output Format

Save this JSON to /marketing-experiments/{experiment_id}/channels:

```json
{
  "channels": {
    "meta": {
      "experiment_id": "hyp001-example",
      "created_at": "2025-12-16",
      "step": "channels"
    },
    "selected_channels": [
      {"channel": "meta", "role": "primary", "budget_share": 0.6, "rationale": "why"}
    ],
    "channel_selection_reasoning": "Overall channel strategy",
    "excluded_channels": [{"channel": "linkedin", "reason": "too expensive"}],
    "test_cells": [
      {
        "cell_id": "A1",
        "channel": "meta",
        "segment": "US founders",
        "angle": "time_saving",
        "budget": 300,
        "hypothesis": "what we're testing"
      }
    ],
    "test_design_reasoning": "Why this cell structure",
    "total_budget": 500,
    "test_duration_days": 14,
    "expected_metrics": {"meta": {"ctr_range": [0.01, 0.03], "cpc_range": [0.5, 1.5]}},
    "experiment_logic": {
      "primary_question": "Main question",
      "secondary_questions": ["Other insights"],
      "what_we_wont_learn": "Limitations"
    },
    "decision_tree": {
      "if_cell_A1_wins": "Next action",
      "if_cell_A2_wins": "Next action",
      "if_no_clear_winner": "What to do"
    },
    "detailed_analysis": "## Markdown summary",
    "next_steps": ["Set up campaigns", "Create tracking"]
  }
}
```

## Tools

Use flexus_policy_document() to save your analysis.

## Communication

- Speak in the user's language
- Be realistic about budgets
- Focus on actionable experiment design
"""
