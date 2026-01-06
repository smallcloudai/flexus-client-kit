import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Awaitable, List, Set, Optional, Tuple

import gql
import websockets
import websockets.exceptions
from gql.transport.exceptions import TransportQueryError

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_utils
from flexus_client_kit import gql_utils

logger = logging.getLogger("ctool")


class NeedsConfirmation(Exception):
    def __init__(self,
        confirm_setup_key: str,
        confirm_command: str,
        confirm_explanation: str,
    ):
        self.confirm_setup_key = confirm_setup_key
        self.confirm_command = confirm_command
        self.confirm_explanation = confirm_explanation
        super().__init__(f"Confirmation needed: {confirm_explanation}")


class WaitForSubchats(Exception):
    def __init__(self, subchats: List[str]):
        self.subchats = subchats
        super().__init__(f"Waiting for subchats: {subchats}")


class AlreadyPostedResult(Exception):
    def __init__(self):
        super().__init__("Result already posted")


class AlreadyFakedResult(Exception):
    def __init__(self):
        super().__init__("Result already faked in scenario")


@dataclass
class ToolResult:
    """
    Local tools (in bots or cloudtool services) should either return str or ToolResult
    """
    content: str
    multimodal: Optional[List[dict]] = None
    dollars: float = 0.0

    def __post_init__(self):
        if self.multimodal is not None and self.content:
            raise ValueError("ToolResult: use either content (str) or multimodal (list), not both")
        if self.multimodal:
            for item in self.multimodal:
                if not isinstance(item, dict):
                    raise ValueError("ToolResult multimodal list items must be dicts: %r" % (item,))
                if "m_type" not in item or "m_content" not in item:
                    raise ValueError("ToolResult multimodal items must have m_type and m_content: %r" % (item,))
                if not isinstance(item["m_type"], str) or not isinstance(item["m_content"], str):
                    raise ValueError("ToolResult m_type and m_content must be strings: %r" % (item,))

    def to_serialized(self) -> str:
        if self.multimodal is not None:
            return json.dumps(self.multimodal)
        return json.dumps(self.content)


@dataclass
class FCloudtoolCall:
    caller_fuser_id: str  # copy of thread owner fuser_id
    located_fgroup_id: str
    fcall_id: str
    fcall_ft_id: str
    fcall_ft_btest_name: str
    fcall_ftm_alt: int
    fcall_called_ftm_num: int
    fcall_call_n: int
    fcall_name: str
    fcall_arguments: str
    fcall_result_ftm_num: int
    fcall_created_ts: float
    fcall_untrusted_key: str
    connected_persona_id: str
    ws_id: str
    subgroups_list: List[str]
    confirmed_by_human: Optional[bool] = None


@dataclass
class CloudTool:
    strict: bool
    name: str
    description: str
    parameters: dict

    def openai_style_tool(self):
        def add_order(obj):
            if isinstance(obj, dict):
                props = obj.get("properties")
                if props:
                    for idx, key in enumerate(props.keys()):
                        props[key].setdefault("order", idx)
                        add_order(props[key])
                for v in obj.values():
                    if isinstance(v, (dict, list)):
                        add_order(v)
            elif isinstance(obj, list):
                for item in obj:
                    add_order(item)

        params = self.parameters.copy()
        add_order(params)
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": params,
            },
            "strict": self.strict,
        }


def sanitize_args(args_dict_from_model: Any) -> tuple[dict, Optional[str]]:
    """
    For use within tool call. Make sure model has generated "args" and it's a dict.
    """
    if isinstance(args_dict_from_model, dict):
        args = args_dict_from_model.get("args", {})
    else:
        return {}, "args_dict_from_model should be a dict"

    if args is None:  # that's allowed, strict mode for tools leads to type=object|none, therefure model might produce None
        return {}, None

    # Model was stupid enough to escape json object and send a string
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except (json.JSONDecodeError, TypeError):
            return {}, "Error: 'args' needs to have 'object', don't pass a string, I couldn't even parse it back to json :/"

    if not isinstance(args, dict):
        return {}, "args must be a dict after normalization"

    return args, None


