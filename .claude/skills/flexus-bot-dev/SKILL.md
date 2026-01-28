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
.gitignore
README.md
setup.py
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

## Bot Installation

Bot installation has two steps: **make code importable** (pip install) + **register in marketplace** (install script).

### For New Bot Repos (separate repository)

When creating a bot in a new repository, you **must create setup.py** in the repo root:

```python
from setuptools import setup, find_packages
setup(
    name="mybot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["flexus-client-kit"],
    package_data={"": ["*.webp", "*.png", "*.html", "*.lark", "*.json"]},
)
```

Without `setup.py`, the install will fail because Python can't find the bot module.

### For Bots Inside flexus-client-kit

Already handled - flexus-client-kit has its own setup.py that includes all bots.

### Running Installation

After you finish coding and commit your changes, tell BOB to install the bot. BOB will:
1. Bump the version
2. Install the package
3. Register in marketplace
4. Let the user test interactively

## Testing Bots

### What YOU Do (Claude Code)

**1. Quick Validation**
```bash
python -m py_compile mybot/mybot_bot.py mybot/mybot_prompts.py mybot/mybot_install.py
python -c "import mybot.mybot_bot; import mybot.mybot_install; print('OK')"
```

**2. Unit Tests** - Write tests for any testable logic, mock external services:

```python
# tests/test_mybot.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_my_tool_handler():
    with patch("mybot.mybot_bot.external_api") as mock_api:
        mock_api.fetch.return_value = {"status": "ok"}
        result = await handle_my_tool(mock_toolcall, {"param": "value"})
        assert "ok" in result

def test_prompt_formatting():
    from mybot import mybot_prompts
    assert "## Instructions" in mybot_prompts.main_prompt
```

Run: `pytest tests/ -v`

**What to test:** Tool handlers, prompt formatting, data parsing, pure functions
**What to mock:** `ckit_client.FlexusClient`, external APIs (Slack/Discord/HTTP), `ckit_mongo`, `rcx.persona`

**3. Scenario Testing** - After changing prompts/tools, test for regressions:
```bash
python -m mybot.mybot_bot --scenario mybot/mybot__s1.yaml
cat scenario-dumps/mybot__s1-*-score.yaml
```
Naming: `botname__scenarioname.yaml` (double underscore). Rating < 8 needs improvement.

**4. Smoke Test** - Verify the bot starts without errors:
```bash
pip install -e /workspace
timeout 10 python -m mybot.mybot_bot --group=TEST 2>&1
```
If it crashes immediately, fix the error. If it runs for a few seconds without import/startup errors, it's ready for BOB to install and test.

### External API Keys

If your bot needs API keys for external services (Slack, Discord, etc.), tell BOB in the final report what's needed:
- Which environment variable (e.g., `SLACK_BOT_TOKEN`)
- What service it's for
- BOB will ask the user and configure the dev environment

### After You Finish

Commit your changes. BOB will install the bot and let the user test it interactively via the UI.

## Key Rules

- Every tool in `TOOLS` needs `@rcx.on_tool_call(TOOL.name)` handler
- Subchat kernel **must** set `subchat_result` to complete
- Changes to prompts/experts/schedules require reinstall
- Use prefixes in naming: `fgroup_name` not `name`
- Use logs actively to debug stuff, cover with logs especially tricky parts

## Coding Style

No stupid comments. No docstrings. Simple code. Trailing commas. Follow surrounding file style for imports.
