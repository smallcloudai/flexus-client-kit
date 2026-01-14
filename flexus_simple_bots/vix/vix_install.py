import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool

from flexus_simple_bots import prompts_common
from flexus_simple_bots.vix import vix_bot, vix_prompts


BOT_DESCRIPTION = """
## Vix - AI Sales Agent

An elite AI sales agent trained in the C.L.O.S.E.R. Framework, designed for consultative selling that prioritizes understanding over pushing.

**Key Features:**
- **C.L.O.S.E.R. Framework**: Proven sales methodology (Clarify, Label, Overview, Sell, Explain/Overcome, Reinforce)
- **Transparent AI**: Always discloses AI nature, building trust through honesty
- **BANT Qualification**: Automatically qualifies leads (Budget, Authority, Need, Timeline)
- **Sentiment Detection**: Adapts approach based on prospect engagement, frustration, or skepticism
- **Smart Handoff**: Knows when to escalate to human agents
- **Policy-Driven**: Uses `/company` and `/sales-strategy` documents for company knowledge

**Perfect for:**
- Sales teams wanting to automate initial conversations
- Businesses that want consultative selling, not pushy tactics
- Companies that value transparency and customer understanding
- Teams needing 24/7 lead engagement and qualification

**Philosophy:**
The one who cares most about the customer wins the sale. Vix doesn't push—she understands and leads. Great sales feel like help, not pressure.

**Skills:**
- **Default**: Main sales conversations using C.L.O.S.E.R. Framework
- **Setup**: Configure your sales strategy and company information
"""


vix_setup_schema = [
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
]


async def install(
    client: ckit_client.FlexusClient,
    ws_id: str,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in tools])
    pic_big = base64.b64encode(open(Path(__file__).with_name("vix-1024x1536.webp"), "rb").read()).decode("ascii")
    pic_small = base64.b64encode(open(Path(__file__).with_name("vix-256x256.webp"), "rb").read()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#dedad0",
        marketable_title1="Vix",
        marketable_title2="Elite AI Sales Agent trained in consultative selling with the C.L.O.S.E.R. Framework.",
        marketable_author="Flexus",
        marketable_occupation="Sales Agent",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Sales",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.vix.vix_bot",
        marketable_setup_default=vix_setup_schema,
        marketable_featured_actions=[
            {"feat_question": "Help me qualify a lead", "feat_run_as_setup": False, "feat_depends_on_setup": []},
            {"feat_question": "Set up my sales strategy", "feat_run_as_setup": False, "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hi there! I'm Vix, an AI sales assistant. I'm here to help you find the right solution. Before we dive in, what's your name?",
        marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
        marketable_daily_budget_default=100_000,
        marketable_default_inbox_default=10_000,
        marketable_experts=[
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=vix_prompts.vix_prompt_default,
                fexp_python_kernel="",
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
            )),
            ("setup", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=vix_prompts.vix_prompt_setup,
                fexp_python_kernel="",
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
            )),
        ],
        marketable_tags=["Sales", "CLOSER", "AI Agent", "Lead Qualification"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:5m", "sched_first_question": "Sort inbox tasks: new leads to todo, irrelevant to irrelevant."},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:2m", "sched_first_question": "Work on the assigned lead/task using C.L.O.S.E.R. Framework."},
        ],
        marketable_forms={},
    )


if __name__ == "__main__":
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("vix_install")
    asyncio.run(install(client, ws_id=args.ws, bot_name=vix_bot.BOT_NAME, bot_version=vix_bot.BOT_VERSION, tools=vix_bot.TOOLS))
