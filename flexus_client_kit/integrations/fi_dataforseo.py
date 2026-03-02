import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("dataforseo")

PROVIDER_NAME = "dataforseo"
METHOD_IDS = [
    "dataforseo.trends.demography.live.v1",
    "dataforseo.trends.explore.live.v1",
    "dataforseo.trends.merged_data.live.v1",
    "dataforseo.trends.subregion_interests.live.v1",
]

_BASE_URL = "https://api.dataforseo.com/v3"

_METHOD_ENDPOINTS = {
    "dataforseo.trends.explore.live.v1": "/dataforseo_trends/explore/live",
    "dataforseo.trends.subregion_interests.live.v1": "/dataforseo_trends/subregion_interests/live",
    "dataforseo.trends.demography.live.v1": "/dataforseo_trends/demography/live",
    "dataforseo.trends.merged_data.live.v1": "/dataforseo_trends/merged_data/live",
}


class IntegrationDataforseo:
    # XXX: requires multiple credentials (DATAFORSEO_LOGIN + DATAFORSEO_PASSWORD).
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
        login = os.environ.get("DATAFORSEO_LOGIN", "")
        password = os.environ.get("DATAFORSEO_PASSWORD", "")
        if not login or not password:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD env vars."}, indent=2, ensure_ascii=False)

        query = args.get("query", "")
        if isinstance(query, str):
            keywords = [query] if query else []
        else:
            keywords = list(query)

        geo = args.get("geo") or {}
        location_name = geo.get("country", "United States") if geo else "United States"
        start_date = args.get("start_date")

        body: Dict[str, Any] = {"keywords": keywords, "location_name": location_name}
        if start_date and method_id == "dataforseo.trends.explore.live.v1":
            body["date_from"] = start_date

        endpoint = _METHOD_ENDPOINTS[method_id]

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.post(
                    _BASE_URL + endpoint,
                    json=[body],
                    auth=(login, password),
                    headers={"Content-Type": "application/json"},
                )
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            tasks = data.get("tasks", [])
            results = []
            for task in tasks:
                task_results = (task.get("result") or [])
                results.extend(task_results)
            summary = f"Found {len(results)} result(s) from {PROVIDER_NAME} ({method_id})."
            payload: Dict[str, Any] = {"ok": True, "results": results, "total": len(results)}
            if args.get("include_raw"):
                payload["raw"] = data
            return summary + "\n\n```json\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
