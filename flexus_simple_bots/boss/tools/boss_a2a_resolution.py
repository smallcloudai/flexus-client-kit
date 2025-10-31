from typing import Dict, Any

import gql

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool


BOSS_A2A_RESOLUTION_TOOL = ckit_cloudtool.CloudTool(
    name="boss_a2a_resolution",
    description="Resolve an agent-to-agent handover task: approve, reject, or request rework",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {"type": "string", "description": "The ID of the task to resolve", "order": 1},
            "resolution": {
                "type": "string",
                "enum": ["approve", "reject", "rework"],
                "description": "Resolution type: approve (forward to target bot), reject (mark irrelevant), or rework (send back with feedback)",
                "order": 2
            },
            "comment": {"type": "string", "description": "Optional comment for approve, required for reject/rework", "order": 3}
        },
        "required": ["task_id", "resolution"]
    },
)

BOSS_A2A_RESOLUTION_EXAMPLES = """
Examples:
- boss_a2a_resolution(task_id="abc123", resolution="reject", comment="This is not aligned with our current priorities")
- boss_a2a_resolution(task_id="abc123", resolution="rework", comment="Need more clarity on ROI and timeline")
- boss_a2a_resolution(task_id="abc123", resolution="approve", comment="Approved, but prioritize customer-facing features first")
- boss_a2a_resolution(task_id="abc123", resolution="approve")  # comment is optional for approve"""


async def handle_a2a_resolution(
    fclient: ckit_client.FlexusClient,
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
) -> str:
    task_id = args.get("task_id", "")
    resolution = args.get("resolution", "")
    comment = args.get("comment", "")

    if not task_id:
        return f"Error: task_id is required\n{BOSS_A2A_RESOLUTION_EXAMPLES}"
    if resolution not in ["approve", "reject", "rework"]:
        return f"Error: resolution must be approve, reject, or rework\n{BOSS_A2A_RESOLUTION_EXAMPLES}"
    if resolution in ["reject", "rework"] and not comment:
        return f"Error: comment is required for {resolution}, please provide one with 'comment' parameter\n{BOSS_A2A_RESOLUTION_EXAMPLES}"

    http = await fclient.use_http()
    async with http as h:
        try:
            r = await h.execute(
                gql.gql("""mutation BossA2AResolution($ktask_id: String!, $boss_intent_resolution: String!, $boss_intent_comment: String!) {
                    boss_a2a_resolution(ktask_id: $ktask_id, boss_intent_resolution: $boss_intent_resolution, boss_intent_comment: $boss_intent_comment)
                }"""),
                variable_values={
                    "ktask_id": task_id,
                    "boss_intent_resolution": resolution,
                    "boss_intent_comment": comment,
                },
            )
            if not r or not r.get("boss_a2a_resolution"):
                return f"Error: Failed to {resolution} task {task_id}"
        except gql.transport.exceptions.TransportQueryError as e:
            return f"Error: {str(e)}"

    if resolution == "approve":
        return f"Task {task_id} approved and forwarded"
    elif resolution == "reject":
        return f"Task {task_id} rejected"
    elif resolution == "rework":
        return f"Task {task_id} sent back for rework"
