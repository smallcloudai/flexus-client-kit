import os
import asyncio
import logging
from typing import Dict, List, Optional

from flexus_client_kit import ckit_bot_exec, ckit_cloudtool


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
                "description": "gh cli args list, e.g. ['issue', 'view', '5']"
            },
        },
        "required": ["args"]
    },
)


class IntegrationGitHub:
    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx: ckit_bot_exec.RobotContext,
        allowed_write_commands: List[List[str]] = [],
        token: Optional[str] = None,
        extra_env: Optional[Dict[str, str]] = None,
    ):
        self.fclient = fclient
        self.rcx = rcx
        self.allowed_write_commands = allowed_write_commands
        self._cached_token: Optional[str] = None
        self._cached_token_exp: Optional[float] = None

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, List[str]], token: str) -> str:
        if not isinstance(model_produced_args, dict) or "args" not in model_produced_args:
            return "Error: no args param found!"
        if not isinstance(model_produced_args["args"], list) or not all(isinstance(arg, str) for arg in model_produced_args["args"]):
            return "Error: args must be a list of str!"

        token = token or self.token
        if not token:
            return "Error: no token configured"
        env = os.environ.copy()
        env["GITHUB_TOKEN"] = token
        cmd = ["gh"] + model_produced_args["args"]
        proc = await asyncio.create_subprocess_exec(
            *["gh"] + args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=TIMEOUT_S)
        except asyncio.TimeoutError:
            proc.kill()
            return "Timeout after %d seconds" % TIMEOUT_S
        return stdout.decode() or "NO OUTPUT" if proc.returncode == 0 else f"Error: {stderr.decode() or stdout.decode()}"

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, List[str]]) -> str:
        if not isinstance(model_produced_args, dict) or "args" not in model_produced_args:
            return "Error: no args param found!"
        if not isinstance(model_produced_args["args"], list) or not all(isinstance(arg, str) for arg in model_produced_args["args"]):
            return "Error: args must be a list of str!"

        args = model_produced_args["args"]
        if not self.is_read_only_command(args) and not self._is_allowed_write_command(args) and not toolcall.confirmed_by_human:
            raise ckit_cloudtool.NeedsConfirmation(
                confirm_setup_key="github_write",
                confirm_command=f"gh {' '.join(args)}",
                confirm_explanation=f"This command will modify GitHub: gh {' '.join(args)}",
            )
        return await self._execute_gh_command(args)
