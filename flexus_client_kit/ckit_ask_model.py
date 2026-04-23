import time
import json
import random
import re
from dataclasses import dataclass
from typing import Optional, Any, List, Union, Dict

import gql

from flexus_client_kit import ckit_expert, ckit_client


def openai_style_cloudtools(cloudtools: List[ckit_expert.FCloudTool]):
    result = []
    for t in cloudtools:
        result.append({
            "type": "function",
            "function": {
                "name": t.ctool_name,
                "description": t.ctool_description,
                "parameters": t.ctool_parameters
            }
        })
    return result


@dataclass
class FThreadMessageOutput:
    ftm_belongs_to_ft_id: str
    ftm_role: str
    ftm_content: Any
    ftm_num: int
    ftm_alt: int
    ftm_prev_alt: int
    ftm_usage: Any
    ftm_tool_calls: Any
    ftm_call_id: str
    ftm_author_label1: str
    ftm_app_specific: Any
    ftm_created_ts: float
    ftm_provenance: Any
    ft_app_capture: Optional[str] = None
    ft_app_searchable: Optional[str] = None
    ft_app_specific: Any = None


@dataclass
class FThreadOutput:
    owner_fuser_id: str
    ft_id: str
    ft_fexp_id: str
    ft_title: str
    ft_btest_name: str
    ft_toolset: Any
    ft_error: Any
    ft_need_assistant: int
    ft_need_tool_calls: int
    ft_need_user: int
    ft_app_capture: str
    ft_app_searchable: str
    ft_app_specific: Any
    ft_persona_id: Optional[str]
    ft_created_ts: float
    ft_updated_ts: float
    ft_budget: int
    ft_coins: int


@dataclass
class FThreadComprehensiveSubs:
    news_action: str
    news_payload_id: str
    news_payload_thread_message: Optional[FThreadMessageOutput]
    news_payload_thread: Optional[FThreadOutput]


@dataclass
class FThreadMessageInput:
    content: Union[str, List[Dict[str, Any]]]
    ftm_author_label1: str
    ftm_author_label2: str
    ftm_provenance: Dict[str, Any]
    ftm_alt: int = 100
    role: str = "user"


async def thread_add_user_messages(
    http: gql.Client,
    ft_id: str,
    messages: List[FThreadMessageInput],
    who_is_asking: str,
) -> None:
    if not messages:
        return
    records = []
    for m in messages:
        assert m.role in ["user", "cd_instruction"]
        records.append({
            "ftm_belongs_to_ft_id": ft_id,
            "ftm_alt": m.ftm_alt,
            "ftm_num": -random.randint(1, 2**31 - 1),
            "ftm_prev_alt": m.ftm_alt,
            "ftm_role": m.role,
            "ftm_author_label1": m.ftm_author_label1,
            "ftm_author_label2": m.ftm_author_label2,
            "ftm_content": json.dumps(m.content),
            "ftm_tool_calls": "null",
            "ftm_call_id": "",
            "ftm_usage": "null",
            "ftm_app_specific": "null",
            "ftm_user_preferences": "null",
            "ftm_provenance": json.dumps(m.ftm_provenance),
        })
    async with http as h:
        await h.execute(
            gql.gql(f"""mutation {who_is_asking}CreateMessages($input: FThreadMultipleMessagesInput!) {{
                thread_messages_create_multiple(input: $input)
            }}"""),
            variable_values={"input": {"ftm_belongs_to_ft_id": ft_id, "messages": records}},
        )


async def bot_activate(
    http: gql.Client,
    who_is_asking: str,
    persona_id: str,
    fexp_name: str,
    first_question: Any,  # string or [{"m_type": "...", "m_content": "..."}]
    first_calls: Any = None,
    title: str = "",
    sched_id: str = "",
    fexp_id: str = "",
    ft_btest_name: str = "",
    model: str = "",
    assign_ktask_id: str = "",
    check_kanban_status: bool = False,
    scenario_initial_cd_instruction: str = "",
    scenario_fake_connected_providers: Optional[List[str]] = None,
) -> str:
    title = title or (fexp_name + " " + time.strftime("%Y%m%d %H:%M:%S"))
    assert re.match(r'^[a-z0-9_]+$', who_is_asking)
    camel_case_for_logs = "".join(word.capitalize() for word in who_is_asking.split("_"))
    async with http as h:
        r = await h.execute(
            gql.gql(f"""mutation {camel_case_for_logs}BotActivate($who_is_asking: String!, $persona_id: String!, $fexp_name: String!, $first_question: String!, $first_calls: String!, $title: String!, $sched_id: String!, $fexp_id: String!, $ft_btest_name: String!, $model: String!, $assign_ktask_id: String!, $check_kanban_status: Boolean!, $scenario_initial_cd_instruction: String!, $scenario_fake_connected_providers: [String!]) {{
                bot_activate(who_is_asking: $who_is_asking, persona_id: $persona_id, fexp_name: $fexp_name, first_question: $first_question, first_calls: $first_calls, title: $title, sched_id: $sched_id, fexp_id: $fexp_id, ft_btest_name: $ft_btest_name, model: $model, assign_ktask_id: $assign_ktask_id, check_kanban_status: $check_kanban_status, scenario_initial_cd_instruction: $scenario_initial_cd_instruction, scenario_fake_connected_providers: $scenario_fake_connected_providers) {{ ft_id }}
            }}"""),
            variable_values={
                "who_is_asking": who_is_asking,
                "persona_id": persona_id,
                "fexp_name": fexp_name,
                "first_question": json.dumps(first_question),
                "first_calls": json.dumps(first_calls),
                "title": title,
                "sched_id": sched_id,
                "fexp_id": fexp_id,
                "ft_btest_name": ft_btest_name,
                "model": model,
                "assign_ktask_id": assign_ktask_id,
                "check_kanban_status": check_kanban_status,
                "scenario_initial_cd_instruction": scenario_initial_cd_instruction,
                "scenario_fake_connected_providers": scenario_fake_connected_providers,
            },
        )
        ft_id = r["bot_activate"]["ft_id"]
    return ft_id


