import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("brightdata")

PROVIDER_NAME = "brightdata"
METHOD_IDS = [
    "brightdata.jobs.data_feed.v1",
    "brightdata.jobs.dataset_query.v1",
]

_BASE_URL = "https://api.brightdata.com"


class IntegrationBrightdata:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _get_api_key(self) -> str:
        if self.rcx is not None:
            return (self.rcx.external_auth.get("brightdata") or {}).get("api_key", "")
        return os.environ.get("BRIGHTDATA_API_TOKEN", "")

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
        token = self._get_api_key()
        if not token:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set BRIGHTDATA_API_TOKEN env var."}, indent=2, ensure_ascii=False)

        if method_id == "brightdata.jobs.data_feed.v1":
            return await self._list_datasets(args, token)
        if method_id == "brightdata.jobs.dataset_query.v1":
            return await self._dataset_query(args, token)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _headers(self, token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def _list_datasets(self, args: Dict[str, Any], token: str) -> str:
        """List available Bright Data datasets (marketplace catalog)."""
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(_BASE_URL + "/datasets/v3/datasets", headers=self._headers(token))
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            datasets = data if isinstance(data, list) else data.get("datasets", data.get("data", []))
            query = str(args.get("query", "")).lower()
            if query and isinstance(datasets, list):
                datasets = [d for d in datasets if query in str(d.get("name", "")).lower() or query in str(d.get("description", "")).lower()]
            summary = f"Found {len(datasets) if isinstance(datasets, list) else 1} dataset(s) from {PROVIDER_NAME}."
            return summary + "\n\n```json\n" + json.dumps({"ok": True, "datasets": datasets}, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _dataset_query(self, args: Dict[str, Any], token: str) -> str:
        """Trigger a dataset snapshot/query and retrieve results."""
        dataset_id = str(args.get("dataset_id", "")).strip()
        if not dataset_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "args.dataset_id required. Use brightdata.jobs.data_feed.v1 to list available datasets."}, indent=2, ensure_ascii=False)

        query = str(args.get("query", "")).strip()
        limit = int(args.get("limit", 20))

        # Trigger snapshot
        body: Dict[str, Any] = {"dataset_id": dataset_id}
        if query:
            body["filters"] = [{"name": "keyword", "value": query}]
        if limit:
            body["limit"] = limit

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.post(_BASE_URL + "/datasets/v3/trigger", json=body, headers=self._headers(token))
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            snapshot_id = data.get("snapshot_id", "")
            summary = f"Dataset query triggered on {PROVIDER_NAME}. snapshot_id={snapshot_id}. Poll /datasets/v3/snapshot/{snapshot_id} for results."
            return summary + "\n\n```json\n" + json.dumps({"ok": True, "snapshot_id": snapshot_id, "status": data.get("status"), "data": data}, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
