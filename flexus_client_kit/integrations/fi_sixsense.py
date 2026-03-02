import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("sixsense")

PROVIDER_NAME = "sixsense"
METHOD_IDS = [
    "sixsense.company.identification.v1",
    "sixsense.people.search.v1",
]

_BASE_EPSILON = "https://epsilon.6sense.com/v3"
_BASE_API = "https://api.6sense.com"


class IntegrationSixsense:
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
            key = os.environ.get("SIXSENSE_API_KEY", "")
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
        if method_id == "sixsense.company.identification.v1":
            return await self._company_identification(args)
        if method_id == "sixsense.people.search.v1":
            return await self._people_search(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _get_key(self) -> str:
        return os.environ.get("SIXSENSE_API_KEY", "")

    def _auth_headers(self, key: str) -> Dict[str, str]:
        return {"Authorization": f"Token {key}"}

    def _handle_error_status(self, status: int, text: str) -> str | None:
        if status == 401:
            return json.dumps({
                "ok": False,
                "error_code": "AUTH_ERROR",
                "provider": PROVIDER_NAME,
                "message": "API key invalid or expired",
            }, indent=2, ensure_ascii=False)
        if status == 402:
            return json.dumps({
                "ok": False,
                "error_code": "QUOTA_EXHAUSTED",
                "provider": PROVIDER_NAME,
                "message": "API credit quota exhausted. Contact your 6sense CSM to top-up.",
            }, indent=2, ensure_ascii=False)
        if status == 403:
            return json.dumps({
                "ok": False,
                "error_code": "ENTITLEMENT_MISSING",
                "provider": PROVIDER_NAME,
                "message": "This API requires a 6sense contract/plan entitlement. Contact 6sense sales.",
            }, indent=2, ensure_ascii=False)
        if status == 429:
            return json.dumps({
                "ok": False,
                "error_code": "RATE_LIMITED",
                "provider": PROVIDER_NAME,
                "message": "Rate limit exceeded (100 req/min). Please retry later.",
            }, indent=2, ensure_ascii=False)
        if status != 200:
            logger.info("sixsense error %s: %s", status, text[:200])
            return json.dumps({
                "ok": False,
                "error_code": "PROVIDER_ERROR",
                "status": status,
                "detail": text[:500],
            }, indent=2, ensure_ascii=False)
        return None

    async def _company_identification(self, args: Dict[str, Any]) -> str:
        key = self._get_key()
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "SIXSENSE_API_KEY env var not set"}, indent=2, ensure_ascii=False)

        domain = str(args.get("domain", "")).strip()
        company_name = str(args.get("company_name", "")).strip()
        ip = str(args.get("ip", "")).strip()

        if not domain and not company_name and not ip:
            return json.dumps({
                "ok": False,
                "error_code": "MISSING_ARGS",
                "message": "At least one of: domain, company_name, ip is required",
            }, indent=2, ensure_ascii=False)

        # Company Identification API v3 — identifies companies by IP of the request.
        # For server-side use: pass ip/domain/company as query params (6sense docs note
        # this API is primarily client-side; server-side results may vary by plan).
        params: Dict[str, str] = {}
        if ip:
            params["ip"] = ip
        if domain:
            params["domain"] = domain
        if company_name:
            params["company"] = company_name

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{_BASE_EPSILON}/company/details",
                    headers=self._auth_headers(key),
                    params=params,
                )
            err = self._handle_error_status(resp.status_code, resp.text)
            if err:
                return err
            data = resp.json()
            return f"sixsense.company.identification ok\n\n```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _people_search(self, args: Dict[str, Any]) -> str:
        key = self._get_key()
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "SIXSENSE_API_KEY env var not set"}, indent=2, ensure_ascii=False)

        domain = str(args.get("domain", "")).strip()
        company_name = str(args.get("company_name", "")).strip()
        title = str(args.get("title", "")).strip()
        limit = int(args.get("limit", 10))

        # People Search API v2 — POST https://api.6sense.com/v2/search/people
        # Accepts arrays for domain, jobTitle; pageSize controls result count.
        payload: Dict[str, Any] = {"pageNo": 1, "pageSize": min(limit, 1000)}
        if domain:
            payload["domain"] = [domain]
        if company_name:
            payload["companyName"] = [company_name]
        if title:
            payload["jobTitle"] = [title]

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{_BASE_API}/v2/search/people",
                    headers={**self._auth_headers(key), "Content-Type": "application/json"},
                    json=payload,
                )
            err = self._handle_error_status(resp.status_code, resp.text)
            if err:
                return err
            data = resp.json()
            return f"sixsense.people.search ok\n\n```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
