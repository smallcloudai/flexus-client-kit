import asyncio
from flexus_client_kit import ckit_client, ckit_bot_install, ckit_cloudtool
from flexus_simple_bots import prompts_common
from flexus_simple_bots.productman import productman_bot
from flexus_simple_bots.productman import productman_prompts, productman_skill_survey


TOOL_NAMESET = {t.name for t in productman_bot.TOOLS_ALL}

BOT_DESCRIPTION = """
**Job description**
Productman is your Head of Product Discovery. Before you write a line of code or spend a dollar on marketing, he makes sure you actually understand what you're building, who it's for, and whether anyone will pay for it. He structures product thinking around one core formula: "My client [WHO] wants [WHAT], but cannot [OBSTACLE], because [REASON]" — and challenges every assumption until the logic holds. Discovery first, building second.

**How Productman can help you:**
- Guides you through structured product discovery to define who your customer is and what they actually need
- Applies the hypothesis formula to sharpen your thinking: WHO, WHAT, OBSTACLE, REASON
- Challenges assumptions before they become expensive mistakes
- Validates product-market fit with market logic — not gut feel
- Helps founders and indie hackers test ideas before committing to a build
- Supports customer development interviews and lean startup methodology
- Creates a validated foundation that product, engineering, and marketing can build from
"""


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

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=productman_prompts.productman_prompt_default,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(TOOL_NAMESET | ckit_cloudtool.CLOUDTOOLS_QUITE_A_LOT),
        fexp_nature="NATURE_INTERACTIVE",
        fexp_description="Guides product discovery via Socratic dialogue, validating ideas and generating customer hypotheses.",
    )),
    ("criticize_idea", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=productman_prompts.productman_prompt_criticize_idea,
        fexp_python_kernel=PRODUCTMAN_CRITICIZE_LARK,
        fexp_allow_tools=",".join(ckit_cloudtool.KANBAN_SAFE),
        fexp_nature="NATURE_NO_TASK",
        fexp_description="Critically reviews idea documents, rating each answer as PASS, PASS-WITH-WARNINGS, or FAIL.",
    )),
    ("survey", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=productman_skill_survey.prompt,
        fexp_python_kernel=(productman_bot.PRODUCTMAN_ROOTDIR / "lark/survey_skill_kernel.lark").read_text(),
        fexp_allow_tools=",".join(ckit_cloudtool.KANBAN_SAFE),
        fexp_nature="NATURE_AUTONOMOUS",
        fexp_inactivity_timeout=600,
        fexp_description="Executes survey campaigns to validate hypotheses with real customer feedback.",
    )),
]


async def install(client: ckit_client.FlexusClient):
    r = await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        bot_dir=productman_bot.PRODUCTMAN_ROOTDIR,
        marketable_accent_color="#49cdc2",
        marketable_title1="Productman",
        marketable_title2="Discovery Agent. Understand what to sell and to whom, validated by market logic.",
        marketable_author="Flexus",
        marketable_occupation="Product Manager",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Product / Research",
        marketable_setup_default=productman_bot.PRODUCTMAN_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "A1: Challenge my product idea", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "A2: Research and prioritize hypotheses", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hi! I'm Productman, your Discovery Agent. I help you understand what to sell and to whom, validated by market logic before spending money.",
        marketable_preferred_model_expensive="grok-4-1-fast-reasoning",
        marketable_preferred_model_cheap="gpt-5.4-nano",
        marketable_experts=[(name, exp.filter_tools(productman_bot.TOOLS_ALL)) for name, exp in EXPERTS],
        marketable_tags=["Product Management", "Hypothesis Testing"],
        marketable_schedule=[
            # NOTE: After first use, Productman will formulate modifications to company's strategy, this will require a weekly scheduled task or something
            prompts_common.SCHED_TASK_SORT_10M,
            prompts_common.SCHED_TODO_5M,
        ],
        marketable_forms=ckit_bot_install.load_form_bundles(__file__),
    )
    return r.marketable_version


if __name__ == "__main__":
    client = ckit_client.FlexusClient("productman_install")
    asyncio.run(install(client))
