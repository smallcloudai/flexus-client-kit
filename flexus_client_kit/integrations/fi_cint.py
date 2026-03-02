import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("cint")

PROVIDER_NAME = "cint"
METHOD_IDS = [
    "cint.projects.create.v1",
    "cint.projects.feasibility.get.v1",
    "cint.projects.launch.v1",
]

_BASE_URL = "https://api.cint.com/v1"
_API_VERSION = "2025-12-18"


class IntegrationCint:
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
            key = os.environ.get("CINT_API_KEY", "")
            return json.dumps({
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "available" if key else "no_credentials",
                "method_count": len(METHOD_IDS),
            }, indent=2, ensure_ascii=False)
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

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        if method_id == "cint.projects.create.v1":
            return await self._projects_create(args)
        if method_id == "cint.projects.feasibility.get.v1":
            return await self._projects_feasibility_get(args)
        if method_id == "cint.projects.launch.v1":
            return await self._projects_launch(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _auth_headers(self, key: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {key}",
            "Cint-API-Version": _API_VERSION,
            "Content-Type": "application/json",
        }

    async def _projects_create(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("CINT_API_KEY", "")
        if not key:
            return json.dumps({
                "ok": False,
                "error_code": "NO_CREDENTIALS",
                "message": "CINT_API_KEY env var not set. Cint API requires enterprise credentials — contact Cint for API access.",
            }, indent=2, ensure_ascii=False)
        account_id = str(args.get("account_id", "")).strip()
        name = str(args.get("name", "")).strip()
        if not account_id or not name:
            return json.dumps({"ok": False, "error_code": "MISSING_ARGS", "required": ["account_id", "name"]}, indent=2, ensure_ascii=False)
        body: Dict[str, Any] = {"name": name}
        target_completes = args.get("target_completes")
        if target_completes is not None:
            body["target_completes"] = int(target_completes)
        country_code = args.get("country_code")
        if country_code:
            body["country_code"] = str(country_code)
        language_code = args.get("language_code")
        if language_code:
            body["language_code"] = str(language_code)
        category = args.get("category")
        if category:
            body["category"] = str(category)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{_BASE_URL}/demand/accounts/{account_id}/projects",
                    json=body,
                    headers=self._auth_headers(key),
                )
            if resp.status_code not in (200, 201, 202):
                logger.info("cint projects.create http %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json() if resp.text else {}
        except httpx.TimeoutException as e:
            logger.info("cint projects.create timeout: %s", e)
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("cint projects.create http error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            logger.info("cint projects.create json decode error: %s", e)
            return json.dumps({"ok": False, "error_code": "JSON_DECODE_ERROR"}, indent=2, ensure_ascii=False)
        return f"cint.projects.create.v1 ok (202 Accepted — async job)\n\n```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"

    async def _projects_feasibility_get(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("CINT_API_KEY", "")
        if not key:
            return json.dumps({
                "ok": False,
                "error_code": "NO_CREDENTIALS",
                "message": "CINT_API_KEY env var not set. Cint API requires enterprise credentials — contact Cint for API access.",
            }, indent=2, ensure_ascii=False)
        account_id = str(args.get("account_id", "")).strip()
        if not account_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARGS", "required": ["account_id"]}, indent=2, ensure_ascii=False)
        project_id = str(args.get("project_id", "")).strip()
        body: Dict[str, Any] = {}
        country_code = args.get("country_code")
        if country_code:
            body["country_code"] = str(country_code)
        language_code = args.get("language_code")
        if language_code:
            body["language_code"] = str(language_code)
        target_completes = args.get("target_completes")
        if target_completes is not None:
            body["target_completes"] = int(target_completes)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                if project_id:
                    url = f"{_BASE_URL}/demand/accounts/{account_id}/projects/{project_id}/feasibility"
                    resp = await client.get(url, headers=self._auth_headers(key))
                else:
                    url = f"{_BASE_URL}/demand/accounts/{account_id}/feasibility"
                    resp = await client.post(url, json=body, headers=self._auth_headers(key))
            if resp.status_code not in (200, 201):
                logger.info("cint projects.feasibility.get http %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
        except httpx.TimeoutException as e:
            logger.info("cint projects.feasibility.get timeout: %s", e)
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("cint projects.feasibility.get http error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            logger.info("cint projects.feasibility.get json decode error: %s", e)
            return json.dumps({"ok": False, "error_code": "JSON_DECODE_ERROR"}, indent=2, ensure_ascii=False)
        return f"cint.projects.feasibility.get.v1 ok\n\n```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"

    async def _projects_launch(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("CINT_API_KEY", "")
        if not key:
            return json.dumps({
                "ok": False,
                "error_code": "NO_CREDENTIALS",
                "message": "CINT_API_KEY env var not set. Cint API requires enterprise credentials — contact Cint for API access.",
            }, indent=2, ensure_ascii=False)
        account_id = str(args.get("account_id", "")).strip()
        project_id = str(args.get("project_id", "")).strip()
        target_group_id = str(args.get("target_group_id", "")).strip()
        if not account_id or not project_id or not target_group_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARGS", "required": ["account_id", "project_id", "target_group_id"]}, indent=2, ensure_ascii=False)
        url = (
            f"{_BASE_URL}/demand/accounts/{account_id}/projects/{project_id}"
            f"/target-groups/{target_group_id}/fielding-run-jobs/launch-from-draft"
        )
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(url, headers=self._auth_headers(key))
            if resp.status_code not in (200, 201, 202):
                logger.info("cint projects.launch http %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            location = resp.headers.get("location", "")
            data = resp.json() if resp.text else {}
        except httpx.TimeoutException as e:
            logger.info("cint projects.launch timeout: %s", e)
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("cint projects.launch http error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            logger.info("cint projects.launch json decode error: %s", e)
            return json.dumps({"ok": False, "error_code": "JSON_DECODE_ERROR"}, indent=2, ensure_ascii=False)
        return f"cint.projects.launch.v1 ok (201 Created — async job)\n\n```json\n{json.dumps({'ok': True, 'job_status_url': location, 'result': data}, indent=2, ensure_ascii=False)}\n```"
