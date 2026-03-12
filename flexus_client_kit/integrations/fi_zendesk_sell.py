import json
import logging
import os
from typing import Any, Dict, List, Union

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("zendesk_sell")

PROVIDER_NAME = "zendesk_sell"
METHOD_IDS = [
    "zendesk_sell.contacts.list.v1",
    "zendesk_sell.deals.list.v1",
]

_BASE_URL = "https://api.getbase.com/v2"


class IntegrationZendeskSell:
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
                "op=help\n"
                "op=status\n"
                "op=list_methods\n"
                "op=call(args={method_id: ...})\n"
                f"known_method_ids={len(METHOD_IDS)}"
            )
        if op == "status":
            token = os.environ.get("ZENDESK_SELL_ACCESS_TOKEN", "")
            return json.dumps(
                {
                    "ok": True,
                    "provider": PROVIDER_NAME,
                    "status": "available" if token else "no_credentials",
                    "method_count": len(METHOD_IDS),
                },
                indent=2,
                ensure_ascii=False,
            )
        if op == "list_methods":
            return json.dumps(
                {"ok": True, "provider": PROVIDER_NAME, "method_ids": METHOD_IDS},
                indent=2,
                ensure_ascii=False,
            )
        if op != "call":
            return "Error: unknown op."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required."
        if method_id not in METHOD_IDS:
            return json.dumps(
                {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
                indent=2,
                ensure_ascii=False,
            )
        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, call_args: Dict[str, Any]) -> str:
        if method_id == "zendesk_sell.contacts.list.v1":
            return await self._contacts_list(call_args)
        if method_id == "zendesk_sell.deals.list.v1":
            return await self._deals_list(call_args)
        return json.dumps(
            {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
            indent=2,
            ensure_ascii=False,
        )

    def _headers(self) -> Dict[str, str]:
        token = os.environ.get("ZENDESK_SELL_ACCESS_TOKEN", "")
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    async def _request(self, path: str, params: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        token = os.environ.get("ZENDESK_SELL_ACCESS_TOKEN", "")
        if not token:
            return json.dumps(
                {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        url = f"{_BASE_URL}{path}"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params, headers=self._headers())
                response.raise_for_status()
        except httpx.TimeoutException as e:
            logger.info("Zendesk Sell timeout path=%s: %s", path, e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "path": path},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPStatusError as e:
            logger.info(
                "Zendesk Sell HTTP error path=%s status=%s: %s",
                path,
                e.response.status_code,
                e,
            )
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "HTTP_ERROR",
                    "path": path,
                    "status_code": e.response.status_code,
                },
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("Zendesk Sell HTTP error path=%s: %s", path, e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "path": path},
                indent=2,
                ensure_ascii=False,
            )
        try:
            payload = response.json()
        except json.JSONDecodeError as e:
            logger.info("Zendesk Sell JSON decode error path=%s: %s", path, e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "path": path},
                indent=2,
                ensure_ascii=False,
            )
        return payload

    def _normalize_contact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        phone = data.get("phone") or data.get("mobile") or ""
        status = data.get("customer_status") or data.get("prospect_status") or "none"
        return {
            "id": data.get("id"),
            "name": data.get("name") or "",
            "email": data.get("email") or "",
            "phone": phone,
            "organization_name": "",
            "status": status,
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
        }

    def _normalize_deal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": data.get("id"),
            "name": data.get("name") or "",
            "value": data.get("value"),
            "currency": data.get("currency") or "",
            "stage_id": data.get("stage_id"),
            "owner_id": data.get("owner_id"),
            "contact_id": data.get("contact_id"),
            "organization_id": data.get("organization_id"),
            "created_at": data.get("created_at"),
            "estimated_close_date": data.get("estimated_close_date"),
        }

    async def _contacts_list(self, call_args: Dict[str, Any]) -> str:
        params: Dict[str, Any] = {}
        name = str(call_args.get("name", "")).strip()
        if name:
            params["name"] = name
        email = str(call_args.get("email", "")).strip()
        if email:
            params["email"] = email
        page = call_args.get("page")
        if page is not None:
            params["page"] = int(page) if isinstance(page, (int, float)) else 1
        else:
            params["page"] = 1
        per_page = call_args.get("per_page")
        if per_page is not None:
            p = int(per_page) if isinstance(per_page, (int, float)) else 25
            params["per_page"] = min(max(p, 1), 100)
        else:
            params["per_page"] = 25
        sort_by = str(call_args.get("sort_by", "")).strip()
        sort_order = str(call_args.get("sort_order", "asc")).strip().lower()
        if sort_by:
            if sort_order == "desc":
                params["sort_by"] = f"{sort_by}:desc"
            else:
                params["sort_by"] = sort_by

        result = await self._request("/contacts", params)
        if isinstance(result, str):
            return result
        items = result.get("items") or []
        meta = result.get("meta") or {}
        normalized: List[Dict[str, Any]] = []
        for item in items:
            data = (item or {}).get("data") or {}
            normalized.append(self._normalize_contact(data))
        return json.dumps(
            {
                "ok": True,
                "items": normalized,
                "meta": {"type": meta.get("type", "collection"), "count": meta.get("count", len(normalized))},
            },
            indent=2,
            ensure_ascii=False,
        )

    async def _deals_list(self, call_args: Dict[str, Any]) -> str:
        params: Dict[str, Any] = {}
        stage_id = call_args.get("stage_id")
        if stage_id is not None:
            params["stage_id"] = int(stage_id) if isinstance(stage_id, (int, float)) else stage_id
        owner_id = call_args.get("owner_id")
        if owner_id is not None:
            params["owner_id"] = int(owner_id) if isinstance(owner_id, (int, float)) else owner_id
        page = call_args.get("page")
        if page is not None:
            params["page"] = int(page) if isinstance(page, (int, float)) else 1
        else:
            params["page"] = 1
        per_page = call_args.get("per_page")
        if per_page is not None:
            p = int(per_page) if isinstance(per_page, (int, float)) else 25
            params["per_page"] = min(max(p, 1), 100)
        else:
            params["per_page"] = 25
        sort_by = str(call_args.get("sort_by", "")).strip()
        sort_order = str(call_args.get("sort_order", "asc")).strip().lower()
        if sort_by:
            if sort_order == "desc":
                params["sort_by"] = f"{sort_by}:desc"
            else:
                params["sort_by"] = sort_by

        result = await self._request("/deals", params)
        if isinstance(result, str):
            return result
        items = result.get("items") or []
        meta = result.get("meta") or {}
        normalized: List[Dict[str, Any]] = []
        for item in items:
            data = (item or {}).get("data") or {}
            normalized.append(self._normalize_deal(data))
        return json.dumps(
            {
                "ok": True,
                "items": normalized,
                "meta": {"type": meta.get("type", "collection"), "count": meta.get("count", len(normalized))},
            },
            indent=2,
            ensure_ascii=False,
        )
