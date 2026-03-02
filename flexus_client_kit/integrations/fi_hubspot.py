import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("hubspot")

PROVIDER_NAME = "hubspot"
METHOD_IDS = [
    "hubspot.calls.list.v1",
    "hubspot.companies.search.v1",
    "hubspot.contacts.search.v1",
    "hubspot.deals.search.v1",
    "hubspot.deals.update.v1",
    "hubspot.notes.list.v1",
    "hubspot.owners.list.v1",
    "hubspot.tickets.search.v1",
]

_BASE_URL = "https://api.hubapi.com"


class IntegrationHubspot:
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
            key = os.environ.get("HUBSPOT_ACCESS_TOKEN", "")
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
        if method_id == "hubspot.calls.list.v1":
            return await self._calls_list(args)
        if method_id == "hubspot.companies.search.v1":
            return await self._companies_search(args)
        if method_id == "hubspot.contacts.search.v1":
            return await self._contacts_search(args)
        if method_id == "hubspot.deals.search.v1":
            return await self._deals_search(args)
        if method_id == "hubspot.deals.update.v1":
            return await self._deals_update(args)
        if method_id == "hubspot.notes.list.v1":
            return await self._notes_list(args)
        if method_id == "hubspot.owners.list.v1":
            return await self._owners_list(args)
        if method_id == "hubspot.tickets.search.v1":
            return await self._tickets_search(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _headers(self, token: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def _ok(self, method_label: str, data: Any) -> str:
        return f"hubspot.{method_label} ok\n\n```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"

    def _provider_error(self, status_code: int, detail: str) -> str:
        logger.info("hubspot provider error status=%s detail=%s", status_code, detail)
        return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": status_code, "detail": detail}, indent=2, ensure_ascii=False)

    def _no_credentials(self) -> str:
        return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)

    def _token(self) -> str:
        return os.environ.get("HUBSPOT_ACCESS_TOKEN", "")

    async def _contacts_search(self, args: Dict[str, Any]) -> str:
        token = self._token()
        if not token:
            return self._no_credentials()
        query = str(args.get("query", "")).strip()
        properties = args.get("properties") or ["email", "firstname", "lastname", "phone", "company"]
        limit = int(args.get("limit", 10))
        body: Dict[str, Any] = {"properties": properties, "limit": limit}
        if query:
            body["query"] = query
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(f"{_BASE_URL}/crm/v3/objects/contacts/search", headers=self._headers(token), json=body)
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
        return self._ok("contacts.search.v1", data)

    async def _notes_list(self, args: Dict[str, Any]) -> str:
        token = self._token()
        if not token:
            return self._no_credentials()
        contact_id = str(args.get("contact_id", "")).strip()
        limit = int(args.get("limit", 20))
        after = str(args.get("after", "")).strip()
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                if contact_id:
                    body: Dict[str, Any] = {
                        "filterGroups": [{"filters": [{"propertyName": "associations.contact", "operator": "EQ", "value": contact_id}]}],
                        "properties": ["hs_note_body", "hs_timestamp"],
                        "limit": limit,
                    }
                    if after:
                        body["after"] = after
                    resp = await client.post(f"{_BASE_URL}/crm/v3/objects/notes/search", headers=self._headers(token), json=body)
                else:
                    params: Dict[str, Any] = {
                        "properties": "hs_note_body,hs_timestamp",
                        "associations": "contact",
                        "limit": limit,
                    }
                    if after:
                        params["after"] = after
                    resp = await client.get(f"{_BASE_URL}/crm/v3/objects/notes", headers=self._headers(token), params=params)
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
        return self._ok("notes.list.v1", data)

    async def _calls_list(self, args: Dict[str, Any]) -> str:
        token = self._token()
        if not token:
            return self._no_credentials()
        contact_id = str(args.get("contact_id", "")).strip()
        limit = int(args.get("limit", 20))
        after = str(args.get("after", "")).strip()
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                if contact_id:
                    body: Dict[str, Any] = {
                        "filterGroups": [{"filters": [{"propertyName": "associations.contact", "operator": "EQ", "value": contact_id}]}],
                        "properties": ["hs_call_body", "hs_call_duration", "hs_timestamp"],
                        "limit": limit,
                    }
                    if after:
                        body["after"] = after
                    resp = await client.post(f"{_BASE_URL}/crm/v3/objects/calls/search", headers=self._headers(token), json=body)
                else:
                    params: Dict[str, Any] = {
                        "properties": "hs_call_body,hs_call_duration,hs_timestamp",
                        "associations": "contact",
                        "limit": limit,
                    }
                    if after:
                        params["after"] = after
                    resp = await client.get(f"{_BASE_URL}/crm/v3/objects/calls", headers=self._headers(token), params=params)
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
        return self._ok("calls.list.v1", data)

    async def _companies_search(self, args: Dict[str, Any]) -> str:
        token = self._token()
        if not token:
            return self._no_credentials()
        query = str(args.get("query", "")).strip()
        properties = args.get("properties") or ["name", "domain", "industry"]
        limit = int(args.get("limit", 10))
        body: Dict[str, Any] = {"properties": properties, "limit": limit}
        if query:
            body["query"] = query
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(f"{_BASE_URL}/crm/v3/objects/companies/search", headers=self._headers(token), json=body)
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
        return self._ok("companies.search.v1", data)

    async def _deals_search(self, args: Dict[str, Any]) -> str:
        token = self._token()
        if not token:
            return self._no_credentials()
        query = str(args.get("query", "")).strip()
        properties = args.get("properties") or ["dealname", "dealstage", "amount"]
        limit = int(args.get("limit", 10))
        body: Dict[str, Any] = {"properties": properties, "limit": limit}
        if query:
            body["query"] = query
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(f"{_BASE_URL}/crm/v3/objects/deals/search", headers=self._headers(token), json=body)
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
        return self._ok("deals.search.v1", data)

    async def _deals_update(self, args: Dict[str, Any]) -> str:
        token = self._token()
        if not token:
            return self._no_credentials()
        deal_id = str(args.get("deal_id", "")).strip()
        if not deal_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "deal_id"}, indent=2, ensure_ascii=False)
        properties = args.get("properties")
        if not properties or not isinstance(properties, dict):
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "properties"}, indent=2, ensure_ascii=False)
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.patch(
                    f"{_BASE_URL}/crm/v3/objects/deals/{deal_id}",
                    headers=self._headers(token),
                    json={"properties": properties},
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
        return self._ok("deals.update.v1", data)

    async def _owners_list(self, args: Dict[str, Any]) -> str:
        token = self._token()
        if not token:
            return self._no_credentials()
        limit = int(args.get("limit", 100))
        after = str(args.get("after", "")).strip()
        params: Dict[str, Any] = {"limit": limit}
        if after:
            params["after"] = after
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(f"{_BASE_URL}/crm/v3/owners", headers=self._headers(token), params=params)
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
        return self._ok("owners.list.v1", data)

    async def _tickets_search(self, args: Dict[str, Any]) -> str:
        token = self._token()
        if not token:
            return self._no_credentials()
        query = str(args.get("query", "")).strip()
        properties = args.get("properties") or ["subject", "content", "hs_ticket_priority"]
        limit = int(args.get("limit", 10))
        body: Dict[str, Any] = {"properties": properties, "limit": limit}
        if query:
            body["query"] = query
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(f"{_BASE_URL}/crm/v3/objects/tickets/search", headers=self._headers(token), json=body)
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
        return self._ok("tickets.search.v1", data)
