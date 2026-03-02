import json
import logging
import os
from typing import Any, Dict, List

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("sentry")

PROVIDER_NAME = "sentry"
BASE_URL = "https://sentry.io/api/0"
METHOD_IDS = [
    "sentry.organizations.issues.list.v1",
]


class IntegrationSentry:
    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Dict[str, Any],
    ) -> str:
        args = model_produced_args or {}
        op = str(args.get("op", "help")).strip()
        if op == "help":
            return f"provider={PROVIDER_NAME}\nop=help | status | list_methods | call\nmethods: {', '.join(METHOD_IDS)}"
        if op == "status":
            key = os.environ.get("SENTRY_AUTH_TOKEN", "")
            return json.dumps(
                {
                    "ok": True,
                    "provider": PROVIDER_NAME,
                    "status": "available" if key else "no_credentials",
                    "method_count": len(METHOD_IDS),
                },
                indent=2,
                ensure_ascii=False,
            )
        if op == "list_methods":
            return json.dumps(
                {"ok": True, "provider": PROVIDER_NAME, "method_ids": METHOD_IDS},
                indent=2,
                ensure_ascii=False,
            )
        if op != "call":
            return "Error: unknown op."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required."
        if method_id not in METHOD_IDS:
            return json.dumps(
                {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
                indent=2,
                ensure_ascii=False,
            )
        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, call_args: Dict[str, Any]) -> str:
        if method_id == "sentry.organizations.issues.list.v1":
            return await self._issues_list(call_args)
        return json.dumps(
            {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
            indent=2,
            ensure_ascii=False,
        )

    async def _issues_list(self, call_args: Dict[str, Any]) -> str:
        token = os.environ.get("SENTRY_AUTH_TOKEN", "")
        if not token:
            return json.dumps(
                {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        org_slug = str(call_args.get("org_slug", "")).strip() or os.environ.get("SENTRY_ORGANIZATION_SLUG", "")
        if not org_slug:
            return json.dumps(
                {"ok": False, "error_code": "NO_ORG_SLUG", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        params: Dict[str, Any] = {}
        query = str(call_args.get("query", "")).strip()
        if query:
            params["query"] = query
        project = call_args.get("project")
        if project:
            params["project"] = [int(p) for p in project]
        limit = call_args.get("limit")
        params["limit"] = int(limit) if limit is not None else 25
        cursor = str(call_args.get("cursor", "")).strip()
        if cursor:
            params["cursor"] = cursor
        environment = str(call_args.get("environment", "")).strip()
        if environment:
            params["environment"] = environment
        url = f"{BASE_URL}/organizations/{org_slug}/issues/"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers, timeout=30.0)
                response.raise_for_status()
        except httpx.TimeoutException as e:
            logger.info("Sentry timeout org_slug=%s: %s", org_slug, e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "org_slug": org_slug},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPStatusError as e:
            logger.info("Sentry HTTP error org_slug=%s status=%s: %s", org_slug, e.response.status_code, e)
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "HTTP_ERROR",
                    "org_slug": org_slug,
                    "status_code": e.response.status_code,
                },
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("Sentry HTTP error org_slug=%s: %s", org_slug, e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "org_slug": org_slug},
                indent=2,
                ensure_ascii=False,
            )
        try:
            payload = response.json()
        except json.JSONDecodeError as e:
            logger.info("Sentry JSON decode error org_slug=%s: %s", org_slug, e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "org_slug": org_slug},
                indent=2,
                ensure_ascii=False,
            )
        try:
            issues: List[Dict[str, Any]] = []
            for item in payload:
                issues.append(
                    {
                        "id": item["id"],
                        "title": item["title"],
                        "culprit": item.get("culprit", ""),
                        "status": item["status"],
                        "level": item["level"],
                        "count": item["count"],
                        "last_seen": item["lastSeen"],
                        "first_seen": item["firstSeen"],
                        "project_slug": item["project"]["slug"],
                    }
                )
        except KeyError as e:
            logger.info("Sentry response missing key org_slug=%s: %s", org_slug, e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "org_slug": org_slug},
                indent=2,
                ensure_ascii=False,
            )
        return json.dumps(
            {"ok": True, "issues": issues},
            indent=2,
            ensure_ascii=False,
        )
