import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("tiktok")

PROVIDER_NAME = "tiktok"
METHOD_IDS = [
    "tiktok.research.video_query.v1",
]

_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
_VIDEO_QUERY_URL = "https://open.tiktokapis.com/v2/research/video/query/"


class IntegrationTiktok:
    # XXX: requires multiple credentials (TIKTOK_CLIENT_KEY + TIKTOK_CLIENT_SECRET).
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

    async def _get_access_token(self, client_key: str, client_secret: str) -> str:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.post(
                _TOKEN_URL,
                data={"client_key": client_key, "client_secret": client_secret, "grant_type": "client_credentials"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        if r.status_code >= 400:
            logger.info("tiktok token request failed: HTTP %s: %s", r.status_code, r.text[:200])
            return ""
        return r.json().get("data", {}).get("access_token", r.json().get("access_token", ""))

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        client_key = os.environ.get("TIKTOK_CLIENT_KEY", "")
        client_secret = os.environ.get("TIKTOK_CLIENT_SECRET", "")
        if not client_key or not client_secret:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET env vars."}, indent=2, ensure_ascii=False)

        try:
            token = await self._get_access_token(client_key, client_secret)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "AUTH_FAILED", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

        if not token:
            return json.dumps({"ok": False, "error_code": "AUTH_FAILED", "message": "Could not obtain TikTok access token. Check TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET."}, indent=2, ensure_ascii=False)

        if method_id == "tiktok.research.video_query.v1":
            return await self._video_query(token, args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _video_query(self, token: str, args: Dict) -> str:
        query = str(args.get("query", ""))
        limit = int(args.get("limit", 20))

        now = datetime.utcnow()
        default_end = now.strftime("%Y%m%d")
        default_start = (now - timedelta(days=30)).strftime("%Y%m%d")

        start_date = str(args.get("start_date", "")).replace("-", "") or default_start
        end_date = str(args.get("end_date", "")).replace("-", "") or default_end

        body = {
            "query": {
                "and": [{"operation": "IN", "field_name": "keyword", "field_values": [query]}],
            },
            "max_count": min(limit, 100),
            "start_date": start_date,
            "end_date": end_date,
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.post(
                    _VIDEO_QUERY_URL,
                    json=body,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                )
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            videos = data.get("data", {}).get("videos", data.get("videos", []))
            summary = f"Found {len(videos)} video(s) from {PROVIDER_NAME}."
            payload: Dict[str, Any] = {"ok": True, "results": videos, "total": len(videos)}
            if args.get("include_raw"):
                payload["raw"] = data
            return summary + "\n\n```json\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
