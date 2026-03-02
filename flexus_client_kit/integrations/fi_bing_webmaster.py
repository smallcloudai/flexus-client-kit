import json
import logging
import os
from typing import Any, Dict
from urllib.parse import quote

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("bing_webmaster")

PROVIDER_NAME = "bing_webmaster"
METHOD_IDS = [
    "bing_webmaster.get_page_query_stats.v1",
    "bing_webmaster.get_page_stats.v1",
    "bing_webmaster.get_rank_and_traffic_stats.v1",
]

_BASE_URL = "https://api.webmaster.tools.bing.com/api/6.0"


class IntegrationBingWebmaster:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _get_api_key(self) -> str:
        if self.rcx is not None:
            return (self.rcx.external_auth.get("bing_webmaster") or {}).get("api_key", "")
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
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set BING_WEBMASTER_KEY env var. Obtain from https://www.bing.com/webmasters/api."}, indent=2, ensure_ascii=False)

        site_url = str(args.get("query", ""))
        if not site_url:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.query must be the site URL (e.g. 'https://example.com/')."}, indent=2, ensure_ascii=False)

        encoded_site = quote(site_url, safe="")
        params = {"apikey": api_key}

        if method_id == "bing_webmaster.get_page_stats.v1":
            endpoint = f"/Sites/{encoded_site}/PageStats"
        elif method_id == "bing_webmaster.get_page_query_stats.v1":
            endpoint = f"/Sites/{encoded_site}/PageQueryStats"
        elif method_id == "bing_webmaster.get_rank_and_traffic_stats.v1":
            endpoint = f"/Sites/{encoded_site}/RankAndTrafficStats"
        else:
            return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(
                    _BASE_URL + endpoint,
                    params=params,
                    headers={"Accept": "application/json"},
                )
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            results = data.get("d", data.get("results", data.get("value", data)))
            if not isinstance(results, list):
                results = [results]
            summary = f"Found {len(results)} result(s) from {PROVIDER_NAME} ({method_id})."
            payload: Dict[str, Any] = {"ok": True, "results": results, "total": len(results)}
            if args.get("include_raw"):
                payload["raw"] = data
            return summary + "\n\n```json\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
