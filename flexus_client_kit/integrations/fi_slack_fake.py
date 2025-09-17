import os
import time
import json
import mimetypes
import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable, List
from pymongo.collection import Collection

from flexus_client_kit import ckit_cloudtool, ckit_client, ckit_bot_exec, ckit_ask_model
from flexus_client_kit.integrations.fi_mongo_store import validate_path, download_file
from flexus_client_kit.integrations.fi_slack import (
    HELP,
    CAPTURE_SUCCESS_MSG,
    CAPTURE_ADVICE_MSG,
    UNCAPTURE_SUCCESS_MSG,
    SKIP_SUCCESS_MSG,
    OTHER_CHAT_ALREADY_CAPTURING_MSG,
    CANNOT_POST_TO_CAPTURED_MSG,
    parse_channel_slash_thread,
    ActivitySlack,
    IntegrationSlack as RealSlack,
    logger,
)


class IntegrationSlackFake:
    """In-memory fake Slack implementation for local testing."""

    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx: ckit_bot_exec.RobotContext,
        SLACK_BOT_TOKEN: str = "",  # not needed, added to match create method of real
        SLACK_APP_TOKEN: str = "",
        should_join: str = "",
        mongo_collection: Optional[Collection] = None,
    ):
        self.fclient = fclient
        self.rcx = rcx
        self.should_join = [x.strip() for x in should_join.split(",") if x.strip()]
        self.actually_joined = set()
        self.activity_callback: Optional[
            Callable[[ActivitySlack, bool], Awaitable[None]]
        ] = None
        self.channels_id2name: Dict[str, str] = {}
        self.channels_name2id: Dict[str, str] = {}
        self.users_id2name: Dict[str, str] = {}
        self.users_name2id: Dict[str, str] = {}
        self.messages: Dict[str, List[Dict[str, Any]]] = {}
        self.captured: Optional[tuple[str, str]] = None
        self.captured_ft_id: Optional[str] = None
        self.reactive_running = False
        self.mongo_collection = mongo_collection

    def set_activity_callback(
        self, cb: Callable[[ActivitySlack, bool], Awaitable[None]]
    ):
        self.activity_callback = cb

    async def start_reactive(self):
        if not self.reactive_running:
            self.reactive_running = True
            FAKE_SLACK_INSTANCES.append(self)

    async def close(self):
        if self.reactive_running:
            self.reactive_running = False
            if self in FAKE_SLACK_INSTANCES:
                FAKE_SLACK_INSTANCES.remove(self)

    async def join_channels(self):
        for name in self.should_join:
            chan_id = name.lstrip("#")
            self.channels_name2id[name] = chan_id
            self.channels_id2name[chan_id] = name
            self.messages.setdefault(chan_id, [])
            self.actually_joined.add(name)

    async def post_into_captured_thread_as_user(self, a: ActivitySlack, chan_id: str) -> bool:
        something_id_slash_thread = f"{chan_id}/{a.thread_ts}" if a.thread_ts else chan_id
        thread_capturing = RealSlack._thread_capturing(self, something_id_slash_thread)
        if not thread_capturing:
            return False
        content = [{"m_type": "text", "m_content": f"👤{a.message_author_name}\n\n{a.message_text}"}]
        if a.file_contents:
            content.extend(a.file_contents)
        try:
            http = await self.fclient.use_http()
            await ckit_ask_model.thread_add_user_message(
                http, thread_capturing.thread_fields.ft_id, content, "slack_fake", ftm_alt=100
            )
            return True
        except Exception:
            logger.exception(f"Failed to post message into captured ft_id={thread_capturing.thread_fields.ft_id}")
            return False

    async def _receive_fake_message(
        self,
        channel: str,
        thread_ts: str,
        ts: str,
        text: str,
        user: str,
        path: Optional[str] = None,
    ):
        chan_id = self.channels_name2id.get(channel, channel)
        self.channels_name2id.setdefault(channel, chan_id)
        self.channels_id2name.setdefault(chan_id, channel)
        self.messages.setdefault(chan_id, [])
        self.users_id2name.setdefault(user, user)
        self.users_name2id.setdefault(user, user)
        msg = {
            "ts": ts,
            "thread_ts": thread_ts,
            "user": user,
            "text": text,
            "file": None,
        }
        file_contents: List[Dict[str, str]] = []
        if path:
            if self.mongo_collection is None:
                msg["file"] = f"(mongo collection not available for {path})"
            else:
                perr = validate_path(path)
                if not perr:
                    try:
                        import tempfile
                        local_path = os.path.join(tempfile.gettempdir(), os.path.basename(path))
                        await download_file(self.mongo_collection, path, local_path)
                        with open(local_path, "rb") as f:
                            data = f.read()
                        mime, _ = mimetypes.guess_type(path)
                        if mime and mime.startswith("image/"):
                            processed = await RealSlack._process_slack_image(self, data, mime)
                            file_contents.append(processed)
                            msg["file"] = f"[image {path}]"
                        elif RealSlack._is_text_file(self, data):
                            processed = await RealSlack._process_slack_text_file(self, data, path)
                            file_contents.append(processed)
                            msg["file"] = processed["m_content"]
                        else:
                            summary = f"[Binary file: {path} ({len(data)} bytes)]"
                            file_contents.append({"m_type": "text", "m_content": summary})
                            msg["file"] = summary
                        os.unlink(local_path)  # Clean up temp file
                    except Exception as e:
                        print(f"Debug: Exception in _receive_fake_message: {e}")
                        import traceback
                        traceback.print_exc()
                        msg["file"] = f"(failed to read {path}: {e})"
                else:
                    msg["file"] = f"(invalid path {path})"
        self.messages[chan_id].append(msg)
        activity = ActivitySlack(
            what_happened="message",
            channel_name=self.channels_id2name[chan_id],
            thread_ts=thread_ts,
            message_ts=ts,
            message_text=text,
            message_author_name=user,
            mention_looked_up={},
            file_contents=file_contents,
        )
        posted = await self.post_into_captured_thread_as_user(activity, chan_id)
        if self.activity_callback:
            await self.activity_callback(activity, posted)

    async def look_assistant_might_have_posted_something(self, msg: ckit_ask_model.FThreadMessageOutput) -> bool:
        if msg.ftm_role != "assistant" or not msg.ftm_content:
            return False
        fthread = self.rcx.latest_threads.get(msg.ftm_belongs_to_ft_id)
        if not fthread:
            return False
        searchable = fthread.thread_fields.ft_app_searchable
        if not searchable.startswith("slack/"):
            return False
        parts = searchable.split("/")
        chan_id = parts[1]
        thread_ts = parts[2] if len(parts) > 2 else None
        ts = str(time.time())
        self.messages.setdefault(chan_id, [])
        self.channels_id2name.setdefault(chan_id, chan_id)
        self.channels_name2id.setdefault(chan_id, chan_id)
        entry = {"ts": ts, "thread_ts": thread_ts or ts, "user": "bot", "text": msg.ftm_content, "file": None, "metadata": {"ft_id": msg.ftm_belongs_to_ft_id}}
        self.messages[chan_id].append(entry)
        if self.activity_callback:
            activity = ActivitySlack(
                what_happened="post",
                channel_name=self.channels_id2name[chan_id],
                thread_ts=thread_ts or ts,
                message_ts=ts,
                message_text=msg.ftm_content,
                message_author_name="bot",
                mention_looked_up={},
                file_contents=[],
            )
            await self.activity_callback(activity, True)
        http = await self.fclient.use_http()
        await ckit_ask_model.thread_app_capture_patch(
            http,
            fthread.thread_fields.ft_id,
            ft_app_specific=json.dumps({"last_posted_assistant_ts": msg.ftm_created_ts}),
        )
        fthread.thread_fields.ft_app_specific = {"last_posted_assistant_ts": msg.ftm_created_ts}
        return True


    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]],
    ) -> str:
        if not model_produced_args:
            return HELP

        op = model_produced_args.get("op", "")
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        channel_slash_thread = ckit_cloudtool.try_best_to_find_argument(
            args, model_produced_args, "channel_slash_thread", ""
        )
        text = ckit_cloudtool.try_best_to_find_argument(
            args, model_produced_args, "text", ""
        )
        attach_file = ckit_cloudtool.try_best_to_find_argument(
            args, model_produced_args, "path", ""
        )

        print_help = not op or "help" in op
        print_status = not op or "status" in op

        result = ""
        if print_status:
            joined = ", ".join(sorted(self.actually_joined)) or "none"
            if self.captured:
                ch = self.channels_id2name.get(self.captured[0], self.captured[0])
                result += f"fake slack: joined [{joined}], capturing #{ch}/{self.captured[1]}\n"
            else:
                result += f"fake slack: joined [{joined}], not capturing\n"

        if print_help:
            result += HELP

        if print_status or print_help:
            return result

        if op == "capture":
            channel, thread = parse_channel_slash_thread(channel_slash_thread)
            if not channel or not thread:
                return "Error: need channel/thread for capture"
            chan_id = self.channels_name2id.get(channel, channel)
            self.channels_name2id.setdefault(channel, chan_id)
            self.channels_id2name.setdefault(chan_id, channel)
            self.messages.setdefault(chan_id, [])

            something_id_slash_thread = f"{chan_id}/{thread}"
            searchable = f"slack/{something_id_slash_thread}"
            already_captured_by = RealSlack._thread_capturing(self, something_id_slash_thread)
            if already_captured_by:
                if already_captured_by.thread_fields.ft_id == toolcall.fcall_ft_id:
                    return "Already captured"
                else:
                    return OTHER_CHAT_ALREADY_CAPTURING_MSG % (something_id_slash_thread,)

            self.captured = (chan_id, thread)
            self.captured_ft_id = toolcall.fcall_ft_id
            http = await self.fclient.use_http()
            await ckit_ask_model.thread_app_capture_patch(
                http, toolcall.fcall_ft_id, ft_app_searchable=searchable
            )
            return (CAPTURE_SUCCESS_MSG % (channel,)) + CAPTURE_ADVICE_MSG

        if op == "uncapture":
            if self.captured_ft_id:
                http = await self.fclient.use_http()
                await ckit_ask_model.thread_app_capture_patch(
                    http, self.captured_ft_id, ft_app_searchable=""
                )
            self.captured = None
            self.captured_ft_id = None
            return UNCAPTURE_SUCCESS_MSG

        if op == "skip":
            return SKIP_SUCCESS_MSG

        if op == "post":
            channel, thread = parse_channel_slash_thread(channel_slash_thread)
            if not channel:
                return "Error: channel required"
            chan_id = self.channels_name2id.get(channel, channel)
            self.channels_name2id.setdefault(channel, chan_id)
            self.channels_id2name.setdefault(chan_id, channel)
            self.messages.setdefault(chan_id, [])
            self.users_id2name.setdefault("bot", "bot")
            self.users_name2id.setdefault("bot", "bot")

            something_id_slash_thread = f"{chan_id}/{thread}" if thread else chan_id
            thread_capturing = RealSlack._thread_capturing(self, something_id_slash_thread)
            if thread_capturing and thread_capturing.thread_fields.ft_id == toolcall.fcall_ft_id:
                return CANNOT_POST_TO_CAPTURED_MSG

            ts = str(time.time())
            thread_ts = thread or ts
            msg: Dict[str, Any] = {
                "ts": ts,
                "thread_ts": thread_ts,
                "user": "bot",
                "text": text,
                "file": None,
                "metadata": {"ft_id": toolcall.fcall_ft_id},
            }
            file_contents: List[Dict[str, str]] = []
            if attach_file:
                if self.mongo_collection is None:
                    return "ERROR: Attaching file is not available. You should setup the slack tool with mongo collection"

                perr = validate_path(attach_file)
                if perr:
                    return f"Error: {perr}"

                try:
                    import tempfile
                    local_path = os.path.join(tempfile.gettempdir(), os.path.basename(attach_file))
                    await download_file(self.mongo_collection, attach_file, local_path)
                    with open(local_path, "rb") as f:
                        data = f.read()
                    mime, _ = mimetypes.guess_type(attach_file)
                    if mime and mime.startswith("image/"):
                        processed = await RealSlack._process_slack_image(self, data, mime)
                        file_contents.append(processed)
                        msg["file"] = f"[image {attach_file}]"
                    elif RealSlack._is_text_file(self, data):
                        processed = await RealSlack._process_slack_text_file(self, data, attach_file)
                        file_contents.append(processed)
                        msg["file"] = processed["m_content"]
                    else:
                        summary = f"[Binary file: {attach_file} ({len(data)} bytes)]"
                        file_contents.append({"m_type": "text", "m_content": summary})
                        msg["file"] = summary
                    os.unlink(local_path)  # Clean up temp file
                except Exception as e:
                    print(f"Debug: Exception in post operation: {e}")
                    import traceback
                    traceback.print_exc()
                    return f"ERROR: Failed to download file from mongo: {e}. Cannot attach it"

            self.messages[chan_id].append(msg)

            if self.activity_callback and thread_capturing and thread_capturing.thread_fields.ft_id == toolcall.fcall_ft_id:
                activity = ActivitySlack(
                    what_happened="post",
                    channel_name=self.channels_id2name[chan_id],
                    thread_ts=thread_ts,
                    message_ts=ts,
                    message_text=text,
                    message_author_name="bot",
                    mention_looked_up={},
                    file_contents=file_contents,
                )
                await self.activity_callback(activity, True)

            if attach_file:
                return (
                    "File upload success (thread)" if thread else "File upload success (channel)"
                )
            return (
                "Post success (thread in channel)" if thread else "Post success (channel)"
            )

        return f"Error: Unknown op {op}"


