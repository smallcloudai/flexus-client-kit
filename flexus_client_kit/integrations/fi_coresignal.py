import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("coresignal")

PROVIDER_NAME = "coresignal"
METHOD_IDS = [
    "coresignal.jobs.posts.v1",
    "coresignal.companies.profile.v1",
]

_BASE_URL = "https://api.coresignal.com/cdapi/v1"


class IntegrationCoresignal:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _get_api_key(self) -> str:
        if self.rcx is not None:
            return (self.rcx.external_auth.get("coresignal") or {}).get("api_key", "")
        return self._get_api_key()

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
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "status": "available", "method_count": len(METHOD_IDS)}, indent=2, ensure_ascii=False)
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
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set CORESIGNAL_API_KEY env var."}, indent=2, ensure_ascii=False)

        if method_id == "coresignal.jobs.posts.v1":
            return await self._jobs_posts(args, api_key)
        if method_id == "coresignal.companies.profile.v1":
            return await self._companies_profile(args, api_key)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _headers(self, api_key: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def _jobs_posts(self, args: Dict[str, Any], api_key: str) -> str:
        query = str(args.get("query", "")).strip()
        limit = int(args.get("limit", 20))
        body: Dict[str, Any] = {"size": limit}
        if query:
            body["query"] = {"bool": {"must": [{"match": {"title": query}}]}}

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.post(_BASE_URL + "/job_posting/search/filter", json=body, headers=self._headers(api_key))
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            results = data if isinstance(data, list) else data.get("data", data.get("results", []))
            include_raw = bool(args.get("include_raw"))
            out: Dict[str, Any] = {"ok": True, "results": results if include_raw else [
                {
                    "title": j.get("title"),
                    "company_name": j.get("company_name"),
                    "location": j.get("location"),
                    "date_posted": j.get("date_posted") or j.get("created"),
                    "url": j.get("url"),
                }
                for j in (results if isinstance(results, list) else [])
            ]}
            summary = f"Found {len(results) if isinstance(results, list) else 1} job posting(s) from {PROVIDER_NAME}."
            return summary + "\n\n```json\n" + json.dumps(out, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _companies_profile(self, args: Dict[str, Any], api_key: str) -> str:
        company_name = str(args.get("company_name", args.get("query", ""))).strip()
        if not company_name:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "args.company_name required."}, indent=2, ensure_ascii=False)

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(
                    _BASE_URL + "/linkedin/company/search/filter",
                    params={"name": company_name},
                    headers=self._headers(api_key),
                )
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            results = data if isinstance(data, list) else data.get("data", data.get("results", data))
            include_raw = bool(args.get("include_raw"))
            out: Dict[str, Any] = {"ok": True, "results": results if include_raw else [
                {
                    "name": c.get("name"),
                    "website": c.get("website"),
                    "industry": c.get("industry"),
                    "employee_count": c.get("employee_count"),
                    "founded": c.get("founded"),
                    "description": str(c.get("description", ""))[:300],
                }
                for c in (results if isinstance(results, list) else [results])
            ]}
            summary = f"Found company profile(s) from {PROVIDER_NAME}."
            return summary + "\n\n```json\n" + json.dumps(out, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
