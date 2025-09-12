import time
import asyncio
import json
import random
import re
from dataclasses import dataclass
from typing import Optional, Any, List, Callable, Union

import gql

from flexus_client_kit import ckit_expert, ckit_client, gql_utils, ckit_localtool


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
    ftm_usage: Any
    ftm_tool_calls: Any
    ftm_app_specific: Any
    ftm_created_ts: float
    ftm_provenance: Any


@dataclass
class FThreadOutput:
    ft_id: str
    ft_error: Optional[Any]
    ft_need_tool_calls: int
    ft_need_user: int
    ft_persona_id: str
    ft_app_searchable: str
    ft_app_specific: Optional[Any]
    ft_updated_ts: float


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
    localtools: Optional[List[Callable]] = None,
    cloudtools: Optional[List[ckit_expert.FCloudTool]] = None,
    on_behalf_of_fuser_id: Optional[str] = None,
) -> FThreadMessageOutput:
    if localtools or cloudtools:
        combined_toolset = []
        if cloudtools:
            combined_toolset.extend(openai_style_cloudtools(cloudtools))
        if localtools:
            combined_toolset.extend([ckit_localtool.openai_style_function_description(f) for f in localtools])
        toolset = combined_toolset

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
                    "ft_toolset": json.dumps(toolset),
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
    content: Union[str, list, dict],
    who_is_asking: str,
    ftm_alt: int,
    user_preferences: str = "null",
    role: str = "user",
) -> None:
    random_ftm_num = -random.randint(1, 2**31 - 1)
    assert role in ["user", "cd_instruction"]

    if isinstance(content, str):
        # For backward compatibility, wrap plain strings
        ftm_content = json.dumps(content)
    elif isinstance(content, (list, dict)):
        ftm_content = json.dumps(content)
    else:
        ftm_content = json.dumps(str(content))

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
                            "ftm_provenance": json.dumps({"system_type": who_is_asking}),
                        },
                    ],
                }
            },
        )


async def bot_activate(
    client: ckit_client.FlexusClient,
    who_is_asking: str,
    persona_id: str,
    activation_type: str,
    first_question: str,
    first_calls: Any = None,
    title: str = "",
    sched_id: str = "",
) -> str:
    assert activation_type in ["default", "todo", "setup", "subchat"]
    title = title or (activation_type + " " + time.strftime("%Y%m%d %H:%M:%S"))
    assert re.match(r'^[a-z0-9_]+$', who_is_asking)
    camel_case_for_logs = "".join(word.capitalize() for word in who_is_asking.split("_"))
    http = await client.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql(f"""mutation {camel_case_for_logs}BotActivate($who_is_asking: String!, $persona_id: String!, $activation_type: String!, $first_question: String!, $first_calls: String!, $title: String!, $sched_id: String!) {{
                bot_activate(who_is_asking: $who_is_asking, persona_id: $persona_id, activation_type: $activation_type, first_question: $first_question, first_calls: $first_calls, title: $title, sched_id: $sched_id) {{ ft_id }}
            }}"""),
            variable_values={
                "who_is_asking": who_is_asking,
                "persona_id": persona_id,
                "activation_type": activation_type,
                "first_question": first_question,
                "first_calls": json.dumps(first_calls),
                "title": title,
                "sched_id": sched_id,
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
    subchat_dest_ft_id: str,
    subchat_dest_ftm_alt: int,
    subchat_dest_ftm_num: int,
    ft_subchat_dest_call_n: int,
) -> None:
    assert re.match(r'^[a-z0-9_]+$', who_is_asking)
    camel_case_for_logs = "".join(word.capitalize() for word in who_is_asking.split("_"))
    http = await client.use_http()
    async with http as h:
        await h.execute(
            gql.gql(f"""mutation {camel_case_for_logs}BotSubchatCreateMultiple($who_is_asking: String!, $persona_id: String!, $first_question: [String!]!, $first_calls: [String!]!, $title: [String!]!, $subchat_dest_ft_id: String!, $subchat_dest_ftm_alt: Int!, $subchat_dest_ftm_num: Int!, $ft_subchat_dest_call_n: Int!) {{
                bot_subchat_create_multiple(who_is_asking: $who_is_asking, persona_id: $persona_id, first_question: $first_question, first_calls: $first_calls, title: $title, subchat_dest_ft_id: $subchat_dest_ft_id, subchat_dest_ftm_alt: $subchat_dest_ftm_alt, subchat_dest_ftm_num: $subchat_dest_ftm_num, ft_subchat_dest_call_n: $ft_subchat_dest_call_n)
            }}"""),
            variable_values={
                "who_is_asking": who_is_asking,
                "persona_id": persona_id,
                "activation_type": "subchat",
                "first_question": first_question,
                "first_calls": first_calls,
                "title": title,
                "subchat_dest_ft_id": subchat_dest_ft_id,
                "subchat_dest_ftm_alt": subchat_dest_ftm_alt,
                "subchat_dest_ftm_num": subchat_dest_ftm_num,
                "ft_subchat_dest_call_n": ft_subchat_dest_call_n,
            },
        )


