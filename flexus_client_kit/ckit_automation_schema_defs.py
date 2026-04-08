"""
Generic automation trigger/action JSON Schema fragments (automation_schema_version 1).

These are platform-agnostic schemas shared across all integrations.
Discord-specific schemas (member_joined, send_dm, add_role, etc.) live in
ckit_discord_automation_schema_defs. Assembled into the full document by
ckit_automation_v1_schema_build.
"""

from __future__ import annotations

# --- Generic triggers ---

SCHEMA_TRIGGER_SCHEDULED_RELATIVE_TO_FIELD = {
    "type": "object",
    "required": ["type", "anchor_field", "delay_seconds"],
    "additionalProperties": False,
    "properties": {
        "type": {"const": "scheduled_relative_to_field"},
        "anchor_field": {
            "type": "string",
            "minLength": 1,
            "description": (
                "CRM member field name (float unix ts) that serves as T=0 for this rule. "
                "Example: 'member_joined_at', 'accepted_at'. The field MUST be populated by some "
                "trigger or action (see trigger_field_matrix.md)."
            ),
        },
        "delay_seconds": {
            "type": "integer",
            "minimum": 0,
            "description": "Seconds after anchor value to schedule the check. 172800 = 48h, 864000 = 10d.",
        },
    },
    "description": (
        "Engine schedules a job at anchor + delay when the anchor field is first set "
        "(or when rule is enabled and anchor already populated). The job re-evaluates conditions at fire time."
    ),
}

SCHEMA_TRIGGER_CRM_FIELD_CHANGED = {
    "type": "object",
    "required": ["type", "field_name"],
    "additionalProperties": False,
    "properties": {
        "type": {"const": "crm_field_changed"},
        "field_name": {
            "type": "string",
            "minLength": 1,
            "description": "CRM member field name to watch.",
        },
        "to_value": {
            "description": "Optional: fire only when the field transitions to this specific value. Omit to fire on any change.",
        },
    },
    "description": (
        "Fires synchronously when engine or tool sets the named CRM field. "
        "Useful for chaining (e.g. intro_done_at set -> cancel pending reminder)."
    ),
}

SCHEMA_TRIGGER_STATUS_TRANSITION = {
    "type": "object",
    "required": ["type", "to_status"],
    "additionalProperties": False,
    "properties": {
        "type": {"const": "status_transition"},
        "from_status": {
            "type": "string",
            "description": (
                "Optional: only fire when transitioning FROM this lifecycle_status. "
                "Omit to fire on any transition into to_status."
            ),
        },
        "to_status": {
            "type": "string",
            "description": "Fire when lifecycle_status becomes this value. Must match a value from crm_member lifecycle_status enum.",
        },
    },
    "description": "Fires when lifecycle_status changes. Subset of crm_field_changed but semantically clearer for status machines.",
}

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

# --- Generic actions ---

SCHEMA_ACTION_SET_CRM_FIELD = {
    "type": "object",
    "required": ["type", "field", "value"],
    "additionalProperties": False,
    "properties": {
        "type": {"const": "set_crm_field"},
        "field": {
            "type": "string",
            "minLength": 1,
            "description": "CRM member field to set.",
        },
        "value": {
            "description": (
                "Value to write. Special string '{now}' = current unix timestamp at execution time. "
                "Other strings/numbers written as-is."
            ),
        },
    },
    "description": (
        "Update a single CRM field on the member document. May trigger crm_field_changed rules in the same cycle."
    ),
}

SCHEMA_ACTION_SET_STATUS = {
    "type": "object",
    "required": ["type", "status"],
    "additionalProperties": False,
    "properties": {
        "type": {"const": "set_status"},
        "status": {
            "type": "string",
            "description": "New lifecycle_status value. Must match crm_member lifecycle_status enum.",
        },
    },
    "description": "Shorthand for set_crm_field on lifecycle_status. May trigger status_transition rules.",
}

SCHEMA_ACTION_ENQUEUE_CHECK = {
    "type": "object",
    "required": ["type", "delay_seconds", "check_rule_id"],
    "additionalProperties": False,
    "properties": {
        "type": {"const": "enqueue_check"},
        "delay_seconds": {
            "type": "integer",
            "minimum": 0,
            "description": "Seconds from now to schedule the follow-up check.",
        },
        "anchor_field": {
            "type": "string",
            "description": "Optional: if provided, delay is relative to this CRM field value instead of 'now'.",
        },
        "check_rule_id": {
            "type": "string",
            "description": (
                "rule_id to re-evaluate when the job fires. Conditions of that rule are checked at fire time "
                "(not at enqueue time)."
            ),
        },
    },
    "description": (
        "Schedule a future job for re-evaluation of another rule. "
        "Job dedup: (guild_id, user_id, check_rule_id) -- see idempotency.md."
    ),
}

SCHEMA_ACTION_CANCEL_PENDING_JOBS = {
    "type": "object",
    "required": ["type", "job_kind_prefix"],
    "additionalProperties": False,
    "properties": {
        "type": {"const": "cancel_pending_jobs"},
        "job_kind_prefix": {
            "type": "string",
            "minLength": 1,
            "description": (
                "Prefix matched against automation job kind for this (guild_id, user_id). "
                "All matching non-done jobs are marked done without execution."
            ),
        },
    },
    "description": "Cancel scheduled jobs that are no longer needed (e.g. cancel intro reminder when intro detected).",
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
        "Invoke a gatekeeper decision. Typically used in rules triggered by LLM expert output, "
        "not by deterministic automation. Included in schema for completeness; most gatekeeper logic lives in expert prompts."
    ),
}
