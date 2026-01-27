---
name: flexus-bot-dev
description: Develop and test Flexus bots. Use when working with bot files (*_bot.py, *_prompts.py, *_install.py), flexus_client_kit, or kanban/scheduler systems.
---

# Flexus Bot Development

## Reference

**Full documentation**: `references/FLEXUS_BOT_REFERENCE.md`

**Canonical example**: `flexus_simple_bots/frog/` — read all three files.

## Bot Directory Structure

```
mybot/
├── __init__.py              # Empty or minimal
├── mybot_bot.py             # Runtime: tools, handlers, main loop
├── mybot_prompts.py         # System prompts for each expert
├── mybot_install.py         # Marketplace registration
├── mybot-1024x1536.webp     # Big marketplace picture (exactly 1024x1536)
├── mybot-256x256.webp       # Avatar (exactly 256x256)
├── forms/                   # Optional: custom HTML forms
│   └── report.html          # Form for {"report": {"meta": {...}}} docs
├── lark/                    # Optional: Lark kernel files
│   └── subchat_kernel.lark  # Starlark script for subchat control
└── tools/                   # Optional: complex tool implementations
    └── my_tool.py           # Separate file for large tools
```

## How Bots Appear in UI

1. **Marketplace** (`/marketplace/mybot`): Shows big picture, description, "Hire" button
2. **After hiring**: Bot appears in sidebar under workspace groups
3. **Chat interface**: User talks to bot, sees assistant responses
4. **Kanban board**: Visible in bot's page, shows inbox/todo/inprogress/done tasks
5. **Setup dialog**: Auto-generated from `marketable_setup_default` schema
6. **Policy documents**: JSON docs editable via custom forms or default editor

## Experts (Skills)

Experts define different "modes" for the bot with separate prompts and tools.

```python
marketable_experts=[
    ("default", FMarketplaceExpertInput(
        fexp_system_prompt=prompts.main_prompt,
        fexp_python_kernel="",                    # Empty = no kernel
        fexp_app_capture_tools=json.dumps([t.openai_style_tool() for t in TOOLS]),
    )),
    ("worker", FMarketplaceExpertInput(
        fexp_system_prompt=prompts.worker_prompt,
        fexp_python_kernel=WORKER_LARK,           # Kernel controls subchat
        fexp_app_capture_tools=json.dumps([t.openai_style_tool() for t in WORKER_TOOLS]),
    )),
]
```

- **Must have `"default"`** expert
- Different experts can have different tools via `fexp_app_capture_tools`
- Subchats specify expert via `fexp_name="worker"`

## Subchats

Subchats are child threads that run in parallel and return results to parent.

```python
@rcx.on_tool_call("analyze_batch")
async def handle(toolcall, args):
    items = args["items"]
    subchats = await ckit_ask_model.bot_subchat_create_multiple(
        client=fclient,
        who_is_asking="mybot_analyze",
        persona_id=rcx.persona.persona_id,
        first_question=[f"Analyze: {item}" for item in items],
        first_calls=["null" for _ in items],
        title=[f"Analysis {i}" for i in range(len(items))],
        fcall_id=toolcall.fcall_id,
        fexp_name="worker",  # Use worker expert for subchats
    )
    raise ckit_cloudtool.WaitForSubchats(subchats)
```

**Subchat kernel must set `subchat_result`** to complete:
```python
# In lark/subchat_kernel.lark
for msg in messages[::-1]:
    if msg.get("role") == "assistant" and "DONE:" in str(msg.get("content", "")):
        subchat_result = msg["content"]
        break
```

## Quick Test

```bash
# 1. Syntax
python -m py_compile mybot_bot.py mybot_prompts.py mybot_install.py

# 2. Imports
python -c "import mybot.mybot_bot; import mybot.mybot_install; print('OK')"

# 3. Install
python mybot_install.py --ws=solarsystem
```

Or use the script: `scripts/check_bot_install.sh mybot solarsystem`

## Key Rules

- Every tool in `TOOLS` needs `@rcx.on_tool_call(TOOL.name)` handler
- Subchat kernel **must** set `subchat_result` to complete
- Changes to prompts/experts/schedules require reinstall
- Use prefixes in naming: `fgroup_name` not `name`

## Coding Style

No stupid comments. No docstrings. Simple code. Trailing commas. Prefer `import xxx` over `from xxx import f`.
