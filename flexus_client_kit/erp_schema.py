from __future__ import annotations
import dataclasses
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, Dict, Type, List

PARTY_KIND_ENUM: List[Dict[str, str]] = [
    {"value": "PERSON", "label": "Person"},
    {"value": "COMPANY", "label": "Company"},
]

CONTACT_CHANNEL_ENUM: List[Dict[str, str]] = [
    {"value": "PHONE_CALL", "label": "Phone call"},
    {"value": "SMS", "label": "SMS"},
    {"value": "WHATSAPP", "label": "WhatsApp"},
    {"value": "TELEGRAM", "label": "Telegram"},
    {"value": "INSTAGRAM", "label": "Instagram"},
    {"value": "EMAIL", "label": "Email"},
    {"value": "OTHER", "label": "Other"},
]

CONTACT_ADDRESS_KIND_ENUM: List[Dict[str, str]] = [
    {"value": "PHONE", "label": "Phone"},
    {"value": "EMAIL", "label": "Email"},
    {"value": "USERNAME", "label": "Username"},
    {"value": "EXTERNAL_ID", "label": "External ID"},
    {"value": "URL", "label": "URL"},
    {"value": "OTHER", "label": "Other"},
]

CRM_EVENT_KIND_ENUM: List[Dict[str, str]] = [
    {"value": "TXN_REQUESTED", "label": "Transaction requested"},
    {"value": "TXN_RESCHEDULE_REQUESTED", "label": "Reschedule requested"},
    {"value": "TXN_CANCEL_REQUESTED", "label": "Cancel requested"},
    {"value": "TXN_CONFIRMED", "label": "Confirmed"},
    {"value": "TXN_REMINDER_SENT", "label": "Reminder sent"},
    {"value": "TXN_COMPLETED", "label": "Completed"},
    {"value": "NOTE_CREATED", "label": "Note created"},
    {"value": "CLIENT_MESSAGE_SUMMARIZED", "label": "Client message summarized"},
    {"value": "CLIENT_INTENT_DETECTED", "label": "Client intent detected"},
    {"value": "OTHER", "label": "Other"},
]

CRM_EVENT_SOURCE_ENUM: List[Dict[str, str]] = [
    {"value": "MANUAL", "label": "Manual"},
    {"value": "BOT", "label": "Bot"},
    {"value": "SYSTEM", "label": "System"},
    {"value": "SCHEDULER", "label": "Scheduler"},
    {"value": "MESSENGER", "label": "Messenger"},
    {"value": "WEB_CHAT", "label": "Web chat"},
    {"value": "EMAIL", "label": "Email"},
    {"value": "PHONE", "label": "Phone"},
    {"value": "EXTERNAL_WEBHOOK", "label": "External webhook"},
    {"value": "OTHER", "label": "Other"},
]

CATALOG_ITEM_KIND_ENUM: List[Dict[str, str]] = [
    {"value": "SERVICE", "label": "Service"},
    {"value": "PRODUCT", "label": "Product"},
    {"value": "SUPPLY", "label": "Supply"},
]

RESOURCE_SLOT_ENUM: List[Dict[str, str]] = [
    {"value": "PRIMARY", "label": "Primary"},
    {"value": "SECONDARY", "label": "Secondary"},
    {"value": "TERTIARY", "label": "Tertiary"},
]

TXN_KIND_ENUM: List[Dict[str, str]] = [
    {"value": "APPOINTMENT", "label": "Appointment"},
    {"value": "SALE", "label": "Sale"},
]

TXN_STATUS_ENUM: List[Dict[str, str]] = [
    {"value": "DRAFT", "label": "Draft"},
    {"value": "BOOKED", "label": "Booked"},
    {"value": "CONFIRMED", "label": "Confirmed"},
    {"value": "ARRIVED", "label": "Arrived"},
    {"value": "IN_PROGRESS", "label": "In progress"},
    {"value": "COMPLETED", "label": "Completed"},
    {"value": "CANCELLED", "label": "Cancelled"},
    {"value": "NO_SHOW", "label": "No show"},
]

TXN_SOURCE_ENUM: List[Dict[str, str]] = [
    {"value": "MANUAL", "label": "Manual"},
    {"value": "BOT", "label": "Bot"},
    {"value": "MESSENGER", "label": "Messenger"},
    {"value": "WEB", "label": "Web"},
]

