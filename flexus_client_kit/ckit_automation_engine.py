"""
Pure automation rule engine: dict in, dict out. No Discord, Mongo, or async.

Community bots pass an in-memory member/event snapshot (fields from the current Discord event)
for condition checks and template resolution before the executor applies side effects.
"""

from __future__ import annotations

import copy
import logging
import re
import time

from flexus_client_kit import ckit_automation

logger = logging.getLogger(__name__)

# Regex for {placeholder} tokens in templates; word chars only (schema field names).
_PLACEHOLDER_RE = re.compile(r"\{(\w+)\}")

# Action types that may carry a message body via template or template_field (executor reads _resolved_body).
_BODY_ACTION_TYPES = frozenset({"send_dm", "post_to_channel"})

_ROLE_ACTION_TYPES = frozenset({"add_role", "remove_role"})


def _safe_float_pair(field_value, operand) -> tuple[float, float] | None:
    """
    Parse both sides to float for numeric comparisons. Returns None on any failure
    so callers can treat the condition as failed (fail-safe, no crash on bad data).
    """
    try:
        return (float(field_value), float(operand))
    except (TypeError, ValueError):
        return None


def _single_condition_ok(condition: dict, member: dict) -> bool:
    """
    Evaluate one condition dict against member. Caller ensures condition is a dict.
    Unknown op logs a warning and yields False (blocks the rule).
    """
    op = condition.get("op")
    field_name = condition.get("field")
    if not isinstance(field_name, str):
        return False
    field_value = member.get(field_name)

    if op == "eq":
        return field_value == condition["value"]
    if op == "neq":
        return field_value != condition["value"]
    if op == "gt":
        if field_value is None:
            return False
        pair = _safe_float_pair(field_value, condition["value"])
        return pair is not None and pair[0] > pair[1]
    if op == "lt":
        if field_value is None:
            return False
        pair = _safe_float_pair(field_value, condition["value"])
        return pair is not None and pair[0] < pair[1]
    if op == "is_set":
        return field_value is not None
    if op == "is_not_set":
        return field_value is None
    if op == "elapsed_gt":
        if field_value is None:
            return False
        pair = _safe_float_pair(field_value, condition["value"])
        return pair is not None and (time.time() - pair[0]) > pair[1]
    if op == "elapsed_lt":
        if field_value is None:
            return False
        pair = _safe_float_pair(field_value, condition["value"])
        return pair is not None and (time.time() - pair[0]) < pair[1]

    logger.warning("evaluate_conditions: unknown op %r (fail-safe False)", op)
    return False


def load_rules(persona_setup: dict) -> list[dict]:
    """
    Load enabled automation rules from persona_setup.  Delegates to
    resolve_automation_rules which prefers the new automation_rules setup field
    and falls back to the legacy automation_published key for backward
    compatibility.  Returns [] if missing or invalid.

    Rules with enabled=False are excluded; rules without an enabled field
    (legacy documents) are treated as enabled for backward compatibility.
    """
    try:
        published = ckit_automation.resolve_automation_rules(persona_setup)
        rules_raw = published.get("rules", [])
        if not isinstance(rules_raw, list):
            return []
        return [r for r in rules_raw if isinstance(r, dict) and r.get("enabled", True) is not False]
    except (KeyError, TypeError, ValueError) as e:
        logger.error("load_rules failed", exc_info=e)
        return []


def match_trigger(event_type: str, event_data: dict, rule: dict, setup: dict) -> bool:
    """
    Return True if this rule's trigger matches the synthetic event_type and payload.
    Unknown event_type -> False. Malformed rule/trigger -> False.
    """
    try:
        trigger = rule.get("trigger")
        if not isinstance(trigger, dict):
            return False
        ttype = trigger.get("type")

        if event_type == "member_joined":
            return ttype == "member_joined"

        if event_type == "member_removed":
            return ttype == "member_removed"

        if event_type == "message_in_channel":
            if ttype != "message_in_channel":
                return False
            ref = trigger.get("channel_id_field")
            if not isinstance(ref, str):
                return False
            resolved = resolve_channel_id(ref, setup)
            return event_data.get("channel_id") == resolved

        return False
    except (KeyError, TypeError, ValueError) as e:
        logger.error("match_trigger failed", exc_info=e)
        return False