async def bot_subchat_create_multiple(
    client: ckit_client.FlexusClient,
    who_is_asking: str,
    persona_id: str,
    first_question: List[str],
    first_calls: List[str],
    title: List[str],
    fcall_id: str,
    fexp_name: str,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    model: str = "",
) -> List[str]:
    assert re.match(r'^[a-z0-9_]+$', who_is_asking)
    camel_case_for_logs = "".join(word.capitalize() for word in who_is_asking.split("_"))
    http = await client.use_http_on_behalf(persona_id, "")
    async with http as h:
        result = await h.execute(
            gql.gql(f"""mutation {camel_case_for_logs}BotSubchatCreateMultiple($who_is_asking: String!, $persona_id: String!, $first_question: [String!]!, $first_calls: [String!]!, $title: [String!]!, $fcall_id: String!, $fexp_name: String!, $max_tokens: Int, $temperature: Float, $model: String) {{
                bot_subchat_create_multiple(who_is_asking: $who_is_asking, persona_id: $persona_id, first_question: $first_question, first_calls: $first_calls, title: $title, fcall_id: $fcall_id, fexp_name: $fexp_name, max_tokens: $max_tokens, temperature: $temperature, model: $model)
            }}"""),
            variable_values={
                "who_is_asking": who_is_asking,
                "persona_id": persona_id,
                "first_question": [json.dumps(q) for q in first_question],
                "first_calls": first_calls,
                "title": title,
                "fcall_id": fcall_id,
                "fexp_name": fexp_name,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "model": model,
            },
        )
        return result["bot_subchat_create_multiple"]



async def thread_app_capture_patch(
    http: gql.Client,
    ft_id: str,
    ft_app_searchable: Optional[str] = None,
    ft_app_specific: Optional[str] = None,
) -> bool:
    assert isinstance(ft_app_specific, str) or ft_app_specific is None
    async with http as http_sess:
        r = await http_sess.execute(gql.gql("""
            mutation ThreadAppCapturePatch($ft_id: String!, $ft_app_searchable: String, $ft_app_specific: String) {
                thread_app_capture_patch(ft_id: $ft_id, ft_app_searchable: $ft_app_searchable, ft_app_specific: $ft_app_specific)
            }"""),
            variable_values={
                "ft_id": ft_id,
                "ft_app_searchable": ft_app_searchable,
                "ft_app_specific": ft_app_specific,
            },
        )
    return r["thread_app_capture_patch"]


@dataclass
class CapturedMessageInput:
    content: Union[str, List[Dict[str, Any]]]
    ftm_author_label1: str
    ftm_author_label2: str
    dedup_key: str
    provenance_generated_by_module: str


async def captured_thread_post_group_messages(
    http: gql.Client,
    persona_id: str,
    ft_app_searchable: str,
    messages: List[CapturedMessageInput],
    only_to_expert: str,
    thread_too_old_s: Optional[float] = None,
) -> str:
    records = [{
        "ftm_content": json.dumps(m.content),
        "ftm_author_label1": m.ftm_author_label1,
        "ftm_author_label2": m.ftm_author_label2,
        "dedup_key": m.dedup_key,
        "provenance_generated_by_module": m.provenance_generated_by_module,
    } for m in messages]
    async with http as h:
        r = await h.execute(gql.gql("""
            mutation CapturedThreadPostGroup($persona_id: String!, $ft_app_searchable: String!, $messages: [CapturedThreadMessageInput!]!, $only_to_expert: String!, $thread_too_old_s: Float) {
                captured_thread_post_group_messages(persona_id: $persona_id, ft_app_searchable: $ft_app_searchable, messages: $messages, only_to_expert: $only_to_expert, thread_too_old_s: $thread_too_old_s)
            }"""),
            variable_values={
                "persona_id": persona_id,
                "ft_app_searchable": ft_app_searchable,
                "messages": records,
                "only_to_expert": only_to_expert,
                "thread_too_old_s": thread_too_old_s,
            },
        )
    return r["captured_thread_post_group_messages"]


async def captured_thread_lookup(
    http: gql.Client,
    persona_id: str,
    ft_app_searchable: str,
) -> str:
    async with http as h:
        r = await h.execute(gql.gql("""
            query CapturedThreadLookup($persona_id: String!, $ft_app_searchable: String!) {
                captured_thread_lookup(persona_id: $persona_id, ft_app_searchable: $ft_app_searchable)
            }"""),
            variable_values={
                "persona_id": persona_id,
                "ft_app_searchable": ft_app_searchable,
            },
        )
    return r["captured_thread_lookup"]
