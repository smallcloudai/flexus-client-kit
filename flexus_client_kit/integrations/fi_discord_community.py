"""
Discord community bots: shared gateway helpers (greenfield).

Does not replace fi_discord2 / Karen. Use for discord_onboarding, discord_moderation,
discord_faq, discord_engagement only.
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

import aiohttp
import discord
from discord.errors import DiscordException, HTTPException

logger = logging.getLogger("fi_discord_community")


def setup_truthy(raw: Any) -> bool:
    if raw is True:
        return True
    if raw is False or raw is None:
        return False
    s = str(raw).strip().lower()
    return s in ("1", "true", "yes", "on")

COL_JOBS = "dc_community_jobs"
COL_ONBOARDING = "dc_onboarding_state"
COL_MOD_EVENTS = "dc_mod_events"
COL_ACTIVITY = "dc_member_activity"
COL_FAQ_RATE = "dc_faq_rate"
COL_MOD_RATELIMIT = "dc_mod_ratelimit_window"

JobHandler = Callable[[Dict[str, Any]], Awaitable[None]]


def build_intents() -> discord.Intents:
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.guilds = True
    intents.dm_messages = True
    intents.guild_messages = True
    intents.guild_reactions = True
    return intents


def parse_snowflake(raw: str) -> Optional[int]:
    if not raw or not isinstance(raw, str):
        return None
    s = raw.strip()
    if not s or not s.isdigit():
        return None
    return int(s)


def discord_bot_api_key_from_external_auth(ext: Dict[str, Any]) -> str:
    # UI manual token = discord_manual; OAuth Karen path may use discord.
    for provider_key in ("discord_manual", "discord"):
        auth = ext.get(provider_key) or {}
        if not isinstance(auth, dict):
            continue
        tok = (auth.get("api_key") or "").strip()
        if tok:
            return tok
    return ""


def guild_matches(guild: Optional[discord.Guild], want_id: Optional[int]) -> bool:
    if want_id is None:
        return True
    if guild is None:
        return False
    return int(guild.id) == int(want_id)


def truncate_message(text: str, limit: int = 2000) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 20] + "\n...(truncated)"


def log_ctx(persona_id: str, guild_id: Optional[int], msg: str, *args: Any) -> None:
    gid = str(guild_id) if guild_id is not None else "-"
    logger.info("[%s guild=%s] " + msg, persona_id, gid, *args)


def _channel_guild_id(channel: discord.abc.Messageable) -> Optional[int]:
    g = getattr(channel, "guild", None)
    return int(g.id) if g is not None else None


async def safe_send(
    channel: discord.abc.Messageable,
    persona_id: str,
    content: str,
) -> Optional[discord.Message]:
    t = truncate_message(content)
    gid = _channel_guild_id(channel)
    delay = 1.0
    for attempt in range(5):
        try:
            return await channel.send(t)
        except HTTPException as e:
            if e.status == 429 and attempt < 4:
                ra = getattr(e, "retry_after", None)
                wait = float(ra) if ra is not None else delay
                wait = max(0.5, min(wait, 30.0))
                log_ctx(persona_id, gid, "safe_send 429 backoff %.1fs", wait)
                await asyncio.sleep(wait)
                delay = min(delay * 2.0, 16.0)
                continue
            log_ctx(persona_id, gid, "safe_send HTTP %s", e.status)
            return None
        except DiscordException as e:
            log_ctx(persona_id, gid, "safe_send failed: %s %s", type(e).__name__, e)
            return None
        except aiohttp.ClientError as e:
            log_ctx(persona_id, gid, "safe_send network: %s %s", type(e).__name__, e)
            return None
    return None


async def safe_dm(
    client: discord.Client,
    user: discord.abc.User,
    persona_id: str,
    content: str,
) -> bool:
    try:
        ch = user.dm_channel or await user.create_dm()
    except DiscordException as e:
        log_ctx(persona_id, None, "create_dm failed for user=%s: %s %s", getattr(user, "id", "?"), type(e).__name__, e)
        return False
    except aiohttp.ClientError as e:
        log_ctx(
            persona_id,
            None,
            "create_dm network for user=%s: %s %s",
            getattr(user, "id", "?"),
            type(e).__name__,
            e,
        )
        return False
    m = await safe_send(ch, persona_id, content)
    return m is not None


async def enqueue_job(
    db: Any,
    kind: str,
    run_at_ts: float,
    payload: Dict[str, Any],
) -> None:
    coll = db[COL_JOBS]
    await coll.insert_one(
        {
            "kind": kind,
            "run_at": float(run_at_ts),
            "payload": payload,
            "done": False,
            "created_ts": time.time(),
        }
    )


async def drain_due_jobs(
    db: Any,
    persona_id: str,
    handlers: Dict[str, JobHandler],
    limit: int = 50,
) -> int:
    coll = db[COL_JOBS]
    now = time.time()
    count = 0
    cursor = coll.find({"done": False, "run_at": {"$lte": now}}).sort("run_at", 1).limit(limit)
    async for doc in cursor:
        kind = doc.get("kind") or ""
        handler = handlers.get(kind)
        if not handler:
            await coll.update_one({"_id": doc["_id"]}, {"$set": {"done": True, "error": "no_handler"}})
            continue
        payload = doc.get("payload") or {}
        try:
            await handler(payload)
        except DiscordException as e:
            log_ctx(persona_id, payload.get("guild_id"), "job %s DiscordException: %s %s", kind, type(e).__name__, e)
        except (TypeError, ValueError, KeyError) as e:
            log_ctx(persona_id, payload.get("guild_id"), "job %s data error: %s %s", kind, type(e).__name__, e)
        await coll.update_one({"_id": doc["_id"]}, {"$set": {"done": True, "finished_ts": time.time()}})
        count += 1
    return count


def compile_url_patterns(lines: str) -> List[re.Pattern[str]]:
    out: List[re.Pattern[str]] = []
    for line in (lines or "").splitlines():
        pat = line.strip()
        if not pat:
            continue
        try:
            out.append(re.compile(pat, re.I))
        except re.error:
            logger.warning("bad url regex ignored: %r", pat[:80])
    return out


DISCORD_INVITE_RE = re.compile(
    r"(discord\.gg/|discordapp\.com/invite/|discord\.com/invite/)[a-zA-Z0-9_-]+",
    re.I,
)


def message_has_invite(content: str) -> bool:
    return bool(DISCORD_INVITE_RE.search(content or ""))


def match_blocked_url(content: str, patterns: List[re.Pattern[str]]) -> bool:
    for p in patterns:
        if p.search(content or ""):
            return True
    return False


async def start_discord_client(
    token: str,
    persona_id: str,
    register: Callable[[discord.Client], None],
) -> Tuple[discord.Client, asyncio.Task[None]]:
    client = discord.Client(intents=build_intents())
    register(client)

    async def _runner() -> None:
        try:
            await client.start(token)
        except asyncio.CancelledError:
            raise
        except DiscordException as e:
            logger.error("[%s] discord client died: %s %s", persona_id, type(e).__name__, e)

    t = asyncio.create_task(_runner())
    return client, t


async def close_discord_client(client: Optional[discord.Client], task: Optional[asyncio.Task]) -> None:
    if task and not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    if client and not client.is_closed():
        await client.close()


def _perm_gaps_basic(perms: discord.Permissions) -> List[str]:
    miss: List[str] = []
    if not perms.view_channel:
        miss.append("view_channel")
    if not perms.send_messages:
        miss.append("send_messages")
    if not perms.read_message_history:
        miss.append("read_message_history")
    return miss


def _perm_gaps_mod(perms: discord.Permissions) -> List[str]:
    miss = _perm_gaps_basic(perms)
    if not perms.manage_messages:
        miss.append("manage_messages")
    return miss


def preflight_text_channels(
    guild: discord.Guild,
    bot_user: discord.ClientUser,
    persona_id: str,
    bot_label: str,
    channels: Dict[str, Tuple[Optional[int], str]],
    *,
    warn_manage_roles: bool = False,
) -> None:
    me = guild.get_member(bot_user.id)
    if not me:
        log_ctx(persona_id, guild.id, "preflight %s: bot not in guild member cache", bot_label)
        return
    for label, (cid, level) in channels.items():
        if not cid:
            continue
        ch = guild.get_channel(int(cid))
        if not isinstance(ch, discord.TextChannel):
            log_ctx(persona_id, guild.id, "preflight %s: %s id=%s missing or not text", bot_label, label, cid)
            continue
        perms = ch.permissions_for(me)
        if level == "mod":
            miss = _perm_gaps_mod(perms)
        else:
            miss = _perm_gaps_basic(perms)
        if miss:
            log_ctx(
                persona_id,
                guild.id,
                "preflight %s: %s ch=%s missing %s",
                bot_label,
                label,
                cid,
                ",".join(miss),
            )
    if warn_manage_roles and not me.guild_permissions.manage_roles:
        log_ctx(
            persona_id,
            guild.id,
            "preflight %s: guild.manage_roles false (assign roles only below bot role)",
            bot_label,
        )
