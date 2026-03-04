import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("prolific")

PROVIDER_NAME = "prolific"
METHOD_IDS = [
    "prolific.studies.create.v1",
    "prolific.studies.get.v1",
    "prolific.submissions.approve.v1",
    "prolific.submissions.list.v1",
    "prolific.submissions.reject.v1",
]

_BASE_URL = "https://api.prolific.com/api/v1"


class IntegrationProlific:
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
            key = os.environ.get("PROLIFIC_API_TOKEN", "")
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
        if method_id == "prolific.studies.create.v1":
            return await self._studies_create(args)
        if method_id == "prolific.studies.get.v1":
            return await self._studies_get(args)
        if method_id == "prolific.submissions.list.v1":
            return await self._submissions_list(args)
        if method_id == "prolific.submissions.approve.v1":
            return await self._submissions_approve(args)
        if method_id == "prolific.submissions.reject.v1":
            return await self._submissions_reject(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _studies_create(self, args: Dict[str, Any]) -> str:
        token = os.environ.get("PROLIFIC_API_TOKEN", "")
        if not token:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        name = str(args.get("name", "")).strip()
        description = str(args.get("description", "")).strip()
        total_available_places = args.get("total_available_places")
        reward = args.get("reward")
        estimated_completion_time = args.get("estimated_completion_time")
        if not name or not description or total_available_places is None or reward is None or estimated_completion_time is None:
            return json.dumps({"ok": False, "error_code": "MISSING_ARGS", "required": ["name", "description", "total_available_places", "reward", "estimated_completion_time"]}, indent=2, ensure_ascii=False)
        body: Dict[str, Any] = {
            "name": name,
            "description": description,
            "total_available_places": int(total_available_places),
            "reward": int(reward),
            "estimated_completion_time": int(estimated_completion_time),
        }
        eligibility = args.get("eligibility_requirements")
        if eligibility is not None:
            body["eligibility_requirements"] = eligibility
        internal_name = args.get("internal_name")
        if internal_name:
            body["internal_name"] = str(internal_name)
        headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(f"{_BASE_URL}/studies/", json=body, headers=headers)
            if resp.status_code not in (200, 201):
                logger.info("prolific studies.create http %s: %s", resp.status_code, resp.text)
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text}, indent=2, ensure_ascii=False)
            data = resp.json()
        except httpx.TimeoutException as e:
            logger.info("prolific studies.create timeout: %s", e)
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("prolific studies.create http error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            logger.info("prolific studies.create json decode error: %s", e)
            return json.dumps({"ok": False, "error_code": "JSON_DECODE_ERROR"}, indent=2, ensure_ascii=False)
        return f"prolific.studies.create.v1 ok\n\n```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"

    async def _studies_get(self, args: Dict[str, Any]) -> str:
        token = os.environ.get("PROLIFIC_API_TOKEN", "")
        if not token:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        study_id = str(args.get("study_id", "")).strip()
        if not study_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARGS", "required": ["study_id"]}, indent=2, ensure_ascii=False)
        headers = {"Authorization": f"Token {token}"}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(f"{_BASE_URL}/studies/{study_id}/", headers=headers)
            if resp.status_code != 200:
                logger.info("prolific studies.get http %s: %s", resp.status_code, resp.text)
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text}, indent=2, ensure_ascii=False)
            data = resp.json()
        except httpx.TimeoutException as e:
            logger.info("prolific studies.get timeout: %s", e)
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("prolific studies.get http error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            logger.info("prolific studies.get json decode error: %s", e)
            return json.dumps({"ok": False, "error_code": "JSON_DECODE_ERROR"}, indent=2, ensure_ascii=False)
        return f"prolific.studies.get.v1 ok\n\n```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"

    async def _submissions_list(self, args: Dict[str, Any]) -> str:
        token = os.environ.get("PROLIFIC_API_TOKEN", "")
        if not token:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        study_id = str(args.get("study_id", "")).strip()
        if not study_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARGS", "required": ["study_id"]}, indent=2, ensure_ascii=False)
        headers = {"Authorization": f"Token {token}"}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(f"{_BASE_URL}/studies/{study_id}/submissions/", headers=headers)
            if resp.status_code != 200:
                logger.info("prolific submissions.list http %s: %s", resp.status_code, resp.text)
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text}, indent=2, ensure_ascii=False)
            data = resp.json()
        except httpx.TimeoutException as e:
            logger.info("prolific submissions.list timeout: %s", e)
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("prolific submissions.list http error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            logger.info("prolific submissions.list json decode error: %s", e)
            return json.dumps({"ok": False, "error_code": "JSON_DECODE_ERROR"}, indent=2, ensure_ascii=False)
        return f"prolific.submissions.list.v1 ok\n\n```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"

    async def _submissions_approve(self, args: Dict[str, Any]) -> str:
        token = os.environ.get("PROLIFIC_API_TOKEN", "")
        if not token:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        submission_id = str(args.get("submission_id", "")).strip()
        if not submission_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARGS", "required": ["submission_id"]}, indent=2, ensure_ascii=False)
        headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
        body = {"action": "APPROVE"}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(f"{_BASE_URL}/submissions/{submission_id}/transition/", json=body, headers=headers)
            if resp.status_code not in (200, 201):
                logger.info("prolific submissions.approve http %s: %s", resp.status_code, resp.text)
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text}, indent=2, ensure_ascii=False)
            data = resp.json()
        except httpx.TimeoutException as e:
            logger.info("prolific submissions.approve timeout: %s", e)
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("prolific submissions.approve http error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            logger.info("prolific submissions.approve json decode error: %s", e)
            return json.dumps({"ok": False, "error_code": "JSON_DECODE_ERROR"}, indent=2, ensure_ascii=False)
        return f"prolific.submissions.approve.v1 ok\n\n```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"

    async def _submissions_reject(self, args: Dict[str, Any]) -> str:
        token = os.environ.get("PROLIFIC_API_TOKEN", "")
        if not token:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        submission_id = str(args.get("submission_id", "")).strip()
        if not submission_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARGS", "required": ["submission_id"]}, indent=2, ensure_ascii=False)
        body: Dict[str, Any] = {"action": "REJECT"}
        rejection_category = args.get("rejection_category")
        if rejection_category:
            body["rejection_category"] = str(rejection_category)
        headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(f"{_BASE_URL}/submissions/{submission_id}/transition/", json=body, headers=headers)
            if resp.status_code not in (200, 201):
                logger.info("prolific submissions.reject http %s: %s", resp.status_code, resp.text)
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text}, indent=2, ensure_ascii=False)
            data = resp.json()
        except httpx.TimeoutException as e:
            logger.info("prolific submissions.reject timeout: %s", e)
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("prolific submissions.reject http error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            logger.info("prolific submissions.reject json decode error: %s", e)
            return json.dumps({"ok": False, "error_code": "JSON_DECODE_ERROR"}, indent=2, ensure_ascii=False)
        return f"prolific.submissions.reject.v1 ok\n\n```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"
