import asyncio
import json
from pathlib import Path

from flexus_client_kit import ckit_automation_v1_schema_build
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots import prompts_common
from flexus_simple_bots.discord_bot import discord_bot_prompts
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION


# Bot package root: same folder as discord_bot.py, setup_schema.json, webp assets, README.
# Passed to marketplace_upsert_dev_bot as bot_dir so name/version/repo/run/pictures match other simple bots.
ROOT = Path(__file__).parent

DISCORD_BOT_SETUP_SCHEMA = json.loads((ROOT / "setup_schema.json").read_text())

EXPERTS = [
    (
        "default",
        ckit_bot_install.FMarketplaceExpertInput(
            fexp_system_prompt=discord_bot_prompts.discord_bot_stub,
            fexp_python_kernel="",
            fexp_allow_tools=",".join(sorted(ckit_cloudtool.CLOUDTOOLS_QUITE_A_LOT)),
            fexp_nature="NATURE_INTERACTIVE",
            fexp_inactivity_timeout=3600,
            fexp_description="Stub expert; Discord automation runs in the bot process.",
            fexp_builtin_skills="[]",
        ),
    ),
]


async def install(client: ckit_client.FlexusClient):
    """Upsert this dev bot in the marketplace; name/version/run/repo/images are derived inside marketplace_upsert_dev_bot from bot_dir."""
    # Import inside install so this module can load before discord_bot (discord_bot imports discord_bot_install at package load).
    from flexus_simple_bots.discord_bot import discord_bot as _discord_bot

    r = await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        bot_dir=ROOT,
        marketable_accent_color="#5865F2",
        marketable_title1="Discord Bot",
        marketable_title2="Welcome flow, follow-up DMs, reaction roles, mod announcements.",
        marketable_author="Flexus",
        marketable_occupation="Community",
        marketable_description=(ROOT / "README.md").read_text(),
        marketable_typical_group="Community / Discord",
        marketable_setup_default=DISCORD_BOT_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "What does this bot do on Discord?", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="I handle member welcome, delayed check-ins, reaction roles, and mod-only !announce on your Discord server.",
        marketable_preferred_model_expensive="grok-4-1-fast-reasoning",
        marketable_preferred_model_cheap="gpt-5.4-nano",
        marketable_experts=[(n, e.filter_tools(_discord_bot.TOOLS)) for n, e in EXPERTS],
        marketable_tags=["Discord", "Community"],
        marketable_schedule=[prompts_common.SCHED_PICK_ONE_5M],
        marketable_auth_supported=["discord"],
        marketable_rules_toolkit=ckit_automation_v1_schema_build.build_automation_v1_schema_document(),
    )
    return r.marketable_version


if __name__ == "__main__":
    async def _main() -> None:
        fclient = ckit_client.FlexusClient(ckit_client.bot_service_name("discord_bot", SIMPLE_BOTS_COMMON_VERSION), endpoint="/v1/jailed-bot")
        await install(fclient)

    asyncio.run(_main())