def try_best_to_find_argument(args: dict, args_dict_from_model: Any, param_name: str, default_value: Any) -> Any:
    """
    This handles cases where the model puts parameters in the wrong place.
    """
    value = args.get(param_name)   # Normal, as asked
    if value:
        return value

    # We might find it on the top level, a common mistake
    if isinstance(args_dict_from_model, dict):
        value = args_dict_from_model.get(param_name)
        if value:
            return value

    return default_value


async def call_python_function_and_save_result(
    call: FCloudtoolCall,
    the_python_function: Callable[[ckit_client.FlexusClient, FCloudtoolCall, Any], Awaitable[Tuple[str | ToolResult, str] | Tuple[None, None]]],
    service_name: str,
    fclient: ckit_client.FlexusClient,
) -> None:
    try:
        args = json.loads(call.fcall_arguments)
        result, prov = await the_python_function(fclient, call, args)
        # NOTE: here we have 2 allowed variants for output
        # 1. (str | ToolResult, str) - immediate answer from handler
        # 2. (None, None) - delayed cloudtool_post_result
        assert (isinstance(result, (str, ToolResult)) and isinstance(prov, str)) or (result is None and prov is None)
        content = result.content if isinstance(result, ToolResult) else result
        dollars = result.dollars if isinstance(result, ToolResult) else 0.0
        logger.info("/%s %s:%03d:%03d %+d result=%s", call.fcall_id, call.fcall_ft_id, call.fcall_ftm_alt, call.fcall_called_ftm_num, call.fcall_call_n, content[:30] if content is not None else "delayed")
    except AlreadyFakedResult:
        logger.info("/%s fake %s:%03d:%03d %+d", call.fcall_id, call.fcall_ft_id, call.fcall_ftm_alt, call.fcall_called_ftm_num, call.fcall_call_n)
        return
    except NeedsConfirmation as e:
        logger.info("%s needs human confirmation: %s", call.fcall_id, e.confirm_explanation)
        try:
            await cloudtool_confirmation_request(
                fclient,
                call.fcall_id,
                e.confirm_setup_key,
                e.confirm_command,
                e.confirm_explanation,
            )
        except TransportQueryError as gql_err:
            if "confirmation already requested" in str(gql_err).lower():
                logger.info("Confirmation already requested for %s, ignoring", call.fcall_id)
            else:
                raise
        return
    except Exception as e:
        logger.warning("error processing call %s %s:%03d:%03d %+d: %s %s" % (call.fcall_id, call.fcall_ft_id, call.fcall_ftm_alt, call.fcall_called_ftm_num, call.fcall_call_n, type(e).__name__, e), exc_info=e)
        content, prov = json.dumps(f"{type(e).__name__} {e}"), json.dumps({"system": service_name})
    if result is not None:
        serialized_result = result if isinstance(result, str) else result.to_serialized()
        await cloudtool_post_result(fclient, call.fcall_id, call.fcall_untrusted_key, serialized_result, prov, dollars)


async def cloudtool_post_result(fclient: ckit_client.FlexusClient, fcall_id: str, fcall_untrusted_key: str, content: str, prov: str, dollars: float = 0.0, as_placeholder: bool = False):
    http_client = await fclient.use_http()
    async with http_client as http:
        await http.execute(
            gql.gql("""mutation CloudtoolPost($input: CloudtoolResultInput!, $as_placeholder: Boolean!) {
                cloudtool_post_result(input: $input, as_placeholder: $as_placeholder)
            }"""),
            variable_values={
                "input": {
                    "fcall_id": fcall_id,
                    "fcall_untrusted_key": fcall_untrusted_key,
                    "ftm_content": content,
                    "ftm_provenance": prov,
                    "dollars": dollars,
                },
                "as_placeholder": as_placeholder,
            },
        )


