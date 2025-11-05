from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict

import gql

from flexus_client_kit import ckit_client, gql_utils, ckit_shutdown, ckit_cloudtool, ckit_ask_model


@dataclass
class FPersonaOutput:
    owner_fuser_id: str
    located_fgroup_id: str
    persona_id: str
    persona_name: str
    persona_marketable_name: str
    persona_marketable_version: int
    persona_discounts: Any
    persona_setup: Any
    persona_created_ts: float
    persona_keepalive_ts: float
    persona_preferred_model: str
    ws_id: str
    ws_timezone: str
    marketable_run_this: Optional[str] = None
    marketable_stage: Optional[str] = None


@dataclass
class FPersonaScheduleOutput:
    sched_id: str
    sched_persona_id: str
    sched_type: str
    sched_when: str
    sched_first_question: str


@dataclass
class FBotThreadsAndCallsSubs:
    news_action: str
    news_about: str
    news_payload_id: str
    news_payload_thread_message: Optional[ckit_ask_model.FThreadMessageOutput]
    news_payload_thread: Optional[ckit_ask_model.FThreadOutput]
    news_payload_persona: Optional[FPersonaOutput]
    news_payload_toolcall: Optional[ckit_cloudtool.FCloudtoolCall]


@dataclass
class FThreadWithMessages:
    persona_id: str
    thread_fields: ckit_ask_model.FThreadOutput
    thread_messages: Dict[str, ckit_ask_model.FThreadMessageOutput] = field(default_factory=dict)
    message_count_at_initial_updates_over: int = 0


async def persona_get(fclient: ckit_client.FlexusClient, persona_id: str) -> FPersonaOutput:
    async with (await fclient.use_http()) as http:
        r = await http.execute(gql.gql(f"""
            query PersonaGet($id: String!) {{
                persona_get(id: $id) {{
                    {gql_utils.gql_fields(FPersonaOutput)}
                }}
            }}"""), variable_values={"id": persona_id})
    return gql_utils.dataclass_from_dict(r["persona_get"], FPersonaOutput)


async def persona_list(fclient: ckit_client.FlexusClient, fgroup_id: str) -> List[FPersonaOutput]:
    async with (await fclient.use_http()) as http:
        r = await http.execute(gql.gql(f"""
            query PersonaList($fgroup_id: String!) {{
                persona_list(located_fgroup_id: $fgroup_id, skip: 0, limit: 100) {{
                    {gql_utils.gql_fields(FPersonaOutput)}
                }}
            }}"""), variable_values={"fgroup_id": fgroup_id})
    return [gql_utils.dataclass_from_dict(p, FPersonaOutput) for p in r["persona_list"]]


async def persona_schedule_list(fclient: ckit_client.FlexusClient, persona_id: str) -> List[FPersonaScheduleOutput]:
    async with (await fclient.use_http()) as http:
        r = await http.execute(gql.gql(f"""
            query GetPersonaSchedule($persona_id: String!) {{
                persona_schedule_list(persona_id: $persona_id) {{
                    scheds {{ {gql_utils.gql_fields(FPersonaScheduleOutput)} }}
                }}
            }}"""), variable_values={"persona_id": persona_id})
    return [gql_utils.dataclass_from_dict(s, FPersonaScheduleOutput) for s in r["persona_schedule_list"]["scheds"]]


async def personas_in_ws_list(fclient: ckit_client.FlexusClient, ws_id: str) -> List[FPersonaOutput]:
    async with (await fclient.use_http()) as http:
        r = await http.execute(gql.gql(f"""
            query PersonasInWsList($ws_id: String!) {{
                workspace_personas_list(ws_id: $ws_id, active_only: true) {{
                    personas {{ {gql_utils.gql_fields(FPersonaOutput)} }}
                }}
            }}"""), variable_values={"ws_id": ws_id})
    if not r or not r.get("workspace_personas_list"):
        return []
    return [gql_utils.dataclass_from_dict(p, FPersonaOutput) for p in r["workspace_personas_list"]["personas"] if p.get("marketable_run_this")]


async def wait_until_bot_threads_stop(
    client: ckit_client.FlexusClient,
    persona: FPersonaOutput,
    inprocess_tools: List[ckit_cloudtool.CloudTool],
    only_ft_id: Optional[str] = None,
    timeout: int = 600,
) -> Dict[str, FThreadWithMessages]:
    initial_updates_over = False
    threads_data: Dict[str, FThreadWithMessages] = {}

    ws_client = await client.use_ws()
    async with ws_client as ws:
        async for r in ws.subscribe(
            gql.gql(f"""subscription BotThreadsStop($fgroup_id: String!, $marketable_name: String!, $marketable_version: Int!, $inprocess_tool_names: [String!]!) {{
                bot_threads_and_calls_subs(fgroup_id: $fgroup_id, marketable_name: $marketable_name, marketable_version: $marketable_version, inprocess_tool_names: $inprocess_tool_names, max_threads: 100, want_personas: false, want_threads: true, want_messages: true) {{
                    {gql_utils.gql_fields(FBotThreadsAndCallsSubs)}
                }}
            }}"""),
            variable_values={
                "fgroup_id": persona.located_fgroup_id,
                "marketable_name": persona.persona_marketable_name,
                "marketable_version": persona.persona_marketable_version,
                "inprocess_tool_names": [t.name for t in inprocess_tools],
            },
        ):
            if ckit_shutdown.shutdown_event.is_set():
                break
            upd = gql_utils.dataclass_from_dict(r["bot_threads_and_calls_subs"], FBotThreadsAndCallsSubs)

            if upd.news_action == "INITIAL_UPDATES_OVER":
                for thread_data in threads_data.values():
                    thread_data.message_count_at_initial_updates_over = len(thread_data.thread_messages)
                initial_updates_over = True

            if (ft := upd.news_payload_thread) and (only_ft_id is None or ft.ft_id == only_ft_id):
                threads_data[ft.ft_id] = threads_data.get(ft.ft_id, FThreadWithMessages(ft.ft_persona_id, ft, thread_messages=dict()))
                threads_data[ft.ft_id].thread_fields = ft

            if (msg := upd.news_payload_thread_message) and (only_ft_id is None or msg.ftm_belongs_to_ft_id == only_ft_id):
                threads_data[msg.ftm_belongs_to_ft_id].thread_messages[f"{msg.ftm_alt:03d}_{msg.ftm_num:03d}"] = msg

            if initial_updates_over and threads_data and all(threads_data[tid].thread_fields.ft_need_user >= 0 for tid in threads_data):
                return threads_data

    raise RuntimeError(f"Timeout waiting for threads to stop after {timeout} seconds")
