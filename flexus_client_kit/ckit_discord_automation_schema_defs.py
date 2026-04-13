"""
Discord-specific automation trigger/action JSON Schema fragments (automation_schema_version 1).

Schemas for guild-scoped triggers and Discord actions live here; product-level definitions are in
ckit_automation_schema_defs. The full document is assembled by ckit_automation_v1_schema_build.
"""

from __future__ import annotations

SCHEMA_TRIGGER_MEMBER_JOINED = {
    "type": "object",
    "required": ["type"],
    "additionalProperties": False,
    "properties": {
        "type": {"const": "member_joined"},
    },
    "description": (
        "Fires on Discord on_member_join (or equivalent member record creation for backfill). "
        "No extra trigger fields; context is the joining user's ids and username from the event."
    ),
}

SCHEMA_TRIGGER_MEMBER_REMOVED = {
    "type": "object",
    "required": ["type"],
    "additionalProperties": False,
    "properties": {
        "type": {"const": "member_removed"},
    },
    "description": (
        "Fires when a member leaves or is removed from the server. No extra saved fields; "
        "guild and member context come from the leave/kick event."
    ),
}

SCHEMA_TRIGGER_MESSAGE_IN_CHANNEL = {
    "type": "object",
    "required": ["type", "channel_id_field"],
    "additionalProperties": False,
    "properties": {
        "type": {"const": "message_in_channel"},
        "channel_id_field": {
            "type": "string",
            "minLength": 1,
            "description": (
                "Reference to a setup field name containing the target channel snowflake "
                "(e.g. 'intro_channel_id'), or a literal snowflake string prefixed with '#' "
                "(e.g. '#1234567890')."
            ),
        },
    },
    "description": (
        "Fires when any guild member posts a message in the specified channel. "
        "Only messages in the configured channel are delivered as events to the bot."
    ),
}

SCHEMA_ACTION_SEND_DM = {
    "type": "object",
    "required": ["type"],
    "additionalProperties": False,
    "properties": {
        "type": {"const": "send_dm"},
        "template": {
            "type": "string",
            "description": "Inline message body. Supports {field_name} placeholders resolved from the event member snapshot and setup fields.",
        },
        "template_field": {
            "type": "string",
            "description": (
                "Alternative: name of a setup field containing the message body. "
                "Mutually preferred over 'template' when operator should edit copy in Setup UI."
            ),
        },
    },
    "description": "Send a DM to the member. Exactly one of 'template' or 'template_field' should be provided.",
}

SCHEMA_ACTION_POST_TO_CHANNEL = {
    "type": "object",
    "required": ["type", "channel_id_field", "template"],
    "additionalProperties": False,
    "properties": {
        "type": {"const": "post_to_channel"},
        "channel_id_field": {
            "type": "string",
            "description": "Setup field name or literal '#snowflake' for the target channel.",
        },
        "template": {
            "type": "string",
            "description": "Message body with {field_name} placeholders.",
        },
    },
    "description": "Post a message to a guild channel.",
}

SCHEMA_ACTION_ADD_ROLE = {
    "type": "object",
    "required": ["type", "role_id_field"],
    "additionalProperties": False,
    "properties": {
        "type": {"const": "add_role"},
        "role_id_field": {
            "type": "string",
            "minLength": 1,
            "description": (
                "Setup field name holding the role snowflake, or a literal id (digits) or '#snowflake', "
                "same resolution rules as channel_id_field. Member and server come from automation context."
            ),
        },
    },
    "description": "Add a Discord role to the member in context for the current server.",
}

SCHEMA_ACTION_REMOVE_ROLE = {
    "type": "object",
    "required": ["type", "role_id_field"],
    "additionalProperties": False,
    "properties": {
        "type": {"const": "remove_role"},
        "role_id_field": {
            "type": "string",
            "minLength": 1,
            "description": (
                "Setup field name holding the role snowflake, or literal id / '#snowflake'. "
                "Member and server come from automation context."
            ),
        },
    },
    "description": "Remove a Discord role from the member in context for the current server.",
}

SCHEMA_ACTION_KICK = {
    "type": "object",
    "required": ["type"],
    "additionalProperties": False,
    "properties": {
        "type": {"const": "kick"},
        "reason": {
            "type": "string",
            "description": (
                "Optional audit reason shown in Discord. Supports {field_name} placeholders like message templates."
            ),
        },
    },
    "description": "Kick the member in context from the current server. Guild and user ids are filled by the runtime.",
}
