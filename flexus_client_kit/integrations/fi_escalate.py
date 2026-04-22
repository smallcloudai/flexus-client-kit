from typing import Any, Dict

import gql

from flexus_client_kit import ckit_bot_exec, ckit_cloudtool


ESCALATE_TO_HUMAN_PROMPT = """
## Escalation to Human

Before escalating to a human, confirm with the client that they will wait for a human to respond.
NEVER call escalate_to_human without doing so.

After calling escalate_to_human, staff is being notified. Once staff speaks in the thread,
say NOTHING_TO_SAY while they and the client talk. Resume if staff asks.

If staff hasn't arrived and the client keeps writing, a brief calming reply is fine —
but don't promise anything or handle what was escalated.

Don't resolve an escalated task until staff has handled it or tells you to.
""".strip()


ESCALATE_TO_HUMAN_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="escalate_to_human",
    description=(
        "Hand off the current thread to a human operator. Call this when the user explicitly asks for a human, "
        "on legal/fraud/compliance mentions, obvious frustration, or any situation beyond your authority. "
        "Before calling, confirm with the client that they will wait for a human to respond."
    ),
    parameters={
        "type": "object",
        "properties": {
            "reason": {
                "type": "string",
                "description": "Short explanation of why a human is needed (one sentence).",
            },
        },
        "required": ["reason"],
        "additionalProperties": False,
    },
)


async def handle_escalate_to_human(
    rcx: ckit_bot_exec.RobotContext,
    toolcall: ckit_cloudtool.FCloudtoolCall,
    model_produced_args: Dict[str, Any],
) -> str:
    reason = (model_produced_args.get("reason") or "").strip()
    if not reason:
        return "Error: reason is required"
    ktask_id = next((t.ktask_id for t in rcx.latest_tasks.values() if t.ktask_inprogress_ft_id == toolcall.fcall_ft_id), None)
    if not ktask_id:
        return "No task assigned to this thread — escalate_to_human only works within a task context."
    http = await rcx.fclient.use_http_on_behalf(toolcall.connected_persona_id, toolcall.fcall_untrusted_key)
    async with http as h:
        await h.execute(gql.gql("""
            mutation BotRequestHumanEscalation($ktask_id: String!, $status: String!, $reason: String) {
                kanban_task_update_escalation_status(ktask_id: $ktask_id, ktask_escalation_status: $status, ktask_escalation_reason: $reason)
            }"""),
            variable_values={"ktask_id": ktask_id, "status": "ESCALATION_REQUESTED", "reason": reason},
        )
    return "⏸️ESCALATED_TO_HUMAN\nReason: %s\nA human operator has been requested. Stop acting on this thread." % reason
