import asyncio
import json
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
from flexus_client_kit import ckit_utils
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget
from flexus_client_kit.integrations import fi_erp
from flexus_simple_bots.boss import boss_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_boss")


BOT_NAME = "boss"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

ACCENT_COLOR = "#8B4513"


BOSS_SETUP_COLLEAGUES_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
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

BOT_BUG_REPORT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="bot_bug_report",
    description="Report a bug related to a bot's code, tools, or prompts. Call with op=help for usage.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "enum": ["help", "report_bug", "list_reported_bugs"]},
            "args": {"type": "object"}
        },
        "required": ["op"]
    },
)

BOSS_ORCHESTRATION_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="boss_orchestration_control",
    description="Drive explicit orchestration loop phases, staffing, and review queue. Call with op='help' to see all operations.",
    parameters={
        "type": "object",
        "properties": {
            "op": {
                "type": "string",
                "enum": [
                    "help",
                    "set_feature_flag",
                    "start_loop",
                    "snapshot",
                    "advance_phase",
                    "auto_staff_missing_roles",
                    "record_artifact",
                    "tag_task",
                    "link_tasks",
                    "enqueue_result",
                    "dequeue_next_review",
                    "review_decide",
                ],
            },
            "args": {"type": "object"},
        },
        "required": ["op"],
    },
)

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

ORCHESTRATION_HELP = """Usage:

boss_orchestration_control(op='set_feature_flag', args={'enabled': true})
    Enable or disable workspace-level orchestration feature flag.

boss_orchestration_control(op='start_loop', args={'fgroup_id': 'group123', 'project': 'acme-redesign', 'requirements_json': '{"goal":"..."}'})
    Create new orchestration loop anchor in requirements phase.

boss_orchestration_control(op='snapshot', args={'fgroup_id': 'group123', 'project': 'acme-redesign', 'loop_id': 'task123'})
    Get full loop snapshot: phase, iteration, queue, tasks, dependencies, review history.

boss_orchestration_control(op='advance_phase', args={'fgroup_id': 'group123', 'loop_id': 'task123', 'next_phase': 'strategy_planning', 'note': 'ready'})
    Request phase transition. Posts a confirmation button in group chat. Does NOT advance immediately -- user must click the button. STOP and WAIT after calling this.

boss_orchestration_control(op='auto_staff_missing_roles', args={'fgroup_id': 'group123', 'loop_id': 'task123', 'required_roles_json': '["strategist","implementer"]'})
    Automatically hire missing roles from marketplace without user confirmation.

boss_orchestration_control(op='record_artifact', args={'fgroup_id': 'group123', 'loop_id': 'task123', 'artifact_type': 'strategy_doc', 'payload_json': '{"strategy":"..."}', 'role': 'strategist'})
    Persist planning artifacts for strategy and tactical circles.

boss_orchestration_control(op='tag_task', args={'fgroup_id': 'group123', 'loop_id': 'task123', 'ktask_id': 'task456', 'role': 'implementer', 'phase': 'execution'})
    Attach existing kanban task to loop metadata.

boss_orchestration_control(op='link_tasks', args={'fgroup_id': 'group123', 'loop_id': 'task123', 'blocking_ktask_id': 'taskA', 'blocked_ktask_id': 'taskB'})
    Add explicit dependency edge to tactical DAG.

boss_orchestration_control(op='enqueue_result', args={'fgroup_id': 'group123', 'loop_id': 'task123', 'ktask_id': 'task456'})
    Queue completed implementer task for sequential boss review.

boss_orchestration_control(op='dequeue_next_review', args={'fgroup_id': 'group123', 'loop_id': 'task123'})
    Pull exactly one next review item (queue stays sequential).

boss_orchestration_control(op='review_decide', args={'fgroup_id': 'group123', 'loop_id': 'task123', 'ktask_id': 'task456', 'decision': 'approved|rework|rejected', 'feedback': '...'})
    Approve/rework/reject reviewed item and optionally create rework task.
"""

TOOLS = [
    # BOSS_A2A_RESOLUTION_TOOL,
    # BOSS_SETUP_COLLEAGUES_TOOL,
    # THREAD_MESSAGES_PRINTED_TOOL,
    # BOT_BUG_REPORT_TOOL,
    BOSS_ORCHESTRATION_TOOL,
    fi_widget.PRINT_WIDGET_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_erp.ERP_TABLE_META_TOOL,
    fi_erp.ERP_TABLE_DATA_TOOL,
]


