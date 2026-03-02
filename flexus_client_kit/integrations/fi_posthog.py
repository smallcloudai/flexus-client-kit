import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("posthog")

PROVIDER_NAME = "posthog"
METHOD_IDS = [
    "posthog.insights.trend.query.v1",
    "posthog.insights.funnel.query.v1",
    "posthog.insights.retention.query.v1",
]


class IntegrationPosthog:
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
            key = os.environ.get("POSTHOG_API_KEY", "")
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "status": "available" if key else "no_credentials", "method_count": len(METHOD_IDS)}, indent=2, ensure_ascii=False)
        if op == "list_methods":
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_ids": METHOD_IDS}, indent=2, ensure_ascii=False)
        if op != "call":
            return "Error: unknown op."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required."
        if method_id not in METHOD_IDS:
            return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)
        return await self._dispatch(method_id, call_args)

    def _base_url(self) -> str:
        host = os.environ.get("POSTHOG_HOST", "https://app.posthog.com")
        project_id = os.environ.get("POSTHOG_PROJECT_ID", "")
        return f"{host}/api/projects/{project_id}"

    def _headers(self) -> Dict[str, str]:
        key = os.environ.get("POSTHOG_API_KEY", "")
        return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    async def _dispatch(self, method_id: str, call_args: Dict[str, Any]) -> str:
        if method_id == "posthog.insights.trend.query.v1":
            return await self._trend_query(call_args)
        if method_id == "posthog.insights.funnel.query.v1":
            return await self._funnel_query(call_args)
        if method_id == "posthog.insights.retention.query.v1":
            return await self._retention_query(call_args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _trend_query(self, call_args: Dict[str, Any]) -> str:
        events = call_args.get("events")
        if not events:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "events"}, indent=2, ensure_ascii=False)
        body: Dict[str, Any] = {"events": events, "insight": "TRENDS"}
        if call_args.get("date_from") is not None:
            body["date_from"] = call_args["date_from"]
        if call_args.get("date_to") is not None:
            body["date_to"] = call_args["date_to"]
        if call_args.get("interval") is not None:
            body["interval"] = call_args["interval"]
        if call_args.get("breakdown") is not None:
            body["breakdown"] = call_args["breakdown"]
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(f"{self._base_url()}/insights/trend/", headers=self._headers(), json=body)
                resp.raise_for_status()
                data = resp.json()
                series = [
                    {"label": item.get("label"), "data": item.get("data"), "count": item.get("count")}
                    for item in (data.get("result") or [])
                ]
                normalized = {
                    "series": series,
                    "date_from": data.get("last_refresh"),
                    "date_to": call_args.get("date_to"),
                }
                return json.dumps({"ok": True, "result": normalized}, indent=2, ensure_ascii=False)
            except httpx.HTTPStatusError as e:
                logger.info("posthog trend query HTTP error: %s", e)
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "status_code": e.response.status_code, "body": e.response.text}, indent=2, ensure_ascii=False)
            except httpx.RequestError as e:
                logger.info("posthog trend query request error: %s", e)
                return json.dumps({"ok": False, "error_code": "REQUEST_ERROR", "error": str(e)}, indent=2, ensure_ascii=False)

    async def _funnel_query(self, call_args: Dict[str, Any]) -> str:
        events = call_args.get("events")
        if not events:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "events"}, indent=2, ensure_ascii=False)
        body: Dict[str, Any] = {
            "events": events,
            "insight": "FUNNELS",
            "funnel_window_days": call_args.get("funnel_window_days", 14),
        }
        if call_args.get("date_from") is not None:
            body["date_from"] = call_args["date_from"]
        if call_args.get("date_to") is not None:
            body["date_to"] = call_args["date_to"]
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(f"{self._base_url()}/insights/funnel/", headers=self._headers(), json=body)
                resp.raise_for_status()
                data = resp.json()
                result = data.get("result") or []
                if isinstance(result, list) and result and isinstance(result[0], list):
                    result = result[0]
                steps = [
                    {
                        "action_id": item.get("action_id"),
                        "name": item.get("name"),
                        "count": item.get("count"),
                        "conversion_rate": item.get("conversion_rate"),
                    }
                    for item in result
                ]
                return json.dumps({"ok": True, "result": {"steps": steps}}, indent=2, ensure_ascii=False)
            except httpx.HTTPStatusError as e:
                logger.info("posthog funnel query HTTP error: %s", e)
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "status_code": e.response.status_code, "body": e.response.text}, indent=2, ensure_ascii=False)
            except httpx.RequestError as e:
                logger.info("posthog funnel query request error: %s", e)
                return json.dumps({"ok": False, "error_code": "REQUEST_ERROR", "error": str(e)}, indent=2, ensure_ascii=False)

    async def _retention_query(self, call_args: Dict[str, Any]) -> str:
        date_from = call_args.get("date_from")
        target_event = call_args.get("target_event")
        returning_event = call_args.get("returning_event")
        if not date_from:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "date_from"}, indent=2, ensure_ascii=False)
        if not target_event:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "target_event"}, indent=2, ensure_ascii=False)
        if not returning_event:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "returning_event"}, indent=2, ensure_ascii=False)
        body: Dict[str, Any] = {
            "target_event": {"id": str(target_event), "type": "events"},
            "returning_event": {"id": str(returning_event), "type": "events"},
            "retention_type": call_args.get("retention_type", "retention_first_time"),
            "period": call_args.get("period", "Week"),
            "total_intervals": call_args.get("total_intervals", 11),
            "date_from": date_from,
        }
        if call_args.get("date_to") is not None:
            body["date_to"] = call_args["date_to"]
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(f"{self._base_url()}/insights/retention/", headers=self._headers(), json=body)
                resp.raise_for_status()
                data = resp.json()
                raw_result = data.get("result") or []
                cohorts = [
                    {
                        "date": item.get("date"),
                        "label": item.get("label"),
                        "values": item.get("values", []),
                    }
                    for item in raw_result
                ]
                normalized = {
                    "period": body.get("period", "Week"),
                    "total_intervals": body.get("total_intervals", 11),
                    "cohorts": cohorts,
                }
                return json.dumps({"ok": True, "result": normalized}, indent=2, ensure_ascii=False)
            except httpx.HTTPStatusError as e:
                logger.info("posthog retention query HTTP error: %s", e)
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "status_code": e.response.status_code, "body": e.response.text}, indent=2, ensure_ascii=False)
            except httpx.RequestError as e:
                logger.info("posthog retention query request error: %s", e)
                return json.dumps({"ok": False, "error_code": "REQUEST_ERROR", "error": str(e)}, indent=2, ensure_ascii=False)
