from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Iterable
from typing import Any, Awaitable, Callable

import discord
from discord.errors import DiscordException

import flexus_client_kit.integrations.fi_discord2 as dc
from flexus_client_kit.ckit_discord_actions import discord_run_platform_action
from flexus_client_kit.ckit_automation_schema_defs import (
    SCHEMA_ACTION_CANCEL_PENDING_JOBS,
    SCHEMA_ACTION_ENQUEUE_CHECK,
    SCHEMA_ACTION_SET_CRM_FIELD,
    SCHEMA_ACTION_SET_STATUS,
    SCHEMA_TRIGGER_CRM_FIELD_CHANGED,
    SCHEMA_TRIGGER_SCHEDULED_RELATIVE_TO_FIELD,
    SCHEMA_TRIGGER_STATUS_TRANSITION,
)
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
    ActionResult,
    ChatConnector,
    NormalizedEvent,
    SemanticContract,
    TriggerDescriptor,
    semantic_contract_to_dict,
)

logger = logging.getLogger(__name__)

_transports: dict[str, "_SharedDiscordTransport"] = {}
_transports_lock = asyncio.Lock()


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
            operator_summary="Runs when someone joins a Discord server the bot is allowed to see.",
            rule_author_configures=("trigger.type member_joined only (no extra trigger fields in saved JSON).",),
            platform_fills_automatically=(
                "DiscordConnector._handle_member_join sets NormalizedEvent.server_id to the guild id string, "
                "user_id to the joined member id string, payload guild_id/user_id integers and username string.",
                "Bot loads CRM member_doc for that guild and user before process_event.",
            ),
            runtime_guarantees=(
                "ckit_automation_engine.match_trigger(event_type member_joined) is true iff rule trigger.type is member_joined.",
                "Conditions and actions see the current CRM member row for the joined user.",
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
                "resolve_channel_id(channel_id_field, setup) supplies the int channel id for matching.",
                "Event payload channel_id/guild_id/user_id/content/message_id come from DiscordConnector._handle_message.",
            ),
            runtime_guarantees=(
                "match_trigger requires event_data channel_id to equal resolve_channel_id result (both ints); "
                "missing or unresolvable channel_id_field yields no match.",
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
                "DiscordConnector._handle_member_remove emits NormalizedEvent with user_id and payload guild_id/user_id "
                "for the leaving member; CRM row is updated before rules run.",
            ),
            runtime_guarantees=(
                "match_trigger(member_removed) is true iff rule trigger.type is member_removed.",
                "discord_bot runs member_removed rules after handle_member_remove, then status_transition to churned.",
            ),
            operator_must_not_set=("Extra trigger payload keys beyond type in persisted rules.",),
        ),
        automation_schema_def=SCHEMA_TRIGGER_MEMBER_REMOVED,
    ),
    TriggerDescriptor(
        type="crm_field_changed",
        label="CRM field changed",
        description="Fires when a CRM field is modified by another rule",
        payload_schema={
            "type": "object",
            "properties": {
                "field_name": {"type": "string"},
                "new_value": {},
            },
        },
        semantic_contract=SemanticContract(
            operator_summary="Runs after another action updates a CRM field on the same member.",
            rule_author_configures=(
                "trigger.field_name; optional trigger.to_value to restrict to one new value.",
            ),
            platform_fills_automatically=(
                "ckit_automation_actions.execute_actions returns field_change dicts; _run_cascade calls process_event "
                "with event_type crm_field_changed and event_data field_name/new_value from the change.",
            ),
            runtime_guarantees=(
                "match_trigger compares trigger.field_name to event_data.field_name; to_value omitted matches any new_value.",
            ),
            operator_must_not_set=(),
        ),
        automation_schema_def=SCHEMA_TRIGGER_CRM_FIELD_CHANGED,
    ),
    TriggerDescriptor(
        type="status_transition",
        label="Status transition",
        description="Fires when lifecycle_status changes",
        payload_schema={
            "type": "object",
            "properties": {
                "old_status": {"type": "string"},
                "new_status": {"type": "string"},
            },
        },
        semantic_contract=SemanticContract(
            operator_summary="Runs when lifecycle_status on the member row changes.",
            rule_author_configures=("trigger.to_status; optional trigger.from_status.",),
            platform_fills_automatically=(
                "Synthetic event_data old_status/new_status from set_status field_change or member remove flow.",
            ),
            runtime_guarantees=(
                "match_trigger requires event_data new_status to equal trigger.to_status; from_status optional same way as crm to_value.",
            ),
            operator_must_not_set=(),
        ),
        automation_schema_def=SCHEMA_TRIGGER_STATUS_TRANSITION,
    ),
    TriggerDescriptor(
        type="scheduled_relative_to_field",
        label="Scheduled check",
        description="Fires after a delay relative to a CRM field timestamp",
        payload_schema={
            "type": "object",
            "properties": {
                "anchor_field": {"type": "string"},
                "delay_seconds": {"type": "integer"},
            },
        },
        semantic_contract=SemanticContract(
            operator_summary="Runs later when a job fires for this rule after a delay from an anchor timestamp.",
            rule_author_configures=(
                "trigger.anchor_field (CRM unix float), trigger.delay_seconds, rule rule_id matched by the job.",
            ),
            platform_fills_automatically=(
                "make_automation_job_handler schedules dc_community_jobs; handler builds event_data check_rule_id guild_id user_id.",
            ),
            runtime_guarantees=(
                "match_trigger(scheduled_check) requires trigger.type scheduled_relative_to_field and "
                "event_data.check_rule_id == rule.rule_id.",
                "discord_bot after member_joined may call execute_actions with a synthetic enqueue_check "
                "that copies trigger anchor_field and delay_seconds so _do_enqueue_check schedules at anchor+delay.",
            ),
            operator_must_not_set=(),
        ),
        automation_schema_def=SCHEMA_TRIGGER_SCHEDULED_RELATIVE_TO_FIELD,
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
            operator_summary="Send a private message to the member in context (automation) or to explicit ids (connector API).",
            rule_author_configures=(
                "Persisted automation: exactly one of template or template_field for the body (automation_v1).",
                "Connector call: user_id and text parameters as in parameter_schema.",
            ),
            platform_fills_automatically=(
                "Engine: _resolve_body_fields sets _resolved_body using resolve_template on template or setup[template_field].",
                "Executor _do_send_dm with connector passes user_id from member_doc and text from _resolved_body; "
                "it does not read a recipient from the action dict beyond what member_doc supplies.",
            ),
            runtime_guarantees=(
                "Empty _resolved_body after resolution fails with empty_body.",
                "discord_run_platform_action send_dm uses params user_id text only.",
            ),
            operator_must_not_set=(
                "Persisted rule: user_id field on the action (not in schema); recipient is always the CRM member in context.",
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
            operator_summary="Post a message into a chosen channel; guild scope comes from execution context when using the connector.",
            rule_author_configures=(
                "Persisted automation: channel_id_field and template (engine also resolves template_field like send_dm).",
                "Connector call: channel_id text required; optional server_id disambiguates allowed guild in discord_run_platform_action.",
            ),
            platform_fills_automatically=(
                "Engine: _resolve_channel_id(channel_id_field) -> _resolved_channel_id; _resolve_body_fields -> _resolved_body.",
                "Executor _do_post_to_channel passes ctx.server_id into payload server_id when non-empty so the connector "
                "can resolve guild_not_allowed against allowed guilds.",
            ),
            runtime_guarantees=(
                "discord_run_platform_action post_to_channel loads the channel, requires TextChannel, "
                "and resolve_guild(guild.id) must succeed or returns guild_not_allowed.",
            ),
            operator_must_not_set=(
                "Persisted rule: server_id on the action; guild is implied by the event or job ctx.server_id.",
            ),
        ),
        automation_schema_def=SCHEMA_ACTION_POST_TO_CHANNEL,
    ),
    ActionDescriptor(
        type="set_crm_field",
        label="Set CRM field",
        description="Update a field on the member's CRM record",
        parameter_schema={
            "type": "object",
            "properties": {
                "field": {"type": "string"},
                "value": {},
            },
            "required": ["field", "value"],
        },
        semantic_contract=SemanticContract(
            operator_summary="Write one field on the member CRM document for the current guild/user.",
            rule_author_configures=("field name and value; value may be literal or the string {now} before engine resolution.",),
            platform_fills_automatically=(
                "Engine _resolve_set_crm_now replaces literal value {now} with float time.time() before execute_actions.",
            ),
            runtime_guarantees=(
                "_do_set_crm_field updates Mongo by guild_id and user_id from member_doc; success refreshes ctx member_doc.",
            ),
            operator_must_not_set=("guild_id and user_id on the action; target row is ctx member_doc.",),
        ),
        automation_schema_def=SCHEMA_ACTION_SET_CRM_FIELD,
    ),
    ActionDescriptor(
        type="set_status",
        label="Set lifecycle status",
        description="Change the member's lifecycle status",
        parameter_schema={
            "type": "object",
            "properties": {"status": {"type": "string"}},
            "required": ["status"],
        },
        semantic_contract=SemanticContract(
            operator_summary="Set lifecycle_status on the member; may emit status_transition to other rules.",
            rule_author_configures=("status string.",),
            platform_fills_automatically=(),
            runtime_guarantees=(
                "_do_set_status uses member_doc guild_id user_id; returns field_change is_status True for cascades.",
            ),
            operator_must_not_set=("Explicit member keys on the action.",),
        ),
        automation_schema_def=SCHEMA_ACTION_SET_STATUS,
    ),
    ActionDescriptor(
        type="enqueue_check",
        label="Schedule a check",
        description="Enqueue a future scheduled check for this member",
        parameter_schema={
            "type": "object",
            "properties": {
                "check_rule_id": {"type": "string"},
                "delay_seconds": {"type": "integer"},
                "anchor_field": {"type": "string"},
            },
            "required": ["check_rule_id", "delay_seconds"],
        },
        semantic_contract=SemanticContract(
            operator_summary="Queue a future run of another rule for this member.",
            rule_author_configures=(
                "check_rule_id of the target rule, delay_seconds; optional anchor_field for delay relative to a CRM timestamp.",
            ),
            platform_fills_automatically=(
                "Job payload guild_id user_id persona_id filled from ctx member_doc and persona_id.",
            ),
            runtime_guarantees=(
                "Dedup: pending job same kind and guild/user skipped with note deduped.",
                "If anchor_field set, member_doc must have that field or action fails anchor_not_set.",
            ),
            operator_must_not_set=("guild_id and user_id in the action; taken from member_doc.",),
        ),
        automation_schema_def=SCHEMA_ACTION_ENQUEUE_CHECK,
    ),
    ActionDescriptor(
        type="cancel_pending_jobs",
        label="Cancel pending jobs",
        description="Cancel scheduled jobs matching a prefix",
        parameter_schema={
            "type": "object",
            "properties": {"job_kind_prefix": {"type": "string"}},
            "required": ["job_kind_prefix"],
        },
        semantic_contract=SemanticContract(
            operator_summary="Mark pending scheduled jobs done for this member whose kind starts with a prefix.",
            rule_author_configures=("job_kind_prefix string matched as regex prefix against dc_community_jobs.kind.",),
            platform_fills_automatically=("Scope restricted to payload.guild_id and payload.user_id from member_doc.",),
            runtime_guarantees=("_do_cancel_pending_jobs update_many sets done and cancelled flags.",),
            operator_must_not_set=(),
        ),
        automation_schema_def=SCHEMA_ACTION_CANCEL_PENDING_JOBS,
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
                "Engine resolve_role_id(role_id_field, setup) -> _resolved_role_id; executor passes user_id from member_doc "
                "and server_id from ctx to discord_run_platform_action.",
            ),
            runtime_guarantees=(
                "discord_run_platform_action add_role requires member and role in guild; fails member_or_role_not_found if not.",
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
            platform_fills_automatically=("Same resolution and ctx filling as add_role.",),
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
                "Executor supplies user_id from member_doc and server_id from ctx; optional reason resolved via "
                "resolve_template when present.",
            ),
            runtime_guarantees=(
                "discord_run_platform_action kick requires member in guild before kick; fails if member already left.",
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
                "ckit_automation_engine.resolve_channel_id returns None on invalid input; engine match or action resolution fails closed.",
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
                "ckit_automation_engine._resolve_body_fields writes _resolved_body for send_dm and post_to_channel only.",
            ),
            operator_must_not_set=(),
        ),
    ),
}


