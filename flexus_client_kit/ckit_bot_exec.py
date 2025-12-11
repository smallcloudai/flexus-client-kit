import json
import re
import asyncio
import logging
import os
import sys
import time
import argparse
import yaml
from typing import Dict, List, Optional, Any, Callable, Awaitable, NamedTuple, Union, Type, TypeVar

import gql
import gql.transport.exceptions

from flexus_client_kit import ckit_client, gql_utils, ckit_service_exec, ckit_kanban, ckit_cloudtool
from flexus_client_kit import ckit_ask_model, ckit_shutdown, ckit_utils, ckit_bot_query, ckit_scenario
from flexus_client_kit import ckit_passwords
from flexus_client_kit import erp_schema


logger = logging.getLogger("btexe")


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
    def __init__(self, fclient: ckit_client.FlexusClient, p: ckit_bot_query.FPersonaOutput):
        self._handler_updated_message: Optional[Callable[[ckit_ask_model.FThreadMessageOutput], Awaitable[None]]] = None
        self._handler_upd_thread: Optional[Callable[[ckit_ask_model.FThreadOutput], Awaitable[None]]] = None
        self._handler_updated_task: Optional[Callable[[ckit_kanban.FPersonaKanbanTaskOutput], Awaitable[None]]] = None
        self._handler_per_tool: Dict[str, Callable[[Dict[str, Any]], Awaitable[str]]] = {}
        self._handler_per_erp_table_change: Dict[str, Callable[[str, Optional[Any], Optional[Any]], Awaitable[None]]] = {}
        self._reached_main_loop = False
        self._completed_initial_unpark = False
        self._parked_messages: Dict[str, ckit_ask_model.FThreadMessageOutput] = {}
        self._parked_threads: Dict[str, ckit_ask_model.FThreadOutput] = {}
        self._parked_tasks: Dict[str, ckit_kanban.FPersonaKanbanTaskOutput] = {}
        self._parked_toolcalls: List[ckit_cloudtool.FCloudtoolCall] = []
        self._parked_erp_changes: List[tuple[str, str, Optional[Dict[str, Any]], Optional[Dict[str, Any]]]] = []
        self._parked_anything_new = asyncio.Event()
        # These fields are designed for direct access:
        self.fclient = fclient
        self.persona = p
        self.latest_threads: Dict[str, ckit_bot_query.FThreadWithMessages] = dict()
        self.latest_tasks: Dict[str, ckit_kanban.FPersonaKanbanTaskOutput] = dict()
        self.created_ts = time.time()
        self.workdir = "/tmp/bot_workspace/%s/" % p.persona_id
        self.running_test_scenario = False
        self.running_happy_yaml = ""
        os.makedirs(self.workdir, exist_ok=True)

    def on_updated_message(self, handler: Callable[[ckit_ask_model.FThreadMessageOutput], Awaitable[None]]):
        self._handler_updated_message = handler
        return handler

    def on_updated_thread(self, handler: Callable[[ckit_ask_model.FThreadOutput], Awaitable[None]]):
        self._handler_upd_thread = handler
        return handler

    def on_updated_task(self, handler: Callable[[ckit_kanban.FPersonaKanbanTaskOutput], Awaitable[None]]):
        self._handler_updated_task = handler
        return handler

    def on_tool_call(self, tool_name: str):
        def decorator(handler: Callable[[ckit_cloudtool.FCloudtoolCall, Dict[str, Any]], Awaitable[Union[str, List[Dict[str, str]]]]]):
            self._handler_per_tool[tool_name] = handler
            return handler
        return decorator

    def on_erp_change(self, table_name: str):
        def decorator(handler: Callable[[str, Optional[Any], Optional[Any]], Awaitable[None]]):
            if table_name not in erp_schema.ERP_TABLE_TO_SCHEMA:
                raise ValueError(f"Unknown ERP table {table_name!r}. Known tables: {list(erp_schema.ERP_TABLE_TO_SCHEMA.keys())}")
            self._handler_per_erp_table_change[table_name] = handler
            return handler
        return decorator

    async def unpark_collected_events(self, sleep_if_no_work: float, turn_tool_calls_into_tasks: bool = False) -> List[asyncio.Task]:
        # logger.info("%s unpark_collected_events() started %d %d %d" % (self.persona.persona_id, len(self._parked_messages), len(self._parked_threads), len(self._parked_toolcalls)))
        self._reached_main_loop = True
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

        todo = list(self._parked_tasks.keys())
        for k in todo:
            task = self._parked_tasks.pop(k)
            did_anything = True
            if self._handler_updated_task:
                try:
                    await self._handler_updated_task(task)
                except Exception as e:
                    logger.error("%s error in on_updated_task handler: %s\n%s", self.persona.persona_id, type(e).__name__, e, exc_info=e)

        erp_changes = list(self._parked_erp_changes)
        self._parked_erp_changes.clear()
        for table_name, action, new_record_dict, old_record_dict in erp_changes:
            did_anything = True
            handler = self._handler_per_erp_table_change.get(table_name)
            if handler:
                try:
                    dataclass_type = erp_schema.ERP_TABLE_TO_SCHEMA[table_name]
                    new_record = gql_utils.dataclass_from_dict(new_record_dict, dataclass_type) if new_record_dict else None
                    old_record = gql_utils.dataclass_from_dict(old_record_dict, dataclass_type) if old_record_dict else None
                    await handler(action, new_record, old_record)
                except Exception as e:
                    logger.error("%s error in on_erp_change(%r) handler: %s\n%s", self.persona.persona_id, table_name, type(e).__name__, e, exc_info=e)

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
            self._completed_initial_unpark = True
            try:
                await asyncio.wait_for(self._parked_anything_new.wait(), timeout=sleep_if_no_work)
            except asyncio.TimeoutError:
                pass

        return bg_calls   # empty if not turn_tool_calls_into_tasks (most regular bots)


    async def _local_tool_call(self, fclient: ckit_client.FlexusClient, toolcall: ckit_cloudtool.FCloudtoolCall) -> None:
        logger.info("%s local_tool_call %s %s(%s) from thread %s" % (self.persona.persona_id, toolcall.fcall_id, toolcall.fcall_name, toolcall.fcall_arguments, toolcall.fcall_ft_id))
        already_serialized = False
        try:
            args = json.loads(toolcall.fcall_arguments)
            if not isinstance(args, dict):
                raise json.JSONDecodeError("Toplevel is not a dict")
            handler = self._handler_per_tool[toolcall.fcall_name]
            tool_result = await handler(toolcall, args)
            if isinstance(tool_result, list):  # Multimodal [{m_type: .., m_content: ...}, ...]
                for item in tool_result:
                    if not isinstance(item, dict):
                        raise ValueError("Tool call handler returned list with non-dict item: %r" % (item,))
                    if "m_type" not in item or "m_content" not in item:
                        raise ValueError("Tool call handler list items must have m_type and m_content: %r" % (item,))
                    if not isinstance(item["m_type"], str) or not isinstance(item["m_content"], str):
                        raise ValueError("m_type and m_content must be strings: %r" % (item,))
                tool_result = json.dumps(tool_result)
                already_serialized = True
            elif not isinstance(tool_result, str):
                raise ValueError("Tool call handler must return a string or list, got instead: %r" % (tool_result,))
            if tool_result == "":
                logger.warning("Tool call %s returned an empty string. Bad practice, model will not know what's happening!" % toolcall.fcall_name)
        except json.JSONDecodeError:
            # nothing in logs -- normal for a model to produce garbage on occasion
            tool_result = "Arguments expected to be a valid json, instead got: %r" % args
        except ckit_cloudtool.WaitForSubchats:
            tool_result = "WAIT_SUBCHATS"
        except ckit_cloudtool.NeedsConfirmation as e:
            logger.info("%s needs human confirmation: %s" % (toolcall.fcall_id, e.confirm_explanation))
            await ckit_cloudtool.cloudtool_confirmation_request(fclient, toolcall.fcall_id, e.confirm_setup_key, e.confirm_command, e.confirm_explanation)
            tool_result = "POSTED_NEED_CONFIRMATION"
        except gql.transport.exceptions.TransportQueryError as e:
            logger.error("%s The construction of system prompt and tools generally should not produce backend errors, but here's one: %s", toolcall.fcall_id, e, exc_info=e)
            tool_result = f"Error: {e}"  # Pass through GraphQL error messages to the model
        except Exception as e:
            logger.error("%s Tool call failed: %s" % (toolcall.fcall_id, e), exc_info=e)  # full error and stack for the author of the bot
            tool_result = "Tool error, see logs for details"  # Not too much visible for end user
        prov = json.dumps({"system": fclient.service_name})
        if tool_result != "WAIT_SUBCHATS" and tool_result != "POSTED_NEED_CONFIRMATION" and tool_result != "ALREADY_POSTED_RESULT":
            if not already_serialized:
                tool_result = json.dumps(tool_result)
            await ckit_cloudtool.cloudtool_post_result(fclient, toolcall.fcall_id, toolcall.fcall_untrusted_key, tool_result, prov)


