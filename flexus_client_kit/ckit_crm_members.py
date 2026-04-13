"""
CRM member persistence for the Discord automation engine.

Owns the dc_members MongoDB collection: indexes, CRUD, handler-facing entry points,
and one-time migration from dc_onboarding_state. Matches async pymongo usage elsewhere
in flexus_client_kit (no ORM).
"""

from __future__ import annotations

import logging
import time
from typing import Any

from pymongo import ReturnDocument
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)

# Primary collection for per-guild Discord member CRM documents (see crm_member.md).
COL_MEMBERS = "dc_members"

# Legacy onboarding collection name before rename to dc_onboarding_state_legacy.
LEGACY_ONBOARDING = "dc_onboarding_state"


def _member_filter(guild_id: int, user_id: int) -> dict[str, int]:
    """Equality filter for the compound natural key used across all member operations."""
    return {"guild_id": int(guild_id), "user_id": int(user_id)}


async def ensure_member_indexes(db: Any) -> None:
    """
    Create dc_members indexes once at bot startup. Idempotent: repeated calls are safe.

    Indexes match the CRM contract: unique member key, sparse scans on status and
    last_message_ts, and workspace routing for future multi-tenant gateway (U4).
    """
    try:
        coll = db[COL_MEMBERS]
        await coll.create_index(
            [("guild_id", 1), ("user_id", 1)],
            unique=True,
        )
        await coll.create_index(
            [("lifecycle_status", 1)],
            sparse=True,
        )
        await coll.create_index(
            [("last_message_ts", 1)],
            sparse=True,
        )
        await coll.create_index(
            [("workspace_id", 1)],
            unique=False,
        )
    except PyMongoError as e:
        logger.error("ensure_member_indexes: MongoDB index creation failed", exc_info=e)
        raise


