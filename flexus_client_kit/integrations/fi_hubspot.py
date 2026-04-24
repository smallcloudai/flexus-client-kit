import asyncio
import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("hubspot")

PROVIDER_NAME = "hubspot"
AUTH_PROVIDER_NAME = "hubspot"
HUBSPOT_BASE = "https://api.hubapi.com"

METHOD_SPECS = {
    "hubspot.crm.objects.list.v1": {
        "method": "GET",
        "path": "/crm/v3/objects/{objectType}",
        "required": ["objectType"],
        "docs_url": "https://developers.hubspot.com/docs/api-reference/latest/crm/objects/contacts/get-contacts",
        "query_keys": ["limit", "after", "properties", "associations", "archived"],
    },
    "hubspot.crm.objects.get.v1": {
        "method": "GET",
        "path": "/crm/v3/objects/{objectType}/{objectId}",
        "required": ["objectType", "objectId"],
        "docs_url": "https://developers.hubspot.com/docs/api-reference/latest/crm/objects/contacts/get-contact",
        "query_keys": ["properties", "associations", "archived"],
    },
    "hubspot.crm.objects.create.v1": {
        "method": "POST",
        "path": "/crm/v3/objects/{objectType}",
        "required": ["objectType"],
        "docs_url": "https://developers.hubspot.com/docs/api-reference/latest/crm/objects/contacts/create-contact",
        "query_keys": [],
    },
    "hubspot.crm.objects.update.v1": {
        "method": "PATCH",
        "path": "/crm/v3/objects/{objectType}/{objectId}",
        "required": ["objectType", "objectId"],
        "docs_url": "https://developers.hubspot.com/docs/api-reference/latest/crm/objects/contacts/update-contact",
        "query_keys": [],
    },
    "hubspot.crm.objects.delete.v1": {
        "method": "DELETE",
        "path": "/crm/v3/objects/{objectType}/{objectId}",
        "required": ["objectType", "objectId"],
        "docs_url": "https://developers.hubspot.com/docs/api-reference/latest/crm/objects/contacts/archive-contact",
        "query_keys": [],
    },
    "hubspot.crm.objects.search.v1": {
        "method": "POST",
        "path": "/crm/v3/objects/{objectType}/search",
        "required": ["objectType"],
        "docs_url": "https://developers.hubspot.com/docs/api-reference/latest/crm/objects/contacts/search-contacts",
        "query_keys": [],
    },
    "hubspot.crm.objects.batch_create.v1": {
        "method": "POST",
        "path": "/crm/v3/objects/{objectType}/batch/create",
        "required": ["objectType", "inputs"],
        "docs_url": "https://developers.hubspot.com/docs/api-reference/latest/crm/objects/contacts/batch/create-contacts",
        "query_keys": [],
    },
    "hubspot.crm.objects.batch_update.v1": {
        "method": "POST",
        "path": "/crm/v3/objects/{objectType}/batch/update",
        "required": ["objectType", "inputs"],
        "docs_url": "https://developers.hubspot.com/docs/api-reference/latest/crm/objects/contacts/batch/update-contacts",
        "query_keys": [],
    },
    "hubspot.crm.objects.batch_archive.v1": {
        "method": "POST",
        "path": "/crm/v3/objects/{objectType}/batch/archive",
        "required": ["objectType", "inputs"],
        "docs_url": "https://developers.hubspot.com/docs/api-reference/latest/crm/objects/contacts/batch/archive-contacts",
        "query_keys": [],
    },
    "hubspot.crm.properties.list.v1": {
        "method": "GET",
        "path": "/crm/v3/properties/{objectType}",
        "required": ["objectType"],
        "docs_url": "https://developers.hubspot.com/docs/api-reference/latest/crm/properties/get-properties",
        "query_keys": ["archived"],
    },
    "hubspot.crm.owners.list.v1": {
        "method": "GET",
        "path": "/crm/v3/owners",
        "required": [],
        "docs_url": "https://developers.hubspot.com/docs/api-reference/latest/crm/owners/get-owners",
        "query_keys": ["limit", "after", "email"],
    },
    "hubspot.crm.engagements.list.v1": {
        "method": "GET",
        "path": "/crm/v3/objects/{engagementType}",
        "required": ["engagementType"],
        "docs_url": "https://developers.hubspot.com/docs/api-reference/latest/crm/activities/notes/get-notes",
        "query_keys": ["limit", "after", "properties", "associations", "archived"],
    },
    "hubspot.crm.engagements.create.v1": {
        "method": "POST",
        "path": "/crm/v3/objects/{engagementType}",
        "required": ["engagementType"],
        "docs_url": "https://developers.hubspot.com/docs/api-reference/latest/crm/activities/calls/create-call",
        "query_keys": [],
    },
    "hubspot.crm.associations.create.v1": {
        "method": "PUT",
        "path": "/crm/v4/objects/{fromObjectType}/{fromObjectId}/associations/{toObjectType}/{toObjectId}",
        "required": ["fromObjectType", "fromObjectId", "toObjectType", "toObjectId"],
        "docs_url": "https://developers.hubspot.com/docs/api-reference/latest/crm/associations/associate-records",
        "query_keys": [],
    },
    "hubspot.crm.associations.list.v1": {
        "method": "GET",
        "path": "/crm/v4/objects/{fromObjectType}/{fromObjectId}/associations/{toObjectType}",
        "required": ["fromObjectType", "fromObjectId", "toObjectType"],
        "docs_url": "https://developers.hubspot.com/docs/api-reference/latest/crm/associations/get-associations",
        "query_keys": ["limit", "after"],
    },
    "hubspot.account.api_usage.v1": {
        "method": "GET",
        "path": "/account-info/2026-03/api-usage/daily/private-apps",
        "required": [],
        "docs_url": "https://developers.hubspot.com/docs/api-reference/latest/account/account-information/get-usage-details",
        "query_keys": [],
    },
}

