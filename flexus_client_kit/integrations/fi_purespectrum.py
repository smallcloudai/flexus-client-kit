import json
import logging
import os
from typing import Any, Dict, Optional

import httpx

from flexus_client_kit import ckit_cloudtool


logger = logging.getLogger("purespectrum")

PROVIDER_NAME = "purespectrum"
METHOD_IDS = [
    "purespectrum.surveys.list.v1",
    "purespectrum.surveys.create.v1",
    "purespectrum.surveys.get.v1",
    "purespectrum.surveys.update.v1",
    "purespectrum.feasibility.get.v1",
    "purespectrum.suppliers.list.v1",
    "purespectrum.traffic_channels.list.v1",
]

_TIMEOUT = 30.0

# PureSpectrum Buy API requires enterprise-issued access tokens.
# Required values:
# - PURESPECTRUM_ACCESS_TOKEN
# Optional values:
# - PURESPECTRUM_ENV=staging to use the staging buyer endpoint
# Credentials are issued by the PureSpectrum product / support team.
PURESPECTRUM_SETUP_SCHEMA: list[dict[str, Any]] = []


class IntegrationPurespectrum:
    def __init__(self, rcx=None) -> None:
        self.rcx = rcx

    def _access_token(self) -> str:
        return str(os.environ.get("PURESPECTRUM_ACCESS_TOKEN", "")).strip()

    def _base_url(self) -> str:
        if str(os.environ.get("PURESPECTRUM_ENV", "")).strip().lower() == "staging":
            return "https://staging.spectrumsurveys.com/buyers/v2"
        return "https://api.spectrumsurveys.com/buyers/v2"

    def _headers(self) -> Dict[str, str]:
        return {
            "access-token": self._access_token(),
            "Content-Type": "application/json",
        }

    def _status(self) -> str:
        env = str(os.environ.get("PURESPECTRUM_ENV", "production")).strip().lower() or "production"
        return json.dumps(
            {
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "ready" if self._access_token() else "missing_credentials",
                "method_count": len(METHOD_IDS),
                "auth_type": "access_token_header",
                "required_env": ["PURESPECTRUM_ACCESS_TOKEN"],
                "optional_env": ["PURESPECTRUM_ENV"],
                "environment": env,
                "products": ["Buyer surveys", "Feasibility", "Suppliers", "Traffic channels"],
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
            "- PureSpectrum Buy API automates survey procurement and sample fulfillment.\n"
            "- Use PURESPECTRUM_ENV=staging during provider onboarding.\n"
            "- Survey payloads usually include category, localization, IR, LOI, live_url, field_time, and quota definitions.\n"
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

    def _require_str(self, method_id: str, args: Dict[str, Any], key: str) -> str:
        value = str(args.get(key, "")).strip()
        if not value:
            raise ValueError(f"{key} is required for {method_id}.")
        return value

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
            return self._error(method_id, "METHOD_UNKNOWN", "Unknown PureSpectrum method.")
        if not self._access_token():
            return self._error(method_id, "AUTH_MISSING", "Set PURESPECTRUM_ACCESS_TOKEN in the runtime environment.")
        return await self._dispatch(method_id, call_args)

    async def _request(
        self,
        method_id: str,
        http_method: str,
        path: str,
        *,
        body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                url = self._base_url() + path
                if http_method == "GET":
                    response = await client.get(url, headers=self._headers(), params=params)
                elif http_method == "POST":
                    response = await client.post(url, headers=self._headers(), params=params, json=body)
                elif http_method == "PATCH":
                    response = await client.patch(url, headers=self._headers(), params=params, json=body)
                else:
                    return self._error(method_id, "UNSUPPORTED_HTTP_METHOD", f"Unsupported HTTP method {http_method}.")
        except httpx.TimeoutException:
            return self._error(method_id, "TIMEOUT", "PureSpectrum request timed out.")
        except httpx.HTTPError as e:
            logger.error("purespectrum request failed", exc_info=e)
            return self._error(method_id, "HTTP_ERROR", f"{type(e).__name__}: {e}")

        if response.status_code >= 400:
            detail: Any = response.text[:1000]
            try:
                detail = response.json()
            except json.JSONDecodeError:
                pass
            logger.info("purespectrum provider error method=%s status=%s body=%s", method_id, response.status_code, response.text[:300])
            return self._error(method_id, "PROVIDER_ERROR", "PureSpectrum returned an error.", http_status=response.status_code, detail=detail)

        if not response.text.strip():
            return self._result(method_id, {})
        try:
            return self._result(method_id, response.json())
        except json.JSONDecodeError:
            return self._result(method_id, response.text)

    def _survey_body(self, method_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "survey_title": self._require_str(method_id, args, "survey_title"),
            "survey_category_code": self._require_str(method_id, args, "survey_category_code"),
            "survey_localization": self._require_str(method_id, args, "survey_localization"),
            "completes_required": int(args.get("completes_required")),
            "expected_ir": int(args.get("expected_ir")),
            "expected_loi": int(args.get("expected_loi")),
            "live_url": self._require_str(method_id, args, "live_url"),
            "field_time": int(args.get("field_time")),
        }
        for key in ["cpi", "qualifications", "quotas", "traffic_channels", "supplier_ids", "exclusions", "metadata"]:
            value = args.get(key)
            if value not in (None, ""):
                body[key] = value
        return body

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        try:
            if method_id == "purespectrum.surveys.list.v1":
                params: Dict[str, Any] = {}
                for key in ["page", "per_page", "status"]:
                    value = args.get(key)
                    if value not in (None, ""):
                        params[key] = value
                return await self._request(method_id, "GET", "/surveys", params=params)
            if method_id == "purespectrum.surveys.create.v1":
                return await self._request(method_id, "POST", "/surveys", body=self._survey_body(method_id, args))
            if method_id == "purespectrum.surveys.get.v1":
                survey_id = self._require_str(method_id, args, "survey_id")
                return await self._request(method_id, "GET", f"/surveys/{survey_id}")
            if method_id == "purespectrum.surveys.update.v1":
                survey_id = self._require_str(method_id, args, "survey_id")
                body: Dict[str, Any] = {}
                for key in [
                    "survey_title",
                    "completes_required",
                    "expected_ir",
                    "expected_loi",
                    "field_time",
                    "live_url",
                    "qualifications",
                    "quotas",
                    "traffic_channels",
                    "supplier_ids",
                ]:
                    value = args.get(key)
                    if value not in (None, ""):
                        body[key] = value
                if not body:
                    return self._error(method_id, "INVALID_ARGS", "At least one survey field is required.")
                return await self._request(method_id, "PATCH", f"/surveys/{survey_id}", body=body)
            if method_id == "purespectrum.feasibility.get.v1":
                params: Dict[str, Any] = {}
                for key in ["survey_category_code", "survey_localization", "completes_required", "expected_ir", "expected_loi"]:
                    value = args.get(key)
                    if value not in (None, ""):
                        params[key] = value
                qualifications = args.get("qualifications")
                if qualifications not in (None, ""):
                    params["qualifications"] = json.dumps(qualifications, ensure_ascii=False)
                return await self._request(method_id, "GET", "/feasibility", params=params)
            if method_id == "purespectrum.suppliers.list.v1":
                return await self._request(method_id, "GET", "/suppliers")
            if method_id == "purespectrum.traffic_channels.list.v1":
                return await self._request(method_id, "GET", "/traffic_channels")
        except ValueError as e:
            return self._error(method_id, "INVALID_ARGS", str(e))
        return self._error(method_id, "METHOD_UNIMPLEMENTED", "Method is declared but not implemented.")
