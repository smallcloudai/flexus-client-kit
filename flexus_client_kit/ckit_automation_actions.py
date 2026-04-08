"""
Execute resolved automation actions and build job handlers for scheduled rules.

The automation engine (ckit_automation_engine) produces flat action dicts with pre-resolved
_resolved_body / _resolved_channel_id. This module performs side effects only, returns per-action
results for logging, and emits field_changes for crm_field_changed / status_transition cascades.

Generic CRM actions (set_crm_field, set_status, enqueue_check, cancel_pending_jobs) work with
any connector. Discord-specific actions (send_dm, post_to_channel, add_role, remove_role, kick)
delegate to the Discord connector via ctx['connector'].execute_action or the legacy direct-client
path (ctx['discord_client'] / ctx['guild']) for backward compatibility.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

import aiohttp
import discord
from discord.errors import DiscordException
from pymongo.errors import PyMongoError

from flexus_client_kit import ckit_crm_members, ckit_job_queue, ckit_person_domain
from flexus_client_kit.ckit_automation import DisabledRulesCache, filter_active_rules
from flexus_client_kit.integrations import fi_discord2 as dc

logger = logging.getLogger(__name__)

# Maximum synthetic cascade rounds after CRM mutations (matches bot loop U2.4 guard).
_MAX_CASCADE_DEPTH = 5


# Dispatcher: action type string -> async handler returning either a result dict only or
# (result dict, optional field_change dict) for CRM mutations.
ActionHandler = Callable[
    [dict, dict],
    Awaitable[Tuple[dict, Optional[dict]]],
]


def _result_dict(
    *,
    ok: bool,
    error: Optional[str] = None,
    note: Optional[str] = None,
    cancelled_count: Optional[int] = None,
) -> dict:
    """
    Normalized per-action outcome merged into execute_actions output rows.

    ok/error are the contract; note carries dedupe hints; cancelled_count is for cancel_pending_jobs.
    """
    out: dict[str, Any] = {"ok": ok, "error": error}
    if note is not None:
        out["note"] = note
    if cancelled_count is not None:
        out["cancelled_count"] = cancelled_count
    return out


def _guild_user_from_member_doc(member_doc: dict) -> Tuple[Optional[int], Optional[int]]:
    """Read compound natural key from CRM doc; None if missing or non-coercible."""
    try:
        gid = member_doc.get("guild_id")
        uid = member_doc.get("user_id")
        if gid is None or uid is None:
            return (None, None)
        return (int(gid), int(uid))
    except (TypeError, ValueError):
        return (None, None)


async def _do_send_dm(action: dict, ctx: dict) -> Tuple[dict, Optional[dict]]:
    try:
        persona_id = str(ctx.get("persona_id") or "")
        body_raw = action.get("_resolved_body")
        body = body_raw if isinstance(body_raw, str) else ""
        if not (body or "").strip():
            return (_result_dict(ok=False, error="empty_body"), None)
        connector = ctx.get("connector")
        if connector is not None:
            member_doc = ctx.get("member_doc")
            if not isinstance(member_doc, dict):
                return (_result_dict(ok=False, error="bad_member_doc"), None)
            uid_s = str(member_doc.get("user_id", "") or "")
            if not uid_s:
                return (_result_dict(ok=False, error="missing_user_id"), None)
            dm_params: dict = {"user_id": uid_s, "text": body}
            sid = str(ctx.get("server_id") or "")
            if sid:
                # Propagate guild context so the gateway ACL can verify this persona's access.
                dm_params["server_id"] = sid
            result = await connector.execute_action("send_dm", dm_params)
            return (_result_dict(ok=result.ok, error=result.error), None)
        member_discord = ctx.get("member_discord")
        if member_discord is None:
            dc.log_ctx(persona_id, _guild_user_from_member_doc(ctx.get("member_doc") or {})[0], "send_dm skipped: no member_discord")
            return (_result_dict(ok=False, error="no_member_discord"), None)
        client = ctx["discord_client"]
        ok_dm = await dc.safe_dm(client, member_discord, persona_id, body)
        if ok_dm:
            return (_result_dict(ok=True, error=None), None)
        return (_result_dict(ok=False, error="safe_dm_failed"), None)
    except DiscordException as e:
        logger.warning("send_dm DiscordException: %s %s", type(e).__name__, e)
        return (_result_dict(ok=False, error=type(e).__name__), None)
    except aiohttp.ClientError as e:
        logger.warning("send_dm ClientError: %s %s", type(e).__name__, e)
        return (_result_dict(ok=False, error=type(e).__name__), None)
    except (KeyError, TypeError) as e:
        logger.error("send_dm context error", exc_info=e)
        return (_result_dict(ok=False, error=type(e).__name__), None)


async def _do_post_to_channel(action: dict, ctx: dict) -> Tuple[dict, Optional[dict]]:
    try:
        persona_id = str(ctx.get("persona_id") or "")
        cid = action.get("_resolved_channel_id")
        if cid is None:
            return (_result_dict(ok=False, error="no_channel_id"), None)
        try:
            channel_id = int(cid)
        except (TypeError, ValueError):
            return (_result_dict(ok=False, error="bad_channel_id"), None)
        body_raw = action.get("_resolved_body")
        body = body_raw if isinstance(body_raw, str) else ""
        if not (body or "").strip():
            return (_result_dict(ok=False, error="empty_body"), None)
        connector = ctx.get("connector")
        if connector is not None:
            sid = str(ctx.get("server_id") or "")
            payload = {"channel_id": str(channel_id), "text": body}
            if sid:
                payload["server_id"] = sid
            result = await connector.execute_action("post_to_channel", payload)
            return (_result_dict(ok=result.ok, error=result.error), None)
        guild = ctx["guild"]
        ch = guild.get_channel(channel_id)
        if ch is None or not isinstance(ch, discord.TextChannel):
            dc.log_ctx(persona_id, int(guild.id) if guild else None, "post_to_channel: channel %s missing or not text", channel_id)
            return (_result_dict(ok=False, error="channel_not_found"), None)
        msg = await dc.safe_send(ch, persona_id, body)
        if msg is not None:
            return (_result_dict(ok=True, error=None), None)
        return (_result_dict(ok=False, error="safe_send_failed"), None)
    except DiscordException as e:
        logger.warning("post_to_channel DiscordException: %s %s", type(e).__name__, e)
        return (_result_dict(ok=False, error=type(e).__name__), None)
    except aiohttp.ClientError as e:
        logger.warning("post_to_channel ClientError: %s %s", type(e).__name__, e)
        return (_result_dict(ok=False, error=type(e).__name__), None)
    except (KeyError, TypeError, AttributeError) as e:
        logger.error("post_to_channel context error", exc_info=e)
        return (_result_dict(ok=False, error=type(e).__name__), None)


async def _do_set_crm_field(action: dict, ctx: dict) -> Tuple[dict, Optional[dict]]:
    """
    Persist one CRM field; value is already resolved by the engine (e.g. float for {now}).

    Updates ctx member_doc in memory on success so later actions in the same batch see it.
    """
    try:
        member_doc = ctx.get("member_doc")
        if not isinstance(member_doc, dict):
            return (_result_dict(ok=False, error="bad_member_doc"), None)
        field = action.get("field")
        if not isinstance(field, str) or not field:
            return (_result_dict(ok=False, error="bad_field"), None)
        value = action.get("value")
        guild_id, user_id = _guild_user_from_member_doc(member_doc)
        if guild_id is None or user_id is None:
            return (_result_dict(ok=False, error="missing_guild_or_user"), None)
        old_val = member_doc.get(field)
        new_doc = await ckit_crm_members.update_member_field(
            ctx["mongo_db"],
            guild_id,
            user_id,
            field,
            value,
        )
        if new_doc is None:
            return (_result_dict(ok=False, error="member_not_found"), None)
        ctx["member_doc"] = new_doc
        fc = {
            "field": field,
            "old_value": old_val,
            "new_value": value,
            "is_status": False,
        }
        return (_result_dict(ok=True, error=None), fc)
    except PyMongoError as e:
        logger.warning("set_crm_field PyMongoError: %s %s", type(e).__name__, e)
        return (_result_dict(ok=False, error=type(e).__name__), None)
    except (KeyError, TypeError) as e:
        logger.error("set_crm_field context error", exc_info=e)
        return (_result_dict(ok=False, error=type(e).__name__), None)


async def _do_set_status(action: dict, ctx: dict) -> Tuple[dict, Optional[dict]]:
    """
    Set lifecycle_status via CRM helper; merges returned doc into ctx for downstream actions.
    """
    try:
        member_doc = ctx.get("member_doc")
        if not isinstance(member_doc, dict):
            return (_result_dict(ok=False, error="bad_member_doc"), None)
        new_status = action.get("status")
        if not isinstance(new_status, str) or not new_status:
            return (_result_dict(ok=False, error="bad_status"), None)
        guild_id, user_id = _guild_user_from_member_doc(member_doc)
        if guild_id is None or user_id is None:
            return (_result_dict(ok=False, error="missing_guild_or_user"), None)
        merged, old_status = await ckit_crm_members.set_member_status(
            ctx["mongo_db"],
            guild_id,
            user_id,
            new_status,
        )
        if merged is None:
            return (_result_dict(ok=False, error="member_not_found"), None)
        ctx["member_doc"] = merged
        fc = {
            "field": "lifecycle_status",
            "old_value": old_status,
            "new_value": new_status,
            "is_status": True,
        }
        return (_result_dict(ok=True, error=None), fc)
    except PyMongoError as e:
        logger.warning("set_status PyMongoError: %s %s", type(e).__name__, e)
        return (_result_dict(ok=False, error=type(e).__name__), None)
    except (KeyError, TypeError) as e:
        logger.error("set_status context error", exc_info=e)
        return (_result_dict(ok=False, error=type(e).__name__), None)


async def _do_enqueue_check(action: dict, ctx: dict) -> Tuple[dict, Optional[dict]]:
    """
    Insert dc_community_jobs row for a future scheduled_check, with dedup on (kind, guild, user).

    Anchor-relative scheduling requires anchor_val present on member_doc when anchor_field is set.
    """
    try:
        member_doc = ctx.get("member_doc")
        if not isinstance(member_doc, dict):
            return (_result_dict(ok=False, error="bad_member_doc"), None)
        check_rule_id = action.get("check_rule_id")
        if not isinstance(check_rule_id, str) or not check_rule_id:
            return (_result_dict(ok=False, error="bad_check_rule_id"), None)
        delay_raw = action.get("delay_seconds")
        try:
            delay_sec = int(delay_raw)
        except (TypeError, ValueError):
            return (_result_dict(ok=False, error="bad_delay_seconds"), None)
        guild_id, user_id = _guild_user_from_member_doc(member_doc)
        if guild_id is None or user_id is None:
            return (_result_dict(ok=False, error="missing_guild_or_user"), None)
        db = ctx["mongo_db"]
        coll = db[ckit_job_queue.COL_JOBS]
        dup = await coll.find_one(
            {
                "kind": check_rule_id,
                "payload.guild_id": guild_id,
                "payload.user_id": user_id,
                "done": False,
            },
        )
        if dup is not None:
            dc.log_ctx(
                str(ctx.get("persona_id") or ""),
                guild_id,
                "enqueue_check deduped kind=%s user=%s",
                check_rule_id,
                user_id,
            )
            return (_result_dict(ok=True, error=None, note="deduped"), None)
        anchor_field = action.get("anchor_field")
        if isinstance(anchor_field, str) and anchor_field:
            anchor_val = member_doc.get(anchor_field)
            if anchor_val is None:
                dc.log_ctx(
                    str(ctx.get("persona_id") or ""),
                    guild_id,
                    "enqueue_check skipped: anchor_field %s not set",
                    anchor_field,
                )
                return (_result_dict(ok=False, error="anchor_not_set"), None)
            try:
                run_at = float(anchor_val) + float(delay_sec)
            except (TypeError, ValueError):
                return (_result_dict(ok=False, error="bad_anchor_value"), None)
        else:
            run_at = time.time() + float(delay_sec)
        payload = {
            "guild_id": guild_id,
            "user_id": user_id,
            "rule_id": check_rule_id,
            "persona_id": str(ctx.get("persona_id") or ""),
        }
        await ckit_job_queue.enqueue_job(db, check_rule_id, run_at, payload)
        return (_result_dict(ok=True, error=None), None)
    except PyMongoError as e:
        logger.warning("enqueue_check PyMongoError: %s %s", type(e).__name__, e)
        return (_result_dict(ok=False, error=type(e).__name__), None)
    except (KeyError, TypeError) as e:
        logger.error("enqueue_check context error", exc_info=e)
        return (_result_dict(ok=False, error=type(e).__name__), None)


async def _do_cancel_pending_jobs(action: dict, ctx: dict) -> Tuple[dict, Optional[dict]]:
    """
    Mark pending jobs done whose kind starts with job_kind_prefix for this member (regex prefix).
    """
    try:
        member_doc = ctx.get("member_doc")
        if not isinstance(member_doc, dict):
            return (_result_dict(ok=False, error="bad_member_doc"), None)
        prefix = action.get("job_kind_prefix")
        if not isinstance(prefix, str) or not prefix:
            return (_result_dict(ok=False, error="bad_prefix"), None)
        guild_id, user_id = _guild_user_from_member_doc(member_doc)
        if guild_id is None or user_id is None:
            return (_result_dict(ok=False, error="missing_guild_or_user"), None)
        db = ctx["mongo_db"]
        coll = db[ckit_job_queue.COL_JOBS]
        pattern = "^%s" % (re.escape(prefix),)
        now_ts = time.time()
        res = await coll.update_many(
            {
                "kind": {"$regex": pattern},
                "payload.guild_id": guild_id,
                "payload.user_id": user_id,
                "done": False,
            },
            {"$set": {"done": True, "cancelled": True, "cancelled_ts": now_ts}},
        )
        n = int(getattr(res, "modified_count", 0) or 0)
        return (_result_dict(ok=True, error=None, cancelled_count=n), None)
    except PyMongoError as e:
        logger.warning("cancel_pending_jobs PyMongoError: %s %s", type(e).__name__, e)
        return (_result_dict(ok=False, error=type(e).__name__), None)
    except (KeyError, TypeError) as e:
        logger.error("cancel_pending_jobs context error", exc_info=e)
        return (_result_dict(ok=False, error=type(e).__name__), None)


async def _do_add_role(action: dict, ctx: dict) -> Tuple[dict, Optional[dict]]:
    try:
        rid = action.get("_resolved_role_id")
        if rid is None:
            return (_result_dict(ok=False, error="no_role_id"), None)
        member_doc = ctx.get("member_doc")
        if not isinstance(member_doc, dict):
            return (_result_dict(ok=False, error="bad_member_doc"), None)
        uid_s = str(member_doc.get("user_id", "") or "")
        if not uid_s:
            return (_result_dict(ok=False, error="missing_user_id"), None)
        connector = ctx.get("connector")
        if connector is None:
            return (_result_dict(ok=False, error="no_connector"), None)
        sid = str(ctx.get("server_id") or "")
        if not sid:
            return (_result_dict(ok=False, error="missing_server_id"), None)
        result = await connector.execute_action(
            "add_role",
            {"user_id": uid_s, "role_id": str(int(rid)), "server_id": sid},
        )
        return (_result_dict(ok=result.ok, error=result.error), None)
    except DiscordException as e:
        logger.warning("add_role DiscordException: %s %s", type(e).__name__, e)
        return (_result_dict(ok=False, error=type(e).__name__), None)
    except aiohttp.ClientError as e:
        logger.warning("add_role ClientError: %s %s", type(e).__name__, e)
        return (_result_dict(ok=False, error=type(e).__name__), None)
    except (KeyError, TypeError, ValueError) as e:
        logger.error("add_role context error", exc_info=e)
        return (_result_dict(ok=False, error=type(e).__name__), None)


async def _do_remove_role(action: dict, ctx: dict) -> Tuple[dict, Optional[dict]]:
    try:
        rid = action.get("_resolved_role_id")
        if rid is None:
            return (_result_dict(ok=False, error="no_role_id"), None)
        member_doc = ctx.get("member_doc")
        if not isinstance(member_doc, dict):
            return (_result_dict(ok=False, error="bad_member_doc"), None)
        uid_s = str(member_doc.get("user_id", "") or "")
        if not uid_s:
            return (_result_dict(ok=False, error="missing_user_id"), None)
        connector = ctx.get("connector")
        if connector is None:
            return (_result_dict(ok=False, error="no_connector"), None)
        sid = str(ctx.get("server_id") or "")
        if not sid:
            return (_result_dict(ok=False, error="missing_server_id"), None)
        result = await connector.execute_action(
            "remove_role",
            {"user_id": uid_s, "role_id": str(int(rid)), "server_id": sid},
        )
        return (_result_dict(ok=result.ok, error=result.error), None)
    except DiscordException as e:
        logger.warning("remove_role DiscordException: %s %s", type(e).__name__, e)
        return (_result_dict(ok=False, error=type(e).__name__), None)
    except aiohttp.ClientError as e:
        logger.warning("remove_role ClientError: %s %s", type(e).__name__, e)
        return (_result_dict(ok=False, error=type(e).__name__), None)
    except (KeyError, TypeError, ValueError) as e:
        logger.error("remove_role context error", exc_info=e)
        return (_result_dict(ok=False, error=type(e).__name__), None)


async def _do_kick(action: dict, ctx: dict) -> Tuple[dict, Optional[dict]]:
    try:
        member_doc = ctx.get("member_doc")
        if not isinstance(member_doc, dict):
            return (_result_dict(ok=False, error="bad_member_doc"), None)
        uid_s = str(member_doc.get("user_id", "") or "")
        if not uid_s:
            return (_result_dict(ok=False, error="missing_user_id"), None)
        connector = ctx.get("connector")
        if connector is None:
            return (_result_dict(ok=False, error="no_connector"), None)
        sid = str(ctx.get("server_id") or "")
        if not sid:
            return (_result_dict(ok=False, error="missing_server_id"), None)
        reason_raw = action.get("_resolved_kick_reason")
        reason = reason_raw if isinstance(reason_raw, str) else ""
        result = await connector.execute_action(
            "kick",
            {"user_id": uid_s, "reason": reason, "server_id": sid},
        )
        return (_result_dict(ok=result.ok, error=result.error), None)
    except DiscordException as e:
        logger.warning("kick DiscordException: %s %s", type(e).__name__, e)
        return (_result_dict(ok=False, error=type(e).__name__), None)
    except aiohttp.ClientError as e:
        logger.warning("kick ClientError: %s %s", type(e).__name__, e)
        return (_result_dict(ok=False, error=type(e).__name__), None)
    except (KeyError, TypeError, ValueError) as e:
        logger.error("kick context error", exc_info=e)
        return (_result_dict(ok=False, error=type(e).__name__), None)


async def _do_call_gatekeeper_tool(action: dict, ctx: dict) -> Tuple[dict, Optional[dict]]:
    """
    Apply a gatekeeper decision for the current Discord member.

    Decision mapping:
      accept       → application DECIDED/APPROVED, CRM lifecycle "accepted"
      reject       → application DECIDED/REJECTED, CRM lifecycle "rejected"
      request_info → application REVIEWING,         CRM lifecycle "pending_review"

    Always applies the CRM lifecycle change (Mongo). Person domain sync
    (GraphQL) is best-effort: failures are logged but do not abort the action.
    Returns a field_change for lifecycle_status so existing status_transition
    cascades keep working.
    """
    try:
        tool_name = action.get("tool_name")
        if tool_name not in ("accept", "reject", "request_info"):
            return (_result_dict(ok=False, error="bad_tool_name"), None)

        member_doc = ctx.get("member_doc")
        if not isinstance(member_doc, dict):
            return (_result_dict(ok=False, error="bad_member_doc"), None)

        guild_id, user_id = _guild_user_from_member_doc(member_doc)
        if guild_id is None or user_id is None:
            return (_result_dict(ok=False, error="missing_guild_or_user"), None)

        # Decision → status mapping
        if tool_name == "accept":
            app_status = "DECIDED"
            app_decision = "APPROVED"
            crm_status = "accepted"
        elif tool_name == "reject":
            app_status = "DECIDED"
            app_decision = "REJECTED"
            crm_status = "rejected"
        else:
            app_status = "REVIEWING"
            app_decision = ""
            crm_status = "pending_review"

        reason_template = action.get("reason_template")
        details: Optional[dict] = {"reason_template": reason_template} if isinstance(reason_template, str) and reason_template else None

        # Best-effort person domain sync (requires fclient + ws_id in ctx)
        fclient = ctx.get("fclient")
        ws_id = ctx.get("ws_id") or ""
        if fclient is not None and ws_id:
            username = str(member_doc.get("discord_username") or user_id)
            discord_user_id = str(user_id)
            person_id = await ckit_person_domain.ensure_person_for_discord_user(
                fclient,
                ws_id,
                discord_user_id,
                username,
            )
            if person_id:
                existing_app = await ckit_person_domain.application_find_latest(
                    fclient,
                    ws_id,
                    person_id,
                )
                if existing_app:
                    app_id: Optional[str] = existing_app["application_id"]
                else:
                        app_id = await ckit_person_domain.application_create_pending(
                        fclient,
                        ws_id,
                        person_id,
                        source="discord_bot",
                        platform="discord",
                        payload={"guild_id": str(guild_id), "discord_user_id": discord_user_id},
                    )
                if app_id:
                    await ckit_person_domain.application_apply_decision(
                        fclient,
                        app_id,
                        app_status,
                        app_decision,
                        details,
                    )
        else:
            logger.warning(
                "call_gatekeeper_tool: fclient or ws_id missing from ctx, skipping person domain sync "
                "persona_id=%s tool=%s guild=%s user=%s",
                ctx.get("persona_id"),
                tool_name,
                guild_id,
                user_id,
            )

        # Always apply CRM lifecycle change — this is the primary side-effect
        old_status = member_doc.get("lifecycle_status")
        merged, _prev = await ckit_crm_members.set_member_status(
            ctx["mongo_db"],
            guild_id,
            user_id,
            crm_status,
        )
        if merged is None:
            return (_result_dict(ok=False, error="member_not_found"), None)

        # Stamp accepted_at when the decision is accept, matching crm_member.md contract.
        # Best-effort: if the extra write fails the lifecycle status change still stands.
        if crm_status == "accepted":
            accepted_doc = await ckit_crm_members.update_member_field(
                ctx["mongo_db"],
                guild_id,
                user_id,
                "accepted_at",
                time.time(),
            )
            if accepted_doc is not None:
                merged = accepted_doc

        ctx["member_doc"] = merged
        fc = {
            "field": "lifecycle_status",
            "old_value": old_status,
            "new_value": crm_status,
            "is_status": True,
        }
        return (_result_dict(ok=True, error=None), fc)
    except PyMongoError as e:
        logger.warning("call_gatekeeper_tool PyMongoError: %s %s", type(e).__name__, e)
        return (_result_dict(ok=False, error=type(e).__name__), None)
    except (TypeError, AttributeError, KeyError) as e:
        logger.error("call_gatekeeper_tool unexpected error", exc_info=e)
        return (_result_dict(ok=False, error=type(e).__name__), None)


# Maps automation action.type to handler coroutine; extend when schema gains new types.
_ACTION_DISPATCH: Dict[str, ActionHandler] = {
    "send_dm": _do_send_dm,
    "post_to_channel": _do_post_to_channel,
    "set_crm_field": _do_set_crm_field,
    "set_status": _do_set_status,
    "enqueue_check": _do_enqueue_check,
    "cancel_pending_jobs": _do_cancel_pending_jobs,
    "add_role": _do_add_role,
    "remove_role": _do_remove_role,
    "kick": _do_kick,
    "call_gatekeeper_tool": _do_call_gatekeeper_tool,
}


async def execute_actions(actions: List[dict], ctx: dict) -> Tuple[List[dict], List[dict]]:
    """
    Run resolved actions in order; collect logging rows and CRM field deltas for cascades.

    One failing action does not stop the rest. CRM handlers refresh ctx['member_doc'] on success.
    """
    try:
        results: List[dict] = []
        field_changes: List[dict] = []
        if not isinstance(actions, list):
            logger.error("execute_actions: actions must be a list")
            return ([], [])
        for action in actions:
            if not isinstance(action, dict):
                logger.warning("execute_actions: skip non-dict action")
                continue
            action_type = action.get("type")
            rule_id = str(action.get("rule_id") or "")
            if not isinstance(action_type, str) or not action_type:
                results.append(
                    {
                        "action_type": "",
                        "rule_id": rule_id,
                        "ok": False,
                        "error": "missing_type",
                    },
                )
                continue
            handler = _ACTION_DISPATCH.get(action_type)
            if handler is None:
                logger.warning("execute_actions: unknown action type %s", action_type)
                results.append(
                    {
                        "action_type": action_type,
                        "rule_id": rule_id,
                        "ok": False,
                        "error": "unknown_action_type",
                    },
                )
                continue
            try:
                partial, fc = await handler(action, ctx)
            except DiscordException as e:
                logger.warning("execute_actions handler DiscordException: %s", e)
                results.append(
                    {
                        "action_type": action_type,
                        "rule_id": rule_id,
                        "ok": False,
                        "error": type(e).__name__,
                    },
                )
                continue
            except aiohttp.ClientError as e:
                logger.warning("execute_actions handler ClientError: %s", e)
                results.append(
                    {
                        "action_type": action_type,
                        "rule_id": rule_id,
                        "ok": False,
                        "error": type(e).__name__,
                    },
                )
                continue
            except PyMongoError as e:
                logger.warning("execute_actions handler PyMongoError: %s", e)
                results.append(
                    {
                        "action_type": action_type,
                        "rule_id": rule_id,
                        "ok": False,
                        "error": type(e).__name__,
                    },
                )
                continue
            except (TypeError, KeyError, ValueError) as e:
                logger.error("execute_actions handler data error", exc_info=e)
                results.append(
                    {
                        "action_type": action_type,
                        "rule_id": rule_id,
                        "ok": False,
                        "error": type(e).__name__,
                    },
                )
                continue
            row = {
                "action_type": action_type,
                "rule_id": rule_id,
                "ok": bool(partial.get("ok")),
                "error": partial.get("error"),
            }
            if "note" in partial:
                row["note"] = partial["note"]
            if "cancelled_count" in partial:
                row["cancelled_count"] = partial["cancelled_count"]
            results.append(row)
            if isinstance(fc, dict):
                field_changes.append(fc)
        return (results, field_changes)
    except (TypeError, KeyError) as e:
        logger.error("execute_actions fatal input error", exc_info=e)
        return ([], [])


async def _run_cascade(
    *,
    db: Any,
    client: Any,
    persona_id: str,
    setup: dict,
    rules: List[dict],
    engine_process_fn: Callable[..., List[dict]],
    ctx: dict,
    initial_field_changes: List[dict],
    guild_id: int,
    user_id: int,
    disabled_rules_cache: Optional[DisabledRulesCache] = None,
) -> None:
    """
    Re-run the engine on synthetic CRM events up to _MAX_CASCADE_DEPTH rounds (scheduled job path).

    Mirrors U2.4 bot loop: refresh member from Mongo per change, then process_event + execute_actions.
    """
    try:
        disabled = disabled_rules_cache.get() if disabled_rules_cache else set()
        active_rules = filter_active_rules(rules, disabled)
        pending = list(initial_field_changes)
        depth = 0
        while pending:
            if depth >= _MAX_CASCADE_DEPTH:
                logger.warning(
                    "automation cascade depth limit reached (%s) guild_id=%s user_id=%s",
                    _MAX_CASCADE_DEPTH,
                    guild_id,
                    user_id,
                )
                return
            depth += 1
            next_pending: List[dict] = []
            for fc in pending:
                fresh = await ckit_crm_members.get_member(db, guild_id, user_id)
                if fresh is None:
                    dc.log_ctx(persona_id, guild_id, "cascade skip: member gone user=%s", user_id)
                    continue
                ctx["member_doc"] = fresh
                ctx["server_id"] = str(guild_id)
                g = client.get_guild(guild_id) if client is not None else None
                if ctx.get("connector") is not None:
                    ctx["platform_user"] = await ctx["connector"].get_user_info(
                        str(user_id),
                        server_id=str(guild_id),
                    )
                else:
                    ctx["member_discord"] = g.get_member(user_id) if g else None
                if fc.get("is_status") is True:
                    event_type = "status_transition"
                    event_data = {
                        "old_status": fc.get("old_value"),
                        "new_status": fc.get("new_value"),
                    }
                else:
                    event_type = "crm_field_changed"
                    event_data = {
                        "field_name": fc.get("field"),
                        "new_value": fc.get("new_value"),
                    }
                try:
                    more_actions = engine_process_fn(
                        event_type,
                        event_data,
                        active_rules,
                        fresh,
                        setup,
                    )
                except (TypeError, KeyError, ValueError) as e:
                    logger.error(
                        "cascade engine_process_fn failed event=%s",
                        event_type,
                        exc_info=e,
                    )
                    continue
                if not isinstance(more_actions, list):
                    logger.warning("cascade: engine did not return a list")
                    continue
                _, more_fc = await execute_actions(more_actions, ctx)
                next_pending.extend(more_fc)
            pending = next_pending
    except PyMongoError as e:
        logger.warning("_run_cascade PyMongoError: %s %s", type(e).__name__, e)
    except (TypeError, KeyError) as e:
        logger.error("_run_cascade unexpected error", exc_info=e)


def make_automation_job_handler(
    rules: List[dict],
    setup: dict,
    engine_process_fn: Callable[..., List[dict]],
    db: Any,
    client: Any,
    persona_id: str,
    disabled_rules_cache: Optional[DisabledRulesCache] = None,
    connector: Any = None,
    fclient: Any = None,
    ws_id: str = "",
) -> Dict[str, Callable[[Dict[str, Any]], Awaitable[None]]]:
    def _build_one(rule_id: str) -> Callable[[Dict[str, Any]], Awaitable[None]]:
        rid = str(rule_id)

        async def _handler(payload: Dict[str, Any]) -> None:
            try:
                if connector is None and client is None:
                    dc.log_ctx(persona_id, None, "job %s: no connector or discord client", rid)
                    return
                disabled = disabled_rules_cache.get() if disabled_rules_cache else set()
                if rid in disabled:
                    dc.log_ctx(persona_id, None, "job %s: rule disabled, skipping", rid)
                    return
                raw_g = payload.get("guild_id")
                raw_u = payload.get("user_id")
                if raw_g is None or raw_u is None:
                    dc.log_ctx(persona_id, None, "job %s missing guild_id or user_id in payload", rid)
                    return
                try:
                    g_id = int(raw_g)
                    u_id = int(raw_u)
                except (TypeError, ValueError):
                    dc.log_ctx(persona_id, None, "job %s bad guild_id/user_id in payload", rid)
                    return
                member = await ckit_crm_members.get_member(db, g_id, u_id)
                if member is None:
                    dc.log_ctx(persona_id, g_id, "scheduled job %s: no CRM row for user=%s", rid, u_id)
                    return
                event_data = {
                    "check_rule_id": rid,
                    "guild_id": g_id,
                    "user_id": u_id,
                }
                try:
                    active_rules = filter_active_rules(rules, disabled)
                    actions = engine_process_fn(
                        "scheduled_check",
                        event_data,
                        active_rules,
                        member,
                        setup,
                    )
                except (TypeError, KeyError, ValueError) as e:
                    logger.error("job %s engine_process_fn failed", rid, exc_info=e)
                    return
                if not isinstance(actions, list):
                    logger.warning("job %s: engine returned non-list", rid)
                    return
                gx = client.get_guild(g_id) if client is not None else None
                if connector is not None:
                    ctx = {
                        "connector": connector,
                        "mongo_db": db,
                        "server_id": str(g_id),
                        "platform_user": await connector.get_user_info(str(u_id), server_id=str(g_id)),
                        "member_doc": member,
                        "persona_id": persona_id,
                        "setup": setup,
                        "fclient": fclient,
                        "ws_id": ws_id,
                    }
                else:
                    ctx = {
                        "discord_client": client,
                        "mongo_db": db,
                        "guild": gx,
                        "member_discord": gx.get_member(u_id) if gx else None,
                        "member_doc": member,
                        "persona_id": persona_id,
                        "setup": setup,
                        "fclient": fclient,
                        "ws_id": ws_id,
                    }
                _, field_changes = await execute_actions(actions, ctx)
                await _run_cascade(
                    db=db,
                    client=client,
                    persona_id=persona_id,
                    setup=setup,
                    rules=rules,
                    engine_process_fn=engine_process_fn,
                    ctx=ctx,
                    initial_field_changes=field_changes,
                    guild_id=g_id,
                    user_id=u_id,
                    disabled_rules_cache=disabled_rules_cache,
                )
            except PyMongoError as e:
                logger.warning("job handler %s PyMongoError: %s %s", rid, type(e).__name__, e)
            except DiscordException as e:
                logger.warning("job handler %s DiscordException: %s %s", rid, type(e).__name__, e)
            except aiohttp.ClientError as e:
                logger.warning("job handler %s ClientError: %s %s", rid, type(e).__name__, e)
            except (TypeError, KeyError, AttributeError) as e:
                logger.error("job handler %s unexpected error", rid, exc_info=e)

        return _handler

    out: Dict[str, Callable[[Dict[str, Any]], Awaitable[None]]] = {}
    try:
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            trig = rule.get("trigger")
            if not isinstance(trig, dict):
                continue
            if trig.get("type") != "scheduled_relative_to_field":
                continue
            rid = rule.get("rule_id")
            if not isinstance(rid, str) or not rid:
                logger.warning("make_automation_job_handler: skip rule without rule_id")
                continue
            out[rid] = _build_one(rid)
        return out
    except (TypeError, AttributeError) as e:
        logger.error("make_automation_job_handler failed", exc_info=e)
        return {}