PAYMENT_STATUS_ENUM: List[Dict[str, str]] = [
    {"value": "PENDING", "label": "Pending"},
    {"value": "PAID", "label": "Paid"},
    {"value": "FAILED", "label": "Failed"},
    {"value": "REFUNDED", "label": "Refunded"},
]

INVENTORY_MOVEMENT_KIND_ENUM: List[Dict[str, str]] = [
    {"value": "RESTOCK", "label": "Restock"},
    {"value": "SALE", "label": "Sale"},
    {"value": "SERVICE_CONSUMPTION", "label": "Service consumption"},
    {"value": "ADJUSTMENT", "label": "Adjustment"},
    {"value": "RETURN", "label": "Return"},
]


@dataclass
class Party:
    ws_id: str
    party_id: str = field(default="", metadata={"pkey": True, "display_name": "Party ID"})
    party_kind: str = field(
        default="PERSON",
        metadata={"importance": 1, "display_name": "Kind", "enum": PARTY_KIND_ENUM, "mutable": True},
    )
    party_first_name: str = field(
        default="",
        metadata={"importance": 1, "display_name": "First name", "extra_search": True, "mutable": True},
    )
    party_last_name: str = field(
        default="",
        metadata={"importance": 1, "display_name": "Last name", "extra_search": True, "mutable": True},
    )
    party_company_name: str = field(
        default="",
        metadata={"importance": 1, "display_name": "Company", "extra_search": True, "mutable": True},
    )
    party_reminder_ctpoint_id: Optional[str] = field(default=None, metadata={"display_name": "Reminder contact point"})
    party_notes: str = field(
        default="",
        metadata={"importance": 1, "display": "string_multiline", "display_name": "Notes", "mutable": True},
    )
    party_tags: List[str] = field(default_factory=list, metadata={"importance": 1, "display_name": "Tags", "mutable": True})
    party_details: dict = field(default_factory=dict, metadata={"display_name": "Details", "mutable": True})
    party_created_ts: float = field(default=0.0, metadata={"importance": 1, "display_name": "Created at"})
    party_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})
    party_archived_ts: float = field(default=0.0, metadata={"display_name": "Archived at", "mutable": True})

    contact_points: Optional[List[PartyContactPoint]] = field(
        default=None,
        metadata={"inbound_fk_table": "party_contact_point", "inbound_fk_col": "ctpoint_party_id"},
    )
    reminder_contact_point: Optional[PartyContactPoint] = field(
        default=None,
        metadata={"fk_field": "party_reminder_ctpoint_id", "description": "included via include=['reminder_contact_point']"},
    )
    crm_events: Optional[List[CrmEvent]] = field(
        default=None,
        metadata={"inbound_fk_table": "crm_event", "inbound_fk_col": "crmev_party_id"},
    )
    txns: Optional[List[Txn]] = field(
        default=None,
        metadata={"inbound_fk_table": "txn", "inbound_fk_col": "txn_party_id"},
    )


@dataclass
class PartyContactPoint:
    ws_id: str
    ctpoint_party_id: str
    ctpoint_channel: str = field(
        metadata={"importance": 1, "display_name": "Channel", "enum": CONTACT_CHANNEL_ENUM, "mutable": True},
    )
    ctpoint_address_kind: str = field(
        metadata={
            "importance": 1,
            "display_name": "Address kind",
            "enum": CONTACT_ADDRESS_KIND_ENUM,
            "mutable": True,
        },
    )
    ctpoint_value: str = field(metadata={"importance": 1, "extra_search": True, "display_name": "Value"})
    ctpoint_id: str = field(default="", metadata={"pkey": True, "display_name": "Contact point ID"})
    ctpoint_display_value: str = field(default="", metadata={"display_name": "Display value", "mutable": True})
    ctpoint_label: str = field(default="", metadata={"importance": 1, "display_name": "Label", "mutable": True})
    ctpoint_reminders_enabled: bool = field(default=True, metadata={"display_name": "Reminders enabled", "mutable": True})
    ctpoint_active: bool = field(default=True, metadata={"importance": 1, "display_name": "Active", "mutable": True})
    ctpoint_verified_ts: float = field(default=0.0, metadata={"display_name": "Verified at", "mutable": True})
    ctpoint_details: dict = field(default_factory=dict, metadata={"display_name": "Details", "mutable": True})
    ctpoint_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    ctpoint_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})
    ctpoint_archived_ts: float = field(default=0.0, metadata={"display_name": "Archived at", "mutable": True})

    party: Optional[Party] = field(default=None, metadata={"fk_field": "ctpoint_party_id", "description": "included via include=['party']"})
    reminder_for: Optional[List[Party]] = field(
        default=None,
        metadata={"inbound_fk_table": "party", "inbound_fk_col": "party_reminder_ctpoint_id"},
    )
    crm_events: Optional[List[CrmEvent]] = field(
        default=None,
        metadata={"inbound_fk_table": "crm_event", "inbound_fk_col": "crmev_ctpoint_id"},
    )


