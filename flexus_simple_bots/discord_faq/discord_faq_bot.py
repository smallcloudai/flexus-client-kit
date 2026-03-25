import asyncio
import json
import logging
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple

import discord
from discord.errors import DiscordException
from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_mongo
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_discord_community as dc
from flexus_simple_bots.discord_faq import discord_faq_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("discord_faq")

BOT_NAME = "discord_faq"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
TOOLS: List[Any] = []


def _parse_faq_rules(raw: str) -> List[Tuple[re.Pattern[str], str]]:
    try:
        v = json.loads(raw or "[]")
    except json.JSONDecodeError:
        return []
    if not isinstance(v, list):
        return []
    out: List[Tuple[re.Pattern[str], str]] = []
    for item in v:
        if not isinstance(item, dict):
            continue
        pat = str(item.get("pattern", ""))
        resp = str(item.get("response", ""))
        if not pat or not resp:
            continue
        try:
            out.append((re.compile(pat), resp))
        except re.error:
            logger.warning("faq pattern skipped: %r", pat[:80])
    return out


def _channel_set(raw: str) -> Set[int]:
    s: Set[int] = set()
    for part in (raw or "").split(","):
        p = part.strip()
        if p.isdigit():
            s.add(int(p))
    return s


async def _rate_ok(mongo_db: Any, ch_id: int, uid: int, min_sec: float) -> bool:
    coll = mongo_db[dc.COL_FAQ_RATE]
    now = time.time()
    key = {"channel_id": ch_id, "user_id": uid}
    doc = await coll.find_one(key)
    if doc and now - float(doc.get("last_ts", 0)) < min_sec:
        return False
    await coll.update_one(key, {"$set": {"last_ts": now}}, upsert=True)
    return True


def _register_discord(
    client: discord.Client,
    setup: Dict[str, Any],
    mongo_db: Any,
    persona_id: str,
    guild_want: Optional[int],
    fclient: ckit_client.FlexusClient,
) -> None:
    channels = _channel_set(setup.get("faq_channel_ids", ""))
    rules = _parse_faq_rules(setup.get("faq_rules_json", "[]"))
    prefix = (setup.get("faq_reply_prefix") or "").strip()
    unmatched = (setup.get("faq_unmatched_reply") or "").strip()
    escalate = str(setup.get("faq_escalate_kanban", "")).lower() in ("1", "true", "yes")
    rl = float(int(setup.get("faq_rate_limit_seconds") or 15))
    ctx_n = int(setup.get("faq_context_messages") or 0)
    faq_dry = dc.setup_truthy(setup.get("faq_dry_run"))

    @client.event
    async def on_ready() -> None:
        dc.log_ctx(persona_id, None, "discord faq ready as %s", client.user)
        if guild_want and client.user and channels:
            g0 = client.get_guild(int(guild_want))
            if g0:
                fm: Dict[str, Tuple[Optional[int], str]] = {}
                for i, cid in enumerate(sorted(channels)):
                    fm["faq_channel_%d" % i] = (cid, "basic")
                dc.preflight_text_channels(g0, client.user, persona_id, "discord_faq", fm)

    @client.event
    async def on_message(message: discord.Message) -> None:
        if message.author.bot:
            return
        if not message.guild or not dc.guild_matches(message.guild, guild_want):
            return
        if message.channel.id not in channels:
            return
        text = (message.content or "").strip()
        if prefix and not text.startswith(prefix):
            return
        body = text[len(prefix) :].strip() if prefix else text
        if not body:
            return
        if client.user and message.author.id == client.user.id:
            return
        if not await _rate_ok(mongo_db, message.channel.id, message.author.id, rl):
            return

        if faq_dry:
            logger.info("[%s] faq_dry trigger user=%s ch=%s body=%r", persona_id, message.author.id, message.channel.id, body[:300])
            return

        for pat, resp in rules:
            if pat.search(body):
                await dc.safe_send(message.channel, persona_id, resp)
                return

        if unmatched:
            await dc.safe_send(message.channel, persona_id, unmatched)

        if escalate:
            hist_note = ""
            if ctx_n > 0 and isinstance(message.channel, discord.TextChannel):
                lines: List[str] = []
                try:
                    async for m in message.channel.history(limit=ctx_n + 1, before=message):
                        if m.author.bot:
                            continue
                        lines.append("%s: %s" % (m.author.display_name, (m.content or "")[:200]))
                except DiscordException as e:
                    dc.log_ctx(persona_id, message.guild.id, "faq history fetch failed: %s %s", type(e).__name__, e)
                lines.reverse()
                if lines:
                    hist_note = "\n\nContext:\n" + "\n".join(lines)
            title = "Discord FAQ escalation user=%s channel=%s\n%s" % (message.author.id, message.channel.id, body[:500])
            details = {
                "discord_channel_id": str(message.channel.id),
                "discord_message_id": str(message.id),
                "discord_user_id": str(message.author.id),
                "question": body,
            }
            await ckit_kanban.bot_kanban_post_into_inbox(
                fclient,
                persona_id,
                title=title + hist_note,
                details_json=json.dumps(details),
                provenance_message="discord_faq_escalation",
                fexp_name="kb_helper",
            )


async def discord_faq_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(discord_faq_install.DISCORD_FAQ_SETUP_SCHEMA, rcx.persona.persona_setup)
    await ckit_integrations_db.main_loop_integrations_init(discord_faq_install.DISCORD_FAQ_INTEGRATIONS, rcx, setup)

    token = dc.discord_bot_api_key_from_external_auth(rcx.external_auth)
    if not token:
        logger.error("%s missing discord api_key", rcx.persona.persona_id)
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=30.0)
        return

    mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    mongo_db = mongo[rcx.persona.persona_id + "_db"]
    guild_want = dc.parse_snowflake(setup.get("dc_guild_id", ""))

    holder: Dict[str, Any] = {}

    def register(cl: discord.Client) -> None:
        holder["c"] = cl
        _register_discord(cl, setup, mongo_db, rcx.persona.persona_id, guild_want, fclient)

    cl, task = await dc.start_discord_client(token, rcx.persona.persona_id, register)
    holder["t"] = task

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=5.0)
    finally:
        await dc.close_discord_client(holder.get("c"), holder.get("t"))
        await mongo.close()
        logger.info("%s exit", rcx.persona.persona_id)


def main() -> None:
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")
    asyncio.run(
        ckit_bot_exec.run_bots_in_this_group(
            fclient,
            marketable_name=BOT_NAME,
            marketable_version_str=BOT_VERSION,
            bot_main_loop=discord_faq_main_loop,
            inprocess_tools=TOOLS,
            scenario_fn=scenario_fn,
            install_func=discord_faq_install.install,
        )
    )


if __name__ == "__main__":
    main()
