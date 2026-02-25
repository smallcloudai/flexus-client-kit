import asyncio
import json
import logging
from typing import Dict, Any

import gql
from pymongo import AsyncMongoClient

from flexus_client_kit.core import ckit_client
from flexus_client_kit.core import ckit_cloudtool
from flexus_client_kit.core import ckit_bot_exec
from flexus_client_kit.core import ckit_shutdown
from flexus_client_kit.core import ckit_ask_model
from flexus_client_kit.core import ckit_mongo
from flexus_client_kit.core import ckit_utils
from flexus_client_kit.integrations.providers.request_response import fi_mongo_store
from flexus_client_kit.integrations.providers.request_response import fi_pdoc
from flexus_client_kit.integrations.providers.request_response import fi_widget
from flexus_client_kit.integrations.providers.request_response import fi_erp
from flexus_simple_bots.handcrafted.boss import boss_install
from flexus_simple_bots.shared.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_boss")


BOT_NAME = "boss"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

ACCENT_COLOR = "#8B4513"


# BOSS_SETUP_COLLEAGUES_TOOL = ckit_cloudtool.CloudTool(
#     strict=False,
#     name="boss_setup_colleagues",
#     description="Manage colleague bot configuration. Call with op='help' to show usage",
#     parameters={
#         "type": "object",
#         "properties": {
#             "op": {"type": "string", "enum": ["help", "get", "update"]},
#             "args": {"type": "object"}
#         },
#         "required": ["op"]
#     },
# )

# THREAD_MESSAGES_PRINTED_TOOL = ckit_cloudtool.CloudTool(
#     strict=False,
#     name="thread_messages_printed",
#     description="Print thread messages. Provide either a2a_task_id to view the thread that handed over this task, or ft_id to view thread directly",
#     parameters={
#         "type": "object",
#         "properties": {
#             "a2a_task_id": {"type": "string", "description": "A2A task ID to view the thread that handed over this task"},
#             "ft_id": {"type": "string", "description": "Thread ID to view messages directly"}
#         }
#     },
# )

# BOT_BUG_REPORT_TOOL = ckit_cloudtool.CloudTool(
#     strict=False,
#     name="bot_bug_report",
#     description="Report a bug related to a bot's code, tools, or prompts. Call with op=help for usage.",
#     parameters={
#         "type": "object",
#         "properties": {
#             "op": {"type": "string", "enum": ["help", "report_bug", "list_reported_bugs"]},
#             "args": {"type": "object"}
#         },
#         "required": ["op"]
#     },
# )

SETUP_COLLEAGUES_HELP = """Usage:

boss_setup_colleagues(op='get', args={'bot_name': 'Frog'})
    View current setup for a colleague bot.

boss_setup_colleagues(op='update', args={'bot_name': 'Frog', 'set_key': 'greeting_style', 'set_val': 'excited'})
    Update a setup key for a colleague bot. Always run get operation before update.

boss_setup_colleagues(op='update', args={'bot_name': 'Frog', 'set_key': 'greeting_style'})
    Reset a setup key to default value (omit set_val). Always run get operation before update.
"""

BOT_BUG_REPORT_HELP = """Report a bug related to a bot's code, tools, or prompts (not configuration issues).
Always list bugs before reporting to avoid duplicates.

Usage:

bot_bug_report(op='report_bug', args={'bot_name': 'Karen 5', 'ft_id': 'ft_abc123', 'bug_summary': 'Bot fails to parse dates in ISO format'})
    Report a bug related to a bot's code, tools, or prompts.

bot_bug_report(op='list_reported_bugs', args={'bot_name': 'Frog'})
    List all reported bugs for a specific bot.
"""

MARKETPLACE_SEARCH_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="flexus_marketplace_search",
    description="Search the Flexus marketplace for bots by keyword. Returns matching bot names, titles, tags, and whether already hired.",
    parameters={
        "type": "object",
        "properties": {
            "q": {"type": "string", "description": "Search query (matches name, title, description, tags)"},
        },
        "required": ["q"],
    },
)

MARKETPLACE_DESC_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="flexus_marketplace_desc",
    description="Get detailed descriptions for specific marketplace bots by their marketable_name. Up to 20 names.",
    parameters={
        "type": "object",
        "properties": {
            "marketable_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of bot marketable_name values to get descriptions for",
            },
        },
        "required": ["marketable_names"],
    },
)

