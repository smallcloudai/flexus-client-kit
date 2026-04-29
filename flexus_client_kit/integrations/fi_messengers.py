import json
import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional

import gql
import gql.transport.exceptions

from flexus_client_kit import ckit_ask_model, ckit_bot_exec, ckit_bot_query, ckit_cloudtool, ckit_kanban, ckit_scenario
from flexus_client_kit.integrations import fi_messenger

logger = logging.getLogger("fi_msgrs")


SUPPORTED_PLATFORMS = {"telegram"}   # XXX add slack, whatsapp, discord, magic_desk as they are migrated

EMSG_TYPE_TO_PLATFORM = {"TELEGRAM": "telegram"}


HELP = """flexus_messenger(op="capture", args={"platform": "telegram", "chat_id": 12345})
    Capture a chat. Their messages appear here, your responses are sent back automatically.

flexus_messenger(op="uncapture")
    Stop capturing this thread's chat. Do this when done.

flexus_messenger(op="post", args={"platform": "telegram", "chat_id": 12345, "text": "..."})
    One-off send without capture. Replies are not received here. Good for tests/reports.

flexus_messenger(op="status")
    Show all messenger connections and the active capture (if any) in this thread.
"""


FLEXUS_MESSENGER_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="flexus_messenger",
    description="Interact with messengers (telegram, ...). Call op=\"help\" for usage.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "capture | uncapture | post | status | help"},
            "args": {"type": "object", "description": "platform/chat_id/text depending on op"},
        },
    },
)


@dataclass
class ActivityMessenger:
    platform: str
    chat_id: str
    chat_type: str   # platform-native: "private"/"group"/"supergroup"/"channel" for telegram
    message_id: str
    text: str
    author_name: str
    author_id: str
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    mentions: List[Dict[str, Any]] = field(default_factory=list)


def parse_emessage(emsg: ckit_bot_query.FExternalMessageOutput) -> Optional[ActivityMessenger]:
    platform = EMSG_TYPE_TO_PLATFORM.get(emsg.emsg_type)
    if not platform:
        return None
    payload = emsg.emsg_payload if isinstance(emsg.emsg_payload, dict) else json.loads(emsg.emsg_payload)
    if not payload.get("mtm_text") and not payload.get("mtm_attachments"):
        return None
    return ActivityMessenger(
        platform=platform,
        chat_id=str(payload.get("mt_external_id", "")),
        chat_type=str(payload.get("mt_kind", "")),
        message_id=str(payload.get("mtm_external_id", "")),
        text=payload.get("mtm_text") or "",
        author_name=payload.get("mtm_author_label") or payload.get("mtm_author_id") or "",
        author_id=str(payload.get("mtm_author_id", "")),
        attachments=payload.get("mtm_attachments") or [],
        mentions=payload.get("mtm_mentions") or [],
    )


def ftm_to_mtm(platform: str, ftm: ckit_ask_model.FThreadMessageOutput) -> Optional[Dict[str, Any]]:
    if platform == "telegram":
        from flexus_client_kit.integrations import fi_telegram
        return fi_telegram.ftm_to_mtm(ftm)
    return None


def escape_text(platform: str, text: str) -> str:
    if platform == "telegram":
        from flexus_client_kit.integrations import fi_telegram
        return fi_telegram.tg_escape_md2(text)
    return text


def accept_outside_messages_only_to_expert(rcx: ckit_bot_exec.RobotContext, fexp_name: str) -> None:
    rcx.outside_messages_fexp_name = fexp_name


def is_bot_mentioned(rcx: ckit_bot_exec.RobotContext, a: ActivityMessenger) -> bool:
    if not a.mentions:
        return False
    if a.platform == "telegram":
        auth = rcx.external_auth.get("telegram") or {}
        bot_id, bot_un = str(auth.get("bot_id", "")), auth.get("bot_username", "")
    else:
        return False
    for m in a.mentions:
        if bot_id and str(m.get("id", "")) == bot_id:
            return True
        if bot_un and (m.get("username") or "").lower() == bot_un.lower():
            return True
    return False


