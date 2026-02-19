import asyncio
import logging
import os
import re
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

import httpx
import gql.transport.exceptions

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_external_auth
from flexus_client_kit import ckit_erp
from flexus_client_kit import erp_schema

logger = logging.getLogger("shopify")

API_VER = "2026-01"

SHOPIFY_SCOPES = [
    "read_all_orders", "read_customers", "read_discounts", "write_draft_orders",
    "read_draft_orders", "read_fulfillments", "read_inventory", "read_orders", "read_products",
]

SHOPIFY_SETUP_SCHEMA = []

SHOPIFY_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="shopify",
    description='Manage Shopify stores, call with op="help" for usage',
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Start with 'help' for usage"},
            "args": {"type": "object"},
        },
        "required": [],
    },
)

SHOPIFY_PROMPT = """## Shopify

Use shopify() tool to connect Shopify stores and manage products/orders. Call shopify(op="help") first.
Connected stores sync products, orders, payments, refunds, and shipments automatically.
You can create draft orders (carts with checkout links) for customers."""

HELP = """Help:

shopify(op="connect", args={"shop": "mystore.myshopify.com"})
    Connect a Shopify store via OAuth. Returns authorization URL.

shopify(op="status")
    Show connected shops and sync status.

shopify(op="sync", args={"shop_id": "..."})
    Manually re-sync products and recent orders for a shop.
    If only one shop is connected, shop_id is optional.

shopify(op="create_draft_order", args={
    "shop_id": "...",
    "line_items": [{"variant_id": "123", "quantity": 1}],
    "email": "customer@example.com",
    "note": "VIP order",
})
    Create a draft order and get checkout URL.

shopify(op="disconnect", args={"shop_id": "..."})
    Disconnect a Shopify store (requires confirmation)."""

WEBHOOK_TOPICS = [
    "orders/create", "orders/updated", "orders/cancelled", "orders/paid",
    "refunds/create",
    "fulfillments/create", "fulfillments/update",
    "products/create", "products/update", "products/delete",
]

FIN_STATUS = {
    "pending": "PENDING", "authorized": "AUTHORIZED",
    "partially_paid": "PARTIALLY_PAID", "paid": "PAID",
    "partially_refunded": "PARTIALLY_REFUNDED", "refunded": "REFUNDED",
    "voided": "VOIDED",
}
FUL_STATUS = {
    None: "UNFULFILLED", "unfulfilled": "UNFULFILLED",
    "partial": "PARTIALLY_FULFILLED", "fulfilled": "FULFILLED", "restocked": "RESTOCKED",
}
SHIP_STATUS = {
    "pending": "PENDING", "open": "PENDING",
    "success": "SHIPPED", "in_transit": "IN_TRANSIT",
    "out_for_delivery": "IN_TRANSIT", "delivered": "DELIVERED",
    "cancelled": "FAILED", "error": "FAILED", "failure": "FAILED",
}


# --- HTTP ---

_GQL_ORDER_TRANSACTIONS = """
query FetchOrderTransactions($cursor: String, $query: String) {
  orders(first: 250, after: $cursor, query: $query) {
    nodes {
      legacyResourceId
      transactions {
        id
        amountSet { shopMoney { amount currencyCode } }
        kind
        status
        gateway
        processedAt
      }
    }
    pageInfo { hasNextPage endCursor }
  }
}
"""


async def _fetch_order_transactions(domain, token, cutoff_iso):
    txn_map = {}
    cursor = None
    while True:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(
                f"https://{domain}/admin/api/{API_VER}/graphql.json",
                headers={"X-Shopify-Access-Token": token, "Content-Type": "application/json"},
                json={"query": _GQL_ORDER_TRANSACTIONS, "variables": {"cursor": cursor, "query": f"created_at:>={cutoff_iso[:10]}"}},
            )
            r.raise_for_status()
            data = r.json()
        if data.get("errors"):
            raise Exception(f"Shopify GQL errors: {data['errors']}")
        orders = data["data"]["orders"]
        for node in orders["nodes"]:
            txn_map[node["legacyResourceId"]] = [
                {
                    "id": tx["id"].split("/")[-1],
                    "amount": tx["amountSet"]["shopMoney"]["amount"],
                    "currency": tx["amountSet"]["shopMoney"]["currencyCode"],
                    "kind": tx["kind"].lower(),
                    "status": tx["status"].lower(),
                    "gateway": tx.get("gateway") or "",
                    "created_at": tx.get("processedAt") or "",
                }
                for tx in node.get("transactions") or []
            ]
        if not orders["pageInfo"]["hasNextPage"]:
            break
        cursor = orders["pageInfo"]["endCursor"]
    return txn_map


