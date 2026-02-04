import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit.integrations import fi_crm_automations

from flexus_simple_bots import prompts_common
from flexus_simple_bots.vix import vix_bot, vix_prompts
from flexus_client_kit.integrations import fi_telegram


BOT_DESCRIPTION = """
## Vix - Sales & Marketing Agent

Integrated sales and marketing agent with CRM management, lead nurturing, and consultative selling.

**Marketing (Default):**
- CRM management, contact import from CSV or landing pages
- Automatic welcome emails to new contacts
- Gmail integration for outreach
- CRM automations (triggers and actions)
- Company and product setup

**Sales:**
- C.L.O.S.E.R. Framework for consultative selling
- BANT lead qualification
- Sentiment detection and adaptive approach
- Smart handoff to human agents

**Nurturing:**
- Lightweight automated tasks
- Send emails using templates
- Follow-ups based on CRM activities

**Skills:**
- **Default**: Marketing, CRM, automations, setup
- **Sales**: Consultative selling with C.L.O.S.E.R. Framework
- **Nurturing**: Automated templated emails and follow-ups (fast model)
"""


vix_setup_schema = fi_crm_automations.CRM_AUTOMATIONS_SETUP_SCHEMA + [
    {
        "bs_name": "faq_url",
        "bs_type": "string_long",
        "bs_default": "",
        "bs_group": "Company Info",
        "bs_order": 1,
        "bs_importance": 0,
        "bs_description": "Public URL to your FAQ page (optional, for reference during sales conversations)",
    },
    {
        "bs_name": "enable_auto_qualify",
        "bs_type": "bool",
        "bs_default": True,
        "bs_group": "Sales Behavior",
        "bs_order": 1,
        "bs_importance": 0,
        "bs_description": "Automatically qualify leads using BANT (Budget, Authority, Need, Timeline)",
    },
    {
        "bs_name": "handoff_threshold",
        "bs_type": "string_short",
        "bs_default": "medium",
        "bs_group": "Sales Behavior",
        "bs_order": 2,
        "bs_importance": 0,
        "bs_description": "When to offer human handoff: low (rarely), medium (balanced), high (proactive)",
    },
] + fi_telegram.TELEGRAM_SETUP_SCHEMA


async def install(
    client: ckit_client.FlexusClient,
    ws_id: str,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in tools])
    nurturing_tools = json.dumps([t.openai_style_tool() for t in tools if t.name not in ("crm_automation",)])
    pic_big = base64.b64encode(open(Path(__file__).with_name("vix-1024x1536.webp"), "rb").read()).decode("ascii")
    pic_small = base64.b64encode(open(Path(__file__).with_name("vix-256x256.webp"), "rb").read()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#dedad0",
        marketable_title1="Vix",
        marketable_title2="Sales & Marketing Agent - CRM, automations, and consultative selling with C.L.O.S.E.R. Framework.",
        marketable_author="Flexus",
        marketable_occupation="Sales & Marketing",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Sales",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.vix.vix_bot",
        marketable_setup_default=vix_setup_schema,
        marketable_featured_actions=[
            {"feat_question": "Help me set up my company and sales pipeline", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Help me send contacts from my landing page to Flexus", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Help me set up welcome emails to new contacts", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hi! I'm Vix, your sales and marketing assistant. I can help with CRM management, email automations, contact imports, and sales conversations. What would you like to work on?",
        marketable_preferred_model_default="claude-opus-4-5-20251101",
        marketable_daily_budget_default=3_000_000,
        marketable_default_inbox_default=300_000,
        marketable_experts=[
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=vix_prompts.vix_prompt_marketing,
                fexp_python_kernel="",
                fexp_block_tools="",
                fexp_allow_tools="",
                fexp_inactivity_timeout=3600,
                fexp_app_capture_tools=bot_internal_tools,
                fexp_description="Marketing assistant for CRM management, contact import, automated outreach, and company/product setup.",
            )),
            ("sales", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=vix_prompts.vix_prompt_sales,
                fexp_python_kernel="",
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_inactivity_timeout=3600,
                fexp_app_capture_tools=bot_internal_tools,
                fexp_description="Conducts sales conversations using C.L.O.S.E.R. Framework, qualifies leads with BANT, and handles objections with consultative approach.",
            )),
            ("nurturing", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=vix_prompts.vix_prompt_nurturing,
                fexp_python_kernel="",
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_inactivity_timeout=600,
                fexp_app_capture_tools=nurturing_tools,
                fexp_description="Lightweight expert for automated tasks: sending templated emails, follow-ups, and simple CRM operations.",
                fexp_preferred_model_default="grok-4-1-fast-non-reasoning",
            )),
        ],
        marketable_tags=["Sales", "Marketing", "CRM", "Email", "Automation"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:1m", "sched_fexp_name": "nurturing"},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:1m"},
        ],
        marketable_forms={},
        marketable_required_policydocs=["/company/summary", "/company/sales-strategy"],
    )


if __name__ == "__main__":
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("vix_install")
    asyncio.run(install(client, ws_id=args.ws, bot_name=vix_bot.BOT_NAME, bot_version=vix_bot.BOT_VERSION, tools=vix_bot.TOOLS))
