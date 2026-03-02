import base64
import json
import logging
import os
from typing import Any, Dict, List

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("gong")

PROVIDER_NAME = "gong"
METHOD_IDS = [
    "gong.calls.list.v1",
    "gong.calls.transcript.get.v1",
]

_BASE_URL = "https://api.gong.io/v2"


class IntegrationGong:
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
            access_key = os.environ.get("GONG_ACCESS_KEY", "")
            access_key_secret = os.environ.get("GONG_ACCESS_KEY_SECRET", "")
            has_creds = bool(access_key and access_key_secret)
            return json.dumps({
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "available" if has_creds else "no_credentials",
                "method_count": len(METHOD_IDS),
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

    def _auth_header(self) -> str:
        access_key = os.environ.get("GONG_ACCESS_KEY", "")
        access_key_secret = os.environ.get("GONG_ACCESS_KEY_SECRET", "")
        credentials = base64.b64encode(f"{access_key}:{access_key_secret}".encode()).decode()
        return f"Basic {credentials}"

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        if method_id == "gong.calls.list.v1":
            return await self._calls_list(args)
        if method_id == "gong.calls.transcript.get.v1":
            return await self._calls_transcript_get(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _calls_list(self, args: Dict[str, Any]) -> str:
        access_key = os.environ.get("GONG_ACCESS_KEY", "")
        access_key_secret = os.environ.get("GONG_ACCESS_KEY_SECRET", "")
        if not (access_key and access_key_secret):
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "GONG_ACCESS_KEY and GONG_ACCESS_KEY_SECRET env vars required"}, indent=2, ensure_ascii=False)
        from_date_time = args.get("from_date_time")
        to_date_time = args.get("to_date_time")
        cursor = args.get("cursor")
        try:
            params: Dict[str, Any] = {}
            if from_date_time:
                params["fromDateTime"] = from_date_time
            if to_date_time:
                params["toDateTime"] = to_date_time
            if cursor:
                params["cursor"] = cursor
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{_BASE_URL}/calls",
                    headers={"Authorization": self._auth_header()},
                    params=params,
                )
            if resp.status_code != 200:
                logger.info("gong calls.list error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            return f"gong.calls.list ok\n\n```json\n{json.dumps({'ok': True, 'calls': data.get('calls', []), 'records': data.get('records', {})}, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _calls_transcript_get(self, args: Dict[str, Any]) -> str:
        access_key = os.environ.get("GONG_ACCESS_KEY", "")
        access_key_secret = os.environ.get("GONG_ACCESS_KEY_SECRET", "")
        if not (access_key and access_key_secret):
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "GONG_ACCESS_KEY and GONG_ACCESS_KEY_SECRET env vars required"}, indent=2, ensure_ascii=False)
        call_ids = args.get("call_ids")
        if not call_ids or not isinstance(call_ids, list):
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "call_ids (list of str) is required"}, indent=2, ensure_ascii=False)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{_BASE_URL}/calls/transcript",
                    headers={
                        "Authorization": self._auth_header(),
                        "Content-Type": "application/json",
                    },
                    json={"filter": {"callIds": call_ids}},
                )
            if resp.status_code != 200:
                logger.info("gong calls.transcript.get error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            return f"gong.calls.transcript.get ok\n\n```json\n{json.dumps({'ok': True, 'callTranscripts': data.get('callTranscripts', [])}, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
