import dataclasses
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, Dict, Type, List


@dataclass
class CrmActivity:
    ws_id: str
    activity_title: str = field(metadata={"importance": 1, "display_name": "Title"})
    activity_type: str = field(metadata={"importance": 1, "display_name": "Type", "enum": [
        {"value": "WEB_CHAT", "label": "Web Chat"},
        {"value": "MESSENGER_CHAT", "label": "Messenger Chat"},
        {"value": "EMAIL", "label": "Email"},
        {"value": "CALL", "label": "Call"},
        {"value": "MEETING", "label": "Meeting"},
    ]})
    activity_direction: str = field(metadata={"importance": 1, "display_name": "Direction", "enum": [
        {"value": "INBOUND", "label": "Inbound"},
        {"value": "OUTBOUND", "label": "Outbound"},
    ]})
    activity_contact_id: str = field(metadata={"importance": 1, "display_name": "Contact"})
    activity_id: str = field(default="", metadata={"pkey": True, "display_name": "Activity ID"})
    activity_platform: str = field(default="", metadata={"importance": 1, "display_name": "Channel"})
    activity_ft_id: Optional[str] = field(default=None, metadata={"importance": 1, "display_name": "Thread"})
    activity_summary: str = field(default="", metadata={"importance": 1, "display": "string_multiline", "display_name": "Summary"})
    activity_details: dict = field(default_factory=dict, metadata={"display_name": "Details"})
    activity_occurred_ts: float = field(default=0.0, metadata={"importance": 1, "display_name": "Occurred at"})
    activity_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    activity_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})


@dataclass
class CrmContact:
    ws_id: str
    contact_first_name: str = field(metadata={"importance": 1, "display_name": "First Name"})
    contact_last_name: str = field(metadata={"importance": 1, "display_name": "Last Name"})
    contact_email: str = field(metadata={"importance": 1, "extra_search": True, "display_name": "Email"})
    contact_phone: str = field(default="", metadata={"display_name": "Phone"})
    contact_id: str = field(default="", metadata={"pkey": True, "display_name": "Contact ID"})
    contact_notes: str = field(default="", metadata={"importance": 1, "display": "string_multiline", "display_name": "Notes"})
    contact_details: dict = field(default_factory=dict, metadata={"display_name": "Details", "description": "Custom JSON data: BANT qualification reasons, social profiles, preferences, custom attributes"})
    contact_tags: List[str] = field(default_factory=list, metadata={"importance": 1, "display_name": "Tags"})
    contact_address_line1: str = field(default="", metadata={"display_name": "Address Line 1"})
    contact_address_line2: str = field(default="", metadata={"display_name": "Address Line 2"})
    contact_address_city: str = field(default="", metadata={"display_name": "City"})
    contact_address_state: str = field(default="", metadata={"display_name": "State"})
    contact_address_zip: str = field(default="", metadata={"display_name": "ZIP Code"})
    contact_address_country: str = field(default="", metadata={"importance": 1, "display_name": "Country"})
    contact_utm_first_source: str = field(default="", metadata={"importance": 1, "display_name": "UTM Source (first touch)", "description": "First marketing interaction that brought this contact"})
    contact_utm_first_medium: str = field(default="", metadata={"display_name": "UTM Medium (first touch)"})
    contact_utm_first_campaign: str = field(default="", metadata={"display_name": "UTM Campaign (first touch)"})
    contact_utm_first_term: str = field(default="", metadata={"display_name": "UTM Term (first touch)"})
    contact_utm_first_content: str = field(default="", metadata={"display_name": "UTM Content (first touch)"})
    contact_utm_last_source: str = field(default="", metadata={"display_name": "UTM Source (last touch)", "description": "Most recent marketing interaction"})
    contact_utm_last_medium: str = field(default="", metadata={"display_name": "UTM Medium (last touch)"})
    contact_utm_last_campaign: str = field(default="", metadata={"display_name": "UTM Campaign (last touch)"})
    contact_utm_last_term: str = field(default="", metadata={"display_name": "UTM Term (last touch)"})
    contact_utm_last_content: str = field(default="", metadata={"display_name": "UTM Content (last touch)"})
    contact_bant_score: int = field(default=-1, metadata={"display_name": "BANT Score", "description": "How many of Budget/Authority/Need/Timeline criteria met. -1=unqualified, 0-1=cold, 2-3=warm, 4=hot"})
    contact_created_ts: float = field(default=0.0, metadata={"importance": 1, "display_name": "Created at"})
    contact_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})
    contact_archived_ts: float = field(default=0.0, metadata={"display_name": "Archived at"})
    contact_commerce_external: dict = field(default_factory=dict, metadata={"display_name": "Commerce External"})