TOOLS = [
    # BOSS_A2A_RESOLUTION_TOOL,
    # BOSS_SETUP_COLLEAGUES_TOOL,
    # THREAD_MESSAGES_PRINTED_TOOL,
    # BOT_BUG_REPORT_TOOL,
    fi_widget.PRINT_WIDGET_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_erp.ERP_TABLE_META_TOOL,
    fi_erp.ERP_TABLE_DATA_TOOL,
    MARKETPLACE_SEARCH_TOOL,
    MARKETPLACE_DESC_TOOL,
]


# async def handle_setup_colleagues(fclient: ckit_client.FlexusClient, ws_id: str, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
#     op = model_produced_args.get("op", "")
#     if not op or op == "help":
#         return SETUP_COLLEAGUES_HELP
#     if op not in ["get", "update"]:
#         return f"Error: Unknown op: {op}\n\n{SETUP_COLLEAGUES_HELP}"
#     args, args_err = ckit_cloudtool.sanitize_args(model_produced_args)
#     if args_err:
#         return f"Error: {args_err}\n\n{SETUP_COLLEAGUES_HELP}"
#     if not (bot_name := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "bot_name", "")):
#         return f"Error: bot_name required in args\n\n{SETUP_COLLEAGUES_HELP}"
#     set_key = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "set_key", "") if op == "update" else None
#     set_val = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "set_val", None) if op == "update" else None
#     if op == "update" and not set_key:
#         return f"Error: set_key required for update\n\n{SETUP_COLLEAGUES_HELP}"

#     if op == "update" and not toolcall.confirmed_by_human:
#         http = await fclient.use_http()
#         async with http as h:
#             try:
#                 r = await h.execute(
#                     gql.gql("""mutation BossSetupColleagues($ws_id: String!, $bot_name: String!, $op: String!, $key: String) {
#                         boss_setup_colleagues(ws_id: $ws_id, bot_name: $bot_name, op: $op, key: $key)
#                     }"""),
#                     variable_values={"ws_id": ws_id, "bot_name": bot_name, "op": "get", "key": set_key},
#                 )
#                 prev_val = r.get("boss_setup_colleagues", "")
#             except gql.transport.exceptions.TransportQueryError as e:
#                 return f"Error: {e}"

#         new_val = set_val if set_val is not None else "(default)"

#         if len(new_val) < 100 and "\n" not in new_val and len(prev_val) < 100 and "\n" not in prev_val:
#             explanation = f"Update {bot_name} setup key '{set_key}':\nNew value: {new_val}\nOld value: {prev_val}"
#         else:
#             new_lines = "\n".join(f"+ {line}" for line in new_val.split("\n"))
#             old_lines = "\n".join(f"- {line}" for line in prev_val.split("\n"))
#             explanation = f"Update {bot_name} setup key '{set_key}':\n\n{new_lines}\n{old_lines}"

#         raise ckit_cloudtool.NeedsConfirmation(
#             confirm_setup_key="boss_can_update_colleague_setup",
#             confirm_command=f"update {bot_name}.{set_key}",
#             confirm_explanation=explanation,
#         )

#     http = await fclient.use_http()
#     async with http as h:
#         try:
#             r = await h.execute(
#                 gql.gql("""mutation BossSetupColleagues($ws_id: String!, $bot_name: String!, $op: String!, $key: String, $val: String) {
#                     boss_setup_colleagues(ws_id: $ws_id, bot_name: $bot_name, op: $op, key: $key, val: $val)
#                 }"""),
#                 variable_values={"ws_id": ws_id, "bot_name": bot_name, "op": op, "key": set_key, "val": set_val},
#             )
#             return r.get("boss_setup_colleagues", f"Error: Failed to {op} setup for {bot_name}")
#         except gql.transport.exceptions.TransportQueryError as e:
#             # FIXME handler does not support apikey/session for regular user to debug
#             # 20251118 09:43:22.373 super [WARN] ⚠️  127.0.0.1 someone introduces itself as 'boss_20003_solar_root' and wants to access /v1/jailed-bot, denied; tries to use super_password=bad-superu... current_state=[curr-secre..., prev-secre...]
#             # 20251118 09:43:22.373 exces [INFO] 127.0.0.1 403 /boss_setup_colleagues 0.000s: Whoops your key didn't work (1).
#             logger.exception("handle_setup_colleagues error")
#             return f"handle_setup_colleagues problem: {e}"


