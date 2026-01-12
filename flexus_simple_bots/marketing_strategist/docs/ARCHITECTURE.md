# Marketing Strategist: Two-Layer Bot Architecture

This document describes the architectural approach used in Marketing Strategist bot,
serving as a reference implementation for the new skill-based bot paradigm.

## Overview

The bot consists of two layers:

```
+--------------------------------------------------+
|                   PERSONA LAYER                   |
|  - Bot identity (Marketing Strategist)            |
|  - Core competencies list                         |
|  - General work pattern                           |
+--------------------------------------------------+
                        |
                        v
+--------------------------------------------------+
|                   SKILLS LAYER                    |
|  +----------+  +----------+  +----------+        |
|  |diagnostic|  | metrics  |  | segment  |  ...   |
|  +----------+  +----------+  +----------+        |
|                                                  |
|  Each skill contains:                            |
|  - System prompt (domain expertise)              |
|  - Lark kernel (validation/control)              |
|  - Tools (shared pdoc tool)                      |
|  - UI fields (title, icon, first_message)        |
|  - Knowledge tags (RAG filtering) [PLANNED]      |
+--------------------------------------------------+
```

## Key Principles

### 1. No Orchestrator

Legacy pattern had a "default" skill that acted as orchestrator, managing pipeline
and calling sub-skills via `run_agent`, `save_input`, etc.

New pattern: All skills are equal. User/Task accesses skills directly via UI button.
No pipeline management, no orchestrator tools.

### 2. Direct Skill Access

Each skill is visible in UI (`fexp_ui_hidden=False`) with:
- `fexp_ui_title`: Display name (e.g., "Diagnostic Analysis")
- `fexp_ui_icon`: PrimeIcons icon (e.g., "pi pi-search")
- `fexp_ui_first_message`: First bot message when skill selected
- `fexp_ui_description`: Tooltip description

User clicks skill button → new chat starts with that skill's system prompt.

### 3. Persona Injection

Each skill's `SYSTEM_PROMPT` is prefixed with `PERSONA_PROMPT`:

```python
SYSTEM_PROMPT = marketing_strategist_persona.PERSONA_PROMPT + """
# Skill: Diagnostic Analysis
...skill-specific content...
"""
```

This maintains consistent bot identity across all skills.

### 4. Isolated Skills

Each skill is self-contained:
- Receives context in first message (user describes their situation)
- Does its work (analysis, document creation)
- Saves result to pdoc
- Ends with `TASK_COMPLETE` marker

No dependency on other skills running first. User can start with any skill.

## Tool Architecture

### Centralized Tool Registry

All tools are defined in `bot.py` in `TOOL_REGISTRY`:

```python
TOOL_REGISTRY = {
    "pdoc": fi_pdoc.POLICY_DOCUMENT_TOOL,
    # Future tools:
    # "web_search": web_research.SEARCH_TOOL,
    # "ad_platform": ad_platform.META_ADS_TOOL,
}
```

### Per-Skill Tool Declaration

Each skill declares which tools it needs:

```python
# skills/diagnostic.py
SKILL_TOOLS = ["pdoc"]

# skills/channels.py (future)
SKILL_TOOLS = ["pdoc", "ad_platform"]
```

### Resolution Flow

```
install.py                          bot.py
+--------------------------+        +------------------+
| _tools_json_for_skill(   |  --->  | get_tools_for_   |
|   skill.SKILL_TOOLS      |        |   skill(names)   |
| )                        |        +------------------+
+--------------------------+               |
                                           v
                                    +------------------+
                                    | TOOL_REGISTRY    |
                                    | resolves names   |
                                    | to tool objects  |
                                    +------------------+
```

### Benefits

1. **Centralization**: All tools in one place (bot.py)
2. **Minimal access**: Skills only get tools they declare
3. **Fail-fast**: Unknown tool name = immediate error
4. **Documentation**: SKILL_TOOLS shows dependencies
5. **Extensibility**: Add tool to registry, add name to skills

## File Structure

```
marketing_strategist/
  __init__.py
  marketing_strategist_persona.py   # PERSONA_PROMPT, PERSONA_COMPETENCIES
  marketing_strategist_prompts.py   # DEFAULT_PROMPT for free-talk
  marketing_strategist_bot.py       # TOOL_REGISTRY, get_tools_for_skill(), main loop
  marketing_strategist_install.py   # Marketplace registration, _tools_json_for_skill()
  skills/
    __init__.py
    diagnostic.py                   # SKILL_NAME, SKILL_TOOLS, SYSTEM_PROMPT, etc.
    metrics.py
    segment.py
    messaging.py
    channels.py
    tactics.py
    compliance.py
  docs/
    ARCHITECTURE.md                 # This file
    SKILL_PATTERN.md                # How to create new skills
```

## Comparison with Legacy Pattern

| Aspect | Legacy (Owl) | New (Marketing) |
|--------|--------------|-----------------|
| Default skill | Orchestrator with pipeline tools | Simple free-talk |
| Skill access | Via `run_agent()` tool | Direct UI button |
| Skill visibility | Hidden (`fexp_ui_hidden=True`) | Visible (`fexp_ui_hidden=False`) |
| Pipeline order | Enforced by orchestrator | None, user chooses |
| Tool count in default | 5 (save_input, run_agent, etc.) | 1 (pdoc only) |
| Completion marker | `AGENT_COMPLETE` | `TASK_COMPLETE` |
| Tool definition | Separate lists (TOOLS, AGENT_TOOLS) | Centralized TOOL_REGISTRY |
| Tool access | All skills get same tools | Per-skill via SKILL_TOOLS |

## Benefits

1. **Simpler code**: No orchestrator logic to maintain
2. **Faster development**: Add skill = add file, no orchestrator changes
3. **User flexibility**: Users choose what they need, no forced pipeline
4. **Better UX**: Clear skill buttons instead of talking to orchestrator
5. **Easier testing**: Each skill testable independently
6. **Future-ready**: Task system will assign directly to skills

## When to Use This Pattern

Use two-layer architecture when:
- Bot has multiple distinct areas of expertise
- Each area can work independently
- Users benefit from direct access to specific capabilities

Keep orchestrator pattern when:
- Strict workflow order is business-critical
- Users must not skip steps
- Pipeline state management is core feature
