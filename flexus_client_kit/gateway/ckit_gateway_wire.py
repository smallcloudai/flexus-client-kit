from __future__ import annotations

import dataclasses
import hashlib
from typing import Any

from flexus_client_kit.ckit_connector import ActionResult, NormalizedEvent

# Wire version for cmd/reply JSON envelopes (service_discord_gateway <-> Redis <-> backend callers).
WIRE_V = 1


def gateway_instance_key_from_token(token: str) -> str:
    t = (token or "").strip().encode("utf-8")
    return hashlib.sha256(t).hexdigest()[:32]


def channel_cmd_discord(gateway_instance_key: str) -> str:
    return "gw:discord:%s:cmd" % (gateway_instance_key,)


def channel_reply_discord(gateway_instance_key: str, request_id: str) -> str:
    return "gw:discord:%s:reply:%s" % (gateway_instance_key, request_id)


@dataclasses.dataclass
class GatewayActionCommandEnvelope:
    v: int
    request_id: str
    platform: str
    gateway_instance_key: str
    persona_id: str
    action_type: str
    params: dict[str, Any]
    reply_channel: str


@dataclasses.dataclass
class GatewayActionResultEnvelope:
    v: int
    request_id: str
    result: dict[str, Any]


def normalized_event_from_dict(d: dict[str, Any]) -> NormalizedEvent:
    return NormalizedEvent(
        source=str(d["source"]),
        server_id=str(d["server_id"]),
        channel_id=str(d["channel_id"]),
        user_id=str(d["user_id"]),
        event_type=str(d["event_type"]),
        payload=dict(d.get("payload") or {}),
        timestamp=float(d["timestamp"]),
    )


def action_result_to_dict(r: ActionResult) -> dict[str, Any]:
    return dataclasses.asdict(r)


def action_result_from_dict(d: dict[str, Any]) -> ActionResult:
    return ActionResult(
        ok=bool(d["ok"]),
        error=d.get("error"),
        data=dict(d["data"]) if d.get("data") is not None else None,
    )


def parse_action_command_envelope(raw: dict[str, Any]) -> GatewayActionCommandEnvelope | None:
    try:
        if int(raw["v"]) != WIRE_V:
            return None
        return GatewayActionCommandEnvelope(
            v=int(raw["v"]),
            request_id=str(raw["request_id"]),
            platform=str(raw["platform"]),
            gateway_instance_key=str(raw["gateway_instance_key"]),
            persona_id=str(raw["persona_id"]),
            action_type=str(raw["action_type"]),
            params=dict(raw.get("params") or {}),
            reply_channel=str(raw["reply_channel"]),
        )
    except (KeyError, TypeError, ValueError):
        return None


def gateway_result_envelope_from_dict(raw: dict[str, Any]) -> GatewayActionResultEnvelope | None:
    try:
        if int(raw["v"]) != WIRE_V:
            return None
        return GatewayActionResultEnvelope(
            v=int(raw["v"]),
            request_id=str(raw["request_id"]),
            result=dict(raw["result"]),
        )
    except (KeyError, TypeError, ValueError):
        return None
