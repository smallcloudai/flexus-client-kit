import json
import logging
import os
from typing import Any, Dict, List

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("crossbeam")

PROVIDER_NAME = "crossbeam"
API_BASE = "https://api.crossbeam.com/v0.1"
METHOD_IDS = [
    "crossbeam.partners.list.v1",
    "crossbeam.account_mapping.overlaps.list.v1",
    "crossbeam.exports.records.get.v1",
]

_AUTH_REQUIRED_OVERLAPS = json.dumps(
    {
        "ok": False,
        "error_code": "AUTH_REQUIRED",
        "provider": PROVIDER_NAME,
        "method_id": "crossbeam.account_mapping.overlaps.list.v1",
        "message": "Account mapping overlaps endpoint structure is not fully documented. Crossbeam REST API requires Supernode plan. Check developers.crossbeam.com for current API spec.",
    },
    indent=2,
    ensure_ascii=False,
)

_AUTH_REQUIRED_EXPORTS = json.dumps(
    {
        "ok": False,
        "error_code": "AUTH_REQUIRED",
        "provider": PROVIDER_NAME,
        "method_id": "crossbeam.exports.records.get.v1",
        "message": "Exports records endpoint structure is not fully documented. Crossbeam REST API requires Supernode plan. Check developers.crossbeam.com for current API spec.",
    },
    indent=2,
    ensure_ascii=False,
)


