import asyncio
import json
import logging
import os
from typing import Any, Dict, List

from discord.errors import DiscordException
from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError

from flexus_client_kit import ckit_automation_actions
from flexus_client_kit import ckit_automation_engine
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_messages
from flexus_client_kit import ckit_mongo
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.ckit_connector import ChatConnector, NormalizedEvent
from flexus_client_kit.ckit_connector_discord_gateway import DiscordGatewayConnector
from flexus_client_kit.gateway.ckit_gateway_wire import normalized_event_from_dict
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
    """Log when the gateway cannot see a channel or the bot lacks common text permissions."""
    try:
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
    except (TypeError, ValueError, AttributeError) as e:
        logger.warning(
            "%s gateway preflight [%s] failed: %s %s",
            persona_id,
            purpose_label,
            type(e).__name__,
            e,
        )


async def _gateway_discord_channel_acl_preflight(
    connector: ChatConnector,
    persona_id: str,
    watched_channel_ids: set[int],
    setup: Dict[str, Any],
) -> None:
    """Best-effort permission warnings for watched channels and checklist/welcome targets."""
    try:
        for cid in sorted(watched_channel_ids):
            await _warn_gateway_channel_acl(connector, persona_id, "watched message_in_channel", cid)
        checklist_cid = dc.parse_snowflake(setup.get("checklist_channel_id", ""))
        if checklist_cid and not dc.setup_truthy(setup.get("disable_checklist_auto_post")):
            await _warn_gateway_channel_acl(connector, persona_id, "checklist_channel", checklist_cid)
        welcome_cid = dc.parse_snowflake(setup.get("welcome_channel_id", ""))
        if welcome_cid:
            await _warn_gateway_channel_acl(connector, persona_id, "welcome_channel", welcome_cid)
    except (TypeError, ValueError) as e:
        logger.warning("%s acl preflight error: %s %s", persona_id, type(e).__name__, e)


BOT_NAME = "discord_bot"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION


TOOLS: List[Any] = []


def _discord_bot_hosted_bot_token() -> tuple[str, str | None]:
    """Return (token, env var name) when FLEXUS_DISCORD_BOT_TOKEN is set."""
    try:
        v = (os.environ.get("FLEXUS_DISCORD_BOT_TOKEN") or "").strip()
        if v:
            return v, "FLEXUS_DISCORD_BOT_TOKEN"
        return "", None
    except (TypeError, AttributeError):
        return "", None


def _parse_bindings(raw: str) -> List[Dict[str, str]]:
    """Parse reaction_roles_json: [{message_id, emoji, role_id}, ...]."""
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
    """Parse comma-separated snowflakes from setup (e.g. mod roles)."""
    out: List[int] = []
    for part in (s or "").split(","):
        p = part.strip()
        if p.isdigit():
            out.append(int(p))
    return out


def _guild_ids_from_persona(persona: Any, setup: Dict[str, Any]) -> set[int]:
    """Guild allowlist from persona_external_addresses discord:<id> or legacy dc_guild_id."""
    try:
        addresses = getattr(persona, "persona_external_addresses", None)
        if isinstance(addresses, list):
            ids: set[int] = set()
            for v in addresses:
                if isinstance(v, str) and v.startswith("discord:"):
                    gid = dc.parse_snowflake(v[len("discord:") :])
                    if gid is not None:
                        ids.add(gid)
            if ids:
                return ids
        legacy_gid = dc.parse_snowflake(setup.get("dc_guild_id", ""))
        if legacy_gid is not None:
            return {legacy_gid}
        return set()
    except (TypeError, ValueError, AttributeError):
        return set()


