import json
from dataclasses import dataclass
import dataclasses
from typing import List, Tuple, Optional, Any

import gql

from flexus_client_kit import ckit_client, gql_utils


@dataclass
class FKanbanTaskInput:
    title: str
    state: str
    details_json: Optional[str] = None


@dataclass
class FPersonaKanbanTaskOutput:
    persona_id: str
    ktask_id: str
    ktask_title: str
    ktask_skill: str
    ktask_inbox_ts: float
    ktask_inbox_provenance: Any
    ktask_daily_timekey: str
    ktask_coins: int
    ktask_budget: int
    ktask_todo_ts: float
    ktask_inprogress_ts: float
    ktask_inprogress_ft_id: Optional[str]
    ktask_inprogress_activity_ts: float
    ktask_done_ts: float
    ktask_resolution_code: Optional[str]
    ktask_resolution_summary: Optional[str]
    ktask_details: Any
    ktask_blocks_ktask_id: Optional[str]

    def calc_bucket(self) -> str:
        if self.ktask_done_ts > 0:
            return 'done'
        if self.ktask_inprogress_ts > 0:
            return 'inprogress'
        if self.ktask_todo_ts > 0:
            return 'todo'
        return 'inbox'


@dataclass
class FPersonaKanbanSubs:
    news_action: str
    news_payload_id: str
    news_payload_task: Optional[FPersonaKanbanTaskOutput]


async def bot_arrange_kanban_situation(
    client: ckit_client.FlexusClient,
    ws_id: str,
    persona_id: str,
    tasks: List[FKanbanTaskInput],
) -> None:
    http = await client.use_http()
    async with http as h:
        await h.execute(
            gql.gql(
                """mutation ArrangeKanban($ws: String!, $pid: String!, $tasks: [FKanbanTaskInput!]!) {
                    bot_arrange_kanban_situation(ws_id: $ws, persona_id: $pid, tasks: $tasks)
                }""",
            ),
            variable_values={
                "ws": ws_id,
                "pid": persona_id,
                "tasks": [dataclasses.asdict(task) for task in tasks],
            },
        )


async def persona_kanban_list(
    client: ckit_client.FlexusClient,
    persona_id: str,
) -> List[FPersonaKanbanTaskOutput]:
    tasks = {}
    ws_client = await client.use_ws()
    async with ws_client as ws:
        async for r in ws.subscribe(
            gql.gql(f"""subscription PersonaKanban($persona_id: String!) {{
                persona_kanban_subs(persona_id: $persona_id, limit_inbox: 100, limit_done: 100) {{
                    news_action
                    news_payload_id
                    news_payload_task {{ {gql_utils.gql_fields(FPersonaKanbanTaskOutput)} }}
                }}
            }}"""),
            variable_values={"persona_id": persona_id}
        ):
            upd = r["persona_kanban_subs"]
            if upd["news_action"] == "INITIAL_UPDATES_OVER":
                break
            if upd["news_payload_task"]:
                task = gql_utils.dataclass_from_dict(upd["news_payload_task"], FPersonaKanbanTaskOutput)
                tasks[upd["news_payload_id"]] = task

    bucket_order = {"inbox": 0, "todo": 1, "inprogress": 2, "done": 3}
    return sorted(tasks.values(), key=lambda t: bucket_order.get(t.calc_bucket(), 4))


async def bot_arrange_kanban_situation2(
    client: ckit_client.FlexusClient,
    ws_id: str,
    persona_id: str,
    tasks: List[Tuple],
) -> None:
    http = await client.use_http()
    tasks_dicts = []
    for task in tasks:
        details = {"fulltext": task[1]}
        tasks_dicts.append({
            "state": task[0],
            "title": task[1][:100],
            "details_json": json.dumps({**details, **task[2]} if len(task) > 2 else details),
        })

    async with http as h:
        await h.execute(
            gql.gql(
                """mutation ArrangeKanban($ws: String!, $pid: String!, $tasks: [FKanbanTaskInput!]!) {
                    bot_arrange_kanban_situation(ws_id: $ws, persona_id: $pid, tasks: $tasks)
                }""",
            ),
            variable_values={
                "ws": ws_id,
                "pid": persona_id,
                "tasks": tasks_dicts,
            },
        )


async def bot_kanban_post_into_inbox(
    client: ckit_client.FlexusClient,
    persona_id: str,
    title: str,
    details_json: str,
    provenance_message: str,
) -> None:
    http = await client.use_http()
    async with http as h:
        await h.execute(
            gql.gql(
                """mutation KanbanInbox($pid: String!, $title: String!, $details: String!, $prov: String!) {
                    bot_kanban_post_into_inbox(persona_id: $pid, title: $title, details_json: $details, provenance_message: $prov)
                }""",
            ),
            variable_values={
                "pid": persona_id,
                "title": title,
                "details": details_json,
                "prov": provenance_message,
            },
        )


# XXX remove
async def get_tasks_by_thread(
    client: ckit_client.FlexusClient,
    ft_id: str,
) -> List[FPersonaKanbanTaskOutput]:
    http = await client.use_http()
    async with http as h:
        result = await h.execute(
            gql.gql("""query GetTasksForThread($ft_id: String!) {
                persona_kanban_tasks_by_thread(ft_id: $ft_id) {
                    persona_id
                    ktask_id
                    ktask_title
                    ktask_skill
                    ktask_inbox_ts
                    ktask_inbox_provenance
                    ktask_daily_timekey
                    ktask_coins
                    ktask_budget
                    ktask_todo_ts
                    ktask_inprogress_ts
                    ktask_inprogress_ft_id
                    ktask_inprogress_activity_ts
                    ktask_done_ts
                    ktask_resolution_code
                    ktask_resolution_summary
                    ktask_details
                    ktask_blocks_ktask_id
                }
            }"""),
            variable_values={"ft_id": ft_id}
        )

    tasks = []
    for task_data in result.get("persona_kanban_tasks_by_thread", []):
        tasks.append(gql_utils.dataclass_from_dict(task_data, FPersonaKanbanTaskOutput))
    return tasks


async def update_task_details(
    client: ckit_client.FlexusClient,
    ktask_id: str,
    details: dict,
) -> bool:
    http = await client.use_http()
    async with http as h:
        result = await h.execute(
            gql.gql("""mutation UpdateTaskDetails($ktask_id: String!, $details: String!) {
                kanban_task_update_details(ktask_id: $ktask_id, ktask_details: $details)
            }"""),
            variable_values={
                "ktask_id": ktask_id,
                "details": json.dumps(details) if isinstance(details, dict) else details
            }
        )
    return result.get("kanban_task_update_details", False)
