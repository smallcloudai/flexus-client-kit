import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("hasdata")

PROVIDER_NAME = "hasdata"
METHOD_IDS = [
    "hasdata.indeed.jobs.v1",
    "hasdata.glassdoor.jobs.v1",
]

_BASE_URL = "https://api.hasdata.com"


class IntegrationHasdata:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _get_api_key(self) -> str:
        if self.rcx is not None:
            return (self.rcx.external_auth.get("hasdata") or {}).get("api_key", "")
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
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set HASDATA_API_KEY env var."}, indent=2, ensure_ascii=False)

        if method_id == "hasdata.indeed.jobs.v1":
            return await self._indeed_jobs(args, api_key)
        if method_id == "hasdata.glassdoor.jobs.v1":
            return await self._glassdoor_jobs(args, api_key)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _headers(self, api_key: str) -> Dict[str, str]:
        return {
            "x-api-key": api_key,
            "Content-Type": "application/json",
        }

    async def _indeed_jobs(self, args: Dict[str, Any], api_key: str) -> str:
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "args.query required."}, indent=2, ensure_ascii=False)

        geo = args.get("geo") or {}
        if isinstance(geo, str):
            geo = {"country": geo}
        location = str(geo.get("city", geo.get("country", "United States")))
        limit = int(args.get("limit", 20))

        params: Dict[str, Any] = {
            "keyword": query,
            "location": location,
            "num": limit,
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.get(_BASE_URL + "/scrape/indeed/jobs", params=params, headers=self._headers(api_key))
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            results = data.get("jobs", data.get("results", data.get("data", [])))
            include_raw = bool(args.get("include_raw"))
            out: Dict[str, Any] = {"ok": True, "source": "indeed", "results": results if include_raw else [
                {
                    "title": j.get("title"),
                    "company": j.get("company"),
                    "location": j.get("location"),
                    "salary": j.get("salary"),
                    "date_posted": j.get("date") or j.get("datePosted"),
                    "url": j.get("url") or j.get("link"),
                }
                for j in (results if isinstance(results, list) else [])
            ]}
            summary = f"Found {len(results) if isinstance(results, list) else 1} Indeed job(s) from {PROVIDER_NAME}."
            return summary + "\n\n```json\n" + json.dumps(out, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _glassdoor_jobs(self, args: Dict[str, Any], api_key: str) -> str:
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "args.query required."}, indent=2, ensure_ascii=False)

        geo = args.get("geo") or {}
        if isinstance(geo, str):
            geo = {"country": geo}
        location = str(geo.get("city", geo.get("country", "United States")))
        limit = int(args.get("limit", 20))

        params: Dict[str, Any] = {
            "keyword": query,
            "location": location,
            "num": limit,
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.get(_BASE_URL + "/scrape/glassdoor/jobs", params=params, headers=self._headers(api_key))
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            results = data.get("jobs", data.get("results", data.get("data", [])))
            include_raw = bool(args.get("include_raw"))
            out: Dict[str, Any] = {"ok": True, "source": "glassdoor", "results": results if include_raw else [
                {
                    "title": j.get("title"),
                    "company": j.get("company") or j.get("employerName"),
                    "location": j.get("location"),
                    "salary": j.get("salary") or j.get("salaryRange"),
                    "date_posted": j.get("date") or j.get("datePosted"),
                    "url": j.get("url") or j.get("link"),
                }
                for j in (results if isinstance(results, list) else [])
            ]}
            summary = f"Found {len(results) if isinstance(results, list) else 1} Glassdoor job(s) from {PROVIDER_NAME}."
            return summary + "\n\n```json\n" + json.dumps(out, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
