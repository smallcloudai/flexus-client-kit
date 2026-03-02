import json
import logging
import os
from typing import Any, Dict, List

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("semrush")

PROVIDER_NAME = "semrush"
METHOD_IDS = [
    "semrush.analytics.keyword_reports.v1",
    "semrush.trends.daily_traffic.v1",
    "semrush.trends.traffic_summary.v1",
]

_BASE_URL = "https://api.semrush.com/"

_GEO_DB_MAP = {
    "US": "us", "GB": "uk", "DE": "de", "FR": "fr", "CA": "ca",
    "AU": "au", "IN": "in", "BR": "br", "ES": "es", "IT": "it",
    "NL": "nl", "RU": "ru", "JP": "jp", "MX": "mx", "PL": "pl",
    "SE": "se", "CH": "ch", "NO": "no", "DK": "dk", "FI": "fi",
}


def _parse_semrush_csv(text: str) -> List[Dict[str, str]]:
    lines = [ln for ln in text.strip().splitlines() if ln.strip()]
    if len(lines) < 2:
        return []
    sep = ";" if ";" in lines[0] else "\t"
    headers = lines[0].split(sep)
    rows = []
    for line in lines[1:]:
        parts = line.split(sep)
        row = {headers[i].strip(): parts[i].strip() if i < len(parts) else "" for i in range(len(headers))}
        rows.append(row)
    return rows


class IntegrationSemrush:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _get_api_key(self) -> str:
        if self.rcx is not None:
            return (self.rcx.external_auth.get("semrush") or {}).get("api_key", "")
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
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set SEMRUSH_KEY env var."}, indent=2, ensure_ascii=False)

        query = str(args.get("query", ""))
        geo = args.get("geo") or {}
        country = geo.get("country", "US") if geo else "US"
        database = _GEO_DB_MAP.get(str(country).upper(), "us")
        limit = int(args.get("limit", 10))

        if method_id == "semrush.trends.traffic_summary.v1":
            return await self._traffic_summary(api_key, query, database, args)
        if method_id == "semrush.trends.daily_traffic.v1":
            return await self._daily_traffic(api_key, query, database, limit, args)
        if method_id == "semrush.analytics.keyword_reports.v1":
            return await self._keyword_reports(api_key, query, database, limit, args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _get_text(self, params: Dict[str, Any]) -> str:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(_BASE_URL, params=params)
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            return r.text
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    def _format(self, results: List[Dict], method_id: str, include_raw: bool, raw_text: str = "") -> str:
        summary = f"Found {len(results)} result(s) from {PROVIDER_NAME} ({method_id})."
        payload: Dict[str, Any] = {"ok": True, "results": results, "total": len(results)}
        if include_raw:
            payload["raw"] = raw_text
        return summary + "\n\n```json\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\n```"

    async def _traffic_summary(self, key: str, query: str, database: str, args: Dict) -> str:
        params = {"type": "domain_ranks", "key": key, "domain": query, "database": database, "export_columns": "Dn,Rk,Or,Ot,Oc,Ad,At,Ac"}
        text = await self._get_text(params)
        try:
            json.loads(text)
            return text
        except ValueError:
            pass
        results = _parse_semrush_csv(text)
        return self._format(results, "semrush.trends.traffic_summary.v1", bool(args.get("include_raw")), text)

    async def _daily_traffic(self, key: str, query: str, database: str, limit: int, args: Dict) -> str:
        params = {"type": "domain_rank_history", "key": key, "domain": query, "database": database, "display_limit": limit}
        text = await self._get_text(params)
        try:
            json.loads(text)
            return text
        except ValueError:
            pass
        results = _parse_semrush_csv(text)
        return self._format(results, "semrush.trends.daily_traffic.v1", bool(args.get("include_raw")), text)

    async def _keyword_reports(self, key: str, query: str, database: str, limit: int, args: Dict) -> str:
        params = {"type": "phrase_all", "key": key, "phrase": query, "database": database, "display_limit": limit}
        text = await self._get_text(params)
        try:
            json.loads(text)
            return text
        except ValueError:
            pass
        results = _parse_semrush_csv(text)
        return self._format(results, "semrush.analytics.keyword_reports.v1", bool(args.get("include_raw")), text)
