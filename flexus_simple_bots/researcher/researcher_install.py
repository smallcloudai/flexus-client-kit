import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_skills
from flexus_simple_bots import prompts_common
from flexus_simple_bots.researcher import researcher_prompts

RESEARCHER_ROOTDIR = Path(__file__).parent
RESEARCHER_SKILLS = ckit_skills.static_skills_find(RESEARCHER_ROOTDIR, shared_skills_allowlist="")
RESEARCHER_SETUP_SCHEMA = json.loads((RESEARCHER_ROOTDIR / "setup_schema.json").read_text())

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=researcher_prompts.DEFAULT_PROMPT,
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools="",
        fexp_description="GTM Research operator - market signals, customer discovery, idea validation, pain & alternatives, segment and pipeline qualification.",
        fexp_builtin_skills=ckit_skills.read_name_description(RESEARCHER_ROOTDIR, RESEARCHER_SKILLS),
    )),
]


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
) -> None:
    pic_big = base64.b64encode((RESEARCHER_ROOTDIR / "researcher-1024x1536.webp").read_bytes()).decode("ascii")
    pic_small = base64.b64encode((RESEARCHER_ROOTDIR / "researcher-256x256.webp").read_bytes()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#0F766E",
        marketable_title1="Researcher",
        marketable_title2="GTM Research - signals, discovery, validation",
        marketable_author="Flexus",
        marketable_occupation="GTM Research Operator",
        marketable_description=(
            "Consolidates market signal detection, customer discovery, idea validation, "
            "pain & alternatives analysis, segment qualification, and pipeline qualification "
            "into a single research operator. Load a skill to activate the relevant workflow."
        ),
        marketable_typical_group="GTM / Research",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.researcher.researcher_bot",
        marketable_setup_default=RESEARCHER_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "Detect market signals for one channel", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Design a JTBD discovery interview instrument", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Validate my product idea", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="I'm Researcher. Load a skill to activate a workflow: market-signal, customer-discovery, productman, pain-alternatives, segment-qualification, or pipeline-qualification.",
        marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
        marketable_daily_budget_default=100_000,
        marketable_default_inbox_default=10_000,
        marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
        marketable_tags=["GTM", "Research", "Discovery", "Signals"],
        marketable_schedule=[prompts_common.SCHED_PICK_ONE_5M],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_forms={},
        marketable_auth_supported=["linkedin", "google"],
        marketable_auth_scopes={
            "linkedin": ["r_profile_basicinfo", "email", "w_member_social"],
            "google": [],
        },
    )


if __name__ == "__main__":
    from flexus_simple_bots.researcher import researcher_bot
    client = ckit_client.FlexusClient("researcher_install")
    asyncio.run(install(client, bot_name=researcher_bot.BOT_NAME, bot_version=researcher_bot.BOT_VERSION, tools=researcher_bot.TOOLS))
