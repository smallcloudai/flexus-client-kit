# Abstract chat platform connector (unified bot plan U3): triggers, actions, normalized events.

from __future__ import annotations

import abc
import dataclasses
import logging
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class SemanticContract:
    """
    Canonical runtime semantics for one trigger or action: what authors persist, what the
    executor fills, and hard guarantees from engine + executor code (single source with descriptors).
    """

    operator_summary: str
    rule_author_configures: tuple[str, ...] = ()
    platform_fills_automatically: tuple[str, ...] = ()
    runtime_guarantees: tuple[str, ...] = ()
    operator_must_not_set: tuple[str, ...] = ()


def semantic_contract_to_dict(contract: SemanticContract | None) -> dict[str, Any] | None:
    if contract is None:
        return None
    return {
        "operator_summary": contract.operator_summary,
        "rule_author_configures": list(contract.rule_author_configures),
        "platform_fills_automatically": list(contract.platform_fills_automatically),
        "runtime_guarantees": list(contract.runtime_guarantees),
        "operator_must_not_set": list(contract.operator_must_not_set),
    }


@dataclasses.dataclass
class TriggerDescriptor:
    type: str
    label: str
    description: str
    payload_schema: dict
    semantic_contract: SemanticContract | None = None
    automation_schema_def: dict | None = None


@dataclasses.dataclass
class ActionDescriptor:
    type: str
    label: str
    description: str
    parameter_schema: dict
    semantic_contract: SemanticContract | None = None
    automation_schema_def: dict | None = None


@dataclasses.dataclass
class NormalizedEvent:
    source: str
    server_id: str
    channel_id: str
    user_id: str
    event_type: str
    payload: dict
    timestamp: float


@dataclasses.dataclass
class ActionResult:
    ok: bool
    error: str | None = None
    data: dict | None = None


class ChatConnector(abc.ABC):
    @property
    @abc.abstractmethod
    def platform(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def raw_client(self) -> Any:
        ...

    @abc.abstractmethod
    async def connect(self) -> None:
        ...

    @abc.abstractmethod
    async def disconnect(self) -> None:
        ...

    @abc.abstractmethod
    def supported_triggers(self) -> list[TriggerDescriptor]:
        ...

    @abc.abstractmethod
    def supported_actions(self) -> list[ActionDescriptor]:
        ...

    @abc.abstractmethod
    def on_event(self, callback: Callable[[NormalizedEvent], Awaitable[None]]) -> None:
        ...

    @abc.abstractmethod
    async def execute_action(self, action_type: str, params: dict) -> ActionResult:
        ...

    @abc.abstractmethod
    def format_mention(self, user_id: str) -> str:
        ...

    @abc.abstractmethod
    async def get_user_info(self, user_id: str, server_id: str = "") -> dict | None:
        ...

    @abc.abstractmethod
    async def get_channel(self, channel_id: str) -> dict | None:
        ...
