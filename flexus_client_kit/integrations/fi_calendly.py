import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("calendly")

PROVIDER_NAME = "calendly"
METHOD_IDS = [
    "calendly.scheduled_events.list.v1",
    "calendly.scheduled_events.invitees.list.v1",
]

_BASE_URL = "https://api.calendly.com"


class IntegrationCalendly:
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
            key = os.environ.get("CALENDLY_ACCESS_TOKEN", "")
            return json.dumps({
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "available" if key else "no_credentials",
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

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        if method_id == "calendly.scheduled_events.list.v1":
            return await self._scheduled_events_list(args)
        if method_id == "calendly.scheduled_events.invitees.list.v1":
            return await self._scheduled_events_invitees_list(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _get_user_uri(self, client: httpx.AsyncClient, token: str) -> str:
        resp = await client.get(
            f"{_BASE_URL}/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        resp.raise_for_status()
        return resp.json()["resource"]["uri"]

    async def _scheduled_events_list(self, args: Dict[str, Any]) -> str:
        token = os.environ.get("CALENDLY_ACCESS_TOKEN", "")
        if not token:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "CALENDLY_ACCESS_TOKEN env var not set"}, indent=2, ensure_ascii=False)
        count = int(args.get("count", 20))
        min_start_time = args.get("min_start_time")
        max_start_time = args.get("max_start_time")
        status = args.get("status")
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                user_uri = await self._get_user_uri(client, token)
                params: Dict[str, Any] = {"user": user_uri, "count": min(count, 100)}
                if min_start_time:
                    params["min_start_time"] = min_start_time
                if max_start_time:
                    params["max_start_time"] = max_start_time
                if status:
                    params["status"] = status
                resp = await client.get(
                    f"{_BASE_URL}/scheduled_events",
                    headers={"Authorization": f"Bearer {token}"},
                    params=params,
                )
            if resp.status_code != 200:
                logger.info("calendly scheduled_events.list error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            return f"calendly.scheduled_events.list ok\n\n```json\n{json.dumps({'ok': True, 'collection': data.get('collection', []), 'pagination': data.get('pagination', {})}, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _scheduled_events_invitees_list(self, args: Dict[str, Any]) -> str:
        token = os.environ.get("CALENDLY_ACCESS_TOKEN", "")
        if not token:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "CALENDLY_ACCESS_TOKEN env var not set"}, indent=2, ensure_ascii=False)
        event_uuid = str(args.get("event_uuid", "")).strip()
        if not event_uuid:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "event_uuid is required"}, indent=2, ensure_ascii=False)
        count = int(args.get("count", 20))
        status = args.get("status")
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                params: Dict[str, Any] = {"count": min(count, 100)}
                if status:
                    params["status"] = status
                resp = await client.get(
                    f"{_BASE_URL}/scheduled_events/{event_uuid}/invitees",
                    headers={"Authorization": f"Bearer {token}"},
                    params=params,
                )
            if resp.status_code != 200:
                logger.info("calendly scheduled_events.invitees.list error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            return f"calendly.scheduled_events.invitees.list ok\n\n```json\n{json.dumps({'ok': True, 'collection': data.get('collection', []), 'pagination': data.get('pagination', {})}, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
