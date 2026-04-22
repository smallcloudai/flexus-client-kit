import asyncio
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.admonster import admonster_bot
from flexus_simple_bots.admonster import admonster_prompts
from flexus_simple_bots import prompts_common

TOOL_NAMESET = {t.name for t in admonster_bot.TOOLS}

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=admonster_prompts.admonster_prompt,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(sorted(set(ckit_cloudtool.CLOUDTOOLS_QUITE_A_LOT) | TOOL_NAMESET)),
        fexp_nature="NATURE_INTERACTIVE",
        fexp_inactivity_timeout=0,
        fexp_description="Automated advertising execution engine that launches campaigns from Owl Strategist tactics, monitors performance hourly, and optimizes based on stop/accelerate rules.",
    )),
    ("setup", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=admonster_prompts.admonster_setup,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(sorted(ckit_cloudtool.KANBAN_ADVANCED | ckit_cloudtool.CLOUDTOOLS_SCARY_TOOLS | TOOL_NAMESET)),
        fexp_nature="NATURE_INTERACTIVE",
        fexp_inactivity_timeout=0,
        fexp_description="Helps users configure Facebook OAuth connections and ad account settings, plus LinkedIn advertising credentials.",
    )),
]

ADMONSTER_DESC = """
**Job description**
AdMonster is your always-on performance marketing engine. He runs Meta campaigns end-to-end, launches A/B tests automatically, and checks results every hour so nothing underperforms for long. While your team sleeps, AdMonster is pausing losers, scaling winners, and logging what he learned. He treats every dollar as an experiment and every experiment as data.

**How AdMonster can help you:**
- Launches and manages Meta ad campaigns from brief to live
- Designs and runs A/B tests across creatives, copy, audiences, and placements
- Monitors campaign performance hourly and flags anomalies in real time
- Automatically pauses underperforming variants and reallocates budget to winners
- Tracks experiment results and maintains a structured log of what worked and why
- Surfaces statistically significant insights so your team makes decisions on evidence, not instinct
- Generates performance reports with clear next-step recommendations
"""


async def install(client: ckit_client.FlexusClient):
    r = await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        bot_dir=admonster_bot.ADMONSTER_ROOTDIR,
        marketable_accent_color="#f6c459",
        marketable_title1="Ad Monster",
        marketable_title2="Keeps track of your campaings, automates A/B tests, gives you new ideas.",
        marketable_author="Flexus",
        marketable_occupation="Advertising Campaign Manager",
        marketable_description=ADMONSTER_DESC,
        marketable_typical_group="Marketing",
        marketable_setup_default=admonster_bot.ADMONSTER_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "List available marketing experiments", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Launch experiment", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Check experiment status and metrics", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Show me all my Facebook campaigns", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Connect Facebook account", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hi! I'm Ad Monster, your automated advertising assistant. I execute marketing experiments from Owl Strategist, monitor campaigns hourly, and optimize based on stop/accelerate rules. I can launch experiments, check status, or manage individual campaigns. What would you like to do?",
        marketable_preferred_model_expensive="grok-4-1-fast-reasoning",
        marketable_preferred_model_cheap="gpt-5.4-nano",
        marketable_experts=[(name, exp.filter_tools(admonster_bot.TOOLS)) for name, exp in EXPERTS],
        marketable_tags=["advertising", "linkedin", "facebook", "marketing", "campaigns", "experiments", "automation"],
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M,
            prompts_common.SCHED_TODO_5M,
        ],
        marketable_forms=ckit_bot_install.load_form_bundles(__file__),
        marketable_auth_supported=["linkedin", "facebook"],
        marketable_auth_scopes={
            "linkedin": [
                "r_profile_basicinfo",
                "email",
                "w_member_social",
            ],
            "facebook": [
                "ads_management",
                "ads_read",
                "business_management",
                "pages_manage_ads",
            ],
        },
    )
    return r.marketable_version


if __name__ == "__main__":
    client = ckit_client.FlexusClient("admonster_install")
    asyncio.run(install(client))
