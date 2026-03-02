import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("youtube")

PROVIDER_NAME = "youtube"
METHOD_IDS = [
    "youtube.comment_threads.list.v1",
    "youtube.search.list.v1",
    "youtube.videos.list.v1",
]

_BASE_URL = "https://www.googleapis.com/youtube/v3"


class IntegrationYoutube:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _get_api_key(self) -> str:
        if self.rcx is not None:
            return (self.rcx.external_auth.get("youtube") or {}).get("api_key", "")
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
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set YOUTUBE_API_KEY env var."}, indent=2, ensure_ascii=False)

        limit = int(args.get("limit", 10))
        geo = args.get("geo") or {}

        if method_id == "youtube.search.list.v1":
            return await self._search_list(api_key, args, limit, geo)
        if method_id == "youtube.videos.list.v1":
            return await self._videos_list(api_key, args)
        if method_id == "youtube.comment_threads.list.v1":
            return await self._comment_threads_list(api_key, args, limit)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _get(self, endpoint: str, params: Dict) -> str:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(_BASE_URL + endpoint, params=params, headers={"Accept": "application/json"})
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            return r.text
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    def _format(self, data: Dict, results: Any, method_id: str, include_raw: bool) -> str:
        count = len(results) if isinstance(results, list) else 1
        summary = f"Found {count} result(s) from {PROVIDER_NAME} ({method_id})."
        payload: Dict[str, Any] = {"ok": True, "results": results, "total": data.get("pageInfo", {}).get("totalResults", count)}
        if include_raw:
            payload["raw"] = data
        return summary + "\n\n```json\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\n```"

    async def _search_list(self, key: str, args: Dict, limit: int, geo: Dict) -> str:
        query = str(args.get("query", ""))
        params: Dict[str, Any] = {
            "key": key,
            "q": query,
            "type": "video",
            "part": "snippet",
            "maxResults": min(limit, 50),
            "relevanceLanguage": "en",
        }
        country = geo.get("country", "") if geo else ""
        if country:
            params["regionCode"] = country
        raw = await self._get("/search", params)
        try:
            data = json.loads(raw)
        except (ValueError, KeyError):
            return raw
        if isinstance(data, dict) and "error_code" in data:
            return raw
        results = data.get("items", [])
        return self._format(data, results, "youtube.search.list.v1", bool(args.get("include_raw")))

    async def _videos_list(self, key: str, args: Dict) -> str:
        video_ids = args.get("video_ids", "") or args.get("video_id", "")
        if isinstance(video_ids, list):
            video_ids = ",".join(video_ids)
        params: Dict[str, Any] = {"key": key, "id": video_ids, "part": "snippet,statistics"}
        raw = await self._get("/videos", params)
        try:
            data = json.loads(raw)
        except (ValueError, KeyError):
            return raw
        if isinstance(data, dict) and "error_code" in data:
            return raw
        results = data.get("items", [])
        return self._format(data, results, "youtube.videos.list.v1", bool(args.get("include_raw")))

    async def _comment_threads_list(self, key: str, args: Dict, limit: int) -> str:
        video_id = str(args.get("video_id", ""))
        params: Dict[str, Any] = {
            "key": key,
            "videoId": video_id,
            "part": "snippet",
            "maxResults": min(limit, 100),
        }
        raw = await self._get("/commentThreads", params)
        try:
            data = json.loads(raw)
        except (ValueError, KeyError):
            return raw
        if isinstance(data, dict) and "error_code" in data:
            return raw
        results = data.get("items", [])
        return self._format(data, results, "youtube.comment_threads.list.v1", bool(args.get("include_raw")))
