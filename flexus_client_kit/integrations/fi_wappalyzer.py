import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("wappalyzer")

PROVIDER_NAME = "wappalyzer"
METHOD_IDS = [
    "wappalyzer.lookup.v2",
]

_BASE_URL = "https://api.wappalyzer.com/v2"


class IntegrationWappalyzer:
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
            key = os.environ.get("WAPPALYZER_API_KEY", "")
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
        if method_id == "wappalyzer.lookup.v2":
            return await self._lookup(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _lookup(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("WAPPALYZER_API_KEY", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "WAPPALYZER_API_KEY env var not set"}, indent=2, ensure_ascii=False)
        url = str(args.get("url", "")).strip()
        if not url:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "url is required"}, indent=2, ensure_ascii=False)
        include_raw = bool(args.get("include_raw", False))
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{_BASE_URL}/lookup/",
                    params={"urls": url},
                    headers={"x-api-key": key},
                )
            if resp.status_code == 401:
                return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "Invalid API key"}, indent=2, ensure_ascii=False)
            if resp.status_code == 403:
                return json.dumps({"ok": False, "error_code": "ENTITLEMENT_MISSING", "message": "Wappalyzer Business-tier plan required"}, indent=2, ensure_ascii=False)
            if resp.status_code != 200:
                logger.info("wappalyzer error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            if include_raw:
                result = {
                    "ok": True,
                    "credit_note": "1 Wappalyzer lookup credit used",
                    "raw": data,
                }
            else:
                normalized = []
                for entry in data:
                    techs = [
                        {
                            "name": t.get("name"),
                            "categories": t.get("categories", []),
                            "version": t.get("version"),
                            "confidence": t.get("confidence"),
                        }
                        for t in entry.get("technologies", [])
                    ]
                    normalized.append({
                        "url": entry.get("url"),
                        "technologies": techs,
                    })
                result = {
                    "ok": True,
                    "credit_note": "1 Wappalyzer lookup credit used",
                    "results": normalized,
                }
            return f"wappalyzer.lookup.v2 ok\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
