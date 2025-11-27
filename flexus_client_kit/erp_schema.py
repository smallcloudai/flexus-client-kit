from dataclasses import dataclass
from typing import Optional, Dict, Type, List


@dataclass
class CrmContact:
    contact_id: int
    ws_id: str
    contact_first_name: str
    contact_last_name: str
    contact_email: str
    contact_notes: str
    contact_details: dict
    contact_address_line1: str
    contact_address_line2: str
    contact_address_city: str
    contact_address_state: str
    contact_address_zip: str
    contact_address_country: str
    contact_utm_first_source: str
    contact_utm_first_medium: str
    contact_utm_first_campaign: str
    contact_utm_first_term: str
    contact_utm_first_content: str
    contact_utm_last_source: str
    contact_utm_last_medium: str
    contact_utm_last_campaign: str
    contact_utm_last_term: str
    contact_utm_last_content: str
    contact_created_ts: float
    contact_updated_ts: float
    contact_deleted_ts: float


@dataclass
class ProductTemplate:
    prodt_id: int
    prodt_name: str
    prodt_type: str
    prodt_pcat_id: int
    prodt_list_price: int  # stored in cents
    prodt_standard_price: int  # stored in cents
    prodt_uom_id: int
    prodt_active: bool
    ws_id: str
    prodt_chips: List[str]


@dataclass
class ProductProduct:
    prod_id: int
    prodt_id: int
    prod_default_code: Optional[str]
    prod_barcode: Optional[str]
    prod_active: bool
    ws_id: str
    prodt: Optional[ProductTemplate] = None   # Optional not because it's not nullable, it's optional because you have an option to include or not include it when querying


@dataclass
class CrmTask:
    task_id: int
    ws_id: str
    contact_id: int
    task_type: str
    task_title: str
    task_notes: str
    task_details: dict
    task_due_ts: float
    task_completed_ts: float
    task_created_ts: float
    task_updated_ts: float


ERP_TABLE_TO_SCHEMA: Dict[str, Type] = {
    "product_product": ProductProduct,
    "product_template": ProductTemplate,
    "crm_contact": CrmContact,
    "crm_task": CrmTask,
}

