import json
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import httpx
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("fi_mcp")


# def _looks_strict(schema: dict) -> bool:
#     if schema.get("additionalProperties") is not False:
#         return False
#     props = schema.get("properties", {})
#     required = set(schema.get("required", []))
#     return bool(props) and required == set(props.keys())


# def _mcp_tool_to_cloudtool(prefix: str, t) -> ckit_cloudtool.CloudTool:
#     return ckit_cloudtool.CloudTool(
#         strict=_looks_strict(t.inputSchema),
#         name=f"{prefix}_{t.name}",
#         description=t.description or t.name,
#         parameters=t.inputSchema,
#     )


class IntegrationMcp:
    def __init__(
        self,
        url: str,
        tokens: Optional[Dict[str, str]] = None,
        tool_prefix: str = "mcp",
        timeout: float = 30,
    ):
        self.url = url.strip()
        self.tool_prefix = tool_prefix
        self.timeout = timeout
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

    def list_tools_tool(self) -> ckit_cloudtool.CloudTool:
        return ckit_cloudtool.CloudTool(
            strict=True,
            name=f"{self.tool_prefix}_list_tools",
            description=f"List available tools from remote MCP server '{self.tool_prefix}'",
            parameters={
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        )

    async def handle_list_tools(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        lines = []
        for t in self._mcp_tools:
            entry = {"tool": t.name, "description": t.description or "", "schema": t.inputSchema}
            if t.annotations:
                entry["annotations"] = t.annotations.model_dump(exclude_none=True)
            lines.append(json.dumps(entry, ensure_ascii=False))
        return "\n".join(lines) if lines else "No tools available"

    async def handle_tool_call(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        original_name = toolcall.fcall_name
        if original_name.startswith(self.tool_prefix + "_"):
            original_name = original_name[len(self.tool_prefix) + 1:]

        # Slow but zero idle sockets
        logger.info("fi_mcp calling %s on %s", original_name, self.url)
        async with self._connect() as session:
            result = await session.call_tool(original_name, model_produced_args or {})
            # XXX handle multimodal content (images etc) when needed
            text = result.content[0].text if result.content and hasattr(result.content[0], "text") else ""
            logger.info("fi_mcp %s done, %d chars", original_name, len(text))
            return text

    def handles(self, tool_name: str) -> bool:
        return tool_name.startswith(self.tool_prefix + "_")

    @asynccontextmanager
    async def _connect_streamable(self):
        h = self.headers or None
        client = httpx.AsyncClient(headers=h, timeout=httpx.Timeout(self.timeout))
        async with streamable_http_client(self.url, http_client=client) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                yield session

    @asynccontextmanager
    async def _connect_sse(self):
        h = self.headers or None
        async with sse_client(self.url, headers=h, timeout=self.timeout) as streams:
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


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)

    async def trivial_test():
        mcp = IntegrationMcp(
            url="https://mcp.context7.com/mcp",
            tool_prefix="context7",
        )
        await mcp.initialize()
        print(await mcp.handle_list_tools(None, {}))

    asyncio.run(trivial_test())
