import asyncio
import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("gdrive")

PROVIDER_NAME = "gdrive"
API_BASE = "https://www.googleapis.com/drive/v3"
METHOD_IDS = [
    "gdrive.files.export.v1",
]

_SCOPE = "https://www.googleapis.com/auth/drive.readonly"


def _get_token() -> str:
    sa_json = os.environ.get("GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON", "")
    if not sa_json:
        return ""
    from google.oauth2 import service_account
    import google.auth.transport.requests
    info = json.loads(sa_json)
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=[_SCOPE]
    )
    request = google.auth.transport.requests.Request()
    creds.refresh(request)
    return creds.token


class IntegrationGdrive:
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
            sa_json = os.environ.get("GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON", "")
            status = "available" if sa_json else "no_credentials"
            return json.dumps(
                {
                    "ok": True,
                    "provider": PROVIDER_NAME,
                    "status": status,
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
            return "Error: unknown op."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required."
        if method_id not in METHOD_IDS:
            return json.dumps(
                {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
                indent=2,
                ensure_ascii=False,
            )
        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, call_args: Dict[str, Any]) -> str:
        if method_id == "gdrive.files.export.v1":
            return await self._files_export(call_args)
        return json.dumps(
            {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
            indent=2,
            ensure_ascii=False,
        )

    async def _files_export(self, call_args: Dict[str, Any]) -> str:
        file_id = str(call_args.get("file_id", "")).strip()
        if not file_id:
            return "Error: file_id required."
        mime_type = str(call_args.get("mime_type", "text/plain")).strip() or "text/plain"
        sa_json = os.environ.get("GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON", "")
        if not sa_json:
            return json.dumps(
                {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        token = await asyncio.to_thread(_get_token)
        if not token:
            return json.dumps(
                {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        url = f"{API_BASE}/files/{file_id}/export"
        params = {"mimeType": mime_type}
        headers = {"Authorization": f"Bearer {token}"}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, params=params, headers=headers, timeout=60.0
                )
                response.raise_for_status()
        except httpx.TimeoutException as e:
            logger.info("GDrive export timeout file_id=%s: %s", file_id, e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "file_id": file_id},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPStatusError as e:
            logger.info(
                "GDrive export HTTP error file_id=%s status=%s: %s",
                file_id,
                e.response.status_code,
                e,
            )
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "HTTP_ERROR",
                    "file_id": file_id,
                    "status_code": e.response.status_code,
                },
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("GDrive export HTTP error file_id=%s: %s", file_id, e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "file_id": file_id},
                indent=2,
                ensure_ascii=False,
            )
        content_bytes = response.content
        content_length = len(content_bytes)
        try:
            content_str = content_bytes.decode("utf-8")
            content_preview = content_str[:2000]
        except UnicodeDecodeError:
            content_preview = "[binary content]"
        return json.dumps(
            {
                "ok": True,
                "file_id": file_id,
                "mime_type": mime_type,
                "content_length": content_length,
                "content_preview": content_preview,
            },
            indent=2,
            ensure_ascii=False,
        )
