import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("reddit")

PROVIDER_NAME = "reddit"
METHOD_IDS = [
    "reddit.comments.list.v1",
    "reddit.search.posts.v1",
    "reddit.subreddit.hot.v1",
    "reddit.subreddit.new.v1",
]

_TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
_API_BASE = "https://oauth.reddit.com"
_USER_AGENT = "Flexus Market Signal Bot/1.0"

_TIME_WINDOW_MAP = {
    "last_7d": "week",
    "last_30d": "month",
    "last_90d": "year",
}


class IntegrationReddit:
    # XXX: requires multiple credentials (REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET).
    # manual auth (single api_key field) does not cover this provider.
    # currently reads from env vars as a fallback.
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

    async def _get_access_token(self) -> str:
        client_id = os.environ.get("REDDIT_CLIENT_ID", "")
        client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
        if not client_id or not client_secret:
            return ""
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.post(
                _TOKEN_URL,
                data={"grant_type": "client_credentials"},
                auth=(client_id, client_secret),
                headers={"User-Agent": _USER_AGENT},
            )
        if r.status_code >= 400:
            logger.info("reddit token request failed: HTTP %s: %s", r.status_code, r.text[:200])
            return ""
        return r.json().get("access_token", "")

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        client_id = os.environ.get("REDDIT_CLIENT_ID", "")
        client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
        if not client_id or not client_secret:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET env vars."}, indent=2, ensure_ascii=False)

        try:
            token = await self._get_access_token()
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "AUTH_FAILED", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

        if not token:
            return json.dumps({"ok": False, "error_code": "AUTH_FAILED", "message": "Could not obtain Reddit access token. Check REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET."}, indent=2, ensure_ascii=False)

        headers = {"Authorization": f"Bearer {token}", "User-Agent": _USER_AGENT}
        subreddit = str(args.get("subreddit", "all"))
        limit = int(args.get("limit", 25))
        query = str(args.get("query", ""))
        time_window = str(args.get("time_window", ""))
        cursor = args.get("cursor", "")

        if method_id == "reddit.subreddit.new.v1":
            url = f"{_API_BASE}/r/{subreddit}/new.json"
            params: Dict[str, Any] = {"limit": limit}
            if cursor:
                params["after"] = cursor
            return await self._get(url, params, headers, method_id, args)
        if method_id == "reddit.subreddit.hot.v1":
            url = f"{_API_BASE}/r/{subreddit}/hot.json"
            params = {"limit": limit}
            return await self._get(url, params, headers, method_id, args)
        if method_id == "reddit.search.posts.v1":
            url = f"{_API_BASE}/search.json"
            time_filter = _TIME_WINDOW_MAP.get(time_window, "all")
            params = {"q": query, "sort": "relevance", "limit": limit, "t": time_filter}
            return await self._get(url, params, headers, method_id, args)
        if method_id == "reddit.comments.list.v1":
            url = f"{_API_BASE}/r/{subreddit}/comments.json"
            params = {"limit": limit}
            return await self._get(url, params, headers, method_id, args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _get(self, url: str, params: Dict, headers: Dict, method_id: str, args: Dict) -> str:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(url, params=params, headers=headers)
            if r.status_code in (403, 429):
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            children = data.get("data", {}).get("children", [])
            results = [c.get("data", c) for c in children]
            summary = f"Found {len(results)} result(s) from {PROVIDER_NAME} ({method_id})."
            payload: Dict[str, Any] = {"ok": True, "results": results, "total": len(results)}
            after = data.get("data", {}).get("after")
            if after:
                payload["next_cursor"] = after
            if args.get("include_raw"):
                payload["raw"] = data
            return summary + "\n\n```json\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
