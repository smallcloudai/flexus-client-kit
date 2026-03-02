import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("event_registry")

PROVIDER_NAME = "event_registry"
METHOD_IDS = [
    "event_registry.article.get_articles.v1",
    "event_registry.event.get_events.v1",
]

_BASE_URL = "https://eventregistry.org/api/v1"


def _resolve_dates(time_window: str, start_date: str, end_date: str) -> tuple[Optional[str], Optional[str]]:
    if start_date:
        return start_date, end_date or None
    if time_window:
        import re
        m = re.match(r"last_(\d+)d", time_window)
        if m:
            days = int(m.group(1))
            now = datetime.now(timezone.utc)
            start = now - timedelta(days=days)
            return start.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")
    return None, None


class IntegrationEventRegistry:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _get_api_key(self) -> str:
        if self.rcx is not None:
            return (self.rcx.external_auth.get("event_registry") or {}).get("api_key", "")
        return self._get_api_key()

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
            api_key = self._get_api_key()
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "status": "available" if api_key else "auth_missing", "method_count": len(METHOD_IDS)}, indent=2, ensure_ascii=False)
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
        if method_id == "event_registry.article.get_articles.v1":
            return await self._get_articles(args)
        if method_id == "event_registry.event.get_events.v1":
            return await self._get_events(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _get_articles(self, args: Dict[str, Any]) -> str:
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set EVENT_REGISTRY_KEY env var."}, indent=2, ensure_ascii=False)
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "query is required"}, indent=2, ensure_ascii=False)
        limit = min(int(args.get("limit", 20)), 100)
        time_window = str(args.get("time_window", ""))
        start_date = str(args.get("start_date", ""))
        end_date = str(args.get("end_date", ""))
        include_raw = bool(args.get("include_raw", False))

        sd, ed = _resolve_dates(time_window, start_date, end_date)
        body: Dict[str, Any] = {
            "action": "getArticles",
            "keyword": query,
            "articlesCount": limit,
            "articlesSortBy": "date",
            "resultType": "articles",
            "apiKey": api_key,
            "lang": "eng",
        }
        if sd:
            body["dateStart"] = sd
        if ed:
            body["dateEnd"] = ed

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.post(_BASE_URL + "/article/getArticles", json=body, headers={"Accept": "application/json"})
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            articles = data.get("articles", {}).get("results", [])
            total = data.get("articles", {}).get("totalResults", len(articles))
            result: Dict[str, Any] = {"ok": True, "results": articles, "total": total}
            if include_raw:
                result["raw"] = data
            summary = f"Found {len(articles)} article(s) from {PROVIDER_NAME}."
            return summary + "\n\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _get_events(self, args: Dict[str, Any]) -> str:
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set EVENT_REGISTRY_KEY env var."}, indent=2, ensure_ascii=False)
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "query is required"}, indent=2, ensure_ascii=False)
        limit = min(int(args.get("limit", 20)), 50)
        include_raw = bool(args.get("include_raw", False))

        body: Dict[str, Any] = {
            "action": "getEvents",
            "keyword": query,
            "eventsCount": limit,
            "eventsSortBy": "date",
            "resultType": "events",
            "apiKey": api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.post(_BASE_URL + "/event/getEvents", json=body, headers={"Accept": "application/json"})
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            events = data.get("events", {}).get("results", [])
            total = data.get("events", {}).get("totalResults", len(events))
            result: Dict[str, Any] = {"ok": True, "results": events, "total": total}
            if include_raw:
                result["raw"] = data
            summary = f"Found {len(events)} event(s) from {PROVIDER_NAME}."
            return summary + "\n\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