# async def handle_thread_messages(fclient: ckit_client.FlexusClient, model_produced_args: Dict[str, Any]) -> str:
#     a2a_task_id = model_produced_args.get("a2a_task_id") or None
#     ft_id = model_produced_args.get("ft_id") or None
#     if not a2a_task_id and not ft_id:
#         return "Error: Either a2a_task_id or ft_id required"
#     http = await fclient.use_http()
#     async with http as h:
#         try:
#             r = await h.execute(
#                 gql.gql("""query BossThreadMsgs($a2a_task_id: String, $ft_id: String) {
#                     thread_messages_printed(a2a_task_id_to_resolve: $a2a_task_id, ft_id: $ft_id) { thread_messages_data }
#                 }"""),
#                 variable_values={"a2a_task_id": a2a_task_id, "ft_id": ft_id},
#             )
#             if not (messages_data := r.get("thread_messages_printed", {}).get("thread_messages_data")):
#                 return "Error: No messages found"
#             return messages_data
#         except gql.transport.exceptions.TransportQueryError as e:
#             return f"GraphQL Error: {e}"


# async def handle_bot_bug_report(fclient: ckit_client.FlexusClient, ws_id: str, model_produced_args: Dict[str, Any]) -> str:
#     op = model_produced_args.get("op", "")
#     if not op or op == "help":
#         return BOT_BUG_REPORT_HELP
#     if op not in ["report_bug", "list_reported_bugs"]:
#         return f"Error: Unknown op: {op}\n\n{BOT_BUG_REPORT_HELP}"
#     args, args_err = ckit_cloudtool.sanitize_args(model_produced_args)
#     if args_err:
#         return f"Error: {args_err}\n\n{BOT_BUG_REPORT_HELP}"
#     if not (bot_name := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "bot_name", "")):
#         return f"Error: bot_name required in args\n\n{BOT_BUG_REPORT_HELP}"

#     http = await fclient.use_http()
#     async with http as h:
#         try:
#             r = await h.execute(
#                 gql.gql("""query WorkspacePersonasList($ws_id: String!, $persona_names_filter: [String!]) {
#                     workspace_personas_list(ws_id: $ws_id, persona_names_filter: $persona_names_filter) {
#                         personas {
#                             persona_marketable_name
#                             persona_marketable_version
#                         }
#                     }
#                 }"""),
#                 variable_values={"ws_id": ws_id, "persona_names_filter": [bot_name]},
#             )
#             personas = r.get("workspace_personas_list", {}).get("personas", [])
#             if not personas:
#                 return f"Error: Bot '{bot_name}' not found in workspace"

#             persona_marketable_name = personas[0]["persona_marketable_name"]
#             persona_marketable_version = personas[0]["persona_marketable_version"]

#             if op == "list_reported_bugs":
#                 r = await h.execute(
#                     gql.gql("""query MarketplaceFeedbackListByBot($persona_marketable_name: String!, $persona_marketable_version: Int!) {
#                         priviledged_feedback_list(persona_marketable_name: $persona_marketable_name, persona_marketable_version: $persona_marketable_version) {
#                             total_count feedbacks { feedback_text }
#                         }
#                     }"""),
#                     variable_values={"persona_marketable_name": persona_marketable_name, "persona_marketable_version": persona_marketable_version},
#                 )
#                 feedback_data = r.get("priviledged_feedback_list", {})
#                 feedbacks = feedback_data.get("feedbacks", [])
#                 total_count = feedback_data.get("total_count", 0)
#                 if not feedbacks:
#                     return f"No reported bugs found for {bot_name}"
#                 result = f"Reported bugs for {bot_name}:\n\n"
#                 for i, fb in enumerate(feedbacks, 1):
#                     result += f"{i}. {ckit_utils.truncate_middle(fb['feedback_text'], 5000)}\n\n"
#                 if total_count > len(feedbacks):
#                     result += f"... and {total_count - len(feedbacks)} more\n"
#                 return result

#             ft_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "ft_id", "")
#             bug_summary = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "bug_summary", "")
#             if not ft_id or not bug_summary:
#                 return f"Error: ft_id and bug_summary required for report_bug\n\n{BOT_BUG_REPORT_HELP}"

#             r = await h.execute(
#                 gql.gql("""mutation ReportBotBug(
#                     $persona_marketable_name: String!,
#                     $persona_marketable_version: Int!,
#                     $feedback_ft_id: String!,
#                     $feedback_text: String!
#                 ) {
#                     priviledged_feedback_submit(
#                         persona_marketable_name: $persona_marketable_name,
#                         persona_marketable_version: $persona_marketable_version,
#                         feedback_ft_id: $feedback_ft_id,
#                         feedback_text: $feedback_text
#                     ) { feedback_id }
#                 }"""),
#                 variable_values={
#                     "persona_marketable_name": persona_marketable_name,
#                     "persona_marketable_version": persona_marketable_version,
#                     "feedback_ft_id": ft_id,
#                     "feedback_text": bug_summary,
#                 },
#             )
#             if not (feedback_id := r.get("priviledged_feedback_submit", {}).get("feedback_id")):
#                 return f"Error: Failed to submit bug report for {bot_name}"
#             return f"Bug report submitted successfully for {bot_name} (feedback_id: {feedback_id})"
#         except gql.transport.exceptions.TransportQueryError as e:
#             return f"GraphQL Error: {e}"


