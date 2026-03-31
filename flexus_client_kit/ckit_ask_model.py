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


async def thread_add_user_message(
    http: gql.Client,
    ft_id: str,
    content: Union[str, List[Dict[str, Any]]],
    who_is_asking: str,
    ftm_alt: int,
    user_preferences: str = "null",
    role: str = "user",
    ftm_provenance: Optional[Dict[str, Any]] = None,
) -> None:
    random_ftm_num = -random.randint(1, 2**31 - 1)
    assert role in ["user", "cd_instruction"]

    if isinstance(content, str):
        ftm_content = json.dumps(content)
    elif isinstance(content, list):
        ftm_content = json.dumps(content)
    else:
        assert 0, "bad type %s" % type(content)

    if ftm_provenance is None:
        ftm_provenance = {"system_type": who_is_asking}

    async with http as h:
        await h.execute(
            gql.gql(f"""mutation {who_is_asking}CreateMessages($input: FThreadMultipleMessagesInput!) {{
                thread_messages_create_multiple(input: $input)
            }}"""),
            variable_values={
                "input": {
                    "ftm_belongs_to_ft_id": ft_id,
                    "messages": [
                        {
                            "ftm_belongs_to_ft_id": ft_id,
                            "ftm_alt": ftm_alt,
                            "ftm_num": random_ftm_num,
                            "ftm_prev_alt": ftm_alt,
                            "ftm_role": role,
                            "ftm_content": ftm_content,
                            "ftm_tool_calls": "null",
                            "ftm_call_id": "",
                            "ftm_usage": "null",
                            "ftm_app_specific": "null",
                            "ftm_user_preferences": user_preferences,
                            "ftm_provenance": json.dumps(ftm_provenance),
                        },
                    ],
                }
            },
        )


async def bot_activate(
    client: ckit_client.FlexusClient,
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
) -> str:
    title = title or (fexp_name + " " + time.strftime("%Y%m%d %H:%M:%S"))
    assert re.match(r'^[a-z0-9_]+$', who_is_asking)
    camel_case_for_logs = "".join(word.capitalize() for word in who_is_asking.split("_"))
    http = await client.use_http_on_behalf(persona_id, "")
    async with http as h:
        r = await h.execute(
            gql.gql(f"""mutation {camel_case_for_logs}BotActivate($who_is_asking: String!, $persona_id: String!, $fexp_name: String!, $first_question: String!, $first_calls: String!, $title: String!, $sched_id: String!, $fexp_id: String!, $ft_btest_name: String!, $model: String!, $assign_ktask_id: String!, $check_kanban_status: Boolean!) {{
                bot_activate(who_is_asking: $who_is_asking, persona_id: $persona_id, fexp_name: $fexp_name, first_question: $first_question, first_calls: $first_calls, title: $title, sched_id: $sched_id, fexp_id: $fexp_id, ft_btest_name: $ft_btest_name, model: $model, assign_ktask_id: $assign_ktask_id, check_kanban_status: $check_kanban_status) {{ ft_id }}
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


async def captured_thread_post_user_message(
    http: gql.Client,
    persona_id: str,
    ft_app_searchable: str,
    content: Union[str, List[Dict[str, Any]]],
    only_to_expert: str = "",
    ftm_provenance: Optional[Dict[str, Any]] = None,
) -> str:
    async with http as h:
        r = await h.execute(gql.gql("""
            mutation CapturedThreadPostSafe($persona_id: String!, $ft_app_searchable: String!, $ftm_content: String!, $only_to_expert: String!, $ftm_provenance: String) {
                captured_thread_post_user_message(persona_id: $persona_id, ft_app_searchable: $ft_app_searchable, ftm_content: $ftm_content, only_to_expert: $only_to_expert, ftm_provenance: $ftm_provenance)
            }"""),
            variable_values={
                "persona_id": persona_id,
                "ft_app_searchable": ft_app_searchable,
                "ftm_content": json.dumps(content),
                "ftm_provenance": json.dumps(ftm_provenance) if ftm_provenance else None,
                "only_to_expert": only_to_expert,
            },
        )
    return r["captured_thread_post_user_message"]


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