async def _shop_req(domain, token, method, path, body=None):
    url = f"https://{domain}/admin/api/{API_VER}/{path}"
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.request(method, url, headers={"X-Shopify-Access-Token": token}, json=body)
        r.raise_for_status()
        return r


def _next_link(hdr):
    if not hdr:
        return None
    for part in hdr.split(","):
        if 'rel="next"' in part:
            m = re.search(r'<([^>]+)>', part)
            return m.group(1) if m else None
    return None


async def _paginate(domain, token, path, key, params=None):
    result = []
    url = f"https://{domain}/admin/api/{API_VER}/{path}"
    hdrs = {"X-Shopify-Access-Token": token}
    p = dict(params or {}, limit=250)
    async with httpx.AsyncClient(timeout=30) as c:
        while url:
            r = await c.get(url, headers=hdrs, params=p)
            r.raise_for_status()
            result.extend(r.json().get(key, []))
            url = _next_link(r.headers.get("link"))
            p = {}  # only first request uses explicit params
    return result


def parse_ts(s):
    if not s:
        return 0.0
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except Exception:
        return 0.0


# --- Mapping ---

def _map_product(ws, shop_id, p):
    return {
        "ws_id": ws, "prod_shop_id": shop_id,
        "prod_external_id": str(p["id"]),
        "prod_name": p.get("title", ""),
        "prod_description": (p.get("body_html") or "")[:2000],
        "prod_type": "physical",
        "prod_category": p.get("product_type", ""),
        "prod_tags": [t.strip() for t in (p.get("tags") or "").split(",") if t.strip()],
        "prod_images": [{"src": i["src"], "alt": i.get("alt", "")} for i in (p.get("images") or [])[:5]],
        "prod_details": {"vendor": p.get("vendor", ""), "handle": p.get("handle", "")},
        "prod_created_ts": parse_ts(p.get("created_at")),
        "prod_modified_ts": parse_ts(p.get("updated_at")),
    }


def _map_variant(ws, v):
    qty = v.get("inventory_quantity") or 0
    inv = "OUT_OF_STOCK" if qty <= 0 else ("LOW_STOCK" if qty < 5 else "IN_STOCK")
    return {
        "ws_id": ws,
        "pvar_external_id": str(v["id"]),
        "pvar_name": v.get("title", "Default"),
        "pvar_sku": v.get("sku") or "",
        "pvar_barcode": v.get("barcode") or "",
        "pvar_price": str(v.get("price", "0")),
        "pvar_compare_at_price": str(v.get("compare_at_price") or "0"),
        "pvar_weight": str(v.get("weight", "0")),
        "pvar_weight_unit": v.get("weight_unit", "kg"),
        "pvar_available_qty": qty,
        "pvar_inventory_status": inv,
        "pvar_options": {f"option{i}": v.get(f"option{i}") for i in (1, 2, 3) if v.get(f"option{i}")},
        "pvar_active": True,
        "pvar_created_ts": parse_ts(v.get("created_at")),
        "pvar_modified_ts": parse_ts(v.get("updated_at")),
    }


