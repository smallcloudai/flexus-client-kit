import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("optimizely")

PROVIDER_NAME = "optimizely"
METHOD_IDS = [
    "optimizely.experiments.create.v1",
    "optimizely.experiments.get.v1",
]

BASE_URL = "https://api.optimizely.com/v2"


class IntegrationOptimizely:
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
            key = os.environ.get("OPTIMIZELY_TOKEN", "")
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
        token = os.environ.get("OPTIMIZELY_TOKEN", "")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        if method_id == "optimizely.experiments.create.v1":
            return await self._experiments_create(headers, call_args)
        if method_id == "optimizely.experiments.get.v1":
            return await self._experiments_get(headers, call_args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _experiments_create(self, headers: Dict[str, str], call_args: Dict[str, Any]) -> str:
        name = call_args.get("name")
        if not name:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "name"}, indent=2, ensure_ascii=False)
        project_id = call_args.get("project_id")
        if project_id is None:
            env_pid = os.environ.get("OPTIMIZELY_PROJECT_ID", "")
            if env_pid:
                project_id = int(env_pid)
        if project_id is None:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "project_id"}, indent=2, ensure_ascii=False)
        body: Dict[str, Any] = {
            "project_id": project_id,
            "name": name,
            "status": call_args.get("status", "paused"),
            "type": call_args.get("type", "a/b"),
        }
        if call_args.get("description") is not None:
            body["description"] = call_args["description"]
        if call_args.get("variations") is not None:
            body["variations"] = call_args["variations"]
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(f"{BASE_URL}/experiments", headers=headers, json=body)
                resp.raise_for_status()
                return json.dumps({"ok": True, "result": resp.json()}, indent=2, ensure_ascii=False)
            except httpx.HTTPStatusError as e:
                logger.info("optimizely create experiment HTTP error: %s", e)
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "status_code": e.response.status_code, "body": e.response.text}, indent=2, ensure_ascii=False)
            except httpx.RequestError as e:
                logger.info("optimizely create experiment request error: %s", e)
                return json.dumps({"ok": False, "error_code": "REQUEST_ERROR", "error": str(e)}, indent=2, ensure_ascii=False)

    async def _experiments_get(self, headers: Dict[str, str], call_args: Dict[str, Any]) -> str:
        experiment_id = call_args.get("experiment_id")
        if not experiment_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "experiment_id"}, indent=2, ensure_ascii=False)
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(f"{BASE_URL}/experiments/{experiment_id}", headers=headers)
                resp.raise_for_status()
                data = resp.json()
                normalized = {
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "status": data.get("status"),
                    "type": data.get("type"),
                    "project_id": data.get("project_id"),
                    "created": data.get("created"),
                    "last_modified": data.get("last_modified"),
                    "variations": data.get("variations"),
                }
                return json.dumps({"ok": True, "result": normalized}, indent=2, ensure_ascii=False)
            except httpx.HTTPStatusError as e:
                logger.info("optimizely get experiment HTTP error: %s", e)
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "status_code": e.response.status_code, "body": e.response.text}, indent=2, ensure_ascii=False)
            except httpx.RequestError as e:
                logger.info("optimizely get experiment request error: %s", e)
                return json.dumps({"ok": False, "error_code": "REQUEST_ERROR", "error": str(e)}, indent=2, ensure_ascii=False)
