import os
import asyncio
import logging
import re
import tempfile
import time
import json
import base64
import io
from collections import deque
from dataclasses import asdict, dataclass, field
from typing import Dict, Any, Optional, Callable, Awaitable, List
import httpx
from PIL import Image
import gql

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_bot_query
from flexus_client_kit import ckit_scenario
from flexus_client_kit import ckit_kanban
from flexus_client_kit.format_utils import format_cat_output
from flexus_client_kit.integrations import fi_messenger

from pymongo.collection import Collection

# Web API https://api.slack.com/web
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

from flexus_client_kit.integrations.fi_mongo_store import validate_path, download_file

logger = logging.getLogger("slack")

# 15 messages per minute:
# https://api.slack.com/changelog/2025-05-terms-rate-limit-update-and-faq

# Apps unsuitable for Slack Marketplace:
# https://api.slack.com/slack-marketplace/guidelines


SLACK_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="slack",
    auth_required="slack",
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
In slack messages, formatting is *bold* _italic_ ~strikeout~. Tables and headers don't work. Double asterisks don't work.
Triple backquotes for code work, but without language specifier, write newline immediately after triple backquotes.
"""

HELP = """
Help:

slack(op="status")

slack(op="capture", args={"channel_slash_thread": "channel_name/thread_ts"})
slack(op="capture", args={"channel_slash_thread": "C1234567890/thread_ts"})
slack(op="capture", args={"channel_slash_thread": "@username/thread_ts"})
    The workhorse of a chatbot. Slack messages start to appear as role="user" messages here, and role="assistant"
    messages get automatically posted to slack. Tool calls and results are invisible for slack users.
    For incoming messages from kanban: the task title contains capture=CHANNEL_ID/MESSAGE_TS — use that value
    directly as channel_slash_thread. Channel IDs (like C1234567890) work directly, no name lookup needed.

slack(op="post", args={"channel_slash_thread": "channel_name", "text": "Hello world!"})
slack(op="post", args={"channel_slash_thread": "channel_name/thread_ts", "text": "Hello world!"})
slack(op="post", args={"channel_slash_thread": "@username", "text": "Hello world!"})
slack(op="post", args={"channel_slash_thread": "@username/thread_ts", "text": "Hello world!"})
    Simple post to a channel. Slack identifies threads by thread_ts that looks like float unix time.
    If you send to @username that will post a DM, not in any channel.
    If you want to talk to a user, don't call "post", call "capture" instead!

slack(op="post", args={"channel_slash_thread": "channel_name", "path": "folder1/output.pdf"})
    Upload a file, path must be a path valid for the mongo tool (no absolute paths, no spaces in paths,
    no traversal).

slack(op="uncapture")
    If you don't want to talk anymore, call this instead of answering.

slack(op="skip")
    Ignore the most recent message but keep capturing the thread. Useful for unrelated messages (e.g. from other participants).
