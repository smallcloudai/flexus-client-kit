import asyncio
import json
import logging
import re
import time
from dataclasses import asdict
from datetime import datetime
from typing import Dict, Any, List
from zoneinfo import ZoneInfo

from pymongo import AsyncMongoClient

from flexus_client_kit.core import ckit_client
from flexus_client_kit.core import ckit_cloudtool
from flexus_client_kit.core import ckit_bot_exec
from flexus_client_kit.core import ckit_kanban
from flexus_client_kit.core import ckit_shutdown
from flexus_client_kit.core import ckit_mongo
from flexus_client_kit.integrations.providers.inbound_webhooks import fi_telegram
from flexus_client_kit.integrations.providers.request_response import fi_mongo_store
from flexus_simple_bots.telegram_groupmod import telegram_groupmod_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("telegram_groupmod")

BOT_NAME = "telegram_groupmod"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

BUFFER_MAX_KB = 128
MESSAGE_MAX_KB = 50
BUFFER_TRIGGER_KB = BUFFER_MAX_KB // 2
BUFFER_SIZE_STEP_KB = BUFFER_TRIGGER_KB // 2
BUFFER_TIME_STEP = 3600

# Plan:
# - debug capture / uncapture for private messages
# - debug immediate reaction to keywords on messages in group
# - debug slow reaction by model


MODERATION_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="telegram_mod_action",
    description="Perform moderation actions on Telegram group members.",
    parameters={
        "type": "object",
        "properties": {
            "op": {
                "type": "string",
                "enum": ["warn", "mute", "unmute", "kick", "ban", "unban", "history", "stats"],
                "description": "warn=add warning, mute=restrict messaging, unmute=lift mute, kick=remove from group, ban=permanent ban, unban=lift ban, history=get user's warning history, stats=moderation stats (set user_id to '*' for whole chat or a specific user_id to filter)",
            },
            "chat_id": {
                "type": "string",
                "description": "Telegram group chat ID",
            },
            "user_id": {
                "type": "string",
                "description": "Telegram user ID to act on",
            },
            "reason": {
                "type": ["string", "null"],
                "description": "Reason for the action",
            },
            "duration_minutes": {
                "type": ["integer", "null"],
                "description": "Duration in minutes for mute (null=permanent until unmute)",
            },
        },
        "required": ["op", "chat_id", "user_id", "reason", "duration_minutes"],
        "additionalProperties": False,
    },
)

DELETE_MESSAGE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="telegram_mod_delete",
    description="Delete a message from a Telegram group.",
    parameters={
        "type": "object",
        "properties": {
            "chat_id": {
                "type": "string",
                "description": "Telegram group chat ID",
            },
            "message_id": {
                "type": "string",
                "description": "Message ID to delete",
            },
            "reason": {
                "type": ["string", "null"],
                "description": "Why the message is being deleted",
            },
        },
        "required": ["chat_id", "message_id", "reason"],
        "additionalProperties": False,
    },
)

HISTORY_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="telegram_mod_history",
    description="Look up a user's moderation history across all groups: warnings, mutes, bans.",
    parameters={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Telegram user ID to look up",
            },
        },
        "required": ["user_id"],
        "additionalProperties": False,
    },
)

BUFFER_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="telegram_mod_buffer",
    description="Retrieve accumulated group messages and clear the buffer. Returns JSON array of messages with chat_id, message_id, author_name, author_id, text, ts, has_attachment. Up to 128KB.",
    parameters={
        "type": "object",
        "properties": {
            "chat_id": {
                "type": "string",
                "description": "Telegram group chat ID to get buffer for, cannot be asterisk.",
            },
        },
        "required": ["chat_id"],
        "additionalProperties": False,
    },
)

TOOLS_ALL = [
    MODERATION_TOOL,
    DELETE_MESSAGE_TOOL,
    HISTORY_TOOL,
    BUFFER_TOOL,
    fi_telegram.TELEGRAM_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
]

TOOLS_DM = [
    HISTORY_TOOL,
    fi_telegram.TELEGRAM_TOOL,
]


def _buffer_size_kb(buf: List[dict]) -> float:
    return sum(len(m["text"]) for m in buf) / 1024.0


