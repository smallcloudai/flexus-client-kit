import os
import asyncio
import logging
from typing import Dict, List

from flexus_client_kit.core import ckit_bot_exec, ckit_cloudtool, ckit_client


logger = logging.getLogger("fi_github")

TIMEOUT_S = 15.0

GITHUB_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
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
    def __init__(self, fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext, allowed_write_commands: List[List[str]] = []):
        self.fclient = fclient
        self.rcx = rcx
        self.allowed_write_commands = allowed_write_commands

    def is_read_only_command(self, args: List[str]) -> bool:
        if not args or args[0] in {"search", "status", "help", "--help", "-h", "version", "--version"}:
            return True
        READ_VERBS = {"view", "list", "status", "search", "browse", "show", "diff", "item-list", "field-list", "files"}
        return len(args) >= 2 and args[1] in READ_VERBS

    def _is_allowed_write_command(self, args: List[str]) -> bool:
        return any(len(args) >= len(a) and args[:len(a)] == a for a in self.allowed_write_commands)

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, List[str]], token: str, extra_env: Dict[str, str] = {}) -> str:
        if not (args := model_produced_args.get("args")):
            return "Error: no args param found!"
        if not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
            return "Error: args must be a list of str!"

        if not self.is_read_only_command(args) and not self._is_allowed_write_command(args) and not toolcall.confirmed_by_human:
            raise ckit_cloudtool.NeedsConfirmation(
                confirm_setup_key="github_write",
                confirm_command=f"gh {' '.join(args)}",
                confirm_explanation=f"This command will modify GitHub: gh {' '.join(args)}",
            )

        env = os.environ.copy()
        env["GITHUB_TOKEN"] = token
        env.update(extra_env)
        proc = await asyncio.create_subprocess_exec(
            *["gh"] + args,
            stdin=asyncio.subprocess.DEVNULL,
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