""" + FORMATTING




SLACK_SETUP_SCHEMA = [
    {
        "bs_name": "slack_bot_name",
        "bs_type": "string_short",
        "bs_default": "",
        "bs_group": "Slack",
        "bs_description": "Custom display name in Slack (uses chat:write.customize). Leave empty to use app default.",
    },
    {
        "bs_name": "slack_bot_icon_url",
        "bs_type": "string_long",
        "bs_default": "",
        "bs_group": "Slack",
        "bs_description": "URL to custom avatar icon in Slack. Leave empty to use app default.",
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
    channel_id: str = ""  # Slack channel ID (C.../D.../G...) for capture, always more reliable than name
    message_author_id: str = ""
    file_contents: List[Dict[str, str]] = field(default_factory=list)


class IntegrationSlack(fi_messenger.FlexusMessenger):
    platform_name = "slack"
    emessage_type = "SLACK"

    def __init__(
            self,
            fclient: ckit_client.FlexusClient,
            rcx: ckit_bot_exec.RobotContext,
            bot_name: str = "",
            bot_icon_url: str = "",
            mongo_collection: Optional[Collection] = None,
    ):
        super().__init__(fclient, rcx)
        self.is_fake = rcx.running_test_scenario
        self.bot_name = bot_name
        self.bot_icon_url = bot_icon_url
        self.mongo_collection = mongo_collection
        self.problems_other = list()
        token = self._get_bot_token()
        logger.info("%s have SLACK_BOT_TOKEN=...%s", rcx.persona.persona_id, (token[-4:] if token else "none"))
        if not token:
            self.web_client = None
            self.oops_a_problem("Slack is not connected, ask user to connect it in bot Integrations", dont_print=True)
        else:
            self.web_client = AsyncWebClient(token=token)
        self.activity_callback: Callable[[ActivitySlack, bool], Awaitable[None]] = self.inbound_activity_to_task
        self.channels_id2name = {}
        self.channels_name2id = {}
        self.users_id2name = {}
        self.users_name2id = {}
        self.users_name2dm = {}
        # Both inbound and outbound deduplicated.
        # Inbound dedup needed: bot receives emessages starting up, handled_emsg_ids delete fails for whatever reason, bot starts up again
        # Outbound dedup needed: bot receives a stray update on existing message (via news mechanism) before it can get an updated last_posted_assistant_ts
        # That's authoritative code that actually got some testing.
        # On laptop 50_000 records: fill deque + set 4.1ms, append+evict 9.2ms, lookup 1.3ms
        self._from_stack_dedup = deque(maxlen=50000)
        self._from_stack_dedup_set = set()
        self._to_slack_dedup = deque(maxlen=50000)
        self._to_slack_dedup_set = set()

    def oops_a_problem(self, text: str, dont_print: bool = False) -> None:
        if not dont_print:
            logger.info("%s slack problem: %s", self.rcx.persona.persona_id, text)
        self.problems_other.append(text)

    def _get_bot_token(self) -> str:
        slack_auth = self.rcx.external_auth.get("slack") or {}
        return (slack_auth.get("token") or {}).get("access_token", "")

    def on_incoming_activity(self, handler: Callable[[ActivitySlack, bool], Awaitable[None]]):
        self.activity_callback = handler
        return handler

    def set_activity_callback(self, cb: Callable[[ActivitySlack, bool], Awaitable[None]]):
        self.activity_callback = cb

    async def inbound_activity_to_task(self, a: ActivitySlack, already_posted_to_captured_thread: bool, extra_details: dict = None, provenance: str = None):
        logger.info("%s Slack %s by @%s in %s: %s", self.rcx.persona.persona_id, a.what_happened, a.message_author_name, a.channel_name, a.message_text[:50])
        if already_posted_to_captured_thread:
            return
        title = "Slack %s user=%r in #%s\n%s" % (a.what_happened, a.message_author_name, a.channel_name, a.message_text)
        if a.file_contents:
            title += f"\n[{len(a.file_contents)} file(s) attached]"
        details = asdict(a)
        to_capture = (a.channel_id or a.channel_name) + "/" + (a.thread_ts or a.message_ts)
        details["to_capture"] = "slack(op=\"capture\", args={\"channel_slash_thread\": %r})" % to_capture
        if a.file_contents:
            details["file_contents"] = f"{len(a.file_contents)} files attached"
        if extra_details:
            details.update(extra_details)
        human_id = "slack:%s" % a.message_author_id if a.message_author_id else ""
        if not self.outside_messages_fexp_name:
            logger.warning("%s accept_outside_messages_only_to_expert() was never called, don't know which expert to use", self.rcx.persona.persona_id)
            return
        post_fn = ckit_kanban.bot_kanban_post_into_inprogress if a.what_happened == "message/im" else ckit_kanban.bot_kanban_post_into_inbox
        await post_fn(
            await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, ""),
            self.rcx.persona.persona_id,
            title=title,
            human_id=human_id,
            details_json=json.dumps(details),
            provenance_message=provenance or "slack_inbound",
            fexp_name=self.outside_messages_fexp_name,
        )

    async def handle_emessage(self, emsg: ckit_bot_query.FExternalMessageOutput) -> None:
        payload = emsg.emsg_payload if isinstance(emsg.emsg_payload, dict) else json.loads(emsg.emsg_payload)
        # backend may send full event_callback or just the inner event
        event = payload.get("event", payload)

        user_id = event.get("user")
        if not user_id:
            logger.info("handle_emessage: no user field, skipping event type=%r subtype=%r keys=%s", event.get("type"), event.get("subtype"), list(event.keys()))
            return

        dedup_key = event.get("client_msg_id") or event.get("ts", "")
        if dedup_key and dedup_key in self._from_stack_dedup_set:
            return
        if dedup_key:
            if len(self._from_stack_dedup) == self._from_stack_dedup.maxlen:
                self._from_stack_dedup_set.discard(self._from_stack_dedup[0])
            self._from_stack_dedup.append(dedup_key)
            self._from_stack_dedup_set.add(dedup_key)

        channel_id = event.get("channel", "")
        channel_type = event.get("channel_type", "channel")
        thread_ts = event.get("thread_ts", "")
        ts = event.get("ts", "")
        text = event.get("text", "")

        if channel_type == "im":
            channel_name = self.users_id2name.get(user_id, user_id)
        else:
            channel_name = self.channels_id2name.get(channel_id, channel_id)

        author_name = await self._get_user_name(user_id)

        user_mentions = re.findall(r'<@([A-Z0-9]+)>', text)
        mention_looked_up = {}
        for uid in user_mentions:
            uname = await self._get_user_name(uid)
            text = text.replace(f'<@{uid}>', f'@{uname}')
            mention_looked_up[uid] = uname

        file_contents = []
        text_files = []
        image_count = 0
        for file_info in event.get("files", [])[:5]:
            try:
                file_bytes, mimetype = await self._download_slack_file(file_info)
                filename = file_info.get("name", "unknown")
                if file_bytes is None:
                    text_files.append(f"[Failed to download: {filename}]")
                elif mimetype and mimetype.startswith("image/") and image_count < 2:
                    file_contents.append(await self._process_slack_image(file_bytes, mimetype))
                    image_count += 1
                elif fi_messenger.is_text_file(file_bytes):
                    processed = await self._process_slack_text_file(file_bytes, filename)
                    text_files.append(processed["m_content"])
                else:
                    text_files.append(f"[Binary file: {filename} ({len(file_bytes)} bytes)]")
            except Exception:
                logger.exception("handle_emessage file processing failed: %s", file_info.get("name", "?"))

        if text_files:
            file_contents.append({"m_type": "text", "m_content": "\n📎 Files:\n" + "\n".join(text_files)})

        event_type = event.get("type", "message")
        if event_type == "app_mention":
            what_happened = "i_was_mentioned"
        else:
            what_happened = f"message/{channel_type}"

        a = ActivitySlack(
            what_happened=what_happened,
            channel_name=channel_name,
            channel_id=channel_id,
            thread_ts=thread_ts,
            message_ts=ts,
            message_text=text,
            message_author_name=author_name,
            mention_looked_up=mention_looked_up,
            message_author_id=user_id,
            file_contents=file_contents,
        )

        really_posted = await self.post_into_captured_thread_as_user(a, channel_id)
        await self.activity_callback(a, really_posted)

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        if not model_produced_args:
            return HELP

        op = model_produced_args.get("op", "")
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        if self.is_fake:
            return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())

        print_help = False
        r = ""

        if not self.web_client:
            assert self.problems_other
            r += "Problems with this tool:\n"
            for problem in self.problems_other:
                r += "  %s\n" % problem
            r += "\n"
            return r

        print_help = not op or "help" in op
        print_status = not op or "status" in op

        if print_status:
            if not self._get_bot_token():
                r += "Don't have Slack token set\n"
            if self.bot_name:
                r += "Bot name: %s\n" % self.bot_name
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
            attach_file = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "path", None)
            something_name, thread_ts = parse_channel_slash_thread(channel_slash_thread)
            if not something_name:
                return "Missing or invalid 'channel_slash_thread' parameter. If this slack thread is already captured, you don't need to call post — just type your message normally and it will appear in Slack automatically.\n"
            try:
                if something_name.startswith('@'):
                    username = something_name.lstrip('@')
                    user_id = self.users_name2id.get(username)
                    if not user_id:
                        return f"ERROR: User {username!r} not found in users_name2id"
                    channel_id = self.users_name2dm.get(username)
                    if not channel_id:
                        dm_resp = await self.web_client.conversations_open(users=user_id)
                        channel_id = dm_resp["channel"]["id"]
                        self.users_name2dm[username] = channel_id
                elif something_name in self.channels_name2id.values():
                    channel_id = something_name
                else:
                    channel_id = self.channels_name2id.get(something_name.lstrip("#"))
                    if not channel_id:
                        return f"ERROR: Channel {something_name!r} not found in channels_name2id"

                this_thread = self.rcx.latest_threads.get(toolcall.fcall_ft_id, None)
                # Caveat: latest_threads might be not deep enough to find it, but here we are handling a failure mode that should not
                # really happen, so it's like an imperfect filter to catch model mistakes.
                if this_thread and this_thread.thread_fields.ft_app_searchable.startswith("slack/"):
                    return "Cannot use \"post\" in a captured thread. Type your message normally and it will appear in Slack automatically.\n"

                something_id_slash_thread = channel_id + ("/" + thread_ts if thread_ts else "")
                # Or maybe the other thread is captured (other_thread might not be this_thread)
                http = await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, toolcall.fcall_untrusted_key)
                other_thread_ft_id = await ckit_ask_model.captured_thread_lookup(
                    http, self.rcx.persona.persona_id, "slack/" + something_id_slash_thread,
                )
                if other_thread_ft_id == toolcall.fcall_ft_id:
                    return "Cannot use \"post\" in a captured thread. Type your message normally and it will appear in Slack automatically.\n"
                if other_thread_ft_id:
                    logger.warning("slack post blocked: target slack/%s already captured by ft_id=%s, this ft_id=%s, persona=%s",
                        something_id_slash_thread, other_thread_ft_id, toolcall.fcall_ft_id, self.rcx.persona.persona_id)
                    return "Hmm this channel_slash_thread is already captured by you in another chat, somehow.\n"

                if attach_file:
                    if self.mongo_collection is None:
                        return "ERROR: Attaching file is not available. You should setup the slack tool with mongo collection"

                    local_path = os.path.join(tempfile.gettempdir(), os.path.basename(attach_file))
                    try:
                        await download_file(self.mongo_collection, attach_file, local_path)
                    except Exception as e:
                        return f"ERROR: Failed to download file from mongo: {e}. Cannot attach it"
                    with open(local_path, 'rb') as f:
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
                    await self.web_client.files_upload_v2(**kwargs)
                    if something_name.startswith('@'):
                        r += f"File upload success to {something_name} (DM)\n"
                    else:
                        r += "File upload success (channel)\n"
                else:
                    if not isinstance(text, str):
                        return "Missing or invalid 'text' parameter\n"
                    kwargs = {"channel": channel_id, "text": text}
                    if thread_ts:
                        kwargs["thread_ts"] = thread_ts
                    if self.bot_name:
                        kwargs["username"] = self.bot_name
                    if self.bot_icon_url:
                        kwargs["icon_url"] = self.bot_icon_url
                    await self.web_client.chat_postMessage(**kwargs)
                    r += f"Post success ({'DM' if something_name.startswith('@') else 'channel'})\n"
            except SlackApiError as e:
                r += "ERROR: %s %s\n" % (type(e).__name__, e)

        elif op == "capture":
            channel_slash_thread = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "channel_slash_thread", "")
            if self.outside_messages_fexp_name and not toolcall.fcall_fexp_name.endswith("_" + self.outside_messages_fexp_name):
                wrong_expert = fi_messenger.CAPTURE_WRONG_EXPERT_MSG % self.outside_messages_fexp_name
                return wrong_expert + (HELP if not channel_slash_thread else "")
            if not channel_slash_thread:
                return "Retry calling this tool with `channel_slash_thread` parameter next time.\n\n" + HELP

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
                    dm_response = await self.web_client.conversations_open(users=user_id)
                    something_id = dm_response["channel"]["id"]
                    self.users_name2dm[username] = something_id
            elif re.match(r'^[A-Z][A-Z0-9]+$', something_name or ""):
                something_id = something_name  # direct Slack channel/DM/group ID
            elif something_name:
                something_id = self.channels_name2id.get(something_name.lstrip("#"), None)
            if not something_id:
                return "Bad channel_slash_thread parameter, it's @username/thread_ts (don't forget @ for users) or channel/thread_ts (it's channel name not id)\n"
            something_id_slash_thread = something_id + ("/" + thread_ts if thread_ts else "")

            searchable = "slack/" + something_id_slash_thread

            try:
                thirty_minutes_ago = str(int(time.time() - 30*60))

                captured_msgs: List[ckit_ask_model.CapturedMessageInput] = []
                total_images = 0
                async for msg in self._get_history(something_name, thread_ts, thirty_minutes_ago, 5):
                    txt = msg.get('text') or ''
                    user_id = msg.get('user')
                    if user_id:
                        author_name = await self._get_user_name(user_id)
                    else:
                        author_name = msg.get('username') or (msg.get('bot_profile') or {}).get('name')
                        if not author_name:
                            author_name = "unknown_user"
                            logger.warning("capture history: no user/username/bot_profile: keys=%s text=%r", list(msg.keys()), txt[:200])
                        user_id = None
                    parts = []
                    if txt:
                        parts.append({"m_type": "text", "m_content": txt})
                    for file_info in msg.get('files', [])[:2]:
                        try:
                            file_bytes, mimetype = await self._download_slack_file(file_info)
                            filename = file_info.get('name', 'unknown')
                            if file_bytes is None:
                                parts.append({"m_type": "text", "m_content": f"[Failed to download: {filename}]"})
                            elif mimetype and mimetype.startswith('image/') and total_images < 3:
                                parts.append(await self._process_slack_image(file_bytes, mimetype))
                                total_images += 1
                            elif fi_messenger.is_text_file(file_bytes):
                                parts.append(await self._process_slack_text_file(file_bytes, filename))
                            else:
                                parts.append({"m_type": "text", "m_content": f"[Binary file: {filename} ({len(file_bytes)} bytes)]"})
                        except Exception:
                            logger.exception("capture file processing failed: %s", file_info.get("name", "?"))
                    if parts:
                        captured_msgs.append(ckit_ask_model.CapturedMessageInput(
                            content=parts,
                            ftm_author_label1=f"slack:{user_id}" if user_id else "slack:unknown",
                            ftm_author_label2=f"{author_name or user_id or 'unknown'}",
                            ftm_provenance={"system_type": "fi_slack"},
                        ))

                http = await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, toolcall.fcall_untrusted_key)
                try:
                    await ckit_ask_model.thread_app_capture_patch(
                        http,
                        toolcall.fcall_ft_id,
                        ft_app_searchable=searchable,
                        ft_app_specific=json.dumps({
                            "last_posted_assistant_ts": max(toolcall.fcall_created_ts, float(thread_ts) if thread_ts else 0) + 0.01
                        }),
                    )
                except gql.transport.exceptions.TransportQueryError as e:
                    return ckit_cloudtool.gql_error_4xx_to_model_reraise_5xx(e, "slack_capture")
                logger.info("Successful capture %s <-> %s, posting %d msgs into the captured thread" % (something_id_slash_thread, toolcall.fcall_ft_id, len(captured_msgs)))
                await ckit_ask_model.captured_thread_post_user_messages(
                    http, self.rcx.persona.persona_id, searchable, captured_msgs,
                    only_to_expert=self.outside_messages_fexp_name,
                )
                r += fi_messenger.CAPTURE_SUCCESS_MSG % (something_name,) + fi_messenger.CAPTURE_ADVICE_MSG
                r += "Remember that slack formatting rules are in effect, and it's not markdown:\n"
                r += FORMATTING

            except SlackApiError as e:
                r += "ERROR: %s %s\n" % (type(e).__name__, e)

        elif op == "uncapture":
            try:
                http = await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, toolcall.fcall_untrusted_key)
                await ckit_ask_model.thread_app_capture_patch(http, toolcall.fcall_ft_id, ft_app_searchable="")
                r += "Uncaptured successfully. This thread is no longer connected to Slack.\n"
            except Exception as e:
                r += "ERROR: %s %s\n" % (type(e).__name__, e)

        elif op == "skip":
            captured_thread = self.rcx.latest_threads.get(toolcall.fcall_ft_id, None)
            if not captured_thread or not captured_thread.thread_fields.ft_app_searchable or not captured_thread.thread_fields.ft_app_searchable.startswith("slack/"):
                return "This thread is not capturing any Slack conversation. Use 'capture' first to start capturing a thread.\n"
            r += "Great, other people are talking, thread is still captured, any new messages will appear in this thread.\n"

        else:
            r += "Unknown operation %r, try \"help\"\n\n" % op

        return r

    async def post_into_captured_thread_as_user(self, a: ActivitySlack, channel_id: str) -> bool:
        something_id_slash_thread = channel_id + ("/" + a.thread_ts if a.thread_ts else "")
        searchable = "slack/" + something_id_slash_thread

        content = [{"m_type": "text", "m_content": a.message_text}]
        if a.file_contents:
            content.extend(a.file_contents)
        content = fi_messenger.compact_message_parts(content)

        http = await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, "")
        logger.info("captured_thread_post searchable=%s msg=%s", searchable, a.message_text[:200])
        try:
            ft_id = await ckit_ask_model.captured_thread_post_user_messages(
                http,
                self.rcx.persona.persona_id,
                searchable,
                [ckit_ask_model.CapturedMessageInput(
                    content=content,
                    ftm_author_label1=f"slack:{a.message_author_id}",
                    ftm_author_label2=f"{a.message_author_name or a.message_author_id}",
                    ftm_provenance={"system_type": "fi_slack"},
                )],
                only_to_expert=self.outside_messages_fexp_name,
                thread_too_old_s=30*86400 if a.thread_ts else 300,
            )
        except gql.transport.exceptions.TransportQueryError as e:
            logger.info("captured_thread_post failed, maybe thread itself already has an error, will uncapture: %s", e)
            return False
        if not ft_id:
            logger.info("No threads match ft_app_searchable=%s so not captured => let bot handle this message.", searchable)
            return False
        logger.info("Captured slack->db ft_id=%s ft_app_searchable=%s sending=%d parts", ft_id, searchable, len(content))
        return True

    async def look_assistant_might_have_posted_something(self, msg: ckit_ask_model.FThreadMessageOutput) -> bool:
        if msg.ftm_role != "assistant":
            return False
        if not msg.ftm_content:
            return False

        if not msg.ft_app_searchable:
            return False
        match = re.match(r'^slack/([^/]+)(?:/(.+))?$', msg.ft_app_searchable)
        if not match:
            # It is actually a chat using telegram or something, not slack, we get all updates, that's fine
            return False
        something_id, thread_ts = match.groups()

        # msg-level ft_app_specific is stale; thread-level has the latest last_posted_assistant_ts
        t = self.rcx.latest_threads.get(msg.ftm_belongs_to_ft_id)
        app_specific = (t.thread_fields.ft_app_specific if t else None) or msg.ft_app_specific
        last_posted_ts = (app_specific or {}).get("last_posted_assistant_ts")
        if last_posted_ts is None:
            logger.warning("slack dedup: no last_posted_assistant_ts ft=%s ft_app_specific=%r", msg.ftm_belongs_to_ft_id, app_specific)
        elif msg.ftm_created_ts <= last_posted_ts:
            return False

        dedup_key = "%s:%03d:%03d" % (msg.ftm_belongs_to_ft_id, msg.ftm_alt, msg.ftm_num)
        if dedup_key in self._to_slack_dedup_set:
            return False

        if not self.web_client:
            return False

        text = msg.ftm_content
        if "TASK_COMPLETED" in text and len(text) <= len("TASK_COMPLETED") + 6:
            logger.info("look_assistant_might_have_posted_something: ftm_content has TASK_COMPLETED, not posting to slack")
            return False
        if "NOTHING_TO_SAY" in text and len(text) <= len("NOTHING_TO_SAY") + 6:
            logger.info("look_assistant_might_have_posted_something: ftm_content has NOTHING_TO_SAY, not posting to slack")
            return False
        text = text.replace("TASK_COMPLETED", "")
        text = text.replace("NOTHING_TO_SAY", "")

        logger.info("assistant->slack ft_id=%s searchable=%s sending %r", msg.ftm_belongs_to_ft_id, msg.ft_app_searchable, text[:20].replace("\n", "\\n"))
        try:
            kwargs = {"channel": something_id, "text": text}
            if thread_ts:
                kwargs["thread_ts"] = thread_ts
            if self.bot_name:
                kwargs["username"] = self.bot_name
            if self.bot_icon_url:
                kwargs["icon_url"] = self.bot_icon_url
            await self.web_client.chat_postMessage(**kwargs)
            if len(self._to_slack_dedup) == self._to_slack_dedup.maxlen:
                self._to_slack_dedup_set.discard(self._to_slack_dedup[0])
            self._to_slack_dedup.append(dedup_key)
            self._to_slack_dedup_set.add(dedup_key)
            logger.info("posted to channel=%s thread_ts=%s", something_id, thread_ts)
        except SlackApiError as e:
            logger.exception("failed to post to slack channel=%s thread_ts=%s", something_id, thread_ts)
            if e.response["error"] == "cannot_reply_to_message":
                try:
                    http = await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, "")
                    await ckit_ask_model.thread_app_capture_patch(http, msg.ftm_belongs_to_ft_id, ft_app_searchable="")
                    logger.info("uncaptured thread ft_id=%s after cannot_reply_to_message", msg.ftm_belongs_to_ft_id)
                except Exception:
                    logger.exception("failed to uncapture thread ft_id=%s", msg.ftm_belongs_to_ft_id)
            return False
        except Exception:
            logger.exception("failed to post to slack channel=%s thread_ts=%s", something_id, thread_ts)
            return False

        http = await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, "")
        await ckit_ask_model.thread_app_capture_patch(http, msg.ftm_belongs_to_ft_id, ft_app_specific=json.dumps({
            "last_posted_assistant_ts": msg.ftm_created_ts
        }))
        logger.info("/look_assistant_might_have_posted_something() success")
        return True

    async def load_workspace_maps(self):
        if not self.web_client:
            return
        my_info = await self.web_client.auth_test()
        logger.info("Slack bot user ID: %s", my_info["user_id"])

        try:
            users_response = await self.web_client.users_list(limit=5000)
            for user in users_response["members"]:
                if user.get("deleted") or user.get("is_bot"):
                    continue
                self.users_id2name[user["id"]] = user["name"]
                self.users_name2id[user["name"]] = user["id"]
                logger.info("user %s -> %s", user["name"], user["id"])
        except SlackApiError as e:
            logger.exception("Failed to list users")
            self.oops_a_problem(f"Failed to list users: {type(e).__name__} {e}", dont_print=True)

        try:
            channels_response = await self.web_client.conversations_list(types="im", limit=5000)
            for rec in channels_response["channels"]:
                if not rec["is_im"]:
                    continue
                username = self.users_id2name.get(rec["user"])
                if username:
                    self.users_name2dm[username] = rec["id"]
                    logger.info("dm %s -> %s", rec["user"], rec["id"])
                # else: DM with a bot or deleted user, skip
        except SlackApiError as e:
            logger.exception("Failed to list DMs")
            self.oops_a_problem(f"Failed to list DMs: {type(e).__name__} {e}", dont_print=True)

        try:
            channels_response = await self.web_client.conversations_list(types="public_channel", limit=1000)
            for channel in channels_response["channels"]:
                self.channels_id2name[channel["id"]] = channel["name"]
                self.channels_name2id[channel["name"]] = channel["id"]
                logger.info("channel #%s -> %s", channel["name"], channel["id"])
        except SlackApiError as e:
            logger.exception("Failed to list channels")
            self.oops_a_problem(f"Failed to list channels: {type(e).__name__} {e}", dont_print=True)


    async def _get_history(self, channel_name: str, thread_ts: Optional[str], long_ago: str, limit_cnt: int):
        if channel_name.startswith('@'):
            channel_id = self.users_name2id.get(channel_name.lstrip("@"))
            if not channel_id:
                raise ValueError(f"User {channel_name} not found in users_name2id")
        elif re.match(r'^[A-Z][A-Z0-9]+$', channel_name):
            channel_id = channel_name  # direct Slack channel/DM/group ID
        else:
            channel_id = self.channels_name2id.get(channel_name)
            if not channel_id:
                raise ValueError(f"Channel {channel_name} not found in channels_name2id")

        logger.info(f"get_history: channel_name={channel_name}, thread_ts={thread_ts!r}, channel_id={channel_id}")

        cursor = None
        while True:
            try:
                if thread_ts and thread_ts.strip():
                    messages_response = await self.web_client.conversations_replies(
                        channel=channel_id, ts=thread_ts, oldest=long_ago, limit=limit_cnt, cursor=cursor
                    )
                else:
                    messages_response = await self.web_client.conversations_history(
                        channel=channel_id, oldest=long_ago, limit=limit_cnt, cursor=cursor
                    )
            except SlackApiError as e:
                if "ratelimited" in str(e):
                    logger.info("ratelimit")
                    await asyncio.sleep(10)
                    continue
                logger.exception("Slack API error in get_history")
                raise

            for msg in messages_response["messages"]:
                yield msg

            if not messages_response.get("has_more"):
                break
            cursor = messages_response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break

    async def _get_user_name(self, user_id: str) -> str:
        if user_id in self.users_id2name:
            return self.users_id2name[user_id]
        if not self.web_client:
            return f"user_{user_id}"
        try:
            author_info = await self.web_client.users_info(user=user_id)
            author_name = author_info["user"]["name"]
            self.users_id2name[user_id] = author_name
            self.users_name2id[author_name] = user_id
            return author_name
        except Exception as e:
            logger.warning(f"Could not resolve user {user_id}: {e}")
            author_name = f"user_{user_id}"
            self.users_id2name[user_id] = author_name
            return author_name

    async def _process_slack_image(self, file_bytes: bytes, mimetype: str) -> dict:
        # Always encode to base64, Slack URLs require authentication and can't be passed directly
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
            logger.exception("Failed to process image")
            return {"m_type": "text", "m_content": f"[Image processing failed: {e}]"}

    async def _process_slack_text_file(self, file_bytes: bytes, filename: str) -> dict:
        formatted = format_cat_output(
            path=filename,
            file_data=file_bytes,
            safety_valve="10k",
        )
        return {"m_type": "text", "m_content": f"📎 {formatted}"}

    async def _download_slack_file(self, file_info: dict) -> tuple[Optional[bytes], Optional[str]]:
        url = file_info.get('url_private_download')
        filename = file_info.get('name', '?')
        if not url:
            logger.warning("no download URL for file %r, keys=%s", filename, list(file_info.keys()))
            return None, None
        headers = {'Authorization': f'Bearer {self._get_bot_token()}'}
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, headers=headers, timeout=30.0)
        if response.status_code != 200:
            logger.error("download %r failed: HTTP %d", filename, response.status_code)
            return None, None
        return response.content, file_info.get('mimetype', 'application/octet-stream')
