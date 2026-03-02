import asyncio
import base64
from pathlib import Path

from flexus_client_kit import ckit_client, ckit_bot_install, ckit_cloudtool
from flexus_client_kit import ckit_skills
from flexus_simple_bots import prompts_common
from flexus_simple_bots.owl import owl_prompts


OWL3_ROOTDIR = Path(__file__).parent
OWL3_SKILLS = ckit_skills.static_skills_find(OWL3_ROOTDIR, shared_skills_allowlist="")

# Reuse owl's pictures — same bot, simplified internals
OWL_ASSETS = Path(__file__).parents[1] / "owl"

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=owl_prompts.DEFAULT_PROMPT,
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools="",
        fexp_description="Guides users through a 7-step growth strategy pipeline from hypothesis to experiment design.",
        fexp_builtin_skills=ckit_skills.read_name_description(OWL3_ROOTDIR, OWL3_SKILLS),
    )),
]


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
):
    pic_big_path = OWL_ASSETS / "owl_strategist-1024x1536.webp"
    pic_small_path = OWL_ASSETS / "owl_strategist-256x256.webp"
    pic_big = base64.b64encode(pic_big_path.read_bytes()).decode("ascii") if pic_big_path.exists() else None
    pic_small = base64.b64encode(pic_small_path.read_bytes()).decode("ascii") if pic_small_path.exists() else None

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#8B4513",
        marketable_title1="Owl3",
        marketable_title2="Growth Strategist — hypothesis to experiment design",
        marketable_author="Flexus",
        marketable_occupation="Growth Strategy",
        marketable_description="Turns validated hypotheses into experiment designs via a 7-step pipeline. Uses skills for schema guidance instead of strict tools.",
        marketable_typical_group="Marketing / Strategy",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.owl3.owl3_bot",
        marketable_setup_default=[],
        marketable_featured_actions=[
            {"feat_question": "Create strategy for my hypothesis", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="I'm Owl. I turn hypotheses into experiment designs. Let me check what's available...",
        marketable_preferred_model_default="grok-4-1-fast-reasoning",
        marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
        marketable_tags=["Marketing", "Strategy", "Growth"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_PICK_ONE_5M | {"sched_when": "EVERY:1m"},
        ],
        marketable_forms={},
    )


if __name__ == "__main__":
    from flexus_simple_bots.owl3 import owl3_bot
    client = ckit_client.FlexusClient("owl3_install")
    asyncio.run(install(client, bot_name=owl3_bot.BOT_NAME, bot_version=owl3_bot.BOT_VERSION, tools=owl3_bot.TOOLS))