def discord_automation_semantics_bundle() -> dict[str, Any]:
    return {
        "semantic_schema_version": 1,
        "triggers": {t.type: semantic_contract_to_dict(t.semantic_contract) for t in DISCORD_TRIGGERS},
        "actions": {a.type: semantic_contract_to_dict(a.semantic_contract) for a in DISCORD_ACTIONS},
        "cross_cutting": dict(_DISCORD_AUTOMATION_CROSS_CUTTING),
    }


def discord_capability_export() -> dict[str, Any]:
    """
    Single source of truth for backend/UI: all triggers and actions the Discord integration supports.

    Reuses the TriggerDescriptor / ActionDescriptor data from DISCORD_TRIGGERS / DISCORD_ACTIONS so
    there is no second parallel catalog model. Backend can call this function to enumerate Discord
    capabilities without importing the descriptor lists directly.

    Return shape::

        {
          "integration": "discord",
          "version": 1,
          "triggers": [{"type": ..., "label": ..., "description": ..., "schema": {...}}, ...],
          "actions":  [{"type": ..., "label": ..., "description": ..., "schema": {...}}, ...],
        }
    """
    return {
        "integration": "discord",
        "version": 1,
        "triggers": [
            {
                "type": t.type,
                "label": t.label,
                "description": t.description,
                "schema": t.automation_schema_def,
            }
            for t in DISCORD_TRIGGERS
        ],
        "actions": [
            {
                "type": a.type,
                "label": a.label,
                "description": a.description,
                "schema": a.automation_schema_def,
            }
            for a in DISCORD_ACTIONS
        ],
    }