class DeltaStreamer:
    """
    Streams tool output deltas via /v1/delta/ws WebSocket.
    Frontend receives DELTA events and appends content in real-time.
    """

    def __init__(self, ws_url: str, call: FCloudtoolCall, role: str = "tool"):
        self._ws_url = ws_url
        self._call = call
        self._role = role
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._closed = False

    @classmethod
    async def connect(
        cls,
        fclient: ckit_client.FlexusClient,
        call: FCloudtoolCall,
        role: str = "tool",
    ) -> "DeltaStreamer":
        ws_url = fclient.base_url_ws.rstrip("/") + "/v1/delta/ws"
        streamer = cls(ws_url, call, role)
        streamer._ws = await websockets.connect(ws_url, ping_interval=20, ping_timeout=20)
        logger.debug("DeltaStreamer connected to %s for call %s", ws_url, call.fcall_id)
        return streamer

    async def send(self, text: str) -> None:
        if not text or self._closed or not self._ws:
            return
        payload = {
            "ftm_belongs_to_ft_id": self._call.fcall_ft_id,
            "ftm_alt": self._call.fcall_ftm_alt,
            "ftm_num": self._call.fcall_result_ftm_num,
            "ftm_prev_alt": self._call.fcall_ftm_alt,
            "delta": {"ftm_role": self._role, "ftm_content": text, "ftm_call_id": self._call.fcall_id},
        }
        await self._ws.send(json.dumps(payload))

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._ws:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None
        logger.debug("DeltaStreamer closed for call %s", self._call.fcall_id)


async def cloudtool_confirmation_request(
    fclient: ckit_client.FlexusClient,
    fcall_id: str,
    confirm_setup_key: str,
    confirm_command: str,
    confirm_explanation: str
):
    http_client = await fclient.use_http()
    async with http_client as http:
        await http.execute(
            gql.gql("""mutation CloudtoolConfirmationRequest(
                $fcall_id: String!,
                $confirm_setup_key: String!,
                $confirm_command: String!,
                $confirm_explanation: String!
            ) {
                cloudtool_confirmation_request(
                    fcall_id: $fcall_id,
                    confirm_setup_key: $confirm_setup_key,
                    confirm_command: $confirm_command,
                    confirm_explanation: $confirm_explanation
                )
            }"""),
            variable_values={
                "fcall_id": fcall_id,
                "confirm_setup_key": confirm_setup_key,
                "confirm_command": confirm_command,
                "confirm_explanation": confirm_explanation,
            },
        )


async def i_am_still_alive(
        fclient: ckit_client.FlexusClient,
        tool_list: List[CloudTool],
        fgroup_id: Optional[str],
        fuser_id: Optional[str],
        shared: bool,
) -> None:
    while not ckit_shutdown.shutdown_event.is_set():
        try:
            http_client = await fclient.use_http()
            async with http_client as http:
                for t in tool_list:
                    await http.execute(
                        gql.gql("""mutation CloudtoolConfirm($name: String!, $desc: String!, $params: String!, $fgroup_id: String, $fuser_id: String, $shared: Boolean!) {
                            cloudtool_confirm_exists(tool_name: $name, ctool_description: $desc, ctool_parameters: $params, fgroup_id: $fgroup_id, fuser_id: $fuser_id, shared: $shared)
                        }"""),
                        variable_values={
                            "name": t.name,
                            "desc": t.description,
                            "params": json.dumps(t.parameters),
                            "fgroup_id": fgroup_id,
                            "fuser_id": fuser_id,
                            "shared": shared,
                        },
                    )
                    logger.info("i_am_still_alive %s", t.name)
            if await ckit_shutdown.wait(120):
                break

        except (
            gql.transport.exceptions.TransportError,
            OSError,
            asyncio.exceptions.TimeoutError
        ) as e:
            if "403:" in str(e):
                # It's gql.transport.exceptions.TransportQueryError with {'message': "403: Whoops your key didn't work (1).", ...}
                # Unfortunately, no separate exception class for 403
                logger.error("That looks bad, my key doesn't work: %s", e)
            else:
                logger.info("i_am_still_alive connection problem")
            if await ckit_shutdown.wait(60):
                break


