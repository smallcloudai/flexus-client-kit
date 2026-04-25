import asyncio
import dataclasses
import json
import logging
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any, Dict, Union

import httpx
try:
    from exceptiongroup import BaseExceptionGroup
except ImportError:
    pass  # Python 3.11+ has BaseExceptionGroup builtin
import mcp.types
import mcp.shared.exceptions
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client
from pydantic import AnyUrl

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_shutdown

logger = logging.getLogger("__mcp")


@dataclasses.dataclass
class McpServerEntry:
    url: str
    auth_provider: str = ""
    dont_validate_tool_result: bool = False  # server returns extra undeclared fields, skip strict structured-content validation


MCP_DATABASE: Dict[str, McpServerEntry] = {
    "context7": McpServerEntry(url="https://mcp.context7.com/mcp"),
    "fibery":   McpServerEntry(url="https://mcp.fibery.io/mcp", auth_provider="fibery", dont_validate_tool_result=True),
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


SESSION_TTL = 60  # seconds of idle before closing cached session


def _truncate(s: str, n: int) -> str:
    s = s.replace("\n", " ").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def _render_prompt(result) -> str:
    out = []
    if result.description:
        out.append(result.description)
        out.append("")
    for m in result.messages:
        c = m.content
        text = getattr(c, "text", None) or getattr(c, "data", None) or ""
        out.append(f"[{m.role}] {text}")
    return "\n".join(out) or "(empty prompt)"


def _render_resource(result) -> str:
    out = []
    for c in result.contents:
        header = f"# {c.uri}"
        if getattr(c, "mimeType", None):
            header += f" ({c.mimeType})"
        out.append(header)
        if hasattr(c, "text"):
            out.append(c.text)
        else:
            out.append("(binary, %d bytes base64)" % len(getattr(c, "blob", "") or ""))
    return "\n\n".join(out) or "(empty resource)"


async def _noop_validate(self, name, result):
    return None


def _disable_strict_output_validation(session: ClientSession):
    # Fibery and possibly other servers return undeclared fields (e.g. "fixLogs")
    # that fail strict additionalProperties=false validation. We only consume
    # result.content[0].text anyway, so skip structured-content validation.
    session._validate_tool_result = _noop_validate.__get__(session, ClientSession)


class IntegrationMcp:
    def __init__(self, mcp_name: str, entry: McpServerEntry, url: str, token: str):
        self.mcp_name = mcp_name
        self.entry = entry
        self.url = url.strip()
        self.headers: Dict[str, str] = {"Authorization": f"Bearer {token}"} if token else {}
        self._use_sse = None  # auto-detected on first connect
        self._mcp_tools = []
        self._mcp_prompts = []     # list[mcp.types.Prompt], empty if server doesn't support prompts
        self._mcp_resources = []   # list[mcp.types.Resource], empty if server doesn't support resources
        self._init_error = ""
        # Session owner task: all open/close happens inside _session_loop to stay in the same task
        self._req_queue: asyncio.Queue = asyncio.Queue()
        self._session_task: asyncio.Task | None = None

    async def initialize(self):
        self._init_error = ""
        # Probe transport: try Streamable HTTP first, fall back to SSE on 4xx
        try:
            async with self._connect_streamable() as session:
                await self._probe_capabilities(session)
                self._use_sse = False
                logger.info("fi_mcp %s using streamable HTTP", self.url)
        except (httpx.HTTPStatusError, BaseExceptionGroup) as e:
            status = _unwrap_http_status(e)
            if status == 401:
                self._init_error = "MCP server %s returned 401 Unauthorized. API key is connected but rejected by the server — check if the key is valid or expired." % self.mcp_name
                logger.info("🛑 " + self._init_error)
                return
            if status not in (404, 405):
                raise
            logger.info("fi_mcp streamable HTTP got %d, trying SSE", status)
            try:
                async with self._connect_sse() as session:
                    await self._probe_capabilities(session)
                    self._use_sse = True
                    logger.info("fi_mcp %s using SSE", self.url)
            except (httpx.HTTPStatusError, BaseExceptionGroup) as e:
                status = _unwrap_http_status(e)
                if status == 401:
                    self._init_error = "MCP server %s returned 401 Unauthorized. API key is connected but rejected by the server — check if the key is valid or expired." % self.mcp_name
                    logger.info("🛑 " + self._init_error)
                    return
                raise
        if not self._init_error:
            self._session_task = asyncio.create_task(self._session_loop())

    async def _probe_capabilities(self, session: ClientSession):
        self._mcp_tools = (await session.list_tools()).tools
        try:
            self._mcp_prompts = (await session.list_prompts()).prompts
        except mcp.shared.exceptions.McpError as e:
            if e.error.code != mcp.types.METHOD_NOT_FOUND:
                logger.info("fi_mcp %s list_prompts error: %s", self.mcp_name, e.error.message)
            self._mcp_prompts = []
        try:
            self._mcp_resources = (await session.list_resources()).resources
        except mcp.shared.exceptions.McpError as e:
            if e.error.code != mcp.types.METHOD_NOT_FOUND:
                logger.info("fi_mcp %s list_resources error: %s", self.mcp_name, e.error.message)
            self._mcp_resources = []
        logger.info("fi_mcp %s: %d tools, %d prompts, %d resources", self.mcp_name, len(self._mcp_tools), len(self._mcp_prompts), len(self._mcp_resources))

    async def close(self):
        if self._session_task and not self._session_task.done():
            self._session_task.cancel()
            try:
                await self._session_task
            except asyncio.CancelledError:
                pass
        self._session_task = None

    @classmethod
    def tool_desc(cls, n: str) -> ckit_cloudtool.CloudTool:
        return ckit_cloudtool.CloudTool(
            strict=False,
            name=f"mcp_{n}",
            description=(
                f"MCP server {n}. Start with op=\"list\" to see tools, prompts, and resources the server offers. "
                "Prompts are server-authored templates that teach correct usage of this server's tools — read them before guessing tool arguments. "
                "Resources are server-hosted documents (schemas, guides, reference data). "
                "Workflow for tools: list → help name=\"fn\" → call name=\"fn\" args={...}. "
                "Workflow for prompts: list → get_prompt name=\"p\" args={...}. "
                "Workflow for resources: list → read_resource uri=\"...\"."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "op": {"type": "string", "enum": ["list", "help", "call", "get_prompt", "read_resource"]},
                    "name": {"type": "string", "description": "Tool or prompt name. Required for help, call, get_prompt."},
                    "uri": {"type": "string", "description": "Resource URI. Required for read_resource."},
                    "args": {"type": "object", "description": "Arguments for call or get_prompt. Use op=\"help\" (for tools) or read the prompt argument list (from op=\"list\") to learn what to pass."},
                },
            },
        )

    async def handle_tool_call(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        if self._init_error:
            return self._init_error
        op = (model_produced_args or {}).get("op", "help")
        args = (model_produced_args or {}).get("args", {})
        name = (model_produced_args or {}).get("name", "")
        uri = (model_produced_args or {}).get("uri", "")

        if op == "list":
            out = []
            out.append(f"# This server offers {len(self._mcp_tools)} tools, use op=\"help\" name=\"...\" then op=\"call\"")
            if self._mcp_tools:
                out += [json.dumps({"tool": t.name, "description": _truncate(t.description or "", 80)}, ensure_ascii=False) for t in self._mcp_tools]
            else:
                out.append("(none)")
            out.append("")
            out.append(f"# Also this server offers {len(self._mcp_prompts)} prompts, use op=\"get_prompt\" name=\"...\" args={{...}}")
            if self._mcp_prompts:
                for p in self._mcp_prompts:
                    entry = {"prompt": p.name, "description": _truncate(p.description or "", 120)}
                    if p.arguments:
                        entry["args"] = [{"name": a.name, "required": bool(a.required), "description": _truncate(a.description or "", 80)} for a in p.arguments]
                    out.append(json.dumps(entry, ensure_ascii=False))
            out.append("")
            out.append(f"# Also there are {len(self._mcp_resources)} resources, use op=\"read_resource\" uri=\"...\"")
            if self._mcp_resources:
                for r in self._mcp_resources:
                    out.append(json.dumps({"uri": str(r.uri), "name": r.name, "description": _truncate(r.description or "", 120), "mimeType": r.mimeType or ""}, ensure_ascii=False))
            return "\n".join(out)

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
            # XXX That might be questionable, removes all the None, why would it do that
            clean_args = {k: v for k, v in (args or {}).items() if v is not None}
            logger.info("fi_mcp calling %s on %s", name, self.url)
            result = await self._session_run("call_tool", name=name, arguments=clean_args)
            # XXX handle multimodal content (images etc) when needed
            text = result.content[0].text if result.content and hasattr(result.content[0], "text") else ""
            logger.info("fi_mcp %s done, %d chars", name, len(text))
            return text

        if op == "get_prompt":
            if not name:
                return "Missing name parameter\n"
            str_args = {k: str(v) for k, v in (args or {}).items() if v is not None}
            logger.info("fi_mcp get_prompt %s on %s", name, self.url)
            result = await self._session_run("get_prompt", name=name, arguments=str_args)
            return _render_prompt(result)

        if op == "read_resource":
            if not uri:
                return "Missing uri parameter\n"
            logger.info("fi_mcp read_resource %s on %s", uri, self.url)
            try:
                parsed = AnyUrl(uri)
            except Exception as e:
                return f"Invalid uri {uri!r}: {e}\n"
            result = await self._session_run("read_resource", uri=parsed)
            return _render_resource(result)

        return f"Unknown op '{op}', use list/help/call/get_prompt/read_resource\n"

    @asynccontextmanager
    async def _connect_streamable(self):
        h = self.headers or None
        client = httpx.AsyncClient(headers=h, timeout=httpx.Timeout(15))
        async with streamable_http_client(self.url, http_client=client) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                if self.entry.dont_validate_tool_result:
                    _disable_strict_output_validation(session)
                await session.initialize()
                yield session

    @asynccontextmanager
    async def _connect_sse(self):
        h = self.headers or None
        async with sse_client(self.url, headers=h, timeout=15) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                if self.entry.dont_validate_tool_result:
                    _disable_strict_output_validation(session)
                await session.initialize()
                yield session

    async def _session_loop(self):
        # All session open/close happens here, in one task, so anyio cancel scopes are happy
        session = None
        stack = None
        while True:
            try:
                fut = await asyncio.wait_for(self._req_queue.get(), timeout=SESSION_TTL)
            except asyncio.TimeoutError:
                if session:
                    logger.info("fi_mcp %s idle %ds, closing session", self.mcp_name, SESSION_TTL)
                    await self._close_stack(stack)
                    session, stack = None, None
                continue
            except asyncio.CancelledError:
                if session:
                    logger.info("fi_mcp %s task cancelled, closing session", self.mcp_name)
                    await self._close_stack(stack)
                return
            # fut is (method_name, kwargs, response_future)
            method_name, kwargs, resp = fut
            try:
                if not session:
                    session, stack = await self._open_session()
                result = await getattr(session, method_name)(**kwargs)
            except Exception as e:
                if session:
                    logger.info("fi_mcp %s session dead, reconnecting", self.mcp_name)
                    await self._close_stack(stack)
                    session, stack = None, None
                    try:
                        session, stack = await self._open_session()
                        result = await getattr(session, method_name)(**kwargs)
                    except Exception as e2:
                        resp.set_exception(e2)
                        continue
                else:
                    resp.set_exception(e)
                    continue
            resp.set_result(result)

    async def _open_session(self):
        stack = AsyncExitStack()
        try:
            if self._use_sse:
                streams = await stack.enter_async_context(sse_client(self.url, headers=self.headers or None, timeout=15))
            else:
                h = self.headers or None
                client = httpx.AsyncClient(headers=h, timeout=httpx.Timeout(15))
                streams = await stack.enter_async_context(streamable_http_client(self.url, http_client=client))
            session = await stack.enter_async_context(ClientSession(streams[0], streams[1]))
            if self.entry.dont_validate_tool_result:
                _disable_strict_output_validation(session)
            await session.initialize()
        except BaseException:
            await self._close_stack(stack)
            raise
        logger.info("fi_mcp %s session opened", self.mcp_name)
        return session, stack

    async def _close_stack(self, stack):
        if not stack:
            return
        logger.info("fi_mcp %s closing session", self.mcp_name)
        try:
            await stack.aclose()
        except (asyncio.CancelledError, GeneratorExit):
            raise
        except BaseException:
            logger.warning("fi_mcp %s error closing session", self.mcp_name, exc_info=True)
        logger.info("fi_mcp %s session closed", self.mcp_name)

    async def _session_run(self, method_name: str, **kwargs):
        resp = asyncio.get_running_loop().create_future()
        await self._req_queue.put((method_name, kwargs, resp))
        return await resp


def _mcp_token_from_external_auth(ext: dict, provider: str) -> str:
    raw = ext.get(provider)
    if not isinstance(raw, dict):
        return ""
    # manual auth: api_key at top level
    v = (raw.get("api_key") or "").strip()
    if v:
        return v
    # OAuth: access_token inside token dict
    tok = raw.get("token")
    if isinstance(tok, dict):
        return (tok.get("access_token") or "").strip()
    return ""


def _validate_names(names: list[str]):
    for n in names:
        if n not in MCP_DATABASE:
            raise ValueError(f"Unknown MCP server {n!r}, known: {list(MCP_DATABASE.keys())}")


def mcp_setup_schema(names: list[str], bs_group: str = "MCP", bs_order_start: int = 100) -> list[Dict[str, Union[str, int]]]:
    _validate_names(names)
    schema = []
    for i, n in enumerate(names):
        url = MCP_DATABASE[n].url
        schema.append({
            "bs_name": f"mcp_{n}_url",
            "bs_type": "string_long",
            "bs_default": url,
            "bs_group": bs_group,
            "bs_order": bs_order_start + i * 10,
            "bs_importance": 0,
            "bs_description": f"MCP server URL for {n}",
        })
    return schema


def mcp_tools(names: list[str]) -> list[ckit_cloudtool.CloudTool]:
    _validate_names(names)
    return [IntegrationMcp.tool_desc(n) for n in names]


async def mcp_launch(names: list[str], rcx: ckit_bot_exec.RobotContext, setup: Dict[str, Any]) -> None:
    _validate_names(names)
    for n in names:
        entry = MCP_DATABASE[n]
        url = setup.get(f"mcp_{n}_url", entry.url)
        if not url:
            async def _not_configured(toolcall, args, _n=n):
                return f"MCP server {_n} is not configured, set mcp_{_n}_url in bot setup"
            rcx.on_tool_call(f"mcp_{n}")(_not_configured)
            continue
        token = _mcp_token_from_external_auth(rcx.external_auth, entry.auth_provider) if entry.auth_provider else ""
        mcp = IntegrationMcp(mcp_name=n, entry=entry, url=url, token=token)
        await mcp.initialize()
        if mcp._session_task:
            ckit_shutdown.give_task_to_cancel(f"mcp_{n}", mcp._session_task)
        rcx.on_tool_call(f"mcp_{n}")(mcp.handle_tool_call)
        logger.info("mcp launched %s -> %s", n, url)


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)

    async def trivial_test():
        mcp = IntegrationMcp(url="https://mcp.context7.com/mcp", mcp_name="context7")
        await mcp.initialize()
        listing = await mcp.handle_tool_call(None, {"op": "list"})
        print("-"*40, "list", "-"*40)
        print(listing)
        for line in listing.strip().split("\n"):
            if not line.startswith("{"):
                continue
            entry = json.loads(line)
            if "tool" not in entry:
                continue
            print("-"*40, "help", entry["tool"], "-"*40)
            print(await mcp.handle_tool_call(None, {"op": "help", "name": entry["tool"]}))
        print("-"*40, "call", "-"*40)
        print(await mcp.handle_tool_call(None, {"op": "call", "name": "resolve-library-id", "args": {"query": "python mcp client", "libraryName": "mcp"}}))
        await mcp.close()

    asyncio.run(trivial_test())
