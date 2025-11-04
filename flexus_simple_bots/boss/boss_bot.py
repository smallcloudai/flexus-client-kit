import asyncio
import logging
from typing import Dict, Any

import gql
from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_mongo
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.boss import boss_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_boss")


BOT_NAME = "boss"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)

ACCENT_COLOR = "#8B4513"


BOSS_A2A_RESOLUTION_TOOL = ckit_cloudtool.CloudTool(
    name="boss_a2a_resolution",
    description="Resolve an agent-to-agent handover task: approve, reject, or request rework",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {"type": "string", "description": "The ID of the task to resolve", "order": 1},
            "resolution": {"type": "string", "enum": ["approve", "reject", "rework"], "description": "Resolution type: approve (forward to target bot), reject (mark irrelevant), or rework (send back with feedback)", "order": 2},
            "comment": {"type": "string", "description": "Optional comment for approve, required for reject/rework", "order": 3}
        },
        "required": ["task_id", "resolution"]
    },
)

BOSS_SETUP_COLLEAGUES_TOOL = ckit_cloudtool.CloudTool(
    name="boss_setup_colleagues",
    description="Manage colleague bot configuration. Call with op='help' to show usage",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "enum": ["help", "get", "update"]},
            "args": {"type": "object"}
        },
        "required": ["op"]
    },
)

THREAD_MESSAGES_PRINTED_TOOL = ckit_cloudtool.CloudTool(
    name="thread_messages_printed",
    description="Print thread messages. Provide either a2a_task_id to view the thread that handed over this task, or ft_id to view thread directly",
    parameters={
        "type": "object",
        "properties": {
            "a2a_task_id": {"type": "string", "description": "A2A task ID to view the thread that handed over this task"},
            "ft_id": {"type": "string", "description": "Thread ID to view messages directly"}
        }
    },
)

TOOLS = [BOSS_A2A_RESOLUTION_TOOL, BOSS_SETUP_COLLEAGUES_TOOL, THREAD_MESSAGES_PRINTED_TOOL, fi_mongo_store.MONGO_STORE_TOOL, fi_pdoc.POLICY_DOCUMENT_TOOL]

SETUP_COLLEAGUES_HELP = """Usage:

boss_setup_colleagues(op='get', args={'bot_name': 'Frog'})
    View current setup for a colleague bot.

boss_setup_colleagues(op='update', args={'bot_name': 'Frog', 'set_key': 'greeting_style', 'set_val': 'excited'})
    Update a setup key for a colleague bot. Always run get operation before update.

boss_setup_colleagues(op='update', args={'bot_name': 'Frog', 'set_key': 'greeting_style'})
    Reset a setup key to default value (omit set_val). Always run get operation before update.
"""

async def handle_a2a_resolution(fclient: ckit_client.FlexusClient, model_produced_args: Dict[str, Any]) -> str:
    task_id = model_produced_args.get("task_id", "")
    resolution = model_produced_args.get("resolution", "")
    comment = model_produced_args.get("comment", "")
    if not task_id or resolution not in ["approve", "reject", "rework"] or (resolution in ["reject", "rework"] and not comment):
        return "Error: task_id required, resolution must be approve/reject/rework, comment required for reject/rework"
    http = await fclient.use_http()
    async with http as h:
        try:
            r = await h.execute(
                gql.gql("""mutation BossA2A($ktask_id: String!, $boss_intent_resolution: String!, $boss_intent_comment: String!) {
                    boss_a2a_resolution(ktask_id: $ktask_id, boss_intent_resolution: $boss_intent_resolution, boss_intent_comment: $boss_intent_comment)
                }"""),
                variable_values={"ktask_id": task_id, "boss_intent_resolution": resolution, "boss_intent_comment": comment},
            )
            if not r or not r.get("boss_a2a_resolution"):
                return f"Error: Failed to {resolution} task {task_id}"
        except gql.transport.exceptions.TransportQueryError as e:
            return f"Error: {e}"
    msg = {"approve": "approved and forwarded", "reject": "rejected", "rework": "sent back for rework"}[resolution]
    return f"Task {task_id} {msg}"


