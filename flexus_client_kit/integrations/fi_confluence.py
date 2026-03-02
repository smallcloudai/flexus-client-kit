import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("confluence")

PROVIDER_NAME = "confluence"
METHOD_IDS = [
    "confluence.pages.create.v1",
    "confluence.pages.update.v1",
]


class IntegrationConfluence:
    def _check_credentials(self) -> str:
        email = os.environ.get("CONFLUENCE_EMAIL", "")
        token = os.environ.get("CONFLUENCE_API_TOKEN", "")
        base_url = os.environ.get("CONFLUENCE_BASE_URL", "")
        if not email or not token or not base_url:
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "NO_CREDENTIALS",
                    "provider": PROVIDER_NAME,
                    "message": "CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, CONFLUENCE_BASE_URL env vars required",
                },
                indent=2,
                ensure_ascii=False,
            )
        return ""

    def _base_url(self) -> str:
        return os.environ.get("CONFLUENCE_BASE_URL", "").rstrip("/")

    def _auth(self) -> httpx.BasicAuth:
        email = os.environ.get("CONFLUENCE_EMAIL", "")
        token = os.environ.get("CONFLUENCE_API_TOKEN", "")
        return httpx.BasicAuth(username=email, password=token)

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
                "op=help\n"
                "op=status\n"
                "op=list_methods\n"
                "op=call(args={method_id: ...})\n"
                f"known_method_ids={len(METHOD_IDS)}"
            )
        if op == "status":
            err = self._check_credentials()
            if err:
                return err
            return json.dumps(
                {
                    "ok": True,
                    "provider": PROVIDER_NAME,
                    "status": "available",
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

    async def _dispatch(self, method_id: str, call_args: Dict[str, Any]) -> str:
        if method_id == "confluence.pages.create.v1":
            return await self._pages_create(call_args)
        if method_id == "confluence.pages.update.v1":
            return await self._pages_update(call_args)
        return json.dumps(
            {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
            indent=2,
            ensure_ascii=False,
        )

    async def _pages_create(self, call_args: Dict[str, Any]) -> str:
        err = self._check_credentials()
        if err:
            return err
        space_id = str(call_args.get("space_id", "")).strip()
        title = str(call_args.get("title", "")).strip()
        body_content = str(call_args.get("body_content", "")).strip()
        parent_id = str(call_args.get("parent_id", "")).strip() or None
        if not space_id:
            return json.dumps(
                {"ok": False, "error_code": "MISSING_ARG", "arg": "space_id"},
                indent=2,
                ensure_ascii=False,
            )
        if not title:
            return json.dumps(
                {"ok": False, "error_code": "MISSING_ARG", "arg": "title"},
                indent=2,
                ensure_ascii=False,
            )
        if not body_content:
            return json.dumps(
                {"ok": False, "error_code": "MISSING_ARG", "arg": "body_content"},
                indent=2,
                ensure_ascii=False,
            )
        base = self._base_url()
        url = f"{base}/wiki/api/v2/pages"
        payload: Dict[str, Any] = {
            "spaceId": space_id,
            "title": title,
            "status": "current",
            "body": {"representation": "storage", "value": body_content},
        }
        if parent_id:
            payload["parentId"] = parent_id
        try:
            async with httpx.AsyncClient(auth=self._auth(), timeout=30.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code != 200:
                    logger.info("Confluence pages.create error %s: %s", resp.status_code, resp.text[:200])
                    return json.dumps(
                        {
                            "ok": False,
                            "error_code": "PROVIDER_ERROR",
                            "status": resp.status_code,
                            "detail": resp.text[:500],
                        },
                        indent=2,
                        ensure_ascii=False,
                    )
                data = resp.json()
        except httpx.TimeoutException as e:
            logger.info("Confluence timeout pages.create: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("Confluence HTTP error pages.create: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)},
                indent=2,
                ensure_ascii=False,
            )
        try:
            page_id = data.get("id", "")
            page_title = data.get("title", "")
            status = data.get("status", "")
            space_id_res = data.get("spaceId", "")
            links = data.get("_links") or {}
            web_url = links.get("webui", "")
            if web_url and base:
                web_url = f"{base}{web_url}" if web_url.startswith("/") else web_url
            normalized = {
                "ok": True,
                "id": page_id,
                "title": page_title,
                "status": status,
                "space_id": space_id_res,
                "web_url": web_url,
            }
        except KeyError as e:
            logger.info("Confluence response missing key pages.create: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        return json.dumps(normalized, indent=2, ensure_ascii=False)

    async def _pages_update(self, call_args: Dict[str, Any]) -> str:
        err = self._check_credentials()
        if err:
            return err
        page_id = str(call_args.get("page_id", "")).strip()
        title = str(call_args.get("title", "")).strip()
        body_content = str(call_args.get("body_content", "")).strip()
        version_number = call_args.get("version_number")
        if not page_id:
            return json.dumps(
                {"ok": False, "error_code": "MISSING_ARG", "arg": "page_id"},
                indent=2,
                ensure_ascii=False,
            )
        if not title:
            return json.dumps(
                {"ok": False, "error_code": "MISSING_ARG", "arg": "title"},
                indent=2,
                ensure_ascii=False,
            )
        if not body_content:
            return json.dumps(
                {"ok": False, "error_code": "MISSING_ARG", "arg": "body_content"},
                indent=2,
                ensure_ascii=False,
            )
        try:
            vn = int(version_number)
        except (TypeError, ValueError):
            return json.dumps(
                {"ok": False, "error_code": "MISSING_ARG", "arg": "version_number (int required)"},
                indent=2,
                ensure_ascii=False,
            )
        base = self._base_url()
        url = f"{base}/wiki/api/v2/pages/{page_id}"
        payload = {
            "id": page_id,
            "title": title,
            "status": "current",
            "version": {"number": vn},
            "body": {"representation": "storage", "value": body_content},
        }
        try:
            async with httpx.AsyncClient(auth=self._auth(), timeout=30.0) as client:
                resp = await client.put(url, json=payload)
                if resp.status_code != 200:
                    logger.info("Confluence pages.update error %s: %s", resp.status_code, resp.text[:200])
                    return json.dumps(
                        {
                            "ok": False,
                            "error_code": "PROVIDER_ERROR",
                            "status": resp.status_code,
                            "detail": resp.text[:500],
                        },
                        indent=2,
                        ensure_ascii=False,
                    )
                data = resp.json()
        except httpx.TimeoutException as e:
            logger.info("Confluence timeout pages.update: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("Confluence HTTP error pages.update: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)},
                indent=2,
                ensure_ascii=False,
            )
        try:
            page_id_res = data.get("id", "")
            page_title = data.get("title", "")
            status = data.get("status", "")
            version = data.get("version") or {}
            vn_res = version.get("number", vn)
            links = data.get("_links") or {}
            web_url = links.get("webui", "")
            if web_url and base:
                web_url = f"{base}{web_url}" if web_url.startswith("/") else web_url
            normalized = {
                "ok": True,
                "id": page_id_res,
                "title": page_title,
                "status": status,
                "version_number": vn_res,
                "web_url": web_url,
            }
        except KeyError as e:
            logger.info("Confluence response missing key pages.update: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        return json.dumps(normalized, indent=2, ensure_ascii=False)
