import asyncio
import base64
import io
import json
import logging
import os
import re
import tempfile
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

import discord
from discord.errors import DiscordException, HTTPException

from flexus_client_kit import ckit_ask_model, ckit_bot_exec, ckit_cloudtool, ckit_client
from flexus_client_kit.format_utils import format_cat_output
from flexus_client_kit.integrations.fi_mongo_store import download_file, validate_path

logger = logging.getLogger("discord")


DISCORD_TOOL = ckit_cloudtool.CloudTool(
    name="discord",
    description="Interact with Discord. Call with op=\"help\" to print usage or op=\"status\" to inspect configuration.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Start with 'help' for usage"},
            "args": {"type": "object"},
        },
        "required": [],
    },
)


def parse_channel_slash_thread(s: str) -> Tuple[Optional[str], Optional[str]]:
    if not isinstance(s, str):
        return None, None
    s = s.strip()
    if not s:
        return None, None
    s = s[1:] if s.startswith("#") else s
    parts = s.split("/", 1)
    return parts[0], parts[1] if len(parts) > 1 else None


FORMATTING = """
Discord formatting supports **bold**, *italics*, __underline__, ~~strikethrough~~ and `inline code`.
For code blocks use triple backticks without language hints. Avoid block quotes when possible.
"""

HELP = """Help:

discord(op="status")

discord(op="capture", args={"channel_slash_thread": "channel_name/thread_id"})
discord(op="capture", args={"channel_slash_thread": "@username"})
    Capture a Discord thread or DM. After capture all new Discord messages appear as role=\"user\" messages
    and anything you type here is posted back to Discord automatically. Threads require thread_id that
    looks like a long integer. For DMs use the @username form without thread id.

discord(op="post", args={"channel_slash_thread": "channel_name", "text": "Hello world!"})
discord(op="post", args={"channel_slash_thread": "channel_name/thread_id", "text": "Reply in thread"})
discord(op="post", args={"channel_slash_thread": "@username", "text": "Hi there"})
discord(op="post", args={"channel_slash_thread": "channel_name", "path": "folder/output.pdf"})
    Post a message or upload a file. Files must live in mongo_store namespace (no absolute paths).

discord(op="uncapture")
    Stop mirroring messages between this Flexus thread and Discord.

discord(op="skip")
    Ignore the most recent message but keep the capture active. Useful for unrelated chatter.
""" + FORMATTING

CAPTURE_SUCCESS_MSG = "Captured! The next thing you write will be visible in Discord. Don't mention this fact and focus on %r.\n"
CAPTURE_ADVICE_MSG = "Don't call op=post for captured threads. Type your reply directly and it will be posted to Discord.\n"
UNCAPTURE_SUCCESS_MSG = "Uncaptured successfully. This thread is no longer connected to Discord.\n"
SKIP_SUCCESS_MSG = "Great, other people are talking, thread is still captured, any new messages will appear in this thread.\n"
OTHER_CHAT_ALREADY_CAPTURING_MSG = "Some other chat is already capturing %s\n"
BAD_CHANNEL_SLASH_THREAD_MSG = "Bad channel_slash_thread parameter, expected channel/thread_id or @username.\n"
MISSING_OR_INVALID_PARAMETER_MSG = "Missing or invalid %r parameter\n"
CANNOT_POST_TO_CAPTURED_MSG = "Cannot use post for a captured thread. Type your message normally and it will appear in Discord automatically.\n"
NOT_CAPTURING_THREAD_MSG = "This thread is not capturing any Discord conversation. Use 'capture' first.\n"
UNKNOWN_OPERATION_MSG = "Unknown operation %r, try \"help\"\n\n"

DISCORD_SETUP_SCHEMA = [
    {
        "bs_name": "DISCORD_BOT_TOKEN",
        "bs_type": "string_long",
        "bs_default": "",
        "bs_group": "Discord",
        "bs_importance": 0,
        "bs_description": "Bot token from Discord developer portal",
    },
    {
        "bs_name": "discord_watch_channels",
        "bs_type": "string_long",
        "bs_default": "support",
        "bs_group": "Discord",
        "bs_importance": 0,
        "bs_description": "Comma-separated list of channel names to watch (without #). Leave empty to watch everything",
    },
]