async def inbound_activity_to_task(
    rcx: ckit_bot_exec.RobotContext,
    a: ActivityMessenger,
    already_posted: bool,
    extra_details: Optional[dict] = None,
    provenance: str = "",
    title: Optional[str] = None,
) -> None:
    logger.info("%s %s %s by %s: %s", rcx.persona.persona_id, a.platform, a.chat_type, a.author_name, a.text[:50])
    if already_posted:
        return
    fexp_name = getattr(rcx, "outside_messages_fexp_name", "")
    if not fexp_name:
        logger.warning("%s outside_messages_fexp_name not set, dropping inbound %s", rcx.persona.persona_id, a.platform)
        return
    details: Dict[str, Any] = {
        "platform": a.platform,
        "chat_id": a.chat_id,
        "chat_type": a.chat_type,
        "message_id": a.message_id,
        "text": a.text,
        "author_name": a.author_name,
        "author_id": a.author_id,
        "to_capture": f"flexus_messenger(op=\"capture\", args={{\"platform\": {a.platform!r}, \"chat_id\": {a.chat_id!r}}})",
    }
    if a.attachments:
        details["attachments"] = f"{len(a.attachments)} files attached"
    if extra_details:
        details.update(extra_details)
    if not title:
        title = f"{a.platform} {a.chat_type} user={a.author_name!r} chat_id={a.chat_id}\n{a.text}"
        if a.attachments:
            title += f"\n[{len(a.attachments)} file(s) attached]"
    into_inprogress = a.chat_type in ("private", "DM", "im") or is_bot_mentioned(rcx, a)
    post_fn = ckit_kanban.bot_kanban_post_into_inprogress if into_inprogress else ckit_kanban.bot_kanban_post_into_inbox
    await post_fn(
        await rcx.fclient.use_http_on_behalf(rcx.persona.persona_id, ""),
        rcx.persona.persona_id,
        title=title,
        human_id=f"{a.platform}:{a.chat_id}",
        details_json=json.dumps(details),
        provenance_message=provenance or f"{a.platform}_inbound",
        fexp_name=fexp_name,
    )


async def default_handle_emessage(rcx: ckit_bot_exec.RobotContext, emsg: ckit_bot_query.FExternalMessageOutput) -> None:
    a = parse_emessage(emsg)
    if not a:
        return
    http = await rcx.fclient.use_http_on_behalf(rcx.persona.persona_id, "")
    captured_ft_id = await ckit_ask_model.captured_thread_lookup(http, rcx.persona.persona_id, f"{a.platform}/{a.chat_id}")
    await inbound_activity_to_task(rcx, a, already_posted=bool(captured_ft_id))


async def messenger_outbound(rcx: ckit_bot_exec.RobotContext, ftm: ckit_ask_model.FThreadMessageOutput) -> bool:
    if ftm.ftm_role not in ("assistant", "user"):
        return False
    searchable = ftm.ft_app_searchable or ""
    if searchable.startswith("_uncaptured/"):
        return False
    if "/" not in searchable:
        return False
    platform, _, mt_external_id = searchable.partition("/")
    if platform not in SUPPORTED_PLATFORMS:
        return False
    if ftm.ftm_role == "user" and ((ftm.ftm_author_label1 or "").startswith(f"{platform}:") or ftm.ftm_author_label1 == "system"):
        return False
    mtm = ftm_to_mtm(platform, ftm)
    if not mtm:
        return False
    t = rcx.latest_threads.get(ftm.ftm_belongs_to_ft_id)
    app_specific = (t.thread_fields.ft_app_specific if t else None) or ftm.ft_app_specific or {}
    last_posted_ts = app_specific.get("last_posted_outbound_ts")
    if last_posted_ts is not None and ftm.ftm_created_ts <= last_posted_ts:
        return False
    http = await rcx.fclient.use_http_on_behalf(rcx.persona.persona_id, "")
    try:
        async with http as h:
            await h.execute(gql.gql("""
                mutation MessengerOutboundFromBot($ft_id: String!, $text: String!, $reply_to_external_id: String!, $from_ftm_alt: Int!, $from_ftm_num: Int!) {
                    messenger_thread_post(ft_id: $ft_id, text: $text, reply_to_external_id: $reply_to_external_id, from_ftm_alt: $from_ftm_alt, from_ftm_num: $from_ftm_num)
                }"""),
                variable_values={
                    "ft_id": ftm.ftm_belongs_to_ft_id,
                    "text": mtm.get("text", ""),
                    "reply_to_external_id": mtm.get("reply_to", ""),
                    "from_ftm_alt": ftm.ftm_alt if ftm.ftm_role == "user" else 0,
                    "from_ftm_num": ftm.ftm_num if ftm.ftm_role == "user" else 0,
                },
            )
    except gql.transport.exceptions.TransportQueryError as e:
        logger.warning("messenger_outbound %s mt_external_id=%s failed: %s", platform, mt_external_id, e)
        return False
    await ckit_ask_model.thread_app_capture_patch(http, ftm.ftm_belongs_to_ft_id, ft_app_specific=json.dumps({
        **app_specific, "last_posted_outbound_ts": ftm.ftm_created_ts,
    }))
    return True


