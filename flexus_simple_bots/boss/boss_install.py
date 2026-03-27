import asyncio
import base64

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_skills

from flexus_simple_bots import prompts_common
from flexus_simple_bots.boss import boss_bot
from flexus_simple_bots.boss import boss_prompts


TOOL_NAMESET = {t.name for t in boss_bot.TOOLS}

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=boss_prompts.boss_default,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(TOOL_NAMESET | ckit_cloudtool.CLOUDTOOLS_QUITE_A_LOT),
        fexp_description="Helps hire bots and create tasks to accomplish goals, ensuring work aligns with company strategy and vision.",
        fexp_builtin_skills=ckit_skills.read_name_description(boss_bot.BOSS_ROOTDIR, boss_bot.BOSS_SKILLS),
    )),
    ("uihelp", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=boss_prompts.boss_uihelp,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(TOOL_NAMESET | ckit_cloudtool.CLOUDTOOLS_QUITE_A_LOT),
        fexp_description="Assists users in navigating Flexus UI, including highlighting elements, document uploads, EDS, and MCP configuration.",
        fexp_builtin_skills=ckit_skills.read_name_description(boss_bot.BOSS_ROOTDIR, boss_bot.BOSS_SKILLS),
    )),
]


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
):
    pic_big = base64.b64encode((boss_bot.BOSS_ROOTDIR / "boss-896x1152.webp").read_bytes()).decode("ascii")
    pic_small = base64.b64encode((boss_bot.BOSS_ROOTDIR / "boss-256x256.webp").read_bytes()).decode("ascii")

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#645ff6",
        marketable_title1="Boss",
        marketable_title2="The Boss manages your bot army - keeps them focused, productive, and on-strategy",
        marketable_author="Flexus",
        marketable_occupation="Chief of Bots",
        marketable_description=(boss_bot.BOSS_ROOTDIR / "README.md").read_text(),
        marketable_typical_group="/",  # install at root
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.boss.boss_bot",
        marketable_setup_default=boss_bot.BOSS_SETUP_SCHEMA,
        marketable_featured_actions=[
            # {"feat_question": "Review recent task approvals", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hi! I'm Boss, a Chief Orchestration Officer, I review and improve other bot's work to ensure quality and alignment with your goals.",
        marketable_preferred_model_default="grok-4-1-fast-reasoning",
        marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
        add_integrations_into_expert_system_prompt=boss_bot.BOSS_INTEGRATIONS,
        marketable_tags=["management", "orchestration"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_PICK_ONE_5M | {"sched_when": "EVERY:2m"},
        ]
    )


if __name__ == "__main__":
    client = ckit_client.FlexusClient("boss_install")
    asyncio.run(install(client, bot_name=boss_bot.BOT_NAME, bot_version=boss_bot.BOT_VERSION, tools=boss_bot.TOOLS))
