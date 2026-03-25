import asyncio
import json
import logging
import re
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any, Deque, Dict, List, Optional, Set, Tuple

import discord
from discord.errors import DiscordException
from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_mongo
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_discord_community as dc
from flexus_simple_bots.discord_moderation import discord_moderation_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("discord_moderation")

BOT_NAME = "discord_moderation"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
TOOLS: List[Any] = []

WINDOW_SEC = 60


def _parse_channel_rules(raw: str) -> List[Tuple[int, re.Pattern[str], str]]:
    try:
        v = json.loads(raw or "[]")
    except json.JSONDecodeError:
        return []
    if not isinstance(v, list):
        return []
    out: List[Tuple[int, re.Pattern[str], str]] = []
    for item in v:
        if not isinstance(item, dict):
            continue
        cid = str(item.get("channel_id", "")).strip()
        pat = str(item.get("must_match_regex", ".*"))
        hint = str(item.get("hint", "Message format not allowed here."))
        if not cid.isdigit():
            continue
        try:
            out.append((int(cid), re.compile(pat), hint))
        except re.error:
            logger.warning("bad channel rule regex skipped: %r", pat[:80])
    return out


async def _mod_log(
    guild: discord.Guild,
    setup: Dict[str, Any],
    persona_id: str,
    text: str,
) -> None:
    lid = dc.parse_snowflake(setup.get("mod_log_channel_id", ""))
    if not lid:
        return
    ch = guild.get_channel(lid)
    if not isinstance(ch, discord.TextChannel):
        return
    await dc.safe_send(ch, persona_id, truncate_message_mod(text))


def truncate_message_mod(text: str) -> str:
    return dc.truncate_message(text, 1900)


async def _record_mod_event(mongo_db: Any, doc: Dict[str, Any]) -> None:
    doc["ts"] = time.time()
    await mongo_db[dc.COL_MOD_EVENTS].insert_one(doc)


