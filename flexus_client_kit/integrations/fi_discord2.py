import asyncio
import base64
import io
import json
import logging
import os
import tempfile
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

import discord
import gql
from discord import File
from discord.abc import Messageable
from discord.errors import DiscordException
from PIL import Image

from flexus_client_kit import (
    ckit_ask_model,
    ckit_bot_exec,
    ckit_cloudtool,
    ckit_client,
    ckit_utils,
)
from flexus_client_kit.format_utils import format_cat_output
from flexus_client_kit.integrations.fi_mongo_store import download_file, validate_path

logger = logging.getLogger("discord")


DISCORD_TOOL = ckit_cloudtool.CloudTool(
    name="discord",
    description="Interact with Discord channels, threads and DMs. Call with op=\"help\" for usage.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Start with 'help' for usage"},
            "args": {"type": "object"},
        },
    },
)


HELP = """Help:

discord(op=\"status\")

Discord uses <channel>/<thread> identifiers. You can pass channel names like `support` or
explicit IDs such as `123456789012345678`. To capture a DM use `@username`.

discord(op=\"capture\", args={"channel_slash_thread": "channel-name/thread-id"})
discord(op=\"capture\", args={"channel_slash_thread": "@username"})
    Forward all future Discord messages from that channel thread (or DM) into the current
    Flexus thread. Assistant responses posted here will be relayed back to Discord.

discord(op=\"post\", args={"channel_slash_thread": "channel-name", "text": "Hello world!"})
discord(op=\"post\", args={"channel_slash_thread": "channel-name/thread-id", "text": "Thread reply"})
discord(op=\"post\", args={"channel_slash_thread": "@username", "text": "Direct message"})
    Send a message to Discord. To upload a file provide args={"path": "mongo_store/path.ext"}.
    Posting to a captured thread is blocked — simply respond in Flexus instead.

discord(op=\"uncapture\")
    Stop forwarding Discord messages for the currently captured thread.

discord(op=\"skip\")
    Ignore the most recent Discord message but keep capturing future updates.
"""


DISCORD_SETUP_SCHEMA = [
    {
        "bs_name": "DISCORD_BOT_TOKEN",
        "bs_type": "string_long",
        "bs_default": "",
        "bs_group": "Discord",
        "bs_importance": 0,
        "bs_description": "Bot token from Discord developer portal.",
    },
    {
        "bs_name": "discord_watch_channels",
        "bs_type": "string_long",
        "bs_default": "",
        "bs_group": "Discord",
        "bs_importance": 0,
        "bs_description": "Optional comma separated list of channel names or IDs to watch.",
    },
]


@dataclass
class ActivityDiscord:
    channel_name: str
    channel_id: str
    thread_id: Optional[str]
    message_id: str
    message_text: str
    message_author_name: str
    attachments: List[Dict[str, str]] = field(default_factory=list)
    mention_looked_up: Dict[str, str] = field(default_factory=dict)


def _parse_channel_reference(ref: str) -> Tuple[Optional[str], Optional[str]]:
    if not isinstance(ref, str):
        return None, None
    ref = ref.strip()
    if not ref:
        return None, None
    if ref.startswith("<#") and ref.endswith(">"):
        ref = ref[2:-1]
    if ref.startswith("<#"):
        ref = ref[2:]
    if ref.startswith("#"):
        ref = ref[1:]
    if ref.startswith("@"):
        return ref, None
    channel, thread = ref.split("/", 1) if "/" in ref else (ref, None)
    return channel or None, thread or None