@dataclass
class CrmEvent:
    ws_id: str
    crmev_kind: str = field(metadata={"importance": 1, "display_name": "Kind", "enum": CRM_EVENT_KIND_ENUM})
    crmev_source: str = field(metadata={"importance": 1, "display_name": "Source", "enum": CRM_EVENT_SOURCE_ENUM})
    crmev_id: str = field(default="", metadata={"pkey": True, "display_name": "Event ID"})
    crmev_party_id: Optional[str] = field(default=None, metadata={"display_name": "Party"})
    crmev_txn_id: Optional[str] = field(default=None, metadata={"display_name": "Transaction"})
    crmev_ctpoint_id: Optional[str] = field(default=None, metadata={"display_name": "Contact point"})
    crmev_source_name: str = field(default="", metadata={"display_name": "Source name"})
    crmev_source_ref: dict = field(default_factory=dict, metadata={"display_name": "Source ref"})
    crmev_title: str = field(default="", metadata={"importance": 1, "display_name": "Title", "extra_search": True})
    crmev_summary: str = field(default="", metadata={"importance": 1, "display": "string_multiline", "display_name": "Summary"})
    crmev_details: dict = field(default_factory=dict, metadata={"display_name": "Details"})
    crmev_occurred_ts: float = field(default=0.0, metadata={"importance": 1, "display_name": "Occurred at"})
    crmev_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})

    party: Optional[Party] = field(default=None, metadata={"fk_field": "crmev_party_id", "description": "included via include=['party']"})
    txn: Optional[Txn] = field(default=None, metadata={"fk_field": "crmev_txn_id", "description": "included via include=['txn']"})
    contact_point: Optional[PartyContactPoint] = field(
        default=None,
        metadata={"fk_field": "crmev_ctpoint_id", "description": "included via include=['contact_point']"},
    )


@dataclass
class CatalogItem:
    ws_id: str
    citem_kind: str = field(metadata={"importance": 1, "display_name": "Kind", "enum": CATALOG_ITEM_KIND_ENUM})
    citem_name: str = field(metadata={"importance": 1, "extra_search": True, "display_name": "Name"})
    citem_id: str = field(default="", metadata={"pkey": True, "display_name": "Catalog item ID"})
    citem_description: str = field(default="", metadata={"display": "string_multiline", "display_name": "Description"})
    citem_category: str = field(default="", metadata={"importance": 1, "display_name": "Category"})
    citem_active: bool = field(default=False, metadata={"importance": 1, "display_name": "Active"})
    citem_tags: List[str] = field(default_factory=list, metadata={"display_name": "Tags"})
    citem_details: dict = field(default_factory=dict, metadata={"display_name": "Details"})
    citem_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    citem_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})
    citem_archived_ts: float = field(default=0.0, metadata={"display_name": "Archived at"})

    variants: Optional[List[CatalogItemVariant]] = field(
        default=None,
        metadata={"inbound_fk_table": "catalog_item_variant", "inbound_fk_col": "civar_citem_id"},
    )