async def telegram_groupmod_main_loop(
    fclient: ckit_client.FlexusClient,
    rcx: ckit_bot_exec.RobotContext,
) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(
        telegram_groupmod_install.TELEGRAM_GROUPMOD_SETUP_SCHEMA,
        rcx.persona.persona_setup,
    )

    warns_before_mute = setup["warns_before_mute"]
    mutes_before_ban = setup["mutes_before_ban"]
    tz = ZoneInfo(rcx.persona.ws_timezone)

    blocklist_phrases = [p.strip().lower() for p in setup.get("blocklist", "").splitlines() if p.strip()]
    whitelisted_domains = {d.strip().lower() for d in setup.get("whitelisted_domains", "").splitlines() if d.strip()}
    block_all_links = setup.get("block_all_links", False)

    _URL_RE = re.compile(r'https?://([^/\s]+)', re.IGNORECASE)

    def _has_blocklist_hit(text: str) -> bool:
        lower = text.lower()
        return any(phrase in lower for phrase in blocklist_phrases)

    def _has_bad_link(text: str) -> bool:
        urls = _URL_RE.findall(text)
        if not urls:
            return False
        if block_all_links:
            return True
        for domain in urls:
            domain = domain.lower()
            if not any(domain == wd or domain.endswith("." + wd) for wd in whitelisted_domains):
                return True
        return False

    mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    db = mongo[rcx.persona.persona_id + "_db"]
    coll_warnings = db["warnings"]
    coll_deleted_log = db["deleted_messages"]
    coll_mod_actions = db["mod_actions"]
    coll_buffer = db["message_buffer"]

    await coll_warnings.create_index("user_id")
    await coll_deleted_log.create_index([("ts", -1)])
    await coll_deleted_log.create_index("ts", expireAfterSeconds=30 * 86400)
    await coll_mod_actions.create_index([("ts", -1)])
    await coll_mod_actions.create_index("ts", expireAfterSeconds=90 * 86400)
    await coll_buffer.create_index("chat_id")
    await coll_buffer.create_index("ts", expireAfterSeconds=7 * 86400)

    tg = fi_telegram.IntegrationTelegram(fclient, rcx)

    # Per-chat message buffers, keyed by chat_id string
    buffers: Dict[str, List[dict]] = {}
    buffer_last_ts: Dict[str, float] = {}
    buffer_last_size: Dict[str, float] = {}

    buffer_unsaved: List[dict] = []        # new messages not yet in mongo, see function below
    buffer_drained_ids: List[Any] = []     # _id's of messages consumed by buffer tool, see function below

    async def sync_buffers_to_mongo():
        logger.info("syncing %d messages to mongo...", len(buffer_unsaved))
        if buffer_unsaved:
            await coll_buffer.insert_many(buffer_unsaved)
            buffer_unsaved.clear()
        if buffer_drained_ids:
            await coll_buffer.delete_many({"_id": {"$in": buffer_drained_ids}})
            buffer_drained_ids.clear()

    # Load from mongo after restart
    async for doc in coll_buffer.find().sort("ts", 1):
        chat_id = doc["chat_id"]
        buffers.setdefault(chat_id, []).append(doc)
        if chat_id not in buffer_last_ts:
            buffer_last_ts[chat_id] = doc["ts"]
    for chat_id, buf in buffers.items():
        buffer_last_size[chat_id] = _buffer_size_kb(buf)
    logger.info("restored %d buffered messages across %d chats from mongo", sum(len(b) for b in buffers.values()), len(buffers))


    # --- messages buffering ---

    @rcx.on_tool_call(BUFFER_TOOL.name)
    async def handle_buffer_tool(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        chat_id = args["chat_id"]
        buf = buffers.pop(chat_id, [])
        if not buf:
            return "Buffer empty, no messages accumulated.\n"
        result = []
        total = 0
        consumed = 0
        for m in buf:
            entry = {
                "chat_id": m["chat_id"],
                "message_id": m["message_id"],
                "author_name": m["author_name"],
                "author_id": m["author_id"],
                "text": m["text"][:MESSAGE_MAX_KB],
                "ts": m["ts"],
                "has_attachment": m.get("has_attachment", False),
                "is_forward": m.get("is_forward", False),
                "is_join": m.get("is_join", False),
            }
            entry_size = len(entry.get("text", ""))
            if total + entry_size > BUFFER_MAX_KB * 1024:
                break
            result.append(entry)
            total += entry_size
            consumed += 1
        drained = buf[:consumed]
        remainder = buf[consumed:]
        buffer_drained_ids.extend(m["_id"] for m in drained if "_id" in m)
        if remainder:
            buffers[chat_id] = remainder
            buffer_last_ts[chat_id] = time.time()
            buffer_last_size[chat_id] = _buffer_size_kb(remainder)
        else:
            buffer_last_ts.pop(chat_id, None)
            buffer_last_size.pop(chat_id, None)
        return json.dumps(result, ensure_ascii=False, indent=1) + "\n"


    # --- ban hammer for the model to use ---

    async def log_mod_action(op: str, chat_id: str, user_id: str, reason: str):
        await coll_mod_actions.insert_one({
            "op": op,
            "chat_id": chat_id,
            "user_id": user_id,
            "reason": reason,
            "ts": time.time(),
        })

    async def check_auto_escalation(chat_id: str, user_id: str) -> str:
        warn_count = await coll_warnings.count_documents({"user_id": user_id, "chat_id": chat_id})
        mute_count = await coll_mod_actions.count_documents({"user_id": user_id, "chat_id": chat_id, "op": "mute"})
        if mute_count >= mutes_before_ban:
            return "ban"
        if warn_count >= warns_before_mute:
            return "mute"
        return ""

    async def _format_history(user_id: str, chat_id: str = "") -> str:
        LIMIT = 50
        now_line = "Now is %s tz=%s" % (datetime.now(tz).strftime("%Y-%m-%d %H:%M %Z"), rcx.persona.ws_timezone)
        q: Dict[str, Any] = {"user_id": user_id}
        if chat_id:
            q["chat_id"] = chat_id
        warns = await coll_warnings.count_documents(q)
        mutes = await coll_mod_actions.count_documents({**q, "op": "mute"})
        bans = await coll_mod_actions.count_documents({**q, "op": "ban"})
        docs = await coll_mod_actions.find(q).sort("ts", -1).limit(LIMIT).to_list(length=LIMIT)
        total = await coll_mod_actions.count_documents(q)
        explanation = "User %s: %d warnings, %d mutes, %d bans" % (user_id, warns, mutes, bans)
        if total > LIMIT:
            explanation += " (showing last %d of %d)" % (LIMIT, total)
        if not docs:
            return "%s\n%s\nNo moderation actions recorded.\n" % (now_line, explanation)
        rows = ["time,chat_id,op,reason"]
        for d in docs:
            t = datetime.fromtimestamp(d["ts"], tz=tz).strftime("%Y-%m-%d %H:%M")
            rows.append("%s,%s,%s,%s" % (t, d.get("chat_id", ""), d["op"], d.get("reason") or ""))
        return "%s\n%s\n\n%s\n" % (now_line, explanation, "\n".join(rows))

    @rcx.on_tool_call(HISTORY_TOOL.name)
    async def handle_history_tool(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await _format_history(args["user_id"])

    @rcx.on_tool_call(MODERATION_TOOL.name)
    async def handle_ban_hammer_tool(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        op = args["op"]
        chat_id = args["chat_id"]
        user_id = args["user_id"]
        reason = args.get("reason") or ""
        duration = args.get("duration_minutes")

        if op == "history":
            return await _format_history(user_id, chat_id)

        elif op == "warn":
            await coll_warnings.insert_one({
                "user_id": user_id, "chat_id": chat_id,
                "reason": reason, "ts": time.time(),
            })
            await log_mod_action("warn", chat_id, user_id, reason)
            escalation = await check_auto_escalation(chat_id, user_id)
            warn_count = await coll_warnings.count_documents({"user_id": user_id, "chat_id": chat_id})
            result = f"Warning #{warn_count} recorded for user {user_id}. Reason: {reason}\n"
            if escalation == "mute":
                result += f"AUTO-ESCALATION: user has {warn_count} warnings (threshold {warns_before_mute}). You should mute this user.\n"
            elif escalation == "ban":
                mute_count = await coll_mod_actions.count_documents({"user_id": user_id, "chat_id": chat_id, "op": "mute"})
                result += f"AUTO-ESCALATION: user has {mute_count} mutes (threshold {mutes_before_ban}). You should ban this user.\n"
            return result

        elif op == "mute":
            # XXX fi_telegram needs: restrict_chat_member(chat_id, user_id, permissions=ChatPermissions(can_send_messages=False), until_date=duration)
            await log_mod_action("mute", chat_id, user_id, reason)
            dur_str = f"{duration} minutes" if duration else "until unmuted"
            return f"Muted user {user_id} for {dur_str}. Reason: {reason}\n"

        elif op == "unmute":
            # XXX fi_telegram needs: restrict_chat_member with full permissions
            await log_mod_action("unmute", chat_id, user_id, reason)
            return f"Unmuted user {user_id}.\n"

        elif op == "kick":
            # XXX fi_telegram needs: unban_chat_member(chat_id, user_id, only_if_banned=False)
            await log_mod_action("kick", chat_id, user_id, reason)
            return f"Kicked user {user_id}. Reason: {reason}\n"

        elif op == "ban":
            # XXX fi_telegram needs: ban_chat_member(chat_id, user_id)
            await log_mod_action("ban", chat_id, user_id, reason)
            return f"Banned user {user_id}. Reason: {reason}\n"

        elif op == "unban":
            # XXX fi_telegram needs: unban_chat_member(chat_id, user_id)
            await log_mod_action("unban", chat_id, user_id, reason)
            return f"Unbanned user {user_id}.\n"

        elif op == "stats":
            LIMIT = 500
            now_line = "Now is %s tz=%s" % (datetime.now(tz).strftime("%Y-%m-%d %H:%M %Z"), rcx.persona.ws_timezone)
            q: Dict[str, Any] = {}
            specific_chat = chat_id and chat_id != "*"
            if specific_chat:
                q["chat_id"] = chat_id
            specific_user = user_id and user_id != "*"
            if specific_user:
                q["user_id"] = user_id
            total = await coll_mod_actions.count_documents(q)
            cursor = coll_mod_actions.find(q).sort("ts", -1).limit(LIMIT)
            docs = await cursor.to_list(length=LIMIT)
            if not docs:
                return "%s\nNo moderation actions recorded%s.\n" % (
                    now_line, " for user %s" % user_id if specific_user else "")
            counts: Dict[str, int] = {}
            for d in docs:
                counts[d["op"]] = counts.get(d["op"], 0) + 1
            summary = ", ".join("%d %s" % (v, k) for k, v in counts.items())
            if specific_user:
                explanation = "User %s" % user_id + (" in chat %s" % chat_id if specific_chat else "") + ": " + summary
            elif specific_chat:
                explanation = "Chat %s: %s" % (chat_id, summary)
            else:
                explanation = "All chats: %s" % summary
            if total > LIMIT:
                explanation += " (showing last %d of %d)" % (LIMIT, total)
            # csv
            headers = ["time", "op"]
            if not specific_chat:
                headers.append("chat_id")
            if not specific_user:
                headers.append("user_id")
            headers.append("reason")
            rows = [",".join(headers)]
            for d in docs:
                t = datetime.fromtimestamp(d["ts"], tz=tz).strftime("%Y-%m-%d %H:%M")
                fields = [t, d["op"]]
                if not specific_chat:
                    fields.append(d.get("chat_id", ""))
                if not specific_user:
                    fields.append(d.get("user_id", ""))
                fields.append(d.get("reason") or "")
                rows.append(",".join(fields))
            return "%s\n%s\n\n%s\n" % (now_line, explanation, "\n".join(rows))

        return f"Unknown op: {op}\n"

    @rcx.on_tool_call(DELETE_MESSAGE_TOOL.name)
    async def handle_delete_message_tool(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        chat_id = args["chat_id"]
        message_id = args["message_id"]
        reason = args.get("reason") or ""
        # XXX fi_telegram needs: delete_message(chat_id, message_id)
        await coll_deleted_log.insert_one({
            "chat_id": chat_id, "message_id": message_id,
            "reason": reason, "ts": time.time(),
        })
        await log_mod_action("delete_message", chat_id, "n/a", reason)
        return f"Deleted message {message_id} in chat {chat_id}. Reason: {reason}\n"

    @rcx.on_tool_call(fi_telegram.TELEGRAM_TOOL.name)
    async def handle_telegram(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await tg.called_by_model(toolcall, args)

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def handle_mongo_store(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await fi_mongo_store.handle_mongo_store(
            rcx.workdir, db["personal_mongo"], toolcall, args,
        )

    @rcx.on_updated_message
    async def handle_message(msg):
        if tg:
            await tg.look_assistant_might_have_posted_something(msg)

    @rcx.on_emessage("TELEGRAM")
    async def handle_emessage(emsg):
        if tg:
            await tg.handle_emessage(emsg)

    async def _post_buffer_task(chat_id: str, reason: str):
        buf = buffers.get(chat_id, [])
        if not buf:
            return
        title = "%s for chat %s (%d messages)" % (reason, chat_id, len(buf))
        details = {
            "chat_id": chat_id,
            "message_count": len(buf),
            "instruction": "Call telegram_mod_buffer(chat_id=%s) to retrieve messages, then review for violations." % chat_id,
        }
        await ckit_kanban.bot_kanban_post_into_inbox(
            fclient,
            rcx.persona.persona_id,
            title=title,
            details_json=json.dumps(details, ensure_ascii=False),
            provenance_message="telegram_buffer_review",
            fexp_name="review_messages",
        )
        logger.info("posted buffer task (%s): %d messages for chat %s", reason, len(buf), chat_id)

    async def maybe_post_time_task(chat_id: str):
        now = time.time()
        last_ts = buffer_last_ts.get(chat_id)
        if last_ts is None:
            return
        prev_period = int(last_ts // BUFFER_TIME_STEP)
        curr_period = int(now // BUFFER_TIME_STEP)
        if curr_period > prev_period:
            buffer_last_ts[chat_id] = now
            await _post_buffer_task(chat_id, "Time to review buffered messages")

    async def maybe_post_size_task(chat_id: str):
        buf = buffers.get(chat_id, [])
        size_kb = _buffer_size_kb(buf)
        last_size = buffer_last_size.get(chat_id, 0.0)
        prev_step = int(last_size // BUFFER_SIZE_STEP_KB)
        curr_step = int(size_kb // BUFFER_SIZE_STEP_KB)
        if curr_step > prev_step:
            buffer_last_size[chat_id] = size_kb
            await _post_buffer_task(chat_id, "Buffer is getting big")

    async def _try_delete_message(chat_id: int, message_id: int, user_id: int, reason: str):
        try:
            await tg.tg_app.bot.delete_message(chat_id=chat_id, message_id=message_id)
            logger.info("auto-deleted msg %s in chat %s: %s", message_id, chat_id, reason)
        except Exception as e:
            logger.warning("failed to delete msg %s in chat %s: %s", message_id, chat_id, e)
        await coll_deleted_log.insert_one({"chat_id": str(chat_id), "message_id": str(message_id), "reason": reason, "ts": time.time()})
        await log_mod_action("auto_delete", str(chat_id), str(user_id), reason)

    @tg.on_incoming_activity
    async def telegram_activity_callback(a: fi_telegram.ActivityTelegram, already_posted_to_captured_thread: bool):
        if already_posted_to_captured_thread:
            return

        is_group = a.chat_type in ("group", "supergroup")
        if is_group:
            chat_id = str(a.chat_id)
            text = a.message_text

            if blocklist_phrases and _has_blocklist_hit(text):
                await _try_delete_message(a.chat_id, a.message_id, a.message_author_id, "blocklist hit")
                return

            if _has_bad_link(text):
                await _try_delete_message(a.chat_id, a.message_id, a.message_author_id, "blocked link")
                return

            buf_entry = {
                "chat_id": chat_id,
                "message_id": a.message_id,
                "author_name": a.message_author_name,
                "author_id": a.message_author_id,
                "text": text,
                "ts": time.time(),
                "has_attachment": bool(a.attachments),
                "is_forward": False,
                # XXX fi_telegram needs: expose forward_origin and new_chat_members on ActivityTelegram
                "is_join": False,
            }
            buffers.setdefault(chat_id, []).append(buf_entry)
            buffer_unsaved.append(buf_entry)
            if chat_id not in buffer_last_ts:
                buffer_last_ts[chat_id] = time.time()
            logger.info("%s telegram group type=%s chat_id=%s msg_id=%s from %r (uid=%s): %s",
                rcx.persona.persona_id, a.chat_type, a.chat_id, a.message_id,
                a.message_author_name, a.message_author_id, text[:120] or "(empty)")
            await maybe_post_size_task(chat_id)
            return

        logger.info("%s telegram private inbound type=%s chat_id=%s msg_id=%s from %r (uid=%s): %s",
            rcx.persona.persona_id, a.chat_type, a.chat_id, a.message_id,
            a.message_author_name, a.message_author_id, a.message_text[:120] or "(empty)")
        details = asdict(a)
        if a.attachments:
            details["attachments"] = f"{len(a.attachments)} files attached"
        title = "%r private message via telegram: %s" % (a.message_author_name, a.message_text)
        await ckit_kanban.bot_kanban_post_into_inbox(
            fclient,
            rcx.persona.persona_id,
            title=title,
            details_json=json.dumps(details),
            provenance_message="telegram_private_message",
            fexp_name="talk_in_dm",
        )

    await tg.register_webhook_and_start()
    last_sync = time.time()
    try:
        while not ckit_shutdown.shutdown_event.is_set():
            for chat_id in list(buffers.keys()):
                await maybe_post_time_task(chat_id)
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
            now = time.time()
            if now - last_sync >= 10.0:
                await sync_buffers_to_mongo()
                last_sync = now
    finally:
        await sync_buffers_to_mongo()
        if tg:
            await tg.close()
        await mongo.close()
        logger.info("telegram_groupmod stopped")


def main():
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(
        ckit_client.bot_service_name(BOT_NAME, BOT_VERSION),
        endpoint="/v1/jailed-bot",
    )
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=telegram_groupmod_main_loop,
        inprocess_tools=TOOLS_ALL,
        scenario_fn=scenario_fn,
        install_func=telegram_groupmod_install.install,
    ))


if __name__ == "__main__":
    main()
