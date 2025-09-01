import os
import asyncio
import logging
import subprocess
import time
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple

import gql

from flexus_client_kit import ckit_cloudtool, ckit_client, ckit_bot_exec


logger = logging.getLogger("github")

TIMEOUT_S=15.0

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
class IntegrationGitHub:
    def __init__(self, fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext, AUTH_ID: str):
        self.fclient = fclient
        self.rcx = rcx
        self.AUTH_ID = AUTH_ID
        self.problems_other = []
        self._cached_token: Optional[str] = None
        self._cached_token_exp: Optional[float] = None

    async def _mint_installation_token(self) -> Tuple[Optional[str], Optional[str]]:
        now = time.time()
        if self._cached_token and self._cached_token_exp and now < self._cached_token_exp - 300:
            return self._cached_token, None
        try:
            http = await self.fclient.use_http()
            async with http as session:
                r = await session.execute(
                    gql.gql(
                        """
                        mutation Mint($ws: String!, $auth_id: String!) {
                          external_service_auth_mint_github_token(ws_id: $ws, auth_id: $auth_id) {
                            access_token
                            installation_id
                          }
                        }
                        """
                    ),
                    variable_values={
                        "ws": self.rcx.persona.ws_id,
                        "auth_id": self.AUTH_ID
                    },
                )
            out = r["external_service_auth_mint_github_token"]
            token = out["access_token"]
            if not token:
                return None, "empty token from server"
            self._cached_token = token
            self._cached_token_exp = now + 3600
            return token, None
        except Exception as e:
            msg = f"Failed to mint installation token: {type(e).__name__} {e}"
            logger.error(msg, exc_info=True)
            self.problems_other.append(msg)
            return None, msg

    async def _prepare_gh_env(self) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
        env = os.environ.copy()
        token, err = await self._mint_installation_token()
        if not token:
            return None, err
        env["GITHUB_TOKEN"] = token
        return env, None

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, List[str]]) -> str:
        env, err = await self._prepare_gh_env()
        if err:
            return f"Error: {err}"
        if not isinstance(model_produced_args, dict) or "args" not in model_produced_args:
            return "Error: no args param found!"
        if not isinstance(model_produced_args["args"], list) or not all(isinstance(arg, str) for arg in model_produced_args["args"]):
            return "Error: args must be a list of str!"
        
        cmd = ["gh"] + model_produced_args["args"]
        try:
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
                return "TimeoutError!"
        except Exception as e:
            return f"Error: {e}"
        if proc.returncode != 0:
            return f"Error: {stderr.decode() or stdout.decode()}"
        return stdout.decode()
