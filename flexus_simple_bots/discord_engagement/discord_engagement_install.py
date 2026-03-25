import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots import prompts_common
from flexus_simple_bots.discord_engagement import discord_engagement_prompts
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION


ROOT = Path(__file__).parent

DISCORD_ENGAGEMENT_SETUP_SCHEMA = json.loads((ROOT / "setup_schema.json").read_text())

EXPERTS = [
    (
        "default",
        ckit_bot_install.FMarketplaceExpertInput(
            fexp_system_prompt=discord_engagement_prompts.discord_engagement_stub,
            fexp_python_kernel="",
            fexp_block_tools="",
            fexp_allow_tools="",
            fexp_inactivity_timeout=3600,
            fexp_description="Stub expert; engagement automation runs on Discord gateway.",
            fexp_builtin_skills="[]",
        ),
    ),
]


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
):
    pic_big_b64 = base64.b64encode((ROOT / "discord_engagement-1024x1536.webp").read_bytes()).decode("ascii")
    pic_small_b64 = base64.b64encode((ROOT / "discord_engagement-256x256.webp").read_bytes()).decode("ascii")
    desc = (ROOT / "README.md").read_text()
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#FEE75C",
        marketable_title1="Discord Engagement",
        marketable_title2="Interest pings, opt-in intros, inactive-member check-ins.",
        marketable_author="Flexus",
        marketable_occupation="Community",
        marketable_description=desc,
        marketable_typical_group="Community / Discord",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.discord_engagement.discord_engagement_bot",
        marketable_setup_default=DISCORD_ENGAGEMENT_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "How does !match work?", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="I highlight keywords with role pings, help members find each other via opt-in tags, and nudge quiet valued members.",
        marketable_preferred_model_default="gpt-5.4-nano",
        marketable_experts=[(n, e.filter_tools(tools)) for n, e in EXPERTS],
        add_integrations_into_expert_system_prompt=[],
        marketable_tags=["Discord", "Engagement", "Community"],
        marketable_picture_big_b64=pic_big_b64,
        marketable_picture_small_b64=pic_small_b64,
        marketable_schedule=[prompts_common.SCHED_PICK_ONE_5M],
        marketable_auth_supported=["discord_manual"],
    )


if __name__ == "__main__":
    async def _main() -> None:
        fclient = ckit_client.FlexusClient(ckit_client.bot_service_name("discord_engagement", SIMPLE_BOTS_COMMON_VERSION), endpoint="/v1/jailed-bot")
        await install(fclient, "discord_engagement", SIMPLE_BOTS_COMMON_VERSION, [])

    asyncio.run(_main())
