import json
import logging
import os
from typing import Any, Dict, Optional

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("userinterviews")

PROVIDER_NAME = "userinterviews"
METHOD_IDS = [
    "userinterviews.participants.list.v1",
    "userinterviews.participants.get.v1",
    "userinterviews.participants.create.v1",
    "userinterviews.participants.update.v1",
    "userinterviews.participants.delete.v1",
]

_BASE_URL = "https://www.userinterviews.com/api"
_ACCEPT = "application/vnd.user-interviews.v2+json"

# User Interviews Hub API uses a bearer API key for reviewed account access.
# Required value:
# - USERINTERVIEWS_API_KEY: issued for the Research Hub / API-enabled account.
# Where colleagues register it:
# - runtime environment or secret manager for the Flexus deployment.
# This module currently targets the publicly confirmed participant profile surface.
USERINTERVIEWS_SETUP_SCHEMA: list[dict[str, Any]] = []


class IntegrationUserinterviews:
    def __init__(self, rcx=None) -> None:
        self.rcx = rcx

    def _api_key(self) -> str:
        try:
            return str(os.environ.get("USERINTERVIEWS_API_KEY", "")).strip()
        except (TypeError, ValueError):
            return ""

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key()}",
            "Accept": _ACCEPT,
            "Content-Type": "application/json",
        }

    def _status(self) -> str:
        return json.dumps({
            "ok": True,
            "provider": PROVIDER_NAME,
            "status": "ready" if self._api_key() else "missing_credentials",
            "method_count": len(METHOD_IDS),
            "auth_type": "bearer_api_key",
            "required_env": ["USERINTERVIEWS_API_KEY"],
            "products": ["Research Hub participant profiles"],
            "message": "Project and invite APIs are only added when the public documentation confirms the current surface.",
        }, indent=2, ensure_ascii=False)

    def _help(self) -> str:
        return (
            f"provider={PROVIDER_NAME}\n"
            "op=help | status | list_methods | call\n"
            f"methods: {', '.join(METHOD_IDS)}\n"
            "notes:\n"
            "- This integration targets the documented participant profile API surface.\n"
            "- Use metadata for custom audience fields synced into Research Hub.\n"
            "- Invite and project orchestration remain intentionally out of scope until their API surface is publicly documented.\n"
        )

    def _error(self, method_id: str, code: str, message: str, **extra: Any) -> str:
        payload: Dict[str, Any] = {
            "ok": False,
            "provider": PROVIDER_NAME,
            "method_id": method_id,
            "error_code": code,
            "message": message,
        }
        payload.update(extra)
        return json.dumps(payload, indent=2, ensure_ascii=False)

    def _result(self, method_id: str, result: Any) -> str:
        return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_id": method_id, "result": result}, indent=2, ensure_ascii=False)

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]],
    ) -> str:
        args = model_produced_args or {}
        op = str(args.get("op", "help")).strip()
        if op == "help":
            return self._help()
        if op == "status":
            return self._status()
        if op == "list_methods":
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_ids": METHOD_IDS}, indent=2, ensure_ascii=False)
        if op != "call":
            return "Error: unknown op. Use help/status/list_methods/call."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_IDS:
            return self._error(method_id, "METHOD_UNKNOWN", "Unknown User Interviews method.")
        if not self._api_key():
            return self._error(method_id, "AUTH_MISSING", "Set USERINTERVIEWS_API_KEY in the runtime environment.")
        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        if method_id == "userinterviews.participants.list.v1":
            return await self._participants_list(args)
        if method_id == "userinterviews.participants.get.v1":
            return await self._participants_get(args)
        if method_id == "userinterviews.participants.create.v1":
            return await self._participants_create(args)
        if method_id == "userinterviews.participants.update.v1":
            return await self._participants_update(args)
        if method_id == "userinterviews.participants.delete.v1":
            return await self._participants_delete(args)
        return self._error(method_id, "METHOD_UNIMPLEMENTED", "Method is declared but not implemented.")

    async def _participants_list(self, args: Dict[str, Any]) -> str:
        try:
            params: Dict[str, Any] = {}
            page = args.get("page")
            per_page = args.get("per_page")
            if page is not None:
                params["page"] = int(page)
            if per_page is not None:
                params["per_page"] = int(per_page)
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(f"{_BASE_URL}/participants", headers=self._headers(), params=params)
            if resp.status_code != 200:
                logger.info("userinterviews participants.list error %s: %s", resp.status_code, resp.text[:200])
                return self._error("userinterviews.participants.list.v1", "PROVIDER_ERROR", "User Interviews returned an error.", status=resp.status_code, detail=resp.text[:500])
            data = resp.json()
            return self._result("userinterviews.participants.list.v1", data)
        except httpx.TimeoutException:
            return self._error("userinterviews.participants.list.v1", "TIMEOUT", "User Interviews request timed out.")
        except httpx.HTTPError as e:
            return self._error("userinterviews.participants.list.v1", "HTTP_ERROR", str(e))
        except (TypeError, ValueError, json.JSONDecodeError) as e:
            logger.error("userinterviews participants.list failed", exc_info=e)
            return self._error("userinterviews.participants.list.v1", "RUNTIME_ERROR", f"{type(e).__name__}: {e}")

    async def _participants_get(self, args: Dict[str, Any]) -> str:
        try:
            participant_id = str(args.get("participant_id", "")).strip()
            if not participant_id:
                return self._error("userinterviews.participants.get.v1", "MISSING_ARG", "participant_id is required")
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(f"{_BASE_URL}/participants/{participant_id}", headers=self._headers())
            if resp.status_code != 200:
                logger.info("userinterviews participants.get error %s: %s", resp.status_code, resp.text[:200])
                return self._error("userinterviews.participants.get.v1", "PROVIDER_ERROR", "User Interviews returned an error.", status=resp.status_code, detail=resp.text[:500])
            data = resp.json()
            return self._result("userinterviews.participants.get.v1", data)
        except httpx.TimeoutException:
            return self._error("userinterviews.participants.get.v1", "TIMEOUT", "User Interviews request timed out.")
        except httpx.HTTPError as e:
            return self._error("userinterviews.participants.get.v1", "HTTP_ERROR", str(e))
        except (TypeError, ValueError, json.JSONDecodeError) as e:
            logger.error("userinterviews participants.get failed", exc_info=e)
            return self._error("userinterviews.participants.get.v1", "RUNTIME_ERROR", f"{type(e).__name__}: {e}")

    async def _participants_create(self, args: Dict[str, Any]) -> str:
        email = str(args.get("email", "")).strip()
        if not email:
            return self._error("userinterviews.participants.create.v1", "MISSING_ARG", "email is required")
        body: Dict[str, Any] = {"email": email}
        name = args.get("name")
        if name:
            body["name"] = str(name)
        metadata = args.get("metadata")
        if metadata and isinstance(metadata, dict):
            body["metadata"] = metadata
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{_BASE_URL}/participants",
                    headers=self._headers(),
                    json=body,
                )
            if resp.status_code not in (200, 201):
                logger.info("userinterviews participants.create error %s: %s", resp.status_code, resp.text[:200])
                return self._error("userinterviews.participants.create.v1", "PROVIDER_ERROR", "User Interviews returned an error.", status=resp.status_code, detail=resp.text[:500])
            data = resp.json()
            return self._result("userinterviews.participants.create.v1", data)
        except httpx.TimeoutException:
            return self._error("userinterviews.participants.create.v1", "TIMEOUT", "User Interviews request timed out.")
        except httpx.HTTPError as e:
            return self._error("userinterviews.participants.create.v1", "HTTP_ERROR", str(e))

    async def _participants_update(self, args: Dict[str, Any]) -> str:
        participant_id = str(args.get("participant_id", "")).strip()
        if not participant_id:
            return self._error("userinterviews.participants.update.v1", "MISSING_ARG", "participant_id is required")
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
            return self._error("userinterviews.participants.update.v1", "MISSING_ARG", "at least one of email, name, metadata must be provided")
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.patch(
                    f"{_BASE_URL}/participants/{participant_id}",
                    headers=self._headers(),
                    json=body,
                )
            if resp.status_code not in (200, 204):
                logger.info("userinterviews participants.update error %s: %s", resp.status_code, resp.text[:200])
                return self._error("userinterviews.participants.update.v1", "PROVIDER_ERROR", "User Interviews returned an error.", status=resp.status_code, detail=resp.text[:500])
            if resp.status_code == 204 or not resp.content:
                return self._result("userinterviews.participants.update.v1", {"participant_id": participant_id, "updated": list(body.keys())})
            data = resp.json()
            return self._result("userinterviews.participants.update.v1", data)
        except httpx.TimeoutException:
            return self._error("userinterviews.participants.update.v1", "TIMEOUT", "User Interviews request timed out.")
        except httpx.HTTPError as e:
            return self._error("userinterviews.participants.update.v1", "HTTP_ERROR", str(e))

    async def _participants_delete(self, args: Dict[str, Any]) -> str:
        participant_id = str(args.get("participant_id", "")).strip()
        if not participant_id:
            return self._error("userinterviews.participants.delete.v1", "MISSING_ARG", "participant_id is required")
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.delete(
                    f"{_BASE_URL}/participants/{participant_id}",
                    headers={
                        "Authorization": f"Bearer {self._api_key()}",
                        "Accept": _ACCEPT,
                    },
                )
            if resp.status_code not in (200, 204):
                logger.info("userinterviews participants.delete error %s: %s", resp.status_code, resp.text[:200])
                return self._error("userinterviews.participants.delete.v1", "PROVIDER_ERROR", "User Interviews returned an error.", status=resp.status_code, detail=resp.text[:500])
            return self._result("userinterviews.participants.delete.v1", {"participant_id": participant_id, "deleted": True})
        except httpx.TimeoutException:
            return self._error("userinterviews.participants.delete.v1", "TIMEOUT", "User Interviews request timed out.")
        except httpx.HTTPError as e:
            return self._error("userinterviews.participants.delete.v1", "HTTP_ERROR", str(e))
