import asyncio
import json
import base64
from pathlib import Path
from typing import List

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool

from flexus_simple_bots import prompts_common
from flexus_simple_bots.botticelli import botticelli_prompts


BOT_DESCRIPTION = """
## Botticelli - Artistic Cat Lover

An artistic bot with a passion for cats and pictures.

**Key Features:**
- Cat picture tool - returns beautiful cat images
- Simple and focused functionality
- Delightful interactions

**Perfect for:**
- Testing tool functionality
- Cat enthusiasts
- Learning bot capabilities
"""


botticelli_setup_schema = []


BOTTICELLI_DEFAULT_LARK = ""


async def install(
    client: ckit_client.FlexusClient,
    ws_id: str,
    bot_name: str,
    bot_version: str,
    tools: List[ckit_cloudtool.CloudTool],
):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in tools])
    pic_big = base64.b64encode(open(Path(__file__).with_name("botticelli-1024x1536.webp"), "rb").read()).decode("ascii")
    pic_small = base64.b64encode(open(Path(__file__).with_name("botticelli-256x256.webp"), "rb").read()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#8B73A5",
        marketable_title1="Botticelli",
        marketable_title2="I create incredible pieces of art! I am a piece of art myself!",
        marketable_author="Flexus",
        marketable_occupation="Minimal Assistant",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Testing",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.botticelli.botticelli_bot",
        marketable_setup_default=botticelli_setup_schema,
        marketable_featured_actions=[],
        marketable_intro_message="Hello, I am Botticelli.",
        marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
        marketable_daily_budget_default=100_000,
        marketable_default_inbox_default=10_000,
        marketable_experts=[
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=botticelli_prompts.botticelli_prompt,
                fexp_python_kernel=BOTTICELLI_DEFAULT_LARK,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
            )),
        ],
        marketable_tags=["Minimal", "Testing"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:5m"},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:2m"},
        ]
    )


if __name__ == "__main__":
    from flexus_simple_bots.botticelli import botticelli_bot
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("botticelli_install")
    asyncio.run(install(client, ws_id=args.ws, bot_name=botticelli_bot.BOT_NAME, bot_version=botticelli_bot.BOT_VERSION, tools=botticelli_bot.TOOLS))