def evaluate_conditions(conditions: list[dict], member: dict) -> bool:
    """
    AND all conditions; empty list is True. Reads fields from the member/event snapshot dict.
    """
    try:
        if not conditions:
            return True
        if not isinstance(conditions, list):
            return False
        if not isinstance(member, dict):
            return False
        for cond in conditions:
            if not isinstance(cond, dict):
                return False
            if not _single_condition_ok(cond, member):
                return False
        return True
    except (KeyError, TypeError, ValueError) as e:
        logger.error("evaluate_conditions failed", exc_info=e)
        return False


def resolve_template(template: str, member: dict, setup: dict) -> str:
    """
    Replace {name} placeholders: special keys now, mention; else member then setup.
    Unknown or unset placeholders stay literal in the output string.
    """
    try:
        if not isinstance(template, str):
            logger.warning(
                "resolve_template expected str, got %s",
                type(template).__name__,
            )
            return ""

        if not isinstance(member, dict):
            member = {}
        if not isinstance(setup, dict):
            setup = {}

        def repl(match) -> str:
            name = match.group(1)
            if name == "now":
                return str(int(time.time()))
            if name == "mention":
                uid = member.get("user_id")
                if uid is None:
                    return match.group(0)
                fmt_fn = setup.get("_format_mention")
                if callable(fmt_fn):
                    return fmt_fn(str(uid))
                return "<@%s>" % uid
            if name in member:
                v = member[name]
                if v is not None:
                    return str(v)
            if name in setup:
                v = setup[name]
                if v is not None:
                    return str(v)
            return match.group(0)

        return _PLACEHOLDER_RE.sub(repl, template)
    except (KeyError, TypeError, ValueError) as e:
        logger.error("resolve_template failed", exc_info=e)
        return template if isinstance(template, str) else ""


def resolve_channel_id(field_ref: str, setup: dict) -> int | None:
    """
    Resolve #snowflake literal or setup key to int channel id. None if invalid or missing.
    """
    try:
        if not isinstance(field_ref, str) or not field_ref:
            return None
        if not isinstance(setup, dict):
            setup = {}
        if field_ref.isdigit():
            return int(field_ref)
        if field_ref.startswith("#"):
            return int(field_ref[1:])
        raw = setup.get(field_ref)
        if raw is None:
            return None
        return int(raw)
    except (KeyError, TypeError, ValueError) as e:
        logger.error("resolve_channel_id failed for %r", field_ref, exc_info=e)
        return None


def resolve_role_id(field_ref: str, setup: dict) -> int | None:
    """Same resolution rules as resolve_channel_id (setup key, digits, or #snowflake)."""
    return resolve_channel_id(field_ref, setup)


def _resolve_body_fields(action: dict, member: dict, setup: dict) -> None:
    """
    Mutates action copy: sets _resolved_body for send_dm / post_to_channel from
    template_field (setup indirection) or inline template.
    """
    atype = action.get("type")
    if atype not in _BODY_ACTION_TYPES:
        return
    if "template_field" in action:
        key = action["template_field"]
        raw = setup.get(key, "") if isinstance(setup, dict) else ""
        if raw is None:
            raw = ""
        if not isinstance(raw, str):
            raw = str(raw)
        action["_resolved_body"] = resolve_template(raw, member, setup)
    elif "template" in action:
        tpl = action["template"]
        if not isinstance(tpl, str):
            tpl = str(tpl)
        action["_resolved_body"] = resolve_template(tpl, member, setup)


