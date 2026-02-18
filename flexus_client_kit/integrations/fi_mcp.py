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
        self.use_sse = self.url.endswith("/sse")
        self._mcp_tools = []

    async def initialize(self):
        async with self._connect() as session:
            response = await session.list_tools()
            self._mcp_tools = response.tools

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
        # strip prefix to get original MCP tool name
        original_name = toolcall.fcall_name
        if original_name.startswith(self.tool_prefix + "_"):
            original_name = original_name[len(self.tool_prefix) + 1:]

        # XXX connect-per-call: slow but zero idle sockets
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
    async def _connect(self):
        h = self.headers or None
        if self.use_sse:
            transport = sse_client(self.url, headers=h)
        else:
            client = httpx.AsyncClient(headers=h, timeout=httpx.Timeout(self.timeout))
            transport = streamable_http_client(self.url, http_client=client)
        async with transport as streams:
            read_stream, write_stream = streams[0], streams[1]
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                yield session


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)

    async def main():
        mcp = IntegrationMcp(
            url="https://mcp.context7.com/mcp",
            tool_prefix="context7",
        )
        await mcp.initialize()
        print(await mcp.handle_list_tools(None, {}))

    asyncio.run(main())
