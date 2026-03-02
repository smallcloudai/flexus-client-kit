import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("yelp")

PROVIDER_NAME = "yelp"
METHOD_IDS = [
    "yelp.businesses.search.v1",
    "yelp.businesses.get.v1",
    "yelp.businesses.reviews.v1",
]

_BASE_URL = "https://api.yelp.com/v3"


class IntegrationYelp:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _get_api_key(self) -> str:
        if self.rcx is not None:
            return (self.rcx.external_auth.get("yelp") or {}).get("api_key", "")
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
        if method_id == "yelp.businesses.search.v1":
            return await self._businesses_search(args)
        if method_id == "yelp.businesses.get.v1":
            return await self._businesses_get(args)
        if method_id == "yelp.businesses.reviews.v1":
            return await self._businesses_reviews(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _auth_headers(self, api_key: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}

    async def _businesses_search(self, args: Dict[str, Any]) -> str:
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set YELP_API_KEY env var."}, indent=2, ensure_ascii=False)
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "query is required"}, indent=2, ensure_ascii=False)
        limit = min(int(args.get("limit", 10)), 50)
        geo = args.get("geo") or {}
        include_raw = bool(args.get("include_raw", False))

        city = geo.get("city", "") if isinstance(geo, dict) else ""
        country = geo.get("country", "") if isinstance(geo, dict) else ""
        location = city or country or "New York"

        params: Dict[str, Any] = {
            "term": query,
            "location": location,
            "limit": limit,
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(_BASE_URL + "/businesses/search", params=params, headers=self._auth_headers(api_key))
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            businesses = data.get("businesses", [])
            total = data.get("total", len(businesses))
            result: Dict[str, Any] = {"ok": True, "results": businesses, "total": total}
            if include_raw:
                result["raw"] = data
            summary = f"Found {len(businesses)} business(es) from {PROVIDER_NAME} (total={total})."
            return summary + "\n\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _businesses_get(self, args: Dict[str, Any]) -> str:
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set YELP_API_KEY env var."}, indent=2, ensure_ascii=False)
        business_id = str(args.get("business_id", "")).strip()
        if not business_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "business_id is required"}, indent=2, ensure_ascii=False)
        include_raw = bool(args.get("include_raw", False))

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(f"{_BASE_URL}/businesses/{business_id}", headers=self._auth_headers(api_key))
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            result: Dict[str, Any] = {"ok": True, "results": [data], "total": 1}
            if include_raw:
                result["raw"] = data
            summary = f"Got business from {PROVIDER_NAME}: {data.get('name', business_id)}."
            return summary + "\n\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _businesses_reviews(self, args: Dict[str, Any]) -> str:
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set YELP_API_KEY env var."}, indent=2, ensure_ascii=False)
        business_id = str(args.get("business_id", "")).strip()
        if not business_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "business_id is required"}, indent=2, ensure_ascii=False)
        limit = min(int(args.get("limit", 3)), 3)
        include_raw = bool(args.get("include_raw", False))

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(
                    f"{_BASE_URL}/businesses/{business_id}/reviews",
                    params={"limit": limit},
                    headers=self._auth_headers(api_key),
                )
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            reviews = data.get("reviews", [])
            total = data.get("total", len(reviews))
            result: Dict[str, Any] = {"ok": True, "results": reviews, "total": total, "note": "Free tier limited to 3 reviews per call"}
            if include_raw:
                result["raw"] = data
            summary = f"Found {len(reviews)} review(s) from {PROVIDER_NAME} (free tier max 3)."
            return summary + "\n\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
