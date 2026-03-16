import json
import logging
import os
from typing import Any, Dict, List

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("recurly")

PROVIDER_NAME = "recurly"
API_BASE = "https://v3.recurly.com"
METHOD_IDS = [
    "recurly.subscriptions.list.v1",
]
_TIMEOUT = 30.0


class IntegrationRecurly:
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
            api_key = os.environ.get("RECURLY_API_KEY", "")
            if os.environ.get("NO_CREDENTIALS"):
                status = "no_credentials"
            else:
                status = "available" if api_key else "no_credentials"
            return json.dumps(
                {
                    "ok": True,
                    "provider": PROVIDER_NAME,
                    "status": status,
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
            return "Error: unknown op. Use help/status/list_methods/call."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_IDS:
            return json.dumps(
                {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
                indent=2,
                ensure_ascii=False,
            )
        if method_id == "recurly.subscriptions.list.v1":
            return await self._subscriptions_list(call_args)
        return json.dumps(
            {"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id},
            indent=2,
            ensure_ascii=False,
        )

    async def _subscriptions_list(self, call_args: Dict[str, Any]) -> str:
        api_key = os.environ.get("RECURLY_API_KEY", "")
        if not api_key or os.environ.get("NO_CREDENTIALS"):
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "NO_CREDENTIALS",
                    "provider": PROVIDER_NAME,
                    "message": "RECURLY_API_KEY env var not set",
                },
                indent=2,
                ensure_ascii=False,
            )
        params: Dict[str, Any] = {}
        state = str(call_args.get("state", "")).strip()
        if state:
            params["state"] = state
        customer_email = str(call_args.get("customer_email", "")).strip()
        if customer_email:
            params["email"] = customer_email
        limit = call_args.get("limit", 20)
        try:
            limit = min(max(int(limit), 1), 200)
        except (TypeError, ValueError):
            limit = 20
        params["limit"] = limit
        begin_time = str(call_args.get("begin_time", "")).strip()
        if begin_time:
            params["begin_time"] = begin_time
        end_time = str(call_args.get("end_time", "")).strip()
        if end_time:
            params["end_time"] = end_time
        url = f"{API_BASE}/subscriptions"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.recurly.v2021-02-25+json",
        }
        try:
            async with httpx.AsyncClient(
                auth=httpx.BasicAuth(username=api_key, password=""),
                timeout=_TIMEOUT,
            ) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
        except httpx.TimeoutException as e:
            logger.info("Recurly subscriptions timeout: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPStatusError as e:
            logger.info("Recurly HTTP error status=%s: %s", e.response.status_code, e)
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
            logger.info("Recurly HTTP error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        try:
            payload = response.json()
        except json.JSONDecodeError as e:
            logger.info("Recurly JSON decode error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        try:
            data = payload.get("data", [])
            has_more = payload.get("has_more", False)
            normalized: List[Dict[str, Any]] = []
            for item in data:
                normalized.append(self._normalize_subscription(item))
        except (KeyError, ValueError) as e:
            logger.info("Recurly response parse error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        return json.dumps(
            {"ok": True, "data": normalized, "has_more": has_more},
            indent=2,
            ensure_ascii=False,
        )

    def _normalize_subscription(self, item: Dict[str, Any]) -> Dict[str, Any]:
        plan = item.get("plan") or {}
        account = item.get("account") or {}
        return {
            "id": item.get("id"),
            "state": item.get("state"),
            "plan_code": plan.get("code"),
            "account_code": account.get("code"),
            "account_email": account.get("email"),
            "current_period_started_at": item.get("current_period_started_at"),
            "current_period_ends_at": item.get("current_period_ends_at"),
            "unit_amount": item.get("unit_amount"),
            "currency": item.get("currency"),
            "quantity": item.get("quantity"),
        }
