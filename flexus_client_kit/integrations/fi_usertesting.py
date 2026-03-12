import json
import logging
import os
from typing import Any, Dict, Optional

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("usertesting")

PROVIDER_NAME = "usertesting"
METHOD_IDS = [
    "usertesting.tests.get.v1",
    "usertesting.tests.sessions.list.v1",
    "usertesting.results.transcript.get.v1",
    "usertesting.results.video.get.v1",
    "usertesting.results.qxscore.get.v1",
]

_BASE_URL = "https://api.use2.usertesting.com/api/v2"
_TIMEOUT = 30.0

# UserTesting access is reviewed and normally enterprise-gated.
# Required values once the account is approved:
# - USERTESTING_ACCESS_TOKEN: bearer token for the Results / platform APIs.
# Optional values for colleague onboarding notes:
# - USERTESTING_CLIENT_ID
# - USERTESTING_CLIENT_SECRET
# These values come from the UserTesting developer portal after the API team approves the app.
USERTESTING_SETUP_SCHEMA: list[dict[str, Any]] = []


class IntegrationUsertesting:
    def __init__(self, rcx=None) -> None:
        self.rcx = rcx

    def _access_token(self) -> str:
        try:
            return str(os.environ.get("USERTESTING_ACCESS_TOKEN", "")).strip()
        except (TypeError, ValueError):
            return ""

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._access_token()}",
            "Content-Type": "application/json",
        }

    def _status(self) -> str:
        return json.dumps(
            {
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "ready" if self._access_token() else "enterprise_review_required",
                "method_count": len(METHOD_IDS),
                "auth_type": "reviewed_bearer_token",
                "required_env": ["USERTESTING_ACCESS_TOKEN"],
                "optional_env": ["USERTESTING_CLIENT_ID", "USERTESTING_CLIENT_SECRET"],
                "message": "UserTesting API access requires enterprise approval and app review before tokens are issued.",
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
            "- UserTesting access is reviewed; obtain credentials from developer.usertesting.com after approval.\n"
            "- This integration focuses on documented test and results retrieval flows.\n"
            "- Test creation is intentionally not exposed until the create flow is officially confirmed for the approved account tier.\n"
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
            return json.dumps(
                {"ok": True, "provider": PROVIDER_NAME, "method_ids": METHOD_IDS},
                indent=2,
                ensure_ascii=False,
            )
        if op != "call":
            return "Error: unknown op. Use help/status/list_methods/call."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_IDS:
            return self._error(method_id, "METHOD_UNKNOWN", "Unknown UserTesting method.")
        if not self._access_token():
            return self._error(
                method_id,
                "AUTH_MISSING",
                "Set USERTESTING_ACCESS_TOKEN after the UserTesting API team approves the app.",
            )
        return await self._dispatch(method_id, call_args)

    async def _request(self, method_id: str, path: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.get(_BASE_URL + path, headers=self._headers())
        except httpx.TimeoutException:
            return self._error(method_id, "TIMEOUT", "UserTesting request timed out.")
        except httpx.HTTPError as e:
            logger.error("usertesting request failed", exc_info=e)
            return self._error(method_id, "HTTP_ERROR", f"{type(e).__name__}: {e}")

        if response.status_code >= 400:
            detail: Any = response.text[:1000]
            try:
                detail = response.json()
            except json.JSONDecodeError:
                pass
            logger.info("usertesting provider error method=%s status=%s body=%s", method_id, response.status_code, response.text[:300])
            return self._error(method_id, "PROVIDER_ERROR", "UserTesting returned an error.", http_status=response.status_code, detail=detail)

        if not response.text.strip():
            return self._result(method_id, {})
        try:
            return self._result(method_id, response.json())
        except json.JSONDecodeError:
            return self._result(method_id, response.text)

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        try:
            if method_id == "usertesting.tests.get.v1":
                test_id = str(args.get("test_id", "")).strip()
                if not test_id:
                    return self._error(method_id, "INVALID_ARGS", "test_id is required.")
                return await self._request(method_id, f"/tests/{test_id}")
            if method_id == "usertesting.tests.sessions.list.v1":
                test_id = str(args.get("test_id", "")).strip()
                if not test_id:
                    return self._error(method_id, "INVALID_ARGS", "test_id is required.")
                return await self._request(method_id, f"/testResults/{test_id}/sessions")
            if method_id == "usertesting.results.transcript.get.v1":
                session_id = str(args.get("session_id", "")).strip()
                if not session_id:
                    return self._error(method_id, "INVALID_ARGS", "session_id is required.")
                return await self._request(method_id, f"/sessions/{session_id}/transcript-vtt")
            if method_id == "usertesting.results.video.get.v1":
                session_id = str(args.get("session_id", "")).strip()
                if not session_id:
                    return self._error(method_id, "INVALID_ARGS", "session_id is required.")
                return await self._request(method_id, f"/sessions/{session_id}/video")
            if method_id == "usertesting.results.qxscore.get.v1":
                test_id = str(args.get("test_id", "")).strip()
                if not test_id:
                    return self._error(method_id, "INVALID_ARGS", "test_id is required.")
                return await self._request(method_id, f"/testResults/{test_id}/qxScores")
        except (TypeError, ValueError) as e:
            logger.error("usertesting dispatch failed", exc_info=e)
            return self._error(method_id, "RUNTIME_ERROR", f"{type(e).__name__}: {e}")
        return self._error(method_id, "METHOD_UNIMPLEMENTED", "Method is declared but not implemented.")
