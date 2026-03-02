import json
import logging
import os
import time
from typing import Any, Dict

import httpx
import jwt

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("ga4")

PROVIDER_NAME = "ga4"
METHOD_IDS = [
    "ga4.properties.run_report.v1",
]

API_BASE = "https://analyticsdata.googleapis.com/v1beta"


class IntegrationGa4:
    async def called_by_model(self, toolcall, model_produced_args):
        args = model_produced_args or {}
        op = str(args.get("op", "help")).strip()
        if op == "help":
            return f"provider={PROVIDER_NAME}\nop=help | status | list_methods | call\nmethods: {', '.join(METHOD_IDS)}"
        if op == "status":
            key = os.environ.get("GOOGLE_ANALYTICS_SERVICE_ACCOUNT_JSON", "")
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

    async def _get_access_token(self):
        sa_json = os.environ.get("GOOGLE_ANALYTICS_SERVICE_ACCOUNT_JSON", "")
        if not sa_json:
            raise ValueError("GOOGLE_ANALYTICS_SERVICE_ACCOUNT_JSON is not set")
        sa = json.loads(sa_json)
        client_email = sa["client_email"]
        private_key = sa["private_key"]
        token_uri = sa["token_uri"]
        now = int(time.time())
        payload = {
            "iss": client_email,
            "sub": client_email,
            "aud": token_uri,
            "iat": now,
            "exp": now + 3600,
            "scope": "https://www.googleapis.com/auth/analytics.readonly",
        }
        token = jwt.encode(payload, private_key, algorithm="RS256")
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(token_uri, data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": token,
            })
            resp.raise_for_status()
        return resp.json()["access_token"]

    async def _dispatch(self, method_id, call_args):
        if method_id == "ga4.properties.run_report.v1":
            return await self._run_report(call_args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _run_report(self, call_args):
        property_id = call_args.get("property_id") or os.environ.get("GA4_PROPERTY_ID", "")
        if not property_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PROPERTY_ID", "error": "property_id required (or set GA4_PROPERTY_ID)"}, indent=2, ensure_ascii=False)

        date_ranges = call_args.get("date_ranges")
        if not date_ranges:
            return json.dumps({"ok": False, "error_code": "MISSING_DATE_RANGES", "error": "date_ranges required"}, indent=2, ensure_ascii=False)

        dimensions = call_args.get("dimensions") or []
        metrics = call_args.get("metrics") or []
        dimension_filter = call_args.get("dimension_filter")
        limit = int(call_args.get("limit") or 100)

        body: Dict[str, Any] = {
            "dateRanges": date_ranges,
            "dimensions": [{"name": d} for d in dimensions],
            "metrics": [{"name": m} for m in metrics],
            "limit": limit,
        }
        if dimension_filter:
            body["dimensionFilter"] = dimension_filter

        try:
            access_token = await self._get_access_token()
        except json.JSONDecodeError as e:
            return json.dumps({"ok": False, "error_code": "SA_JSON_INVALID", "error": str(e)}, indent=2, ensure_ascii=False)
        except KeyError as e:
            return json.dumps({"ok": False, "error_code": "SA_JSON_MISSING_FIELD", "error": str(e)}, indent=2, ensure_ascii=False)
        except ValueError as e:
            return json.dumps({"ok": False, "error_code": "CONFIG_ERROR", "error": str(e)}, indent=2, ensure_ascii=False)
        except jwt.PyJWTError as e:
            return json.dumps({"ok": False, "error_code": "JWT_ERROR", "error": str(e)}, indent=2, ensure_ascii=False)
        except httpx.HTTPStatusError as e:
            logger.info("ga4 token exchange failed: %s %s", e.response.status_code, e.response.text)
            return json.dumps({"ok": False, "error_code": "TOKEN_EXCHANGE_FAILED", "status": e.response.status_code, "error": e.response.text}, indent=2, ensure_ascii=False)
        except httpx.TimeoutException as e:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "error": str(e)}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "error": str(e)}, indent=2, ensure_ascii=False)

        url = f"{API_BASE}/{property_id}:runReport"
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(url, json=body, headers=headers)
                resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            logger.info("ga4 run_report failed: %s %s", e.response.status_code, e.response.text)
            return json.dumps({"ok": False, "error_code": "API_ERROR", "status": e.response.status_code, "error": e.response.text}, indent=2, ensure_ascii=False)
        except httpx.TimeoutException as e:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "error": str(e)}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "error": str(e)}, indent=2, ensure_ascii=False)

        dim_headers = [h["name"] for h in data.get("dimensionHeaders", [])]
        met_headers = [h["name"] for h in data.get("metricHeaders", [])]
        rows = []
        for row in data.get("rows", []):
            dim_values = [v["value"] for v in row.get("dimensionValues", [])]
            met_values = [v["value"] for v in row.get("metricValues", [])]
            rows.append({
                "dimensions": dict(zip(dim_headers, dim_values)),
                "metrics": dict(zip(met_headers, met_values)),
            })

        return json.dumps({
            "ok": True,
            "row_count": data.get("rowCount", len(rows)),
            "rows": rows,
        }, indent=2, ensure_ascii=False)