async def handle_setup_colleagues(fclient: ckit_client.FlexusClient, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
    op = model_produced_args.get("op", "")
    if not op or op == "help":
        return SETUP_COLLEAGUES_HELP
    if op not in ["get", "update"]:
        return f"Error: Unknown op: {op}\n\n{SETUP_COLLEAGUES_HELP}"
    args, args_err = ckit_cloudtool.sanitize_args(model_produced_args)
    if args_err:
        return f"Error: {args_err}\n\n{SETUP_COLLEAGUES_HELP}"
    if not (bot_name := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "bot_name", "")):
        return f"Error: bot_name required in args\n\n{SETUP_COLLEAGUES_HELP}"
    set_key = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "set_key", "") if op == "update" else None
    set_val = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "set_val", None) if op == "update" else None
    if op == "update" and not set_key:
        return f"Error: set_key required for update\n\n{SETUP_COLLEAGUES_HELP}"

    if op == "update" and not toolcall.confirmed_by_human:
        http = await fclient.use_http()
        async with http as h:
            r = await h.execute(
                gql.gql("""mutation BossSetupColleagues($bot_name: String!, $op: String!, $key: String) {
                    boss_setup_colleagues(bot_name: $bot_name, op: $op, key: $key)
                }"""),
                variable_values={"bot_name": bot_name, "op": "get", "key": set_key},
            )
            prev_val = r.get("boss_setup_colleagues", "")

        new_val = set_val if set_val is not None else "(default)"

        if len(new_val) < 100 and "\n" not in new_val and len(prev_val) < 100 and "\n" not in prev_val:
            explanation = f"Update {bot_name} setup key '{set_key}':\nNew value: {new_val}\nOld value: {prev_val}"
        else:
            new_lines = "\n".join(f"+ {line}" for line in new_val.split("\n"))
            old_lines = "\n".join(f"- {line}" for line in prev_val.split("\n"))
            explanation = f"Update {bot_name} setup key '{set_key}':\n\n{new_lines}\n{old_lines}"

        raise ckit_cloudtool.NeedsConfirmation(
            confirm_setup_key="boss_can_update_colleague_setup",
            confirm_command=f"update {bot_name}.{set_key}",
            confirm_explanation=explanation,
        )

    http = await fclient.use_http()
    async with http as h:
        try:
            r = await h.execute(
                gql.gql("""mutation BossSetupColleagues($bot_name: String!, $op: String!, $key: String, $val: String) {
                    boss_setup_colleagues(bot_name: $bot_name, op: $op, key: $key, val: $val)
                }"""),
                variable_values={"bot_name": bot_name, "op": op, "key": set_key, "val": set_val},
            )
            return r.get("boss_setup_colleagues", f"Error: Failed to {op} setup for {bot_name}")
        except gql.transport.exceptions.TransportQueryError as e:
            return f"GraphQL Error: {e}"


async def handle_thread_messages(fclient: ckit_client.FlexusClient, model_produced_args: Dict[str, Any]) -> str:
    a2a_task_id = model_produced_args.get("a2a_task_id") or None
    ft_id = model_produced_args.get("ft_id") or None
    if not a2a_task_id and not ft_id:
        return "Error: Either a2a_task_id or ft_id required"
    http = await fclient.use_http()
    async with http as h:
        try:
            r = await h.execute(
                gql.gql("""query BossThreadMsgs($a2a_task_id: String, $ft_id: String) {
                    thread_messages_printed(a2a_task_id_to_resolve: $a2a_task_id, ft_id: $ft_id) { thread_messages_data }
                }"""),
                variable_values={"a2a_task_id": a2a_task_id, "ft_id": ft_id},
            )
            if not (messages_data := r.get("thread_messages_printed", {}).get("thread_messages_data")):
                return "Error: No messages found"
            return messages_data
        except gql.transport.exceptions.TransportQueryError as e:
            return f"GraphQL Error: {e}"


async def boss_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(boss_install.boss_setup_schema, rcx.persona.persona_setup)

    mongo_conn_str = await ckit_mongo.get_mongodb_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    dbname = rcx.persona.persona_id + "_db"
    mydb = mongo[dbname]
    personal_mongo = mydb["personal_mongo"]

    pdoc_integration = fi_pdoc.IntegrationPdoc(fclient, rcx.persona.located_fgroup_id)

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_tool_call(BOSS_A2A_RESOLUTION_TOOL.name)
    async def toolcall_a2a_resolution(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await handle_a2a_resolution(fclient, model_produced_args)

    @rcx.on_tool_call(BOSS_SETUP_COLLEAGUES_TOOL.name)
    async def toolcall_colleague_setup(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await handle_setup_colleagues(fclient, toolcall, model_produced_args)

    @rcx.on_tool_call(THREAD_MESSAGES_PRINTED_TOOL.name)
    async def toolcall_thread_messages_printed(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await handle_thread_messages(fclient, model_produced_args)

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
