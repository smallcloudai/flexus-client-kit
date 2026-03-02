import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("mediastack")

PROVIDER_NAME = "mediastack"
METHOD_IDS = [
    "mediastack.news.search.v1",
]

_BASE_URL = "https://api.mediastack.com/v1"


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


class IntegrationMediastack:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _get_api_key(self) -> str:
        if self.rcx is not None:
            return (self.rcx.external_auth.get("mediastack") or {}).get("api_key", "")
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
        if method_id == "mediastack.news.search.v1":
            return await self._news_search(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _news_search(self, args: Dict[str, Any]) -> str:
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set MEDIASTACK_KEY env var."}, indent=2, ensure_ascii=False)
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "query is required"}, indent=2, ensure_ascii=False)
        limit = min(int(args.get("limit", 25)), 100)
        geo = args.get("geo") or {}
        time_window = str(args.get("time_window", ""))
        start_date = str(args.get("start_date", ""))
        end_date = str(args.get("end_date", ""))
        cursor = args.get("cursor", None)
        include_raw = bool(args.get("include_raw", False))

        params: Dict[str, Any] = {
            "access_key": api_key,
            "keywords": query,
            "languages": "en",
            "limit": limit,
            "sort": "published_desc",
        }
        country = geo.get("country", "") if isinstance(geo, dict) else ""
        if country:
            params["countries"] = country.lower()
        sd, ed = _resolve_dates(time_window, start_date, end_date)
        if sd and ed:
            params["date"] = f"{sd},{ed}"
        elif sd:
            params["date"] = sd
        if cursor is not None:
            params["offset"] = int(cursor)

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(_BASE_URL + "/news", params=params, headers={"Accept": "application/json"})
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            articles = data.get("data", [])
            total = data.get("pagination", {}).get("total", len(articles))
            offset = data.get("pagination", {}).get("offset", 0)
            result: Dict[str, Any] = {"ok": True, "results": articles, "total": total}
            next_offset = offset + limit
            if next_offset < total:
                result["next_cursor"] = next_offset
            if include_raw:
                result["raw"] = data
            summary = f"Found {len(articles)} article(s) from {PROVIDER_NAME} (total={total})."
            return summary + "\n\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