async def upsert_member_on_join(
    db: Any,
    guild_id: int,
    user_id: int,
    workspace_id: str,
    discord_username: str,
) -> dict:
    """
    Insert or update a member row on Discord on_member_join.

    $set refreshes join time, username, lifecycle, and workspace so re-join updates
    mutable CRM fields. $setOnInsert applies defaults only on first insert so tags,
    intro timestamps, and other accumulated fields survive leave/re-join cycles.
    """
    try:
        coll = db[COL_MEMBERS]
        flt = _member_filter(guild_id, user_id)
        now = time.time()
        doc = await coll.find_one_and_update(
            flt,
            {
                "$set": {
                    "member_joined_at": now,
                    "discord_username": discord_username,
                    "lifecycle_status": "accepted",
                    "workspace_id": workspace_id,
                    "platform": "discord",
                },
                "$setOnInsert": {
                    "dm_opt_out": False,
                    "tags": [],
                    "networking_opt_in": False,
                },
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        if doc is None:
            raise RuntimeError("upsert_member_on_join: find_one_and_update returned None after upsert")
        return doc
    except PyMongoError as e:
        logger.error(
            "upsert_member_on_join: guild_id=%s user_id=%s failed",
            guild_id,
            user_id,
            exc_info=e,
        )
        raise


async def get_member(db: Any, guild_id: int, user_id: int) -> dict | None:
    """Load a single member document by guild and user id, or None if absent."""
    try:
        coll = db[COL_MEMBERS]
        return await coll.find_one(_member_filter(guild_id, user_id))
    except PyMongoError as e:
        logger.error("get_member: guild_id=%s user_id=%s failed", guild_id, user_id, exc_info=e)
        raise


async def update_member_field(
    db: Any,
    guild_id: int,
    user_id: int,
    field: str,
    value: Any,
) -> dict | None:
    """Set one CRM field and return the post-update document (None if member row missing)."""
    try:
        if not isinstance(field, str) or not field:
            raise TypeError("update_member_field: field must be a non-empty str")
        coll = db[COL_MEMBERS]
        return await coll.find_one_and_update(
            _member_filter(guild_id, user_id),
            {"$set": {field: value}},
            return_document=ReturnDocument.AFTER,
        )
    except TypeError as e:
        logger.error(
            "update_member_field: guild_id=%s user_id=%s field=%r invalid",
            guild_id,
            user_id,
            field,
            exc_info=e,
        )
        raise
    except PyMongoError as e:
        logger.error(
            "update_member_field: guild_id=%s user_id=%s field=%s failed",
            guild_id,
            user_id,
            field,
            exc_info=e,
        )
        raise


async def update_member_fields(
    db: Any,
    guild_id: int,
    user_id: int,
    fields: dict,
) -> dict | None:
    """Atomically $set multiple CRM fields; returns updated doc or None if no row exists."""
    try:
        if not isinstance(fields, dict):
            raise TypeError("update_member_fields: fields must be a dict")
        coll = db[COL_MEMBERS]
        if not fields:
            # No $set payload: return current row without claiming a multi-field update failed.
            return await coll.find_one(_member_filter(guild_id, user_id))
        return await coll.find_one_and_update(
            _member_filter(guild_id, user_id),
            {"$set": fields},
            return_document=ReturnDocument.AFTER,
        )
    except TypeError as e:
        logger.error(
            "update_member_fields: guild_id=%s user_id=%s invalid fields dict",
            guild_id,
            user_id,
            exc_info=e,
        )
        raise
    except PyMongoError as e:
        logger.error(
            "update_member_fields: guild_id=%s user_id=%s failed",
            guild_id,
            user_id,
            exc_info=e,
        )
        raise


async def set_member_status(
    db: Any,
    guild_id: int,
    user_id: int,
    new_status: str,
) -> tuple[dict | None, str | None]:
    """
    Atomically set lifecycle_status and expose the previous value for status_transition rules.

    Uses ReturnDocument.BEFORE so old lifecycle_status is read from the same atomic
    update. The first tuple element is the effective new member view (BEFORE doc with
    lifecycle_status overwritten) so callers avoid a second round-trip.
    """
    try:
        if not isinstance(new_status, str):
            raise TypeError("set_member_status: new_status must be str")
        coll = db[COL_MEMBERS]
        old_doc = await coll.find_one_and_update(
            _member_filter(guild_id, user_id),
            {"$set": {"lifecycle_status": new_status}},
            return_document=ReturnDocument.BEFORE,
        )
        if old_doc is None:
            return (None, None)
        old_status = old_doc.get("lifecycle_status")
        old_status_str = old_status if isinstance(old_status, str) else None
        merged = dict(old_doc)
        merged["lifecycle_status"] = new_status
        return (merged, old_status_str)
    except TypeError as e:
        logger.error(
            "set_member_status: guild_id=%s user_id=%s new_status=%r invalid",
            guild_id,
            user_id,
            new_status,
            exc_info=e,
        )
        raise
    except PyMongoError as e:
        logger.error(
            "set_member_status: guild_id=%s user_id=%s new_status=%s failed",
            guild_id,
            user_id,
            new_status,
            exc_info=e,
        )
        raise


async def handle_member_join(
    db: Any,
    guild_id: int,
    user_id: int,
    workspace_id: str,
    username: str,
) -> dict:
    """Engine hook: persist join metadata before automation rules run on member_joined."""
    try:
        return await upsert_member_on_join(
            db,
            guild_id,
            user_id,
            workspace_id,
            username,
        )
    except PyMongoError as e:
        logger.error(
            "handle_member_join: guild_id=%s user_id=%s failed",
            guild_id,
            user_id,
            exc_info=e,
        )
        raise


async def handle_message(db: Any, guild_id: int, user_id: int) -> None:
    """
    Engine hook: bump last_message_ts for inactivity and message-triggered automation.

    Upserts a minimal dc_members row on first observed message so get_member() and
    rules that run after handle_message (e.g. message_in_channel) work even when
    on_member_join never fired in this deployment. Existing rows only get
    last_message_ts updated; we do not set member_joined_at or workspace_id here.
    """
    try:
        coll = db[COL_MEMBERS]
        now = time.time()
        await coll.update_one(
            _member_filter(guild_id, user_id),
            {
                "$set": {"last_message_ts": now},
                "$setOnInsert": {
                    "platform": "discord",
                    "dm_opt_out": False,
                    "tags": [],
                    "networking_opt_in": False,
                },
            },
            upsert=True,
        )
    except PyMongoError as e:
        logger.error(
            "handle_message: guild_id=%s user_id=%s failed",
            guild_id,
            user_id,
            exc_info=e,
        )
        raise


async def handle_member_remove(
    db: Any,
    guild_id: int,
    user_id: int,
) -> tuple[str | None, str | None]:
    """
    Engine hook: mark member churned and return (old_status, new_status) for cascades.

    new_status is always the literal "churned". If no CRM row exists, returns (None, None).
    """
    try:
        coll = db[COL_MEMBERS]
        old_doc = await coll.find_one_and_update(
            _member_filter(guild_id, user_id),
            {"$set": {"lifecycle_status": "churned"}},
            return_document=ReturnDocument.BEFORE,
        )
        if old_doc is None:
            return (None, None)
        old_raw = old_doc.get("lifecycle_status")
        old_status = old_raw if isinstance(old_raw, str) else None
        return (old_status, "churned")
    except PyMongoError as e:
        logger.error(
            "handle_member_remove: guild_id=%s user_id=%s failed",
            guild_id,
            user_id,
            exc_info=e,
        )
        raise


def _legacy_float(raw: Any) -> float | None:
    """Parse legacy onboarding numeric timestamps; None if missing or not coercible."""
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


async def migrate_legacy_collections(db: Any) -> None:
    """
    One-time import from dc_onboarding_state into dc_members, then rename the source.

    Idempotent: if dc_members already contains any document, skips the whole migration
    (including rename) so a second startup does not duplicate or break indexes.
    Does not read dc_member_activity (different DB / deferred to U4).
    """
    try:
        members = db[COL_MEMBERS]
        if await members.count_documents({}, limit=1) > 0:
            logger.info(
                "migrate_legacy_collections: skip (collection %s already has documents)",
                COL_MEMBERS,
            )
            return

        names = await db.list_collection_names()
        if LEGACY_ONBOARDING not in names:
            logger.info(
                "migrate_legacy_collections: skip (collection %s not found)",
                LEGACY_ONBOARDING,
            )
            return

        src = db[LEGACY_ONBOARDING]
        migrated = 0
        async for leg in src.find({}):
            gid = leg.get("guild_id")
            uid = leg.get("user_id")
            if gid is None or uid is None:
                logger.info("migrate_legacy_collections: skip row without guild_id/user_id")
                continue
            try:
                guild_id = int(gid)
                user_id = int(uid)
            except (TypeError, ValueError):
                logger.info("migrate_legacy_collections: skip row with non-int guild_id/user_id")
                continue

            joined_ts = _legacy_float(leg.get("joined_ts"))
            if joined_ts is None:
                logger.info(
                    "migrate_legacy_collections: skip guild_id=%s user_id=%s (no joined_ts)",
                    guild_id,
                    user_id,
                )
                continue

            followup_ts = _legacy_float(leg.get("followup_ts"))
            engaged = leg.get("engaged") is True
            followup_sent = leg.get("followup_sent") is True
            last_msg = _legacy_float(leg.get("last_message_ts"))

            intro_done_at = None
            if engaged:
                intro_done_at = followup_ts if followup_ts is not None else joined_ts + 1.0

            intro_reminder_sent_at = None
            if followup_sent:
                intro_reminder_sent_at = (
                    followup_ts if followup_ts is not None else joined_ts + 172800.0
                )

            new_doc: dict[str, Any] = {
                "guild_id": guild_id,
                "user_id": user_id,
                "workspace_id": "",
                "discord_username": "",
                "member_joined_at": joined_ts,
                "lifecycle_status": "accepted",
                "dm_opt_out": False,
                "tags": [],
                "networking_opt_in": False,
            }
            if intro_done_at is not None:
                new_doc["intro_done_at"] = intro_done_at
            if intro_reminder_sent_at is not None:
                new_doc["intro_reminder_sent_at"] = intro_reminder_sent_at
            if last_msg is not None:
                new_doc["last_message_ts"] = last_msg

            await members.insert_one(new_doc)
            migrated += 1

        logger.info(
            "migrate_legacy_collections: inserted %s documents into %s",
            migrated,
            COL_MEMBERS,
        )
        await src.rename("dc_onboarding_state_legacy")
        logger.info(
            "migrate_legacy_collections: renamed %s to dc_onboarding_state_legacy",
            LEGACY_ONBOARDING,
        )
    except PyMongoError as e:
        logger.error("migrate_legacy_collections: MongoDB operation failed", exc_info=e)
        raise
