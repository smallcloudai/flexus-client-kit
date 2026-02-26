import asyncio
import logging
from typing import Dict, Any

from flexus_client_kit.core import ckit_client
from flexus_client_kit.core import ckit_cloudtool
from flexus_client_kit.core import ckit_bot_exec
from flexus_client_kit.core import ckit_shutdown
from flexus_client_kit.core import ckit_ask_model
from flexus_client_kit.core import ckit_kanban
from flexus_client_kit.integrations.providers.request_response import fi_gmail
from flexus_client_kit.integrations.providers.request_response import fi_google_calendar
from flexus_client_kit.integrations.providers.request_response import fi_jira
from flexus_simple_bots.clerkwing import clerkwing_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("clerk")

BOT_NAME = "clerkwing"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

TOOLS = [
    fi_gmail.GMAIL_TOOL,
    fi_google_calendar.GOOGLE_CALENDAR_TOOL,
    fi_jira.JIRA_TOOL,
]


async def clerkwing_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(clerkwing_install.clerkwing_setup_schema, rcx.persona.persona_setup)

    gmail_integration = fi_gmail.IntegrationGmail(fclient, rcx)
    calendar_integration = fi_google_calendar.IntegrationGoogleCalendar(fclient, rcx)
    jira_integration = fi_jira.IntegrationJira(
        fclient,
        rcx,
        jira_instance_url=setup["jira_instance_url"],
    )

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_updated_task
    async def updated_task_in_db(t: ckit_kanban.FPersonaKanbanTaskOutput):
        pass

    @rcx.on_tool_call(fi_gmail.GMAIL_TOOL.name)
    async def toolcall_gmail(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await gmail_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_google_calendar.GOOGLE_CALENDAR_TOOL.name)
    async def toolcall_calendar(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await calendar_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_jira.JIRA_TOOL.name)
    async def toolcall_jira(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await jira_integration.called_by_model(toolcall, model_produced_args)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=clerkwing_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=clerkwing_install.install,
    ))


if __name__ == "__main__":
    main()