@dataclass
class CatalogItemVariant:
    ws_id: str
    civar_citem_id: str
    civar_name: str = field(metadata={"importance": 1, "extra_search": True, "display_name": "Name"})
    civar_id: str = field(default="", metadata={"pkey": True, "display_name": "Variant ID"})
    civar_sku: str = field(default="", metadata={"importance": 1, "display_name": "SKU"})
    civar_barcode: str = field(default="", metadata={"display_name": "Barcode"})
    civar_attrs: dict = field(default_factory=dict, metadata={"display_name": "Attributes"})
    civar_price: Decimal = field(default=Decimal(0), metadata={"importance": 1, "display_name": "Price"})
    civar_cost: Decimal = field(default=Decimal(0), metadata={"display_name": "Cost"})
    civar_duration_min: int = field(default=0, metadata={"importance": 1, "display_name": "Duration (min)"})
    civar_unit: str = field(default="pcs", metadata={"display_name": "Unit"})
    civar_sellable: bool = field(default=False, metadata={"importance": 1, "display_name": "Sellable"})
    civar_stock_tracked: bool = field(default=False, metadata={"importance": 1, "display_name": "Stock tracked"})
    civar_active: bool = field(default=False, metadata={"importance": 1, "display_name": "Active"})
    civar_details: dict = field(default_factory=dict, metadata={"display_name": "Details"})
    civar_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    civar_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})
    civar_archived_ts: float = field(default=0.0, metadata={"display_name": "Archived at"})

    catalog_item: Optional[CatalogItem] = field(
        default=None,
        metadata={"fk_field": "civar_citem_id", "description": "included via include=['catalog_item']"},
    )
    resource_requirements: Optional[List[CatalogItemResourceRequirement]] = field(
        default=None,
        metadata={"inbound_fk_table": "catalog_item_resource_requirement", "inbound_fk_col": "cireq_civar_id"},
    )
    supply_requirements_as_service: Optional[List[CatalogItemSupplyRequirement]] = field(
        default=None,
        metadata={"inbound_fk_table": "catalog_item_supply_requirement", "inbound_fk_col": "csreq_service_civar_id"},
    )
    supply_requirements_as_supply: Optional[List[CatalogItemSupplyRequirement]] = field(
        default=None,
        metadata={"inbound_fk_table": "catalog_item_supply_requirement", "inbound_fk_col": "csreq_supply_civar_id"},
    )
    txn_lines: Optional[List[TxnLine]] = field(
        default=None,
        metadata={"inbound_fk_table": "txn_line", "inbound_fk_col": "txnline_civar_id"},
    )
    inventory_balances: Optional[List[InventoryBalance]] = field(
        default=None,
        metadata={"inbound_fk_table": "inventory_balance", "inbound_fk_col": "ibal_civar_id"},
    )
    inventory_movements: Optional[List[InventoryMovement]] = field(
        default=None,
        metadata={"inbound_fk_table": "inventory_movement", "inbound_fk_col": "imov_civar_id"},
    )


@dataclass
class Resource:
    ws_id: str
    resource_slot: str = field(metadata={"importance": 1, "display_name": "Slot", "enum": RESOURCE_SLOT_ENUM})
    resource_name: str = field(metadata={"importance": 1, "extra_search": True, "display_name": "Name"})
    resource_id: str = field(default="", metadata={"pkey": True, "display_name": "Resource ID"})
    resource_active: bool = field(default=True, metadata={"importance": 1, "display_name": "Active"})
    resource_notes: str = field(default="", metadata={"display": "string_multiline", "display_name": "Notes"})
    resource_tags: List[str] = field(default_factory=list, metadata={"display_name": "Tags"})
    resource_details: dict = field(default_factory=dict, metadata={"display_name": "Details"})
    resource_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    resource_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})
    resource_archived_ts: float = field(default=0.0, metadata={"display_name": "Archived at"})

    availability: Optional[List[ResourceAvailability]] = field(
        default=None,
        metadata={"inbound_fk_table": "resource_availability", "inbound_fk_col": "ravail_resource_id"},
    )
    requirements: Optional[List[CatalogItemResourceRequirement]] = field(
        default=None,
        metadata={"inbound_fk_table": "catalog_item_resource_requirement", "inbound_fk_col": "cireq_resource_id"},
    )
    bookings: Optional[List[TxnLineResourceBooking]] = field(
        default=None,
        metadata={"inbound_fk_table": "txn_line_resource_booking", "inbound_fk_col": "booking_resource_id"},
    )