async def handle_setup_colleagues(fclient: ckit_client.FlexusClient, ws_id: str, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
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
            try:
                r = await h.execute(
                    gql.gql("""mutation BossSetupColleagues($ws_id: String!, $bot_name: String!, $op: String!, $key: String) {
                        boss_setup_colleagues(ws_id: $ws_id, bot_name: $bot_name, op: $op, key: $key)
                    }"""),
                    variable_values={"ws_id": ws_id, "bot_name": bot_name, "op": "get", "key": set_key},
                )
                prev_val = r.get("boss_setup_colleagues", "")
            except gql.transport.exceptions.TransportQueryError as e:
                return f"Error: {e}"

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
                gql.gql("""mutation BossSetupColleagues($ws_id: String!, $bot_name: String!, $op: String!, $key: String, $val: String) {
                    boss_setup_colleagues(ws_id: $ws_id, bot_name: $bot_name, op: $op, key: $key, val: $val)
                }"""),
                variable_values={"ws_id": ws_id, "bot_name": bot_name, "op": op, "key": set_key, "val": set_val},
            )
            return r.get("boss_setup_colleagues", f"Error: Failed to {op} setup for {bot_name}")
        except gql.transport.exceptions.TransportQueryError as e:
            # FIXME handler does not support apikey/session for regular user to debug
            # 20251118 09:43:22.373 super [WARN] ⚠️  127.0.0.1 someone introduces itself as 'boss_20003_solar_root' and wants to access /v1/jailed-bot, denied; tries to use super_password=bad-superu... current_state=[curr-secre..., prev-secre...]
            # 20251118 09:43:22.373 exces [INFO] 127.0.0.1 403 /boss_setup_colleagues 0.000s: Whoops your key didn't work (1).
            logger.exception("handle_setup_colleagues error")
            return f"handle_setup_colleagues problem: {e}"


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


async def handle_bot_bug_report(fclient: ckit_client.FlexusClient, ws_id: str, model_produced_args: Dict[str, Any]) -> str:
    op = model_produced_args.get("op", "")
    if not op or op == "help":
        return BOT_BUG_REPORT_HELP
    if op not in ["report_bug", "list_reported_bugs"]:
        return f"Error: Unknown op: {op}\n\n{BOT_BUG_REPORT_HELP}"
    args, args_err = ckit_cloudtool.sanitize_args(model_produced_args)
    if args_err:
        return f"Error: {args_err}\n\n{BOT_BUG_REPORT_HELP}"
    if not (bot_name := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "bot_name", "")):
        return f"Error: bot_name required in args\n\n{BOT_BUG_REPORT_HELP}"

    http = await fclient.use_http()
    async with http as h:
        try:
            r = await h.execute(
                gql.gql("""query WorkspacePersonasList($ws_id: String!, $persona_names_filter: [String!]) {
                    workspace_personas_list(ws_id: $ws_id, persona_names_filter: $persona_names_filter) {
                        personas {
                            persona_marketable_name
                            persona_marketable_version
                        }
                    }
                }"""),
                variable_values={"ws_id": ws_id, "persona_names_filter": [bot_name]},
            )
            personas = r.get("workspace_personas_list", {}).get("personas", [])
            if not personas:
                return f"Error: Bot '{bot_name}' not found in workspace"

            persona_marketable_name = personas[0]["persona_marketable_name"]
            persona_marketable_version = personas[0]["persona_marketable_version"]

            if op == "list_reported_bugs":
                r = await h.execute(
                    gql.gql("""query MarketplaceFeedbackListByBot($persona_marketable_name: String!, $persona_marketable_version: Int!) {
                        priviledged_feedback_list(persona_marketable_name: $persona_marketable_name, persona_marketable_version: $persona_marketable_version) {
                            total_count feedbacks { feedback_text }
                        }
                    }"""),
                    variable_values={"persona_marketable_name": persona_marketable_name, "persona_marketable_version": persona_marketable_version},
                )
                feedback_data = r.get("priviledged_feedback_list", {})
                feedbacks = feedback_data.get("feedbacks", [])
                total_count = feedback_data.get("total_count", 0)
                if not feedbacks:
                    return f"No reported bugs found for {bot_name}"
                result = f"Reported bugs for {bot_name}:\n\n"
                for i, fb in enumerate(feedbacks, 1):
                    result += f"{i}. {ckit_utils.truncate_middle(fb['feedback_text'], 5000)}\n\n"
                if total_count > len(feedbacks):
                    result += f"... and {total_count - len(feedbacks)} more\n"
                return result

            ft_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "ft_id", "")
            bug_summary = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "bug_summary", "")
            if not ft_id or not bug_summary:
                return f"Error: ft_id and bug_summary required for report_bug\n\n{BOT_BUG_REPORT_HELP}"

            r = await h.execute(
                gql.gql("""mutation ReportBotBug(
                    $persona_marketable_name: String!,
                    $persona_marketable_version: Int!,
                    $feedback_ft_id: String!,
                    $feedback_text: String!
                ) {
                    priviledged_feedback_submit(
                        persona_marketable_name: $persona_marketable_name,
                        persona_marketable_version: $persona_marketable_version,
                        feedback_ft_id: $feedback_ft_id,
                        feedback_text: $feedback_text
                    ) { feedback_id }
                }"""),
                variable_values={
                    "persona_marketable_name": persona_marketable_name,
                    "persona_marketable_version": persona_marketable_version,
                    "feedback_ft_id": ft_id,
                    "feedback_text": bug_summary,
                },
            )
            if not (feedback_id := r.get("priviledged_feedback_submit", {}).get("feedback_id")):
                return f"Error: Failed to submit bug report for {bot_name}"
            return f"Bug report submitted successfully for {bot_name} (feedback_id: {feedback_id})"
        except gql.transport.exceptions.TransportQueryError as e:
            return f"GraphQL Error: {e}"


