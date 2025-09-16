import json
import re
import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Awaitable, NamedTuple, Set, Union

import gql

from flexus_client_kit import ckit_client, gql_utils, ckit_service_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_shutdown


logger = logging.getLogger("btexe")


@dataclass
class FPersonaOutput:
    owner_fuser_id: str
    located_fgroup_id: str
    persona_id: str
    persona_name: str
    persona_marketable_name: str
    persona_marketable_version: int
    persona_discounts: Any
    persona_setup: Any
    persona_created_ts: float
    ws_id: str
    ws_timezone: str


@dataclass
class FBotThreadsAndCallsSubs:
    news_action: str
    news_about: str
    news_payload_id: str
    news_payload_thread_message: Optional[ckit_ask_model.FThreadMessageOutput]
    news_payload_thread: Optional[ckit_ask_model.FThreadOutput]
    news_payload_persona: Optional[FPersonaOutput]
    news_payload_toolcall: Optional[ckit_cloudtool.FCloudtoolCall]


@dataclass
class FThreadWithMessages:
    persona_id: str
    thread_fields: ckit_ask_model.FThreadOutput
    thread_messages: Dict[str, ckit_ask_model.FThreadMessageOutput] = field(default_factory=dict)


def official_setup_mixing_procedure(marketable_setup_default, persona_setup) -> Dict[str, Union[str, int, float, bool, list]]:
    """
    Returns setup dict for a bot to run with. If a value is not set in persona_setup by the user, returns the default.
    Also validates marketable_setup_default -- that's what you use to publish a bot default settings on marketplace.
    """
    result = dict()
    minimal_set = set(["bs_type", "bs_default", "bs_group", "bs_name"])
    full_set = minimal_set | set(["bs_description", "bs_order", "bs_placeholder", "bs_importance"])
    types = {"string_short": str, "string_long": str, "string_multiline": str, "bool": bool, "int": int, "float": float, "list_dict": list}
    for d in marketable_setup_default:
        k = d["bs_name"]
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{1,39}$', k):
            raise ValueError("Bad key for setup %r" % k)

        if d["bs_type"] == "list_dict":
            allowed_keys = full_set | set(["bs_elements"])
            if not set(d.keys()).issubset(allowed_keys):
                raise ValueError("You have unrecognized keys in marketable_setup_default: %s" % (set(d.keys()) - allowed_keys))
        else:
            if not set(d.keys()).issubset(full_set):
                raise ValueError("You have unrecognized keys in marketable_setup_default: %s" % (set(d.keys()) - full_set))

        if not set(d.keys()).issuperset(minimal_set):
            raise ValueError("You have missing keys in marketable_setup_default: %s" % (minimal_set - set(d.keys())))
        if d["bs_type"] not in types:
            raise ValueError("You have unrecognized type in marketable_setup_default: %s" % d["bs_type"])

        if d["bs_type"] == "list_dict":
            if not isinstance(d["bs_default"], list):
                raise ValueError("Default value %s for %s must be a list for type list_dict" % (d["bs_default"], k))
        elif not isinstance(d["bs_default"], types[d["bs_type"]]):
            raise ValueError("Default value %s for %s is not of type %s" % (d["bs_default"], k, d["bs_type"]))

        x = persona_setup.get(k, None)
        if x is None:
            x = d["bs_default"]
        result[k] = types[d["bs_type"]](x) if d["bs_type"] != "list_dict" else (x if isinstance(x, list) else [])
    return result


