import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("g2")

PROVIDER_NAME = "g2"
METHOD_IDS = [
    "g2.vendors.list.v1",
    "g2.reviews.list.v1",
    "g2.categories.benchmark.v1",
]

_BASE_URL = "https://data.g2.com/api/v1"


class IntegrationG2:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _get_api_key(self) -> str:
        if self.rcx is not None:
            return (self.rcx.external_auth.get("g2") or {}).get("api_key", "")
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
        if method_id == "g2.vendors.list.v1":
            return await self._vendors_list(args)
        if method_id == "g2.reviews.list.v1":
            return await self._reviews_list(args)
        if method_id == "g2.categories.benchmark.v1":
            return await self._categories_benchmark(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _g2_headers(self, api_key: str) -> Dict[str, str]:
        return {
            "Authorization": f"Token token={api_key}",
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
        }

    async def _vendors_list(self, args: Dict[str, Any]) -> str:
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set G2_API_KEY env var. Generate token at https://my.g2.com/developers or https://www.g2.com/static/integrations"}, indent=2, ensure_ascii=False)
        query = str(args.get("query", "")).strip()
        limit = min(int(args.get("limit", 10)), 100)
        cursor = args.get("cursor", None)
        include_raw = bool(args.get("include_raw", False))

        params: Dict[str, Any] = {
            "page[size]": limit,
            "page[number]": int(cursor) if cursor is not None else 1,
        }
        if query:
            params["filter[name]"] = query

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(_BASE_URL + "/products", params=params, headers=self._g2_headers(api_key))
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            items = data.get("data", [])
            meta = data.get("meta", {})
            total = meta.get("record_count", len(items))
            result: Dict[str, Any] = {"ok": True, "results": items, "total": total}
            links = data.get("links", {})
            if links.get("next"):
                result["next_cursor"] = (int(cursor) if cursor else 1) + 1
            if include_raw:
                result["raw"] = data
            summary = f"Found {len(items)} product(s) from {PROVIDER_NAME} (total={total})."
            return summary + "\n\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _reviews_list(self, args: Dict[str, Any]) -> str:
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set G2_API_KEY env var. Generate token at https://my.g2.com/developers or https://www.g2.com/static/integrations"}, indent=2, ensure_ascii=False)
        query = str(args.get("query", "")).strip()
        limit = min(int(args.get("limit", 10)), 100)
        cursor = args.get("cursor", None)
        include_raw = bool(args.get("include_raw", False))

        params: Dict[str, Any] = {
            "page[size]": limit,
            "page[number]": int(cursor) if cursor is not None else 1,
        }
        if query:
            params["filter[product_name]"] = query

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(_BASE_URL + "/survey-responses", params=params, headers=self._g2_headers(api_key))
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            items = data.get("data", [])
            meta = data.get("meta", {})
            total = meta.get("record_count", len(items))
            result: Dict[str, Any] = {"ok": True, "results": items, "total": total}
            links = data.get("links", {})
            if links.get("next"):
                result["next_cursor"] = (int(cursor) if cursor else 1) + 1
            if include_raw:
                result["raw"] = data
            summary = f"Found {len(items)} review(s) from {PROVIDER_NAME} (total={total})."
            return summary + "\n\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _categories_benchmark(self, args: Dict[str, Any]) -> str:
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set G2_API_KEY env var. Generate token at https://my.g2.com/developers or https://www.g2.com/static/integrations"}, indent=2, ensure_ascii=False)
        query = str(args.get("query", "")).strip()
        limit = min(int(args.get("limit", 10)), 100)
        cursor = args.get("cursor", None)
        include_raw = bool(args.get("include_raw", False))

        params: Dict[str, Any] = {
            "page[size]": limit,
            "page[number]": int(cursor) if cursor is not None else 1,
        }
        if query:
            params["filter[name]"] = query

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(_BASE_URL + "/categories", params=params, headers=self._g2_headers(api_key))
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            items = data.get("data", [])
            meta = data.get("meta", {})
            total = meta.get("record_count", len(items))
            result: Dict[str, Any] = {"ok": True, "results": items, "total": total}
            links = data.get("links", {})
            if links.get("next"):
                result["next_cursor"] = (int(cursor) if cursor else 1) + 1
            if include_raw:
                result["raw"] = data
            summary = f"Found {len(items)} categorie(s) from {PROVIDER_NAME} (total={total})."
            return summary + "\n\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