FAKE_SLACK_INSTANCES: List[IntegrationSlackFake] = []


async def post_fake_slack_message(
    channel_slash_thread: str,
    text: str,
    user: str = "user",
    path: Optional[str] = None,
):
    channel, thread = parse_channel_slash_thread(channel_slash_thread)
    if not channel:
        return
    ts = str(time.time())
    thread_ts = thread or ts
    for inst in list(FAKE_SLACK_INSTANCES):
        await inst._receive_fake_message(
            channel, thread_ts, ts, text, user, path
        )
    return {"ts": ts, "thread_ts": thread_ts}


async def wait_for_bot_message(channel_slash_thread: str, timeout_seconds: int = 400, slack_instance=None) -> List[Dict[str, Any]]:
    loop = asyncio.get_running_loop()
    start = loop.time()

    if not slack_instance:
        while not FAKE_SLACK_INSTANCES:
            if loop.time() - start > timeout_seconds:
                raise TimeoutError("No fake Slack instances available")
            await asyncio.sleep(0.1)

    fi_slack = slack_instance or FAKE_SLACK_INSTANCES[0]
    channel, thread = parse_channel_slash_thread(channel_slash_thread)

    def bot_msgs(msgs):
        return [m for m in msgs if m.get("user") == "bot" and (not thread or m.get("thread_ts") == thread)]

    initial_msgs = bot_msgs(fi_slack.messages.get(channel, []))

    while True:
        current_msgs = bot_msgs(fi_slack.messages.get(channel, []))
        if len(current_msgs) > len(initial_msgs):
            return current_msgs[len(initial_msgs):]

        if loop.time() - start > timeout_seconds:
            raise TimeoutError("bot did not respond")

        await asyncio.sleep(0.2)
