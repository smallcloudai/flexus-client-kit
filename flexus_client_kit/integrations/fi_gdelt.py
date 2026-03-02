import json
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("gdelt")

PROVIDER_NAME = "gdelt"
METHOD_IDS = [
    "gdelt.doc.search.v1",
    "gdelt.events.search.v1",
]

_DOC_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
_EVENTS_URL = "https://api.gdeltproject.org/api/v2/events/search"


def _resolve_dates(
    time_window: str,
    start_date: str,
    end_date: str,
) -> tuple[Optional[str], Optional[str]]:
    if start_date:
        sd = start_date.replace("-", "") + "000000"
        ed = (end_date.replace("-", "") + "235959") if end_date else None
        return sd, ed
    if time_window:
        m = re.match(r"last_(\d+)d", time_window)
        if m:
            days = int(m.group(1))
            now = datetime.now(timezone.utc)
            start = now - timedelta(days=days)
            return start.strftime("%Y%m%d%H%M%S"), now.strftime("%Y%m%d%H%M%S")
    return None, None


class IntegrationGdelt:
    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Dict[str, Any],
    ) -> str:
        args = model_produced_args or {}
        op = str(args.get("op", "help")).strip()
        if op == "help":
            return (
                f"provider={PROVIDER_NAME}\n"
                "op=help | status | list_methods | call\n"
                f"methods: {', '.join(METHOD_IDS)}"
            )
        if op == "status":
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "status": "available", "method_count": len(METHOD_IDS)}, indent=2, ensure_ascii=False)
        if op == "list_methods":
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_ids": METHOD_IDS}, indent=2, ensure_ascii=False)
        if op != "call":
            return "Error: unknown op. Use help/status/list_methods/call."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_IDS:
            return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)
        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        if method_id == "gdelt.doc.search.v1":
            return await self._doc_search(args)
        if method_id == "gdelt.events.search.v1":
            return await self._events_search(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _doc_search(self, args: Dict[str, Any]) -> str:
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "query is required"}, indent=2, ensure_ascii=False)
        limit = min(int(args.get("limit", 25)), 250)
        time_window = str(args.get("time_window", ""))
        start_date = str(args.get("start_date", ""))
        end_date = str(args.get("end_date", ""))
        include_raw = bool(args.get("include_raw", False))

        params: Dict[str, Any] = {
            "query": query + " sourcelang:english",
            "mode": "artlist",
            "format": "json",
            "maxrecords": limit,
            "sort": "DateDesc",
        }
        start_dt, end_dt = _resolve_dates(time_window, start_date, end_date)
        if start_dt:
            params["startdatetime"] = start_dt
        if end_dt:
            params["enddatetime"] = end_dt

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(_DOC_URL, params=params, headers={"Accept": "application/json"})
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            articles = data.get("articles", [])
            result: Dict[str, Any] = {"ok": True, "results": articles, "total": len(articles)}
            if include_raw:
                result["raw"] = data
            summary = f"Found {len(articles)} article(s) from {PROVIDER_NAME}."
            return summary + "\n\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _events_search(self, args: Dict[str, Any]) -> str:
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "query is required"}, indent=2, ensure_ascii=False)
        limit = min(int(args.get("limit", 25)), 250)
        include_raw = bool(args.get("include_raw", False))

        params: Dict[str, Any] = {
            "query": query,
            "format": "json",
            "maxrecords": limit,
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(_EVENTS_URL, params=params, headers={"Accept": "application/json"})
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            events = data.get("events", data.get("results", []))
            result: Dict[str, Any] = {"ok": True, "results": events, "total": len(events)}
            if include_raw:
                result["raw"] = data
            summary = f"Found {len(events)} event(s) from {PROVIDER_NAME}."
            return summary + "\n\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
