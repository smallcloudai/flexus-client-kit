"""
Product-level and shared JSON Schema fragments for automation_schema_version 1.

Discord-specific trigger/action shapes live in ckit_discord_automation_schema_defs and are
merged into the full document by ckit_automation_v1_schema_build.
"""

from __future__ import annotations

# Product-level trigger (not tied to any integration platform).
SCHEMA_TRIGGER_MANUAL_CAMPAIGN_PRODUCT = {
    "type": "object",
    "required": ["type"],
    "additionalProperties": False,
    "properties": {
        "type": {"const": "manual_campaign"},
        "segment_ref": {
            "type": "string",
            "description": "Optional reference to a saved segment definition or filter id. Omit for 'all members'.",
        },
    },
    "description": (
        "Not auto-triggered. Operator initiates from UI ('send now' or 'schedule at'). "
        "Segment filtering happens before per-member condition evaluation."
    ),
}

# Product-level action (not tied to any integration platform).
SCHEMA_ACTION_CALL_GATEKEEPER_PRODUCT = {
    "type": "object",
    "required": ["type", "tool_name"],
    "additionalProperties": False,
    "properties": {
        "type": {"const": "call_gatekeeper_tool"},
        "tool_name": {
            "type": "string",
            "enum": ["accept", "reject", "request_info"],
            "description": "Gatekeeper decision tool to invoke.",
        },
        "reason_template": {
            "type": "string",
            "description": "Optional message/reason with {field} placeholders.",
        },
    },
    "description": (
        "Invoke a gatekeeper decision. Typically used from expert-driven flows; "
        "workspace person-domain application state is updated, not local bot CRM."
    ),
}
