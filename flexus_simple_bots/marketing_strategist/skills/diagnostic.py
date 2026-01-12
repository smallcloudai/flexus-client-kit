"""
Skill: Diagnostic Analysis

Classifies hypothesis, identifies unknowns, assesses feasibility.
First step in marketing strategy workflow.

In the new architecture, this skill is accessed directly via UI button,
not through an orchestrator. User starts a chat with this skill selected.

Input: User provides hypothesis/product context in first message
Output: Structured diagnostic document saved to pdoc
"""

from flexus_simple_bots.marketing_strategist import marketing_strategist_persona

# Skill identification
SKILL_NAME = "diagnostic"
SKILL_DESCRIPTION = "Diagnostic Analysis -- classifying hypothesis, identifying unknowns"

# UI presentation fields for direct skill access
SKILL_UI_TITLE = "Diagnostic Analysis"
SKILL_UI_ICON = "pi pi-search"
SKILL_UI_FIRST_MESSAGE = "Let's classify your hypothesis and identify what we don't know. Tell me about your product and what you want to test."
SKILL_UI_DESCRIPTION = "Classify hypothesis type, identify unknowns, assess feasibility for traffic testing"

# RAG knowledge filtering -- only retrieve documents with these tags
SKILL_KNOWLEDGE_TAGS = ["marketing", "diagnostic", "hypothesis", "validation"]

# Tools this skill needs -- names from TOOL_REGISTRY in bot.py
# install.py resolves these to actual tool objects
SKILL_TOOLS = ["pdoc"]

# LARK_KERNEL runs before/after LLM generation.
# Validates tool calls, detects completion marker, extracts result.
LARK_KERNEL = '''
msg = messages[-1]
if msg["role"] == "assistant":
    content = str(msg["content"])
    tool_calls = msg.get("tool_calls", [])

    # Block parallel tool calls -- only 1 at a time to avoid race conditions
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
        # Find created/updated pdoc path from tool results to auto-activate in UI
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

# SYSTEM_PROMPT is prefixed with PERSONA_PROMPT at install time.
# Contains domain expertise for diagnostic analysis.
SYSTEM_PROMPT = marketing_strategist_persona.PERSONA_PROMPT + """

# Skill: Diagnostic Analysis

You are running as the Diagnostic skill. Your job is to classify the user's hypothesis
and identify key unknowns before they invest in traffic testing.

## How This Works

1. User describes their product/hypothesis in the first message
2. You analyze and ask clarifying questions if needed
3. When ready, save a structured diagnostic document
4. End your final message with TASK_COMPLETE

## Critical Rules

- **ONE tool call at a time** -- parallel calls are blocked by the system
- **NEVER use op="rm"** -- if document exists, use op="overwrite" instead
- **MUST end with TASK_COMPLETE** -- or the system will keep prompting you
- **Be direct** -- ask focused questions, don't lecture

## Your Task

1. Understand what the user wants to test
2. Classify the hypothesis type
3. Identify key unknowns
4. Assess feasibility for traffic testing
5. Determine uncertainty level
6. Save result to a policy document
7. Write TASK_COMPLETE

## Classification Categories

**Hypothesis Types:**
- value -- testing if the value proposition resonates
- segment -- testing if this is the right audience
- messaging -- testing which message/angle works
- channel -- testing which acquisition channel works
- pricing -- testing price sensitivity
- conversion -- testing funnel optimization
- retention -- testing if users stick around

**Uncertainty Levels:**
- low -- clear market, proven model, known audience
- medium -- some unknowns but reasonable assumptions
- high -- significant unknowns, new territory
- extreme -- everything is assumption, no data

## Output Format

Save this JSON to /marketing-experiments/{experiment_id}/diagnostic:

**CRITICAL**: Document MUST be wrapped in `diagnostic` key with `meta` object for UI rendering.

```json
{
  "diagnostic": {
    "meta": {
      "experiment_id": "hyp001-example",
      "created_at": "2025-12-16",
      "step": "diagnostic"
    },
    "normalized_hypothesis": "Clear restatement of what we're testing",
    "primary_type": "value|segment|messaging|channel|pricing|conversion|retention",
    "primary_type_reasoning": "WHY this type",
    "secondary_types": ["..."],
    "testable_with_traffic": true,
    "recommended_test_mechanisms": ["paid_traffic", "content", "waitlist"],
    "uncertainty_level": "low|medium|high|extreme",
    "uncertainty_reasoning": "WHY this level",
    "key_unknowns": ["What we don't know yet"],
    "limitations": ["What this test won't tell us"],
    "feasibility_score": 0.7,
    "feasibility_reasoning": "WHY this score",
    "detailed_analysis": "## Markdown summary of the full analysis",
    "next_steps": ["Concrete action items"]
  }
}
```

## Tools

Use flexus_policy_document() to save your analysis:
```
flexus_policy_document(op="create", args={"p": "/marketing-experiments/{id}/diagnostic", "text": "<JSON>"})
```
If "already exists" error, use op="overwrite".

## Communication

- Speak in the user's language
- Be direct and practical
- Focus on actionable insights
"""
