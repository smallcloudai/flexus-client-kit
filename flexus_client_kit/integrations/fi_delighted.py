import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("delighted")

PROVIDER_NAME = "delighted"
API_BASE = "https://api.delighted.com/v1"
METHOD_IDS = [
    "delighted.metrics.get.v1",
]
_TIMEOUT = 30.0


class IntegrationDelighted:
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
            api_key = os.environ.get("DELIGHTED_API_KEY", "")
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
        if method_id == "delighted.metrics.get.v1":
            return await self._metrics_get(call_args)
        return json.dumps(
            {"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id},
            indent=2,
            ensure_ascii=False,
        )

    async def _metrics_get(self, call_args: Dict[str, Any]) -> str:
        api_key = os.environ.get("DELIGHTED_API_KEY", "")
        if not api_key or os.environ.get("NO_CREDENTIALS"):
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "NO_CREDENTIALS",
                    "provider": PROVIDER_NAME,
                    "message": "DELIGHTED_API_KEY env var not set",
                },
                indent=2,
                ensure_ascii=False,
            )
        params: Dict[str, Any] = {}
        since = call_args.get("since")
        if since is not None:
            params["since"] = since
        until = call_args.get("until")
        if until is not None:
            params["until"] = until
        trend = str(call_args.get("trend", "")).strip()
        if trend:
            params["trend"] = trend
        token = str(call_args.get("token", "")).strip()
        if token:
            params["token"] = token
        channel = str(call_args.get("channel", "")).strip()
        if channel:
            params["channel"] = channel
        url = f"{API_BASE}/metrics.json"
        headers = {"Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(
                auth=httpx.BasicAuth(username=api_key, password=""),
                timeout=_TIMEOUT,
            ) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
        except httpx.TimeoutException as e:
            logger.info("Delighted metrics timeout: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPStatusError as e:
            logger.info("Delighted HTTP error status=%s: %s", e.response.status_code, e)
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
            logger.info("Delighted HTTP error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        try:
            payload = response.json()
        except json.JSONDecodeError as e:
            logger.info("Delighted JSON decode error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        try:
            normalized = self._normalize_metrics(payload)
        except (KeyError, ValueError) as e:
            logger.info("Delighted response parse error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        return json.dumps(
            {"ok": True, "data": normalized},
            indent=2,
            ensure_ascii=False,
        )

    def _normalize_metrics(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "nps": payload.get("nps"),
            "promoter_count": payload.get("promoter_count"),
            "passive_count": payload.get("passive_count"),
            "detractor_count": payload.get("detractor_count"),
            "survey_request_count": payload.get("survey_request_count"),
            "responded": payload.get("responded") or payload.get("response_count"),
            "percent_promoters": payload.get("percent_promoters") or payload.get("promoter_percent"),
            "percent_passives": payload.get("percent_passives") or payload.get("passive_percent"),
            "percent_detractors": payload.get("percent_detractors") or payload.get("detractor_percent"),
            "average_score": payload.get("average_score"),
        }
