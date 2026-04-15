# Automation catalog descriptors: persisted-rule semantics and trigger/action metadata for schema assembly.
# Runtime connector contracts (NormalizedEvent, ChatConnector) live in ckit_connector.

from __future__ import annotations

import dataclasses
from typing import Any


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
