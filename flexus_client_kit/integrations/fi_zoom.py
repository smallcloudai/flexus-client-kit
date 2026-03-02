import base64
import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("zoom")

PROVIDER_NAME = "zoom"
METHOD_IDS = [
    "zoom.meetings.recordings.get.v1",
    "zoom.recordings.list.v1",
    "zoom.recordings.transcript.download.v1",
]

_BASE_URL = "https://api.zoom.us/v2"
_TOKEN_URL = "https://zoom.us/oauth/token"


class IntegrationZoom:
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
            account_id = os.environ.get("ZOOM_ACCOUNT_ID", "")
            client_id = os.environ.get("ZOOM_CLIENT_ID", "")
            client_secret = os.environ.get("ZOOM_CLIENT_SECRET", "")
            has_creds = bool(account_id and client_id and client_secret)
            return json.dumps({
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "available" if has_creds else "no_credentials",
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

    async def _get_token(self) -> str:
        account_id = os.environ.get("ZOOM_ACCOUNT_ID", "")
        client_id = os.environ.get("ZOOM_CLIENT_ID", "")
        client_secret = os.environ.get("ZOOM_CLIENT_SECRET", "")
        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                _TOKEN_URL,
                params={"grant_type": "account_credentials", "account_id": account_id},
                headers={"Authorization": f"Basic {credentials}"},
            )
        resp.raise_for_status()
        return resp.json()["access_token"]

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        if method_id == "zoom.meetings.recordings.get.v1":
            return await self._meetings_recordings_get(args)
        if method_id == "zoom.recordings.list.v1":
            return await self._recordings_list(args)
        if method_id == "zoom.recordings.transcript.download.v1":
            return await self._recordings_transcript_download(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _meetings_recordings_get(self, args: Dict[str, Any]) -> str:
        account_id = os.environ.get("ZOOM_ACCOUNT_ID", "")
        client_id = os.environ.get("ZOOM_CLIENT_ID", "")
        client_secret = os.environ.get("ZOOM_CLIENT_SECRET", "")
        if not (account_id and client_id and client_secret):
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET env vars required"}, indent=2, ensure_ascii=False)
        meeting_id = str(args.get("meeting_id", "")).strip()
        if not meeting_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "meeting_id is required"}, indent=2, ensure_ascii=False)
        try:
            token = await self._get_token()
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{_BASE_URL}/meetings/{meeting_id}/recordings",
                    headers={"Authorization": f"Bearer {token}"},
                )
            if resp.status_code != 200:
                logger.info("zoom meetings.recordings.get error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            files = [
                {"file_id": f.get("id"), "file_type": f.get("file_type"), "file_size": f.get("file_size"), "status": f.get("status"), "download_url": f.get("download_url"), "play_url": f.get("play_url")}
                for f in data.get("recording_files", [])
            ]
            return json.dumps({"ok": True, "meeting_id": data.get("id"), "topic": data.get("topic"), "start_time": data.get("start_time"), "duration": data.get("duration"), "recording_files": files}, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPStatusError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _recordings_list(self, args: Dict[str, Any]) -> str:
        account_id = os.environ.get("ZOOM_ACCOUNT_ID", "")
        client_id = os.environ.get("ZOOM_CLIENT_ID", "")
        client_secret = os.environ.get("ZOOM_CLIENT_SECRET", "")
        if not (account_id and client_id and client_secret):
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET env vars required"}, indent=2, ensure_ascii=False)
        user_id = str(args.get("user_id", "me")).strip() or "me"
        from_date = args.get("from_date")
        to_date = args.get("to_date")
        page_size = int(args.get("page_size", 30))
        try:
            token = await self._get_token()
            params: Dict[str, Any] = {"page_size": min(page_size, 300)}
            if from_date:
                params["from"] = from_date
            if to_date:
                params["to"] = to_date
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{_BASE_URL}/users/{user_id}/recordings",
                    headers={"Authorization": f"Bearer {token}"},
                    params=params,
                )
            if resp.status_code != 200:
                logger.info("zoom recordings.list error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            return f"zoom.recordings.list ok\n\n```json\n{json.dumps({'ok': True, 'meetings': data.get('meetings', []), 'total_records': data.get('total_records', 0)}, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPStatusError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _recordings_transcript_download(self, args: Dict[str, Any]) -> str:
        account_id = os.environ.get("ZOOM_ACCOUNT_ID", "")
        client_id = os.environ.get("ZOOM_CLIENT_ID", "")
        client_secret = os.environ.get("ZOOM_CLIENT_SECRET", "")
        if not (account_id and client_id and client_secret):
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET env vars required"}, indent=2, ensure_ascii=False)
        download_url = str(args.get("download_url", "")).strip()
        meeting_uuid = str(args.get("meeting_uuid", "")).strip()
        if not download_url and not meeting_uuid:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "Either download_url or meeting_uuid is required"}, indent=2, ensure_ascii=False)
        try:
            token = await self._get_token()
            if not download_url:
                async with httpx.AsyncClient(timeout=30) as client:
                    resp = await client.get(
                        f"{_BASE_URL}/meetings/{meeting_uuid}/recordings",
                        headers={"Authorization": f"Bearer {token}"},
                    )
                if resp.status_code != 200:
                    logger.info("zoom recordings lookup error %s: %s", resp.status_code, resp.text[:200])
                    return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
                recording_data = resp.json()
                recording_files = recording_data.get("recording_files", [])
                transcript_file = next(
                    (f for f in recording_files if f.get("file_type") == "TRANSCRIPT"),
                    None,
                )
                if not transcript_file:
                    return json.dumps({"ok": False, "error_code": "NO_TRANSCRIPT", "message": "No transcript file found for this recording"}, indent=2, ensure_ascii=False)
                download_url = transcript_file.get("download_url", "")
            async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
                resp = await client.get(
                    download_url,
                    headers={"Authorization": f"Bearer {token}"},
                )
            if resp.status_code != 200:
                logger.info("zoom transcript download error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            transcript_text = resp.text
            return f"zoom.recordings.transcript.download ok\n\n```text\n{transcript_text[:10000]}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPStatusError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
