import contextlib
import logging
import os
import re
import urllib.parse
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

import httpx
import gql.transport.exceptions

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_external_auth
from flexus_client_kit import ckit_erp
from flexus_client_kit import erp_schema

logger = logging.getLogger("shopify")

API_VER = "2026-01"

SHOPIFY_SCOPES = [
    "read_customers", "read_discounts", "write_discounts", "write_draft_orders",
    "read_draft_orders", "read_fulfillments", "read_inventory", "write_inventory",
    "read_orders", "read_products", "write_products",
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
You can create/update/delete products, manage collections, set discounts, adjust inventory,
and create draft orders (carts with checkout links) for customers."""

SHOPIFY_CART_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="shopify_cart",
    description='Manage shopping cart (Shopify draft order). ops: create, add, remove, view.',
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "enum": ["create", "add", "remove", "view"], "description": "Operation"},
            "draft_order_id": {"type": "string", "description": "Draft order ID (from create). Required for add/remove/view."},
            "line_items": {
                "type": "array",
                "description": "Items: [{variant_id, quantity}]. variant_id = pvar_external_id from com_product_variant.",
                "items": {"type": "object", "properties": {"variant_id": {"type": "string"}, "quantity": {"type": "integer"}}},
            },
            "variant_id": {"type": "string", "description": "Variant to remove (for op=remove)"},
            "email": {"type": "string", "description": "Customer email (optional, for create)"},
            "note": {"type": "string", "description": "Order note (optional, for create)"},
        },
        "required": ["op"],
    },
)

SHOPIFY_SALES_PROMPT = """## Shopify Products & Cart

Products are in com_product / com_product_variant ERP tables. Use pvar_external_id as variant_id in cart operations.

Recommend products naturally, build the cart incrementally, share the checkout link when ready."""

HELP = """Help:

shopify(op="connect", args={"shop_domain": "mystore.myshopify.com"})
    Connect a Shopify store via OAuth. Only one store at a time.

shopify(op="status")
    Show connected shop and sync status.

shopify(op="sync")
    Manually re-sync products and recent orders.

shopify(op="create_product", args={
    "title": "Product Name", "body_html": "<p>Description</p>",
    "vendor": "Brand", "product_type": "Category", "tags": "tag1, tag2",
    "options": ["Color", "Size"],
    "variants": [{"option1": "Black", "option2": "S", "price": "12.99", "sku": "SKU-BLK-S", "inventory_quantity": 10}],
    "images": ["https://example.com/img.jpg"],
})
    Create a product. variants, options, and images are optional.
    Use options to name variant axes (e.g. ["Color","Size"]), then option1/option2 in each variant.
    Response includes variant IDs — save them for update_variant, cart operations.

shopify(op="update_product", args={"product_id": "...", "title": "New Title", ...})
    Update product fields (title, body_html, vendor, product_type, tags, images). No variants here — use create/update/delete_variant.

shopify(op="delete_product", args={"product_id": "..."})
    Delete a product (requires confirmation).

shopify(op="create_variant", args={"product_id": "...", "price": "29.99", "sku": "SKU2", "option1": "Blue"})
    Add a variant to a product.

shopify(op="update_variant", args={"variant_id": "...", "price": "19.99", "inventory_quantity": 50})
    Update a variant's fields.

shopify(op="delete_variant", args={"product_id": "...", "variant_id": "..."})
    Delete a variant (requires confirmation).

shopify(op="create_collection", args={
    "title": "Collection Name", "body_html": "<p>Description</p>",
})
    Create a custom collection.

shopify(op="create_discount", args={
    "title": "SUMMER20", "value_type": "percentage", "value": "-20.0",
    "target_type": "line_item", "target_selection": "all",
    "starts_at": "2026-01-01T00:00:00Z", "ends_at": "2026-06-01T00:00:00Z",
})
    Create a price rule discount. value_type: percentage or fixed_amount. ends_at is optional.

shopify(op="list_discounts")
    List all discount codes and their price rules.

shopify(op="list_collections")
    List all custom collections.

shopify(op="update_inventory", args={
    "inventory_item_id": "...", "location_id": "...", "available": 50,
})
    Set inventory level. Get inventory_item_id from product variants, location_id from shop.

shopify(op="disconnect")
    Disconnect the Shopify store."""

_VARIANT_KEYS = ("price", "sku", "barcode", "compare_at_price", "option1", "option2", "option3", "weight", "weight_unit", "inventory_quantity")

WEBHOOK_TOPICS = [
    "customers/create", "customers/update",
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

_GQL_COLLECTIONS = """
query FetchCollections($cursor: String) {
  collections(first: 50, after: $cursor) {
    nodes {
      id
      title
      productsCount { count }
      products(first: 3) { nodes { title } }
    }
    pageInfo { hasNextPage endCursor }
  }
}
"""

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


async def _fetch_order_transactions(domain: str, token: str, cutoff_iso: str) -> dict:
    txn_map = {}
    cursor = None
    async with httpx.AsyncClient(timeout=30) as c:
        while True:
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


async def _shop_req(domain: str, token: str, method: str, path: str, body: Optional[dict] = None, c: Optional[httpx.AsyncClient] = None) -> httpx.Response:
    url = f"https://{domain}/admin/api/{API_VER}/{path}"
    async with (contextlib.nullcontext(c) if c else httpx.AsyncClient(timeout=30)) as client:
        r = await client.request(method, url, headers={"X-Shopify-Access-Token": token}, json=body)
        r.raise_for_status()
        return r


def _next_link(hdr: Optional[str]) -> Optional[str]:
    if not hdr:
        return None
    for part in hdr.split(","):
        if 'rel="next"' in part:
            m = re.search(r'<([^>]+)>', part)
            return m.group(1) if m else None
    return None


async def _paginate(domain: str, token: str, path: str, key: str, params: Optional[dict] = None) -> list:
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


def parse_ts(s: Optional[str]) -> float:
    if not s:
        return 0.0
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except Exception:
        return 0.0


# --- Mapping ---

def _map_product(ws: str, shop_id: str, p: dict) -> dict:
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


def _map_variant(ws: str, v: dict) -> dict:
    qty = v.get("inventory_quantity") or 0
    inv = "OUT_OF_STOCK" if qty <= 0 else ("LOW_STOCK" if qty < 5 else "IN_STOCK")
    return {
        "ws_id": ws,
        "pvar_external_id": str(v["id"]),
        "prod_external_id": str(v.get("product_id", "")),
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


def _map_order(ws: str, shop_id: str, o: dict) -> dict:
    shipping = sum(float(s.get("price", "0")) for s in (o.get("shipping_lines") or []))
    refunded = sum(
        sum(float(t.get("amount", "0")) for t in (r.get("transactions") or []))
        for r in (o.get("refunds") or [])
    )
    email = (o.get("email") or o.get("contact_email") or "").lower()
    return {
        "ws_id": ws, "order_shop_id": shop_id,
        "order_external_id": str(o["id"]),
        "order_number": str(o.get("order_number", o.get("name", ""))),
        "contact_email": email,
        "order_email": email,
        "order_financial_status": FIN_STATUS.get(o.get("financial_status", ""), "PENDING"),
        "order_fulfillment_status": FUL_STATUS.get(o.get("fulfillment_status"), "UNFULFILLED"),
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
        "order_shipping_charges": o.get("shipping_lines", []),
        "order_shipments": [_map_fulfillment_entry(f) for f in (o.get("fulfillments") or [])],
        "order_details": {"name": o.get("name", ""), "source": o.get("source_name", "")},
        "order_created_ts": parse_ts(o.get("created_at")),
        "order_modified_ts": parse_ts(o.get("updated_at")),
        "order_cancelled_ts": parse_ts(o.get("cancelled_at")),
    }


def _map_line_item(ws: str, li: dict) -> dict:
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


def _map_transaction(ws: str, t: dict) -> dict:
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


def _map_refund(ws: str, r: dict) -> dict:
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
        "refund_status": "COMPLETED",
        "refund_line_items": items,
        "refund_created_ts": parse_ts(r.get("created_at")),
    }


def _map_fulfillment_entry(f: dict) -> dict:
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

    def __init__(self, fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext):
        self.fclient = fclient
        self.rcx = rcx
        self.shop: Optional[erp_schema.ComShop] = None

    async def _load_current_shop(self) -> None:
        auth = self.rcx.external_auth.get("shopify")
        if not (domain := (auth.auth_key2value.get("url_template_vars") or {}).get("shop_domain") if auth else None):
            self.shop = None
            return
        shops = await ckit_erp.query_erp_table(
            self.fclient, "com_shop", self.rcx.persona.ws_id, erp_schema.ComShop,
            filters={"AND": ["shop_type:=:SHOPIFY", f"shop_domain:=:{domain}"]},
        )
        self.shop = next(iter(shops), None)

    def _get_token(self) -> Optional[str]:
        auth = self.rcx.external_auth.get("shopify")
        return (auth.auth_key2value.get("token") or {}).get("access_token") if auth else None

    async def _register_webhooks(self) -> str:
        if not (token := self._get_token()):
            return "No access token for webhook registration"
        if override := os.environ.get("SHOPIFY_WEBHOOK_URL"):
            address_base = override.rstrip("/")
        elif os.environ.get("FLEXUS_ENV") == "production":
            address_base = f"https://flexus.team/v1/webhook/shopify/{self.shop.shop_id}"
        elif os.environ.get("FLEXUS_ENV") == "staging":
            address_base = f"https://staging.flexus.team/v1/webhook/shopify/{self.shop.shop_id}"
        else:
            return "Webhook URL not configured: set FLEXUS_ENV or SHOPIFY_WEBHOOK_URL"
        existing = await _paginate(self.shop.shop_domain, token, "webhooks.json", "webhooks")
        ours = {w["topic"]: w for w in existing if w["topic"] in WEBHOOK_TOPICS}
        async with httpx.AsyncClient(timeout=30) as c:
            for topic, w in list(ours.items()):
                if w.get("address") != address_base:
                    try:
                        await _shop_req(self.shop.shop_domain, token, "DELETE", f"webhooks/{w['id']}.json", c=c)
                    except httpx.HTTPStatusError as e:
                        if e.response.status_code != 404:
                            logger.warning("failed to delete webhook %s: %s", w['id'], e)
                    except Exception as e:
                        logger.warning("failed to delete webhook %s: %s", w['id'], e)
                    del ours[topic]
        failed = []
        async with httpx.AsyncClient(timeout=30) as c:
            for topic in WEBHOOK_TOPICS:
                if topic in ours:
                    continue
                try:
                    await _shop_req(self.shop.shop_domain, token, "POST", "webhooks.json", {
                        "webhook": {"topic": topic, "address": address_base, "format": "json"},
                    }, c=c)
                except httpx.HTTPStatusError as e:
                    body = e.response.text[:200] if e.response else ""
                    logger.warning("webhook %s failed for %s: %s %s", topic, self.shop.shop_domain, e.response.status_code, body)
                    failed.append(f"{topic} ({body})" if body else topic)
                except Exception as e:
                    logger.warning("webhook %s failed for %s: %s", topic, self.shop.shop_domain, e)
                    failed.append(topic)
        if failed:
            return "Failed to register webhooks: %s" % ", ".join(failed)
        return ""

    async def _sync_shop(self) -> str:
        if not (token := self._get_token()):
            return "No access token"
        ws = self.rcx.persona.ws_id
        errors = []

        products = await _paginate(self.shop.shop_domain, token, "products.json", "products")
        if products:
            err = await self._upsert_products(products)
            if err:
                errors.append(err)

        cutoff = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
        orders = await _paginate(
            self.shop.shop_domain, token, "orders.json", "orders",
            {"status": "any", "created_at_min": cutoff},
        )
        txn_map = await _fetch_order_transactions(self.shop.shop_domain, token, cutoff)
        for o in orders:
            if str(o["id"]) in txn_map:
                o["transactions"] = txn_map[str(o["id"])]
        if orders:
            err = await self._upsert_orders(orders)
            if err:
                errors.append(err)

        await ckit_erp.patch_erp_record(
            self.fclient, "com_shop", ws, self.shop.shop_id,
            {"shop_sync_cursor": datetime.now(timezone.utc).isoformat()},
        )
        if errors:
            return "Sync errors: " + "; ".join(errors)
        return f"Synced {len(products)} products, {len(orders)} orders for {self.shop.shop_domain}"

    async def _upsert(self, table: str, ws: str, upsert_key: str, recs: list, fk_from: str = "", fk_table: str = "", fk_id: str = "", fk_to: str = "", fk_case_insensitive: bool = False) -> str:
        try:
            res = await ckit_erp.batch_upsert_erp_records(self.fclient, table, ws, upsert_key, recs, fk_from=fk_from, fk_table=fk_table, fk_id=fk_id, fk_to=fk_to, fk_case_insensitive=fk_case_insensitive)
            if isinstance(res, dict) and res.get("errors"):
                return f"{table}: {res['failed']} failed — {res['errors']}"
            return ""
        except Exception as e:
            return f"{table} upsert failed: {e}"

    async def _upsert_products(self, products: list) -> Optional[str]:
        ws, shop_id = self.rcx.persona.ws_id, self.shop.shop_id
        err = await self._upsert("com_product", ws, "prod_external_id", [_map_product(ws, shop_id, p) for p in products])
        if err:
            return err
        var_records = [_map_variant(ws, v) for p in products for v in (p.get("variants") or [])]
        if var_records:
            return await self._upsert("com_product_variant", ws, "pvar_external_id", var_records,
                fk_from="prod_external_id", fk_table="com_product", fk_id="prod_id", fk_to="pvar_prod_id")

    async def _upsert_orders(self, orders: list) -> Optional[str]:
        ws, shop_id = self.rcx.persona.ws_id, self.shop.shop_id
        contacts = {}
        for o in orders:
            email = (o.get("email") or o.get("contact_email") or "").strip().lower()
            if not email or email in contacts:
                continue
            c = o.get("customer") or {}
            addr = (c.get("default_address") or {})
            contacts[email] = {
                "ws_id": ws, "contact_email": email,
                "contact_first_name": c.get("first_name") or "",
                "contact_last_name": c.get("last_name") or "",
                "contact_phone": c.get("phone") or "",
                "contact_address_line1": addr.get("address1") or "",
                "contact_address_city": addr.get("city") or "",
                "contact_address_state": addr.get("province") or "",
                "contact_address_zip": addr.get("zip") or "",
                "contact_address_country": addr.get("country") or "",
            }
        if contacts:
            await self._upsert("crm_contact", ws, "contact_email", list(contacts.values()))
        err = await self._upsert("com_order", ws, "order_external_id", [_map_order(ws, shop_id, o) for o in orders],
            fk_from="contact_email", fk_table="crm_contact", fk_id="contact_id", fk_to="order_contact_id", fk_case_insensitive=True)
        if err:
            return err

        items, payments, refunds = [], [], []
        for o in orders:
            ext_id = str(o["id"])
            for li in o.get("line_items") or []:
                items.append({**_map_line_item(ws, li), "order_external_id": ext_id})
            for tx in o.get("transactions") or []:
                if tx.get("kind") not in ("sale", "capture") or tx.get("status") != "success":
                    continue
                payments.append({**_map_transaction(ws, tx), "order_external_id": ext_id})
            for r in o.get("refunds") or []:
                refunds.append({**_map_refund(ws, r), "order_external_id": ext_id})
        errors = []
        for table, key, fk_to, recs in [
            ("com_order_item", "oitem_external_id", "oitem_order_id", items),
            ("com_payment", "pay_external_id", "pay_order_id", payments),
            ("com_refund", "refund_external_id", "refund_order_id", refunds),
        ]:
            if recs:
                e = await self._upsert(table, ws, key, recs,
                    fk_from="order_external_id", fk_table="com_order", fk_id="order_id", fk_to=fk_to)
                if e:
                    errors.append(e)
        if errors:
            return "; ".join(errors)

    # --- Tool interface ---

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[dict[str, Any]]) -> str:
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
            return await self._op_sync()
        if op == "create_product":
            return await self._op_create_product(args, model_produced_args)
        if op == "update_product":
            return await self._op_update_product(args, model_produced_args)
        if op == "delete_product":
            return await self._op_delete_product(args, model_produced_args, toolcall)
        if op == "create_variant":
            return await self._op_create_variant(args, model_produced_args)
        if op == "update_variant":
            return await self._op_update_variant(args, model_produced_args)
        if op == "delete_variant":
            return await self._op_delete_variant(args, model_produced_args, toolcall)
        if op == "list_collections":
            return await self._op_list_collections()
        if op == "create_collection":
            return await self._op_create_collection(args, model_produced_args)
        if op == "list_discounts":
            return await self._op_list_discounts()
        if op == "create_discount":
            return await self._op_create_discount(args, model_produced_args)
        if op == "update_inventory":
            return await self._op_update_inventory(args, model_produced_args)
        if op == "create_draft_order":
            return await self._op_create_draft_order(args, model_produced_args)
        if op == "disconnect":
            return await self._op_disconnect(toolcall)
        return f"Unknown operation: {op}\n\nTry shopify(op='help') for usage."

    async def _op_connect(self, args: dict, model_produced_args: Optional[dict[str, Any]]) -> str:
        existing = await ckit_erp.query_erp_table(
            self.fclient, "com_shop", self.rcx.persona.ws_id, erp_schema.ComShop,
            filters="shop_type:=:SHOPIFY",
        )
        shop_domain = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "shop_domain", None)
        if not shop_domain:
            return "Missing required: 'shop_domain' (e.g. mystore.myshopify.com)"
        s = shop_domain.strip().lower()
        shop_domain = urllib.parse.urlparse(s if "://" in s else f"https://{s}").hostname or s
        if "." not in shop_domain:
            shop_domain += ".myshopify.com"
        if active := next(iter(existing), None):
            if active.shop_domain == shop_domain:
                return f"Already connected: {shop_domain}."
            return f"Already connected: {active.shop_domain}. Disconnect first with shopify(op='disconnect')."
        try:
            auth_url = await ckit_external_auth.start_external_auth_flow(
                self.fclient, "shopify", self.rcx.persona.ws_id,
                self.rcx.persona.owner_fuser_id, SHOPIFY_SCOPES,
                url_template_vars={"shop_domain": shop_domain},
                persona_id=self.rcx.persona.persona_id,
            )
            return f"Please authorize Flexus to access your Shopify store:\n{auth_url}\n\nAfter authorizing, call shopify(op='sync') to complete setup."
        except gql.transport.exceptions.TransportQueryError as e:
            return f"Failed to start OAuth: {e}"

    async def _op_status(self) -> str:
        await self._load_current_shop()
        if self.shop:
            sync = f"synced {self.shop.shop_sync_cursor}" if self.shop.shop_sync_cursor else "not synced"
            return f"Connected: {self.shop.shop_name} ({self.shop.shop_domain}) — {sync}"
        auth = self.rcx.external_auth.get("shopify")
        domain = (auth.auth_key2value.get("url_template_vars") or {}).get("shop_domain") if auth else None
        if domain:
            return f"{domain} — authorized but not synced yet, call shopify(op='sync') to complete"
        return "No Shopify store connected.\nUse shopify(op='connect', args={'shop_domain': 'mystore.myshopify.com'}) to connect."

    async def _op_sync(self) -> str:
        await self._load_current_shop()
        if not self.shop:
            return await self._try_detect_new_shop()
        if wh_err := await self._register_webhooks():
            return f"ERROR: Webhook setup failed for {self.shop.shop_domain}, sync did NOT run. {wh_err}. Check app permissions and try shopify(op='sync') again."
        return await self._sync_shop()

    async def _try_detect_new_shop(self) -> str:
        auth = self.rcx.external_auth.get("shopify")
        if not auth or not (token := self._get_token()):
            return "No shops connected and no pending auth.\nUse shopify(op='connect') first."
        domain = (auth.auth_key2value.get("url_template_vars") or {}).get("shop_domain")
        if not domain:
            return "Auth found but shop domain unknown. Please reconnect."
        try:
            r = await _shop_req(domain, token, "GET", "shop.json")
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
            "shop_auth_id": auth.auth_id,
            "shop_details": {
                "shopify_id": str(info.get("id", "")),
                "email": info.get("email", ""),
                "plan": info.get("plan_name", ""),
            },
        })
        await self._load_current_shop()
        if not self.shop:
            return f"Created shop record for {domain} but failed to reload."
        if wh_err := await self._register_webhooks():
            return f"ERROR: Webhook setup failed for {domain}, sync did NOT run. {wh_err}. Check app permissions and try shopify(op='sync') again."
        return await self._sync_shop()

    def _product_payload(self, args, model_produced_args, base: dict, include_variants: bool = False) -> dict:
        for key in ("title", "body_html", "vendor", "product_type", "tags"):
            if (val := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, key, None)) is not None:
                base[key] = val
        if include_variants:
            options = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "options", None)
            variants = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "variants", None)
            if variants:
                base["variants"] = variants
                if not options:
                    # auto-infer how many option axes are used so Shopify doesn't drop option2/option3
                    n = max((sum(1 for i in (1, 2, 3) if v.get(f"option{i}")) for v in variants), default=1)
                    options = [f"Option {i}" for i in range(1, n + 1)]
            if options:
                base["options"] = [{"name": o} if isinstance(o, str) else o for o in options]
        if images := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "images", None):
            base["images"] = [{"src": u} if isinstance(u, str) else u for u in images]
        return base

    def _fmt_product(self, p: dict) -> str:
        lines = [f"Product: {p['title']} (ID: {p['id']})"]
        for v in p.get("variants") or []:
            opts = " / ".join(filter(None, [v.get(f"option{i}") for i in (1, 2, 3)]))
            lines.append(f"  variant {v['id']} {opts} price={v['price']} qty={v.get('inventory_quantity', '?')}")
        return "\n".join(lines)

    def _variant_payload(self, args, model_produced_args, base: dict) -> dict:
        for key in _VARIANT_KEYS:
            if (val := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, key, None)) is not None:
                base[key] = val
        return base

    async def _op_create_draft_order(self, args, model_produced_args):
        await self._load_current_shop()
        if not self.shop or not (token := self._get_token()):
            return "No shop connected."
        if not (line_items := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "line_items", None)):
            return "Missing 'line_items': [{variant_id, quantity}]"
        draft = {"line_items": line_items, **{k: v for k in ("email", "note") if (v := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, k, None))}}
        try:
            d = (await _shop_req(self.shop.shop_domain, token, "POST", "draft_orders.json", {"draft_order": draft})).json()["draft_order"]
            return f"Draft order created (ID: {d['id']})\nCheckout: {d.get('invoice_url', '')}"
        except httpx.HTTPStatusError as e:
            return f"Failed: {e.response.text[:300]}"

    async def _op_create_product(self, args, model_produced_args):
        await self._load_current_shop()
        if not self.shop or not (token := self._get_token()):
            return "No shop connected."
        payload = self._product_payload(args, model_produced_args, {}, include_variants=True)
        if not payload.get("title"):
            return "Missing 'title'."
        try:
            p = (await _shop_req(self.shop.shop_domain, token, "POST", "products.json", {"product": payload})).json()["product"]
            return self._fmt_product(p)
        except httpx.HTTPStatusError as e:
            return f"Failed: {e.response.text[:300]}"

    async def _op_update_product(self, args, model_produced_args):
        await self._load_current_shop()
        if not self.shop or not (token := self._get_token()):
            return "No shop connected."
        if not (pid := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "product_id", None)):
            return "Missing 'product_id'."
        try:
            p = (await _shop_req(self.shop.shop_domain, token, "PUT", f"products/{pid}.json", {"product": self._product_payload(args, model_produced_args, {"id": pid})})).json()["product"]
            return self._fmt_product(p)
        except httpx.HTTPStatusError as e:
            return f"Failed: {e.response.text[:300]}"

    async def _op_delete_product(self, args, model_produced_args, toolcall):
        await self._load_current_shop()
        if not self.shop or not (token := self._get_token()):
            return "No shop connected."
        if not (pid := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "product_id", None)):
            return "Missing 'product_id'."
        if not toolcall.confirmed_by_human:
            raise ckit_cloudtool.NeedsConfirmation(
                confirm_setup_key="shopify_delete_product",
                confirm_command=f"shopify delete_product {pid}",
                confirm_explanation=f"This will permanently delete product {pid} from Shopify",
            )
        try:
            await _shop_req(self.shop.shop_domain, token, "DELETE", f"products/{pid}.json")
            return f"Product {pid} deleted."
        except httpx.HTTPStatusError as e:
            return f"Failed: {e.response.text[:300]}"

    async def _op_create_variant(self, args, model_produced_args):
        await self._load_current_shop()
        if not self.shop or not (token := self._get_token()):
            return "No shop connected."
        if not (pid := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "product_id", None)):
            return "Missing 'product_id'."
        payload = self._variant_payload(args, model_produced_args, {})
        if not payload.get("price"):
            return "Missing 'price'."
        try:
            v = (await _shop_req(self.shop.shop_domain, token, "POST", f"products/{pid}/variants.json", {"variant": payload})).json()["variant"]
            return f"Variant created: {v.get('title')} (ID: {v['id']}) price={v.get('price')}"
        except httpx.HTTPStatusError as e:
            return f"Failed: {e.response.text[:300]}"

    async def _op_update_variant(self, args, model_produced_args):
        await self._load_current_shop()
        if not self.shop or not (token := self._get_token()):
            return "No shop connected."
        if not (vid := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "variant_id", None)):
            return "Missing 'variant_id'."
        try:
            v = (await _shop_req(self.shop.shop_domain, token, "PUT", f"variants/{vid}.json", {"variant": self._variant_payload(args, model_produced_args, {"id": vid})})).json()["variant"]
            return f"Variant updated: {v.get('title')} (ID: {v['id']}) price={v.get('price')}"
        except httpx.HTTPStatusError as e:
            return f"Failed: {e.response.text[:300]}"

    async def _op_delete_variant(self, args, model_produced_args, toolcall):
        await self._load_current_shop()
        if not self.shop or not (token := self._get_token()):
            return "No shop connected."
        pid = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "product_id", None)
        vid = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "variant_id", None)
        if not pid or not vid:
            return "Missing 'product_id' and/or 'variant_id'."
        if not toolcall.confirmed_by_human:
            raise ckit_cloudtool.NeedsConfirmation(
                confirm_setup_key="shopify_delete_variant",
                confirm_command=f"shopify delete_variant {vid}",
                confirm_explanation=f"This will permanently delete variant {vid}",
            )
        try:
            await _shop_req(self.shop.shop_domain, token, "DELETE", f"products/{pid}/variants/{vid}.json")
            return f"Variant {vid} deleted."
        except httpx.HTTPStatusError as e:
            return f"Failed: {e.response.text[:300]}"

    async def _op_list_discounts(self):
        await self._load_current_shop()
        if not self.shop or not (token := self._get_token()):
            return "No shop connected."
        rules = await _paginate(self.shop.shop_domain, token, "price_rules.json", "price_rules")
        if not rules:
            return "No discounts found."
        lines = []
        for rule in rules:
            codes = await _paginate(self.shop.shop_domain, token, f"price_rules/{rule['id']}/discount_codes.json", "discount_codes")
            code_str = ", ".join(c["code"] for c in codes) if codes else "(no codes)"
            ends = f" → {rule['ends_at']}" if rule.get("ends_at") else ""
            lines.append(f"- {code_str}: {rule['value_type']} {rule['value']} (rule {rule['id']}, starts {rule['starts_at']}{ends})")
        return "\n".join(lines)

    async def _op_list_collections(self):
        await self._load_current_shop()
        if not self.shop or not (token := self._get_token()):
            return "No shop connected."
        colls, cursor = [], None
        async with httpx.AsyncClient(timeout=30) as c:
            while True:
                r = await c.post(
                    f"https://{self.shop.shop_domain}/admin/api/{API_VER}/graphql.json",
                    headers={"X-Shopify-Access-Token": token, "Content-Type": "application/json"},
                    json={"query": _GQL_COLLECTIONS, "variables": {"cursor": cursor}},
                )
                r.raise_for_status()
                data = r.json()
                if data.get("errors"):
                    return f"Shopify GQL errors: {data['errors']}"
                page = data["data"]["collections"]
                colls.extend(page["nodes"])
                if not page["pageInfo"]["hasNextPage"]:
                    break
                cursor = page["pageInfo"]["endCursor"]
        if not colls:
            return "No collections found."
        lines = []
        for col in colls:
            count = col["productsCount"]["count"]
            sample = ", ".join(p["title"] for p in col["products"]["nodes"])
            cid = col["id"].split("/")[-1]
            lines.append(f"- {col['title']} (ID: {cid}, {count} products{': ' + sample if sample else ''})")
        return "\n".join(lines)

    async def _op_create_collection(self, args, model_produced_args):
        await self._load_current_shop()
        if not self.shop or not (token := self._get_token()):
            return "No shop connected."
        if not (title := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "title", None)):
            return "Missing 'title'."
        coll = {"title": title}
        if body := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "body_html", None):
            coll["body_html"] = body
        try:
            c = (await _shop_req(self.shop.shop_domain, token, "POST", "custom_collections.json", {"custom_collection": coll})).json()["custom_collection"]
            return f"Collection created: {c['title']} (ID: {c['id']})"
        except httpx.HTTPStatusError as e:
            return f"Failed: {e.response.text[:300]}"

    async def _op_create_discount(self, args, model_produced_args):
        await self._load_current_shop()
        if not self.shop or not (token := self._get_token()):
            return "No shop connected."
        if not (title := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "title", None)):
            return "Missing 'title' (discount code)."
        rule = {"title": title}
        for key in ("value_type", "value", "target_type", "target_selection", "starts_at", "ends_at"):
            if (val := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, key, None)) is not None:
                rule[key] = val
        rule.setdefault("value_type", "percentage")
        rule.setdefault("target_type", "line_item")
        rule.setdefault("target_selection", "all")
        if not rule.get("value"):
            return "Missing 'value' (e.g. '-20.0' for 20% off)."
        if not rule.get("starts_at"):
            rule["starts_at"] = datetime.now(timezone.utc).isoformat()
        try:
            pr = (await _shop_req(self.shop.shop_domain, token, "POST", "price_rules.json", {"price_rule": rule})).json()["price_rule"]
            await _shop_req(self.shop.shop_domain, token, "POST", f"price_rules/{pr['id']}/discount_codes.json", {"discount_code": {"code": title}})
            return f"Discount created: {title} ({pr['value_type']} {pr['value']}) — code: {title}"
        except httpx.HTTPStatusError as e:
            return f"Failed: {e.response.text[:300]}"

    async def _op_update_inventory(self, args, model_produced_args):
        await self._load_current_shop()
        if not self.shop or not (token := self._get_token()):
            return "No shop connected."
        inv_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "inventory_item_id", None)
        loc_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "location_id", None)
        available = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "available", None)
        if not inv_id:
            return "Missing 'inventory_item_id'."
        if not loc_id:
            return "Missing 'location_id'."
        if available is None:
            return "Missing 'available' (quantity)."
        try:
            await _shop_req(self.shop.shop_domain, token, "POST", "inventory_levels/set.json", {
                "inventory_item_id": int(inv_id), "location_id": int(loc_id), "available": int(available),
            })
            return f"Inventory updated: item {inv_id} at location {loc_id} set to {available}."
        except httpx.HTTPStatusError as e:
            return f"Failed: {e.response.text[:300]}"

    async def _op_disconnect(self, toolcall):
        if not toolcall.confirmed_by_human:
            raise ckit_cloudtool.NeedsConfirmation(
                confirm_setup_key="shopify_disconnect",
                confirm_command="shopify disconnect",
                confirm_explanation="This will disconnect the Shopify store and stop syncing",
            )
        await self._load_current_shop()
        auth = self.rcx.external_auth.get("shopify")
        if not self.shop:
            if auth:
                await ckit_external_auth.external_auth_disconnect(self.fclient, self.rcx.persona.ws_id, auth.auth_id)
                return "Pending auth disconnected."
            return "No shop connected."
        cleanup_err = None
        try:
            if token := self._get_token():
                async with httpx.AsyncClient(timeout=30) as c:
                    for w in await _paginate(self.shop.shop_domain, token, "webhooks.json", "webhooks"):
                        if w["topic"] in WEBHOOK_TOPICS:
                            await _shop_req(self.shop.shop_domain, token, "DELETE", f"webhooks/{w['id']}.json", c=c)
            if auth:
                await ckit_external_auth.external_auth_disconnect(self.fclient, self.rcx.persona.ws_id, auth.auth_id)
        except Exception as e:
            cleanup_err = str(e)
            logger.warning("failed to clean up shop %s: %s", self.shop.shop_id, e)
        await ckit_erp.patch_erp_record(
            self.fclient, "com_shop", self.rcx.persona.ws_id, self.shop.shop_id,
            {"shop_archived_ts": time.time()},
        )
        if cleanup_err:
            return f"Shop {self.shop.shop_id} disconnected, but cleanup had errors: {cleanup_err}"
        return f"Shop {self.shop.shop_id} disconnected."

    async def handle_cart(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Optional[dict[str, Any]]) -> str:
        if not args or not args.get("op"):
            return "Missing 'op'. Use: create, add, remove, view."
        await self._load_current_shop()
        if not self.shop:
            return "No Shopify store connected. Use shopify(op='connect') first."
        if not (token := self._get_token()):
            return f"No access token for {self.shop.shop_domain}."
        op = args["op"]
        if op == "create":
            return await self._cart_create(token, args)
        if op not in ("add", "remove", "view"):
            return f"Unknown op: {op}. Use: create, add, remove, view."
        doid = args.get("draft_order_id")
        if not doid:
            return "Missing 'draft_order_id'. Create a cart first."
        if op == "view":
            return await self._cart_view(token, doid)
        if op == "add":
            return await self._cart_add(token, doid, args.get("line_items"))
        return await self._cart_remove(token, doid, args.get("variant_id"))

    async def _cart_create(self, token: str, args: dict) -> str:
        if not args.get("line_items"):
            return "Missing 'line_items': [{variant_id, quantity}]"
        draft = {"line_items": args["line_items"], **{k: args[k] for k in ("email", "note") if args.get(k)}}
        try:
            r = await _shop_req(self.shop.shop_domain, token, "POST", "draft_orders.json", {"draft_order": draft})
            return self._fmt_cart(r.json()["draft_order"])
        except httpx.HTTPStatusError as e:
            return f"Failed: {e.response.text[:300]}"

    async def _cart_view(self, token: str, doid: str) -> str:
        try:
            r = await _shop_req(self.shop.shop_domain, token, "GET", f"draft_orders/{doid}.json")
            return self._fmt_cart(r.json()["draft_order"])
        except httpx.HTTPStatusError as e:
            return f"Failed: {e.response.text[:300]}"

    async def _cart_add(self, token: str, doid: str, line_items: Optional[list]) -> str:
        if not line_items:
            return "Missing 'line_items': [{variant_id, quantity}]"
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                r = await _shop_req(self.shop.shop_domain, token, "GET", f"draft_orders/{doid}.json", c=c)
                existing = r.json()["draft_order"]["line_items"]
                # Merge: bump quantity for existing variants, append new ones
                by_vid = {str(li["variant_id"]): li for li in existing}
                for item in line_items:
                    vid = str(item["variant_id"])
                    if vid in by_vid:
                        by_vid[vid]["quantity"] += item.get("quantity", 1)
                    else:
                        by_vid[vid] = {"variant_id": int(vid), "quantity": item.get("quantity", 1)}
                r = await _shop_req(self.shop.shop_domain, token, "PUT", f"draft_orders/{doid}.json", {
                    "draft_order": {"line_items": list(by_vid.values())},
                }, c=c)
            return self._fmt_cart(r.json()["draft_order"])
        except httpx.HTTPStatusError as e:
            return f"Failed: {e.response.text[:300]}"

    async def _cart_remove(self, token: str, doid: str, variant_id: Optional[str]) -> str:
        if not variant_id:
            return "Missing 'variant_id'."
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                r = await _shop_req(self.shop.shop_domain, token, "GET", f"draft_orders/{doid}.json", c=c)
                existing = r.json()["draft_order"]["line_items"]
                updated = [li for li in existing if str(li["variant_id"]) != str(variant_id)]
                if len(updated) == len(existing):
                    return f"Variant {variant_id} not found in cart."
                r = await _shop_req(self.shop.shop_domain, token, "PUT", f"draft_orders/{doid}.json", {
                    "draft_order": {"line_items": updated},
                }, c=c)
            return self._fmt_cart(r.json()["draft_order"])
        except httpx.HTTPStatusError as e:
            return f"Failed: {e.response.text[:300]}"

    def _fmt_cart(self, d: dict) -> str:
        lines = [f"Draft order: {d['id']}"]
        for li in d.get("line_items", []):
            lines.append(f"  - {li.get('title', '?')} (variant {li['variant_id']}) x{li['quantity']} — {li.get('price', '?')}")
        lines.append(f"Total: {d.get('total_price', '?')} {d.get('currency', '')}")
        if d.get("invoice_url"):
            lines.append(f"Checkout: {d['invoice_url']}")
        return "\n".join(lines)