METHOD_IDS = list(METHOD_SPECS.keys())

WRITE_METHODS = {
    "hubspot.crm.objects.create.v1",
    "hubspot.crm.objects.update.v1",
    "hubspot.crm.objects.delete.v1",
    "hubspot.crm.objects.batch_create.v1",
    "hubspot.crm.objects.batch_update.v1",
    "hubspot.crm.objects.batch_archive.v1",
    "hubspot.crm.engagements.create.v1",
    "hubspot.crm.associations.create.v1",
}

DESTRUCTIVE_METHODS = {
    "hubspot.crm.objects.delete.v1",
    "hubspot.crm.objects.batch_archive.v1",
}

HUBSPOT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name=PROVIDER_NAME,
    description='Interact with HubSpot CRM: contacts, companies, deals, tickets, engagements, associations. ops: help, status, list_methods, call. Example: op="call", args={"method_id":"hubspot.crm.objects.search.v1","objectType":"contacts","body":{"filterGroups":[{"filters":[{"propertyName":"email","operator":"EQ","value":"alice@example.com"}]}]}}',
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Operation: help, status, list_methods, call"},
            "args": {"type": ["object", "null"], "description": "Arguments for the operation"},
        },
        "required": ["op", "args"],
        "additionalProperties": False,
    },
)

HUBSPOT_PROMPT = (
    "HubSpot integration available for CRM work. "
    "Common objectTypes: contacts, companies, deals, tickets. "
    "Common engagementTypes: calls, emails, meetings, notes. "
    "Use search to find records, then read or update. "
    "For associations, use create with fromObjectType/fromObjectId/toObjectType/toObjectId."
)


