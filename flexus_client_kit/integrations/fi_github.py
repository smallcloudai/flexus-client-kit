import os
import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

import gql

from flexus_client_kit import ckit_cloudtool, ckit_client, ckit_bot_exec, gql_utils


logger = logging.getLogger("fi_github")

TIMEOUT_S = 15.0

GITHUB_TOOL = ckit_cloudtool.CloudTool(
    name="github",
    description=(
        "Interact with GitHub via the gh CLI. Provide full list of args as a JSON array , e.g ['issue', 'create', '--title', 'My title']"
    ),
    parameters={
        "type": "object",
        "properties": {
            "args": {
                "type": "array",
                "items": {"type": "string"},
                "description": "gh cli args list, e.g. ['issue', 'create', '--title', 'My title']"
            },
        },
        "required": ["args"]
    },
)


@dataclass
class FGitHubMintTokenOutput:
    token: str
    expires_at: str
    installation_id: str


class IntegrationGitHub:
    def __init__(self, fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext):
        self.fclient = fclient
        self.rcx = rcx
        self._cached_token: Optional[str] = None
        self._cached_token_exp: Optional[float] = None

    async def _mint_installation_token(self) -> str:
        now = time.time()
        if self._cached_token and self._cached_token_exp and now < self._cached_token_exp - 300:
            return self._cached_token
        http = await self.fclient.use_http()
        async with http as session:
            r = await session.execute(gql.gql(f"""
                mutation MintGithubToken($ws: String!) {{
                    external_auth_mint_github_token(ws_id: $ws) {{
                        {gql_utils.gql_fields(FGitHubMintTokenOutput)}
                    }}
                }}"""),
                variable_values={"ws": self.rcx.persona.ws_id},
            )
        out = r["external_auth_mint_github_token"]
        token = out["token"]
        if not token:
            raise RuntimeError("empty token from server")
        self._cached_token = token
        self._cached_token_exp = datetime.fromisoformat(out["expires_at"].replace("Z", "+00:00")).timestamp()
        return token

    async def _prepare_gh_env(self) -> Dict[str, str]:
        env = os.environ.copy()
        token = await self._mint_installation_token()
        env["GITHUB_TOKEN"] = token
        return env

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, List[str]]) -> str:
        env = await self._prepare_gh_env()
        if not isinstance(model_produced_args, dict) or "args" not in model_produced_args:
            return "Error: no args param found!"
        if not isinstance(model_produced_args["args"], list) or not all(isinstance(arg, str) for arg in model_produced_args["args"]):
            return "Error: args must be a list of str!"

        cmd = ["gh"] + model_produced_args["args"]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=TIMEOUT_S)
        except asyncio.TimeoutError:
            proc.kill()
            return "Timeout after %d seconds" % TIMEOUT_S
        if proc.returncode != 0:
            return f"Error: {stderr.decode() or stdout.decode()}"
        return stdout.decode()