async def boss_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(boss_install.boss_setup_schema, rcx.persona.persona_setup)

    mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    dbname = rcx.persona.persona_id + "_db"
    mydb = mongo[dbname]
    personal_mongo = mydb["personal_mongo"]

    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)
    erp_integration = fi_erp.IntegrationErp(fclient, rcx.persona.ws_id, personal_mongo)

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    # @rcx.on_tool_call(BOSS_SETUP_COLLEAGUES_TOOL.name)
    # async def toolcall_colleague_setup(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
    #     return await handle_setup_colleagues(fclient, rcx.persona.ws_id, toolcall, model_produced_args)

    # @rcx.on_tool_call(THREAD_MESSAGES_PRINTED_TOOL.name)
    # async def toolcall_thread_messages_printed(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
    #     return await handle_thread_messages(fclient, model_produced_args)

    # @rcx.on_tool_call(BOT_BUG_REPORT_TOOL.name)
    # async def toolcall_bot_bug_report(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
    #     return await handle_bot_bug_report(fclient, rcx.persona.ws_id, model_produced_args)

    @rcx.on_tool_call(fi_widget.PRINT_WIDGET_TOOL.name)
    async def toolcall_print_widget(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_widget.handle_print_widget(toolcall, model_produced_args)

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

    @rcx.on_tool_call(fi_erp.ERP_TABLE_META_TOOL.name)
    async def toolcall_erp_meta(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await erp_integration.handle_erp_meta(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_erp.ERP_TABLE_DATA_TOOL.name)
    async def toolcall_erp_data(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await erp_integration.handle_erp_data(toolcall, model_produced_args)

    @rcx.on_tool_call(MARKETPLACE_SEARCH_TOOL.name)
    async def toolcall_marketplace_search(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        q = model_produced_args.get("q", "").strip()
        if not q:
            return "Error: q (search query) is required"
        http = await fclient.use_http()
        async with http as h:
            r = await h.execute(gql.gql("""
                query BossMarketplaceSearch($q: String!, $ws_id: String!) {
                    marketplace_boss_search(q: $q, ws_id: $ws_id) {
                        marketable_name marketable_title1 marketable_title2 marketable_tags already_hired
                    }
                }"""),
                variable_values={"q": q, "ws_id": rcx.persona.ws_id},
            )
        items = r.get("marketplace_boss_search", [])
        return f"{len(items)} bots found\n\n" + "\n".join(json.dumps(it) for it in items)

    @rcx.on_tool_call(MARKETPLACE_DESC_TOOL.name)
    async def toolcall_marketplace_desc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        names = model_produced_args.get("marketable_names", [])
        if not names or not isinstance(names, list):
            return "Error: marketable_names (list of strings) is required"
        if len(names) > 20:
            return "Error: max 20 names at a time"
        http = await fclient.use_http()
        async with http as h:
            r = await h.execute(gql.gql("""
                query BossMarketplaceDesc($marketable_names: [String!]!, $ws_id: String!) {
                    marketplace_boss_desc(marketable_names: $marketable_names, ws_id: $ws_id) {
                        marketable_name marketable_title1 marketable_title2 marketable_description marketable_tags marketable_occupation
                        experts { fexp_name fexp_description }
                    }
                }"""),
                variable_values={"marketable_names": names, "ws_id": rcx.persona.ws_id},
            )
        items = r.get("marketplace_boss_desc", [])
        parts = [f"{len(items)} descriptions found"]
        for it in items:
            parts.append(json.dumps({
                "marketable_name": it["marketable_name"],
                "title1": it["marketable_title1"],
                "title2": it["marketable_title2"],
                "occupation": it["marketable_occupation"],
                "tags": it["marketable_tags"],
                "description": it["marketable_description"],
                "experts": it["experts"],
            }, indent=2, ensure_ascii=False))
        return "\n\n".join(parts)

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
        bot_main_loop=boss_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=boss_install.install,
    ))


if __name__ == "__main__":
    main()
