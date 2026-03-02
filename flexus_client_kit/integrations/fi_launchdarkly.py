import json
import logging
import os
from typing import Any, Dict

import httpx

logger = logging.getLogger("launchdarkly")

PROVIDER_NAME = "launchdarkly"
METHOD_IDS = [
    "launchdarkly.flags.get.v1",
    "launchdarkly.flags.patch.v1",
]

_BASE_URL = "https://app.launchdarkly.com/api/v2"


class IntegrationLaunchdarkly:
    async def called_by_model(self, toolcall, model_produced_args):
        args = model_produced_args or {}
        op = str(args.get("op", "help")).strip()
        if op == "help":
            return (f"provider={PROVIDER_NAME}\nop=help | status | list_methods | call\nmethods: {', '.join(METHOD_IDS)}")
        if op == "status":
            key = os.environ.get("LAUNCHDARKLY_API_KEY", "")
            proj = os.environ.get("LAUNCHDARKLY_PROJECT_KEY", "")
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "status": "available" if (key and proj) else "no_credentials", "method_count": len(METHOD_IDS)}, indent=2, ensure_ascii=False)
        if op == "list_methods":
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_ids": METHOD_IDS}, indent=2, ensure_ascii=False)
        if op != "call":
            return "Error: unknown op. Use help/status/list_methods/call."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_IDS:
            return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)
        return await self._dispatch(method_id, call_args)

    def _headers(self):
        key = os.environ.get("LAUNCHDARKLY_API_KEY", "")
        return {"Authorization": key, "Content-Type": "application/json"}

    def _project_key(self):
        return os.environ.get("LAUNCHDARKLY_PROJECT_KEY", "default")

    def _client(self):
        return httpx.AsyncClient(base_url=_BASE_URL, headers=self._headers(), timeout=30)

    async def _dispatch(self, method_id, call_args):
        if method_id == "launchdarkly.flags.get.v1":
            return await self._flags_get(call_args)
        if method_id == "launchdarkly.flags.patch.v1":
            return await self._flags_patch(call_args)

    async def _flags_get(self, call_args):
        flag_key = str(call_args.get("flag_key", "")).strip()
        if not flag_key:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "flag_key"}, indent=2, ensure_ascii=False)

        env = str(call_args.get("env", "")).strip()
        project_key = self._project_key()

        params: Dict[str, Any] = {}
        if env:
            params["env"] = env

        async with self._client() as client:
            resp = await client.get(f"/flags/{project_key}/{flag_key}", params=params)

        if resp.status_code != 200:
            logger.info("launchdarkly flags get failed: status=%d body=%s", resp.status_code, resp.text[:500])
            return json.dumps({"ok": False, "error_code": "API_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)

        data = resp.json()
        environments = data.get("environments") or {}

        on_value = None
        if env and env in environments:
            on_value = environments[env].get("on")
        elif environments:
            first_env = next(iter(environments.values()))
            on_value = first_env.get("on")

        return json.dumps({
            "ok": True,
            "key": data.get("key"),
            "name": data.get("name"),
            "kind": data.get("kind"),
            "on": on_value,
            "variations": data.get("variations"),
            "environments": environments,
            "tags": data.get("tags"),
            "created_date": data.get("creationDate"),
        }, indent=2, ensure_ascii=False)

    async def _flags_patch(self, call_args):
        flag_key = str(call_args.get("flag_key", "")).strip()
        if not flag_key:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "flag_key"}, indent=2, ensure_ascii=False)

        patch_operations = call_args.get("patch_operations")
        if not patch_operations or not isinstance(patch_operations, list):
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "patch_operations"}, indent=2, ensure_ascii=False)

        project_key = self._project_key()

        async with self._client() as client:
            resp = await client.patch(f"/flags/{project_key}/{flag_key}", json=patch_operations)

        if resp.status_code not in (200, 201):
            logger.info("launchdarkly flags patch failed: status=%d body=%s", resp.status_code, resp.text[:500])
            return json.dumps({"ok": False, "error_code": "API_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)

        data = resp.json()
        return json.dumps({"ok": True, "key": data.get("key"), "name": data.get("name")}, indent=2, ensure_ascii=False)
