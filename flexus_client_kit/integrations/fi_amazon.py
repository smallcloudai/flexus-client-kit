import json
import logging
import os
import time
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("amazon")

PROVIDER_NAME = "amazon"
METHOD_IDS = [
    "amazon.catalog.get_item.v1",
    "amazon.catalog.search_items.v1",
    "amazon.pricing.get_item_offers_batch.v1",
    "amazon.pricing.get_listing_offers_batch.v1",
]

_BASE_URL = "https://sellingpartnerapi-na.amazon.com"
_LWA_URL = "https://api.amazon.com/auth/o2/token"

_token_cache: list = ["", 0.0]  # [access_token, expiry_timestamp]


def _auth_missing() -> str:
    missing = [v for v in ("AMAZON_LWA_CLIENT_ID", "AMAZON_LWA_CLIENT_SECRET", "AMAZON_REFRESH_TOKEN") if not os.environ.get(v)]
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
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(
            _LWA_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": os.environ.get("AMAZON_REFRESH_TOKEN", ""),
                "client_id": os.environ.get("AMAZON_LWA_CLIENT_ID", ""),
                "client_secret": os.environ.get("AMAZON_LWA_CLIENT_SECRET", ""),
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    r.raise_for_status()
    resp = r.json()
    _token_cache[0] = resp["access_token"]
    _token_cache[1] = time.time() + resp.get("expires_in", 3600)
    return _token_cache[0]


class IntegrationAmazon:
    # XXX: requires multiple credentials (AMAZON_LWA_CLIENT_ID + AMAZON_LWA_CLIENT_SECRET + AMAZON_REFRESH_TOKEN).
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
            missing = [v for v in ("AMAZON_LWA_CLIENT_ID", "AMAZON_LWA_CLIENT_SECRET", "AMAZON_REFRESH_TOKEN") if not os.environ.get(v)]
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
        if method_id == "amazon.catalog.search_items.v1":
            return await self._catalog_search(args)
        if method_id == "amazon.catalog.get_item.v1":
            return await self._catalog_get_item(args)
        if method_id == "amazon.pricing.get_item_offers_batch.v1":
            return await self._pricing_item_offers(args)
        if method_id == "amazon.pricing.get_listing_offers_batch.v1":
            return await self._pricing_listing_offers(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _catalog_search(self, args: Dict[str, Any]) -> str:
        query = str(args.get("query", "")).strip()
        limit = min(int(args.get("limit", 10)), 20)
        marketplace_id = os.environ.get("AMAZON_MARKETPLACE_ID", "ATVPDKIKX0DER")
        try:
            token = await _get_access_token()
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(
                    _BASE_URL + "/catalog/2022-04-01/items",
                    params={
                        "marketplaceIds": marketplace_id,
                        "keywords": query,
                        "includedData": "summaries,attributes",
                        "pageSize": limit,
                    },
                    headers={"x-amz-access-token": token, "Accept": "application/json"},
                )
            if r.status_code >= 400:
                logger.info("amazon HTTP %s: %s", r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            items = data.get("items", [])
            compact = [
                {
                    "asin": it.get("asin", ""),
                    "name": (it.get("summaries") or [{}])[0].get("itemName", ""),
                    "brand": (it.get("summaries") or [{}])[0].get("brand", ""),
                }
                for it in items
            ]
            result = {"ok": True, "query": query, "total": data.get("numberOfResults", len(items)), "results": items if args.get("include_raw") else compact}
            return f"Found {len(items)} item(s) from {PROVIDER_NAME}.\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _catalog_get_item(self, args: Dict[str, Any]) -> str:
        asin = str(args.get("asin", "")).strip()
        if not asin:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.asin required"}, indent=2, ensure_ascii=False)
        marketplace_id = os.environ.get("AMAZON_MARKETPLACE_ID", "ATVPDKIKX0DER")
        try:
            token = await _get_access_token()
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(
                    _BASE_URL + f"/catalog/2022-04-01/items/{asin}",
                    params={"marketplaceIds": marketplace_id, "includedData": "summaries,attributes,salesRanks"},
                    headers={"x-amz-access-token": token, "Accept": "application/json"},
                )
            if r.status_code >= 400:
                logger.info("amazon HTTP %s: %s", r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            return f"Found 1 result(s) from {PROVIDER_NAME}.\n\n```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _pricing_item_offers(self, args: Dict[str, Any]) -> str:
        asin = str(args.get("asin", "")).strip()
        if not asin:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.asin required"}, indent=2, ensure_ascii=False)
        marketplace_id = os.environ.get("AMAZON_MARKETPLACE_ID", "ATVPDKIKX0DER")
        try:
            token = await _get_access_token()
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.post(
                    _BASE_URL + "/batches/products/pricing/v0/itemOffers",
                    json={"requests": [{"uri": f"/products/pricing/v0/items/{asin}/offers", "method": "GET", "MarketplaceId": marketplace_id, "ItemCondition": "New"}]},
                    headers={"x-amz-access-token": token, "Accept": "application/json", "Content-Type": "application/json"},
                )
            if r.status_code >= 400:
                logger.info("amazon HTTP %s: %s", r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            return f"Found 1 result(s) from {PROVIDER_NAME}.\n\n```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _pricing_listing_offers(self, args: Dict[str, Any]) -> str:
        asin = str(args.get("asin", "")).strip()
        seller_sku = str(args.get("seller_sku", "")).strip()
        sku = seller_sku or asin
        if not sku:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.asin or args.seller_sku required"}, indent=2, ensure_ascii=False)
        marketplace_id = os.environ.get("AMAZON_MARKETPLACE_ID", "ATVPDKIKX0DER")
        try:
            token = await _get_access_token()
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.post(
                    _BASE_URL + "/batches/products/pricing/v0/listingOffers",
                    json={"requests": [{"uri": f"/products/pricing/v0/listings/{sku}/offers", "method": "GET", "MarketplaceId": marketplace_id, "ItemCondition": "New"}]},
                    headers={"x-amz-access-token": token, "Accept": "application/json", "Content-Type": "application/json"},
                )
            if r.status_code >= 400:
                logger.info("amazon HTTP %s: %s", r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            return f"Found 1 result(s) from {PROVIDER_NAME}.\n\n```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
