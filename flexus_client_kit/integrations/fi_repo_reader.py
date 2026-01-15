import os
import logging
import time
import subprocess
import tempfile
from typing import Dict, Any, Optional

from flexus_client_kit import ckit_cloudtool, ckit_github, ckit_devenv, ckit_bot_exec
from flexus_client_kit.integrations import fi_localfile

logger = logging.getLogger("repo_file")

REPO_CACHE_DIR = os.path.join(tempfile.gettempdir(), "flexus_repos")
REPO_REFRESH_TIMEOUT = 600

_repo_last_access: Dict[str, float] = {}


REPO_READER_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="repo_reader",
    description="Read files from github repositories, call with op=help for usage",
    parameters={
        "type": "object",
        "properties": {
            "op": {
                "type": "string",
                "enum": ["help", "cat", "find", "grep", "ls"],
                "description": "Operation: cat (read file), find (glob search), grep (regex search), ls (list dir)",
            },
            "args": {
                "type": "object",
                "additionalProperties": False,
                "description": "All arguments required, set to null if not used for this operation",
                "properties": {
                    "repo": {"type": "string", "description": "GitHub URL or owner/repo"},
                    "branch": {"type": ["string", "null"], "description": "Branch name, defaults to repo default"},
                    "path": {"type": ["string", "null"], "description": "File or directory path"},
                    "lines_range": {"type": ["string", "null"], "description": "Line range for cat: '1:20', ':20', '21:'"},
                    "safety_valve": {"type": ["string", "null"], "description": "Max output size for cat, e.g. '10k'"},
                    "pattern": {"type": ["string", "null"], "description": "Glob pattern for find, regex for grep"},
                    "recursive": {"type": ["boolean", "null"], "description": "Recursive grep search, default true"},
                    "include": {"type": ["string", "null"], "description": "File glob filter for grep, e.g. '*.py'"},
                    "context": {"type": ["integer", "null"], "description": "Context lines around grep matches"},
                },
                "required": ["repo", "branch", "path", "lines_range", "safety_valve", "pattern", "recursive", "include", "context"],
            },
        },
        "required": ["op", "args"],
        "additionalProperties": False,
    },
)

HELP_EXAMPLES = r"""
Required in args: repo (github URL)
Optional in args: branch (defaults to repository's default branch)

Examples:
  repo_reader(op="cat", args={"repo": "https://github.com/owner/name", "path": "src/main.py", "lines_range": "1:20"})
  repo_reader(op="find", args={"repo": "https://github.com/owner/name", "branch": "dev", "pattern": "*.py"})
  repo_reader(op="grep", args={"repo": "https://github.com/owner/name", "pattern": "TODO", "context": 2, "include": "*.py"})
  repo_reader(op="ls", args={"repo": "https://github.com/owner/name", "path": "src"})
"""

HELP = fi_localfile.HELP_TEXT + "\n" + HELP_EXAMPLES


async def _ensure_repo_cached(repo_url: str, branch: Optional[str], github_token: Optional[ckit_github.GhRepoToken], persona_id: str) -> str:
    if not (repo_path := ckit_github.extract_repo_path_from_url(repo_url)):
        raise ValueError(f"Invalid repo URL: {repo_url}")

    cache_key = f"{persona_id}/{repo_path}/{branch}" if branch else f"{persona_id}/{repo_path}"
    cache_path = os.path.join(REPO_CACHE_DIR, cache_key)
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    token_part = f"oauth2:{github_token.token}@" if github_token else ""
    clone_url = f"https://{token_part}github.com/{repo_path}.git"

    needs_clone = not os.path.exists(cache_path)
    needs_pull = not needs_clone and time.time() - _repo_last_access.get(cache_key, 0) > REPO_REFRESH_TIMEOUT

    if needs_clone:
        logger.info(f"{cache_path} Cloning {cache_key}...")
        cmd = ["git", "clone", "--depth", "1"] + (["--branch", branch] if branch else []) + [clone_url, cache_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to clone {cache_key}: {result.stderr}")
    elif needs_pull:
        logger.info(f"{cache_path} Pulling latest changes for {cache_key}...")
        result = subprocess.run(["git", "pull"], capture_output=True, text=True, cwd=cache_path)
        if result.returncode != 0:
            logger.info(f"Failed to pull {cache_key}: {result.stderr}", exc_info=True)

    _repo_last_access[cache_key] = time.time()
    return cache_path


async def handle_repo_reader(
    rcx: ckit_bot_exec.RobotContext,
    model_produced_args: Dict[str, Any],
) -> str:
    op = model_produced_args.get("op", "")
    if not op or "help" in op:
        return HELP + "\n\n" + await ckit_devenv.format_devenv_list(rcx.fclient, rcx.persona.located_fgroup_id)

    args = model_produced_args.get("args", {})
    if not (repo_input := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "repo", "")):
        return "Error: repo parameter is required\n\n" + HELP + "\n\n" + await ckit_devenv.format_devenv_list(rcx.fclient, rcx.persona.located_fgroup_id)

    repo_url = repo_input if repo_input.startswith(("https://", "git@")) else f"https://github.com/{repo_input}"
    gh_token = await ckit_github.get_github_token_with_cache(rcx.fclient, rcx.persona.located_fgroup_id, repo_url)
    branch = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "branch", None)
    try:
        cache_path = await _ensure_repo_cached(repo_url, branch, gh_token, rcx.persona.persona_id)
    except ValueError as e:
        return f"{e}\n\n" + await ckit_devenv.format_devenv_list(rcx.fclient, rcx.persona.located_fgroup_id)
    except (RuntimeError, OSError, subprocess.SubprocessError) as e:
        logger.info(f"Could not access repo {repo_url}: {e}", exc_info=True)
        return f"Error accessing repository: {e}\n\n" + await ckit_devenv.format_devenv_list(rcx.fclient, rcx.persona.located_fgroup_id)

    return await fi_localfile.handle_localfile(cache_path, model_produced_args)
