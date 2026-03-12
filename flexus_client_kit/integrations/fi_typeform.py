import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("typeform")

PROVIDER_NAME = "typeform"
METHOD_IDS = [
    "typeform.forms.create.v1",
    "typeform.forms.update.v1",
    "typeform.responses.list.v1",
]

_BASE_URL = "https://api.typeform.com"


class IntegrationTypeform:
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
            key = os.environ.get("TYPEFORM_ACCESS_TOKEN", "")
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
        if method_id == "typeform.forms.create.v1":
            return await self._forms_create(args)
        if method_id == "typeform.forms.update.v1":
            return await self._forms_update(args)
        if method_id == "typeform.responses.list.v1":
            return await self._responses_list(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _forms_create(self, args: Dict[str, Any]) -> str:
        token = os.environ.get("TYPEFORM_ACCESS_TOKEN", "")
        if not token:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        title = str(args.get("title", "")).strip()
        if not title:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "title"}, indent=2, ensure_ascii=False)
        fields = args.get("fields") or []
        body: Dict[str, Any] = {"title": title}
        if fields:
            body["fields"] = fields
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(f"{_BASE_URL}/forms", json=body, headers=headers)
                if resp.status_code != 201:
                    logger.info("typeform forms.create failed: status=%d body=%s", resp.status_code, resp.text[:500])
                    return json.dumps({
                        "ok": False,
                        "error_code": "PROVIDER_ERROR",
                        "status": resp.status_code,
                        "detail": resp.text[:500],
                    }, indent=2, ensure_ascii=False)
                data = resp.json()
        except httpx.TimeoutException as e:
            logger.info("typeform forms.create timeout: %s", e)
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("typeform forms.create http error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        result = {
            "id": data.get("id", ""),
            "title": data.get("title", ""),
            "_links": data.get("_links", {}),
            "full": data,
        }
        return (
            f"typeform.forms.create.v1 ok\n\n"
            f"```json\n{json.dumps({'ok': True, 'result': result}, indent=2, ensure_ascii=False)}\n```"
        )

    async def _forms_update(self, args: Dict[str, Any]) -> str:
        token = os.environ.get("TYPEFORM_ACCESS_TOKEN", "")
        if not token:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        form_id = str(args.get("form_id", "")).strip()
        if not form_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "form_id"}, indent=2, ensure_ascii=False)
        body: Dict[str, Any] = {}
        if args.get("title"):
            body["title"] = str(args["title"]).strip()
        if args.get("fields"):
            body["fields"] = args["fields"]
        if not body:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "detail": "Provide title or fields to update"}, indent=2, ensure_ascii=False)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.put(f"{_BASE_URL}/forms/{form_id}", json=body, headers=headers)
                if resp.status_code != 200:
                    logger.info("typeform forms.update failed: status=%d body=%s", resp.status_code, resp.text[:500])
                    return json.dumps({
                        "ok": False,
                        "error_code": "PROVIDER_ERROR",
                        "status": resp.status_code,
                        "detail": resp.text[:500],
                    }, indent=2, ensure_ascii=False)
                data = resp.json()
        except httpx.TimeoutException as e:
            logger.info("typeform forms.update timeout: %s", e)
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("typeform forms.update http error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        result = {
            "id": data.get("id", ""),
            "title": data.get("title", ""),
            "_links": data.get("_links", {}),
            "full": data,
        }
        return (
            f"typeform.forms.update.v1 ok\n\n"
            f"```json\n{json.dumps({'ok': True, 'result': result}, indent=2, ensure_ascii=False)}\n```"
        )

    async def _responses_list(self, args: Dict[str, Any]) -> str:
        token = os.environ.get("TYPEFORM_ACCESS_TOKEN", "")
        if not token:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        form_id = str(args.get("form_id", "")).strip()
        if not form_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "form_id"}, indent=2, ensure_ascii=False)
        page_size = int(args.get("page_size", 25))
        params: Dict[str, Any] = {"page_size": page_size}
        before = args.get("before")
        if before:
            params["before"] = str(before)
        headers = {
            "Authorization": f"Bearer {token}",
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{_BASE_URL}/forms/{form_id}/responses",
                    params=params,
                    headers=headers,
                )
                if resp.status_code != 200:
                    logger.info("typeform responses.list failed: status=%d body=%s", resp.status_code, resp.text[:500])
                    return json.dumps({
                        "ok": False,
                        "error_code": "PROVIDER_ERROR",
                        "status": resp.status_code,
                        "detail": resp.text[:500],
                    }, indent=2, ensure_ascii=False)
                data = resp.json()
        except httpx.TimeoutException as e:
            logger.info("typeform responses.list timeout: %s", e)
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("typeform responses.list http error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        result = {
            "total_items": data.get("total_items", 0),
            "page_count": data.get("page_count", 0),
            "items": data.get("items", []),
        }
        return (
            f"typeform.responses.list.v1 ok\n\n"
            f"```json\n{json.dumps({'ok': True, 'result': result}, indent=2, ensure_ascii=False)}\n```"
        )
