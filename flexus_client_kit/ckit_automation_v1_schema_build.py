"""
Build automation_schema_version 1 JSON Schema from a connector's capability catalog
(triggers + actions) plus product-only trigger/action defs. Single compile-time
assembly surface: backend validation and assist contracts derive from the same document.

Discord is the default/reference integration; pass triggers/actions explicitly to build
a schema for a different integration.
"""

from __future__ import annotations

import copy
from typing import Any

from flexus_client_kit.ckit_automation_schema_defs import (
    SCHEMA_ACTION_CALL_GATEKEEPER_PRODUCT,
    SCHEMA_TRIGGER_MANUAL_CAMPAIGN_PRODUCT,
)
from flexus_client_kit.ckit_connector_discord import DISCORD_ACTIONS, DISCORD_TRIGGERS


def _def_name_trigger(type_id: str) -> str:
    return "trigger_%s" % type_id


def _def_name_action(type_id: str) -> str:
    return "action_%s" % type_id


def _persisted_keys_from_schema_object(fragment: dict) -> frozenset[str]:
    props = fragment.get("properties")
    if not isinstance(props, dict):
        return frozenset()
    return frozenset(props.keys())


def automation_persisted_trigger_property_keys(
    triggers: list | None = None,
) -> dict[str, frozenset[str]]:
    """Return {type -> frozenset of persisted property names} for each trigger.

    Defaults to the Discord integration triggers. Pass ``triggers`` explicitly
    to use a different connector's catalog.
    """
    if triggers is None:
        triggers = DISCORD_TRIGGERS
    out: dict[str, frozenset[str]] = {}
    for t in triggers:
        d = t.automation_schema_def
        if d is None:
            raise RuntimeError("trigger %r missing automation_schema_def" % t.type)
        out[t.type] = _persisted_keys_from_schema_object(d)
    out["manual_campaign"] = _persisted_keys_from_schema_object(SCHEMA_TRIGGER_MANUAL_CAMPAIGN_PRODUCT)
    return out


def automation_persisted_action_property_keys(
    actions: list | None = None,
) -> dict[str, frozenset[str]]:
    """Return {type -> frozenset of persisted property names} for each action.

    Defaults to the Discord integration actions. Pass ``actions`` explicitly
    to use a different connector's catalog.
    """
    if actions is None:
        actions = DISCORD_ACTIONS
    out: dict[str, frozenset[str]] = {}
    for a in actions:
        d = a.automation_schema_def
        if d is None:
            raise RuntimeError("action %r missing automation_schema_def" % a.type)
        out[a.type] = _persisted_keys_from_schema_object(d)
    out["call_gatekeeper_tool"] = _persisted_keys_from_schema_object(SCHEMA_ACTION_CALL_GATEKEEPER_PRODUCT)
    return out


def schema_trigger_types_ordered(triggers: list | None = None) -> tuple[str, ...]:
    keys = sorted(automation_persisted_trigger_property_keys(triggers).keys())
    return tuple(keys)


def schema_action_types_ordered(actions: list | None = None) -> tuple[str, ...]:
    keys = sorted(automation_persisted_action_property_keys(actions).keys())
    return tuple(keys)


_STATIC_DEFS: dict[str, Any] = {
    "rule": {
        "type": "object",
        "required": ["rule_id", "enabled", "trigger"],
        "additionalProperties": False,
        "properties": {
            "rule_id": {
                "type": "string",
                "minLength": 1,
                "description": (
                    "Stable, human-readable id (e.g. 'intro-reminder-48h'). Unique within a config blob. "
                    "Used in job dedup keys and logs."
                ),
            },
            "enabled": {
                "type": "boolean",
                "description": "Master switch. Disabled rules are stored but never evaluated.",
            },
            "description": {
                "type": "string",
                "description": "Optional human-readable note shown in UI.",
            },
            "trigger": {"$ref": "#/$defs/trigger"},
            "conditions": {
                "type": "array",
                "items": {"$ref": "#/$defs/condition"},
                "default": [],
                "description": (
                    "All conditions are AND-ed. Empty array = unconditional (trigger alone is sufficient). "
                    "Used in flat (non-branched) rules."
                ),
            },
            "actions": {
                "type": "array",
                "items": {"$ref": "#/$defs/action"},
                "minItems": 1,
                "description": (
                    "Executed sequentially when trigger fires and all conditions pass. Used in flat (non-branched) rules."
                ),
            },
            "branches": {
                "type": "array",
                "items": {"$ref": "#/$defs/branch"},
                "minItems": 1,
                "description": (
                    "If/elif/else logic: first branch whose conditions all pass is executed, rest are skipped. "
                    "Mutually exclusive with top-level conditions+actions."
                ),
            },
        },
        "oneOf": [
            {"required": ["actions"]},
            {"required": ["branches"]},
        ],
    },
    "branch": {
        "type": "object",
        "required": ["actions"],
        "additionalProperties": False,
        "properties": {
            "label": {
                "type": "string",
                "description": "Optional UI label for this branch (e.g. 'English speakers', 'Default').",
            },
            "conditions": {
                "type": "array",
                "items": {"$ref": "#/$defs/condition"},
                "default": [],
                "description": (
                    "AND-ed conditions for this branch. Empty array = 'otherwise' (always matches, use as last branch)."
                ),
            },
            "actions": {
                "type": "array",
                "items": {"$ref": "#/$defs/action"},
                "minItems": 1,
                "description": "Actions to execute when this branch's conditions pass.",
            },
        },
        "description": "One branch in an if/elif/else chain. First matching branch wins.",
    },
    "condition": {
        "type": "object",
        "required": ["field", "op"],
        "additionalProperties": False,
        "properties": {
            "field": {
                "type": "string",
                "minLength": 1,
                "description": "CRM member field path to evaluate.",
            },
            "op": {
                "type": "string",
                "enum": ["eq", "neq", "gt", "lt", "is_set", "is_not_set", "elapsed_gt", "elapsed_lt"],
                "description": (
                    "Comparison operator. elapsed_gt/elapsed_lt: 'now - field_value > value_seconds' / '< value_seconds'. "
                    "is_set/is_not_set: field is non-null / null (value ignored)."
                ),
            },
            "value": {
                "description": (
                    "Comparison operand. Type depends on op: number for gt/lt/elapsed_*, string or number for eq/neq, "
                    "ignored for is_set/is_not_set."
                ),
            },
        },
        "description": "Single boolean predicate on a CRM field. All conditions in a rule are AND-ed.",
    },
}


