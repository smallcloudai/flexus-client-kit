import asyncio
import logging
from typing import Dict, Any

from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_mongo
from flexus_client_kit.integrations import fi_mongo_store
from flexus_simple_bots.boss import boss_install
from flexus_simple_bots.boss.tools import boss_approval
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_boss")


BOT_NAME = "boss"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)

ACCENT_COLOR = "#8B4513"


TOOLS = [
    boss_approval.BOSS_APPROVE_TASK_TOOL,
    boss_approval.BOSS_REJECT_TASK_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
]


async def boss_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(boss_install.boss_setup_schema, rcx.persona.persona_setup)

    mongo_conn_str = await ckit_mongo.get_mongodb_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    dbname = rcx.persona.persona_id + "_db"
    mydb = mongo[dbname]
    personal_mongo = mydb["personal_mongo"]

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_tool_call(boss_approval.BOSS_APPROVE_TASK_TOOL.name)
    async def toolcall_approve_task(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await boss_approval.handle_approve_task(fclient, toolcall, model_produced_args)

    @rcx.on_tool_call(boss_approval.BOSS_REJECT_TASK_TOOL.name)
    async def toolcall_reject_task(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await boss_approval.handle_reject_task(fclient, toolcall, model_produced_args)

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def toolcall_mongo_store(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_mongo_store.handle_mongo_store(
            rcx.workdir,
            personal_mongo,
            toolcall,
            model_produced_args,
        )

    rcx.ready()

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    group = ckit_bot_exec.parse_bot_group_argument()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION_INT, group), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version=BOT_VERSION_INT,
        fgroup_id=group,
        bot_main_loop=boss_main_loop,
        inprocess_tools=TOOLS,
    ))


if __name__ == "__main__":
    main()
