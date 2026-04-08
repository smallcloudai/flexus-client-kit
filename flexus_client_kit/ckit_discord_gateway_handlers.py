from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

import discord

from flexus_client_kit.ckit_connector import NormalizedEvent


def bind_discord_gateway_client(
    client: discord.Client,
    emit: Callable[[NormalizedEvent], Awaitable[None]],
) -> None:
    @client.event
    async def on_ready() -> None:
        for g in list(client.guilds):
            await _emit_server_connected(g, emit)

    @client.event
    async def on_member_join(member: discord.Member) -> None:
        if member.bot:
            return
        await emit(
            NormalizedEvent(
                source="discord",
                server_id=str(member.guild.id),
                channel_id="",
                user_id=str(member.id),
                event_type="member_joined",
                payload={
                    "username": str(member),
                    "guild_id": int(member.guild.id),
                    "user_id": int(member.id),
                },
                timestamp=time.time(),
            ),
        )

    @client.event
    async def on_message(message: discord.Message) -> None:
        if message.author.bot:
            return
        if not message.guild:
            return
        if isinstance(message.channel, discord.DMChannel):
            return
        await emit(
            NormalizedEvent(
                source="discord",
                server_id=str(message.guild.id),
                channel_id=str(message.channel.id),
                user_id=str(message.author.id),
                event_type="message_in_channel",
                payload={
                    "content": message.content or "",
                    "channel_id": int(message.channel.id),
                    "guild_id": int(message.guild.id),
                    "user_id": int(message.author.id),
                    "message_id": str(message.id),
                },
                timestamp=time.time(),
            ),
        )

    @client.event
    async def on_member_remove(member: discord.Member) -> None:
        if member.bot:
            return
        await emit(
            NormalizedEvent(
                source="discord",
                server_id=str(member.guild.id),
                channel_id="",
                user_id=str(member.id),
                event_type="member_removed",
                payload={
                    "username": str(member),
                    "guild_id": int(member.guild.id),
                    "user_id": int(member.id),
                },
                timestamp=time.time(),
            ),
        )

    @client.event
    async def on_guild_remove(guild: discord.Guild) -> None:
        await emit(
            NormalizedEvent(
                source="discord",
                server_id=str(guild.id),
                channel_id="",
                user_id="",
                event_type="server_disconnected",
                payload={"guild_id": int(guild.id)},
                timestamp=time.time(),
            ),
        )

    @client.event
    async def on_guild_join(guild: discord.Guild) -> None:
        await _emit_server_connected(guild, emit)

    @client.event
    async def on_guild_available(guild: discord.Guild) -> None:
        await _emit_server_connected(guild, emit)


async def _emit_server_connected(
    g: discord.Guild,
    emit: Callable[[NormalizedEvent], Awaitable[None]],
) -> None:
    mc = getattr(g, "member_count", None)
    if mc is None:
        mc = 0
    await emit(
        NormalizedEvent(
            source="discord",
            server_id=str(g.id),
            channel_id="",
            user_id="",
            event_type="server_connected",
            payload={
                "guild_id": int(g.id),
                "guild_name": g.name or "",
                "approx_member_count": int(mc),
            },
            timestamp=time.time(),
        ),
    )