async def run_cloudtool_service_real(
    service_name: str,
    endpoint: str,
    superuser: bool,
    tools: List[CloudTool],
    the_python_function: Callable[[ckit_client.FlexusClient, FCloudtoolCall, Any], Awaitable[Tuple[str, str] | Tuple[None, None]]],  # should return tuple of tool result ftm_content as serialized json, and ftm_provenance as serialized json
    max_tasks: int,
    fgroup_id: Optional[str],
    fuser_id: Optional[str],
    shared: bool,
) -> None:
    fclient = ckit_client.FlexusClient(
        service_name,
        endpoint=endpoint,
        superuser=superuser,
    )

    workset: Set[asyncio.Task] = set()

    async def monitor_performance() -> None:
        idle_sec = 0
        full_sec = 0
        minute = int(time.time() // 60)
        badstat = True
        while not ckit_shutdown.shutdown_event.is_set():
            if await ckit_shutdown.wait(1):
                break
            if len(workset) == 0:
                idle_sec += 1
            if len(workset) == max_tasks:
                full_sec += 1
            now_minute = int(time.time() // 60)
            if now_minute != minute:
                if badstat:
                    badstat = False
                else:
                    logger.info("idle %0.1f%% full %0.1f%% now %d", (idle_sec * 100 / 60), (full_sec * 100 / 60), len(workset))
                idle_sec = 0
                full_sec = 0
                minute = now_minute

    def workset_done(task: asyncio.Task, call: FCloudtoolCall) -> None:
        workset.discard(task)
        if task.exception():
            logger.error("cloudtool task error", exc_info=task.exception())

    still_alive = asyncio.create_task(i_am_still_alive(fclient, tools, fgroup_id, fuser_id, shared))
    still_alive.add_done_callback(lambda t: ckit_utils.report_crash(t, logger))
    perfmon = asyncio.create_task(monitor_performance())
    perfmon.add_done_callback(lambda t: ckit_utils.report_crash(t, logger))

    ws_client = await fclient.use_ws()
    ckit_shutdown.give_ws_client(service_name, ws_client)

    try:
        async with ws_client as ws:
            async for r in ws.subscribe(gql.gql(
                f"""subscription CloudtoolWait($names: [String!]!, $fgroup_id: String, $fuser_id: String) {{
                    cloudtool_wait_for_call(tool_names: $names, fgroup_id: $fgroup_id, fuser_id: $fuser_id) {{
                        {gql_utils.gql_fields(FCloudtoolCall)}
                    }}
                }}"""),
                variable_values={
                    "names": [t.name for t in tools],
                    "fgroup_id": fgroup_id,
                    "fuser_id": None if shared else fuser_id,
                }
            ):
                while len(workset) >= max_tasks:
                    logger.warning("too many tasks %d, sleeping instead of reading subs", len(workset))
                    if await ckit_shutdown.wait(1):
                        break
                call = gql_utils.dataclass_from_dict(r["cloudtool_wait_for_call"], FCloudtoolCall)
                logger.info(" %s %s:%03d:%03d %+d %s(%s)", call.fcall_id, call.fcall_ft_id, call.fcall_ftm_alt, call.fcall_called_ftm_num, call.fcall_call_n, call.fcall_name, str(call.fcall_arguments)[:20])

                t = asyncio.create_task(call_python_function_and_save_result(call, the_python_function, service_name, fclient))
                t.add_done_callback(lambda t, c = call: workset_done(t, c))
                workset.add(t)
    finally:
        logger.info("run_cloudtool_service_real going down!")
        ckit_shutdown.take_away_ws_client(service_name)
        perfmon.cancel()
        still_alive.cancel()
        await asyncio.gather(still_alive, perfmon, *workset, return_exceptions=True)


async def run_cloudtool_service(
    service_name: str,
    endpoint: str,
    superuser: bool,
    tools: List[CloudTool],
    # should return tuple of tool result ftm_content as serialized json, and ftm_provenance as serialized json or tuple of None for delayed returns
    the_python_function: Callable[[ckit_client.FlexusClient, FCloudtoolCall, Any], Awaitable[Tuple[str, str] | Tuple[None, None]]],
    max_tasks: int = 64,
    fgroup_id: Optional[str] = None,
    fuser_id: Optional[str] = None,
    shared: bool = True,
) -> None:
    while not ckit_shutdown.shutdown_event.is_set():
        try:
            await run_cloudtool_service_real(
                service_name,
                endpoint,
                superuser,
                tools,
                the_python_function,
                max_tasks,
                fgroup_id,
                fuser_id,
                shared,
            )

        except (websockets.exceptions.ConnectionClosedError, gql.transport.exceptions.TransportError, OSError):
            if ckit_shutdown.shutdown_event.is_set():
                break
            logger.info("got disconnected, will connect again in 60s")
            await ckit_shutdown.wait(60)

        except Exception as e:
            logger.error("caught exception %s: %s" % (type(e).__name__, e), exc_info=e)
            await ckit_shutdown.wait(60)
