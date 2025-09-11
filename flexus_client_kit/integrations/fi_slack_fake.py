import os
import time
import json
import mimetypes
import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable, List

from flexus_client_kit import ckit_cloudtool, ckit_client, ckit_bot_exec, ckit_ask_model
from flexus_client_kit.integrations import fi_localfile
from flexus_client_kit.integrations.fi_slack import (
    SLACK_TOOL,
    SLACK_SETUP_SCHEMA,
    HELP,
    parse_channel_slash_thread,
    ActivitySlack,
    IntegrationSlack as RealSlack,
)


FAKE_SLACK_INSTANCES: List[Any] = []


class IntegrationSlackFake:
    """In-memory fake Slack implementation for local testing."""

    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx: ckit_bot_exec.RobotContext,
        SLACK_BOT_TOKEN: str = "",  # not needed, added to match create method of real
        SLACK_APP_TOKEN: str = "",
        should_join: str = "",
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
        if self.captured == (chan_id, a.thread_ts) and self.captured_ft_id:
            content = [{"m_type": "text", "m_content": f"👤{a.message_author_name}\n\n{a.message_text}"}]
            if a.file_contents:
                content.extend(a.file_contents)
            try:
                http = await self.fclient.use_http()
                await ckit_ask_model.thread_add_user_message(
                    http, self.captured_ft_id, content, "slack_fake", ftm_alt=100
                )
                return True
            except Exception:
                return False
        return False

    async def _receive_fake_message(
        self,
        channel: str,
        thread_ts: str,
        ts: str,
        text: str,
        user: str,
        localfile_path: Optional[str] = None,
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
        if localfile_path:
            perr = fi_localfile.validate_path(localfile_path)
            if not perr:
                path = os.path.join(
                    getattr(self.rcx, "workdir", "/tmp/slack_fake"), localfile_path
                )
                try:
                    with open(path, "rb") as f:
                        data = f.read()
                    mime, _ = mimetypes.guess_type(localfile_path)
                    if mime and mime.startswith("image/"):
                        processed = await RealSlack.process_slack_image(self, data, mime)
                        file_contents.append(processed)
                        msg["file"] = f"[image {localfile_path}]"
                    elif RealSlack.is_text_file(self, data):
                        processed = await RealSlack.process_slack_text_file(self, data, localfile_path)
                        file_contents.append(processed)
                        msg["file"] = processed["m_content"]
                    else:
                        summary = f"[Binary file: {localfile_path} ({len(data)} bytes)]"
                        file_contents.append({"m_type": "text", "m_content": summary})
                        msg["file"] = summary
                except Exception:
                    msg["file"] = f"(failed to read {localfile_path})"
            else:
                msg["file"] = f"(invalid path {localfile_path})"
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
        entry = {"ts": ts, "thread_ts": thread_ts or ts, "user": "bot", "text": msg.ftm_content, "file": None}
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

    async def get_history(
        self,
        web_api_client: Any,
        channel_name: str,
        thread_ts: Optional[str],
        long_ago: str,
        limit_cnt: int,
    ):
        chan_id = self.channels_name2id.get(channel_name, channel_name.lstrip("#"))
        msgs = self.messages.get(chan_id, [])
        oldest = float(long_ago) if long_ago else 0.0
        cnt = 0
        for m in msgs:
            if float(m["ts"]) < oldest:
                continue
            if thread_ts and m["thread_ts"] != thread_ts:
                continue
            yield m
            cnt += 1
            if cnt >= limit_cnt:
                break

    async def get_user_name(self, web_api_client: Any, user_id: str) -> str:
        return self.users_id2name.get(user_id, user_id)

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
        localfile_path = ckit_cloudtool.try_best_to_find_argument(
            args, model_produced_args, "localfile_path", ""
        )

        if not op or "help" in op:
            return HELP

        if op == "status":
            joined = ", ".join(sorted(self.actually_joined)) or "none"
            if self.captured:
                ch = self.channels_id2name.get(self.captured[0], self.captured[0])
                return f"fake slack: joined [{joined}], capturing #{ch}/{self.captured[1]}"
            return f"fake slack: joined [{joined}], not capturing"

        if op == "capture":
            channel, thread = parse_channel_slash_thread(channel_slash_thread)
            if not channel or not thread:
                return "Error: need channel/thread for capture"
            chan_id = self.channels_name2id.get(channel, channel)
            self.channels_name2id.setdefault(channel, chan_id)
            self.channels_id2name.setdefault(chan_id, channel)
            self.messages.setdefault(chan_id, [])
            self.captured = (chan_id, thread)
            self.captured_ft_id = toolcall.fcall_ft_id
            http = await self.fclient.use_http()
            searchable = f"slack/{chan_id}/{thread}"
            await ckit_ask_model.thread_app_capture_patch(
                http, toolcall.fcall_ft_id, ft_app_searchable=searchable
            )
            return (
                "Captured! The next thing you write will be visible in Slack. "
                f"Don't comment on that fact and think about what do you want to say in '{channel}'."
            )

        if op == "uncapture":
            if self.captured_ft_id:
                http = await self.fclient.use_http()
                await ckit_ask_model.thread_app_capture_patch(
                    http, self.captured_ft_id, ft_app_searchable=""
                )
            self.captured = None
            self.captured_ft_id = None
            return "Uncaptured successfully. This thread is no longer connected to Slack."

        if op == "skip":
            return (
                "Great, other people are talking, thread is still captured, "
                "any new messages will appear in this thread."
            )

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

            ts = str(time.time())
            thread_ts = thread or ts
            msg: Dict[str, Any] = {
                "ts": ts,
                "thread_ts": thread_ts,
                "user": "bot",
                "text": text,
                "file": None,
            }
            file_contents: List[Dict[str, str]] = []
            if localfile_path:
                perr = fi_localfile.validate_path(localfile_path)
                if perr:
                    return f"Error: {perr}"
                path = os.path.join(
                    getattr(self.rcx, "workdir", "/tmp/slack_fake"), localfile_path
                )
                try:
                    with open(path, "rb") as f:
                        data = f.read()
                    mime, _ = mimetypes.guess_type(localfile_path)
                    if mime and mime.startswith("image/"):
                        processed = await RealSlack.process_slack_image(self, data, mime)
                        file_contents.append(processed)
                        msg["file"] = f"[image {localfile_path}]"
                    elif RealSlack.is_text_file(self, data):
                        processed = await RealSlack.process_slack_text_file(self, data, localfile_path)
                        file_contents.append(processed)
                        msg["file"] = processed["m_content"]
                    else:
                        summary = f"[Binary file: {localfile_path} ({len(data)} bytes)]"
                        file_contents.append({"m_type": "text", "m_content": summary})
                        msg["file"] = summary
                except Exception:
                    msg["file"] = f"(failed to read {localfile_path})"

            self.messages[chan_id].append(msg)

            if (
                self.activity_callback
                and self.captured == (chan_id, thread_ts)
            ):
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

            if localfile_path:
                return (
                    "File upload success (thread)" if thread else "File upload success (channel)"
                )
            return (
                "Post success (thread in channel)" if thread else "Post success (channel)"
            )

        return f"Error: Unknown op {op}"


async def post_fake_slack_message(
    channel_slash_thread: str,
    text: str,
    user: str = "user",
    localfile_path: Optional[str] = None,
):
    channel, thread = parse_channel_slash_thread(channel_slash_thread)
    if not channel:
        return
    ts = str(time.time())
    thread_ts = thread or ts
    for inst in list(FAKE_SLACK_INSTANCES):
        await inst._receive_fake_message(
            channel, thread_ts, ts, text, user, localfile_path
        )
    return {"ts": ts, "thread_ts": thread_ts}


async def wait_for_bot_message(channel_slash_thread: str, timeout_seconds: int = 400, slack_instance=None) -> List[Dict[str, Any]]:
    loop = asyncio.get_running_loop()
    start = loop.time()

    if not slack_instance:
        while not FAKE_SLACK_INSTANCES:
            if loop.time() - start > timeout_seconds:
                raise RuntimeError("No fake Slack instances available")
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
            raise RuntimeError("bot did not respond")

        await asyncio.sleep(0.2)
