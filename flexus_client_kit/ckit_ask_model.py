import time
import asyncio
import json
import random
import re
from dataclasses import dataclass
from typing import Optional, Any, List, Callable, Union, Dict

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


async def ask_model(
    client: ckit_client.FlexusClient,
    inside_fgroup_id: str,
    fexp_id: str,
    persona_id: str,
    title: str,
    model: str,
    who_is_asking: str,
    question: str,
    # localtools: Optional[List[Callable]] = None,
    # cloudtools: Optional[List[ckit_expert.FCloudTool]] = None,
    on_behalf_of_fuser_id: Optional[str] = None,
) -> FThreadMessageOutput:
    # if localtools or cloudtools:
    #     combined_toolset = []
    #     if cloudtools:
    #         combined_toolset.extend(openai_style_cloudtools(cloudtools))
    #     if localtools:
    #         combined_toolset.extend([ckit_localtool.openai_style_function_description(f) for f in localtools])
    #     toolset = combined_toolset

    http = await client.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql(f"""mutation {who_is_asking}CreateCapturedThread($input: FThreadInput!, $u: String) {{
                create_captured_thread(input: $input, on_behalf_of_fuser_id: $u) {{ ft_id }}
            }}"""),
            variable_values={
                "input": {
                    "owner_shared": False,
                    "located_fgroup_id": inside_fgroup_id,
                    "ft_fexp_id": fexp_id,
                    "ft_persona_id": persona_id,
                    "ft_title": title,
                    "ft_toolset": "null",
                    "ft_app_capture": "bot",  # XXX fix me service name or something
                },
                "u": on_behalf_of_fuser_id,
            },
        )
        ft_id = r["create_captured_thread"]["ft_id"]
    user_preferences = json.dumps({"model": model, "disable_title_generation": True, "disable_streaming": True})
    ftm_alt = 100
    await thread_add_user_message(http, ft_id, question, who_is_asking, user_preferences)


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
    skill: str,
    first_question: str,
    first_calls: Any = None,
    cd_instruction: str = "",
    title: str = "",
    sched_id: str = "",
    fexp_id: str = "",
    ft_btest_name: str = "",
    model: str = "",
) -> str:
    title = title or (skill + " " + time.strftime("%Y%m%d %H:%M:%S"))
    assert re.match(r'^[a-z0-9_]+$', who_is_asking)
    camel_case_for_logs = "".join(word.capitalize() for word in who_is_asking.split("_"))
    http = await client.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql(f"""mutation {camel_case_for_logs}BotActivate($who_is_asking: String!, $persona_id: String!, $skill: String!, $first_question: String!, $first_calls: String!, $cd_instruction: String!, $title: String!, $sched_id: String!, $fexp_id: String!, $ft_btest_name: String!, $model: String!) {{
                bot_activate(who_is_asking: $who_is_asking, persona_id: $persona_id, skill: $skill, first_question: $first_question, first_calls: $first_calls, cd_instruction: $cd_instruction, title: $title, sched_id: $sched_id, fexp_id: $fexp_id, ft_btest_name: $ft_btest_name, model: $model) {{ ft_id }}
            }}"""),
            variable_values={
                "who_is_asking": who_is_asking,
                "persona_id": persona_id,
                "skill": skill,
                "first_question": first_question,
                "first_calls": json.dumps(first_calls),
                "cd_instruction": cd_instruction,
                "title": title,
                "sched_id": sched_id,
                "fexp_id": fexp_id,
                "ft_btest_name": ft_btest_name,
                "model": model,
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
    skill: str,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    model: str = "",
) -> List[str]:
    assert re.match(r'^[a-z0-9_]+$', who_is_asking)
    camel_case_for_logs = "".join(word.capitalize() for word in who_is_asking.split("_"))
    http = await client.use_http()
    async with http as h:
        result = await h.execute(
            gql.gql(f"""mutation {camel_case_for_logs}BotSubchatCreateMultiple($who_is_asking: String!, $persona_id: String!, $first_question: [String!]!, $first_calls: [String!]!, $title: [String!]!, $fcall_id: String!, $skill: String!, $max_tokens: Int, $temperature: Float, $model: String) {{
                bot_subchat_create_multiple(who_is_asking: $who_is_asking, persona_id: $persona_id, first_question: $first_question, first_calls: $first_calls, title: $title, fcall_id: $fcall_id, skill: $skill, max_tokens: $max_tokens, temperature: $temperature, model: $model)
            }}"""),
            variable_values={
                "who_is_asking": who_is_asking,
                "persona_id": persona_id,
                "first_question": first_question,
                "first_calls": first_calls,
                "title": title,
                "fcall_id": fcall_id,
                "skill": skill,
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


async def test(super: bool):
    inside_fgroup_id = "solar_root"
    system_prompt = "Flexus client kit test system prompt. Just answer the question!"
    if not super:
        client = ckit_client.FlexusClient("ckit_test", api_key="sk_alice_123456")
        fexp_id = await ckit_expert.make_sure_have_expert(
            client,
            system_prompt,
            "",
            "alice@example.com",
            inside_fgroup_id,
            "ckit_test",
        )
    else:
        client = ckit_client.FlexusClient("ckit_test", endpoint="/v1/jailed-bot")
        # this will create a global expert
        fexp_id = await ckit_expert.make_sure_have_expert(
            client,
            system_prompt,
            "",
            None,
            None,
            "ckit_test",
        )
    print("fexp_id", fexp_id)
    YYYmmdd_HHMMSS = time.strftime("%Y%m%d %H:%M:%S")
    response = await ask_model(
        client,
        inside_fgroup_id=inside_fgroup_id,
        fexp_id=fexp_id,
        persona_id="karen1",
        title="Test %s" % YYYmmdd_HHMMSS,
        model="gpt-4.1-mini",
        who_is_asking="ckit_ask_model",
        on_behalf_of_fuser_id="alice@example.com",
        question="What is the meaning of life?",
    )
    print("ftm_belongs_to_ft_id", response.ftm_belongs_to_ft_id)
    print("RESPONSE:", response.ftm_content)


if __name__ == "__main__":
    asyncio.run(test(True))
