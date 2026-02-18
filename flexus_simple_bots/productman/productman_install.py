import asyncio
import base64
import json
from pathlib import Path
from typing import List

from flexus_client_kit import ckit_client, ckit_bot_install
from flexus_client_kit import ckit_cloudtool

from flexus_simple_bots import prompts_common
from flexus_simple_bots.productman import productman_bot, productman_prompts, productman_skill_survey


BOT_DESCRIPTION = """
## Productman — Discovery Agent

Head of Product Discovery. Understand what to sell and to whom, validated by market logic before spending money.

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


PRODUCTMAN_CRITICIZE_LARK = f"""
print("Criticize idea subchat is working")
if messages[-1]["role"] == "assistant":
    content = str(messages[-1]["content"])
    if "RATING-COMPLETED" in content:
        print("Rating completed, finishing subchat")
        subchat_result = "Rating complete, read the file using flexus_policy_document(op=activate, ...) to see the ratings."
    elif "RATING-ERROR" in content:
        print("Rating completed, apparently an error")
        subchat_result = content
    elif len(messages[-1].get("tool_calls", [])) == 0:
        post_cd_instruction = "Follow the system prompt, your answer need to end with RATING-COMPLETED or RATING-ERROR"
"""


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: List[ckit_cloudtool.CloudTool],
):
    pic_big = base64.b64encode(open(Path(__file__).with_name("productman-1024x1536.webp"), "rb").read()).decode("ascii")
    pic_small = base64.b64encode(open(Path(__file__).with_name("productman-256x256.webp"), "rb").read()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#4A90E2",
        marketable_title1="Productman",
        marketable_title2="Discovery Agent. Understand what to sell and to whom, validated by market logic.",
        marketable_author="Flexus",
        marketable_occupation="Product Manager",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Product / Research",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.productman.productman_bot",
        marketable_setup_default=productman_setup_schema,
        marketable_featured_actions=[
            {"feat_question": "A1: Challenge my product idea", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "A2: Research and prioritize hypotheses", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hi! I'm Productman, your Discovery Agent. I help you understand what to sell and to whom, validated by market logic before spending money.",
        marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
        marketable_daily_budget_default=200_000,
        marketable_default_inbox_default=20_000,
        marketable_experts=[
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=productman_prompts.productman_prompt_default,
                fexp_python_kernel="",
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=json.dumps([t.openai_style_tool() for t in productman_bot.TOOLS_DEFAULT]),
                fexp_description="Guides product discovery via Socratic dialogue, validating ideas and generating customer hypotheses.",
            )),
            ("criticize_idea", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=productman_prompts.productman_prompt_criticize_idea,
                fexp_python_kernel=PRODUCTMAN_CRITICIZE_LARK,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=json.dumps([t.openai_style_tool() for t in productman_bot.TOOLS_VERIFY_SUBCHAT]),
                fexp_description="Critically reviews idea documents, rating each answer as PASS, PASS-WITH-WARNINGS, or FAIL.",
            )),
            ("survey", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=productman_skill_survey.prompt,
                fexp_python_kernel=open(Path(__file__).parent / "lark/survey_skill_kernel.lark").read(),
                fexp_block_tools="",
                fexp_allow_tools="*bot_kanban",
                fexp_app_capture_tools=json.dumps([t.openai_style_tool() for t in productman_bot.TOOLS_SURVEY]),
                fexp_description="Executes survey campaigns to validate hypotheses with real customer feedback.",
            )),
        ],
        marketable_tags=["Product Management", "Hypothesis Testing"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            # NOTE: After first use, Productman will formulate modifications to company's strategy, this will require a weekly scheduled task or something
            prompts_common.SCHED_TASK_SORT_10M,
            prompts_common.SCHED_TODO_5M,
        ],
        marketable_forms=ckit_bot_install.load_form_bundles(__file__),
    )


if __name__ == "__main__":
    client = ckit_client.FlexusClient("productman_install")
    asyncio.run(install(client, bot_name=productman_bot.BOT_NAME, bot_version=productman_bot.BOT_VERSION, tools=productman_bot.TOOLS_ALL))