@dataclass
class ResourceAvailability:
    ws_id: str
    ravail_resource_id: str
    ravail_date: str
    ravail_start_minute_of_day: int
    ravail_end_minute_of_day: int
    ravail_id: str = field(default="", metadata={"pkey": True, "display_name": "Availability ID"})
    ravail_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    ravail_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})
    ravail_archived_ts: float = field(default=0.0, metadata={"display_name": "Archived at"})

    resource: Optional[Resource] = field(default=None, metadata={"fk_field": "ravail_resource_id", "description": "included via include=['resource']"})


@dataclass
class CatalogItemResourceRequirement:
    ws_id: str
    cireq_civar_id: str
    cireq_slot: str = field(metadata={"importance": 1, "display_name": "Slot", "enum": RESOURCE_SLOT_ENUM})
    cireq_resource_id: str
    cireq_id: str = field(default="", metadata={"pkey": True, "display_name": "Requirement ID"})
    cireq_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    cireq_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})

    variant: Optional[CatalogItemVariant] = field(default=None, metadata={"fk_field": "cireq_civar_id", "description": "included via include=['variant']"})
    resource: Optional[Resource] = field(default=None, metadata={"fk_field": "cireq_resource_id", "description": "included via include=['resource']"})


@dataclass
class CatalogItemSupplyRequirement:
    ws_id: str
    csreq_service_civar_id: str
    csreq_supply_civar_id: str
    csreq_quantity: Decimal
    csreq_id: str = field(default="", metadata={"pkey": True, "display_name": "Supply requirement ID"})
    csreq_unit: str = field(default="pcs", metadata={"display_name": "Unit"})
    csreq_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    csreq_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})

    service_variant: Optional[CatalogItemVariant] = field(
        default=None,
        metadata={"fk_field": "csreq_service_civar_id", "description": "included via include=['service_variant']"},
    )
    supply_variant: Optional[CatalogItemVariant] = field(
        default=None,
        metadata={"fk_field": "csreq_supply_civar_id", "description": "included via include=['supply_variant']"},
    )


@dataclass
class Txn:
    ws_id: str
    txn_kind: str = field(metadata={"importance": 1, "display_name": "Kind", "enum": TXN_KIND_ENUM})
    txn_id: str = field(default="", metadata={"pkey": True, "display_name": "Transaction ID"})
    txn_party_id: Optional[str] = field(default=None, metadata={"importance": 1, "display_name": "Party"})
    txn_status: str = field(
        default="DRAFT",
        metadata={"importance": 1, "display_name": "Status", "enum": TXN_STATUS_ENUM},
    )
    txn_source: str = field(
        default="MANUAL",
        metadata={"importance": 1, "display_name": "Source", "enum": TXN_SOURCE_ENUM},
    )
    txn_source_name: str = field(default="", metadata={"display_name": "Source name"})
    txn_source_ref: dict = field(default_factory=dict, metadata={"display_name": "Source ref"})
    txn_scheduled_ts1: float = field(default=0.0, metadata={"importance": 1, "display_name": "Scheduled start"})
    txn_scheduled_ts2: float = field(default=0.0, metadata={"importance": 1, "display_name": "Scheduled end"})
    txn_currency: str = field(default="USD", metadata={"display_name": "Currency"})
    txn_subtotal: Decimal = field(default=Decimal(0), metadata={"display_name": "Subtotal"})
    txn_discount_total: Decimal = field(default=Decimal(0), metadata={"display_name": "Discount total"})
    txn_tax_total: Decimal = field(default=Decimal(0), metadata={"display_name": "Tax total"})
    txn_total: Decimal = field(default=Decimal(0), metadata={"importance": 1, "display_name": "Total"})
    txn_notes: str = field(default="", metadata={"importance": 1, "display": "string_multiline", "display_name": "Notes"})
    txn_tags: List[str] = field(default_factory=list, metadata={"display_name": "Tags"})
    txn_details: dict = field(default_factory=dict, metadata={"display_name": "Details"})
    txn_created_ts: float = field(default=0.0, metadata={"importance": 1, "display_name": "Created at"})
    txn_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})
    txn_completed_ts: float = field(default=0.0, metadata={"display_name": "Completed at"})
    txn_cancelled_ts: float = field(default=0.0, metadata={"display_name": "Cancelled at"})
    txn_archived_ts: float = field(default=0.0, metadata={"display_name": "Archived at"})

    party: Optional[Party] = field(default=None, metadata={"fk_field": "txn_party_id", "description": "included via include=['party']"})
    lines: Optional[List[TxnLine]] = field(
        default=None,
        metadata={"inbound_fk_table": "txn_line", "inbound_fk_col": "txnline_txn_id"},
    )
    payments: Optional[List[Payment]] = field(
        default=None,
        metadata={"inbound_fk_table": "payment", "inbound_fk_col": "payment_txn_id"},
    )
    crm_events: Optional[List[CrmEvent]] = field(
        default=None,
        metadata={"inbound_fk_table": "crm_event", "inbound_fk_col": "crmev_txn_id"},
    )
    inventory_movements: Optional[List[InventoryMovement]] = field(
        default=None,
        metadata={"inbound_fk_table": "inventory_movement", "inbound_fk_col": "imov_txn_id"},
    )


