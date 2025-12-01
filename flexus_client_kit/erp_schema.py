import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Type, List


@dataclass
class CrmContact:
    contact_id: str
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
class CrmTask:
    ws_id: str
    contact_id: str
    task_type: str
    task_title: str
    task_notes: str = ""
    task_details: dict = field(default_factory=dict)
    task_id: str = ""
    task_due_ts: float = 0.0
    task_completed_ts: float = 0.0
    task_created_ts: float = field(default_factory=time.time)
    task_updated_ts: float = field(default_factory=time.time)
    contact: Optional['CrmContact'] = None


@dataclass
class ProductTemplate:
    prodt_id: str
    prodt_name: str
    prodt_type: str
    prodt_pcat_id: str
    prodt_list_price: int  # stored in cents
    prodt_standard_price: int  # stored in cents
    prodt_uom_id: str
    prodt_active: bool
    ws_id: str
    prodt_chips: List[str]
    pcat: Optional['ProductCategory'] = None
    uom: Optional['ProductUom'] = None


@dataclass
class ProductProduct:
    prod_id: str
    prodt_id: str
    prod_default_code: Optional[str]
    prod_barcode: Optional[str]
    prod_active: bool
    ws_id: str
    prodt: Optional[ProductTemplate] = None   # Optional not because it's not nullable, it's optional because you have an option to include or not include it when querying


@dataclass
class ProductCategory:
    pcat_id: str
    pcat_name: str
    pcat_parent_id: Optional[str]
    pcat_active: bool
    ws_id: str
    parent: Optional['ProductCategory'] = None


@dataclass
class ProductTag:
    tag_id: str
    tag_name: str
    tag_sequence: int
    tag_color: str
    tag_visible_to_customers: bool
    ws_id: str


@dataclass
class ProductUom:
    uom_id: str
    uom_name: str
    uom_category_id: Optional[str]
    uom_active: bool
    ws_id: str
    category: Optional[ProductCategory] = None


@dataclass
class ProductM2mTemplateTag:
    id: str
    tag_id: str
    prodt_id: str
    ws_id: str
    tag: Optional[ProductTag] = None
    prodt: Optional['ProductTemplate'] = None


ERP_TABLE_TO_SCHEMA: Dict[str, Type] = {
    "crm_contact": CrmContact,
    "crm_task": CrmTask,
    "product_template": ProductTemplate,
    "product_product": ProductProduct,
    "product_category": ProductCategory,
    "product_tag": ProductTag,
    "product_uom": ProductUom,
    "product_m2m_template_tag": ProductM2mTemplateTag,
}

