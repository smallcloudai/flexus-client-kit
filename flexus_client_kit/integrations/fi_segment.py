import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("segment")

PROVIDER_NAME = "segment"
METHOD_IDS = [
    "segment.tracking_plans.list.v1",
    "segment.tracking_plans.get.v1",
]

BASE_URL = "https://api.segmentapis.com"


class IntegrationSegment:
    async def called_by_model(self, toolcall, model_produced_args):
        args = model_produced_args or {}
        op = str(args.get("op", "help")).strip()
        if op == "help":
            return f"provider={PROVIDER_NAME}\nop=help | status | list_methods | call\nmethods: {', '.join(METHOD_IDS)}"
        if op == "status":
            key = os.environ.get("SEGMENT_ACCESS_TOKEN", "")
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "status": "available" if key else "no_credentials", "method_count": len(METHOD_IDS)}, indent=2, ensure_ascii=False)
        if op == "list_methods":
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_ids": METHOD_IDS}, indent=2, ensure_ascii=False)
        if op != "call":
            return "Error: unknown op."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required."
        if method_id not in METHOD_IDS:
            return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)
        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id, call_args):
        if method_id == "segment.tracking_plans.list.v1":
            return await self._tracking_plans_list(call_args)
        if method_id == "segment.tracking_plans.get.v1":
            return await self._tracking_plan_get(call_args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _headers(self):
        token = os.environ.get("SEGMENT_ACCESS_TOKEN", "")
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def _tracking_plans_list(self, call_args):
        pagination_count = int(call_args.get("pagination_count", 10))
        pagination_cursor = call_args.get("pagination_cursor", None)
        params = {"pagination[count]": pagination_count}
        if pagination_cursor:
            params["pagination[cursor]"] = pagination_cursor
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(f"{BASE_URL}/tracking-plans", headers=self._headers(), params=params)
                resp.raise_for_status()
                data = resp.json()
        except httpx.TimeoutException as e:
            logger.info("segment tracking_plans list timeout: %s", e)
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "error": str(e)}, indent=2, ensure_ascii=False)
        except httpx.HTTPStatusError as e:
            logger.info("segment tracking_plans list http status error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "status_code": e.response.status_code, "error": str(e)}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("segment tracking_plans list http error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "error": str(e)}, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            logger.info("segment tracking_plans list json decode error: %s", e)
            return json.dumps({"ok": False, "error_code": "JSON_DECODE_ERROR", "error": str(e)}, indent=2, ensure_ascii=False)
        try:
            raw_plans = data["data"]["trackingPlans"]
        except KeyError as e:
            logger.info("segment tracking_plans list unexpected response shape: %s", e)
            return json.dumps({"ok": False, "error_code": "UNEXPECTED_RESPONSE", "error": f"Missing key: {e}"}, indent=2, ensure_ascii=False)
        tracking_plans = [
            {
                "id": p.get("id", ""),
                "name": p.get("name", ""),
                "slug": p.get("slug", ""),
                "description": p.get("description", ""),
                "created_at": p.get("createdAt", ""),
                "updated_at": p.get("updatedAt", ""),
                "rules_count": p.get("rulesCount", 0),
            }
            for p in raw_plans
        ]
        return json.dumps({"ok": True, "tracking_plans": tracking_plans}, indent=2, ensure_ascii=False)

    async def _tracking_plan_get(self, call_args):
        tracking_plan_id = str(call_args.get("tracking_plan_id", "")).strip()
        if not tracking_plan_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "error": "tracking_plan_id is required"}, indent=2, ensure_ascii=False)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(f"{BASE_URL}/tracking-plans/{tracking_plan_id}", headers=self._headers())
                resp.raise_for_status()
                data = resp.json()
        except httpx.TimeoutException as e:
            logger.info("segment tracking_plan get timeout: %s", e)
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "error": str(e)}, indent=2, ensure_ascii=False)
        except httpx.HTTPStatusError as e:
            logger.info("segment tracking_plan get http status error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "status_code": e.response.status_code, "error": str(e)}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("segment tracking_plan get http error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "error": str(e)}, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            logger.info("segment tracking_plan get json decode error: %s", e)
            return json.dumps({"ok": False, "error_code": "JSON_DECODE_ERROR", "error": str(e)}, indent=2, ensure_ascii=False)
        try:
            plan = data["data"]["trackingPlan"]
        except KeyError as e:
            logger.info("segment tracking_plan get unexpected response shape: %s", e)
            return json.dumps({"ok": False, "error_code": "UNEXPECTED_RESPONSE", "error": f"Missing key: {e}"}, indent=2, ensure_ascii=False)
        raw_rules = plan.get("rules") or []
        rules = [
            {
                "key": r.get("key", ""),
                "type": r.get("type", ""),
                "schema": r.get("jsonSchema", {}),
            }
            for r in raw_rules
        ]
        return json.dumps({
            "ok": True,
            "id": plan.get("id", ""),
            "name": plan.get("name", ""),
            "description": plan.get("description", ""),
            "rules": rules,
        }, indent=2, ensure_ascii=False)
