import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("notion")

PROVIDER_NAME = "notion"
NOTION_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2026-03-11"

METHOD_SPECS = {
    "notion.search.v1": {
        "method": "POST",
        "path": "/search",
        "required": [],
        "docs_url": "https://developers.notion.com/reference/post-search",
    },
    "notion.retrieve_page.v1": {
        "method": "GET",
        "path": "/pages/{page_id}",
        "required": ["page_id"],
        "docs_url": "https://developers.notion.com/reference/retrieve-a-page",
    },
    "notion.retrieve_block_children.v1": {
        "method": "GET",
        "path": "/blocks/{block_id}/children",
        "required": ["block_id"],
        "docs_url": "https://developers.notion.com/reference/get-block-children",
    },
    "notion.query_data_source.v1": {
        "method": "POST",
        "path": "/data_sources/{data_source_id}/query",
        "required": ["data_source_id"],
        "docs_url": "https://developers.notion.com/reference/query-a-data-source",
    },
    "notion.create_page.v1": {
        "method": "POST",
        "path": "/pages",
        "required": ["parent", "properties"],
        "docs_url": "https://developers.notion.com/reference/post-page",
    },
    "notion.update_page.v1": {
        "method": "PATCH",
        "path": "/pages/{page_id}",
        "required": ["page_id"],
        "docs_url": "https://developers.notion.com/reference/patch-page",
    },
    "notion.append_block_children.v1": {
        "method": "POST",
        "path": "/blocks/{block_id}/children",
        "required": ["block_id", "children"],
        "docs_url": "https://developers.notion.com/reference/patch-block-children",
    },
    "notion.archive_page.v1": {
        "method": "PATCH",
        "path": "/pages/{page_id}",
        "required": ["page_id"],
        "docs_url": "https://developers.notion.com/reference/patch-page",
    },
    "notion.delete_block.v1": {
        "method": "DELETE",
        "path": "/blocks/{block_id}",
        "required": ["block_id"],
        "docs_url": "https://developers.notion.com/reference/delete-a-block",
    },
}

METHOD_IDS = list(METHOD_SPECS.keys())

NOTION_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name=PROVIDER_NAME,
    description="notion: knowledge base and content hub. op=help|status|list_methods|call",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "enum": ["help", "status", "list_methods", "call"]},
            "args": {"type": ["object", "null"], "additionalProperties": False},
        },
        "required": ["op", "args"],
        "additionalProperties": False,
    },
)

NOTION_PROMPT = (
    "Notion integration available for knowledge base/content hub work. "
    "Always discover first with search, then read page/blocks or query data sources. "
    "Notion only returns pages/data sources shared with this integration."
)


