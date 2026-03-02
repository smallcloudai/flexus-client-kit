import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("trustpilot")

PROVIDER_NAME = "trustpilot"
METHOD_IDS = [
    "trustpilot.business_units.find.v1",
    "trustpilot.business_units.get_public.v1",
    "trustpilot.reviews.list.v1",
]

_BASE_URL = "https://api.trustpilot.com/v1"


class IntegrationTrustpilot:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _get_api_key(self) -> str:
        if self.rcx is not None:
            return (self.rcx.external_auth.get("trustpilot") or {}).get("api_key", "")
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
        if method_id == "trustpilot.business_units.find.v1":
            return await self._find_business_unit(args)
        if method_id == "trustpilot.business_units.get_public.v1":
            return await self._get_business_unit(args)
        if method_id == "trustpilot.reviews.list.v1":
            return await self._list_reviews(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _find_business_unit(self, args: Dict[str, Any]) -> str:
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set TRUSTPILOT_API_KEY env var."}, indent=2, ensure_ascii=False)
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "query (business name or domain) is required"}, indent=2, ensure_ascii=False)
        geo = args.get("geo") or {}
        country = geo.get("country", "US") if isinstance(geo, dict) else "US"
        include_raw = bool(args.get("include_raw", False))

        params: Dict[str, Any] = {
            "name": query,
            "country": country,
            "apikey": api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(_BASE_URL + "/business-units/find", params=params, headers={"Accept": "application/json"})
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            result: Dict[str, Any] = {"ok": True, "results": [data], "total": 1}
            if include_raw:
                result["raw"] = data
            summary = f"Found business unit from {PROVIDER_NAME}: {data.get('displayName', query)}."
            return summary + "\n\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _get_business_unit(self, args: Dict[str, Any]) -> str:
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set TRUSTPILOT_API_KEY env var."}, indent=2, ensure_ascii=False)
        business_unit_id = str(args.get("business_unit_id", "")).strip()
        include_raw = bool(args.get("include_raw", False))

        if not business_unit_id:
            query = str(args.get("query", "")).strip()
            if not query:
                return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "business_unit_id or query is required"}, indent=2, ensure_ascii=False)
            geo = args.get("geo") or {}
            country = geo.get("country", "US") if isinstance(geo, dict) else "US"
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    r = await client.get(
                        _BASE_URL + "/business-units/find",
                        params={"name": query, "country": country, "apikey": api_key},
                        headers={"Accept": "application/json"},
                    )
                if r.status_code >= 400:
                    logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                    return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
                found = r.json()
                business_unit_id = found.get("id", "")
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
            except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

        if not business_unit_id:
            return json.dumps({"ok": False, "error_code": "NOT_FOUND", "message": "Could not resolve business unit ID"}, indent=2, ensure_ascii=False)

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(
                    f"{_BASE_URL}/business-units/{business_unit_id}",
                    params={"apikey": api_key},
                    headers={"Accept": "application/json"},
                )
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            result: Dict[str, Any] = {"ok": True, "results": [data], "total": 1}
            if include_raw:
                result["raw"] = data
            summary = f"Got business unit from {PROVIDER_NAME}: {data.get('displayName', business_unit_id)}."
            return summary + "\n\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _list_reviews(self, args: Dict[str, Any]) -> str:
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set TRUSTPILOT_API_KEY env var."}, indent=2, ensure_ascii=False)
        business_unit_id = str(args.get("business_unit_id", "")).strip()
        limit = min(int(args.get("limit", 20)), 20)
        cursor = args.get("cursor", None)
        include_raw = bool(args.get("include_raw", False))

        if not business_unit_id:
            query = str(args.get("query", "")).strip()
            if not query:
                return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "business_unit_id or query is required"}, indent=2, ensure_ascii=False)
            geo = args.get("geo") or {}
            country = geo.get("country", "US") if isinstance(geo, dict) else "US"
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    r = await client.get(
                        _BASE_URL + "/business-units/find",
                        params={"name": query, "country": country, "apikey": api_key},
                        headers={"Accept": "application/json"},
                    )
                if r.status_code >= 400:
                    logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                    return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
                found = r.json()
                business_unit_id = found.get("id", "")
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
            except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

        if not business_unit_id:
            return json.dumps({"ok": False, "error_code": "NOT_FOUND", "message": "Could not resolve business unit ID"}, indent=2, ensure_ascii=False)

        params: Dict[str, Any] = {
            "apikey": api_key,
            "perPage": limit,
            "language": "en",
        }
        if cursor:
            params["page"] = int(cursor)

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(
                    f"{_BASE_URL}/business-units/{business_unit_id}/reviews",
                    params=params,
                    headers={"Accept": "application/json"},
                )
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            reviews = data.get("reviews", [])
            total = data.get("pagination", {}).get("total", len(reviews))
            result: Dict[str, Any] = {"ok": True, "results": reviews, "total": total}
            if include_raw:
                result["raw"] = data
            summary = f"Found {len(reviews)} review(s) from {PROVIDER_NAME} (total={total})."
            return summary + "\n\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
