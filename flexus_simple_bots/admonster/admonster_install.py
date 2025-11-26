"""
AdMonster Bot - Installation Script

WHAT: Registers the AdMonster bot in the Flexus marketplace.
WHY: Makes the bot discoverable, configurable, and installable by users.

USAGE:
    python -m flexus_simple_bots.admonster.admonster_install --ws WORKSPACE_ID

Creates/updates a marketplace entry with:
- Bot metadata (name, description, images, tags)
- Setup schema (configuration fields shown to user in UI)
- Experts (AI personas with different system prompts)
- Featured actions (quick-start buttons in UI)
"""

import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install

from flexus_simple_bots.admonster import admonster_bot, admonster_prompts


# Setup schema - defines configuration fields shown in bot's setup UI
# User fills these to configure their bot instance
admonster_setup_schema = [
    {
        "bs_name": "ad_account_id",      # Field identifier (used in code)
        "bs_type": "string_short",        # Input type: string_short, string_long, string_multiline, bool, int, float
        "bs_default": "",                 # Default value
        "bs_group": "LinkedIn",           # UI tab/group name
        "bs_importance": 1,               # Sort order within group
        "bs_description": "LinkedIn Ads Account ID",  # Help text
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


async def install(client: ckit_client.FlexusClient, ws_id: str):
    """
    Register or update AdMonster bot in the marketplace.
    
    Args:
        client: Authenticated Flexus client
        ws_id: Target workspace ID (bot becomes available in this workspace)
    """
    # Convert tool definitions to OpenAI-style format for the AI model
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in admonster_bot.TOOLS])
    
    # Load bot images (marketplace display)
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
        
        # Marketplace display text
        marketable_title1="Ad Monster",
        marketable_title2="Keeps track of your campaings, automates A/B tests, gives you new ideas.",
        marketable_author="Flexus",
        marketable_occupation="Advertising Campaign Manager",
        marketable_description="Manage LinkedIn advertising campaigns, create campaign groups, monitor analytics, and optimize ad performance.",
        marketable_typical_group="Marketing",  # Suggested group for organizing in UI
        
        # Links and execution
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit",
        marketable_run_this="python -m flexus_simple_bots.admonster.admonster_bot",
        
        # Configuration
        marketable_setup_default=admonster_setup_schema,
        
        # Featured actions - quick-start buttons shown in UI
        # feat_depends_on_setup: list of setup fields required for this action
        marketable_featured_actions=[
            {"feat_question": "Show me all my LinkedIn campaigns", "feat_run_as_setup": False, "feat_depends_on_setup": ["ad_account_id"]},
            {"feat_question": "Create a new brand awareness campaign", "feat_run_as_setup": False, "feat_depends_on_setup": ["ad_account_id"]},
            {"feat_question": "Analyze my campaign performance", "feat_run_as_setup": False, "feat_depends_on_setup": ["ad_account_id"]},
            {"feat_question": "Check my Facebook ads status", "feat_run_as_setup": False, "feat_depends_on_setup": ["facebook_ad_account_id"]},
        ],
        
        # First message bot sends when user starts a new chat
        marketable_intro_message="Hi! I'm Ad Monster, your LinkedIn & Facebook advertising assistant. I can help you create campaigns, monitor performance, and optimize your ad spend. Let's start by checking your current campaigns!",
        
        # AI model preferences
        marketable_preferred_model_default="grok-code-fast-1",
        
        # Budget limits (in tokens)
        marketable_daily_budget_default=50_000_000,
        marketable_default_inbox_default=5_000_000,
        
        # Experts - different AI personas for different contexts
        # "default" expert used for normal chat, "setup" expert used during configuration
        marketable_experts=[
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_name="admonster_default",
                fexp_system_prompt=admonster_prompts.admonster_prompt,
                fexp_python_kernel="",
                fexp_block_tools="*setup*",  # Block setup-related tools in normal mode
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
            )),
            ("setup", ckit_bot_install.FMarketplaceExpertInput(
                fexp_name="admonster_setup",
                fexp_system_prompt=admonster_prompts.admonster_setup,
                fexp_python_kernel="",
                fexp_block_tools="",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
            )),
        ],
        
        # Searchable tags for marketplace
        marketable_tags=["advertising", "linkedin", "facebook", "marketing", "campaigns"],
        
        # Bot images
        marketable_picture_big_b64=big,
        marketable_picture_small_b64=small,
        
        # Scheduled tasks (empty for now - bot runs on-demand only)
        marketable_schedule=[]
    )


if __name__ == "__main__":
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("admonster_install")
    asyncio.run(install(client, ws_id=args.ws))
