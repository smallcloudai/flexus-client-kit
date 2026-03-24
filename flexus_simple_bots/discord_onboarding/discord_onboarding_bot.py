import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import discord
from discord.errors import DiscordException
from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_mongo
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_discord_community as dc
from flexus_simple_bots.discord_onboarding import discord_onboarding_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("discord_onboarding")


BOT_NAME = "discord_onboarding"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

TOOLS: List[Any] = []


def _parse_bindings(raw: str) -> List[Dict[str, str]]:
    try:
        v = json.loads(raw or "[]")
    except json.JSONDecodeError:
        return []
    if not isinstance(v, list):
        return []
    out: List[Dict[str, str]] = []
    for item in v:
        if not isinstance(item, dict):
            continue
        mid = str(item.get("message_id", "")).strip()
        emo = str(item.get("emoji", "")).strip()
        rid = str(item.get("role_id", "")).strip()
        if mid and emo and rid:
            out.append({"message_id": mid, "emoji": emo, "role_id": rid})
    return out


def _role_ids_csv(s: str) -> List[int]:
    out: List[int] = []
    for part in (s or "").split(","):
        p = part.strip()
        if p.isdigit():
            out.append(int(p))
    return out


def _emoji_key(emoji: discord.PartialEmoji | str) -> str:
    if isinstance(emoji, str):
        return emoji
    if emoji.id:
        return "%s:%s" % (emoji.name, emoji.id)
    return emoji.name or ""


async def _followup_handler(
    client: discord.Client,
    setup: Dict[str, Any],
    mongo_db: Any,
    persona_id: str,
    payload: Dict[str, Any],
) -> None:
    gid = payload.get("guild_id")
    uid = payload.get("user_id")
    if gid is None or uid is None:
        return
    guild = client.get_guild(int(gid))
    if not guild:
        return
    coll = mongo_db[dc.COL_ONBOARDING]
    doc = await coll.find_one({"guild_id": int(gid), "user_id": int(uid)})
    if not doc or doc.get("engaged") or doc.get("followup_sent"):
        return
    body = (setup.get("followup_dm_body") or "").strip()
    if not body:
        return
    if dc.setup_truthy(setup.get("dry_run_followup")):
        dc.log_ctx(persona_id, int(gid), "dry_run_followup user=%s (no DM)", uid)
        await coll.update_one(
            {"guild_id": int(gid), "user_id": int(uid)},
            {"$set": {"followup_sent": True, "followup_ts": time.time(), "dry_run": True}},
            upsert=True,
        )
        return
    m = guild.get_member(int(uid))
    if not m:
        try:
            m = await guild.fetch_member(int(uid))
        except DiscordException:
            return
    ok = await dc.safe_dm(client, m, persona_id, body)
    await coll.update_one(
        {"guild_id": int(gid), "user_id": int(uid)},
        {"$set": {"followup_sent": bool(ok), "followup_ts": time.time()}},
        upsert=True,
    )