@dataclass
class CrmDeal:
    ws_id: str
    deal_name: str = field(metadata={"importance": 1, "display_name": "Name"})
    deal_pipeline_id: str = field(metadata={"importance": 1, "display_name": "Pipeline"})
    deal_stage_id: str = field(metadata={"importance": 1, "display_name": "Stage", "fk_scope": {"stage_pipeline_id": "deal_pipeline_id"}})
    deal_id: str = field(default="", metadata={"pkey": True, "display_name": "Deal ID"})
    deal_contact_id: Optional[str] = field(default=None, metadata={"importance": 1, "display_name": "Contact"})
    deal_value: Decimal = field(default=Decimal(0), metadata={"importance": 1, "display_name": "Value"})
    deal_expected_close_ts: float = field(default=0.0, metadata={"importance": 1, "display_name": "Expected Close"})
    deal_closed_ts: float = field(default=0.0, metadata={"display_name": "Closed at"})
    deal_lost_reason: str = field(default="", metadata={"display_name": "Lost Reason"})
    deal_notes: str = field(default="", metadata={"importance": 1, "display": "string_multiline", "display_name": "Notes"})
    deal_tags: List[str] = field(default_factory=list, metadata={"importance": 1, "display_name": "Tags"})
    deal_details: dict = field(default_factory=dict, metadata={"display_name": "Details", "description": "Custom fields JSON"})
    deal_owner_fuser_id: str = field(default="", metadata={"importance": 1, "display_name": "Owner"})
    deal_priority: str = field(default="NONE", metadata={"importance": 1, "display_name": "Priority", "enum": [{"value": "NONE", "label": "None"}, {"value": "LOW", "label": "Low"}, {"value": "MEDIUM", "label": "Medium"}, {"value": "HIGH", "label": "High"}]})
    deal_created_ts: float = field(default=0.0, metadata={"importance": 1, "display_name": "Created at"})
    deal_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})
    deal_archived_ts: float = field(default=0.0, metadata={"display_name": "Archived at"})


@dataclass
class CrmPipeline:
    ws_id: str
    pipeline_name: str = field(metadata={"importance": 1, "display_name": "Name"})
    pipeline_id: str = field(default="", metadata={"pkey": True, "display_name": "Pipeline ID"})
    pipeline_active: bool = field(default=True, metadata={"importance": 1, "display_name": "Active"})
    pipeline_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    pipeline_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})
    pipeline_archived_ts: float = field(default=0.0, metadata={"display_name": "Archived at"})


@dataclass
class CrmPipelineStage:
    ws_id: str
    stage_name: str = field(metadata={"importance": 1, "display_name": "Name"})
    stage_pipeline_id: str = field(metadata={"importance": 1, "display_name": "Pipeline"})
    stage_id: str = field(default="", metadata={"pkey": True, "display_name": "Stage ID"})
    stage_sequence: int = field(default=0, metadata={"display_name": "Sequence"})
    stage_probability: int = field(default=0, metadata={"importance": 1, "display_name": "Win Probability %", "description": "0-100 win probability percentage"})
    stage_status: str = field(default="OPEN", metadata={"importance": 1, "display_name": "Status", "enum": [{"value": "OPEN", "label": "Open"}, {"value": "WON", "label": "Won"}, {"value": "LOST", "label": "Lost"}]})
    stage_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    stage_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})
    stage_archived_ts: float = field(default=0.0, metadata={"display_name": "Archived at"})