class BotInstance(NamedTuple):
    fclient: ckit_client.FlexusClient
    atask: asyncio.Task
    instance_rcx: RobotContext


async def crash_boom_bang(fclient: ckit_client.FlexusClient, rcx: RobotContext, bot_main_loop: Callable[[ckit_client.FlexusClient, RobotContext], Awaitable[None]]) -> None:
    logger.info("%s START name=%r" % (rcx.persona.persona_id, rcx.persona.persona_name))
    while not ckit_shutdown.shutdown_event.is_set():
        try:
            await bot_main_loop(fclient, rcx)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error("%s Bot main loop problem: %s %s", rcx.persona.persona_id, type(e).__name__, e, exc_info=True)
        logger.info("%s will sleep 60 seconds and restart", rcx.persona.persona_id)
        await ckit_shutdown.wait(60)
    logger.info("%s STOP" % rcx.persona.persona_id)


async def i_am_still_alive(
    fclient: ckit_client.FlexusClient,
    marketable_name: str,
    marketable_version: int,
) -> None:
    while not ckit_shutdown.shutdown_event.is_set():
        try:
            http_client = await fclient.use_http()
            async with http_client as http:
                await http.execute(
                    gql.gql("""mutation BotConfirmExists($marketable_name: String!, $marketable_version: Int!, $ws_id_prefix: String!) {
                        bot_confirm_exists(marketable_name: $marketable_name, marketable_version: $marketable_version, ws_id_prefix: $ws_id_prefix)
                    }"""),
                    variable_values={
                        "marketable_name": marketable_name,
                        "marketable_version": marketable_version,
                        "ws_id_prefix": fclient.ws_id,
                    },
                )
                logger.info("i_am_still_alive %s:%d ws_id=%s", marketable_name, marketable_version, fclient.ws_id)
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


