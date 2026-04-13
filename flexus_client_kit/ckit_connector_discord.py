"""
Discord automation v1 catalogs and assist semantics (JSON Schema fragments, trigger/action descriptors).

Runtime ingress uses the gateway-backed ``DiscordGatewayConnector`` in ``ckit_connector_discord_gateway``;
there is no in-process discord.py client in this module. ``DISCORD_TRIGGERS``, ``DISCORD_ACTIONS``, and
``discord_automation_semantics_bundle()`` remain the single source for schema assembly and reviewer payloads.
"""

from __future__ import annotations

from typing import Any

from flexus_client_kit.ckit_discord_automation_schema_defs import (
    SCHEMA_ACTION_ADD_ROLE,
    SCHEMA_ACTION_KICK,
    SCHEMA_ACTION_POST_TO_CHANNEL,
    SCHEMA_ACTION_REMOVE_ROLE,
    SCHEMA_ACTION_SEND_DM,
    SCHEMA_TRIGGER_MEMBER_JOINED,
    SCHEMA_TRIGGER_MEMBER_REMOVED,
    SCHEMA_TRIGGER_MESSAGE_IN_CHANNEL,
)
from flexus_client_kit.ckit_connector import (
    ActionDescriptor,
    SemanticContract,
    TriggerDescriptor,
    semantic_contract_to_dict,
)

# --- Automation v1 Discord catalog (same source as supported_triggers / supported_actions / assist) ---

DISCORD_TRIGGERS: list[TriggerDescriptor] = [
    TriggerDescriptor(
        type="member_joined",
        label="Member joined",
        description="Fires when a new member joins the server",
        payload_schema={
            "type": "object",
            "properties": {
                "guild_id": {"type": "integer"},
                "user_id": {"type": "integer"},
                "username": {"type": "string"},
            },
        },
        semantic_contract=SemanticContract(
            operator_summary="Runs when someone joins a Discord server the bot can access.",
            rule_author_configures=("trigger.type member_joined only (no extra trigger fields in saved JSON).",),
            platform_fills_automatically=(
                "When someone joins, the normalized event carries the server id and member id; the payload includes "
                "guild id, user id, and display name.",
                "The worker builds in-memory event context (ids + username) for templates and actions; no persisted profile.",
            ),
            runtime_guarantees=(
                "A rule matches when its trigger type is member_joined and the incoming event is a join for that server.",
                "Conditions and actions apply to the current member in scope.",
            ),
            operator_must_not_set=("Trigger payload keys in persisted rules (automation_v1 has none beyond type).",),
        ),
        automation_schema_def=SCHEMA_TRIGGER_MEMBER_JOINED,
    ),
    TriggerDescriptor(
        type="message_in_channel",
        label="Message in channel",
        description="Fires when a message is posted in a watched channel",
        payload_schema={
            "type": "object",
            "properties": {
                "channel_id": {"type": "integer"},
                "guild_id": {"type": "integer"},
                "user_id": {"type": "integer"},
                "content": {"type": "string"},
                "message_id": {"type": "string"},
            },
        },
        semantic_contract=SemanticContract(
            operator_summary="Runs when a human posts in one configured channel.",
            rule_author_configures=("trigger.channel_id_field referencing a setup key, bare numeric id, or #snowflake literal.",),
            platform_fills_automatically=(
                "The channel reference from the bot setup is resolved to a numeric channel id for matching.",
                "The event payload includes channel, server, author, message text, and message id from the live message.",
            ),
            runtime_guarantees=(
                "Matching requires the event channel id to equal the resolved channel id from your setup; "
                "a missing or unresolvable channel reference yields no match.",
            ),
            operator_must_not_set=("Hard-coded channel ids inside trigger except via channel_id_field string form.",),
        ),
        automation_schema_def=SCHEMA_TRIGGER_MESSAGE_IN_CHANNEL,
    ),
    TriggerDescriptor(
        type="member_removed",
        label="Member left/kicked",
        description="Fires when a member leaves or is removed from the server",
        payload_schema={
            "type": "object",
            "properties": {
                "guild_id": {"type": "integer"},
                "user_id": {"type": "integer"},
                "username": {"type": "string"},
            },
        },
        semantic_contract=SemanticContract(
            operator_summary="Runs when someone leaves the server or is kicked (same Discord event).",
            rule_author_configures=("trigger.type member_removed only (no extra trigger fields in saved JSON).",),
            platform_fills_automatically=(
                "When someone leaves, the normalized event carries the member id, server id, and display name from Discord.",
            ),
            runtime_guarantees=(
                "A rule matches when its trigger type is member_removed and the event is a leave or kick for that member.",
            ),
            operator_must_not_set=("Extra trigger payload keys beyond type in persisted rules.",),
        ),
        automation_schema_def=SCHEMA_TRIGGER_MEMBER_REMOVED,
    ),
]


