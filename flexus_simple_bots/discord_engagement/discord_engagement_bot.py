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
from flexus_client_kit import ckit_mongo
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_discord_community as dc
from flexus_simple_bots.discord_engagement import discord_engagement_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("discord_engagement")

BOT_NAME = "discord_engagement"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
TOOLS: List[Any] = []

KW_CD_COL = "dc_engagement_keyword_cd"


def _parse_keyword_map(raw: str) -> Dict[str, int]:
    try:
        v = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}
    if not isinstance(v, dict):
        return {}
    out: Dict[str, int] = {}
    for k, spec in v.items():
        kw = str(k).strip().lower()
        if not kw:
            continue
        if isinstance(spec, dict):
            rid = str(spec.get("role_id", "")).strip()
        else:
            rid = str(spec).strip()
        if rid.isdigit():
            out[kw] = int(rid)
    return out


def _role_ids_csv(s: str) -> List[int]:
    out: List[int] = []
    for part in (s or "").split(","):
        p = part.strip()
        if p.isdigit():
            out.append(int(p))
    return out


async def _kw_cooldown_ok(mongo_db: Any, ch_id: int, kw: str, min_sec: float) -> bool:
    coll = mongo_db[KW_CD_COL]
    now = time.time()
    key = {"channel_id": ch_id, "keyword": kw}
    doc = await coll.find_one(key)
    if doc and now - float(doc.get("last_ts", 0)) < min_sec:
        return False
    await coll.update_one(key, {"$set": {"last_ts": now}}, upsert=True)
    return True


async def _activity_touch(mongo_db: Any, guild_id: int, user_id: int) -> None:
    coll = mongo_db[dc.COL_ACTIVITY]
    now = time.time()
    await coll.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"last_message_ts": now}},
        upsert=True,
    )


async def _scan_inactivity(
    client: discord.Client,
    setup: Dict[str, Any],
    mongo_db: Any,
    persona_id: str,
    guild_want: int,
    payload: Dict[str, Any],
) -> None:
    del payload
    interval_h = float(int(setup.get("inactivity_scan_interval_hours") or 24))
    next_run = time.time() + interval_h * 3600.0
    guild = client.get_guild(int(guild_want))
    if not guild:
        await dc.enqueue_job(mongo_db, "engagement_inactivity_scan", next_run, {"guild_id": int(guild_want)})
        return
    valuable = _role_ids_csv(setup.get("valuable_role_ids", ""))
    if not valuable:
        await dc.enqueue_job(mongo_db, "engagement_inactivity_scan", next_run, {"guild_id": int(guild_want)})
        return
    opt_in = dc.parse_snowflake(setup.get("inactivity_opt_in_role_id", ""))
    days = float(int(setup.get("inactivity_days") or 14))
    body = (setup.get("checkin_dm_body") or "").strip()
    max_dm = int(setup.get("max_checkin_dms_per_scan") or 10)
    cd_days = float(int(setup.get("checkin_cooldown_days") or 7))
    no_dm = dc.setup_truthy(setup.get("disable_inactivity_dm"))
    log_only = dc.setup_truthy(setup.get("inactivity_log_only"))
    if not body:
        await dc.enqueue_job(mongo_db, "engagement_inactivity_scan", next_run, {"guild_id": int(guild_want)})
        return

    coll = mongo_db[dc.COL_ACTIVITY]
    now = time.time()
    sent = 0
    seen: Set[int] = set()

    for rid in valuable:
        role = guild.get_role(rid)
        if not role:
            continue
        for m in role.members:
            if m.bot or m.id in seen:
                continue
            seen.add(m.id)
            if opt_in and opt_in not in {x.id for x in m.roles}:
                continue
            doc = await coll.find_one({"guild_id": int(guild.id), "user_id": int(m.id)}) or {}
            last_msg = doc.get("last_message_ts")
            joined_ts = m.joined.timestamp() if m.joined else now
            last_act = float(last_msg) if last_msg else joined_ts
            if now - last_act < days * 86400.0:
                continue
            last_ck = float(doc.get("last_checkin_ts") or 0)
            if last_ck and now - last_ck < cd_days * 86400.0:
                continue
            if no_dm:
                continue
            if log_only:
                logger.info(
                    "[%s] inactivity_log_only would_dm user=%s guild=%s",
                    persona_id,
                    m.id,
                    guild.id,
                )
                continue
            ok = await dc.safe_dm(client, m, persona_id, body)
            if ok:
                sent += 1
                await coll.update_one(
                    {"guild_id": int(guild.id), "user_id": int(m.id)},
                    {"$set": {"last_checkin_ts": now}},
                    upsert=True,
                )
            if sent >= max_dm:
                break

    await dc.enqueue_job(mongo_db, "engagement_inactivity_scan", next_run, {"guild_id": int(guild_want)})


