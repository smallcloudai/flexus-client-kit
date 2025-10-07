import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install

from flexus_simple_bots.admonster import admonster_bot, admonster_prompts


admonster_setup_schema = [
    {
        "bs_name": "LINKEDIN_ACCESS_TOKEN",
        "bs_type": "string_long",
        "bs_default": "",
        "bs_group": "LinkedIn",
        "bs_order": 1,
        "bs_importance": 0,
        "bs_description": "LinkedIn API Access Token (obtain via OAuth flow)",
    },
    {
        "bs_name": "LINKEDIN_AD_ACCOUNT_ID",
        "bs_type": "string_long",
        "bs_default": "513489554",
        "bs_group": "LinkedIn",
        "bs_order": 2,
        "bs_importance": 0,
        "bs_description": "LinkedIn Ads Account ID",
    },
]

async def install(client: ckit_client.FlexusClient, ws_id: str):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in admonster_bot.TOOLS])
    with open(Path(__file__).with_name("ad_monster-1024x1536.webp"), "rb") as f:
        big = base64.b64encode(f.read()).decode("ascii")
    with open(Path(__file__).with_name("ad_monster-256x256.webp"), "rb") as f:
        small = base64.b64encode(f.read()).decode("ascii")

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=admonster_bot.BOT_NAME,
        marketable_version=admonster_bot.BOT_VERSION,
        marketable_accent_color=admonster_bot.ACCENT_COLOR,
        marketable_title1="Ad Monster",
        marketable_title2="Keeps track of your campaings, automates A/B tests, gives you new ideas.",
        marketable_author="Flexus",
        marketable_occupation="Advertising Campaign Manager",
        marketable_description="Manage LinkedIn advertising campaigns, create campaign groups, monitor analytics, and optimize ad performance.",
        marketable_typical_group="Marketing",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit",
        marketable_run_this="python -m flexus_simple_bots.admonster.admonster_bot",
        marketable_setup_default=admonster_setup_schema,
        marketable_featured_actions=[
            {"feat_question": "Show me all my LinkedIn campaigns", "feat_run_as_setup": False, "feat_depends_on_setup": ["LINKEDIN_ACCESS_TOKEN"]},
            {"feat_question": "Create a new brand awareness campaign", "feat_run_as_setup": False, "feat_depends_on_setup": ["LINKEDIN_ACCESS_TOKEN"]},
            {"feat_question": "Analyze my campaign performance", "feat_run_as_setup": False, "feat_depends_on_setup": ["LINKEDIN_ACCESS_TOKEN"]},
        ],
        marketable_intro_message="Hi! I'm Ad Monster, your LinkedIn advertising assistant. I can help you create campaigns, monitor performance, and optimize your ad spend. Let's start by checking your current campaigns with linkedin(op='status')!",
        marketable_preferred_model_default="grok-code-fast-1",
        marketable_daily_budget_default=50_000_000,
        marketable_default_inbox_default=5_000_000,
        marketable_expert_default=ckit_bot_install.FMarketplaceExpertInput(
            fexp_name="admonster_default",
            fexp_system_prompt=admonster_prompts.admonster_prompt,
            fexp_python_kernel="",
            fexp_block_tools="*setup*",
            fexp_allow_tools="",
            fexp_app_capture_tools=bot_internal_tools,
        ),
        marketable_expert_setup=ckit_bot_install.FMarketplaceExpertInput(
            fexp_name="admonster_setup",
            fexp_system_prompt=admonster_prompts.admonster_setup,
            fexp_python_kernel="",
            fexp_block_tools="",
            fexp_allow_tools="",
            fexp_app_capture_tools=bot_internal_tools,
        ),
        marketable_tags=["advertising", "linkedin", "marketing", "campaigns"],
        marketable_picture_big_b64=big,
        marketable_picture_small_b64=small,
        marketable_schedule=[]
    )


if __name__ == "__main__":
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("admonster_install")
    asyncio.run(install(client, ws_id=args.ws))
