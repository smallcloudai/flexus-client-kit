import asyncio
import json
import logging
from dataclasses import asdict
from typing import Dict, Any

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit.integrations import fi_slack
from flexus_simple_bots.karen import karen_install

logger = logging.getLogger("bot_karen")


BOT_NAME = "karen"
BOT_VERSION = "0.1.16"
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)

ACCENT_COLOR = "#23CCCC"

TOOLS = [fi_slack.SLACK_TOOL]


async def karen_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(karen_install.karen_setup_default, rcx.persona.persona_setup)
    slack = fi_slack.IntegrationSlack(
        fclient,
        rcx,
        SLACK_BOT_TOKEN=setup["SLACK_BOT_TOKEN"],
        SLACK_APP_TOKEN=setup["SLACK_APP_TOKEN"],
        should_join=setup["slack_should_join"],
    )

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        # print("%s WOW A MESSAGE!!! msg.ftm_num=%d msg.ftm_content=%r" % (rcx.persona.persona_id, msg.ftm_num, str(msg.ftm_content)[:20].replace("\n", "\\n")))
        await slack.look_assistant_might_have_posted_something(msg)

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        # logger.info("updated thread %s %s captured=%s" % (rcx.persona.persona_id, th.ft_id, th.ft_app_searchable))
        pass

    @rcx.on_tool_call(fi_slack.SLACK_TOOL.name)
    async def toolcall_slack(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await slack.called_by_model(toolcall, model_produced_args)

    async def slack_activity_callback(a: fi_slack.ActivitySlack, already_posted_to_captured_thread: bool):
        logger.info(f"{rcx.persona.persona_id} 🔔 what_happened={a.what_happened} {a.channel_name} by @{a.message_author_name}: {a.message_text}")
        if not already_posted_to_captured_thread:
            channel_name_slash_thread = a.channel_name
            if a.thread_ts:
                channel_name_slash_thread += "/" + a.thread_ts
            title = "%s user=%r in %s\n%s" % (a.what_happened, a.message_author_name, channel_name_slash_thread, a.message_text)
            if a.file_contents:
                title += f"\n[{len(a.file_contents)} file(s) attached]"
            details = asdict(a)
            if a.file_contents:
                details['file_contents'] = f"{len(a.file_contents)} files attached"

            await ckit_kanban.bot_kanban_post_into_inbox(
                fclient,
                rcx.persona.persona_id,
                title=title,
                details_json=json.dumps(details),
            )

    slack.set_activity_callback(slack_activity_callback)
    await slack.join_channels()

    try:
        await slack.start_reactive()

        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)  # calls all your rcx.on_* inside and catches exceptions
            # happy_about_threads = ""
            # for t in rcx.latest_threads.values():
            #     happy_about_threads += "  thread %s has %d messages\n" % (t.thread_fields.ft_id, len(t.thread_messages))
            # print("%s WORK\n%s" % (rcx.persona.persona_id, happy_about_threads))

    finally:
        await slack.close()
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", type=str, required=True, help="Flexus group ID where the bot will run, take it from the address bar in the browser when you are looking on something inside a group.")
    args = parser.parse_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION_INT, args.group), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version=BOT_VERSION_INT,
        fgroup_id=args.group,
        bot_main_loop=karen_main_loop,
        inprocess_tools=TOOLS,
    ))


if __name__ == "__main__":
    main()
