from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable, Iterable
from typing import Any

from flexus_client_kit import ckit_shutdown
from flexus_client_kit.ckit_connector import (
    ActionDescriptor,
    ActionResult,
    ChatConnector,
    NormalizedEvent,
    TriggerDescriptor,
)
from flexus_client_kit.ckit_connector_discord import DISCORD_ACTIONS, DISCORD_TRIGGERS
from flexus_client_kit.gateway.ckit_gateway_redis import DiscordGatewayRedisSidecar

logger = logging.getLogger(__name__)


class DiscordGatewayConnector(ChatConnector):
    def __init__(
        self,
        token: str,
        persona_id: str,
        *,
        initial_guild_ids: set[int] | None = None,
        sidecar: DiscordGatewayRedisSidecar | None = None,
    ) -> None:
        self._persona_id = persona_id
        self._allowed_guild_ids: set[int] = set(initial_guild_ids or [])
        self._sidecar = sidecar or DiscordGatewayRedisSidecar(token)
        self._event_callback: Callable[[NormalizedEvent], Awaitable[None]] | None = None
        self._connected = False
        self._refresh_task: asyncio.Task[None] | None = None

    @property
    def platform(self) -> str:
        return "discord"

    @property
    def raw_client(self) -> Any:
        return None

    @property
    def allowed_guild_ids(self) -> frozenset[int]:
        return frozenset(self._allowed_guild_ids)

    @property
    def gateway_instance_key(self) -> str:
        return self._sidecar.gateway_instance_key

    def supported_triggers(self) -> list[TriggerDescriptor]:
        return DISCORD_TRIGGERS

    def supported_actions(self) -> list[ActionDescriptor]:
        return DISCORD_ACTIONS

    def on_event(self, callback: Callable[[NormalizedEvent], Awaitable[None]]) -> None:
        self._event_callback = callback

    def format_mention(self, user_id: str) -> str:
        return "<@%s>" % (user_id,)

    async def set_allowed_guild_ids(self, ids: Iterable[int]) -> None:
        new_ids = {int(x) for x in ids}
        self._allowed_guild_ids = new_ids
        if self._connected:
            await self._sidecar.update_guild_channels(new_ids)
            if new_ids:
                await self._sidecar.register_persona_guilds(self._persona_id, new_ids)

    async def update_guild_ids(self, ids: Iterable[int]) -> None:
        await self.set_allowed_guild_ids(ids)

    async def get_user_info(self, user_id: str, server_id: str = "") -> dict | None:
        if not self._connected:
            return None
        r = await self._sidecar.get_user_info(self._persona_id, user_id, server_id)
        if not r.ok or not r.data:
            return None
        return dict(r.data)

    async def get_channel(self, channel_id: str) -> dict | None:
        if not self._connected:
            return None
        r = await self._sidecar.get_channel(self._persona_id, channel_id)
        if not r.ok or not r.data:
            return None
        return dict(r.data)

    def _guild_allowed_id(self, server_id: str) -> bool:
        if not server_id.strip():
            return False
        try:
            gid = int(server_id)
        except (TypeError, ValueError):
            return False
        return gid in self._allowed_guild_ids

    async def _dispatch(self, event: NormalizedEvent) -> None:
        if not self._guild_allowed_id(event.server_id):
            return
        cb = self._event_callback
        if cb is not None:
            await cb(event)

    async def connect(self) -> None:
        await self._sidecar.start_event_consumer(self._dispatch, self._allowed_guild_ids)
        if self._allowed_guild_ids:
            await self._sidecar.register_persona_guilds(self._persona_id, self._allowed_guild_ids)
        self._connected = True
        self._refresh_task = asyncio.create_task(self._guild_refresh_loop())

    async def _guild_refresh_loop(self) -> None:
        """Re-register persona->guild TTL in Redis every 120s for long-lived processes."""
        while self._connected and not ckit_shutdown.shutdown_event.is_set():
            await ckit_shutdown.wait(120.0)
            if not self._connected:
                break
            if self._allowed_guild_ids:
                await self._sidecar.register_persona_guilds(self._persona_id, self._allowed_guild_ids)

    async def disconnect(self) -> None:
        self._connected = False
        rt = self._refresh_task
        self._refresh_task = None
        if rt is not None:
            rt.cancel()
            try:
                await rt
            except asyncio.CancelledError:
                pass
        await self._sidecar.unregister_persona_guilds(self._persona_id)
        await self._sidecar.close()

    async def execute_action(self, action_type: str, params: dict) -> ActionResult:
        if not self._connected:
            return ActionResult(ok=False, error="not_connected")
        return await self._sidecar.execute_action(
            self._persona_id,
            action_type,
            params,
        )
