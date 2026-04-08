import asyncio
import json
import logging
import os
from typing import Any, Dict, List

import discord
from discord.errors import DiscordException
from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError

from flexus_client_kit import ckit_automation_actions
from flexus_client_kit import ckit_automation_engine
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_crm_members
from flexus_client_kit import ckit_job_queue
from flexus_client_kit import ckit_messages
from flexus_client_kit import ckit_mongo
from flexus_client_kit import ckit_person_domain
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.ckit_automation import DisabledRulesCache, filter_active_rules
from flexus_client_kit.ckit_connector import ChatConnector, NormalizedEvent
from flexus_client_kit.ckit_connector_discord import DiscordConnector
from flexus_client_kit.ckit_connector_discord_gateway import DiscordGatewayConnector
from flexus_client_kit.integrations import fi_discord2 as dc
from flexus_simple_bots.discord_bot import discord_bot_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("discord_bot")


async def _warn_gateway_channel_acl(
    connector: ChatConnector,
    persona_id: str,
    purpose_label: str,
    channel_id: int,
) -> None:
    info = await connector.get_channel(str(channel_id))
    if info is None:
        logger.warning(
            "%s gateway preflight [%s]: channel_id=%s not reachable "
            "(missing, not a guild channel, or guild not allowlisted)",
            persona_id,
            purpose_label,
            channel_id,
        )
        return
    missing = [
        k
        for k in (
            "view_channel",
            "send_messages",
            "read_message_history",
            "manage_messages",
        )
        if k in info and info[k] is False
    ]
    if not missing:
        return
    logger.warning(
        "%s gateway preflight [%s]: channel_id=%s guild_id=%s name=%r missing permissions: %s",
        persona_id,
        purpose_label,
        info.get("channel_id", str(channel_id)),
        info.get("guild_id"),
        info.get("name", ""),
        ",".join(missing),
    )


async def _gateway_discord_channel_acl_preflight(
    connector: ChatConnector,
    persona_id: str,
    watched_channel_ids: set[int],
    setup: Dict[str, Any],
) -> None:
    for cid in sorted(watched_channel_ids):
        await _warn_gateway_channel_acl(connector, persona_id, "watched message_in_channel", cid)
    checklist_cid = dc.parse_snowflake(setup.get("checklist_channel_id", ""))
    if checklist_cid and not dc.setup_truthy(setup.get("disable_checklist_auto_post")):
        await _warn_gateway_channel_acl(connector, persona_id, "checklist_channel", checklist_cid)
    welcome_cid = dc.parse_snowflake(setup.get("welcome_channel_id", ""))
    if welcome_cid:
        await _warn_gateway_channel_acl(connector, persona_id, "welcome_channel", welcome_cid)


BOT_NAME = "discord_bot"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION


def _has_gatekeeper_actions(rules: List[dict]) -> bool:
    """Return True when any published rule contains at least one call_gatekeeper_tool action."""
    for rule in rules:
        actions = rule.get("actions") or []
        if any(isinstance(a, dict) and a.get("type") == "call_gatekeeper_tool" for a in actions):
            return True
    return False

TOOLS: List[Any] = []


def _discord_bot_hosted_bot_token() -> tuple[str, str | None]:
    v = (os.environ.get("FLEXUS_DISCORD_BOT_TOKEN") or "").strip()
    if v:
        return v, "FLEXUS_DISCORD_BOT_TOKEN"
    return "", None


def _decide_use_gateway(base_url_http: str) -> bool:
    """Decide whether to use DiscordGatewayConnector (True) or DiscordConnector (False).

    Decision priority:
    1. FLEXUS_DISCORD_USE_GATEWAY env var (explicit override, truthy/falsy string)
    2. Local dev heuristic: if FLEXUS_API_BASEURL points at localhost → direct socket
    3. Hosted default: if base_url is not localhost → gateway

    This prevents local-only workers from routing events through a gateway subscriber
    that is not running locally, which would produce "no subscribers" log spam and
    silently drop all automation rule executions.
    """
    explicit = os.environ.get("FLEXUS_DISCORD_USE_GATEWAY", "").strip().lower()
    if explicit in ("1", "true", "yes", "on"):
        return True
    if explicit in ("0", "false", "no", "off"):
        return False
    # No explicit override — use the backend URL to detect local dev.
    is_local = "localhost" in base_url_http or "127.0.0.1" in base_url_http
    return not is_local


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


