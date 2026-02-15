import asyncio
import base64
import io
import json
import logging
import os
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional

import gql
from PIL import Image
import telegram
import telegram.ext

from flexus_client_kit import ckit_ask_model, ckit_bot_exec, ckit_bot_query, ckit_client, ckit_cloudtool, ckit_erp
from flexus_client_kit.format_utils import format_cat_output
from flexus_client_kit.integrations import fi_messenger

logger = logging.getLogger("teleg")

# Testing telegram with webhook on localhost:
#
# npm install --global smee-client
# Visit https://smee.io/ , click Start a new channel => CHAN
#
# In parallel console (unfortunately the complete path needed):
# smee -u https://smee.io/CHAN --target http://127.0.0.1:8008/v1/webhook/telegram/TELE_BOT_ID
#
# In dev console:
# export FLEXUS_TELEGRAM_WEBHOOK_URL="https://smee.io/CHAN"
# => start bot


TELEGRAM_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="telegram",
    description="Interact with Telegram. Call with op=\"help\" for usage, or op=\"status+help\" for both.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Start with 'help' for usage"},
            "args": {"type": "object"},
        },
    },
)

HELP = """Help:

telegram(op="status")

telegram(op="capture", args={"chat_id": 123456789})
    Capture a Telegram chat. Messages will appear here and your responses will be sent back.
    You can only capture chats where the bot is a member.

telegram(op="uncapture", args={"contact_id": "abc123", "conversation_summary": "Brief summary"})
    Stop capturing. If contact_id is provided, logs a CRM activity with the summary.

telegram(op="post", args={"chat_id": 123456789, "text": "Hello!"})
    Post a message to a Telegram chat. Don't use this for captured chats.

telegram(op="skip")
    Ignore the most recent message but keep capturing.

telegram(op="generate_chat_link", args={"contact_id": "abc123"})
    Generate a link that opens a chat with this bot and passes the contact_id.
    When clicked, bot receives /start c_<contact_id>.
"""

TELEGRAM_SETUP_SCHEMA = [
    {
        "bs_name": "TELEGRAM_BOT_TOKEN",
        "bs_type": "string_long",
        "bs_default": "",
        "bs_group": "Telegram",
        "bs_importance": 0,
        "bs_description": "Bot token from @BotFather",
    },
]


@dataclass
class ActivityTelegram:
    chat_id: int
    chat_type: str  # "private", "group", "supergroup", "channel"
    message_id: int
    message_text: str
    message_author_name: str
    message_author_id: int
    attachments: List[Dict[str, str]] = field(default_factory=list)