DISCORD_ACTIONS: list[ActionDescriptor] = [
    ActionDescriptor(
        type="send_dm",
        label="Send DM",
        description="Send a direct message to a user",
        parameter_schema={
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "text": {"type": "string"},
            },
            "required": ["user_id", "text"],
        },
        semantic_contract=SemanticContract(
            operator_summary="Send a private message to the member in context (saved automation) or to explicit ids (programmatic API).",
            rule_author_configures=(
                "Persisted automation: exactly one of template or template_field for the body (automation_v1).",
                "Programmatic call: user_id and text parameters as in parameter_schema.",
            ),
            platform_fills_automatically=(
                "The engine resolves the message body from the template or from a setup-backed field, then delivers it.",
                "For saved rules, the recipient is the user id from the triggering event; the action does not supply a separate recipient id.",
            ),
            runtime_guarantees=(
                "If the body is empty after resolution, delivery fails with empty_body.",
                "Direct-message delivery uses the resolved recipient id and body text only.",
            ),
            operator_must_not_set=(
                "Persisted rule: user_id field on the action (not in schema); recipient is always the member in context.",
            ),
        ),
        automation_schema_def=SCHEMA_ACTION_SEND_DM,
    ),
    ActionDescriptor(
        type="post_to_channel",
        label="Post to channel",
        description="Post a message in a text channel",
        parameter_schema={
            "type": "object",
            "properties": {
                "channel_id": {"type": "string"},
                "text": {"type": "string"},
                "server_id": {"type": "string"},
            },
            "required": ["channel_id", "text"],
        },
        semantic_contract=SemanticContract(
            operator_summary="Post a message into a chosen channel; guild scope comes from execution context when using the live integration.",
            rule_author_configures=(
                "Persisted automation: channel_id_field and template (engine also resolves template_field like send_dm).",
                "Programmatic call: channel_id text required; optional server_id disambiguates allowed guild when posting.",
            ),
            platform_fills_automatically=(
                "The engine resolves the channel id from the field reference and resolves the message body like direct messages.",
                "When posting, the current server scope is passed so delivery can reject unauthorized guilds.",
            ),
            runtime_guarantees=(
                "Posting loads the channel, requires a text channel, and the bot must be allowed in that server or delivery returns guild_not_allowed.",
            ),
            operator_must_not_set=(
                "Persisted rule: server_id on the action; guild is implied by the event or job execution scope.",
            ),
        ),
        automation_schema_def=SCHEMA_ACTION_POST_TO_CHANNEL,
    ),
    ActionDescriptor(
        type="add_role",
        label="Add role",
        description="Add a Discord role to the member",
        parameter_schema={
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "role_id": {"type": "string"},
                "server_id": {"type": "string"},
            },
            "required": ["user_id", "role_id"],
        },
        semantic_contract=SemanticContract(
            operator_summary="Add a Discord role to the member the rule is running for.",
            rule_author_configures=("role_id_field naming a setup key, literal role id, or #snowflake (same as channel_id_field).",),
            platform_fills_automatically=(
                "The engine resolves the role id from the field reference; the executor passes the member id and server scope for delivery.",
            ),
            runtime_guarantees=(
                "The member and role must exist in the server; otherwise delivery fails with member_or_role_not_found.",
            ),
            operator_must_not_set=("user_id, server_id, guild_id, role_id on persisted action; use role_id_field only.",),
        ),
        automation_schema_def=SCHEMA_ACTION_ADD_ROLE,
    ),
    ActionDescriptor(
        type="remove_role",
        label="Remove role",
        description="Remove a Discord role from the member",
        parameter_schema={
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "role_id": {"type": "string"},
                "server_id": {"type": "string"},
            },
            "required": ["user_id", "role_id"],
        },
        semantic_contract=SemanticContract(
            operator_summary="Remove a Discord role from the member the rule is running for.",
            rule_author_configures=("role_id_field like add_role.",),
            platform_fills_automatically=("Same role resolution and member/server scope as add_role.",),
            runtime_guarantees=("Same as add_role for guild and member resolution.",),
            operator_must_not_set=("user_id, server_id, guild_id, role_id on persisted action; use role_id_field only.",),
        ),
        automation_schema_def=SCHEMA_ACTION_REMOVE_ROLE,
    ),
    ActionDescriptor(
        type="kick",
        label="Kick member",
        description="Kick the member from the server",
        parameter_schema={
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "reason": {"type": "string"},
                "server_id": {"type": "string"},
            },
            "required": ["user_id"],
        },
        semantic_contract=SemanticContract(
            operator_summary="Kick the member the rule is running for from the current server.",
            rule_author_configures=("Optional reason string; supports {field} placeholders like message templates.",),
            platform_fills_automatically=(
                "The platform uses the current member and server in scope and resolves the reason text before delivery.",
            ),
            runtime_guarantees=(
                "Kick requires the member to be in the guild before kick; fails if the member already left.",
            ),
            operator_must_not_set=("user_id, server_id, guild_id on persisted action.",),
        ),
        automation_schema_def=SCHEMA_ACTION_KICK,
    ),
]


