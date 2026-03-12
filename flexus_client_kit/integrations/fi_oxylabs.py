import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("oxylabs")

PROVIDER_NAME = "oxylabs"
METHOD_IDS = [
    "oxylabs.jobs.source_query.v1",
]

_BASE_URL = "https://realtime.oxylabs.io/v1"


class IntegrationOxylabs:
    # XXX: requires multiple credentials (OXYLABS_USERNAME + OXYLABS_PASSWORD).
    # manual auth (single api_key field) does not cover this provider.
    # currently reads from env vars as a fallback.
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
        username = os.environ.get("OXYLABS_USERNAME", "")
        password = os.environ.get("OXYLABS_PASSWORD", "")
        if not username or not password:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set OXYLABS_USERNAME and OXYLABS_PASSWORD env vars."}, indent=2, ensure_ascii=False)

        if method_id == "oxylabs.jobs.source_query.v1":
            return await self._source_query(args, username, password)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _source_query(self, args: Dict[str, Any], username: str, password: str) -> str:
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "args.query required."}, indent=2, ensure_ascii=False)

        geo = args.get("geo") or {}
        if isinstance(geo, str):
            geo = {"country": geo}
        geo_location = str(geo.get("country", "United States")) or "United States"

        source = str(args.get("source", "google_search_jobs"))
        body = {
            "source": source,
            "query": query,
            "domain": "com",
            "geo_location": geo_location,
            "parse": True,
        }
        try:
            async with httpx.AsyncClient(timeout=30.0, auth=(username, password)) as client:
                r = await client.post(_BASE_URL + "/queries", json=body)
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            results = data.get("results", [])
            include_raw = bool(args.get("include_raw"))
            out: Dict[str, Any] = {"ok": True, "results": results if include_raw else results}
            summary = f"Found {len(results)} result(s) from {PROVIDER_NAME}."
            return summary + "\n\n```json\n" + json.dumps(out, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
