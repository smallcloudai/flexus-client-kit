import json
import logging
import os
from typing import Any, Dict, List

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("partnerstack")

PROVIDER_NAME = "partnerstack"
API_BASE = "https://api.partnerstack.com/api/v2"
METHOD_IDS = [
    "partnerstack.partnerships.list.v1",
    "partnerstack.partners.list.v1",
    "partnerstack.transactions.list.v1",
    "partnerstack.transactions.create.v1",
    "partnerstack.payouts.list.v1",
]
_TIMEOUT = 30.0


def _check_credentials() -> tuple[str, str] | None:
    public_key = os.environ.get("PARTNERSTACK_PUBLIC_KEY", "")
    secret_key = os.environ.get("PARTNERSTACK_SECRET_KEY", "")
    if not public_key or not secret_key:
        return None
    return (public_key, secret_key)


def _auth() -> httpx.BasicAuth | None:
    creds = _check_credentials()
    if not creds:
        return None
    return httpx.BasicAuth(username=creds[0], password=creds[1])


def _clamp_limit(limit: Any, default: int = 25, max_val: int = 250) -> int:
    try:
        n = int(limit) if limit is not None else default
        return max(1, min(max_val, n))
    except (TypeError, ValueError):
        return default


class IntegrationPartnerstack:
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
                f"known_method_ids={len(METHOD_IDS)}"
            )
        if op == "status":
            creds = _check_credentials()
            status = "no_credentials" if not creds else "available"
            return json.dumps(
                {
                    "ok": True,
                    "provider": PROVIDER_NAME,
                    "status": status,
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
            return "Error: unknown op. Use help/status/list_methods/call."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_IDS:
            return json.dumps(
                {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
                indent=2,
                ensure_ascii=False,
            )
        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, call_args: Dict[str, Any]) -> str:
        auth = _auth()
        if not auth:
            return json.dumps(
                {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        handlers = {
            "partnerstack.partnerships.list.v1": self._partnerships_list,
            "partnerstack.partners.list.v1": self._partners_list,
            "partnerstack.transactions.list.v1": self._transactions_list,
            "partnerstack.transactions.create.v1": self._transactions_create,
            "partnerstack.payouts.list.v1": self._payouts_list,
        }
        handler = handlers.get(method_id)
        if not handler:
            return json.dumps(
                {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
                indent=2,
                ensure_ascii=False,
            )
        return await handler(call_args, auth)

    def _http_error_response(self, method_id: str, e: Exception, extra: Dict[str, Any] | None = None) -> str:
        out: Dict[str, Any] = {
            "ok": False,
            "error_code": "HTTP_ERROR",
            "provider": PROVIDER_NAME,
            "method_id": method_id,
        }
        if extra:
            out.update(extra)
        if isinstance(e, httpx.TimeoutException):
            out["error_code"] = "TIMEOUT"
            logger.info("PartnerStack timeout method_id=%s: %s", method_id, e)
        elif isinstance(e, httpx.HTTPStatusError):
            out["status_code"] = e.response.status_code
            logger.info("PartnerStack HTTP error method_id=%s status=%s: %s", method_id, e.response.status_code, e)
        else:
            logger.info("PartnerStack HTTP error method_id=%s: %s", method_id, e)
        return json.dumps(out, indent=2, ensure_ascii=False)

    async def _partnerships_list(self, call_args: Dict[str, Any], auth: httpx.BasicAuth) -> str:
        limit = _clamp_limit(call_args.get("limit"), 25, 250)
        params: Dict[str, Any] = {"limit": limit}
        min_created = call_args.get("min_created")
        max_created = call_args.get("max_created")
        status = call_args.get("status")
        if min_created is not None:
            params["min_created"] = int(min_created)
        if max_created is not None:
            params["max_created"] = int(max_created)
        if status:
            params["status"] = str(status).strip()
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.get(f"{API_BASE}/partnerships", auth=auth, params=params)
                response.raise_for_status()
        except httpx.TimeoutException as e:
            return self._http_error_response("partnerstack.partnerships.list.v1", e)
        except httpx.HTTPStatusError as e:
            return self._http_error_response("partnerstack.partnerships.list.v1", e)
        except httpx.HTTPError as e:
            return self._http_error_response("partnerstack.partnerships.list.v1", e)
        try:
            payload = response.json()
        except json.JSONDecodeError as e:
            logger.info("PartnerStack JSON decode partnerships: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        try:
            data = payload.get("data") or {}
            items = data.get("items") or []
            has_more = data.get("has_more", False)
            total_count = data.get("total_count") or data.get("total")
        except (KeyError, ValueError) as e:
            logger.info("PartnerStack response partnerships: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        normalized: List[Dict[str, Any]] = []
        for it in items:
            company = it.get("company") or {}
            normalized.append({
                "key": it.get("key", ""),
                "name": company.get("name", ""),
                "email": company.get("email", ""),
                "created_at": it.get("created_at"),
                "group_key": company.get("key", ""),
                "approved_state": it.get("status", ""),
            })
        return json.dumps(
            {"ok": True, "items": normalized, "has_more": has_more, "total_count": total_count},
            indent=2,
            ensure_ascii=False,
        )

    async def _partners_list(self, call_args: Dict[str, Any], auth: httpx.BasicAuth) -> str:
        limit = _clamp_limit(call_args.get("limit"), 25, 250)
        params: Dict[str, Any] = {"limit": limit}
        min_created = call_args.get("min_created")
        max_created = call_args.get("max_created")
        if min_created is not None:
            params["min_created"] = int(min_created)
        if max_created is not None:
            params["max_created"] = int(max_created)
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.get(f"{API_BASE}/partners", auth=auth, params=params)
                response.raise_for_status()
        except httpx.TimeoutException as e:
            return self._http_error_response("partnerstack.partners.list.v1", e)
        except httpx.HTTPStatusError as e:
            return self._http_error_response("partnerstack.partners.list.v1", e)
        except httpx.HTTPError as e:
            return self._http_error_response("partnerstack.partners.list.v1", e)
        try:
            payload = response.json()
        except json.JSONDecodeError as e:
            logger.info("PartnerStack JSON decode partners: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        try:
            data = payload.get("data") or {}
            items = data.get("items") or []
            has_more = data.get("has_more", False)
        except (KeyError, ValueError) as e:
            logger.info("PartnerStack response partners: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        normalized: List[Dict[str, Any]] = []
        for it in items:
            normalized.append({
                "key": it.get("key", ""),
                "name": it.get("name", ""),
                "email": it.get("email", ""),
                "created_at": it.get("created_at"),
            })
        return json.dumps(
            {"ok": True, "items": normalized, "has_more": has_more},
            indent=2,
            ensure_ascii=False,
        )

    async def _transactions_list(self, call_args: Dict[str, Any], auth: httpx.BasicAuth) -> str:
        limit = _clamp_limit(call_args.get("limit"), 25, 250)
        params: Dict[str, Any] = {"limit": limit}
        min_created = call_args.get("min_created")
        max_created = call_args.get("max_created")
        partnership_key = call_args.get("partnership_key")
        if min_created is not None:
            params["min_created"] = int(min_created)
        if max_created is not None:
            params["max_created"] = int(max_created)
        if partnership_key:
            params["partnership_key"] = str(partnership_key).strip()
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.get(f"{API_BASE}/transactions", auth=auth, params=params)
                response.raise_for_status()
        except httpx.TimeoutException as e:
            return self._http_error_response("partnerstack.transactions.list.v1", e)
        except httpx.HTTPStatusError as e:
            return self._http_error_response("partnerstack.transactions.list.v1", e)
        except httpx.HTTPError as e:
            return self._http_error_response("partnerstack.transactions.list.v1", e)
        try:
            payload = response.json()
        except json.JSONDecodeError as e:
            logger.info("PartnerStack JSON decode transactions list: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        try:
            data = payload.get("data") or {}
            items = data.get("items") or []
            has_more = data.get("has_more", False)
        except (KeyError, ValueError) as e:
            logger.info("PartnerStack response transactions list: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        normalized: List[Dict[str, Any]] = []
        for it in items:
            cust = it.get("customer") or {}
            cust_key = cust.get("key") if isinstance(cust, dict) else None
            if cust_key is None:
                cust_key = it.get("customer_key", "")
            st = it.get("status")
            if st is None and "approved" in it:
                st = "approved" if it.get("approved") else "pending"
            normalized.append({
                "key": it.get("key", ""),
                "amount": it.get("amount"),
                "currency": it.get("currency", ""),
                "customer_key": cust_key,
                "partnership_key": it.get("partnership_key", ""),
                "created_at": it.get("created_at"),
                "status": st or "",
            })
        return json.dumps(
            {"ok": True, "items": normalized, "has_more": has_more},
            indent=2,
            ensure_ascii=False,
        )

    async def _transactions_create(self, call_args: Dict[str, Any], auth: httpx.BasicAuth) -> str:
        partnership_key = str(call_args.get("partnership_key", "")).strip()
        customer_key = str(call_args.get("customer_key", "")).strip()
        amount = call_args.get("amount")
        currency = str(call_args.get("currency", "usd")).strip().upper() or "USD"
        description = call_args.get("description")
        if not partnership_key:
            return json.dumps(
                {"ok": False, "error_code": "MISSING_ARG", "message": "partnership_key required"},
                indent=2,
                ensure_ascii=False,
            )
        if not customer_key:
            return json.dumps(
                {"ok": False, "error_code": "MISSING_ARG", "message": "customer_key required"},
                indent=2,
                ensure_ascii=False,
            )
        try:
            amount_int = int(amount)
        except (TypeError, ValueError):
            return json.dumps(
                {"ok": False, "error_code": "MISSING_ARG", "message": "amount (int, cents) required"},
                indent=2,
                ensure_ascii=False,
            )
        body: Dict[str, Any] = {
            "partnership_key": partnership_key,
            "customer_key": customer_key,
            "amount": amount_int,
            "currency": currency,
        }
        if description is not None:
            body["description"] = str(description)
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.post(
                    f"{API_BASE}/transactions",
                    auth=auth,
                    json=body,
                )
                response.raise_for_status()
        except httpx.TimeoutException as e:
            return self._http_error_response("partnerstack.transactions.create.v1", e)
        except httpx.HTTPStatusError as e:
            return self._http_error_response("partnerstack.transactions.create.v1", e)
        except httpx.HTTPError as e:
            return self._http_error_response("partnerstack.transactions.create.v1", e)
        try:
            payload = response.json()
        except json.JSONDecodeError as e:
            logger.info("PartnerStack JSON decode transactions create: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        try:
            data = payload.get("data")
            if isinstance(data, dict):
                it = data
            elif isinstance(data, list) and data:
                it = data[0]
            else:
                it = payload
            cust = it.get("customer") or {}
            cust_key = cust.get("key") if isinstance(cust, dict) else None
            if cust_key is None:
                cust_key = it.get("customer_key", "")
            st = it.get("status")
            if st is None and "approved" in it:
                st = "approved" if it.get("approved") else "pending"
            normalized = {
                "key": it.get("key", ""),
                "amount": it.get("amount"),
                "currency": it.get("currency", ""),
                "customer_key": cust_key,
                "partnership_key": it.get("partnership_key", ""),
                "created_at": it.get("created_at"),
                "status": st or "",
            }
        except (KeyError, ValueError) as e:
            logger.info("PartnerStack response transactions create: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        return json.dumps(
            {"ok": True, "transaction": normalized},
            indent=2,
            ensure_ascii=False,
        )

    async def _payouts_list(self, call_args: Dict[str, Any], auth: httpx.BasicAuth) -> str:
        limit = _clamp_limit(call_args.get("limit"), 25, 250)
        params: Dict[str, Any] = {"limit": limit}
        min_created = call_args.get("min_created")
        max_created = call_args.get("max_created")
        if min_created is not None:
            params["min_created"] = int(min_created)
        if max_created is not None:
            params["max_created"] = int(max_created)
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.get(f"{API_BASE}/payouts", auth=auth, params=params)
                response.raise_for_status()
        except httpx.TimeoutException as e:
            return self._http_error_response("partnerstack.payouts.list.v1", e)
        except httpx.HTTPStatusError as e:
            return self._http_error_response("partnerstack.payouts.list.v1", e)
        except httpx.HTTPError as e:
            return self._http_error_response("partnerstack.payouts.list.v1", e)
        try:
            payload = response.json()
        except json.JSONDecodeError as e:
            logger.info("PartnerStack JSON decode payouts: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        try:
            data = payload.get("data") or {}
            items = data.get("items") or []
            has_more = data.get("has_more", False)
        except (KeyError, ValueError) as e:
            logger.info("PartnerStack response payouts: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        normalized: List[Dict[str, Any]] = []
        for it in items:
            normalized.append({
                "key": it.get("key", ""),
                "amount": it.get("amount"),
                "currency": it.get("currency", ""),
                "status": it.get("status", ""),
                "created_at": it.get("created_at"),
                "partnership_key": it.get("partnership_key", ""),
            })
        return json.dumps(
            {"ok": True, "items": normalized, "has_more": has_more},
            indent=2,
            ensure_ascii=False,
        )