class RobotContext:
    def __init__(self, fclient: ckit_client.FlexusClient, p: FPersonaOutput):
        self._handler_updated_message: Optional[Callable[[ckit_ask_model.FThreadMessageOutput], Awaitable[None]]] = None
        self._handler_upd_thread: Optional[Callable[[ckit_ask_model.FThreadOutput], Awaitable[None]]] = None
        self._handler_per_tool: Dict[str, Callable[[Dict[str, Any]], Awaitable[str]]] = {}
        self._ready = False
        self._parked_messages: Dict[str, ckit_ask_model.FThreadMessageOutput] = {}
        self._parked_threads: Dict[str, ckit_ask_model.FThreadOutput] = {}
        self._parked_toolcalls: List[ckit_cloudtool.FCloudtoolCall] = []
        self._parked_anything_new = asyncio.Event()
        # These fields are designed for direct access:
        self.fclient = fclient
        self.persona = p
        self.latest_threads: Dict[str, FThreadWithMessages] = dict()
        self.created_ts = time.time()
        self.workdir = "/tmp/bot_workspace/%s/" % p.persona_id
        os.makedirs(self.workdir, exist_ok=True)

    def on_updated_message(self, handler: Callable[[ckit_ask_model.FThreadMessageOutput], Awaitable[None]]):
        self._handler_updated_message = handler
        return handler

    def on_updated_thread(self, handler: Callable[[ckit_ask_model.FThreadOutput], Awaitable[None]]):
        self._handler_upd_thread = handler
        return handler

    def on_tool_call(self, tool_name: str):
        def decorator(handler: Callable[[Dict[str, Any]], Awaitable[str]]):
            self._handler_per_tool[tool_name] = handler
            return handler
        return decorator

    def ready(self):
        self._ready = True

    async def unpark_collected_events(self, sleep_if_no_work: float, turn_tool_calls_into_tasks: bool = False) -> List[asyncio.Task]:
        # logger.info("%s unpark_collected_events() started %d %d %d" % (self.persona.persona_id, len(self._parked_messages), len(self._parked_threads), len(self._parked_toolcalls)))
        did_anything = False
        self._parked_anything_new.clear()

        todo = list(self._parked_messages.keys())  # can appear more in the background, as we await in loop body
        for k in todo:
            msg = self._parked_messages.pop(k)
            did_anything = True
            if self._handler_updated_message:
                try:
                    await self._handler_updated_message(msg)
                except Exception as e:
                    logger.error("%s error in handler_updated_message handler: %s\n%s", self.persona.persona_id, type(e).__name__, e, exc_info=e)

        todo = list(self._parked_threads.keys())
        for k in todo:
            thread = self._parked_threads.pop(k)
            did_anything = True
            if self._handler_upd_thread:
                try:
                    await self._handler_upd_thread(thread)
                except Exception as e:
                    logger.error("%s error in on_updated_thread handler: %s\n%s", self.persona.persona_id, type(e).__name__, e, exc_info=e)

        mycalls = list(self._parked_toolcalls)
        self._parked_toolcalls.clear()
        bg_calls = []
        for c in mycalls:
            did_anything = True
            if not turn_tool_calls_into_tasks:  # run immediately and wait
                try:
                    await self._local_tool_call(self.fclient, c)
                except Exception as e:
                    logger.error("%s error in on_tool_call() handler: %s\n%s", self.persona.persona_id, type(e).__name__, e, exc_info=e)
            else:
                bg_calls.append(asyncio.create_task(self._local_tool_call(self.fclient, c)))

        if not did_anything:
            try:
                await asyncio.wait_for(self._parked_anything_new.wait(), timeout=sleep_if_no_work)
            except asyncio.TimeoutError:
                pass

        return bg_calls   # empty if not turn_tool_calls_into_tasks (most regular bots)


    async def _local_tool_call(self, fclient: ckit_client.FlexusClient, toolcall: ckit_cloudtool.FCloudtoolCall) -> None:
        logger.info("%s local_tool_call %s %s(%s)" % (self.persona.persona_id, toolcall.fcall_id, toolcall.fcall_name, toolcall.fcall_arguments))
        try:
            args = json.loads(toolcall.fcall_arguments)
            if not isinstance(args, dict):
                raise json.JSONDecodeError("Toplevel is not a dict")
            handler = self._handler_per_tool[toolcall.fcall_name]
            tool_result = await handler(toolcall, args)
            if not isinstance(tool_result, str):
                raise ValueError("Tool call handler must return a string, got instead: %r" % (tool_result,))
            if tool_result == "":
                logger.warning("Tool call %s returned an empty string. Bad practice, model will not know what's happening!" % toolcall.fcall_name)
        except json.JSONDecodeError:
            # nothing in logs -- normal for a model to produce garbage on occasion
            tool_result = "Arguments expected to be a valid json, instead got: %r" % args
        except ckit_cloudtool.NeedsConfirmation as e:
            logger.info("%s needs human confirmation: %s" % (toolcall.fcall_id, e.confirm_explanation))
            await ckit_cloudtool.cloudtool_confirmation_request(fclient, toolcall.fcall_id, e.confirm_setup_key, e.confirm_command, e.confirm_explanation)
            tool_result = "POSTED_NEED_CONFIRMATION"
        except Exception as e:
            logger.error("Tool call %s failed: %s" % (toolcall.fcall_id, e), exc_info=True)  # full error and stack for the author of the bot
            tool_result = "Tool error, see logs for details"  # Not too much visible for end user
        prov = json.dumps({"system": fclient.service_name})
        if tool_result != "WAIT_SUBCHATS" and tool_result != "POSTED_NEED_CONFIRMATION":
            tool_result = json.dumps(tool_result)
            await ckit_cloudtool.cloudtool_post_result(fclient, toolcall, tool_result, prov)