def _map_order(ws, shop_id, o, contact_id=None):
    shipping = sum(float(s.get("price", "0")) for s in (o.get("shipping_lines") or []))
    refunded = sum(
        sum(float(t.get("amount", "0")) for t in (r.get("transactions") or []))
        for r in (o.get("refunds") or [])
    )
    return {
        "ws_id": ws, "order_shop_id": shop_id,
        "order_external_id": str(o["id"]),
        "order_number": str(o.get("order_number", o.get("name", ""))),
        "order_contact_id": contact_id,
        "order_email": (o.get("email") or o.get("contact_email") or "").lower(),
        "order_financial_status": FIN_STATUS.get(o.get("financial_status", ""), "PENDING"),
        "order_fulfillment_status": FUL_STATUS.get(o.get("fulfillment_status") or "", "UNFULFILLED"),
        "order_currency": o.get("currency", ""),
        "order_subtotal": str(o.get("subtotal_price", "0")),
        "order_total_tax": str(o.get("total_tax", "0")),
        "order_total_shipping": str(shipping),
        "order_total_discount": str(o.get("total_discounts", "0")),
        "order_total": str(o.get("total_price", "0")),
        "order_total_refunded": str(refunded),
        "order_notes": o.get("note") or "",
        "order_tags": [t.strip() for t in (o.get("tags") or "").split(",") if t.strip()],
        "order_tax_lines": o.get("tax_lines", []),
        "order_shipping_lines": o.get("shipping_lines", []),
        "order_shipments": [_map_fulfillment_entry(f) for f in (o.get("fulfillments") or [])],
        "order_details": {"name": o.get("name", ""), "source": o.get("source_name", "")},
        "order_created_ts": parse_ts(o.get("created_at")),
        "order_modified_ts": parse_ts(o.get("updated_at")),
        "order_cancelled_ts": parse_ts(o.get("cancelled_at")),
    }


def _map_line_item(ws, li):
    total = float(li.get("price", "0")) * int(li.get("quantity", 1)) - float(li.get("total_discount", "0"))
    return {
        "ws_id": ws,
        "oitem_external_id": str(li["id"]),
        "oitem_name": li.get("name") or li.get("title", ""),
        "oitem_sku": li.get("sku") or "",
        "oitem_quantity": int(li.get("quantity", 1)),
        "oitem_unit_price": str(li.get("price", "0")),
        "oitem_total_discount": str(li.get("total_discount", "0")),
        "oitem_total": str(total),
        "oitem_details": {"variant_id": str(li.get("variant_id") or ""), "product_id": str(li.get("product_id") or "")},
    }


def _map_transaction(ws, t):
    st = {"success": "COMPLETED", "failure": "FAILED"}.get(t.get("status"), "PENDING")
    return {
        "ws_id": ws,
        "pay_external_id": str(t["id"]),
        "pay_amount": str(t.get("amount", "0")),
        "pay_currency": t.get("currency", ""),
        "pay_status": st,
        "pay_provider": t.get("gateway", ""),
        "pay_details": {"kind": t.get("kind", ""), "authorization": t.get("authorization", "")},
        "pay_created_ts": parse_ts(t.get("created_at")),
    }


def _map_refund(ws, r):
    amt = sum(float(t.get("amount", "0")) for t in (r.get("transactions") or []))
    cur = ((r.get("transactions") or [{}])[0]).get("currency", "")
    items = []
    for ri in r.get("refund_line_items") or []:
        item = {"line_item_id": str(ri.get("line_item_id", "")), "quantity": ri.get("quantity", 0)}
        item.update(ri.get("line_item") or {})
        items.append(item)
    return {
        "ws_id": ws,
        "refund_external_id": str(r["id"]),
        "refund_amount": str(amt),
        "refund_currency": cur,
        "refund_reason": r.get("note") or "",
        "refund_status": "COMPLETED" if r.get("status", "success") == "success" else "PENDING",
        "refund_line_items": items,
        "refund_created_ts": parse_ts(r.get("created_at")),
    }


def _map_fulfillment_entry(f):
    urls = f.get("tracking_urls") or []
    return {
        "id": str(f["id"]),
        "carrier": f.get("tracking_company") or "",
        "tracking_number": f.get("tracking_number") or "",
        "tracking_url": urls[0] if urls else (f.get("tracking_url") or ""),
        "status": SHIP_STATUS.get(f.get("status", ""), "PENDING"),
        "line_items": [{"id": str(li.get("id", "")), "quantity": li.get("quantity", 0)} for li in (f.get("line_items") or [])],
        "created_ts": parse_ts(f.get("created_at")),
        "modified_ts": parse_ts(f.get("updated_at")),
    }