@dataclass
class ComOrder:
    ws_id: str
    order_shop_id: str = field(metadata={"importance": 1, "display_name": "Shop"})
    order_id: str = field(default="", metadata={"pkey": True, "display_name": "Order ID"})
    order_external_id: str = field(default="", metadata={"display_name": "External ID"})
    order_number: str = field(default="", metadata={"importance": 1, "display_name": "Order Number"})
    order_contact_id: Optional[str] = field(default=None, metadata={"importance": 1, "display_name": "Contact"})
    order_email: str = field(default="", metadata={"importance": 1, "display_name": "Email"})
    order_financial_status: str = field(default="PENDING", metadata={"importance": 1, "display_name": "Financial Status", "enum": [
        {"value": "PENDING", "label": "Pending"},
        {"value": "PAID", "label": "Paid"},
        {"value": "PARTIALLY_PAID", "label": "Partially Paid"},
        {"value": "REFUNDED", "label": "Refunded"},
        {"value": "PARTIALLY_REFUNDED", "label": "Partially Refunded"},
        {"value": "VOIDED", "label": "Voided"},
    ]})
    order_fulfillment_status: str = field(default="UNFULFILLED", metadata={"importance": 1, "display_name": "Fulfillment Status", "enum": [
        {"value": "UNFULFILLED", "label": "Unfulfilled"},
        {"value": "PARTIAL", "label": "Partial"},
        {"value": "FULFILLED", "label": "Fulfilled"},
    ]})
    order_currency: str = field(default="", metadata={"importance": 1, "display_name": "Currency"})
    order_subtotal: Decimal = field(default=Decimal(0), metadata={"importance": 1, "display_name": "Subtotal"})
    order_total_tax: Decimal = field(default=Decimal(0), metadata={"display_name": "Total Tax"})
    order_total_shipping: Decimal = field(default=Decimal(0), metadata={"display_name": "Total Shipping"})
    order_total_discount: Decimal = field(default=Decimal(0), metadata={"display_name": "Total Discount"})
    order_total: Decimal = field(default=Decimal(0), metadata={"importance": 1, "display_name": "Total"})
    order_total_refunded: Decimal = field(default=Decimal(0), metadata={"display_name": "Total Refunded"})
    order_notes: str = field(default="", metadata={"display": "string_multiline", "display_name": "Notes"})
    order_tags: List[str] = field(default_factory=list, metadata={"importance": 1, "display_name": "Tags"})
    order_tax_lines: list = field(default_factory=list, metadata={"display_name": "Tax Lines"})
    order_shipping_lines: list = field(default_factory=list, metadata={"display_name": "Shipping Lines"})
    order_shipments: list = field(default_factory=list, metadata={"display_name": "Shipments", "description": 'JSON array: [{"id":"ext123","carrier":"FedEx","tracking_number":"FX123","tracking_url":"https://...","status":"SHIPPED","line_items":[{"id":"li_1","quantity":1}],"created_ts":0.0,"modified_ts":0.0}]. Status: PENDING, IN_TRANSIT, SHIPPED, DELIVERED, FAILED.'})
    order_details: dict = field(default_factory=dict, metadata={"display_name": "Details"})
    order_created_ts: float = field(default=0.0, metadata={"importance": 1, "display_name": "Created at"})
    order_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})
    order_cancelled_ts: float = field(default=0.0, metadata={"display_name": "Cancelled at"})
    order_archived_ts: float = field(default=0.0, metadata={"display_name": "Archived at"})


@dataclass
class ComOrderItem:
    ws_id: str
    oitem_order_id: str = field(metadata={"importance": 1, "display_name": "Order"})
    oitem_name: str = field(metadata={"importance": 1, "display_name": "Name"})
    oitem_id: str = field(default="", metadata={"pkey": True, "display_name": "Item ID"})
    oitem_pvar_id: Optional[str] = field(default=None, metadata={"display_name": "Variant"})
    oitem_external_id: str = field(default="", metadata={"display_name": "External ID"})
    oitem_sku: str = field(default="", metadata={"importance": 1, "display_name": "SKU"})
    oitem_quantity: int = field(default=1, metadata={"importance": 1, "display_name": "Quantity"})
    oitem_unit_price: Decimal = field(default=Decimal(0), metadata={"importance": 1, "display_name": "Unit Price"})
    oitem_total_discount: Decimal = field(default=Decimal(0), metadata={"display_name": "Total Discount"})
    oitem_total: Decimal = field(default=Decimal(0), metadata={"importance": 1, "display_name": "Total"})
    oitem_details: dict = field(default_factory=dict, metadata={"display_name": "Details"})
    oitem_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    oitem_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})


@dataclass
class ComPayment:
    ws_id: str
    pay_order_id: str = field(metadata={"importance": 1, "display_name": "Order"})
    pay_id: str = field(default="", metadata={"pkey": True, "display_name": "Payment ID"})
    pay_external_id: str = field(default="", metadata={"display_name": "External ID"})
    pay_amount: Decimal = field(default=Decimal(0), metadata={"importance": 1, "display_name": "Amount"})
    pay_currency: str = field(default="", metadata={"importance": 1, "display_name": "Currency"})
    pay_status: str = field(default="PENDING", metadata={"importance": 1, "display_name": "Status", "enum": [
        {"value": "PENDING", "label": "Pending"},
        {"value": "COMPLETED", "label": "Completed"},
        {"value": "FAILED", "label": "Failed"},
        {"value": "REFUNDED", "label": "Refunded"},
    ]})
    pay_provider: str = field(default="", metadata={"importance": 1, "display_name": "Provider"})
    pay_details: dict = field(default_factory=dict, metadata={"display_name": "Details"})
    pay_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    pay_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})


