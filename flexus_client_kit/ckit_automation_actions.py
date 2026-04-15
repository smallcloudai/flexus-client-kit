"""
Execute resolved automation actions for Discord community bots.

The automation engine (ckit_automation_engine) produces flat action dicts with pre-resolved
_resolved_body / _resolved_channel_id. This module performs side effects only and returns per-action
results for logging. Execution context uses event_member: guild_id, user_id, and optional
discord_username from the inbound normalized Discord event (no persisted CRM rows).
"""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

import aiohttp

from flexus_client_kit import ckit_person_domain

logger = logging.getLogger(__name__)

# Dispatcher: action type string -> async handler returning a normalized result dict.
ActionHandler = Callable[[dict, dict], Awaitable[dict]]


def _result_dict(
    *,
    ok: bool,
    error: Optional[str] = None,
    note: Optional[str] = None,
    cancelled_count: Optional[int] = None,
) -> dict:
    """
    Normalized per-action outcome merged into execute_actions output rows.

    ok/error are the contract; note carries dedupe hints where applicable.
    """
    out: dict[str, Any] = {"ok": ok, "error": error}
    if note is not None:
        out["note"] = note
    if cancelled_count is not None:
        out["cancelled_count"] = cancelled_count
    return out


def _guild_user_from_event_member(event_member: dict) -> Tuple[Optional[int], Optional[int]]:
    """Read guild/user ids from the in-memory event_member dict."""
    try:
        gid = event_member.get("guild_id")
        uid = event_member.get("user_id")
        if gid is None or uid is None:
            return (None, None)
        return (int(gid), int(uid))
    except (TypeError, ValueError):
        return (None, None)


async def _do_send_dm(action: dict, ctx: dict) -> dict:
    """Deliver a DM via connector.execute_action(send_dm)."""
    try:
        persona_id = str(ctx.get("persona_id") or "")
        body_raw = action.get("_resolved_body")
        body = body_raw if isinstance(body_raw, str) else ""
        if not (body or "").strip():
            return _result_dict(ok=False, error="empty_body")
        connector = ctx.get("connector")
        if connector is not None:
            em = ctx.get("event_member")
            if not isinstance(em, dict):
                return _result_dict(ok=False, error="bad_event_member")
            uid_s = str(em.get("user_id", "") or "")
            if not uid_s:
                return _result_dict(ok=False, error="missing_user_id")
            dm_params: dict = {"user_id": uid_s, "text": body}
            sid = str(ctx.get("server_id") or "")
            if sid:
                dm_params["server_id"] = sid
            result = await connector.execute_action("send_dm", dm_params)
            return _result_dict(ok=result.ok, error=result.error)
        logger.warning(
            "send_dm: missing ChatConnector in ctx; persona_id=%s",
            persona_id,
        )
        return _result_dict(ok=False, error="no_connector")
    except aiohttp.ClientError as e:
        logger.warning("send_dm ClientError: %s %s", type(e).__name__, e)
        return _result_dict(ok=False, error=type(e).__name__)
    except (KeyError, TypeError) as e:
        logger.error("send_dm context error", exc_info=e)
        return _result_dict(ok=False, error=type(e).__name__)


async def _do_post_to_channel(action: dict, ctx: dict) -> dict:
    """Post to a guild text channel via connector.execute_action."""
    try:
        persona_id = str(ctx.get("persona_id") or "")
        cid = action.get("_resolved_channel_id")
        if cid is None:
            return _result_dict(ok=False, error="no_channel_id")
        try:
            channel_id = int(cid)
        except (TypeError, ValueError):
            return _result_dict(ok=False, error="bad_channel_id")
        body_raw = action.get("_resolved_body")
        body = body_raw if isinstance(body_raw, str) else ""
        if not (body or "").strip():
            return _result_dict(ok=False, error="empty_body")
        connector = ctx.get("connector")
        if connector is not None:
            sid = str(ctx.get("server_id") or "")
            payload = {"channel_id": str(channel_id), "text": body}
            if sid:
                payload["server_id"] = sid
            result = await connector.execute_action("post_to_channel", payload)
            return _result_dict(ok=result.ok, error=result.error)
        logger.warning(
            "post_to_channel: missing ChatConnector in ctx; persona_id=%s",
            persona_id,
        )
        return _result_dict(ok=False, error="no_connector")
    except aiohttp.ClientError as e:
        logger.warning("post_to_channel ClientError: %s %s", type(e).__name__, e)
        return _result_dict(ok=False, error=type(e).__name__)
    except (KeyError, TypeError, AttributeError) as e:
        logger.error("post_to_channel context error", exc_info=e)
        return _result_dict(ok=False, error=type(e).__name__)


