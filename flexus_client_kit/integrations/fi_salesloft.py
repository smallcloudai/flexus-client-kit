import json
import logging
import os
from typing import Any, Dict, List

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("salesloft")

PROVIDER_NAME = "salesloft"
API_BASE = "https://api.salesloft.com/v2"
METHOD_IDS = [
    "salesloft.people.list.v1",
    "salesloft.cadence_memberships.create.v1",
]


def _extract_phone(p: Dict[str, Any]) -> str:
    phone = p.get("phone", "")
    if phone:
        return str(phone)
    phones = p.get("phone_numbers")
    if isinstance(phones, list) and phones:
        first = phones[0]
        return first.get("value", "") if isinstance(first, dict) else ""
    return ""


def _normalize_person(p: Dict[str, Any]) -> Dict[str, Any]:
    email = ""
    if isinstance(p.get("email_address"), str):
        email = p["email_address"]
    elif isinstance(p.get("email_addresses"), list) and p["email_addresses"]:
        email = str(p["email_addresses"][0]) if p["email_addresses"] else ""
    return {
        "id": p.get("id"),
        "first_name": p.get("first_name", ""),
        "last_name": p.get("last_name", ""),
        "email": email,
        "title": p.get("title", ""),
        "company": p.get("organization", {}).get("name", "") if isinstance(p.get("organization"), dict) else (p.get("company", "") or ""),
        "phone": _extract_phone(p),
        "created_at": p.get("created_at", ""),
        "updated_at": p.get("updated_at", ""),
        "crm_url": p.get("crm_url", ""),
    }


class IntegrationSalesloft:
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
            token = os.environ.get("SALESLOFT_ACCESS_TOKEN", "")
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
        if method_id == "salesloft.people.list.v1":
            return await self._people_list(call_args)
        if method_id == "salesloft.cadence_memberships.create.v1":
            return await self._cadence_memberships_create(call_args)
        return json.dumps(
            {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
            indent=2,
            ensure_ascii=False,
        )

    def _get_token(self) -> str:
        return os.environ.get("SALESLOFT_ACCESS_TOKEN", "")

    def _headers(self) -> Dict[str, str]:
        token = self._get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def _people_list(self, call_args: Dict[str, Any]) -> str:
        token = self._get_token()
        if not token:
            return json.dumps(
                {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        params: Dict[str, Any] = {}
        email = str(call_args.get("email", "")).strip()
        if email:
            params["email_addresses[]"] = email
        per_page = call_args.get("per_page", 25)
        if isinstance(per_page, int) and 1 <= per_page <= 100:
            params["per_page"] = per_page
        else:
            params["per_page"] = 25
        page = call_args.get("page", 1)
        if isinstance(page, int) and page >= 1:
            params["page"] = page
        else:
            params["page"] = 1
        include_paging = call_args.get("include_paging_counts")
        if include_paging is True:
            params["include_paging_counts"] = "true"
        url = f"{API_BASE}/people.json"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=self._headers(), timeout=30.0)
                response.raise_for_status()
        except httpx.TimeoutException as e:
            logger.info("Salesloft people.list timeout: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPStatusError as e:
            logger.info("Salesloft people.list HTTP status=%s: %s", e.response.status_code, e)
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "HTTP_ERROR",
                    "provider": PROVIDER_NAME,
                    "status_code": e.response.status_code,
                },
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("Salesloft people.list HTTP error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        try:
            payload = response.json()
        except ValueError as e:
            logger.info("Salesloft people.list JSON decode: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        try:
            data: List[Dict[str, Any]] = payload.get("data") or []
            metadata = payload.get("metadata") or {}
            paging = metadata.get("paging") or {}
        except (KeyError, ValueError) as e:
            logger.info("Salesloft people.list response structure: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        normalized = [_normalize_person(p) for p in data if isinstance(p, dict)]
        result: Dict[str, Any] = {
            "ok": True,
            "data": normalized,
            "metadata": {"paging": paging},
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    async def _cadence_memberships_create(self, call_args: Dict[str, Any]) -> str:
        token = self._get_token()
        if not token:
            return json.dumps(
                {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        person_id = call_args.get("person_id")
        cadence_id = call_args.get("cadence_id")
        if person_id is None or cadence_id is None:
            return json.dumps(
                {"ok": False, "error_code": "MISSING_ARGS", "message": "person_id and cadence_id required"},
                indent=2,
                ensure_ascii=False,
            )
        try:
            person_id = int(person_id)
            cadence_id = int(cadence_id)
        except (TypeError, ValueError):
            return json.dumps(
                {"ok": False, "error_code": "INVALID_ARGS", "message": "person_id and cadence_id must be integers"},
                indent=2,
                ensure_ascii=False,
            )
        body: Dict[str, Any] = {"person_id": person_id, "cadence_id": cadence_id}
        user_id = call_args.get("user_id")
        if user_id is not None:
            try:
                body["user_id"] = int(user_id)
            except (TypeError, ValueError):
                pass
        url = f"{API_BASE}/cadence_memberships.json"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=body,
                    headers=self._headers(),
                    timeout=30.0,
                )
                response.raise_for_status()
        except httpx.TimeoutException as e:
            logger.info("Salesloft cadence_memberships.create timeout: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPStatusError as e:
            logger.info("Salesloft cadence_memberships.create HTTP status=%s: %s", e.response.status_code, e)
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "HTTP_ERROR",
                    "provider": PROVIDER_NAME,
                    "status_code": e.response.status_code,
                },
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("Salesloft cadence_memberships.create HTTP error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        try:
            payload = response.json()
        except ValueError as e:
            logger.info("Salesloft cadence_memberships.create JSON decode: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        data = payload.get("data") or payload
        result = {
            "ok": True,
            "id": data.get("id"),
            "person_id": data.get("person_id"),
            "cadence_id": data.get("cadence_id"),
            "current_state": data.get("current_state"),
            "created_at": data.get("created_at"),
        }
        return json.dumps(result, indent=2, ensure_ascii=False)
