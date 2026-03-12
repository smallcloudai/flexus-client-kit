import json
import logging
import os
from typing import Any, Dict, Optional

import httpx

from flexus_client_kit import ckit_cloudtool


logger = logging.getLogger("toloka")

PROVIDER_NAME = "toloka"
METHOD_IDS = [
    "toloka.projects.list.v1",
    "toloka.projects.create.v1",
    "toloka.pools.create.v1",
    "toloka.pools.open.v1",
    "toloka.tasks.batch_create.v1",
    "toloka.assignments.list.v1",
    "toloka.assignments.approve.v1",
    "toloka.assignments.reject.v1",
    "toloka.webhook_subscriptions.list.v1",
    "toloka.webhook_subscriptions.create.v1",
]

_TIMEOUT = 30.0

# Toloka uses ApiKey authentication.
# Required values:
# - TOLOKA_API_KEY
# Optional values:
# - TOLOKA_ENV=sandbox to route to the sandbox API host
# Toloka sandbox should be used during questionnaire and anti-fraud dry runs.
TOLOKA_SETUP_SCHEMA: list[dict[str, Any]] = []


class IntegrationToloka:
    def __init__(self, rcx=None) -> None:
        self.rcx = rcx

    def _api_key(self) -> str:
        return str(os.environ.get("TOLOKA_API_KEY", "")).strip()

    def _base_url(self) -> str:
        if str(os.environ.get("TOLOKA_ENV", "")).strip().lower() == "sandbox":
            return "https://sandbox.toloka.dev/api/v1"
        return "https://toloka.dev/api/v1"

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"ApiKey {self._api_key()}",
            "Content-Type": "application/json",
        }

    def _status(self) -> str:
        env = str(os.environ.get("TOLOKA_ENV", "production")).strip().lower() or "production"
        return json.dumps(
            {
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "ready" if self._api_key() else "missing_credentials",
                "method_count": len(METHOD_IDS),
                "auth_type": "api_key_header",
                "required_env": ["TOLOKA_API_KEY"],
                "optional_env": ["TOLOKA_ENV"],
                "environment": env,
                "products": ["Projects", "Pools", "Tasks", "Assignments", "Webhook subscriptions"],
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
            "- Toloka is useful for budget-sensitive validation, screeners, and quick survey operations.\n"
            "- Use sandbox first to validate pool setup, filters, and review rules.\n"
            "- Assignments should be adjudicated explicitly because quality-control rules differ by project.\n"
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
            return self._error(method_id, "METHOD_UNKNOWN", "Unknown Toloka method.")
        if not self._api_key():
            return self._error(method_id, "AUTH_MISSING", "Set TOLOKA_API_KEY in the runtime environment.")
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
            return self._error(method_id, "TIMEOUT", "Toloka request timed out.")
        except httpx.HTTPError as e:
            logger.error("toloka request failed", exc_info=e)
            return self._error(method_id, "HTTP_ERROR", f"{type(e).__name__}: {e}")
        if response.status_code >= 400:
            detail: Any = response.text[:1000]
            try:
                detail = response.json()
            except json.JSONDecodeError:
                pass
            logger.info("toloka provider error method=%s status=%s body=%s", method_id, response.status_code, response.text[:300])
            return self._error(method_id, "PROVIDER_ERROR", "Toloka returned an error.", http_status=response.status_code, detail=detail)
        if not response.text.strip():
            return self._result(method_id, {})
        try:
            return self._result(method_id, response.json())
        except json.JSONDecodeError:
            return self._result(method_id, response.text)

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        if method_id == "toloka.projects.list.v1":
            params: Dict[str, Any] = {}
            for key in ["id_gt", "id_lte", "status"]:
                value = args.get(key)
                if value not in (None, ""):
                    params[key] = value
            return await self._request(method_id, "GET", "/projects", params=params)
        if method_id == "toloka.projects.create.v1":
            return await self._request(method_id, "POST", "/projects", body=args)
        if method_id == "toloka.pools.create.v1":
            return await self._request(method_id, "POST", "/pools", body=args)
        if method_id == "toloka.pools.open.v1":
            pool_id = str(args.get("pool_id", "")).strip()
            if not pool_id:
                return self._error(method_id, "INVALID_ARGS", "pool_id is required.")
            return await self._request(method_id, "PATCH", f"/pools/{pool_id}/open", body={})
        if method_id == "toloka.tasks.batch_create.v1":
            tasks = args.get("tasks")
            if not isinstance(tasks, list) or not tasks:
                return self._error(method_id, "INVALID_ARGS", "tasks must be a non-empty list.")
            body: Dict[str, Any] = {"tasks": tasks}
            pool_id = args.get("pool_id")
            if pool_id not in (None, ""):
                body["pool_id"] = pool_id
            allow_defaults = args.get("allow_defaults")
            if allow_defaults is not None:
                body["allow_defaults"] = bool(allow_defaults)
            return await self._request(method_id, "POST", "/tasks", body=body)
        if method_id == "toloka.assignments.list.v1":
            params = {}
            for key in ["pool_id", "status", "limit", "sort"]:
                value = args.get(key)
                if value not in (None, ""):
                    params[key] = value
            return await self._request(method_id, "GET", "/assignments", params=params)
        if method_id == "toloka.assignments.approve.v1":
            assignment_id = str(args.get("assignment_id", "")).strip()
            if not assignment_id:
                return self._error(method_id, "INVALID_ARGS", "assignment_id is required.")
            body = {"public_comment": str(args.get("public_comment", "")).strip()}
            return await self._request(method_id, "PATCH", f"/assignments/{assignment_id}/approve", body=body)
        if method_id == "toloka.assignments.reject.v1":
            assignment_id = str(args.get("assignment_id", "")).strip()
            if not assignment_id:
                return self._error(method_id, "INVALID_ARGS", "assignment_id is required.")
            body = {"public_comment": str(args.get("public_comment", "")).strip()}
            return await self._request(method_id, "PATCH", f"/assignments/{assignment_id}/reject", body=body)
        if method_id == "toloka.webhook_subscriptions.list.v1":
            return await self._request(method_id, "GET", "/webhook-subscriptions")
        if method_id == "toloka.webhook_subscriptions.create.v1":
            event_type = str(args.get("event_type", "")).strip()
            webhook_url = str(args.get("webhook_url", "")).strip()
            if not event_type or not webhook_url:
                return self._error(method_id, "INVALID_ARGS", "event_type and webhook_url are required.")
            return await self._request(method_id, "POST", "/webhook-subscriptions", body={"event_type": event_type, "webhook_url": webhook_url})
        return self._error(method_id, "METHOD_UNIMPLEMENTED", "Method is declared but not implemented.")