class DiscordConnector(ChatConnector):
    def __init__(
        self,
        token: str,
        persona_id: str,
        *,
        initial_guild_ids: set[int] | None = None,
    ) -> None:
        self._token = token
        self._persona_id = persona_id
        self._allowed_guild_ids: set[int] = set(initial_guild_ids or [])
        self._connected_announced: set[int] = set()
        self._missing_access_announced: set[int] = set()
        self._client: discord.Client | None = None
        self._task: asyncio.Task[None] | None = None
        self._shared_transport: _SharedDiscordTransport | None = None
        self._event_callback: Callable[[NormalizedEvent], Awaitable[None]] | None = None

    @property
    def platform(self) -> str:
        return "discord"

    @property
    def raw_client(self) -> discord.Client | None:
        return self._client

    @property
    def allowed_guild_ids(self) -> frozenset[int]:
        return frozenset(self._allowed_guild_ids)

    @property
    def guild(self) -> discord.Guild | None:
        c = self._client
        if c is None:
            return None
        for g in c.guilds:
            if int(g.id) in self._allowed_guild_ids:
                return g
        return c.guilds[0] if c.guilds else None

    def supported_triggers(self) -> list[TriggerDescriptor]:
        return DISCORD_TRIGGERS

    def supported_actions(self) -> list[ActionDescriptor]:
        return DISCORD_ACTIONS

    def on_event(self, callback: Callable[[NormalizedEvent], Awaitable[None]]) -> None:
        self._event_callback = callback

    def format_mention(self, user_id: str) -> str:
        return "<@%s>" % (user_id,)

    def _guild_allowed(self, guild: discord.Guild | None) -> bool:
        if guild is None:
            return False
        return int(guild.id) in self._allowed_guild_ids

    def _find_guild(self, guild_id: int) -> discord.Guild | None:
        c = self._client
        if c is None:
            return None
        if guild_id not in self._allowed_guild_ids:
            return None
        g = c.get_guild(guild_id)
        return g

    def _resolve_action_guild_id(self, params: dict) -> int | None:
        raw = params.get("server_id") or params.get("guild_id") or ""
        if raw is None or str(raw).strip() == "":
            return None
        try:
            gid = int(raw)
        except (TypeError, ValueError):
            return None
        return gid

    def _allowed_guild_ids_not_visible(
        self,
        client: discord.Client,
    ) -> set[int]:
        visible = {int(g.id) for g in client.guilds}
        return {gid for gid in self._allowed_guild_ids if gid not in visible}

    async def _emit_missing_allowed_guild_access_once(
        self,
        client: discord.Client,
        gids: Iterable[int],
    ) -> None:
        not_visible = self._allowed_guild_ids_not_visible(client)
        for gid in gids:
            if gid not in not_visible:
                continue
            if gid in self._missing_access_announced:
                continue
            dc.log_ctx(
                self._persona_id,
                gid,
                "allowed guild not visible to bot token (not in client.guilds / no access)",
            )
            await self._emit(
                NormalizedEvent(
                    source="discord",
                    server_id=str(gid),
                    channel_id="",
                    user_id="",
                    event_type="server_disconnected",
                    payload={
                        "guild_id": gid,
                        "missing_bot_access": True,
                    },
                    timestamp=time.time(),
                ),
            )
            self._missing_access_announced.add(gid)

    async def set_allowed_guild_ids(self, ids: Iterable[int]) -> None:
        new_set = {int(x) for x in ids}
        old = self._allowed_guild_ids
        removed = old - new_set
        added = new_set - old
        self._allowed_guild_ids = new_set
        for gid in removed:
            self._missing_access_announced.discard(gid)
            if gid in self._connected_announced:
                self._connected_announced.discard(gid)
                await self._emit(
                    NormalizedEvent(
                        source="discord",
                        server_id=str(gid),
                        channel_id="",
                        user_id="",
                        event_type="server_disconnected",
                        payload={"guild_id": gid},
                        timestamp=time.time(),
                    ),
                )
        c = self._client
        if c is not None:
            for g in list(c.guilds):
                gid = int(g.id)
                if gid in new_set and gid not in self._connected_announced:
                    await self._emit_server_connected(g)
            for gid in added:
                g = c.get_guild(gid)
                if g is not None and gid not in self._connected_announced:
                    await self._emit_server_connected(g)
                elif g is None:
                    await self._emit_missing_allowed_guild_access_once(c, [gid])

    async def update_guild_ids(self, ids: Iterable[int]) -> None:
        await self.set_allowed_guild_ids(ids)

    async def get_user_info(self, user_id: str, server_id: str = "") -> dict | None:
        c = self._client
        if c is None:
            return None
        try:
            uid = int(user_id)
        except (TypeError, ValueError):
            return None
        if server_id and str(server_id).strip():
            try:
                gid = int(server_id)
            except (TypeError, ValueError):
                return None
            g = self._find_guild(gid)
            if g is None:
                return None
            member = g.get_member(uid)
            if member is None:
                return None
            return {"user_id": str(member.id), "display_name": member.display_name}
        for gid in self._allowed_guild_ids:
            g = c.get_guild(gid)
            if g is None:
                continue
            member = g.get_member(uid)
            if member is not None:
                return {"user_id": str(member.id), "display_name": member.display_name}
        return None

    async def get_channel(self, channel_id: str) -> dict | None:
        c = self._client
        if c is None:
            return None
        try:
            cid = int(channel_id)
        except (TypeError, ValueError):
            return None
        ch = c.get_channel(cid)
        if ch is None:
            return None
        g = getattr(ch, "guild", None)
        if g is not None and not self._guild_allowed(g):
            return None
        nm = getattr(ch, "name", None) or ""
        out: dict = {"channel_id": str(ch.id), "name": nm, "type": str(ch.type)}
        if g is not None:
            out["guild_id"] = str(g.id)
            me = g.me
            if me is not None and hasattr(ch, "permissions_for"):
                pr = ch.permissions_for(me)
                out["view_channel"] = pr.view_channel
                out["send_messages"] = pr.send_messages
                out["read_message_history"] = pr.read_message_history
                out["manage_messages"] = pr.manage_messages
        return out

    async def _emit(self, event: NormalizedEvent) -> None:
        cb = self._event_callback
        if cb is None:
            return
        await cb(event)

    async def _emit_server_connected(self, g: discord.Guild) -> None:
        gid = int(g.id)
        self._missing_access_announced.discard(gid)
        self._connected_announced.add(gid)
        mc = getattr(g, "member_count", None)
        if mc is None:
            mc = 0
        await self._emit(
            NormalizedEvent(
                source="discord",
                server_id=str(gid),
                channel_id="",
                user_id="",
                event_type="server_connected",
                payload={
                    "guild_id": gid,
                    "guild_name": g.name or "",
                    "approx_member_count": int(mc),
                },
                timestamp=time.time(),
            ),
        )

    async def _handle_member_join(self, member: discord.Member) -> None:
        if member.bot or not self._guild_allowed(member.guild):
            return
        event = NormalizedEvent(
            source="discord",
            server_id=str(member.guild.id),
            channel_id="",
            user_id=str(member.id),
            event_type="member_joined",
            payload={
                "username": str(member),
                "guild_id": int(member.guild.id),
                "user_id": int(member.id),
            },
            timestamp=time.time(),
        )
        await self._emit(event)

    async def _handle_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if not message.guild:
            return
        if isinstance(message.channel, discord.DMChannel):
            return
        if not self._guild_allowed(message.guild):
            return
        event = NormalizedEvent(
            source="discord",
            server_id=str(message.guild.id),
            channel_id=str(message.channel.id),
            user_id=str(message.author.id),
            event_type="message_in_channel",
            payload={
                "content": message.content or "",
                "channel_id": int(message.channel.id),
                "guild_id": int(message.guild.id),
                "user_id": int(message.author.id),
                "message_id": str(message.id),
            },
            timestamp=time.time(),
        )
        await self._emit(event)

    async def _handle_member_remove(self, member: discord.Member) -> None:
        if member.bot or not self._guild_allowed(member.guild):
            return
        event = NormalizedEvent(
            source="discord",
            server_id=str(member.guild.id),
            channel_id="",
            user_id=str(member.id),
            event_type="member_removed",
            payload={
                "username": str(member),
                "guild_id": int(member.guild.id),
                "user_id": int(member.id),
            },
            timestamp=time.time(),
        )
        await self._emit(event)

    async def _handle_guild_remove(self, guild: discord.Guild) -> None:
        gid = int(guild.id)
        if gid not in self._allowed_guild_ids and gid not in self._connected_announced:
            return
        if gid in self._connected_announced:
            self._connected_announced.discard(gid)
        if gid in self._allowed_guild_ids:
            self._missing_access_announced.add(gid)
        await self._emit(
            NormalizedEvent(
                source="discord",
                server_id=str(gid),
                channel_id="",
                user_id="",
                event_type="server_disconnected",
                payload={"guild_id": gid},
                timestamp=time.time(),
            ),
        )

    async def _handle_guild_join_available(self, guild: discord.Guild) -> None:
        if not self._guild_allowed(guild):
            return
        gid = int(guild.id)
        if gid in self._connected_announced:
            return
        await self._emit_server_connected(guild)

    async def _sync_shared_ready(self, client: discord.Client) -> None:
        for g in list(client.guilds):
            if self._guild_allowed(g) and int(g.id) not in self._connected_announced:
                await self._emit_server_connected(g)
        await self._emit_missing_allowed_guild_access_once(
            client,
            self._allowed_guild_ids,
        )

    async def connect(self) -> None:
        tr = await _get_or_create_transport(self._token)
        self._shared_transport = tr
        await tr.attach(self)

    async def disconnect(self) -> None:
        tr = self._shared_transport
        self._shared_transport = None
        if tr is not None:
            await tr.detach(self)
        self._client = None
        self._task = None
        self._connected_announced.clear()
        self._missing_access_announced.clear()

    async def execute_action(self, action_type: str, params: dict) -> ActionResult:
        client = self._client
        if client is None:
            return ActionResult(ok=False, error="not_connected")

        def resolve_guild(gid: int) -> discord.Guild | None:
            if gid not in self._allowed_guild_ids:
                return None
            return client.get_guild(gid)

        return await discord_run_platform_action(
            client,
            self._persona_id,
            action_type,
            params,
            resolve_guild=resolve_guild,
        )


