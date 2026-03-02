import datetime
import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("zendesk")

PROVIDER_NAME = "zendesk"
METHOD_IDS = [
    "zendesk.incremental.ticket_events.comment_events.list.v1",
    "zendesk.ticket_comments.list.v1",
    "zendesk.tickets.audits.list.v1",
    "zendesk.tickets.list.v1",
    "zendesk.tickets.search.v1",
]


def _base_url() -> str:
    subdomain = os.environ.get("ZENDESK_SUBDOMAIN", "")
    return f"https://{subdomain}.zendesk.com/api/v2"


def _auth() -> tuple:
    email = os.environ.get("ZENDESK_EMAIL", "")
    api_token = os.environ.get("ZENDESK_API_TOKEN", "")
    return (f"{email}/token", api_token)


def _no_creds() -> str:
    return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)


class IntegrationZendesk:
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
            subdomain = os.environ.get("ZENDESK_SUBDOMAIN", "")
            email = os.environ.get("ZENDESK_EMAIL", "")
            api_token = os.environ.get("ZENDESK_API_TOKEN", "")
            has_creds = bool(subdomain and email and api_token)
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

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        if method_id == "zendesk.incremental.ticket_events.comment_events.list.v1":
            return await self._incremental_ticket_events_comment_events_list(args)
        if method_id == "zendesk.ticket_comments.list.v1":
            return await self._ticket_comments_list(args)
        if method_id == "zendesk.tickets.audits.list.v1":
            return await self._tickets_audits_list(args)
        if method_id == "zendesk.tickets.list.v1":
            return await self._tickets_list(args)
        if method_id == "zendesk.tickets.search.v1":
            return await self._tickets_search(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _ok(self, method_label: str, data: Any) -> str:
        return f"zendesk.{method_label} ok\n\n```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"

    def _provider_error(self, status_code: int, detail: str) -> str:
        logger.info("zendesk provider error status=%s detail=%s", status_code, detail)
        return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": status_code, "detail": detail}, indent=2, ensure_ascii=False)

    def _has_creds(self) -> bool:
        return bool(
            os.environ.get("ZENDESK_SUBDOMAIN", "")
            and os.environ.get("ZENDESK_EMAIL", "")
            and os.environ.get("ZENDESK_API_TOKEN", "")
        )

    async def _incremental_ticket_events_comment_events_list(self, args: Dict[str, Any]) -> str:
        if not self._has_creds():
            return _no_creds()
        start_time_raw = args.get("start_time")
        if start_time_raw is None:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "start_time"}, indent=2, ensure_ascii=False)
        if isinstance(start_time_raw, str):
            try:
                start_time = int(datetime.datetime.fromisoformat(start_time_raw).timestamp())
            except ValueError as e:
                return json.dumps({"ok": False, "error_code": "INVALID_ARG", "arg": "start_time", "detail": str(e)}, indent=2, ensure_ascii=False)
        else:
            start_time = int(start_time_raw)
        params: Dict[str, Any] = {"start_time": start_time, "include": "comment_events"}
        limit = args.get("limit")
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(
                    f"{_base_url()}/incremental/ticket_events.json",
                    params=params,
                    auth=_auth(),
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code != 200:
            return self._provider_error(resp.status_code, resp.text[:500])
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return self._provider_error(resp.status_code, "invalid json in response")
        events = data.get("ticket_events", [])
        if limit is not None:
            events = events[:int(limit)]
        result = {
            "ticket_events": events,
            "next_page": data.get("next_page"),
            "count": data.get("count"),
            "end_time": data.get("end_time"),
        }
        return self._ok("incremental.ticket_events.comment_events.list.v1", result)

    async def _ticket_comments_list(self, args: Dict[str, Any]) -> str:
        if not self._has_creds():
            return _no_creds()
        ticket_id = args.get("ticket_id")
        if not ticket_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "ticket_id"}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {}
        cursor = args.get("cursor")
        if cursor:
            params["page[after]"] = cursor
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(
                    f"{_base_url()}/tickets/{ticket_id}/comments.json",
                    params=params,
                    auth=_auth(),
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code != 200:
            return self._provider_error(resp.status_code, resp.text[:500])
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return self._provider_error(resp.status_code, "invalid json in response")
        return self._ok("ticket_comments.list.v1", data)

    async def _tickets_audits_list(self, args: Dict[str, Any]) -> str:
        if not self._has_creds():
            return _no_creds()
        ticket_id = args.get("ticket_id")
        if not ticket_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "ticket_id"}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {}
        cursor = args.get("cursor")
        if cursor:
            params["cursor"] = cursor
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(
                    f"{_base_url()}/tickets/{ticket_id}/audits.json",
                    params=params,
                    auth=_auth(),
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code != 200:
            return self._provider_error(resp.status_code, resp.text[:500])
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return self._provider_error(resp.status_code, "invalid json in response")
        return self._ok("tickets.audits.list.v1", data)

    async def _tickets_list(self, args: Dict[str, Any]) -> str:
        if not self._has_creds():
            return _no_creds()
        sort_by = str(args.get("sort_by", "created_at"))
        sort_order = str(args.get("sort_order", "desc"))
        page = int(args.get("page", 1))
        per_page = min(int(args.get("per_page", 25)), 100)
        params: Dict[str, Any] = {
            "sort_by": sort_by,
            "sort_order": sort_order,
            "page": page,
            "per_page": per_page,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(
                    f"{_base_url()}/tickets.json",
                    params=params,
                    auth=_auth(),
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code != 200:
            return self._provider_error(resp.status_code, resp.text[:500])
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return self._provider_error(resp.status_code, "invalid json in response")
        return self._ok("tickets.list.v1", data)

    async def _tickets_search(self, args: Dict[str, Any]) -> str:
        if not self._has_creds():
            return _no_creds()
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "query"}, indent=2, ensure_ascii=False)
        page = int(args.get("page", 1))
        per_page = int(args.get("per_page", 25))
        params: Dict[str, Any] = {
            "query": query,
            "type": "ticket",
            "page": page,
            "per_page": per_page,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(
                    f"{_base_url()}/search.json",
                    params=params,
                    auth=_auth(),
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code != 200:
            return self._provider_error(resp.status_code, resp.text[:500])
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return self._provider_error(resp.status_code, "invalid json in response")
        return self._ok("tickets.search.v1", data)
