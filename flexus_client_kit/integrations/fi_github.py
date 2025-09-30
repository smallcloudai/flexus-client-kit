import os
import asyncio
import aiofiles
import logging
from typing import Dict, List, Optional

from flexus_client_kit import ckit_bot_exec, ckit_cloudtool


logger = logging.getLogger("fi_github")

TIMEOUT_S = 15.0

GITHUB_TOOL = ckit_cloudtool.CloudTool(
    name="github",
    description=(
        "Interact with GitHub via the gh CLI. Provide full list of args as a JSON array , e.g ['issue', 'create', '--title', 'My title']"
        "Optionally provide path to .env file for GH_TOKEN"
    ),
    parameters={
        "type": "object",
        "properties": {
            "args": {
                "type": "array",
                "items": {"type": "string"},
                "description": "gh cli args list, e.g. ['issue', 'create', '--title', 'My title']"
            },
            "env": {
                "type": "string",
                "description": "path/to/env file"
            }
        },
        "required": ["args"]
    },
)

class IntegrationGithub:
    def __init__(self, rcx: ckit_bot_exec.RobotContext, token: Optional[str]=None):
        self.rcx = rcx
        self.token = token

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, List[str]]) -> str:
        if not isinstance(model_produced_args, dict) or "args" not in model_produced_args:
            return "Error: no args param found!"
        if not isinstance(model_produced_args["args"], list) or not all(isinstance(arg, str) for arg in model_produced_args["args"]):
            return "Error: args must be a list of str!"

        if "env" in model_produced_args: 
            env_path = os.path.join(self.rcx.workdir, model_produced_args["env"])
            if not os.path.isfile(env_path):
                return "Error: env does not exist or is not a file"
            async with aiofiles.open(env_path, "r") as f:
                token = None
                async for line in f:
                    line = line.strip()
                    if line.startswith(("GH_TOKEN=", "GITHUB_TOKEN=")) :
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
            if not token:
                return "Error: GH_TOKEN not found in env file"

        elif self.token:
            token = self.token
        else: 
            return "Error: no token configured, provide path to env in args"
        env = os.environ.copy()
        env["GITHUB_TOKEN"] = token
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
        output_str = stdout.decode()
        if output_str == "": # sometimes no output non-tty
            output_str = "NO OUTPUT"
        return output_str
