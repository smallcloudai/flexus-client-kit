from __future__ import annotations

import asyncio
import dataclasses
import json
import logging
import os
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

import redis.asyncio as aioredis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from flexus_client_kit import ckit_shutdown
from flexus_client_kit.ckit_connector import ActionResult, NormalizedEvent
from flexus_client_kit.gateway.ckit_gateway_wire import (
    WIRE_V,
    GatewayActionCommandEnvelope,
    GatewayActionResultEnvelope,
    GatewayEventEnvelope,
    action_result_from_dict,
    action_result_to_dict,
    channel_cmd_discord,
    channel_events_discord,
    channel_events_discord_guild,
    channel_reply_discord,
    gateway_instance_key_from_token,
    gateway_result_envelope_from_dict,
    normalized_event_from_dict,
    parse_event_envelope,
    registry_key_persona_guilds,
)

logger = logging.getLogger(__name__)


def _redis_common_kwargs() -> dict[str, Any]:
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = os.getenv("REDIS_PORT", "6379")
    return dict(
        host=redis_host,
        port=int(redis_port),
        username=os.getenv("REDIS_USER"),
        password=os.getenv("REDIS_PASSWORD"),
        db=int(os.getenv("REDIS_DB", "0")),
        decode_responses=True,
        socket_timeout=20,
        socket_connect_timeout=20,
        socket_keepalive=True,
        ssl_ca_certs=os.getenv("REDIS_CA_PATH"),
        ssl_certfile=os.getenv("REDIS_SSL_CERT"),
        ssl_keyfile=os.getenv("REDIS_SSL_KEY"),
        ssl=int(redis_port) == 6380,
        ssl_check_hostname=False,
        ssl_cert_reqs=None,
    )


def redis_client_from_env() -> aioredis.StrictRedis:
    return aioredis.StrictRedis(**_redis_common_kwargs())


def redis_pubsub_client_from_env() -> aioredis.StrictRedis:
    kw = _redis_common_kwargs()
    kw["socket_timeout"] = None
    kw["health_check_interval"] = 0
    return aioredis.StrictRedis(**kw)


