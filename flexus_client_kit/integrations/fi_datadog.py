import json
import logging
import os
from typing import Any, Dict, List

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("datadog")

PROVIDER_NAME = "datadog"
METHOD_IDS = [
    "datadog.metrics.timeseries.query.v1",
    "datadog.metrics.query.v1",
]


def _base_url() -> str:
    site = os.environ.get("DD_SITE", "datadoghq.com")
    return f"https://api.{site}/api/v1"


class IntegrationDatadog:
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
            api_key = os.environ.get("DD_API_KEY", "")
            app_key = os.environ.get("DD_APP_KEY", "")
            status = "available" if (api_key and app_key) else "no_credentials"
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
        if method_id in ("datadog.metrics.timeseries.query.v1", "datadog.metrics.query.v1"):
            return await self._timeseries_query(call_args)
        return json.dumps(
            {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
            indent=2,
            ensure_ascii=False,
        )

    async def _timeseries_query(self, call_args: Dict[str, Any]) -> str:
        query = str(call_args.get("query", "")).strip()
        if not query:
            return "Error: query required."
        from_ts = call_args.get("from_ts")
        to_ts = call_args.get("to_ts")
        if from_ts is None or to_ts is None:
            return "Error: from_ts and to_ts required."
        try:
            from_ts = int(from_ts)
            to_ts = int(to_ts)
        except (TypeError, ValueError):
            return "Error: from_ts and to_ts must be integers."
        api_key = os.environ.get("DD_API_KEY", "")
        app_key = os.environ.get("DD_APP_KEY", "")
        if not api_key or not app_key:
            return json.dumps(
                {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        url = f"{_base_url()}/query"
        params = {"from": from_ts, "to": to_ts, "query": query}
        headers = {
            "DD-API-KEY": api_key,
            "DD-APPLICATION-KEY": app_key,
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, params=params, headers=headers, timeout=30.0
                )
                response.raise_for_status()
        except httpx.TimeoutException as e:
            logger.info("Datadog timeout query=%s: %s", query, e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "query": query},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPStatusError as e:
            logger.info(
                "Datadog HTTP error query=%s status=%s: %s",
                query,
                e.response.status_code,
                e,
            )
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "HTTP_ERROR",
                    "query": query,
                    "status_code": e.response.status_code,
                },
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("Datadog HTTP error query=%s: %s", query, e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "query": query},
                indent=2,
                ensure_ascii=False,
            )
        try:
            payload = response.json()
        except ValueError as e:
            logger.info("Datadog JSON decode error query=%s: %s", query, e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "query": query},
                indent=2,
                ensure_ascii=False,
            )
        status = payload.get("status", "")
        if status != "ok":
            err_msg = payload.get("error", "unknown")
            logger.info("Datadog query error query=%s status=%s: %s", query, status, err_msg)
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "QUERY_ERROR",
                    "query": query,
                    "status": status,
                    "error": err_msg,
                },
                indent=2,
                ensure_ascii=False,
            )
        series_raw = payload.get("series") or []
        normalized: List[Dict[str, Any]] = []
        for s in series_raw:
            metric = s.get("metric", "")
            scope = s.get("scope", "")
            pointlist = s.get("pointlist") or []
            unit = s.get("unit")
            points = [{"ts": p[0], "value": p[1]} for p in pointlist if len(p) >= 2]
            normalized.append(
                {"metric": metric, "scope": scope, "points": points, "unit": unit}
            )
        return json.dumps(
            {"ok": True, "query": query, "series": normalized},
            indent=2,
            ensure_ascii=False,
        )
