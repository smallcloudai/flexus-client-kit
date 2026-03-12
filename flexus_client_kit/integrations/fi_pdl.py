import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("pdl")

PROVIDER_NAME = "pdl"
METHOD_IDS = [
    "pdl.company.enrich.v1",
    "pdl.person.enrich.v1",
]

_BASE_URL = "https://api.peopledatalabs.com/v5"


class IntegrationPdl:
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
            key = os.environ.get("PDL_API_KEY", "")
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
        if method_id == "pdl.company.enrich.v1":
            return await self._company_enrich(args)
        if method_id == "pdl.person.enrich.v1":
            return await self._person_enrich(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _company_enrich(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("PDL_API_KEY", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "PDL_API_KEY env var not set"}, indent=2, ensure_ascii=False)
        domain = str(args.get("domain", "")).strip()
        name = str(args.get("name", "")).strip()
        ticker = str(args.get("ticker", "")).strip()
        include_raw = bool(args.get("include_raw", False))
        if not domain and not name and not ticker:
            return json.dumps({"ok": False, "error_code": "MISSING_ARGS", "message": "At least one of domain/name/ticker is required"}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {"pretty": "true"}
        if domain:
            params["website"] = domain
        if name:
            params["name"] = name
        if ticker:
            params["ticker"] = ticker
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{_BASE_URL}/company/enrich",
                    headers={"X-Api-Key": key},
                    params=params,
                )
            if resp.status_code == 404:
                return json.dumps({"ok": False, "error_code": "NOT_FOUND", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
            if resp.status_code == 402:
                return json.dumps({"ok": False, "error_code": "CREDITS_EXHAUSTED", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
            if resp.status_code != 200:
                logger.info("pdl error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            result: Dict[str, Any] = {
                "ok": True,
                "credit_note": "1 PDL credit used",
                "provider": PROVIDER_NAME,
                "data": {
                    "name": data.get("name"),
                    "website": data.get("website"),
                    "industry": data.get("industry"),
                    "employee_count": data.get("employee_count"),
                    "revenue": data.get("inferred_revenue"),
                    "location": data.get("location"),
                    "tech": data.get("tech"),
                },
            }
            if include_raw:
                result["raw"] = data
            return f"pdl.company.enrich ok\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _person_enrich(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("PDL_API_KEY", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "PDL_API_KEY env var not set"}, indent=2, ensure_ascii=False)
        email = str(args.get("email", "")).strip()
        name = str(args.get("name", "")).strip()
        company = str(args.get("company", "")).strip()
        location = str(args.get("location", "")).strip()
        profile = str(args.get("profile", "")).strip()
        include_raw = bool(args.get("include_raw", False))
        if not email and not name and not company and not location and not profile:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "At least one of email/name/company/location/profile is required"}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {"pretty": "true"}
        if email:
            params["email"] = email
        if name:
            params["name"] = name
        if company:
            params["company"] = company
        if location:
            params["location"] = location
        if profile:
            params["profile"] = profile
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{_BASE_URL}/person/enrich",
                    headers={"X-Api-Key": key},
                    params=params,
                )
            if resp.status_code == 404:
                return json.dumps({"ok": False, "error_code": "NOT_FOUND", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
            if resp.status_code == 402:
                return json.dumps({"ok": False, "error_code": "CREDITS_EXHAUSTED", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
            if resp.status_code != 200:
                logger.info("pdl error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            inner = data.get("data") or data
            result: Dict[str, Any] = {
                "ok": True,
                "credit_note": "This call consumes API credits.",
                "provider": PROVIDER_NAME,
                "data": {
                    "id": inner.get("id"),
                    "full_name": inner.get("full_name"),
                    "email": inner.get("email") or inner.get("work_email"),
                    "job_title": inner.get("job_title"),
                    "company": inner.get("job_company_name"),
                    "location": inner.get("location"),
                    "linkedin_url": inner.get("linkedin_url"),
                    "likelihood": data.get("likelihood"),
                },
            }
            if include_raw:
                result["raw"] = data
            return f"pdl.person.enrich ok\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