async def _do_add_role(action: dict, ctx: dict) -> dict:
    """Resolve role id and call connector add_role."""
    try:
        rid = action.get("_resolved_role_id")
        if rid is None:
            return _result_dict(ok=False, error="no_role_id")
        em = ctx.get("event_member")
        if not isinstance(em, dict):
            return _result_dict(ok=False, error="bad_event_member")
        uid_s = str(em.get("user_id", "") or "")
        if not uid_s:
            return _result_dict(ok=False, error="missing_user_id")
        connector = ctx.get("connector")
        if connector is None:
            return _result_dict(ok=False, error="no_connector")
        sid = str(ctx.get("server_id") or "")
        if not sid:
            return _result_dict(ok=False, error="missing_server_id")
        result = await connector.execute_action(
            "add_role",
            {"user_id": uid_s, "role_id": str(int(rid)), "server_id": sid},
        )
        return _result_dict(ok=result.ok, error=result.error)
    except aiohttp.ClientError as e:
        logger.warning("add_role ClientError: %s %s", type(e).__name__, e)
        return _result_dict(ok=False, error=type(e).__name__)
    except (KeyError, TypeError, ValueError) as e:
        logger.error("add_role context error", exc_info=e)
        return _result_dict(ok=False, error=type(e).__name__)


async def _do_remove_role(action: dict, ctx: dict) -> dict:
    """Resolve role id and call connector remove_role."""
    try:
        rid = action.get("_resolved_role_id")
        if rid is None:
            return _result_dict(ok=False, error="no_role_id")
        em = ctx.get("event_member")
        if not isinstance(em, dict):
            return _result_dict(ok=False, error="bad_event_member")
        uid_s = str(em.get("user_id", "") or "")
        if not uid_s:
            return _result_dict(ok=False, error="missing_user_id")
        connector = ctx.get("connector")
        if connector is None:
            return _result_dict(ok=False, error="no_connector")
        sid = str(ctx.get("server_id") or "")
        if not sid:
            return _result_dict(ok=False, error="missing_server_id")
        result = await connector.execute_action(
            "remove_role",
            {"user_id": uid_s, "role_id": str(int(rid)), "server_id": sid},
        )
        return _result_dict(ok=result.ok, error=result.error)
    except aiohttp.ClientError as e:
        logger.warning("remove_role ClientError: %s %s", type(e).__name__, e)
        return _result_dict(ok=False, error=type(e).__name__)
    except (KeyError, TypeError, ValueError) as e:
        logger.error("remove_role context error", exc_info=e)
        return _result_dict(ok=False, error=type(e).__name__)


async def _do_kick(action: dict, ctx: dict) -> dict:
    """Kick the member in context via connector.execute_action(kick)."""
    try:
        em = ctx.get("event_member")
        if not isinstance(em, dict):
            return _result_dict(ok=False, error="bad_event_member")
        uid_s = str(em.get("user_id", "") or "")
        if not uid_s:
            return _result_dict(ok=False, error="missing_user_id")
        connector = ctx.get("connector")
        if connector is None:
            return _result_dict(ok=False, error="no_connector")
        sid = str(ctx.get("server_id") or "")
        if not sid:
            return _result_dict(ok=False, error="missing_server_id")
        reason_raw = action.get("_resolved_kick_reason")
        reason = reason_raw if isinstance(reason_raw, str) else ""
        result = await connector.execute_action(
            "kick",
            {"user_id": uid_s, "reason": reason, "server_id": sid},
        )
        return _result_dict(ok=result.ok, error=result.error)
    except aiohttp.ClientError as e:
        logger.warning("kick ClientError: %s %s", type(e).__name__, e)
        return _result_dict(ok=False, error=type(e).__name__)
    except (KeyError, TypeError, ValueError) as e:
        logger.error("kick context error", exc_info=e)
        return _result_dict(ok=False, error=type(e).__name__)


