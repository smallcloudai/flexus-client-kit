import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("stackexchange")

PROVIDER_NAME = "stackexchange"
METHOD_IDS = [
    "stackexchange.questions.list.v1",
    "stackexchange.tags.info.v1",
    "stackexchange.tags.related.v1",
]

_BASE_URL = "https://api.stackexchange.com/2.3"


class IntegrationStackexchange:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _get_api_key(self) -> str:
        if self.rcx is not None:
            return (self.rcx.external_auth.get("stackexchange") or {}).get("api_key", "")
        return os.environ.get("STACKEXCHANGE_KEY", "")

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
        if method_id == "stackexchange.questions.list.v1":
            return await self._questions_list(args)
        if method_id == "stackexchange.tags.info.v1":
            return await self._tags_info(args)
        if method_id == "stackexchange.tags.related.v1":
            return await self._tags_related(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _base_params(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {"site": "stackoverflow"}
        key = self._get_api_key()
        if key:
            params["key"] = key
        return params

    async def _questions_list(self, args: Dict[str, Any]) -> str:
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "args.query required."}, indent=2, ensure_ascii=False)
        limit = min(int(args.get("limit", 20)), 100)
        params = self._base_params()
        params.update({"q": query, "sort": "relevance", "order": "desc", "pagesize": limit, "filter": "withbody"})
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(_BASE_URL + "/search/advanced", params=params)
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            items = data.get("items", [])
            include_raw = bool(args.get("include_raw"))
            out: Dict[str, Any] = {"ok": True, "quota_remaining": data.get("quota_remaining"), "results": items if include_raw else [
                {
                    "title": q.get("title"),
                    "score": q.get("score"),
                    "answer_count": q.get("answer_count"),
                    "view_count": q.get("view_count"),
                    "tags": q.get("tags", []),
                    "creation_date": q.get("creation_date"),
                    "link": q.get("link"),
                }
                for q in items
            ]}
            summary = f"Found {len(items)} question(s) from Stack Overflow for '{query}'."
            return summary + "\n\n```json\n" + json.dumps(out, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _tags_info(self, args: Dict[str, Any]) -> str:
        query = str(args.get("query", "")).strip().replace(" ", "-")
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "args.query required (tag name)."}, indent=2, ensure_ascii=False)
        params = self._base_params()
        params["filter"] = "default"
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(f"{_BASE_URL}/tags/{query}/info", params=params)
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            items = data.get("items", [])
            include_raw = bool(args.get("include_raw"))
            out: Dict[str, Any] = {"ok": True, "results": items if include_raw else [
                {
                    "name": t.get("name"),
                    "count": t.get("count"),
                    "is_moderator_only": t.get("is_moderator_only"),
                    "is_required": t.get("is_required"),
                }
                for t in items
            ]}
            summary = f"Tag info for '{query}' from Stack Overflow."
            return summary + "\n\n```json\n" + json.dumps(out, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _tags_related(self, args: Dict[str, Any]) -> str:
        query = str(args.get("query", "")).strip().replace(" ", "-")
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "args.query required (tag name)."}, indent=2, ensure_ascii=False)
        params = self._base_params()
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(f"{_BASE_URL}/tags/{query}/related", params=params)
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            items = data.get("items", [])
            include_raw = bool(args.get("include_raw"))
            out: Dict[str, Any] = {"ok": True, "results": items if include_raw else [
                {"name": t.get("name"), "count": t.get("count")}
                for t in items
            ]}
            summary = f"Found {len(items)} related tag(s) for '{query}' on Stack Overflow."
            return summary + "\n\n```json\n" + json.dumps(out, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
