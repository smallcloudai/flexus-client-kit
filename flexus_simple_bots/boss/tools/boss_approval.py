import json
import logging
from typing import Dict, Any

from flexus_client_kit import ckit_client, ckit_cloudtool, ckit_kanban

logger = logging.getLogger("boss.approval")


BOSS_APPROVE_TASK_TOOL = ckit_cloudtool.CloudTool(
    name="boss_approve_task",
    description="Approve a task from a colleague bot, optionally with modifications",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The ID of the task to approve"
            },
            "modification": {
                "type": "string",
                "description": "Optional modifications or instructions to add to the approved task"
            }
        },
        "required": ["task_id"]
    },
)

BOSS_REJECT_TASK_TOOL = ckit_cloudtool.CloudTool(
    name="boss_reject_task",
    description="Reject a task from a colleague bot with a reason",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The ID of the task to reject"
            },
            "reason": {
                "type": "string",
                "description": "Reason for rejecting the task"
            }
        },
        "required": ["task_id", "reason"]
    },
)


async def handle_approve_task(
    fclient: ckit_client.FlexusClient,
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
) -> str:
    if not (task_id := args.get("task_id")):
        return "Error: task_id is required"
    modification = args.get("modification", "")

    if not (task := await ckit_kanban.bot_kanban_get_task(client=fclient, ktask_id=task_id)):
        return f"Error: Task {task_id} not found"
    if task.ktask_done_ts > 0:
        return f"Error: Task {task_id} is already done"

    details = task.ktask_details
    from_bot_name = details.get("handed_over_from_bot_name", "")
    from_bot_title2 = details.get("handed_over_from_bot_title2", "")
    target_bot_persona_id = details.get("handed_over_to_persona_id", "")
    description = details.get("description", "")

    if not target_bot_persona_id:
        return f"Error: No target bot persona_id in task {task_id}"

    await ckit_kanban.bot_kanban_post_into_inbox(
        client=fclient,
        persona_id=target_bot_persona_id,
        title=task.ktask_title or description[:100],
        details_json=json.dumps({
            "from_bot": f"{from_bot_name} ({from_bot_title2})" if from_bot_title2 else from_bot_name,
            "description": f"{description}\n\nBoss modification: {modification}" if modification else description,
            "task_type": details.get("task_type", ""),
        }),
    )

    summary = f"Task approved and forwarded to {target_bot_persona_id}"
    await ckit_kanban.bot_kanban_mark_done(
        client=fclient,
        ktask_id=task_id,
        resolution_code="KTASK_SUCCESS",
        resolution_summary=summary,
    )

    logger.info(f"Approved {task_id}: {from_bot_name} → {target_bot_persona_id}")
    return f"Task approved and forwarded to {target_bot_persona_id}, task assigned to this chat successfully marked as done"


async def handle_reject_task(
    fclient: ckit_client.FlexusClient,
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
) -> str:
    if not (task_id := args.get("task_id")):
        return "Error: task_id is required"
    if not (reason := args.get("reason")):
        return "Error: reason is required"

    if not (task := await ckit_kanban.bot_kanban_get_task(client=fclient, ktask_id=task_id)):
        return f"Error: Task {task_id} not found"
    if task.ktask_done_ts > 0:
        return f"Error: Task {task_id} is already done"

    await ckit_kanban.bot_kanban_mark_done(
        client=fclient,
        ktask_id=task_id,
        resolution_code="KTASK_IRRELEVANT",
        resolution_summary=reason,
    )

    return f"Task {task_id} was rejected, task assigned to this chat finished as irrelevant"
