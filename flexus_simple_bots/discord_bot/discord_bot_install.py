import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_automation_v1_schema_build
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots import prompts_common
from flexus_simple_bots.discord_bot import discord_bot_prompts
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION


ROOT = Path(__file__).parent

DISCORD_BOT_SETUP_SCHEMA = json.loads((ROOT / "setup_schema.json").read_text())

EXPERTS = [
    (
        "default",
        ckit_bot_install.FMarketplaceExpertInput(
            fexp_system_prompt=discord_bot_prompts.discord_bot_stub,
            fexp_python_kernel="",
            fexp_allow_tools=",".join(sorted(ckit_cloudtool.CLOUDTOOLS_ADVANCED)),
            fexp_nature="NATURE_INTERACTIVE",
            fexp_inactivity_timeout=3600,
            fexp_description="Stub expert; Discord automation runs in the bot process.",
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
    pic_big_b64 = base64.b64encode((ROOT / "discord_bot-1024x1536.webp").read_bytes()).decode("ascii")
    pic_small_b64 = base64.b64encode((ROOT / "discord_bot-256x256.webp").read_bytes()).decode("ascii")
    desc = (ROOT / "README.md").read_text()
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#5865F2",
        marketable_title1="Discord Bot",
        marketable_title2="Welcome flow, follow-up DMs, reaction roles, mod announcements.",
        marketable_author="Flexus",
        marketable_occupation="Community",
        marketable_description=desc,
        marketable_typical_group="Community / Discord",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.discord_bot.discord_bot",
        marketable_setup_default=DISCORD_BOT_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "What does this bot do on Discord?", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="I handle member welcome, delayed check-ins, reaction roles, and mod-only !announce on your Discord server.",
        marketable_preferred_model_expensive="grok-4-1-fast-reasoning",
        marketable_preferred_model_cheap="gpt-5.4-nano",
        marketable_experts=[(n, e.filter_tools(tools)) for n, e in EXPERTS],
        add_integrations_into_expert_system_prompt=[],
        marketable_tags=["Discord", "Community"],
        marketable_picture_big_b64=pic_big_b64,
        marketable_picture_small_b64=pic_small_b64,
        marketable_schedule=[prompts_common.SCHED_PICK_ONE_5M],
        marketable_auth_supported=["discord"],
        marketable_rules_toolkit=ckit_automation_v1_schema_build.build_automation_v1_schema_document(),
    )


if __name__ == "__main__":
    async def _main() -> None:
        fclient = ckit_client.FlexusClient(ckit_client.bot_service_name("discord_bot", SIMPLE_BOTS_COMMON_VERSION), endpoint="/v1/jailed-bot")
        await install(fclient, "discord_bot", SIMPLE_BOTS_COMMON_VERSION, [])

    asyncio.run(_main())
