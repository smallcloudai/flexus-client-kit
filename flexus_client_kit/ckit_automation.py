from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Optional

import jsonschema
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)

# Loaded by set_automation_schema_dict() from ckit_automation_v1_schema_build (authoritative) or
# set_automation_schema(path) for tests / offline fixtures.
_AUTOMATION_SCHEMA: dict | None = None


def set_automation_schema_dict(schema: dict) -> None:
    global _AUTOMATION_SCHEMA
    if not isinstance(schema, dict):
        raise TypeError("set_automation_schema_dict expects dict")
    _AUTOMATION_SCHEMA = schema


def set_automation_schema(schema_path: str) -> None:
    """
    Load automation JSON Schema from disk. Fail-fast: raises if file is missing or invalid JSON.
    """
    global _AUTOMATION_SCHEMA
    _AUTOMATION_SCHEMA = json.loads(Path(schema_path).read_text(encoding="utf-8"))


def extract_automation_published(persona_setup: dict) -> dict:
    """
    Extract published automation config from persona_setup JSONB.
    Returns empty dict if no published automations exist.
    Published config lives inside persona_setup so changes trigger bot restart
    via the existing subscription comparison in ckit_bot_exec.py.

    Prefer resolve_automation_rules() for new code; this function is kept for
    legacy call-sites that have not yet been migrated.
    """
    try:
        result = persona_setup.get("automation_published", {})
        return result if isinstance(result, dict) else {}
    except (AttributeError, TypeError) as e:
        logger.error("extract_automation_published failed", exc_info=e)
        return {}


def resolve_automation_rules(persona_setup: dict) -> dict:
    """
    Resolve the published automation rules document from persona_setup JSONB.

    Migration-safe: prefers the new setup field automation_rules (stored as a
    JSON string by automation_publish) and falls back to the legacy
    automation_published dict for personas that were published before the storage
    move.  Returns an empty dict when neither field is present or valid.
    """
    try:
        if not isinstance(persona_setup, dict):
            return {}
        raw = persona_setup.get("automation_rules")
        if isinstance(raw, str) and raw.strip():
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    return parsed
            except (json.JSONDecodeError, ValueError):
                logger.warning("resolve_automation_rules: automation_rules field is not valid JSON, falling back to automation_published")
        legacy = persona_setup.get("automation_published", {})
        return legacy if isinstance(legacy, dict) else {}
    except (AttributeError, TypeError) as e:
        logger.error("resolve_automation_rules failed", exc_info=e)
        return {}


def extract_automation_draft(persona_automation_draft: Any) -> dict:
    """
    Extract draft automation config from the separate persona_automation_draft column.
    Draft lives in its own Prisma column to avoid triggering bot restarts on save.
    Returns empty dict if column is NULL or invalid.
    """
    try:
        if persona_automation_draft is None:
            return {}
        if isinstance(persona_automation_draft, dict):
            return persona_automation_draft
        return {}
    except (AttributeError, TypeError) as e:
        logger.error("extract_automation_draft failed", exc_info=e)
        return {}


def validate_automation_json(data: dict) -> list[str]:
    """
    Validate an automation config dict against automation_v1.schema.json.
    Returns list of error strings (empty list = valid).
    Used by GraphQL mutations automation_draft_save and automation_publish.
    """
    if _AUTOMATION_SCHEMA is None:
        return ["automation schema not loaded -- call set_automation_schema_dict at backend startup"]
    errors = []
    try:
        validator = jsonschema.Draft202012Validator(_AUTOMATION_SCHEMA)
        for error in validator.iter_errors(data):
            path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "$"
            errors.append("%s: %s" % (path, error.message))
    except jsonschema.SchemaError as e:
        errors.append("schema error: %s" % e.message)
    return errors


class DisabledRulesCache:
    def __init__(self, mongo_db: Any, interval: float = 30.0):
        self._mongo_db = mongo_db
        self._interval = interval
        self._disabled: set = set()
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        await self._refresh()
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def get(self) -> set:
        return self._disabled

    async def _refresh(self) -> None:
        try:
            doc = await self._mongo_db["bot_runtime_config"].find_one({"_id": "disabled_rule_ids"})
            if doc and isinstance(doc.get("ids"), list):
                self._disabled = {str(x) for x in doc["ids"] if x}
            else:
                self._disabled = set()
        except PyMongoError as e:
            logger.warning("DisabledRulesCache refresh failed (mongo), keeping last known state: %s %s", type(e).__name__, e)
        except (TypeError, ValueError) as e:
            logger.warning("DisabledRulesCache refresh failed (bad doc), keeping last known state: %s %s", type(e).__name__, e)

    async def _loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(self._interval)
                await self._refresh()
            except asyncio.CancelledError:
                break


def filter_active_rules(all_rules: list, disabled: set) -> list:
    if not disabled:
        return all_rules
    return [r for r in all_rules if r.get("rule_id", "") not in disabled]