async def flexus_messenger_called_by_model(
    rcx: ckit_bot_exec.RobotContext,
    toolcall: ckit_cloudtool.FCloudtoolCall,
    model_args: Optional[Dict[str, Any]],
) -> str:
    if not model_args:
        return HELP
    if rcx.running_test_scenario:
        return await ckit_scenario.scenario_generate_tool_result_via_model(rcx.fclient, toolcall, open(__file__).read())
    args, args_error = ckit_cloudtool.sanitize_args(model_args)
    if args_error:
        return args_error
    op = model_args.get("op", "help") or "help"
    if op == "help":
        return HELP
    inner = model_args.get("args", {}) or {}

    if op == "uncapture":
        http = await rcx.fclient.use_http_on_behalf(rcx.persona.persona_id, toolcall.fcall_untrusted_key)
        try:
            async with http as h:
                await h.execute(gql.gql("""
                    mutation MessengerThreadUncaptureFromBot($ft_id: String!) {
                        messenger_thread_uncapture(ft_id: $ft_id)
                    }"""),
                    variable_values={"ft_id": toolcall.fcall_ft_id},
                )
        except gql.transport.exceptions.TransportQueryError as e:
            return f"uncapture failed: {e}\n"
        return fi_messenger.UNCAPTURE_SUCCESS_MSG

    if op == "status":
        # XXX backend mutation: messenger_status(persona_id, ft_id) — all connections + capture in this thread
        return "XXX backend mutation messenger_status not implemented yet\n"

    platform = ckit_cloudtool.try_best_to_find_argument(inner, model_args, "platform", "")
    if platform not in SUPPORTED_PLATFORMS:
        return f"unknown or missing platform {platform!r}; supported: {sorted(SUPPORTED_PLATFORMS)}\n"

    if op == "capture":
        fexp_name = getattr(rcx, "outside_messages_fexp_name", "")
        if fexp_name and not toolcall.fcall_fexp_name.endswith("_" + fexp_name):
            return f"This expert is not suitable to capture outside chats. Hand over to expert {fexp_name!r} instead.\n"
        chat_id = ckit_cloudtool.try_best_to_find_argument(inner, model_args, "chat_id", None)
        if chat_id is None:
            return "Missing chat_id (find it in the inbound kanban task details)\n"
        mt_external_id = str(chat_id)
        mt_platform = platform.upper()
        http = await rcx.fclient.use_http_on_behalf(rcx.persona.persona_id, toolcall.fcall_untrusted_key)
        try:
            async with http as h:
                await h.execute(gql.gql("""
                    mutation MessengerThreadCaptureFromBot($ft_id: String!, $mt_platform: String!, $mt_external_id: String!) {
                        messenger_thread_capture(ft_id: $ft_id, mt_platform: $mt_platform, mt_external_id: $mt_external_id)
                    }"""),
                    variable_values={
                        "ft_id": toolcall.fcall_ft_id,
                        "mt_platform": mt_platform,
                        "mt_external_id": mt_external_id,
                    },
                )
        except gql.transport.exceptions.TransportQueryError as e:
            return f"capture failed: {e}\n"
        return (fi_messenger.CAPTURE_SUCCESS_MSG % f"{platform} chat_id={chat_id}") + "\n" + fi_messenger.CAPTURE_ADVICE_MSG

    if op == "post":
        chat_id = ckit_cloudtool.try_best_to_find_argument(inner, model_args, "chat_id", None)
        text = ckit_cloudtool.try_best_to_find_argument(inner, model_args, "text", "")
        if chat_id is None or not text:
            return "Missing chat_id or text\n"
        http = await rcx.fclient.use_http_on_behalf(rcx.persona.persona_id, toolcall.fcall_untrusted_key)
        try:
            async with http as h:
                await h.execute(gql.gql("""
                    mutation MessengerOnlyPostFromBot($ft_id: String!, $mt_platform: String!, $mt_external_id: String!, $text: String!) {
                        messenger_only_post(ft_id: $ft_id, mt_platform: $mt_platform, mt_external_id: $mt_external_id, text: $text)
                    }"""),
                    variable_values={
                        "ft_id": toolcall.fcall_ft_id,
                        "mt_platform": platform.upper(),
                        "mt_external_id": str(chat_id),
                        "text": escape_text(platform, text),
                    },
                )
        except gql.transport.exceptions.TransportQueryError as e:
            return f"post failed: {e}\n"
        return f"posted to {platform} chat_id={chat_id}\n"

    return fi_messenger.UNKNOWN_OPERATION_MSG % op