def _resolve_channel_field(action: dict, setup: dict) -> None:
    """Mutates action copy: _resolved_channel_id from channel_id_field if present."""
    if "channel_id_field" not in action:
        return
    ref = action["channel_id_field"]
    if isinstance(ref, str):
        action["_resolved_channel_id"] = resolve_channel_id(ref, setup)
    else:
        action["_resolved_channel_id"] = None


def _resolve_role_field(action: dict, setup: dict) -> None:
    if action.get("type") not in _ROLE_ACTION_TYPES:
        return
    ref = action.get("role_id_field")
    if isinstance(ref, str):
        action["_resolved_role_id"] = resolve_role_id(ref, setup)
    else:
        action["_resolved_role_id"] = None


def _resolve_kick_reason(action: dict, member: dict, setup: dict) -> None:
    if action.get("type") != "kick":
        return
    raw = action.get("reason")
    if not isinstance(raw, str) or not (raw or "").strip():
        action["_resolved_kick_reason"] = ""
        return
    action["_resolved_kick_reason"] = resolve_template(raw, member, setup)


def resolve_actions(actions: list[dict], member: dict, setup: dict) -> list[dict]:
    """
    Deep-copy each action and fill executor-facing fields: _resolved_body,
    _resolved_channel_id, _resolved_role_id, _resolved_kick_reason.
    """
    try:
        if not isinstance(actions, list):
            return []
        if not isinstance(member, dict):
            member = {}
        if not isinstance(setup, dict):
            setup = {}
        out = []
        for act in actions:
            if not isinstance(act, dict):
                continue
            cloned = copy.deepcopy(act)
            _resolve_body_fields(cloned, member, setup)
            _resolve_channel_field(cloned, setup)
            _resolve_role_field(cloned, setup)
            _resolve_kick_reason(cloned, member, setup)
            out.append(cloned)
        return out
    except (KeyError, TypeError, ValueError) as e:
        logger.error("resolve_actions failed", exc_info=e)
        return []


def _execute_flat_rule(rule: dict, member: dict, setup: dict, result: list[dict]) -> None:
    """Old-style rule: single conditions+actions block."""
    conds = rule.get("conditions", [])
    if not evaluate_conditions(conds, member):
        return
    acts = rule.get("actions", [])
    if not isinstance(acts, list):
        return
    resolved = resolve_actions(acts, member, setup)
    rid = rule.get("rule_id", "")
    for a in resolved:
        a["rule_id"] = rid
    result.extend(resolved)


def _execute_branched_rule(rule: dict, member: dict, setup: dict, result: list[dict]) -> None:
    """Branched rule: first branch whose conditions all pass wins, rest are skipped."""
    branches = rule.get("branches", [])
    if not isinstance(branches, list):
        return
    rid = rule.get("rule_id", "")
    for branch in branches:
        if not isinstance(branch, dict):
            continue
        conds = branch.get("conditions", [])
        if not evaluate_conditions(conds, member):
            continue
        acts = branch.get("actions", [])
        if not isinstance(acts, list):
            continue
        resolved = resolve_actions(acts, member, setup)
        for a in resolved:
            a["rule_id"] = rid
        result.extend(resolved)
        return


def process_event(
    event_type: str,
    event_data: dict,
    rules: list[dict],
    member: dict,
    setup: dict,
) -> list[dict]:
    """
    Run all rules: for each, if trigger matches, evaluate conditions/branches and
    append resolved actions. Supports both flat rules (conditions+actions) and
    branched rules (branches array, first matching branch wins).
    Returns a flat list of action dicts ready for the executor.
    """
    try:
        if not isinstance(event_data, dict):
            event_data = {}
        if not isinstance(rules, list):
            return []
        if not isinstance(member, dict):
            member = {}
        if not isinstance(setup, dict):
            setup = {}
        result = []
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            if not match_trigger(event_type, event_data, rule, setup):
                continue
            if "branches" in rule:
                _execute_branched_rule(rule, member, setup, result)
            else:
                _execute_flat_rule(rule, member, setup, result)
        return result
    except (KeyError, TypeError, ValueError) as e:
        logger.error("process_event failed", exc_info=e)
        return []


