import asyncio
import base64
import json
import logging
import os
from typing import Any, Dict, List

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("bombora")

PROVIDER_NAME = "bombora"
METHOD_IDS = [
    "bombora.companysurge.company_scores.get.v1",
    "bombora.companysurge.topics.list.v1",
]

_BASE_URL = "https://sentry.bombora.com"
_POLL_INTERVAL_S = 20
_MAX_POLL_ATTEMPTS = 3


class IntegrationBombora:
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
            client_id = os.environ.get("BOMBORA_CLIENT_ID", "")
            client_secret = os.environ.get("BOMBORA_CLIENT_SECRET", "")
            return json.dumps({
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "available" if (client_id and client_secret) else "no_credentials",
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
        if method_id == "bombora.companysurge.topics.list.v1":
            return await self._topics_list(args)
        if method_id == "bombora.companysurge.company_scores.get.v1":
            return await self._company_scores_get(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _get_token(self, client: httpx.AsyncClient) -> str:
        """Return Basic auth token (base64 of client_id:client_secret).

        Bombora Surge API uses HTTP Basic auth — this helper encodes the
        credentials and returns the token string ready for the Authorization
        header.  The client param is accepted for interface consistency with
        OAuth2-style helpers used in other integrations.
        """
        client_id = os.environ.get("BOMBORA_CLIENT_ID", "")
        client_secret = os.environ.get("BOMBORA_CLIENT_SECRET", "")
        raw = f"{client_id}:{client_secret}".encode()
        return base64.b64encode(raw).decode()

    def _build_headers(self, token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Basic {token}",
            "Referer": "bombora.com",
        }

    def _check_credentials(self) -> str:
        if not os.environ.get("BOMBORA_CLIENT_ID", "") or not os.environ.get("BOMBORA_CLIENT_SECRET", ""):
            return json.dumps({
                "ok": False,
                "error_code": "NO_CREDENTIALS",
                "message": "BOMBORA_CLIENT_ID and BOMBORA_CLIENT_SECRET env vars not set",
            }, indent=2, ensure_ascii=False)
        return ""

    async def _topics_list(self, args: Dict[str, Any]) -> str:
        cred_err = self._check_credentials()
        if cred_err:
            return cred_err
        limit = int(args.get("limit", 50))
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                token = await self._get_token(client)
                resp = await client.get(
                    f"{_BASE_URL}/v2/cmp/GetMyTopics",
                    headers=self._build_headers(token),
                )
            if resp.status_code == 401:
                return json.dumps({
                    "ok": False,
                    "error_code": "AUTH_ERROR",
                    "message": "Invalid Bombora credentials. Check BOMBORA_CLIENT_ID and BOMBORA_CLIENT_SECRET.",
                }, indent=2, ensure_ascii=False)
            if resp.status_code == 403:
                return json.dumps({
                    "ok": False,
                    "error_code": "ENTITLEMENT_MISSING",
                    "provider": PROVIDER_NAME,
                    "message": "This provider requires a contract/plan entitlement. Contact Bombora sales.",
                }, indent=2, ensure_ascii=False)
            if resp.status_code != 200:
                logger.info("bombora topics_list error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({
                    "ok": False,
                    "error_code": "PROVIDER_ERROR",
                    "status": resp.status_code,
                    "detail": resp.text[:500],
                }, indent=2, ensure_ascii=False)
            data = resp.json()
            topics: List[Dict[str, Any]] = (data.get("Topics") or [])[:limit]
            result = {
                "ok": True,
                "provider": PROVIDER_NAME,
                "total_returned": len(topics),
                "limit": limit,
                "topics": [
                    {"id": t.get("Id"), "name": t.get("Name"), "description": t.get("Description")}
                    for t in topics
                ],
            }
            return f"bombora.companysurge.topics.list ok\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _company_scores_get(self, args: Dict[str, Any]) -> str:
        cred_err = self._check_credentials()
        if cred_err:
            return cred_err
        domains = args.get("domains") or []
        if not domains:
            return json.dumps({
                "ok": False,
                "error_code": "MISSING_ARG",
                "message": "domains is required (list of domain strings)",
            }, indent=2, ensure_ascii=False)
        topic_ids = args.get("topic_ids") or []
        body: Dict[str, Any] = {
            "Domains": list(domains),
            "OutputFormat": "json",
        }
        if topic_ids:
            body["Topics"] = [int(t) for t in topic_ids]
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                token = await self._get_token(client)
                headers = self._build_headers(token)
                create_resp = await client.post(
                    f"{_BASE_URL}/v4/Surge/Create",
                    headers={**headers, "Content-Type": "application/json"},
                    json=body,
                )
                if create_resp.status_code == 401:
                    return json.dumps({
                        "ok": False,
                        "error_code": "AUTH_ERROR",
                        "message": "Invalid Bombora credentials. Check BOMBORA_CLIENT_ID and BOMBORA_CLIENT_SECRET.",
                    }, indent=2, ensure_ascii=False)
                if create_resp.status_code == 403:
                    return json.dumps({
                        "ok": False,
                        "error_code": "ENTITLEMENT_MISSING",
                        "provider": PROVIDER_NAME,
                        "message": "This provider requires a contract/plan entitlement. Contact Bombora sales.",
                    }, indent=2, ensure_ascii=False)
                if create_resp.status_code != 200:
                    logger.info("bombora surge_create error %s: %s", create_resp.status_code, create_resp.text[:200])
                    return json.dumps({
                        "ok": False,
                        "error_code": "PROVIDER_ERROR",
                        "status": create_resp.status_code,
                        "detail": create_resp.text[:500],
                    }, indent=2, ensure_ascii=False)
                create_data = create_resp.json()
                if not create_data.get("Success"):
                    return json.dumps({
                        "ok": False,
                        "error_code": "REPORT_CREATE_FAILED",
                        "message": create_data.get("Message", ""),
                    }, indent=2, ensure_ascii=False)
                job_id = str(create_data.get("Id", ""))
                for _ in range(_MAX_POLL_ATTEMPTS):
                    await asyncio.sleep(_POLL_INTERVAL_S)
                    result_resp = await client.get(
                        f"{_BASE_URL}/v2/Surge/TryGetResult",
                        headers=headers,
                        params={"id": job_id},
                    )
                    if result_resp.status_code != 200:
                        logger.info("bombora surge_result error %s: %s", result_resp.status_code, result_resp.text[:200])
                        break
                    content_type = result_resp.headers.get("content-type", "")
                    if "octet-stream" in content_type or "json" in content_type:
                        try:
                            report_data = result_resp.json()
                        except (json.JSONDecodeError, ValueError):
                            report_data = result_resp.text[:2000]
                        result = {
                            "ok": True,
                            "provider": PROVIDER_NAME,
                            "job_id": job_id,
                            "domains_queried": list(domains),
                            "results": report_data,
                        }
                        return f"bombora.companysurge.company_scores.get ok\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
                    poll_data = result_resp.json()
                    if poll_data.get("Success") is True:
                        result = {
                            "ok": True,
                            "provider": PROVIDER_NAME,
                            "job_id": job_id,
                            "domains_queried": list(domains),
                            "results": poll_data,
                        }
                        return f"bombora.companysurge.company_scores.get ok\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
            return json.dumps({
                "ok": True,
                "status": "processing",
                "provider": PROVIDER_NAME,
                "job_id": job_id,
                "domains_queried": list(domains),
                "message": (
                    "Bombora report is still processing (typically takes 10-15 minutes). "
                    "Re-call with op=call, method_id=bombora.companysurge.company_scores.get.v1 "
                    "and job_id to retrieve results when ready."
                ),
                "check_url": f"{_BASE_URL}/v2/Surge/TryGetResult?id={job_id}",
            }, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
