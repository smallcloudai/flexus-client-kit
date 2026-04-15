"""
Shared Discord helpers (no discord.py socket here): snowflake/setup/auth/logging for bots, connectors, fi_discord2.

Automation v1 trigger/action catalogs and ``discord_automation_semantics_bundle()`` live in
``ckit_connector_discord_catalog``; runtime ``DiscordLocalConnector`` is in ``ckit_connector_discord_local``.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

# Same logger name as fi_discord2.IntegrationDiscord / community utilities so log
# lines keep the same logger and formatting when code moves between modules.
_discord_shared_logger = logging.getLogger("discord")


def parse_snowflake(raw: str) -> Optional[int]:
    """
    Parse a bare decimal Discord snowflake string to int, or None if invalid.

    Accepts only stripped all-digit strings; used for setup ids and persona_external_addresses.
    """
    if not raw or not isinstance(raw, str):
        return None
    s = raw.strip()
    if not s or not s.isdigit():
        return None
    return int(s)


def setup_truthy(raw: Any) -> bool:
    """
    Coerce setup checkbox / string flags to bool (1, true, yes, on).

    Matches legacy community-bot semantics for disable_* and similar keys.
    """
    if raw is True:
        return True
    if raw is False or raw is None:
        return False
    s = str(raw).strip().lower()
    return s in ("1", "true", "yes", "on")


def discord_bot_api_key_from_external_auth(ext: Dict[str, Any]) -> str:
    """
    Resolve Discord bot token from workspace external_auth (legacy OAuth payloads).

    Precedence: discord_manual, then discord; skips non-dict provider values with a warning.
    """
    for provider_key in ("discord_manual", "discord"):
        raw = ext.get(provider_key)
        if raw is None:
            continue
        if not isinstance(raw, dict):
            _discord_shared_logger.warning(
                "discord_bot_api_key_from_external_auth: provider %r value is not a dict, skipping",
                provider_key,
            )
            continue
        tok = (raw.get("api_key") or "").strip()
        if tok:
            return tok
    return ""


def log_ctx(persona_id: str, guild_id: Optional[int], msg: str, *args: Any) -> None:
    """
    Prefix structured Discord integration logs with persona and optional guild id.

    Format matches historical fi_discord2 community-bot lines: [%s guild=%s] + message.
    """
    gid = str(guild_id) if guild_id is not None else "-"
    _discord_shared_logger.info("[%s guild=%s] " + msg, persona_id, gid, *args)
