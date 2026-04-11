import json
import logging
from typing import Any, Dict, Optional, Union
from contextlib import asynccontextmanager

import httpx
from exceptiongroup import BaseExceptionGroup
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("fi_mcp")


MCP_DATABASE = {  # "prefix": ("default_url", {"token_name": "default_value", ...}, "auth_provider"),
"context7": ("https://mcp.context7.com/mcp", {}),
"fibery": ("https://mcp.fibery.io/mcp", {"token": ""}, ["fibery_manual", "fibery"]),
}


def _unwrap_http_status(e: BaseException) -> int:
    # MCP client wraps HTTPStatusError in ExceptionGroup via anyio TaskGroup
    if isinstance(e, httpx.HTTPStatusError):
        return e.response.status_code
    if isinstance(e, BaseExceptionGroup):
        for exc in e.exceptions:
            s = _unwrap_http_status(exc)
            if s:
                return s
    return 0


class IntegrationMcp:
    def __init__(
        self,
        url: str,
        mcp_name: str,
        tokens: Optional[Dict[str, str]] = None,
    ):
        self.url = url.strip()
        self.mcp_name = mcp_name
        self.headers: Dict[str, str] = {}
        if tokens:
            for k, v in tokens.items():
                kl = k.lower()
                if kl in ("token", "bearer", "api_key"):
                    self.headers["Authorization"] = f"Bearer {v}"
                else:
                    self.headers[k] = v
        logger.info("AAAAAAAAAAAAAA3 %s", self.headers)
        self._use_sse = None  # auto-detected on first connect
        self._mcp_tools = []
        self._init_error = ""

    async def initialize(self):
        self._init_error = ""
        # Probe transport: try Streamable HTTP first, fall back to SSE on 4xx
        try:
            async with self._connect_streamable() as session:
                self._mcp_tools = (await session.list_tools()).tools
                self._use_sse = False
                logger.info("fi_mcp %s using streamable HTTP", self.url)
                return
        except (httpx.HTTPStatusError, BaseExceptionGroup) as e:
            status = _unwrap_http_status(e)
            if status == 401:
                self._init_error = "MCP server %s returned 401 Unauthorized, check your API key" % self.mcp_name
                logger.error(self._init_error)
                return
            if status not in (404, 405):
                raise
            logger.info("fi_mcp streamable HTTP got %d, trying SSE", status)
        try:
            async with self._connect_sse() as session:
                self._mcp_tools = (await session.list_tools()).tools
                self._use_sse = True
                logger.info("fi_mcp %s using SSE", self.url)
        except (httpx.HTTPStatusError, BaseExceptionGroup) as e:
            status = _unwrap_http_status(e)
            if status == 401:
                self._init_error = "MCP server %s returned 401 Unauthorized, check your API key" % self.mcp_name
                logger.error(self._init_error)
                return
            raise

    @classmethod
    def tool_desc(cls, n: str) -> ckit_cloudtool.CloudTool:
        return ckit_cloudtool.CloudTool(
            strict=False,
            name=f"mcp_{n}",
            description=f"MCP server {n}, start with op=\"list\", you will see the list of available functions, continue with op=\"help\" name=\"function_of_interest\".",
            parameters={
                "type": "object",
                "properties": {
                    "op": {"type": "string", "enum": ["list", "help", "call"]},
                    "name": {"type": "string", "description": "Name of the function"},
                    "args": {"type": "object", "description": "Arguments of a call, use op=\"help\" first to find what the arguments should be."},
                },
            },
        )

    async def handle_tool_call(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        if self._init_error:
            return self._init_error
        op = (model_produced_args or {}).get("op", "help")
        args = (model_produced_args or {}).get("args", {})
        name = (model_produced_args or {}).get("name", "")

        if op == "list":
            if not self._mcp_tools:
                return "No tools available"
            lines = [json.dumps({"tool": t.name, "description": (t.description or "")[:50] + ("\u2026" if len(t.description or "") > 50 else "")}, ensure_ascii=False) for t in self._mcp_tools]
            return "\n".join(lines)

        if op == "help":
            if not name:
                return "Missing name parameter\n"
            for t in self._mcp_tools:
                if t.name == name:
                    entry = {"tool": t.name, "description": t.description or "", "args_schema": t.inputSchema}
                    if t.annotations:
                        entry["annotations"] = t.annotations.model_dump(exclude_none=True)
                    return json.dumps(entry, indent=2, ensure_ascii=False)
            return f"Unknown tool '{name}'\n"

        if op == "call":
            if not name:
                return "Missing name parameter\n"
            logger.info("fi_mcp calling %s on %s", name, self.url)
            async with self._connect() as session:
                result = await session.call_tool(name, args or {})
                # XXX handle multimodal content (images etc) when needed
                text = result.content[0].text if result.content and hasattr(result.content[0], "text") else ""
                logger.info("fi_mcp %s done, %d chars", name, len(text))
                return text

        return f"Unknown op '{op}', use help/list/call\n"

    @asynccontextmanager
    async def _connect_streamable(self):
        h = self.headers or None
        client = httpx.AsyncClient(headers=h, timeout=httpx.Timeout(15))
        async with streamable_http_client(self.url, http_client=client) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                yield session

    @asynccontextmanager
    async def _connect_sse(self):
        h = self.headers or None
        async with sse_client(self.url, headers=h, timeout=15) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                yield session

    @asynccontextmanager
    async def _connect(self):
        if self._use_sse is None:
            raise RuntimeError("call initialize() before using MCP integration")
        ctx = self._connect_sse() if self._use_sse else self._connect_streamable()
        async with ctx as session:
            yield session


def _mcp_token_from_external_auth(ext: dict, providers: list[str]) -> str:
    for provider in providers:
        raw = ext.get(provider)
        if not isinstance(raw, dict):
            continue
        # manual auth: api_key at top level
        v = (raw.get("api_key") or "").strip()
        if v:
            return v
        # OAuth: access_token inside token dict
        tok = raw.get("token")
        if isinstance(tok, dict):
            v = (tok.get("access_token") or "").strip()
            if v:
                return v
    return ""


def _validate_names(names: list[str]):
    for n in names:
        if n not in MCP_DATABASE:
            raise ValueError(f"Unknown MCP server {n!r}, known: {list(MCP_DATABASE.keys())}")


def mcp_setup_schema(names: list[str], bs_group: str = "MCP", bs_order_start: int = 100) -> list[Dict[str, Union[str, int]]]:
    _validate_names(names)
    schema = []
    for i, n in enumerate(names):
        entry = MCP_DATABASE[n]
        default_url, default_tokens = entry[0], entry[1]
        schema.append({
            "bs_name": f"mcp_{n}_url",
            "bs_type": "string_long",
            "bs_default": default_url,
            "bs_group": bs_group,
            "bs_order": bs_order_start + i * 10,
            "bs_importance": 0,
            "bs_description": f"MCP server URL for {n}",
        })
        for tk, tv in default_tokens.items():
            schema.append({
                "bs_name": f"mcp_{n}_{tk}",
                "bs_type": "string_long",
                "bs_default": tv,
                "bs_group": bs_group,
                "bs_order": bs_order_start + i * 10 + 1,
                "bs_importance": 0,
                "bs_description": f"Token '{tk}' for {n} MCP server",
            })
    return schema


def mcp_tools(names: list[str]) -> list[ckit_cloudtool.CloudTool]:
    _validate_names(names)
    return [IntegrationMcp.tool_desc(n) for n in names]


async def mcp_launch(names: list[str], rcx: ckit_bot_exec.RobotContext, setup: Dict[str, Any]) -> None:
    _validate_names(names)
    for n in names:
        entry = MCP_DATABASE[n]
        default_url, default_tokens = entry[0], entry[1]
        auth_providers = entry[2] if len(entry) > 2 else []
        if isinstance(auth_providers, str):
            auth_providers = [auth_providers]
        url = setup.get(f"mcp_{n}_url", default_url)
        if not url:
            async def _not_configured(toolcall, args, _n=n):
                return f"MCP server {_n} is not configured, set mcp_{_n}_url in bot setup"
            rcx.on_tool_call(f"mcp_{n}")(_not_configured)
            continue
        tokens = {}
        for tk in default_tokens:
            v = ""
            if auth_providers and tk in ("token", "bearer", "api_key"):
                v = _mcp_token_from_external_auth(rcx.external_auth, auth_providers)
            if not v:
                v = setup.get(f"mcp_{n}_{tk}", default_tokens[tk])
            if v:
                tokens[tk] = v
        logger.info("AAAAAAAAAAAAAA2 %s %s", n, str(tokens))
        mcp = IntegrationMcp(url=url, tokens=tokens or None, mcp_name=n)
        await mcp.initialize()
        rcx.on_tool_call(f"mcp_{n}")(mcp.handle_tool_call)
        logger.info("mcp launched %s -> %s", n, url)


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)

    async def trivial_test():
        mcp = IntegrationMcp(
            url="https://mcp.context7.com/mcp",
            mcp_name="context7",
        )
        await mcp.initialize()
        listing = await mcp.handle_tool_call(None, {"op": "list"})
        print("-"*40, "list", "-"*40)
        print(listing)
        for line in listing.strip().split("\n"):
            print("-"*40, "help", "-"*40)
            name = json.loads(line)["tool"]
            print(await mcp.handle_tool_call(None, {"op": "help", "name": name}))
        print("-"*40, "call", "-"*40)
        print(await mcp.handle_tool_call(None, {"op": "call", "name": "resolve-library-id", "args": {"query": "python mcp client", "libraryName": "mcp"}}))

    asyncio.run(trivial_test())