class IntegrationDiscord:
    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx: ckit_bot_exec.RobotContext,
        DISCORD_BOT_TOKEN: str,
        watch_channels: str,
        mongo_collection: Optional[Any] = None,
    ):
        self.fclient = fclient
        self.rcx = rcx
        self.bot_token = DISCORD_BOT_TOKEN.strip()
        self.mongo_collection = mongo_collection
        self.activity_callback: Optional[Callable[[ActivityDiscord, bool], Awaitable[None]]] = None
        self.prev_messages: deque[str] = deque(maxlen=200)
        self.user_id2name: Dict[str, str] = {}
        self.user_name2id: Dict[str, str] = {}
        self.channel_id2name: Dict[str, str] = {}
        self.channel_name2id: Dict[str, str] = {}
        self.problems_other: List[str] = []
        self.watch_channel_ids: set[str] = set()
        self.watch_channel_names: set[str] = set()
        self.reactive_task: Optional[asyncio.Task] = None
        self.client: Optional[discord.Client] = None

        for item in [x.strip() for x in watch_channels.split(",") if x.strip()]:
            if item.isdigit():
                self.watch_channel_ids.add(item)
            else:
                self.watch_channel_names.add(item.lstrip("#").lower())

        if not self.bot_token:
            self.problems_other.append("DISCORD_BOT_TOKEN is not configured")
            return

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.dm_messages = True
        intents.guild_messages = True

        self.client = discord.Client(intents=intents)
        self._setup_event_handlers()

    def set_activity_callback(self, cb: Callable[[ActivityDiscord, bool], Awaitable[None]]):
        self.activity_callback = cb

    async def start_reactive(self) -> None:
        if not self.client or self.reactive_task:
            return
        try:
            self.reactive_task = asyncio.create_task(self.client.start(self.bot_token))
            self.reactive_task.add_done_callback(lambda t: ckit_utils.report_crash(t, logger))
        except Exception as e:
            logger.exception("Failed to start discord client")
            self.problems_other.append(f"{type(e).__name__} {e}")
            self.client = None

    async def close(self) -> None:
        if self.reactive_task and not self.reactive_task.done():
            self.reactive_task.cancel()
            try:
                await self.reactive_task
            except asyncio.CancelledError:
                pass
        if self.client and not self.client.is_closed():
            await self.client.close()
        self.reactive_task = None
        self.client = None

    async def join_channels(self) -> None:
        if self.watch_channel_ids or self.watch_channel_names:
            logger.info("Discord watch list: ids=%s names=%s", self.watch_channel_ids, self.watch_channel_names)

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

        if not self.client:
            summary = "Problems with this tool:\n" + "\n".join(f"  {p}" for p in self.problems_other)
            return summary + "\n"

        print_help = not op or "help" in op
        print_status = not op or "status" in op

        result = ""
        if print_status:
            ready = await self._ensure_ready()
            result += "Discord client: %s\n" % ("connected" if ready else "connecting")
            if self.watch_channel_ids or self.watch_channel_names:
                result += "Watching channels: %s\n" % ", ".join(sorted(self.watch_channel_ids | self.watch_channel_names))
            result += "Known guild channels: %d\n" % len(self.channel_id2name)
            if self.problems_other:
                result += "Problems:\n"
                for problem in self.problems_other:
                    result += f"  {problem}\n"
            result += "\n"

        if print_help:
            result += HELP
            return result

        if op == "post":
            channel_ref = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "channel_slash_thread", "")
            text = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "text", None)
            attach_path = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "path", None)

            if not channel_ref:
                return "Missing channel_slash_thread parameter\n"
            destination = await self._resolve_destination(channel_ref)
            if destination.error:
                return destination.error
            if destination.thread_identifier:
                thread_capture = self._thread_capturing(destination.thread_identifier)
                if thread_capture and thread_capture.thread_fields.ft_id == toolcall.fcall_ft_id:
                    return "Cannot use post for a captured thread. Respond normally instead.\n"

            if not text and not attach_path:
                return "Provide text or path for posting\n"

            await self._send_message(destination, text, attach_path)
            if attach_path and not text:
                return "File upload success\n"
            if attach_path and text:
                return "File upload success with comment\n"
            return "Post success\n"

        if op == "capture":
            channel_ref = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "channel_slash_thread", "")
            if not channel_ref:
                return "Missing channel_slash_thread parameter\n"
            destination = await self._resolve_destination(channel_ref)
            if destination.error:
                return destination.error
            identifier = destination.thread_identifier or destination.channel_identifier
            if not identifier:
                return "Cannot capture this location\n"
            searchable = f"discord/{identifier}"
            already = self._thread_capturing(identifier)
            if already:
                if already.thread_fields.ft_id == toolcall.fcall_ft_id:
                    return "Already captured\n"
                return "Some other chat is already capturing %s\n" % identifier

            messages = await self._collect_recent_messages(destination)
            http = await self.fclient.use_http()
            if messages:
                await ckit_ask_model.thread_add_user_message(
                    http,
                    toolcall.fcall_ft_id,
                    messages,
                    "fi_discord2",
                    ftm_alt=100,
                )
            await ckit_ask_model.thread_app_capture_patch(
                http,
                toolcall.fcall_ft_id,
                ft_app_searchable=searchable,
                ft_app_specific=json.dumps({"last_posted_assistant_ts": toolcall.fcall_created_ts}),
            )
            return "Captured! Future Discord messages will appear here.\n"

        if op == "uncapture":
            http = await self.fclient.use_http()
            await ckit_ask_model.thread_app_capture_patch(http, toolcall.fcall_ft_id, ft_app_searchable="")
            return "Uncaptured successfully.\n"

        if op == "skip":
            captured_thread = self.rcx.latest_threads.get(toolcall.fcall_ft_id)
            if not captured_thread or not captured_thread.thread_fields.ft_app_searchable.startswith("discord/"):
                return "This thread is not capturing any Discord conversation.\n"
            return "Skipped. The capture remains active.\n"

        return "Unknown operation %r, try \"help\"\n" % op

    async def _ensure_ready(self) -> bool:
        if not self.client:
            return False
        for _ in range(30):
            if self.client.is_ready():
                return True
            await asyncio.sleep(1)
        return self.client.is_ready()

    def _thread_capturing(self, identifier: str) -> Optional[ckit_bot_exec.FThreadWithMessages]:
        searchable = f"discord/{identifier}"
        for thread in self.rcx.latest_threads.values():
            if thread.thread_fields.ft_app_searchable == searchable:
                return thread
        return None

    async def _resolve_destination(self, channel_ref: str):
        @dataclass
        class Destination:
            target: Optional[Messageable]
            channel_identifier: Optional[str]
            thread_identifier: Optional[str]
            display_name: str
            error: Optional[str]

        channel_token, thread_token = _parse_channel_reference(channel_ref)
        if not channel_token:
            return Destination(None, None, None, "", "channel_slash_thread not understood\n")

        await self._ensure_ready()

        if channel_token.startswith("@"):
            username = channel_token[1:]
            user_id = self.user_name2id.get(username.lower())
            if not user_id and username.isdigit():
                user_id = username
            if not user_id:
                return Destination(None, None, None, "", f"Unknown Discord user {username!r}\n")
            user = self.client.get_user(int(user_id)) if self.client else None
            if not user and self.client:
                try:
                    user = await self.client.fetch_user(int(user_id))
                except DiscordException as e:
                    return Destination(None, None, None, "", f"Cannot fetch user: {e}\n")
            if not user:
                return Destination(None, None, None, "", f"Cannot resolve user {username!r}\n")
            channel = user.dm_channel or await user.create_dm()
            return Destination(channel, str(channel.id), None, user.display_name or user.name, None)

        channel_obj: Optional[discord.abc.GuildChannel] = None
        if channel_token.isdigit() and self.client:
            channel_obj = self.client.get_channel(int(channel_token))
            if not channel_obj:
                try:
                    channel_obj = await self.client.fetch_channel(int(channel_token))
                except DiscordException as e:
                    return Destination(None, None, None, "", f"Cannot fetch channel: {e}\n")
        if not channel_obj and self.client:
            lookup = channel_token.lower()
            channel_id = self.channel_name2id.get(lookup)
            if channel_id:
                channel_obj = self.client.get_channel(int(channel_id))
        if not channel_obj:
            return Destination(None, None, None, "", f"Unknown Discord channel {channel_token!r}\n")

        self._record_channel(channel_obj)
        if thread_token:
            thread_obj: Optional[discord.Thread]
            if thread_token.isdigit() and self.client:
                thread_obj = self.client.get_channel(int(thread_token))  # type: ignore[assignment]
                if not thread_obj:
                    try:
                        thread_obj = await self.client.fetch_channel(int(thread_token))  # type: ignore[assignment]
                    except DiscordException as e:
                        return Destination(None, None, None, "", f"Cannot fetch thread: {e}\n")
            else:
                thread_obj = None
            if not thread_obj and isinstance(channel_obj, discord.TextChannel):
                thread_obj = channel_obj.get_thread(int(thread_token)) if thread_token and thread_token.isdigit() else None
            if not thread_obj:
                return Destination(None, None, None, "", f"Unknown Discord thread {thread_token!r}\n")
            self._record_thread(thread_obj)
            return Destination(thread_obj, str(thread_obj.parent_id or channel_obj.id), str(thread_obj.id), thread_obj.name, None)

        return Destination(channel_obj, str(channel_obj.id), None, channel_obj.name, None)

    async def _send_message(self, destination, text: Optional[str], attach_path: Optional[str]) -> None:
        if not destination.target:
            raise RuntimeError("destination missing")
        files: List[File] = []
        if attach_path:
            if not self.mongo_collection:
                raise RuntimeError("Mongo collection not configured for attachments")
            perr = validate_path(attach_path)
            if perr:
                raise RuntimeError(perr)
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp_name = tmp.name
            try:
                await download_file(self.mongo_collection, attach_path, tmp_name)
                with open(tmp_name, "rb") as f:
                    payload = f.read()
                file_obj = File(io.BytesIO(payload), filename=attach_path.split("/")[-1])
                files.append(file_obj)
            finally:
                try:
                    os.unlink(tmp_name)
                except OSError:
                    pass
        try:
            await destination.target.send(content=text, files=files if files else None)
        except DiscordException as e:
            raise RuntimeError(f"Discord error: {e}")

    async def _collect_recent_messages(self, destination) -> List[Dict[str, Any]]:
        if not destination.target:
            return []
        try:
            history = []
            async for message in destination.target.history(limit=10, oldest_first=False):
                if self.client and message.author == self.client.user:
                    continue
                history.append(message)
        except DiscordException:
            logger.exception("Failed to read discord history")
            return []

        parts: List[Dict[str, Any]] = []
        for message in reversed(history):
            author_name = self._record_user(message.author)
            text = message.content.strip()
            if text:
                parts.append({"m_type": "text", "m_content": f"👤{author_name}\n\n{text}"})
            attachments = await self._extract_attachments(message)
            parts.extend(attachments)
        return parts

    async def _extract_attachments(self, message: discord.Message) -> List[Dict[str, str]]:
        items: List[Dict[str, str]] = []
        for attachment in message.attachments:
            try:
                data = await attachment.read()
            except DiscordException:
                logger.exception("Failed to download attachment")
                continue
            if attachment.content_type and attachment.content_type.startswith("image/"):
                image_part = self._process_image(data)
                if image_part:
                    items.append(image_part)
            else:
                summary = format_cat_output(attachment.filename or "attachment", data, "10k")
                items.append({"m_type": "text", "m_content": f"📎 {summary}"})
        return items

    def _process_image(self, data: bytes) -> Optional[Dict[str, str]]:
        try:
            img = Image.open(io.BytesIO(data))
            img.thumbnail((600, 600), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            if img.mode == "RGBA":
                img = img.convert("RGB")
            img.save(buf, format="JPEG", quality=80, optimize=True)
            buf.seek(0)
            return {"m_type": "image/jpeg", "m_content": base64.b64encode(buf.read()).decode("utf-8")}
        except Exception:
            logger.exception("Failed to process image")
            return None

    def _setup_event_handlers(self) -> None:
        if not self.client:
            return

        @self.client.event  # type: ignore[misc]
        async def on_ready():
            logger.info("Logged in to Discord as %s", self.client.user)
            await self._populate_caches()

        @self.client.event  # type: ignore[misc]
        async def on_message(message: discord.Message):
            await self._handle_incoming_message(message)

    async def _populate_caches(self) -> None:
        if not self.client:
            return
        for guild in self.client.guilds:
            for channel in guild.text_channels:
                self._record_channel(channel)
            for thread in guild.threads:
                self._record_thread(thread)
            try:
                async for member in guild.fetch_members(limit=None):
                    self._record_user(member)
            except DiscordException:
                logger.info("Unable to prefetch all members for guild %s", guild.id)

    def _record_channel(self, channel: discord.abc.GuildChannel) -> None:
        self.channel_id2name[str(channel.id)] = getattr(channel, "name", str(channel.id))
        if hasattr(channel, "name"):
            self.channel_name2id[channel.name.lower()] = str(channel.id)

    def _record_thread(self, thread: discord.Thread) -> None:
        self.channel_id2name[str(thread.id)] = thread.name
        self.channel_name2id[thread.name.lower()] = str(thread.id)

    def _record_user(self, member: discord.abc.User) -> str:
        display = member.display_name if hasattr(member, "display_name") else member.name
        self.user_id2name[str(member.id)] = display
        self.user_name2id[display.lower()] = str(member.id)
        return display

    async def _handle_incoming_message(self, message: discord.Message) -> None:
        if not self.client:
            return
        if message.author == self.client.user:
            return
        if message.guild is None and not isinstance(message.channel, discord.DMChannel):
            return

        channel_identifier, thread_identifier = self._identify_message_location(message)
        if not channel_identifier:
            return

        if self.watch_channel_ids or self.watch_channel_names:
            channel_name = self.channel_id2name.get(channel_identifier, "")
            if (
                channel_identifier not in self.watch_channel_ids
                and channel_name.lower() not in self.watch_channel_names
            ):
                return

        if str(message.id) in self.prev_messages:
            return
        self.prev_messages.append(str(message.id))

        author_name = self._record_user(message.author)
        text = message.content or ""
        attachments = await self._extract_attachments(message)

        activity = ActivityDiscord(
            channel_name=self.channel_id2name.get(channel_identifier, channel_identifier),
            channel_id=channel_identifier,
            thread_id=thread_identifier,
            message_id=str(message.id),
            message_text=text,
            message_author_name=author_name,
            attachments=attachments,
        )

        posted = await self.post_into_captured_thread_as_user(activity)
        if self.activity_callback:
            await self.activity_callback(activity, posted)

    def _identify_message_location(self, message: discord.Message) -> Tuple[Optional[str], Optional[str]]:
        if isinstance(message.channel, discord.Thread):
            self._record_thread(message.channel)
            return str(message.channel.parent_id or message.channel.id), str(message.channel.id)
        if isinstance(message.channel, discord.DMChannel):
            return str(message.channel.id), None
        if hasattr(message.channel, "id"):
            self._record_channel(message.channel)
            return str(message.channel.id), None
        return None, None

    async def post_into_captured_thread_as_user(self, activity: ActivityDiscord) -> bool:
        identifier = activity.channel_id
        if activity.thread_id:
            identifier += f"/{activity.thread_id}"
        thread_capturing = self._thread_capturing(identifier)
        if thread_capturing is None or thread_capturing.thread_fields.ft_error:
            return False

        http = await self.fclient.use_http()
        parts: List[Dict[str, str]] = []
        text = activity.message_text.strip()
        if text:
            parts.append({"m_type": "text", "m_content": f"👤{activity.message_author_name}\n\n{text}"})
        parts.extend(activity.attachments)
        if not parts:
            return False
        if len(parts) > 5:
            text_parts = [p for p in parts if p["m_type"] == "text"]
            image_parts = [p for p in parts if p["m_type"].startswith("image/")]
            combined = "\n\n".join(p["m_content"] for p in text_parts)
            parts = [{"m_type": "text", "m_content": combined}] + image_parts[:2]

        try:
            await ckit_ask_model.thread_add_user_message(
                http,
                thread_capturing.thread_fields.ft_id,
                parts,
                "fi_discord2",
                ftm_alt=100,
                user_preferences=json.dumps({"reopen_task_instruction": 1}),
            )
            return True
        except gql.transport.exceptions.TransportQueryError as e:  # type: ignore[attr-defined]
            logger.info("Discord capture failed, uncapturing: %s", e)
            await ckit_ask_model.thread_app_capture_patch(
                http,
                thread_capturing.thread_fields.ft_id,
                ft_app_searchable="",
            )
            return False

    async def look_assistant_might_have_posted_something(self, msg: ckit_ask_model.FThreadMessageOutput) -> bool:
        if msg.ftm_role != "assistant" or not msg.ftm_content:
            return False
        fthread = self.rcx.latest_threads.get(msg.ftm_belongs_to_ft_id)
        if not fthread:
            return False
        searchable = fthread.thread_fields.ft_app_searchable
        if not searchable.startswith("discord/"):
            return False
        identifier = searchable[len("discord/") :]
        channel_id, thread_id = identifier.split("/", 1) if "/" in identifier else (identifier, None)

        await self._ensure_ready()
        if not self.client:
            return False

        target = None
        if thread_id:
            target = self.client.get_channel(int(thread_id))
            if not target:
                try:
                    target = await self.client.fetch_channel(int(thread_id))
                except DiscordException:
                    logger.exception("Cannot fetch discord thread %s", thread_id)
                    return False
        else:
            target = self.client.get_channel(int(channel_id))
            if not target:
                try:
                    target = await self.client.fetch_channel(int(channel_id))
                except DiscordException:
                    logger.exception("Cannot fetch discord channel %s", channel_id)
                    return False
        if not target:
            return False

        text = self._format_assistant_message(msg.ftm_content)
        if not text:
            return False

        try:
            await target.send(text)
        except DiscordException:
            logger.exception("Failed to post assistant message to Discord")
            return False

        http = await self.fclient.use_http()
        await ckit_ask_model.thread_app_capture_patch(
            http,
            fthread.thread_fields.ft_id,
            ft_app_specific=json.dumps({"last_posted_assistant_ts": msg.ftm_created_ts}),
        )
        fthread.thread_fields.ft_app_specific = {"last_posted_assistant_ts": msg.ftm_created_ts}
        return True

    def _format_assistant_message(self, content: Any) -> str:
        if isinstance(content, str):
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                return content
        else:
            parsed = content

        if isinstance(parsed, list):
            parts = []
            for item in parsed:
                if isinstance(item, dict):
                    if item.get("m_type") == "text":
                        parts.append(item.get("m_content", ""))
                    elif item.get("m_type", "").startswith("image/"):
                        parts.append("[image attachment]")
                    else:
                        parts.append(str(item))
                else:
                    parts.append(str(item))
            return "\n\n".join([p for p in parts if p]).strip()
        if isinstance(parsed, dict):
            return parsed.get("m_content", str(parsed))
        return str(parsed)
