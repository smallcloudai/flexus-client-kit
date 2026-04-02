---
name: store-setup
description: Guide the user through setting up a product store — either connecting Shopify or creating an internal product catalog.
---

# Store Setup

First check if a shop already exists: `erp_table_data(table_name="com_shop")`

If no shop exists, ask: **"Do you have a Shopify store to connect, or should I set up a product catalog here?"**

## Shopify Store

1. Connect with `shopify(op="connect", args={"shop_domain": "mystore.myshopify.com"})`
2. Check status with `shopify(op="status")` — products sync automatically
3. Use `shopify(op="help")` for full list of operations: create/update/delete products, manage collections, set discounts, adjust inventory

Connected stores sync products, orders, payments, refunds, and shipments automatically.

## Internal Catalog (No Shopify)

1. Create a shop: `erp_table_crud(op="create", table_name="com_shop", data={"shop_type": "internal", "shop_name": "..."})`
2. Create products: `erp_table_crud(op="create", table_name="com_product", data={...})`
3. Create at least one variant per product — price and inventory live on variants: `erp_table_crud(op="create", table_name="com_product_variant", data={"pvar_product_id": "...", "pvar_price": ..., ...})`

Use `erp_table_meta(table_name="com_product")` and `erp_table_meta(table_name="com_product_variant")` to see available fields.

## Conversational Approach

Walk through the catalog conversationally — ask broad questions, don't go field by field. If they have a website, read it first and propose a catalog. Create products as you go, confirm each one.
