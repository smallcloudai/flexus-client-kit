import time
import uuid
import json
import asyncio
import logging
import os
from typing import Any, Dict, Optional, Callable

import gql
from PIL import Image
from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_bot_exec, ckit_bot_install, ckit_client, ckit_mongo, ckit_shutdown, ckit_cloudtool, ckit_ask_model, ckit_utils, gql_utils

logger = logging.getLogger("scenario")

MARKETPLACE_DEV_STAGES = ["MARKETPLACE_DEV", "MARKETPLACE_WAITING_IMAGE", "MARKETPLACE_FAILED_IMAGE_BUILD"]


async def select_workspace_for_scenario(
    fclient: ckit_client.FlexusClient,
    bs: ckit_client.BasicStuffOutput,
    persona_marketable_name: Optional[str] = None,
) -> ckit_client.FWorkspaceOutput:
    '''Find ws with persona_marketable_name available for dev, fallback to any ws with have_admin, or the first one'''
    if persona_marketable_name:
        for w in bs.workspaces:
            if w.have_admin:
                async with (await fclient.use_http()) as http:
                    details = await http.execute(gql.gql("""
                        query MarketplaceDetails($ws_id: String!, $marketable_name: String!) {
                            marketplace_details(ws_id: $ws_id, marketable_name: $marketable_name) {
                                versions { marketable_stage }
                            }
                        }"""), variable_values={"ws_id": w.ws_id, "marketable_name": persona_marketable_name})

                    versions = details["marketplace_details"]["versions"]
                    if any(v["marketable_stage"] in MARKETPLACE_DEV_STAGES for v in versions):
                        return w
    return next((w for w in bs.workspaces if w.have_admin), bs.workspaces[0])


