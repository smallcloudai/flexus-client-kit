"""
In-process Discord ``ChatConnector`` for the discord_bot worker: one discord.py client per
process, events as ``NormalizedEvent`` via ``bind_discord_gateway_client``, actions via
``discord_run_platform_action``. Guild allowlist is enforced on both ingress and
``resolve_guild`` so behavior matches the former gateway emessage path.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable, Iterable
from typing import Any

import discord
from discord.errors import DiscordException

from flexus_client_kit.ckit_automation_catalog import ActionDescriptor, TriggerDescriptor
from flexus_client_kit.ckit_connector import ActionResult, ChatConnector, NormalizedEvent
from flexus_client_kit.ckit_connector_discord_catalog import DISCORD_ACTIONS, DISCORD_TRIGGERS
from flexus_client_kit.integrations.fi_discord2 import (
    bind_discord_gateway_client,
    close_discord_client,
    discord_run_platform_action,
    start_discord_client,
)

logger = logging.getLogger(__name__)


class DiscordLocalConnector(ChatConnector):
    """
    Live discord.py client in the bot process: same normalized events and actions as the
    gateway service, without Redis or ``on_emessage("DISCORD")``.
    """

    def __init__(
        self,
        token: str,
        persona_id: str,
        *,
        initial_guild_ids: set[int] | None = None,
    ) -> None:
        self._token = (token or "").strip()
        self._persona_id = persona_id
        self._allowed_guild_ids: set[int] = {int(x) for x in (initial_guild_ids or set())}
        self._client: discord.Client | None = None
        self._runner_task: asyncio.Task[None] | None = None
        self._event_callback: Callable[[NormalizedEvent], Awaitable[None]] | None = None
        self._connected = False

    @property
    def platform(self) -> str:
        return "discord"

    @property
    def raw_client(self) -> Any:
        return self._client

    @property
    def allowed_guild_ids(self) -> frozenset[int]:
        return frozenset(self._allowed_guild_ids)

    async def set_allowed_guild_ids(self, ids: Iterable[int]) -> None:
        self._allowed_guild_ids = {int(x) for x in ids}

    async def update_guild_ids(self, ids: Iterable[int]) -> None:
        await self.set_allowed_guild_ids(ids)

    def supported_triggers(self) -> list[TriggerDescriptor]:
        return DISCORD_TRIGGERS

    def supported_actions(self) -> list[ActionDescriptor]:
        return DISCORD_ACTIONS

    def on_event(self, callback: Callable[[NormalizedEvent], Awaitable[None]]) -> None:
        self._event_callback = callback

    def format_mention(self, user_id: str) -> str:
        return "<@%s>" % (user_id,)

    def _resolve_guild(self, gid: int) -> discord.Guild | None:
        try:
            if not self._allowed_guild_ids or gid not in self._allowed_guild_ids:
                return None
            if self._client is None:
                return None
            g = self._client.get_guild(gid)
            return g
        except (TypeError, ValueError, AttributeError) as e:
            logger.warning("resolve_guild: %s %s", type(e).__name__, e)
            return None

    async def connect(self) -> None:
        try:
            if not self._token:
                raise ValueError("DiscordLocalConnector: empty token")

            def register(client: discord.Client) -> None:
                async def emit(ev: NormalizedEvent) -> None:
                    try:
                        gid = int(ev.server_id)
                    except (TypeError, ValueError) as e:
                        logger.warning(
                            "%s discord emit skip (bad server_id): %s %s",
                            self._persona_id,
                            type(e).__name__,
                            e,
                        )
                        return
                    allowed = self._allowed_guild_ids
                    if not allowed or gid not in allowed:
                        return
                    cb = self._event_callback
                    if cb is None:
                        return
                    await cb(ev)

                bind_discord_gateway_client(client, emit)

            self._client, self._runner_task = await start_discord_client(
                self._token,
                self._persona_id,
                register,
            )
            self._connected = True
        except (ValueError, DiscordException, RuntimeError, OSError) as e:
            logger.error("DiscordLocalConnector connect failed: %s %s", type(e).__name__, e)
            raise

    async def disconnect(self) -> None:
        try:
            await close_discord_client(self._client, self._runner_task)
        except asyncio.CancelledError:
            raise
        except (DiscordException, RuntimeError) as e:
            logger.warning("DiscordLocalConnector disconnect: %s %s", type(e).__name__, e)
        finally:
            self._client = None
            self._runner_task = None
            self._connected = False

    async def execute_action(self, action_type: str, params: dict) -> ActionResult:
        try:
            if not self._connected or self._client is None:
                return ActionResult(ok=False, error="not_connected")
            return await discord_run_platform_action(
                self._client,
                self._persona_id,
                action_type,
                params,
                resolve_guild=self._resolve_guild,
            )
        except DiscordException as e:
            logger.warning(
                "DiscordLocalConnector execute_action %s: %s %s",
                action_type,
                type(e).__name__,
                e,
            )
            return ActionResult(ok=False, error="%s: %s" % (type(e).__name__, e))

    async def get_user_info(self, user_id: str, server_id: str = "") -> dict | None:
        try:
            r = await self.execute_action(
                "get_user_info",
                {"user_id": str(user_id), "server_id": str(server_id or "")},
            )
            if not r.ok or not r.data:
                return None
            return dict(r.data)
        except (TypeError, ValueError, KeyError) as e:
            logger.warning("get_user_info: %s %s", type(e).__name__, e)
            return None

    async def get_channel(self, channel_id: str) -> dict | None:
        try:
            r = await self.execute_action("get_channel", {"channel_id": str(channel_id)})
            if not r.ok or not r.data:
                return None
            return dict(r.data)
        except (TypeError, ValueError, KeyError) as e:
            logger.warning("get_channel: %s %s", type(e).__name__, e)
            return None
