import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("paddle")

PROVIDER_NAME = "paddle"
METHOD_IDS = [
    "paddle.prices.list.v1",
    "paddle.products.list.v1",
    "paddle.subscriptions.list.v1",
    "paddle.transactions.list.v1",
    "paddle.transactions.get.v1",
]

_BASE_URL = "https://api.paddle.com"
_SANDBOX_URL = "https://sandbox-api.paddle.com"


def _base_url() -> str:
    if str(os.environ.get("PADDLE_SANDBOX", "")).lower() == "true":
        return _SANDBOX_URL
    return _BASE_URL


class IntegrationPaddle:
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
            key = os.environ.get("PADDLE_API_KEY", "")
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
        if method_id == "paddle.products.list.v1":
            return await self._products_list(args)
        if method_id == "paddle.prices.list.v1":
            return await self._prices_list(args)
        if method_id == "paddle.subscriptions.list.v1":
            return await self._subscriptions_list(args)
        if method_id == "paddle.transactions.list.v1":
            return await self._transactions_list(args)
        if method_id == "paddle.transactions.get.v1":
            return await self._transactions_get(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _products_list(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("PADDLE_API_KEY", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "PADDLE_API_KEY env var not set"}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {}
        if args.get("status"):
            params["status"] = str(args["status"])
        if args.get("after"):
            params["after"] = str(args["after"])
        per_page = args.get("per_page", 50)
        params["per_page"] = min(max(int(per_page) if per_page is not None else 50, 1), 200)
        if args.get("type"):
            params["type"] = str(args["type"])
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{_base_url()}/products",
                    params=params,
                    headers={"Authorization": f"Bearer {key}"},
                )
            if resp.status_code != 200:
                logger.info("paddle products.list error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            raw_items = data.get("data") or []
            items = []
            for p in raw_items:
                items.append({
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "description": p.get("description"),
                    "status": p.get("status"),
                    "created_at": p.get("created_at"),
                    "custom_data": p.get("custom_data"),
                })
            meta = data.get("meta") or {}
            pagination = meta.get("pagination") or {}
            result: Dict[str, Any] = {
                "ok": True,
                "provider": PROVIDER_NAME,
                "method_id": "paddle.products.list.v1",
                "data": items,
                "meta": {"pagination": {"next": pagination.get("next"), "has_more": pagination.get("has_more", False)}},
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("paddle products.list HTTP error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        except (KeyError, ValueError) as e:
            logger.info("paddle products.list parse error: %s", e)
            return json.dumps({"ok": False, "error_code": "PARSE_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _prices_list(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("PADDLE_API_KEY", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "PADDLE_API_KEY env var not set"}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {}
        if args.get("product_id"):
            params["product_id"] = str(args["product_id"])
        if args.get("status"):
            params["status"] = str(args["status"])
        if args.get("after"):
            params["after"] = str(args["after"])
        per_page = args.get("per_page", 50)
        params["per_page"] = min(max(int(per_page) if per_page is not None else 50, 1), 200)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{_base_url()}/prices",
                    params=params,
                    headers={"Authorization": f"Bearer {key}"},
                )
            if resp.status_code != 200:
                logger.info("paddle prices.list error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            raw_items = data.get("data") or []
            items = []
            for p in raw_items:
                unit_price_obj = p.get("unit_price") or {}
                items.append({
                    "id": p.get("id"),
                    "product_id": p.get("product_id"),
                    "description": p.get("description"),
                    "unit_price": unit_price_obj.get("amount"),
                    "billing_cycle": p.get("billing_cycle"),
                    "status": p.get("status"),
                    "currency_code": unit_price_obj.get("currency_code"),
                })
            meta = data.get("meta") or {}
            pagination = meta.get("pagination") or {}
            result: Dict[str, Any] = {
                "ok": True,
                "provider": PROVIDER_NAME,
                "method_id": "paddle.prices.list.v1",
                "data": items,
                "meta": {"pagination": {"next": pagination.get("next"), "has_more": pagination.get("has_more", False)}},
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("paddle prices.list HTTP error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        except (KeyError, ValueError) as e:
            logger.info("paddle prices.list parse error: %s", e)
            return json.dumps({"ok": False, "error_code": "PARSE_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _subscriptions_list(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("PADDLE_API_KEY", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "PADDLE_API_KEY env var not set"}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {}
        if args.get("status"):
            params["status"] = str(args["status"])
        if args.get("customer_id"):
            params["customer_id"] = str(args["customer_id"])
        if args.get("price_id"):
            params["price_id"] = str(args["price_id"])
        if args.get("after"):
            params["after"] = str(args["after"])
        per_page = args.get("per_page", 20)
        params["per_page"] = min(max(int(per_page) if per_page is not None else 20, 1), 200)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{_base_url()}/subscriptions",
                    params=params,
                    headers={"Authorization": f"Bearer {key}"},
                )
            if resp.status_code != 200:
                logger.info("paddle subscriptions.list error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            raw_items = data.get("data") or []
            items = []
            for s in raw_items:
                billing_cycle = s.get("billing_cycle") or {}
                items.append({
                    "id": s.get("id"),
                    "status": s.get("status"),
                    "customer_id": s.get("customer_id"),
                    "currency_code": s.get("currency_code"),
                    "billing_interval": billing_cycle.get("interval"),
                    "billing_frequency": billing_cycle.get("frequency"),
                    "created_at": s.get("created_at"),
                    "started_at": s.get("started_at"),
                    "next_billed_at": s.get("next_billed_at"),
                    "canceled_at": s.get("canceled_at"),
                })
            meta = data.get("meta") or {}
            pagination = meta.get("pagination") or {}
            result: Dict[str, Any] = {
                "ok": True,
                "provider": PROVIDER_NAME,
                "method_id": "paddle.subscriptions.list.v1",
                "data": items,
                "meta": {"pagination": {"next": pagination.get("next"), "has_more": pagination.get("has_more", False)}},
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("paddle subscriptions.list HTTP error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        except (KeyError, ValueError) as e:
            logger.info("paddle subscriptions.list parse error: %s", e)
            return json.dumps({"ok": False, "error_code": "PARSE_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _transactions_list(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("PADDLE_API_KEY", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "PADDLE_API_KEY env var not set"}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {}
        if args.get("status"):
            params["status"] = str(args["status"])
        if args.get("after"):
            params["after"] = str(args["after"])
        per_page = args.get("per_page", 50)
        params["per_page"] = min(max(int(per_page) if per_page is not None else 50, 1), 200)
        if args.get("customer_id"):
            params["customer_id"] = str(args["customer_id"])
        if args.get("subscription_id"):
            params["subscription_id"] = str(args["subscription_id"])
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{_base_url()}/transactions",
                    params=params,
                    headers={"Authorization": f"Bearer {key}"},
                )
            if resp.status_code != 200:
                logger.info("paddle transactions.list error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            data = resp.json()
            raw_items = data.get("data") or []
            items = []
            for t in raw_items:
                items.append({
                    "id": t.get("id"),
                    "status": t.get("status"),
                    "customer_id": t.get("customer_id"),
                    "subscription_id": t.get("subscription_id"),
                    "currency_code": t.get("currency_code"),
                    "details": t.get("details"),
                    "created_at": t.get("created_at"),
                    "updated_at": t.get("updated_at"),
                })
            meta = data.get("meta") or {}
            pagination = meta.get("pagination") or {}
            result: Dict[str, Any] = {
                "ok": True,
                "provider": PROVIDER_NAME,
                "method_id": "paddle.transactions.list.v1",
                "data": items,
                "meta": {"pagination": {"next": pagination.get("next"), "has_more": pagination.get("has_more", False)}},
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("paddle transactions.list HTTP error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        except (KeyError, ValueError) as e:
            logger.info("paddle transactions.list parse error: %s", e)
            return json.dumps({"ok": False, "error_code": "PARSE_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _transactions_get(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("PADDLE_API_KEY", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": "PADDLE_API_KEY env var not set"}, indent=2, ensure_ascii=False)
        transaction_id = args.get("transaction_id")
        if not transaction_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "transaction_id required"}, indent=2, ensure_ascii=False)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{_base_url()}/transactions/{transaction_id}",
                    headers={"Authorization": f"Bearer {key}"},
                )
            if resp.status_code != 200:
                logger.info("paddle transactions.get error %s: %s", resp.status_code, resp.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)
            raw = resp.json()
            t = raw.get("data") or raw
            result: Dict[str, Any] = {
                "ok": True,
                "provider": PROVIDER_NAME,
                "method_id": "paddle.transactions.get.v1",
                "data": {
                    "id": t.get("id"),
                    "status": t.get("status"),
                    "customer_id": t.get("customer_id"),
                    "subscription_id": t.get("subscription_id"),
                    "currency_code": t.get("currency_code"),
                    "details": t.get("details"),
                    "created_at": t.get("created_at"),
                    "updated_at": t.get("updated_at"),
                    "items": t.get("items"),
                },
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("paddle transactions.get HTTP error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        except (KeyError, ValueError) as e:
            logger.info("paddle transactions.get parse error: %s", e)
            return json.dumps({"ok": False, "error_code": "PARSE_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
