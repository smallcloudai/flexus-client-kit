import json
import logging
import os
from typing import Any, Dict, Optional

import httpx

from flexus_client_kit import ckit_cloudtool


logger = logging.getLogger("respondent")

PROVIDER_NAME = "respondent"
METHOD_IDS = [
    "respondent.projects.create.v1",
    "respondent.projects.publish.v1",
    "respondent.screener_responses.list.v1",
    "respondent.screener_responses.qualify.v1",
    "respondent.screener_responses.invite.v1",
    "respondent.screener_responses.attended.v1",
    "respondent.screener_responses.reject.v1",
    "respondent.screener_responses.report.v1",
]

_BASE_URL = "https://api.respondent.io/v1"
_TIMEOUT = 30.0

# Respondent requires partner credentials and staging review before production credentials.
# Required values:
# - RESPONDENT_API_KEY
# - RESPONDENT_API_SECRET
# Common runtime IDs used in onboarding:
# - organization_id
# - team_id
# - researcher_id
# These come from the Respondent researcher organization used for API projects.
RESPONDENT_SETUP_SCHEMA: list[dict[str, Any]] = []


class IntegrationRespondent:
    def __init__(self, rcx=None) -> None:
        self.rcx = rcx

    def _api_key(self) -> str:
        return str(os.environ.get("RESPONDENT_API_KEY", "")).strip()

    def _api_secret(self) -> str:
        return str(os.environ.get("RESPONDENT_API_SECRET", "")).strip()

    def _headers(self) -> Dict[str, str]:
        return {
            "x-api-key": self._api_key(),
            "x-api-secret": self._api_secret(),
            "Content-Type": "application/json",
        }

    def _status(self) -> str:
        has_key = bool(self._api_key())
        has_secret = bool(self._api_secret())
        return json.dumps(
            {
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "ready" if (has_key and has_secret) else "missing_credentials",
                "method_count": len(METHOD_IDS),
                "auth_type": "api_key_and_secret",
                "required_env": [
                    v for v, present in [
                        ("RESPONDENT_API_KEY", has_key),
                        ("RESPONDENT_API_SECRET", has_secret),
                    ] if not present
                ],
                "products": ["Projects", "Screener responses", "Invite and attendance workflow"],
                "message": "Production credentials require a staging demo and API partner approval from Respondent.",
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
            "- Respondent requires staging implementation review before production credentials are issued.\n"
            "- Invite, attended, reject, and report flows are mandatory for a compliant production integration.\n"
            "- Moderated studies also require a scheduling and messaging mechanism outside this core integration file.\n"
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
            return self._error(method_id, "METHOD_UNKNOWN", "Unknown Respondent method.")
        if not self._api_key() or not self._api_secret():
            return self._error(method_id, "AUTH_MISSING", "Set RESPONDENT_API_KEY and RESPONDENT_API_SECRET in the runtime environment.")
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
                url = _BASE_URL + path
                if http_method == "GET":
                    response = await client.get(url, headers=self._headers(), params=params)
                elif http_method == "POST":
                    response = await client.post(url, headers=self._headers(), params=params, json=body)
                elif http_method == "PATCH":
                    response = await client.patch(url, headers=self._headers(), params=params, json=body)
                else:
                    return self._error(method_id, "UNSUPPORTED_HTTP_METHOD", f"Unsupported HTTP method {http_method}.")
        except httpx.TimeoutException:
            return self._error(method_id, "TIMEOUT", "Respondent request timed out.")
        except httpx.HTTPError as e:
            logger.error("respondent request failed", exc_info=e)
            return self._error(method_id, "HTTP_ERROR", f"{type(e).__name__}: {e}")

        if response.status_code >= 400:
            detail: Any = response.text[:1000]
            try:
                detail = response.json()
            except json.JSONDecodeError:
                pass
            logger.info("respondent provider error method=%s status=%s body=%s", method_id, response.status_code, response.text[:300])
            return self._error(method_id, "PROVIDER_ERROR", "Respondent returned an error.", http_status=response.status_code, detail=detail)

        if not response.text.strip():
            return self._result(method_id, {})
        try:
            return self._result(method_id, response.json())
        except json.JSONDecodeError:
            return self._result(method_id, response.text)

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        try:
            if method_id == "respondent.projects.create.v1":
                return await self._request(method_id, "POST", "/projects", body=args)
            if method_id == "respondent.projects.publish.v1":
                project_id = self._require_str(method_id, args, "project_id")
                return await self._request(method_id, "PATCH", f"/projects/{project_id}/publish", body={})
            if method_id == "respondent.screener_responses.list.v1":
                project_id = self._require_str(method_id, args, "project_id")
                params: Dict[str, Any] = {}
                for key in ["page", "per_page", "status", "qualified"]:
                    value = args.get(key)
                    if value not in (None, ""):
                        params[key] = value
                return await self._request(method_id, "GET", f"/projects/{project_id}/screener-responses", params=params)
            if method_id == "respondent.screener_responses.qualify.v1":
                project_id = self._require_str(method_id, args, "project_id")
                screener_response_id = self._require_str(method_id, args, "screener_response_id")
                return await self._request(method_id, "PATCH", f"/projects/{project_id}/screener-responses/{screener_response_id}/qualify", body={})
            if method_id == "respondent.screener_responses.invite.v1":
                project_id = self._require_str(method_id, args, "project_id")
                screener_response_id = self._require_str(method_id, args, "screener_response_id")
                body: Dict[str, Any] = {}
                for key in ["meetingLink", "bookingLink", "message"]:
                    value = args.get(key)
                    if value not in (None, ""):
                        body[key] = value
                return await self._request(method_id, "PATCH", f"/projects/{project_id}/screener-responses/{screener_response_id}/invite", body=body)
            if method_id == "respondent.screener_responses.attended.v1":
                project_id = self._require_str(method_id, args, "project_id")
                screener_response_id = self._require_str(method_id, args, "screener_response_id")
                return await self._request(method_id, "PATCH", f"/projects/{project_id}/screener-responses/{screener_response_id}/attended", body={})
            if method_id == "respondent.screener_responses.reject.v1":
                project_id = self._require_str(method_id, args, "project_id")
                screener_response_id = self._require_str(method_id, args, "screener_response_id")
                body: Dict[str, Any] = {}
                reason = str(args.get("reason", "")).strip()
                if reason:
                    body["reason"] = reason
                return await self._request(method_id, "PATCH", f"/projects/{project_id}/screener-responses/{screener_response_id}/reject", body=body)
            if method_id == "respondent.screener_responses.report.v1":
                project_id = self._require_str(method_id, args, "project_id")
                screener_response_id = self._require_str(method_id, args, "screener_response_id")
                body = {}
                report_reason = str(args.get("reason", "")).strip()
                if report_reason:
                    body["reason"] = report_reason
                return await self._request(method_id, "PATCH", f"/projects/{project_id}/screener-responses/{screener_response_id}/report", body=body)
        except ValueError as e:
            return self._error(method_id, "INVALID_ARGS", str(e))
        return self._error(method_id, "METHOD_UNIMPLEMENTED", "Method is declared but not implemented.")