class BotsCollection:
    def __init__(
        self,
        ws_id_prefix: str,
        marketable_name: str,
        marketable_version: int,
        inprocess_tools: List[ckit_cloudtool.CloudTool],
        bot_main_loop: Callable[[ckit_client.FlexusClient, RobotContext], Awaitable[None]],
        subscribe_to_erp_tables: List[str] = [],
        running_test_scenario: bool = False,
        running_happy_yaml: str = "",
    ):
        self.ws_id_prefix = ws_id_prefix
        self.marketable_name = marketable_name
        self.marketable_version = marketable_version
        self.inprocess_tools = inprocess_tools
        self.bot_main_loop = bot_main_loop
        self.subscribe_to_erp_tables = subscribe_to_erp_tables
        self.bots_running: Dict[str, BotInstance] = {}
        self.thread_tracker: Dict[str, ckit_bot_query.FThreadWithMessages] = {}
        self.running_test_scenario = running_test_scenario
        self.running_happy_yaml = running_happy_yaml


async def subscribe_and_produce_callbacks(
    fclient: ckit_client.FlexusClient,
    ws_client: gql.Client,
    bc: BotsCollection,
):
    MAX_THREADS = 100
    # XXX check if it will really crash downstream without this check
    assert fclient.service_name.startswith(bc.marketable_name)

    bc.thread_tracker.clear()  # Control reaches this after exception and reconnect, a new subscription will send all the threads anew, need to clear

    async with ws_client as ws:
        assert fclient.ws_id is not None or fclient.group_id is not None
        # group_id takes priority over ws_id, send only one (not both)
        use_group_id = fclient.group_id if fclient.group_id else None
        use_ws_id_prefix = None if use_group_id else fclient.ws_id
        async for r in ws.subscribe(
            gql.gql(f"""subscription KarenThreads($marketable_name: String!, $marketable_version: Int!, $inprocess_tool_names: [String!]!, $want_erp_tables: [String!]!, $ws_id_prefix: String, $group_id: String) {{
                bot_threads_calls_tasks(marketable_name: $marketable_name, marketable_version: $marketable_version, inprocess_tool_names: $inprocess_tool_names, max_threads: {MAX_THREADS}, want_personas: true, want_threads: true, want_messages: true, want_tasks: true, want_erp_tables: $want_erp_tables, ws_id_prefix: $ws_id_prefix, group_id: $group_id) {{
                    {gql_utils.gql_fields(ckit_bot_query.FBotThreadsCallsTasks)}
                }}
            }}"""),
            variable_values={
                "marketable_name": bc.marketable_name,
                "marketable_version": bc.marketable_version,
                "inprocess_tool_names": [t.name for t in bc.inprocess_tools],
                "want_erp_tables": bc.subscribe_to_erp_tables,
                "ws_id_prefix": use_ws_id_prefix,
                "group_id": use_group_id,
            },
        ):
            upd = gql_utils.dataclass_from_dict(r["bot_threads_calls_tasks"], ckit_bot_query.FBotThreadsCallsTasks)
            handled = False
            reassign_threads = False
            # logger.info("subs %s %s %s" % (upd.news_action, upd.news_about, upd.news_payload_id))

            if upd.news_about == "flexus_persona":
                if upd.news_action in ["INSERT", "UPDATE"]:
                    assert upd.news_payload_persona.ws_id
                    assert upd.news_payload_persona.ws_timezone
                    handled = True
                    persona_id = upd.news_payload_id
                    if bot := bc.bots_running.get(persona_id, None):
                        if bot.instance_rcx.persona.persona_setup != upd.news_payload_persona.persona_setup:
                            logger.info("Persona %s setup changed, restarting bot." % persona_id)
                            bc.bots_running[persona_id].atask.cancel()
                            try:
                                await bc.bots_running[persona_id].atask
                            except asyncio.CancelledError:
                                pass
                            del bc.bots_running[persona_id]
                    if persona_id not in bc.bots_running:
                        rcx = RobotContext(fclient, upd.news_payload_persona)
                        rcx.running_test_scenario = bc.running_test_scenario
                        rcx.running_happy_yaml = bc.running_happy_yaml
                        bc.bots_running[persona_id] = BotInstance(
                            fclient=fclient,
                            atask=asyncio.create_task(crash_boom_bang(fclient, rcx, bc.bot_main_loop)),
                            instance_rcx=rcx,
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
                        bc.thread_tracker[thread.ft_id] = ckit_bot_query.FThreadWithMessages(thread.ft_persona_id, thread, thread_messages=dict())
                    persona_id = thread.ft_persona_id
                    if persona_id in bc.bots_running:
                        bc.bots_running[persona_id].instance_rcx._parked_threads[thread.ft_id] = thread
                        bc.bots_running[persona_id].instance_rcx._parked_anything_new.set()
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
                            bc.bots_running[persona_id].instance_rcx._parked_messages[k] = message
                            bc.bots_running[persona_id].instance_rcx._parked_anything_new.set()
                        else:
                            logger.info("Thread %s is about persona=%s which is not running here." % (message.ftm_belongs_to_ft_id, persona_id))
                    else:
                        logger.info("Thread %s not found for the new message arrived, most likely ok because server side sends messages again when it sees a new untracked thread." % message.ftm_belongs_to_ft_id)
                    if message.ftm_role == "assistant" and "lark_logs1" in message.ftm_provenance and message.ftm_provenance["lark_logs1"]:
                        logger.info("Lark1 logs in %s:%03d:%03d:\n%s" % (message.ftm_belongs_to_ft_id, message.ftm_alt, message.ftm_num, "\n".join(message.ftm_provenance["lark_logs1"])))
                    if message.ftm_role == "assistant" and "lark_logs2" in message.ftm_provenance and message.ftm_provenance["lark_logs2"]:
                        logger.info("Lark2 logs in %s:%03d:%03d:\n%s" % (message.ftm_belongs_to_ft_id, message.ftm_alt, message.ftm_num, "\n".join(message.ftm_provenance["lark_logs2"])))
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
                        if toolcall.fcall_name not in bot.instance_rcx._handler_per_tool:
                            # give bot main loop a couple of seconds to start up and install the handler, it's async everything here ... :/
                            for _ in range(10):
                                if bot.instance_rcx._reached_main_loop:
                                    break
                                if await ckit_shutdown.wait(1):
                                    break
                        set1 = set(t.name for t in bc.inprocess_tools)
                        set2 = set(bot.instance_rcx._handler_per_tool.keys())
                        if set1 != set2:
                            logger.error(
                                "Whoops make sure you call on_tool_call() for each of inprocess_tools.\nYou advertise: %r\nYou have hanlders: %r"
                                % (set1, set2)
                            )
                            ckit_shutdown.shutdown_event.set()
                            break
                        assert toolcall.fcall_name in set1
                        assert toolcall.fcall_name in set2
                        bot.instance_rcx._parked_toolcalls.append(toolcall)
                        bot.instance_rcx._parked_anything_new.set()
                    else:
                        logger.info("%s is about persona=%s which is not running here." % (toolcall.fcall_id, persona_id))

            elif upd.news_about == "flexus_persona_kanban_task":
                if upd.news_action in ["INSERT", "UPDATE"]:
                    handled = True
                    task = upd.news_payload_task
                    persona_id = task.persona_id
                    if persona_id in bc.bots_running:
                        bc.bots_running[persona_id].instance_rcx.latest_tasks[task.ktask_id] = task
                        bc.bots_running[persona_id].instance_rcx._parked_tasks[task.ktask_id] = task
                        bc.bots_running[persona_id].instance_rcx._parked_anything_new.set()
                    else:
                        logger.info("Task %s is about persona=%s which is not running here." % (task.ktask_id, persona_id))
                elif upd.news_action == "DELETE":
                    handled = True
                    for p in bc.bots_running.values():
                        if upd.news_payload_id in p.instance_rcx.latest_tasks:
                            del p.instance_rcx.latest_tasks[upd.news_payload_id]

            elif upd.news_about.startswith("erp."):
                table_name = upd.news_about[4:]
                if upd.news_action in ["INSERT", "UPDATE", "DELETE"]:
                    handled = True
                    new_record = upd.news_payload_erp_record_new
                    old_record = upd.news_payload_erp_record_old
                    for bot in bc.bots_running.values():
                        bot.instance_rcx._parked_erp_changes.append((table_name, upd.news_action, new_record, old_record))
                        bot.instance_rcx._parked_anything_new.set()

            elif upd.news_action == "INITIAL_UPDATES_OVER":
                if len(bc.bots_running) == 0:
                    logger.warning("backend knows of zero bots with marketable_name=%r and marketable_version=%r, if you are trying to run a dev bot, the previous dev bot might got upgraded to a build (not dev) version" % (
                        bc.marketable_name, bc.marketable_version
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
                assert len(bc.thread_tracker) <= MAX_THREADS, "backend should send STOP_TRACKING wtf"   # actually sometimes triggers after reconnect :/
                # There we go, now it's O(1) because it's limited
                for bot in bc.bots_running.values():
                    to_test = list(bot.instance_rcx.latest_threads.keys())
                    for t in to_test:
                        if t not in bc.thread_tracker:
                            del bot.instance_rcx.latest_threads[t]
                for tid, thread in bc.thread_tracker.items():
                    persona_id = thread.thread_fields.ft_persona_id
                    assert persona_id, "Oops persona_id is empty 8-[  ]"
                    if persona_id in bc.bots_running:
                        ev = bc.bots_running[persona_id].instance_rcx
                        if tid not in ev.latest_threads:
                            ev.latest_threads[tid] = thread
                            ev._parked_messages.update(thread.thread_messages)
                            ev._parked_anything_new.set()
                    else:
                        ckit_utils.log_with_throttle(logger.info,
                            "Thread %s belongs to persona %s, but no bot is running for it, maybe a little async not a big deal.", tid, persona_id)

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


async def run_happy_trajectory(
    bc: BotsCollection,
    scenario: ckit_scenario.ScenarioSetup,
    trajectory_yaml_path: str,
) -> None:
    with open(trajectory_yaml_path) as f:
        trajectory_happy = f.read()

    trajectory_data = yaml.safe_load(trajectory_happy)
    judge_instructions = trajectory_data.get("judge_instructions", "")

    first_calls = None
    messages = trajectory_data["messages"]
    if messages and len(messages) >= 2:
        first_assistant = messages[1]
        if first_assistant["role"] == "assistant" and first_assistant["tool_calls"]:
            first_calls = []
            for tc in first_assistant["tool_calls"]:
                first_calls.append({
                    "type": tc.get("type", "function"),
                    "function": {
                        "name": tc["function"]["name"],
                        "arguments": tc["function"]["arguments"]
                    }
                })
    logger.info(f"bot_activate() first_calls, taken from the happy path:\n{first_calls}")
    trajectory_happy_messages_only = ckit_scenario.yaml_dump_with_multiline({"messages": trajectory_data["messages"]})

    skill__scenario = os.path.splitext(os.path.basename(trajectory_yaml_path))[0]
    bot_version = ckit_client.marketplace_version_as_str(scenario.persona.persona_marketable_version)
    model_name = scenario.explicit_model or scenario.persona.persona_preferred_model
    await ckit_scenario.bot_scenario_result_upsert(
        scenario.fclient,
        ckit_scenario.BotScenarioUpsertInput(
            btest_marketable_name=scenario.persona.persona_marketable_name,
            btest_marketable_version_str=bot_version,
            btest_name=skill__scenario,
            btest_model=model_name,
            btest_experiment=scenario.experiment or "",
            btest_trajectory_happy=trajectory_happy,
            btest_trajectory_actual="",
            btest_rating_happy=0,
            btest_rating_actually=0,
            btest_feedback_happy="",
            btest_feedback_actually="",
            btest_shaky_human=0,
            btest_shaky_tool=0,
            btest_criticism="{}",
            btest_cost=0,
        ),
    )
    logger.info("Saved happy trajectory to database before starting test, fake cloud tools will use it")

    max_steps = 30
    ft_id: Optional[str] = None
    cost_judge = 0
    cost_human = 0
    cost_tools = 0
    stop_reason = ""
    last_human_message = ""
    try:
        assert "__" in skill__scenario
        skill = skill__scenario.split("__")[0]
        assert skill != "default", "the first part before \"__\" in scenario name should be the bot name, not \"default\""
        if skill == scenario.persona.persona_marketable_name:
            skill = "default"
        for step in range(max_steps):
            ht1 = time.time()
            result = await ckit_scenario.scenario_generate_human_message(
                scenario.fclient,
                trajectory_happy,
                scenario.fgroup_id,
                ft_id,
            )
            ht2 = time.time()
            cost_human += result.cost
            stop_reason = result.stop_reason
            last_human_message = result.next_human_message
            logger.info("human says %0.2fs: %r shaky=%s stop_reason=%r" % (ht2-ht1, result.next_human_message, result.shaky, result.stop_reason))
            if result.scenario_done:
                break

            if not ft_id:  # same as step==0
                ft_id = await ckit_ask_model.bot_activate(
                    client=scenario.fclient,
                    who_is_asking="trajectory_scenario",
                    persona_id=scenario.persona.persona_id,
                    skill=skill,
                    first_question=result.next_human_message,
                    first_calls=first_calls,
                    title="Trajectory Test",
                    ft_btest_name=skill__scenario,
                    model=scenario.explicit_model,
                )
                logger.info(f"Scenario thread {ft_id}")
            else:
                http = await scenario.fclient.use_http()
                await ckit_ask_model.thread_add_user_message(
                    http=http,
                    ft_id=ft_id,
                    content=result.next_human_message,
                    who_is_asking="trajectory_scenario",
                    ftm_alt=100,
                    ftm_provenance={"who_is_asking": "trajectory_scenario", "shaky": result.shaky},
                )

            wait_secs = 600  # increased from 160 for subchat scenarios
            start_time = time.time()
            while time.time() - start_time < wait_secs:
                my_bot = bc.bots_running.get(scenario.persona.persona_id, None)
                if my_bot is None:
                    logger.info("WAIT for bot to initialize...")
                    if await ckit_shutdown.wait(1):
                        break
                    continue
                try:
                    await asyncio.wait_for(my_bot.instance_rcx._parked_anything_new.wait(), timeout=1.0)
                except asyncio.TimeoutError:
                    pass
                if ckit_shutdown.shutdown_event.is_set():
                    break
                if not my_bot.instance_rcx._completed_initial_unpark:
                    logger.info("WAIT for bot to complete initial unpark, it might have crashed or still initializing")
                    if await ckit_shutdown.wait(1):
                        break
                    continue
                my_thread: Optional[ckit_bot_query.FThreadWithMessages] = my_bot.instance_rcx.latest_threads.get(ft_id, None)
                if my_thread is None:
                    logger.info("WAIT for thread to appear in bot's latest_threads...")
                    continue
                sorted_messages = sorted(my_thread.thread_messages.values(), key=lambda m: (m.ftm_alt, m.ftm_num))
                trajectory_msg_count = sum(
                    1 for k, m in my_thread.thread_messages.items()
                    if m.ftm_role == "user" and m.ftm_provenance.get("who_is_asking") == "trajectory_scenario"
                )
                if trajectory_msg_count < step + 1:
                    # logger.info("WAIT for the message the human just posted to appear...")
                    continue
                # Cool now we can believe my_thread.thread_fields because async notifications sent here are not crazy late (and it's fine
                # if they are late a little bit, just like the UI works fine based on subscription only)
                if my_thread.thread_fields.ft_need_user != -1:
                    if my_thread.thread_fields.ft_need_user != 100:
                        logger.warning("Whoops my_thread.thread_fields.ft_need_user=%d that's crazy, did the thread branch off under my supposedly controlled conditions?")
                        return
                    break
                continue  # wait for next second, silently (no "WAIT waiting for the actual reponse")
            else:
                logger.error("Timeout after %d seconds, no reponse from model or tools :/", wait_secs)
                stop_reason = "timeout"
                break

            continue  # post the next human message

        else:
            logger.info("Scenario did not complete in %d steps, quit", max_steps)

    except asyncio.exceptions.CancelledError:
        logger.info("Scenario is cancelled")

    finally:
        logger.info("Scenario is over, problem or not")
        threads_output = await ckit_scenario.scenario_print_threads(scenario.fclient, scenario.fgroup_id)
        logger.info("Scenario is over, threads in fgroup_id=%s:\n%s", scenario.fgroup_id, threads_output)

        if ft_id and stop_reason != "timeout":
            judge_result = await ckit_scenario.scenario_judge(
                scenario.fclient,
                trajectory_happy_messages_only,
                ft_id,
                judge_instructions,
            )
            cost_judge += judge_result.cost

            output_dir = os.path.abspath(os.path.join(os.getcwd(), "scenario-dumps"))
            logger.info(f"Scenario output directory: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)

            shaky_human = sum(1 for m in sorted_messages if m.ftm_role == "user" and m.ftm_provenance.get("shaky") == True)
            shaky_tool = sum(1 for m in sorted_messages if m.ftm_role == "tool" and m.ftm_provenance.get("shaky") == True)

            cost_assistant = my_thread.thread_fields.ft_coins
            for m in sorted_messages:
                if m.ftm_role == "tool" and m.ftm_usage:
                    cost_tools += m.ftm_usage["coins"]

            cost_stop_output = (
                f"Happy trajectory rating: \033[93m{judge_result.rating_happy}/10\033[0m\n"
                f"Happy trajectory feedback: {judge_result.feedback_happy}\n"
                f"Actual trajectory rating: \033[93m{judge_result.rating_actually}/10\033[0m\n"
                f"Actual trajectory feedback: {judge_result.feedback_actually}\n"
                f"    Cost breakdown:\n"
                f"        judge: \033[93m${('%0.2f' % (cost_judge / 1e6))}\033[0m\n"
                f"        human: \033[93m${('%0.2f' % (cost_human / 1e6))}\033[0m\n"
                f"        tools: \033[93m${('%0.2f' % (cost_tools / 1e6))}\033[0m\n"
                f"        assst: \033[93m${('%0.2f' % (cost_assistant / 1e6))}\033[0m\n"
                f"    Stop reason: \033[97m{stop_reason}\033[0m\n"
            )
            logger.info(f"Summary:\n{cost_stop_output}")

            experiment_suffix = f"-{scenario.experiment}" if scenario.experiment else ""
            happy_path = os.path.join(output_dir, f"{skill__scenario}-v{bot_version}{experiment_suffix}-{model_name}-happy.yaml")
            with open(happy_path, "w") as f:
                f.write("# This is generated file don't edit!\n\n")
                f.write(trajectory_happy_messages_only)
            logger.info(f"exported {happy_path}")

            trajectory_actual = ckit_scenario.fmessages_to_yaml(sorted_messages)
            actual_path = os.path.join(output_dir, f"{skill__scenario}-v{bot_version}{experiment_suffix}-{model_name}-actual.yaml")
            with open(actual_path, "w") as f:
                f.write("# This is generated file don't edit!\n\n")
                f.write(trajectory_actual)
            logger.info(f"exported {actual_path}")

            score_data = {
                "happy_rating": judge_result.rating_happy,
                "happy_feedback": judge_result.feedback_happy,
                "actual_rating": judge_result.rating_actually,
                "actual_feedback": judge_result.feedback_actually,
                "criticism": judge_result.criticism,
                "shaky_human": shaky_human,
                "shaky_tool": shaky_tool,
                "stop_reason": stop_reason,
                "stop_but_had_it_not_stopped_the_next_human_message_would_be": last_human_message,
                "cost": {
                    "judge": cost_judge,
                    "human": cost_human,
                    "tools": cost_tools,
                    "assistant": cost_assistant,
                },
            }
            score_yaml = ckit_scenario.yaml_dump_with_multiline(score_data)
            score_path = os.path.join(output_dir, f"{skill__scenario}-v{bot_version}{experiment_suffix}-{model_name}-score.yaml")
            with open(score_path, "w") as f:
                f.write(score_yaml)
            logger.info(f"exported {score_path}")

            total_cost = cost_judge + cost_human + cost_tools + cost_assistant
            await ckit_scenario.bot_scenario_result_upsert(
                scenario.fclient,
                ckit_scenario.BotScenarioUpsertInput(
                    btest_marketable_name=scenario.persona.persona_marketable_name,
                    btest_marketable_version_str=bot_version,
                    btest_name=skill__scenario,
                    btest_model=model_name,
                    btest_experiment=scenario.experiment or "",
                    btest_trajectory_happy=trajectory_happy,
                    btest_trajectory_actual=trajectory_actual,
                    btest_rating_happy=judge_result.rating_happy,
                    btest_rating_actually=judge_result.rating_actually,
                    btest_feedback_happy=judge_result.feedback_happy,
                    btest_feedback_actually=judge_result.feedback_actually,
                    btest_shaky_human=shaky_human,
                    btest_shaky_tool=shaky_tool,
                    btest_criticism=json.dumps(judge_result.criticism),
                    btest_cost=total_cost,
                ),
            )
            logger.info("Full scenario results saved to database")

        if scenario.should_cleanup:
            await scenario.cleanup()
            logger.info("Cleanup completed.")
        else:
            logger.info("Skipping cleanup (--no-cleanup flag set)")

        loop = asyncio.get_running_loop()
        ckit_shutdown.spiral_down_now(loop, enable_exit1=False)


async def run_bots_in_this_group(
    fclient: ckit_client.FlexusClient,
    *,
    marketable_name: str,
    marketable_version_str: str,
    inprocess_tools: List[ckit_cloudtool.CloudTool],
    bot_main_loop: Callable[[ckit_client.FlexusClient, RobotContext], Awaitable[None]],
    scenario_fn: str,
    install_func: Callable[[ckit_client.FlexusClient, str], Awaitable[None]],
    subscribe_to_erp_tables: List[str] = [],
) -> None:
    marketable_version = ckit_client.marketplace_version_as_int(marketable_version_str)

    if fclient.ws_id and fclient.group_id:
        raise ValueError("Both ws_id and group_id are set, only one is allowed")

    if fclient.use_ws_ticket:
        if not fclient.ws_id and not fclient.group_id:
            raise ValueError("Neither ws_id nor group_id is set, one is required")
        ws_id_prefix = fclient.ws_id  # None if using group_id

    elif fclient.api_key:
        # This is a dev bot, meaning it runs at bot author's console, using their api key
        if not fclient.ws_id and not fclient.group_id:
            r = await ckit_client.query_basic_stuff(fclient)
            for ws in r.workspaces:
                logger.info("  Workspace %r, owned by %s, name %r" % (ws.ws_id, ws.ws_owner_fuser_id, ws.root_group_name))
            logger.info("Please set FLEXUS_WORKSPACE or FLEXUS_GROUP to one of the above")
            return
        if fclient.ws_id:
            logger.info("Installing %s:%s into workspace %s", marketable_name, marketable_version_str, fclient.ws_id)
            await install_func(fclient, fclient.ws_id, marketable_name, marketable_version_str, inprocess_tools)
        ws_id_prefix = fclient.ws_id  # None if using group_id

    elif fclient.inside_radix_process:
        # Dev computer, detected by absence of FLEXUS_WS_TICKET, for testing a radix process
        superpassword, _ = await ckit_passwords.get_superuser_token_from_vault(fclient.endpoint)
        fclient.dev_ws_ticket = ckit_passwords.make_flexus_ws_ticket_from_creds(fclient.service_name, superpassword)
        ws_id_prefix = fclient.ws_id

    else:
        assert False

    scenario = None
    scenario_task = None
    running_test_scenario = False
    running_happy_yaml = ""
    fgroup_id = ""
    if scenario_fn:
        with open(scenario_fn) as f:
            running_happy_yaml = f.read()
        running_test_scenario = True
        scenario = ckit_scenario.ScenarioSetup(service_name="trajectory_replay")
        await scenario.create_group_and_hire_bot(
            marketable_name=marketable_name,
            marketable_version=marketable_version,
            persona_setup={},
        )
        fgroup_id = scenario.fgroup_id
        assert fgroup_id
    bc = BotsCollection(
        ws_id_prefix=ws_id_prefix,
        marketable_name=marketable_name,
        marketable_version=marketable_version,
        inprocess_tools=inprocess_tools,
        bot_main_loop=bot_main_loop,
        subscribe_to_erp_tables=subscribe_to_erp_tables,
        running_test_scenario=running_test_scenario,
        running_happy_yaml=running_happy_yaml,
    )
    if scenario_fn:
        scenario_task = asyncio.create_task(run_happy_trajectory(bc, scenario, scenario_fn))
        scenario_task.add_done_callback(lambda t: ckit_utils.report_crash(t, ckit_scenario.logger))
    keepalive_task = asyncio.create_task(i_am_still_alive(fclient, marketable_name, marketable_version))
    keepalive_task.add_done_callback(lambda t: ckit_utils.report_crash(t, logger))
    try:
        await ckit_service_exec.run_typical_single_subscription_with_restart_on_network_errors(fclient, subscribe_and_produce_callbacks, bc)
    finally:
        keepalive_task.cancel()
        await asyncio.gather(keepalive_task, return_exceptions=True)
        await shutdown_bots(bc)
    logger.info("run_bots_in_this_group exit")


def parse_bot_args():
    parser = ckit_scenario.bot_launch_argparse()
    args = parser.parse_args()

    if args.scenario:
        if not os.path.exists(args.scenario):
            fallback = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), os.path.basename(args.scenario))
            assert os.path.exists(fallback), f"scenario file not found at {args.scenario} or {fallback}"
            args.scenario = fallback

    return args.scenario
