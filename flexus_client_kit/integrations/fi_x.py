import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("x")

PROVIDER_NAME = "x"
METHOD_IDS = [
    "x.tweets.counts_recent.v1",
    "x.tweets.search_recent.v1",
]

_BASE_URL = "https://api.twitter.com/2"


class IntegrationX:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _get_api_key(self) -> str:
        if self.rcx is not None:
            return (self.rcx.external_auth.get("x") or {}).get("api_key", "")
        return os.environ.get("X_BEARER_TOKEN", "")

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
        bearer_token = self._get_api_key()
        if not bearer_token:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set X_BEARER_TOKEN env var."}, indent=2, ensure_ascii=False)

        headers = {"Authorization": f"Bearer {bearer_token}"}
        query = str(args.get("query", ""))
        limit = int(args.get("limit", 10))

        if method_id == "x.tweets.counts_recent.v1":
            return await self._counts_recent(headers, query, args)
        if method_id == "x.tweets.search_recent.v1":
            return await self._search_recent(headers, query, limit, args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _counts_recent(self, headers: Dict, query: str, args: Dict) -> str:
        params = {"query": query, "granularity": "day"}
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(_BASE_URL + "/tweets/counts/recent", params=params, headers=headers)
            if r.status_code in (403, 429):
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            results = data.get("data", [])
            meta = data.get("meta", {})
            summary = f"Found {len(results)} day(s) of tweet counts from {PROVIDER_NAME}. Total tweets: {meta.get('total_tweet_count', 'N/A')}."
            payload: Dict[str, Any] = {"ok": True, "results": results, "meta": meta, "total": len(results)}
            if args.get("include_raw"):
                payload["raw"] = data
            return summary + "\n\n```json\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _search_recent(self, headers: Dict, query: str, limit: int, args: Dict) -> str:
        max_results = min(limit, 100)
        max_results = max(max_results, 10)
        params = {
            "query": query,
            "max_results": max_results,
            "tweet.fields": "created_at,author_id,public_metrics,lang",
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(_BASE_URL + "/tweets/search/recent", params=params, headers=headers)
            if r.status_code in (403, 429):
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            results = data.get("data", [])
            meta = data.get("meta", {})
            summary = f"Found {len(results)} tweet(s) from {PROVIDER_NAME}."
            payload: Dict[str, Any] = {"ok": True, "results": results, "meta": meta, "total": meta.get("result_count", len(results))}
            if args.get("include_raw"):
                payload["raw"] = data
            return summary + "\n\n```json\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
