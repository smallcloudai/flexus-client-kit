import json
import logging
import os
from typing import Any, Dict, List

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("outreach")

PROVIDER_NAME = "outreach"
API_BASE = "https://api.outreach.io/api/v2"
METHOD_IDS = [
    "outreach.prospects.list.v1",
    "outreach.prospects.create.v1",
    "outreach.sequences.list.v1",
]
TIMEOUT_S = 30.0


class IntegrationOutreach:
    def _headers(self, token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
        }

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
            token = os.environ.get("OUTREACH_ACCESS_TOKEN", "")
            status = "available" if token else "no_credentials"
            return json.dumps(
                {"ok": True, "provider": PROVIDER_NAME, "status": status, "method_count": len(METHOD_IDS)},
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
        if method_id == "outreach.prospects.list.v1":
            return await self._prospects_list(call_args)
        if method_id == "outreach.prospects.create.v1":
            return await self._prospects_create(call_args)
        if method_id == "outreach.sequences.list.v1":
            return await self._sequences_list(call_args)
        return json.dumps(
            {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
            indent=2,
            ensure_ascii=False,
        )

    def _ensure_token(self) -> str:
        token = os.environ.get("OUTREACH_ACCESS_TOKEN", "")
        if not token:
            raise ValueError("NO_CREDENTIALS")
        return token

    async def _prospects_list(self, args: Dict[str, Any]) -> str:
        try:
            token = self._ensure_token()
        except ValueError:
            return json.dumps(
                {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        page_size = min(max(int(args.get("page_size", 10)), 1), 100)
        page_number = max(int(args.get("page_number", 1)), 1)
        page_offset = (page_number - 1) * page_size
        params: Dict[str, Any] = {
            "page[size]": page_size,
            "page[offset]": page_offset,
            "count": "false",
        }
        email = str(args.get("email", "")).strip()
        if email:
            params["filter[emails]"] = email
        name = str(args.get("name", "")).strip()
        if name:
            params["filter[name]"] = name
        filter_owner_id = args.get("filter_owner_id")
        if filter_owner_id is not None:
            params["filter[owner][id]"] = int(filter_owner_id)
        url = f"{API_BASE}/prospects"
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_S) as client:
                r = await client.get(url, params=params, headers=self._headers(token))
        except httpx.TimeoutException as e:
            logger.info("Outreach prospects list timeout: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("Outreach prospects list HTTP error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        if r.status_code >= 400:
            logger.info("Outreach prospects list HTTP %s: %s", r.status_code, r.text[:200])
            return json.dumps(
                {"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]},
                indent=2,
                ensure_ascii=False,
            )
        try:
            payload = r.json()
            data_list = payload.get("data") or []
        except (json.JSONDecodeError, KeyError) as e:
            logger.info("Outreach prospects list parse error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        results: List[Dict[str, Any]] = []
        for item in data_list:
            attrs = (item.get("attributes") or {}) if isinstance(item, dict) else {}
            rels = (item.get("relationships") or {}) if isinstance(item, dict) else {}
            stage_data = (rels.get("stage") or {}).get("data") if isinstance(rels.get("stage"), dict) else None
            stage_id = stage_data.get("id") if isinstance(stage_data, dict) else None
            emails = attrs.get("emails") or []
            primary_email = emails[0] if emails else None
            results.append({
                "id": item.get("id"),
                "first_name": attrs.get("firstName"),
                "last_name": attrs.get("lastName"),
                "email": primary_email,
                "title": attrs.get("title"),
                "company": attrs.get("company"),
                "stage": stage_id,
                "created_at": attrs.get("createdAt"),
                "updated_at": attrs.get("updatedAt"),
            })
        return json.dumps(
            {"ok": True, "results": results, "count": len(results)},
            indent=2,
            ensure_ascii=False,
        )

    async def _prospects_create(self, args: Dict[str, Any]) -> str:
        try:
            token = self._ensure_token()
        except ValueError:
            return json.dumps(
                {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        email = str(args.get("email", "")).strip()
        if not email:
            return json.dumps(
                {"ok": False, "error_code": "MISSING_ARG", "message": "email required."},
                indent=2,
                ensure_ascii=False,
            )
        attrs: Dict[str, Any] = {"emails": [email]}
        first_name = str(args.get("first_name", "")).strip()
        if first_name:
            attrs["firstName"] = first_name
        last_name = str(args.get("last_name", "")).strip()
        if last_name:
            attrs["lastName"] = last_name
        title = str(args.get("title", "")).strip()
        if title:
            attrs["title"] = title
        company = str(args.get("company", "")).strip()
        if company:
            attrs["company"] = company
        phone = str(args.get("phone", "")).strip()
        if phone:
            attrs["mobilePhones"] = [phone]
        body = {"data": {"type": "prospect", "attributes": attrs}}
        url = f"{API_BASE}/prospects"
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_S) as client:
                r = await client.post(url, json=body, headers=self._headers(token))
        except httpx.TimeoutException as e:
            logger.info("Outreach prospects create timeout: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("Outreach prospects create HTTP error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        if r.status_code >= 400:
            logger.info("Outreach prospects create HTTP %s: %s", r.status_code, r.text[:200])
            return json.dumps(
                {"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]},
                indent=2,
                ensure_ascii=False,
            )
        try:
            payload = r.json()
            data = payload.get("data")
            if not isinstance(data, dict):
                raise KeyError("data")
            attrs_res = data.get("attributes") or {}
            emails_res = attrs_res.get("emails") or []
            primary_email_res = emails_res[0] if emails_res else email
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.info("Outreach prospects create parse error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        result = {
            "id": data.get("id"),
            "first_name": attrs_res.get("firstName"),
            "last_name": attrs_res.get("lastName"),
            "email": primary_email_res,
            "title": attrs_res.get("title"),
            "company": attrs_res.get("company"),
        }
        return json.dumps(
            {"ok": True, "prospect": result},
            indent=2,
            ensure_ascii=False,
        )

    async def _sequences_list(self, args: Dict[str, Any]) -> str:
        try:
            token = self._ensure_token()
        except ValueError:
            return json.dumps(
                {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        page_size = min(max(int(args.get("page_size", 10)), 1), 100)
        page_number = max(int(args.get("page_number", 1)), 1)
        page_offset = (page_number - 1) * page_size
        params: Dict[str, Any] = {
            "page[size]": page_size,
            "page[offset]": page_offset,
            "count": "false",
        }
        name = str(args.get("name", "")).strip()
        if name:
            params["filter[name]"] = name
        url = f"{API_BASE}/sequences"
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_S) as client:
                r = await client.get(url, params=params, headers=self._headers(token))
        except httpx.TimeoutException as e:
            logger.info("Outreach sequences list timeout: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("Outreach sequences list HTTP error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        if r.status_code >= 400:
            logger.info("Outreach sequences list HTTP %s: %s", r.status_code, r.text[:200])
            return json.dumps(
                {"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]},
                indent=2,
                ensure_ascii=False,
            )
        try:
            payload = r.json()
            data_list = payload.get("data") or []
        except (json.JSONDecodeError, KeyError) as e:
            logger.info("Outreach sequences list parse error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        results: List[Dict[str, Any]] = []
        for item in data_list:
            attrs = (item.get("attributes") or {}) if isinstance(item, dict) else {}
            results.append({
                "id": item.get("id"),
                "name": attrs.get("name"),
                "description": attrs.get("description"),
                "enabled": attrs.get("enabled"),
                "created_at": attrs.get("createdAt"),
            })
        return json.dumps(
            {"ok": True, "results": results, "count": len(results)},
            indent=2,
            ensure_ascii=False,
        )