def _event_member_dict(guild_id: int, user_id: int, pl: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal member snapshot for the automation engine and actions (templates, role tools).

    Loaded from the normalized Discord payload only — nothing persisted on the worker.
    """
    uname = pl.get("username", "")
    if not isinstance(uname, str):
        uname = ""
    return {
        "guild_id": guild_id,
        "user_id": user_id,
        "discord_username": uname,
    }


async def _maybe_gateway_auto_post_checklist(
    connector: ChatConnector,
    setup: Dict[str, Any],
    mongo_db: Any,
    persona_id: str,
    pl: Dict[str, Any],
    allowed_guild_ids: frozenset[int],
) -> None:
    """
    One-time checklist message per guild via gateway post_to_channel + dc_onboarding_meta marker.

    Replaces the old raw-client path that called channel.send locally.
    """
    try:
        if dc.setup_truthy(setup.get("disable_checklist_auto_post")):
            return
        gid = int(pl.get("guild_id", 0) or 0)
        if not gid or (allowed_guild_ids and gid not in allowed_guild_ids):
            return
        cid = dc.parse_snowflake(setup.get("checklist_channel_id", ""))
        if not cid:
            return
        body = (setup.get("checklist_message_body") or "").strip()
        if not body:
            return
        checklist_meta_coll = mongo_db["dc_onboarding_meta"]
        meta_id = "checklist_posted:%s" % gid
        doc = await checklist_meta_coll.find_one({"_id": meta_id})
        if doc and doc.get("posted"):
            return
        result = await connector.execute_action(
            "post_to_channel",
            {
                "channel_id": str(cid),
                "text": body,
                "server_id": str(gid),
            },
        )
        if not result.ok:
            dc.log_ctx(persona_id, gid, "checklist auto-post failed: %s", result.error or "unknown")
            return
        extra: Dict[str, Any] = {"posted": True, "channel_id": str(cid), "guild_id": str(gid)}
        data = getattr(result, "data", None)
        if isinstance(data, dict) and data.get("message_id"):
            extra["message_id"] = data["message_id"]
        await checklist_meta_coll.update_one({"_id": meta_id}, {"$set": extra}, upsert=True)
    except PyMongoError as e:
        dc.log_ctx(persona_id, None, "checklist meta PyMongoError: %s %s", type(e).__name__, e)
    except (TypeError, ValueError, KeyError) as e:
        dc.log_ctx(persona_id, None, "checklist auto-post error: %s %s", type(e).__name__, e)


async def _handle_reaction_binding_event(
    connector: ChatConnector,
    setup: Dict[str, Any],
    persona_id: str,
    event_type: str,
    pl: Dict[str, Any],
) -> None:
    """
    Apply reaction_roles_json using gateway add_role/remove_role (reaction_* events from service_discord_gateway).
    """
    try:
        if dc.setup_truthy(setup.get("disable_reaction_roles")):
            return
        try:
            gid = int(pl.get("guild_id", 0) or 0)
            uid = int(pl.get("user_id", 0) or 0)
        except (TypeError, ValueError):
            return
        if not gid or not uid:
            return
        mid = str(pl.get("message_id", "") or "")
        key = str(pl.get("emoji", "") or "")
        if not mid or not key:
            return
        bindings = _parse_bindings(setup.get("reaction_roles_json", "[]"))
        for b in bindings:
            if b["message_id"] != mid:
                continue
            if b["emoji"] != key:
                continue
            act = "add_role" if event_type == "reaction_added" else "remove_role"
            result = await connector.execute_action(
                act,
                {
                    "user_id": str(uid),
                    "role_id": b["role_id"],
                    "server_id": str(gid),
                },
            )
            if not result.ok:
                dc.log_ctx(persona_id, gid, "reaction role %s failed: %s", act, result.error or "unknown")
            return
    except (TypeError, ValueError, KeyError) as e:
        dc.log_ctx(persona_id, None, "reaction binding error: %s %s", type(e).__name__, e)


async def discord_bot_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    """Discord community bot: gateway-only ingress (on_emessage DISCORD); no in-process Discord socket."""
    connector: ChatConnector | None = None
    mongo: Any = None
    persona_id_loop = rcx.persona.persona_id
    try:
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

        logger.info(
            "%s Discord runtime: gateway-only (token source=%s, backend=%s); "
            "ingress via on_emessage(DISCORD); service_discord_gateway must be running.",
            rcx.persona.persona_id,
            hosted_env,
            fclient.base_url_http,
        )

        mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
        mongo = AsyncMongoClient(mongo_conn_str)
        mongo_db = mongo[persona_id_loop + "_db"]

        rules = ckit_automation_engine.load_rules(persona_setup_raw)
        dc.log_ctx(rcx.persona.persona_id, None, "loaded %d automation rules", len(rules))

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

        gw = DiscordGatewayConnector(
            token,
            rcx.persona.persona_id,
            fclient,
            initial_guild_ids=initial_guild_ids,
        )
        connector = gw

        augmented_setup = dict(setup)
        augmented_setup["_format_mention"] = connector.format_mention

        await ckit_messages.ensure_message_indexes(mongo_db)

        async def handle_normalized_event(event: NormalizedEvent) -> None:
            """Dispatch one gateway-normalized Discord event (member, message, checklist, reactions)."""
            try:
                persona_id = rcx.persona.persona_id
                pl = event.payload if isinstance(event.payload, dict) else {}

                if event.event_type == "server_connected":
                    await _maybe_gateway_auto_post_checklist(
                        connector,
                        setup,
                        mongo_db,
                        persona_id,
                        pl,
                        connector.allowed_guild_ids,
                    )
                    return

                if event.event_type in ("server_disconnected",):
                    return

                if event.event_type in ("reaction_added", "reaction_removed"):
                    await _handle_reaction_binding_event(connector, setup, persona_id, event.event_type, pl)
                    return

                if event.event_type == "member_joined":
                    try:
                        gid = int(pl["guild_id"])
                        uid = int(pl["user_id"])
                    except (KeyError, TypeError, ValueError):
                        return
                    event_member = _event_member_dict(gid, uid, pl)

                    if len(rules) == 0:
                        return

                    ctx: Dict[str, Any] = {
                        "connector": connector,
                        "mongo_db": mongo_db,
                        "server_id": event.server_id,
                        "platform_user": await connector.get_user_info(event.user_id, server_id=event.server_id),
                        "event_member": event_member,
                        "persona_id": persona_id,
                        "setup": augmented_setup,
                        "fclient": fclient,
                        "ws_id": workspace_id,
                    }
                    actions = ckit_automation_engine.process_event(
                        "member_joined",
                        {"guild_id": gid, "user_id": uid},
                        rules,
                        event_member,
                        augmented_setup,
                    )
                    await ckit_automation_actions.execute_actions(actions, ctx)
                    return

                if event.event_type == "message_in_channel":
                    pl_msg = event.payload if isinstance(event.payload, dict) else {}
                    content = (pl_msg.get("content") or "").strip()
                    if content.lower().startswith("!announce ") and mod_roles:
                        try:
                            gid_ann = int(pl_msg.get("guild_id", 0) or 0)
                        except (TypeError, ValueError):
                            gid_ann = 0
                        try:
                            uid_int = int(event.user_id)
                        except (TypeError, ValueError):
                            uid_int = 0
                        if gid_ann and uid_int:
                            info = await connector.get_user_info(str(uid_int), server_id=str(gid_ann))
                            if isinstance(info, dict):
                                raw_roles = info.get("role_ids") or []
                                author_roles = set()
                                for x in raw_roles:
                                    try:
                                        author_roles.add(int(x))
                                    except (TypeError, ValueError):
                                        continue
                                if author_roles.intersection(mod_roles):
                                    rest = content[len("!announce ") :].strip()
                                    if rest:
                                        pings = " ".join("<@&%d>" % r for r in announce_pings)
                                        text = "%s\n%s" % (pings, rest) if pings else rest
                                        cid_str = str(pl_msg.get("channel_id", ""))
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
                    try:
                        gid = int(pl_msg["guild_id"])
                        uid = int(pl_msg["user_id"])
                        ch_id = int(pl_msg["channel_id"])
                    except (KeyError, TypeError, ValueError):
                        return

                    if ch_id in watched_channel_ids:
                        await ckit_messages.store_message(
                            mongo_db,
                            server_id=event.server_id,
                            channel_id=str(ch_id),
                            user_id=str(uid),
                            platform="discord",
                            content=pl_msg.get("content") or "",
                            timestamp=event.timestamp,
                            message_id=str(pl_msg.get("message_id") or ""),
                        )
                    if ch_id not in watched_channel_ids:
                        return

                    event_member = _event_member_dict(gid, uid, pl_msg)
                    ctx_msg: Dict[str, Any] = {
                        "connector": connector,
                        "mongo_db": mongo_db,
                        "server_id": event.server_id,
                        "platform_user": await connector.get_user_info(event.user_id, server_id=event.server_id),
                        "event_member": event_member,
                        "persona_id": persona_id,
                        "setup": augmented_setup,
                        "fclient": fclient,
                        "ws_id": workspace_id,
                    }
                    actions = ckit_automation_engine.process_event(
                        "message_in_channel",
                        {"guild_id": gid, "user_id": uid, "channel_id": ch_id},
                        rules,
                        event_member,
                        augmented_setup,
                    )
                    await ckit_automation_actions.execute_actions(actions, ctx_msg)
                    return

                if event.event_type == "member_removed":
                    if len(rules) == 0:
                        return
                    try:
                        gid = int(pl["guild_id"])
                        uid = int(pl["user_id"])
                    except (KeyError, TypeError, ValueError):
                        return
                    event_member = _event_member_dict(gid, uid, pl)
                    ctx_rm: Dict[str, Any] = {
                        "connector": connector,
                        "mongo_db": mongo_db,
                        "server_id": event.server_id,
                        "platform_user": await connector.get_user_info(event.user_id, server_id=event.server_id),
                        "event_member": event_member,
                        "persona_id": persona_id,
                        "setup": augmented_setup,
                        "fclient": fclient,
                        "ws_id": workspace_id,
                    }
                    actions_leave = ckit_automation_engine.process_event(
                        "member_removed",
                        {"guild_id": gid, "user_id": uid},
                        rules,
                        event_member,
                        augmented_setup,
                    )
                    await ckit_automation_actions.execute_actions(actions_leave, ctx_rm)
                    return
            except PyMongoError as e:
                gid_log = None
                try:
                    payload = event.payload if isinstance(event.payload, dict) else {}
                    gid_log = int(payload.get("guild_id", 0) or 0) or None
                except (TypeError, ValueError):
                    gid_log = None
                dc.log_ctx(rcx.persona.persona_id, gid_log, "normalized event PyMongoError: %s %s", type(e).__name__, e)
            except DiscordException as e:
                gid_log = None
                try:
                    payload = event.payload if isinstance(event.payload, dict) else {}
                    gid_log = int(payload.get("guild_id", 0) or 0) or None
                except (TypeError, ValueError):
                    gid_log = None
                dc.log_ctx(rcx.persona.persona_id, gid_log, "normalized event DiscordException: %s %s", type(e).__name__, e)
            except (TypeError, KeyError, ValueError) as e:
                gid_log = None
                try:
                    payload = event.payload if isinstance(event.payload, dict) else {}
                    gid_log = int(payload.get("guild_id", 0) or 0) or None
                except (TypeError, ValueError):
                    gid_log = None
                dc.log_ctx(rcx.persona.persona_id, gid_log, "normalized event data error: %s %s", type(e).__name__, e)

        @rcx.on_emessage("DISCORD")
        async def _on_discord_emessage(emsg) -> None:
            """Inbound path: backend delivers gateway-normalized Discord payloads here."""
            try:
                ev = normalized_event_from_dict(emsg.emsg_payload)
            except (KeyError, TypeError, ValueError) as e:
                logger.warning(
                    "%s discord emessage parse error: %s %s",
                    rcx.persona.persona_id,
                    type(e).__name__,
                    e,
                )
                return
            try:
                gid = int(ev.server_id)
            except (TypeError, ValueError):
                return
            allowed = connector.allowed_guild_ids
            if allowed and gid not in allowed:
                return
            await handle_normalized_event(ev)

        await connector.connect()

        await _gateway_discord_channel_acl_preflight(
            connector,
            rcx.persona.persona_id,
            watched_channel_ids,
            setup,
        )

        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=5.0)
    finally:
        if connector is not None:
            try:
                await connector.disconnect()
            except (RuntimeError, AttributeError) as e:
                logger.warning("connector disconnect: %s %s", type(e).__name__, e)
        if mongo is not None:
            try:
                await mongo.close()
            except (RuntimeError, AttributeError, TypeError) as e:
                logger.warning("mongo close: %s %s", type(e).__name__, e)
        logger.info("%s exit", persona_id_loop)


def main() -> None:
    """CLI entry: run bots for this process group with the discord_bot loop."""
    try:
        scenario_fn = ckit_bot_exec.parse_bot_args()
        fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")
        asyncio.run(
            ckit_bot_exec.run_bots_in_this_group(
                fclient,
                bot_main_loop=discord_bot_main_loop,
                inprocess_tools=TOOLS,
                scenario_fn=scenario_fn,
                install_func=discord_bot_install.install,
            )
        )
    except (RuntimeError, OSError) as e:
        logger.error("main failed: %s %s", type(e).__name__, e)
        raise


if __name__ == "__main__":
    main()
