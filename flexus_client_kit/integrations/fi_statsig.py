import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("statsig")

PROVIDER_NAME = "statsig"
METHOD_IDS = [
    "statsig.experiments.create.v1",
    "statsig.experiments.update.v1",
]

BASE_URL = "https://statsigapi.net/console/v1"


class IntegrationStatsig:
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
            key = os.environ.get("STATSIG_CONSOLE_API_KEY", "")
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

    async def _dispatch(self, method_id: str, call_args: Dict[str, Any]) -> str:
        key = os.environ.get("STATSIG_CONSOLE_API_KEY", "")
        headers = {"statsig-api-key": key, "Content-Type": "application/json"}
        if method_id == "statsig.experiments.create.v1":
            return await self._experiments_create(headers, call_args)
        if method_id == "statsig.experiments.update.v1":
            return await self._experiments_update(headers, call_args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _experiments_create(self, headers: Dict[str, str], call_args: Dict[str, Any]) -> str:
        name = call_args.get("name")
        if not name:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "name"}, indent=2, ensure_ascii=False)
        body: Dict[str, Any] = {
            "name": name,
            "idType": call_args.get("id_type", "userID"),
            "allocation": call_args.get("allocation", 0.1),
        }
        if call_args.get("description") is not None:
            body["description"] = call_args["description"]
        if call_args.get("hypothesis") is not None:
            body["hypothesis"] = call_args["hypothesis"]
        if call_args.get("primary_metric_tags") is not None:
            body["primaryMetricTags"] = call_args["primary_metric_tags"]
        if call_args.get("duration") is not None:
            body["duration"] = call_args["duration"]
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(f"{BASE_URL}/experiments", headers=headers, json=body)
                resp.raise_for_status()
                return json.dumps({"ok": True, "result": resp.json()}, indent=2, ensure_ascii=False)
            except httpx.HTTPStatusError as e:
                logger.info("statsig create experiment HTTP error: %s", e)
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "status_code": e.response.status_code, "body": e.response.text}, indent=2, ensure_ascii=False)
            except httpx.RequestError as e:
                logger.info("statsig create experiment request error: %s", e)
                return json.dumps({"ok": False, "error_code": "REQUEST_ERROR", "error": str(e)}, indent=2, ensure_ascii=False)

    async def _experiments_update(self, headers: Dict[str, str], call_args: Dict[str, Any]) -> str:
        experiment_id = call_args.get("experiment_id")
        if not experiment_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "experiment_id"}, indent=2, ensure_ascii=False)
        body: Dict[str, Any] = {}
        if call_args.get("status") is not None:
            body["status"] = call_args["status"]
        if call_args.get("allocation") is not None:
            body["allocation"] = call_args["allocation"]
        if call_args.get("description") is not None:
            body["description"] = call_args["description"]
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.patch(f"{BASE_URL}/experiments/{experiment_id}", headers=headers, json=body)
                resp.raise_for_status()
                return json.dumps({"ok": True, "result": resp.json()}, indent=2, ensure_ascii=False)
            except httpx.HTTPStatusError as e:
                logger.info("statsig update experiment HTTP error: %s", e)
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "status_code": e.response.status_code, "body": e.response.text}, indent=2, ensure_ascii=False)
            except httpx.RequestError as e:
                logger.info("statsig update experiment request error: %s", e)
                return json.dumps({"ok": False, "error_code": "REQUEST_ERROR", "error": str(e)}, indent=2, ensure_ascii=False)
