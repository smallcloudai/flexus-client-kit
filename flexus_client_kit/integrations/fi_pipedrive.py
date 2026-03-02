import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("pipedrive")

PROVIDER_NAME = "pipedrive"
METHOD_IDS = [
    "pipedrive.deals.list.v1",
    "pipedrive.deals.search.v1",
    "pipedrive.itemsearch.search.v1",
    "pipedrive.organizations.search.v1",
]

_BASE_URL = "https://api.pipedrive.com/v1"


class IntegrationPipedrive:
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
            key = os.environ.get("PIPEDRIVE_API_TOKEN", "")
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
        if method_id == "pipedrive.organizations.search.v1":
            return await self._organizations_search(args)
        if method_id == "pipedrive.deals.search.v1":
            return await self._deals_search(args)
        if method_id == "pipedrive.deals.list.v1":
            return await self._deals_list(args)
        if method_id == "pipedrive.itemsearch.search.v1":
            return await self._itemsearch_search(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _organizations_search(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("PIPEDRIVE_API_TOKEN", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "PIPEDRIVE_API_TOKEN env var not set"}, indent=2, ensure_ascii=False)
        term = str(args.get("term", "")).strip()
        if not term:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "term is required"}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {
            "api_token": key,
            "term": term,
            "limit": int(args.get("limit", 10)),
            "start": int(args.get("start", 0)),
            "exact_match": str(args.get("exact_match", False)).lower(),
        }
        if args.get("fields"):
            params["fields"] = str(args["fields"])
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(f"{_BASE_URL}/organizations/search", params=params)
            if resp.status_code != 200:
                logger.info("pipedrive organizations_search error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            result = {
                "ok": True,
                "items": (data.get("data") or {}).get("items", []),
                "result_score": (data.get("data") or {}).get("result_score", 0),
            }
            return f"pipedrive.organizations.search ok\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _deals_search(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("PIPEDRIVE_API_TOKEN", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "PIPEDRIVE_API_TOKEN env var not set"}, indent=2, ensure_ascii=False)
        term = str(args.get("term", "")).strip()
        if not term:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "term is required"}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {
            "api_token": key,
            "term": term,
            "limit": int(args.get("limit", 10)),
            "start": int(args.get("start", 0)),
            "exact_match": str(args.get("exact_match", False)).lower(),
        }
        if args.get("fields"):
            params["fields"] = str(args["fields"])
        if args.get("status"):
            params["status"] = str(args["status"])
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(f"{_BASE_URL}/deals/search", params=params)
            if resp.status_code != 200:
                logger.info("pipedrive deals_search error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            result = {
                "ok": True,
                "items": (data.get("data") or {}).get("items", []),
                "result_score": (data.get("data") or {}).get("result_score", 0),
            }
            return f"pipedrive.deals.search ok\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _deals_list(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("PIPEDRIVE_API_TOKEN", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "PIPEDRIVE_API_TOKEN env var not set"}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {
            "api_token": key,
            "limit": int(args.get("limit", 20)),
            "start": int(args.get("start", 0)),
        }
        if args.get("status"):
            params["status"] = str(args["status"])
        if args.get("user_id") is not None:
            params["user_id"] = int(args["user_id"])
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(f"{_BASE_URL}/deals", params=params)
            if resp.status_code != 200:
                logger.info("pipedrive deals_list error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            items = (data.get("data") or []) if isinstance(data.get("data"), list) else []
            result = {"ok": True, "items": items}
            return f"pipedrive.deals.list ok\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _itemsearch_search(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("PIPEDRIVE_API_TOKEN", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "PIPEDRIVE_API_TOKEN env var not set"}, indent=2, ensure_ascii=False)
        term = str(args.get("term", "")).strip()
        if not term:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "term is required"}, indent=2, ensure_ascii=False)
        limit = int(args.get("limit", 10))
        limit = min(max(limit, 1), 500)
        params: Dict[str, Any] = {
            "api_token": key,
            "term": term,
            "exact_match": str(args.get("exact_match", False)).lower(),
            "limit": limit,
            "start": int(args.get("start", 0)),
        }
        if args.get("item_types"):
            params["item_types"] = str(args["item_types"])
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(f"{_BASE_URL}/itemSearch", params=params)
            if resp.status_code != 200:
                logger.info("pipedrive itemsearch_search error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            items = (data.get("data") or {}).get("items", [])
            result = {"ok": True, "items": items}
            return f"pipedrive.itemsearch.search ok\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
