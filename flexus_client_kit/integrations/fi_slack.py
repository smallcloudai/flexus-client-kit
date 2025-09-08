import os
import asyncio
import logging
import re
import time
import json
import base64
import io
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, Awaitable, List
import httpx
from PIL import Image
import gql

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit.integrations import fi_localfile
from flexus_client_kit.integrations.fi_localfile import format_cat_output


# This uses Bolt SDK, a thin wrapper over Events & Web API
from slack_bolt.async_app import AsyncApp

# Web API https://api.slack.com/web
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

# This uses Socket Mode, good for local dev; for prod marketplace use HTTPS Events
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler


logger = logging.getLogger("slack")

# 15 messages per minute:
# https://api.slack.com/changelog/2025-05-terms-rate-limit-update-and-faq

# Apps unsuitable for Slack Marketplace:
# https://api.slack.com/slack-marketplace/guidelines


SLACK_TOOL = ckit_cloudtool.CloudTool(
    name="slack",
    description="Interact with Slack, call with op=\"help\" to print usage, call with op=\"status+help\" to see both status and help in one call",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Start with 'help' for usage"},
            "args": {"type": "object"},
        },
        "required": []
    },
)

def parse_channel_slash_thread(s: str) -> tuple[Optional[str], Optional[str]]:
    if not isinstance(s, str):
        return None, None
    s = s[1:] if s.startswith("#") else s
    parts = s.split("/", 1)
    return parts[0], parts[1] if len(parts) > 1 else None

FORMATTING = """
In slack messages, formatting is *bold* _italic_ ~strikeout~. Tables and headers don't work.
Triple backquotes for code work, but without language specifier, write newline immediately after triple backquotes.
"""

HELP = """
Help:

slack(op="status")

slack(op="capture", args={"channel_slash_thread": "channel_name/thread_ts"})
slack(op="capture", args={"channel_slash_thread": "@username/thread_ts"})
    The workhorse of a chatbot. Slack messages start to appear as role="user" messages here, and role="assistant"
    messages get automatically posted to slack. Tool calls and results are invisible for slack users.
    Capture only works for slack threads, not channels, find 'message_ts' in the details of a kanban task, and
    then put it after slash as thread_ts.

slack(op="post", args={"channel_slash_thread": "channel_name", "text": "Hello world!"})
slack(op="post", args={"channel_slash_thread": "channel_name/thread_ts", "text": "Hello world!"})
slack(op="post", args={"channel_slash_thread": "@username", "text": "Hello world!"})
slack(op="post", args={"channel_slash_thread": "@username/thread_ts", "text": "Hello world!"})
    Simple post to a channel. Slack identifies threads by thread_ts that looks like float unix time.
    If you send to @username that will post a DM, not in any channel.
    If you want to talk to a user, don't call "post", call "capture" instead!

slack(op="post", args={"channel_slash_thread": "channel_name", "localfile_path": "folder1/output.pdf"})
    Upload a file, localfile_path must be a path valid for the localfile tool (no absolute paths, no spaces in paths,
    no traversal). The file is read from the same workdir used when calling localfile.

slack(op="uncapture")
    If you don't want to talk anymore, call this instead of answering.

slack(op="skip")
    Ignore the most recent message but keep capturing the thread. Useful for unrelated messages (e.g. from other participants).
""" + FORMATTING


SLACK_SETUP_SCHEMA = [
   {
        "bs_name": "SLACK_BOT_TOKEN",
        "bs_type": "string_long",
        "bs_default": "",
        "bs_group": "Slack",
        "bs_importance": 0,
        "bs_description": "Bot User OAuth Token from Slack app settings (starts with xoxb-)",
    },
    {
        "bs_name": "SLACK_APP_TOKEN",
        "bs_type": "string_long",
        "bs_default": "",
        "bs_group": "Slack",
        "bs_importance": 0,
        "bs_description": "App-Level Token from Slack app settings (starts with xapp-)",
    },
    {
        "bs_name": "slack_should_join",
        "bs_type": "string_long",
        "bs_default": "#general,#random,#support",
        "bs_group": "Slack",
        "bs_importance": 0,
        "bs_description": "Comma-separated list of Slack channels the bot should automatically join",
    },
]


@dataclass
class ActivitySlack:
    what_happened: str
    channel_name: str
    thread_ts: str
    message_ts: str
    message_text: str
    message_author_name: str
    mention_looked_up: Dict[str, str]
    file_contents: List[Dict[str, str]] = field(default_factory=list)


