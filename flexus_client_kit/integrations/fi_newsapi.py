import json
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("newsapi")

PROVIDER_NAME = "newsapi"
_BASE_URL = "https://newsapi.org/v2"

_METHOD_SPECS = {
    "newsapi.everything.v1": {
        "kind": "everything",
        "path": "/everything",
        "docs_url": "https://newsapi.org/docs/endpoints/everything",
        "result_key": "articles",
    },
    "newsapi.top_headlines.v1": {
        "kind": "top_headlines",
        "path": "/top-headlines",
        "docs_url": "https://newsapi.org/docs/endpoints/top-headlines",
        "result_key": "articles",
    },
    "newsapi.sources.v1": {
        "kind": "sources",
        "path": "/top-headlines/sources",
        "docs_url": "https://newsapi.org/docs/endpoints/sources",
        "result_key": "sources",
    },
}
METHOD_IDS = list(_METHOD_SPECS.keys())


def _resolve_dates(time_window: str, start_date: str, end_date: str) -> tuple[Optional[str], Optional[str]]:
    if start_date:
        return start_date, end_date or None
    if time_window:
        match = re.match(r"last_(\d+)d", time_window)
        if match:
            days = int(match.group(1))
            now = datetime.now(timezone.utc)
            start = now - timedelta(days=days)
            return start.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")
    return None, None


def _compact_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: value
        for key, value in data.items()
        if value is not None and (not isinstance(value, str) or value.strip() != "")
    }


def _normalize_csv_value(value: Any) -> Any:
    if isinstance(value, list):
        parts = [str(item).strip() for item in value if str(item).strip()]
        return ",".join(parts)
    return value