class IntegrationCrossbeam:
    def _headers(self, api_key: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _check_credentials(self) -> str:
        key = os.environ.get("CROSSBEAM_API_KEY", "")
        if not key:
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "NO_CREDENTIALS",
                    "provider": PROVIDER_NAME,
                    "message": "CROSSBEAM_API_KEY env var not set",
                },
                indent=2,
                ensure_ascii=False,
            )
        return ""

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
            key = os.environ.get("CROSSBEAM_API_KEY", "")
            return json.dumps(
                {
                    "ok": True,
                    "provider": PROVIDER_NAME,
                    "status": "available" if key else "no_credentials",
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

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        if method_id == "crossbeam.partners.list.v1":
            return await self._partners_list(args)
        if method_id == "crossbeam.account_mapping.overlaps.list.v1":
            return await self._overlaps_list(args)
        if method_id == "crossbeam.exports.records.get.v1":
            return await self._exports_records_get(args)
        return json.dumps(
            {"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id},
            indent=2,
            ensure_ascii=False,
        )

    async def _partners_list(self, args: Dict[str, Any]) -> str:
        cred_err = self._check_credentials()
        if cred_err:
            return cred_err
        limit = int(args.get("limit", 25))
        limit = min(max(limit, 1), 100)
        page_cursor = str(args.get("page_cursor", "")).strip()
        params: Dict[str, Any] = {"limit": limit}
        if page_cursor:
            params["page_cursor"] = page_cursor
        key = os.environ.get("CROSSBEAM_API_KEY", "")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(
                    f"{API_BASE}/partners",
                    headers=self._headers(key),
                    params=params,
                )
            if resp.status_code == 401:
                return json.dumps(
                    {
                        "ok": False,
                        "error_code": "AUTH_ERROR",
                        "provider": PROVIDER_NAME,
                        "message": "Invalid CROSSBEAM_API_KEY. Check credentials.",
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            if resp.status_code == 403:
                return json.dumps(
                    {
                        "ok": False,
                        "error_code": "ENTITLEMENT_MISSING",
                        "provider": PROVIDER_NAME,
                        "message": "Crossbeam REST API requires Supernode plan.",
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            if resp.status_code != 200:
                logger.info("crossbeam partners_list error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps(
                    {
                        "ok": False,
                        "error_code": "PROVIDER_ERROR",
                        "provider": PROVIDER_NAME,
                        "status": resp.status_code,
                        "detail": resp.text[:500],
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            try:
                data = resp.json()
            except json.JSONDecodeError as e:
                logger.info("crossbeam partners_list JSON decode error: %s", e)
                return json.dumps(
                    {"ok": False, "error_code": "INVALID_JSON", "provider": PROVIDER_NAME},
                    indent=2,
                    ensure_ascii=False,
                )
            items_raw = data.get("items") or data.get("partners") or data.get("data") or []
            pagination = data.get("pagination") or {}
            next_cursor = pagination.get("next_page_cursor") or pagination.get("next_cursor") or ""
            normalized: List[Dict[str, Any]] = []
            for it in items_raw:
                normalized.append({
                    "id": it.get("id"),
                    "name": it.get("name"),
                    "account_count": it.get("account_count"),
                    "status": it.get("status"),
                    "created_at": it.get("created_at"),
                })
            result = {
                "ok": True,
                "provider": PROVIDER_NAME,
                "items": normalized,
                "next_page_cursor": next_cursor if next_cursor else None,
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except httpx.TimeoutException as e:
            logger.info("crossbeam partners_list timeout: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("crossbeam partners_list HTTP error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "detail": str(e)},
                indent=2,
                ensure_ascii=False,
            )

    async def _overlaps_list(self, args: Dict[str, Any]) -> str:
        cred_err = self._check_credentials()
        if cred_err:
            return cred_err
        partner_id = str(args.get("partner_id", "")).strip()
        if not partner_id:
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "MISSING_ARG",
                    "provider": PROVIDER_NAME,
                    "message": "partner_id is required",
                },
                indent=2,
                ensure_ascii=False,
            )
        limit = int(args.get("limit", 25))
        limit = min(max(limit, 1), 100)
        page_cursor = str(args.get("page_cursor", "")).strip()
        population_id = str(args.get("population_id", "")).strip()
        params: Dict[str, Any] = {"limit": limit, "partner_id": partner_id}
        if page_cursor:
            params["page_cursor"] = page_cursor
        if population_id:
            params["population_id"] = population_id
        key = os.environ.get("CROSSBEAM_API_KEY", "")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(
                    f"{API_BASE}/account-mapping/overlaps",
                    headers=self._headers(key),
                    params=params,
                )
            if resp.status_code == 404:
                return _AUTH_REQUIRED_OVERLAPS
            if resp.status_code == 401:
                return json.dumps(
                    {
                        "ok": False,
                        "error_code": "AUTH_ERROR",
                        "provider": PROVIDER_NAME,
                        "message": "Invalid CROSSBEAM_API_KEY.",
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            if resp.status_code == 403:
                return json.dumps(
                    {
                        "ok": False,
                        "error_code": "ENTITLEMENT_MISSING",
                        "provider": PROVIDER_NAME,
                        "message": "Account mapping requires Supernode plan.",
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            if resp.status_code != 200:
                logger.info("crossbeam overlaps_list error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps(
                    {
                        "ok": False,
                        "error_code": "PROVIDER_ERROR",
                        "provider": PROVIDER_NAME,
                        "status": resp.status_code,
                        "detail": resp.text[:500],
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            try:
                data = resp.json()
            except json.JSONDecodeError as e:
                logger.info("crossbeam overlaps_list JSON decode error: %s", e)
                return json.dumps(
                    {"ok": False, "error_code": "INVALID_JSON", "provider": PROVIDER_NAME},
                    indent=2,
                    ensure_ascii=False,
                )
            items_raw = data.get("items") or data.get("overlaps") or data.get("data") or []
            pagination = data.get("pagination") or {}
            next_cursor = pagination.get("next_page_cursor") or pagination.get("next_cursor") or ""
            normalized: List[Dict[str, Any]] = []
            for it in items_raw:
                normalized.append({
                    "account_name": it.get("account_name") or it.get("name"),
                    "your_crm_id": it.get("your_crm_id") or it.get("crm_id"),
                    "partner_crm_id": it.get("partner_crm_id") or it.get("partner_id"),
                    "overlap_type": it.get("overlap_type") or it.get("type"),
                    "partner_name": it.get("partner_name") or it.get("partner"),
                })
            result = {
                "ok": True,
                "provider": PROVIDER_NAME,
                "items": normalized,
                "next_page_cursor": next_cursor if next_cursor else None,
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except httpx.TimeoutException as e:
            logger.info("crossbeam overlaps_list timeout: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("crossbeam overlaps_list HTTP error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "detail": str(e)},
                indent=2,
                ensure_ascii=False,
            )

    async def _exports_records_get(self, args: Dict[str, Any]) -> str:
        cred_err = self._check_credentials()
        if cred_err:
            return cred_err
        export_id = str(args.get("export_id", "")).strip()
        if not export_id:
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "MISSING_ARG",
                    "provider": PROVIDER_NAME,
                    "message": "export_id is required",
                },
                indent=2,
                ensure_ascii=False,
            )
        limit = int(args.get("limit", 50))
        limit = min(max(limit, 1), 100)
        page_cursor = str(args.get("page_cursor", "")).strip()
        params: Dict[str, Any] = {"limit": limit}
        if page_cursor:
            params["page_cursor"] = page_cursor
        key = os.environ.get("CROSSBEAM_API_KEY", "")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(
                    f"{API_BASE}/exports/{export_id}/records",
                    headers=self._headers(key),
                    params=params,
                )
            if resp.status_code == 404:
                return _AUTH_REQUIRED_EXPORTS
            if resp.status_code == 401:
                return json.dumps(
                    {
                        "ok": False,
                        "error_code": "AUTH_ERROR",
                        "provider": PROVIDER_NAME,
                        "message": "Invalid CROSSBEAM_API_KEY.",
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            if resp.status_code == 403:
                return json.dumps(
                    {
                        "ok": False,
                        "error_code": "ENTITLEMENT_MISSING",
                        "provider": PROVIDER_NAME,
                        "message": "Exports require Supernode plan.",
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            if resp.status_code != 200:
                logger.info("crossbeam exports_records_get error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps(
                    {
                        "ok": False,
                        "error_code": "PROVIDER_ERROR",
                        "provider": PROVIDER_NAME,
                        "status": resp.status_code,
                        "detail": resp.text[:500],
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            try:
                data = resp.json()
            except json.JSONDecodeError as e:
                logger.info("crossbeam exports_records_get JSON decode error: %s", e)
                return json.dumps(
                    {"ok": False, "error_code": "INVALID_JSON", "provider": PROVIDER_NAME},
                    indent=2,
                    ensure_ascii=False,
                )
            records_raw = data.get("records") or data.get("items") or data.get("data") or []
            if isinstance(records_raw, dict):
                records_raw = list(records_raw.values()) if records_raw else []
            records = list(records_raw)[:limit]
            pagination = data.get("pagination") or {}
            next_cursor = pagination.get("next_page_cursor") or pagination.get("next_cursor") or ""
            result = {
                "ok": True,
                "provider": PROVIDER_NAME,
                "export_id": export_id,
                "records": records,
                "next_page_cursor": next_cursor if next_cursor else None,
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except httpx.TimeoutException as e:
            logger.info("crossbeam exports_records_get timeout: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("crossbeam exports_records_get HTTP error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "detail": str(e)},
                indent=2,
                ensure_ascii=False,
            )