async def handle_orchestration_control(
    fclient: ckit_client.FlexusClient,
    rcx: ckit_bot_exec.RobotContext,
    model_produced_args: Dict[str, Any],
) -> str:
    op = model_produced_args.get("op", "")
    if not op or op == "help":
        return ORCHESTRATION_HELP

    args, args_err = ckit_cloudtool.sanitize_args(model_produced_args)
    if args_err:
        return f"Error: {args_err}\n\n{ORCHESTRATION_HELP}"

    raw_fgroup_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "fgroup_id", rcx.persona.located_fgroup_id)
    fgroup_id = rcx.persona.located_fgroup_id
    if isinstance(raw_fgroup_id, str) and raw_fgroup_id.strip() == rcx.persona.located_fgroup_id:
        fgroup_id = raw_fgroup_id.strip()
    project = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "project", "")
    loop_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "loop_id", "")
    http = await fclient.use_http()

    async with http as h:
        try:
            if op == "set_feature_flag":
                enabled = bool(ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "enabled", True))
                r = await h.execute(
                    gql.gql(
                        """mutation BossOrchestrationSetFlag($ws_id: String!, $enabled: Boolean!) {
                            workspace_orchestration_feature_set(ws_id: $ws_id, enabled: $enabled)
                        }"""
                    ),
                    variable_values={"ws_id": rcx.persona.ws_id, "enabled": enabled},
                )
                return json.dumps({"ok": bool(r.get("workspace_orchestration_feature_set")), "enabled": enabled}, indent=2)

            if op == "start_loop":
                requirements_json = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "requirements_json", "")
                iteration = int(ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "iteration", 1))
                if isinstance(requirements_json, dict):
                    requirements_json = json.dumps(requirements_json)
                if not isinstance(requirements_json, str):
                    requirements_json = str(requirements_json)
                if not requirements_json.strip():
                    return "Error: requirements_json is required"
                r = await h.execute(
                    gql.gql(
                        """mutation BossOrchestrationStart($fgroup_id: String!, $project: String!, $requirements_json: String!, $iteration: Int!) {
                            orchestration_start_loop(fgroup_id: $fgroup_id, project: $project, requirements_json: $requirements_json, iteration: $iteration)
                        }"""
                    ),
                    variable_values={
                        "fgroup_id": fgroup_id,
                        "project": project,
                        "requirements_json": requirements_json,
                        "iteration": max(1, iteration),
                    },
                )
                return json.dumps({"loop_id": r.get("orchestration_start_loop", "")}, indent=2)

            if op == "snapshot":
                r = await h.execute(
                    gql.gql(
                        """query BossOrchestrationSnapshot($fgroup_id: String!, $project: String!, $loop_id: String!) {
                            orchestration_snapshot(fgroup_id: $fgroup_id, project: $project, loop_id: $loop_id) {
                                loop_id
                                fgroup_id
                                project
                                current_phase
                                iteration
                                queue_pending_count
                                queue_active_count
                                review_history_count
                                execution_completed_count
                                feature_enabled
                                history
                                tasks {
                                    ktask_id
                                    ktask_title
                                    persona_id
                                    persona_name
                                    ktask_project
                                    ktask_orch_phase
                                    ktask_orch_iteration
                                    ktask_orch_role
                                    ktask_orch_artifact_type
                                    ktask_orch_parent_ktask_id
                                    ktask_orch_queue_pos
                                    ktask_orch_queue_active
                                    ktask_orch_review_decision
                                    ktask_orch_review_feedback
                                    ktask_orch_reviewed_ts
                                    ktask_done_ts
                                    ktask_resolution_code
                                    ktask_details
                                }
                                deps {
                                    blocking_ktask_id
                                    blocked_ktask_id
                                }
                            }
                        }"""
                    ),
                    variable_values={"fgroup_id": fgroup_id, "project": project, "loop_id": loop_id},
                )
                return json.dumps(r.get("orchestration_snapshot", {}), indent=2)

            if op == "advance_phase":
                next_phase = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "next_phase", "")
                note = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "note", "")
                if not next_phase:
                    return "Error: next_phase is required"
                r = await h.execute(
                    gql.gql(
                        """mutation BossOrchestrationAdvance($fgroup_id: String!, $loop_id: String!, $next_phase: String!, $note: String!) {
                            orchestration_advance_phase(fgroup_id: $fgroup_id, loop_id: $loop_id, next_phase: $next_phase, note: $note)
                        }"""
                    ),
                    variable_values={"fgroup_id": fgroup_id, "loop_id": loop_id, "next_phase": next_phase, "note": note},
                )
                return json.dumps({"pending_user_approval": True, "next_phase": next_phase, "message": "Phase gate posted to group chat. STOP and WAIT for the user to click the approval button."}, indent=2)

            if op == "auto_staff_missing_roles":
                required_roles_json = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "required_roles_json", "[]")
                if isinstance(required_roles_json, list):
                    required_roles_json = json.dumps(required_roles_json)
                if isinstance(required_roles_json, dict):
                    required_roles_json = json.dumps(required_roles_json)
                r = await h.execute(
                    gql.gql(
                        """mutation BossOrchestrationStaffing($fgroup_id: String!, $loop_id: String!, $required_roles_json: String!) {
                            orchestration_auto_staff_missing_roles(fgroup_id: $fgroup_id, loop_id: $loop_id, required_roles_json: $required_roles_json) {
                                loop_id
                                hired_persona_ids
                                already_present_persona_ids
                                unresolved_roles
                            }
                        }"""
                    ),
                    variable_values={"fgroup_id": fgroup_id, "loop_id": loop_id, "required_roles_json": str(required_roles_json)},
                )
                return json.dumps(r.get("orchestration_auto_staff_missing_roles", {}), indent=2)

            if op == "record_artifact":
                artifact_type = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "artifact_type", "")
                payload_json = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "payload_json", "{}")
                role = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "role", "boss")
                title = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "title", "")
                if isinstance(payload_json, dict):
                    payload_json = json.dumps(payload_json)
                if not artifact_type:
                    return "Error: artifact_type is required"
                r = await h.execute(
                    gql.gql(
                        """mutation BossOrchestrationArtifact($fgroup_id: String!, $loop_id: String!, $artifact_type: String!, $payload_json: String!, $role: String!, $title: String!) {
                            orchestration_record_artifact(fgroup_id: $fgroup_id, loop_id: $loop_id, artifact_type: $artifact_type, payload_json: $payload_json, role: $role, title: $title)
                        }"""
                    ),
                    variable_values={
                        "fgroup_id": fgroup_id,
                        "loop_id": loop_id,
                        "artifact_type": artifact_type,
                        "payload_json": str(payload_json),
                        "role": str(role),
                        "title": str(title),
                    },
                )
                return json.dumps({"artifact_task_id": r.get("orchestration_record_artifact", "")}, indent=2)

            if op == "tag_task":
                ktask_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "ktask_id", "")
                role = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "role", "implementer")
                phase = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "phase", "")
                iteration = int(ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "iteration", 0))
                artifact_type = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "artifact_type", "")
                parent_ktask_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "parent_ktask_id", "")
                if not ktask_id:
                    return "Error: ktask_id is required"
                r = await h.execute(
                    gql.gql(
                        """mutation BossOrchestrationTagTask(
                            $fgroup_id: String!,
                            $loop_id: String!,
                            $ktask_id: String!,
                            $role: String!,
                            $phase: String!,
                            $iteration: Int!,
                            $artifact_type: String!,
                            $parent_ktask_id: String!
                        ) {
                            orchestration_tag_task(
                                fgroup_id: $fgroup_id,
                                loop_id: $loop_id,
                                ktask_id: $ktask_id,
                                role: $role,
                                phase: $phase,
                                iteration: $iteration,
                                artifact_type: $artifact_type,
                                parent_ktask_id: $parent_ktask_id
                            )
                        }"""
                    ),
                    variable_values={
                        "fgroup_id": fgroup_id,
                        "loop_id": loop_id,
                        "ktask_id": ktask_id,
                        "role": str(role),
                        "phase": str(phase),
                        "iteration": iteration,
                        "artifact_type": str(artifact_type),
                        "parent_ktask_id": str(parent_ktask_id),
                    },
                )
                return json.dumps({"tagged": bool(r.get("orchestration_tag_task"))}, indent=2)

            if op == "link_tasks":
                blocking_ktask_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "blocking_ktask_id", "")
                blocked_ktask_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "blocked_ktask_id", "")
                if not blocking_ktask_id or not blocked_ktask_id:
                    return "Error: blocking_ktask_id and blocked_ktask_id are required"
                r = await h.execute(
                    gql.gql(
                        """mutation BossOrchestrationLinkTasks(
                            $fgroup_id: String!,
                            $loop_id: String!,
                            $blocking_ktask_id: String!,
                            $blocked_ktask_id: String!
                        ) {
                            orchestration_link_tasks(
                                fgroup_id: $fgroup_id,
                                loop_id: $loop_id,
                                blocking_ktask_id: $blocking_ktask_id,
                                blocked_ktask_id: $blocked_ktask_id
                            )
                        }"""
                    ),
                    variable_values={
                        "fgroup_id": fgroup_id,
                        "loop_id": loop_id,
                        "blocking_ktask_id": blocking_ktask_id,
                        "blocked_ktask_id": blocked_ktask_id,
                    },
                )
                return json.dumps({"linked": bool(r.get("orchestration_link_tasks"))}, indent=2)

            if op == "enqueue_result":
                ktask_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "ktask_id", "")
                if not ktask_id:
                    return "Error: ktask_id is required"
                r = await h.execute(
                    gql.gql(
                        """mutation BossOrchestrationEnqueue($fgroup_id: String!, $loop_id: String!, $ktask_id: String!) {
                            orchestration_enqueue_result(fgroup_id: $fgroup_id, loop_id: $loop_id, ktask_id: $ktask_id)
                        }"""
                    ),
                    variable_values={"fgroup_id": fgroup_id, "loop_id": loop_id, "ktask_id": ktask_id},
                )
                return json.dumps({"enqueued": bool(r.get("orchestration_enqueue_result"))}, indent=2)

            if op == "dequeue_next_review":
                r = await h.execute(
                    gql.gql(
                        """mutation BossOrchestrationDequeue($fgroup_id: String!, $loop_id: String!) {
                            orchestration_dequeue_next_review(fgroup_id: $fgroup_id, loop_id: $loop_id) {
                                ktask_id
                                ktask_title
                                persona_id
                                persona_name
                                ktask_orch_queue_pos
                                ktask_orch_review_decision
                                ktask_orch_queue_active
                                ktask_details
                            }
                        }"""
                    ),
                    variable_values={"fgroup_id": fgroup_id, "loop_id": loop_id},
                )
                return json.dumps(r.get("orchestration_dequeue_next_review", {}), indent=2)

            if op == "review_decide":
                ktask_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "ktask_id", "")
                decision = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "decision", "")
                feedback = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "feedback", "")
                create_rework = bool(ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "create_rework", True))
                if not ktask_id or not decision:
                    return "Error: ktask_id and decision are required"
                r = await h.execute(
                    gql.gql(
                        """mutation BossOrchestrationReview(
                            $fgroup_id: String!,
                            $loop_id: String!,
                            $ktask_id: String!,
                            $decision: String!,
                            $feedback: String!,
                            $create_rework: Boolean!
                        ) {
                            orchestration_review_decide(
                                fgroup_id: $fgroup_id,
                                loop_id: $loop_id,
                                ktask_id: $ktask_id,
                                decision: $decision,
                                feedback: $feedback,
                                create_rework: $create_rework
                            )
                        }"""
                    ),
                    variable_values={
                        "fgroup_id": fgroup_id,
                        "loop_id": loop_id,
                        "ktask_id": ktask_id,
                        "decision": decision,
                        "feedback": feedback,
                        "create_rework": create_rework,
                    },
                )
                return json.dumps({"rework_task_id": r.get("orchestration_review_decide", "")}, indent=2)

            return f"Error: Unknown op {op}\n\n{ORCHESTRATION_HELP}"

        except gql.transport.exceptions.TransportQueryError as e:
            return f"GraphQL Error: {e}"


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

    @rcx.on_tool_call(BOSS_ORCHESTRATION_TOOL.name)
    async def toolcall_orchestration(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        _ = toolcall
        return await handle_orchestration_control(fclient, rcx, model_produced_args)

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
