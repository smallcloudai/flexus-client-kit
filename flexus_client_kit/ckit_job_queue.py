from __future__ import annotations

import logging
import time
from typing import Any, Awaitable, Callable, Dict

logger = logging.getLogger(__name__)


def _log_ctx(persona_id: str, guild_id: Any, msg: str, *args: Any) -> None:
    gid = str(guild_id) if guild_id is not None else "-"
    logger.info("[%s guild=%s] " + msg, persona_id, gid, *args)

COL_JOBS = "dc_community_jobs"

JobHandler = Callable[[Dict[str, Any]], Awaitable[None]]


async def enqueue_job(
    db: Any,
    kind: str,
    run_at_ts: float,
    payload: Dict[str, Any],
) -> None:
    coll = db[COL_JOBS]
    await coll.insert_one(
        {
            "kind": kind,
            "run_at": float(run_at_ts),
            "payload": payload,
            "done": False,
            "created_ts": time.time(),
        },
    )


async def drain_due_jobs(
    db: Any,
    persona_id: str,
    handlers: Dict[str, JobHandler],
    limit: int = 50,
) -> int:
    coll = db[COL_JOBS]
    now = time.time()
    count = 0
    cursor = coll.find({"done": False, "run_at": {"$lte": now}}).sort("run_at", 1).limit(limit)
    async for doc in cursor:
        kind = doc.get("kind") or ""
        handler = handlers.get(kind)
        if not handler:
            await coll.update_one({"_id": doc["_id"]}, {"$set": {"done": True, "error": "no_handler"}})
            continue
        payload = doc.get("payload") or {}
        try:
            await handler(payload)
        except (TypeError, ValueError, KeyError) as e:
            _log_ctx(persona_id, payload.get("guild_id"), "job %s data error: %s %s", kind, type(e).__name__, e)
        await coll.update_one({"_id": doc["_id"]}, {"$set": {"done": True, "finished_ts": time.time()}})
        count += 1
    return count
