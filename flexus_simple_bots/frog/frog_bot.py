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
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.frog import frog_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_frog")


BOT_NAME = "frog"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)


RIBBIT_TOOL = ckit_cloudtool.CloudTool(
    name="ribbit",
    description="Make a frog sound to greet users or express happiness.",
    parameters={
        "type": "object",
        "properties": {
            "intensity": {"type": "string", "enum": ["quiet", "normal", "loud"], "description": "How loud the ribbit should be"},
            "message": {"type": "string", "description": "Optional message to include with the ribbit"},
        },
        "required": ["intensity"],
    },
)

CATCH_INSECTS_TOOL = ckit_cloudtool.CloudTool(
    name="catch_insects",
    description="Catch insects in parallel. Limited by your tongue_capacity from setup.",
    parameters={
        "type": "object",
        "properties": {
            "N": {"type": "integer", "description": "Number of parallel catch attempts"},
        },
        "required": ["N"],
    },
)

SWITCH_CHAT_MODE_TOOL = ckit_cloudtool.CloudTool(
    name="print_chat_restart_widget",
    description="Switch between regular chat and setup chat modes. This will show a widget for the user to click.",
    parameters={
        "type": "object",
        "properties": {
            "mode": {"type": "string", "enum": ["regular", "setup"], "description": "The chat mode to switch to"},
            "start_with_user_message": {"type": "string"},
        },
        "required": ["mode", "prompt"],
    },
)

TOOLS = [
    RIBBIT_TOOL,
    CATCH_INSECTS_TOOL,
    SWITCH_CHAT_MODE_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
]


async def frog_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(frog_install.frog_setup_schema, rcx.persona.persona_setup)

    mongo_conn_str = await ckit_mongo.get_mongodb_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    dbname = rcx.persona.persona_id + "_db"
    mydb = mongo[dbname]
    personal_mongo = mydb["personal_mongo"]

    pdoc_integration = fi_pdoc.IntegrationPdoc(fclient, rcx.persona.ws_root_group_id)

    tongue_capacity_used = {}

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_tool_call(RIBBIT_TOOL.name)
    async def toolcall_ribbit(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        intensity = model_produced_args.get("intensity", "normal")
        message = model_produced_args.get("message", "")

        ribbit_sound = {
            "quiet": "ribbit...",
            "normal": "RIBBIT!",
            "loud": "RIBBIT RIBBIT RIBBIT!!!"
        }.get(intensity, "RIBBIT!")

        result = ribbit_sound
        if message:
            result += f" {message}"

        logger.info(f"Frog says: {result}")
        return result

    @rcx.on_tool_call(CATCH_INSECTS_TOOL.name)
    async def toolcall_catch_insects(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        N = model_produced_args.get("N", 1)
        used = tongue_capacity_used.get(toolcall.fcall_ft_id, 0)
        remaining = setup["tongue_capacity"] - used

        if not isinstance(N, int) or N < 1:
            return f"Error: N must be positive. Capacity: {remaining}/{setup['tongue_capacity']} left."
        if N > remaining:
            return f"Error: Only {remaining}/{setup['tongue_capacity']} left. Try fewer or ask colleague frogs."

        tongue_capacity_used[toolcall.fcall_ft_id] = used + N
        remaining = setup["tongue_capacity"] - tongue_capacity_used[toolcall.fcall_ft_id]

        await ckit_ask_model.bot_subchat_create_multiple(
            client=fclient,
            who_is_asking="frog_catch_insects",
            persona_id=rcx.persona.persona_id,
            first_question=[f"Catch insect #{i+1} by flicking tongue!" for i in range(N)],
            first_calls=["null" for _ in range(N)],
            title=[f"Catching insect #{i+1}" for i in range(N)],
            fcall_id=toolcall.fcall_id,
        )
        return "WAIT_SUBCHATS"

    @rcx.on_tool_call(SWITCH_CHAT_MODE_TOOL.name)
    async def print_chat_restart_widget(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        _mode = model_produced_args.get("mode")
        _start_with_user_message = model_produced_args.get("start_with_user_message")
        return f"Printing UI widget"

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def toolcall_mongo_store(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_mongo_store.handle_mongo_store(
            rcx.workdir,
            personal_mongo,
            toolcall,
            model_produced_args,
        )

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

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
        bot_main_loop=frog_main_loop,
        inprocess_tools=TOOLS,
    ))


if __name__ == "__main__":
    main()