def _register_discord(
    client: discord.Client,
    setup: Dict[str, Any],
    mongo_db: Any,
    persona_id: str,
    guild_want: Optional[int],
) -> None:
    bindings = _parse_bindings(setup.get("reaction_roles_json", "[]"))
    mod_roles = set(_role_ids_csv(setup.get("mod_role_ids", "")))
    announce_pings = _role_ids_csv(setup.get("announce_ping_role_ids", ""))
    checklist_meta_coll = mongo_db["dc_onboarding_meta"]

    @client.event
    async def on_ready() -> None:
        dc.log_ctx(persona_id, None, "discord ready as %s", client.user)
        if guild_want and client.user:
            g0 = client.get_guild(int(guild_want))
            if g0:
                dc.preflight_text_channels(
                    g0,
                    client.user,
                    persona_id,
                    "discord_onboarding",
                    {
                        "welcome_channel": (dc.parse_snowflake(setup.get("welcome_channel_id", "")), "basic"),
                        "checklist": (dc.parse_snowflake(setup.get("checklist_channel_id", "")), "mod"),
                    },
                    warn_manage_roles=len(bindings) > 0,
                )
        if dc.setup_truthy(setup.get("disable_checklist_auto_post")):
            return
        cid = dc.parse_snowflake(setup.get("checklist_channel_id", ""))
        if not cid or not guild_want:
            return
        g = client.get_guild(int(guild_want))
        if not g:
            return
        doc = await checklist_meta_coll.find_one({"_id": "checklist_posted"})
        if doc and doc.get("message_id"):
            return
        ch = g.get_channel(cid)
        if not isinstance(ch, discord.TextChannel):
            return
        body = (setup.get("checklist_message_body") or "").strip()
        if not body:
            return
        msg = await dc.safe_send(ch, persona_id, body)
        if not msg:
            return
        await checklist_meta_coll.update_one(
            {"_id": "checklist_posted"},
            {"$set": {"message_id": str(msg.id), "channel_id": str(cid)}},
            upsert=True,
        )
        if dc.setup_truthy(setup.get("pin_checklist")):
            try:
                await msg.pin(reason="start here checklist")
            except DiscordException as e:
                dc.log_ctx(persona_id, g.id, "pin checklist failed: %s %s", type(e).__name__, e)

    @client.event
    async def on_member_join(member: discord.Member) -> None:
        if not dc.guild_matches(member.guild, guild_want):
            return
        if member.bot:
            return
        coll = mongo_db[dc.COL_ONBOARDING]
        now = time.time()
        await coll.update_one(
            {"guild_id": int(member.guild.id), "user_id": int(member.id)},
            {
                "$set": {
                    "joined_ts": now,
                    "engaged": False,
                    "followup_sent": False,
                }
            },
            upsert=True,
        )
        dm_body = (setup.get("welcome_dm_body") or "").strip()
        if dm_body and not dc.setup_truthy(setup.get("disable_welcome_dm")):
            await dc.safe_dm(client, member, persona_id, dm_body)
        wch = dc.parse_snowflake(setup.get("welcome_channel_id", ""))
        if wch:
            ch = member.guild.get_channel(wch)
            if isinstance(ch, discord.TextChannel):
                pub = (setup.get("welcome_channel_body") or "Welcome {mention}!").replace("{mention}", member.mention)
                await dc.safe_send(ch, persona_id, pub)
        days = int(setup.get("followup_days") or 2)
        if days > 0:
            await dc.enqueue_job(
                mongo_db,
                "onboarding_followup",
                now + float(days) * 86400.0,
                {"guild_id": int(member.guild.id), "user_id": int(member.id), "persona_id": persona_id},
            )

    @client.event
    async def on_message(message: discord.Message) -> None:
        if message.author.bot:
            return
        if not message.guild or not dc.guild_matches(message.guild, guild_want):
            return
        if isinstance(message.channel, discord.DMChannel):
            return
        content = (message.content or "").strip()
        if content.lower().startswith("!announce ") and mod_roles:
            author_roles = {r.id for r in message.author.roles}
            if not author_roles.intersection(mod_roles):
                return
            rest = content[len("!announce ") :].strip()
            if not rest:
                return
            pings = " ".join("<@&%d>" % r for r in announce_pings)
            text = "%s\n%s" % (pings, rest) if pings else rest
            await dc.safe_send(message.channel, persona_id, text)
            return
        coll = mongo_db[dc.COL_ONBOARDING]
        await coll.update_one(
            {"guild_id": int(message.guild.id), "user_id": int(message.author.id)},
            {"$set": {"engaged": True, "last_message_ts": time.time()}},
            upsert=True,
        )

    @client.event
    async def on_raw_reaction_add(payload: discord.RawReactionActionEvent) -> None:
        if dc.setup_truthy(setup.get("disable_reaction_roles")):
            return
        if client.user and payload.user_id == client.user.id:
            return
        if guild_want and int(payload.guild_id or 0) != int(guild_want):
            return
        guild = client.get_guild(payload.guild_id)
        if not guild:
            return
        mid = str(payload.message_id)
        key = _emoji_key(payload.emoji)
        for b in bindings:
            if b["message_id"] != mid:
                continue
            if b["emoji"] != key and b["emoji"] != getattr(payload.emoji, "name", None):
                continue
            role = guild.get_role(int(b["role_id"]))
            if not role:
                return
            member = guild.get_member(payload.user_id)
            if not member or member.bot:
                return
            try:
                await member.add_roles(role, reason="reaction role")
            except DiscordException as e:
                dc.log_ctx(persona_id, guild.id, "add_roles failed: %s %s", type(e).__name__, e)

    @client.event
    async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent) -> None:
        if dc.setup_truthy(setup.get("disable_reaction_roles")):
            return
        if guild_want and int(payload.guild_id or 0) != int(guild_want):
            return
        guild = client.get_guild(payload.guild_id)
        if not guild:
            return
        mid = str(payload.message_id)
        key = _emoji_key(payload.emoji)
        for b in bindings:
            if b["message_id"] != mid:
                continue
            if b["emoji"] != key and b["emoji"] != getattr(payload.emoji, "name", None):
                continue
            role = guild.get_role(int(b["role_id"]))
            if not role:
                return
            member = guild.get_member(payload.user_id)
            if not member or member.bot:
                return
            try:
                await member.remove_roles(role, reason="reaction role remove")
            except DiscordException as e:
                dc.log_ctx(persona_id, guild.id, "remove_roles failed: %s %s", type(e).__name__, e)


async def discord_onboarding_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(discord_onboarding_install.DISCORD_ONBOARDING_SETUP_SCHEMA, rcx.persona.persona_setup)
    token = dc.discord_bot_api_key_from_external_auth(rcx.external_auth)
    if not token:
        logger.error("%s missing discord api_key in external_auth", rcx.persona.persona_id)
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=30.0)
        return

    mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    mongo_db = mongo[rcx.persona.persona_id + "_db"]

    guild_want = dc.parse_snowflake(setup.get("dc_guild_id", ""))

    client_holder: Dict[str, Any] = {"c": None, "t": None}

    def register(cl: discord.Client) -> None:
        client_holder["c"] = cl
        _register_discord(cl, setup, mongo_db, rcx.persona.persona_id, guild_want)

    cl, task = await dc.start_discord_client(token, rcx.persona.persona_id, register)
    client_holder["t"] = task

    async def on_followup(payload: Dict[str, Any]) -> None:
        c = client_holder.get("c")
        if isinstance(c, discord.Client):
            await _followup_handler(c, setup, mongo_db, rcx.persona.persona_id, payload)

    job_handlers = {"onboarding_followup": on_followup}

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await dc.drain_due_jobs(mongo_db, rcx.persona.persona_id, job_handlers, limit=30)
            await rcx.unpark_collected_events(sleep_if_no_work=5.0)
    finally:
        await dc.close_discord_client(client_holder.get("c"), client_holder.get("t"))
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
            bot_main_loop=discord_onboarding_main_loop,
            inprocess_tools=TOOLS,
            scenario_fn=scenario_fn,
            install_func=discord_onboarding_install.install,
        )
    )


if __name__ == "__main__":
    main()