class _SharedDiscordTransport:
    def __init__(self, token: str) -> None:
        self._token = token
        self._client: discord.Client | None = None
        self._task: asyncio.Task[None] | None = None
        self._connectors: set[DiscordConnector] = set()
        self._lock = asyncio.Lock()

    def _bind_client_events(self, client: discord.Client) -> None:
        tr = self

        @client.event
        async def on_ready() -> None:
            logger.info("discord shared transport ready as %s", client.user)
            for c in list(tr._connectors):
                await c._sync_shared_ready(client)

        @client.event
        async def on_member_join(member: discord.Member) -> None:
            for c in list(tr._connectors):
                await c._handle_member_join(member)

        @client.event
        async def on_message(message: discord.Message) -> None:
            for c in list(tr._connectors):
                await c._handle_message(message)

        @client.event
        async def on_member_remove(member: discord.Member) -> None:
            for c in list(tr._connectors):
                await c._handle_member_remove(member)

        @client.event
        async def on_guild_remove(guild: discord.Guild) -> None:
            for c in list(tr._connectors):
                await c._handle_guild_remove(guild)

        @client.event
        async def on_guild_join(guild: discord.Guild) -> None:
            for c in list(tr._connectors):
                await c._handle_guild_join_available(guild)

        @client.event
        async def on_guild_available(guild: discord.Guild) -> None:
            for c in list(tr._connectors):
                await c._handle_guild_join_available(guild)

    def _start_client(self) -> None:
        if self._client is not None:
            return
        client = discord.Client(intents=dc.build_intents())
        self._bind_client_events(client)
        self._client = client

        async def _runner() -> None:
            try:
                await client.start(self._token)
            except asyncio.CancelledError:
                raise
            except DiscordException as e:
                logger.error(
                    "discord shared transport died: %s %s",
                    type(e).__name__,
                    e,
                )

        self._task = asyncio.create_task(_runner())

    async def _stop_client(self) -> None:
        await dc.close_discord_client(self._client, self._task)
        self._client = None
        self._task = None
        async with _transports_lock:
            if _transports.get(self._token) is self:
                del _transports[self._token]

    async def attach(self, conn: DiscordConnector) -> None:
        async with self._lock:
            first = len(self._connectors) == 0
            self._connectors.add(conn)
            if first:
                self._start_client()
            assert self._client is not None
            conn._client = self._client
            cli = self._client
            if cli.is_ready():
                await conn._sync_shared_ready(cli)

    async def detach(self, conn: DiscordConnector) -> None:
        async with self._lock:
            self._connectors.discard(conn)
            conn._client = None
            if not self._connectors:
                await self._stop_client()


async def _get_or_create_transport(token: str) -> _SharedDiscordTransport:
    async with _transports_lock:
        existing = _transports.get(token)
        if existing is not None:
            return existing
        created = _SharedDiscordTransport(token)
        _transports[token] = created
        return created