class IntegrationTelegram:
    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx: ckit_bot_exec.RobotContext,
        TELEGRAM_BOT_TOKEN: str,
    ):
        self.fclient = fclient
        self.rcx = rcx
        self.bot_token = TELEGRAM_BOT_TOKEN.strip()
        self.problems_accumulator: List[str] = []

        self.activity_callback: Optional[Callable[[ActivityTelegram, bool], Awaitable[None]]] = None
        self.tg_app: Optional[telegram.ext.Application] = None

        self._prev_messages: deque[str] = deque(maxlen=fi_messenger.MAX_DEDUP_MESSAGES)

        if not self.bot_token:
            self.oops_a_problem("TELEGRAM_BOT_TOKEN is not configured")
            return

        try:
            self.tg_app = telegram.ext.Application.builder().token(self.bot_token).build()
            # self._setup_handlers()
        except ImportError:
            self.oops_a_problem("python-telegram-bot not installed")
        except Exception as e:
            logger.exception("Failed to initialize Telegram bot")
            self.oops_a_problem(f"{type(e).__name__}: {e}")

    def oops_a_problem(self, text: str) -> None:
        logger.info("%s telegram problem: %s", self.rcx.persona.persona_id, text)
        self.problems_accumulator.append(text)

    @classmethod
    async def create(cls, fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext, TELEGRAM_BOT_TOKEN: str) -> "IntegrationTelegram":
        instance = cls(fclient, rcx, TELEGRAM_BOT_TOKEN)
        if instance.tg_app and ":" in instance.bot_token:
            bot_id = instance.bot_token.split(":")[0]
            await instance._register_and_set_webhook(bot_id)
        return instance

    async def _register_and_set_webhook(self, bot_id: str) -> None:
        logger.info("%s telegram registered successfully %s", self.rcx.persona.persona_id, bot_id)
        if webhook_url := os.environ.get("FLEXUS_TELEGRAM_WEBHOOK_URL"):
            pass
        elif os.environ.get("FLEXUS_ENV") == "production":
            webhook_url = f"https://flexus.team/v1/webhook/telegram/{bot_id}"
        elif os.environ.get("FLEXUS_ENV") == "staging":
            webhook_url = f"https://staging.flexus.team/v1/webhook/telegram/{bot_id}"
        else:
            self.oops_a_problem("FLEXUS_ENV must be 'production' or 'staging', or set FLEXUS_TELEGRAM_WEBHOOK_URL")
            return
        try:
            await self.tg_app.initialize()
            info = await self.tg_app.bot.get_webhook_info()
            if info.url != webhook_url:
                await self.tg_app.bot.set_webhook(webhook_url)
                logger.info("%s telegram webhook set successfully %s", self.rcx.persona.persona_id, webhook_url)
        except Exception as e:
            logger.exception("%s telegram failed to set webhook", self.rcx.persona.persona_id)
            self.oops_a_problem(f"webhook: {type(e).__name__}: {e}")

        # For some reason, even start() is not necessary, it works without it
        # await self.tg_app.start()

    def set_activity_callback(self, cb: Callable[[ActivityTelegram, bool], Awaitable[None]]) -> None:
        self.activity_callback = cb

    async def close(self) -> None:
        if self.tg_app:
            try:
                if self.tg_app.updater and self.tg_app.updater.running:
                    await self.tg_app.updater.stop()
                await self.tg_app.stop()
                await self.tg_app.shutdown()
            except Exception:
                logger.exception("%s telegram failed to close", self.rcx.persona.persona_id)
                pass

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        if not model_produced_args:
            return HELP

        op = model_produced_args.get("op", "")
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        if not self.tg_app:
            return "Problems:\n" + "\n".join(f"  {p}" for p in self.problems_accumulator) + "\n"

        print_help = not op or "help" in op
        print_status = not op or "status" in op
        r = ""

        if print_status:
            try:
                bot_info = await self.tg_app.bot.get_me()
                r += f"Bot: @{bot_info.username} (id={bot_info.id})\n"
            except Exception as e:
                r += f"Bot info error: {e}\n"
            if self.problems_accumulator:
                r += "Problems:\n" + "\n".join(f"  {p}" for p in self.problems_accumulator) + "\n"
            r += "\n"

        if print_help:
            return r + HELP
        if print_status:
            return r

        if op == "post":
            chat_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "chat_id", None)
            text = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "text", None)
            if not chat_id:
                return "Missing chat_id parameter\n"
            if not text:
                return "Missing text parameter\n"

            if (thread_cap := self._thread_capturing(str(chat_id))) and thread_cap.thread_fields.ft_id == toolcall.fcall_ft_id:
                return "Cannot post to captured chat. Your responses are sent automatically.\n"

            try:
                await self.tg_app.bot.send_message(chat_id=int(chat_id), text=text)
                return "Post success\n"
            except Exception as e:
                return f"ERROR: {type(e).__name__}: {e}\n"

        if op == "capture":
            chat_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "chat_id", None)
            if not chat_id:
                return "Missing chat_id parameter\n"

            identifier = str(chat_id)
            if already := self._thread_capturing(identifier):
                if already.thread_fields.ft_id == toolcall.fcall_ft_id:
                    return "Already captured\n"
                return fi_messenger.OTHER_CHAT_ALREADY_CAPTURING_MSG % identifier

            http = await self.fclient.use_http()
            searchable = fi_messenger.build_searchable("telegram", identifier)
            await ckit_ask_model.thread_app_capture_patch(
                http,
                toolcall.fcall_ft_id,
                ft_app_searchable=searchable,
                ft_app_specific=json.dumps({"last_posted_assistant_ts": toolcall.fcall_created_ts}),
            )
            if fthread := self.rcx.latest_threads.get(toolcall.fcall_ft_id):
                fthread.thread_fields.ft_app_searchable = searchable
            return fi_messenger.CAPTURE_SUCCESS_MSG % identifier + fi_messenger.CAPTURE_ADVICE_MSG

        if op == "uncapture":
            contact_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "contact_id", None)
            summary = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "conversation_summary", None)
            if contact_id and not summary:
                return "Missing conversation_summary.\n"

            http = await self.fclient.use_http()
            await ckit_ask_model.thread_app_capture_patch(http, toolcall.fcall_ft_id, ft_app_searchable="")
            if fthread := self.rcx.latest_threads.get(toolcall.fcall_ft_id):
                fthread.thread_fields.ft_app_searchable = ""
            if contact_id:
                await ckit_erp.create_erp_record(self.fclient, "crm_activity", self.rcx.persona.ws_id, {
                    "ws_id": self.rcx.persona.ws_id,
                    "activity_title": "TELEGRAM conversation",
                    "activity_type": "MESSENGER_CHAT",
                    "activity_platform": "TELEGRAM",
                    "activity_direction": "INBOUND",
                    "activity_contact_id": contact_id,
                    "activity_ft_id": toolcall.fcall_ft_id,
                    "activity_summary": summary,
                    "activity_occurred_ts": time.time(),
                })
            return fi_messenger.UNCAPTURE_SUCCESS_MSG

        if op == "skip":
            if not (captured := self.rcx.latest_threads.get(toolcall.fcall_ft_id)) or not captured.thread_fields.ft_app_searchable.startswith("telegram/"):
                return fi_messenger.NOT_CAPTURING_MSG
            return fi_messenger.SKIP_SUCCESS_MSG

        if op == "generate_chat_link":
            contact_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "contact_id", None)
            if not contact_id:
                return "Missing contact_id parameter\n"
            try:
                bot_info = await self.tg_app.bot.get_me()
                return f"https://t.me/{bot_info.username}?start=c_{contact_id}\n"
            except Exception as e:
                return f"ERROR: {type(e).__name__}: {e}\n"

        return fi_messenger.UNKNOWN_OPERATION_MSG % op

    async def _extract_attachments(self, msg: telegram.Message) -> List[Dict[str, str]]:
        items: List[Dict[str, str]] = []
        photo = msg.photo[-1] if msg.photo else None
        doc = msg.document

        if photo:
            try:
                file = await photo.get_file()
                data = await file.download_as_bytearray()
                img_part = self._process_image(bytes(data))
                if img_part:
                    items.append(img_part)
            except Exception as e:
                logger.warning("Failed to download photo: %s", e)

        if doc:
            try:
                file = await doc.get_file()
                data = await file.download_as_bytearray()
                if doc.mime_type and doc.mime_type.startswith("image/"):
                    img_part = self._process_image(bytes(data))
                    if img_part:
                        items.append(img_part)
                elif fi_messenger.is_text_file(bytes(data)):
                    formatted = format_cat_output(doc.file_name or "file", bytes(data), safety_valve="10k")
                    items.append({"m_type": "text", "m_content": f"{fi_messenger.FILE_EMOJI} {formatted}"})
                else:
                    items.append({"m_type": "text", "m_content": f"[Binary file: {doc.file_name} ({len(data)} bytes)]"})
            except Exception as e:
                logger.warning("Failed to download document: %s", e)

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

    def _thread_capturing(self, identifier: str) -> Optional[ckit_bot_query.FThreadWithMessages]:
        return fi_messenger.find_thread_capturing(self.rcx, "telegram", identifier)

    async def post_into_captured_thread_as_user(self, activity: ActivityTelegram) -> bool:
        if not (thread_cap := self._thread_capturing(str(activity.chat_id))):
            return False
        http = await self.fclient.use_http()
        if thread_cap.thread_fields.ft_error:
            logger.info("telegram post_into_captured: thread has error, uncapturing ft_id=%s", thread_cap.thread_fields.ft_id)
            await ckit_ask_model.thread_app_capture_patch(http, thread_cap.thread_fields.ft_id, ft_app_searchable="")
            return False

        parts: List[Dict[str, str]] = []
        if activity.message_text.strip():
            parts.append({"m_type": "text", "m_content": fi_messenger.format_user_message(activity.message_author_name, activity.message_text)})
        parts.extend(activity.attachments)
        if not parts:
            return True  # empty message, keep capture, don't create task
        parts = fi_messenger.compact_message_parts(parts)

        try:
            await ckit_ask_model.thread_add_user_message(
                http,
                thread_cap.thread_fields.ft_id,
                parts,
                "fi_telegram",
                ftm_alt=100,
                user_preferences=json.dumps({"reopen_task_instruction": 1}),
            )
            return True
        except gql.transport.exceptions.TransportQueryError as e:
            logger.info("Telegram capture failed, uncapturing: %s", e)
            await ckit_ask_model.thread_app_capture_patch(http, thread_cap.thread_fields.ft_id, ft_app_searchable="")
            return False

    async def look_assistant_might_have_posted_something(self, msg: ckit_ask_model.FThreadMessageOutput) -> bool:
        if msg.ftm_role != "assistant" or not msg.ftm_content:
            return False

        if not (fthread := self.rcx.latest_threads.get(msg.ftm_belongs_to_ft_id)):
            return False
        if not (searchable := fthread.thread_fields.ft_app_searchable).startswith("telegram/"):
            return False

        last_ts = fi_messenger.get_last_posted_ts(fthread)
        if msg.ftm_created_ts <= last_ts:
            return False

        chat_id = int(searchable[len("telegram/"):])
        if not isinstance(msg.ftm_content, str):
            logger.warning("telegram handle_assistant_might_have_posted: ftm_content is not a string")
            return False
        if not self.tg_app:
            return False

        try:
            await self.tg_app.bot.send_message(chat_id=chat_id, text=msg.ftm_content)
        except Exception as e:
            logger.warning("Failed to post to Telegram chat %d: %s", chat_id, e)
            return False

        http = await self.fclient.use_http()
        await ckit_ask_model.thread_app_capture_patch(
            http,
            fthread.thread_fields.ft_id,
            ft_app_specific=json.dumps({"last_posted_assistant_ts": msg.ftm_created_ts}),
        )
        fthread.thread_fields.ft_app_specific = {"last_posted_assistant_ts": msg.ftm_created_ts}
        return True

    async def handle_emessage(self, emsg: ckit_bot_query.FExternalMessageOutput) -> None:
        # external message! FExternalMessageOutput(
        #  emsg_id='vgfz9BmBpa',
        #  emsg_persona_id='6gjySpynvG',
        #  emsg_type='TELEGRAM',
        #  emsg_from='telegram:14931503',
        #  emsg_to='telegram:8497987008',
        #  emsg_external_id='22',
        #  emsg_payload={'message': {'chat': {'id': 14931503, 'type': 'private', 'username': 'handle', 'first_name': 'Real Name'}, 'date': 1770975588, 'from': {'id': 14931503, 'is_bot': False, 'username': 'handle', 'first_name': 'Real Name', 'language_code': 'en'}, 'text': 'hello wrold', 'message_id': 22}, 'update_id': 257336450},
        #  emsg_created_ts=1770975590.564911,
        # ws_id='solarsystem')

        payload = emsg.emsg_payload if isinstance(emsg.emsg_payload, dict) else json.loads(emsg.emsg_payload)
        update = telegram.Update.de_json(payload, bot=None)   # Scary, strange types, date becomes datetime.datetime etc, but good for validation

        msg = update.message or update.edited_message
        if not msg or not msg.from_user:
            return
        if str(msg.message_id) in self._prev_messages:
            return
        self._prev_messages.append(str(msg.message_id))
        user = msg.from_user
        activity = ActivityTelegram(
            chat_id=msg.chat.id,
            chat_type=str(msg.chat.type),
            message_id=msg.message_id,
            message_text=msg.text or msg.caption or "",
            message_author_name=user.full_name or user.username or str(user.id),
            message_author_id=user.id,
            attachments=[],
        )
        posted = await self.post_into_captured_thread_as_user(activity)
        if self.activity_callback:
            await self.activity_callback(activity, posted)
