import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("salesforce")

PROVIDER_NAME = "salesforce"
METHOD_IDS = [
    "salesforce.query.account.v1",
    "salesforce.query.opportunity.v1",
    "salesforce.query.soql.v1",
    "salesforce.query.user.v1",
]

_API_VERSION = "v58.0"


class IntegrationSalesforce:
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
            token = os.environ.get("SALESFORCE_ACCESS_TOKEN", "")
            url = os.environ.get("SALESFORCE_INSTANCE_URL", "")
            return json.dumps({
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "available" if (token and url) else "no_credentials",
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
        if method_id == "salesforce.query.soql.v1":
            return await self._query_soql(args)
        if method_id == "salesforce.query.opportunity.v1":
            return await self._query_opportunity(args)
        if method_id == "salesforce.query.account.v1":
            return await self._query_account(args)
        if method_id == "salesforce.query.user.v1":
            return await self._query_user(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _soql_exec(self, soql: str, max_records: int) -> str:
        token = os.environ.get("SALESFORCE_ACCESS_TOKEN", "")
        instance_url = os.environ.get("SALESFORCE_INSTANCE_URL", "")
        if not token or not instance_url:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "SALESFORCE_ACCESS_TOKEN and SALESFORCE_INSTANCE_URL env vars required"}, indent=2, ensure_ascii=False)
        base_url = f"{instance_url.rstrip('/')}/services/data/{_API_VERSION}"
        headers = {"Authorization": f"Bearer {token}"}
        records: list[Dict[str, Any]] = []
        total_size = 0
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(f"{base_url}/query", params={"q": soql}, headers=headers)
                if resp.status_code != 200:
                    logger.info("salesforce soql error %s: %s", resp.status_code, resp.text[:200])
                    return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
                data = resp.json()
                total_size = data.get("totalSize", 0)
                records.extend(data.get("records", []))
                while not data.get("done", True) and len(records) < max_records:
                    next_url = data.get("nextRecordsUrl", "")
                    if not next_url:
                        break
                    resp = await client.get(f"{instance_url.rstrip('/')}{next_url}", headers=headers)
                    if resp.status_code != 200:
                        break
                    data = resp.json()
                    records.extend(data.get("records", []))
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        records = records[:max_records]
        return json.dumps({"ok": True, "total_size": total_size, "returned": len(records), "records": records}, indent=2, ensure_ascii=False)

    async def _query_opportunity(self, args: Dict[str, Any]) -> str:
        limit = min(int(args.get("limit", 100)), 200)
        where = str(args.get("where", "")).strip()
        where_clause = f" WHERE {where}" if where else ""
        soql = f"SELECT Id, Name, Amount, StageName, CloseDate, AccountId, OwnerId, Probability, Type, LeadSource FROM Opportunity{where_clause} LIMIT {limit}"
        return await self._soql_exec(soql, limit)

    async def _query_account(self, args: Dict[str, Any]) -> str:
        limit = min(int(args.get("limit", 100)), 200)
        where = str(args.get("where", "")).strip()
        where_clause = f" WHERE {where}" if where else ""
        soql = f"SELECT Id, Name, Industry, AnnualRevenue, NumberOfEmployees, BillingCountry, BillingState, OwnerId, Type FROM Account{where_clause} LIMIT {limit}"
        return await self._soql_exec(soql, limit)

    async def _query_user(self, args: Dict[str, Any]) -> str:
        limit = min(int(args.get("limit", 50)), 200)
        where = str(args.get("where", "IsActive = true")).strip()
        where_clause = f" WHERE {where}" if where else ""
        soql = f"SELECT Id, Name, Email, Title, UserType, IsActive, Profile.Name FROM User{where_clause} LIMIT {limit}"
        return await self._soql_exec(soql, limit)

    async def _query_soql(self, args: Dict[str, Any]) -> str:
        token = os.environ.get("SALESFORCE_ACCESS_TOKEN", "")
        instance_url = os.environ.get("SALESFORCE_INSTANCE_URL", "")
        if not token or not instance_url:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "SALESFORCE_ACCESS_TOKEN and SALESFORCE_INSTANCE_URL env vars required"}, indent=2, ensure_ascii=False)
        soql = str(args.get("soql", "")).strip()
        if not soql:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "soql is required"}, indent=2, ensure_ascii=False)
        max_records = int(args.get("max_records", 100))
        base_url = f"{instance_url.rstrip('/')}/services/data/{_API_VERSION}"
        headers = {"Authorization": f"Bearer {token}"}
        records = []
        total_size = 0
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{base_url}/query",
                    params={"q": soql},
                    headers=headers,
                )
                if resp.status_code != 200:
                    logger.info("salesforce query_soql error %s: %s", resp.status_code, resp.text[:200])
                    return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
                data = resp.json()
                total_size = data.get("totalSize", 0)
                records.extend(data.get("records", []))
                while not data.get("done", True) and len(records) < max_records:
                    next_url = data.get("nextRecordsUrl", "")
                    if not next_url:
                        break
                    resp = await client.get(
                        f"{instance_url.rstrip('/')}{next_url}",
                        headers=headers,
                    )
                    if resp.status_code != 200:
                        logger.info("salesforce query_soql pagination error %s: %s", resp.status_code, resp.text[:200])
                        break
                    data = resp.json()
                    records.extend(data.get("records", []))
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        records = records[:max_records]
        result = {
            "ok": True,
            "total_size": total_size,
            "returned": len(records),
            "records": records,
        }
        return f"salesforce.query.soql ok\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
