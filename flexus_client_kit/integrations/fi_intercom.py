import json
import logging
import os
from typing import Any, Dict, List, Optional

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("intercom")

PROVIDER_NAME = "intercom"
METHOD_IDS = [
    "intercom.conversations.list.v1",
    "intercom.conversations.search.v1",
]

_BASE_URL = "https://api.intercom.io"
_INTERCOM_VERSION = "2.11"


class IntegrationIntercom:
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
            key = os.environ.get("INTERCOM_ACCESS_TOKEN", "")
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
        if method_id == "intercom.conversations.list.v1":
            return await self._conversations_list(args)
        if method_id == "intercom.conversations.search.v1":
            return await self._conversations_search(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _headers(self, token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Intercom-Version": _INTERCOM_VERSION,
        }

    def _ok(self, method_label: str, data: Any) -> str:
        return f"intercom.{method_label} ok\n\n```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"

    def _provider_error(self, status_code: int, detail: str) -> str:
        logger.info("intercom provider error status=%s detail=%s", status_code, detail)
        return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": status_code, "detail": detail}, indent=2, ensure_ascii=False)

    def _no_credentials(self) -> str:
        return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)

    def _build_search_body(
        self,
        contact_id: Optional[str],
        query_string: Optional[str],
        per_page: int,
        starting_after: Optional[str],
    ) -> Dict[str, Any]:
        filters: List[Dict[str, Any]] = []
        if contact_id:
            filters.append({"field": "contact_ids", "operator": "=", "value": contact_id})
        if query_string:
            filters.append({"field": "source.body", "operator": "~", "value": query_string})

        if filters:
            query: Dict[str, Any] = {"operator": "AND", "value": filters} if len(filters) > 1 else filters[0]
        else:
            query = {"field": "id", "operator": ">", "value": "0"}

        pagination: Dict[str, Any] = {"per_page": per_page}
        if starting_after:
            pagination["starting_after"] = starting_after

        return {"query": query, "pagination": pagination}

    async def _conversations_list(self, args: Dict[str, Any]) -> str:
        token = os.environ.get("INTERCOM_ACCESS_TOKEN", "")
        if not token:
            return self._no_credentials()

        contact_id = str(args.get("contact_id", "")).strip() or None
        if contact_id:
            return await self._conversations_search({
                "method_id": "intercom.conversations.search.v1",
                "contact_id": contact_id,
                "per_page": args.get("per_page", 20),
                "starting_after": args.get("starting_after"),
            })

        order = str(args.get("order", "desc")).strip()
        per_page = int(args.get("per_page", 20))
        starting_after = str(args.get("starting_after", "")).strip() or None

        params: Dict[str, Any] = {"order": order, "per_page": per_page}
        if starting_after:
            params["starting_after"] = starting_after

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(
                    f"{_BASE_URL}/conversations",
                    headers=self._headers(token),
                    params=params,
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

        if resp.status_code not in (200, 201):
            return self._provider_error(resp.status_code, resp.text[:500])
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return self._provider_error(resp.status_code, "invalid json in response")
        return self._ok("conversations.list.v1", data)

    async def _conversations_search(self, args: Dict[str, Any]) -> str:
        token = os.environ.get("INTERCOM_ACCESS_TOKEN", "")
        if not token:
            return self._no_credentials()

        contact_id = str(args.get("contact_id", "")).strip() or None
        query_string = str(args.get("query_string", "")).strip() or None
        per_page = int(args.get("per_page", 20))
        starting_after = str(args.get("starting_after", "")).strip() or None

        body = self._build_search_body(contact_id, query_string, per_page, starting_after)
        headers = {**self._headers(token), "Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(
                    f"{_BASE_URL}/conversations/search",
                    headers=headers,
                    json=body,
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

        if resp.status_code not in (200, 201):
            return self._provider_error(resp.status_code, resp.text[:500])
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return self._provider_error(resp.status_code, "invalid json in response")
        return self._ok("conversations.search.v1", data)