class DiscordGatewayRedisSidecar:
    def __init__(
        self,
        token: str,
        *,
        redis_cmd: aioredis.StrictRedis | None = None,
        redis_pubsub: aioredis.StrictRedis | None = None,
    ) -> None:
        self._token = token
        self._key = gateway_instance_key_from_token(token)
        # Legacy broadcast channel kept for direct-socket / dev-fallback reference.
        self._events_ch = channel_events_discord(self._key)
        self._cmd_ch = channel_cmd_discord(self._key)
        self._redis_cmd = redis_cmd
        self._redis_pubsub = redis_pubsub
        self._own_cmd = redis_cmd is None
        self._own_pubsub = redis_pubsub is None
        self._stop = asyncio.Event()
        self._reader_task: asyncio.Task[None] | None = None
        self._cb: Callable[[NormalizedEvent], Awaitable[None]] | None = None
        # Live pubsub handle shared between reader loop and update_guild_channels.
        self._ps: Any | None = None
        # Currently active per-guild subscription channels.
        self._subscribed_guild_channels: set[str] = set()

    @property
    def gateway_instance_key(self) -> str:
        return self._key

    @property
    def events_channel(self) -> str:
        # Returns legacy broadcast channel for reference; production path uses per-guild channels.
        return self._events_ch

    @property
    def cmd_channel(self) -> str:
        return self._cmd_ch

    async def start_event_consumer(
        self,
        on_event: Callable[[NormalizedEvent], Awaitable[None]],
        guild_ids: set[int] | None = None,
    ) -> None:
        self._cb = on_event
        self._stop.clear()
        if self._redis_pubsub is None:
            self._redis_pubsub = redis_pubsub_client_from_env()
        initial_channels = {
            channel_events_discord_guild(self._key, str(g))
            for g in (guild_ids or set())
        }
        self._subscribed_guild_channels = initial_channels
        self._reader_task = asyncio.create_task(self._event_reader_loop(initial_channels))

    async def update_guild_channels(self, guild_ids: set[int]) -> None:
        """Subscribe to new per-guild channels and drop channels no longer in the allowed set."""
        new_channels = {channel_events_discord_guild(self._key, str(g)) for g in guild_ids}
        to_add = new_channels - self._subscribed_guild_channels
        to_remove = self._subscribed_guild_channels - new_channels
        ps = self._ps
        if ps is None:
            # Reader loop not yet running; track for when it starts.
            self._subscribed_guild_channels = new_channels
            return
        try:
            if to_add:
                await ps.subscribe(*to_add)
            if to_remove:
                await ps.unsubscribe(*to_remove)
        except (RedisConnectionError, OSError, RuntimeError) as e:
            logger.warning("update_guild_channels: %s %s", type(e).__name__, e)
        self._subscribed_guild_channels = new_channels

    async def register_persona_guilds(self, persona_id: str, guild_ids: set[int]) -> None:
        """Write persona->guild Set in Redis with a 300s TTL; called on connect and refresh."""
        if self._redis_cmd is None:
            self._redis_cmd = redis_client_from_env()
        reg_key = registry_key_persona_guilds(self._key, persona_id)
        try:
            pipe = self._redis_cmd.pipeline()
            pipe.delete(reg_key)
            if guild_ids:
                pipe.sadd(reg_key, *[str(g) for g in guild_ids])
            pipe.expire(reg_key, 300)
            await pipe.execute()
        except (RedisConnectionError, RedisTimeoutError, OSError, RuntimeError) as e:
            logger.warning("register_persona_guilds: %s %s", type(e).__name__, e)

    async def unregister_persona_guilds(self, persona_id: str) -> None:
        """Remove persona->guild Set from Redis on clean disconnect."""
        if self._redis_cmd is None:
            return
        reg_key = registry_key_persona_guilds(self._key, persona_id)
        try:
            await self._redis_cmd.delete(reg_key)
        except (RedisConnectionError, RedisTimeoutError, OSError, RuntimeError) as e:
            logger.warning("unregister_persona_guilds: %s %s", type(e).__name__, e)

    async def stop_event_consumer(self) -> None:
        self._stop.set()
        t = self._reader_task
        self._reader_task = None
        if t is not None:
            t.cancel()
            try:
                await t
            except asyncio.CancelledError:
                pass
        if self._own_pubsub and self._redis_pubsub is not None:
            await self._redis_pubsub.close()
            self._redis_pubsub = None

    async def close(self) -> None:
        await self.stop_event_consumer()
        if self._own_cmd and self._redis_cmd is not None:
            await self._redis_cmd.close()
            self._redis_cmd = None

    async def _event_reader_loop(self, initial_channels: set[str]) -> None:
        r = self._redis_pubsub
        if r is None:
            return
        ps = r.pubsub()
        self._ps = ps
        if initial_channels:
            await ps.subscribe(*initial_channels)
        try:
            while not self._stop.is_set() and not ckit_shutdown.shutdown_event.is_set():
                try:
                    msg = await ps.get_message(ignore_subscribe_messages=True, timeout=1.0)
                except (RedisConnectionError, RedisTimeoutError, OSError, RuntimeError) as e:
                    logger.warning("gateway event redis read: %s %s", type(e).__name__, e)
                    await ckit_shutdown.wait(1.0)
                    continue
                if not msg or msg.get("type") != "message":
                    continue
                data = msg.get("data")
                if not data:
                    continue
                try:
                    raw = json.loads(data)
                except json.JSONDecodeError:
                    continue
                env = parse_event_envelope(raw)
                if env is None:
                    continue
                cb = self._cb
                if cb is None:
                    continue
                try:
                    await cb(normalized_event_from_dict(env.event))
                except asyncio.CancelledError:
                    raise
        finally:
            self._ps = None
            try:
                await ps.close()
            except (RedisConnectionError, OSError, RuntimeError):
                pass

    async def get_user_info(
        self,
        persona_id: str,
        user_id: str,
        server_id: str = "",
        *,
        timeout_sec: float = 45.0,
    ) -> ActionResult:
        return await self.execute_action(
            persona_id,
            "get_user_info",
            {"user_id": str(user_id), "server_id": str(server_id or "")},
            timeout_sec=timeout_sec,
        )

    async def get_channel(
        self,
        persona_id: str,
        channel_id: str,
        *,
        timeout_sec: float = 45.0,
    ) -> ActionResult:
        return await self.execute_action(
            persona_id,
            "get_channel",
            {"channel_id": str(channel_id)},
            timeout_sec=timeout_sec,
        )

    async def execute_action(
        self,
        persona_id: str,
        action_type: str,
        params: dict,
        *,
        timeout_sec: float = 90.0,
    ) -> ActionResult:
        if self._redis_cmd is None:
            self._redis_cmd = redis_client_from_env()
        r = self._redis_cmd
        request_id = str(uuid.uuid4())
        reply_ch = channel_reply_discord(self._key, request_id)
        cmd = GatewayActionCommandEnvelope(
            v=WIRE_V,
            request_id=request_id,
            platform="discord",
            gateway_instance_key=self._key,
            persona_id=persona_id,
            action_type=action_type,
            params=params,
            reply_channel=reply_ch,
        )
        ps_r = redis_pubsub_client_from_env()
        ps = ps_r.pubsub()
        await ps.subscribe(reply_ch)
        try:
            payload = json.dumps(dataclasses.asdict(cmd))
            n = await r.publish(self._cmd_ch, payload)
            if n < 1:
                logger.warning("gateway cmd publish: no subscribers on %s", self._cmd_ch)
            deadline = time.monotonic() + timeout_sec
            while time.monotonic() < deadline:
                if ckit_shutdown.shutdown_event.is_set():
                    return ActionResult(ok=False, error="shutdown")
                try:
                    msg = await ps.get_message(
                        ignore_subscribe_messages=True,
                        timeout=min(5.0, max(0.5, deadline - time.monotonic())),
                    )
                except (RedisConnectionError, RedisTimeoutError, OSError, RuntimeError) as e:
                    logger.warning("gateway reply redis: %s %s", type(e).__name__, e)
                    await ckit_shutdown.wait(0.5)
                    continue
                if not msg or msg.get("type") != "message":
                    continue
                raw_data = msg.get("data")
                if not raw_data:
                    continue
                try:
                    raw = json.loads(raw_data)
                except json.JSONDecodeError:
                    continue
                renv = gateway_result_envelope_from_dict(raw)
                if renv is None or renv.request_id != request_id:
                    continue
                return action_result_from_dict(renv.result)
            return ActionResult(ok=False, error="action_timeout")
        finally:
            try:
                await ps.unsubscribe(reply_ch)
                await ps.close()
                await ps_r.close()
            except (RedisConnectionError, OSError, RuntimeError):
                pass
