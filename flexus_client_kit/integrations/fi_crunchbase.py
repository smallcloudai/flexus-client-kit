import json
import logging
import os
from typing import Any, Dict, List

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("crunchbase")

PROVIDER_NAME = "crunchbase"
METHOD_IDS = [
    "crunchbase.organizations.lookup.v1",
    "crunchbase.organizations.search.v1",
]

_BASE_URL = "https://api.crunchbase.com/api/v4"

_DEFAULT_LOOKUP_FIELDS = [
    "short_description",
    "num_employees_enum",
    "revenue_range",
    "funding_total",
    "last_funding_type",
    "founded_on",
    "location_identifiers",
]

_DEFAULT_SEARCH_FIELDS = [
    "identifier",
    "short_description",
    "num_employees_enum",
    "funding_total",
]


class IntegrationCrunchbase:
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
            key = os.environ.get("CRUNCHBASE_API_KEY", "")
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
        if method_id == "crunchbase.organizations.lookup.v1":
            return await self._organizations_lookup(args)
        if method_id == "crunchbase.organizations.search.v1":
            return await self._organizations_search(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _organizations_lookup(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("CRUNCHBASE_API_KEY", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "CRUNCHBASE_API_KEY env var not set"}, indent=2, ensure_ascii=False)
        permalink = str(args.get("permalink", "")).strip()
        if not permalink:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "permalink is required"}, indent=2, ensure_ascii=False)
        field_ids: List[str] = args.get("field_ids") or _DEFAULT_LOOKUP_FIELDS
        params = {
            "user_key": key,
            "field_ids": ",".join(field_ids),
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{_BASE_URL}/entities/organizations/{permalink}",
                    params=params,
                )
            if resp.status_code == 404:
                return json.dumps({"ok": False, "error_code": "NOT_FOUND", "permalink": permalink}, indent=2, ensure_ascii=False)
            if resp.status_code != 200:
                logger.info("crunchbase lookup error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            properties = data.get("properties", {})
            return f"crunchbase.organizations.lookup ok\n\n```json\n{json.dumps({'ok': True, 'permalink': permalink, 'properties': properties}, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _organizations_search(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("CRUNCHBASE_API_KEY", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "CRUNCHBASE_API_KEY env var not set"}, indent=2, ensure_ascii=False)
        limit = int(args.get("limit") or 10)
        predicates = [
            {
                "type": "predicate",
                "field_id": "facet_ids",
                "operator_id": "includes",
                "values": ["company"],
            },
        ]
        name = str(args.get("name", "")).strip()
        if name:
            predicates.append({
                "type": "predicate",
                "field_id": "identifier",
                "operator_id": "contains",
                "values": [name],
            })
        location = str(args.get("location", "")).strip()
        if location:
            predicates.append({
                "type": "predicate",
                "field_id": "location_identifiers",
                "operator_id": "includes",
                "values": [location],
            })
        num_employees_min = args.get("num_employees_min")
        if num_employees_min is not None:
            predicates.append({
                "type": "predicate",
                "field_id": "num_employees_enum",
                "operator_id": "gte",
                "values": [num_employees_min],
            })
        num_employees_max = args.get("num_employees_max")
        if num_employees_max is not None:
            predicates.append({
                "type": "predicate",
                "field_id": "num_employees_enum",
                "operator_id": "lte",
                "values": [num_employees_max],
            })
        funding_total_min = args.get("funding_total_min")
        if funding_total_min is not None:
            predicates.append({
                "type": "predicate",
                "field_id": "funding_total",
                "operator_id": "gte",
                "values": [funding_total_min],
            })
        body = {
            "field_ids": _DEFAULT_SEARCH_FIELDS,
            "query": predicates,
            "limit": limit,
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{_BASE_URL}/searches/organizations",
                    params={"user_key": key},
                    json=body,
                )
            if resp.status_code != 200:
                logger.info("crunchbase search error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            entities = [e.get("properties", {}) for e in data.get("entities", [])]
            return f"crunchbase.organizations.search ok\n\n```json\n{json.dumps({'ok': True, 'count': len(entities), 'results': entities}, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
