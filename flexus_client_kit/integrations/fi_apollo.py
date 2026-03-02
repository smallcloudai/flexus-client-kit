import json
import logging
import os
from typing import Any, Dict, List

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("apollo")

PROVIDER_NAME = "apollo"
METHOD_IDS = [
    "apollo.contacts.create.v1",
    "apollo.organizations.bulk_enrich.v1",
    "apollo.organizations.enrich.v1",
    "apollo.people.enrich.v1",
    "apollo.people.search.v1",
    "apollo.sequences.contacts.add.v1",
]

_BASE_URL = "https://api.apollo.io/v1"


class IntegrationApollo:
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
            key = os.environ.get("APOLLO_API_KEY", "")
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
        if method_id == "apollo.organizations.enrich.v1":
            return await self._organizations_enrich(args)
        if method_id == "apollo.organizations.bulk_enrich.v1":
            return await self._organizations_bulk_enrich(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _organizations_enrich(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("APOLLO_API_KEY", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "APOLLO_API_KEY env var not set"}, indent=2, ensure_ascii=False)
        domain = str(args.get("domain", "")).strip()
        if not domain:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "domain is required"}, indent=2, ensure_ascii=False)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{_BASE_URL}/organizations/enrich",
                    params={"domain": domain, "api_key": key},
                )
            if resp.status_code == 422:
                return json.dumps({"ok": False, "error_code": "NOT_FOUND", "message": f"Domain not found: {domain}"}, indent=2, ensure_ascii=False)
            if resp.status_code != 200:
                logger.info("apollo organizations_enrich error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            result = {
                "ok": True,
                "credit_note": "This call consumes API credits.",
                "organization": data.get("organization"),
            }
            return f"apollo.organizations.enrich ok\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _organizations_bulk_enrich(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("APOLLO_API_KEY", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "APOLLO_API_KEY env var not set"}, indent=2, ensure_ascii=False)
        domains: List[str] = args.get("domains", [])
        if not domains:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "domains list is required"}, indent=2, ensure_ascii=False)
        if len(domains) > 10:
            return json.dumps({"ok": False, "error_code": "INVALID_ARG", "message": "domains list must not exceed 10 items"}, indent=2, ensure_ascii=False)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{_BASE_URL}/organizations/bulk_enrich",
                    json={"api_key": key, "domains": domains},
                )
            if resp.status_code != 200:
                logger.info("apollo organizations_bulk_enrich error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            result = {
                "ok": True,
                "credit_note": "This call consumes API credits.",
                "organizations": data.get("organizations", []),
            }
            return f"apollo.organizations.bulk_enrich ok\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
