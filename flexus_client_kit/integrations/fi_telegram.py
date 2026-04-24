import asyncio
import re
import json
import logging
import gql

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
    auth_required="telegram",
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

telegram(op="capture", args={"chat_id": 12345})
    Capture a Telegram chat. Messages will appear here and your responses will be sent back.
    chat_id is from the inbound kanban task details.

telegram(op="uncapture")
    Stop capturing this Telegram chat. Do this at the end when you're done talking.
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
        self._processing_mtm_keys: set[tuple[str, str]] = set()

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

        if op == "capture":
            if self.outside_messages_fexp_name and not toolcall.fcall_fexp_name.endswith("_" + self.outside_messages_fexp_name):
                return fi_messenger.CAPTURE_WRONG_EXPERT_MSG % self.outside_messages_fexp_name
            chat_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "chat_id", None)
            try:
                chat_id = int(chat_id) if chat_id is not None else None
            except (TypeError, ValueError):
                chat_id = None
            if chat_id is None:
                return "Missing chat_id parameter (find it in the inbound kanban task details)\n"
            # Telegram: positive chat_id = DM (needs bot_id prefix to disambiguate same user across bots), negative = group.
            bot_id = self.bot_token.split(":", 1)[0]
            mt_external_id = f"{bot_id}/{chat_id}" if chat_id > 0 else str(chat_id)
            http = await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, toolcall.fcall_untrusted_key)
            searchable = f"telegram/{mt_external_id}"
            try:
                await ckit_ask_model.thread_app_capture_patch(
                    http,
                    toolcall.fcall_ft_id,
                    ft_app_searchable=searchable,
                    ft_app_specific=json.dumps({"last_posted_assistant_ts": toolcall.fcall_created_ts, "mt_external_id": mt_external_id}),
                )
            except gql.transport.exceptions.TransportQueryError as e:
                return ckit_cloudtool.gql_error_4xx_to_model_reraise_5xx(e, "telegram_capture")
            return fi_messenger.CAPTURE_SUCCESS_MSG % mt_external_id + fi_messenger.CAPTURE_ADVICE_MSG + "\n" + \
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

    def on_incoming_activity(self, handler: Callable[[ActivityTelegram, bool], Awaitable[None]]):
        self._activity_callback = handler
        return handler

    async def handle_messenger_msg(
        self,
        action: str,
        old: Optional[ckit_bot_query.FMessengerThreadMessageOutput],
        new: Optional[ckit_bot_query.FMessengerThreadMessageOutput],
    ) -> None:
        if action not in ("INSERT", "UPDATE") or not new:
            return
        mtm = new
        if mtm.mt_platform != "TELEGRAM":
            return
        mtm_key = (mtm.mtm_belongs_to_mt_id, mtm.mtm_external_id)
        if mtm_key in self._processing_mtm_keys:
            return
        self._processing_mtm_keys.add(mtm_key)
        try:
            # mt_external_id is "{bot_id}/{chat_id}" for DM, "{chat_id}" for group.
            raw = mtm.mt_external_id
            chat_id_str = raw.split("/", 1)[1] if "/" in raw else raw
            try:
                chat_id = int(chat_id_str)
            except ValueError:
                chat_id = 0
            try:
                message_id = int(mtm.mtm_external_id)
            except ValueError:
                message_id = 0
            activity = ActivityTelegram(
                chat_id=chat_id,
                chat_type="private" if mtm.mt_kind == "DM" else "group",
                message_id=message_id,
                message_text=mtm.mtm_text or "",
                message_author_name=mtm.mtm_author_label or mtm.mtm_author_id,
                message_author_id=int(mtm.mtm_author_id) if mtm.mtm_author_id.isdigit() else 0,
                attachments=mtm.mtm_attachments if isinstance(mtm.mtm_attachments, list) else [],
            )
            http = await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, "")
            captured_ft_id = await ckit_ask_model.captured_thread_lookup(http, self.rcx.persona.persona_id, f"telegram/{mtm.mt_external_id}")
            if self._activity_callback is self.inbound_activity_to_task:
                await self.inbound_activity_to_task(activity, already_posted=bool(captured_ft_id), extra_details={"mt_external_id": mtm.mt_external_id})
            else:
                await self._activity_callback(activity, bool(captured_ft_id))
        finally:
            self._processing_mtm_keys.discard(mtm_key)

    async def inbound_activity_to_task(self, a: ActivityTelegram, already_posted: bool, extra_details: dict = None, provenance: str = None, title: str = None):
        logger.info("%s Telegram %s by @%s: %s", self.rcx.persona.persona_id, a.chat_type, a.message_author_name, a.message_text[:50])
        if already_posted:
            return
        details = asdict(a)
        details["to_capture"] = "telegram(op=\"capture\", args={\"chat_id\": %d})" % a.chat_id
        if a.attachments:
            details["attachments"] = f"{len(a.attachments)} files attached"
        if extra_details:
            details.update(extra_details)
        if not title:
            title = "Telegram %s user=%r chat_id=%d\n%s" % (a.chat_type, a.message_author_name, a.chat_id, a.message_text)
            if a.attachments:
                title += f"\n[{len(a.attachments)} file(s) attached]"
        human_id = "telegram:%d" % a.chat_id
        if not self.outside_messages_fexp_name:
            logger.warning("%s accept_outside_messages_only_to_expert() was never called, don't know which expert to use", self.rcx.persona.persona_id)
            return
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

    async def look_assistant_might_have_posted_something(self, msg: ckit_ask_model.FThreadMessageOutput) -> bool:
        return False

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