def _register_discord(
    client: discord.Client,
    setup: Dict[str, Any],
    mongo_db: Any,
    persona_id: str,
    guild_want: Optional[int],
) -> None:
    kw_map = _parse_keyword_map(setup.get("keyword_pings_json", "{}"))
    kw_cd = float(int(setup.get("keyword_cooldown_seconds") or 120))
    net_ch = dc.parse_snowflake(setup.get("networking_channel_id", ""))
    kw_off = dc.setup_truthy(setup.get("disable_keyword_pings"))

    @client.event
    async def on_ready() -> None:
        dc.log_ctx(persona_id, None, "discord engagement ready as %s", client.user)
        if guild_want and client.user:
            g0 = client.get_guild(int(guild_want))
            if g0 and net_ch:
                dc.preflight_text_channels(
                    g0,
                    client.user,
                    persona_id,
                    "discord_engagement",
                    {"networking": (net_ch, "basic")},
                )
        if guild_want:
            pending = await mongo_db[dc.COL_JOBS].count_documents(
                {"done": False, "kind": "engagement_inactivity_scan"},
            )
            if pending == 0:
                await dc.enqueue_job(
                    mongo_db,
                    "engagement_inactivity_scan",
                    time.time() + 90.0,
                    {"guild_id": int(guild_want)},
                )

    @client.event
    async def on_message(message: discord.Message) -> None:
        if message.author.bot:
            return
        if not message.guild or not dc.guild_matches(message.guild, guild_want):
            return
        gid = int(message.guild.id)
        uid = int(message.author.id)
        await _activity_touch(mongo_db, gid, uid)

        text = (message.content or "").strip()
        low = text.lower()

        if low.startswith("!interests "):
            raw_tags = text[len("!interests ") :].strip()
            tags = [t.strip().lower() for t in raw_tags.replace(";", ",").split(",") if t.strip()]
            coll = mongo_db[dc.COL_ACTIVITY]
            await coll.update_one(
                {"guild_id": gid, "user_id": uid},
                {"$set": {"tags": tags, "networking_opt_in": True, "last_message_ts": time.time()}},
                upsert=True,
            )
            await dc.safe_send(message.channel, persona_id, "Saved your interests: %s" % ", ".join(tags) if tags else "Cleared.")
            return

        if low == "!match" or low.startswith("!match "):
            if not net_ch:
                await dc.safe_send(message.channel, persona_id, "Networking channel is not configured.")
                return
            coll = mongo_db[dc.COL_ACTIVITY]
            me = await coll.find_one({"guild_id": gid, "user_id": uid}) or {}
            tags = [str(t).lower() for t in (me.get("tags") or [])]
            if not me.get("networking_opt_in") or not tags:
                await dc.safe_send(
                    message.channel,
                    persona_id,
                    "Use `!interests tag1, tag2` first (opt-in required for introductions).",
                )
                return
            matches: List[Tuple[int, int]] = []
            others = await coll.find({"guild_id": gid, "networking_opt_in": True}).to_list(length=500)
            for doc in others:
                ouid = int(doc.get("user_id", 0))
                if ouid == uid:
                    continue
                otags = {str(t).lower() for t in (doc.get("tags") or [])}
                overlap = len(set(tags) & otags)
                if overlap > 0:
                    matches.append((overlap, ouid))
            matches.sort(key=lambda x: -x[0])
            ch = message.guild.get_channel(net_ch) if message.guild else None
            if not isinstance(ch, discord.TextChannel):
                await dc.safe_send(message.channel, persona_id, "Networking channel not found.")
                return
            lines: List[str] = []
            for _, ouid in matches[:3]:
                mem = message.guild.get_member(ouid)
                mention = mem.mention if mem else "<@%d>" % ouid
                lines.append("Possible match: %s (overlap on shared interest tags)" % mention)
            msg_body = "\n".join(lines) if lines else "No opt-in members with overlapping tags yet."
            await dc.safe_send(ch, persona_id, "%s asked for intros:\n%s" % (message.author.mention, msg_body))
            return

        if kw_off or not kw_map or not isinstance(message.channel, discord.TextChannel):
            return
        for kw, role_id in kw_map.items():
            try:
                pat = re.compile(r"(?<!\w)%s(?!\w)" % re.escape(kw), re.I)
            except re.error:
                continue
            if not pat.search(text):
                continue
            if not await _kw_cooldown_ok(mongo_db, message.channel.id, kw, kw_cd):
                continue
            role = message.guild.get_role(role_id)
            if not role:
                continue
            await dc.safe_send(
                message.channel,
                persona_id,
                "%s might be relevant for this thread (keyword **%s**)." % (role.mention, kw),
            )
            return


async def discord_engagement_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(
        discord_engagement_install.DISCORD_ENGAGEMENT_SETUP_SCHEMA,
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

    async def on_inactivity(payload: Dict[str, Any]) -> None:
        c = holder.get("c")
        if not isinstance(c, discord.Client) or not guild_want:
            return
        await _scan_inactivity(c, setup, mongo_db, rcx.persona.persona_id, int(guild_want), payload)

    jobs = {"engagement_inactivity_scan": on_inactivity}

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await dc.drain_due_jobs(mongo_db, rcx.persona.persona_id, jobs, limit=20)
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
            bot_main_loop=discord_engagement_main_loop,
            inprocess_tools=TOOLS,
            scenario_fn=scenario_fn,
            install_func=discord_engagement_install.install,
        )
    )


if __name__ == "__main__":
    main()