def _guild_ids_from_persona(persona: Any, setup: Dict[str, Any]) -> set[int]:
    """Parse Discord guild IDs from persona_external_addresses (entries like 'discord:<id>').
    Falls back to the legacy dc_guild_id setup field when the list is absent or yields nothing.
    """
    addresses = getattr(persona, "persona_external_addresses", None)
    if isinstance(addresses, list):
        ids: set[int] = set()
        for v in addresses:
            if isinstance(v, str) and v.startswith("discord:"):
                gid = dc.parse_snowflake(v[len("discord:"):])
                if gid is not None:
                    ids.add(gid)
        if ids:
            return ids
    legacy_gid = dc.parse_snowflake(setup.get("dc_guild_id", ""))
    if legacy_gid is not None:
        return {legacy_gid}
    return set()


def _emoji_key(emoji: discord.PartialEmoji | str) -> str:
    if isinstance(emoji, str):
        return emoji
    if emoji.id:
        return "%s:%s" % (emoji.name, emoji.id)
    return emoji.name or ""


def _register_reaction_roles(
    raw_client: discord.Client,
    setup: Dict[str, Any],
    persona_id: str,
    connector: ChatConnector,
) -> None:
    bindings = _parse_bindings(setup.get("reaction_roles_json", "[]"))

    @raw_client.event
    async def on_raw_reaction_add(payload: discord.RawReactionActionEvent) -> None:
        if dc.setup_truthy(setup.get("disable_reaction_roles")):
            return
        if raw_client.user and payload.user_id == raw_client.user.id:
            return
        allowed = connector.allowed_guild_ids
        gid_ev = int(payload.guild_id or 0)
        if not allowed or gid_ev not in allowed:
            return
        guild = raw_client.get_guild(payload.guild_id)
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

    @raw_client.event
    async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent) -> None:
        if dc.setup_truthy(setup.get("disable_reaction_roles")):
            return
        allowed = connector.allowed_guild_ids
        gid_ev = int(payload.guild_id or 0)
        if not allowed or gid_ev not in allowed:
            return
        guild = raw_client.get_guild(payload.guild_id)
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


async def _maybe_auto_post_checklist(
    connector: ChatConnector,
    setup: Dict[str, Any],
    mongo_db: Any,
    persona_id: str,
    guild_ids: set[int],
) -> None:
    bindings = _parse_bindings(setup.get("reaction_roles_json", "[]"))
    rc = connector.raw_client
    if not rc or not guild_ids:
        return
    if dc.setup_truthy(setup.get("disable_checklist_auto_post")):
        return
    cid = dc.parse_snowflake(setup.get("checklist_channel_id", ""))
    if not cid:
        return
    checklist_meta_coll = mongo_db["dc_onboarding_meta"]
    body = (setup.get("checklist_message_body") or "").strip()
    if not body:
        return
    for gid in guild_ids:
        g = rc.get_guild(gid)
        if not g:
            continue
        dc.preflight_text_channels(
            g,
            rc.user,
            persona_id,
            "discord_bot",
            {
                "welcome_channel": (dc.parse_snowflake(setup.get("welcome_channel_id", "")), "basic"),
                "checklist": (cid, "mod"),
            },
            warn_manage_roles=len(bindings) > 0,
        )
        meta_id = "checklist_posted:%s" % gid
        doc = await checklist_meta_coll.find_one({"_id": meta_id})
        if doc and doc.get("message_id"):
            continue
        ch = g.get_channel(cid)
        if not isinstance(ch, discord.TextChannel):
            continue
        msg = await dc.safe_send(ch, persona_id, body)
        if not msg:
            continue
        await checklist_meta_coll.update_one(
            {"_id": meta_id},
            {"$set": {"message_id": str(msg.id), "channel_id": str(cid), "guild_id": str(gid)}},
            upsert=True,
        )
        if dc.setup_truthy(setup.get("pin_checklist")):
            try:
                await msg.pin(reason="start here checklist")
            except DiscordException as e:
                dc.log_ctx(persona_id, g.id, "pin checklist failed: %s %s", type(e).__name__, e)


