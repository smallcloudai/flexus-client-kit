import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("pinterest")

PROVIDER_NAME = "pinterest"
METHOD_IDS = [
    "pinterest.trends.keywords_top.v1",
]

_TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"
_BASE_URL = "https://api.pinterest.com/v5"


class IntegrationPinterest:
    # XXX: requires multiple credentials (PINTEREST_APP_ID + PINTEREST_APP_SECRET).
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

    async def _get_access_token(self, app_id: str, app_secret: str) -> str:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.post(
                _TOKEN_URL,
                data={"grant_type": "client_credentials"},
                auth=(app_id, app_secret),
                headers={"Accept": "application/json"},
            )
        if r.status_code >= 400:
            logger.info("pinterest token request failed: HTTP %s: %s", r.status_code, r.text[:200])
            return ""
        return r.json().get("access_token", "")

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        app_id = os.environ.get("PINTEREST_APP_ID", "")
        app_secret = os.environ.get("PINTEREST_APP_SECRET", "")
        if not app_id or not app_secret:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set PINTEREST_APP_ID and PINTEREST_APP_SECRET env vars."}, indent=2, ensure_ascii=False)

        try:
            token = await self._get_access_token(app_id, app_secret)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "AUTH_FAILED", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

        if not token:
            return json.dumps({"ok": False, "error_code": "AUTH_FAILED", "message": "Could not obtain Pinterest access token. Check PINTEREST_APP_ID and PINTEREST_APP_SECRET."}, indent=2, ensure_ascii=False)

        if method_id == "pinterest.trends.keywords_top.v1":
            return await self._keywords_top(token, args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _keywords_top(self, token: str, args: Dict) -> str:
        keyword = str(args.get("query", ""))
        if not keyword:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.query (keyword) is required."}, indent=2, ensure_ascii=False)

        geo = args.get("geo") or {}
        region = (geo.get("country", "US") if geo else "US").upper()
        limit = int(args.get("limit", 50))

        params: Dict[str, Any] = {"region": region, "limit": limit}
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(
                    f"{_BASE_URL}/trends/keywords/{keyword}/top/",
                    params=params,
                    headers=headers,
                )
            if r.status_code == 403:
                logger.info("%s HTTP 403 — Trends API may require Pinterest Partner access.", PROVIDER_NAME)
                return json.dumps({
                    "ok": False,
                    "error_code": "PROVIDER_ERROR",
                    "status": 403,
                    "detail": "Pinterest Trends API requires approved Partner access. Apply at https://developers.pinterest.com/",
                }, indent=2, ensure_ascii=False)
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            results = data.get("trends", data.get("items", data.get("results", [])))
            if not isinstance(results, list):
                results = [results]
            summary = f"Found {len(results)} trend(s) from {PROVIDER_NAME} for keyword '{keyword}'."
            payload: Dict[str, Any] = {"ok": True, "results": results, "total": len(results)}
            if args.get("include_raw"):
                payload["raw"] = data
            return summary + "\n\n```json\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
