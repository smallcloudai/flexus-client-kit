import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install

from flexus_simple_bots.slonik import slonik_bot, slonik_prompts


slonik_setup_schema = [
    {
        "bs_name": "confirm_read",
        "bs_type": "bool",
        "bs_default": False,
        "bs_group": "Confirmations",
        "bs_order": 1,
        "bs_description": "Tell the robot what issues should escalate to a human engineer",
    },
]

async def install(client: ckit_client.FlexusClient, ws_id: str):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in slonik_bot.TOOLS])
    with open(Path(__file__).with_name("slonik-1024x1536.webp"), "rb") as f:
        big = base64.b64encode(f.read()).decode("ascii")
    with open(Path(__file__).with_name("slonik-256x256.webp"), "rb") as f:
        small = base64.b64encode(f.read()).decode("ascii")

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=slonik_bot.BOT_NAME,
        marketable_version=slonik_bot.BOT_VERSION,
        marketable_accent_color=slonik_bot.ACCENT_COLOR,
        marketable_title1="Slonik",
        marketable_title2="Database assistant for PostgreSQL operations.",
        marketable_author="Flexus",
        marketable_occupation="Database Assistant",
        marketable_description="Database assistant that helps with PostgreSQL queries and data analysis.",
        marketable_typical_group="Admin Tools",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit",
        marketable_run_this="python -m flexus_simple_bots.slonik.slonik_bot",
        marketable_setup_default=slonik_setup_schema,
        marketable_featured_actions=[
            {"feat_question": "Test whether database connection works", "feat_run_as_setup": False, "feat_depends_on_setup": []},
            {"feat_question": "Analyze database performance", "feat_run_as_setup": False, "feat_depends_on_setup": []},
            {"feat_question": "Help me write a SQL query", "feat_run_as_setup": False, "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hi! I'm Slonik, your PostgreSQL database assistant. I can help you run queries, analyze data, and optimize database performance.",
        marketable_preferred_model_default="grok-code-fast-1",
        marketable_daily_budget_default=50_000_000,
        marketable_default_inbox_default=5_000_000,
        marketable_experts=[
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=slonik_prompts.slonik_prompt,
                fexp_python_kernel="",
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
            )),
            ("setup", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=slonik_prompts.slonik_setup,
                fexp_python_kernel="",
                fexp_block_tools="",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
            )),
        ],
        marketable_tags=["database", "postgresql", "sql"],
        marketable_picture_big_b64=big,
        marketable_picture_small_b64=small,
        marketable_schedule=[]
    )


if __name__ == "__main__":
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("slonik_install")
    asyncio.run(install(client, ws_id=args.ws))
