import json
import logging
from typing import Any, Dict, Optional
from contextlib import asynccontextmanager

import httpx
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("fi_mcp")


class IntegrationMcp:
    def __init__(
        self,
        url: str,
        tokens: Optional[Dict[str, str]] = None,
        tool_prefix: str = "mcp",
    ):
        self.url = url.strip()
        self.tool_prefix = tool_prefix
        self.headers: Dict[str, str] = {}
        if tokens:
            for k, v in tokens.items():
                if k.lower() in ("token", "bearer", "api_key"):
                    self.headers["Authorization"] = f"Bearer {v}"
                else:
                    self.headers[k] = v
        self._use_sse = None  # auto-detected on first connect
        self._mcp_tools = []

    async def initialize(self):
        # Probe transport: try Streamable HTTP first, fall back to SSE on 4xx
        try:
            async with self._connect_streamable() as session:
                self._mcp_tools = (await session.list_tools()).tools
                self._use_sse = False
                logger.info("fi_mcp %s using streamable HTTP", self.url)
                return
        except httpx.HTTPStatusError as e:
            if e.response.status_code not in (404, 405):
                raise
            logger.info("fi_mcp streamable HTTP got %d, trying SSE", e.response.status_code)
        async with self._connect_sse() as session:
            self._mcp_tools = (await session.list_tools()).tools
            self._use_sse = True
            logger.info("fi_mcp %s using SSE", self.url)

    @classmethod
    def tool_desc(cls, tool_prefix: str) -> ckit_cloudtool.CloudTool:
        return ckit_cloudtool.CloudTool(
            strict=False,
            name=f"{tool_prefix}",
            description=f"MCP server {tool_prefix}, start with op=\"list\", you will see the list of available functions, continue with op=\"help\" name=\"function_of_interest\".",
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


class ManyMCPsDeclaration:
    def __init__(self, names: list[str]):
        self.names = names
        self._integrations: Dict[str, IntegrationMcp] = {}

    def tools(self) -> list[ckit_cloudtool.CloudTool]:
        return [IntegrationMcp.tool_desc(n) for n in self.names]

    async def launch(self, rcx) -> None:
        for n in self.names:
            mcp = IntegrationMcp(url=n["url"], tokens=n.get("tokens"), tool_prefix=n["tool_prefix"])
            await mcp.initialize()
            self._integrations[n["tool_prefix"]] = mcp
            rcx._handler_per_tool[n["tool_prefix"]] = mcp.handle_tool_call
            logger.info("fi_mcp registered %s -> %s", n["tool_prefix"], n["url"])


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)

    async def trivial_test():
        mcp = IntegrationMcp(
            url="https://mcp.context7.com/mcp",
            tool_prefix="context7",
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
