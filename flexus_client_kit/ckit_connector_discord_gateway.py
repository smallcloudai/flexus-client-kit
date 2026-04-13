from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable, Iterable
from typing import Any

import gql
import gql.transport.exceptions

from flexus_client_kit import ckit_client
from flexus_client_kit.ckit_connector import (
    ActionDescriptor,
    ActionResult,
    ChatConnector,
    NormalizedEvent,
    TriggerDescriptor,
)
from flexus_client_kit.ckit_connector_discord import DISCORD_ACTIONS, DISCORD_TRIGGERS
from flexus_client_kit.gateway.ckit_gateway_wire import gateway_instance_key_from_token

logger = logging.getLogger(__name__)

# Module-level GQL document so it is parsed once, not on every call.
_DISCORD_GW_ACTION = gql.gql("""
    mutation BotDiscordGatewayAction(
        $personaId: String!
        $instanceKey: String!
        $actionType: String!
        $params: JSON!
    ) {
        botDiscordGatewayAction(
            personaId: $personaId
            instanceKey: $instanceKey
            actionType: $actionType
            params: $params
        )
    }
""")


class DiscordGatewayConnector(ChatConnector):
    """Backend-backed gateway connector.

    Inbound events arrive via the standard bot_threads_calls_tasks / on_emessage("DISCORD")
    path — this connector no longer opens Redis event consumers.

    Outbound actions are forwarded to the backend bot_discord_gateway_action mutation which
    internally routes commands through the trusted Redis cmd channel to service_discord_gateway.
    """

    def __init__(
        self,
        token: str,
        persona_id: str,
        fclient: ckit_client.FlexusClient,
        *,
        initial_guild_ids: set[int] | None = None,
    ) -> None:
        self._persona_id = persona_id
        # Instance key derived locally from the token — pure function, no Redis needed.
        self._instance_key = gateway_instance_key_from_token(token)
        self._fclient = fclient
        self._allowed_guild_ids: set[int] = set(initial_guild_ids or [])
        # Kept for ChatConnector ABC compliance; not used in gateway mode
        # (events arrive via on_emessage instead of this callback).
        self._event_callback: Callable[[NormalizedEvent], Awaitable[None]] | None = None
        self._connected = False

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
        return self._instance_key

    def supported_triggers(self) -> list[TriggerDescriptor]:
        return DISCORD_TRIGGERS

    def supported_actions(self) -> list[ActionDescriptor]:
        return DISCORD_ACTIONS

    def on_event(self, callback: Callable[[NormalizedEvent], Awaitable[None]]) -> None:
        # Stored for ABC compliance; in gateway mode the bot uses on_emessage("DISCORD") instead.
        self._event_callback = callback

    def format_mention(self, user_id: str) -> str:
        return "<@%s>" % (user_id,)

    async def set_allowed_guild_ids(self, ids: Iterable[int]) -> None:
        """Update the in-memory guild allowlist. No Redis registration needed."""
        self._allowed_guild_ids = {int(x) for x in ids}

    async def update_guild_ids(self, ids: Iterable[int]) -> None:
        await self.set_allowed_guild_ids(ids)

    async def connect(self) -> None:
        """Mark connector as active. No Redis subscriptions are opened."""
        self._connected = True

    async def disconnect(self) -> None:
        """Mark connector as inactive."""
        self._connected = False

    async def get_user_info(self, user_id: str, server_id: str = "") -> dict | None:
        if not self._connected:
            return None
        r = await self.execute_action(
            "get_user_info",
            {"user_id": str(user_id), "server_id": str(server_id or "")},
        )
        if not r.ok or not r.data:
            return None
        return dict(r.data)

    async def get_channel(self, channel_id: str) -> dict | None:
        if not self._connected:
            return None
        r = await self.execute_action(
            "get_channel",
            {"channel_id": str(channel_id)},
        )
        if not r.ok or not r.data:
            return None
        return dict(r.data)

    async def execute_action(self, action_type: str, params: dict) -> ActionResult:
        if not self._connected:
            return ActionResult(ok=False, error="not_connected")
        try:
            http_client = await self._fclient.use_http_on_behalf(
                self._persona_id,
                "discord_gw_action",
                execute_timeout=95.0,
            )
            async with http_client as http:
                result = await http.execute(
                    _DISCORD_GW_ACTION,
                    variable_values={
                        "personaId": self._persona_id,
                        "instanceKey": self._instance_key,
                        "actionType": action_type,
                        "params": params,
                    },
                )
            data = result.get("botDiscordGatewayAction") or {}
            return ActionResult(
                ok=bool(data.get("ok")),
                error=data.get("error"),
                data=data.get("data"),
            )
        except gql.transport.exceptions.TransportError as e:
            logger.warning("discord gateway action transport error: %s %s", type(e).__name__, e)
            return ActionResult(ok=False, error="transport_error")