class IntegrationNewsapi:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _auth(self) -> Dict[str, Any]:
        if self.rcx is not None:
            return self.rcx.external_auth.get(PROVIDER_NAME) or {}
        return {}

    def _get_api_key(self) -> str:
        auth = self._auth()
        return str(
            auth.get("api_key", "")
            or auth.get("token", "")
            or os.environ.get("NEWSAPI_API_KEY", "")
            or os.environ.get("NEWSAPI_KEY", "")
        ).strip()

    def _status(self) -> str:
        api_key = self._get_api_key()
        return json.dumps({
            "ok": True,
            "provider": PROVIDER_NAME,
            "status": "ready" if api_key else "missing_credentials",
            "has_api_key": bool(api_key),
            "method_count": len(METHOD_IDS),
        }, indent=2, ensure_ascii=False)

    def _help(self) -> str:
        return (
            f"provider={PROVIDER_NAME}\n"
            "op=help | status | list_methods | call\n"
            "call args: method_id plus the documented NewsAPI query params for that method\n"
            "aliases: query->q, limit->pageSize, geo.country->country, time_window/start_date/end_date->from/to for everything\n"
            f"methods={len(METHOD_IDS)}"
        )

    def _clean_params(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {
            key: value
            for key, value in args.items()
            if key not in {"method_id", "include_raw"}
            and value is not None
            and (not isinstance(value, str) or value.strip() != "")
        }

    def _normalize_params(self, method_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        params = self._clean_params(args)
        geo = params.pop("geo", None)
        query = params.pop("query", None)
        limit = params.pop("limit", None)
        time_window = str(params.pop("time_window", "")).strip()
        start_date = str(params.pop("start_date", "")).strip()
        end_date = str(params.pop("end_date", "")).strip()

        if query is not None and "q" not in params:
            params["q"] = query
        if limit is not None and "pageSize" not in params:
            params["pageSize"] = limit
        if isinstance(geo, dict):
            country = str(geo.get("country", "")).strip().lower()
            if country and "country" not in params:
                params["country"] = country

        if method_id == "newsapi.everything.v1":
            start_resolved, end_resolved = _resolve_dates(time_window, start_date, end_date)
            if start_resolved and "from" not in params:
                params["from"] = start_resolved
            if end_resolved and "to" not in params:
                params["to"] = end_resolved

        for key in ("searchIn", "sources", "domains", "excludeDomains"):
            if key in params:
                params[key] = _normalize_csv_value(params[key])

        return _compact_dict(params)

    def _coerce_positive_int(self, params: Dict[str, Any], key: str, maximum: int | None = None) -> None:
        if key not in params:
            return
        try:
            value = int(params[key])
        except (TypeError, ValueError):
            raise ValueError(f"{key} must be an integer.") from None
        if value < 1:
            raise ValueError(f"{key} must be >= 1.")
        if maximum is not None and value > maximum:
            raise ValueError(f"{key} must be <= {maximum}.")
        params[key] = value

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
                "methods": _METHOD_SPECS,
            }, indent=2, ensure_ascii=False)
        if op != "call":
            return "Error: unknown op. Use help/status/list_methods/call."
        raw_call_args = args.get("args") or {}
        if not isinstance(raw_call_args, dict):
            return json.dumps({
                "ok": False,
                "error_code": "INVALID_ARGS",
                "message": "args must be an object.",
            }, indent=2, ensure_ascii=False)
        nested_params = raw_call_args.get("params")
        if nested_params is not None and not isinstance(nested_params, dict):
            return json.dumps({
                "ok": False,
                "error_code": "INVALID_ARGS",
                "message": "args.params must be an object when provided.",
            }, indent=2, ensure_ascii=False)
        call_args = dict(nested_params or {})
        call_args.update({
            key: value
            for key, value in raw_call_args.items()
            if key != "params"
        })
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in _METHOD_SPECS:
            return json.dumps({
                "ok": False,
                "error_code": "METHOD_UNKNOWN",
                "method_id": method_id,
            }, indent=2, ensure_ascii=False)
        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        if method_id == "newsapi.everything.v1":
            return await self._everything(method_id, args)
        if method_id == "newsapi.top_headlines.v1":
            return await self._top_headlines(method_id, args)
        if method_id == "newsapi.sources.v1":
            return await self._sources(method_id, args)
        return json.dumps({
            "ok": False,
            "error_code": "METHOD_UNIMPLEMENTED",
            "method_id": method_id,
        }, indent=2, ensure_ascii=False)

    async def _request_json(
        self,
        method_id: str,
        params: Dict[str, Any],
        include_raw: bool,
    ) -> str:
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({
                "ok": False,
                "error_code": "AUTH_MISSING",
                "message": "Set api_key in newsapi auth or NEWSAPI_API_KEY env var.",
            }, indent=2, ensure_ascii=False)
        spec = _METHOD_SPECS[method_id]
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(
                    _BASE_URL + spec["path"],
                    params=params,
                    headers={"X-Api-Key": api_key, "Accept": "application/json"},
                )
            if response.status_code >= 400:
                logger.info("%s GET %s HTTP %s: %s", PROVIDER_NAME, spec["path"], response.status_code, response.text[:200])
                return json.dumps({
                    "ok": False,
                    "error_code": "PROVIDER_ERROR",
                    "status": response.status_code,
                    "detail": response.text[:300],
                }, indent=2, ensure_ascii=False)
            data = response.json()
            result_key = spec["result_key"]
            items = data.get(result_key, [])
            result = {
                "ok": True,
                "provider": PROVIDER_NAME,
                "method_id": method_id,
                "docs_url": spec["docs_url"],
                "total": data.get("totalResults", len(items)),
                result_key: items,
            }
            if include_raw:
                result["raw"] = data
            return json.dumps(result, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({
                "ok": False,
                "error_code": "TIMEOUT",
                "provider": PROVIDER_NAME,
            }, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, json.JSONDecodeError) as e:
            return json.dumps({
                "ok": False,
                "error_code": "HTTP_ERROR",
                "detail": f"{type(e).__name__}: {e}",
            }, indent=2, ensure_ascii=False)

    async def _everything(self, method_id: str, args: Dict[str, Any]) -> str:
        try:
            include_raw = bool(args.get("include_raw", False))
            params = self._normalize_params(method_id, args)
            self._coerce_positive_int(params, "pageSize", maximum=100)
            self._coerce_positive_int(params, "page")
            if not any(params.get(key) for key in ("q", "sources", "domains")):
                return json.dumps({
                    "ok": False,
                    "error_code": "MISSING_ARGS",
                    "message": "Provide at least one of q, sources, or domains.",
                }, indent=2, ensure_ascii=False)
            return await self._request_json(method_id, params, include_raw)
        except ValueError as e:
            return json.dumps({
                "ok": False,
                "error_code": "INVALID_ARG",
                "message": str(e),
            }, indent=2, ensure_ascii=False)

    async def _top_headlines(self, method_id: str, args: Dict[str, Any]) -> str:
        try:
            include_raw = bool(args.get("include_raw", False))
            params = self._normalize_params(method_id, args)
            self._coerce_positive_int(params, "pageSize", maximum=100)
            self._coerce_positive_int(params, "page")
            if params.get("sources") and (params.get("country") or params.get("category")):
                return json.dumps({
                    "ok": False,
                    "error_code": "INVALID_ARGS",
                    "message": "sources cannot be combined with country or category for top_headlines.",
                }, indent=2, ensure_ascii=False)
            return await self._request_json(method_id, params, include_raw)
        except ValueError as e:
            return json.dumps({
                "ok": False,
                "error_code": "INVALID_ARG",
                "message": str(e),
            }, indent=2, ensure_ascii=False)

    async def _sources(self, method_id: str, args: Dict[str, Any]) -> str:
        try:
            include_raw = bool(args.get("include_raw", False))
            params = self._normalize_params(method_id, args)
            params.pop("pageSize", None)
            params.pop("page", None)
            params.pop("q", None)
            return await self._request_json(method_id, params, include_raw)
        except ValueError as e:
            return json.dumps({
                "ok": False,
                "error_code": "INVALID_ARG",
                "message": str(e),
            }, indent=2, ensure_ascii=False)