class ScenarioSetup:
    def __init__(self, service_name: str = "test_scenario"):
        self.fclient = ckit_client.FlexusClient(service_name=service_name)
        self.bot_fclient = ckit_client.FlexusClient(service_name=f"{service_name}_bot", endpoint="/v1/jailed-bot")
        self.fgroup_id: Optional[str] = None
        self.fgroup_name: Optional[str] = None
        self.persona: Optional[ckit_bot_exec.FPersonaOutput] = None
        self.mongo_collection: Optional[AsyncMongoClient] = None
        self.bs: Optional[ckit_client.BasicStuffOutput] = None
        self.ws: Optional[ckit_client.FWorkspaceOutput] = None
        self.main_thread_id: Optional[str] = None
        self.inprocess_tools: list = []
        self._background_tasks: set = set()

    async def create_group_and_hire_bot(
        self,
        persona_marketable_name: str,
        persona_marketable_version: Optional[int],
        persona_setup: dict,
        inprocess_tools: list,
        group_prefix: str = "test",
    ) -> None:
        self.inprocess_tools = inprocess_tools
        self.bs = await ckit_client.query_basic_stuff(self.fclient)
        self.ws = await select_workspace_for_scenario(self.fclient, self.bs, persona_marketable_name)
        await self.create_test_group(group_prefix)
        await self.hire_bot(persona_marketable_name, persona_marketable_version, persona_setup)
        logger.info("Scenario setup completed in group %s", self.fgroup_name)

    async def create_test_group(self, group_prefix: str) -> None:
        self.fgroup_name = f"{group_prefix}-{uuid.uuid4().hex[:6]}"
        async with (await self.fclient.use_http()) as http:
            self.fgroup_id = (await http.execute(
                gql.gql("""mutation($input: FlexusGroupInput!){group_create(input:$input){fgroup_id}}"""),
                variable_values={"input": {"fgroup_name": self.fgroup_name, "fgroup_parent_id": self.ws.ws_root_group_id}},
            ))["group_create"]["fgroup_id"]

    async def hire_bot(
        self,
        persona_marketable_name: str,
        persona_marketable_version: Optional[int],
        persona_setup: dict,
    ) -> None:
        install = await ckit_bot_install.bot_install_from_marketplace(
            client=self.fclient, ws_id=self.ws.ws_id, inside_fgroup=self.fgroup_id,
            persona_marketable_name=persona_marketable_name, new_setup=persona_setup,
            persona_name=f"{persona_marketable_name} Test {self.fgroup_id[-4:]}", install_dev_version=True,
        )

        async with (await self.fclient.use_http()) as http:
            persona_details = await http.execute(gql.gql("""
                query PersonaGet($id: String!) {
                    persona_get(id: $id) {
                        persona_marketable_version
                    }
                }"""), variable_values={"id": install.persona_id})
        installed_version = persona_details["persona_get"]["persona_marketable_version"]

        if persona_marketable_version and installed_version != persona_marketable_version:
            raise RuntimeError(f"Expected version {persona_marketable_version}, got {installed_version}")

        self.persona = ckit_bot_exec.FPersonaOutput(
            owner_fuser_id=self.bs.fuser_id, located_fgroup_id=self.fgroup_id, persona_id=install.persona_id,
            persona_name=f"{persona_marketable_name} Test {self.fgroup_id[-4:]}", persona_marketable_name=persona_marketable_name,
            persona_marketable_version=installed_version, persona_discounts=None,
            persona_setup=dict(persona_setup), persona_created_ts=time.time(),
            ws_id=self.ws.ws_id, ws_timezone="UTC"
        )

    async def create_fake_files_and_upload_to_mongo(self, workdir: str) -> None:
        os.makedirs(workdir, exist_ok=True)
        Image.new('RGB', (100, 100), color='red').save(f'{workdir}/1.png')
        Image.new('RGB', (100, 100), color='blue').save(f'{workdir}/2.png')
        open(f'{workdir}/1.txt', 'w').write('This is test file 1\nWith multiple lines\nFor testing file attachments')
        open(f'{workdir}/2.json', 'w').write('{"test": "data", "file": "2", "content": "json test file"}')

        self.mongo_collection = AsyncMongoClient(await ckit_mongo.get_mongodb_creds(self.bot_fclient, self.persona.persona_id))[self.persona.persona_id + "_db"]["files"]
        for filename in ['1.png', '2.png', '1.txt', '2.json']:
            with open(f'{workdir}/{filename}', 'rb') as f:
                await ckit_mongo.store_file(self.mongo_collection, filename, f.read())

    async def print_main_thread(self) -> None:
        if not self.main_thread_id:
            logger.info("No main thread set (setup.main_thread_id is None)")
            return

        async with (await self.fclient.use_http()) as http:
            thread_info = await http.execute(gql.gql("""
                query GetThread($id: String!) {
                    thread_get(id: $id) { ft_id ft_app_searchable }
                }"""), variable_values={"id": self.main_thread_id})

            if not thread_info["thread_get"]:
                logger.info(f"Main thread {self.main_thread_id} not found")
                return

            messages = await http.execute(gql.gql("""
                query ThreadMessages($ft_id: String!) {
                    thread_messages_list(ft_id: $ft_id) { ftm_role ftm_content ftm_alt ftm_tool_calls }
                }"""), variable_values={"ft_id": self.main_thread_id})

            thread = thread_info["thread_get"]
            logger.info(f"\n📝 Main Thread ft_id: {thread['ft_id']} captured_from: {thread.get('ft_app_searchable', 'N/A')}")
            colors = {"user": "\033[94m", "assistant": "\033[92m", "system": "\033[93m", "tool": "\033[95m", "kernel": "\033[96m"}
            for msg in messages["thread_messages_list"]:
                if msg["ftm_alt"] == 100:
                    content = str(msg["ftm_content"])[:300] + "..." if len(str(msg["ftm_content"])) > 300 else str(msg["ftm_content"])
                    color = colors.get(msg['ftm_role'], "\033[0m")
                    logger.info(f"  {color}{msg['ftm_role']}\033[0m: {content}")

                    if msg['ftm_role'] == 'assistant' and msg.get('ftm_tool_calls'):
                        for tool_call in msg['ftm_tool_calls']:
                            tool_name = tool_call.get('function', {}).get('name', 'unknown')
                            tool_args = str(tool_call.get('function', {}).get('arguments', ''))[:100] + "..." if len(str(tool_call.get('function', {}).get('arguments', ''))) > 100 else str(tool_call.get('function', {}).get('arguments', ''))
                            logger.info(f"    \033[96m🔧 {tool_name}\033[0m: {tool_args}")

    async def run_scenario(self, scenario_func: Callable[..., None], cleanup_wait_secs: int = 300, **kwargs) -> None:
        ckit_shutdown.setup_signals()
        scenario_task = asyncio.create_task(scenario_func(self, **kwargs))
        ckit_shutdown.give_task_to_cancel("scenario", scenario_task)
        try:
            await scenario_task
            logger.info("Test completed successfully!")
        except asyncio.CancelledError:
            logger.info("Scenario cancelled")
        except Exception as e:
            logger.exception("\033[91mERROR\033[0m")
        finally:
            ckit_shutdown.take_away_task_to_cancel("scenario")
            await self.print_main_thread()
            logger.info(f"Waiting {cleanup_wait_secs} seconds before cleanup... (Ctrl+C to cleanup immediately)")
            await ckit_shutdown.wait(cleanup_wait_secs)
            await self.cleanup()
            logger.info("Cleanup completed.")

    def create_fake_toolcall_output(self, call_id: str, ft_id: str, args: dict) -> ckit_cloudtool.FCloudtoolCall:
        if not self.persona:
            raise RuntimeError("Must call setup() first")
        return ckit_cloudtool.FCloudtoolCall(
            caller_fuser_id=self.persona.owner_fuser_id, located_fgroup_id=self.persona.located_fgroup_id,
            fcall_id=call_id, fcall_ft_id=ft_id, fcall_ftm_alt=100, fcall_called_ftm_num=1,
            fcall_call_n=0, fcall_name="slack", fcall_arguments=json.dumps(args), fcall_created_ts=time.time(),
            connected_persona_id=self.persona.persona_id, ws_id=self.persona.ws_id, subgroups_list=[],
            fcall_untrusted_key="",
        )

    async def wait_for_toolcall(
        self,
        fcall_name: str,
        ft_id: Optional[str],
        expected_params: Dict[str, Any],
        timeout_seconds: float = 120.0,
    ) -> ckit_ask_model.FThreadMessageOutput:
        deadline = asyncio.get_running_loop().time() + timeout_seconds
        initial_updates_over = False
        message_with_the_tool_call = None
        threads_tracked = {ft_id} if ft_id else set()
        threads_stopped = set()

        ws_client = await self.bot_fclient.use_ws()
        async with ws_client as ws:
            async for r in ws.subscribe(
                gql.gql(f"""subscription ScenarioThreads($fgroup_id: String!, $marketable_name: String!, $marketable_version: Int!, $inprocess_tool_names: [String!]!) {{
                    bot_threads_and_calls_subs(fgroup_id: $fgroup_id, marketable_name: $marketable_name, marketable_version: $marketable_version, inprocess_tool_names: $inprocess_tool_names, max_threads: 100, want_personas: false, want_threads: true, want_messages: true) {{
                        {gql_utils.gql_fields(ckit_bot_exec.FBotThreadsAndCallsSubs)}
                    }}
                }}"""),
                variable_values={
                    "fgroup_id": self.fgroup_id,
                    "marketable_name": self.persona.persona_marketable_name,
                    "marketable_version": self.persona.persona_marketable_version,
                    "inprocess_tool_names": [t.name for t in self.inprocess_tools],
                },
            ):
                if asyncio.get_running_loop().time() > deadline or ckit_shutdown.shutdown_event.is_set():
                    raise TimeoutError()
                upd = gql_utils.dataclass_from_dict(r["bot_threads_and_calls_subs"], ckit_bot_exec.FBotThreadsAndCallsSubs)

                initial_updates_over |= upd.news_action == "INITIAL_UPDATES_OVER"

                if (thread := upd.news_payload_thread):
                    if ft_id is None:
                        threads_tracked.add(thread.ft_id)
                    if thread.ft_need_user >= 0 and thread.ft_id in threads_tracked:
                        threads_stopped.add(thread.ft_id)

                        if message_with_the_tool_call and message_with_the_tool_call.ftm_belongs_to_ft_id == thread.ft_id:
                            return message_with_the_tool_call
                        if initial_updates_over and threads_stopped == threads_tracked:
                            raise RuntimeError(f"Tool call {fcall_name} with parameters {expected_params} not found")

                if initial_updates_over and (message := upd.news_payload_thread_message):
                    if ft_id is None or message.ftm_belongs_to_ft_id == ft_id:
                        for call in message.ftm_tool_calls or []:
                            try:
                                args = json.loads(call["function"]["arguments"])
                                if call["function"]["name"] == fcall_name and all(
                                    args.get(key) == value for key, value in expected_params.items()
                                ) and message_with_the_tool_call is None:
                                    message_with_the_tool_call = message
                                    break
                            except (json.JSONDecodeError, KeyError):
                                pass

    async def cleanup(self) -> None:
        if self.fgroup_id:
            try:
                async with (await self.fclient.use_http()) as http:
                    await http.execute(gql.gql("""mutation($id:String!){group_delete(fgroup_id:$id)}"""), variable_values={"id": self.fgroup_id})
            except Exception as e:
                logger.warning(f"⚠️ Failed to delete test group {self.fgroup_name}: {e}")