class IntegrationSlack:
    def __init__(self, fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext, SLACK_BOT_TOKEN: str, SLACK_APP_TOKEN: str, should_join: str):
        self.fclient = fclient
        self.rcx = rcx
        self.SLACK_BOT_TOKEN = SLACK_BOT_TOKEN
        self.SLACK_APP_TOKEN = SLACK_APP_TOKEN
        self.should_join = [x.strip() for x in should_join.split(",") if x.strip()]
        self.actually_joined = set()
        self.problems_joining = list()
        self.problems_other = list()
        self.socket_mode_something = None
        self.reactive_task = None
        try:
            self.reactive_slack = AsyncApp(token=SLACK_BOT_TOKEN)
            self._setup_event_handlers()
        except Exception as e:
            logger.info(f"Failed to connect and setup event handlers: {type(e).__name__} {e}")
            self.problems_other.append("%s %s" % (type(e).__name__, e))
            self.reactive_slack = None
        self.activity_callback: Optional[Callable[[ActivitySlack, bool], Awaitable[None]]] = None
        self.prev_messages = deque(maxlen=200)
        self.channels_id2name = {}
        self.channels_name2id = {}
        self.users_id2name = {}
        self.users_name2id = {}
        self.users_name2dm = {}

    def set_activity_callback(self, cb: Callable[[ActivitySlack, bool], Awaitable[None]]):
        self.activity_callback = cb

    async def start_reactive(self):
        if not self.reactive_slack:
            return
        try:
            self.socket_mode_something = AsyncSocketModeHandler(self.reactive_slack, self.SLACK_APP_TOKEN)
            self.reactive_task = asyncio.create_task(self.socket_mode_something.start_async())
        except Exception as e:
            logger.error(f"Failed to start socket mode: {type(e).__name__} {e}")
            self.problems_other.append("%s %s" % (type(e).__name__, e))
            self.socket_mode_something = None

    async def close(self):
        if self.reactive_task and not self.reactive_task.done():
            self.reactive_task.cancel()
            try:
                await self.reactive_task
            except asyncio.CancelledError:
                pass
            self.reactive_task = None
        if self.socket_mode_something:
            await self.socket_mode_something.close_async()
            self.socket_mode_something = None
        self.reactive_slack = None

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        if not model_produced_args:
            return HELP

        op = model_produced_args.get("op", "")
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        print_help = False
        r = ""

        if not self.reactive_slack:
            assert self.problems_other
            r += "Problems with this tool:\n"
            for problem in self.problems_other:
                r += "  %s\n" % problem
            r += "\n"
            return r

        print_help = not op or "help" in op
        print_status = not op or "status" in op

        if print_status:
            if not self.SLACK_BOT_TOKEN:
                r += "Don't have SLACK_BOT_TOKEN set\n"
            if not self.SLACK_APP_TOKEN:
                r += "Don't have SLACK_APP_TOKEN set\n"
            r += "Instructued to join %d channels, actually joined %d channels:\n" % (len(self.should_join), len(self.actually_joined))
            for channel in self.should_join:
                r += "  %s\n" % (channel,)
            r += "\n"
            if self.problems_joining:
                r += "Problems joining channels:\n"
                for problem in self.problems_joining:
                    r += "  %s\n" % problem
                r += "\n"
            if self.problems_other:
                r += "Other problems:\n"
                for problem in self.problems_other:
                    r += "  %s\n" % problem
                r += "\n"

        if print_help:
            r += HELP

        elif print_status:
            pass

        elif op == "post":
            text = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "text", None)
            channel_slash_thread = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "channel_slash_thread", "")
            attach_file = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "localfile_path", None)
            something_name, thread_ts = parse_channel_slash_thread(channel_slash_thread)
            if not something_name:
                return "Missing or invalid channel_slash_thread parameter"
            try:
                if something_name.startswith('@'):
                    username = something_name.lstrip('@')
                    user_id = self.users_name2id.get(username)
                    if not user_id:
                        return f"ERROR: User {username!r} not found in users_name2id"
                    channel_id = self.users_name2dm.get(username)
                    if not channel_id:
                        dm_resp = await self.reactive_slack.client.conversations_open(users=user_id)
                        channel_id = dm_resp["channel"]["id"]
                        self.users_name2dm[username] = channel_id
                else:
                    channel_id = self.channels_name2id.get(something_name)
                    if not channel_id:
                        return f"ERROR: Channel {something_name!r} not found in channels_name2id"

                if attach_file:
                    perr = fi_localfile.validate_path(attach_file)
                    if perr:
                        return f"ERROR: {perr}"
                    abs_path = os.path.abspath(os.path.join(self.rcx.workdir, attach_file))
                    if not abs_path.startswith(os.path.abspath(self.rcx.workdir) + os.sep):
                        return "ERROR: Path resolves outside workspace"
                    if not os.path.exists(abs_path):
                        return f"ERROR: File {attach_file} does not exist"
                    with open(abs_path, 'rb') as f:
                        file_bytes = f.read()
                    filename = os.path.basename(attach_file)
                    kwargs = {
                        "channel": channel_id,
                        "file": file_bytes,
                        "filename": filename,
                    }
                    if text:
                        kwargs["initial_comment"] = text
                    if thread_ts:
                        kwargs["thread_ts"] = thread_ts
                    await self.reactive_slack.client.files_upload_v2(**kwargs)
                    if something_name.startswith('@'):
                        r += f"File upload success to {something_name} (DM)\n"
                    else:
                        r += "File upload success (channel)\n"
                else:
                    if not isinstance(text, str):
                        return "Missing or invalid text parameter\n"
                    if thread_ts:
                        await self.reactive_slack.client.chat_postMessage(
                            channel=channel_id,
                            text=text,
                            thread_ts=thread_ts
                        )
                        r += f"Post success (thread in {'DM' if something_name.startswith('@') else 'channel'})\n"
                    else:
                        await self.reactive_slack.client.chat_postMessage(
                            channel=channel_id,
                            text=text
                        )
                        r += f"Post success ({'DM' if something_name.startswith('@') else 'channel'})\n"
            except SlackApiError as e:
                r += "ERROR: %s %s\n" % (type(e).__name__, e)

        elif op == "capture":
            channel_slash_thread = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "channel_slash_thread", "")
            something_name, thread_ts = parse_channel_slash_thread(channel_slash_thread)
            something_id = ""
            if something_name.startswith('@'):
                username = something_name.lstrip("@")
                user_id = self.users_name2id.get(username, None)
                if not user_id:
                    return f"ERROR: User {username!r} not found in users_name2id"
                something_id = self.users_name2dm.get(username, None)
                if not something_id:
                    logger.info("Creating DM for %r" % (username,))
                    dm_response = await self.reactive_slack.client.conversations_open(users=user_id)
                    something_id = dm_response["channel"]["id"]
                    self.users_name2dm[username] = something_id
            elif something_name:
                channel_id = self.channels_name2id.get(something_name.lstrip("#"), None)
                something_id = channel_id
            if not something_id:
                return "Bad channel_slash_thread parameter, it's @username/thread_ts (don't forget @ for users) or channel/thread_ts (it's channel name not id)\n"
            something_id_slash_thread = something_id + ("/" + thread_ts if thread_ts else "")

            searchable = "slack/" + something_id_slash_thread
            already_captured_by = None
            for t in self.rcx.latest_threads.values():
                if t.thread_fields.ft_app_searchable == searchable:
                    already_captured_by = t
                    break
            if already_captured_by:
                if already_captured_by.thread_fields.ft_id == toolcall.fcall_ft_id:
                    return "Already captured"
                else:
                    return "Some other chat is already capturing %s" % (something_id_slash_thread,)

            try:
                web_api_client: AsyncWebClient = self.reactive_slack.client
                thirty_minutes_ago = str(int(time.time() - 30*60))

                text_content = ""
                image_parts = []
                file_summaries = []
                async for msg in self.get_history(web_api_client, something_name, thread_ts, thirty_minutes_ago, 10):
                    if text := msg.get('text', None):
                        user_id = msg.get('user')
                        if user_id:
                            author_name = await self.get_user_name(web_api_client, user_id)
                        else:
                            author_name = "unknown_user"
                        text_content += f"👤{author_name}\n\n{text}\n\n"

                    files = msg.get('files', [])
                    for file_info in files[:2]:  # Limit to 2 files per message to avoid overwhelming
                        try:
                            file_bytes, mimetype = await self.download_slack_file(file_info)
                            if file_bytes:
                                filename = file_info.get('name', 'unknown')
                                if mimetype and mimetype.startswith('image/') and len(image_parts) < 3:  # Max 3 images total
                                    image_parts.append(await self.process_slack_image(file_bytes, mimetype))
                                elif self.is_text_file(file_bytes):
                                    processed = await self.process_slack_text_file(file_bytes, filename)
                                    file_summaries.append(processed['m_content'])
                                else:
                                    file_summaries.append(f"[Binary file: {filename} ({len(file_bytes)} bytes)]")
                        except Exception as e:
                            logger.error(f"Error processing file during capture: {e}")

                all_message_parts = []
                if text_content:
                    all_message_parts.append({"m_type": "text", "m_content": text_content.strip()})

                if file_summaries:
                    files_text = "\n📎 Attached files:\n" + "\n".join(file_summaries)
                    all_message_parts.append({"m_type": "text", "m_content": files_text})

                all_message_parts.extend(image_parts)

                logger.info("Successful capture %s <-> %s, posting %d parts into the captured thread" % (something_id_slash_thread, toolcall.fcall_ft_id, len(all_message_parts)))
                http = await self.fclient.use_http()
                if all_message_parts:
                    await ckit_ask_model.thread_add_user_message(
                        http,
                        toolcall.fcall_ft_id,
                        all_message_parts,
                        "fi_slack",
                        ftm_alt=100,
                    )
                await ckit_ask_model.thread_app_capture_patch(
                    http,
                    toolcall.fcall_ft_id,
                    ft_app_searchable=searchable,
                    ft_app_specific=json.dumps({
                        "last_posted_assistant_ts": max(toolcall.fcall_created_ts, float(thread_ts) if thread_ts else 0) + 0.01
                    }),
                )
                r += "Captured! The next thing you write will be visible in Slack. Don't comment on that fact and think about what do you want to say in %r.\n" % (something_name,)

            except SlackApiError as e:
                r += "ERROR: %s %s\n" % (type(e).__name__, e)

        elif op == "uncapture":
            try:
                http = await self.fclient.use_http()
                await ckit_ask_model.thread_app_capture_patch(
                    http,
                    toolcall.fcall_ft_id,
                    ft_app_searchable="",
                )
                r += "Uncaptured successfully. This thread is no longer connected to Slack.\n"
            except Exception as e:
                r += "ERROR: %s %s\n" % (type(e).__name__, e)

        elif op == "skip":
            captured_thread = self.rcx.latest_threads.get(toolcall.fcall_ft_id, None)
            if not captured_thread or not captured_thread.thread_fields.ft_app_searchable or not captured_thread.thread_fields.ft_app_searchable.startswith("slack/"):
                return "This thread is not capturing any Slack conversation. Use 'capture' first to start capturing a thread."

            r += "Great, other people are talking, thread is still captured, any new messages will appear in this thread.\n"

        else:
            r += "Unknown operation %r, try \"help\"\n\n" % op

        return r

    def _setup_event_handlers(self):
        # https://docs.slack.dev/reference/events
        # Slack is a mess :/

        @self.reactive_slack.event("app_mention")
        async def handle_app_mention(event, say, logger):
            await self._any_activity(event)

        @self.reactive_slack.event("message")
        async def handle_message(event, client, logger):
            assert isinstance(client, AsyncWebClient)
            await self._any_activity(event)

        @self.reactive_slack.message()
        async def handle_im1(event, client, logger):
            print("QQQQ reactive_slack.message")

        @self.reactive_slack.event({"type":"message","channel_type":"im"})
        async def handle_im2(event, client, logger):
            print("QQQQ handle_im2")

        @self.reactive_slack.event("im_created")
        async def handle_im3(event, client, logger):
            print("QQQQ handle_im3")

        @self.reactive_slack.event("group_topic")  # use conversation.topic
        async def handle_group_topic(event, client, logger):
            await self._any_activity(event)

        @self.reactive_slack.event("reaction_added")
        async def handle_reaction_added(event, client, logger):
            await self._any_activity(event)

        @self.reactive_slack.event("reaction_removed")
        async def handle_reaction_removed(event, client, logger):
            await self._any_activity(event)

    async def _any_activity(self, slack_event):
        # print("slack event", slack_event)
        client_msg_id = slack_event.get("client_msg_id", None)
        text = slack_event.get("text", "")
        user_id = slack_event.get("user", None)
        if not user_id:
            return None

        # dedup -- the same event can arrive as a message, and then as a mention
        if client_msg_id and client_msg_id in self.prev_messages:
            return None  # dup event
        if client_msg_id:
            self.prev_messages.append(client_msg_id)

        web_api_client = self.reactive_slack.client
        t0 = time.time()

        something_id = None   # will look for captured thread slack/ + something_id
        something_name = None
        # XXX use channels_id2name = {}
        if 1:
            channel_info = await web_api_client.conversations_info(channel=slack_event["channel"])
            # print("channel_info", channel_info)
            # for a DM:
            # channel_info {'ok': True, 'channel': {'id': 'D0978UQ5N13', 'created': 1753360767, 'is_archived': False, 'is_im': True, 'is_org_shared': False, 'context_team_id': 'T02M4C97Y7L', 'updated': 1753411231245, 'user': 'U02M4CUNSRH', 'last_read': '0000000000.000000',
            # 'latest': {'user': 'U02M4CUNSRH', 'type': 'message', 'ts': '1753858934.524369', 'client_msg_id': 'bd72e041-89af-4c97-ac92-629479ce6710', 'text': 'hi Karen', 'team': 'T02M4C97Y7L',
            # 'blocks': [{'type': 'rich_text', 'block_id': 'TxFjM', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'text', 'text': 'hi Karen'}]}]}]},
            # 'unread_count': 11, 'unread_count_display': 9, 'is_open': True, 'properties': {'tabs': [{'type': 'files', 'label': '', 'id': 'files'}], 'tabz': [{'type': 'files'}]}, 'priority': 0}}
            is_dm = channel_info["channel"]["is_im"]
            something_id = channel_info["channel"]["id"]
            if is_dm:
                user_id = channel_info["channel"]["user"]
                something_name = self.users_id2name.get(user_id, None)
            else:
                something_name = self.channels_id2name.get(something_id, None)
        # print("something_id", something_id)
        # print("something_name", something_name)

        event_type = slack_event["type"]
        thread_ts = slack_event.get("thread_ts", "")

        if event_type == "app_mention":
            what_happened = "i_was_mentioned"
        elif event_type == "message":
            channel_type = slack_event["channel_type"]
            if channel_type in {"channel", "im", "group", "mpim"}:
                what_happened = f"message/{channel_type}"
            else:
                logger.info("🚩 unknown channel_type %r", channel_type)
                return None
        else:
            logger.info("🚩 unknown type %r", event_type)
            return None

        t1 = time.time()
        author_username = await self.get_user_name(web_api_client, user_id)
        t2 = time.time()

        user_mentions = re.findall(r'<@([A-Z0-9]+)>', text)
        mention_looked_up = dict()
        for user_id in user_mentions:
            user_name = await self.get_user_name(web_api_client, user_id)
            text = text.replace(f'<@{user_id}>', f'@{user_name}')
            mention_looked_up[user_id] = user_name

        file_contents = []
        files = slack_event.get('files', [])
        image_count = 0
        text_files = []
        for file_info in files[:5]:  # Process up to 5 files
            try:
                file_bytes, mimetype = await self.download_slack_file(file_info)
                if file_bytes:
                    filename = file_info.get('name', 'unknown')
                    if mimetype and mimetype.startswith('image/') and image_count < 2:  # Max 2 images
                        file_contents.append(await self.process_slack_image(file_bytes, mimetype))
                        image_count += 1
                    elif self.is_text_file(file_bytes):
                        processed = await self.process_slack_text_file(file_bytes, filename)
                        text_files.append(processed['m_content'])
                    else:
                        text_files.append(f"[Binary file: {filename} ({len(file_bytes)} bytes)]")
            except Exception as e:
                logger.error(f"Error processing file {file_info.get('name', 'unknown')}: {e}")
                text_files.append(f"[File processing error: {file_info.get('name', 'unknown')}]")

        if text_files:
            combined_text = "\n📎 Files:\n" + "\n".join(text_files)
            file_contents.append({"m_type": "text", "m_content": combined_text})

        t3 = time.time()
        logger.info("slack activity timing %0.3fs %0.3fs %0.3fs" % (t1 - t0, t2 - t1, t3 - t2))

        a = ActivitySlack(
            what_happened=what_happened,
            channel_name=something_name,
            thread_ts=thread_ts,
            message_ts=slack_event["ts"],
            message_text=text,
            message_author_name=author_username,
            mention_looked_up=mention_looked_up,
            file_contents=file_contents,
        )

        really_posted = await self.post_into_captured_thread_as_user(a, something_id)
        if self.activity_callback:
            await self.activity_callback(a, already_posted_to_captured_thread=really_posted)

    async def post_into_captured_thread_as_user(self, a: ActivitySlack, something_id: str) -> bool:
        captured_thread = None
        expected_app_seachable = "slack/" + something_id
        if a.thread_ts:
            expected_app_seachable += "/" + a.thread_ts
        for t in self.rcx.latest_threads.values():
            # print("COMPARE\n  %s\n  %s" % (t.thread_fields.ft_app_searchable, expected_app_seachable))
            if t.thread_fields.ft_app_searchable == expected_app_seachable:
                captured_thread = t
        if captured_thread is None:
            logger.info("None of recent threads match ft_app_searchable=%s, so I'll let bot handle this message." % (expected_app_seachable,))
            return False
        if captured_thread.thread_fields.ft_error is not None:
            logger.info("post_into_captured_thread_as_user() thread ft_app_searchable=%s matches, but it has error so I'll let bot handle this message" % (captured_thread.thread_fields.ft_app_searchable,))
            return False

        if captured_thread is not None:
            http = await self.fclient.use_http()

            content = [{"m_type": "text", "m_content": f"👤{a.message_author_name}\n\n{a.message_text}"}]
            if a.file_contents:
                content.extend(a.file_contents)
            if len(content) > 5:
                text_parts = [c for c in content if c.get('m_type') == 'text']
                image_parts = [c for c in content if c.get('m_type', '').startswith('image/')][:2]
                combined_text = "\n\n".join(p['m_content'] for p in text_parts)
                content = [{"m_type": "text", "m_content": combined_text}] + image_parts

            logger.info("Captured slack->db ft_id=%s ft_app_searchable=%s sending=%d parts" % (captured_thread.thread_fields.ft_id, expected_app_seachable, len(content)))
            user_pref = json.dumps({"reopen_task_instruction": 1})
            try:
                await ckit_ask_model.thread_add_user_message(http, captured_thread.thread_fields.ft_id, content, "karen_bot", ftm_alt=100, user_preferences=user_pref)
                return True
            except gql.transport.exceptions.TransportQueryError as e:
                logger.info("A problem, probably because the captured thread over budget or something bad happened, will uncapture the thread: %s" % (str(e),))
                await ckit_ask_model.thread_app_capture_patch(
                    http,
                    captured_thread.thread_fields.ft_id,
                    ft_app_searchable="",
                )
                return False

        logger.info("No captured thread for", expected_app_seachable)
        return False

    async def look_assistant_might_have_posted_something(self, msg: ckit_ask_model.FThreadMessageOutput) -> bool:
        if msg.ftm_role != "assistant":
            return False
        if not msg.ftm_content:  # empty message, slack will not even allow you to post an empty message (there might be tool calls in assistant)
            return False

        fthread = self.rcx.latest_threads.get(msg.ftm_belongs_to_ft_id, None)
        if not fthread:
            logger.info("look_assistant_might_have_posted_something(): thread ft_id=%s doesn't even exist in the list of latest threads" % msg.ftm_belongs_to_ft_id)
            return False
        searchable = fthread.thread_fields.ft_app_searchable
        if searchable == '':
            return False
        match = re.match(r'^slack/([^/]+)(?:/(.+))?$', searchable)
        if not match:
            logger.info("look_assistant_might_have_posted_something(): thread ft_app_searchable=%r doesn't look like a slack/channel/thread" % searchable)
            return False
        something_id, thread_ts = match.groups()

        my_specific = fthread.thread_fields.ft_app_specific
        if my_specific is not None:
            last_posted_assistant_ts = my_specific["last_posted_assistant_ts"]   # well it's my thread I know it's there
            if msg.ftm_created_ts <= last_posted_assistant_ts:
                # Already posted that one, arrived again after subscription reconnect or something
                logger.info("look_assistant_might_have_posted_something(): already posted that one last_posted_assistant_ts=%0.1f" % last_posted_assistant_ts)
                return False

        logger.info("look_assistant_might_have_posted_something() captured assistant->slack ft_id=%s ft_app_searchable=%s, sending %r" % (msg.ftm_belongs_to_ft_id, searchable, msg.ftm_content[:20].replace("\n", "\\n")))
        web_api_client: AsyncWebClient = self.reactive_slack.client
        try:
            if thread_ts:
                await web_api_client.chat_postMessage(
                    channel=something_id,
                    text=msg.ftm_content,
                    thread_ts=thread_ts,
                )
            else:
                await web_api_client.chat_postMessage(
                    channel=something_id,
                    text=msg.ftm_content,
                )
            logger.info(f"Successfully posted assistant message to channel {something_id!r} thread_ts {thread_ts!r}")
        except SlackApiError as e:
            logger.error(f"Failed to post message to channel {something_id!r} thread_ts {thread_ts!r}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error posting message to Slack: {type(e).__name__}: {e}", exc_info=True)
            return False

        http = await self.fclient.use_http()
        await ckit_ask_model.thread_app_capture_patch(http, fthread.thread_fields.ft_id, ft_app_specific=json.dumps({
            "last_posted_assistant_ts": msg.ftm_created_ts
        }))
        # It will take time for the updated fthread to come back via subsription, and we might have more messages incoming
        # in the pipeline, so for them also change local object:
        fthread.thread_fields.ft_app_specific = {
            "last_posted_assistant_ts": msg.ftm_created_ts
        }
        logger.info("/look_assistant_might_have_posted_something() success")
        return True


    def is_text_file(self, data: bytes) -> bool:
        if not data:
            return True
        if b'\x00' in data[:1024]:  # Check first 1KB for null bytes
            return False
        sample_size = min(1024, len(data))
        try:
            sample_text = data[:sample_size].decode('utf-8')
        except UnicodeDecodeError:
            return False
        printable_chars = sum(1 for c in sample_text if c.isprintable() or c.isspace())
        printable_ratio = printable_chars / len(sample_text) if sample_text else 1.0
        return printable_ratio > 0.8

    async def process_slack_image(self, file_bytes: bytes, mimetype: str) -> dict:
        try:
            img = Image.open(io.BytesIO(file_bytes))
            img.thumbnail((600, 600), Image.Resampling.LANCZOS)
            buffer = io.BytesIO()
            if img.mode == "RGBA":
                img = img.convert("RGB")
            img.save(buffer, format='JPEG', quality=80, optimize=True)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            return {"m_type": "image/jpeg", "m_content": image_base64}
        except Exception as e:
            logger.error(f"Failed to process image: {e}")
            return {"m_type": "text", "m_content": f"[Image processing failed: {e}]"}

    async def process_slack_text_file(self, file_bytes: bytes, filename: str) -> dict:
        formatted = format_cat_output(
            path=filename,
            file_data=file_bytes,
            line_range="1:",
            safety_valve="10k"  # Limit to 10KB
        )
        return {"m_type": "text", "m_content": f"📎 {formatted}"}

    async def download_slack_file(self, file_info: dict) -> tuple[Optional[bytes], Optional[str]]:
        url = file_info.get('url_private_download')
        if not url:
            logger.warning(f"No download URL for file: {file_info.get('name', 'unknown')}")
            return None, None

        headers = {'Authorization': f'Bearer {self.SLACK_BOT_TOKEN}'}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30.0)
                if response.status_code == 200:
                    return response.content, file_info.get('mimetype', 'application/octet-stream')
                else:
                    logger.error(f"Failed to download file, status: {response.status_code}")
                    return None, None
        except Exception as e:
            logger.error(f"Error downloading file from Slack: {e}")
            return None, None

    # - - other stuff like joining the right channels - -

    async def get_history(self, web_api_client: AsyncWebClient, channel_name: str, thread_ts: Optional[str], long_ago: str, limit_cnt: int):
        if channel_name.startswith('@'):
            channel_id = self.users_name2id.get(channel_name.lstrip("@"))
            if not channel_id:
                raise ValueError(f"User {channel_name} not found in users_name2id")
        else:
            channel_id = self.channels_name2id.get(channel_name)
            if not channel_id:
                raise ValueError(f"Channel {channel_name} not found in channels_name2id")

        logger.info(f"get_history: channel_name={channel_name}, thread_ts={thread_ts!r}, channel_id={channel_id}")

        cursor = None
        while True:
            try:
                if thread_ts and thread_ts.strip():
                    # Get replies in a thread
                    logger.info(f"Using conversations_replies with ts={thread_ts}")
                    messages_response = await web_api_client.conversations_replies(
                        channel=channel_id, ts=thread_ts, oldest=long_ago, limit=limit_cnt, cursor=cursor
                    )
                else:
                    # Get channel history
                    logger.info(f"Using conversations_history (no thread)")
                    messages_response = await web_api_client.conversations_history(
                        channel=channel_id, oldest=long_ago, limit=limit_cnt, cursor=cursor
                    )
            except SlackApiError as e:
                if "ratelimited" in str(e):
                    logger.info("ratelimit")
                    await asyncio.sleep(10)
                    continue
                logger.error(f"Slack API error in get_history: {e}")
                raise

            for msg in messages_response["messages"]:
                yield msg

            cursor = messages_response.get("response_metadata", {}).get("next_cursor")
            if not messages_response.get("has_more") or not cursor:
                break

    async def join_channels(self):
        if not self.reactive_slack:
            return
        web_api_client: AsyncWebClient = self.reactive_slack.client
        my_info = await web_api_client.auth_test()
        my_user_id = my_info["user_id"]
        logger.info(f"Bot user ID: {my_user_id}")

        try:
            users_response = await web_api_client.users_list(limit=5000)
            for user in users_response["members"]:
                if not user.get("deleted", False) and not user.get("is_bot", False):
                    user_id = user["id"]
                    user_name = user["name"]
                    self.users_id2name[user_id] = user_name
                    self.users_name2id[user_name] = user_id
                    logger.info(f"👤 User {user_name} -> {user_id}")
        except SlackApiError as e:
            logger.error(f"Failed to list users: {type(e).__name__} {e}")
            self.problems_other.append(f"Failed to list users: {type(e).__name__} {e}")

        try:
            channels_response = await web_api_client.conversations_list(types="im", limit=5000)
            for rec in channels_response["channels"]:
                # {'id': 'D097A1KDER3', 'created': 1753370403, 'is_archived': False, 'is_im': True, 'is_org_shared': False, 'context_team_id': 'T02M4C97Y7L', 'updated': 1753370403910, 'user': 'U06CTJEKA3B', 'is_user_deleted': False, 'priority': 0}
                if not rec['is_im']:
                    logger.error("Hmm I asked for DM list, and I see", rec)
                    continue
                user_id = rec['user']
                dm_channel_id = rec['id']
                username = self.users_id2name.get(user_id)
                if username:
                    self.users_name2dm[username] = dm_channel_id
                    logger.info(f"✉️  DM {user_id} -> {dm_channel_id}")
                else:
                    logger.error(f"User {user_id} not found in users_id2name, cannot map DM channel {dm_channel_id}")
        except SlackApiError as e:
            logger.error(f"Failed to list DMs: {type(e).__name__} {e}")
            self.problems_other.append(f"Failed to list DMs: {type(e).__name__} {e}")

        try:
            channels_response = await web_api_client.conversations_list(types="public_channel", limit=1000)
            for channel in channels_response["channels"]:
                self.channels_id2name[channel["id"]] = channel["name"]
                self.channels_name2id[channel["name"]] = channel["id"]

                should_join = channel['name'] in self.should_join or ("#" + channel['name']) in self.should_join
                is_member = channel.get('is_member', False)

                if not should_join:
                    if is_member:
                        try:
                            await web_api_client.conversations_leave(channel=channel["id"])
                            logger.info(f"❌ Left #{channel['name']}")
                        except SlackApiError as e:
                            self.problems_joining.append("%s %s" % (type(e).__name__, e))
                    logger.info(f"✖️  channel #{channel['name']} -> {channel['id']}")
                    continue

                logger.info(f"☑️  channel #{channel['name']} -> {channel['id']}")
                self.actually_joined.add(channel['name'])

                if not is_member:
                    try:
                        await web_api_client.conversations_join(channel=channel["id"])
                        logger.info(f"✅ Joined #{channel['name']}")
                    except SlackApiError as e:
                        self.problems_joining.append("%s %s" % (type(e).__name__, e))
        except SlackApiError as e:
            logger.error(f"Failed to list channels: {type(e).__name__} {e}")
            self.problems_other.append(f"Failed to list channels: {type(e).__name__} {e}")

        # async for msg in self.get_history(web_api_client, channel["id"], long_ago):
        #     ts = datetime.fromtimestamp(float(msg['ts']))
        #     text = msg.get('text', '')[:50].replace("\n", "\\n")
        #     logger.info(f"  {ts.strftime('%Y%m%d %H:%M')}: {text}")

    async def get_user_name(self, web_api_client: AsyncWebClient, user_id: str) -> str:
        if user_id in self.users_id2name:
            return self.users_id2name[user_id]
        try:
            author_info = await web_api_client.users_info(user=user_id)
            author_name = author_info["user"]["name"]
            self.users_id2name[user_id] = author_name
            self.users_name2id[author_name] = user_id
            return author_name
        except Exception as e:
            logger.warning(f"Could not resolve user {user_id}: {e}")
            author_name = f"user_{user_id}"
            self.users_id2name[user_id] = author_name
            return author_name


async def test():
    should_join = ["general", "random", "karen-test"]
    bot = IntegrationSlack(
        SLACK_BOT_TOKEN=os.environ.get("SLACK_BOT_TOKEN"),
        SLACK_APP_TOKEN=os.environ.get("SLACK_APP_TOKEN"),
        should_join=should_join,
    )
    await bot.join_channels()
    await bot.start()


if __name__ == "__main__":
    from flexus_client_kit import ckit_logs
    ckit_logs.setup_logger()
    asyncio.run(test())

