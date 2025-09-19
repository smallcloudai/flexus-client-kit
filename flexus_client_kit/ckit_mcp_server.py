import time
import json
import asyncio
import logging
from typing import Optional
from dataclasses import dataclass

import gql

from flexus_client_kit import ckit_client, gql_utils

logger = logging.getLogger("mcp_server")


@dataclass
class FMcpServerOutput:
    owner_fuser_id: str
    owner_shared: bool
    located_fgroup_id: str
    mcp_id: str
    mcp_name: str
    mcp_command: str
    mcp_description: str
    mcp_preinstall_script: str
    mcp_enabled: bool
    mcp_env_vars: Optional[dict]
    mcp_created_ts: float
    mcp_modified_ts: float


async def create_mcp(
    fclient: ckit_client.FlexusClient,
    located_fgroup_id: str,
    mcp_name: str,
    mcp_command: str,
    mcp_description: str = "",
    mcp_preinstall_script: str = "",
    mcp_env_vars: Optional[dict] = None
) -> FMcpServerOutput:
    async with (await fclient.use_http()) as http:
        resp = await http.execute(gql.gql(f"""mutation CreateMCP($input: FMcpServerInput!) {{
            mcp_server_create(input: $input) {{ {gql_utils.gql_fields(FMcpServerOutput)} }}
        }}"""), variable_values={"input": {
            "located_fgroup_id": located_fgroup_id,
            "mcp_name": mcp_name,
            "mcp_command": mcp_command,
            "mcp_description": mcp_description,
            "mcp_enabled": True,
            "mcp_preinstall_script": mcp_preinstall_script,
            "owner_shared": True,
            "mcp_env_vars": json.dumps(mcp_env_vars or {})
        }})
    return gql_utils.dataclass_from_dict(resp["mcp_server_create"], FMcpServerOutput)


async def wait_for_mcp(fclient: ckit_client.FlexusClient, mcp_id: str, timeout: int = 600) -> bool:
    logger.info("Waiting for MCP server to be ready...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        async with (await fclient.use_http()) as http:
            resp = await http.execute(gql.gql("""query GetMCP($id: String!) {
                mcp_server_get(id: $id) { mcp_status }
            }"""), variable_values={"id": mcp_id})
        if resp["mcp_server_get"]["mcp_status"] == "RUNNING":
            logger.info("✓ MCP server is ready")
            return True
        await asyncio.sleep(2)
    logger.warning("⚠️ MCP server failed to start within timeout")
    return False