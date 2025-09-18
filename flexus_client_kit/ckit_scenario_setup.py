import tempfile
import time
import uuid
import json
import asyncio
import contextlib
import traceback
import logging
from typing import Optional, Callable, Any

import gql
from PIL import Image
from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_bot_exec, ckit_bot_install, ckit_client, ckit_mongo, ckit_shutdown

logger = logging.getLogger("scenario")


async def select_workspace(
    fclient: ckit_client.FlexusClient,
    bs: ckit_client.BasicStuffOutput,
    persona_name: Optional[str] = None,
    require_dev: bool = False
) -> ckit_client.FWorkspaceOutput:
    if persona_name:
        dev_stages = ["MARKETPLACE_DEV", "MARKETPLACE_WAITING_IMAGE", "MARKETPLACE_FAILED_IMAGE_BUILD"]
        for w in bs.workspaces:
            if w.have_admin:
                try:
                    async with (await fclient.use_http()) as http:
                        details = await http.execute(gql.gql("""
                            query MarketplaceDetails($ws_id: String!, $marketable_name: String!) {
                                marketplace_details(ws_id: $ws_id, marketable_name: $marketable_name) {
                                    versions { marketable_stage }
                                }
                            }"""), variable_values={"ws_id": w.ws_id, "marketable_name": persona_name})

                        versions = details["marketplace_details"]["versions"]
                        if require_dev and any(v["marketable_stage"] in dev_stages for v in versions):
                            return w
                        elif not require_dev and versions:
                            return w
                except:
                    continue
    return next((w for w in bs.workspaces if w.have_admin), bs.workspaces[0])


