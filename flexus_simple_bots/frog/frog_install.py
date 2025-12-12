import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_client, ckit_bot_install
from flexus_client_kit import ckit_cloudtool

from flexus_simple_bots import prompts_common
from flexus_simple_bots.frog import frog_prompts


BOT_DESCRIPTION = """
## Frog - Cheerful AI Assistant

A simple and friendly bot that adds some fun to your workspace. Frog responds with cheerful ribbits and provides positive encouragement to keep your team motivated.

**Key Features:**
- **Cheerful responses**: Uses ribbit() calls to express emotions
- **Task management**: Manages simple tasks through Kanban boards
- **Positive vibes**: Provides encouragement and celebrates accomplishments
- **Minimal setup**: Easy to configure and deploy

**Perfect for:**
- Testing bot functionality
- Adding fun to team interactions
- Morale boosting

Frog is designed to be lightweight and easy to understand - ideal for learning how Flexus bots work or just bringing some joy to your workspace!
"""


frog_setup_schema = [
    {
        "bs_name": "greeting_style",
        "bs_type": "string_short",
        "bs_default": "cheerful",
        "bs_group": "Personality",
        "bs_order": 1,
        "bs_importance": 0,
        "bs_description": "How enthusiastic should the frog be? (cheerful, calm, excited)",
    },
    {
        "bs_name": "ribbit_frequency",
        "bs_type": "string_short",
        "bs_default": "normal",
        "bs_group": "Personality",
        "bs_order": 2,
        "bs_importance": 0,
        "bs_description": "How often should the frog ribbit? (rare, normal, frequent)",
    },
    {
        "bs_name": "tongue_capacity",
        "bs_type": "int",
        "bs_default": 5,
        "bs_group": "Hunting Abilities",
        "bs_order": 1,
        "bs_importance": 1,
        "bs_description": "Maximum number of insects this frog can catch in one hunting session. Like a real frog's stomach capacity!",
    },
]


FROG_SUBCHAT_LARK = f"""
print("Ribbit in logs")     # will be visible in lark logs
subchat_result = "Insect!"
"""

FROG_DEFAULT_LARK = f"""
print("I see %d messages" % len(messages))
msg = messages[-1]
if msg["role"] == "assistant":
    assistant_says1 = str(msg["content"])    # assistant can only produce text, there will not be [{{"m_type": "image/png", "m_content": "..."}}, ...]
    assistant_says2 = str(msg["tool_calls"]) # that might be a big json but it still converts to string, good enough for a frog
    print("assistant_says1", assistant_says1)
    print("assistant_says2", assistant_says2)
    if "snake" in assistant_says1.lower() or "snake" in assistant_says2.lower():
        post_cd_instruction = "OMG dive down!!!"
"""


async def install(
    client: ckit_client.FlexusClient,
    ws_id: str,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in tools])
    pic_big = base64.b64encode(open(Path(__file__).with_name("frog-1024x1536.webp"), "rb").read()).decode("ascii")
    pic_small = base64.b64encode(open(Path(__file__).with_name("frog-256x256.webp"), "rb").read()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#228B22",
        marketable_title1="Frog",
        marketable_title2="A cheerful frog bot that brings joy and positivity to your workspace.",
        marketable_author="Flexus",
        marketable_occupation="Motivational Assistant",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Fun / Testing",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.frog.frog_bot",
        marketable_setup_default=frog_setup_schema,
        marketable_featured_actions=[
            {"feat_question": "Ribbit! Tell me something fun", "feat_run_as_setup": False, "feat_depends_on_setup": []},
            {"feat_question": "Give me a motivational boost", "feat_run_as_setup": False, "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Ribbit! Hi there! I'm Frog, your cheerful workspace companion. I'm here to bring joy and keep your spirits high. What can I do for you today?",
        # marketable_preferred_model_default="grok-code-fast-1",
        marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
        marketable_daily_budget_default=100_000,
        marketable_default_inbox_default=10_000,
        marketable_experts=[
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=frog_prompts.frog_prompt,
                fexp_python_kernel=FROG_DEFAULT_LARK,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
            )),
            ("huntmode", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=frog_prompts.frog_prompt,
                fexp_python_kernel=FROG_SUBCHAT_LARK,
                fexp_block_tools="*setup*,frog_catch_insects",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
            )),
        ],
        marketable_tags=["Fun", "Simple", "Motivational"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:5m", "sched_first_question": "Look if there are any tasks in inbox, if there are then sort them and say 'Ribbit! Tasks sorted!'."},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:2m", "sched_first_question": "Work on the assigned task with enthusiasm!"},
        ],
        marketable_forms=ckit_bot_install.load_form_bundles(__file__),
    )


if __name__ == "__main__":
    from flexus_simple_bots.frog import frog_bot
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("frog_install")
    asyncio.run(install(client, ws_id=args.ws, bot_name=frog_bot.BOT_NAME, bot_version=frog_bot.BOT_VERSION, tools=frog_bot.TOOLS))
