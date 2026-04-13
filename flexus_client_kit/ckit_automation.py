from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import jsonschema

from flexus_client_kit.ckit_automation_v1_schema_build import build_automation_v1_schema_document

logger = logging.getLogger(__name__)

# Eagerly built from the Discord automation catalog (integration triggers/actions) at import time.
# Tests and offline fixtures can override via set_automation_schema_dict() / set_automation_schema().
_AUTOMATION_SCHEMA: dict = build_automation_v1_schema_document()


def set_automation_schema_dict(schema: dict) -> None:
    global _AUTOMATION_SCHEMA
    if not isinstance(schema, dict):
        raise TypeError("set_automation_schema_dict expects dict")
    _AUTOMATION_SCHEMA = schema


def set_automation_schema(schema_path: str) -> None:
    """Load automation JSON Schema from disk. Raises if file is missing or invalid JSON."""
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
    Validate an automation config dict against the v1 schema.
    Returns list of error strings (empty = valid).
    """
    errors = []
    try:
        validator = jsonschema.Draft202012Validator(_AUTOMATION_SCHEMA)
        for error in validator.iter_errors(data):
            path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "$"
            errors.append("%s: %s" % (path, error.message))
    except jsonschema.SchemaError as e:
        errors.append("schema error: %s" % e.message)
    return errors


