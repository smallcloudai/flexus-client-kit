import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("capterra")

PROVIDER_NAME = "capterra"
METHOD_IDS = [
    "capterra.products.list.v1",
    "capterra.reviews.list.v1",
    "capterra.categories.list.v1",
]

_BASE_URL = "https://www.capterra.com/api/v1"

_PARTNER_NOTE = (
    "Capterra (Gartner Digital Markets) does not expose a public product/review REST API. "
    "Access requires a Gartner Digital Markets partner agreement. "
    "Contact https://digital-markets.gartner.com to request API access."
)


class IntegrationCapterra:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _get_api_key(self) -> str:
        if self.rcx is not None:
            return (self.rcx.external_auth.get("capterra") or {}).get("api_key", "")
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
                f"methods: {', '.join(METHOD_IDS)}\n"
                f"note: {_PARTNER_NOTE}"
            )
        if op == "status":
            api_key = self._get_api_key()
            return json.dumps({
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "available" if api_key else "auth_missing",
                "method_count": len(METHOD_IDS),
                "note": _PARTNER_NOTE,
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
        if method_id == "capterra.products.list.v1":
            return await self._products_list(args)
        if method_id == "capterra.reviews.list.v1":
            return await self._reviews_list(args)
        if method_id == "capterra.categories.list.v1":
            return await self._categories_list(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _products_list(self, args: Dict[str, Any]) -> str:
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": f"Set CAPTERRA_API_KEY env var. {_PARTNER_NOTE}"}, indent=2, ensure_ascii=False)
        query = str(args.get("query", "")).strip()
        limit = min(int(args.get("limit", 25)), 100)
        cursor = args.get("cursor", None)
        include_raw = bool(args.get("include_raw", False))

        params: Dict[str, Any] = {"limit": limit, "apiKey": api_key}
        if query:
            params["q"] = query
        if cursor is not None:
            params["offset"] = int(cursor)

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(_BASE_URL + "/products", params=params, headers={"Accept": "application/json"})
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300], "note": _PARTNER_NOTE}, indent=2, ensure_ascii=False)
            data = r.json()
            items = data.get("data", data.get("results", data.get("products", [])))
            total = data.get("total", len(items))
            result: Dict[str, Any] = {"ok": True, "results": items, "total": total}
            if include_raw:
                result["raw"] = data
            summary = f"Found {len(items)} product(s) from {PROVIDER_NAME} (total={total})."
            return summary + "\n\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}", "note": _PARTNER_NOTE}, indent=2, ensure_ascii=False)

    async def _reviews_list(self, args: Dict[str, Any]) -> str:
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": f"Set CAPTERRA_API_KEY env var. {_PARTNER_NOTE}"}, indent=2, ensure_ascii=False)
        query = str(args.get("query", "")).strip()
        limit = min(int(args.get("limit", 25)), 100)
        cursor = args.get("cursor", None)
        include_raw = bool(args.get("include_raw", False))

        params: Dict[str, Any] = {"limit": limit, "apiKey": api_key}
        if query:
            params["q"] = query
        if cursor is not None:
            params["offset"] = int(cursor)

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(_BASE_URL + "/reviews", params=params, headers={"Accept": "application/json"})
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300], "note": _PARTNER_NOTE}, indent=2, ensure_ascii=False)
            data = r.json()
            items = data.get("data", data.get("results", data.get("reviews", [])))
            total = data.get("total", len(items))
            result: Dict[str, Any] = {"ok": True, "results": items, "total": total}
            if include_raw:
                result["raw"] = data
            summary = f"Found {len(items)} review(s) from {PROVIDER_NAME} (total={total})."
            return summary + "\n\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}", "note": _PARTNER_NOTE}, indent=2, ensure_ascii=False)

    async def _categories_list(self, args: Dict[str, Any]) -> str:
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": f"Set CAPTERRA_API_KEY env var. {_PARTNER_NOTE}"}, indent=2, ensure_ascii=False)
        query = str(args.get("query", "")).strip()
        limit = min(int(args.get("limit", 25)), 100)
        include_raw = bool(args.get("include_raw", False))

        params: Dict[str, Any] = {"limit": limit, "apiKey": api_key}
        if query:
            params["q"] = query

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(_BASE_URL + "/categories", params=params, headers={"Accept": "application/json"})
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300], "note": _PARTNER_NOTE}, indent=2, ensure_ascii=False)
            data = r.json()
            items = data.get("data", data.get("results", data.get("categories", [])))
            total = data.get("total", len(items))
            result: Dict[str, Any] = {"ok": True, "results": items, "total": total}
            if include_raw:
                result["raw"] = data
            summary = f"Found {len(items)} categorie(s) from {PROVIDER_NAME} (total={total})."
            return summary + "\n\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}", "note": _PARTNER_NOTE}, indent=2, ensure_ascii=False)
