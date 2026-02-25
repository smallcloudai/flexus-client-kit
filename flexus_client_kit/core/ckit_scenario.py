import uuid
import logging
import argparse
import yaml
import dataclasses
from dataclasses import dataclass
from typing import Optional, Dict, List, Union, Any

import gql

from flexus_client_kit.core import gql_utils, ckit_bot_install, ckit_client, ckit_ask_model, ckit_kanban, ckit_bot_query, ckit_cloudtool

logger = logging.getLogger("cksce")


def bot_launch_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", type=str, help="Reproduce a happy trajectory emulating human and tools, path to YAML file")
    parser.add_argument("--no-cleanup", action="store_true", help="Skip cleanup of test group")
    parser.add_argument("--model", type=str, default="")
    parser.add_argument("--experiment", "-E", type=str, default="", help="Experiment name to append to output files")
    return parser


@dataclass
class ScenarioHumanMessageOutput:
    scenario_done: bool
    next_human_message: str
    shaky: bool
    stop_reason: str
    cost: int


@dataclass
class ScenarioJudgeOutput:
    rating_happy: int
    feedback_happy: str
    rating_actually: int
    feedback_actually: str
    criticism: dict
    cost: int


@dataclass
class BotScenarioUpsertInput:
    btest_marketable_name: str
    btest_marketable_version_str: str
    btest_name: str
    btest_model: str
    btest_experiment: str
    btest_trajectory_happy: str
    btest_trajectory_actual: str
    btest_rating_happy: int
    btest_rating_actually: int
    btest_feedback_happy: str
    btest_feedback_actually: str
    btest_shaky_human: int
    btest_shaky_tool: int
    btest_criticism: str
    btest_cost: int


async def scenario_generate_human_message(
    client: ckit_client.FlexusClient,
    happy_trajectory: str,
    fgroup_id: str,
    ft_id: Optional[str] = None,
) -> ScenarioHumanMessageOutput:
    http_client = await client.use_http()
    http_client.execute_timeout = 120
    async with http_client as http:
        r = await http.execute(
            gql.gql(f"""mutation ScenarioGenerateHumanMessage(
                $happy_trajectory: String!,
                $fgroup_id: String!,
                $ft_id: String
            ) {{
                scenario_generate_human_message(
                    happy_trajectory: $happy_trajectory,
                    fgroup_id: $fgroup_id,
                    ft_id: $ft_id
                ) {{
                    {gql_utils.gql_fields(ScenarioHumanMessageOutput)}
                }}
            }}"""),
            variable_values={
                "happy_trajectory": happy_trajectory,
                "fgroup_id": fgroup_id,
                "ft_id": ft_id,
            },
        )
    return gql_utils.dataclass_from_dict(r["scenario_generate_human_message"], ScenarioHumanMessageOutput)


async def scenario_judge(
    client: ckit_client.FlexusClient,
    happy_trajectory: str,
    ft_id: str,
    judge_instructions: str,
) -> ScenarioJudgeOutput:
    http_client = await client.use_http()
    http_client.execute_timeout = 120
    async with http_client as http:
        r = await http.execute(
            gql.gql(f"""mutation ScenarioJudge(
                $happy_trajectory: String!,
                $ft_id: String!,
                $judge_instructions: String!
            ) {{
                scenario_judge(
                    happy_trajectory: $happy_trajectory,
                    ft_id: $ft_id,
                    judge_instructions: $judge_instructions
                ) {{
                    {gql_utils.gql_fields(ScenarioJudgeOutput)}
                }}
            }}"""),
            variable_values={
                "happy_trajectory": happy_trajectory,
                "ft_id": ft_id,
                "judge_instructions": judge_instructions,
            },
        )
    return gql_utils.dataclass_from_dict(r["scenario_judge"], ScenarioJudgeOutput)