class IntegrationHubSpot:
    def __init__(self, rcx=None, api_key: str = ""):
        self.rcx = rcx
        self.api_key = (api_key or "").strip()

    def _auth(self) -> Dict[str, Any]:
        if self.rcx is None:
            return {}
        return self.rcx.external_auth.get(AUTH_PROVIDER_NAME) or self.rcx.external_auth.get("hubspot_manual") or {}

    def _get_token(self) -> str:
        auth = self._auth()
        token_obj = auth.get("token") if isinstance(auth.get("token"), dict) else {}
        return str(
            self.api_key
            or auth.get("api_key", "")
            or token_obj.get("access_token", "")
            or auth.get("access_token", "")
            or os.environ.get("HUBSPOT_ACCESS_TOKEN", "")
            or os.environ.get("HUBSPOT_API_KEY", "")
        ).strip()

    def _help(self) -> str:
        return (
            "provider=hubspot\n"
            "op=help | status | list_methods | call\n"
            "call args: method_id plus endpoint params/body fields\n"
            "for payload methods, pass body={...}; for pagination use limit/after\n"
            "objectType examples: contacts, companies, deals, tickets\n"
            "engagementType examples: calls, emails, meetings, notes\n"
            "Examples:\n"
            '  op="call", args={"method_id":"hubspot.crm.objects.search.v1","objectType":"contacts","body":{"filterGroups":[{"filters":[{"propertyName":"email","operator":"EQ","value":"alice@example.com"}]}]}}\n'
            '  op="call", args={"method_id":"hubspot.crm.objects.create.v1","objectType":"contacts","body":{"properties":{"email":"alice@example.com","firstname":"Alice"}}}\n'
            '  op="call", args={"method_id":"hubspot.crm.objects.update.v1","objectType":"contacts","objectId":"123","body":{"properties":{"firstname":"Bob"}}}\n'
            '  op="call", args={"method_id":"hubspot.crm.associations.create.v1","fromObjectType":"contacts","fromObjectId":"123","toObjectType":"companies","toObjectId":"456"}\n'
            "auth: use setup field hubspot_api_key or external_auth['hubspot']['api_key']"
        )

    def _status(self) -> str:
        tok = self._get_token()
        return json.dumps({
            "ok": True,
            "provider": PROVIDER_NAME,
            "status": "ready" if tok else "missing_credentials",
            "has_api_key": bool(tok),
            "setup_required": not bool(tok),
            "ready_for_calls": bool(tok),
            "method_count": len(METHOD_IDS),
        }, indent=2, ensure_ascii=False)

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Dict[str, Any],
    ) -> str:
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error
        op = str(args.get("op", "")).strip()
        if not op:
            if args.get("method_id") or (isinstance(args.get("args"), dict) and args["args"].get("method_id")):
                op = "call"
            else:
                op = "help"
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
            return self._error("INVALID_ARGS", "args must be an object.")
        nested = raw.get("params")
        if nested is not None and not isinstance(nested, dict):
            return self._error("INVALID_ARGS", "args.params must be an object when provided.")

        call_args = dict(nested or {})
        call_args.update({k: v for k, v in raw.items() if k != "params"})
        if not call_args and "method_id" in args:
            call_args = {k: v for k, v in args.items() if k not in {"op", "args"}}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_SPECS:
            return self._error("METHOD_UNKNOWN", "Unknown method_id.", method_id=method_id)

        if method_id in DESTRUCTIVE_METHODS and not toolcall.confirmed_by_human:
            raise ckit_cloudtool.NeedsConfirmation(
                confirm_setup_key="hubspot_destructive",
                confirm_command=f"hubspot {method_id}",
                confirm_explanation=f"This will permanently delete data in HubSpot: {method_id}",
            )

        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        spec = METHOD_SPECS[method_id]
        b = self._extract_body(method_id, args)
        if isinstance(b, str):
            return self._error("INVALID_ARGS", b, method_id=method_id)
        for key in spec["required"]:
            v = args.get(key)
            if v is None and isinstance(b, dict):
                v = b.get(key)
            if v is None or (isinstance(v, str) and not v.strip()):
                return self._error("MISSING_REQUIRED", f"Missing required argument: {key}", method_id=method_id, missing=key)

        path = self._build_path(spec["path"], args)
        q = self._extract_query(args, spec)

        return await self._request_json(method_id, spec["method"], path, q, b)

    def _extract_query(self, args: Dict[str, Any], spec: Dict[str, Any]) -> Dict[str, Any]:
        q = dict(args.get("query") or {}) if isinstance(args.get("query"), dict) else {}
        for k in spec.get("query_keys", []):
            if k in args and args[k] is not None:
                q[k] = args[k]
        return q

    def _extract_body(self, method_id: str, args: Dict[str, Any]) -> Dict[str, Any] | None | str:
        if isinstance(args.get("body"), dict):
            return args["body"]

        if method_id in {
            "hubspot.crm.objects.create.v1",
            "hubspot.crm.objects.update.v1",
            "hubspot.crm.engagements.create.v1",
        }:
            if isinstance(args.get("properties"), dict):
                return {"properties": args["properties"]}
            return "Provide properties object or body for create/update."

        if method_id in {
            "hubspot.crm.objects.search.v1",
        }:
            payload = {}
            for k in ("filterGroups", "sorts", "query", "properties", "limit", "after"):
                if k in args and args[k] is not None:
                    payload[k] = args[k]
            return payload

        if method_id in {
            "hubspot.crm.objects.batch_create.v1",
            "hubspot.crm.objects.batch_update.v1",
            "hubspot.crm.objects.batch_archive.v1",
        }:
            if isinstance(args.get("inputs"), list):
                return {"inputs": args["inputs"]}
            return "Provide inputs array or body for batch operation."

        if method_id == "hubspot.crm.associations.create.v1":
            body = {}
            if isinstance(args.get("associationTypeId"), int):
                body["associationTypeId"] = args["associationTypeId"]
            if isinstance(args.get("associationCategory"), str):
                body["associationCategory"] = args["associationCategory"]
            return body if body else None

        return None

    def _build_path(self, path_tpl: str, args: Dict[str, Any]) -> str:
        path = path_tpl
        for key in (
            "objectType", "objectId", "engagementType",
            "fromObjectType", "fromObjectId", "toObjectType", "toObjectId",
        ):
            token = "{" + key + "}"
            if token in path:
                path = path.replace(token, str(args.get(key, "")).strip())
        return path

    async def _request_json(
        self,
        method_id: str,
        method: str,
        path: str,
        query: Dict[str, Any],
        body: Dict[str, Any] | None,
    ) -> str:
        tok = self._get_token()
        if not tok:
            return self._error("AUTH_MISSING", "Set hubspot api_key in external auth or HUBSPOT_ACCESS_TOKEN env var.", method_id=method_id)

        headers = {
            "Authorization": f"Bearer {tok}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        url = HUBSPOT_BASE + path

        try:
            async with httpx.AsyncClient(timeout=30.0) as cli:
                response = None
                for attempt in range(4):
                    response = await cli.request(
                        method,
                        url,
                        headers=headers,
                        params=query or None,
                        json=body if method in {"POST", "PATCH", "PUT", "DELETE"} else None,
                    )
                    if response.status_code != 429:
                        break
                    wait_s = min(2 ** attempt, 30)
                    logger.warning("hubspot rate limited method=%s wait=%ss attempt=%s", method_id, wait_s, attempt + 1)
                    await asyncio.sleep(wait_s)
                assert response is not None
        except Exception as e:
            logger.exception("hubspot request failed: %s", method_id)
            return self._error("REQUEST_FAILED", str(e), method_id=method_id)

        data: Any = {}
        if response.text:
            try:
                data = response.json()
            except json.JSONDecodeError:
                data = response.text

        if response.status_code >= 400:
            error_code = "PROVIDER_ERROR"
            message = "HubSpot request failed."
            if response.status_code == 401:
                error_code = "AUTH_REJECTED"
                message = "HubSpot rejected the token. Check that the Private App token is valid and has required scopes."
            elif response.status_code == 403:
                error_code = "INSUFFICIENT_PERMISSIONS"
                message = "HubSpot accepted the token but denied this operation due to missing permissions or scopes."
            elif response.status_code == 404:
                error_code = "NOT_FOUND"
                message = "The requested HubSpot resource was not found."
            elif response.status_code == 409:
                error_code = "CONFLICT"
                message = "HubSpot reported a conflict. This often means a duplicate record or conflicting state."
            elif response.status_code == 429:
                error_code = "RATE_LIMITED"
                message = "HubSpot rate limit exceeded after retries."
            return json.dumps({
                "ok": False,
                "provider": PROVIDER_NAME,
                "method_id": method_id,
                "status": response.status_code,
                "error_code": error_code,
                "message": message,
                "setup_required": False,
                "has_api_key": bool(tok),
                "error": data,
            }, indent=2, ensure_ascii=False)

        result = {
            "ok": True,
            "provider": PROVIDER_NAME,
            "method_id": method_id,
            "status": response.status_code,
            "result": data,
        }
        if isinstance(data, dict):
            result["result_preview"] = {
                "results_count": len(data.get("results", [])) if isinstance(data.get("results"), list) else None,
                "has_more": bool(data.get("paging", {}).get("next", {}).get("after")),
                "next_after": data.get("paging", {}).get("next", {}).get("after"),
                "id": data.get("id"),
                "total": data.get("total"),
            }
        return json.dumps(result, indent=2, ensure_ascii=False)

    def _error(self, code: str, message: str, **extra) -> str:
        payload = {
            "ok": False,
            "provider": PROVIDER_NAME,
            "error_code": code,
            "message": message,
            "setup_required": code == "AUTH_MISSING",
        }
        payload.update(extra)
        return json.dumps(payload, indent=2, ensure_ascii=False)