@dataclass
class ComProduct:
    ws_id: str
    prod_name: str = field(metadata={"importance": 1, "display_name": "Name"})
    prod_shop_id: str = field(metadata={"importance": 1, "display_name": "Shop"})
    prod_id: str = field(default="", metadata={"pkey": True, "display_name": "Product ID"})
    prod_external_id: str = field(default="", metadata={"importance": 1, "display_name": "External ID"})
    prod_description: str = field(default="", metadata={"importance": 1, "display": "string_multiline", "display_name": "Description"})
    prod_type: str = field(default="physical", metadata={"importance": 1, "display_name": "Type", "enum": [
        {"value": "physical", "label": "Physical"},
        {"value": "digital", "label": "Digital"},
        {"value": "service", "label": "Service"},
    ]})
    prod_category: str = field(default="", metadata={"importance": 1, "display_name": "Category"})
    prod_tags: List[str] = field(default_factory=list, metadata={"importance": 1, "display_name": "Tags"})
    prod_images: list = field(default_factory=list, metadata={"display_name": "Images"})
    prod_details: dict = field(default_factory=dict, metadata={"display_name": "Details"})
    prod_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    prod_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})
    prod_archived_ts: float = field(default=0.0, metadata={"display_name": "Archived at"})


@dataclass
class ComProductVariant:
    ws_id: str
    pvar_prod_id: str = field(metadata={"importance": 1, "display_name": "Product"})
    pvar_id: str = field(default="", metadata={"pkey": True, "display_name": "Variant ID"})
    pvar_external_id: str = field(default="", metadata={"display_name": "External ID"})
    pvar_name: str = field(default="", metadata={"importance": 1, "display_name": "Name"})
    pvar_sku: str = field(default="", metadata={"importance": 1, "display_name": "SKU"})
    pvar_barcode: str = field(default="", metadata={"display_name": "Barcode"})
    pvar_price: Decimal = field(default=Decimal(0), metadata={"importance": 1, "display_name": "Price"})
    pvar_compare_at_price: Decimal = field(default=Decimal(0), metadata={"display_name": "Compare at Price"})
    pvar_cost: Decimal = field(default=Decimal(0), metadata={"display_name": "Cost"})
    pvar_available_qty: int = field(default=0, metadata={"importance": 1, "display_name": "Available Qty"})
    pvar_inventory_status: str = field(default="UNKNOWN", metadata={"importance": 1, "display_name": "Inventory Status", "enum": [
        {"value": "UNKNOWN", "label": "Unknown"},
        {"value": "IN_STOCK", "label": "In Stock"},
        {"value": "LOW_STOCK", "label": "Low Stock"},
        {"value": "OUT_OF_STOCK", "label": "Out of Stock"},
    ]})
    pvar_weight: Decimal = field(default=Decimal(0), metadata={"display_name": "Weight"})
    pvar_weight_unit: str = field(default="kg", metadata={"display_name": "Weight Unit"})
    pvar_options: dict = field(default_factory=dict, metadata={"display_name": "Options"})
    pvar_active: bool = field(default=True, metadata={"importance": 1, "display_name": "Active"})
    pvar_details: dict = field(default_factory=dict, metadata={"display_name": "Details"})
    pvar_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    pvar_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})


@dataclass
class ComRefund:
    ws_id: str
    refund_order_id: str = field(metadata={"importance": 1, "display_name": "Order"})
    refund_id: str = field(default="", metadata={"pkey": True, "display_name": "Refund ID"})
    refund_external_id: str = field(default="", metadata={"display_name": "External ID"})
    refund_amount: Decimal = field(default=Decimal(0), metadata={"importance": 1, "display_name": "Amount"})
    refund_currency: str = field(default="", metadata={"importance": 1, "display_name": "Currency"})
    refund_reason: str = field(default="", metadata={"importance": 1, "display_name": "Reason"})
    refund_status: str = field(default="PENDING", metadata={"importance": 1, "display_name": "Status", "enum": [
        {"value": "PENDING", "label": "Pending"},
        {"value": "COMPLETED", "label": "Completed"},
        {"value": "FAILED", "label": "Failed"},
    ]})
    refund_line_items: list = field(default_factory=list, metadata={"display_name": "Line Items"})
    refund_details: dict = field(default_factory=dict, metadata={"display_name": "Details"})
    refund_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    refund_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})



