import base64
import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("qualtrics")

PROVIDER_NAME = "qualtrics"
METHOD_IDS = [
    "qualtrics.contacts.create.v1",
    "qualtrics.contacts.list.v1",
    "qualtrics.distributions.create.v1",
    "qualtrics.mailinglists.list.v1",
    "qualtrics.responseexports.file.get.v1",
    "qualtrics.responseexports.progress.get.v1",
    "qualtrics.responseexports.start.v1",
    "qualtrics.surveys.create.v1",
    "qualtrics.surveys.update.v1",
]

_NO_CREDENTIALS = json.dumps(
    {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
    indent=2,
    ensure_ascii=False,
)


class IntegrationQualtrics:
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
            token = os.environ.get("QUALTRICS_API_TOKEN", "")
            base_url = os.environ.get("QUALTRICS_BASE_URL", "")
            return json.dumps(
                {
                    "ok": True,
                    "provider": PROVIDER_NAME,
                    "status": "available" if (token and base_url) else "no_credentials",
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
        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        dispatch = {
            "qualtrics.surveys.create.v1": self._surveys_create,
            "qualtrics.surveys.update.v1": self._surveys_update,
            "qualtrics.responseexports.start.v1": self._responseexports_start,
            "qualtrics.responseexports.progress.get.v1": self._responseexports_progress_get,
            "qualtrics.responseexports.file.get.v1": self._responseexports_file_get,
            "qualtrics.mailinglists.list.v1": self._mailinglists_list,
            "qualtrics.contacts.create.v1": self._contacts_create,
            "qualtrics.contacts.list.v1": self._contacts_list,
            "qualtrics.distributions.create.v1": self._distributions_create,
        }
        return await dispatch[method_id](args)

    def _get_credentials(self):
        token = os.environ.get("QUALTRICS_API_TOKEN", "")
        base_url = os.environ.get("QUALTRICS_BASE_URL", "").rstrip("/")
        return token, base_url

    def _headers(self, token: str) -> Dict[str, str]:
        return {"X-API-TOKEN": token, "Content-Type": "application/json"}

    def _ok(self, method_id: str, data: Any) -> str:
        return (
            f"qualtrics.{method_id} ok\n\n"
            f"```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"
        )

    def _provider_error(self, status_code: int, detail: Any) -> str:
        logger.info("qualtrics provider error status=%s detail=%s", status_code, detail)
        return json.dumps(
            {"ok": False, "error_code": "PROVIDER_ERROR", "status": status_code, "detail": detail},
            indent=2,
            ensure_ascii=False,
        )

    async def _surveys_create(self, args: Dict[str, Any]) -> str:
        token, base_url = self._get_credentials()
        if not token or not base_url:
            return _NO_CREDENTIALS
        survey_name = str(args.get("survey_name", "")).strip()
        language = str(args.get("language", "EN")).strip() or "EN"
        if not survey_name:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "survey_name"}, indent=2, ensure_ascii=False)
        body = {"SurveyName": survey_name, "Language": language, "ProjectCategory": "CORE"}
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(
                    f"{base_url}/API/v3/survey-definitions",
                    headers=self._headers(token),
                    json=body,
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code not in (200, 201):
            return self._provider_error(resp.status_code, resp.text)
        try:
            data = resp.json().get("result", resp.json())
        except json.JSONDecodeError:
            data = resp.text
        return self._ok("surveys.create.v1", data)

    async def _surveys_update(self, args: Dict[str, Any]) -> str:
        token, base_url = self._get_credentials()
        if not token or not base_url:
            return _NO_CREDENTIALS
        survey_id = str(args.get("survey_id", "")).strip()
        if not survey_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "survey_id"}, indent=2, ensure_ascii=False)
        body: Dict[str, Any] = {}
        survey_name = args.get("survey_name")
        if survey_name:
            body["SurveyName"] = str(survey_name).strip()
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.put(
                    f"{base_url}/API/v3/survey-definitions/{survey_id}",
                    headers=self._headers(token),
                    json=body,
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code not in (200, 204):
            return self._provider_error(resp.status_code, resp.text)
        try:
            data = resp.json().get("result", resp.json())
        except json.JSONDecodeError:
            data = {"survey_id": survey_id, "updated": True}
        return self._ok("surveys.update.v1", data)

    async def _responseexports_start(self, args: Dict[str, Any]) -> str:
        token, base_url = self._get_credentials()
        if not token or not base_url:
            return _NO_CREDENTIALS
        survey_id = str(args.get("survey_id", "")).strip()
        if not survey_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "survey_id"}, indent=2, ensure_ascii=False)
        fmt = str(args.get("format", "json")).strip() or "json"
        body = {"format": fmt}
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(
                    f"{base_url}/API/v3/surveys/{survey_id}/export-responses",
                    headers=self._headers(token),
                    json=body,
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code not in (200, 202):
            return self._provider_error(resp.status_code, resp.text)
        try:
            data = resp.json().get("result", resp.json())
        except json.JSONDecodeError:
            data = resp.text
        return self._ok("responseexports.start.v1", data)

    async def _responseexports_progress_get(self, args: Dict[str, Any]) -> str:
        token, base_url = self._get_credentials()
        if not token or not base_url:
            return _NO_CREDENTIALS
        survey_id = str(args.get("survey_id", "")).strip()
        progress_id = str(args.get("progress_id", "")).strip()
        if not survey_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "survey_id"}, indent=2, ensure_ascii=False)
        if not progress_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "progress_id"}, indent=2, ensure_ascii=False)
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(
                    f"{base_url}/API/v3/surveys/{survey_id}/export-responses/{progress_id}",
                    headers=self._headers(token),
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code != 200:
            return self._provider_error(resp.status_code, resp.text)
        try:
            data = resp.json().get("result", resp.json())
        except json.JSONDecodeError:
            data = resp.text
        return self._ok("responseexports.progress.get.v1", data)

    async def _responseexports_file_get(self, args: Dict[str, Any]) -> str:
        token, base_url = self._get_credentials()
        if not token or not base_url:
            return _NO_CREDENTIALS
        survey_id = str(args.get("survey_id", "")).strip()
        file_id = str(args.get("file_id", "")).strip()
        if not survey_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "survey_id"}, indent=2, ensure_ascii=False)
        if not file_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "file_id"}, indent=2, ensure_ascii=False)
        headers = {"X-API-TOKEN": token}
        async with httpx.AsyncClient(timeout=60) as client:
            try:
                resp = await client.get(
                    f"{base_url}/API/v3/surveys/{survey_id}/export-responses/{file_id}/file",
                    headers=headers,
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code != 200:
            return self._provider_error(resp.status_code, resp.text)
        encoded = base64.b64encode(resp.content).decode("ascii")
        data = {"note": "ZIP file, base64 encoded", "content_type": resp.headers.get("content-type", ""), "data_base64": encoded}
        return self._ok("responseexports.file.get.v1", data)

    async def _mailinglists_list(self, args: Dict[str, Any]) -> str:
        token, base_url = self._get_credentials()
        if not token or not base_url:
            return _NO_CREDENTIALS
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(
                    f"{base_url}/API/v3/mailinglists",
                    headers=self._headers(token),
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code != 200:
            return self._provider_error(resp.status_code, resp.text)
        try:
            data = resp.json().get("result", resp.json())
        except json.JSONDecodeError:
            data = resp.text
        return self._ok("mailinglists.list.v1", data)

    async def _contacts_create(self, args: Dict[str, Any]) -> str:
        token, base_url = self._get_credentials()
        if not token or not base_url:
            return _NO_CREDENTIALS
        mailing_list_id = str(args.get("mailing_list_id", "")).strip()
        email = str(args.get("email", "")).strip()
        if not mailing_list_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "mailing_list_id"}, indent=2, ensure_ascii=False)
        if not email:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "email"}, indent=2, ensure_ascii=False)
        body: Dict[str, Any] = {"email": email}
        first_name = args.get("first_name")
        last_name = args.get("last_name")
        if first_name:
            body["firstName"] = str(first_name).strip()
        if last_name:
            body["lastName"] = str(last_name).strip()
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(
                    f"{base_url}/API/v3/mailinglists/{mailing_list_id}/contacts",
                    headers=self._headers(token),
                    json=body,
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code not in (200, 201):
            return self._provider_error(resp.status_code, resp.text)
        try:
            data = resp.json().get("result", resp.json())
        except json.JSONDecodeError:
            data = resp.text
        return self._ok("contacts.create.v1", data)

    async def _contacts_list(self, args: Dict[str, Any]) -> str:
        token, base_url = self._get_credentials()
        if not token or not base_url:
            return _NO_CREDENTIALS
        mailing_list_id = str(args.get("mailing_list_id", "")).strip()
        if not mailing_list_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "mailing_list_id"}, indent=2, ensure_ascii=False)
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(
                    f"{base_url}/API/v3/mailinglists/{mailing_list_id}/contacts",
                    headers=self._headers(token),
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code != 200:
            return self._provider_error(resp.status_code, resp.text)
        try:
            data = resp.json().get("result", resp.json())
        except json.JSONDecodeError:
            data = resp.text
        return self._ok("contacts.list.v1", data)

    async def _distributions_create(self, args: Dict[str, Any]) -> str:
        token, base_url = self._get_credentials()
        if not token or not base_url:
            return _NO_CREDENTIALS
        survey_id = str(args.get("survey_id", "")).strip()
        mailing_list_id = str(args.get("mailing_list_id", "")).strip()
        send_date = str(args.get("send_date", "")).strip()
        from_email = str(args.get("from_email", "")).strip()
        from_name = str(args.get("from_name", "")).strip()
        subject = str(args.get("subject", "")).strip()
        missing = [k for k, v in {
            "survey_id": survey_id,
            "mailing_list_id": mailing_list_id,
            "send_date": send_date,
            "from_email": from_email,
            "from_name": from_name,
            "subject": subject,
        }.items() if not v]
        if missing:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "args": missing}, indent=2, ensure_ascii=False)
        body = {
            "surveyId": survey_id,
            "recipients": {"mailingListId": mailing_list_id},
            "sendDate": send_date,
            "header": {
                "fromEmail": from_email,
                "fromName": from_name,
                "subject": subject,
                "replyToEmail": from_email,
            },
        }
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(
                    f"{base_url}/API/v3/distributions",
                    headers=self._headers(token),
                    json=body,
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code not in (200, 201):
            return self._provider_error(resp.status_code, resp.text)
        try:
            data = resp.json().get("result", resp.json())
        except json.JSONDecodeError:
            data = resp.text
        return self._ok("distributions.create.v1", data)
