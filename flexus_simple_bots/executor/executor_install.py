import asyncio
import base64

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_skills
from flexus_simple_bots import prompts_common
from flexus_simple_bots.executor import executor_bot
from flexus_simple_bots.executor import executor_prompts

TOOL_NAMESET = {t.name for t in executor_bot.TOOLS}

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=executor_prompts.DEFAULT_PROMPT,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(TOOL_NAMESET | ckit_cloudtool.CLOUDTOOLS_QUITE_A_LOT),
        fexp_nature="NATURE_INTERACTIVE",
        fexp_description="GTM Execution operator — pilot onboarding, pilot success tracking, and pilot conversion into signed revenue.",
        fexp_builtin_skills=ckit_skills.read_name_description(executor_bot.EXECUTOR_ROOTDIR, executor_bot.EXECUTOR_SKILLS),
    )),
]


async def install(client: ckit_client.FlexusClient):
    pic_big = base64.b64encode((executor_bot.EXECUTOR_ROOTDIR / "executor-1024x1536.webp").read_bytes()).decode("ascii")
    pic_small = base64.b64encode((executor_bot.EXECUTOR_ROOTDIR / "executor-256x256.webp").read_bytes()).decode("ascii")
    r = await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        bot_dir=executor_bot.EXECUTOR_ROOTDIR,
        marketable_accent_color="#B45309",
        marketable_title1="Executor",
        marketable_title2="GTM Execution — ads, pilots, partners, retention",
        marketable_author="Flexus",
        marketable_occupation="GTM Execution Operator",
        marketable_description=(
            "Consolidates pilot onboarding, pilot success tracking, and pilot conversion "
            "into a single execution operator. Load a skill to activate the relevant workflow."
        ),
        marketable_typical_group="GTM / Execution",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.executor.executor_bot",
        marketable_setup_default=executor_bot.EXECUTOR_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "Prepare a pilot kickoff plan with the right stakeholders and milestones", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Track pilot success criteria and midpoint risks", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Turn a successful pilot into a signed commercial agreement", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="I'm Executor. Load a skill to activate a workflow: pilot-onboarding, pilot-success-tracking, or pilot-conversion.",
        marketable_preferred_model_expensive="grok-4-1-fast-reasoning",
        marketable_preferred_model_cheap="gpt-5.4-nano",
        marketable_daily_budget_default=100_000,
        marketable_default_inbox_default=10_000,
        marketable_experts=[(name, exp.filter_tools(executor_bot.TOOLS)) for name, exp in EXPERTS],
        add_integrations_into_expert_system_prompt=executor_bot.EXECUTOR_INTEGRATIONS,
        marketable_tags=["GTM", "Execution", "Pilots", "Onboarding", "Conversion"],
        marketable_schedule=[prompts_common.SCHED_PICK_ONE_5M],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_forms={},
        marketable_auth_supported=["google"],
        marketable_auth_scopes={
            "google": [],
        },
    )
    return r.marketable_version


if __name__ == "__main__":
    client = ckit_client.FlexusClient("executor_install")
    asyncio.run(install(client))