@dataclass
class ActivityDiscord:
    what_happened: str
    channel_name: str
    thread_id: Optional[str]
    message_id: str
    message_text: str
    message_author_name: str
    mention_looked_up: Dict[str, str]
    channel_key: str
    attachments: List[Dict[str, str]] = field(default_factory=list)


class IntegrationDiscord:
    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx: ckit_bot_exec.RobotContext,
        DISCORD_BOT_TOKEN: str,
        watch_channels: str,
        mongo_collection=None,
        filter_all_bots: bool = True,
    ):
        self.fclient = fclient
        self.rcx = rcx
        self.DISCORD_BOT_TOKEN = DISCORD_BOT_TOKEN
        self.watch_channels = [x.strip().lstrip("#") for x in (watch_channels or "").split(",") if x.strip()]
        self.mongo_collection = mongo_collection
        self.filter_all_bots = filter_all_bots
        self.activity_callback: Optional[Callable[[ActivityDiscord, bool], Awaitable[None]]] = None
        self.problems_joining: List[str] = []
        self.problems_other: List[str] = []
        self.actually_joined: set[str] = set()
        self.prev_messages: deque[str] = deque(maxlen=256)
        self.channels_id2name: Dict[int, str] = {}
        self.channels_name2id: Dict[str, int] = {}
        self.threads_id2parent: Dict[int, Tuple[int, str]] = {}
        self.users_id2name: Dict[int, str] = {}
        self.users_name2id: Dict[str, int] = {}
        self._ready_event = asyncio.Event()
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.dm_messages = True
        intents.guild_messages = True
        intents.guild_typing = False
        intents.dm_typing = False
        self.bot = discord.Client(intents=intents)
        self.bot_task: Optional[asyncio.Task] = None
        self._closing = False

        @self.bot.event
        async def on_ready():
            logger.info("Discord bot logged in as %s", self.bot.user)
            self._ready_event.set()

        @self.bot.event
        async def on_message(message: discord.Message):
            await self._handle_message(message)

    def set_activity_callback(self, cb: Callable[[ActivityDiscord, bool], Awaitable[None]]):
        self.activity_callback = cb

    async def start_reactive(self):
        if not self.DISCORD_BOT_TOKEN:
            self.problems_other.append("Discord bot token is empty")
            return
        if self.bot_task and not self.bot_task.done():
            return
        try:
            self.bot_task = asyncio.create_task(self.bot.start(self.DISCORD_BOT_TOKEN))
        except Exception as e:
            logger.exception("Failed to start discord client")
            self.problems_other.append(f"{type(e).__name__} {e}")
            self.bot_task = None

    async def close(self):
        self._closing = True
        if self.bot_task and not self.bot_task.done():
            try:
                await self.bot.close()
            except Exception:
                logger.exception("Error closing discord client")
            self.bot_task.cancel()
            try:
                await self.bot_task
            except asyncio.CancelledError:
                pass
            self.bot_task = None
        self._ready_event.clear()

    async def join_channels(self):
        if not self.bot_task:
            return
        try:
            await asyncio.wait_for(self._ready_event.wait(), timeout=30)
        except asyncio.TimeoutError:
            self.problems_other.append("Discord client did not become ready in time")
            return

        try:
            for guild in self.bot.guilds:
                for channel in guild.text_channels:
                    self.channels_id2name[channel.id] = channel.name
                    self.channels_name2id[channel.name] = channel.id
                    if not self.watch_channels or channel.name in self.watch_channels:
                        self.actually_joined.add(channel.name)
                for thread in guild.threads:
                    parent = thread.parent
                    parent_name = parent.name if parent else "thread"
                    self.threads_id2parent[thread.id] = (parent.id if parent else 0, parent_name)
            for guild in self.bot.guilds:
                async for member in guild.fetch_members(limit=None):
                    self.users_id2name[member.id] = member.name
                    self.users_name2id[member.name] = member.id
        except HTTPException as e:
            logger.exception("Failed to fetch guild information")
            self.problems_other.append(f"Failed to inspect guilds: {type(e).__name__} {e}")

        for channel in self.watch_channels:
            if channel and channel not in self.actually_joined:
                self.problems_joining.append(f"Not watching #{channel} (not found)")

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        if not model_produced_args:
            return HELP

        op = model_produced_args.get("op", "")
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        if not self.bot_task and op not in {"help", "status"}:
            return "Discord client is not running. Check status first.\n"

        print_help = not op or "help" in op
        print_status = not op or "status" in op
        r = ""

        if print_status:
            r += "Watching %d channels (configured %d):\n" % (len(self.actually_joined), len(self.watch_channels))
            for channel in sorted(self.actually_joined):
                r += f"  #{channel}\n"
            if self.watch_channels and not self.actually_joined:
                r += "  (none found)\n"
            r += "\n"
            if self.problems_joining:
                r += "Problems configuring watch list:\n"
                for problem in self.problems_joining:
                    r += f"  {problem}\n"
                r += "\n"
            if self.problems_other:
                r += "Other problems:\n"
                for problem in self.problems_other:
                    r += f"  {problem}\n"
                r += "\n"

        if print_help:
            r += HELP

        if print_help or print_status:
            return r

        if op == "post":
            channel_slash_thread = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "channel_slash_thread", "")
            text = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "text", None)
            attach_file = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "path", None)
            if not channel_slash_thread:
                return MISSING_OR_INVALID_PARAMETER_MSG % "channel_slash_thread"

            channel_name, thread_id = parse_channel_slash_thread(channel_slash_thread)
            if not channel_name:
                return MISSING_OR_INVALID_PARAMETER_MSG % "channel_slash_thread"

            target, channel_key, pretty_name, err = await self._resolve_target(channel_name, thread_id)
            if err:
                return err
            assert channel_key
            assert target is not None

            thread_capturing = self._thread_capturing(channel_key)
            if thread_capturing and thread_capturing.thread_fields.ft_id == toolcall.fcall_ft_id:
                return CANNOT_POST_TO_CAPTURED_MSG

            files = []
            if attach_file:
                if self.mongo_collection is None:
                    return "ERROR: Attaching file is not available. Configure mongo_store first"
                path_error = validate_path(attach_file)
                if path_error:
                    return f"Error: {path_error}"
                try:
                    local_path = os.path.join(tempfile.gettempdir(), os.path.basename(attach_file))
                    await download_file(self.mongo_collection, attach_file, local_path)
                    with open(local_path, "rb") as f:
                        data = f.read()
                    discord_file = discord.File(io.BytesIO(data), filename=os.path.basename(attach_file))
                    files.append(discord_file)
                except Exception as e:
                    logger.exception("Failed to download file for discord upload")
                    return f"ERROR: Failed to download file from mongo: {e}."

            try:
                await target.send(content=text, files=files if files else None)
            except DiscordException as e:
                logger.exception("Discord post failed")
                return f"ERROR: {type(e).__name__} {e}"

            if files:
                if thread_id:
                    return f"File upload success (thread {pretty_name})\n"
                return f"File upload success ({pretty_name})\n"
            if thread_id:
                return f"Post success (thread in {pretty_name})\n"
            return f"Post success ({pretty_name})\n"

        if op == "capture":
            channel_slash_thread = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "channel_slash_thread", "")
            channel_name, thread_id = parse_channel_slash_thread(channel_slash_thread)
            if not channel_name:
                return BAD_CHANNEL_SLASH_THREAD_MSG

            target, channel_key, pretty_name, err = await self._resolve_target(channel_name, thread_id)
            if err:
                return err
            assert channel_key
            assert target is not None

            searchable = f"discord/{channel_key}"
            already = self._thread_capturing(channel_key)
            if already:
                if already.thread_fields.ft_id == toolcall.fcall_ft_id:
                    return "Already captured"
                return OTHER_CHAT_ALREADY_CAPTURING_MSG % channel_key

            try:
                history_parts, last_ts = await self._collect_history(target)
            except DiscordException as e:
                logger.exception("Failed to fetch discord history")
                return f"ERROR: {type(e).__name__} {e}"

            http = await self.fclient.use_http()
            if history_parts:
                await ckit_ask_model.thread_add_user_message(
                    http,
                    toolcall.fcall_ft_id,
                    history_parts,
                    "fi_discord2",
                    ftm_alt=100,
                )
            await ckit_ask_model.thread_app_capture_patch(
                http,
                toolcall.fcall_ft_id,
                ft_app_searchable=searchable,
                ft_app_specific=json.dumps({
                    "last_posted_assistant_ts": max(last_ts, toolcall.fcall_created_ts) + 0.01,
                }),
            )
            return CAPTURE_SUCCESS_MSG % pretty_name + CAPTURE_ADVICE_MSG

        if op == "uncapture":
            http = await self.fclient.use_http()
            await ckit_ask_model.thread_app_capture_patch(http, toolcall.fcall_ft_id, ft_app_searchable="")
            return UNCAPTURE_SUCCESS_MSG

        if op == "skip":
            captured_thread = self.rcx.latest_threads.get(toolcall.fcall_ft_id, None)
            if not captured_thread or not captured_thread.thread_fields.ft_app_searchable or not captured_thread.thread_fields.ft_app_searchable.startswith("discord/"):
                return NOT_CAPTURING_THREAD_MSG
            return SKIP_SUCCESS_MSG

        return UNKNOWN_OPERATION_MSG % op

    def _thread_capturing(self, channel_key: str):
        searchable = f"discord/{channel_key}"
        for thread in self.rcx.latest_threads.values():
            if thread.thread_fields.ft_app_searchable == searchable:
                return thread
        return None

    async def _handle_message(self, message: discord.Message):
        if self._closing:
            return
        if message.author.bot:
            if self.filter_all_bots:
                return
            elif message.author.id == self.bot.user.id:
                return
        if not message.content and not message.attachments:
            return
        msg_id = str(message.id)
        if msg_id in self.prev_messages:
            return
        self.prev_messages.append(msg_id)

        channel = message.channel
        channel_key: Optional[str] = None
        channel_display = ""
        thread_id = None

        if isinstance(channel, discord.Thread):
            parent = channel.parent
            parent_name = parent.name if parent else "thread"
            channel_key = f"thread/{channel.id}"
            channel_display = f"{parent_name}/{channel.name}"
            thread_id = str(channel.id)
            if parent:
                self.channels_id2name[parent.id] = parent.name
                self.channels_name2id[parent.name] = parent.id
            self.threads_id2parent[channel.id] = (parent.id if parent else 0, parent_name)
        elif isinstance(channel, discord.DMChannel):
            channel_key = f"dm/{message.author.id}"
            channel_display = f"@{message.author.name}"
        else:
            self.channels_id2name[channel.id] = channel.name
            self.channels_name2id[channel.name] = channel.id
            channel_key = f"channel/{channel.id}"
            channel_display = channel.name

        if channel_key is None:
            return

        if self.watch_channels and channel_key.startswith("channel/") and channel_display not in self.watch_channels:
            return

        self.users_id2name[message.author.id] = message.author.name
        self.users_name2id[message.author.name] = message.author.id

        mention_lookup = {str(user.id): user.name for user in message.mentions}

        attachments: List[Dict[str, str]] = []
        text_file_summaries: List[str] = []
        image_parts: List[Dict[str, str]] = []
        for attachment in message.attachments[:5]:
            try:
                data = await attachment.read()
            except DiscordException:
                logger.exception("Failed to download attachment %s", attachment.filename)
                continue
            mimetype = attachment.content_type or ""
            if mimetype.startswith("image/"):
                img_part = self._process_image(data)
                if img_part:
                    image_parts.append(img_part)
            elif self._is_text_file(data):
                formatted = format_cat_output(attachment.filename, data, safety_valve="10k")
                text_file_summaries.append(f"📎 {formatted}")
            else:
                text_file_summaries.append(f"[Binary file: {attachment.filename} ({len(data)} bytes)]")

        if text_file_summaries:
            attachments.append({"m_type": "text", "m_content": "\n".join(text_file_summaries)})
        attachments.extend(image_parts)

        activity = ActivityDiscord(
            what_happened="message/dm" if isinstance(channel, discord.DMChannel) else "message/channel",
            channel_name=channel_display,
            thread_id=thread_id,
            message_id=str(message.id),
            message_text=message.clean_content or message.content or "",
            message_author_name=message.author.name,
            mention_looked_up=mention_lookup,
            channel_key=channel_key,
            attachments=attachments,
        )

        posted = await self.post_into_captured_thread_as_user(activity)
        if self.activity_callback:
            await self.activity_callback(activity, already_posted_to_captured_thread=posted)

    def _process_image(self, data: bytes) -> Optional[Dict[str, str]]:
        try:
            from PIL import Image
        except ImportError:
            logger.warning("Pillow not installed, cannot process discord image")
            return None
        try:
            with Image.open(io.BytesIO(data)) as img:
                if img.mode == "RGBA":
                    img = img.convert("RGB")
                img.thumbnail((600, 600), Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80, optimize=True)
                buffer.seek(0)
                encoded = base64.b64encode(buffer.read()).decode("utf-8")
                return {"m_type": "image/jpeg", "m_content": encoded}
        except Exception:
            logger.exception("Failed to process discord image")
            return None

    def _is_text_file(self, data: bytes) -> bool:
        if not data:
            return True
        if b"\x00" in data[:1024]:
            return False
        try:
            sample = data[:1024].decode("utf-8")
        except UnicodeDecodeError:
            return False
        printable = sum(1 for ch in sample if ch.isprintable() or ch.isspace())
        return printable / max(1, len(sample)) > 0.8

    async def _collect_history(self, target) -> Tuple[List[Dict[str, str]], float]:
        messages: List[discord.Message] = []
        cutoff = time.time() - 30 * 60
        async for msg in target.history(limit=10, oldest_first=False):
            if msg.created_at.timestamp() < cutoff:
                break
            if msg.author.bot:
                if self.filter_all_bots:
                    continue
                elif msg.author.id == self.bot.user.id:
                    continue
            messages.append(msg)
        messages.reverse()

        text_segments: List[str] = []
        file_summaries: List[str] = []
        image_parts: List[Dict[str, str]] = []
        last_ts = time.time()
        for msg in messages:
            author = msg.author.name
            content = msg.clean_content or msg.content or ""
            if content:
                text_segments.append(f"👤{author}\n\n{content}")
            for attachment in msg.attachments[:3]:
                try:
                    data = await attachment.read()
                except DiscordException:
                    logger.exception("Failed to download attachment during capture")
                    continue
                mimetype = attachment.content_type or ""
                if mimetype.startswith("image/"):
                    img_part = self._process_image(data)
                    if img_part:
                        image_parts.append(img_part)
                elif self._is_text_file(data):
                    formatted = format_cat_output(attachment.filename, data, safety_valve="10k")
                    file_summaries.append(f"📎 {formatted}")
                else:
                    file_summaries.append(f"[Binary file: {attachment.filename} ({len(data)} bytes)]")
            last_ts = max(last_ts, msg.created_at.timestamp())

        parts: List[Dict[str, str]] = []
        if text_segments:
            parts.append({"m_type": "text", "m_content": "\n\n".join(text_segments)})
        if file_summaries:
            parts.append({"m_type": "text", "m_content": "\n".join(file_summaries)})
        parts.extend(image_parts)
        return parts, last_ts

    async def _resolve_target(self, channel_name: str, thread_id: Optional[str]):
        if channel_name.startswith("@"):
            username = channel_name.lstrip("@")
            user = await self._find_user(username)
            if not user:
                return None, None, None, f"ERROR: User {username!r} not found"
            channel = user.dm_channel or await user.create_dm()
            return channel, f"dm/{user.id}", f"@{user.name}", None

        if thread_id:
            try:
                thread_obj = self.bot.get_channel(int(thread_id))
                if thread_obj is None:
                    thread_obj = await self.bot.fetch_channel(int(thread_id))
            except DiscordException:
                thread_obj = None
            if not isinstance(thread_obj, discord.Thread):
                return None, None, None, f"ERROR: Thread {thread_id!r} not found"
            parent = thread_obj.parent
            pretty = f"{parent.name}/{thread_obj.name}" if parent else thread_obj.name
            return thread_obj, f"thread/{thread_obj.id}", pretty, None

        channel_id = self.channels_name2id.get(channel_name)
        if channel_id is None:
            return None, None, None, f"ERROR: Channel {channel_name!r} not found"
        try:
            channel_obj = self.bot.get_channel(channel_id)
            if channel_obj is None:
                channel_obj = await self.bot.fetch_channel(channel_id)
        except DiscordException:
            channel_obj = None
        if channel_obj is None:
            return None, None, None, f"ERROR: Channel {channel_name!r} unavailable"
        return channel_obj, f"channel/{channel_id}", channel_name, None

    async def _find_user(self, username: str) -> Optional[discord.User]:
        user_id = self.users_name2id.get(username)
        if user_id:
            user = self.bot.get_user(user_id)
            if user:
                return user
            try:
                return await self.bot.fetch_user(user_id)
            except DiscordException:
                return None
        for guild in self.bot.guilds:
            member = discord.utils.get(guild.members, name=username)
            if member:
                self.users_name2id[username] = member.id
                self.users_id2name[member.id] = member.name
                return member
        return None

    async def post_into_captured_thread_as_user(self, activity: ActivityDiscord) -> bool:
        thread = self._thread_capturing(activity.channel_key)
        if thread is None:
            return False
        if thread.thread_fields.ft_error is not None:
            return False

        http = await self.fclient.use_http()
        content = [{"m_type": "text", "m_content": f"👤{activity.message_author_name}\n\n{activity.message_text}"}]
        if activity.attachments:
            content.extend(activity.attachments)
        if len(content) > 5:
            text_parts = [c for c in content if c.get("m_type") == "text"]
            image_parts = [c for c in content if c.get("m_type", "").startswith("image/")][:2]
            combined = "\n\n".join(part["m_content"] for part in text_parts)
            content = [{"m_type": "text", "m_content": combined}] + image_parts
        user_pref = json.dumps({"reopen_task_instruction": 1})
        try:
            await ckit_ask_model.thread_add_user_message(
                http,
                thread.thread_fields.ft_id,
                content,
                "fi_discord2",
                ftm_alt=100,
                user_preferences=user_pref,
            )
            return True
        except Exception as e:
            logger.exception("Failed to mirror discord message into Flexus: %s", e)
            return False

    async def look_assistant_might_have_posted_something(self, msg: ckit_ask_model.FThreadMessageOutput) -> bool:
        if msg.ftm_role != "assistant" or not msg.ftm_content:
            return False
        fthread = self.rcx.latest_threads.get(msg.ftm_belongs_to_ft_id, None)
        if not fthread:
            return False
        searchable = fthread.thread_fields.ft_app_searchable or ""
        match = re.match(r"^discord/(.*)$", searchable)
        if not match:
            return False
        channel_key = match.group(1)
        target = await self._resolve_channel_for_post(channel_key)
        if target is None:
            return False
        text = msg.ftm_content if isinstance(msg.ftm_content, str) else json.dumps(msg.ftm_content)
        try:
            await target.send(content=text)
        except DiscordException:
            logger.exception("Failed to post assistant reply to Discord")
            return False

        http = await self.fclient.use_http()
        await ckit_ask_model.thread_app_capture_patch(
            http,
            fthread.thread_fields.ft_id,
            ft_app_specific=json.dumps({"last_posted_assistant_ts": msg.ftm_created_ts}),
        )
        fthread.thread_fields.ft_app_specific = {"last_posted_assistant_ts": msg.ftm_created_ts}
        return True

    async def _resolve_channel_for_post(self, channel_key: str):
        kind, _, ident = channel_key.partition("/")
        if kind == "thread":
            try:
                thread_obj = self.bot.get_channel(int(ident))
                if thread_obj is None:
                    thread_obj = await self.bot.fetch_channel(int(ident))
            except DiscordException:
                return None
            return thread_obj
        if kind == "channel":
            channel_id = int(ident)
            try:
                channel_obj = self.bot.get_channel(channel_id)
                if channel_obj is None:
                    channel_obj = await self.bot.fetch_channel(channel_id)
            except DiscordException:
                return None
            return channel_obj
        if kind == "dm":
            try:
                user = self.bot.get_user(int(ident)) or await self.bot.fetch_user(int(ident))
                if not user:
                    return None
                return user.dm_channel or await user.create_dm()
            except DiscordException:
                return None
        return None
