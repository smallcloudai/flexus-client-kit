from typing import Any, Dict

import gql

from flexus_client_kit import ckit_ask_model, ckit_bot_exec, ckit_cloudtool, ckit_messages, ckit_scenario, gql_utils


THREAD_READ_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="thread_read",
    description="Read the message transcript of a Flexus thread by its ft_id. Returns a YAML dump of user/assistant/tool messages (system messages excluded).",
    parameters={
        "type": "object",
        "properties": {
            "ft_id": {"type": "string", "description": "Thread ID (ft_id) of the Flexus thread to read."},
        },
        "required": ["ft_id"],
        "additionalProperties": False,
    },
)


async def handle_thread_read(
    rcx: ckit_bot_exec.RobotContext,
    toolcall: ckit_cloudtool.FCloudtoolCall,
    model_produced_args: Dict[str, Any],
) -> str:
    if rcx.running_test_scenario:
        return await ckit_scenario.scenario_generate_tool_result_via_model(rcx.fclient, toolcall, "")
    ft_id = model_produced_args["ft_id"]
    http = await rcx.fclient.use_http_on_behalf(rcx.persona.persona_id, "")
    r = await http.execute_async(gql.gql(f"""
        query ThreadReadTranscript($ft_id: String!) {{
            thread_messages_list(ft_id: $ft_id) {{ {gql_utils.gql_fields(ckit_ask_model.FThreadMessageOutput)} }}
        }}"""),
        variable_values={"ft_id": ft_id},
    )
    msgs = [gql_utils.dataclass_from_dict(m, ckit_ask_model.FThreadMessageOutput) for m in r["thread_messages_list"]]
    msgs = [m for m in msgs if m.ftm_role != "system"]
    return ckit_messages.fmessages_to_yaml(msgs, limits={"assistant": 5000, "tool": 1000, "tool_args": 300})
