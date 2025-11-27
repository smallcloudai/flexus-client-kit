from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict

import gql

from flexus_client_kit import ckit_client, gql_utils, ckit_kanban, ckit_shutdown, ckit_cloudtool, ckit_ask_model


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
    ws_root_group_id: str
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
class FBotThreadsCallsTasks:
    news_action: str
    news_about: str
    news_payload_id: str
    news_payload_thread_message: Optional[ckit_ask_model.FThreadMessageOutput]
    news_payload_thread: Optional[ckit_ask_model.FThreadOutput]
    news_payload_persona: Optional[FPersonaOutput]
    news_payload_toolcall: Optional[ckit_cloudtool.FCloudtoolCall]
    news_payload_task: Optional[ckit_kanban.FPersonaKanbanTaskOutput]
    news_payload_erp_record: Optional[Dict[str, Any]] = None


@dataclass
class FThreadWithMessages:
    persona_id: str
    thread_fields: ckit_ask_model.FThreadOutput
    thread_messages: Dict[str, ckit_ask_model.FThreadMessageOutput] = field(default_factory=dict)
    message_count_at_initial_updates_over: int = 0


async def persona_list(fclient: ckit_client.FlexusClient, fgroup_id: str) -> List[FPersonaOutput]:
    async with (await fclient.use_http()) as http:
        r = await http.execute(gql.gql(f"""
            query PersonaList($fgroup_id: String!) {{
                persona_list(located_fgroup_id: $fgroup_id, skip: 0, limit: 100) {{
                    {gql_utils.gql_fields(FPersonaOutput)}
                }}
            }}"""), variable_values={"fgroup_id": fgroup_id})
    return [gql_utils.dataclass_from_dict(p, FPersonaOutput) for p in r["persona_list"]]


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
