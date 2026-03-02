import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("amplitude")

PROVIDER_NAME = "amplitude"
API_BASE = "https://amplitude.com/api/2"
METHOD_IDS = [
    "amplitude.dashboardrest.chart.get.v1",
]


class IntegrationAmplitude:
    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Dict[str, Any],
    ) -> str:
        args = model_produced_args or {}
        op = str(args.get("op", "help")).strip()
        if op == "help":
            return f"provider={PROVIDER_NAME}\nop=help | status | list_methods | call\nmethods: {', '.join(METHOD_IDS)}"
        if op == "status":
            key = os.environ.get("AMPLITUDE_API_KEY", "")
            return json.dumps(
                {
                    "ok": True,
                    "provider": PROVIDER_NAME,
                    "status": "available" if key else "no_credentials",
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
        if method_id == "amplitude.dashboardrest.chart.get.v1":
            return await self._chart_get(call_args)
        return json.dumps(
            {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
            indent=2,
            ensure_ascii=False,
        )

    async def _chart_get(self, call_args: Dict[str, Any]) -> str:
        chart_id = str(call_args.get("chart_id", "")).strip()
        if not chart_id:
            return "Error: chart_id required."
        api_key = os.environ.get("AMPLITUDE_API_KEY", "")
        secret_key = os.environ.get("AMPLITUDE_SECRET_KEY", "")
        if not api_key or not secret_key:
            return json.dumps(
                {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        params: Dict[str, str] = {}
        start = str(call_args.get("start", "")).strip()
        end = str(call_args.get("end", "")).strip()
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        url = f"{API_BASE}/chart/{chart_id}"
        try:
            async with httpx.AsyncClient(auth=(api_key, secret_key)) as client:
                response = await client.get(url, params=params, timeout=30.0)
                response.raise_for_status()
        except httpx.TimeoutException as e:
            logger.info("Amplitude timeout chart_id=%s: %s", chart_id, e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "chart_id": chart_id},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPStatusError as e:
            logger.info("Amplitude HTTP error chart_id=%s status=%s: %s", chart_id, e.response.status_code, e)
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "HTTP_ERROR",
                    "chart_id": chart_id,
                    "status_code": e.response.status_code,
                },
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("Amplitude HTTP error chart_id=%s: %s", chart_id, e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "chart_id": chart_id},
                indent=2,
                ensure_ascii=False,
            )
        try:
            payload = response.json()
        except json.JSONDecodeError as e:
            logger.info("Amplitude JSON decode error chart_id=%s: %s", chart_id, e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "chart_id": chart_id},
                indent=2,
                ensure_ascii=False,
            )
        try:
            data = payload["data"]
            title = data.get("title", "")
            series = data.get("series") or data.get("seriesLabels") or []
            x_values = data.get("xValues") or []
        except KeyError as e:
            logger.info("Amplitude response missing key chart_id=%s: %s", chart_id, e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "chart_id": chart_id},
                indent=2,
                ensure_ascii=False,
            )
        return json.dumps(
            {
                "ok": True,
                "chart_id": chart_id,
                "title": title,
                "series": series,
                "xValues": x_values,
            },
            indent=2,
            ensure_ascii=False,
        )