def build_automation_v1_schema_document(
    triggers: list | None = None,
    actions: list | None = None,
) -> dict[str, Any]:
    """
    Assemble the full automation v1 JSON Schema document.

    ``triggers`` and ``actions`` are lists of TriggerDescriptor / ActionDescriptor from a
    connector's capability catalog. Defaults to the Discord integration. Pass different
    lists to produce a schema for another integration.
    """
    if triggers is None:
        triggers = DISCORD_TRIGGERS
    if actions is None:
        actions = DISCORD_ACTIONS

    defs: dict[str, Any] = dict(_STATIC_DEFS)

    trigger_refs: list[dict[str, str]] = []
    for t in sorted(triggers, key=lambda x: x.type):
        frag = t.automation_schema_def
        if frag is None:
            raise RuntimeError("trigger %s: automation_schema_def required" % t.type)
        name = _def_name_trigger(t.type)
        defs[name] = copy.deepcopy(frag)
        trigger_refs.append({"$ref": "#/$defs/%s" % name})

    defs["trigger_manual_campaign"] = copy.deepcopy(SCHEMA_TRIGGER_MANUAL_CAMPAIGN_PRODUCT)
    trigger_refs.append({"$ref": "#/$defs/trigger_manual_campaign"})
    trigger_refs.sort(key=lambda r: r["$ref"])

    defs["trigger"] = {
        "type": "object",
        "required": ["type"],
        "description": "Discriminated union on 'type'. Each type carries its own required payload fields.",
        "oneOf": trigger_refs,
    }

    action_refs: list[dict[str, str]] = []
    for a in sorted(actions, key=lambda x: x.type):
        frag = a.automation_schema_def
        if frag is None:
            raise RuntimeError("action %s: automation_schema_def required" % a.type)
        name = _def_name_action(a.type)
        defs[name] = copy.deepcopy(frag)
        action_refs.append({"$ref": "#/$defs/%s" % name})

    defs["action_call_gatekeeper_tool"] = copy.deepcopy(SCHEMA_ACTION_CALL_GATEKEEPER_PRODUCT)
    action_refs.append({"$ref": "#/$defs/action_call_gatekeeper_tool"})
    action_refs.sort(key=lambda r: r["$ref"])

    defs["action"] = {
        "type": "object",
        "required": ["type"],
        "description": "Discriminated union on 'type'.",
        "oneOf": action_refs,
    }

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "flexus-automation-v1",
        "title": "Flexus automation rules v1",
        "description": (
            "Machine-readable contract for community bot automation. Built from a connector's capability "
            "catalog (triggers + actions) plus product-level triggers/actions. "
            "Validate with jsonschema or check-jsonschema."
        ),
        "type": "object",
        "required": ["automation_schema_version", "rules"],
        "additionalProperties": False,
        "properties": {
            "automation_schema_version": {
                "const": 1,
                "description": "Schema version for forward-compatible migrations.",
            },
            "rules": {
                "type": "array",
                "items": {"$ref": "#/$defs/rule"},
                "description": (
                    "Ordered list of automation rules. Evaluation order matters only for actions that mutate state "
                    "consumed by later rules in the same event cycle."
                ),
            },
        },
        "$defs": defs,
    }


if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path

    p = argparse.ArgumentParser(description="Write automation v1 JSON Schema built from the Discord catalog.")
    p.add_argument(
        "--write",
        metavar="PATH",
        help="If set, write schema JSON to this path (UTF-8, indent 4).",
    )
    args = p.parse_args()
    # Default to Discord integration for the CLI tool.
    doc = build_automation_v1_schema_document(triggers=DISCORD_TRIGGERS, actions=DISCORD_ACTIONS)
    if args.write:
        Path(args.write).write_text(json.dumps(doc, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
