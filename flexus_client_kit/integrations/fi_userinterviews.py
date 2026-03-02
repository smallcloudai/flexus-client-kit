import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("userinterviews")

PROVIDER_NAME = "userinterviews"
METHOD_IDS = [
    "userinterviews.participants.create.v1",
    "userinterviews.participants.update.v1",
    "userinterviews.participants.delete.v1",
]

_BASE_URL = "https://www.userinterviews.com/api"
_ACCEPT = "application/vnd.user-interviews.v2+json"


class IntegrationUserinterviews:
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
            key = os.environ.get("USERINTERVIEWS_API_KEY", "")
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
        if method_id == "userinterviews.participants.create.v1":
            return await self._participants_create(args)
        if method_id == "userinterviews.participants.update.v1":
            return await self._participants_update(args)
        if method_id == "userinterviews.participants.delete.v1":
            return await self._participants_delete(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _participants_create(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("USERINTERVIEWS_API_KEY", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "USERINTERVIEWS_API_KEY env var not set"}, indent=2, ensure_ascii=False)
        email = str(args.get("email", "")).strip()
        if not email:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "email is required"}, indent=2, ensure_ascii=False)
        body: Dict[str, Any] = {"email": email}
        name = args.get("name")
        if name:
            body["name"] = str(name)
        metadata = args.get("metadata")
        if metadata and isinstance(metadata, dict):
            body["metadata"] = metadata
        headers = {
            "Authorization": f"Bearer {key}",
            "Accept": _ACCEPT,
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{_BASE_URL}/participants",
                    headers=headers,
                    json=body,
                )
            if resp.status_code not in (200, 201):
                logger.info("userinterviews participants.create error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            return f"userinterviews.participants.create ok\n\n```json\n{json.dumps({'ok': True, 'participant': data}, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _participants_update(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("USERINTERVIEWS_API_KEY", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "USERINTERVIEWS_API_KEY env var not set"}, indent=2, ensure_ascii=False)
        participant_id = str(args.get("participant_id", "")).strip()
        if not participant_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "participant_id is required"}, indent=2, ensure_ascii=False)
        body: Dict[str, Any] = {}
        email = args.get("email")
        if email is not None:
            body["email"] = str(email).strip()
        name = args.get("name")
        if name is not None:
            body["name"] = str(name)
        metadata = args.get("metadata")
        if metadata is not None and isinstance(metadata, dict):
            body["metadata"] = metadata
        if not body:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "at least one of email, name, metadata must be provided"}, indent=2, ensure_ascii=False)
        headers = {
            "Authorization": f"Bearer {key}",
            "Accept": _ACCEPT,
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.patch(
                    f"{_BASE_URL}/participants/{participant_id}",
                    headers=headers,
                    json=body,
                )
            if resp.status_code not in (200, 204):
                logger.info("userinterviews participants.update error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            if resp.status_code == 204 or not resp.content:
                return json.dumps({"ok": True, "participant_id": participant_id, "updated": list(body.keys())}, indent=2, ensure_ascii=False)
            data = resp.json()
            return f"userinterviews.participants.update ok\n\n```json\n{json.dumps({'ok': True, 'participant': data}, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _participants_delete(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("USERINTERVIEWS_API_KEY", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "USERINTERVIEWS_API_KEY env var not set"}, indent=2, ensure_ascii=False)
        participant_id = str(args.get("participant_id", "")).strip()
        if not participant_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "participant_id is required"}, indent=2, ensure_ascii=False)
        headers = {
            "Authorization": f"Bearer {key}",
            "Accept": _ACCEPT,
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.delete(
                    f"{_BASE_URL}/participants/{participant_id}",
                    headers=headers,
                )
            if resp.status_code not in (200, 204):
                logger.info("userinterviews participants.delete error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            return json.dumps({"ok": True, "participant_id": participant_id, "deleted": True}, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
