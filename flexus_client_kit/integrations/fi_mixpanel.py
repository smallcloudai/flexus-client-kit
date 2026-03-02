import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("mixpanel")

PROVIDER_NAME = "mixpanel"
METHOD_IDS = [
    "mixpanel.retention.query.v1",
    "mixpanel.frequency.query.v1",
    "mixpanel.funnels.query.v1",
]

BASE_URL = "https://mixpanel.com/api/2.0"


class IntegrationMixpanel:
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
            key = os.environ.get("MIXPANEL_PROJECT_SECRET", "")
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

    def _auth(self):
        return (os.environ.get("MIXPANEL_PROJECT_SECRET", ""), "")

    def _project_id(self) -> str:
        return os.environ.get("MIXPANEL_PROJECT_ID", "")

    async def _dispatch(self, method_id: str, call_args: Dict[str, Any]) -> str:
        if method_id == "mixpanel.retention.query.v1":
            return await self._retention_query(call_args)
        if method_id == "mixpanel.frequency.query.v1":
            return await self._frequency_query(call_args)
        if method_id == "mixpanel.funnels.query.v1":
            return await self._funnels_query(call_args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _retention_query(self, call_args: Dict[str, Any]) -> str:
        event = call_args.get("event")
        from_date = call_args.get("from_date")
        to_date = call_args.get("to_date")
        if not event:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "event"}, indent=2, ensure_ascii=False)
        if not from_date:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "from_date"}, indent=2, ensure_ascii=False)
        if not to_date:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "to_date"}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {
            "project_id": self._project_id(),
            "event": event,
            "from_date": from_date,
            "to_date": to_date,
            "interval": call_args.get("interval", 1),
            "unit": call_args.get("unit", "day"),
        }
        if call_args.get("born_event") is not None:
            params["born_event"] = call_args["born_event"]
        if call_args.get("born_where") is not None:
            params["born_where"] = call_args["born_where"]
        if call_args.get("where") is not None:
            params["where"] = call_args["where"]
        async with httpx.AsyncClient(auth=self._auth()) as client:
            try:
                resp = await client.get(f"{BASE_URL}/retention/", params=params)
                resp.raise_for_status()
                return json.dumps({"ok": True, "result": resp.json()}, indent=2, ensure_ascii=False)
            except httpx.HTTPStatusError as e:
                logger.info("mixpanel retention query HTTP error: %s", e)
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "status_code": e.response.status_code, "body": e.response.text}, indent=2, ensure_ascii=False)
            except httpx.RequestError as e:
                logger.info("mixpanel retention query request error: %s", e)
                return json.dumps({"ok": False, "error_code": "REQUEST_ERROR", "error": str(e)}, indent=2, ensure_ascii=False)

    async def _frequency_query(self, call_args: Dict[str, Any]) -> str:
        event = call_args.get("event")
        from_date = call_args.get("from_date")
        to_date = call_args.get("to_date")
        if not event:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "event"}, indent=2, ensure_ascii=False)
        if not from_date:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "from_date"}, indent=2, ensure_ascii=False)
        if not to_date:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "to_date"}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {
            "project_id": self._project_id(),
            "event": event,
            "from_date": from_date,
            "to_date": to_date,
            "unit": call_args.get("unit", "day"),
        }
        if call_args.get("on") is not None:
            params["on"] = call_args["on"]
        if call_args.get("where") is not None:
            params["where"] = call_args["where"]
        if call_args.get("type") is not None:
            params["type"] = call_args["type"]
        async with httpx.AsyncClient(auth=self._auth()) as client:
            try:
                resp = await client.get(f"{BASE_URL}/segmentation/", params=params)
                resp.raise_for_status()
                return json.dumps({"ok": True, "result": resp.json()}, indent=2, ensure_ascii=False)
            except httpx.HTTPStatusError as e:
                logger.info("mixpanel frequency query HTTP error: %s", e)
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "status_code": e.response.status_code, "body": e.response.text}, indent=2, ensure_ascii=False)
            except httpx.RequestError as e:
                logger.info("mixpanel frequency query request error: %s", e)
                return json.dumps({"ok": False, "error_code": "REQUEST_ERROR", "error": str(e)}, indent=2, ensure_ascii=False)

    def _normalize_funnels_response(
        self,
        raw: Dict[str, Any],
        funnel_id: int,
        from_date: str,
        to_date: str,
    ) -> Dict[str, Any]:
        steps = []
        data_steps = raw.get("data", {}).get("steps") or raw.get("steps") or []
        for s in data_steps:
            steps.append({
                "count": s.get("count", s.get("value", 0)),
                "step_label": s.get("step_label", s.get("label", "")),
                "goal": s.get("goal", ""),
                "overall_conv_ratio": s.get("overall_conv_ratio", s.get("conversion_rate")),
            })
        analysis_data = raw.get("data", {}).get("analysis") or raw.get("analysis") or {}
        analysis = {
            "completion": analysis_data.get("completion"),
            "starting_amount": analysis_data.get("starting_amount"),
        }
        return {
            "funnel_id": funnel_id,
            "from_date": from_date,
            "to_date": to_date,
            "steps": steps,
            "analysis": analysis,
        }

    async def _funnels_query(self, call_args: Dict[str, Any]) -> str:
        funnel_id = call_args.get("funnel_id")
        from_date = call_args.get("from_date")
        to_date = call_args.get("to_date")
        if funnel_id is None:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "funnel_id"}, indent=2, ensure_ascii=False)
        try:
            funnel_id = int(funnel_id)
        except (TypeError, ValueError):
            return json.dumps({"ok": False, "error_code": "INVALID_ARG", "arg": "funnel_id", "expected": "int"}, indent=2, ensure_ascii=False)
        if not from_date:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "from_date"}, indent=2, ensure_ascii=False)
        if not to_date:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "to_date"}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {
            "project_id": self._project_id(),
            "funnel_id": funnel_id,
            "from_date": from_date,
            "to_date": to_date,
            "unit": call_args.get("unit", "day"),
        }
        if call_args.get("where") is not None:
            params["where"] = call_args["where"]
        if call_args.get("on") is not None:
            params["on"] = call_args["on"]
        if call_args.get("limit") is not None:
            params["limit"] = call_args["limit"]
        async with httpx.AsyncClient(auth=self._auth()) as client:
            try:
                resp = await client.get(f"{BASE_URL}/funnels/", params=params)
                resp.raise_for_status()
                raw = resp.json()
                normalized = self._normalize_funnels_response(raw, funnel_id, from_date, to_date)
                return json.dumps({"ok": True, "result": normalized}, indent=2, ensure_ascii=False)
            except httpx.HTTPStatusError as e:
                logger.info("mixpanel funnels query HTTP error: %s", e)
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "status_code": e.response.status_code, "body": e.response.text}, indent=2, ensure_ascii=False)
            except httpx.RequestError as e:
                logger.info("mixpanel funnels query request error: %s", e)
                return json.dumps({"ok": False, "error_code": "REQUEST_ERROR", "error": str(e)}, indent=2, ensure_ascii=False)
