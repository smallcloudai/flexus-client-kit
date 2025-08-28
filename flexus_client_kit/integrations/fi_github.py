import os
import asyncio
import logging
import subprocess
import time
import datetime as _dt
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple

from github import GithubIntegration, Auth

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
    def _normalize_private_key(self, private_key: str) -> str:
        """Normalize private key format by ensuring proper newlines"""
        if not private_key.strip():
            return private_key
        
        # If the key doesn't have newlines but has the expected structure, restore them
        key = private_key.strip()
        if '-----BEGIN' in key and '-----END' in key and '\n' not in key:
            # Key is on one line with spaces, restore proper formatting
            import re
            # Replace spaces between base64 chunks with newlines, but preserve header/footer
            key = re.sub(r'(-----BEGIN[^-]+-----)\s+', r'\1\n', key)
            key = re.sub(r'\s+(-----END[^-]+-----)', r'\n\1', key)
            # Add newlines every 64 characters in the middle section
            lines = key.split('\n')
            if len(lines) >= 2:
                # Process the middle content (between header and footer)
                middle_content = ''.join(lines[1:-1])
                # Remove any existing spaces
                middle_content = middle_content.replace(' ', '')
                # Split into 64-character lines
                formatted_lines = [lines[0]]  # header
                for i in range(0, len(middle_content), 64):
                    formatted_lines.append(middle_content[i:i+64])
                formatted_lines.append(lines[-1])  # footer
                key = '\n'.join(formatted_lines)
        
        return key

    def __init__(self, fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext, GITHUB_APP_ID: str, GITHUB_INSTALLATION_ID: str, GITHUB_APP_PRIVATE_KEY: str, GITHUB_REPO: str):
        self.fclient = fclient
        self.rcx = rcx
        self.GITHUB_APP_ID = GITHUB_APP_ID
        self.GITHUB_INSTALLATION_ID = GITHUB_INSTALLATION_ID
        self.GITHUB_APP_PRIVATE_KEY = self._normalize_private_key(GITHUB_APP_PRIVATE_KEY)
        self.GITHUB_REPO = GITHUB_REPO
        self.problems_other = []
        # Token cache
        self._cached_token: Optional[str] = None
        self._cached_token_exp: Optional[float] = None
        # Do not call network on init: tokens are minted lazily
        try:
            int(self.GITHUB_APP_ID)
            int(self.GITHUB_INSTALLATION_ID)
        except Exception as e:
            logger.error(f"GitHub App configuration invalid: {type(e).__name__} {e}")
            self.problems_other.append(f"Invalid GitHub App configuration: {type(e).__name__} {e}")

    async def _mint_installation_token(self) -> Tuple[Optional[str], Optional[str]]:
        now = time.time()
        if self._cached_token and self._cached_token_exp and now < self._cached_token_exp - 300:
            return self._cached_token, None
        try:
            app_id = int(self.GITHUB_APP_ID)
            installation_id = int(self.GITHUB_INSTALLATION_ID)
            app_auth = Auth.AppAuth(app_id, self.GITHUB_APP_PRIVATE_KEY)
            gi = GithubIntegration(auth=app_auth)
            tok = gi.get_access_token(installation_id)
            token = tok.token
            exp = tok.expires_at
            if isinstance(exp, str):
                try:
                    exp_dt = _dt.datetime.fromisoformat(exp.replace('Z', '+00:00'))
                except Exception:
                    exp_dt = _dt.datetime.utcnow() + _dt.timedelta(minutes=50)
            else:
                exp_dt = exp
            self._cached_token = token
            self._cached_token_exp = exp_dt.timestamp() if hasattr(exp_dt, 'timestamp') else (now + 3600)
            return token, None
        except Exception as e:
            msg = f"Failed to mint installation token: {type(e).__name__} {e}"
            logger.error(msg, exc_info=True)
            self.problems_other.append(msg)
            return None, msg

    async def _prepare_gh_env(self) -> Tuple[Optional[dict], Optional[str]]:
        env = os.environ.copy()
        token = env.get("GH_TOKEN") or env.get("GITHUB_TOKEN")
        if not token:
            token, err = await self._mint_installation_token()
            if not token:
                return None, err or "Failed to obtain GH token"
        env["GH_TOKEN"] = token
        env["GITHUB_TOKEN"] = token
        if self.GITHUB_REPO:
            env["GH_REPO"] = self.GITHUB_REPO
        try:
            chk = subprocess.run(["gh", "auth", "status"], env=env, capture_output=True, text=True, timeout=TIMEOUT_S)
            if chk.returncode != 0:
                return None, (chk.stderr or chk.stdout)
        except subprocess.TimeoutExpired:
            return None, "Timeout during gh auth check"
        except Exception as e:
            return None, f"Auth check error: {e}"
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