_DISCORD_AUTOMATION_CROSS_CUTTING: dict[str, dict[str, Any]] = {
    "resolve_channel_id": semantic_contract_to_dict(
        SemanticContract(
            operator_summary="Turns channel_id_field strings into integer Discord channel ids for matching and posting.",
            rule_author_configures=(
                "channel_id_field on trigger message_in_channel or action post_to_channel.",
            ),
            platform_fills_automatically=(
                "All-decimal string parses as int; #suffix parses suffix as int; else setup[key] coerced with int().",
            ),
            runtime_guarantees=(
                "Invalid channel references yield no resolved id; trigger matching and posting fail closed.",
            ),
            operator_must_not_set=(),
        ),
    ),
    "resolve_template": semantic_contract_to_dict(
        SemanticContract(
            operator_summary="Substitutes braced tokens in message templates for DM and channel posts.",
            rule_author_configures=(
                "template string and/or template_field referencing setup; send_dm and post_to_channel in automation.",
            ),
            platform_fills_automatically=(
                "{now} -> unix seconds; {mention} -> formatted mention from member user_id; "
                "other names from member then setup; unknown tokens left unchanged.",
            ),
            runtime_guarantees=(
                "Body resolution runs for direct message and channel post actions only; other actions do not use it.",
            ),
            operator_must_not_set=(),
        ),
    ),
}


def discord_automation_semantics_bundle() -> dict[str, Any]:
    """
    Flatten trigger/action semantic contracts plus cross-cutting helpers for assist payloads.

    Returns a JSON-serializable dict (semantic_schema_version, triggers, actions, cross_cutting).
    """
    try:
        return {
            "semantic_schema_version": 1,
            "triggers": {t.type: semantic_contract_to_dict(t.semantic_contract) for t in DISCORD_TRIGGERS},
            "actions": {a.type: semantic_contract_to_dict(a.semantic_contract) for a in DISCORD_ACTIONS},
            "cross_cutting": dict(_DISCORD_AUTOMATION_CROSS_CUTTING),
        }
    except (TypeError, KeyError, AttributeError) as e:
        raise RuntimeError("discord_automation_semantics_bundle: failed to assemble semantics dict") from e