@dataclass
class TxnLine:
    ws_id: str
    txnline_txn_id: str
    txnline_item_kind: str = field(metadata={"importance": 1, "display_name": "Item kind", "enum": CATALOG_ITEM_KIND_ENUM})
    txnline_name: str = field(metadata={"importance": 1, "extra_search": True, "display_name": "Name"})
    txnline_id: str = field(default="", metadata={"pkey": True, "display_name": "Line ID"})
    txnline_civar_id: Optional[str] = field(default=None, metadata={"display_name": "Catalog variant"})
    txnline_quantity: Decimal = field(default=Decimal(1), metadata={"importance": 1, "display_name": "Quantity"})
    txnline_unit: str = field(default="pcs", metadata={"display_name": "Unit"})
    txnline_unit_price: Decimal = field(default=Decimal(0), metadata={"importance": 1, "display_name": "Unit price"})
    txnline_discount_total: Decimal = field(default=Decimal(0), metadata={"display_name": "Discount"})
    txnline_tax_total: Decimal = field(default=Decimal(0), metadata={"display_name": "Tax"})
    txnline_total: Decimal = field(default=Decimal(0), metadata={"importance": 1, "display_name": "Line total"})
    txnline_duration_min: int = field(default=0, metadata={"display_name": "Duration (min)"})
    txnline_sort_order: int = field(default=0, metadata={"display_name": "Sort order"})
    txnline_notes: str = field(default="", metadata={"display_name": "Notes"})
    txnline_details: dict = field(default_factory=dict, metadata={"display_name": "Details"})
    txnline_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    txnline_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})

    txn: Optional[Txn] = field(default=None, metadata={"fk_field": "txnline_txn_id", "description": "included via include=['txn']"})
    variant: Optional[CatalogItemVariant] = field(default=None, metadata={"fk_field": "txnline_civar_id", "description": "included via include=['variant']"})
    resource_bookings: Optional[List[TxnLineResourceBooking]] = field(
        default=None,
        metadata={"inbound_fk_table": "txn_line_resource_booking", "inbound_fk_col": "booking_txnline_id"},
    )
    inventory_movements: Optional[List[InventoryMovement]] = field(
        default=None,
        metadata={"inbound_fk_table": "inventory_movement", "inbound_fk_col": "imov_txnline_id"},
    )


@dataclass
class TxnLineResourceBooking:
    ws_id: str
    booking_txnline_id: str
    booking_resource_id: str
    booking_slot: str = field(metadata={"importance": 1, "display_name": "Slot", "enum": RESOURCE_SLOT_ENUM})
    booking_ts1: float
    booking_ts2: float
    booking_id: str = field(default="", metadata={"pkey": True, "display_name": "Booking ID"})
    booking_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    booking_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})
    booking_cancelled_ts: float = field(default=0.0, metadata={"display_name": "Cancelled at"})

    line: Optional[TxnLine] = field(default=None, metadata={"fk_field": "booking_txnline_id", "description": "included via include=['line']"})
    resource: Optional[Resource] = field(default=None, metadata={"fk_field": "booking_resource_id", "description": "included via include=['resource']"})


