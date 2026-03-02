import json
import logging
import os
from typing import Any, Dict

import httpx

logger = logging.getLogger("notion")

PROVIDER_NAME = "notion"
METHOD_IDS = [
    "notion.pages.create.v1",
    "notion.pages.search.v1",
]

_BASE_URL = "https://api.notion.com/v1"
_NOTION_VERSION = "2022-06-28"


class IntegrationNotion:
    async def called_by_model(self, toolcall, model_produced_args):
        args = model_produced_args or {}
        op = str(args.get("op", "help")).strip()
        if op == "help":
            return (f"provider={PROVIDER_NAME}\nop=help | status | list_methods | call\nmethods: {', '.join(METHOD_IDS)}")
        if op == "status":
            key = os.environ.get("NOTION_API_KEY", "")
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "status": "available" if key else "no_credentials", "method_count": len(METHOD_IDS)}, indent=2, ensure_ascii=False)
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

    def _headers(self):
        key = os.environ.get("NOTION_API_KEY", "")
        return {
            "Authorization": f"Bearer {key}",
            "Notion-Version": _NOTION_VERSION,
            "Content-Type": "application/json",
        }

    def _client(self):
        return httpx.AsyncClient(base_url=_BASE_URL, headers=self._headers(), timeout=30)

    async def _dispatch(self, method_id, call_args):
        if method_id == "notion.pages.create.v1":
            return await self._pages_create(call_args)
        if method_id == "notion.pages.search.v1":
            return await self._pages_search(call_args)

    async def _pages_create(self, call_args):
        parent_database_id = str(call_args.get("parent_database_id", "")).strip()
        if not parent_database_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "parent_database_id"}, indent=2, ensure_ascii=False)
        title = str(call_args.get("title", "")).strip()
        if not title:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "title"}, indent=2, ensure_ascii=False)

        extra_properties = call_args.get("properties") or {}
        content = call_args.get("content", "")

        properties: Dict[str, Any] = {
            "title": {"title": [{"text": {"content": title}}]},
        }
        properties.update(extra_properties)

        body: Dict[str, Any] = {
            "parent": {"database_id": parent_database_id},
            "properties": properties,
        }
        if content:
            body["children"] = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": str(content)}}]},
                }
            ]

        async with self._client() as client:
            resp = await client.post("/pages", json=body)

        if resp.status_code not in (200, 201):
            logger.info("notion pages create failed: status=%d body=%s", resp.status_code, resp.text[:500])
            return json.dumps({"ok": False, "error_code": "API_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)

        data = resp.json()
        return json.dumps({"ok": True, "id": data.get("id"), "url": data.get("url"), "created_time": data.get("created_time")}, indent=2, ensure_ascii=False)

    async def _pages_search(self, call_args):
        query = str(call_args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "query"}, indent=2, ensure_ascii=False)

        filter_type = str(call_args.get("filter_type", "page")).strip() or "page"
        sort_direction = str(call_args.get("sort_direction", "descending")).strip() or "descending"
        page_size = int(call_args.get("page_size", 20))

        body = {
            "query": query,
            "filter": {"value": filter_type, "property": "object"},
            "sort": {"direction": sort_direction, "timestamp": "last_edited_time"},
            "page_size": page_size,
        }

        async with self._client() as client:
            resp = await client.post("/search", json=body)

        if resp.status_code != 200:
            logger.info("notion pages search failed: status=%d body=%s", resp.status_code, resp.text[:500])
            return json.dumps({"ok": False, "error_code": "API_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)

        data = resp.json()
        results = []
        for item in data.get("results", []):
            title = ""
            props = item.get("properties") or {}
            title_prop = props.get("title") or {}
            title_arr = title_prop.get("title") or item.get("title") or []
            if title_arr:
                title = title_arr[0].get("plain_text", "")
            results.append({
                "id": item.get("id"),
                "title": title,
                "url": item.get("url"),
                "last_edited_time": item.get("last_edited_time"),
                "created_time": item.get("created_time"),
            })
        return json.dumps({"ok": True, "results": results}, indent=2, ensure_ascii=False)
