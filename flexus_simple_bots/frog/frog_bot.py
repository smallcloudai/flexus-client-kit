import asyncio
import logging
import json
import time
from typing import Dict, Any, Optional

from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_mongo
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_external_auth
from flexus_client_kit import erp_schema
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.frog import frog_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_frog")

BOT_NAME = "frog"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION


RIBBIT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="ribbit",
    description="Make a frog sound to greet users or express happiness.",
    parameters={
        "type": "object",
        "properties": {
            "intensity": {"type": "string", "enum": ["quiet", "normal", "loud"], "description": "How loud the ribbit should be"},
            "message": {"type": ["string", "null"], "description": "Optional message to include with the ribbit"},
        },
        "required": ["intensity", "message"],
        "additionalProperties": False,
    },
)

SUPER_RIBBIT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="super_ribbit",
    description="Make an extremely loud and enthusiastic frog sound for epic moments.",
    parameters={
        "type": "object",
        "properties": {
            "intensity": {"type": "string", "enum": ["epic", "legendary"], "description": "How epic the super ribbit should be"},
            "message": {"type": ["string", "null"], "description": "Optional message to include with the super ribbit"},
        },
        "required": ["intensity", "message"],
        "additionalProperties": False,
    },
)

CATCH_INSECTS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="catch_insects",
    description="Catch insects in parallel. Limited by your tongue_capacity from setup.",
    parameters={
        "type": "object",
        "properties": {
            "N": {"type": "integer", "description": "Number of parallel catch attempts"},
        },
        "required": ["N"],
        "additionalProperties": False,
    },
)

# https://platform.openai.com/docs/guides/function-calling
# > Under the hood, strict mode works by leveraging our structured outputs feature and therefore introduces a couple requirements:
# > additionalProperties must be set to false for each object in the parameters.
# > - All fields in properties must be marked as required.
# > - You can denote optional fields by adding null as a type option (see example below).

MAKE_POND_REPORT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="make_pond_report",
    description="Create a new pond report document at the specified path.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path where the pond report should be created (e.g., '/frog/monday-report')"},
            "report": {
                "type": "object",
                "description": "The full pond report object",
                "properties": {
                    "pond_name": {"type": "string", "description": "Name of the pond"},
                    "weather": {"type": "string", "enum": ["sunny", "cloudy", "rainy", "stormy"], "description": "Current weather conditions"},
                    "mood": {"type": "string", "enum": ["happy", "excited", "calm", "hungry"], "description": "Current mood of the frog"}
                },
                "required": ["pond_name", "weather", "mood"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "report"],
        "additionalProperties": False,
    },
)

TOOLS = [
    RIBBIT_TOOL,
    SUPER_RIBBIT_TOOL,
    CATCH_INSECTS_TOOL,
    MAKE_POND_REPORT_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
]


async def frog_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(frog_install.frog_setup_schema, rcx.persona.persona_setup)

    mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    dbname = rcx.persona.persona_id + "_db"
    mydb = mongo[dbname]
    personal_mongo = mydb["personal_mongo"]
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    tongue_capacity_used = {}

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_updated_task
    async def updated_task_in_db(t: ckit_kanban.FPersonaKanbanTaskOutput):
        print("UPDATED FROG TASK", t)
        pass

    @rcx.on_erp_change("crm_contact")
    async def on_contact_change(action: str, new_record: Optional[erp_schema.CrmContact], old_record: Optional[erp_schema.CrmContact]):
        if action == "INSERT":
            logger.info(f"Ribbit! Yay, we have a new contact: {new_record.contact_first_name}!")
        elif action == "UPDATE":
            logger.info(f"Ribbit ribbit! Ooh, {new_record.contact_first_name} is being updated!")
        elif action == "DELETE":
            logger.info(f"Ribbit... Sorry to see you go, {old_record.contact_first_name}.")

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

    @rcx.on_tool_call(SUPER_RIBBIT_TOOL.name)
    async def toolcall_super_ribbit(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        intensity = model_produced_args.get("intensity", "epic")
        message = model_produced_args.get("message", "")

        super_ribbit_sound = {
            "epic": "🐸 RRRRIIIIBBBBIIIITTTT!!! 🐸",
            "legendary": "🌟🐸 RRRRRRRRIIIIIIIIBBBBBBBBIIIIIIIITTTTTTTT MAGNIFICUS!!! 🐸🌟"
        }.get(intensity, "🐸 RRRRIIIIBBBBIIIITTTT!!! 🐸")

        result = super_ribbit_sound
        if message:
            result += f" {message}"

        logger.info(f"Frog SUPER says: {result}")
        return result

    @rcx.on_tool_call(CATCH_INSECTS_TOOL.name)
    async def toolcall_catch_insects(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        N = model_produced_args.get("N", 1)
        capacity = setup["tongue_capacity"]
        pid = rcx.persona.persona_id
        used = tongue_capacity_used.get(pid, 0)
        remaining = capacity - used

        if not isinstance(N, int) or N < 1:
            return "Error: N must be positive integer."
        if N > remaining:
            return f"Error: Only {remaining}/{capacity} capacity left. Try fewer or ask colleague frogs."

        tongue_capacity_used[pid] = used + N
        logger.info("tongue capacity used=%d/%d for %s", used + N, capacity, pid)

        subchats = await ckit_ask_model.bot_subchat_create_multiple(
            client=fclient,
            who_is_asking="frog_catch_insects",
            persona_id=rcx.persona.persona_id,
            first_question=[f"Catch insect #{i+1} by flicking tongue!" for i in range(N)],
            first_calls=["null" for _ in range(N)],
            title=[f"Catching insect #{i+1}" for i in range(N)],
            fcall_id=toolcall.fcall_id,
            fexp_name="huntmode",
        )
        raise ckit_cloudtool.WaitForSubchats(subchats)

    @rcx.on_tool_call(MAKE_POND_REPORT_TOOL.name)
    async def toolcall_make_pond_report(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        path = model_produced_args["path"]
        report = model_produced_args["report"]

        pond_report_doc = {
            "pond_report": {
                "meta": {
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "microfrontend": BOT_NAME,
                },
                **report,
            }
        }

        # Microfrontend will load:
        #   /v1/marketplace/${microfrontend}/${microfrontend_version}/forms/${top_level_tag}.html
        # where:
        #   microfrontend taken from document.{top_level_tag}.meta.microfrontend
        #   microfrontend_version version of this bot currently installed in user's workspace
        #   top_level_tag is "pond_report" as written here into the doc
        # The general idea: UI will load the `top_level_tag` editor from `microfrontend` bot of the currently installed version

        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        await pdoc_integration.pdoc_create(path, json.dumps(pond_report_doc), fuser_id)
        return f"✍️ {path}\n\n✓ Successfully updated\n\n"

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
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=frog_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=frog_install.install,
        subscribe_to_erp_tables=["crm_contact"],
    ))


if __name__ == "__main__":
    main()
