import json
import logging
import os
from typing import Any, Dict, List

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("stripe")

PROVIDER_NAME = "stripe"
METHOD_IDS = [
    "stripe.checkout.sessions.list.v1",
    "stripe.invoices.list.v1",
    "stripe.payment_intents.list.v1",
    "stripe.prices.list.v1",
    "stripe.products.list.v1",
    "stripe.subscriptions.list.v1",
]

_BASE_URL = "https://api.stripe.com/v1"
_TIMEOUT = 30.0


class IntegrationStripe:
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
            key = os.environ.get("STRIPE_SECRET_KEY", "")
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
        if method_id == "stripe.checkout.sessions.list.v1":
            return await self._checkout_sessions_list(call_args)
        if method_id == "stripe.invoices.list.v1":
            return await self._invoices_list(call_args)
        if method_id == "stripe.payment_intents.list.v1":
            return await self._payment_intents_list(call_args)
        if method_id == "stripe.prices.list.v1":
            return await self._prices_list(call_args)
        if method_id == "stripe.products.list.v1":
            return await self._products_list(call_args)
        if method_id == "stripe.subscriptions.list.v1":
            return await self._subscriptions_list(call_args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _get_key(self) -> str:
        return os.environ.get("STRIPE_SECRET_KEY", "").strip()

    def _auth_headers(self, key: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {key}"}

    def _handle_error_status(self, status: int, text: str) -> str | None:
        if status == 401:
            return json.dumps({
                "ok": False,
                "error_code": "AUTH_ERROR",
                "provider": PROVIDER_NAME,
                "message": "STRIPE_SECRET_KEY invalid or expired",
            }, indent=2, ensure_ascii=False)
        if status >= 400:
            logger.info("stripe error %s: %s", status, text[:200])
            return json.dumps({
                "ok": False,
                "error_code": "PROVIDER_ERROR",
                "provider": PROVIDER_NAME,
                "status": status,
                "detail": text[:500],
            }, indent=2, ensure_ascii=False)
        return None

    def _normalize_product(self, p: Dict[str, Any]) -> Dict[str, Any]:
        default_price = p.get("default_price")
        default_price_id = None
        if isinstance(default_price, str):
            default_price_id = default_price
        elif isinstance(default_price, dict) and default_price:
            default_price_id = default_price.get("id")
        return {
            "id": p.get("id"),
            "name": p.get("name"),
            "description": p.get("description"),
            "active": p.get("active"),
            "created": p.get("created"),
            "metadata": p.get("metadata") or {},
            "default_price_id": default_price_id,
        }

    def _normalize_price(self, pr: Dict[str, Any]) -> Dict[str, Any]:
        recurring = pr.get("recurring") or {}
        out: Dict[str, Any] = {
            "id": pr.get("id"),
            "product": pr.get("product"),
            "currency": pr.get("currency"),
            "unit_amount": pr.get("unit_amount"),
            "type": pr.get("type"),
            "active": pr.get("active"),
        }
        if recurring:
            out["recurring"] = {
                "interval": recurring.get("interval"),
                "interval_count": recurring.get("interval_count"),
            }
        else:
            out["recurring"] = None
        return out

    async def _products_list(self, args: Dict[str, Any]) -> str:
        key = self._get_key()
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME, "message": "STRIPE_SECRET_KEY env var not set"}, indent=2, ensure_ascii=False)

        active = args.get("active")
        limit = min(int(args.get("limit", 10)), 100)
        starting_after = str(args.get("starting_after", "")).strip() or None
        ending_before = str(args.get("ending_before", "")).strip() or None

        params: Dict[str, Any] = {"limit": limit}
        if active is not None:
            params["active"] = "true" if active else "false"
        if starting_after:
            params["starting_after"] = starting_after
        if ending_before:
            params["ending_before"] = ending_before

        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.get(
                    f"{_BASE_URL}/products",
                    headers=self._auth_headers(key),
                    params=params,
                )
            err = self._handle_error_status(resp.status_code, resp.text)
            if err:
                return err
            data = resp.json()
            raw_list = data.get("data", [])
            has_more = data.get("has_more", False)
            normalized: List[Dict[str, Any]] = [self._normalize_product(p) for p in raw_list]
            out = {"ok": True, "data": normalized, "has_more": has_more}
            return json.dumps(out, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("stripe HTTP error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)
        except KeyError as e:
            logger.info("stripe KeyError: %s", e)
            return json.dumps({"ok": False, "error_code": "PARSE_ERROR", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)
        except ValueError as e:
            logger.info("stripe ValueError: %s", e)
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _checkout_sessions_list(self, args: Dict[str, Any]) -> str:
        key = self._get_key()
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME, "message": "STRIPE_SECRET_KEY env var not set"}, indent=2, ensure_ascii=False)

        limit = min(int(args.get("limit", 10)), 100)
        starting_after = str(args.get("starting_after", "")).strip() or None
        ending_before = str(args.get("ending_before", "")).strip() or None
        payment_status = str(args.get("payment_status", "")).strip() or None
        customer = str(args.get("customer", "")).strip() or None

        params: Dict[str, Any] = {"limit": limit}
        if starting_after:
            params["starting_after"] = starting_after
        if ending_before:
            params["ending_before"] = ending_before
        if payment_status:
            params["payment_status"] = payment_status
        if customer:
            params["customer"] = customer

        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.get(
                    f"{_BASE_URL}/checkout/sessions",
                    headers=self._auth_headers(key),
                    params=params,
                )
            err = self._handle_error_status(resp.status_code, resp.text)
            if err:
                return err
            data = resp.json()
            raw_list = data.get("data", [])
            has_more = data.get("has_more", False)
            normalized: List[Dict[str, Any]] = [
                {
                    "id": s.get("id"),
                    "payment_status": s.get("payment_status"),
                    "amount_total": s.get("amount_total"),
                    "currency": s.get("currency"),
                    "created": s.get("created"),
                    "customer": s.get("customer"),
                    "expires_at": s.get("expires_at"),
                    "url": s.get("url"),
                }
                for s in raw_list
            ]
            out = {"ok": True, "data": normalized, "has_more": has_more}
            return json.dumps(out, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("stripe HTTP error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)
        except KeyError as e:
            logger.info("stripe KeyError: %s", e)
            return json.dumps({"ok": False, "error_code": "PARSE_ERROR", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)
        except ValueError as e:
            logger.info("stripe ValueError: %s", e)
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _payment_intents_list(self, args: Dict[str, Any]) -> str:
        key = self._get_key()
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME, "message": "STRIPE_SECRET_KEY env var not set"}, indent=2, ensure_ascii=False)

        limit = min(int(args.get("limit", 10)), 100)
        starting_after = str(args.get("starting_after", "")).strip() or None
        customer = str(args.get("customer", "")).strip() or None
        created_gte = args.get("created_gte")
        created_lte = args.get("created_lte")

        params: Dict[str, Any] = {"limit": limit}
        if starting_after:
            params["starting_after"] = starting_after
        if customer:
            params["customer"] = customer
        if created_gte is not None:
            params["created[gte]"] = int(created_gte)
        if created_lte is not None:
            params["created[lte]"] = int(created_lte)

        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.get(
                    f"{_BASE_URL}/payment_intents",
                    headers=self._auth_headers(key),
                    params=params,
                )
            err = self._handle_error_status(resp.status_code, resp.text)
            if err:
                return err
            data = resp.json()
            raw_list = data.get("data", [])
            has_more = data.get("has_more", False)
            normalized: List[Dict[str, Any]] = [
                {
                    "id": pi.get("id"),
                    "amount": pi.get("amount"),
                    "currency": pi.get("currency"),
                    "status": pi.get("status"),
                    "created": pi.get("created"),
                    "customer": pi.get("customer"),
                    "payment_method_types": pi.get("payment_method_types"),
                }
                for pi in raw_list
            ]
            out = {"ok": True, "data": normalized, "has_more": has_more}
            return json.dumps(out, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("stripe HTTP error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)
        except KeyError as e:
            logger.info("stripe KeyError: %s", e)
            return json.dumps({"ok": False, "error_code": "PARSE_ERROR", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)
        except ValueError as e:
            logger.info("stripe ValueError: %s", e)
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _subscriptions_list(self, args: Dict[str, Any]) -> str:
        key = self._get_key()
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME, "message": "STRIPE_SECRET_KEY env var not set"}, indent=2, ensure_ascii=False)

        limit = min(int(args.get("limit", 10)), 100)
        starting_after = str(args.get("starting_after", "")).strip() or None
        status = str(args.get("status", "")).strip() or None
        customer = str(args.get("customer", "")).strip() or None
        price = str(args.get("price", "")).strip() or None

        params: Dict[str, Any] = {"limit": limit}
        if starting_after:
            params["starting_after"] = starting_after
        if status:
            params["status"] = status
        if customer:
            params["customer"] = customer
        if price:
            params["price"] = price

        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.get(
                    f"{_BASE_URL}/subscriptions",
                    headers=self._auth_headers(key),
                    params=params,
                )
            err = self._handle_error_status(resp.status_code, resp.text)
            if err:
                return err
            data = resp.json()
            raw_list = data.get("data", [])
            has_more = data.get("has_more", False)

            def _norm_sub(s: Dict[str, Any]) -> Dict[str, Any]:
                items = s.get("items") or {}
                items_data = items.get("data", []) if isinstance(items, dict) else []
                currency = None
                if items_data:
                    first_item = items_data[0]
                    price_obj = first_item.get("price") or {}
                    if isinstance(price_obj, dict):
                        currency = price_obj.get("currency")
                    elif isinstance(first_item.get("price"), str):
                        currency = None
                return {
                    "id": s.get("id"),
                    "status": s.get("status"),
                    "customer": s.get("customer"),
                    "current_period_start": s.get("current_period_start"),
                    "current_period_end": s.get("current_period_end"),
                    "items_count": len(items_data),
                    "currency": currency,
                }

            normalized: List[Dict[str, Any]] = [_norm_sub(s) for s in raw_list]
            out = {"ok": True, "data": normalized, "has_more": has_more}
            return json.dumps(out, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("stripe HTTP error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)
        except KeyError as e:
            logger.info("stripe KeyError: %s", e)
            return json.dumps({"ok": False, "error_code": "PARSE_ERROR", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)
        except ValueError as e:
            logger.info("stripe ValueError: %s", e)
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _invoices_list(self, args: Dict[str, Any]) -> str:
        key = self._get_key()
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME, "message": "STRIPE_SECRET_KEY env var not set"}, indent=2, ensure_ascii=False)

        limit = min(int(args.get("limit", 10)), 100)
        starting_after = str(args.get("starting_after", "")).strip() or None
        status = str(args.get("status", "")).strip() or None
        customer = str(args.get("customer", "")).strip() or None
        subscription = str(args.get("subscription", "")).strip() or None

        params: Dict[str, Any] = {"limit": limit}
        if starting_after:
            params["starting_after"] = starting_after
        if status:
            params["status"] = status
        if customer:
            params["customer"] = customer
        if subscription:
            params["subscription"] = subscription

        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.get(
                    f"{_BASE_URL}/invoices",
                    headers=self._auth_headers(key),
                    params=params,
                )
            err = self._handle_error_status(resp.status_code, resp.text)
            if err:
                return err
            data = resp.json()
            raw_list = data.get("data", [])
            has_more = data.get("has_more", False)
            normalized: List[Dict[str, Any]] = [
                {
                    "id": inv.get("id"),
                    "status": inv.get("status"),
                    "amount_paid": inv.get("amount_paid"),
                    "amount_due": inv.get("amount_due"),
                    "currency": inv.get("currency"),
                    "customer": inv.get("customer"),
                    "created": inv.get("created"),
                    "due_date": inv.get("due_date"),
                    "subscription": inv.get("subscription"),
                }
                for inv in raw_list
            ]
            out = {"ok": True, "data": normalized, "has_more": has_more}
            return json.dumps(out, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("stripe HTTP error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)
        except KeyError as e:
            logger.info("stripe KeyError: %s", e)
            return json.dumps({"ok": False, "error_code": "PARSE_ERROR", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)
        except ValueError as e:
            logger.info("stripe ValueError: %s", e)
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _prices_list(self, args: Dict[str, Any]) -> str:
        key = self._get_key()
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME, "message": "STRIPE_SECRET_KEY env var not set"}, indent=2, ensure_ascii=False)

        product = str(args.get("product", "")).strip() or None
        active = args.get("active")
        limit = min(int(args.get("limit", 10)), 100)
        starting_after = str(args.get("starting_after", "")).strip() or None
        ending_before = str(args.get("ending_before", "")).strip() or None
        currency = str(args.get("currency", "")).strip().lower() or None

        params: Dict[str, Any] = {"limit": limit}
        if product:
            params["product"] = product
        if active is not None:
            params["active"] = "true" if active else "false"
        if starting_after:
            params["starting_after"] = starting_after
        if ending_before:
            params["ending_before"] = ending_before
        if currency:
            params["currency"] = currency

        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.get(
                    f"{_BASE_URL}/prices",
                    headers=self._auth_headers(key),
                    params=params,
                )
            err = self._handle_error_status(resp.status_code, resp.text)
            if err:
                return err
            data = resp.json()
            raw_list = data.get("data", [])
            has_more = data.get("has_more", False)
            normalized: List[Dict[str, Any]] = [self._normalize_price(pr) for pr in raw_list]
            out = {"ok": True, "data": normalized, "has_more": has_more}
            return json.dumps(out, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("stripe HTTP error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)
        except KeyError as e:
            logger.info("stripe KeyError: %s", e)
            return json.dumps({"ok": False, "error_code": "PARSE_ERROR", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)
        except ValueError as e:
            logger.info("stripe ValueError: %s", e)
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)
