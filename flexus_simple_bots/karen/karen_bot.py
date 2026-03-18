import asyncio
import logging
from typing import Dict, Any

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit.integrations import fi_discord2
from flexus_client_kit.integrations import fi_repo_reader
from flexus_simple_bots.karen import karen_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_karen")


BOT_NAME = "karen"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

TOOLS = [
    fi_discord2.DISCORD_TOOL,
    fi_repo_reader.REPO_READER_TOOL,
    *[t for rec in karen_install.KAREN_INTEGRATIONS for t in rec.integr_tools],
]

async def karen_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(karen_install.KAREN_SETUP_SCHEMA, rcx.persona.persona_setup)
    integrations = await ckit_integrations_db.main_loop_integrations_init(karen_install.KAREN_INTEGRATIONS, rcx, setup)
    _slack: fi_slack.IntegrationSlack = integrations["slack"]

    # SAFETY
    # What we are trying to prevent: an outside user via slack/telegram/etc having access to any tools that leak information
    # about the company, or do any actions like sending A2A to Boss, that would be really silly.
    # How: expert 'very_limited' only has allowlist of tools, all messengers informed about the destination expert that they
    # are allowed to post the outside messages to.
    for me in rcx.messengers:
        me.accept_outside_messages_only_to_expert("very_limited")

    discord = fi_discord2.IntegrationDiscord(
        fclient,
        rcx,
        watch_channels=setup["discord_watch_channels"],
    )

    @rcx.on_tool_call(fi_discord2.DISCORD_TOOL.name)
    async def toolcall_discord(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await discord.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_repo_reader.REPO_READER_TOOL.name)
    async def toolcall_repo_reader(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_repo_reader.handle_repo_reader(rcx, model_produced_args)

    async def discord_activity_callback(a: fi_discord2.ActivityDiscord, already_posted_to_captured_thread: bool):
        import json
        from dataclasses import asdict
        from flexus_client_kit import ckit_kanban
        logger.info(f"{rcx.persona.persona_id} 🔔 Discord message in {a.channel_name} by @{a.message_author_name}: {a.message_text}")
        if already_posted_to_captured_thread:
            return
        channel_name_slash_thread = a.channel_name
        if a.thread_id:
            channel_name_slash_thread += "/" + a.thread_id
        title = "Discord user=%r in %s\n%s" % (a.message_author_name, channel_name_slash_thread, a.message_text)
        if a.attachments:
            title += f"\n[{len(a.attachments)} file(s) attached]"
        details = asdict(a)
        if a.attachments:
            details['attachments'] = f"{len(a.attachments)} files attached"

        logger.info("%s posting to kanban: title=%r details=%r", rcx.persona.persona_id, title, details)
        await ckit_kanban.bot_kanban_post_into_inbox(
            fclient,
            rcx.persona.persona_id,
            title=title,
            details_json=json.dumps(details),
            provenance_message="karen_discord_activity"
        )

    discord.set_activity_callback(discord_activity_callback)
    await discord.join_channels()

    try:
        await discord.start_reactive()

        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        await discord.close()
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=karen_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=karen_install.install,
    ))


if __name__ == "__main__":
    main()