async def wait_until_thread_stops(
    client: ckit_client.FlexusClient,
    ft_id: str,
    timeout: int = 600,
    localtools: List[Callable] = [],
) -> FThreadMessageOutput:
    thread = None
    messages = dict()
    called_local_for = set()

    def last_assistant(check_alt: int, no_calls_only: bool):
        alt_only = [m for m in messages.values() if m.ftm_alt == check_alt]
        alt_only.sort(key=lambda m: m.ftm_num)
        i = len(alt_only) - 1
        while i > 0:
            if alt_only[i].ftm_role == "assistant" and (not no_calls_only or not alt_only[i].ftm_tool_calls):
                return alt_only[i]
            i -= 1
        return None

    async def _check_incoming_updates():
        nonlocal messages, thread
        ws_client = await client.use_ws()
        async with ws_client as ws:
            q = gql.gql(f"""subscription ClientKitAskModel($id: String!) {{
                comprehensive_thread_subs(ft_id: $id, want_deltas: false) {{
                    {gql_utils.gql_fields(FThreadComprehensiveSubs)}
                }}
            }}""")
            async for res in ws.subscribe(q, variable_values={"id": ft_id}):
                upd = gql_utils.dataclass_from_dict(res["comprehensive_thread_subs"], FThreadComprehensiveSubs)
                if upd.news_payload_thread and upd.news_payload_thread.ft_error:
                    raise RuntimeError(str(upd.news_payload_thread.ft_error))
                if t := upd.news_payload_thread:
                    thread = t
                if m := upd.news_payload_thread_message:
                    key = "%03d:%03d" % (m.ftm_alt, m.ftm_num)
                    messages[key] = m
                if (alt := thread.ft_need_tool_calls) > -1:
                    if ass := last_assistant(alt, no_calls_only=False):
                        key = "%03d:%03d" % (ass.ftm_alt, ass.ftm_num)
                        if key not in called_local_for:
                            called_local_for.add(key)
                            await ckit_localtool.call_local_functions_and_upload_results(client, ass, localtools)
                if (alt := thread.ft_need_user) > -1:
                    if ass := last_assistant(alt, no_calls_only=True):
                        for m in messages.values():
                            print(m.ftm_num, m.ftm_role)
                        return ass

    try:
        return await asyncio.wait_for(_check_incoming_updates(), timeout=timeout)
    except asyncio.TimeoutError:
        # XXX dump thread to logs
        # logger.info(f"Hmm I hit a timeout"
        raise RuntimeError(f"Timeout waiting for assistant response in ft_id=%s after %d seconds" % (ft_id, timeout))


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
        client = ckit_client.FlexusClient("ckit_test", endpoint="/v1/superuser-bot")
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
