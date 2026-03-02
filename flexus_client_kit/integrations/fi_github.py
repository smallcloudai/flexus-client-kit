import json
import os
import asyncio
import logging
from typing import Any, Dict, List

import httpx

from flexus_client_kit import ckit_bot_exec, ckit_cloudtool, ckit_client


logger = logging.getLogger("fi_github")

TIMEOUT_S = 15.0

PROVIDER_NAME = "github"
METHOD_IDS = [
    "github.search.repositories.v1",
    "github.search.issues.v1",
    "github.repos.get.v1",
]

_BASE_URL = "https://api.github.com"


class IntegrationGithub:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _get_api_key(self) -> str:
        if self.rcx is not None:
            return (self.rcx.external_auth.get("github") or {}).get("api_key", "")
        return os.environ.get("GITHUB_TOKEN", "")

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Dict[str, Any],
    ) -> str:
        args = model_produced_args or {}
        op = str(args.get("op", "help")).strip()
        if op == "help":
            return (
                f"provider={PROVIDER_NAME}\n"
                "op=help | status | list_methods | call\n"
                f"methods: {', '.join(METHOD_IDS)}"
            )
        if op == "status":
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "status": "available", "method_count": len(METHOD_IDS)}, indent=2, ensure_ascii=False)
        if op == "list_methods":
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_ids": METHOD_IDS}, indent=2, ensure_ascii=False)
        if op != "call":
            return "Error: unknown op. Use help/status/list_methods/call."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_IDS:
            return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)
        return await self._dispatch(method_id, call_args)

    def _make_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Flexus-Market-Signal/1.0",
        }
        token = self._get_api_key()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        if method_id == "github.search.repositories.v1":
            return await self._search_repositories(args)
        if method_id == "github.search.issues.v1":
            return await self._search_issues(args)
        if method_id == "github.repos.get.v1":
            return await self._repos_get(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _search_repositories(self, args: Dict[str, Any]) -> str:
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "args.query required."}, indent=2, ensure_ascii=False)
        language = str(args.get("language", ""))
        if language:
            query = f"{query}+language:{language}"
        sort = str(args.get("sort", "stars"))
        limit = min(int(args.get("limit", 20)), 100)
        params: Dict[str, Any] = {"q": query, "sort": sort, "order": "desc", "per_page": limit}
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(_BASE_URL + "/search/repositories", params=params, headers=self._make_headers())
            if r.status_code == 403 and "rate limit" in r.text.lower():
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "message": "GitHub rate limit exceeded. Set GITHUB_TOKEN env var for higher limits (5000 req/hr vs 60)."}, indent=2, ensure_ascii=False)
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            items = data.get("items", [])
            include_raw = bool(args.get("include_raw"))
            out: Dict[str, Any] = {"ok": True, "total_count": data.get("total_count", len(items)), "results": items if include_raw else [
                {
                    "full_name": repo.get("full_name"),
                    "description": repo.get("description"),
                    "stars": repo.get("stargazers_count"),
                    "forks": repo.get("forks_count"),
                    "language": repo.get("language"),
                    "updated_at": repo.get("updated_at"),
                    "url": repo.get("html_url"),
                }
                for repo in items
            ]}
            summary = f"Found {data.get('total_count', len(items))} repositories on GitHub for '{args.get('query')}'."
            return summary + "\n\n```json\n" + json.dumps(out, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _search_issues(self, args: Dict[str, Any]) -> str:
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "args.query required."}, indent=2, ensure_ascii=False)
        limit = min(int(args.get("limit", 20)), 100)
        params: Dict[str, Any] = {"q": query, "sort": "created", "order": "desc", "per_page": limit}
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(_BASE_URL + "/search/issues", params=params, headers=self._make_headers())
            if r.status_code == 403 and "rate limit" in r.text.lower():
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "message": "GitHub rate limit exceeded. Set GITHUB_TOKEN env var for higher limits."}, indent=2, ensure_ascii=False)
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            items = data.get("items", [])
            include_raw = bool(args.get("include_raw"))
            out: Dict[str, Any] = {"ok": True, "total_count": data.get("total_count", len(items)), "results": items if include_raw else [
                {
                    "title": issue.get("title"),
                    "state": issue.get("state"),
                    "comments": issue.get("comments"),
                    "created_at": issue.get("created_at"),
                    "repository_url": issue.get("repository_url"),
                    "url": issue.get("html_url"),
                }
                for issue in items
            ]}
            summary = f"Found {data.get('total_count', len(items))} issues on GitHub for '{args.get('query')}'."
            return summary + "\n\n```json\n" + json.dumps(out, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _repos_get(self, args: Dict[str, Any]) -> str:
        owner = str(args.get("owner", ""))
        repo = str(args.get("repo", ""))
        if not owner or not repo:
            query = str(args.get("query", ""))
            if "/" in query:
                parts = query.split("/", 1)
                owner, repo = parts[0].strip(), parts[1].strip()
        if not owner or not repo:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "Provide args.owner+args.repo or args.query as 'owner/repo'."}, indent=2, ensure_ascii=False)
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(f"{_BASE_URL}/repos/{owner}/{repo}", headers=self._make_headers())
            if r.status_code == 404:
                return json.dumps({"ok": False, "error_code": "NOT_FOUND", "message": f"Repository {owner}/{repo} not found."}, indent=2, ensure_ascii=False)
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            include_raw = bool(args.get("include_raw"))
            result = data if include_raw else {
                "full_name": data.get("full_name"),
                "description": data.get("description"),
                "stars": data.get("stargazers_count"),
                "forks": data.get("forks_count"),
                "open_issues": data.get("open_issues_count"),
                "language": data.get("language"),
                "license": (data.get("license") or {}).get("spdx_id"),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "url": data.get("html_url"),
                "topics": data.get("topics", []),
            }
            summary = f"Repository {owner}/{repo} from {PROVIDER_NAME}."
            return summary + "\n\n```json\n" + json.dumps({"ok": True, "result": result}, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

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
