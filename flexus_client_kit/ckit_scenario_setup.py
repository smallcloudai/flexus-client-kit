import tempfile
import time
import uuid
from typing import Optional

import gql
from PIL import Image
from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_bot_exec, ckit_bot_install, ckit_client, ckit_mongo


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


async def create_test_group(fclient: ckit_client.FlexusClient, ws: ckit_client.FWorkspaceOutput, prefix: str = "test") -> str:
    async with (await fclient.use_http()) as http:
        return (await http.execute(
            gql.gql("""mutation($input: FlexusGroupInput!){group_create(input:$input){fgroup_id}}"""),
            variable_values={"input": {"fgroup_name": f"{prefix}-{uuid.uuid4().hex[:6]}", "fgroup_parent_id": ws.ws_root_group_id}},
        ))["group_create"]["fgroup_id"]


async def install_persona(
    fclient: ckit_client.FlexusClient,
    bs: ckit_client.BasicStuffOutput,
    ws: ckit_client.FWorkspaceOutput,
    fgroup_id: str,
    persona_name: str,
    name: Optional[str] = None,
    setup: Optional[dict] = None,
    require_dev: bool = False
) -> ckit_bot_exec.FPersonaOutput:
    args = {
        "client": fclient, "ws_id": ws.ws_id, "inside_fgroup": fgroup_id,
        "persona_marketable_name": persona_name, "new_setup": setup or {},
        "persona_name": name or f"{persona_name} Test {fgroup_id[-4:]}"
    }

    try:
        install = await ckit_bot_install.bot_install_from_marketplace(**args, install_dev_version=True)
    except Exception as e:
        if require_dev:
            raise e
        install = await ckit_bot_install.bot_install_from_marketplace(**args, install_dev_version=False)

    async with (await fclient.use_http()) as http:
        persona_details = await http.execute(gql.gql("""
            query PersonaGet($id: String!) {
                persona_get(id: $id) {
                    persona_marketable_version
                }
            }"""), variable_values={"id": install.persona_id})

    return ckit_bot_exec.FPersonaOutput(
        owner_fuser_id=bs.fuser_id, located_fgroup_id=fgroup_id, persona_id=install.persona_id,
        persona_name=args["persona_name"], persona_marketable_name=persona_name,
        persona_marketable_version=persona_details["persona_get"]["persona_marketable_version"], persona_discounts=None,
        persona_setup=dict(setup or {}), persona_created_ts=time.time(),
        ws_id=ws.ws_id, ws_timezone="UTC"
    )


async def setup_test_files_in_mongo(bot_fclient: ckit_client.FlexusClient, persona_id: str, workdir: str) -> AsyncMongoClient:
    import os
    os.makedirs(workdir, exist_ok=True)
    Image.new('RGB', (100, 100), color='red').save(f'{workdir}/1.png')
    Image.new('RGB', (100, 100), color='blue').save(f'{workdir}/2.png')
    open(f'{workdir}/1.txt', 'w').write('This is test file 1\nWith multiple lines\nFor testing file attachments')
    open(f'{workdir}/2.json', 'w').write('{"test": "data", "file": "2", "content": "json test file"}')

    mongo_collection = AsyncMongoClient(await ckit_mongo.get_mongodb_creds(bot_fclient, persona_id))[persona_id + "_db"]["files"]
    for filename in ['1.png', '2.png', '1.txt', '2.json']:
        with open(f'{workdir}/{filename}', 'rb') as f:
            await ckit_mongo.store_file(mongo_collection, filename, f.read())
    return mongo_collection


async def cleanup_test_group(fclient: ckit_client.FlexusClient, fgroup_id: str) -> None:
    try:
        async with (await fclient.use_http()) as http:
            await http.execute(gql.gql("""mutation($id:String!){group_delete(fgroup_id:$id)}"""), variable_values={"id": fgroup_id})
    except Exception as e:
        print(f"⚠️ Failed to delete test group {fgroup_id}: {e}")


class ScenarioSetup:
    def __init__(self, service_name: str = "test_scenario"):
        self.fclient = ckit_client.FlexusClient(service_name=service_name)
        self.bot_fclient = ckit_client.FlexusClient(service_name=f"{service_name}_bot", endpoint="/v1/jailed-bot")
        self.fgroup_id: Optional[str] = None

    async def setup(
        self,
        persona_name: str,
        setup: Optional[dict] = None,
        require_dev: bool = False,
        prefix: str = "test"
    ) -> tuple[ckit_bot_exec.RobotContext, AsyncMongoClient]:
        bs = await ckit_client.query_basic_stuff(self.fclient)
        ws = await select_workspace(self.fclient, bs, persona_name, require_dev)
        self.fgroup_id = await create_test_group(self.fclient, ws, prefix)
        persona = await install_persona(self.fclient, bs, ws, self.fgroup_id, persona_name, setup=setup, require_dev=require_dev)
        rcx = ckit_bot_exec.RobotContext(self.bot_fclient, persona)
        return rcx, await setup_test_files_in_mongo(self.bot_fclient, persona.persona_id, rcx.workdir)

    async def cleanup(self) -> None:
        if self.fgroup_id:
            await cleanup_test_group(self.fclient, self.fgroup_id)