@dataclass
class Payment:
    ws_id: str
    payment_txn_id: str
    payment_amount: Decimal
    payment_id: str = field(default="", metadata={"pkey": True, "display_name": "Payment ID"})
    payment_currency: str = field(default="USD", metadata={"display_name": "Currency"})
    payment_status: str = field(
        default="PENDING",
        metadata={"importance": 1, "display_name": "Status", "enum": PAYMENT_STATUS_ENUM},
    )
    payment_provider: str = field(default="", metadata={"display_name": "Provider"})
    payment_external_id: str = field(default="", metadata={"display_name": "External ID"})
    payment_details: dict = field(default_factory=dict, metadata={"display_name": "Details"})
    payment_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    payment_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})

    txn: Optional[Txn] = field(default=None, metadata={"fk_field": "payment_txn_id", "description": "included via include=['txn']"})
    refunds: Optional[List[Refund]] = field(
        default=None,
        metadata={"inbound_fk_table": "refund", "inbound_fk_col": "refund_payment_id"},
    )


@dataclass
class Refund:
    ws_id: str
    refund_payment_id: str
    refund_amount: Decimal
    refund_id: str = field(default="", metadata={"pkey": True, "display_name": "Refund ID"})
    refund_reason: str = field(default="", metadata={"display_name": "Reason"})
    refund_details: dict = field(default_factory=dict, metadata={"display_name": "Details"})
    refund_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    refund_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})

    payment: Optional[Payment] = field(default=None, metadata={"fk_field": "refund_payment_id", "description": "included via include=['payment']"})


@dataclass
class InventoryLocation:
    ws_id: str
    iloc_name: str = field(metadata={"importance": 1, "extra_search": True, "display_name": "Name"})
    iloc_id: str = field(default="", metadata={"pkey": True, "display_name": "Location ID"})
    iloc_active: bool = field(default=True, metadata={"importance": 1, "display_name": "Active"})
    iloc_details: dict = field(default_factory=dict, metadata={"display_name": "Details"})
    iloc_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})
    iloc_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})
    iloc_archived_ts: float = field(default=0.0, metadata={"display_name": "Archived at"})

    balances: Optional[List[InventoryBalance]] = field(
        default=None,
        metadata={"inbound_fk_table": "inventory_balance", "inbound_fk_col": "ibal_iloc_id"},
    )
    movements: Optional[List[InventoryMovement]] = field(
        default=None,
        metadata={"inbound_fk_table": "inventory_movement", "inbound_fk_col": "imov_iloc_id"},
    )


@dataclass
class InventoryBalance:
    ws_id: str
    ibal_civar_id: str
    ibal_iloc_id: str
    ibal_id: str = field(default="", metadata={"pkey": True, "display_name": "Balance ID"})
    ibal_quantity: Decimal = field(default=Decimal(0), metadata={"importance": 1, "display_name": "Quantity"})
    ibal_low_stock_at: Decimal = field(default=Decimal(0), metadata={"display_name": "Low stock threshold"})
    ibal_modified_ts: float = field(default=0.0, metadata={"display_name": "Modified at"})

    variant: Optional[CatalogItemVariant] = field(default=None, metadata={"fk_field": "ibal_civar_id", "description": "included via include=['variant']"})
    location: Optional[InventoryLocation] = field(default=None, metadata={"fk_field": "ibal_iloc_id", "description": "included via include=['location']"})


@dataclass
class InventoryMovement:
    ws_id: str
    imov_civar_id: str
    imov_iloc_id: str
    imov_kind: str = field(metadata={"importance": 1, "display_name": "Kind", "enum": INVENTORY_MOVEMENT_KIND_ENUM})
    imov_quantity_delta: Decimal
    imov_id: str = field(default="", metadata={"pkey": True, "display_name": "Movement ID"})
    imov_txn_id: Optional[str] = field(default=None, metadata={"display_name": "Transaction"})
    imov_txnline_id: Optional[str] = field(default=None, metadata={"display_name": "Line"})
    imov_unit: str = field(default="pcs", metadata={"display_name": "Unit"})
    imov_note: str = field(default="", metadata={"display_name": "Note"})
    imov_created_ts: float = field(default=0.0, metadata={"display_name": "Created at"})

    variant: Optional[CatalogItemVariant] = field(default=None, metadata={"fk_field": "imov_civar_id", "description": "included via include=['variant']"})
    location: Optional[InventoryLocation] = field(default=None, metadata={"fk_field": "imov_iloc_id", "description": "included via include=['location']"})
    txn: Optional[Txn] = field(default=None, metadata={"fk_field": "imov_txn_id", "description": "included via include=['txn']"})
    line: Optional[TxnLine] = field(default=None, metadata={"fk_field": "imov_txnline_id", "description": "included via include=['line']"})