async def _do_call_gatekeeper_tool(action: dict, ctx: dict) -> dict:
    """
    Apply a gatekeeper decision using workspace person-domain APIs only (GraphQL).

    Maps accept / reject / request_info to application status updates. Does not write Mongo.
    """
    try:
        tool_name = action.get("tool_name")
        if tool_name not in ("accept", "reject", "request_info"):
            return _result_dict(ok=False, error="bad_tool_name")

        em = ctx.get("event_member")
        if not isinstance(em, dict):
            return _result_dict(ok=False, error="bad_event_member")

        guild_id, user_id = _guild_user_from_event_member(em)
        if guild_id is None or user_id is None:
            return _result_dict(ok=False, error="missing_guild_or_user")

        if tool_name == "accept":
            app_status = "DECIDED"
            app_decision = "APPROVED"
        elif tool_name == "reject":
            app_status = "DECIDED"
            app_decision = "REJECTED"
        else:
            app_status = "REVIEWING"
            app_decision = ""

        reason_template = action.get("reason_template")
        details: Optional[dict] = {"reason_template": reason_template} if isinstance(reason_template, str) and reason_template else None

        fclient = ctx.get("fclient")
        ws_id = ctx.get("ws_id") or ""
        if fclient is None or not ws_id:
            logger.warning(
                "call_gatekeeper_tool: fclient or ws_id missing from ctx, skipping person domain sync "
                "persona_id=%s tool=%s guild=%s user=%s",
                ctx.get("persona_id"),
                tool_name,
                guild_id,
                user_id,
            )
            return _result_dict(ok=False, error="missing_workspace_context")

        username = str(em.get("discord_username") or user_id)
        discord_user_id = str(user_id)
        person_id = await ckit_person_domain.ensure_person_for_discord_user(
            fclient,
            ws_id,
            discord_user_id,
            username,
        )
        if not person_id:
            return _result_dict(ok=False, error="person_unresolved")

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
        if not app_id:
            return _result_dict(ok=False, error="no_application_id")

        await ckit_person_domain.application_apply_decision(
            fclient,
            app_id,
            app_status,
            app_decision,
            details,
        )
        return _result_dict(ok=True, error=None)
    except aiohttp.ClientError as e:
        logger.warning("call_gatekeeper_tool ClientError: %s %s", type(e).__name__, e)
        return _result_dict(ok=False, error=type(e).__name__)
    except (TypeError, AttributeError, KeyError) as e:
        logger.error("call_gatekeeper_tool unexpected error", exc_info=e)
        return _result_dict(ok=False, error=type(e).__name__)


# Maps automation action.type to handler coroutine.
_ACTION_DISPATCH: Dict[str, ActionHandler] = {
    "send_dm": _do_send_dm,
    "post_to_channel": _do_post_to_channel,
    "add_role": _do_add_role,
    "remove_role": _do_remove_role,
    "kick": _do_kick,
    "call_gatekeeper_tool": _do_call_gatekeeper_tool,
}


async def execute_actions(actions: List[dict], ctx: dict) -> List[dict]:
    """
    Run resolved actions in order; collect logging rows. One failing action does not stop the rest.
    """
    try:
        results: List[dict] = []
        if not isinstance(actions, list):
            logger.error("execute_actions: actions must be a list")
            return []
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
                partial = await handler(action, ctx)
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
        return results
    except (TypeError, KeyError) as e:
        logger.error("execute_actions fatal input error", exc_info=e)
        return []
