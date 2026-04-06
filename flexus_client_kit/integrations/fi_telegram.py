import asyncio
import re
import json
import logging
import gql

from collections import deque
from dataclasses import asdict, dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional

import telegram
import telegram.ext

from flexus_client_kit import ckit_ask_model, ckit_bot_exec, ckit_bot_query, ckit_client, ckit_cloudtool, ckit_kanban, ckit_scenario, gql_utils
from flexus_client_kit.format_utils import format_cat_output
from flexus_client_kit.integrations import fi_messenger

logger = logging.getLogger("teleg")


# Testing telegram with webhook on localhost:
#
# Install ngrok: https://ngrok.com/download
# ngrok http 8008
# => copy the https://xxx.ngrok-free.app URL
#
# In backend console:
# export WEBHOOK_BASE_URL="https://xxx.ngrok-free.app"
# => reconnect Telegram in Integrations to register the webhook


# Capturing mechanics:
# private message(s) from user => bot python code creates kanban tasks in inbox =>
# scheduler runs SCHED_TASK_SORT_10M => one or several tasks joined go into kanban todo column =>
# scheduler runs SCHED_TODO_5M => bot activates, runs telegram(op=capture) => talks to human directly =>
# human is happy => scheduler hits fexp_inactivity_timeout => bot moves task to kanban done and summarizes
# the conversation.


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

telegram(op="uncapture")
    Stop capturing this Telegram chat. Do this at the end when you're done talking.

telegram(op="post", args={"chat_id": 123456789, "text": "Hello!"})
    Post a message to a Telegram chat. Don't use this for captured chats. Remember to use MarkdownV2 markup.
"""
# Unclear why is this useful, commeted out for now:
# telegram(op="generate_chat_link", args={"contact_id": "abc123"})
#     Generate a link that opens a chat with this bot and passes the contact_id.
#     When clicked, bot receives /start c_<contact_id>.

# https://core.telegram.org/bots/api#formatting-options
TG_MARKUP_HELP = """
Telegram uses MarkdownV2 markup:

*bold*  _italic_  __underline__  ~strikethrough~
`inline code`
```python
code block
```
[link text](https://example.com)
||spoiler||

> blockquote
> each line must start with >

No bullet lists or tables.
"""

HELP += TG_MARKUP_HELP

_TG_MD2_SPECIAL = re.compile(r"([_*\[\]()~`>#+\-=|{}.!\\<>])")
_TG_MD2_CODE_ESCAPE = re.compile(r"([`\\])")
_TG_MD2_LINK_URL_ESCAPE = re.compile(r"([)\\])")
_TG_MD2_MARKUP = re.compile(
    r"(?sm)"
    r"```.*?```"             # code blocks
    r"|`[^`]+`"              # inline code
    r"|\*[^*\n]+\*"          # bold (no newline crossing)
    r"|(?<!\w)__[^_\n]+__(?!\w)"  # underline (word-boundary, before italic)
    r"|(?<!\w)_[^_\n]+_(?!\w)"    # italic (word-boundary, like Telegram's parser)
    r"|~[^~\n]+~"            # strikethrough
    r"|\|\|[^|\n]+\|\|"     # spoiler
    r"|\[[^\]]+\]\([^)]*(?:\([^)]*\)[^)]*)*\)"  # links (supports one level of parens in URL)
    r"|^>[^\n]*"             # blockquote lines (only at line start)
)


def _escape_markup_match(m: re.Match) -> str:
    s = m.group(0)
    if s.startswith("```"):
        inner = s[3:-3]
        return "```" + _TG_MD2_CODE_ESCAPE.sub(r"\\\1", inner) + "```"
    if s.startswith("`"):
        inner = s[1:-1]
        return "`" + _TG_MD2_CODE_ESCAPE.sub(r"\\\1", inner) + "`"
    if s.startswith("["):
        # [text](url) — escape special chars in text, escape ) and \ in url
        bracket_end = s.index("](")
        text_part = s[1:bracket_end]
        url_part = s[bracket_end+2:-1]
        return "[" + _TG_MD2_SPECIAL.sub(r"\\\1", text_part) + "](" + _TG_MD2_LINK_URL_ESCAPE.sub(r"\\\1", url_part) + ")"
    if s.startswith(">"):
        return ">" + _TG_MD2_SPECIAL.sub(r"\\\1", s[1:])
    # bold, italic, underline, strikethrough, spoiler: escape special chars in inner text
    for delim in ("__", "||", "*", "_", "~"):
        if s.startswith(delim) and s.endswith(delim) and len(s) > 2 * len(delim):
            inner = s[len(delim):-len(delim)]
            return delim + _TG_MD2_SPECIAL.sub(r"\\\1", inner) + delim
    return s


def tg_escape_md2(text: str) -> str:
    parts = []
    last = 0
    for m in _TG_MD2_MARKUP.finditer(text):
        if m.start() > last:
            parts.append(_TG_MD2_SPECIAL.sub(r"\\\1", text[last:m.start()]))
        parts.append(_escape_markup_match(m))
        last = m.end()
    if last < len(text):
        parts.append(_TG_MD2_SPECIAL.sub(r"\\\1", text[last:]))
    return "".join(parts)


@dataclass
class ActivityTelegram:
    chat_id: int
    chat_type: str  # "private", "group", "supergroup", "channel"
    message_id: int
    message_text: str
    message_author_name: str
    message_author_id: int
    attachments: List[Dict[str, str]] = field(default_factory=list)


class IntegrationTelegram(fi_messenger.FlexusMessenger):
    platform_name = "telegram"
    emessage_type = "TELEGRAM"

    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx: ckit_bot_exec.RobotContext,
    ):
        super().__init__(fclient, rcx)
        self.is_fake = rcx.running_test_scenario
        tg_auth = rcx.external_auth.get("telegram") or {}
        self.bot_token = tg_auth.get("api_key", "").strip()
        self.webhook_secret = tg_auth.get("webhook_secret", "")
        self.webhook_error = tg_auth.get("webhook_error", "")
        self.problems_accumulator: List[str] = []
        if self.webhook_error:
            self.oops_a_problem(f"Telegram webhook error on connect: {self.webhook_error} — reconnect Telegram in Integrations to fix")

        self.tg_app: Optional[telegram.ext.Application] = None

        self._activity_callback: Callable[[ActivityTelegram, bool], Awaitable[None]] = self.inbound_activity_to_task
        # See fi_slack.py for explanation of deque+set dedup pattern
        self._from_tg_dedup = deque(maxlen=50000)
        self._from_tg_dedup_set = set()
        self._to_tg_dedup = deque(maxlen=50000)
        self._to_tg_dedup_set = set()

        if not self.bot_token:
            self.oops_a_problem("Telegram is not connected, ask user to connect it in bot Integrations", dont_print=True)
            return

        if ":" not in self.bot_token:
            self.oops_a_problem("Telegram api_key should have format bot_id:SECRET_KEY")

        try:
            self.tg_app = telegram.ext.Application.builder().token(self.bot_token).build()
        except ImportError:
            self.oops_a_problem("python-telegram-bot not installed")
        except Exception as e:
            logger.exception("Failed to initialize Telegram bot")
            self.oops_a_problem(f"{type(e).__name__}: {e}")

    def oops_a_problem(self, text: str, dont_print: bool =False) -> None:
        if not dont_print:
            logger.info("%s telegram problem: %s", self.rcx.persona.persona_id, text)
        self.problems_accumulator.append(text)

    async def initialize(self) -> None:
        if self.webhook_error or not self.tg_app:
            return
        try:
            await self.tg_app.initialize()
            logger.info("%s telegram bot %s initialized", self.rcx.persona.persona_id, self.bot_token.split(":")[0])
        except Exception as e:
            logger.exception("%s telegram failed to initialize", self.rcx.persona.persona_id)
            self.oops_a_problem(f"initialize: {type(e).__name__}: {e}")

    async def close(self) -> None:
        if self.tg_app and self.tg_app.running:
            try:
                await self.tg_app.stop()
                await self.tg_app.shutdown()
                self.tg_app = None
            except Exception:
                logger.exception("%s telegram failed to close", self.rcx.persona.persona_id)

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        if not model_produced_args:
            return HELP

        op = model_produced_args.get("op", "")
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        if self.is_fake:
            return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())

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

            this_thread = self.rcx.latest_threads.get(toolcall.fcall_ft_id)
            if this_thread and (this_thread.thread_fields.ft_app_searchable or "").startswith("telegram/"):
                return "Cannot post to captured chat. Your responses are sent automatically.\n"

            http = await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, toolcall.fcall_untrusted_key)
            capturing_ft_id = await ckit_ask_model.captured_thread_lookup(
                http, self.rcx.persona.persona_id, f"telegram/{chat_id}",
            )
            if capturing_ft_id == toolcall.fcall_ft_id:
                return "Cannot post to captured chat. Your responses are sent automatically.\n"
            if capturing_ft_id:
                logger.warning("telegram post blocked: target telegram/%s already captured by ft_id=%s, this ft_id=%s, persona=%s",
                    chat_id, capturing_ft_id, toolcall.fcall_ft_id, self.rcx.persona.persona_id)
                return "This chat is already captured in another thread.\n"

            try:
                await self.tg_app.bot.send_message(chat_id=int(chat_id), text=tg_escape_md2(text), parse_mode="MarkdownV2")
                return "Post success\n"
            except Exception as e:
                return f"ERROR: {type(e).__name__}: {e}\n"

        if op == "capture":
            if self.outside_messages_fexp_name and not toolcall.fcall_fexp_name.endswith("_" + self.outside_messages_fexp_name):
                return fi_messenger.CAPTURE_WRONG_EXPERT_MSG % self.outside_messages_fexp_name
            chat_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "chat_id", None)
            if not chat_id:
                return "Missing chat_id parameter\n"

            identifier = str(chat_id)
            http = await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, toolcall.fcall_untrusted_key)
            searchable = f"telegram/{identifier}"
            try:
                await ckit_ask_model.thread_app_capture_patch(
                    http,
                    toolcall.fcall_ft_id,
                    ft_app_searchable=searchable,
                    ft_app_specific=json.dumps({"last_posted_assistant_ts": toolcall.fcall_created_ts}),
                )
            except gql.transport.exceptions.TransportQueryError as e:
                return ckit_cloudtool.gql_error_4xx_to_model_reraise_5xx(e, "telegram_capture")
            return fi_messenger.CAPTURE_SUCCESS_MSG % identifier + fi_messenger.CAPTURE_ADVICE_MSG + "\n" + \
                "Reminder: after this point telegram MarkdownV2 markup rules are in effect for your output, there are no tables! Here's markup help for you again.\n\n" + \
                TG_MARKUP_HELP

        if op == "uncapture":
            http = await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, toolcall.fcall_untrusted_key)
            await ckit_ask_model.thread_app_capture_patch(http, toolcall.fcall_ft_id, ft_app_searchable="")
            if fthread := self.rcx.latest_threads.get(toolcall.fcall_ft_id):
                fthread.thread_fields.ft_app_searchable = ""
            return fi_messenger.UNCAPTURE_SUCCESS_MSG

        # if op == "generate_chat_link":
        #     contact_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "contact_id", None)
        #     if not contact_id:
        #         return "Missing contact_id parameter\n"
        #     try:
        #         bot_info = await self.tg_app.bot.get_me()
        #         return f"https://t.me/{bot_info.username}?start=c_{contact_id}\n"
        #     except Exception as e:
        #         return f"ERROR: {type(e).__name__}: {e}\n"

        return fi_messenger.UNKNOWN_OPERATION_MSG % op

    async def handle_emessage(self, emsg: ckit_bot_query.FExternalMessageOutput) -> None:
        # external message FExternalMessageOutput(
        #  emsg_id='vgfz9BmBpa',
        #  emsg_persona_id='6gjySpynvG',
        #  emsg_type='TELEGRAM',
        #  emsg_from='telegram:14931503',
        #  emsg_to='telegram:8497987008',
        #  emsg_external_id='22',
        #  emsg_payload={'message': {'chat': {'id': 14931503, 'type': 'private', 'username': 'handle', 'first_name': 'Real Name'}, 'date': 1770975588, 'from': {'id': 14931503, 'is_bot': False, 'username': 'handle', 'first_name': 'Real Name', 'language_code': 'en'}, 'text': 'hello wrold', 'message_id': 22}, 'update_id': 257336450},
        #  emsg_created_ts=1770975590.564911,
        #  ws_id='solarsystem')

        payload = emsg.emsg_payload
        update = telegram.Update.de_json(payload, bot=None)   # Scary, strange types, date becomes datetime.datetime etc, but good for validation

        msg = update.message or update.edited_message
        if not msg or not msg.from_user:
            return
        dedup_key = str(msg.message_id)
        if dedup_key in self._from_tg_dedup_set:
            return
        if len(self._from_tg_dedup) == self._from_tg_dedup.maxlen:
            self._from_tg_dedup_set.discard(self._from_tg_dedup[0])
        self._from_tg_dedup.append(dedup_key)
        self._from_tg_dedup_set.add(dedup_key)
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
        already_posted_to_captured_thread = await self.post_into_captured_thread_as_user(activity)
        await self._activity_callback(activity, already_posted_to_captured_thread)

    def on_incoming_activity(self, handler: Callable[[ActivityTelegram, bool], Awaitable[None]]):
        self._activity_callback = handler
        return handler

    async def inbound_activity_to_task(self, a: ActivityTelegram, already_posted: bool, extra_details: dict = None, provenance: str = None, title: str = None):
        logger.info("%s Telegram %s by @%s: %s", self.rcx.persona.persona_id, a.chat_type, a.message_author_name, a.message_text[:50])
        if already_posted:
            return
        details = asdict(a)
        details["to_capture"] = "telegram(op=\"capture\", args={\"chat_id\": %r})" % a.chat_id
        if a.attachments:
            details["attachments"] = f"{len(a.attachments)} files attached"
        if extra_details:
            details.update(extra_details)
        if not title:
            title = "Telegram %s user=%r chat_id=%d\n%s" % (a.chat_type, a.message_author_name, a.chat_id, a.message_text)
            if a.attachments:
                title += f"\n[{len(a.attachments)} file(s) attached]"
        human_id = "telegram:%d" % a.chat_id
        post_fn = ckit_kanban.bot_kanban_post_into_inprogress if a.chat_type == "private" else ckit_kanban.bot_kanban_post_into_inbox
        await post_fn(
            await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, ""),
            self.rcx.persona.persona_id,
            title=title,
            human_id=human_id,
            details_json=json.dumps(details),
            provenance_message=provenance or "telegram_inbound",
            fexp_name=self.outside_messages_fexp_name,
        )

    async def post_into_captured_thread_as_user(self, activity: ActivityTelegram) -> bool:
        msg_text = activity.message_text
        if not msg_text.strip():
            return True  # empty message, keep capture, do nothing
        # parts.append({"m_type": "text", "m_content": f"👤{activity.message_author_name}\n\n{activity.message_text}"})
        # parts: List[Dict[str, str]] = []
        # parts.extend(activity.attachments)
        # parts = fi_messenger.compact_message_parts(parts)
        searchable = f"telegram/{activity.chat_id}"
        content = [{"m_type": "text", "m_content": f"👤{activity.message_author_name}\n\n{msg_text}"}]
        http = await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, "")
        logger.info("captured_thread_post searchable=%s msg=%s", searchable, msg_text[:200])
        ft_id = await ckit_ask_model.captured_thread_post_user_message(
            http,
            self.rcx.persona.persona_id,
            searchable,
            content,
            only_to_expert=self.outside_messages_fexp_name,
            thread_too_old_s=3600,
        )
        if not ft_id:
            return False
        logger.info("%s telegram inbound captured ft_id=%s type=%s chat_id=%s msg_id=%s from %r (uid=%s): %s",
            self.rcx.persona.persona_id, ft_id,
            activity.chat_type, activity.chat_id, activity.message_id,
            activity.message_author_name, activity.message_author_id, msg_text[:120] or "(empty)")
        return True

    async def look_assistant_might_have_posted_something(self, msg: ckit_ask_model.FThreadMessageOutput) -> bool:
        if msg.ftm_role != "assistant" or not msg.ftm_content:
            return False

        searchable = msg.ft_app_searchable or ""
        if not searchable.startswith("telegram/"):
            return False

        app_specific = msg.ft_app_specific
        # XXX do we really need it?
        if app_specific is None:
            t = self.rcx.latest_threads.get(msg.ftm_belongs_to_ft_id)
            if t:
                app_specific = t.thread_fields.ft_app_specific
        last_posted_ts = (app_specific or {}).get("last_posted_assistant_ts")
        if last_posted_ts is None:
            logger.warning("tg dedup: no last_posted_assistant_ts ft=%s ft_app_specific=%r", msg.ftm_belongs_to_ft_id, app_specific)
        elif msg.ftm_created_ts <= last_posted_ts:
            return False

        dedup_key = "%s:%03d:%03d" % (msg.ftm_belongs_to_ft_id, msg.ftm_alt, msg.ftm_num)
        if dedup_key in self._to_tg_dedup_set:
            return False

        chat_id = int(searchable[len("telegram/"):])
        if not isinstance(msg.ftm_content, str):
            logger.warning("telegram look_assistant_might_have_posted_something: ftm_content is not a string: %r" % msg.ftm_content)
            return False
        if not self.tg_app:
            return False

        text = msg.ftm_content
        if "TASK_COMPLETED" in text and len(text) <= len("TASK_COMPLETED") + 6:
            logger.info("telegram look_assistant_might_have_posted_something: ftm_content has TASK_COMPLETED, not posting to the captured chat")
            return False
        text = text.replace("TASK_COMPLETED", "")   # yes, sometimes the model writes it anyway

        try:
            await self.tg_app.bot.send_message(chat_id=chat_id, text=tg_escape_md2(text), parse_mode="MarkdownV2")
            if len(self._to_tg_dedup) == self._to_tg_dedup.maxlen:
                self._to_tg_dedup_set.discard(self._to_tg_dedup[0])
            self._to_tg_dedup.append(dedup_key)
            self._to_tg_dedup_set.add(dedup_key)
        except Exception as e:
            logger.warning("Failed to post to Telegram chat %d: %s\n%s", chat_id, e, text)
            return False

        http = await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, "")
        await ckit_ask_model.thread_app_capture_patch(
            http,
            msg.ftm_belongs_to_ft_id,
            ft_app_specific=json.dumps({"last_posted_assistant_ts": msg.ftm_created_ts}),
        )
        return True

    # -- Additional stuff --
    # How to handle images

    # async def _extract_attachments(self, msg: telegram.Message) -> List[Dict[str, str]]:
    #     items: List[Dict[str, str]] = []
    #     photo = msg.photo[-1] if msg.photo else None
    #     doc = msg.document

    #     if photo:
    #         try:
    #             file = await photo.get_file()
    #             data = await file.download_as_bytearray()
    #             img_part = self._process_image(bytes(data))
    #             if img_part:
    #                 items.append(img_part)
    #         except Exception as e:
    #             logger.warning("Failed to download photo: %s", e)

    #     if doc:
    #         try:
    #             file = await doc.get_file()
    #             data = await file.download_as_bytearray()
    #             if doc.mime_type and doc.mime_type.startswith("image/"):
    #                 img_part = self._process_image(bytes(data))
    #                 if img_part:
    #                     items.append(img_part)
    #             elif fi_messenger.is_text_file(bytes(data)):
    #                 formatted = format_cat_output(doc.file_name or "file", bytes(data), safety_valve="10k")
    #                 items.append({"m_type": "text", "m_content": f"📎 {formatted}"})
    #             else:
    #                 items.append({"m_type": "text", "m_content": f"[Binary file: {doc.file_name} ({len(data)} bytes)]"})
    #         except Exception as e:
    #             logger.warning("Failed to download document: %s", e)

    #     return items

    # def _process_image(self, data: bytes) -> Optional[Dict[str, str]]:
    #     try:
    #         img = Image.open(io.BytesIO(data))
    #         img.thumbnail((600, 600), Image.Resampling.LANCZOS)
    #         buf = io.BytesIO()
    #         if img.mode == "RGBA":
    #             img = img.convert("RGB")
    #         img.save(buf, format="JPEG", quality=80, optimize=True)
    #         buf.seek(0)
    #         return {"m_type": "image/jpeg", "m_content": base64.b64encode(buf.read()).decode("utf-8")}
    #     except Exception:
    #         logger.exception("Failed to process image")
    #         return None


if __name__ == "__main__":
    import os

    bot_token = os.environ["TELEG_TEST_BOT"]
    chat_id = os.environ["TELEG_TEST_CHAT"]

    test_msg = r"""Hello! This is a *bold* test message. Here's _italic_ and ~strikethrough~ too.

Some tricky chars: prices are $9.99 (USD) and $12.50 - not bad! Version 2.0 is out.

HTML example: <div class="container"> is not a tag here.
Ampersand: Tom & Jerry. Less than: 5 < 10. Greater: 10 > 5.

```sql
SELECT u.name, COUNT(*) AS total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.created_at > '2025-01-01'
GROUP BY u.name
HAVING COUNT(*) >= 3;
```

Inline code: `print("hello world!")` works fine.

A [link to Google](https://www.google.com) and some ||spoiler text|| here.

*bold with - dashes and $prices!* and _italic (with parens) - also tricky_ and ~strike - through~

>This is a blockquote
>with multiple lines

List of things:
- item one
- item two (with parens)
- item #3!
"""

    test_msg_hard = r"""Edge cases for MarkdownV2 escaping:

Lone special chars: price is $9.99 and 50% off! Also: 2+2=4, x<y>z, a|b, {braces}, #hashtag.

Backslashes already in text: C:\Users\name\file.txt and \\server\share

Empty delimiters that are NOT markup: ** ~~ __ || just double chars hanging out.

Unmatched stars: one * in the middle * of text (not bold, spaces around).

Adjacent markup no gap: *bold1**bold2* and _italic1__italic2_

Markup with every special char inside: *hello (world) [brackets] {curly} $dollar #hash +plus =equals -dash .dot !bang ~tilde |pipe > < \backslash*

_italic with $price! and (parens) and [square]_

~strike with 100% and #tag~

||spoiler with (parens) and $money!||

Links with nasty URLs: [click (here)!](https://example.com/path?a=1&b=2#frag)
[another link](https://example.com/foo(bar))

Code with markup chars: `*bold* _italic_ ~strike~` should stay literal.

```
code block with * and _ and ~ and | and $ and () and [] and {} and # and + and = and . and ! and > and < and \
also ` backtick inside
```

>blockquote with *bold markup* and $price and (parens)
>second line with [brackets] and {curly} and #hash

Multiple blockquotes separated:
>first block
regular text between
>second block

Underscore snake_case_variable should not become italic. Same with __dunder_method__.

Stars in math: 2*3*4 and a*b (not bold because no matching).

Pipes in tables: col1 | col2 | col3

Exclamation! Period. Hash# Plus+ Equals= Dash- all at word boundaries.

Mixed line: I paid $9.99 (USD) for *premium* at https://example.com — worth it!

Trailing special chars at EOF: test!"""

    test_msg_ru = r"""Русский текст с особыми символами:

Цена: 9.99$ (включая НДС 20%) — выгодно! А ещё: 2+2=4, x<y>z, a|b, {скобки}, #хештег.

Путь к файлу: C:\Users\Вася\документы\отчёт.txt и \\сервер\папка

Пустые разделители: ** ~~ __ || просто двойные символы.

Одинокие звёздочки: одна * посреди текста * не жирный (пробелы вокруг).

*Жирный текст с (скобками), [квадратными] и {фигурными} — всё внутри!*

_Курсив с ценой 9.99$ и (скобками) и [квадратными]_

~Зачёркнутый с 100% и #тегом~

||Спойлер: убийца — дворецкий! Цена $99.99 (шок)||

Ссылки: [нажми (сюда)!](https://example.com/path?a=1&b=2#фрагмент)
[ещё ссылка](https://ru.wikipedia.org/wiki/Кот_(значения))

Код: `*жирный* _курсив_ ~зачёркнутый~` — литерал.

```
блок кода: * и _ и ~ и | и $ и () и [] и {} и # и + и = и . и ! и > и < и \
также ` обратная кавычка
```

>цитата с *жирным* и $ценой и (скобками)
>вторая строка [квадратные] и {фигурные} и #хеш

Несколько цитат:
>первый блок
обычный текст между
>второй блок

Переменные: snake_case_переменная и __dunder_метод__ не должны стать курсивом.

Математика: 2*3*4 и a*b (не жирный).

Таблицы: кол1 | кол2 | кол3

Смешанная строка: я заплатил $9.99 (USD) за *премиум* на https://example.com — оно того стоит!

Эмодзи и спецсимволы: 🎉 Привет! 👋 (тест) [тест] {тест} #тест +тест =тест -тест .тест !тест ~тест |тест >тест <тест \тест

Конец с восклицанием!"""

    async def _test():
        app = telegram.ext.Application.builder().token(bot_token).build()
        await app.initialize()
        for label, msg in [("original", test_msg), ("hard", test_msg_hard), ("russian", test_msg_ru)]:
            escaped = tg_escape_md2(msg)
            print(f"--- {label} escaped ---")
            print(escaped)
            print(f"--- sending {label} ---")
            try:
                await app.bot.send_message(chat_id=int(chat_id), text=escaped, parse_mode="MarkdownV2")
                print(f"{label}: ok!")
            except telegram.error.BadRequest as e:
                print(f"{label}: FAILED: {e}")

    asyncio.run(_test())
