from typing import Dict, Any

import gql

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool


THREAD_MESSAGES_PRINTED_TOOL = ckit_cloudtool.CloudTool(
    name="thread_messages_printed",
    description="Print thread messages. Provide either a2a_task_id to view the thread that handed over this task, or ft_id to view thread directly",
    parameters={
        "type": "object",
        "properties": {
            "a2a_task_id": {
                "type": "string",
                "description": "A2A task ID to view the thread that handed over this task"
            },
            "ft_id": {
                "type": "string",
                "description": "Thread ID to view messages directly"
            }
        },
    },
)


async def handle_thread_messages_printed(
    fclient: ckit_client.FlexusClient,
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
) -> str:
    a2a_task_id = args.get("a2a_task_id") or None
    ft_id = args.get("ft_id") or None
    if not a2a_task_id and not ft_id:
        return "Error: Either a2a_task_id or ft_id is required"
    http = await fclient.use_http()
    async with http as h:
        try:
            r = await h.execute(gql.gql("""
                query BossThreadMessagesPrinted($a2a_task_id: String, $ft_id: String) {
                    thread_messages_printed(a2a_task_id_to_resolve: $a2a_task_id, ft_id: $ft_id) {
                        thread_messages_data
                    }
                }"""),
                variable_values={"a2a_task_id": a2a_task_id, "ft_id": ft_id},
            )
            if not (messages_data := r.get("thread_messages_printed", {}).get("thread_messages_data")):
                return f"Error: No messages found for {'a2a_task_id=' + a2a_task_id if a2a_task_id else 'ft_id=' + ft_id}"
            return messages_data
        except gql.transport.exceptions.TransportQueryError as e:
            return f"GraphQL Error: {str(e)}"
