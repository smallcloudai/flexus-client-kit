import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("adzuna")

PROVIDER_NAME = "adzuna"
METHOD_IDS = [
    "adzuna.jobs.search_ads.v1",
    "adzuna.jobs.regional_data.v1",
]

_BASE_URL = "https://api.adzuna.com/v1/api"


class IntegrationAdzuna:
    # XXX: requires multiple credentials (ADZUNA_APP_ID + ADZUNA_APP_KEY).
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

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        app_id = os.environ.get("ADZUNA_APP_ID", "")
        app_key = os.environ.get("ADZUNA_APP_KEY", "")
        if not app_id or not app_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set ADZUNA_APP_ID and ADZUNA_APP_KEY env vars."}, indent=2, ensure_ascii=False)

        if method_id == "adzuna.jobs.search_ads.v1":
            return await self._search_ads(args, app_id, app_key)
        if method_id == "adzuna.jobs.regional_data.v1":
            return await self._regional_data(args, app_id, app_key)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _search_ads(self, args: Dict[str, Any], app_id: str, app_key: str) -> str:
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "args.query required."}, indent=2, ensure_ascii=False)

        geo = args.get("geo") or {}
        if isinstance(geo, str):
            geo = {"country": geo}
        country = str(geo.get("country", "us")).lower() or "us"
        city = str(geo.get("city", ""))
        limit = min(int(args.get("limit", 20)), 50)

        params: Dict[str, Any] = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": limit,
            "what": query,
            "sort_by": "date",
            "max_days_old": 30,
        }
        if city:
            params["where"] = city

        url = f"{_BASE_URL}/jobs/{country}/search/1"
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(url, params=params)
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            results = data.get("results", [])
            include_raw = bool(args.get("include_raw"))
            out = {"ok": True, "total": data.get("count", len(results)), "results": results}
            if not include_raw:
                out["results"] = [
                    {
                        "title": j.get("title"),
                        "company": j.get("company", {}).get("display_name"),
                        "location": j.get("location", {}).get("display_name"),
                        "salary_min": j.get("salary_min"),
                        "salary_max": j.get("salary_max"),
                        "created": j.get("created"),
                        "redirect_url": j.get("redirect_url"),
                    }
                    for j in results
                ]
            summary = f"Found {len(results)} job(s) from {PROVIDER_NAME}."
            return summary + "\n\n```json\n" + json.dumps(out, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _regional_data(self, args: Dict[str, Any], app_id: str, app_key: str) -> str:
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "args.query required."}, indent=2, ensure_ascii=False)

        geo = args.get("geo") or {}
        if isinstance(geo, str):
            geo = {"country": geo}
        country = str(geo.get("country", "us")).lower() or "us"

        url = f"{_BASE_URL}/jobs/{country}/histogram"
        params = {"app_id": app_id, "app_key": app_key, "what": query}
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(url, params=params)
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            summary = f"Regional salary histogram from {PROVIDER_NAME} for '{query}'."
            return summary + "\n\n```json\n" + json.dumps({"ok": True, "data": data}, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
