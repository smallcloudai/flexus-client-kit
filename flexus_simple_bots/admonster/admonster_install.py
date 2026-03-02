import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_skills
from flexus_simple_bots.admonster import admonster_prompts
from flexus_simple_bots import prompts_common


ADMONSTER_ROOTDIR = Path(__file__).parent
ADMONSTER_SKILLS = ckit_skills.static_skills_find(ADMONSTER_ROOTDIR, shared_skills_allowlist="")
ADMONSTER_SETUP_SCHEMA = json.loads((ADMONSTER_ROOTDIR / "setup_schema.json").read_text())

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=admonster_prompts.admonster_prompt,
        fexp_python_kernel="",
        fexp_block_tools="*setup*",
        fexp_allow_tools="",
        fexp_inactivity_timeout=0,
        fexp_description="Automated advertising execution engine that launches campaigns from Owl Strategist tactics, monitors performance hourly, and optimizes based on stop/accelerate rules.",
    )),
    ("setup", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=admonster_prompts.admonster_setup,
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools="",
        fexp_inactivity_timeout=0,
        fexp_description="Helps users configure Facebook OAuth connections and ad account settings, plus LinkedIn advertising credentials.",
    )),
]


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
):
    pic_big = base64.b64encode((ADMONSTER_ROOTDIR / "ad_monster-1024x1536.webp").read_bytes()).decode("ascii")
    pic_small = base64.b64encode((ADMONSTER_ROOTDIR / "ad_monster-256x256.webp").read_bytes()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#f6c459",
        marketable_title1="Ad Monster",
        marketable_title2="Keeps track of your campaings, automates A/B tests, gives you new ideas.",
        marketable_author="Flexus",
        marketable_occupation="Advertising Campaign Manager",
        marketable_description="Execute marketing experiments from Owl Strategist, manage Meta/LinkedIn campaigns, automate A/B tests with hourly monitoring.",
        marketable_typical_group="Marketing",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit",
        marketable_run_this="python -m flexus_simple_bots.admonster.admonster_bot",
        marketable_setup_default=ADMONSTER_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "List available marketing experiments", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Launch experiment", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Check experiment status and metrics", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Show me all my Facebook campaigns", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Connect Facebook account", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hi! I'm Ad Monster, your automated advertising assistant. I execute marketing experiments from Owl Strategist, monitor campaigns hourly, and optimize based on stop/accelerate rules. I can launch experiments, check status, or manage individual campaigns. What would you like to do?",
        marketable_preferred_model_default="grok-code-fast-1",
        marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
        marketable_tags=["advertising", "linkedin", "facebook", "marketing", "campaigns", "experiments", "automation"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
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


if __name__ == "__main__":
    from flexus_simple_bots.admonster import admonster_bot
    client = ckit_client.FlexusClient("admonster_install")
    asyncio.run(install(client, bot_name=admonster_bot.BOT_NAME, bot_version=admonster_bot.BOT_VERSION, tools=admonster_bot.TOOLS))