def _register_discord(
    client: discord.Client,
    setup: Dict[str, Any],
    mongo_db: Any,
    persona_id: str,
    guild_want: Optional[int],
) -> None:
    url_patterns = dc.compile_url_patterns(setup.get("url_block_regexes", ""))
    rules = _parse_channel_rules(setup.get("channel_rules_json", "[]"))
    invite_block = str(setup.get("block_invite_links", "true")).lower() in ("1", "true", "yes")
    max_per_min = int(setup.get("max_messages_per_minute") or 0)
    new_age_days = int(setup.get("new_account_max_age_days") or 0)
    quar_rid = dc.parse_snowflake(setup.get("new_account_quarantine_role_id", ""))
    dry = dc.setup_truthy(setup.get("moderation_dry_run"))

    buckets: Dict[Tuple[int, int], Deque[float]] = defaultdict(deque)

    def _rate_allow(gid: int, uid: int) -> bool:
        if max_per_min <= 0:
            return True
        now = time.time()
        dq = buckets[(gid, uid)]
        while dq and now - dq[0] > WINDOW_SEC:
            dq.popleft()
        if len(dq) >= max_per_min:
            return False
        dq.append(now)
        return True

    @client.event
    async def on_ready() -> None:
        dc.log_ctx(persona_id, None, "discord moderation ready as %s", client.user)
        if guild_want and client.user:
            g0 = client.get_guild(int(guild_want))
            if g0:
                me = g0.get_member(client.user.id)
                if me:
                    gm: List[str] = []
                    if not me.guild_permissions.manage_messages:
                        gm.append("manage_messages")
                    if new_age_days > 0 and not quar_rid and not me.guild_permissions.kick_members:
                        gm.append("kick_members")
                    if new_age_days > 0 and quar_rid and not me.guild_permissions.manage_roles:
                        gm.append("manage_roles")
                    if gm:
                        dc.log_ctx(persona_id, g0.id, "preflight discord_moderation guild missing %s", ",".join(gm))
                ch_map: Dict[str, Tuple[Optional[int], str]] = {
                    "mod_log": (dc.parse_snowflake(setup.get("mod_log_channel_id", "")), "basic"),
                }
                seen: Set[int] = set()
                for rid, _pat, _hint in rules:
                    if rid not in seen:
                        seen.add(rid)
                        ch_map["channel_rule_%d" % rid] = (rid, "mod")
                dc.preflight_text_channels(g0, client.user, persona_id, "discord_moderation", ch_map)

    @client.event
    async def on_member_join(member: discord.Member) -> None:
        if not dc.guild_matches(member.guild, guild_want) or member.bot:
            return
        if new_age_days <= 0:
            return
        created = member.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - created).total_seconds() / 86400.0
        if age_days > float(new_age_days):
            return
        await _mod_log(
            member.guild,
            setup,
            persona_id,
            "New account join: %s (%s) age_days=%.2f" % (member, member.id, age_days),
        )
        if dry:
            await _mod_log(
                member.guild,
                setup,
                persona_id,
                "[DRY] would quarantine or kick new account %s" % member.id,
            )
            await _record_mod_event(
                mongo_db,
                {"action": "dry_new_account", "guild_id": member.guild.id, "user_id": member.id, "age_days": age_days},
            )
            return
        if quar_rid:
            role = member.guild.get_role(quar_rid)
            if role:
                try:
                    await member.add_roles(role, reason="new account quarantine")
                except DiscordException as e:
                    dc.log_ctx(persona_id, member.guild.id, "quarantine role failed: %s %s", type(e).__name__, e)
            return
        try:
            await member.kick(reason="Account too new (configured policy)")
        except DiscordException as e:
            dc.log_ctx(persona_id, member.guild.id, "kick new account failed: %s %s", type(e).__name__, e)
        await _record_mod_event(
            mongo_db,
            {"action": "kick_new_account", "guild_id": member.guild.id, "user_id": member.id, "age_days": age_days},
        )

    @client.event
    async def on_message(message: discord.Message) -> None:
        if message.author.bot:
            return
        if not message.guild or not dc.guild_matches(message.guild, guild_want):
            return
        gid = int(message.guild.id)
        uid = int(message.author.id)
        if not _rate_allow(gid, uid):
            if dry:
                await _mod_log(
                    message.guild,
                    setup,
                    persona_id,
                    "[DRY] rate limit would delete user=%s ch=%s" % (uid, message.channel.id),
                )
                await _record_mod_event(
                    mongo_db,
                    {"action": "rate_limit", "guild_id": gid, "user_id": uid, "channel_id": message.channel.id, "dry_run": True},
                )
                return
            try:
                await message.delete()
            except DiscordException as e:
                dc.log_ctx(persona_id, gid, "delete rate limit msg failed: %s %s", type(e).__name__, e)
            await _mod_log(message.guild, setup, persona_id, "Rate limit delete user=%s channel=%s" % (uid, message.channel.id))
            await _record_mod_event(
                mongo_db,
                {"action": "rate_limit", "guild_id": gid, "user_id": uid, "channel_id": message.channel.id},
            )
            return

        content = message.content or ""
        if invite_block and dc.message_has_invite(content):
            if dry:
                await _mod_log(message.guild, setup, persona_id, "[DRY] invite block would delete user=%s" % uid)
                await _record_mod_event(
                    mongo_db,
                    {"action": "invite_block", "guild_id": gid, "user_id": uid, "channel_id": message.channel.id, "dry_run": True},
                )
                return
            try:
                await message.delete()
            except DiscordException as e:
                dc.log_ctx(persona_id, gid, "delete invite failed: %s %s", type(e).__name__, e)
            await _mod_log(message.guild, setup, persona_id, "Removed invite link from user=%s" % uid)
            await _record_mod_event(
                mongo_db,
                {"action": "invite_block", "guild_id": gid, "user_id": uid, "channel_id": message.channel.id},
            )
            return

        if dc.match_blocked_url(content, url_patterns):
            if dry:
                await _mod_log(message.guild, setup, persona_id, "[DRY] URL rule would delete user=%s" % uid)
                await _record_mod_event(
                    mongo_db,
                    {"action": "url_block", "guild_id": gid, "user_id": uid, "channel_id": message.channel.id, "dry_run": True},
                )
                return
            try:
                await message.delete()
            except DiscordException as e:
                dc.log_ctx(persona_id, gid, "delete url pattern failed: %s %s", type(e).__name__, e)
            await _mod_log(message.guild, setup, persona_id, "URL pattern delete user=%s" % uid)
            await _record_mod_event(
                mongo_db,
                {"action": "url_block", "guild_id": gid, "user_id": uid, "channel_id": message.channel.id},
            )
            return

        ch_id = message.channel.id
        for rid, pat, hint in rules:
            if rid != ch_id:
                continue
            if pat.search(content):
                break
            if dry:
                await _mod_log(
                    message.guild,
                    setup,
                    persona_id,
                    "[DRY] channel rule would delete user=%s ch=%s" % (uid, ch_id),
                )
                await _record_mod_event(
                    mongo_db,
                    {"action": "channel_rule", "guild_id": gid, "user_id": uid, "channel_id": ch_id, "dry_run": True},
                )
                return
            try:
                await message.delete()
            except DiscordException as e:
                dc.log_ctx(persona_id, gid, "delete channel rule failed: %s %s", type(e).__name__, e)
            await _mod_log(
                message.guild,
                setup,
                persona_id,
                "Channel rule delete user=%s channel=%s hint=%s" % (uid, ch_id, hint),
            )
            await _record_mod_event(
                mongo_db,
                {"action": "channel_rule", "guild_id": gid, "user_id": uid, "channel_id": ch_id},
            )
            hint_ch = message.channel
            if isinstance(hint_ch, discord.TextChannel):
                await dc.safe_send(hint_ch, persona_id, hint)
            return


async def discord_moderation_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(
        discord_moderation_install.DISCORD_MODERATION_SETUP_SCHEMA,
        rcx.persona.persona_setup,
    )
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
        _register_discord(cl, setup, mongo_db, rcx.persona.persona_id, guild_want)

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
            bot_main_loop=discord_moderation_main_loop,
            inprocess_tools=TOOLS,
            scenario_fn=scenario_fn,
            install_func=discord_moderation_install.install,
        )
    )


if __name__ == "__main__":
    main()