@dataclass
class ComShop:
    ws_id: str
    shop_name: str = field(metadata={"importance": 1, "display_name": "Name"})
    shop_type: str = field(metadata={"importance": 1, "display_name": "Type"})
    shop_id: str = field(default="", metadata={"pkey": True, "display_name": "Shop ID"})
    shop_domain: str = field(default="", metadata={"importance": 1, "display_name": "Domain"})
    shop_currency: str = field(default="USD", metadata={"importance": 1, "display_name": "Currency"})
    shop_credentials: dict = field(default_factory=dict, metadata={"display_name": "Credentials"})
    shop_webhook_secret: str = field(default="", metadata={"display_name": "Webhook Secret"})
    shop_sync_cursor: str = field(default="", metadata={"display_name": "Sync Cursor"})
    shop_details: dict = field(default_factory=dict, metadata={"display_name": "Details"})
    shop_active: bool = field(default=True, metadata={"importance": 1, "display_name": "Active"})
    shop_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    shop_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})
    shop_archived_ts: float = field(default=0.0, metadata={"display_name": "Archived at"})


ERP_TABLE_TO_SCHEMA: Dict[str, Type] = {
    "crm_activity": CrmActivity,
    "crm_contact": CrmContact,
    "crm_deal": CrmDeal,
    "crm_pipeline": CrmPipeline,
    "crm_pipeline_stage": CrmPipelineStage,
    "com_order": ComOrder,
    "com_order_item": ComOrderItem,
    "com_payment": ComPayment,
    "com_product": ComProduct,
    "com_product_variant": ComProductVariant,
    "com_refund": ComRefund,
    "com_shop": ComShop,
}

ERP_DISPLAY_NAME_CONFIGS: Dict[str, str] = {
    "crm_activity": "{activity_title}",
    "crm_contact": "{contact_first_name} {contact_last_name}",
    "crm_deal": "{deal_name}",
    "crm_pipeline": "{pipeline_name}",
    "crm_pipeline_stage": "{stage_name}",
    "com_order": "{order_number}",
    "com_order_item": "{oitem_name}",
    "com_payment": "{pay_id}",
    "com_product": "{prod_name}",
    "com_product_variant": "{pvar_name} {pvar_sku}",
    "com_refund": "{refund_id}",
    "com_shop": "{shop_name}",
}


def get_pkey_field(cls: Type) -> str:
    for name, f in cls.__dataclass_fields__.items():
        if f.metadata.get("pkey"):
            return name
    raise ValueError(f"No pkey field in {cls.__name__}")


def get_required_fields(cls: Type) -> List[str]:
    pkey = get_pkey_field(cls)
    return [
        name for name, f in cls.__dataclass_fields__.items()
        if name != "ws_id" and name != pkey
        and f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING
    ]


def get_important_fields(cls: Type) -> List[str]:
    return [name for name, f in cls.__dataclass_fields__.items() if f.metadata.get("importance", 0) > 0]


def get_extra_search_fields(cls: Type) -> List[str]:
    return [name for name, f in cls.__dataclass_fields__.items() if f.metadata.get("extra_search")]


def get_field_display(cls: Type, field_name: str) -> Optional[str]:
    f = cls.__dataclass_fields__.get(field_name)
    return f.metadata.get("display") if f else None


def get_field_enum(cls: Type, field_name: str) -> Optional[List[Dict[str, str]]]:
    f = cls.__dataclass_fields__.get(field_name)
    return (f.metadata.get("enum") if f else None) or None


def get_field_display_name(cls: Type, field_name: str) -> Optional[str]:
    f = cls.__dataclass_fields__.get(field_name)
    return f.metadata.get("display_name") if f else None


def get_field_description(cls: Type, field_name: str) -> Optional[str]:
    f = cls.__dataclass_fields__.get(field_name)
    return f.metadata.get("description") if f else None


def get_field_fk_scope(cls: Type, field_name: str) -> Optional[Dict[str, str]]:
    f = cls.__dataclass_fields__.get(field_name)
    return (f.metadata.get("fk_scope") if f else None) or None