async def _bootstrap_existing_members(
    raw_client: discord.Client,
    allowed_guild_ids: frozenset[int],
    fclient: ckit_client.FlexusClient,
    workspace_id: str,
    persona_id: str,
) -> None:
    """
    One-shot idempotent sync for members already in the guild when the bot starts.

    Creates/upserts crm_person + crm_person_identity + crm_contact for every
    non-bot member in every allowed guild. Does NOT create crm_application rows
    (those are reserved for new joins). Safe to rerun.

    Only called when raw_client is not None (non-gateway / local-socket path).
    The gateway path has no access to the member list from the worker process.
    """
    total = 0
    for gid in sorted(allowed_guild_ids):
        guild = raw_client.get_guild(gid)
        if guild is None:
            continue
        for member in list(guild.members):
            if member.bot:
                continue
            uid = member.id
            display = member.display_name or member.name or str(uid)
            await ckit_person_domain.ensure_person_for_discord_user(
                fclient,
                workspace_id,
                str(uid),
                display,
            )
            await ckit_person_domain.ensure_discord_contact(
                fclient,
                workspace_id,
                str(uid),
                display,
            )
            total += 1
            await asyncio.sleep(0)  # yield to event loop between members so heartbeats stay alive
    dc.log_ctx(persona_id, None, "member bootstrap complete: %d members synced across %d guilds", total, len(allowed_guild_ids))