class ScenarioSetup:
    def __init__(self, service_name: str = "test_scenario"):
        self.fclient = ckit_client.FlexusClient(service_name=service_name)
        self.bot_fclient = ckit_client.FlexusClient(service_name=f"{service_name}_bot", endpoint="/v1/jailed-bot")
        self.fgroup_id: Optional[str] = None
        self.fgroup_name: Optional[str] = None
        self.persona: Optional[ckit_bot_exec.FPersonaOutput] = None
        self.rcx: Optional[ckit_bot_exec.RobotContext] = None
        self.mongo_collection: Optional[AsyncMongoClient] = None
        self.bs: Optional[ckit_client.BasicStuffOutput] = None
        self.ws: Optional[ckit_client.FWorkspaceOutput] = None

    async def setup(
        self,
        persona_name: str,
        persona_setup: Optional[dict] = None,
        persona_require_dev: bool = False,
        group_prefix: str = "test"
    ) -> tuple[ckit_bot_exec.RobotContext, AsyncMongoClient]:
        self.bs = await ckit_client.query_basic_stuff(self.fclient)
        self.ws = await select_workspace(self.fclient, self.bs, persona_name, persona_require_dev)
        await self.create_test_group(group_prefix)
        await self.install_persona(persona_name, persona_setup, persona_require_dev)
        await self.setup_mongo()
        logger.info("Scenario setup completed in group %s", self.fgroup_name)
        return self.rcx, self.mongo_collection

    async def create_test_group(self, group_prefix: str) -> None:
        self.fgroup_name = f"{group_prefix}-{uuid.uuid4().hex[:6]}"
        async with (await self.fclient.use_http()) as http:
            self.fgroup_id = (await http.execute(
                gql.gql("""mutation($input: FlexusGroupInput!){group_create(input:$input){fgroup_id}}"""),
                variable_values={"input": {"fgroup_name": self.fgroup_name, "fgroup_parent_id": self.ws.ws_root_group_id}},
            ))["group_create"]["fgroup_id"]

    async def install_persona(
        self,
        persona_name: str,
        persona_setup: Optional[dict] = None,
        persona_require_dev: bool = False,
    ) -> None:
        args = {
            "client": self.fclient, "ws_id": self.ws.ws_id, "inside_fgroup": self.fgroup_id,
            "persona_marketable_name": persona_name, "new_setup": persona_setup or {},
            "persona_name": f"{persona_name} Test {self.fgroup_id[-4:]}"
        }

        try:
            install = await ckit_bot_install.bot_install_from_marketplace(**args, install_dev_version=True)
        except Exception as e:
            if persona_require_dev:
                raise e
            install = await ckit_bot_install.bot_install_from_marketplace(**args, install_dev_version=False)

        async with (await self.fclient.use_http()) as http:
            persona_details = await http.execute(gql.gql("""
                query PersonaGet($id: String!) {
                    persona_get(id: $id) {
                        persona_marketable_version
                    }
                }"""), variable_values={"id": install.persona_id})

        self.persona = ckit_bot_exec.FPersonaOutput(
            owner_fuser_id=self.bs.fuser_id, located_fgroup_id=self.fgroup_id, persona_id=install.persona_id,
            persona_name=args["persona_name"], persona_marketable_name=persona_name,
            persona_marketable_version=persona_details["persona_get"]["persona_marketable_version"], persona_discounts=None,
            persona_setup=dict(persona_setup or {}), persona_created_ts=time.time(),
            ws_id=self.ws.ws_id, ws_timezone="UTC"
        )
        self.rcx = ckit_bot_exec.RobotContext(self.bot_fclient, self.persona)

    async def setup_mongo(self) -> None:
        import os
        os.makedirs(self.rcx.workdir, exist_ok=True)
        Image.new('RGB', (100, 100), color='red').save(f'{self.rcx.workdir}/1.png')
        Image.new('RGB', (100, 100), color='blue').save(f'{self.rcx.workdir}/2.png')
        open(f'{self.rcx.workdir}/1.txt', 'w').write('This is test file 1\nWith multiple lines\nFor testing file attachments')
        open(f'{self.rcx.workdir}/2.json', 'w').write('{"test": "data", "file": "2", "content": "json test file"}')

        self.mongo_collection = AsyncMongoClient(await ckit_mongo.get_mongodb_creds(self.bot_fclient, self.persona.persona_id))[self.persona.persona_id + "_db"]["files"]
        for filename in ['1.png', '2.png', '1.txt', '2.json']:
            with open(f'{self.rcx.workdir}/{filename}', 'rb') as f:
                await ckit_mongo.store_file(self.mongo_collection, filename, f.read())

    async def create_mcp(
        self,
        name: str,
        command: str,
        description: str = "",
        env_vars: Optional[dict] = None
    ) -> str:
        if not self.fgroup_id:
            raise RuntimeError("Must call setup() first")
        async with (await self.fclient.use_http()) as http:
            resp = await http.execute(
                gql.gql("""mutation CreateMCP($input: FMcpServerInput!) {
                    mcp_server_create(input: $input) { mcp_id }
                }"""),
                variable_values={
                    "input": {
                        "located_fgroup_id": self.fgroup_id,
                        "mcp_name": name,
                        "mcp_command": command,
                        "mcp_description": description,
                        "mcp_enabled": True,
                        "mcp_preinstall_script": "",
                        "owner_shared": True,
                        "mcp_env_vars": json.dumps(env_vars or {})
                    }
                }
            )
        return resp["mcp_server_create"]["mcp_id"]

    async def wait_for_mcp(self, mcp_id: str, timeout: int = 600) -> bool:
        logger.info("Waiting for MCP server to be ready...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                async with (await self.fclient.use_http()) as http:
                    resp = await http.execute(
                        gql.gql("""query GetMCP($id: String!) {
                            mcp_server_get(id: $id) { mcp_status }
                        }"""),
                        variable_values={"id": mcp_id}
                    )
                if resp["mcp_server_get"]["mcp_status"] == "RUNNING":
                    logger.info("✓ MCP server is ready")
                    return True
            except:
                pass
            await asyncio.sleep(2)
        logger.warning("⚠️ MCP server failed to start within timeout")
        return False

    async def print_captured_thread(self) -> None:
        if not self.fgroup_id:
            return
        async with (await self.fclient.use_http()) as http:
            threads = await http.execute(gql.gql("""
                query ListThreads($fgroup_id: String!) {
                    thread_list(located_fgroup_id: $fgroup_id, skip: 0, limit: 10) { ft_id ft_app_searchable }
                }"""), variable_values={"fgroup_id": self.fgroup_id})

            for thread in threads["thread_list"]:
                if thread["ft_app_searchable"].startswith("slack/"):
                    messages = await http.execute(gql.gql("""
                        query ThreadMessages($ft_id: String!) {
                            thread_messages_list(ft_id: $ft_id) { ftm_role ftm_content ftm_alt ftm_tool_calls }
                        }"""), variable_values={"ft_id": thread["ft_id"]})

                    logger.info(f"\n📝 ft_id: {thread['ft_id']} captured_from: {thread['ft_app_searchable']}")
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
            await self.print_captured_thread()
            logger.info(f"Waiting {cleanup_wait_secs} seconds before cleanup... (Ctrl+C to cleanup immediately)")
            await ckit_shutdown.wait(cleanup_wait_secs)
            await self.cleanup()
            logger.info("Cleanup completed.")

    async def cleanup(self) -> None:
        if self.fgroup_id:
            try:
                async with (await self.fclient.use_http()) as http:
                    await http.execute(gql.gql("""mutation($id:String!){group_delete(fgroup_id:$id)}"""), variable_values={"id": self.fgroup_id})
            except Exception as e:
                logger.warning(f"⚠️ Failed to delete test group {self.fgroup_name}: {e}")
