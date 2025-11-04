import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install

from flexus_simple_bots import prompts_common
from flexus_simple_bots.productman import productman_bot, productman_prompts


BOT_DESCRIPTION = """
## Productman - Stage0 Product Validation Coach

A systematic product validation coach that guides you through a 3-node process to validate product ideas using the Stage0 methodology.

**Hypothesis Formula:**
"My client [WHO] wants [WHAT], but cannot [OBSTACLE], because [REASON]"

**Perfect for:**
- Startups validating product-market fit
- Product managers exploring new features
- Indie hackers testing ideas before building
- Customer development and lean startup practitioners

Productman structures product thinking, challenges assumptions, and creates a validated foundation before you write any code.
"""


productman_setup_schema = [
    {
        "bs_name": "additional_instructions",
        "bs_type": "string_multiline",
        "bs_default": "",
        "bs_group": "Customization",
        "bs_order": 1,
        "bs_importance": 0,
        "bs_description": "Additional instructions or preferences for how Productman should behave (e.g., language preference, industry focus, intensity of challenging)",
    },
]


async def install(
    client: ckit_client.FlexusClient,
    ws_id: str,
):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in productman_bot.TOOLS])
    pic_big = base64.b64encode(open(Path(__file__).with_name("productman-1024x1536.webp"), "rb").read()).decode("ascii")
    pic_small = base64.b64encode(open(Path(__file__).with_name("productman-256x256.webp"), "rb").read()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=productman_bot.BOT_NAME,
        marketable_version=productman_bot.BOT_VERSION,
        marketable_accent_color="#4A90E2",
        marketable_title1="Productman",
        marketable_title2="Your hypothesis-driven product manager. Formulate, test, and iterate on product ideas systematically.",
        marketable_author="Flexus",
        marketable_occupation="Product Manager",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Product / Research",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.productman.productman_bot",
        marketable_setup_default=productman_setup_schema,
        marketable_featured_actions=[
            {"feat_question": "Start Node 1: Challenge my product idea", "feat_run_as_setup": False, "feat_depends_on_setup": []},
            {"feat_question": "Start Node 2: Research and prioritize hypotheses", "feat_run_as_setup": False, "feat_depends_on_setup": []},
            {"feat_question": "Start Node 3: Design experiments", "feat_run_as_setup": False, "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hi! I'm Productman, your Stage0 Product Validation Coach. I guide you through (1) Problem Challenge, (2) Market Research, (3) Solution Design",
        marketable_preferred_model_default="grok-4-fast-non-reasoning",
        marketable_daily_budget_default=200_000,
        marketable_default_inbox_default=20_000,
        marketable_expert_default=ckit_bot_install.FMarketplaceExpertInput(
            fexp_name="productman_default",
            fexp_system_prompt=productman_prompts.productman_prompt,
            fexp_python_kernel="",
            fexp_block_tools="*setup*",
            fexp_allow_tools="",
            fexp_app_capture_tools=bot_internal_tools,
        ),
        marketable_expert_setup=ckit_bot_install.FMarketplaceExpertInput(
            fexp_name="productman_setup",
            fexp_system_prompt=productman_prompts.productman_prompt,
            fexp_python_kernel="",
            fexp_block_tools="",
            fexp_allow_tools="",
            fexp_app_capture_tools=bot_internal_tools,
        ),
        marketable_tags=["Product Management", "Hypothesis Testing"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            # NOTE: After first use, Productman will formulate modifications to company's strategy, this will require a weekly scheduled task or something
            prompts_common.SCHED_TASK_SORT_10M,
            prompts_common.SCHED_TODO_5M,
        ]
    )


if __name__ == "__main__":
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("productman_install")
    asyncio.run(install(client, ws_id=args.ws))