def _represent_multiline_str(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


def yaml_dump_with_multiline(data: dict) -> str:
    dumper = yaml.Dumper
    dumper.add_representer(str, _represent_multiline_str)
    return yaml.dump(data, Dumper=dumper, default_flow_style=False, allow_unicode=True, width=100, sort_keys=False)


def fmessages_to_yaml(messages: list) -> str:
    export_messages = []
    for msg in messages:
        m = {"role": msg.ftm_role}
        if msg.ftm_content:
            m["content"] = msg.ftm_content
        if msg.ftm_tool_calls and msg.ftm_tool_calls not in ("null", "[]"):
            m["tool_calls"] = msg.ftm_tool_calls
        if msg.ftm_call_id:
            m["call_id"] = msg.ftm_call_id
        export_messages.append(m)
    return yaml_dump_with_multiline({"messages": export_messages})


async def scenario_generate_tool_result_via_model(
    fclient: ckit_client.FlexusClient,
    toolcall: ckit_cloudtool.FCloudtoolCall,
    tool_handler_source_code: str,
) -> str:
    http_client = await fclient.use_http(execute_timeout=120)
    async with http_client as http:
        await http.execute(
            gql.gql("""mutation ScenarioGenerateToolResult(
                $fcall_id: String!,
                $fcall_untrusted_key: String!,
                $tool_handler_source_code: String!
            ) {
                scenario_generate_tool_result_via_model(
                    fcall_id: $fcall_id,
                    fcall_untrusted_key: $fcall_untrusted_key,
                    tool_handler_source_code: $tool_handler_source_code
                )
            }"""),
            variable_values={
                "fcall_id": toolcall.fcall_id,
                "fcall_untrusted_key": toolcall.fcall_untrusted_key,
                "tool_handler_source_code": tool_handler_source_code,
            },
        )
    raise ckit_cloudtool.AlreadyPostedResult()


async def scenario_print_personas(fclient: ckit_client.FlexusClient, fgroup_id: str) -> str:
    lines = []
    for persona in (await ckit_bot_query.persona_list(fclient, fgroup_id)):
        lines.append(f"    👤{persona.persona_id} name={persona.persona_name!r} marketplace={persona.persona_marketable_name}@{persona.persona_marketable_version} pref_model={persona.persona_preferred_model}")
        kanban_tasks = await ckit_kanban.persona_kanban_list(fclient, persona.persona_id)
        if kanban_tasks:
            for task in kanban_tasks:
                extras = []
                if task.ktask_resolution_code:
                    extras.append(f"resolution_code:{task.ktask_resolution_code}")
                if task.ktask_resolution_summary:
                    extras.append(f"resolution_summary:'{task.ktask_resolution_summary}'")
                if hasattr(task.ktask_details, 'get') and task.ktask_details and task.ktask_details.get('humanhours'):
                    extras.append(f"humanhours:{task.ktask_details['humanhours']}")
                extra_str = f" {' '.join(extras)}" if extras else ""
                lines.append(f"        📋 {task.calc_bucket()} id:{task.ktask_id} title:'{task.ktask_title}' budget:{task.ktask_budget} coins:{task.ktask_coins}{extra_str}")
        else:
            lines.append(f"        📋 No kanban tasks")
    return "\n".join(lines)


async def scenario_print_threads(fclient: ckit_client.FlexusClient, fgroup_id: str) -> str:
    async with (await fclient.use_http()) as http:
        threads = await http.execute(gql.gql(f"""
            query GetGroupThreads($fgroup_id: String!) {{
                thread_list(located_fgroup_id: $fgroup_id, skip: 0, limit: 100) {{
                    {gql_utils.gql_fields(ckit_ask_model.FThreadOutput)}
                }}
            }}"""), variable_values={"fgroup_id": fgroup_id})

        lines = []
        for thread_dict in threads["thread_list"]:
            thread = gql_utils.dataclass_from_dict(thread_dict, ckit_ask_model.FThreadOutput)

            a, t, u = thread.ft_need_assistant, thread.ft_need_tool_calls, thread.ft_need_user
            need_str = f"need_assistant={a}" if a != -1 else f"ended_with need_tool_calls={t}" if t != -1 else f"ended_with need_user={u}"
            persona_id = thread.ft_persona_id or "N/A"
            tool_names = ",".join([tool['function']['name'] for tool in thread.ft_toolset])
            lines.append(f"    📝{thread.ft_id} title={thread.ft_title!r} persona={persona_id} exp={thread.ft_fexp_id} budget={thread.ft_budget} coins={thread.ft_coins}")
            lines.append(f"    searchable={thread.ft_app_searchable!r} capture={thread.ft_app_capture!r} {need_str}")
            lines.append(f"    toolset={tool_names}")
            if thread.ft_error:
                lines.append(f"    ft_error=\033[91m{thread.ft_error}\033[0m")

            messages = await http.execute(gql.gql(f"""
                query ThreadMessages($ft_id: String!) {{
                    thread_messages_list(ft_id: $ft_id) {{ {gql_utils.gql_fields(ckit_ask_model.FThreadMessageOutput)} }}
                }}"""), variable_values={"ft_id": thread.ft_id})

            colors = {
                "user": "\033[93m",      # Bright Yellow
                "assistant": "\033[92m", # Bright Green
                "system": "\033[95m",
                "cd_instruction": "\033[95m",
                "tool": "\033[95m",      # Bright Magenta
                "kernel": "\033[96m"     # Bright Cyan
            }

            for msg_dict in messages["thread_messages_list"]:
                msg = gql_utils.dataclass_from_dict(msg_dict, ckit_ask_model.FThreadMessageOutput)
                if msg.ftm_alt == 100:
                    content = str(msg.ftm_content).replace('\n', '\\n')[:120]
                    if len(str(msg.ftm_content)) > 120:
                        content += "..."
                    color = colors.get(msg.ftm_role, "\033[0m")
                    msg_key = "%03d:%03d" % (msg.ftm_alt, msg.ftm_num)
                    lines.append(f"        {msg_key} {color}{msg.ftm_role}\033[0m: {content}")
                    if msg.ftm_role == 'assistant' and msg.ftm_tool_calls:
                        for tool_call in msg.ftm_tool_calls:
                            tool_name = tool_call.get('function', {}).get('name', 'unknown')
                            tool_args = str(tool_call.get('function', {}).get('arguments', ''))[:60]
                            if len(str(tool_call.get('function', {}).get('arguments', ''))) > 60:
                                tool_args += "..."
                            lines.append(f"            🔧 {tool_name}: {tool_args}")
                    if msg.ftm_role == 'assistant' and msg.ftm_usage:
                        lines.append(f"            ⏳ {'%0.3f' % msg.ftm_usage['llm_lag']}s")
        if len(lines) == 0:
            lines.append("    No threads")
    return "\n".join(lines)


class ScenarioSetup:
    def __init__(self, service_name: str = "test_scenario"):
        parser = bot_launch_argparse()
        args = parser.parse_args()

        self.fclient = ckit_client.FlexusClient(service_name=service_name)
        self.fgroup_id: Optional[str] = None
        self.fgroup_name: Optional[str] = None
        self.persona: Optional[ckit_bot_query.FPersonaOutput] = None
        self.ws: Optional[ckit_client.FWorkspaceOutput] = None
        self.should_cleanup = not args.no_cleanup
        self.explicit_model = args.model
        self.experiment = args.experiment

    async def create_group_and_hire_bot(
        self,
        marketable_name: str,
        marketable_version: Optional[int],
        persona_setup: dict,
        group_prefix: str = "test",
    ) -> None:
        if not self.fclient.ws_id:
            raise RuntimeError("FLEXUS_WORKSPACE environment variable is not set")

        async with (await self.fclient.use_http()) as http:
            ws_query = await http.execute(gql.gql(f"""
                query GetWorkspace {{
                    query_basic_stuff(want_invitations: false) {{
                        workspaces {{
                            {gql_utils.gql_fields(ckit_client.FWorkspaceOutput)}
                        }}
                    }}
                }}"""))
            workspaces = [gql_utils.dataclass_from_dict(w, ckit_client.FWorkspaceOutput) for w in ws_query["query_basic_stuff"]["workspaces"]]
            self.ws = next((w for w in workspaces if w.ws_id == self.fclient.ws_id), None)
            if not self.ws:
                raise RuntimeError(f"Workspace {self.fclient.ws_id} not found in user's workspaces")

            self.fgroup_name = f"{group_prefix}-{uuid.uuid4().hex[:6]}"
            self.fgroup_id = (await http.execute(gql.gql("""
                mutation CreateGroup($input: FlexusGroupInput!) {
                    group_create(input: $input) { fgroup_id }
                }"""),
                variable_values={
                    "input": {
                        "fgroup_name": self.fgroup_name,
                        "fgroup_parent_id": self.ws.ws_root_group_id,
                    }
                },
            ))["group_create"]["fgroup_id"]

            try:
                install = await ckit_bot_install.bot_install_from_marketplace(
                    client=self.fclient,
                    ws_id=self.ws.ws_id,
                    inside_fgroup=self.fgroup_id,
                    persona_marketable_name=marketable_name,
                    persona_name=f"{marketable_name} {self.fgroup_id[-4:]}",
                    new_setup=persona_setup,
                    install_dev_version=True,
                )
                personas = await ckit_bot_query.personas_in_ws_list(self.fclient, self.ws.ws_id)
                self.persona = next((p for p in personas if p.persona_id == install.persona_id), None)
                if not self.persona:
                    raise RuntimeError(f"Persona {install.persona_id} not found in workspace after installation")
                if marketable_version and self.persona.persona_marketable_version != marketable_version:
                    raise RuntimeError(f"Expected version {marketable_version}, got {self.persona.persona_marketable_version}")

                logger.info("Hired bot %s in group %s", self.persona.persona_id, self.fgroup_name)

            except Exception as e:
                try:
                    await http.execute(gql.gql("""mutation($id:String!){group_delete(fgroup_id:$id)}"""), variable_values={"id": self.fgroup_id})
                except Exception as cleanup_error:
                    logger.warning(f"⚠️ Failed to delete test group {self.fgroup_name} after installation failure: {cleanup_error}")
                raise e

    async def cleanup(self) -> None:
        if self.fgroup_id:
            try:
                async with (await self.fclient.use_http()) as http:
                    await http.execute(gql.gql("""mutation($id:String!){group_delete(fgroup_id:$id)}"""), variable_values={"id": self.fgroup_id})
            except Exception as e:
                logger.warning(f"⚠️ Failed to delete test group {self.fgroup_name}: {e}")


async def bot_scenario_result_upsert(
    client: ckit_client.FlexusClient,
    input: BotScenarioUpsertInput,
) -> bool:
    http_client = await client.use_http()
    async with http_client as http:
        result = await http.execute(
            gql.gql("""mutation BotScenarioResultUpsert($input: BotScenarioUpsertInput!) {
                bot_scenario_result_upsert(input: $input)
            }"""),
            variable_values={
                "input": dataclasses.asdict(input)
            }
        )
    return result["bot_scenario_result_upsert"]
