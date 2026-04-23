import asyncio
import logging
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_kanban

from flexus_client_kit import erp_schema
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_skills
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit.integrations import fi_mcp
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_telegram
from flexus_client_kit.integrations import fi_slack
from flexus_client_kit import ckit_bot_version
import gql.transport.exceptions

logger = logging.getLogger("bot_frog")


BOT_NAME = ckit_bot_version.bot_name_from_file(__file__)

FROG_ROOTDIR = Path(__file__).parent
FROG_SKILLS: list[str] = ckit_skills.static_skills_find(FROG_ROOTDIR, shared_skills_allowlist="*", integration_skills_allowlist="*")
FROG_MCPS = ["context7"]
FROG_SETUP_SCHEMA = json.loads((FROG_ROOTDIR / "setup_schema.json").read_text())
FROG_SETUP_SCHEMA.extend(fi_mcp.mcp_setup_schema(FROG_MCPS))

FROG_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    FROG_ROOTDIR,
    allowlist=[
        "flexus_policy_document",
        "print_widget",
        "gmail",
        "google_business",
        "google_ads",
        "google_sheets",
        "google_docs",
        "telegram",
        "slack",
        "x",
        "notion",
        "airtable",
        "hubspot",
        "twilio",
        "skills"
    ],
    builtin_skills=FROG_SKILLS,
)

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

GROUPCHAT_INVITE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="groupchat_invite",
    description=(
        "Invite a colleague frog into this thread as a groupchat peer. They see only your "
        "summary_so_far, not the full history. After this, messages here are shared with them."
    ),
    parameters={
        "type": "object",
        "properties": {
            "colleague_name": {"type": "string", "description": "persona_name of the colleague to invite (must be in this workspace, must expose the same expert you're running)"},
            "summary_so_far": {"type": "string", "description": "Everything the invitee needs to be useful. They do not see prior messages."},
            "standby": {"type": "boolean", "description": "True: you go silent after inviting, the colleague drives. False: both participate."},
        },
        "required": ["colleague_name", "summary_so_far", "standby"],
        "additionalProperties": False,
    },
)


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
    CATCH_INSECTS_TOOL,
    GROUPCHAT_INVITE_TOOL,
    MAKE_POND_REPORT_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
    *[t for rec in FROG_INTEGRATIONS for t in rec.integr_tools],
    *fi_mcp.mcp_tools(FROG_MCPS),
]


async def frog_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(FROG_SETUP_SCHEMA, rcx.persona.persona_setup)
    integr_objects = await ckit_integrations_db.main_loop_integrations_init(FROG_INTEGRATIONS, rcx, setup, need_mongo=True)
    pdoc_integration: fi_pdoc.IntegrationPdoc = integr_objects["flexus_policy_document"]
    tg: Optional[fi_telegram.IntegrationTelegram] = integr_objects.get("telegram")
    sl: Optional[fi_slack.IntegrationSlack] = integr_objects.get("slack")
    await fi_mcp.mcp_launch(FROG_MCPS, rcx, setup)

    tongue_capacity_used = {}

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        # Note: this and rcx.latest_threads have limited depth!
        # On start, some replay will arrive (100 threads or so) to address any bot downtime.
        # This handler is suitable to print for debugging, to write a consistency check (that does not crash if the thread not found in rcx.latest_threads).
        # Don't assume you'll find any thread infinitely in the past.
        pass

    # @rcx.on_updated_task
    # async def updated_task_in_db(action: str, old_task: Optional[ckit_kanban.FPersonaKanbanTaskOutput], new_task: Optional[ckit_kanban.FPersonaKanbanTaskOutput]):
    #     logger.info(f"Ribbit! task {action}: old={old_task} new={new_task}")

    @rcx.on_erp_change("crm_contact")
    async def on_contact_change(action: str, old_record: Optional[erp_schema.CrmContact], new_record: Optional[erp_schema.CrmContact]):
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

    @rcx.on_tool_call(GROUPCHAT_INVITE_TOOL.name)
    async def toolcall_groupchat_invite(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        colleague_name = model_produced_args["colleague_name"]
        summary_so_far = model_produced_args["summary_so_far"]
        standby = model_produced_args["standby"]
        http = await fclient.use_http_on_behalf(rcx.persona.persona_id, toolcall.fcall_untrusted_key)
        try:
            new_ft_id = await ckit_ask_model.groupchat_invite(http, toolcall.fcall_ft_id, colleague_name, summary_so_far, standby)
        except gql.transport.exceptions.TransportQueryError as e:
            return ckit_cloudtool.gql_error_4xx_to_model_reraise_5xx(e, "groupchat_invite")
        return f"Ribbit! Invited {colleague_name} (ft_id={new_ft_id})."

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

        await pdoc_integration.pdoc_create(path, json.dumps(pond_report_doc), persona_id=rcx.persona.persona_id, fcall_untrusted_key=toolcall.fcall_untrusted_key)
        return f"✍️ {path}\n\n✓ Successfully updated\n\n"

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def toolcall_mongo_store(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_mongo_store.handle_mongo_store(rcx, toolcall, model_produced_args)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
            # Here you can do whatever, just don't block with non-async code! Try not to keep sockets/resources you don't need,
            # also a common pitfall: execution reaches here far more often than every 10s when updates from backend actively arrive.
    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    from flexus_simple_bots.frog import frog_install
    scenario_fn = ckit_bot_exec.parse_bot_args()
    bot_version = ckit_bot_version.read_version_file(__file__)
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, bot_version), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        bot_main_loop=frog_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=frog_install.install,
        subscribe_to_erp_tables=["crm_contact"],
    ))


if __name__ == "__main__":
    main()
