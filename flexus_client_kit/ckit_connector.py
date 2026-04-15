# Abstract chat platform connector (unified bot plan U3): normalized events, actions, runtime ChatConnector API.
# Automation catalog descriptors (TriggerDescriptor, ActionDescriptor, SemanticContract) live in ckit_automation_catalog.

from __future__ import annotations

import abc
import dataclasses
import logging
from typing import Any, Awaitable, Callable

from flexus_client_kit.ckit_automation_catalog import ActionDescriptor, TriggerDescriptor

logger = logging.getLogger(__name__)


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