# --- Integration ---

class IntegrationShopify:

    def __init__(self, fclient: ckit_client.FlexusClient, rcx):
        self.fclient = fclient
        self.rcx = rcx
        self.shops: List[erp_schema.ComShop] = []

    @classmethod
    async def create(cls, fclient, rcx):
        inst = cls(fclient, rcx)
        await inst._load_shops()
        for shop in inst.shops:
            if not shop.shop_sync_cursor:
                try:
                    if wh_err := await inst._register_webhooks(shop):
                        logger.error("webhook setup failed for %s: %s", shop.shop_domain, wh_err)
                    else:
                        await inst._sync_shop(shop)
                except Exception as e:
                    logger.error("initial sync failed for %s: %s", shop.shop_domain, e)
        return inst

    async def _load_shops(self):
        all_shops = await ckit_erp.query_erp_table(
            self.fclient, "com_shop", self.rcx.persona.ws_id, erp_schema.ComShop,
            filters="shop_type:=:SHOPIFY",
        )
        for s in all_shops:
            logger.info("_load_shops raw: domain=%s active=%s archived_ts=%s type=%s id=%s", s.shop_domain, s.shop_active, s.shop_archived_ts, s.shop_type, s.shop_id)
        self.shops = [s for s in all_shops if s.shop_active and not s.shop_archived_ts]
        logger.info("_load_shops filtered: %d shops", len(self.shops))

    async def _get_token(self, shop):
        creds = shop.shop_credentials or {}
        if creds.get("access_token"):
            return creds["access_token"]
        try:
            auth = await ckit_external_auth.decrypt_external_auth(self.fclient, f"shopify:{shop.shop_domain}")
            return (auth or {}).get("access_token")
        except Exception:
            return None

    async def _register_webhooks(self, shop) -> str:
        token = await self._get_token(shop)
        if not token:
            return "No access token for webhook registration"
        if override := os.environ.get("SHOPIFY_WEBHOOK_URL"):
            address_base = override.rstrip("/")
        elif os.environ.get("FLEXUS_ENV") == "production":
            address_base = f"https://flexus.team/v1/webhook/shopify/{shop.shop_id}"
        elif os.environ.get("FLEXUS_ENV") == "staging":
            address_base = f"https://staging.flexus.team/v1/webhook/shopify/{shop.shop_id}"
        else:
            return "Webhook URL not configured: set FLEXUS_ENV or SHOPIFY_WEBHOOK_URL"
        existing = await _paginate(shop.shop_domain, token, "webhooks.json", "webhooks")
        ours = {w["topic"]: w for w in existing if w["topic"] in WEBHOOK_TOPICS}
        for topic, w in list(ours.items()):
            if w.get("address") != address_base:
                try:
                    await _shop_req(shop.shop_domain, token, "DELETE", f"webhooks/{w['id']}.json")
                except Exception:
                    pass
                del ours[topic]
        failed = []
        for topic in WEBHOOK_TOPICS:
            if topic in ours:
                continue
            try:
                await _shop_req(shop.shop_domain, token, "POST", "webhooks.json", {
                    "webhook": {"topic": topic, "address": address_base, "format": "json"},
                })
            except httpx.HTTPStatusError as e:
                body = e.response.text[:200] if e.response else ""
                logger.warning("webhook %s failed for %s: %s %s", topic, shop.shop_domain, e.response.status_code, body)
                failed.append(f"{topic} ({body})" if body else topic)
            except Exception as e:
                logger.warning("webhook %s failed for %s: %s", topic, shop.shop_domain, e)
                failed.append(topic)
        if failed:
            return "Failed to register webhooks: %s" % ", ".join(failed)
        return ""

    async def _sync_shop(self, shop):
        token = await self._get_token(shop)
        if not token:
            return "No access token"
        ws = self.rcx.persona.ws_id
        errors = []

        products = await _paginate(shop.shop_domain, token, "products.json", "products")
        if products:
            err = await self._upsert_products(ws, shop.shop_id, products)
            if err:
                errors.append(err)

        cutoff = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
        orders = await _paginate(
            shop.shop_domain, token, "orders.json", "orders",
            {"status": "any", "created_at_min": cutoff},
        )
        txn_map = await _fetch_order_transactions(shop.shop_domain, token, cutoff)
        for o in orders:
            if str(o["id"]) in txn_map:
                o["transactions"] = txn_map[str(o["id"])]
        if orders:
            err = await self._upsert_orders(ws, shop.shop_id, orders)
            if err:
                errors.append(err)

        await ckit_erp.patch_erp_record(
            self.fclient, "com_shop", ws, shop.shop_id,
            {"shop_sync_cursor": datetime.now(timezone.utc).isoformat()},
        )
        if errors:
            return "Sync errors: " + "; ".join(errors)
        return f"Synced {len(products)} products, {len(orders)} orders for {shop.shop_domain}"

    async def _upsert(self, table, ws, upsert_key, recs):
        try:
            res = await ckit_erp.batch_upsert_erp_records(self.fclient, table, ws, upsert_key, recs)
            if isinstance(res, dict) and res.get("errors"):
                return f"{table}: {res['failed']} failed — {res['errors']}"
        except Exception as e:
            return f"{table} upsert failed: {e}"

    async def _upsert_products(self, ws, shop_id, products):
        recs = [_map_product(ws, shop_id, p) for p in products]
        err = await self._upsert("com_product", ws, "prod_external_id", recs)
        if err:
            return err
        db_prods = await ckit_erp.query_erp_table(
            self.fclient, "com_product", ws, erp_schema.ComProduct,
            filters=f"prod_shop_id:=:{shop_id}", limit=5000,
        )
        ext_to_id = {p.prod_external_id: p.prod_id for p in db_prods}
        var_records = []
        for p in products:
            pid = ext_to_id.get(str(p["id"]))
            if not pid:
                continue
            for v in p.get("variants") or []:
                rec = _map_variant(ws, v)
                rec["pvar_prod_id"] = pid
                var_records.append(rec)
        if var_records:
            err = await self._upsert("com_product_variant", ws, "pvar_external_id", var_records)
            if err:
                return err

    async def _upsert_orders(self, ws, shop_id, orders):
        # Contact linking by email
        emails = {(o.get("email") or "").lower() for o in orders} - {""}
        contact_map = {}
        for email in emails:
            try:
                cs = await ckit_erp.query_erp_table(
                    self.fclient, "crm_contact", ws, erp_schema.CrmContact,
                    filters=f"contact_email:ILIKE:{email}", limit=1,
                )
                if cs:
                    contact_map[email] = cs[0].contact_id
            except Exception:
                pass

        order_recs = [_map_order(ws, shop_id, o, contact_map.get((o.get("email") or "").lower())) for o in orders]
        err = await self._upsert("com_order", ws, "order_external_id", order_recs)
        if err:
            return err

        db_orders = await ckit_erp.query_erp_table(
            self.fclient, "com_order", ws, erp_schema.ComOrder,
            filters=f"order_shop_id:=:{shop_id}", limit=10000,
        )
        ext_to_id = {o.order_external_id: o.order_id for o in db_orders}

        items, payments, refunds = [], [], []
        for o in orders:
            oid = ext_to_id.get(str(o["id"]))
            if not oid:
                continue
            for li in o.get("line_items") or []:
                rec = _map_line_item(ws, li)
                rec["oitem_order_id"] = oid
                items.append(rec)
            for tx in o.get("transactions") or []:
                if tx.get("kind") not in ("sale", "capture") or tx.get("status") != "success":
                    continue
                rec = _map_transaction(ws, tx)
                rec["pay_order_id"] = oid
                payments.append(rec)
            for r in o.get("refunds") or []:
                rec = _map_refund(ws, r)
                rec["refund_order_id"] = oid
                refunds.append(rec)
        errors = []
        for table, key, recs in [
            ("com_order_item", "oitem_external_id", items),
            ("com_payment", "pay_external_id", payments),
            ("com_refund", "refund_external_id", refunds),
        ]:
            if recs:
                e = await self._upsert(table, ws, key, recs)
                if e:
                    errors.append(e)
        if errors:
            return "; ".join(errors)

    # --- Tool interface ---

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        if not model_produced_args:
            return HELP
        op = model_produced_args.get("op", "")
        args, err = ckit_cloudtool.sanitize_args(model_produced_args)
        if err:
            return err
        if not op or "help" in op:
            return HELP
        if op == "connect":
            return await self._op_connect(args, model_produced_args)
        if op == "status":
            return await self._op_status()
        if op == "sync":
            return await self._op_sync(args, model_produced_args)
        if op == "create_draft_order":
            return await self._op_create_draft_order(args, model_produced_args)
        if op == "disconnect":
            return await self._op_disconnect(args, model_produced_args, toolcall)
        return f"Unknown operation: {op}\n\nTry shopify(op='help') for usage."

    async def _op_connect(self, args, mpa):
        shop = ckit_cloudtool.try_best_to_find_argument(args, mpa, "shop", None)
        if not shop:
            return "Missing required: 'shop' (e.g. mystore.myshopify.com)"
        shop = shop.strip().lower().replace("https://", "").replace("http://", "").rstrip("/")
        if "/" in shop:
            shop = shop.split("/")[0]
        if "." not in shop:
            shop += ".myshopify.com"
        for s in self.shops:
            if s.shop_domain == shop:
                return f"Already connected: {shop} (ID: {s.shop_id})"
        try:
            auth_url = await ckit_external_auth.start_external_auth_flow(
                self.fclient, "shopify", self.rcx.persona.ws_id,
                self.rcx.persona.owner_fuser_id, SHOPIFY_SCOPES + [f"shop:{shop}"],
            )
            return f"Please authorize Flexus to access your Shopify store:\n{auth_url}\n\nAfter authorizing, call shopify(op='sync') to complete setup."
        except gql.transport.exceptions.TransportQueryError as e:
            return f"Failed to start OAuth: {e}"

    async def _op_status(self):
        await self._load_shops()
        if not self.shops:
            return "No Shopify stores connected.\nUse shopify(op='connect', args={'shop': 'mystore.myshopify.com'}) to connect."
        lines = ["Connected Shopify stores:\n"]
        for s in self.shops:
            sync = f"synced {s.shop_sync_cursor}" if s.shop_sync_cursor else "not synced"
            lines.append(f"  {s.shop_name} ({s.shop_domain}) [ID: {s.shop_id}] — {sync}")
        return "\n".join(lines)

    async def _op_sync(self, args, mpa):
        shop_id = ckit_cloudtool.try_best_to_find_argument(args, mpa, "shop_id", None)
        if not shop_id:
            await self._load_shops()
            if len(self.shops) == 1:
                shop_id = self.shops[0].shop_id
            elif not self.shops:
                return await self._try_detect_new_shop()
            else:
                return "Multiple shops connected. Specify 'shop_id'. Use shopify(op='status') to list."
        shop = next((s for s in self.shops if s.shop_id == shop_id), None)
        if not shop:
            await self._load_shops()
            shop = next((s for s in self.shops if s.shop_id == shop_id), None)
        if not shop:
            return f"Shop not found: {shop_id}"
        if wh_err := await self._register_webhooks(shop):
            return f"ERROR: Webhook setup failed for {shop.shop_domain}, sync did NOT run. {wh_err}. Check app permissions and try shopify(op='sync') again."
        return await self._sync_shop(shop)

    async def _try_detect_new_shop(self):
        try:
            td = await ckit_external_auth.get_external_auth_token(
                self.fclient, "shopify", self.rcx.persona.ws_id, self.rcx.persona.owner_fuser_id,
            )
        except Exception:
            td = None
        if not td or not td.access_token:
            return "No shops connected and no pending auth.\nUse shopify(op='connect') first."

        domain = None
        for sv in td.scope_values or []:
            if sv.startswith("shop:"):
                domain = sv[5:]
                break
        if not domain:
            return "Auth found but shop domain unknown. Please reconnect."

        try:
            r = await _shop_req(domain, td.access_token, "GET", "shop.json")
            info = r.json()["shop"]
        except Exception as e:
            return f"Failed to verify shop connection: {e}"

        ws = self.rcx.persona.ws_id
        await ckit_erp.create_erp_record(self.fclient, "com_shop", ws, {
            "ws_id": ws,
            "shop_name": info.get("name", domain),
            "shop_type": "SHOPIFY",
            "shop_domain": domain,
            "shop_currency": info.get("currency", "USD"),
            "shop_credentials": {"access_token": td.access_token},
            "shop_active": True,
            "shop_details": {
                "shopify_id": str(info.get("id", "")),
                "email": info.get("email", ""),
                "plan": info.get("plan_name", ""),
            },
        })
        await self._load_shops()
        shop = next((s for s in self.shops if s.shop_domain == domain), None)
        if not shop:
            return f"Created shop record for {domain} but failed to reload."
        if wh_err := await self._register_webhooks(shop):
            return f"ERROR: Webhook setup failed for {domain}, sync did NOT run. {wh_err}. Check app permissions and try shopify(op='sync') again."
        return await self._sync_shop(shop)

    async def _op_create_draft_order(self, args, mpa):
        shop_id = ckit_cloudtool.try_best_to_find_argument(args, mpa, "shop_id", None)
        if not shop_id and len(self.shops) == 1:
            shop_id = self.shops[0].shop_id
        if not shop_id:
            return "Missing 'shop_id'. Use shopify(op='status') to list shops."
        shop = next((s for s in self.shops if s.shop_id == shop_id), None)
        if not shop:
            return f"Shop not found: {shop_id}"
        token = await self._get_token(shop)
        if not token:
            return f"No access token for {shop.shop_domain}."
        line_items = ckit_cloudtool.try_best_to_find_argument(args, mpa, "line_items", None)
        if not line_items:
            return "Missing 'line_items': [{variant_id, quantity}]"
        draft = {"line_items": line_items}
        email = ckit_cloudtool.try_best_to_find_argument(args, mpa, "email", None)
        note = ckit_cloudtool.try_best_to_find_argument(args, mpa, "note", None)
        if email:
            draft["email"] = email
        if note:
            draft["note"] = note
        try:
            r = await _shop_req(shop.shop_domain, token, "POST", "draft_orders.json", {"draft_order": draft})
            d = r.json()["draft_order"]
            return f"Draft order created (ID: {d['id']})\nCheckout: {d.get('invoice_url', '')}"
        except httpx.HTTPStatusError as e:
            return f"Failed: {e.response.text[:300]}"

    async def _op_disconnect(self, args, mpa, toolcall):
        shop_id = ckit_cloudtool.try_best_to_find_argument(args, mpa, "shop_id", None)
        if not shop_id:
            return "Missing 'shop_id'."
        if not toolcall.confirmed_by_human:
            raise ckit_cloudtool.NeedsConfirmation(
                confirm_setup_key="shopify_disconnect",
                confirm_command=f"shopify disconnect {shop_id}",
                confirm_explanation="This will disconnect the Shopify store and stop syncing",
            )
        shop = next((s for s in self.shops if s.shop_id == shop_id), None)
        if shop:
            try:
                token = await self._get_token(shop)
                if token:
                    for w in await _paginate(shop.shop_domain, token, "webhooks.json", "webhooks"):
                        if w["topic"] in WEBHOOK_TOPICS:
                            await _shop_req(shop.shop_domain, token, "DELETE", f"webhooks/{w['id']}.json")
            except Exception as e:
                logger.warning("failed to delete webhooks for %s: %s", shop_id, e)
        await ckit_erp.patch_erp_record(
            self.fclient, "com_shop", self.rcx.persona.ws_id, shop_id,
            {"shop_archived_ts": time.time(), "shop_active": False},
        )
        await self._load_shops()
        return f"Shop {shop_id} disconnected."

    def close(self):
        pass