class IntegrationNotion:
    def __init__(self, rcx=None, api_key: str = ""):
        self.rcx = rcx
        self.api_key = (api_key or "").strip()

    def _auth(self) -> Dict[str, Any]:
        if self.rcx is None:
            return {}
        return self.rcx.external_auth.get("notion_manual") or self.rcx.external_auth.get(PROVIDER_NAME) or {}

    def _get_token(self) -> str:
        auth = self._auth()
        token_obj = auth.get("token") if isinstance(auth.get("token"), dict) else {}
        return str(
            self.api_key
            or auth.get("api_key", "")
            or token_obj.get("access_token", "")
            or auth.get("access_token", "")
            or os.environ.get("NOTION_API_KEY", "")
            or os.environ.get("NOTION_TOKEN", "")
        ).strip()

    def _help(self) -> str:
        return (
            "provider=notion\n"
            "op=help | status | list_methods | call\n"
            "call args: method_id plus endpoint params/body fields\n"
            "for payload methods, pass body={...}; for pagination use page_size/start_cursor"
        )

    def _status(self) -> str:
        tok = self._get_token()
        return json.dumps({
            "ok": True,
            "provider": PROVIDER_NAME,
            "status": "ready" if tok else "missing_credentials",
            "has_api_key": bool(tok),
            "method_count": len(METHOD_IDS),
            "notion_version": NOTION_VERSION,
        }, indent=2, ensure_ascii=False)

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Dict[str, Any],
    ) -> str:
        args = model_produced_args or {}
        op = str(args.get("op", "help")).strip()
        if op == "help":
            return self._help()
        if op == "status":
            return self._status()
        if op == "list_methods":
            return json.dumps({
                "ok": True,
                "provider": PROVIDER_NAME,
                "method_ids": METHOD_IDS,
                "methods": METHOD_SPECS,
            }, indent=2, ensure_ascii=False)
        if op != "call":
            return "Error: unknown op. Use help/status/list_methods/call."

        raw = args.get("args") or {}
        if not isinstance(raw, dict):
            return json.dumps({
                "ok": False,
                "error_code": "INVALID_ARGS",
                "message": "args must be an object.",
            }, indent=2, ensure_ascii=False)
        nested = raw.get("params")
        if nested is not None and not isinstance(nested, dict):
            return json.dumps({
                "ok": False,
                "error_code": "INVALID_ARGS",
                "message": "args.params must be an object when provided.",
            }, indent=2, ensure_ascii=False)

        call_args = dict(nested or {})
        call_args.update({k: v for k, v in raw.items() if k != "params"})
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_SPECS:
            return json.dumps({
                "ok": False,
                "error_code": "METHOD_UNKNOWN",
                "method_id": method_id,
            }, indent=2, ensure_ascii=False)
        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        spec = METHOD_SPECS[method_id]
        for key in spec["required"]:
            if args.get(key) is None or (isinstance(args.get(key), str) and args.get(key, "").strip() == ""):
                return json.dumps({
                    "ok": False,
                    "error_code": "MISSING_REQUIRED",
                    "method_id": method_id,
                    "missing": key,
                }, indent=2, ensure_ascii=False)

        path = spec["path"]
        for key in ("page_id", "block_id", "data_source_id"):
            if "{" + key + "}" in path:
                path = path.replace("{" + key + "}", str(args[key]).strip())

        method = spec["method"]
        body = args.get("body") if isinstance(args.get("body"), dict) else None
        include_raw = bool(args.get("include_raw", False))
        query_keys = {"start_cursor", "page_size"}
        query = {k: args[k] for k in query_keys if k in args and args[k] is not None}

        if method == "POST" and body is None:
            payload = {k: v for k, v in args.items() if k not in {
                "method_id", "include_raw", "body", "page_id", "block_id", "data_source_id", "params",
            }}
            body = payload if payload else {}
        elif method == "PATCH" and body is None:
            payload = {k: v for k, v in args.items() if k not in {
                "method_id", "include_raw", "body", "page_id", "params",
            }}
            body = payload if payload else {}

        if method_id == "notion.archive_page.v1":
            body = dict(body or {})
            body.setdefault("in_trash", True)
        elif method_id == "notion.delete_block.v1":
            body = dict(body or {})
            body.setdefault("in_trash", True)

        return await self._request_json(method_id, method, path, query, body, include_raw)

    async def _request_json(
        self,
        method_id: str,
        method: str,
        path: str,
        query: Dict[str, Any],
        body: Dict[str, Any] | None,
        include_raw: bool,
    ) -> str:
        tok = self._get_token()
        if not tok:
            return json.dumps({
                "ok": False,
                "error_code": "AUTH_MISSING",
                "message": "Set notion api_key in external auth or NOTION_API_KEY env var.",
            }, indent=2, ensure_ascii=False)

        headers = {
            "Authorization": f"Bearer {tok}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        url = NOTION_BASE + path
        try:
            async with httpx.AsyncClient(timeout=25.0) as cli:
                r = await cli.request(method, url, headers=headers, params=query or None, json=body if body and method in {"POST", "PATCH", "DELETE"} else None)
            data = r.json() if r.text else {}
        except Exception as e:
            logger.exception("notion request failed: %s", method_id)
            return json.dumps({
                "ok": False,
                "error_code": "REQUEST_FAILED",
                "method_id": method_id,
                "message": str(e),
            }, indent=2, ensure_ascii=False)

        if r.status_code >= 400:
            return json.dumps({
                "ok": False,
                "method_id": method_id,
                "status": r.status_code,
                "error": data,
            }, indent=2, ensure_ascii=False)

        out = {
            "ok": True,
            "method_id": method_id,
            "status": r.status_code,
            "result": data,
        }
        if not include_raw and isinstance(data, dict):
            out["result_preview"] = {
                "object": data.get("object"),
                "id": data.get("id"),
                "results_count": len(data.get("results", [])) if isinstance(data.get("results"), list) else None,
                "has_more": data.get("has_more"),
                "next_cursor": data.get("next_cursor"),
            }
        return json.dumps(out, indent=2, ensure_ascii=False)
