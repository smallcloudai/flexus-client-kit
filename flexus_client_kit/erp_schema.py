import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Type, List


@dataclass
class CrmContact:
    ws_id: str
    contact_first_name: str
    contact_last_name: str
    contact_email: str
    contact_id: str = ""
    contact_notes: str = ""
    contact_details: dict = field(default_factory=dict)
    contact_tags: List[str] = field(default_factory=list)
    contact_address_line1: str = ""
    contact_address_line2: str = ""
    contact_address_city: str = ""
    contact_address_state: str = ""
    contact_address_zip: str = ""
    contact_address_country: str = ""
    contact_utm_first_source: str = ""
    contact_utm_first_medium: str = ""
    contact_utm_first_campaign: str = ""
    contact_utm_first_term: str = ""
    contact_utm_first_content: str = ""
    contact_utm_last_source: str = ""
    contact_utm_last_medium: str = ""
    contact_utm_last_campaign: str = ""
    contact_utm_last_term: str = ""
    contact_utm_last_content: str = ""
    contact_created_ts: float = 0.0
    contact_modified_ts: float = 0.0
    contact_archived_ts: float = 0.0


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
    task_modified_ts: float = field(default_factory=time.time)
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


ERP_DEFAULT_VISIBLE_FIELDS: Dict[str, List[str]] = {
    "crm_contact": [
        "contact_first_name",
        "contact_last_name",
        "contact_email",
        "contact_notes",
        "contact_tags",
        "contact_utm_first_source",
        "contact_address_country",
        "contact_created_ts",
    ],
    "crm_task": [
        "task_title",
        "task_type",
        "task_notes",
        "task_due_ts",
        "task_completed_ts",
        "contact_id",
    ],
    "product_template": [
        "prodt_name",
        "prodt_type",
        "prodt_list_price",
        "prodt_standard_price",
        "prodt_active",
        "prodt_chips",
    ],
    "product_product": [
        "prodt_id",
        "prod_default_code",
        "prod_barcode",
        "prod_active",
    ],
    "product_category": [
        "pcat_name",
        "pcat_parent_id",
        "pcat_active",
    ],
    "product_tag": [
        "tag_name",
        "tag_sequence",
        "tag_color",
        "tag_visible_to_customers",
    ],
    "product_uom": [
        "uom_name",
        "uom_category_id",
        "uom_active",
    ],
}