ERP_TABLE_TO_SCHEMA: Dict[str, Type] = {
    "party": Party,
    "party_contact_point": PartyContactPoint,
    "crm_event": CrmEvent,
    "catalog_item": CatalogItem,
    "catalog_item_variant": CatalogItemVariant,
    "resource": Resource,
    "resource_availability": ResourceAvailability,
    "catalog_item_resource_requirement": CatalogItemResourceRequirement,
    "catalog_item_supply_requirement": CatalogItemSupplyRequirement,
    "txn": Txn,
    "txn_line": TxnLine,
    "txn_line_resource_booking": TxnLineResourceBooking,
    "payment": Payment,
    "refund": Refund,
    "inventory_location": InventoryLocation,
    "inventory_balance": InventoryBalance,
    "inventory_movement": InventoryMovement,
}

ERP_TABLE_LABELS: Dict[str, str] = {
    "party": "Party",
    "party_contact_point": "Contact point",
    "crm_event": "CRM event",
    "catalog_item": "Catalog item",
    "catalog_item_variant": "Catalog item variant",
    "resource": "Resource",
    "resource_availability": "Resource availability",
    "catalog_item_resource_requirement": "Resource requirement",
    "catalog_item_supply_requirement": "Supply requirement",
    "txn": "Transaction",
    "txn_line": "Transaction line",
    "txn_line_resource_booking": "Resource booking",
    "payment": "Payment",
    "refund": "Refund",
    "inventory_location": "Inventory location",
    "inventory_balance": "Inventory balance",
    "inventory_movement": "Inventory movement",
}

ERP_DISPLAY_NAME_CONFIGS: Dict[str, str] = {
    "party": "{party_company_name} {party_first_name} {party_last_name}",
    "party_contact_point": "{ctpoint_label} {ctpoint_value}",
    "crm_event": "{crmev_title}",
    "catalog_item": "{citem_name}",
    "catalog_item_variant": "{civar_name}",
    "resource": "{resource_name}",
    "resource_availability": "{ravail_date}",
    "catalog_item_resource_requirement": "{cireq_id}",
    "catalog_item_supply_requirement": "{csreq_id}",
    "txn": "{txn_id}",
    "txn_line": "{txnline_name}",
    "txn_line_resource_booking": "{booking_id}",
    "payment": "{payment_id}",
    "refund": "{refund_id}",
    "inventory_location": "{iloc_name}",
    "inventory_balance": "{ibal_id}",
    "inventory_movement": "{imov_id}",
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


def get_field_examples(cls: Type, field_name: str) -> Optional[str]:
    f = cls.__dataclass_fields__.get(field_name)
    return f.metadata.get("examples") if f else None


def get_field_fk_scope(cls: Type, field_name: str) -> Optional[Dict[str, str]]:
    f = cls.__dataclass_fields__.get(field_name)
    return (f.metadata.get("fk_scope") if f else None) or None


def get_field_editable(cls: Type, field_name: str) -> bool:
    f = cls.__dataclass_fields__.get(field_name)
    return f.metadata.get("editable", True) if f else True


def get_mutable_fields(cls: Type) -> List[str]:
    """Field names allowed for ERP ingest updates (`mutable` metadata), in dataclass declaration order."""
    return [name for name, f in cls.__dataclass_fields__.items() if f.metadata.get("mutable")]


def get_relation_to_fk_map(cls: Type) -> Dict[str, str]:
    return {name: f.metadata["fk_field"] for name, f in cls.__dataclass_fields__.items() if f.metadata.get("fk_field")}


def get_inbound_relation_map(cls: Type) -> Dict[str, tuple]:
    return {name: (f.metadata["inbound_fk_table"], f.metadata["inbound_fk_col"]) for name, f in cls.__dataclass_fields__.items() if f.metadata.get("inbound_fk_table")}