class BotInstance(NamedTuple):
    fclient: ckit_client.FlexusClient
    atask: asyncio.Task
    eventgen: RobotContext


async def crash_boom_bang(fclient: ckit_client.FlexusClient, rcx: RobotContext, bot_main_loop: Callable[[ckit_client.FlexusClient, RobotContext], Awaitable[None]]) -> None:
    logger.info("%s START name=%r" % (rcx.persona.persona_id, rcx.persona.persona_name))
    try:
        await bot_main_loop(fclient, rcx)

    except asyncio.CancelledError:
        pass

    except Exception as e:
        logger.error("Bot main loop: %s %s" % (type(e).__name__, e), exc_info=True)

    finally:
        logger.info("%s STOP" % rcx.persona.persona_id)


class BotsCollection:
    def __init__(
        self,
        fgroup_id: str,
        marketable_name: str,
        marketable_version: int,
        inprocess_tools: List[ckit_cloudtool.CloudTool],
        bot_main_loop: Callable[[ckit_client.FlexusClient, RobotContext], Awaitable[None]],
    ):
        self.fgroup_id = fgroup_id
        self.marketable_name = marketable_name
        self.marketable_version = marketable_version
        self.inprocess_tools = inprocess_tools
        self.bot_main_loop = bot_main_loop
        self.bots_running: Dict[str, BotInstance] = {}
        self.thread_tracker: Dict[str, FThreadWithMessages] = {}


