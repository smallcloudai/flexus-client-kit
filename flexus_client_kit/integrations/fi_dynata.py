import json
import logging
import os
from typing import Any, Dict, Optional

import httpx

from flexus_client_kit import ckit_cloudtool


logger = logging.getLogger("dynata")

PROVIDER_NAME = "dynata"
METHOD_IDS = [
    "dynata.demand.projects.create.v1",
    "dynata.demand.projects.get.v1",
    "dynata.demand.quota_cells.launch.v1",
    "dynata.rex.respondents.upsert.v1",
]

_TIMEOUT = 30.0

# Dynata exposes more than one API family.
# Demand API values:
# - DYNATA_DEMAND_API_KEY
# - DYNATA_DEMAND_BASE_URL
# REX values:
# - DYNATA_REX_ACCESS_KEY
# - DYNATA_REX_SECRET_KEY
# - DYNATA_REX_BASE_URL
# The base URLs are provided by Dynata during onboarding, so this integration does not invent them.
DYNATA_SETUP_SCHEMA: list[dict[str, Any]] = []


class IntegrationDynata:
    def __init__(self, rcx=None) -> None:
        self.rcx = rcx

    def _demand_api_key(self) -> str:
        return str(os.environ.get("DYNATA_DEMAND_API_KEY", "")).strip()

    def _demand_base_url(self) -> str:
        return str(os.environ.get("DYNATA_DEMAND_BASE_URL", "")).strip().rstrip("/")

    def _rex_access_key(self) -> str:
        return str(os.environ.get("DYNATA_REX_ACCESS_KEY", "")).strip()

    def _rex_secret_key(self) -> str:
        return str(os.environ.get("DYNATA_REX_SECRET_KEY", "")).strip()

    def _rex_base_url(self) -> str:
        return str(os.environ.get("DYNATA_REX_BASE_URL", "")).strip().rstrip("/")

    def _status(self) -> str:
        return json.dumps(
            {
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "ready" if (self._demand_api_key() and self._demand_base_url()) or (self._rex_access_key() and self._rex_secret_key() and self._rex_base_url()) else "partial_or_missing_credentials",
                "method_count": len(METHOD_IDS),
                "demand_ready": bool(self._demand_api_key() and self._demand_base_url()),
                "rex_ready": bool(self._rex_access_key() and self._rex_secret_key() and self._rex_base_url()),
                "required_env": [
                    "DYNATA_DEMAND_API_KEY",
                    "DYNATA_DEMAND_BASE_URL",
                    "DYNATA_REX_ACCESS_KEY",
                    "DYNATA_REX_SECRET_KEY",
                    "DYNATA_REX_BASE_URL",
                ],
                "products": ["Demand API", "Respondent Exchange (REX)"],
                "message": "Dynata issues different credentials for Demand and REX flows; configure whichever family you plan to use.",
            },
            indent=2,
            ensure_ascii=False,
        )

    def _help(self) -> str:
        return (
            f"provider={PROVIDER_NAME}\n"
            "op=help | status | list_methods | call\n"
            f"methods: {', '.join(METHOD_IDS)}\n"
            "notes:\n"
            "- Dynata Demand and REX are separate API families with separate credentials.\n"
            "- Base URLs come from Dynata onboarding, so Flexus stores them as runtime config.\n"
            "- This file exposes only the documented high-value recruitment flows with stable naming.\n"
        )

    def _error(self, method_id: str, code: str, message: str, **extra: Any) -> str:
        payload: Dict[str, Any] = {
            "ok": False,
            "provider": PROVIDER_NAME,
            "method_id": method_id,
            "error_code": code,
            "message": message,
        }
        payload.update(extra)
        return json.dumps(payload, indent=2, ensure_ascii=False)

    def _result(self, method_id: str, result: Any) -> str:
        return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_id": method_id, "result": result}, indent=2, ensure_ascii=False)

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]],
    ) -> str:
        args = model_produced_args or {}
        op = str(args.get("op", "help")).strip()
        if op == "help":
            return self._help()
        if op == "status":
            return self._status()
        if op == "list_methods":
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_ids": METHOD_IDS}, indent=2, ensure_ascii=False)
        if op != "call":
            return "Error: unknown op. Use help/status/list_methods/call."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_IDS:
            return self._error(method_id, "METHOD_UNKNOWN", "Unknown Dynata method.")
        return await self._dispatch(method_id, call_args)

    async def _demand_request(self, method_id: str, http_method: str, path: str, *, body: Optional[Dict[str, Any]] = None) -> str:
        if not self._demand_api_key() or not self._demand_base_url():
            return self._error(method_id, "AUTH_MISSING", "Set DYNATA_DEMAND_API_KEY and DYNATA_DEMAND_BASE_URL in the runtime environment.")
        headers = {
            "Authorization": self._demand_api_key(),
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                url = self._demand_base_url() + path
                if http_method == "GET":
                    response = await client.get(url, headers=headers)
                elif http_method == "POST":
                    response = await client.post(url, headers=headers, json=body)
                else:
                    return self._error(method_id, "UNSUPPORTED_HTTP_METHOD", f"Unsupported HTTP method {http_method}.")
        except httpx.TimeoutException:
            return self._error(method_id, "TIMEOUT", "Dynata Demand request timed out.")
        except httpx.HTTPError as e:
            logger.error("dynata demand request failed", exc_info=e)
            return self._error(method_id, "HTTP_ERROR", f"{type(e).__name__}: {e}")
        if response.status_code >= 400:
            return self._error(method_id, "PROVIDER_ERROR", "Dynata Demand returned an error.", http_status=response.status_code, detail=response.text[:1000])
        if not response.text.strip():
            return self._result(method_id, {})
        try:
            return self._result(method_id, response.json())
        except json.JSONDecodeError:
            return self._result(method_id, response.text)

    async def _rex_request(self, method_id: str, path: str, body: Dict[str, Any]) -> str:
        if not self._rex_access_key() or not self._rex_secret_key() or not self._rex_base_url():
            return self._error(method_id, "AUTH_MISSING", "Set DYNATA_REX_ACCESS_KEY, DYNATA_REX_SECRET_KEY, and DYNATA_REX_BASE_URL in the runtime environment.")
        headers = {
            "access_key": self._rex_access_key(),
            "secret_key": self._rex_secret_key(),
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.put(self._rex_base_url() + path, headers=headers, json=body)
        except httpx.TimeoutException:
            return self._error(method_id, "TIMEOUT", "Dynata REX request timed out.")
        except httpx.HTTPError as e:
            logger.error("dynata rex request failed", exc_info=e)
            return self._error(method_id, "HTTP_ERROR", f"{type(e).__name__}: {e}")
        if response.status_code >= 400:
            return self._error(method_id, "PROVIDER_ERROR", "Dynata REX returned an error.", http_status=response.status_code, detail=response.text[:1000])
        if not response.text.strip():
            return self._result(method_id, {})
        try:
            return self._result(method_id, response.json())
        except json.JSONDecodeError:
            return self._result(method_id, response.text)

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        if method_id == "dynata.demand.projects.create.v1":
            return await self._demand_request(method_id, "POST", "/projects", body=args)
        if method_id == "dynata.demand.projects.get.v1":
            project_id = str(args.get("project_id", "")).strip()
            if not project_id:
                return self._error(method_id, "INVALID_ARGS", "project_id is required.")
            return await self._demand_request(method_id, "GET", f"/projects/{project_id}")
        if method_id == "dynata.demand.quota_cells.launch.v1":
            quota_cell_id = str(args.get("quota_cell_id", "")).strip()
            if not quota_cell_id:
                return self._error(method_id, "INVALID_ARGS", "quota_cell_id is required.")
            body = {}
            project_id = str(args.get("project_id", "")).strip()
            if project_id:
                body["project_id"] = project_id
            return await self._demand_request(method_id, "POST", f"/quota-cells/{quota_cell_id}/launch", body=body)
        if method_id == "dynata.rex.respondents.upsert.v1":
            respondent_id = str(args.get("respondent_id", "")).strip()
            country = str(args.get("country", "")).strip()
            language = str(args.get("language", "")).strip()
            if not respondent_id or not country or not language:
                return self._error(method_id, "INVALID_ARGS", "respondent_id, country, and language are required.")
            body = dict(args)
            return await self._rex_request(method_id, "/put-respondent", body=body)
        return self._error(method_id, "METHOD_UNIMPLEMENTED", "Method is declared but not implemented.")
