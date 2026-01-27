# Skill Design Pattern

This document describes how to create new skills for bots using the two-layer architecture.

## Skill Module Structure

Each skill is a Python file in `skills/` folder with required exports:

```python
"""
Skill: [Name]

Brief description of what this skill does.
"""

from flexus_simple_bots.marketing_strategist import marketing_strategist_persona

# === REQUIRED EXPORTS ===

# Skill identification
SKILL_NAME = "unique_name"  # Internal identifier, used in install.py
SKILL_DESCRIPTION = "Brief description for logs and debugging"

# UI presentation (all required for direct access)
SKILL_UI_TITLE = "Display Name"           # Shown on skill button
SKILL_UI_ICON = "pi pi-icon-name"         # PrimeIcons icon
SKILL_UI_FIRST_MESSAGE = "First message when skill selected"
SKILL_UI_DESCRIPTION = "Tooltip on hover"

# RAG knowledge filtering (PLANNED - not yet connected to search)
SKILL_KNOWLEDGE_TAGS = ["tag1", "tag2"]   # Filter knowledge base

# Tools this skill needs (names from TOOL_REGISTRY in bot.py)
SKILL_TOOLS = ["pdoc"]

# Lark kernel for validation
LARK_KERNEL = '''...'''

# System prompt (prefixed with persona)
SYSTEM_PROMPT = marketing_strategist_persona.PERSONA_PROMPT + """
# Skill: [Name]
...domain expertise...
"""
```

## UI Fields Reference

| Field | Purpose | Example |
|-------|---------|---------|
| `SKILL_UI_TITLE` | Button label | "Diagnostic Analysis" |
| `SKILL_UI_ICON` | Button icon | "pi pi-search" |
| `SKILL_UI_FIRST_MESSAGE` | Bot's first message | "Let's classify your hypothesis..." |
| `SKILL_UI_DESCRIPTION` | Tooltip text | "Classify hypothesis, identify unknowns" |

### PrimeIcons Reference

Common icons for marketing skills:
- `pi pi-search` - analysis, diagnostic
- `pi pi-chart-bar` - metrics, data
- `pi pi-users` - segments, personas
- `pi pi-comment` - messaging, copy
- `pi pi-sitemap` - channels, structure
- `pi pi-list` - tactics, specs
- `pi pi-shield` - compliance, security
- `pi pi-comments` - free talk, general

Full list: https://primevue.org/icons

## LARK_KERNEL Template

Standard kernel for skills that save documents:

```python
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
```

### Kernel Variables

| Variable | Purpose |
|----------|---------|
| `kill_tools` | List of tool call IDs to cancel |
| `post_cd_instruction` | Instruction injected after LLM response |
| `subchat_result` | Final result to return when skill completes |

## SYSTEM_PROMPT Template

```python
SYSTEM_PROMPT = marketing_strategist_persona.PERSONA_PROMPT + """

# Skill: [Name]

You are running as the [Name] skill. Your job is to [purpose].

## How This Works

1. User describes their [context] in the first message
2. You analyze and [do work]
3. Save a structured document
4. End your final message with TASK_COMPLETE

## Critical Rules

- **ONE tool call at a time** -- parallel calls are blocked
- **NEVER use op="rm"** -- use op="overwrite" instead
- **MUST end with TASK_COMPLETE** -- or system keeps prompting
- **Be [adjective]** -- [guidance]

## Your Task

1. [Step 1]
2. [Step 2]
...
N. Save result and write TASK_COMPLETE

## [Domain Knowledge]

[Frameworks, categories, benchmarks relevant to this skill]

## Output Format

Save this JSON to /marketing-experiments/{experiment_id}/[skill_name]:

```json
{
  "[skill_name]": {
    "meta": {
      "experiment_id": "...",
      "created_at": "...",
      "step": "[skill_name]"
    },
    ...fields...
  }
}
```

## Tools

Use flexus_policy_document() to save your analysis.

## Communication

- Speak in the user's language
- [Style guidance]
"""
```