async def discord_bot_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    persona_setup_raw = rcx.persona.persona_setup or {}
    setup = ckit_bot_exec.official_setup_mixing_procedure(
        discord_bot_install.DISCORD_BOT_SETUP_SCHEMA,
        persona_setup_raw,
    )
    token, hosted_env = _discord_bot_hosted_bot_token()
    if not token:
        token = dc.discord_bot_api_key_from_external_auth(rcx.external_auth)
        hosted_env = "external_auth" if token else None
    if not token:
        logger.error(
            "%s missing Discord bot token: set FLEXUS_DISCORD_BOT_TOKEN, "
            "or provide legacy external_auth api_key (discord_manual / discord)",
            rcx.persona.persona_id,
        )
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=30.0)
        return

    use_gateway = _decide_use_gateway(fclient.base_url_http)
    if use_gateway:
        logger.info(
            "%s Discord runtime: gateway mode (token source=%s, backend=%s); "
            "guild allowlist from persona_external_addresses; "
            "worker has no Discord socket — ensure service_discord_gateway subscriber is running. "
            "Set FLEXUS_DISCORD_USE_GATEWAY=0 to force direct-socket mode.",
            rcx.persona.persona_id,
            hosted_env,
            fclient.base_url_http,
        )
    else:
        logger.info(
            "%s Discord runtime: direct-socket mode (token source=%s, backend=%s); "
            "DiscordConnector holds the gateway connection in this process. "
            "Set FLEXUS_DISCORD_USE_GATEWAY=1 to force gateway mode.",
            rcx.persona.persona_id,
            hosted_env,
            fclient.base_url_http,
        )

    mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    mongo_db = mongo[rcx.persona.persona_id + "_db"]

    await ckit_crm_members.migrate_legacy_collections(mongo_db)
    await ckit_crm_members.ensure_member_indexes(mongo_db)

    disabled_cache = DisabledRulesCache(mongo_db)
    await disabled_cache.start()

    rules = ckit_automation_engine.load_rules(persona_setup_raw)
    dc.log_ctx(rcx.persona.persona_id, None, "loaded %d automation rules", len(rules))
    scheduled_rules = ckit_automation_engine.find_scheduled_rules(rules)

    watched_channel_ids: set[int] = set()
    for r in rules:
        trig = r.get("trigger", {})
        if trig.get("type") == "message_in_channel":
            cid = ckit_automation_engine.resolve_channel_id(trig.get("channel_id_field", ""), setup)
            if cid is not None:
                watched_channel_ids.add(cid)

    workspace_id = rcx.persona.located_fgroup_id or ""

    if len(rules) == 0:
        dc.log_ctx(rcx.persona.persona_id, None, "no automation rules published, lifecycle automation inactive")

    mod_roles = set(_role_ids_csv(setup.get("mod_role_ids", "")))
    announce_pings = _role_ids_csv(setup.get("announce_ping_role_ids", ""))

    initial_guild_ids = _guild_ids_from_persona(rcx.persona, setup)
    dc.log_ctx(rcx.persona.persona_id, None, "allowed guild ids from persona_external_addresses: %s", sorted(initial_guild_ids))
    if use_gateway:
        connector: ChatConnector = DiscordGatewayConnector(token, rcx.persona.persona_id, initial_guild_ids=initial_guild_ids)
    else:
        connector = DiscordConnector(token, rcx.persona.persona_id, initial_guild_ids=initial_guild_ids)
    await connector.set_allowed_guild_ids(initial_guild_ids)

    augmented_setup = dict(setup)
    augmented_setup["_format_mention"] = connector.format_mention

    await ckit_messages.ensure_message_indexes(mongo_db)

    async def _schedule_scan_after_join(ctx: Dict[str, Any], guild_id: int, user_id: int) -> None:
        if not scheduled_rules:
            return
        fresh_doc = await ckit_crm_members.get_member(mongo_db, guild_id, user_id)
        if fresh_doc is None:
            return
        ctx["member_doc"] = fresh_doc
        for sr in scheduled_rules:
            trig = sr.get("trigger", {})
            anchor_field = trig.get("anchor_field", "")
            delay_seconds = trig.get("delay_seconds", 0)
            if anchor_field and fresh_doc.get(anchor_field) is not None:
                enqueue_action = {
                    "type": "enqueue_check",
                    "check_rule_id": sr["rule_id"],
                    "anchor_field": anchor_field,
                    "delay_seconds": delay_seconds,
                }
                await ckit_automation_actions.execute_actions([enqueue_action], ctx)

    async def handle_normalized_event(event: NormalizedEvent) -> None:
        persona_id = rcx.persona.persona_id
        try:
            if event.event_type in ("server_connected", "server_disconnected"):
                return
            if event.event_type == "member_joined":
                pl = event.payload
                gid = int(pl["guild_id"])
                uid = int(pl["user_id"])
                uname = pl.get("username", "")
                if not isinstance(uname, str):
                    uname = ""
                member_doc = await ckit_crm_members.handle_member_join(
                    mongo_db,
                    gid,
                    uid,
                    workspace_id,
                    uname,
                )

                # Best-effort person domain sync: resolve/create canonical person +
                # discord identity, then register a durable application record.
                # Runs regardless of whether automation rules exist so that even
                # workspaces with zero published rules get a proper foundation record.
                if workspace_id:
                    _has_gk = _has_gatekeeper_actions(rules)
                    person_id = await ckit_person_domain.ensure_person_for_discord_user(
                        fclient,
                        workspace_id,
                        str(uid),
                        uname,
                    )
                    if person_id:
                        existing_app = await ckit_person_domain.application_find_latest(
                            fclient,
                            workspace_id,
                            person_id,
                        )
                        if not existing_app:
                            _sync_app_id = await ckit_person_domain.application_create_pending(
                                fclient,
                                workspace_id,
                                person_id,
                                source="discord_bot",
                                platform="discord",
                                payload={"guild_id": str(gid), "discord_user_id": str(uid)},
                            )
                        else:
                            _sync_app_id = existing_app["application_id"]
                        # When there is no gatekeeper the member is immediately accepted by
                        # handle_member_join (lifecycle_status="accepted"). Advance the
                        # durable application to DECIDED/APPROVED so it stays consistent.
                        if _sync_app_id and not _has_gk:
                            _existing_status = (
                                existing_app["application_status"] if existing_app else "PENDING"
                            )
                            if _existing_status not in ("DECIDED", "CLOSED"):
                                await ckit_person_domain.application_apply_decision(
                                    fclient,
                                    _sync_app_id,
                                    "DECIDED",
                                    "APPROVED",
                                    None,
                                )
                    # Ensure a CRM contact row exists for every joining member,
                    # keyed idempotently by contact_platform_ids.discord.
                    await ckit_person_domain.ensure_discord_contact(
                        fclient,
                        workspace_id,
                        str(uid),
                        uname,
                    )

                if len(rules) == 0:
                    return

                # When gatekeeper rules are configured, start member in pending_review
                # so the AI review decision (accept/reject/request_info) controls progression.
                # Without gatekeeper, preserve the existing "accepted" flow from handle_member_join.
                if _has_gatekeeper_actions(rules):
                    updated_doc, _prev = await ckit_crm_members.set_member_status(
                        mongo_db,
                        gid,
                        uid,
                        "pending_review",
                    )
                    if updated_doc is not None:
                        member_doc = updated_doc

                ctx: Dict[str, Any] = {
                    "connector": connector,
                    "mongo_db": mongo_db,
                    "server_id": event.server_id,
                    "platform_user": await connector.get_user_info(event.user_id, server_id=event.server_id),
                    "member_doc": member_doc,
                    "persona_id": persona_id,
                    "setup": augmented_setup,
                    "fclient": fclient,
                    "ws_id": workspace_id,
                }
                active_rules = filter_active_rules(rules, disabled_cache.get())
                actions = ckit_automation_engine.process_event(
                    "member_joined",
                    {"guild_id": gid, "user_id": uid},
                    active_rules,
                    member_doc,
                    augmented_setup,
                )
                _, field_changes = await ckit_automation_actions.execute_actions(actions, ctx)
                await ckit_automation_actions._run_cascade(
                    db=mongo_db,
                    client=connector.raw_client,
                    persona_id=persona_id,
                    setup=augmented_setup,
                    rules=rules,
                    engine_process_fn=ckit_automation_engine.process_event,
                    ctx=ctx,
                    initial_field_changes=field_changes,
                    guild_id=gid,
                    user_id=uid,
                    disabled_rules_cache=disabled_cache,
                )
                await _schedule_scan_after_join(ctx, gid, uid)
                return

            if event.event_type == "message_in_channel":
                pl = event.payload
                content = (pl.get("content") or "").strip()
                if content.lower().startswith("!announce ") and mod_roles:
                    rc_ann = connector.raw_client
                    if rc_ann is None:
                        return
                    try:
                        gid_ann = int(pl.get("guild_id", 0) or 0)
                    except (TypeError, ValueError):
                        gid_ann = 0
                    g0 = rc_ann.get_guild(gid_ann) if gid_ann else None
                    if g0 is not None:
                        try:
                            uid_int = int(event.user_id)
                        except (TypeError, ValueError):
                            uid_int = 0
                        member = g0.get_member(uid_int) if uid_int else None
                        if member and not member.bot:
                            author_roles = {r.id for r in member.roles}
                            if author_roles.intersection(mod_roles):
                                rest = content[len("!announce ") :].strip()
                                if rest:
                                    pings = " ".join("<@&%d>" % r for r in announce_pings)
                                    text = "%s\n%s" % (pings, rest) if pings else rest
                                    cid_str = str(pl.get("channel_id", ""))
                                    await connector.execute_action(
                                        "post_to_channel",
                                        {
                                            "channel_id": cid_str,
                                            "text": text,
                                            "server_id": str(gid_ann),
                                        },
                                    )
                    return

                if len(rules) == 0:
                    return
                gid = int(pl["guild_id"])
                uid = int(pl["user_id"])
                ch_id = int(pl["channel_id"])
                await ckit_crm_members.handle_message(mongo_db, gid, uid)
                if ch_id in watched_channel_ids:
                    await ckit_messages.store_message(
                        mongo_db,
                        server_id=event.server_id,
                        channel_id=str(ch_id),
                        user_id=str(uid),
                        platform="discord",
                        content=pl.get("content") or "",
                        timestamp=event.timestamp,
                        message_id=str(pl.get("message_id") or ""),
                    )
                if ch_id not in watched_channel_ids:
                    return
                member_doc = await ckit_crm_members.get_member(mongo_db, gid, uid)
                if member_doc is None:
                    return
                ctx_msg: Dict[str, Any] = {
                    "connector": connector,
                    "mongo_db": mongo_db,
                    "server_id": event.server_id,
                    "platform_user": await connector.get_user_info(event.user_id, server_id=event.server_id),
                    "member_doc": member_doc,
                    "persona_id": persona_id,
                    "setup": augmented_setup,
                    "fclient": fclient,
                    "ws_id": workspace_id,
                }
                active_rules = filter_active_rules(rules, disabled_cache.get())
                actions = ckit_automation_engine.process_event(
                    "message_in_channel",
                    {"guild_id": gid, "user_id": uid, "channel_id": ch_id},
                    active_rules,
                    member_doc,
                    augmented_setup,
                )
                _, field_changes = await ckit_automation_actions.execute_actions(actions, ctx_msg)
                await ckit_automation_actions._run_cascade(
                    db=mongo_db,
                    client=connector.raw_client,
                    persona_id=persona_id,
                    setup=augmented_setup,
                    rules=rules,
                    engine_process_fn=ckit_automation_engine.process_event,
                    ctx=ctx_msg,
                    initial_field_changes=field_changes,
                    guild_id=gid,
                    user_id=uid,
                    disabled_rules_cache=disabled_cache,
                )
                return

            if event.event_type == "member_removed":
                pl = event.payload
                gid = int(pl["guild_id"])
                uid = int(pl["user_id"])
                old_status, _new_status = await ckit_crm_members.handle_member_remove(mongo_db, gid, uid)
                if len(rules) == 0:
                    return
                member_doc = await ckit_crm_members.get_member(mongo_db, gid, uid)
                if member_doc is None:
                    return
                ctx_rm: Dict[str, Any] = {
                    "connector": connector,
                    "mongo_db": mongo_db,
                    "server_id": event.server_id,
                    "platform_user": await connector.get_user_info(event.user_id, server_id=event.server_id),
                    "member_doc": member_doc,
                    "persona_id": persona_id,
                    "setup": augmented_setup,
                    "fclient": fclient,
                    "ws_id": workspace_id,
                }
                active_rules = filter_active_rules(rules, disabled_cache.get())
                actions_leave = ckit_automation_engine.process_event(
                    "member_removed",
                    {"guild_id": gid, "user_id": uid},
                    active_rules,
                    member_doc,
                    augmented_setup,
                )
                _, fc_leave = await ckit_automation_actions.execute_actions(actions_leave, ctx_rm)
                await ckit_automation_actions._run_cascade(
                    db=mongo_db,
                    client=connector.raw_client,
                    persona_id=persona_id,
                    setup=augmented_setup,
                    rules=rules,
                    engine_process_fn=ckit_automation_engine.process_event,
                    ctx=ctx_rm,
                    initial_field_changes=fc_leave,
                    guild_id=gid,
                    user_id=uid,
                    disabled_rules_cache=disabled_cache,
                )
                if old_status is None:
                    return
                member_doc_st = await ckit_crm_members.get_member(mongo_db, gid, uid)
                if member_doc_st is None:
                    return
                ctx_rm["member_doc"] = member_doc_st
                actions = ckit_automation_engine.process_event(
                    "status_transition",
                    {"old_status": old_status, "new_status": "churned"},
                    active_rules,
                    member_doc_st,
                    augmented_setup,
                )
                _, field_changes = await ckit_automation_actions.execute_actions(actions, ctx_rm)
                await ckit_automation_actions._run_cascade(
                    db=mongo_db,
                    client=connector.raw_client,
                    persona_id=persona_id,
                    setup=augmented_setup,
                    rules=rules,
                    engine_process_fn=ckit_automation_engine.process_event,
                    ctx=ctx_rm,
                    initial_field_changes=field_changes,
                    guild_id=gid,
                    user_id=uid,
                    disabled_rules_cache=disabled_cache,
                )
                return
        except PyMongoError as e:
            gid_log = None
            try:
                gid_log = int(event.payload.get("guild_id", 0) or 0) or None
            except (TypeError, ValueError):
                gid_log = None
            dc.log_ctx(persona_id, gid_log, "normalized event PyMongoError: %s %s", type(e).__name__, e)
        except DiscordException as e:
            gid_log = None
            try:
                gid_log = int(event.payload.get("guild_id", 0) or 0) or None
            except (TypeError, ValueError):
                gid_log = None
            dc.log_ctx(persona_id, gid_log, "normalized event DiscordException: %s %s", type(e).__name__, e)
        except (TypeError, KeyError, ValueError) as e:
            gid_log = None
            try:
                gid_log = int(event.payload.get("guild_id", 0) or 0) or None
            except (TypeError, ValueError):
                gid_log = None
            dc.log_ctx(persona_id, gid_log, "normalized event data error: %s %s", type(e).__name__, e)

    connector.on_event(handle_normalized_event)
    await connector.connect()

    if use_gateway:
        await _gateway_discord_channel_acl_preflight(
            connector,
            rcx.persona.persona_id,
            watched_channel_ids,
            setup,
        )

    raw = connector.raw_client
    # Optional single-guild fallback: in direct-socket mode only, if persona_external_addresses
    # has no guild IDs configured but the bot token can see exactly one guild, use that guild
    # automatically. Strictly bounded to the "exactly one guild visible" case so it cannot
    # silently pick the wrong server when multiple guilds are present.
    if not use_gateway and raw is not None and not connector.allowed_guild_ids:
        visible = list(raw.guilds)
        if len(visible) == 1:
            fallback_id = int(visible[0].id)
            logger.warning(
                "%s direct-socket mode: no guild configured in persona_external_addresses; "
                "bot token sees exactly one guild (%d / %r) — using it as fallback. "
                "Add discord:%d to persona_external_addresses to silence this warning.",
                rcx.persona.persona_id,
                fallback_id,
                visible[0].name,
                fallback_id,
            )
            await connector.set_allowed_guild_ids({fallback_id})
        elif len(visible) > 1:
            logger.warning(
                "%s direct-socket mode: no guild configured in persona_external_addresses "
                "and bot token sees %d guilds — cannot auto-select. "
                "Add discord:<guild_id> to persona_external_addresses.",
                rcx.persona.persona_id,
                len(visible),
            )

    if raw is not None:
        _register_reaction_roles(raw, setup, rcx.persona.persona_id, connector)

    checklist_ready_done = False
    bootstrap_done = False
    automation_handlers_built = False
    job_handlers: Dict[str, Any] = {}

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            if not checklist_ready_done and connector.raw_client is not None:
                await _maybe_auto_post_checklist(
                    connector,
                    setup,
                    mongo_db,
                    rcx.persona.persona_id,
                    set(connector.allowed_guild_ids),
                )
                checklist_ready_done = True
            if not bootstrap_done and connector.raw_client is not None and workspace_id:
                # Fire-and-forget: run bootstrap in the background so the main
                # loop keeps processing events while members are being synced.
                asyncio.create_task(
                    _bootstrap_existing_members(
                        connector.raw_client,
                        connector.allowed_guild_ids,
                        fclient,
                        workspace_id,
                        rcx.persona.persona_id,
                    )
                )
                bootstrap_done = True
            if not automation_handlers_built and len(rules) > 0:
                job_handlers = ckit_automation_actions.make_automation_job_handler(
                    rules,
                    augmented_setup,
                    ckit_automation_engine.process_event,
                    mongo_db,
                    connector.raw_client,
                    rcx.persona.persona_id,
                    disabled_rules_cache=disabled_cache,
                    connector=connector,
                    fclient=fclient,
                    ws_id=workspace_id,
                )
                automation_handlers_built = True
            await ckit_job_queue.drain_due_jobs(mongo_db, rcx.persona.persona_id, job_handlers, limit=30)
            await rcx.unpark_collected_events(sleep_if_no_work=5.0)
    finally:
        await disabled_cache.stop()
        await connector.disconnect()
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
            bot_main_loop=discord_bot_main_loop,
            inprocess_tools=TOOLS,
            scenario_fn=scenario_fn,
            install_func=discord_bot_install.install,
        )
    )


if __name__ == "__main__":
    main()
