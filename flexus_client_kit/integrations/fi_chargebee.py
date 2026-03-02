import json
import logging
import os
from typing import Any, Dict, List

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("chargebee")

PROVIDER_NAME = "chargebee"
METHOD_IDS = [
    "chargebee.invoices.list.v1",
    "chargebee.subscriptions.list.v1",
]

_TIMEOUT = 30.0


def _base_url() -> str:
    site = os.environ.get("CHARGEBEE_SITE", "")
    return f"https://{site}.chargebee.com/api/v2" if site else ""


def _check_credentials() -> tuple[str, str]:
    api_key = os.environ.get("CHARGEBEE_API_KEY", "").strip()
    site = os.environ.get("CHARGEBEE_SITE", "").strip()
    return api_key, site


class IntegrationChargebee:
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
            api_key, site = _check_credentials()
            status = "available" if (api_key and site) else "no_credentials"
            return json.dumps({
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": status,
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
        if method_id == "chargebee.subscriptions.list.v1":
            return await self._subscriptions_list(call_args)
        if method_id == "chargebee.invoices.list.v1":
            return await self._invoices_list(call_args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _no_credentials(self) -> str:
        return json.dumps({
            "ok": False,
            "error_code": "NO_CREDENTIALS",
            "provider": PROVIDER_NAME,
            "message": "CHARGEBEE_API_KEY or CHARGEBEE_SITE env var not set",
        }, indent=2, ensure_ascii=False)

    def _handle_error_status(self, status: int, text: str) -> str | None:
        if status == 401:
            return json.dumps({
                "ok": False,
                "error_code": "AUTH_ERROR",
                "provider": PROVIDER_NAME,
                "message": "CHARGEBEE_API_KEY invalid or expired",
            }, indent=2, ensure_ascii=False)
        if status >= 400:
            logger.info("chargebee error %s: %s", status, text[:200])
            return json.dumps({
                "ok": False,
                "error_code": "PROVIDER_ERROR",
                "provider": PROVIDER_NAME,
                "status": status,
                "detail": text[:500],
            }, indent=2, ensure_ascii=False)
        return None

    def _normalize_subscription(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        sub = entry.get("subscription") or {}
        items = sub.get("subscription_items") or []
        plan_id = None
        amount = sub.get("total_dues")
        if items:
            first = items[0]
            plan_id = first.get("item_price_id") or first.get("item_id")
            if amount is None:
                amount = sum(i.get("amount", 0) for i in items)
        return {
            "id": sub.get("id"),
            "customer_id": sub.get("customer_id"),
            "plan_id": plan_id,
            "status": sub.get("status"),
            "current_term_start": sub.get("current_term_start"),
            "current_term_end": sub.get("current_term_end"),
            "amount": amount,
            "currency_code": sub.get("currency_code"),
        }

    def _normalize_invoice(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        inv = entry.get("invoice") or entry
        return {
            "id": inv.get("id"),
            "subscription_id": inv.get("subscription_id"),
            "customer_id": inv.get("customer_id"),
            "status": inv.get("status"),
            "amount_paid": inv.get("amount_paid"),
            "amount_due": inv.get("amount_due"),
            "currency_code": inv.get("currency_code"),
            "date": inv.get("date"),
            "due_date": inv.get("due_date"),
        }

    async def _subscriptions_list(self, args: Dict[str, Any]) -> str:
        api_key, site = _check_credentials()
        if not api_key or not site:
            return self._no_credentials()

        limit = min(max(int(args.get("limit", 20)), 1), 100)
        offset = str(args.get("offset", "")).strip() or None
        status = str(args.get("status", "")).strip() or None
        plan_id = str(args.get("plan_id", "")).strip() or None
        customer_id = str(args.get("customer_id", "")).strip() or None

        params: Dict[str, Any] = {"limit": limit}
        if offset:
            params["offset"] = offset
        if status:
            params["status[is]"] = status
        if plan_id:
            params["plan_id[is]"] = plan_id
        if customer_id:
            params["customer_id[is]"] = customer_id

        try:
            base = _base_url()
            if not base:
                return self._no_credentials()
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.get(
                    f"{base}/subscriptions",
                    auth=(api_key, ""),
                    params=params,
                )
            err = self._handle_error_status(resp.status_code, resp.text)
            if err:
                return err
            data = resp.json()
            raw_list = data.get("list", [])
            next_offset = data.get("next_offset")
            normalized: List[Dict[str, Any]] = [self._normalize_subscription(e) for e in raw_list]
            out = {"ok": True, "data": normalized, "next_offset": next_offset}
            return json.dumps(out, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("chargebee HTTP error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)
        except KeyError as e:
            logger.info("chargebee KeyError: %s", e)
            return json.dumps({"ok": False, "error_code": "PARSE_ERROR", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)
        except ValueError as e:
            logger.info("chargebee ValueError: %s", e)
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)

    async def _invoices_list(self, args: Dict[str, Any]) -> str:
        api_key, site = _check_credentials()
        if not api_key or not site:
            return self._no_credentials()

        limit = min(max(int(args.get("limit", 20)), 1), 100)
        offset = str(args.get("offset", "")).strip() or None
        status = str(args.get("status", "")).strip() or None
        subscription_id = str(args.get("subscription_id", "")).strip() or None
        customer_id = str(args.get("customer_id", "")).strip() or None

        params: Dict[str, Any] = {"limit": limit}
        if offset:
            params["offset"] = offset
        if status:
            params["status[is]"] = status
        if subscription_id:
            params["subscription_id[is]"] = subscription_id
        if customer_id:
            params["customer_id[is]"] = customer_id

        try:
            base = _base_url()
            if not base:
                return self._no_credentials()
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.get(
                    f"{base}/invoices",
                    auth=(api_key, ""),
                    params=params,
                )
            err = self._handle_error_status(resp.status_code, resp.text)
            if err:
                return err
            data = resp.json()
            raw_list = data.get("list", [])
            next_offset = data.get("next_offset")
            normalized: List[Dict[str, Any]] = [self._normalize_invoice(e) for e in raw_list]
            out = {"ok": True, "data": normalized, "next_offset": next_offset}
            return json.dumps(out, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            logger.info("chargebee HTTP error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)
        except KeyError as e:
            logger.info("chargebee KeyError: %s", e)
            return json.dumps({"ok": False, "error_code": "PARSE_ERROR", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)
        except ValueError as e:
            logger.info("chargebee ValueError: %s", e)
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "provider": PROVIDER_NAME, "detail": str(e)}, indent=2, ensure_ascii=False)
