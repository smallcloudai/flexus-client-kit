import base64
import json
import logging
import os
import time
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("ebay")

PROVIDER_NAME = "ebay"
METHOD_IDS = [
    "ebay.browse.get_items.v1",
    "ebay.browse.search.v1",
    "ebay.marketplace_insights.item_sales_search.v1",
]

_BASE_URL = "https://api.ebay.com"
_TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
_SCOPE = "https://api.ebay.com/oauth/api_scope"

_token_cache: list = ["", 0.0]  # [access_token, expiry_timestamp]


def _auth_missing() -> str:
    missing = [v for v in ("EBAY_APP_ID", "EBAY_CERT_ID") if not os.environ.get(v)]
    if not missing:
        return ""
    return json.dumps({
        "ok": False,
        "error_code": "AUTH_MISSING",
        "message": f"Set env vars: {', '.join(missing)}",
    }, indent=2, ensure_ascii=False)


async def _get_access_token() -> str:
    if _token_cache[0] and time.time() < _token_cache[1] - 30:
        return _token_cache[0]
    app_id = os.environ.get("EBAY_APP_ID", "")
    cert_id = os.environ.get("EBAY_CERT_ID", "")
    credentials = base64.b64encode(f"{app_id}:{cert_id}".encode()).decode()
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(
            _TOKEN_URL,
            data={"grant_type": "client_credentials", "scope": _SCOPE},
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
    r.raise_for_status()
    resp = r.json()
    _token_cache[0] = resp["access_token"]
    _token_cache[1] = time.time() + resp.get("expires_in", 7200)
    return _token_cache[0]


class IntegrationEbay:
    # XXX: requires multiple credentials (EBAY_APP_ID + EBAY_CERT_ID).
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
            missing = [v for v in ("EBAY_APP_ID", "EBAY_CERT_ID") if not os.environ.get(v)]
            return json.dumps({
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "available",
                "method_count": len(METHOD_IDS),
                "auth": ("missing: " + ", ".join(missing)) if missing else "configured",
            }, indent=2, ensure_ascii=False)
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
        if auth_err := _auth_missing():
            return auth_err
        if method_id == "ebay.browse.search.v1":
            return await self._browse_search(args)
        if method_id == "ebay.browse.get_items.v1":
            return await self._browse_get_item(args)
        if method_id == "ebay.marketplace_insights.item_sales_search.v1":
            return await self._marketplace_insights_sales(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _browse_search(self, args: Dict[str, Any]) -> str:
        query = str(args.get("query", "")).strip()
        limit = min(int(args.get("limit", 10)), 50)
        try:
            token = await _get_access_token()
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(
                    _BASE_URL + "/buy/browse/v1/item_summary/search",
                    params={"q": query, "limit": limit, "sort": "bestMatch", "fieldgroups": "EXTENDED"},
                    headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                )
            if r.status_code >= 400:
                logger.info("ebay HTTP %s: %s", r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            items = data.get("itemSummaries", [])
            compact = [
                {
                    "itemId": it.get("itemId", ""),
                    "title": it.get("title", ""),
                    "price": (it.get("price") or {}).get("value", ""),
                    "currency": (it.get("price") or {}).get("currency", ""),
                    "condition": it.get("condition", ""),
                    "buyingOptions": it.get("buyingOptions", []),
                }
                for it in items
            ]
            result = {"ok": True, "query": query, "total": data.get("total", len(items)), "results": items if args.get("include_raw") else compact}
            return f"Found {len(items)} item(s) from {PROVIDER_NAME}.\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _browse_get_item(self, args: Dict[str, Any]) -> str:
        item_id = str(args.get("item_id", "")).strip()
        try:
            token = await _get_access_token()
            if item_id:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    r = await client.get(
                        _BASE_URL + f"/buy/browse/v1/item/{item_id}",
                        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                    )
                if r.status_code >= 400:
                    logger.info("ebay HTTP %s: %s", r.status_code, r.text[:200])
                    return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
                data = r.json()
                return f"Found 1 result(s) from {PROVIDER_NAME}.\n\n```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"
            query = str(args.get("query", "")).strip()
            if not query:
                return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.item_id or args.query required"}, indent=2, ensure_ascii=False)
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(
                    _BASE_URL + "/buy/browse/v1/item_summary/search",
                    params={"q": query, "limit": 1, "sort": "bestMatch"},
                    headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                )
            if r.status_code >= 400:
                logger.info("ebay HTTP %s: %s", r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            items = data.get("itemSummaries", [])
            return f"Found {len(items)} result(s) from {PROVIDER_NAME}.\n\n```json\n{json.dumps({'ok': True, 'results': items}, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _marketplace_insights_sales(self, args: Dict[str, Any]) -> str:
        query = str(args.get("query", "")).strip()
        limit = min(int(args.get("limit", 10)), 50)
        try:
            token = await _get_access_token()
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(
                    _BASE_URL + "/buy/marketplace-insights/v1_beta/item_sales/search",
                    params={"q": query, "limit": limit},
                    headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                )
            if r.status_code == 403:
                return json.dumps({"ok": False, "error_code": "AUTH_REQUIRED", "provider": PROVIDER_NAME, "message": "Marketplace Insights API requires special scope approval from eBay."}, indent=2, ensure_ascii=False)
            if r.status_code >= 400:
                logger.info("ebay HTTP %s: %s", r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            items = data.get("itemSales", data.get("itemSummaries", []))
            result = {"ok": True, "query": query, "total": data.get("total", len(items)), "results": items if args.get("include_raw") else items[:limit]}
            return f"Found {len(items)} sold item(s) from {PROVIDER_NAME}.\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
