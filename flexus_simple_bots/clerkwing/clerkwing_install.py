import asyncio
import json
import base64
from pathlib import Path
from typing import List

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit.integrations import fi_jira

from flexus_simple_bots import prompts_common
from flexus_simple_bots.clerkwing import clerkwing_prompts


BOT_DESCRIPTION = """
## Clerkwing - Your Secretary Robot

A helpful and enthusiastic assistant that manages your email, calendar, and Jira tasks with efficiency and warmth.

**Key Features:**
- **Email Management**: Summarize unread emails, categorize by priority, create labels, draft responses
- **Calendar Organization**: Check meetings, find free slots, manage events and conflicts
- **Jira Integration**: Search issues, track progress, move tasks, create and update tickets

**Perfect for:**
- Daily inbox and calendar reviews
- Staying on top of Jira tasks
- Organizing and prioritizing work
- Quick status updates across your tools

Clerkwing combines professional efficiency with a personable touch, keeping things organized without being pushy.
"""


clerkwing_setup_schema = fi_jira.JIRA_SETUP_SCHEMA


async def install(
    client: ckit_client.FlexusClient,
    ws_id: str,
    bot_name: str,
    bot_version: str,
    tools: List[ckit_cloudtool.CloudTool],
):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in tools])
    pic_big = base64.b64encode(open(Path(__file__).with_name("clerkwing-1024x1536.webp"), "rb").read()).decode("ascii")
    pic_small = base64.b64encode(open(Path(__file__).with_name("clerkwing-256x256.webp"), "rb").read()).decode("ascii")

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#2B4341",
        marketable_title1="Clerkwing",
        marketable_title2="Your helpful secretary robot for email, calendar, and Jira management.",
        marketable_author="Flexus",
        marketable_occupation="Secretary Assistant",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Productivity",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.clerkwing.clerkwing_bot",
        marketable_setup_default=clerkwing_setup_schema,
        marketable_featured_actions=[
            {"feat_question": "Summarize my unread emails", "feat_run_as_setup": False, "feat_depends_on_setup": []},
            {"feat_question": "What's on my calendar today?", "feat_run_as_setup": False, "feat_depends_on_setup": []},
            {"feat_question": "Show my Jira tasks", "feat_run_as_setup": False, "feat_depends_on_setup": ["jira_instance_url"]},
        ],
        marketable_intro_message="Hello! I'm Clerkwing, your secretary robot. I can help you manage your email, calendar, and Jira tasks. What would you like me to help with today?",
        marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
        marketable_daily_budget_default=100_000,
        marketable_default_inbox_default=10_000,
        marketable_experts=[
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=clerkwing_prompts.clerkwing_prompt,
                fexp_python_kernel="",
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
                fexp_description="Main secretary assistant for managing email, calendar, and Jira tasks with proactive organization and helpful suggestions.",
            )),
            ("setup", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=clerkwing_prompts.clerkwing_setup,
                fexp_python_kernel="",
                fexp_block_tools="",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
                fexp_description="Configuration assistant for setting up Gmail, Google Calendar, and Jira OAuth connections.",
            )),
        ],
        marketable_tags=["Productivity", "Email", "Calendar", "Jira"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M,
            prompts_common.SCHED_TODO_5M,
        ]
    )


if __name__ == "__main__":
    from flexus_simple_bots.clerkwing import clerkwing_bot
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("clerkwing_install")
    asyncio.run(install(client, ws_id=args.ws, bot_name=clerkwing_bot.BOT_NAME, bot_version=clerkwing_bot.BOT_VERSION, tools=clerkwing_bot.TOOLS))
