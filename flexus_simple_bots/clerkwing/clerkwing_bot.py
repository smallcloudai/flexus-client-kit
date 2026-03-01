import asyncio
import logging

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_integrations_db
from flexus_simple_bots.clerkwing import clerkwing_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("clerk")

BOT_NAME = "clerkwing"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

CLERKWING_INTEGRATIONS = ckit_integrations_db.integrations_load(
    clerkwing_install.CLERKWING_ROOTDIR,
    allowlist=[
        "gmail",
        "google_calendar",
        "jira",
    ],
    builtin_skills=clerkwing_install.CLERKWING_SKILLS,
)

TOOLS = [*[t for rec in CLERKWING_INTEGRATIONS for t in rec.integr_tools]]


async def clerkwing_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(clerkwing_install.CLERKWING_SETUP_SCHEMA, rcx.persona.persona_setup)
    await ckit_integrations_db.integrations_init_all(CLERKWING_INTEGRATIONS, rcx, setup=setup)

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_updated_task
    async def updated_task_in_db(t: ckit_kanban.FPersonaKanbanTaskOutput):
        pass

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
