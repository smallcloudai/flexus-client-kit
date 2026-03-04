import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_skills
from flexus_simple_bots import prompts_common
from flexus_simple_bots.executor import executor_prompts

EXECUTOR_ROOTDIR = Path(__file__).parent
EXECUTOR_SKILLS = [
    s for s in ckit_skills.static_skills_find(EXECUTOR_ROOTDIR, shared_skills_allowlist="")
    if s != "botticelli"
]
EXECUTOR_SETUP_SCHEMA = json.loads((EXECUTOR_ROOTDIR / "setup_schema.json").read_text())

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=executor_prompts.DEFAULT_PROMPT,
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools="",
        fexp_description="GTM Execution operator — ad campaigns, paid tests, pilot delivery, partner ecosystem, retention and churn analysis.",
        fexp_builtin_skills=ckit_skills.read_name_description(EXECUTOR_ROOTDIR, EXECUTOR_SKILLS),
    )),
]


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
) -> None:
    pic_big = base64.b64encode((EXECUTOR_ROOTDIR / "executor-1024x1536.webp").read_bytes()).decode("ascii")
    pic_small = base64.b64encode((EXECUTOR_ROOTDIR / "executor-256x256.webp").read_bytes()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#B45309",
        marketable_title1="Executor",
        marketable_title2="GTM Execution — ads, pilots, partners, retention",
        marketable_author="Flexus",
        marketable_occupation="GTM Execution Operator",
        marketable_description=(
            "Consolidates ad campaign execution, paid channel tests, "
            "pilot delivery, partner ecosystem operations, retention intelligence, and churn learning "
            "into a single execution operator. Load a skill to activate the relevant workflow."
        ),
        marketable_typical_group="GTM / Execution",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.executor.executor_bot",
        marketable_setup_default=EXECUTOR_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "Launch Meta ad campaign from Owl Strategist tactics", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Build a paid-channel execution plan", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Run a controlled paid-channel test", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Analyze cohort retention and revenue", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Classify churn root causes", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="I'm Executor. Load a skill to activate a workflow: admonster, creative-paid-channels, pilot-delivery, partner-ecosystem, retention-intelligence, or churn-learning.",
        marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
        marketable_daily_budget_default=100_000,
        marketable_default_inbox_default=10_000,
        marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
        marketable_tags=["GTM", "Execution", "Ads", "Creatives", "Pilots", "Retention"],
        marketable_schedule=[prompts_common.SCHED_PICK_ONE_5M],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_forms={},
        marketable_auth_supported=["linkedin", "facebook", "google"],
        marketable_auth_scopes={
            "linkedin": ["r_profile_basicinfo", "email", "w_member_social"],
            "facebook": ["ads_management", "ads_read", "business_management", "pages_manage_ads"],
            "google": [],
        },
    )


if __name__ == "__main__":
    from flexus_simple_bots.executor import executor_bot
    client = ckit_client.FlexusClient("executor_install")
    asyncio.run(install(client, bot_name=executor_bot.BOT_NAME, bot_version=executor_bot.BOT_VERSION, tools=executor_bot.TOOLS))
