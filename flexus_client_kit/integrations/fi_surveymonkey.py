import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("surveymonkey")

PROVIDER_NAME = "surveymonkey"
METHOD_IDS = [
    "surveymonkey.collectors.create.v1",
    "surveymonkey.responses.list.v1",
    "surveymonkey.surveys.create.v1",
    "surveymonkey.surveys.responses.list.v1",
    "surveymonkey.surveys.update.v1",
]

_BASE_URL = "https://api.surveymonkey.com/v3"


class IntegrationSurveymonkey:
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
            key = os.environ.get("SURVEYMONKEY_ACCESS_TOKEN", "")
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
        if method_id == "surveymonkey.surveys.create.v1":
            return await self._surveys_create(args)
        if method_id == "surveymonkey.surveys.update.v1":
            return await self._surveys_update(args)
        if method_id == "surveymonkey.collectors.create.v1":
            return await self._collectors_create(args)
        if method_id == "surveymonkey.responses.list.v1":
            return await self._responses_list(args)
        if method_id == "surveymonkey.surveys.responses.list.v1":
            return await self._responses_list(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _headers(self, token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _ok(self, method_label: str, data: Any) -> str:
        return (
            f"surveymonkey.{method_label} ok\n\n"
            f"```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"
        )

    def _provider_error(self, status_code: int, detail: str) -> str:
        logger.info("surveymonkey provider error status=%s detail=%s", status_code, detail)
        return json.dumps({
            "ok": False,
            "error_code": "PROVIDER_ERROR",
            "status": status_code,
            "detail": detail,
        }, indent=2, ensure_ascii=False)

    async def _surveys_create(self, args: Dict[str, Any]) -> str:
        token = os.environ.get("SURVEYMONKEY_ACCESS_TOKEN", "")
        if not token:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        title = str(args.get("title", "")).strip()
        if not title:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "title"}, indent=2, ensure_ascii=False)
        payload: Dict[str, Any] = {"title": title}
        pages = args.get("pages")
        if pages:
            payload["pages"] = pages
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(
                    f"{_BASE_URL}/surveys",
                    headers=self._headers(token),
                    json=payload,
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code not in (200, 201):
            return self._provider_error(resp.status_code, resp.text[:500])
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return self._provider_error(resp.status_code, "invalid json in response")
        return self._ok("surveys.create.v1", data)

    async def _surveys_update(self, args: Dict[str, Any]) -> str:
        token = os.environ.get("SURVEYMONKEY_ACCESS_TOKEN", "")
        if not token:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        survey_id = str(args.get("survey_id", "")).strip()
        if not survey_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "survey_id"}, indent=2, ensure_ascii=False)
        payload: Dict[str, Any] = {}
        title = args.get("title")
        if title is not None:
            payload["title"] = str(title)
        pages = args.get("pages")
        if pages is not None:
            payload["pages"] = pages
        if not payload:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "title or pages"}, indent=2, ensure_ascii=False)
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.patch(
                    f"{_BASE_URL}/surveys/{survey_id}",
                    headers=self._headers(token),
                    json=payload,
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code == 204:
            return self._ok("surveys.update.v1", {})
        if resp.status_code not in (200, 201):
            return self._provider_error(resp.status_code, resp.text[:500])
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return self._provider_error(resp.status_code, "invalid json in response")
        return self._ok("surveys.update.v1", data)

    async def _collectors_create(self, args: Dict[str, Any]) -> str:
        token = os.environ.get("SURVEYMONKEY_ACCESS_TOKEN", "")
        if not token:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        survey_id = str(args.get("survey_id", "")).strip()
        if not survey_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "survey_id"}, indent=2, ensure_ascii=False)
        collector_type = str(args.get("type", "weblink")).strip()
        payload: Dict[str, Any] = {"type": collector_type}
        name = args.get("name")
        if name:
            payload["name"] = str(name)
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(
                    f"{_BASE_URL}/surveys/{survey_id}/collectors",
                    headers=self._headers(token),
                    json=payload,
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code not in (200, 201):
            return self._provider_error(resp.status_code, resp.text[:500])
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return self._provider_error(resp.status_code, "invalid json in response")
        return self._ok("collectors.create.v1", data)

    async def _responses_list(self, args: Dict[str, Any]) -> str:
        token = os.environ.get("SURVEYMONKEY_ACCESS_TOKEN", "")
        if not token:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        survey_id = str(args.get("survey_id", "")).strip()
        if not survey_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "survey_id"}, indent=2, ensure_ascii=False)
        try:
            per_page = int(args.get("per_page", 50))
            page = int(args.get("page", 1))
        except (ValueError, TypeError) as e:
            return json.dumps({"ok": False, "error_code": "INVALID_ARG", "detail": str(e)}, indent=2, ensure_ascii=False)
        params = {"per_page": per_page, "page": page}
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(
                    f"{_BASE_URL}/surveys/{survey_id}/responses/bulk",
                    headers=self._headers(token),
                    params=params,
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code != 200:
            return self._provider_error(resp.status_code, resp.text[:500])
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return self._provider_error(resp.status_code, "invalid json in response")
        return self._ok("surveys.responses.list.v1", data)
