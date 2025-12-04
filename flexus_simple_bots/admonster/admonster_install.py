import asyncio
import json
import base64
from pathlib import Path
from typing import List
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.admonster import admonster_prompts
admonster_setup_schema = [
    {
        "bs_name": "ad_account_id",
        "bs_type": "string_short",
        "bs_default": "",
        "bs_group": "LinkedIn",
        "bs_importance": 1,
        "bs_description": "LinkedIn Ads Account ID",
    },
    {
        "bs_name": "facebook_ad_account_id",
        "bs_type": "string_short",
        "bs_default": "",
        "bs_group": "Facebook",
        "bs_importance": 1,
        "bs_description": "Facebook Ads Account ID (act_...)",
    },
]
async def install(
    client: ckit_client.FlexusClient,
    ws_id: str,
    bot_name: str,
    bot_version: str,
    tools: List[ckit_cloudtool.CloudTool],
):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in tools])
    with open(Path(__file__).with_name("ad_monster-1024x1536.webp"), "rb") as f:
        big = base64.b64encode(f.read()).decode("ascii")
    with open(Path(__file__).with_name("ad_monster-256x256.webp"), "rb") as f:
        small = base64.b64encode(f.read()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#0077B5",
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
            {"feat_question": "Show me all my LinkedIn campaigns", "feat_run_as_setup": False, "feat_depends_on_setup": ["ad_account_id"]},
            {"feat_question": "Create a new brand awareness campaign", "feat_run_as_setup": False, "feat_depends_on_setup": ["ad_account_id"]},
            {"feat_question": "Analyze my campaign performance", "feat_run_as_setup": False, "feat_depends_on_setup": ["ad_account_id"]},
            {"feat_question": "Check my Facebook ads status", "feat_run_as_setup": False, "feat_depends_on_setup": ["facebook_ad_account_id"]},
        ],
        marketable_intro_message="Hi! I'm Ad Monster, your LinkedIn & Facebook advertising assistant. I can help you create campaigns, monitor performance, and optimize your ad spend. Let's start by checking your current campaigns!",
        marketable_preferred_model_default="grok-code-fast-1",
        marketable_daily_budget_default=50_000_000,
        marketable_default_inbox_default=5_000_000,
        marketable_experts=[
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=admonster_prompts.admonster_prompt,
                fexp_python_kernel="",
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
                fexp_inactivity_timeout=0,
            )),
            ("setup", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=admonster_prompts.admonster_setup,
                fexp_python_kernel="",
                fexp_block_tools="",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
                fexp_inactivity_timeout=0,
            )),
        ],
        marketable_tags=["advertising", "linkedin", "facebook", "marketing", "campaigns"],
        marketable_picture_big_b64=big,
        marketable_picture_small_b64=small,
        marketable_schedule=[]
    )
if __name__ == "__main__":
    from flexus_simple_bots.admonster import admonster_bot
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("admonster_install")
    asyncio.run(install(client, ws_id=args.ws, bot_name=admonster_bot.BOT_NAME, bot_version=admonster_bot.BOT_VERSION, tools=admonster_bot.TOOLS))