async def subscribe_and_produce_callbacks(
    fclient: ckit_client.FlexusClient,
    ws_client: gql.Client,
    bc: BotsCollection,
):
    MAX_THREADS = 100
    assert fclient.service_name.startswith(bc.marketable_name)

    async with ws_client as ws:
        async for r in ws.subscribe(
            gql.gql(f"""subscription KarenThreads($fgroup_id: String!, $marketable_name: String!, $marketable_version: Int!, $inprocess_tool_names: [String!]!) {{
                bot_threads_and_calls_subs(fgroup_id: $fgroup_id, marketable_name: $marketable_name, marketable_version: $marketable_version, inprocess_tool_names: $inprocess_tool_names, max_threads: {MAX_THREADS}, want_personas: true, want_threads: true, want_messages: true) {{
                    {gql_utils.gql_fields(FBotThreadsAndCallsSubs)}
                }}
            }}"""),
            variable_values={
                "fgroup_id": bc.fgroup_id,
                "marketable_name": bc.marketable_name,
                "marketable_version": bc.marketable_version,
                "inprocess_tool_names": [t.name for t in bc.inprocess_tools],
            },
        ):
            upd = gql_utils.dataclass_from_dict(r["bot_threads_and_calls_subs"], FBotThreadsAndCallsSubs)
            handled = False
            reassign_threads = False
            logger.info("subs %s %s %s" % (upd.news_action, upd.news_about, upd.news_payload_id))

            if upd.news_about == "flexus_persona":
                if upd.news_action in ["INSERT", "UPDATE"]:
                    assert upd.news_payload_persona.ws_id
                    assert upd.news_payload_persona.ws_timezone
                    handled = True
                    persona_id = upd.news_payload_id
                    if bot := bc.bots_running.get(persona_id, None):
                        if bot.eventgen.persona.persona_setup != upd.news_payload_persona.persona_setup:
                            logger.info("Persona %s setup changed, restarting bot." % persona_id)
                            bc.bots_running[persona_id].atask.cancel()
                            try:
                                await bc.bots_running[persona_id].atask
                            except asyncio.CancelledError:
                                pass
                            del bc.bots_running[persona_id]
                    if persona_id not in bc.bots_running:
                        rcx = RobotContext(fclient, upd.news_payload_persona)
                        bc.bots_running[persona_id] = BotInstance(
                            fclient=fclient,
                            atask=asyncio.create_task(crash_boom_bang(fclient, rcx, bc.bot_main_loop)),
                            eventgen=rcx,
                        )
                        reassign_threads = True

                elif upd.news_action == "DELETE":
                    handled = True
                    persona_id = upd.news_payload_id
                    if persona_id in bc.bots_running:
                        bc.bots_running[persona_id].atask.cancel()
                        try:
                            await bc.bots_running[persona_id].atask
                        except asyncio.CancelledError:
                            pass
                        del bc.bots_running[persona_id]

            elif upd.news_about == "flexus_thread":
                if upd.news_action in ["INSERT", "UPDATE"]:
                    handled = True
                    thread = upd.news_payload_thread
                    if thread.ft_id in bc.thread_tracker:
                        bc.thread_tracker[thread.ft_id].thread_fields = thread
                    else:
                        bc.thread_tracker[thread.ft_id] = FThreadWithMessages(thread.ft_persona_id, thread_fields=thread, thread_messages=dict())
                    persona_id = thread.ft_persona_id
                    if persona_id in bc.bots_running:
                        bc.bots_running[persona_id].eventgen._parked_threads[thread.ft_id] = thread
                        bc.bots_running[persona_id].eventgen._parked_anything_new.set()
                    reassign_threads = True

                elif upd.news_action in ["DELETE", "STOP_TRACKING"]:
                    # threads are never deleted (DELETE), but whatever it's a garbage collector for very old threads or something, let's handle that too
                    handled = True
                    if upd.news_payload_id in bc.thread_tracker:
                        logger.info("%s deleted from thread_tracker" % upd.news_payload_id)
                        del bc.thread_tracker[upd.news_payload_id]
                    reassign_threads = True

            elif upd.news_about == "flexus_thread_message":
                if upd.news_action in ["INSERT", "UPDATE"]:
                    message = upd.news_payload_thread_message
                    handled = True
                    if message.ftm_belongs_to_ft_id in bc.thread_tracker:
                        k = "%03d:%03d" % (message.ftm_alt, message.ftm_num)
                        bc.thread_tracker[message.ftm_belongs_to_ft_id].thread_messages[k] = message
                        persona_id = bc.thread_tracker[message.ftm_belongs_to_ft_id].persona_id
                        if persona_id in bc.bots_running:
                            bc.bots_running[persona_id].eventgen._parked_messages[k] = message
                            bc.bots_running[persona_id].eventgen._parked_anything_new.set()
                        else:
                            logger.info("Thread %s is about persona=%s which is not running here." % (message.ftm_belongs_to_ft_id, persona_id))
                    else:
                        logger.info("Thread %s not found for the new message arrived, most likely ok because server side sends messages again when it sees a new untracked thread." % message.ftm_belongs_to_ft_id)
                    if message.ftm_role == "kernel" and "logs" in message.ftm_provenance and message.ftm_provenance["logs"]:
                        logger.info("Lark logs in %s:%03d:%03d:\n%s" % (message.ftm_belongs_to_ft_id, message.ftm_alt, message.ftm_num, "\n".join(message.ftm_provenance["logs"])))
                elif upd.news_action == "DELETE":
                    # messages are never deleted as well
                    handled = True

            elif upd.news_about == "flexus_tool_call":
                if upd.news_action in ["CALL"]:
                    handled = True
                    toolcall = upd.news_payload_toolcall
                    persona_id = toolcall.connected_persona_id
                    if persona_id in bc.bots_running:
                        bot = bc.bots_running[persona_id]
                        if toolcall.fcall_name not in bot.eventgen._handler_per_tool:
                            # give bot main loop a couple of seconds to start up and install the handler, it's async everything here ... :/
                            for _ in range(10):
                                if bot.eventgen._ready:
                                    break
                                if await ckit_shutdown.wait(1):
                                    break
                        set1 = set(t.name for t in bc.inprocess_tools)
                        set2 = set(bot.eventgen._handler_per_tool.keys())
                        if set1 != set2:
                            logger.error(
                                "Whoops make sure you call on_tool_call() for each of inprocess_tools.\nYou advertise: %r\nYou have hanlders: %r"
                                % (set1, set2)
                            )
                            ckit_shutdown.shutdown_event.set()
                            break
                        assert toolcall.fcall_name in set1
                        assert toolcall.fcall_name in set2
                        bot.eventgen._parked_toolcalls.append(toolcall)
                        bot.eventgen._parked_anything_new.set()
                    else:
                        logger.info("%s is about persona=%s which is not running here." % (toolcall.fcall_id, persona_id))

            elif upd.news_action == "INITIAL_UPDATES_OVER":
                if len(bc.bots_running) == 0:
                    logger.warning("backend knows of zero bots located in group %s, with marketable_name=%r and marketable_version=%r" % (
                        bc.fgroup_id, bc.marketable_name, bc.marketable_version
                    ))
                handled = True

            elif upd.news_action == "SUPERTEST":
                # This is simple startup-shutdown test as a part of CI, to catch simple problems earlier
                ckit_shutdown.shutdown_event.set()
                logger.info(f"Super test is passed with msg: {upd.news_payload_id}")
                handled = True

            if not handled:
                logger.warning("Subscription has sent me something I can't understand:\n%s\n" % upd)

            if reassign_threads:
                assert len(bc.thread_tracker) <= MAX_THREADS, "backend should send STOP_TRACKING wtf"
                # There we go, now it's O(1) because it's limited
                for bot in bc.bots_running.values():
                    to_test = list(bot.eventgen.latest_threads.keys())
                    for t in to_test:
                        if t not in bc.thread_tracker:
                            del bot.eventgen.latest_threads[t]
                for tid, thread in bc.thread_tracker.items():
                    persona_id = thread.thread_fields.ft_persona_id
                    assert persona_id, "Oops persona_id is empty 8-[  ]"
                    if persona_id in bc.bots_running:
                        ev = bc.bots_running[persona_id].eventgen
                        if tid not in ev.latest_threads:
                            ev.latest_threads[tid] = thread
                            ev._parked_messages.update(thread.thread_messages)
                            ev._parked_anything_new.set()
                    else:
                        logger.info("Thread %s belongs to persona %s, but no bot is running for it, maybe a little async not a big deal." % (tid, persona_id))

            if ckit_shutdown.shutdown_event.is_set():
                break


async def shutdown_bots(
    bc: BotsCollection,
):
    still_running = [bot for bot in bc.bots_running.values() if not bot.atask.done()]
    if still_running:
        logger.info(f"Cancelling {len(still_running)} remaining bot tasks...")
        for bot in still_running:
            bot.atask.cancel()
        await asyncio.gather(*[bot.atask for bot in still_running], return_exceptions=True)

    logger.info("shutdown_bots success")


async def run_bots_in_this_group(
    fclient: ckit_client.FlexusClient,
    *,
    fgroup_id: str,
    marketable_name: str,
    marketable_version: int,
    inprocess_tools: List[ckit_cloudtool.CloudTool],
    bot_main_loop: Callable[[ckit_client.FlexusClient, RobotContext], Awaitable[None]],
) -> None:
    bc = BotsCollection(
        fgroup_id=fgroup_id,
        marketable_name=marketable_name,
        marketable_version=marketable_version,
        inprocess_tools=inprocess_tools,
        bot_main_loop=bot_main_loop,
    )

    await ckit_service_exec.run_typical_single_subscription_with_restart_on_network_errors(fclient, subscribe_and_produce_callbacks, bc)
    await shutdown_bots(bc)
    logger.info("run_bots_in_this_group exit")
