import asyncio
import base64
from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_skills
from flexus_simple_bots import prompts_common
from flexus_simple_bots.strategist import strategist_prompts

STRATEGIST_ROOTDIR = Path(__file__).parent
STRATEGIST_SKILLS = ckit_skills.static_skills_find(STRATEGIST_ROOTDIR, shared_skills_allowlist="")

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=strategist_prompts.DEFAULT_PROMPT,
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools="",
        fexp_description="GTM Strategy operator — calibration, diagnostics, experiment design, MVP validation, positioning, pricing, and GTM economics.",
        fexp_builtin_skills=ckit_skills.read_name_description(STRATEGIST_ROOTDIR, STRATEGIST_SKILLS),
    )),
]


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
) -> None:
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#8B4513",
        marketable_title1="Strategist",
        marketable_title2="GTM Strategy — from hypothesis to experiment to launch",
        marketable_author="Flexus",
        marketable_occupation="GTM Strategy Operator",
        marketable_description=(
            "Consolidates marketing strategy calibration, experiment design, MVP validation, "
            "positioning & offer architecture, pricing validation, and GTM economics & RTM "
            "into a single strategy operator. Load a skill to activate the relevant workflow."
        ),
        marketable_typical_group="GTM / Strategy",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.strategist.strategist_bot",
        marketable_setup_default=[],
        marketable_featured_actions=[
            {"feat_question": "Create strategy for my hypothesis", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Design an experiment for this risk", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Validate our pricing hypothesis", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="I'm Strategist. Load a skill to activate a workflow: filling-section01-calibration, experiment-design, mvp-validation, positioning-offer, pricing-validation, or gtm-economics-rtm.",
        marketable_preferred_model_default="grok-4-1-fast-reasoning",
        marketable_daily_budget_default=100_000,
        marketable_default_inbox_default=10_000,
        marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
        marketable_tags=["GTM", "Strategy", "Experiments", "Growth"],
        marketable_schedule=[prompts_common.SCHED_PICK_ONE_5M | {"sched_when": "EVERY:1m"}],
        marketable_forms={},
    )


if __name__ == "__main__":
    from flexus_simple_bots.strategist import strategist_bot
    client = ckit_client.FlexusClient("strategist_install")
    asyncio.run(install(client, bot_name=strategist_bot.BOT_NAME, bot_version=strategist_bot.BOT_VERSION, tools=strategist_bot.TOOLS))