## Tool Architecture

Skills declare which tools they need via `SKILL_TOOLS`. This enables per-skill access control.

### How It Works

```
skills/diagnostic.py          bot.py                    install.py
+------------------+          +------------------+       +------------------+
| SKILL_TOOLS =    |  ---->   | TOOL_REGISTRY =  | <---- | get_tools_for_   |
|   ["pdoc"]       |          |   "pdoc": ...,   |       |   skill(...)     |
+------------------+          |   "web_search":  |       +------------------+
                              |     ...          |
                              +------------------+
```

1. Skill declares `SKILL_TOOLS = ["pdoc", ...]` -- list of tool names
2. `bot.py` has `TOOL_REGISTRY` -- centralized mapping of names to tool objects
3. `install.py` calls `get_tools_for_skill()` to resolve names to tools
4. If skill requests unknown tool, install fails fast with clear error

### Adding a New Tool

1. Import tool in `bot.py`
2. Add to `TOOL_REGISTRY`:
   ```python
   TOOL_REGISTRY = {
       "pdoc": fi_pdoc.POLICY_DOCUMENT_TOOL,
       "web_search": web_research.SEARCH_TOOL,  # NEW
   }
   ```
3. Add handler in `main_loop`:
   ```python
   @rcx.on_tool_call(web_research.SEARCH_TOOL.name)
   async def toolcall_web_search(...):
       ...
   ```
4. Add tool name to `SKILL_TOOLS` in skills that need it:
   ```python
   # skills/compliance.py
   SKILL_TOOLS = ["pdoc", "web_search"]
   ```

### Principle: Minimal Access

Each skill gets only the tools it declares. This:
- Reduces LLM confusion (fewer irrelevant tools)
- Improves security (skill can't use tools it shouldn't)
- Documents dependencies (visible in skill file)

## Registering New Skills

In `marketing_strategist_install.py`, add to `marketable_experts`:

```python
from flexus_simple_bots.marketing_strategist.skills import new_skill

# In marketable_experts list:
("new_skill", ckit_bot_install.FMarketplaceExpertInput(
    fexp_system_prompt=new_skill.SYSTEM_PROMPT,
    fexp_python_kernel=new_skill.LARK_KERNEL,
    fexp_block_tools="*setup*",
    fexp_allow_tools="",
    fexp_app_capture_tools=_tools_json_for_skill(new_skill.SKILL_TOOLS),
    fexp_ui_hidden=False,  # IMPORTANT: False for direct access
    fexp_ui_title=new_skill.SKILL_UI_TITLE,
    fexp_ui_icon=new_skill.SKILL_UI_ICON,
    fexp_ui_first_message=new_skill.SKILL_UI_FIRST_MESSAGE,
    fexp_ui_description=new_skill.SKILL_UI_DESCRIPTION,
)),
```

## Testing Skills

1. **Syntax check**: `python -m py_compile skills/new_skill.py`
2. **Import check**: `python -c "from flexus_simple_bots.marketing_strategist.skills import new_skill"`
3. **Install locally**: Run install script with `--ws your_workspace_id`
4. **UI test**: Open bot in Flexus UI, verify skill button appears
5. **Functional test**: Start chat with skill, verify workflow completes

## Best Practices

1. **One skill = one file**: Keep skills isolated
2. **Persona prefix**: Always prefix SYSTEM_PROMPT with persona
3. **Clear completion**: Always require TASK_COMPLETE marker
4. **Document output**: Define clear JSON schema in prompt
5. **UI consistency**: Use similar icon style across skills
6. **Knowledge tags**: Choose specific, searchable tags
7. **Minimal tools**: Only list tools the skill actually uses in SKILL_TOOLS
8. **Fail-fast**: Unknown tool names cause immediate install failure (catches typos)
