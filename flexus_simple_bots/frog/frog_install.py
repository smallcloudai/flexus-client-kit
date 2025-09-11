import asyncio
import json
import base64
import argparse
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install

from flexus_simple_bots.frog import frog_bot, frog_prompts


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
- Simple task tracking
- Morale boosting

Frog is designed to be lightweight and easy to understand - ideal for learning how Flexus bots work or just bringing some joy to your workspace!
"""


frog_setup_default = [
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
]


FROG_BUDGET_WARNING = f"""
warning_text = "💿 Token budget is running low. Wrap up your current work, summarize the current chat thread, include what the original user's request was and the current status, and what to do next. Then call kanban_restart() with this summary to refresh context"

if coins > budget * 0.5 and not messages[-1]["tool_calls"]:
    for i, msg in enumerate(messages):
        warning_already_sent = False
        if msg["role"] == "kernel" and msg.get("content") and warning_text in str(msg["content"]):
            warning_already_sent = True
            break
    if not warning_already_sent:
        post_content = warning_text
"""


async def install(
    client: ckit_client.FlexusClient,
    ws_id: str,
):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in frog_bot.TOOLS])
    with open(Path(__file__).with_name("frog-1024x1536.webp"), "rb") as f:
        big = base64.b64encode(f.read()).decode("ascii")
    with open(Path(__file__).with_name("frog-256x256.webp"), "rb") as f:
        small = base64.b64encode(f.read()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=frog_bot.BOT_NAME,
        marketable_version=frog_bot.BOT_VERSION,
        marketable_title1="Frog",
        marketable_title2="A cheerful frog bot that brings joy and positivity to your workspace.",
        marketable_author="Flexus",
        marketable_occupation="Motivational Assistant",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Fun / Testing",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.frog.frog_bot",
        marketable_setup_default=frog_setup_default,
        marketable_preferred_model_default="grok-code-fast-1",
        marketable_daily_budget_default=100_000,
        marketable_default_inbox_default=10_000,
        marketable_expert_default=ckit_bot_install.FMarketplaceExpertInput(
            fexp_name="frog_default",
            fexp_system_prompt=frog_prompts.short_prompt,
            fexp_python_kernel=FROG_BUDGET_WARNING,
            fexp_block_tools="*setup*",
            fexp_allow_tools="",
            fexp_app_capture_tools=bot_internal_tools,
        ),
        marketable_expert_setup=ckit_bot_install.FMarketplaceExpertInput(
            fexp_name="frog_setup",
            fexp_system_prompt=frog_prompts.frog_setup,
            fexp_python_kernel=FROG_BUDGET_WARNING,
            fexp_block_tools="",
            fexp_allow_tools="",
            fexp_app_capture_tools=bot_internal_tools,
        ),
        marketable_tags=["fun", "simple", "motivational"],
        marketable_picture_big_b64=big,
        marketable_picture_small_b64=small,
        marketable_schedule=[
            {
                "sched_type": "SCHED_TASK_SORT",
                "sched_when": "EVERY:5m",
                "sched_first_question": "Look if there are any tasks in inbox, if there are then sort them and say 'Ribbit! Tasks sorted!'.",
            },
            {
                "sched_type": "SCHED_TODO",
                "sched_when": "EVERY:2m",
                "sched_first_question": "Work on the assigned task with enthusiasm!",
            },
        ]
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseurl", default="", help="Base URL for the Flexus API")
    parser.add_argument("--apikey", default="sk_alice_123456", help="API key for authentication")
    parser.add_argument("--ws", default="solarsystem", help="Workspace ID")
    args = parser.parse_args()
    client = ckit_client.FlexusClient("frog_install", base_url=args.baseurl, api_key=args.apikey)
    asyncio.run(install(client, ws_id=args.ws))