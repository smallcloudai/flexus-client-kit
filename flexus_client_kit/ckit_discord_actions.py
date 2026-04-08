from __future__ import annotations

from collections.abc import Callable

import aiohttp
import discord
from discord.errors import DiscordException

import flexus_client_kit.integrations.fi_discord2 as dc
from flexus_client_kit.ckit_connector import ActionResult


async def discord_run_platform_action(
    client: discord.Client,
    persona_id: str,
    action_type: str,
    params: dict,
    *,
    resolve_guild: Callable[[int], discord.Guild | None],
) -> ActionResult:
    if action_type == "send_dm":
        try:
            uid = int(params["user_id"])
            text = str(params["text"])
        except (TypeError, ValueError, KeyError):
            return ActionResult(ok=False, error="bad_params")
        try:
            user = await client.fetch_user(uid)
        except DiscordException as e:
            dc.log_ctx(persona_id, None, "send_dm fetch_user: %s %s", type(e).__name__, e)
            return ActionResult(ok=False, error="%s: %s" % (type(e).__name__, e))
        except aiohttp.ClientError as e:
            dc.log_ctx(persona_id, None, "send_dm fetch_user network: %s %s", type(e).__name__, e)
            return ActionResult(ok=False, error="%s: %s" % (type(e).__name__, e))
        try:
            ok = await dc.safe_dm(client, user, persona_id, text)
            return ActionResult(ok=ok)
        except DiscordException as e:
            dc.log_ctx(persona_id, None, "send_dm: %s %s", type(e).__name__, e)
            return ActionResult(ok=False, error="%s: %s" % (type(e).__name__, e))
        except aiohttp.ClientError as e:
            dc.log_ctx(persona_id, None, "send_dm network: %s %s", type(e).__name__, e)
            return ActionResult(ok=False, error="%s: %s" % (type(e).__name__, e))

    if action_type == "post_to_channel":
        try:
            cid = int(params["channel_id"])
            text = str(params["text"])
        except (TypeError, ValueError, KeyError):
            return ActionResult(ok=False, error="bad_params")
        ch: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None = None
        try:
            ch = client.get_channel(cid)
            if not isinstance(ch, discord.TextChannel):
                return ActionResult(ok=False, error="channel_not_found")
            gch = ch.guild
            if gch is None or resolve_guild(int(gch.id)) is None:
                return ActionResult(ok=False, error="guild_not_allowed")
            msg = await dc.safe_send(ch, persona_id, text)
            return ActionResult(ok=msg is not None)
        except DiscordException as e:
            lg = None
            if isinstance(ch, discord.TextChannel) and ch.guild is not None:
                lg = int(ch.guild.id)
            dc.log_ctx(persona_id, lg, "post_to_channel: %s %s", type(e).__name__, e)
            return ActionResult(ok=False, error="%s: %s" % (type(e).__name__, e))
        except aiohttp.ClientError as e:
            dc.log_ctx(persona_id, None, "post_to_channel network: %s %s", type(e).__name__, e)
            return ActionResult(ok=False, error="%s: %s" % (type(e).__name__, e))

    if action_type == "get_user_info":
        try:
            uid = int(params["user_id"])
        except (TypeError, ValueError, KeyError):
            return ActionResult(ok=False, error="bad_params")
        raw_sid = params.get("server_id") or params.get("guild_id") or ""
        if str(raw_sid).strip():
            try:
                gid = int(raw_sid)
            except (TypeError, ValueError):
                return ActionResult(ok=False, error="bad_server_id")
            g = resolve_guild(gid)
            if g is None:
                return ActionResult(ok=False, error="guild_not_found")
            member = g.get_member(uid)
            if member is None:
                try:
                    member = await g.fetch_member(uid)
                except DiscordException:
                    member = None
            if member is None:
                return ActionResult(ok=False, error="member_not_found")
            return ActionResult(
                ok=True,
                data={"user_id": str(member.id), "display_name": member.display_name},
            )
        for guild in client.guilds:
            member = guild.get_member(uid)
            if member is not None:
                return ActionResult(
                    ok=True,
                    data={"user_id": str(member.id), "display_name": member.display_name},
                )
        return ActionResult(ok=False, error="member_not_found")

    if action_type == "get_channel":
        try:
            cid = int(params["channel_id"])
        except (TypeError, ValueError, KeyError):
            return ActionResult(ok=False, error="bad_params")
        ch = client.get_channel(cid)
        if ch is None:
            return ActionResult(ok=False, error="channel_not_found")
        gch = getattr(ch, "guild", None)
        if gch is None:
            return ActionResult(ok=False, error="not_guild_channel")
        if resolve_guild(int(gch.id)) is None:
            return ActionResult(ok=False, error="guild_not_allowed")
        nm = getattr(ch, "name", None) or ""
        data: dict = {
            "channel_id": str(ch.id),
            "name": nm,
            "type": str(ch.type),
            "guild_id": str(gch.id),
        }
        me = gch.me
        if me is not None and hasattr(ch, "permissions_for"):
            pr = ch.permissions_for(me)
            data["view_channel"] = pr.view_channel
            data["send_messages"] = pr.send_messages
            data["read_message_history"] = pr.read_message_history
            data["manage_messages"] = pr.manage_messages
        return ActionResult(ok=True, data=data)

    g: discord.Guild | None = None
    if action_type in ("add_role", "remove_role", "kick"):
        raw = params.get("server_id") or params.get("guild_id") or ""
        if raw is None or str(raw).strip() == "":
            return ActionResult(ok=False, error="missing_server_id")
        try:
            gid = int(raw)
        except (TypeError, ValueError):
            return ActionResult(ok=False, error="bad_params")
        g = resolve_guild(gid)
        if g is None:
            return ActionResult(ok=False, error="guild_not_found")

    if action_type in ("add_role", "remove_role"):
        try:
            uid = int(params["user_id"])
            rid = int(params["role_id"])
        except (TypeError, ValueError, KeyError):
            return ActionResult(ok=False, error="bad_params")
        try:
            member = g.get_member(uid)
            role = g.get_role(rid)
            if member is None or role is None:
                return ActionResult(ok=False, error="member_or_role_not_found")
            if action_type == "add_role":
                await member.add_roles(role)
            else:
                await member.remove_roles(role)
            return ActionResult(ok=True)
        except DiscordException as e:
            dc.log_ctx(persona_id, g.id, "%s: %s %s", action_type, type(e).__name__, e)
            return ActionResult(ok=False, error="%s: %s" % (type(e).__name__, e))
        except aiohttp.ClientError as e:
            dc.log_ctx(persona_id, g.id, "%s network: %s %s", action_type, type(e).__name__, e)
            return ActionResult(ok=False, error="%s: %s" % (type(e).__name__, e))

    if action_type == "kick":
        try:
            uid = int(params["user_id"])
        except (TypeError, ValueError, KeyError):
            return ActionResult(ok=False, error="bad_params")
        reason = str(params.get("reason") or "")
        try:
            member = g.get_member(uid)
            if member is None:
                return ActionResult(ok=False, error="member_not_found")
            await member.kick(reason=reason or None)
            return ActionResult(ok=True)
        except DiscordException as e:
            dc.log_ctx(persona_id, g.id, "kick: %s %s", type(e).__name__, e)
            return ActionResult(ok=False, error="%s: %s" % (type(e).__name__, e))
        except aiohttp.ClientError as e:
            dc.log_ctx(persona_id, g.id, "kick network: %s %s", type(e).__name__, e)
            return ActionResult(ok=False, error="%s: %s" % (type(e).__name__, e))

    return ActionResult(ok=False, error="unknown_action_type")
